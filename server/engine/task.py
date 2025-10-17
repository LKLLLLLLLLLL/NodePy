from ..celery import celery_app
from ..lib.FileManager import FileManager
from ..lib.CacheManager import CacheManager
from .graph import GraphRequestModel, NodeGraph
from .nodes.Exceptions import NodeParameterError, NodeValidationError, NodeExecutionError
from ..app.services.task_updater import TaskUpdater
from typing import Any
import redis
import os
import logging

logger = logging.getLogger(__name__)

def get_redis_connection() -> redis.Redis:
    """Creates a Redis connection for the task."""
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    return redis.from_url(redis_url, decode_responses=True)

@celery_app.task(bind=True)
def execute_nodes_task(self, node_graph: dict[str, Any], project_id: str, user_id: str):
    """
    Celery task to execute a node graph with real-time updates via Redis Pub/Sub.
    Uses a TaskUpdater to handle state reporting.
    """
    redis_conn = get_redis_connection()
    updater = TaskUpdater(self, redis_conn)
    
    try:
        # 1. Validate data model
        graph = None
        try:
            graph_request = GraphRequestModel(**node_graph)
            file_manager = FileManager(user_id=user_id, project_id=project_id)
            cache_manager = CacheManager(user_id=user_id, project_id=project_id)
            graph = NodeGraph(file_manager=file_manager, cache_manager=cache_manager, request=graph_request)
            updater.update(state="PROGRESS", meta={"stage": "VALIDATION", "status": "SUCCESS"})
        except Exception as e:
            updater.set_final_state(state="FAILURE", meta={"stage": "VALIDATION", "status": "FAILURE", "error": {"type": "unknown", "msg": str(e)}})
            return

        # 2. Construct nodes
        try:
            assert graph is not None
            graph.construct_nodes()
            updater.update(state="PROGRESS", meta={"stage": "CONSTRUCTION", "status": "SUCCESS"})
        except NodeParameterError as e:
            updater.set_final_state(state="FAILURE", meta={"stage": "CONSTRUCTION", "status": "FAILURE", "error": {"type": "NodeParameterError", "node_id": e.node_id, "msg": e.err_msg}})
            return
        except Exception as e:
            updater.set_final_state(state="FAILURE", meta={"stage": "CONSTRUCTION", "status": "FAILURE", "error": {"type": "unknown", "msg": str(e)}})
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
                updater.update(state="PROGRESS", meta=meta)
            
            graph.static_analyse(callback=anl_reporter)
            updater.update(state="PROGRESS", meta={"stage": "STATIC_ANALYSIS", "status": "SUCCESS"})
        except NodeValidationError as e:
            updater.set_final_state(state="FAILURE", meta={"stage": "STATIC_ANALYSIS", "status": "FAILURE", "error": {"type": "NodeValidationError", "node_id": e.node_id, "node_input": e.err_input, "msg": e.err_msg}})
            return
        except Exception as e:
            updater.set_final_state(state="FAILURE", meta={"stage": "STATIC_ANALYSIS", "status": "FAILURE", "error": {"type": "unknown", "msg": str(e)}})
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
                updater.update(state="PROGRESS", meta=meta)
                
            graph.execute(callback=exec_reporter)
            updater.set_final_state(state="SUCCESS", meta={"stage": "EXECUTION", "status": "SUCCESS"})
        except NodeExecutionError as e:
            updater.set_final_state(state="FAILURE", meta={"stage": "EXECUTION", "status": "FAILURE", "error": {"type": "NodeExecutionError", "node_id": e.node_id, "msg": e.err_msg}})
            return
        except Exception as e:
            updater.set_final_state(state="FAILURE", meta={"stage": "EXECUTION", "status": "FAILURE", "error": {"type": "unknown", "msg": str(e)}})
            return
            
    finally:
        redis_conn.close()
