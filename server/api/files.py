from fastapi import APIRouter, UploadFile, File as fastapiFile, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from server.models.file import File, UserFileList
from server.models.exception import InsufficientStorageError
from server.models.database import get_async_session
from server.lib.FileManager import FileManager
from typing import cast, Literal
import io
from loguru import logger

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

@router.post(
    "/upload/{project_id}",
    status_code=201,
    responses={
        201: {"description": "File uploaded successfully", "model": File},
        400: {"description": "Bad Request - invalid file or parameters"},
        403: {"description": "Forbidden - not allowed"},
        500: {"description": "Internal Server Error"},
        507: {"description": "Insufficient Storage - user storage limit exceeded"},
    },
)
async def upload_file(project_id: int, 
                      node_id: str, 
                      file: UploadFile = fastapiFile(),
                      async_db_session = Depends(get_async_session)) -> File:
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
        file_manager = FileManager(async_db_session=async_db_session)
        saved_file = await file_manager.write_async(content=content, filename=file.filename, format=format, node_id=node_id, project_id=project_id, user_id=user_id)
        return saved_file
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except InsufficientStorageError as e:
        raise HTTPException(status_code=507, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error uploading file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/list",
    responses={
        200: {"description": "List of files for the user", "model": UserFileList},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)
async def list_files(async_db_session=Depends(get_async_session)) -> UserFileList:
    logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    user_id = 1  # for debug
    try:
        file_manager = FileManager(async_db_session=async_db_session)
        user_file_list = await file_manager.list_file_async(user_id=user_id)
        return user_file_list
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error listing files for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/{key}",
    responses={
        200: {
            "description": "Binary file content",
            "content": {
                "application/octet-stream": {"schema": {"type": "string", "format": "binary"}},
            },
        },
        403: {"description": "Forbidden - not allowed to access this file"},
        404: {"description": "File not found"},
        500: {"description": "Internal Server Error"},
    },
)
async def get_file_content(key: str, async_db_session = Depends(get_async_session)) -> StreamingResponse:
    """
    Get the content of a file by its key and project id.
    The project id is used to verify the access permission.
    
    **important: if user want to re upload a file, you need to delete the old file first,
    otherwise the file space may not be released.**
    """
    user_id = 1  # for debug
    try:
        file_manager = FileManager(async_db_session=async_db_session)
        file = await file_manager.get_file_by_key_async(key=key)
        content = await file_manager.read_async(file=file, user_id=user_id)
        media_type = MIME_TYPES.get(file.format, "application/octet-stream")
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={key}.{file.format}"
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving file content for key {key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class DeleteResponse(BaseModel):
    status: str

@router.delete(
    "/{key}",
    responses={
        200: {"description": "File deleted successfully", "content": {"application/json": {"example": {"status": "success"}}}},
        403: {"description": "Forbidden - not allowed to access this file"},
        404: {"description": "File not found"},
        500: {"description": "Internal Server Error"},
    },
)
async def delete_file(key: str, async_db_session = Depends(get_async_session)) -> DeleteResponse:
    """
    Delete a file by its key and project id.
    The project id is used to verify the access permission.
    """
    user_id = 1  # for debug
    try:
        file_manager = FileManager(async_db_session=async_db_session)
        file = await file_manager.get_file_by_key_async(key=key)
        await file_manager.delete_async(file=file, user_id=user_id)
        return DeleteResponse(status="success")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting file with key {key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
