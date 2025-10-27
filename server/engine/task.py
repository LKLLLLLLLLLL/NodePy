from server.celery import celery_app
from server.lib.FileManager import FileManager
from server.lib.CacheManager import CacheManager
from server.lib.ProjectLock import ProjectLock
from server.models.data import Data
from server.models.project import WorkflowTopology, ProjectPatch, DataRef, ProjNodeError, ProjWorkflow
from server.models.database import NodeOutputRecord, ProjectRecord, DatabaseTransaction
from .executer import ProjectExecutor
from server.models.exception import NodeParameterError, NodeValidationError, NodeExecutionError
from typing import Any, Literal
from server.lib.SreamQueue import StreamQueue, Status
from celery.exceptions import SoftTimeLimitExceeded
from loguru import logger

@celery_app.task(
    bind=True,
    time_limit=10*60,  # 10 minutes
    soft_time_limit=9*60,  # 9 minutes
)
def execute_project_task(self, topo_graph_dict: dict, user_id: int):
    """
    Celery task to execute a node graph with real-time updates via Redis Streams.
    Uses StreamQueue (sync version) to handle state reporting.
    """
    topo_graph = WorkflowTopology(**topo_graph_dict)
    project_id = topo_graph.project_id
    task_id = self.request.id
    
    # lock to prevent concurrent runs on the same project
    with ProjectLock(project_id=project_id, max_block_time=30.0, identity=task_id):  # wait up to 30 seconds to acquire lock
        with StreamQueue(task_id) as queue:
            with DatabaseTransaction() as db_client:
                # 0. get old workflow from db
                project_record = db_client.query(ProjectRecord).filter(ProjectRecord.id == project_id).first()
                if project_record is None:
                    raise ValueError("Project not found")
                if project_record.workflow is None:
                    raise ValueError("Project workflow is empty")
                workflow = ProjWorkflow(**project_record.workflow)  # type: ignore

                # 1. Validate data model
                try:
                    graph = None
                    try:
                        file_manager = FileManager(async_db_session=None)  # sync version
                        cache_manager = CacheManager()
                        graph = ProjectExecutor(file_manager=file_manager, cache_manager=cache_manager, topology=topo_graph, user_id=user_id)
                        queue.push_message_sync(
                            Status.IN_PROGRESS, 
                            {"stage": "VALIDATION", "status": "SUCCESS"}
                        )
                    except Exception as e:
                        patch = ProjectPatch(
                                    key=["workflow", "error_message"], 
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
                        workflow.apply_patch(patch)
                        raise

                    # 2. Construct nodes
                    assert graph is not None
                    has_exception = False
                    def construct_reporter(node_id: str, status: Literal["success", "error"], exception: Exception | None) -> bool:
                        nonlocal has_exception
                        if status == "success":
                            meta = {
                                "stage": "CONSTRUCTION",
                                "node_id": node_id,
                                "status": "IN_PROGRESS",
                            }
                            queue.push_message_sync(Status.IN_PROGRESS, meta)
                            return True
                        # error case
                        assert exception is not None
                        try:
                            raise exception
                        except NodeParameterError as e:
                            has_exception = True
                            node_index = topo_graph.get_index_by_node_id(e.node_id)
                            assert node_index is not None
                            patch = ProjectPatch(
                                key=["workflow", "nodes", node_index, "error"],
                                value=ProjNodeError(
                                    params=e.err_param_keys, inputs=None, message=e.err_msgs
                                ),
                            )
                            queue.push_message_sync(
                                Status.IN_PROGRESS,
                                {
                                    "stage": "CONSTRUCTION",
                                    "status": "IN_PROGRESS",
                                    "patch": [patch.model_dump()],
                                },
                            )
                            workflow.apply_patch(patch)
                        except Exception as e:
                            has_exception = True
                            patch = ProjectPatch(
                                key=["workflow", "error_message"],
                                value="Construction Error:" + str(e)
                            )
                            queue.push_message_sync(
                                Status.IN_PROGRESS,
                                {
                                    "stage": "CONSTRUCTION",
                                    "status": "IN_PROGRESS",
                                    "patch": [patch.model_dump()]
                                }
                            )
                            workflow.apply_patch(patch)
                        return True # continue execution for other nodes
                    graph.construct_nodes(callback=construct_reporter)
                    if has_exception:
                        queue.push_message_sync(
                            Status.FAILURE, 
                            {"stage": "CONSTRUCTION", "status": "FAILURE"}
                        )
                        return  # stop execution if construction failed
                    else:
                        queue.push_message_sync(
                            Status.IN_PROGRESS, 
                            {"stage": "CONSTRUCTION", "status": "SUCCESS"}
                        )

                    # 3. Static analysis
                    assert graph is not None
                    def anl_reporter(node_id: str, status: Literal["success", "error"], result: dict[str, Any] | Exception) -> bool:
                        nonlocal has_exception
                        if status == "success":
                            assert isinstance(result, dict)
                            output_schemas = result
                            node_index = topo_graph.get_index_by_node_id(node_id)
                            assert node_index is not None
                            patch = ProjectPatch(
                                key=["workflow", "nodes", node_index, "schema_out"],
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
                            workflow.apply_patch(patch)
                            return True
                        # error case
                        assert isinstance(result, Exception)
                        try:
                            raise result
                        except NodeValidationError as e:
                            has_exception = True
                            node_index = topo_graph.get_index_by_node_id(e.node_id)
                            assert node_index is not None
                            patch = ProjectPatch(
                                        key=["workflow", "nodes", node_index, "error"],
                                        value=ProjNodeError(
                                            params=None, inputs=e.err_inputs, message=e.err_msgs
                                        ),
                                    )
                            queue.push_message_sync(
                                Status.IN_PROGRESS, 
                                {
                                    "stage": "STATIC_ANALYSIS", 
                                    "status": "IN_PROGRESS", 
                                    "patch": [patch.model_dump()]
                                }
                            )
                            workflow.apply_patch(patch)
                        except Exception as e:
                            has_exception = True
                            patch = ProjectPatch(
                                        key=["workflow", "error_message"],
                                        value="Static Analysis Error:" + str(e)
                                    )
                            queue.push_message_sync(
                                Status.IN_PROGRESS, 
                                {
                                    "stage": "STATIC_ANALYSIS", 
                                    "status": "IN_PROGRESS", 
                                    "patch": [patch.model_dump()]
                                }
                            )
                            workflow.apply_patch(patch)
                        return True # continue execution for other nodes
                    graph.static_analyse(callback=anl_reporter)
                    if has_exception:
                        queue.push_message_sync(
                            Status.FAILURE, 
                            {"stage": "STATIC_ANALYSIS", "status": "FAILURE"}
                        )
                        return  # stop execution if static analysis failed
                    else:
                        queue.push_message_sync(Status.IN_PROGRESS, {"stage": "STATIC_ANALYSIS", "status": "SUCCESS"})

                    # 4. Execute graph
                    assert graph is not None
                    def exec_before_reporter(node_id: str) -> None: # for timer in frontend
                        meta = {
                            "stage": "EXECUTION",
                            "status": "IN_PROGRESS",
                            "node_id": node_id,
                            "timer": "start"
                        }
                        queue.push_message_sync(Status.IN_PROGRESS, meta)

                    def exec_after_reporter(node_id: str, status: Literal["success", "error"], result: dict[str, Data] | Exception, running_time: float | None) -> bool:
                        nonlocal has_exception
                        if status == "success":  
                            assert isinstance(result, dict)
                            output_data = result                  
                            data_zips = {}
                            for port, data in output_data.items():
                                # 1. store data in database
                                db_data = NodeOutputRecord(
                                    project_id=project_id,
                                    node_id=node_id,
                                    port=port,
                                    data=data.to_view().to_dict()
                                )
                                db_client.add(db_data)
                                # 2. construct datazip
                                db_client.flush()
                                id_data = db_data.id
                                data_zips[port] = DataRef(data_id = id_data) # type: ignore
                            # 3. report to frontend
                            node_index = topo_graph.get_index_by_node_id(node_id)
                            assert node_index is not None
                            data_patch = ProjectPatch(
                                key = ["workflow", "nodes", node_index, "data_out"],
                                value = data_zips
                            )
                            time_patch = ProjectPatch(
                                key = ["workflow", "nodes", node_index, "runningtime"],
                                value = running_time
                            )
                            meta = {
                                "stage": "EXECUTION",
                                "status": "IN_PROGRESS",
                                "node_id": node_id,
                                "timer": "stop",
                                "patch": [data_patch.model_dump(), time_patch.model_dump()], 
                                # frontend has its own timer calculation, ours timer only for save to db
                                # if user refresh the page, the runningtime will change to the backend calculated one
                            }
                            queue.push_message_sync(Status.IN_PROGRESS, meta)
                            workflow.apply_patch(data_patch)
                            workflow.apply_patch(time_patch)
                            return True
                        # error case
                        assert isinstance(result, Exception)
                        try:
                            raise result
                        except NodeExecutionError as e:
                            has_exception = True
                            node_index = topo_graph.get_index_by_node_id(e.node_id)
                            assert node_index is not None
                            patch = ProjectPatch(
                                key=["workflow", "nodes", node_index, "error"],
                                value=ProjNodeError(
                                    params=None, inputs=None, message=e.err_msg
                                ),
                            )
                            queue.push_message_sync(
                                Status.IN_PROGRESS, 
                                {
                                    "stage": "EXECUTION", 
                                    "status": "IN_PROGRESS", 
                                    "patch": [patch.model_dump()]
                                }
                            )
                            workflow.apply_patch(patch)
                            return True
                        except Exception as e:
                            has_exception = True
                            patch = ProjectPatch(
                                key=["workflow", "error_message"],
                                value="Execution Error:" + str(e)
                            )
                            queue.push_message_sync(
                                Status.IN_PROGRESS,
                                {
                                    "stage": "EXECUTION", 
                                    "status": "IN_PROGRESS", 
                                    "patch": [patch.model_dump()]
                                }
                            )
                            workflow.apply_patch(patch)
                            return True
                    graph.execute(callbefore=exec_before_reporter, callafter=exec_after_reporter)
                    if has_exception:
                        queue.push_message_sync(
                            Status.FAILURE, 
                            {"stage": "EXECUTION", "status": "FAILURE"}
                        )
                        return  # stop execution if execution failed
                    else:
                        queue.push_message_sync(Status.SUCCESS, {"stage": "EXECUTION", "status": "SUCCESS"})

                    # 5. Finalize and save workflow
                    project_record.workflow = workflow.model_dump() # type: ignore
                    db_client.commit()

                except SoftTimeLimitExceeded:
                    logger.exception("Task time limit exceeded")
                    patch = ProjectPatch(
                        key=["workflow", "error_message"],
                        value="Error: Task timed out."
                    )
                    if workflow:
                        workflow.apply_patch(patch)
                    queue.push_message_sync(
                        Status.FAILURE,
                        {
                            "stage": "UNKNOWN",
                            "status": "FAILURE",
                            "patch": [patch.model_dump()]
                        }
                    )
                except Exception as e:
                    logger.exception(f"Error during task execution: {e}")
                    patch = ProjectPatch(
                        key=["workflow", "error_message"],
                        value="Error:" + str(e)
                    )
                    if workflow:
                        workflow.apply_patch(patch)
                    queue.push_message_sync(
                        Status.FAILURE,
                        {
                            "stage": "UNKNOWN",
                            "status": "FAILURE",
                            "patch": [patch.model_dump()]
                        }
                    )
                finally:
                    project_record.workflow = workflow.model_dump() # type: ignore
                    if db_client.is_active:
                        db_client.commit()  # Commit the error state to the DB
