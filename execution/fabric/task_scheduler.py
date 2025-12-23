"""
Task Scheduler

Schedules and manages task execution with priority handling,
dependency resolution, and resource awareness.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import heapq


class TaskState(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    id: str
    priority: int
    dependencies: List[str]
    deadline: Optional[datetime]
    resource_requirements: Dict
    state: TaskState
    created_at: datetime


class TaskScheduler:
    """Schedules tasks with priority and dependencies."""
    
    def __init__(self, max_concurrent: int = 10):
        self._queue: List = []
        self._running: Dict[str, ScheduledTask] = {}
        self._completed: Dict[str, ScheduledTask] = {}
        self._max_concurrent = max_concurrent
    
    def submit(self, task: ScheduledTask) -> str:
        """Submit task to scheduler."""
        heapq.heappush(self._queue, (task.priority, task.created_at, task))
        return task.id
    
    def get_next(self) -> Optional[ScheduledTask]:
        """Get next task ready to run."""
        if len(self._running) >= self._max_concurrent:
            return None
        
        for i, (_, _, task) in enumerate(self._queue):
            if self._dependencies_met(task):
                self._queue.pop(i)
                heapq.heapify(self._queue)
                task.state = TaskState.RUNNING
                self._running[task.id] = task
                return task
        return None
    
    def complete(self, task_id: str, success: bool) -> None:
        """Mark task as complete."""
        if task_id in self._running:
            task = self._running.pop(task_id)
            task.state = TaskState.COMPLETED if success else TaskState.FAILED
            self._completed[task_id] = task
    
    def _dependencies_met(self, task: ScheduledTask) -> bool:
        """Check if task dependencies are satisfied."""
        return all(
            dep in self._completed and 
            self._completed[dep].state == TaskState.COMPLETED
            for dep in task.dependencies
        )
