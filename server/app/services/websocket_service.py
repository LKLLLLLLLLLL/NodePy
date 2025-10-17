"""
WebSocket connection management service.
Handles the lifecycle of WebSocket connections and message broadcasting via Redis Pub/Sub.
"""
from fastapi import WebSocket
import redis.asyncio as redis
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class WebSocketService:
    """Manages WebSocket connections and broadcasts messages via Redis."""
    
    def __init__(self, redis_pool: redis.ConnectionPool):
        self._redis_pool = redis_pool
    
    async def connect(self, task_id: str, websocket: WebSocket) -> None:
        """
        Accepts a WebSocket connection, sends cached status, and listens for real-time updates.
        """
        await websocket.accept()
        logger.info(f"WebSocket connected for task: {task_id}")
        
        redis_conn = redis.Redis(connection_pool=self._redis_pool)
        pubsub = redis_conn.pubsub()
        
        status_key = f"task_status:{task_id}"
        channel = f"task:{task_id}"

        try:
            # 1. Send cached historical state first to avoid race conditions
            latest_message = await redis_conn.hget(status_key, "latest_message")
            if latest_message:
                await websocket.send_text(latest_message)
                logger.info(f"Sent cached status to task {task_id}")

            # 2. Subscribe to the channel for real-time updates
            await pubsub.subscribe(channel)
            
            # 3. Listen for new messages
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=60)
                if message:
                    data = message['data']
                    await websocket.send_text(data)
                    
                    try:
                        payload = json.loads(data)
                        if payload.get("state") in ["SUCCESS", "FAILURE"]:
                            logger.info(f"Task {task_id} finished. Closing WebSocket.")
                            break
                    except json.JSONDecodeError:
                        pass
                
                # Check if client is still connected
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                except (asyncio.TimeoutError, asyncio.CancelledError):
                    pass
                except Exception:
                    logger.warning(f"Client for task {task_id} disconnected.")
                    break
        
        finally:
            logger.info(f"Cleaning up resources for task {task_id}")
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await redis_conn.close()
            try:
                await websocket.close()
            except Exception:
                pass
