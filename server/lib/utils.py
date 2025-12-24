import base64
import hashlib
import os
import pickle
import signal
import tempfile
from typing import Any, Callable

import billiard
from billiard.queues import Queue
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import Session

from server.models.database import ProjectRecord
from server.models.project import Project, ProjUIState, ProjWorkflow


async def get_project_by_id(
    db: AsyncSession, project_id: int, user_id: int | None
) -> Project | None:
    """
    Asynchronous version of get_project_by_id.
    If user_id is None, indicates previliged operation.
    """
    project_record = await db.get(ProjectRecord, project_id)
    if project_record is None:
        return None
    editable = True
    if user_id is not None:
        if project_record.owner_id != user_id:  # type: ignore
            if not project_record.show_in_explore:  # type: ignore
                raise PermissionError("User does not have access to this project.")
            else:
                editable = False
    workflow = ProjWorkflow(**project_record.workflow)  # type: ignore
    ui_state = ProjUIState(**project_record.ui_state)  # type: ignore
    return Project(
        project_name=project_record.name,  # type: ignore
        project_id=project_record.id,  # type: ignore
        user_id=project_record.owner_id,  # type: ignore
        updated_at=int(project_record.updated_at.timestamp() * 1000),  # type: ignore
        thumb=base64.b64encode(project_record.thumb).decode("utf-8") if project_record.thumb else None,  # type: ignore
        editable=editable,
        workflow=workflow,
        ui_state=ui_state,
    )

def get_project_by_id_sync(
    db: Session, project_id: int, user_id: int | None
) -> Project | None:
    """
    Synchronous version of get_project_by_id.
    If user_id is None, indicates previliged operation.
    """
    project_record = db.get(ProjectRecord, project_id)
    if project_record is None:
        return None
    editable = True
    if user_id is not None:
        if project_record.owner_id != user_id:  # type: ignore
            if not project_record.show_in_examples:  # type: ignore
                raise PermissionError("User does not have access to this project.")
            else:
                editable = False
    workflow = ProjWorkflow(**project_record.workflow)  # type: ignore
    ui_state = ProjUIState(**project_record.ui_state)  # type: ignore
    return Project(
        project_name=project_record.name,  # type: ignore
        project_id=project_record.id,  # type: ignore
        user_id=project_record.owner_id,  # type: ignore
        updated_at=int(project_record.updated_at.timestamp() * 1000),  # type: ignore
        thumb=base64.b64encode(project_record.thumb).decode("utf-8") if project_record.thumb else None,  # type: ignore
        editable=editable,
        workflow=workflow,
        ui_state=ui_state,
    )


async def set_project_record(db: AsyncSession, project: Project, user_id: int) -> None:
    project_record = await db.get(ProjectRecord, project.project_id)
    if project_record is None:
        raise ValueError("Project not found.")
    if project_record.owner_id != user_id:  # type: ignore
        raise PermissionError("User does not have access to this project.")
    project_record.name = project.project_name  # type: ignore
    project_record.workflow = project.workflow.model_dump()  # type: ignore
    project_record.ui_state = project.ui_state.model_dump()  # type: ignore
    project_record.thumb = (  # type: ignore
        base64.b64decode(project.thumb) if project.thumb else None
    )

def set_project_record_sync(db: Session, project: Project, user_id: int) -> None:
    project_record = db.get(ProjectRecord, project.project_id)
    if project_record is None:
        raise ValueError("Project not found.")
    if project_record.owner_id != user_id:  # type: ignore
        raise PermissionError("User does not have access to this project.")
    project_record.name = project.project_name  # type: ignore
    project_record.workflow = project.workflow.model_dump()  # type: ignore
    project_record.ui_state = project.ui_state.model_dump()  # type: ignore
    project_record.thumb = (  # type: ignore
        base64.b64decode(project.thumb) if project.thumb else None
    )

class TimeoutException(Exception):
    """Exception raised when a timeout occurs"""
    pass


class InterruptedError(BaseException):
    """Exception raised when execution is interrupted by callback"""
    pass


def timeout[T](seconds: float):
    """
    A decorator to set a timeout for a function execution using SIGALRM.
    Compatible with existing SIGTERM-based revocation mechanism.
    """
    def _decorator(func: Callable[..., T]) -> Callable[..., T]:
        def _wrapper(*args, **kwargs) -> T:
            def _timeout_handler(signum, frame):
                raise TimeoutException(
                    f"Function execution timed out after {seconds} seconds."
                )

            # Save old SIGALRM handler (not SIGTERM, which is used for revocation)
            old_alarm_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.setitimer(signal.ITIMER_REAL, seconds)

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Cancel alarm and restore old handler
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old_alarm_handler)

        return _wrapper
    return _decorator


