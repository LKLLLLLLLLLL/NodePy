import asyncio
import datetime
import io
import json
import os
from typing import Literal, cast
from uuid import uuid4

import pandas
from loguru import logger
from minio import Minio, S3Error
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.celery import celery_app
from server.models.database import FileRecord, ProjectRecord, UserRecord, get_session
from server.models.exception import InsufficientStorageError
from server.models.file import File, FileItem, UserFileList
from server.models.schema import ColType


class FileManager:
    """
    The unified library for managing files for nodes,
    including uploading, downloading, reading, writing, deleting files.
    Each file manager is bind to a user_id and project_id.
    Can be used in multiple containers.

    When project_id is provided, all operations including writing are enabled.
    When project_id is None, only read, delete, and list operations are permitted.
    """
    def __init__(self, async_db_session: AsyncSession | None) -> None:
        self.minio_client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT", ""),
            access_key=os.getenv("MINIO_ROOT_USER", ""),
            secret_key=os.getenv("MINIO_ROOT_PASSWORD", ""),
            secure=False  # MinIO in Docker is HTTP, not HTTPS
        )
        if async_db_session:
            self.db_client = None
            self.async_db_client = async_db_session
        else:
            self.db_client = next(get_session())
            self.async_db_client = None
        self.bucket = "nodepy-files"
        # Ensure bucket exists
        if not self.minio_client.bucket_exists(self.bucket):
            self.minio_client.make_bucket(self.bucket)

    def get_file_by_key_sync(self, key: str) -> File:
        """ Get a File object by its key """
        if not self.db_client:
            raise AssertionError("Synchronous DB client is not initialized")
        db_file = self.db_client.query(FileRecord).filter(FileRecord.file_key == key).first()
        if not db_file:
            raise ValueError("File record not found in database")
        return File(
            key=db_file.file_key, # type: ignore
            filename=db_file.filename, # type: ignore
            format=cast(Literal["png", "jpg", "pdf", "csv"], db_file.format),
            size=db_file.file_size, # type: ignore
        )
    
    async def get_file_by_key_async(self, key: str) -> File:
        if not self.async_db_client:
            raise AssertionError("Asynchronous DB client is not initialized")
        stmt = select(FileRecord).where(FileRecord.file_key == key)
        result = await self.async_db_client.execute(stmt)
        db_file = result.scalars().first()
        if not db_file:
            raise ValueError("File record not found in database")
        return File(
            key=db_file.file_key, # type: ignore
            filename=db_file.filename, # type: ignore
            format=cast(Literal["png", "jpg", "pdf", "csv"], db_file.format),
            size=db_file.file_size,  # type: ignore
        )

    def _cal_user_occupy_sync(self, user_id: int) -> int:
        """ Calculate the total file occupy for a user """
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        total = self.db_client.query(FileRecord).with_entities(
            FileRecord.file_size
        ).filter(
            FileRecord.user_id == user_id
        ).all()
        return sum(size for (size,) in total)  # type: ignore

    async def _cal_user_occupy_async(self, user_id: int) -> int:
        """ Calculate the total file occupy for a user """
        if self.async_db_client is None:
            raise AssertionError("Asynchronous DB client is not initialized")
        stmt = select(FileRecord.file_size).where(FileRecord.user_id == user_id)
        result = await self.async_db_client.execute(stmt)
        total = result.scalars().all()
        return sum(size for size in total)  # type: ignore

    def _get_col_types(self, content: bytes) -> dict[str, ColType]:
        df = pandas.read_csv(io.StringIO(content.decode('utf-8')))
        col_types = {}
        for col in df.columns:
            dtype = df[col].dtype
            col_type = ColType.from_ptype(dtype)
            col_types[col] = col_type
        return col_types
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

    def write_sync(self, 
                   filename: str, 
                   content: bytes | io.BytesIO, 
                   format: Literal["png", "jpg", "pdf", "csv"], 
                   node_id: str, 
                   project_id: int, 
                   user_id: int
    ) -> File:
        """ Write content to a file for a user, return the file path """
        logger.debug("@@@@@@@@@@@@@@@@@@@@@")
        logger.debug(f"Writing file sync: filename={filename}, format={format}, node_id={node_id}, project_id={project_id}, user_id={user_id}")
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        if isinstance(content, io.BytesIO):
            content.seek(0)
            content = content.getvalue()
        # detect col_types for csv
        col_types: dict[str, ColType] | None = None
        if format == "csv":
            col_types = self._get_col_types(content)
        key = uuid4().hex
        existing_file = self.db_client.query(FileRecord).filter((FileRecord.project_id == project_id) & (FileRecord.node_id == node_id)).first()
        try:
            # check storage limit
            user = self.db_client.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            file_occupy = self._cal_user_occupy_sync(user_id)
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
                try:
                    self.minio_client.remove_object(
                        bucket_name=self.bucket,
                        object_name=old_key # type: ignore
                    )
                except Exception:
                    pass
            else:
                file = FileRecord(
                    file_key=key,
                    filename=filename,
                    format=format,
                    user_id=user_id,
                    project_id=project_id,
                    node_id=node_id,
                    file_size=len(content),
                )
                self.db_client.add(file)
            self.db_client.commit()
        except S3Error as e:
            self.db_client.rollback()
            logger.exception(f"Failed to upload file to MinIO: {e}")
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
            logger.exception(f"Failed to write file: {e}")
            raise IOError(f"Failed to write file: {e}")
        return File(key=key, col_types=col_types, filename=filename, format=format, size=len(content))
    
    async def write_async(self, 
                          filename: str, 
                          content: bytes | io.BytesIO, 
                          format: Literal["png", "jpg", "pdf", "csv"], 
                          node_id: str, 
                          project_id: int, 
                          user_id: int
    ) -> File:
        """ Write content to a file for a user, return the file path """
        if self.async_db_client is None:
            raise AssertionError("Asynchronous DB client is not initialized")
        if isinstance(content, io.BytesIO):
            content.seek(0)
            content = content.getvalue()
        # detect col_types for csv
        col_types: dict[str, ColType] | None = None
        if format == "csv":
            col_types = self._get_col_types(content)
        key = uuid4().hex
        stmt = select(FileRecord).where(
            (FileRecord.project_id == project_id) & (FileRecord.node_id == node_id)
        )
        result = await self.async_db_client.execute(stmt)
        existing_file = result.scalars().first()
        try:
            # check storage limit
            stmt = select(UserRecord).where(UserRecord.id == user_id)
            result = await self.async_db_client.execute(stmt)
            user = result.scalars().first()
            if not user:
                raise ValueError("User not found")
            file_occupy = await self._cal_user_occupy_async(user_id)
            if file_occupy + len(content) > user.file_total_space: # type: ignore
                raise InsufficientStorageError("User storage limit exceeded")
            # upload to MinIO
            await asyncio.to_thread(
                self.minio_client.put_object,
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
                try:
                    await asyncio.to_thread(
                        self.minio_client.remove_object,
                        bucket_name=self.bucket,
                        object_name=old_key # type: ignore
                    )
                except Exception:
                    pass
            else:
                file = FileRecord(
                    file_key=key,
                    filename=filename,
                    format=format,
                    user_id=user_id,
                    project_id=project_id,
                    node_id=node_id,
                    file_size=len(content),
                )
                self.async_db_client.add(file)
            await self.async_db_client.commit()
        except S3Error as e:
            await self.async_db_client.rollback()
            logger.exception(f"Failed to upload file to MinIO: {e}")
            raise IOError(f"Failed to upload file to MinIO: {e}")
        except InsufficientStorageError as e:
            raise e
        except Exception as e:
            await self.async_db_client.rollback()
            try:
                await asyncio.to_thread(
                    self.minio_client.remove_object,
                    bucket_name=self.bucket,
                    object_name=key
                )
            except Exception:
                pass
            logger.exception(f"Failed to write file: {e}")
            raise IOError(f"Failed to write file: {e}")
        return File(key=key, col_types=col_types, filename=filename, format=format, size=len(content))
    
    def delete_sync(self, file: File, user_id: int | None) -> None:
        """ Delete a file. If user_id is None, means admin operation """
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        # validate file ownership
        db_file = self.db_client.query(FileRecord).filter(FileRecord.file_key == file.key).first()
        if not db_file:
            raise IOError("File record not found in database")
        if user_id and db_file.user_id != user_id: # type: ignore
            raise PermissionError("Permission denied to access this file")
        try:
            self.minio_client.remove_object(
                bucket_name=self.bucket,
                object_name=file.key
            )
            db_file = self.db_client.query(FileRecord).filter(FileRecord.file_key == file.key).first()
            if not db_file:
                raise IOError("File record not found in database")
            user = self.db_client.query(UserRecord).filter(UserRecord.id == db_file.user_id).first()
            if not user:
                raise IOError("User not found in database")
            self.db_client.delete(db_file)
            self.db_client.commit()
        except S3Error as e:
            logger.exception(f"Failed to delete file from MinIO: {e}")
            self.db_client.rollback()
            raise IOError(f"Failed to delete file from MinIO: {e}")
        except Exception as e:
            logger.exception(f"Failed to delete file record from database: {e}")
            self.db_client.rollback()
            raise IOError(f"Failed to delete file record from database: {e}")

    async def delete_async(self, file: File, user_id: int | None) -> None:
        """ Delete a file. If user_id is None, means admin operation """
        if self.async_db_client is None:
            raise AssertionError("Asynchronous DB client is not initialized")
        # validate file ownership
        stmt = select(FileRecord).where(FileRecord.file_key == file.key)
        result = await self.async_db_client.execute(stmt)
        db_file = result.scalars().first()
        if not db_file:
            raise IOError("File record not found in database")
        if user_id and db_file.user_id != user_id: # type: ignore
            raise PermissionError("Permission denied to access this file")
        try:
            await asyncio.to_thread(
                self.minio_client.remove_object,
                bucket_name=self.bucket,
                object_name=file.key
            )
            stmt = select(FileRecord).where(FileRecord.file_key == file.key)
            result = await self.async_db_client.execute(stmt)
            db_file = result.scalars().first()
            if not db_file:
                raise IOError("File record not found in database")
            stmt = select(UserRecord).where(UserRecord.id == db_file.user_id)
            result = await self.async_db_client.execute(stmt)
            user = result.scalars().first()
            if not user:
                raise IOError("User not found in database")
            await self.async_db_client.delete(db_file)
            await self.async_db_client.commit()
        except S3Error as e:
            logger.exception(f"Failed to delete file from MinIO: {e}")
            await self.async_db_client.rollback()
            raise IOError(f"Failed to delete file from MinIO: {e}")
        except Exception as e:
            logger.exception(f"Failed to delete file record from database: {e}")
            await self.async_db_client.rollback()
            raise IOError(f"Failed to delete file record from database: {e}")

    def read_sync(self, file: File, user_id: int | None) -> bytes:
        """Read content from a file"""
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        db_file = self.db_client.query(FileRecord).filter(FileRecord.file_key == file.key).first()
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
            logger.exception(f"Failed to read file from MinIO: {e}")
            raise IOError(f"Failed to read file from MinIO: {e}")

    async def read_async(self, file: File, user_id: int | None) -> bytes:
        """Read content from a file"""
        if self.async_db_client is None:
            raise AssertionError("Asynchronous DB client is not initialized")
        stmt = select(FileRecord).where(FileRecord.file_key == file.key)
        result = await self.async_db_client.execute(stmt)
        db_file = result.scalars().first()
        if not db_file:
            raise ValueError("File record not found in database")
        if user_id and db_file.user_id != user_id: # type: ignore
            raise PermissionError("Permission denied to access this file")
        try:
            response = await asyncio.to_thread(
                self.minio_client.get_object,
                bucket_name=self.bucket,
                object_name=file.key
            )
            data = response.read()
            return data
        except S3Error as e:
            logger.exception(f"Failed to read file from MinIO: {e}")
            raise IOError(f"Failed to read file from MinIO: {e}")

    def list_file_sync(self, user_id: int) -> UserFileList:
        """ List all files owned by the user in the project """
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        try:
            db_files = self.db_client.query(FileRecord).filter(
                FileRecord.user_id == user_id,
            ).all()
            user = self.db_client.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not user:
                raise ValueError("User not found in database")
            file_items = []
            for db_file in db_files:
                # query project name
                project = self.db_client.query(ProjectRecord).filter(ProjectRecord.id == db_file.project_id).first()
                project_name = project.name if project else ""
                file_items.append(
                    FileItem(
                        key=db_file.file_key,  # type: ignore
                        filename=db_file.filename,  # type: ignore
                        format=cast(
                            Literal["png", "jpg", "pdf", "csv"], db_file.format
                        ),
                        size=db_file.file_size,  # type: ignore
                        modified_at=int(db_file.last_modify_time.timestamp() * 1000),  # type: ignore
                        project_name=project_name,  # type: ignore
                    )
                )
            return UserFileList(
                user_id=user_id,
                files=file_items,
                total_size=user.file_total_space, # type: ignore
                used_size=self._cal_user_occupy_sync(user_id)
            )
        except Exception as e:
            logger.exception(f"Failed to list files: {e}")
            raise IOError(f"Failed to list files: {e}")

    async def list_file_async(self, user_id: int) -> UserFileList:
        """ List all files owned by the user in the project """
        if self.async_db_client is None:
            raise AssertionError("Asynchronous DB client is not initialized")
        try:
            stmt = select(FileRecord).where(FileRecord.user_id == user_id)
            result = await self.async_db_client.execute(stmt)
            db_files = result.scalars().all()
            stmt = select(UserRecord).where(UserRecord.id == user_id)
            result = await self.async_db_client.execute(stmt)
            user = result.scalars().first()
            if not user:
                raise ValueError("User not found in database")
            file_items = []
            for db_file in db_files:
                # query project name
                stmt = select(ProjectRecord).where(ProjectRecord.id == db_file.project_id)
                result = await self.async_db_client.execute(stmt)
                project = result.scalars().first()
                project_name = project.name if project else ""
                file_items.append(FileItem(
                    key=db_file.file_key, # type: ignore
                    filename=db_file.filename, # type: ignore
                    format=cast(Literal["png", "jpg", "pdf", "csv"], db_file.format),
                    size=db_file.file_size, # type: ignore
                    modified_at=int(db_file.last_modify_time.timestamp() * 1000), # type: ignore
                    project_name=project_name # type: ignore
                ))
            return UserFileList(
                user_id=user_id,
                files=file_items,
                total_size=user.file_total_space, # type: ignore
                used_size=await self._cal_user_occupy_async(user_id)
            )
        except Exception as e:
            logger.exception(f"Failed to list files: {e}")
            raise IOError(f"Failed to list files: {e}")
    
    def check_file_exists_sync(self, file: File) -> bool:
        """ 
        Check if a file exists
        This will check both database and MinIO
        """
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        db_file = self.db_client.query(FileRecord).filter(FileRecord.file_key == file.key).first()
        if not db_file:
            return False
        try:
            self.minio_client.stat_object(
                bucket_name=self.bucket,
                object_name=file.key
            )
            return True
        except S3Error:
            return False
    
    async def check_file_exists_async(self, file: File) -> bool:
        """ 
        Check if a file exists
        This will check both database and MinIO
        """
        if self.async_db_client is None:
            raise AssertionError("Asynchronous DB client is not initialized")
        stmt = select(FileRecord).where(FileRecord.file_key == file.key)
        result = await self.async_db_client.execute(stmt)
        db_file = result.scalars().first()
        if not db_file:
            return False
        try:
            await asyncio.to_thread(
                self.minio_client.stat_object,
                bucket_name=self.bucket,
                object_name=file.key
            )
            return True
        except S3Error:
            return False
    
@celery_app.task
def cleanup_orphan_files_task():
    """
    A periodic Celery task to clean up orphan files in MinIO that are not referenced in the database.
    """
    db_client = next(get_session())
    file_manager = FileManager(async_db_session=None)
    minio_client = Minio(
        endpoint=os.getenv("MINIO_ENDPOINT", ""),
        access_key=os.getenv("MINIO_ROOT_USER", ""),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", ""),
        secure=False  # MinIO in Docker is HTTP, not HTTPS
    )
    # step 1: delete files for invalid node_id
    try:
        logger.info("Starting cleanup of orphan files...")
        
        # 1. get all existing node_id from projects
        all_projects = db_client.query(ProjectRecord).all()
        valid_node_ids = set()
        for project in all_projects:
            if project.workflow: # type: ignore
                workflow_data = project.workflow
                if isinstance(workflow_data, str):
                    workflow_data = json.loads(workflow_data)
                for node in workflow_data.get("nodes", []):
                    node_id = node.get("id")
                    if node_id:
                        valid_node_ids.add((project.id, node_id))
        
        # 2. list all files keys from db
        all_files = db_client.query(FileRecord).all()
        
        orphan_files = []
        for db_file in all_files:
            modify_time = db_file.last_modify_time
            if (datetime.datetime.now() - modify_time).total_seconds() < 3600: # 1 hour
                continue  # skip files modified within the last hour
            if (db_file.project_id, db_file.node_id) not in valid_node_ids:
                orphan_files.append(db_file)
        if not orphan_files:
            logger.info("No orphan files found.")
            return
        
        # 3. delete orphan files from MinIO and database
        for file_record in orphan_files:
            try:
                file_to_delete = file_manager.get_file_by_key_sync(file_record.file_key)
                file_manager.delete_sync(file_to_delete, user_id=None)  # Admin operation
            except Exception as e:
                logger.error(f"Failed to delete orphan file {file_record.file_key}: {e}")
        db_client.commit()

        logger.info(f"Cleanup completed. Deleted {len(orphan_files)} orphan files.")
    except Exception as e:
        logger.exception(f"Failed to clean up orphan files: {e}")

    # step 2: delete files in MinIO not in database
    try:
        objects = file_manager.minio_client.list_objects(bucket_name=file_manager.bucket, recursive=True)
        db_file_keys = set([db_file.file_key for db_file in db_client.query(FileRecord.file_key).all()])
        for obj in objects:
            if obj.object_name not in db_file_keys:
                assert isinstance(obj.object_name, str)
                try:
                    minio_client.remove_object(
                        bucket_name=file_manager.bucket,
                        object_name=obj.object_name
                    )
                except Exception as e:
                    logger.exception(f"Failed to delete orphan MinIO file {obj.object_name}: {e}")
        logger.info("MinIO orphan file cleanup completed.")
    finally:
        db_client.close()