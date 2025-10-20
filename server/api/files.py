from fastapi import APIRouter, UploadFile, File as fastapiFile, HTTPException
from fastapi.responses import StreamingResponse
from server.models.file import File, UserFileList
from ..lib.FileManager import FileManager
from typing import cast, Literal
import io

"""
Apis for file operations.
"""
router = APIRouter()

MIME_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "pdf": "application/pdf",
    "csv": "text/csv",
}

@router.post("/files/upload")
async def upload_file(project_id: int, file: UploadFile = fastapiFile()) -> File:
    """
    Upload a file to a project. Return the saved file info.
    """
    content = await file.read()
    # validate file format
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Filename is required")
    if not file.filename.endswith(('.png', '.jpg', '.pdf', '.csv')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    format = cast(Literal['png', 'jpg', 'pdf', 'csv'], file.filename.split('.')[-1])
    user_id = 1  # for debug
    try:
        file_manager = FileManager(user_id=user_id, project_id=project_id)
        saved_file = file_manager.write(content=content, format=format)
        return saved_file
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{key}")
async def get_file_content(project_id: int, key: str) -> StreamingResponse:
    """
    Get the content of a file by its key and project id.
    The project id is used to verify the access permission.
    
    **important: if user want to re upload a file, you need to delete the old file first,
    otherwise the file space may not be released.**
    """
    user_id = 1  # for debug
    try:
        file_manager = FileManager(user_id=user_id, project_id=project_id)
        file = file_manager.get_file_by_key(key=key)
        content = file_manager.read(file=file)
        media_type = MIME_TYPES.get(file.format, "application/octet-stream")
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={key}.{file.format}"
            },
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{key}")
async def delete_file(project_id: int, key: str) -> dict[str, str]:
    """
    Delete a file by its key and project id.
    The project id is used to verify the access permission.
    """
    user_id = 1  # for debug
    try:
        file_manager = FileManager(user_id=user_id, project_id=project_id)
        file = file_manager.get_file_by_key(key=key)
        file_manager.delete(file=file)
        return {"status": "success"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/list")
async def list_files(project_id: int) -> UserFileList:
    user_id = 1  # for debug
    try:
        file_manager = FileManager(user_id=user_id, project_id=project_id)
        user_file_list = file_manager.list_file()
        return user_file_list
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))