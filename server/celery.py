
from celery import Celery

from server.config import (
    CELERY_REDIS_URL,
    CLEAN_ORPHAN_FILE_INTERVAL_SEC,
    FETCH_BACKWARD_INTERVAL_SEC,
    FETCH_FORWARD_INTERVAL_SEC,
    TASK_MAX_RUNNING_TIME_SEC,
)

"""
Shared configuration across deferrent container.
"""

celery_app = Celery(
    "nodepy",
    broker=CELERY_REDIS_URL,  # Message broker
    backend=CELERY_REDIS_URL,  # Result backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,  # Track task startup
    task_time_limit=TASK_MAX_RUNNING_TIME_SEC,
    task_soft_time_limit=0.9 * TASK_MAX_RUNNING_TIME_SEC,
    worker_prefetch_multiplier=1,  # Fetch one task at a time (avoid long task blocking)
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (prevent memory leaks)
    worker_send_task_events=True,  # Send task events
    include=[
        "server.interpreter.task",
        "server.lib.FinancialDataManager",
    ],  # Explicitly include task modules
)

celery_app.conf.beat_schedule = {
    "cleanup-orphan-files-every-hour": {
        "task": "server.lib.FileManager.cleanup_soft_deleted_files_task",
        "schedule": CLEAN_ORPHAN_FILE_INTERVAL_SEC,
        # "schedule": 60.0,  # Every 60 seconds (for testing purposes)
    },
    "update-forward-every-5-minutes": {
        "task": "server.lib.FinancialDataManager.update_forward_task",
        "schedule": FETCH_FORWARD_INTERVAL_SEC,
        # "schedule": 60.0,  # Every 1 minute (for testing purposes)
    },
    "backfill-history-every-hour": {
        "task": "server.lib.FinancialDataManager.backfill_history_task",
        "schedule": FETCH_BACKWARD_INTERVAL_SEC,
        # "schedule": 120.0,  # Every 2 minutes (for testing purposes)
    },
}
