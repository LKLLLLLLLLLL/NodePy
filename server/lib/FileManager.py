from typing import Literal, cast
import io
import os
from minio import Minio, S3Error
from uuid import uuid4
from ..models.database import File as DBFile, User, get_session, Project
from server.models.file import File, FileItem, UserFileList
from server.celery import celery_app
import datetime
from server.models.exception import InsufficientStorageError
import json

class FileManager:
    """
    The unified library for managing files for nodes,
    including uploading, downloading, reading, writing, deleting files.
    Each file manager is bind to a user_id and project_id.
    Can be used in multiple containers.

    When project_id is provided, all operations including writing are enabled.
    When project_id is None, only read, delete, and list operations are permitted.
    """
    def __init__(self) -> None:
        self.minio_client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT", ""),
            access_key=os.getenv("MINIO_ROOT_USER", ""),
            secret_key=os.getenv("MINIO_ROOT_PASSWORD", ""),
            secure=False  # MinIO in Docker is HTTP, not HTTPS
        )
        self.db_client = next(get_session())
        self.bucket = "nodepy-files"
        # Ensure bucket exists
        if not self.minio_client.bucket_exists(self.bucket):
            self.minio_client.make_bucket(self.bucket)

    def get_file_by_key(self, key: str) -> File:
        """ Get a File object by its key """
        db_file = self.db_client.query(DBFile).filter(DBFile.file_key == key).first()
        if not db_file:
            raise IOError("File record not found in database")
        if db_file.user_id != self.user_id: # type: ignore
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

    def write(self, filename: str, content: bytes | io.BytesIO, format: Literal["png", "jpg", "pdf", "csv"], node_id: str, project_id: int, user_id: int) -> File:
        """ Write content to a file for a user, return the file path """
        if isinstance(content, io.BytesIO):
            content.seek(0)
            content = content.getvalue()
        key = uuid4().hex
        existing_file = self.db_client.query(DBFile).filter(DBFile.project_id == project_id and DBFile.node_id == node_id).first()
        try:
            # check storage limit
            user = self.db_client.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            file_occupy = self._cal_user_occupy(user_id)
            if file_occupy + len(content) > user.file_total_space: # type: ignore
                raise InsufficientStorageError("User storage limit exceeded")
            # upload to MinIO
            self.minio_client.put_object(
                bucket_name=self.bucket,
                object_name=key,
                data=io.BytesIO(content),
                length=len(content),
                metadata={"project_id": str(project_id), "user_id": str(user_id), "filename": filename, "node_id": node_id}
            )
            # record in database
            if existing_file:
                # replace existing file
                old_key = existing_file.file_key
                existing_file.file_key = key    # type: ignore
                existing_file.filename = filename  # type: ignore
                existing_file.format = format  # type: ignore
                existing_file.user_id = user_id  # type: ignore
                existing_file.project_id = project_id  # type: ignore
                existing_file.node_id = node_id # type: ignore
                existing_file.file_size = len(content) # type: ignore
                existing_file.upload_time = datetime.datetime.now(datetime.timezone.utc).isoformat()  # type: ignore
                try:
                    self.minio_client.remove_object(
                        bucket_name=self.bucket,
                        object_name=old_key # type: ignore
                    )
                except Exception:
                    pass
            else:
                file = DBFile(
                    file_key=key,
                    filename=filename,
                    format=format,
                    user_id=user_id,
                    project_id=project_id,
                    node_id=node_id,
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
    
    def delete(self, file: File, user_id: int | None) -> None:
        """ Delete a file. If user_id is None, means admin operation """
        # validate file ownership
        db_file = self.db_client.query(DBFile).filter(DBFile.file_key == file.key).first()
        if not db_file:
            raise IOError("File record not found in database")
        if user_id and db_file.user_id != user_id: # type: ignore
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

    def read(self, file: File, user_id: int | None) -> bytes:
        """Read content from a file"""
        db_file = self.db_client.query(DBFile).filter(DBFile.file_key == file.key).first()
        if not db_file:
            raise ValueError("File record not found in database")
        if user_id and db_file.user_id != user_id: # type: ignore
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
    
    def list_file(self, user_id: int) -> UserFileList:
        """ List all files owned by the user in the project """
        try:
            db_files = self.db_client.query(DBFile).filter(
                DBFile.user_id == user_id,
            ).all()
            user = self.db_client.query(User).filter(User.id == user_id).first()
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
                user_id=user_id,
                files=file_items,
                total_size=user.file_total_space, # type: ignore
                used_size=self._cal_user_occupy(user_id)
            )
        except Exception as e:
            raise IOError(f"Failed to list files: {e}")

@celery_app.task
def cleanup_orphan_files_task():
    """
    A periodic Celery task to clean up orphan files in MinIO that are not referenced in the database.
    """
    db_client = next(get_session())
    file_manager = FileManager()
    minio_client = Minio(
        endpoint=os.getenv("MINIO_ENDPOINT", ""),
        access_key=os.getenv("MINIO_ROOT_USER", ""),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", ""),
        secure=False  # MinIO in Docker is HTTP, not HTTPS
    )
    # step 1: delete files for invalid node_id
    try:
        print("Starting cleanup of orphan files...")
        
        # 1. get all existing node_id from projects
        all_projects = db_client.query(Project).all()
        valid_node_ids = set()
        for project in all_projects:
            if project.graph: # type: ignore
                graph_data = project.graph
                if isinstance(graph_data, str):
                    graph_data = json.loads(graph_data)
                for node in graph_data.get("nodes", []):
                    node_id = node.get("id")
                    if node_id:
                        valid_node_ids.add((project.id, node_id))
        
        # 2. list all files keys from db
        all_files = db_client.query(DBFile).all()
        
        orphan_files = []
        for db_file in all_files:
            if (db_file.project_id, db_file.node_id) not in valid_node_ids:
                orphan_files.append(db_file)
        if not orphan_files:
            print("No orphan files found.")
            return
        
        # 3. delete orphan files from MinIO and database
        for file_record in orphan_files:
            try:
                file_to_delete = file_manager.get_file_by_key(file_record.file_key)
                file_manager.delete(file_to_delete, user_id=None)  # Admin operation
            except Exception as e:
                print(f"Failed to delete orphan file {file_record.file_key}: {e}") # type: ignore
        db_client.commit()
        
        print(f"Cleanup completed. Deleted {len(orphan_files)} orphan files.")
    except Exception as e:
        print(f"Failed to clean up orphan files: {e}")

    # step 2: delete files in MinIO not in database
    try:
        objects = file_manager.minio_client.list_objects(bucket_name=file_manager.bucket, recursive=True)
        db_file_keys = set([db_file.file_key for db_file in db_client.query(DBFile.file_key).all()])
        for obj in objects:
            if obj.object_name not in db_file_keys:
                assert isinstance(obj.object_name, str)
                try:
                    minio_client.remove_object(
                        bucket_name=file_manager.bucket,
                        object_name=obj.object_name
                    )
                except Exception as e:
                    print(f"Failed to delete orphan MinIO file {obj.object_name}: {e}")
        print("MinIO orphan file cleanup completed.") 
    finally:
        db_client.close()