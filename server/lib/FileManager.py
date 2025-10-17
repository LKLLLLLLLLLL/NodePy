from pathlib import Path
from typing import Literal, cast
import io
from pydantic import BaseModel, model_validator
import os
import tempfile

class File(BaseModel):
    """
    A abstract file class to represent files managed by FileManager.
    """
    path: Path # a simple implementation using local path
    format: Literal["png", "jpg", "pdf", "csv"]
    
    model_config = {
        "arbitrary_types_allowed": True  # 允许非 Pydantic 类型
    }

    @model_validator(mode="after")
    def verify(self) -> "File":
        if not self.path.exists():
            raise ValueError(f"File path does not exist: {self.path}")
        if not self.path.is_file():
            raise ValueError(f"Path is not a file: {self.path}")
        suffix = self.path.suffix.lower().lstrip(".")
        if suffix not in ["png", "jpg", "pdf", "csv"]:
            raise ValueError(f"Unsupported file format: {suffix}")
        if suffix != self.format:
            raise ValueError(f"File format mismatch: expected {self.format}, got {suffix}")
        return self

    @staticmethod
    def infer_format(filename: str) -> Literal["png", "jpg", "pdf", "csv"]:
        suffix = filename.split(".")[-1].lower()
        if suffix not in ["png", "jpg", "pdf", "csv"]:
            raise ValueError(f"Unsupported file format: {suffix}")
        return cast(Literal["png", "jpg", "pdf", "csv"], suffix) # for mypy

    def get_name(self) -> str:
        return self.path.name

    def get_size(self) -> int:
        return self.path.stat().st_size

    def get_format(self) -> Literal["png", "jpg", "pdf", "csv"]:
        return self.format


class FileManager:
    """
    The unified library for managing files for nodes,
    including uploading, downloading, reading, writing, deleting files.
    Each file manager is bind to a user_id and project_id.
    Can be used in multiple containers.
    """
    
    tmp_path: Path # a simple implementation using local tmp path
    user_id: str
    project_id: str
    
    def __init__(self, user_id: str, project_id: str) -> None:
        system_tmp_path = os.environ.get("TMP_PATH", None)
        if system_tmp_path is None:
            system_tmp_path = tempfile.gettempdir()
        self.tmp_path = Path(system_tmp_path)
        self.tmp_path.mkdir(parents=True, exist_ok=True)
        if not isinstance(user_id, str) or user_id.strip() == "":
            raise ValueError("user_id cannot be empty.")
        if not isinstance(project_id, str) or project_id.strip() == "":
            raise ValueError("project_id cannot be empty.")
        self.user_id = user_id
        self.project_id = project_id

    def write(self, filename: str, content: bytes) -> File:
        """ Write content to a file for a user, return the file path """
        try:
            user_path = self.tmp_path / self.user_id
            user_path.mkdir(parents=True, exist_ok=True)
            project_path = user_path / self.project_id
            project_path.mkdir(parents=True, exist_ok=True)
            file_path = project_path / filename
            with open(file_path, "wb") as f:
                f.write(content)
            return File(path=file_path, format=File.infer_format(filename))
        except PermissionError as e:
            raise IOError(f"Permission denied when writing file {filename} for user {self.user_id} and project {self.project_id}: {e}")
        except OSError as e:
            raise IOError(f"Failed to write file {filename} for user {self.user_id} and project {self.project_id}: {e}")

    """
    For unsupport lib, you can use write method like this:
    ```py
    buffer = FileManager.get_buffer()
    somelib.save(buffer, format="png")
    buffer.seek(0)
    file = file_manager.write_from_buffer(
        user_id=user_id, 
        filename=filename,
        buffer=buffer
    )
    ```
    """
    @staticmethod
    def get_buffer() -> io.BytesIO:
        return io.BytesIO()

    def write_from_buffer(self, filename: str, buffer: io.BytesIO) -> File:
        """ Write content from a buffer to a file for a user, return the file path """
        user_path = self.tmp_path / self.user_id
        user_path.mkdir(parents=True, exist_ok=True)
        project_path = user_path / self.project_id
        project_path.mkdir(parents=True, exist_ok=True)
        file_path = project_path / filename
        with open(file_path, "wb") as f:
            f.write(buffer.getvalue())
        return File(path=file_path, format=File.infer_format(filename))

    def read(self, file: File) -> bytes:
        """Read content from a file"""
        try:
            with open(file.path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file.path}")
        except PermissionError as e:
            raise IOError(f"Permission denied when reading file {file.path} for user {self.user_id} and project {self.project_id}: {e}")