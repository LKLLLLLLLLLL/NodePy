"""
Task execution service.
Encapsulates Celery task calls and provides a unified task management interface.
"""
from typing import Dict, Any
from celery import Celery
from celery.result import AsyncResult
import logging

logger = logging.getLogger(__name__)

class TaskService:
    """Service for submitting and managing Celery tasks."""
    
    def __init__(self, celery_app: Celery):
        """
        Initializes the task service.
        
        Args:
            celery_app: The Celery application instance.
        """
        self.celery_app = celery_app
    
    def submit_node_execution(
        self, 
        node_graph: Dict[str, Any],
        project_id: str,
        user_id: str
    ) -> str:
        """
        Submits a node graph execution task.
        
        Args:
            node_graph: The node graph data.
            project_id: The project ID.
            user_id: The user ID.
            
        Returns:
            The task ID.
        """
        from ...engine.task import execute_nodes_task
        
        task = execute_nodes_task.delay(
            node_graph=node_graph,
            project_id=project_id,
            user_id=user_id
        )
        
        logger.info(f"Submitted task {task.id} for user {user_id}, project {project_id}")
        return task.id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Gets the status of a task.
        
        Args:
            task_id: The task ID.
            
        Returns:
            Task status information.
        """
        result = AsyncResult(task_id, app=self.celery_app)
        
        return {
            "task_id": task_id,
            "state": result.state,
            "info": result.info if isinstance(result.info, dict) else {}
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancels a task.
        
        Args:
            task_id: The task ID.
            
        Returns:
            True if cancellation was successful.
        """
        result = AsyncResult(task_id, app=self.celery_app)
        result.revoke(terminate=True)
        logger.info(f"Task {task_id} cancelled")
        return True
