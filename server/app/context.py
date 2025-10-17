"""
Application context management.
Handles the lifecycle of global service instances.
"""
import redis.asyncio as redis
from typing import Optional, AsyncGenerator
import os
from .services.websocket_service import WebSocketService
from .services.task_service import TaskService
import logging

logger = logging.getLogger(__name__)

# Get Redis URL from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

class AppContext:
    """Manages global service instances."""
    
    def __init__(self):
        self.redis_pool: Optional[redis.ConnectionPool] = None
        self.websocket_service: Optional[WebSocketService] = None
        self.task_service: Optional[TaskService] = None
    
    def initialize(self, celery_app):
        """Initializes all services."""
        logger.info("Initializing application context...")
        
        self.redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
        self.websocket_service = WebSocketService(self.redis_pool)
        self.task_service = TaskService(celery_app)
        
        logger.info("Application context initialized successfully.")
    
    async def startup(self):
        """Application startup callback."""
        if self.websocket_service:
            # This can be used to initialize any background tasks for the service
            pass
        logger.info("Application context started.")
    
    async def shutdown(self):
        """Application shutdown callback."""
        if self.redis_pool:
            await self.redis_pool.disconnect()
        logger.info("Application context shut down.")

# Global application context instance
app_context = AppContext()

async def get_redis_connection() -> AsyncGenerator[redis.Redis, None]:
    """Dependency to get a Redis connection from the pool."""
    conn = None
    if app_context.redis_pool is None:
        raise RuntimeError("Redis connection pool not initialized.")
    try:
        conn = redis.Redis(connection_pool=app_context.redis_pool)
        yield conn
    finally:
        if conn is not None:
            await conn.close()

def get_websocket_service() -> WebSocketService:
    """Dependency injection: get WebSocket service."""
    if app_context.websocket_service is None:
        raise RuntimeError("WebSocketService not initialized.")
    return app_context.websocket_service

def get_task_service() -> TaskService:
    """Dependency injection: get task service."""
    if app_context.task_service is None:
        raise RuntimeError("TaskService not initialized.")
    return app_context.task_service
