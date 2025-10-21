from typing import Literal, cast
import io
import os
from minio import Minio, S3Error
from uuid import uuid4
from ..models.database import File as DBFile, User, get_session, Project
from server.models.file import File, FileItem, UserFileList
import datetime
from server.models.exception import InsufficientStorageError

class FileManager:
    """
    The unified library for managing files for nodes,
    including uploading, downloading, reading, writing, deleting files.
    Each file manager is bind to a user_id and project_id.
    Can be used in multiple containers.
    """
    def __init__(self, user_id: int, project_id: int) -> None:
        self.minio_client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT", ""),
            access_key=os.getenv("MINIO_ROOT_USER", ""),
            secret_key=os.getenv("MINIO_ROOT_PASSWORD", ""),
            secure=False  # MinIO in Docker is HTTP, not HTTPS
        )
        self.db_client = get_session()
        self.bucket = "nodepy-files"
        self.user_id = user_id
        self.project_id = project_id
        # Ensure bucket exists
        if not self.minio_client.bucket_exists(self.bucket):
            self.minio_client.make_bucket(self.bucket)

    def __del__(self):
        if hasattr(self, "db_client"):
            self.db_client.close()

    def get_file_by_key(self, key: str) -> File:
        """ Get a File object by its key """
        db_file = self.db_client.query(DBFile).filter(DBFile.file_key == key).first()
        if not db_file:
            raise IOError("File record not found in database")
        if db_file.user_id != self.user_id or db_file.project_id != self.project_id: # type: ignore
            raise PermissionError("Permission denied to access this file")
        return File(
            key=db_file.file_key,
            filename=db_file.filename,
            format=cast(Literal["png", "jpg", "pdf", "csv"], db_file.format),
            size=db_file.file_size, # type: ignore
            uploaded_at=db_file.upload_time # type: ignore
        )
    def _cal_user_occupy(self, user_id: int) -> int:
        """ Calculate the total file occupy for a user """
        total = self.db_client.query(DBFile).with_entities(
            DBFile.file_size
        ).filter(
            DBFile.user_id == user_id
        ).all()
        return sum([size for (size,) in total])  # type: ignore

    """
    For unsupport lib, you can use write method like this:
    ```py
    buffer = FileManager.get_buffer()
    somelib.save(buffer, format="png")
    file = file_manager.write(
        content=buffer,
        filename="plot.png",
        format="png"
    )
    ```
    """

    @staticmethod
    def get_buffer() -> io.BytesIO:
        return io.BytesIO()

    def write(self, filename: str, content: bytes | io.BytesIO, format: Literal["png", "jpg", "pdf", "csv"]) -> File:
        """ Write content to a file for a user, return the file path """
        if isinstance(content, io.BytesIO):
            content.seek(0)
            content = content.getvalue()
        key = uuid4().hex
        try:
            user = self.db_client.query(User).filter(User.id == self.user_id).first()
            if not user:
                raise ValueError("User not found")
            file_occupy = self._cal_user_occupy(self.user_id)
            if file_occupy + len(content) > user.file_total_space: # type: ignore
                raise InsufficientStorageError("User storage limit exceeded")
            self.minio_client.put_object(
                bucket_name=self.bucket,
                object_name=key,
                data=io.BytesIO(content),
                length=len(content),
                metadata={"project_id": str(self.project_id), "user_id": str(self.user_id), "filename": filename}
            )
            file = DBFile(
                file_key=key,
                filename=filename,
                format=format,
                user_id=self.user_id,
                project_id=self.project_id,
                file_size=len(content),
                upload_time=datetime.datetime.now(datetime.timezone.utc).isoformat()
            )
            self.db_client.add(file)
            self.db_client.commit()
        except S3Error as e:
            self.db_client.rollback()
            raise IOError(f"Failed to upload file to MinIO: {e}")
        except InsufficientStorageError as e:
            raise e
        except Exception as e:
            self.db_client.rollback()
            try:
                self.minio_client.remove_object(
                    bucket_name=self.bucket,
                    object_name=key
                )
            except Exception:
                pass
            raise IOError(f"Failed to write file: {e}")
        return File(key=key, filename=filename, format=format, size=len(content))
    
    def delete(self, file: File) -> None:
        """ Delete a file """
        # validate file ownership
        db_file = self.db_client.query(DBFile).filter(DBFile.file_key == file.key).first()
        if not db_file:
            raise IOError("File record not found in database")
        if db_file.user_id != self.user_id or db_file.project_id != self.project_id: # type: ignore
            raise PermissionError("Permission denied to access this file")
        try:
            self.minio_client.remove_object(
                bucket_name=self.bucket,
                object_name=file.key
            )
            db_file = self.db_client.query(DBFile).filter(DBFile.file_key == file.key).first()
            if not db_file:
                raise IOError("File record not found in database")
            user = self.db_client.query(User).filter(User.id == db_file.user_id).first()
            if not user:
                raise IOError("User not found in database")
            self.db_client.delete(db_file)
            self.db_client.commit()
        except S3Error as e:
            self.db_client.rollback()
            raise IOError(f"Failed to delete file from MinIO: {e}")
        except Exception as e:
            self.db_client.rollback()
            raise IOError(f"Failed to delete file record from database: {e}")

    def read(self, file: File) -> bytes:
        """Read content from a file"""
        db_file = self.db_client.query(DBFile).filter(DBFile.file_key == file.key).first()
        if not db_file:
            raise ValueError("File record not found in database")
        if db_file.user_id != self.user_id or db_file.project_id != self.project_id: # type: ignore
            raise PermissionError("Permission denied to access this file")
        try:
            response = self.minio_client.get_object(
                bucket_name=self.bucket,
                object_name=file.key
            )
            data = response.read()
            return data
        except S3Error as e:
            raise IOError(f"Failed to read file from MinIO: {e}")
    
    def list_file(self) -> UserFileList:
        """ List all files owned by the user in the project """
        try:
            db_files = self.db_client.query(DBFile).filter(
                DBFile.user_id == self.user_id,
                DBFile.project_id == self.project_id
            ).all()
            user = self.db_client.query(User).filter(User.id == self.user_id).first()
            if not user:
                raise ValueError("User not found in database")
            file_items = []
            for db_file in db_files:
                # query project name
                project = self.db_client.query(Project).filter(Project.id == db_file.project_id).first()
                project_name = project.name if project else ""
                file_items.append(FileItem(
                    key=db_file.file_key, # type: ignore
                    filename=db_file.filename, # type: ignore
                    format=cast(Literal["png", "jpg", "pdf", "csv"], db_file.format),
                    size=db_file.file_size, # type: ignore
                    uploaded_at=db_file.upload_time, # type: ignore
                    project_name=project_name # type: ignore
                ))
            return UserFileList(
                user_id=self.user_id,
                files=file_items,
                total_size=user.file_total_space, # type: ignore
                used_size=self._cal_user_occupy(self.user_id)
            )
        except Exception as e:
            raise IOError(f"Failed to list files: {e}")

