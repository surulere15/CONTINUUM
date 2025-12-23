"""
Task Scheduler

Goal-driven scheduling. Tasks serve goals, not the reverse.

ORCHESTRATION - Phase II.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
import heapq


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class TaskState(Enum):
    """Task execution state."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """A task in the scheduler."""
    task_id: str
    goal_id: str
    priority: TaskPriority
    action: str
    state: TaskState
    created_at: datetime
    scheduled_at: Optional[datetime]
    deadline: Optional[datetime]
    
    def __lt__(self, other: "ScheduledTask") -> bool:
        """Compare by priority for heap."""
        return self.priority.value < other.priority.value


class OrphanTaskError(Exception):
    """Raised when task has no goal."""
    pass


class DeadlineViolationError(Exception):
    """Raised when deadline would be violated."""
    pass


class TaskScheduler:
    """
    Goal-Driven Task Scheduler.
    
    Tasks serve goals. Goals drive scheduling.
    No task without purpose.
    """
    
    def __init__(self, max_concurrent: int = 10):
        """Initialize scheduler."""
        self._tasks: Dict[str, ScheduledTask] = {}
        self._queue: List[ScheduledTask] = []
        self._running: Dict[str, ScheduledTask] = {}
        self._max_concurrent = max_concurrent
        self._task_count = 0
    
    def schedule(
        self,
        goal_id: str,
        action: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        deadline: Optional[datetime] = None,
    ) -> ScheduledTask:
        """
        Schedule a task for a goal.
        
        Args:
            goal_id: Parent goal (required)
            action: Action to execute
            priority: Task priority
            deadline: Optional deadline
            
        Returns:
            ScheduledTask
            
        Raises:
            OrphanTaskError: If no goal
        """
        if not goal_id:
            raise OrphanTaskError(
                "Cannot schedule task without goal. "
                "Tasks serve goals."
            )
        
        task_id = f"task_{self._task_count}"
        self._task_count += 1
        
        task = ScheduledTask(
            task_id=task_id,
            goal_id=goal_id,
            priority=priority,
            action=action,
            state=TaskState.PENDING,
            created_at=datetime.utcnow(),
            scheduled_at=None,
            deadline=deadline,
        )
        
        self._tasks[task_id] = task
        heapq.heappush(self._queue, task)
        task.state = TaskState.SCHEDULED
        task.scheduled_at = datetime.utcnow()
        
        return task
    
    def dispatch(self) -> Optional[ScheduledTask]:
        """
        Dispatch next task for execution.
        
        Returns:
            Next task or None
        """
        if len(self._running) >= self._max_concurrent:
            return None
        
        while self._queue:
            task = heapq.heappop(self._queue)
            
            # Check deadline
            if task.deadline and datetime.utcnow() > task.deadline:
                task.state = TaskState.FAILED
                continue
            
            task.state = TaskState.RUNNING
            self._running[task.task_id] = task
            return task
        
        return None
    
    def complete(self, task_id: str, success: bool = True) -> None:
        """Mark task complete."""
        if task_id in self._running:
            task = self._running.pop(task_id)
            task.state = TaskState.COMPLETED if success else TaskState.FAILED
    
    def cancel(self, task_id: str) -> None:
        """Cancel a task."""
        if task_id in self._tasks:
            self._tasks[task_id].state = TaskState.CANCELLED
    
    def cancel_by_goal(self, goal_id: str) -> int:
        """Cancel all tasks for a goal."""
        count = 0
        for task in self._tasks.values():
            if task.goal_id == goal_id and task.state in (TaskState.PENDING, TaskState.SCHEDULED):
                task.state = TaskState.CANCELLED
                count += 1
        return count
    
    def schedule_orphan(self, *args, **kwargs) -> None:
        """FORBIDDEN: Schedule orphan task."""
        raise OrphanTaskError(
            "Orphan tasks are forbidden. "
            "All tasks must have a goal."
        )
    
    @property
    def pending_count(self) -> int:
        """Pending tasks."""
        return len(self._queue)
    
    @property
    def running_count(self) -> int:
        """Running tasks."""
        return len(self._running)
