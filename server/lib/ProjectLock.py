import redis.asyncio as redis
import redis as redis_sync
import os
from typing import Optional, Self

LOCK_REDIS_URL = os.getenv("REDIS_URL", "") + "/3"

class ProjectLock:
    """
    This class handles project locking to prevent concurrent modifications.
    """
    def __init__(self, project_id: int) -> None:
        self._async_conn: Optional[redis.Redis] = None
        self._sync_conn: Optional[redis_sync.Redis] = None
        self._project_id = project_id

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
        acquired = await self._async_conn.set(lock_key, "locked", nx=True)
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

    async def set_timeout_async(self, seconds: int | None) -> None:
        """
        Set a timeout for the lock.
        """
        if self._async_conn is None:
            self._async_conn = await redis.Redis.from_url(LOCK_REDIS_URL)
        lock_key = f"project_lock:{self._project_id}"
        if seconds:
            await self._async_conn.expire(lock_key, seconds)
        else:
            await self._async_conn.persist(lock_key)

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
        acquired = self._sync_conn.set(lock_key, "locked", nx=True)
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

    def set_timeout_sync(self, seconds: int | None) -> None:
        """
        Set a timeout for the lock.
        """
        if self._sync_conn is None:
            self._sync_conn = redis_sync.Redis.from_url(LOCK_REDIS_URL)
        lock_key = f"project_lock:{self._project_id}"
        if seconds:
            self._sync_conn.expire(lock_key, seconds)
        else:
            self._sync_conn.persist(lock_key)