def time_check[T](seconds: float, callback: Callable[[], bool]):
    """
    A decorator to periodically check a condition during function execution using SIGALRM.
    The callback is called every 'seconds' seconds.
    Compatible with existing SIGTERM-based revocation mechanism.
    """
    def _decorator(func: Callable[..., T]) -> Callable[..., T]:
        def _wrapper(*args, **kwargs) -> T:
            result_container = {"result": None, "exception": None, "completed": False}

            def _check_handler(signum, frame):
                # Check if callback allows continuation
                try:
                    should_continue = callback()
                    if not should_continue:
                        raise InterruptedError(
                            "Execution was interrupted by the time_check callback."
                        )
                except Exception as e:
                    # Store exception to re-raise later
                    result_container["exception"] = e
                    raise e

            # Save old SIGALRM handler
            old_alarm_handler = signal.signal(signal.SIGALRM, _check_handler)
            # Set up periodic alarm
            signal.setitimer(signal.ITIMER_REAL, seconds, seconds)

            try:
                result_container["result"] = func(*args, **kwargs)
                result_container["completed"] = True
            finally:
                # Cancel alarm and restore old handler
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old_alarm_handler)

            # Re-raise any exception from callback
            if result_container["exception"] is not None:
                raise result_container["exception"]

            return result_container["result"]

        return _wrapper
    return _decorator

def _process_wrapper(queue: Queue, func: Callable, args: tuple, kwargs: dict) -> None:
    """
    Helper function to run the target function in a separate process.
    Must be defined at module level for pickling.
    """
    # Reset SIGTERM handler to default so p.terminate() kills the process immediately
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    try:
        result = func(*args, **kwargs)
        # Use temp file to avoid pipe buffer limits and deadlocks with large data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as f:
            pickle.dump(result, f)
            temp_path = f.name
        queue.put({"status": "success", "result_path": temp_path})
    except Exception as e:
        queue.put({"status": "error", "error": e})


def run_in_process[T](func: Callable[..., T]) -> Callable[..., T]:
    """
    A decorator to run a function (usually a node's process method) in a separate process.
    This allows the main thread to remain responsive to signals (like SIGTERM for revocation)
    even if the function executes blocking C-extension code (e.g., numpy, scikit-learn) that holds the GIL.
    """

    def _wrapper(*args, **kwargs) -> T:
        # This is safe on Linux/Docker
        ctx = billiard.context.ForkContext()
        queue = Queue(ctx=ctx)

        # Start the subprocess
        p = ctx.Process(target=_process_wrapper, args=(queue, func, args, kwargs))
        p.start()

        try:
            # Wait for process to finish, checking for signals periodically
            while p.is_alive():
                p.join(timeout=0.5)
        except Exception:
            # If any exception occurs (including RevokeException from signal handler),
            # terminate the child process immediately to reclaim resources.
            if p.is_alive():
                logger.warning(f"Terminating process {p.pid} due to interruption.")
                p.terminate()
                p.join()
            raise

        # Check result from queue
        if p.exitcode != 0:
            raise RuntimeError(f"Process exited with code {p.exitcode}")

        if not queue.empty():
            res = queue.get()
            if res["status"] == "error":
                raise res["error"]

            # Success, read from file
            temp_path = res["result_path"]
            try:
                with open(temp_path, "rb") as f:
                    result = pickle.load(f)
                return result
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        else:
            raise RuntimeError("Process finished but returned no result")

    return _wrapper

def safe_hash(obj: Any) -> str:
    """
    A safe hash function that handles unhashable objects.
    Optimized for speed.
    """
    def _serialize(obj: Any) -> str:
        if isinstance(obj, (str, int, float, bool, type(None))):
            return str(obj)
        elif isinstance(obj, (list, tuple)):
            return "[" + ",".join(_serialize(item) for item in obj) + "]"
        elif isinstance(obj, dict):
            # Sort keys for determinism
            return (
                "{"
                + ",".join(
                    f"{_serialize(k)}:{_serialize(v)}" for k, v in sorted(obj.items())
                )
                + "}"
            )
        elif isinstance(obj, object):
            if hasattr(obj, "fast_hash") and callable(getattr(obj, "fast_hash")):
                return str(obj.fast_hash())  # type: ignore
            elif hasattr(obj, "__hash__") and callable(getattr(obj, "__hash__")):
                return str(hash(obj))  # type: ignore
            elif hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
                logger.warning(
                    f"Object of type {type(obj)} is unhashable; using to_dict() for hashing."
                )
                return _serialize(obj.to_dict())  # type: ignore
            else:
                raise TypeError(
                    f"Object of type {type(obj)} is unhashable and has no to_dict() method."
                )
        else:
            raise TypeError(f"Object of type {type(obj)} is unhashable.")

    serialized = _serialize(obj)
    hash_value = hashlib.md5(serialized.encode("utf-8")).hexdigest()
    return hash_value
