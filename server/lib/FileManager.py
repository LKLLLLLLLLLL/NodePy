import asyncio
import io
import os
import time
from typing import cast
from urllib.parse import quote
from uuid import uuid4

from loguru import logger
from minio import Minio, S3Error
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from server.celery import celery_app
from server.lib.DataManager import DataManager
from server.models.data import DataRef
from server.models.database import (
    FileRecord,
    ProjectRecord,
    UserRecord,
    get_session,
)
from server.models.exception import InsufficientStorageError
from server.models.file import FILE_FORMATS_TYPE, File, FileItem, UserFileList
from server.models.project import ProjWorkflow
from server.models.schema import ColType, Schema


class FileManager:
    """
    The unified library for managing files for nodes,
    including uploading, downloading, reading, writing, deleting files.
    Each file manager is bind to a user_id and project_id.
    And can be used in multiple containers.

    When project_id is provided, all operations including writing are enabled.
    When project_id is None, only read, delete, and list operations are permitted.
    """
    def __init__(self, async_db_session: AsyncSession | None = None, sync_db_session: Session | None = None) -> None:
        self.minio_client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT", ""),
            access_key=os.getenv("MINIO_ROOT_USER", ""),
            secret_key=os.getenv("MINIO_ROOT_PASSWORD", ""),
            secure=False  # MinIO in Docker is HTTP, not HTTPS
        )
        if async_db_session:
            assert sync_db_session is None
            self.db_client = None
            self.async_db_client = async_db_session
        elif sync_db_session:
            assert async_db_session is None
            self.db_client = sync_db_session
            self.async_db_client = None
        else:
            raise AssertionError("Either async_db_session or sync_db_session must be provided")
        self.bucket = "nodepy-files"
        # Ensure bucket exists
        if not self.minio_client.bucket_exists(self.bucket):
            self.minio_client.make_bucket(self.bucket)


    def _cal_user_occupy_sync(self, user_id: int) -> int:
        """ Calculate the total file occupy for a user """
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        total = self.db_client.query(FileRecord).with_entities(
            FileRecord.file_size
        ).filter(
            FileRecord.user_id == user_id,
            FileRecord.is_deleted.is_(False),  # type: ignore
            FileRecord.project_id.isnot(None)
        ).all()
        return sum(size for (size,) in total)  # type: ignore

    async def _cal_user_occupy_async(self, user_id: int) -> int:
        """ Calculate the total file occupy for a user """
        if self.async_db_client is None:
            raise AssertionError("Asynchronous DB client is not initialized")
        stmt = select(FileRecord.file_size).where(
            FileRecord.user_id == user_id, 
            FileRecord.is_deleted.is_(False),  # type: ignore
            FileRecord.project_id.isnot(None)
        )
        result = await self.async_db_client.execute(stmt)
        total = result.scalars().all()
        return sum(size for size in total)  # type: ignore

    def _get_col_types(self, content: bytes, format: FILE_FORMATS_TYPE) -> dict[str, ColType]:
        import pandas
        
        if format == "csv":
            df = pandas.read_csv(io.StringIO(content.decode('utf-8')))
        elif format == "xlsx":
            df = pandas.read_excel(io.BytesIO(content))
        elif format == "json":
            df = pandas.read_json(io.StringIO(content.decode('utf-8')))
        else:
            raise ValueError(f"Unsupported format for column type detection: {format}")
        col_types = {}
        for col in df.columns:
            dtype = df[col].dtype
            col_type = ColType.from_ptype(dtype)
            col_types[col] = col_type
        return col_types
    
    def get_file_by_key_sync(self, key: str) -> File:
        """ Get a File object by its key """
        if not self.db_client:
            raise AssertionError("Synchronous DB client is not initialized")
        db_file = self.db_client.query(FileRecord).filter(
            FileRecord.file_key == key,
            FileRecord.is_deleted.is_(False),
            FileRecord.project_id.isnot(None)
        ).first()
        if not db_file:
            raise ValueError("File record not found in database")
        return File(
            key=db_file.file_key, # type: ignore
            filename=db_file.filename, # type: ignore
            format=cast(FILE_FORMATS_TYPE, db_file.format),
            size=db_file.file_size, # type: ignore
        )
    
    async def get_file_by_key_async(self, key: str) -> File:
        if not self.async_db_client:
            raise AssertionError("Asynchronous DB client is not initialized")
        stmt = select(FileRecord).where(
            FileRecord.file_key == key,
            FileRecord.is_deleted.is_(False),
            FileRecord.project_id.isnot(None)
        )
        result = await self.async_db_client.execute(stmt)
        db_file = result.scalars().first()
        if not db_file:
            raise ValueError("File record not found in database")
        return File(
            key=db_file.file_key,  # type: ignore
            filename=db_file.filename,  # type: ignore
            format=cast(FILE_FORMATS_TYPE, db_file.format),
            size=db_file.file_size,  # type: ignore
        )

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
                   format: FILE_FORMATS_TYPE, 
                   node_id: str, 
                   project_id: int, 
                   user_id: int
    ) -> File:
        """ Write content to a file for a user, return the file path """
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        if isinstance(content, io.BytesIO):
            content.seek(0)
            content = content.getvalue()
        # detect col_types for csv, xlsx, json
        col_types: dict[str, ColType] | None = None
        if format in (
            "csv",
            "csv",
            "xlsx",
            "json",
        ):
            col_types = self._get_col_types(content, format)
        key = uuid4().hex + f".{format}"        
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
                metadata={"project_id": str(project_id), "user_id": str(user_id), "filename": quote(filename), "node_id": node_id}
            )
            # record in database
            # no need to replace existing file, they will be cleaned up in periodic task
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
    
    async def write_async(
        self,
        filename: str,
        content: bytes | io.BytesIO,
        format: FILE_FORMATS_TYPE,
        node_id: str,
        project_id: int,
        user_id: int,
    ) -> File:
        """ Write content to a file for a user, return the file path """
        if self.async_db_client is None:
            raise AssertionError("Asynchronous DB client is not initialized")
        if isinstance(content, io.BytesIO):
            content.seek(0)
            content = content.getvalue()
        # detect col_types for csv, xlsx, json
        col_types: dict[str, ColType] | None = None
        if format in (
            "csv",
            "csv",
            "xlsx",
            "json",
        ):
            col_types = self._get_col_types(content, format)
        key = uuid4().hex + f".{format}"
        stmt = select(FileRecord).where(
            (FileRecord.project_id == project_id) & (FileRecord.node_id == node_id)
        )
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
                metadata={"project_id": str(project_id), "user_id": str(user_id), "filename": quote(filename), "node_id": node_id}
            )
            # record in database
            # no need to replace existing file, they will be cleaned up in periodic task
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
        db_file = self.db_client.query(FileRecord).filter(
            FileRecord.file_key == file.key,
            FileRecord.is_deleted.is_(False), 
            FileRecord.project_id.isnot(None)
        ).first()
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
        stmt = select(FileRecord).where(
            FileRecord.file_key == file.key,
            FileRecord.is_deleted.is_(False), 
            FileRecord.project_id.isnot(None)
        )
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
        db_file = self.db_client.query(FileRecord).filter(
            FileRecord.file_key == file.key, 
            FileRecord.is_deleted.is_(False), 
            FileRecord.project_id.isnot(None)
        ).first()
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
        stmt = select(FileRecord).where(
            FileRecord.file_key == file.key,
            FileRecord.is_deleted.is_(False),
            FileRecord.project_id.isnot(None)
        )
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
                FileRecord.is_deleted.is_(False),
                FileRecord.project_id.isnot(None)
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
                            FILE_FORMATS_TYPE, db_file.format
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
            stmt = select(FileRecord).where(
                FileRecord.user_id == user_id,
                FileRecord.is_deleted.is_(False),
                FileRecord.project_id.isnot(None)
            )
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
                    format=cast(FILE_FORMATS_TYPE, db_file.format),
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
        db_file = self.db_client.query(FileRecord).filter(
            FileRecord.file_key == file.key, 
            FileRecord.is_deleted.is_(False), 
            FileRecord.project_id.isnot(None)
        ).first()
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
        stmt = select(FileRecord).where(
            FileRecord.file_key == file.key,
            FileRecord.is_deleted.is_(False),
            FileRecord.project_id.isnot(None)
        )
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

    def clean_orphan_file_sync(self, project_id: int) -> None:
        """ Flag files with no project reference it deleted in the database """
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        data_manager = DataManager(sync_db_session=self.db_client)
        try:
            # 1. get workflow of the project
            project_record = self.db_client.query(ProjectRecord).filter(ProjectRecord.id == project_id).first()
            if not project_record:
                raise ValueError("Project not found")
            workflow = ProjWorkflow.model_validate(project_record.workflow)  # type: ignore
            # 2. get all dataref from workflow
            nodes = workflow.nodes
            referenced_data_ids = set()
            for node in nodes:
                for data_ref in node.data_out.values():
                    referenced_data_ids.add(data_ref.data_id)
            # 3. get data payloads for file keys
            referenced_file_keys = set()
            for data_id in referenced_data_ids:
                data = data_manager.read_sync(data_ref = DataRef(data_id=data_id))
                if data.extract_schema().type == Schema.Type.FILE:
                    file_payload = data.payload
                    assert isinstance(file_payload, File)
                    referenced_file_keys.add(file_payload.key)
            # 4. get file keys referenced in node parameters
            for node in nodes:
                for param in node.param.values():
                    try:
                        file = File.model_validate(param)
                        logger.debug(f"Found referenced file {file.filename} with key {file.key}")
                        referenced_file_keys.add(file.key)
                    except Exception:
                        continue

            # 5. flag files not in referenced_file_keys as deleted
            all_file_records = self.db_client.query(FileRecord).filter(
                FileRecord.project_id == project_id,
                FileRecord.is_deleted.is_(False)  # type: ignore
            ).all()
            soft_delete_files = []
            for file_record in all_file_records:
                if file_record.file_key not in referenced_file_keys:
                    file_record.is_deleted = True  # type: ignore
                    soft_delete_files.append(file_record.filename)
            self.db_client.commit()
            logger.info(f"Soft deleted {len(soft_delete_files)} orphan files for project {project_id}")
        except Exception as e:
            logger.exception(f"Failed to flag orphan files: {e}")
            self.db_client.rollback()
            raise IOError(f"Failed to flag orphan files: {e}")

