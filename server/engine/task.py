import asyncio
import signal
import threading
from typing import Any, Literal

from celery.exceptions import SoftTimeLimitExceeded
from celery.result import AsyncResult
from loguru import logger

from server.celery import celery_app
from server.lib.CacheManager import CacheManager
from server.lib.FileManager import FileManager
from server.lib.ProjectLock import ProjectLock
from server.lib.StreamQueue import Status, StreamQueue
from server.lib.utils import get_project_by_id_sync, set_project_record_sync
from server.models.data import Data
from server.models.database import DatabaseTransaction, NodeOutputRecord
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.project import (
    DataRef,
    ProjNodeError,
    ProjWorkflow,
    ProjWorkflowPatch,
)
from server.models.project_topology import WorkflowTopology

from .executer import ProjectExecutor


class RevokeException(Exception):
    pass

# Thread-safe flag for revocation
_revoke_flags = {}
_revoke_lock = threading.Lock()

@celery_app.task(
    bind=True,
    time_limit=10*60,  # 10 minutes
    soft_time_limit=9*60,  # 9 minutes
)
def execute_project_task(self, project_id: int, user_id: int):
    """
    Celery task to execute a node graph with real-time updates via Redis Streams.
    Uses StreamQueue (sync version) to handle state reporting.
    """
    logger.debug(f"Task start: {self.request.id}")
    task_id = self.request.id

    def _signal_handler(signum, frame):
        """Signal handler for SIGTERM"""
        logger.debug(f"Received signal {signum} for task {task_id}")
        with _revoke_lock:
            _revoke_flags[task_id] = True
    # Set up signal handler for graceful termination
    signal.signal(signal.SIGTERM, _signal_handler)
    # Initialize revoke flag for this task
    with _revoke_lock:
        _revoke_flags[task_id] = False
    def check_revoke() -> None:
        """Check if task has been revoked using multiple methods"""
        with _revoke_lock:
            if _revoke_flags.get(task_id, False):
                logger.debug(f"Task {task_id} revoked via signal")
                raise RevokeException()

    # lock to prevent concurrent runs on the same project
    with (ProjectLock(project_id=project_id, max_block_time=30.0, identity=task_id, scope="workflow"), 
          StreamQueue(task_id) as queue, 
          DatabaseTransaction() as db_client
        ):
        # 0. get old workflow from db
        project = get_project_by_id_sync(db_client, project_id, user_id)
        if project is None:
            raise ValueError("Project not found.")
        workflow: ProjWorkflow = project.workflow
        topo_graph: WorkflowTopology = project.to_topo()
        
        # 1. cleanup 
        # remove all error messages from previous runs
        patches = workflow.generate_del_error_patches()
        for patch in patches:
            workflow.apply_patch(patch)
            queue.push_message_sync(
                Status.IN_PROGRESS,
                {"stage": "CLEANUP",
                    "status": "IN_PROGRESS",
                    "patch": [patch.model_dump()]
                }
            )
        # remove all schemas from previous runs
        patches = workflow.generate_del_schema_data_patches()
        for patch in patches:
            workflow.apply_patch(patch)
            queue.push_message_sync(
                Status.IN_PROGRESS,
                {"stage": "CLEANUP",
                    "status": "IN_PROGRESS",
                    "patch": [patch.model_dump()]
                }
            )
        # remove all running times from previous runs
        patches = workflow.generate_del_runningtime_patches()
        for patch in patches:
            workflow.apply_patch(patch)
            queue.push_message_sync(
                Status.IN_PROGRESS,
                {"stage": "CLEANUP",
                    "status": "IN_PROGRESS",
                    "patch": [patch.model_dump()]
                }
            )

        try:
            graph = None
            # 2. Validate data model
            try:
                file_manager = FileManager(async_db_session=None)  # sync version
                cache_manager = CacheManager()
                graph = ProjectExecutor(file_manager=file_manager, cache_manager=cache_manager, topology=topo_graph, user_id=user_id)
                queue.push_message_sync(
                    Status.IN_PROGRESS, 
                    {"stage": "VALIDATION", "status": "SUCCESS"}
                )
            except Exception as e:
                patch = ProjWorkflowPatch(
                            key=["error_message"], 
                            value="Validation Error: " + str(e)
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
                return  # stop execution if validation failed
            # 3. Construct nodes
            assert graph is not None
            has_exception = False
            def construct_reporter(node_id: str, status: Literal["success", "error"], exception: Exception | None) -> bool:
                check_revoke()
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
                    patch = ProjWorkflowPatch(
                        key=["nodes", node_index, "error"],
                        value=ProjNodeError(
                            type="param", params=e.err_param_keys, inputs=None, message=e.err_msgs
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
                    logger.exception(f"Unexpected error during node construction: {e}")
                    has_exception = True
                    patch = ProjWorkflowPatch(
                        key=["error_message"],
                        value="Construction Error: " + str(e)
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
                # cleanup all data output (schemas have been cleaned in step 1)
                patches = workflow.generate_del_data_patches()
                for patch in patches:
                    workflow.apply_patch(patch)
                    queue.push_message_sync(
                        Status.IN_PROGRESS,
                        {"stage": "CONSTRUCTION",
                            "status": "IN_PROGRESS",
                            "patch": [patch.model_dump()]
                        }
                    )
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

            # 4. Static analysis
            assert graph is not None
            def anl_reporter(node_id: str, status: Literal["success", "error"], result: dict[str, Any] | Exception) -> bool:
                check_revoke()
                nonlocal has_exception
                if status == "success":
                    assert isinstance(result, dict)
                    output_schemas = result
                    node_index = topo_graph.get_index_by_node_id(node_id)
                    assert node_index is not None
                    patch = ProjWorkflowPatch(
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
                    patch = ProjWorkflowPatch(
                                key=["nodes", node_index, "error"],
                                value=ProjNodeError(
                                    type="validation", params=None, inputs=e.err_inputs, message=e.err_msgs
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
                    logger.exception(f"Unexpected error during static analysis: {e}")
                    has_exception = True
                    patch = ProjWorkflowPatch(
                                key=["error_message"],
                                value="Static Analysis Error: " + str(e)
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
                # cleanup all data output (schemas have been cleaned in step 1)
                patches = workflow.generate_del_data_patches()
                for patch in patches:
                    workflow.apply_patch(patch)
                    queue.push_message_sync(
                        Status.IN_PROGRESS,
                        {"stage": "STATIC_ANALYSIS",
                            "status": "IN_PROGRESS",
                            "patch": [patch.model_dump()]
                        }
                    )
                queue.push_message_sync(
                    Status.FAILURE, 
                    {"stage": "STATIC_ANALYSIS", "status": "FAILURE"}
                )
                return  # stop execution if static analysis failed
            else:
                queue.push_message_sync(Status.IN_PROGRESS, {"stage": "STATIC_ANALYSIS", "status": "SUCCESS"})

            # 5. Execute graph
            assert graph is not None
            def exec_before_reporter(node_id: str) -> None: # for timer in frontend
                check_revoke()
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
                    data_patch = ProjWorkflowPatch(
                        key = ["nodes", node_index, "data_out"],
                        value = data_zips
                    )
                    time_patch = ProjWorkflowPatch(
                        key = ["nodes", node_index, "runningtime"],
                        value = running_time
                    )
                    meta = {
                        "stage": "EXECUTION",
                        "status": "IN_PROGRESS",
                        "node_id": node_id,
                        "timer": "stop",
                        "patch": [data_patch.model_dump(), time_patch.model_dump()], 
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
                    patch = ProjWorkflowPatch(
                        key=["nodes", node_index, "error"],
                        value=ProjNodeError(
                            type="execution", params=None, inputs=None, message=e.err_msg
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
                    logger.exception(f"Unexpected error during node execution: {e}")
                    has_exception = True
                    patch = ProjWorkflowPatch(
                        key=["error_message"],
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
                # cleanup unreached nodes' data output
                unreached_node_ids = getattr(graph, "_last_unreached_node_ids", [])
                patches = workflow.generate_del_data_patches(node_indexs=unreached_node_ids)
                for patch in patches:
                    workflow.apply_patch(patch)
                    queue.push_message_sync(
                        Status.IN_PROGRESS,
                        {"stage": "EXECUTION",
                            "status": "IN_PROGRESS",
                            "patch": [patch.model_dump()]
                        }
                    )
                queue.push_message_sync(
                    Status.FAILURE, 
                    {"stage": "EXECUTION", "status": "FAILURE"}
                )
                return  # stop execution if execution failed
            else:
                queue.push_message_sync(Status.SUCCESS, {"stage": "EXECUTION", "status": "SUCCESS"})

            # 6. Finalize and save workflow
            set_project_record_sync(db_client, project, user_id)
            db_client.commit()
            logger.debug(f"Task {task_id} completed successfully")

        except SoftTimeLimitExceeded:
            logger.exception("Task time limit exceeded")
            patch = ProjWorkflowPatch(
                key=["error_message"],
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
        except RevokeException:
            logger.debug("Task revoked")
            patch = ProjWorkflowPatch(
                key=["error_message"],
                value="Error: Task was revoked."
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
            patch = ProjWorkflowPatch(
                key=["error_message"],
                value="Error: " + str(e)
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
            logger.debug(f"Task {task_id} finalized")
            set_project_record_sync(db_client, project, user_id)
            if db_client.is_active:
                db_client.commit()  # Commit the error state to the DB

async def revoke_project_task(task_id: str, timeout: float = 30) -> None:
    """
    Wrapper to revoke a task only it has been started.
    """
    total_wait = 0.0
    while total_wait < timeout:
        task_result = AsyncResult(task_id, app=celery_app)
        if task_result.state != "PENDING":
            celery_app.control.revoke(
                task_id, terminate=True, signal=signal.SIGTERM
            )
            logger.debug(f"Task {task_id} terminated")
            break
        else:
            await asyncio.sleep(0.5)
            total_wait += 0.5