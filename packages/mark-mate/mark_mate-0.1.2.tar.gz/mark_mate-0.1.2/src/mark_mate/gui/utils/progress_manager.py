"""
Progress management utilities for MarkMate GUI.

Provides progress tracking and UI updates for long-running operations.
"""

import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

import flet as ft


@dataclass
class ProgressState:
    """State information for a progress operation."""
    task_id: str
    message: str
    progress: float  # 0.0 to 1.0
    start_time: float
    is_error: bool = False
    is_complete: bool = False


class ProgressManager:
    """Manages progress tracking and UI updates for async operations."""
    
    def __init__(self):
        self.progress_states: Dict[str, ProgressState] = {}
        self.ui_callbacks: Dict[str, Callable[[ProgressState], None]] = {}
    
    def start_progress(
        self, 
        task_id: str, 
        initial_message: str = "Starting...",
        ui_callback: Optional[Callable[[ProgressState], None]] = None,
    ) -> Callable[[str, float], None]:
        """
        Start tracking progress for a task.
        
        Args:
            task_id: Unique task identifier
            initial_message: Initial progress message
            ui_callback: Function to call for UI updates
            
        Returns:
            Progress update function
        """
        state = ProgressState(
            task_id=task_id,
            message=initial_message,
            progress=0.0,
            start_time=time.time(),
        )
        
        self.progress_states[task_id] = state
        
        if ui_callback:
            self.ui_callbacks[task_id] = ui_callback
            ui_callback(state)
        
        def update_progress(message: str, progress: float):
            """Update progress for this task."""
            self.update_progress(task_id, message, progress)
        
        return update_progress
    
    def update_progress(self, task_id: str, message: str, progress: float):
        """Update progress for a specific task."""
        if task_id in self.progress_states:
            state = self.progress_states[task_id]
            state.message = message
            state.progress = max(0.0, min(1.0, progress))  # Clamp to 0-1
            
            # Check if complete
            if progress >= 1.0:
                state.is_complete = True
            
            # Notify UI callback
            if task_id in self.ui_callbacks:
                self.ui_callbacks[task_id](state)
    
    def set_error(self, task_id: str, error_message: str):
        """Mark a task as having an error."""
        if task_id in self.progress_states:
            state = self.progress_states[task_id]
            state.message = error_message
            state.is_error = True
            
            # Notify UI callback
            if task_id in self.ui_callbacks:
                self.ui_callbacks[task_id](state)
    
    def complete_progress(self, task_id: str, final_message: str = "Complete!"):
        """Mark a task as complete."""
        if task_id in self.progress_states:
            state = self.progress_states[task_id]
            state.message = final_message
            state.progress = 1.0
            state.is_complete = True
            
            # Notify UI callback
            if task_id in self.ui_callbacks:
                self.ui_callbacks[task_id](state)
    
    def get_elapsed_time(self, task_id: str) -> Optional[float]:
        """Get elapsed time for a task in seconds."""
        if task_id in self.progress_states:
            return time.time() - self.progress_states[task_id].start_time
        return None
    
    def get_eta(self, task_id: str) -> Optional[float]:
        """Get estimated time remaining for a task in seconds."""
        if task_id in self.progress_states:
            state = self.progress_states[task_id]
            if state.progress > 0:
                elapsed = self.get_elapsed_time(task_id)
                if elapsed:
                    total_estimated = elapsed / state.progress
                    return max(0, total_estimated - elapsed)
        return None
    
    def cleanup_task(self, task_id: str):
        """Clean up progress tracking for a completed task."""
        self.progress_states.pop(task_id, None)
        self.ui_callbacks.pop(task_id, None)
    
    def get_all_active_tasks(self) -> Dict[str, ProgressState]:
        """Get all currently active (not complete) tasks."""
        return {
            task_id: state 
            for task_id, state in self.progress_states.items()
            if not state.is_complete
        }


class ProgressDialog(ft.UserControl):
    """A modal dialog for showing progress of long-running operations."""
    
    def __init__(
        self, 
        title: str = "Processing...",
        cancellable: bool = True,
        on_cancel: Optional[Callable[[], None]] = None,
    ):
        super().__init__()
        self.title = title
        self.cancellable = cancellable
        self.on_cancel = on_cancel
        
        self.message = "Starting..."
        self.progress = 0.0
        self.is_error = False
        
        # UI components
        self.progress_bar = ft.ProgressBar(value=0.0, width=400)
        self.message_text = ft.Text(self.message, size=14)
        self.cancel_button = ft.ElevatedButton(
            "Cancel",
            on_click=self.handle_cancel,
            disabled=not cancellable,
        )
    
    def build(self):
        """Build the progress dialog UI."""
        return ft.AlertDialog(
            modal=True,
            title=ft.Text(self.title),
            content=ft.Container(
                content=ft.Column([
                    self.message_text,
                    ft.Container(height=10),
                    self.progress_bar,
                ], 
                tight=True),
                width=400,
                padding=ft.padding.all(20),
            ),
            actions=[
                self.cancel_button,
            ] if self.cancellable else [],
        )
    
    def update_progress(self, state: ProgressState):
        """Update the dialog with new progress state."""
        self.message = state.message
        self.progress = state.progress
        self.is_error = state.is_error
        
        # Update UI components
        self.message_text.value = self.message
        self.progress_bar.value = self.progress
        
        # Change color for errors
        if self.is_error:
            self.progress_bar.color = ft.Colors.RED
            self.message_text.color = ft.Colors.RED
        else:
            self.progress_bar.color = ft.Colors.BLUE
            self.message_text.color = ft.Colors.BLACK
        
        # Update UI
        self.update()
    
    def handle_cancel(self, e):
        """Handle cancel button click."""
        if self.on_cancel:
            self.on_cancel()
    
    def show(self, page: ft.Page):
        """Show the dialog."""
        page.dialog = self
        self.open = True
        page.update()
    
    def hide(self, page: ft.Page):
        """Hide the dialog."""
        self.open = False
        page.update()