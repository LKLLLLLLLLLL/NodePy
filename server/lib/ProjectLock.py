import asyncio
import os
import time
from typing import Literal, Optional, Self

import redis as redis_sync
import redis.asyncio as redis
from loguru import logger

from server.models.exception import ProjectLockError, ProjLockIdentityError

LOCK_REDIS_URL = os.getenv("REDIS_URL", "") + "/3"
RETRY_INTERVAL = 0.1  # seconds
APPOINTED_LOCK_EXPIRY = 30  # seconds

class ProjectLock:
    """
    This class handles project locking to prevent concurrent modifications.
    """
    def __init__(self, 
                 project_id: int, 
                 identity: str | None, 
                 max_block_time: float | None,
                 scope: Literal["workflow", "ui_state", "all"]
    ) -> None:
        """
        If max_block_time is None, wait indefinitely.
        If identity is provided, you will get the lock first to the identity-satisfied lock releaser.
        """
        self._async_conn: Optional[redis.Redis] = None
        self._sync_conn: Optional[redis_sync.Redis] = None
        self._project_id = project_id
        self._identity = identity
        self._max_block_time = max_block_time or float("inf")
        self._scope: Literal["workflow", "ui_state", "all"] = scope

    @staticmethod
    def _get_lock_key(project_id: int, scope: Literal["workflow", "ui_state", "all"]) -> list[str]:
        keys = []
        if scope in ["workflow", "all"]:
            keys.append(f"project_lock:{project_id}:workflow")
        if scope in ["ui_state", "all"]:
            keys.append(f"project_lock:{project_id}:ui_state")
        return keys

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
    async def is_locked_async(project_id: int, scope: Literal["workflow", "ui_state", "all"]) -> bool:
        async with redis.Redis.from_url(LOCK_REDIS_URL) as conn:
            lock_key = ProjectLock._get_lock_key(project_id, scope)
            exists = False
            for key in lock_key:
                exists = exists or bool(await conn.exists(key))
            return exists
    
    async def lock_async(self) -> None:
        """
        Lock the project.
        """
        if self._async_conn is None:
            self._async_conn = await redis.Redis.from_url(LOCK_REDIS_URL)
        lock_keys = ProjectLock._get_lock_key(self._project_id, self._scope)
        identity_key = f"project_lock:{self._project_id}:appointed"
        total_wait = 0.0
        acquired = False
        identity = None
        while total_wait < self._max_block_time:  # wait up to max_block_time
            # operations below implement a atomic checking identity and setting a lock 
            # with optimistic locking
            await self._async_conn.watch(identity_key)
            identity = await self._async_conn.get(identity_key)
            if identity is not None:
                if self._identity is None or identity.decode() != self._identity:  # type: ignore
                    await self._async_conn.unwatch()
                    await asyncio.sleep(RETRY_INTERVAL)
                    total_wait += RETRY_INTERVAL
                    continue  # wait for appointed identity to acquire the lock
            async with self._async_conn.pipeline() as pipe:
                pipe.multi()
                for key in lock_keys:
                    pipe.set(key, "locked", nx=True)
                results = await pipe.execute()
                if results and all(results):
                    acquired = True
                    break
                else:
                    for i, result in enumerate(results):
                        if result:
                            await self._async_conn.delete(lock_keys[i])
            total_wait += RETRY_INTERVAL
            await asyncio.sleep(RETRY_INTERVAL)
        if not acquired:
            logger.error(f"Failed to acquire lock for project {self._project_id} within {self._max_block_time} seconds.")
            raise ProjectLockError(f"Project {self._project_id} is already locked.")                
        if identity is not None:
            # clear appointed identity after acquiring the lock
            identity_key = f"project_lock:{self._project_id}:appointed"
            await self._async_conn.delete(identity_key)
        else:
            if self._identity is not None:
                # get the lock, but not satisfy my identity. Because the identity can be expired, it tends that I will never got the right lock, so throw exception.
                await self.release_async() # release the lock, because the __aexit__ may not be called
                logger.error(f"Project {self._project_id} lock identity does not match the appointed identity.")
                raise ProjLockIdentityError(
                    f"Project {self._project_id} lock identity does not match the appointed identity."
                )

    async def release_async(self) -> None:
        """
        Release the lock for the project.
        """
        if self._async_conn is None:
            self._async_conn = await redis.Redis.from_url(LOCK_REDIS_URL)
        # delete lock
        lock_keys = ProjectLock._get_lock_key(self._project_id, self._scope)
        for key in lock_keys:
            await self._async_conn.delete(key)
    
    async def appoint_transfer_async(self, identity: str) -> None:
        """
        Appoint a specific identity to transfer the lock.
        """
        if self._async_conn is None:
            self._async_conn = await redis.Redis.from_url(LOCK_REDIS_URL)
        key = f"project_lock:{self._project_id}:appointed"
        await self._async_conn.set(key, identity, ex=APPOINTED_LOCK_EXPIRY)

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
        with redis_sync.Redis.from_url(LOCK_REDIS_URL) as conn:
            lock_keys = ProjectLock._get_lock_key(project_id, "all")
            exists = False
            for key in lock_keys:
                exists = exists or bool(conn.exists(key))
            return exists
    
    def lock_sync(self) -> None:
        """
        Lock the project.
        """
        if self._sync_conn is None:
            self._sync_conn = redis_sync.Redis.from_url(LOCK_REDIS_URL)
        lock_keys = ProjectLock._get_lock_key(self._project_id, self._scope)
        identity_key = f"project_lock:{self._project_id}:appointed"
        total_wait = 0.0
        acquired = False
        identity = None
        while total_wait < self._max_block_time:  # wait up to max_block_time
            # operations below implement a atomic checking identity and setting a lock 
            # with optimistic locking
            self._sync_conn.watch(identity_key)
            identity = self._sync_conn.get(identity_key)
            if identity is not None:
                if self._identity is None or identity.decode() != self._identity:  # type: ignore
                    self._sync_conn.unwatch()
                    time.sleep(RETRY_INTERVAL)
                    total_wait += RETRY_INTERVAL
                    continue  # wait for appointed identity to acquire the lock
            with self._sync_conn.pipeline() as pipe:
                pipe.multi()
                for key in lock_keys:
                    pipe.set(key, "locked", nx=True)
                results = pipe.execute()
                if results and all(results):
                    acquired = True
                    break
                else:
                    for i, result in enumerate(results):
                        if result:
                            self._sync_conn.delete(lock_keys[i])
            total_wait += RETRY_INTERVAL
            time.sleep(RETRY_INTERVAL)
        if not acquired:
            logger.error(f"Failed to acquire lock for project {self._project_id} within {self._max_block_time} seconds.")
            raise ProjectLockError(f"Project {self._project_id} is already locked.")
        if identity is not None:
            # clear appointed identity after acquiring the lock
            identity_key = f"project_lock:{self._project_id}:appointed"
            self._sync_conn.delete(identity_key)
        else:
            if self._identity is not None:
                # get the lock, but not satisfy my identity. Because the identity can be expired, it tends that I will never got the right lock, so throw exception.
                self.release_sync() # release the lock, because the __exit__ may not be called
                logger.error(f"Project {self._project_id} lock identity does not match the appointed identity.")
                raise ProjLockIdentityError(
                    f"Project {self._project_id} lock identity does not match the appointed identity."
                )

    def release_sync(self) -> None:
        """
        Release the lock for the project.
        """
        if self._sync_conn is None:
            self._sync_conn = redis_sync.Redis.from_url(LOCK_REDIS_URL)
        # delete lock
        lock_keys = ProjectLock._get_lock_key(self._project_id, self._scope)
        for key in lock_keys:
            self._sync_conn.delete(key)

    def appoint_transfer_sync(self, identity: str) -> None:
        """
        Appoint a specific identity to transfer the lock.
        """
        if self._sync_conn is None:
            self._sync_conn = redis_sync.Redis.from_url(LOCK_REDIS_URL)
        key = f"project_lock:{self._project_id}:appointed"
        self._sync_conn.set(key, identity, ex=APPOINTED_LOCK_EXPIRY)