@celery_app.task
def cleanup_soft_deleted_files_task():
    """
    A periodic Celery task to clean up files that are marked as deleted in the database.
    """
    start_time = time.perf_counter()
    db_client = next(get_session())
    file_manager = FileManager(sync_db_session=db_client)

    deleted_count = 0
    try:
        # 1. get all files marked as deleted or the project_id is null in database
        soft_deleted_files = db_client.query(FileRecord).filter(
            FileRecord.is_deleted.is_(True)  | (FileRecord.project_id.is_(None))  # type: ignore
        ).all()

        if not soft_deleted_files:
            logger.info("No soft-deleted files to clean up.")
            return

        logger.debug(f"Soft-deleted files to delete: {[file.filename for file in soft_deleted_files]}")
        logger.info(f"Found {len(soft_deleted_files)} soft-deleted files to permanently delete.")

        # 2. Delete them from MinIO and database
        for file_record in soft_deleted_files:
            try:
                # Delete from MinIO
                file_manager.minio_client.remove_object(
                    bucket_name=file_manager.bucket, object_name=file_record.file_key # type: ignore
                )
                # Delete from database
                db_client.delete(file_record)
                deleted_count += 1
            except S3Error as e:
                # If the file does not exist in MinIO, continue deleting the database record
                if e.code == "NoSuchKey":
                    logger.warning(
                        f"File {file_record.file_key} not found in MinIO, but deleting from DB."
                    )
                    db_client.delete(file_record)
                    deleted_count += 1
                else:
                    logger.error(
                        f"Failed to delete orphan file {file_record.file_key} from MinIO: {e}"
                    )
            except Exception as e:
                logger.error(
                    f"Failed to delete orphan file record {file_record.file_key} from DB: {e}"
                )

        db_client.commit()
        logger.info(f"Cleanup completed. Permanently deleted {deleted_count} files.")

    except Exception as e:
        logger.exception(f"An error occurred during orphan file cleanup task: {e}")
        db_client.rollback()
    finally:
        db_client.close()
        logger.info(
            f"Orphan file cleanup task finished in {time.perf_counter() - start_time:.2f} seconds."
        )
