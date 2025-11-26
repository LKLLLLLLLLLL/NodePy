from typing import Literal, Optional

from pydantic import BaseModel

from server.models.types import ColType

FILE_FORMATS = [
    # pictures
    "png",
    "jpg",
    # documents
    "pdf",
    "word",
    "txt",
    # sheets
    "csv",
    "xlsx",
    "json",
]
FILE_FORMATS_TYPE = Literal["png", "jpg", "pdf", "word", "txt", "csv", "xlsx", "json"]

class File(BaseModel):
    """
    A abstract file class to represent files managed by FileManager.
    """

    key: str  # for minio object key
    filename: str  # original file name
    format: FILE_FORMATS_TYPE
    col_types: Optional[dict[str, ColType]] = None  # only for csv files
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
    format: FILE_FORMATS_TYPE
    size: int  # file size in bytes
    modified_at: int  # timestamp in milliseconds
    project_name: str

class UserFileList(BaseModel):
    """
    The list of files owned by a user.
    """
    user_id: int
    files: list[FileItem]
    total_size: int  # total size in bytes
    used_size: int   # used size in bytes    
