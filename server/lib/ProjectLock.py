import redis.asyncio as redis
import redis as redis_sync
import os
from typing import Optional, Self
import asyncio
import time

LOCK_REDIS_URL = os.getenv("REDIS_URL", "") + "/3"
RETRY_INTERVAL = 0.1  # seconds

class ProjectLock:
    """
    This class handles project locking to prevent concurrent modifications.
    """
    def __init__(self, project_id: int, max_block_time: float | None) -> None:
        self._async_conn: Optional[redis.Redis] = None
        self._sync_conn: Optional[redis_sync.Redis] = None
        self._project_id = project_id
        self._max_block_time = max_block_time or float("inf")

    # ====================== async methods ====================== 
    async def __aenter__(self) -> Self:
        """
        Acquire a lock for the given project_id.
        """
        await self.lock_async()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Release the lock.
        """
        await self.release_async()
        if self._async_conn is not None:
            await self._async_conn.close()
            self._async_conn = None

    @staticmethod
    async def is_locked_async(project_id: int) -> bool:
        """
        Check if the project is locked.
        """
        if ProjectLock._async_conn is None:
            ProjectLock._async_conn = await redis.Redis.from_url(LOCK_REDIS_URL)
        lock_key = f"project_lock:{project_id}"
        exists = await ProjectLock._async_conn.exists(lock_key)
        return exists == 1
    
    async def lock_async(self) -> None:
        """
        Lock the project.
        """
        if self._async_conn is None:
            self._async_conn = await redis.Redis.from_url(LOCK_REDIS_URL)
        lock_key = f"project_lock:{self._project_id}"
        total_wait = 0.0
        acquired = False
        while total_wait < self._max_block_time:  # wait up to max_block_time
            acquired = await self._async_conn.set(lock_key, "locked", nx=True)
            if acquired:
                break
            total_wait += RETRY_INTERVAL
            await asyncio.sleep(RETRY_INTERVAL)
        if not acquired:
            raise RuntimeError(f"Project {self._project_id} is already locked.")

    async def release_async(self) -> None:
        """
        Release the lock for the project.
        """
        if self._async_conn is None:
            self._async_conn = await redis.Redis.from_url(LOCK_REDIS_URL)
        # delete caller info
        key = f"project_lock:{self._project_id}:info"
        await self._async_conn.delete(key)
        # delete lock
        lock_key = f"project_lock:{self._project_id}"
        await self._async_conn.delete(lock_key)

    async def set_caller_info_async(self, info: str) -> None:
        """
        Set caller info to the lock.
        """
        if self._async_conn is None:
            self._async_conn = await redis.Redis.from_url(LOCK_REDIS_URL)
        key = f"project_lock:{self._project_id}:info"
        await self._async_conn.set(key, info)

    # ====================== sync methods ======================
    def __enter__(self) -> Self:
        """
        Acquire a lock for the given project_id.
        """
        self.lock_sync()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Release the lock.
        """
        self.release_sync()
        if self._sync_conn is not None:
            self._sync_conn.close()
            self._sync_conn = None
    
    @staticmethod
    def is_locked_sync(project_id: int) -> bool:
        """
        Check if the project is locked.
        """
        if ProjectLock._sync_conn is None:
            ProjectLock._sync_conn = redis_sync.Redis.from_url(LOCK_REDIS_URL)
        lock_key = f"project_lock:{project_id}"
        exists = ProjectLock._sync_conn.exists(lock_key)
        return exists == 1
    
    def lock_sync(self) -> None:
        """
        Lock the project.
        """
        if self._sync_conn is None:
            self._sync_conn = redis_sync.Redis.from_url(LOCK_REDIS_URL)
        lock_key = f"project_lock:{self._project_id}"
        total_wait = 0.0
        acquired = False
        while total_wait < self._max_block_time:  # wait up to max_block_time
            acquired = self._sync_conn.set(lock_key, "locked", nx=True)
            if acquired:
                break
            total_wait += RETRY_INTERVAL
            time.sleep(RETRY_INTERVAL)
        if not acquired:
            raise RuntimeError(f"Project {self._project_id} is already locked.")
    
    def release_sync(self) -> None:
        """
        Release the lock for the project.
        """
        if self._sync_conn is None:
            self._sync_conn = redis_sync.Redis.from_url(LOCK_REDIS_URL)
        # delete caller info
        key = f"project_lock:{self._project_id}:info"
        self._sync_conn.delete(key)
        # delete lock
        lock_key = f"project_lock:{self._project_id}"
        self._sync_conn.delete(lock_key)
