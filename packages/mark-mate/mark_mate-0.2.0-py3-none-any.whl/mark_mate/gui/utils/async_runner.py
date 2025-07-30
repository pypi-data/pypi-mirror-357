"""
Async task runner utilities for MarkMate GUI.

Provides utilities for running async operations with progress tracking and cancellation.
"""

import asyncio
import logging
from typing import Any, Callable, Optional, Dict
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class TaskRunner:
    """Utility class for running async tasks with progress tracking."""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    async def run_task(
        self,
        task_id: str,
        coro_func: Callable,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
        complete_callback: Optional[Callable[[Any], None]] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Run an async task with progress tracking.
        
        Args:
            task_id: Unique identifier for the task
            coro_func: Async function to run
            progress_callback: Function to call for progress updates
            error_callback: Function to call on error
            complete_callback: Function to call on completion
            *args, **kwargs: Arguments to pass to coro_func
            
        Returns:
            Task result
        """
        logger.info(f"Starting task: {task_id}")
        
        try:
            # Create the task
            task = asyncio.create_task(coro_func(*args, **kwargs))
            self.running_tasks[task_id] = task
            
            if progress_callback:
                progress_callback(f"Starting {task_id}...", 0.0)
            
            # Wait for completion
            result = await task
            
            if complete_callback:
                complete_callback(result)
            
            if progress_callback:
                progress_callback(f"{task_id} completed", 1.0)
            
            logger.info(f"Task completed successfully: {task_id}")
            return result
            
        except asyncio.CancelledError:
            logger.info(f"Task cancelled: {task_id}")
            if error_callback:
                error_callback(f"Task {task_id} was cancelled")
            raise
            
        except Exception as e:
            logger.error(f"Task failed: {task_id} - {str(e)}")
            if error_callback:
                error_callback(f"Task {task_id} failed: {str(e)}")
            raise
            
        finally:
            # Clean up
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.
        
        Args:
            task_id: ID of task to cancel
            
        Returns:
            True if task was cancelled, False if not found
        """
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()
            logger.info(f"Cancelled task: {task_id}")
            return True
        
        logger.warning(f"Task not found for cancellation: {task_id}")
        return False
    
    def cancel_all_tasks(self):
        """Cancel all running tasks."""
        for task_id in list(self.running_tasks.keys()):
            self.cancel_task(task_id)
    
    def get_running_tasks(self) -> list[str]:
        """Get list of currently running task IDs."""
        return list(self.running_tasks.keys())
    
    def is_task_running(self, task_id: str) -> bool:
        """Check if a specific task is running."""
        return task_id in self.running_tasks
    
    def __del__(self):
        """Cleanup executor on destruction."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)