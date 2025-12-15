import json
from enum import Enum
from typing import Any, Optional

import redis as redis_sync
import redis.asyncio as redis

from server.config import STREAMQUEUE_REDIS_URL
from server.config import STREAMQUEUE_TTL_SECONDS as STREAM_TTL_SECONDS


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

    def __init__(self, stream_name: str, maxlen: int = 1000):
        """
        Args:
            maxlen: Maximum number of messages to keep in each stream
        """
        self.stream_name = stream_name
        self.maxlen = maxlen
        self._async_conn: Optional[redis.Redis] = None
        self._sync_conn: Optional[redis_sync.Redis] = None
        self._position: str = "0-0" # "0-0" indicates reading from the start in redis
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
    
    # ======= Helper functions for distributed status management =======
    def _refresh_ttl_sync(self):
        if self._sync_conn is None:
            raise AssertionError("Must use 'with StreamQueue()' context manager")
        self._sync_conn.expire(f"{self.stream_name}:stream", STREAM_TTL_SECONDS)
        self._sync_conn.expire(f"{self.stream_name}:sender_finished", STREAM_TTL_SECONDS)
        self._sync_conn.expire(f"{self.stream_name}:reader_finished", STREAM_TTL_SECONDS)
    
    async def _refresh_ttl_async(self):
        if self._async_conn is None:
            raise AssertionError("Must use 'async with StreamQueue()' context manager")
        await self._async_conn.expire(f"{self.stream_name}:stream", STREAM_TTL_SECONDS)
        await self._async_conn.expire(f"{self.stream_name}:sender_finished", STREAM_TTL_SECONDS)
        await self._async_conn.expire(f"{self.stream_name}:reader_finished", STREAM_TTL_SECONDS)
        
    def _finish_sender_sync(self):
        """Mark the sender as finished in sync mode"""
        if self._sync_conn is None:
            raise AssertionError("Must use 'with StreamQueue()' context manager")
        self._sync_conn.set(f"{self.stream_name}:sender_finished", str(True))

    def _is_sender_finished_sync(self) -> bool:
        """Check if the sender is finished in sync mode"""
        if self._sync_conn is None:
            raise AssertionError("Must use 'with StreamQueue()' context manager")
        return self._sync_conn.get(f"{self.stream_name}:sender_finished") == "True"
    
    async def _finish_sender_async(self):
        """Mark the sender as finished in async mode"""
        if self._async_conn is None:
            raise AssertionError("Must use 'async with StreamQueue()' context manager")
        await self._async_conn.set(f"{self.stream_name}:sender_finished", str(True))

    async def _is_sender_finished_async(self) -> bool:
        """Check if the sender is finished in async mode"""
        if self._async_conn is None:
            raise AssertionError("Must use 'async with StreamQueue()' context manager")
        val = await self._async_conn.get(f"{self.stream_name}:sender_finished")
        return val == "True"
    
    def _finish_reader_sync(self):
        """Mark the reader as finished in sync mode"""
        if self._sync_conn is None:
            raise AssertionError("Must use 'with StreamQueue()' context manager")
        self._sync_conn.set(f"{self.stream_name}:reader_finished", str(True))

    def _is_reader_finished_sync(self) -> bool:
        """Check if the reader is finished in sync mode"""
        if self._sync_conn is None:
            raise AssertionError("Must use 'with StreamQueue()' context manager")
        return self._sync_conn.get(f"{self.stream_name}:reader_finished") == "True"

    async def _finish_reader_async(self):
        """Mark the reader as finished in async mode"""
        if self._async_conn is None:
            raise AssertionError("Must use 'async with StreamQueue()' context manager")
        await self._async_conn.set(f"{self.stream_name}:reader_finished", str(True))

    async def _is_reader_finished_async(self) -> bool:
        """Check if the reader is finished in async mode"""
        if self._async_conn is None:
            raise AssertionError("Must use 'async with StreamQueue()' context manager")
        val = await self._async_conn.get(f"{self.stream_name}:reader_finished")
        return val == "True"    
    
    def _try_cleanup_stream_sync(self):
        """Cleanup the stream if both sender and reader are finished (sync mode)"""
        if self._sync_conn is None:
            raise AssertionError("Must use 'with StreamQueue()' context manager")
        sender_finished = self._sync_conn.get(f"{self.stream_name}:sender_finished") == "True"
        reader_finished = self._sync_conn.get(f"{self.stream_name}:reader_finished") == "True"
        if sender_finished and reader_finished:
            self._sync_conn.delete(f"{self.stream_name}:stream")
            self._sync_conn.delete(f"{self.stream_name}:sender_finished")
            self._sync_conn.delete(f"{self.stream_name}:reader_finished")
        elif not sender_finished and reader_finished:
            raise RuntimeError("Inconsistent state: reader finished but sender not finished")
    
    async def _try_cleanup_stream_async(self):
        """Cleanup the stream if both sender and reader are finished (async mode)"""
        if self._async_conn is None:
            raise AssertionError("Must use 'async with StreamQueue()' context manager")
        sender_finished = await self._async_conn.get(f"{self.stream_name}:sender_finished") == "True"
        reader_finished = await self._async_conn.get(f"{self.stream_name}:reader_finished") == "True"
        if sender_finished and reader_finished:
            await self._async_conn.delete(f"{self.stream_name}:stream")
            await self._async_conn.delete(f"{self.stream_name}:sender_finished")
            await self._async_conn.delete(f"{self.stream_name}:reader_finished")
        elif not sender_finished and reader_finished:
            raise RuntimeError("Inconsistent state: reader finished but sender not finished")
    
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
            raise AssertionError("Must use 'async with StreamQueue()' context manager")
        if await self._is_sender_finished_async():
            raise RuntimeError("Cannot push message to a finished sending stream")
        
        if isinstance(message, dict):
            message = json.dumps(message)
        
        message_id = await self._async_conn.xadd(
            f"{self.stream_name}:stream",
            {"status": status.value, "data": message},
            maxlen=self.maxlen,
            approximate=True
        )
        await self._refresh_ttl_async()
        
        if status.is_finished():
            await self._finish_sender_async()
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
            raise AssertionError("Must use 'async with StreamQueue()' context manager")
        if await self._is_reader_finished_async():
            raise RuntimeError("Cannot read message from a finished reading stream")

        last_id = self._position
        resp = await self._async_conn.xread(
            {f"{self.stream_name}:stream": last_id},
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
        self._position = message_id
        # Update finished status
        if message_status.is_finished():
            await self._finish_reader_async()

        return message_status, message_data

    async def close(self):
        """Async: Close the Redis connection"""
        assert self._async_conn
        await self._refresh_ttl_async()
        await self._try_cleanup_stream_async()
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
            raise AssertionError("Must use 'with StreamQueue()' context manager")
        if self._is_sender_finished_sync():
            raise RuntimeError("Cannot push message to a finished sending stream")

        if isinstance(message, dict):
            message = json.dumps(message)
        
        message_id = self._sync_conn.xadd(
            f"{self.stream_name}:stream",
            {"status": status.value, "data": message},
            maxlen=self.maxlen,
            approximate=True
        )
        self._refresh_ttl_sync()

        if status.is_finished():
            self._finish_sender_sync()
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
            raise AssertionError("Must use 'with StreamQueue()' context manager")
        if self._is_reader_finished_sync():
            raise RuntimeError("Cannot read message from a finished reading stream")

        last_id = self._position
        resp = self._sync_conn.xread(
            {f"{self.stream_name}:stream": last_id},
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
        self._position = message_id
        # Update finished status
        if message_status.is_finished():
            self._finish_reader_sync()

        return message_status, message_data

    def close_sync(self):
        """Sync: Close the Redis connection"""
        assert self._sync_conn
        self._refresh_ttl_sync()
        self._try_cleanup_stream_sync()
        self._sync_conn.close()
        self._sync_conn = None
