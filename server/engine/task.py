from server.celery import celery_app
from server.lib.FileManager import FileManager
from server.lib.CacheManager import CacheManager
from server.models.data import Data
from server.models.graph import GraphTopoModel, GraphPatch, NodeError, DataZip, Graph
from server.models.database import get_session, Data as DBData, Project
from .graph import NodeGraph
from server.models.exception import NodeParameterError, NodeValidationError, NodeExecutionError
from typing import Any
from server.lib.SreamQueue import StreamQueue, Status
import os
import redis
import time

LOCK_REDIS_URL = os.getenv("REDIS_URL", "") + "/3"

@celery_app.task(bind=True)
def execute_nodes_task(self, graph_request_dict: dict, user_id: int):
    """
    Celery task to execute a node graph with real-time updates via Redis Streams.
    Uses StreamQueue (sync version) to handle state reporting.
    """
    graph_request = GraphTopoModel(**graph_request_dict)
    project_id = graph_request.project_id
    task_id = self.request.id
    
    # get db client
    db_client = next(get_session())
    
    # lock to prevent concurrent runs on the same project
    print(LOCK_REDIS_URL)
    redis_client = redis.Redis.from_url(LOCK_REDIS_URL, decode_responses=True)
    lock_key = f"lock:project_run:{project_id}"
    project_lock = redis_client.lock(lock_key, timeout=600)

    project, graph_data = None, None
    with StreamQueue(task_id) as queue:
        try:
            # 0. lock all rows related to this project
            project = db_client.query(Project).filter(Project.id == project_id).first()
            if project is None:
                raise ValueError("Project not found")
            if project.graph is None:
                raise ValueError("Project graph is empty")
            graph_data = Graph(**project.graph) # a graph obj in memory for update # type: ignore
            db_client.query(DBData).filter(DBData.project_id == project_id).delete() # delete old data
            # 1. Validate data model
            graph = None
            try:
                file_manager = FileManager()
                cache_manager = CacheManager(project_id=project_id)
                graph = NodeGraph(file_manager=file_manager, cache_manager=cache_manager, request=graph_request, user_id=user_id)
                queue.push_message_sync(
                    Status.IN_PROGRESS, 
                    {"stage": "VALIDATION", "status": "SUCCESS"}
                )
            except Exception as e:
                patch = GraphPatch(
                            key=["error_message"], 
                            value="Validation Error:" + str(e)
                        )
                queue.push_message_sync(
                    Status.FAILURE,
                    {
                        "stage": "VALIDATION", 
                        "status": "FAILURE",
                        "patch": [patch.model_dump()]
                    }
                )
                graph_data.apply_patch(patch)
                return

            # 2. Construct nodes
            try:
                assert graph is not None
                graph.construct_nodes()
                queue.push_message_sync(
                    Status.IN_PROGRESS, 
                    {"stage": "CONSTRUCTION", "status": "SUCCESS"}
                )
            except NodeParameterError as e:
                node_index = graph_request.get_index_by_node_id(e.node_id)
                assert node_index is not None
                patch = GraphPatch(
                            key=["nodes", node_index, "error"],
                            value=NodeError(
                                param=e.err_param_key, input=None, message=e.err_msg
                            ),
                        )
                queue.push_message_sync(
                    Status.FAILURE,
                    {
                        "stage": "CONSTRUCTION",
                        "status": "FAILURE",
                        "patch": [patch.model_dump()],
                    }
                )
                graph_data.apply_patch(patch)
                return
            except Exception as e:
                patch = GraphPatch(
                            key=["error_message"],
                            value="Construction Error:" + str(e)
                        )
                queue.push_message_sync(
                    Status.FAILURE, 
                    {
                        "stage": "CONSTRUCTION", 
                        "status": "FAILURE",
                        "patch": [patch.model_dump()]
                    }
                )
                graph_data.apply_patch(patch)
                raise

            # 3. Static analysis
            try:
                assert graph is not None
                def anl_reporter(node_id: str, output_schemas: dict[str, Any]) -> None:
                    node_index = graph_request.get_index_by_node_id(node_id)
                    assert node_index is not None
                    patch = GraphPatch(
                        key=["nodes", node_index, "schema_out"],
                        value=output_schemas
                    )
                    queue.push_message_sync(
                        Status.IN_PROGRESS,
                        {
                            "stage": "STATIC_ANALYSIS", 
                            "status": "SUCCESS", 
                            "patch": [patch.model_dump()]
                        }
                    )
                    graph_data.apply_patch(patch)
                
                graph.static_analyse(callback=anl_reporter)
                queue.push_message_sync(Status.IN_PROGRESS, {"stage": "STATIC_ANALYSIS", "status": "SUCCESS"})
            except NodeValidationError as e:
                node_index = graph_request.get_index_by_node_id(e.node_id)
                assert node_index is not None
                patch = GraphPatch(
                            key=["nodes", node_index, "error"],
                            value=NodeError(
                                param=None, input=e.err_input, message=e.err_msg
                            ),
                        )
                queue.push_message_sync(
                    Status.FAILURE, 
                    {
                        "stage": "STATIC_ANALYSIS", 
                        "status": "FAILURE", 
                        "patch": [patch.model_dump()]
                    }
                )
                graph_data.apply_patch(patch)
                raise
            except Exception as e:
                patch = GraphPatch(
                            key=["error_message"],
                            value="Static Analysis Error:" + str(e)
                        )
                queue.push_message_sync(
                    Status.FAILURE, 
                    {
                        "stage": "STATIC_ANALYSIS", 
                        "status": "FAILURE", 
                        "patch": [patch.model_dump()]
                    }
                )
                graph_data.apply_patch(patch)
                raise

            # 4. Execute graph
            try:
                assert graph is not None
                timers: dict[str, float] = {}
                def exec_before_reporter(node_id: str) -> None: # for timer in frontend
                    meta = {
                        "stage": "EXECUTION",
                        "status": "IN_PROGRESS",
                        "node_id": node_id,
                        "timer": "start"
                    }
                    queue.push_message_sync(Status.IN_PROGRESS, meta)
                    timers[node_id] = time.perf_counter()
                    
                def exec_after_reporter(node_id: str, output_data: dict[str, Data]) -> None:
                    # 1. get running time
                    end_time = time.perf_counter()
                    running_time = (end_time - timers[node_id]) * 1000  # in ms
                    
                    data_zips = {}
                    for port, data in output_data.items():
                        # 2. store data in database
                        db_data = DBData(
                            project_id=project_id,
                            node_id=node_id,
                            port=port,
                            data=data.to_view().to_dict()
                        )
                        db_client.add(db_data)
                        # 3. construct datazip
                        db_client.flush()
                        id_data = db_data.id
                        data_zips[port] = DataZip(
                            url=f"/nodes/data/{id_data}"
                        )                    
                    # 4. report to frontend
                    node_index = graph_request.get_index_by_node_id(node_id)
                    assert node_index is not None
                    data_patch = GraphPatch(
                        key = ["nodes", node_index, "data_out"],
                        value = data_zips
                    )
                    time_patch = GraphPatch(
                        key = ["nodes", node_index, "runningtime"],
                        value = running_time
                    )
                    meta = {
                        "stage": "EXECUTION",
                        "status": "IN_PROGRESS",
                        "node_id": node_id,
                        "timer": "stop",
                        "patch": [data_patch.model_dump()] # frontend has its own timer calculation, ours timer only for save to db
                    }
                    queue.push_message_sync(Status.IN_PROGRESS, meta)
                    graph_data.apply_patch(data_patch)
                    graph_data.apply_patch(time_patch)

                graph.execute(callbefore=exec_before_reporter, callafter=exec_after_reporter)
                queue.push_message_sync(Status.SUCCESS, {"stage": "EXECUTION", "status": "SUCCESS"})
            except NodeExecutionError as e:
                node_index = graph_request.get_index_by_node_id(e.node_id)
                assert node_index is not None
                patch = GraphPatch(
                    key=["nodes", node_index, "error"],
                    value=NodeError(
                        param=None, input=None, message=e.err_msg
                    ),
                )
                queue.push_message_sync(
                    Status.FAILURE, 
                    {
                        "stage": "EXECUTION", 
                        "status": "FAILURE", 
                        "patch": [patch.model_dump()]
                    }
                )
                graph_data.apply_patch(patch)
                raise
            except Exception as e:
                patch = GraphPatch(
                    key=["error_message"],
                    value="Execution Error:" + str(e)
                )
                queue.push_message_sync(
                    Status.FAILURE,
                    {
                        "stage": "EXECUTION", 
                        "status": "FAILURE", 
                        "patch": [patch.model_dump()]
                    }
                )
                graph_data.apply_patch(patch)
                raise
            
            project.graph = graph_data.model_dump() # type: ignore
            db_client.commit()

        except Exception:
            # Catch any unexpected errors OR re-raised specific errors
            # If an error occurred, graph_data might hold the error patch
            if graph_data and project:
                project.graph = graph_data.model_dump() # type: ignore

            if db_client.is_active:
                db_client.commit()  # Commit the error state to the DB
            else:
                db_client.rollback()  # Or rollback if something went very wrong

        finally:
            if project_lock.locked():
                project_lock.release()
            db_client.close()
