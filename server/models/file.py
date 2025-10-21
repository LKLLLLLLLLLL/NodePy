from typing import Literal
from pydantic import BaseModel

class File(BaseModel):
    """
    A abstract file class to represent files managed by FileManager.
    """

    key: str  # for minio object key
    filename: str  # original file name
    format: Literal["png", "jpg", "pdf", "csv"]
    size: int  # file size in bytes

    def to_dict(self) -> dict[str, str]:
        return super().model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "File":
        return cls.model_validate(data)

class FileItem(BaseModel):
    """
    The file item showed in the file list.
    """
    key: str
    filename: str
    format: Literal["png", "jpg", "pdf", "csv"]
    size: int  # file size in bytes
    uploaded_at: str  # ISO format datetime string
    project_name: str

class UserFileList(BaseModel):
    """
    The list of files owned by a user.
    """
    user_id: int
    files: list[FileItem]
    total_size: int  # total size in bytes
    used_size: int   # used size in bytes    
