"""
Core scheduler implementation for ZScheduler
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Union, Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore

from ..tasks.task import Task
from ..events.event_emitter import EventEmitter
from .schedule_builder import ScheduleBuilder
from .schedule import Schedule

logger = logging.getLogger(__name__)

class Scheduler:
    """
    The main scheduler class that manages all scheduled tasks.

    Features:
    - Schedule OS commands and Python functions/classes/modules
    - One-time, recurring, and N-times schedules
    - Flexible time specifications (absolute dates, relative times, cron expressions)
    - Event-based architecture for monitoring and notifications
    """

    def __init__(self, job_store: Optional[Any] = None):
        """
        Initialize a new scheduler instance.

        Args:
            job_store: Optional custom job store, defaults to memory store
        """
        self._scheduler = BackgroundScheduler(
            jobstores={'default': job_store or MemoryJobStore()}
        )
        self._events = EventEmitter()
        self._schedules: Dict[str, Schedule] = {}
        self._running = False

    def schedule(self, target: Union[str, Callable, Any], *args, **kwargs) -> ScheduleBuilder:
        """
        Creates a schedule for the given target.

        Args:
            target: The target to schedule (command string, function, etc.)
            *args: Positional arguments to pass to the target function
            **kwargs: Keyword arguments to pass to the target function

        Returns:
            A ScheduleBuilder to configure the schedule

        Examples:
            >>> scheduler.schedule("echo Hello").daily_at("12:00")
            >>> scheduler.schedule(my_func, arg1, arg2).every(minutes=5)
        """
        return ScheduleBuilder(self, target, *args, **kwargs)

    def _add_schedule(self, schedule: Schedule) -> str:
        """
        Add a schedule to the scheduler.

        Args:
            schedule: The schedule to add

        Returns:
            The schedule ID
        """
        self._schedules[schedule.id] = schedule

        # Add to APScheduler
        job = self._scheduler.add_job(
            schedule.execute,
            schedule.trigger_type,
            **schedule.trigger_args,
            id=schedule.id,
            name=schedule.name or f"Task-{schedule.id[:8]}"
        )

        self._events.emit("schedule_added", schedule)
        return schedule.id

    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a schedule from the scheduler.

        Args:
            schedule_id: ID of the schedule to remove

        Returns:
            True if removed, False if not found
        """
        if schedule_id not in self._schedules:
            return False

        schedule = self._schedules.pop(schedule_id)
        self._scheduler.remove_job(schedule_id)
        self._events.emit("schedule_removed", schedule)
        return True

    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """
        Get a schedule by its ID.

        Args:
            schedule_id: ID of the schedule to retrieve

        Returns:
            The schedule if found, None otherwise
        """
        return self._schedules.get(schedule_id)

    def get_schedules(self) -> List[Schedule]:
        """
        Get all schedules.

        Returns:
            List of all schedules
        """
        return list(self._schedules.values())

    def pause_schedule(self, schedule_id: str) -> bool:
        """
        Pause a schedule.

        Args:
            schedule_id: ID of the schedule to pause

        Returns:
            True if paused, False if not found
        """
        if schedule_id not in self._schedules:
            return False

        self._scheduler.pause_job(schedule_id)
        schedule = self._schedules[schedule_id]
        schedule.paused = True
        self._events.emit("schedule_paused", schedule)
        return True

    def resume_schedule(self, schedule_id: str) -> bool:
        """
        Resume a paused schedule.

        Args:
            schedule_id: ID of the schedule to resume

        Returns:
            True if resumed, False if not found
        """
        if schedule_id not in self._schedules:
            return False

        self._scheduler.resume_job(schedule_id)
        schedule = self._schedules[schedule_id]
        schedule.paused = False
        self._events.emit("schedule_resumed", schedule)
        return True

    def start(self) -> None:
        """Start the scheduler"""
        if self._running:
            return

        self._scheduler.start()
        self._running = True
        self._events.emit("scheduler_started", self)

    def stop(self) -> None:
        """Stop the scheduler"""
        if not self._running:
            return

        self._scheduler.shutdown()
        self._running = False
        self._events.emit("scheduler_stopped", self)

    def on(self, event_name: str, callback: Callable) -> None:
        """
        Register an event listener.

        Args:
            event_name: Name of the event to listen for
            callback: Function to call when the event occurs
        """
        self._events.on(event_name, callback)

    @property
    def running(self) -> bool:
        """Whether the scheduler is running"""
        return self._running
