import redis.asyncio as redis
import redis as redis_sync
import os
import json
from typing import Any, Optional
from enum import Enum

STREAMQUEUE_REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379") + "/1"

class Status(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    IN_PROGRESS = "in_progress"
    TIMEOUT = "timeout"
    
    def is_finished(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILURE}

class StreamQueue:
    """
    A simple wrapper around Redis Streams that supports both sync and async usage.
    
    Usage (Async):
        async with StreamQueue() as queue:
            await queue.push_message("message")
            msg = await queue.read_message()

    Usage (Sync):
        with StreamQueue() as queue:
            queue.push_message_sync("message")
            msg = queue.read_message_sync()
    """
    # shared members between all instances
    _positions: dict[str, str] = {}  # Track read positions per stream
    _finished: dict[str, bool] = {}  # Track finished status per stream

    def __init__(self, stream_name: str, maxlen: int = 1000):
        """
        Args:
            maxlen: Maximum number of messages to keep in each stream
        """
        self.stream_name = stream_name
        self.maxlen = maxlen
        self._async_conn: Optional[redis.Redis] = None
        self._sync_conn: Optional[redis_sync.Redis] = None
        self._is_async_context = False
    
    # ========== Context Manager Support (Async) ==========
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._async_conn = redis.from_url(STREAMQUEUE_REDIS_URL, decode_responses=True)
        self._is_async_context = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    # ========== Context Manager Support (Sync) ==========
    
    def __enter__(self):
        """Sync context manager entry"""
        self._sync_conn = redis_sync.from_url(STREAMQUEUE_REDIS_URL, decode_responses=True)
        self._is_async_context = False
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit"""
        self.close_sync()
    
    # ========== Async Methods ==========
    
    async def push_message(self, status: Status, message: str | dict[str, Any]) -> str:
        """
        Async: Pushes a message to the specified Redis Stream.
        
        Args:
            stream_key: The Redis stream key
            message: The message content (string or dict)
            
        Returns:
            The ID of the added message
        """
        if self._async_conn is None:
            raise RuntimeError("Must use 'async with StreamQueue()' context manager")
        if self._finished.get(self.stream_name):
            raise RuntimeError("Cannot push message to a finished stream")
        
        if isinstance(message, dict):
            message = json.dumps(message)
        
        message_id = await self._async_conn.xadd(
            self.stream_name,
            {"status": status.value, "data": message},
            maxlen=self.maxlen,
            approximate=True
        )
        return message_id

    async def read_message(self, timeout_ms: int = 60000) -> tuple[Status, str | None]:
        """
        Async: Reads the next message from the specified Redis Stream.
        Automatically tracks position.
        
        Args:
            stream_key: The Redis stream key
            timeout_ms: Timeout in milliseconds (default 60s)
            
        Returns:
            The message content or None if timeout
        """
        if self._async_conn is None:
            raise RuntimeError("Must use 'async with StreamQueue()' context manager")
        if self._finished.get(self.stream_name):
            raise RuntimeError("Cannot read message from a finished stream")

        last_id = self._positions.get(self.stream_name, "0-0")
        resp = await self._async_conn.xread(
            {self.stream_name: last_id},
            count=1,
            block=timeout_ms
        )
        
        if not resp:
            return Status.TIMEOUT, None

        _, messages = resp[0]
        if not messages:
            raise RuntimeError("Unexpected empty message list")
        
        message_id, fields = messages[0]
        message_status = Status(fields.get("status"))
        message_data = fields.get("data")
        
        # Update position for next read
        self._positions[self.stream_name] = message_id
        # Update finished status
        if message_status.is_finished():
            self._finished[self.stream_name] = True

        return message_status, message_data

    async def close(self):
        """Async: Close the Redis connection"""
        assert self._async_conn
        if self._finished.get(self.stream_name):
            self._async_conn.delete(self.stream_name) # Clean up stream if finished
        await self._async_conn.close()
        self._async_conn = None
    
    # ========== Sync Methods ==========
    
    def push_message_sync(self, status: Status, message: str | dict[str, Any]) -> str:
        """
        Sync: Pushes a message to the specified Redis Stream.
        
        Args:
            stream_key: The Redis stream key
            message: The message content (string or dict)
            
        Returns:
            The ID of the added message
        """
        if self._sync_conn is None:
            raise RuntimeError("Must use 'with StreamQueue()' context manager")
        if self._finished.get(self.stream_name):
            raise RuntimeError("Cannot push message to a finished stream")
        
        if isinstance(message, dict):
            message = json.dumps(message)
        
        message_id = self._sync_conn.xadd(
            self.stream_name,
            {"status": status.value, "data": message},
            maxlen=self.maxlen,
            approximate=True
        )
        return str(message_id)

    def read_message_sync(self, timeout_ms: int = 60000) -> tuple[Status, str | None]:
        """
        Sync: Reads the next message from the specified Redis Stream.
        Automatically tracks position.
        
        Args:
            stream_key: The Redis stream key
            timeout_ms: Timeout in milliseconds (default 60s)
            
        Returns:
            The message content or None if timeout
        """
        if self._sync_conn is None:
            raise RuntimeError("Must use 'with StreamQueue()' context manager")
        if self._finished.get(self.stream_name):
            raise RuntimeError("Cannot read message from a finished stream")

        last_id = self._positions.get(self.stream_name, "0-0")
        resp = self._sync_conn.xread(
            {self.stream_name: last_id},
            count=1,
            block=timeout_ms
        )
        
        if not resp:
            return Status.TIMEOUT, None

        assert isinstance(resp, list)
        _, messages = resp[0]
        if not messages:
            raise RuntimeError("Unexpected empty message list")
        
        message_id, fields = messages[0]
        message_status = Status(fields.get("status"))
        message_data = fields.get("data")
        
        # Update position for next read
        self._positions[self.stream_name] = message_id
        # Update finished status
        if message_status.is_finished():
            self._finished[self.stream_name] = True

        return message_status, message_data

    def close_sync(self):
        """Sync: Close the Redis connection"""
        assert self._sync_conn
        if self._finished.get(self.stream_name):
            self._sync_conn.delete(self.stream_name) # Clean up stream if finished
        self._sync_conn.close()
        self._sync_conn = None
    
    def reset_position(self):
        """Reset the read position for a stream (works for both sync and async)"""
        if self.stream_name in self._positions:
            del self._positions[self.stream_name]
