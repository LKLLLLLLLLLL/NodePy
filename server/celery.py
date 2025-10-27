from celery import Celery
import os

"""
Shared configuration across deferrent container.
"""

celery_app = Celery(
    "nodepy",
    broker=os.getenv("REDIS_URL", "redis://redis:6379"),  # Message broker
    backend=os.getenv("REDIS_URL", "redis://redis:6379"),  # Result backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,  # Track task startup
    task_time_limit=30 * 60,  # Task timeout: 30 minutes
    task_soft_time_limit=25 * 60,  # Soft timeout: 25 minutes (warning)
    worker_prefetch_multiplier=1,  # Fetch one task at a time (avoid long task blocking)
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (prevent memory leaks)
    worker_send_task_events=True,  # Send task events
    include=["server.engine.task"],  # Explicitly include task modules
)

celery_app.conf.beat_schedule = {
    "cleanup-orphan-files-every-hour": {
        "task": "server.lib.FileManager.cleanup_orphan_files_task",
        "schedule": 3600.0,  # Every hour
        # "schedule": 60.0,  # Every minute (for testing purposes)
    },
}
