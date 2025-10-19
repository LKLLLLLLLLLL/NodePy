from ..celery import celery_app
from ..lib.FileManager import FileManager
from ..lib.CacheManager import CacheManager
from .graph import GraphRequestModel, NodeGraph
from .nodes.Exceptions import NodeParameterError, NodeValidationError, NodeExecutionError
from typing import Any
from ..lib.SreamQueue import StreamQueue, Status

@celery_app.task(bind=True)
def execute_nodes_task(self, graph_request_dict: dict, user_id: str):
    """
    Celery task to execute a node graph with real-time updates via Redis Streams.
    Uses StreamQueue (sync version) to handle state reporting.
    """
    graph_request = GraphRequestModel(**graph_request_dict)
    project_id = graph_request.project_id
    task_id = self.request.id
    
    with StreamQueue(task_id) as queue:
        try:
            # 1. Validate data model
            graph = None
            try:
                file_manager = FileManager(user_id=user_id, project_id=project_id)
                cache_manager = CacheManager(user_id=user_id, project_id=project_id)
                graph = NodeGraph(file_manager=file_manager, cache_manager=cache_manager, request=graph_request)
                queue.push_message_sync(Status.IN_PROGRESS, {"stage": "VALIDATION", "status": "SUCCESS"})
            except Exception as e:
                queue.push_message_sync(Status.FAILURE, {"stage": "VALIDATION", "status": "FAILURE", "error": {"type": "unknown", "msg": str(e)}})
                return

            # 2. Construct nodes
            try:
                assert graph is not None
                graph.construct_nodes()
                queue.push_message_sync(Status.IN_PROGRESS, {"stage": "CONSTRUCTION", "status": "SUCCESS"})
            except NodeParameterError as e:
                queue.push_message_sync(Status.FAILURE, {"stage": "CONSTRUCTION", "status": "FAILURE", "error": {"type": "NodeParameterError", "node_id": e.node_id, "msg": e.err_msg}})
                return
            except Exception as e:
                queue.push_message_sync(Status.FAILURE, {"stage": "CONSTRUCTION", "status": "FAILURE", "error": {"type": "unknown", "msg": str(e)}})
                return

            # 3. Static analysis
            try:
                assert graph is not None
                def anl_reporter(node_id: str, output_schemas: dict[str, Any]) -> None:
                    meta = {
                        "stage": "STATIC_ANALYSIS",
                        "status": "IN_PROGRESS",
                        "node_id": node_id,
                        "output_schemas": {k: v.to_dict() for k, v in output_schemas.items()}
                    }
                    queue.push_message_sync(Status.IN_PROGRESS, meta)
                
                graph.static_analyse(callback=anl_reporter)
                queue.push_message_sync(Status.IN_PROGRESS, {"stage": "STATIC_ANALYSIS", "status": "SUCCESS"})
            except NodeValidationError as e:
                queue.push_message_sync(Status.FAILURE, {"stage": "STATIC_ANALYSIS", "status": "FAILURE", "error": {"type": "NodeValidationError", "node_id": e.node_id, "node_input": e.err_input, "msg": e.err_msg}})
                return
            except Exception as e:
                queue.push_message_sync(Status.FAILURE, {"stage": "STATIC_ANALYSIS", "status": "FAILURE", "error": {"type": "unknown", "msg": str(e)}})
                return

            # 4. Execute graph
            try:
                assert graph is not None
                def exec_reporter(node_id: str, output_data: dict[str, Any]) -> None:
                    meta = {
                        "stage": "EXECUTION",
                        "status": "IN_PROGRESS",
                        "node_id": node_id,
                        "output_data": {k: v.to_dict() for k, v in output_data.items()}
                    }
                    queue.push_message_sync(Status.IN_PROGRESS, {"stage": "EXECUTION", "status": "IN_PROGRESS", "meta": meta})
                    
                graph.execute(callback=exec_reporter)
                queue.push_message_sync(Status.SUCCESS, {"stage": "EXECUTION", "status": "SUCCESS"})
            except NodeExecutionError as e:
                queue.push_message_sync(Status.FAILURE, {"stage": "EXECUTION", "status": "FAILURE", "error": {"type": "NodeExecutionError", "node_id": e.node_id, "msg": e.err_msg}})
                return
            except Exception as e:
                queue.push_message_sync(Status.FAILURE, {"stage": "EXECUTION", "status": "FAILURE", "error": {"type": "unknown", "msg": str(e)}})
                return
                
        except Exception as e:
            # Catch any unexpected errors
            queue.push_message_sync(Status.FAILURE, {"stage": "UNKNOWN", "status": "FAILURE", "error": {"type": "unknown", "msg": str(e)}})
