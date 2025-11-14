from sqlalchemy.ext.asyncio import AsyncSession
from server.models.project import Project, ProjUIState, ProjWorkflow
from server.models.database import ProjectRecord
import base64
from typing import Any, Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json
import hashlib


async def get_project_by_id(
    db: AsyncSession, project_id: int, user_id: int
) -> Project | None:
    project_record = await db.get(ProjectRecord, project_id)
    if project_record is None:
        return None
    if project_record.owner_id != user_id:  # type: ignore
        raise PermissionError("User does not have access to this project.")
    workflow = ProjWorkflow(**project_record.workflow)  # type: ignore
    ui_state = ProjUIState(**project_record.ui_state)  # type: ignore
    return Project(
        project_name=project_record.name,  # type: ignore
        project_id=project_record.id,  # type: ignore
        user_id=project_record.owner_id,  # type: ignore
        updated_at=int(project_record.updated_at.timestamp() * 1000),  # type: ignore
        thumb=base64.b64encode(project_record.thumb).decode("utf-8") if project_record.thumb else None,  # type: ignore
        workflow=workflow,
        ui_state=ui_state,
    )


async def set_project_record(db: AsyncSession, project: Project, user_id: int) -> None:
    project_record = await db.get(ProjectRecord, project.project_id)
    if project_record is None:
        raise ValueError("Project not found.")
    if project_record.owner_id != user_id:  # type: ignore
        raise PermissionError("User does not have access to this project.")
    try:
        project_record.name = project.project_name  # type: ignore
        project_record.workflow = project.workflow.model_dump()  # type: ignore
        project_record.ui_state = project.ui_state.model_dump()  # type: ignore
        project_record.thumb = (  # type: ignore
            base64.b64decode(project.thumb) if project.thumb else None
        )
        await db.commit()
    except Exception:
        await db.rollback()
        raise

def timeout(seconds: float):
    """
    A decorator to set a timeout for a function execution.
    If the function raise error, timeout will raise the error as well.
    """

    def _decorator(func: Callable):
        def _wrapper(*args, **kwargs) -> tuple[bool, Any]:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    result = future.result(timeout=seconds)
                    return True, result
                except TimeoutError:
                    return False, None
        return _wrapper
    return _decorator

def safe_hash(obj: Any) -> str:
    """
    A safe hash function that handles unhashable objects.
    For unhashable objects, if it has write the to_dict() method, use its dict representation for hashing.
    """
    if isinstance(obj, (str, int, float, bool, type(None))):
        obj_bytes = json.dumps(obj, sort_keys=True).encode('utf-8')
        return hashlib.sha256(obj_bytes).hexdigest()
    elif isinstance(obj, dict):
        hash_dict = {}
        for k, v in obj.items():
            hash_dict[safe_hash(k)] = safe_hash(v)
        obj_bytes = json.dumps(hash_dict, sort_keys=True).encode('utf-8')
        return hashlib.sha256(obj_bytes).hexdigest()
    elif isinstance(obj, object): 
        if hasattr(obj, "__hash__") and callable(getattr(obj, "__hash__")):
            return hashlib.sha256(repr(obj).encode('utf-8')).hexdigest()
        elif hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
            return safe_hash(obj.to_dict()) # type: ignore
        else:
            raise TypeError(f"Object of type {type(obj)} is unhashable and has no to_dict() method.")
    elif isinstance(obj, (list, tuple)):
        hash_list = [safe_hash(item) for item in obj]
        obj_bytes = json.dumps(hash_list).encode('utf-8')
        return hashlib.sha256(obj_bytes).hexdigest()
    else:
        raise TypeError(f"Object of type {type(obj)} is unhashable.")