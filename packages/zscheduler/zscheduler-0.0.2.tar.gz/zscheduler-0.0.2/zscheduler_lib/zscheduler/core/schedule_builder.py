"""
Schedule builder for ZScheduler - provides fluent API for schedule configuration
"""

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union, TYPE_CHECKING

import dateutil.parser
from croniter import croniter

from ..tasks.task import Task
from ..tasks.command_task import CommandTask
from ..tasks.python_task import PythonTask
from .schedule import Schedule

if TYPE_CHECKING:
    from .scheduler import Scheduler

class ScheduleBuilder:
    """
    Fluent API for building schedules.

    This class provides a fluent interface for configuring schedules,
    allowing for readable and concise schedule definitions.
    """

    def __init__(self, scheduler: 'Scheduler', target: Union[str, Callable, Any], *args, **kwargs):
        """
        Initialize a new schedule builder.

        Args:
            scheduler: The scheduler instance
            target: The target to schedule (command string, function, etc.)
            *args: Positional arguments to pass to the target function
            **kwargs: Keyword arguments to pass to the target function
        """
        self._scheduler = scheduler
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self._task = self._create_task(target, *args, **kwargs)
        self._name: Optional[str] = None
        self._trigger_type: str = "date"
        self._trigger_args: Dict[str, Any] = {}
        self._max_runs: Optional[int] = None

    def _create_task(self, target: Union[str, Callable, Any], *args, **kwargs) -> Task:
        """
        Create a task for the given target.

        Args:
            target: The target to schedule
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            A Task instance suitable for the target
        """
        if isinstance(target, str):
            return CommandTask(target)
        else:
            return PythonTask(target, *args, **kwargs)

    def _build_schedule(self) -> str:
        """
        Build and add the schedule to the scheduler.

        Returns:
            The schedule ID
        """
        schedule = Schedule(
            task=self._task,
            name=self._name,
            trigger_type=self._trigger_type,
            trigger_args=self._trigger_args,
            max_runs=self._max_runs
        )
        return self._scheduler._add_schedule(schedule)

    def name(self, name: str) -> 'ScheduleBuilder':
        """
        Set a name for this schedule.

        Args:
            name: The schedule name

        Returns:
            Self for method chaining
        """
        self._name = name
        return self

    def at(self, dt: Union[str, datetime]) -> str:
        """
        Schedule to run once at a specific date and time.

        Args:
            dt: The date and time to run (string or datetime)

        Returns:
            The schedule ID
        """
        if isinstance(dt, str):
            dt = dateutil.parser.parse(dt)

        self._trigger_type = "date"
        self._trigger_args = {"run_date": dt}
        return self._build_schedule()

    def after(self, **kwargs) -> str:
        """
        Schedule to run once after a specified time interval.

        Args:
            **kwargs: Time interval (seconds, minutes, hours, days, weeks)

        Returns:
            The schedule ID

        Examples:
            >>> scheduler.schedule(func).after(minutes=5)
            >>> scheduler.schedule(func).after(hours=2, minutes=30)
        """
        delta = timedelta(**kwargs)
        run_date = datetime.now() + delta

        self._trigger_type = "date"
        self._trigger_args = {"run_date": run_date}
        return self._build_schedule()

    def every(self, **kwargs) -> 'ScheduleBuilder':
        """
        Schedule to run at a regular interval.

        Args:
            **kwargs: Interval (seconds, minutes, hours, days, weeks)

        Returns:
            Self for method chaining

        Examples:
            >>> scheduler.schedule(func).every(minutes=5).start_now()
            >>> scheduler.schedule(func).every(hours=1).repeat(5)
        """
        self._trigger_type = "interval"
        self._trigger_args = kwargs
        return self

    def start_now(self) -> str:
        """
        Start the recurring schedule immediately.

        Returns:
            The schedule ID
        """
        return self._build_schedule()

    def start_at(self, dt: Union[str, datetime]) -> str:
        """
        Start the recurring schedule at a specific time.

        Args:
            dt: Start date/time (string or datetime)

        Returns:
            The schedule ID
        """
        if isinstance(dt, str):
            dt = dateutil.parser.parse(dt)

        self._trigger_args["start_date"] = dt
        return self._build_schedule()

    def repeat(self, count: int) -> 'ScheduleBuilder':
        """
        Set a maximum number of times to run.

        Args:
            count: Maximum number of runs

        Returns:
            Self for method chaining
        """
        self._max_runs = count
        return self

    def cron(self, expr: str) -> str:
        """
        Schedule using a cron expression.

        Args:
            expr: Cron expression (e.g., "0 12 * * *" for daily at noon)

        Returns:
            The schedule ID
        """
        if not croniter.is_valid(expr):
            raise ValueError(f"Invalid cron expression: {expr}")

        self._trigger_type = "cron"

        # Parse the cron expression into APScheduler arguments
        parts = expr.split()
        if len(parts) == 5:
            minute, hour, day, month, day_of_week = parts
        elif len(parts) == 6:
            minute, hour, day, month, day_of_week, year = parts
        else:
            raise ValueError("Invalid cron expression format")

        self._trigger_args = {
            "minute": minute,
            "hour": hour,
            "day": day,
            "month": month,
            "day_of_week": day_of_week
        }

        if len(parts) == 6:
            self._trigger_args["year"] = year

        return self._build_schedule()

    def daily_at(self, time_str: str) -> str:
        """
        Schedule to run daily at a specific time.

        Args:
            time_str: Time in "HH:MM" format

        Returns:
            The schedule ID
        """
        hour, minute = time_str.split(":")

        self._trigger_type = "cron"
        self._trigger_args = {
            "minute": minute,
            "hour": hour,
            "day": "*",
            "month": "*",
            "day_of_week": "*"
        }

        return self._build_schedule()

    def weekly_on(self, day: Union[int, str], time: str) -> str:
        """
        Schedule to run weekly on a specific day and time.

        Args:
            day: Day of the week (0-6 or name like "mon", "tue")
            time: Time in "HH:MM" format

        Returns:
            The schedule ID
        """
        hour, minute = time.split(":")

        self._trigger_type = "cron"
        self._trigger_args = {
            "minute": minute,
            "hour": hour,
            "day": "*",
            "month": "*",
            "day_of_week": str(day)
        }

        return self._build_schedule()

    def monthly_on(self, day: int, time: str) -> str:
        """
        Schedule to run monthly on a specific day and time.

        Args:
            day: Day of the month (1-31)
            time: Time in "HH:MM" format

        Returns:
            The schedule ID
        """
        hour, minute = time.split(":")

        self._trigger_type = "cron"
        self._trigger_args = {
            "minute": minute,
            "hour": hour,
            "day": str(day),
            "month": "*",
            "day_of_week": "*"
        }

        return self._build_schedule()
