"""
Service to update and broadcast task progress.
"""
import redis
import json
import logging
from celery import Task

logger = logging.getLogger(__name__)

class TaskUpdater:
    """
    Handles task state updates, caching, and broadcasting via Redis.
    """
    def __init__(self, task: Task, redis_conn: redis.Redis):
        self.task = task
        self.redis_conn = redis_conn
        self.task_id = task.request.id
        self.status_key = f"task_status:{self.task_id}"
        self.channel = f"task:{self.task_id}"

    def update(self, state: str, meta: dict):
        """
        Updates Celery state, caches the latest status in a Redis Hash,
        and publishes the update to a Redis Pub/Sub channel.
        """
        # 1. Update Celery's backend state
        self.task.update_state(state=state, meta=meta)

        # 2. Cache the latest full message
        message = json.dumps({"state": state, "info": meta})
        self.redis_conn.hset(self.status_key, "latest_message", message)
        # Set an expiration time for the cache to auto-clean old tasks
        self.redis_conn.expire(self.status_key, 3600)  # Expire in 1 hour

        # 3. Publish the update to the Pub/Sub channel
        self.redis_conn.publish(self.channel, message)
        logger.debug(f"Updated and published to {self.channel}: {message}")

    def set_final_state(self, state: str, meta: dict):
        """
        Sets the final state and ensures the last message is published.
        """
        self.update(state, meta)
        logger.info(f"Task {self.task_id} finished with state: {state}")
