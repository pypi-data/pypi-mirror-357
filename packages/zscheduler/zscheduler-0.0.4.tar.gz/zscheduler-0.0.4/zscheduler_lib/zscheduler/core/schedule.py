"""
Schedule class for ZScheduler - represents a scheduled task
"""

import uuid
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ..tasks.task import Task

logger = logging.getLogger(__name__)

class Schedule:
    """
    Represents a scheduled task with execution metadata.

    A Schedule combines a Task with scheduling information and
    keeps track of execution history and status.
    """

    def __init__(
        self,
        task: Task,
        trigger_type: str,
        trigger_args: Dict[str, Any],
        name: Optional[str] = None,
        max_runs: Optional[int] = None
    ):
        """
        Initialize a new schedule.

        Args:
            task: The task to execute
            trigger_type: The trigger type (date, interval, cron)
            trigger_args: Arguments for the trigger
            name: Optional name for the schedule
            max_runs: Maximum number of times to run the task
        """
        self.id = str(uuid.uuid4())
        self.task = task
        self.name = name
        self.trigger_type = trigger_type
        self.trigger_args = trigger_args
        self.max_runs = max_runs

        self.created_at = datetime.now()
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.run_count = 0
        self.paused = False
        self.execution_history = []

    def execute(self) -> None:
        """
        Execute the scheduled task.

        This method is called by the scheduler when the trigger fires.
        It handles execution, error handling, and housekeeping.
        """
        if self.max_runs is not None and self.run_count >= self.max_runs:
            logger.info(f"Schedule {self.id} reached maximum runs ({self.max_runs}), skipping execution")
            return

        self.last_run = datetime.now()
        self.run_count += 1

        start_time = datetime.now()
        execution_id = str(uuid.uuid4())

        logger.info(f"Executing schedule {self.id} (run {self.run_count})")

        execution_record = {
            "id": execution_id,
            "start_time": start_time,
            "success": False,
            "error": None,
            "result": None,
            "duration": None
        }

        try:
            result = self.task.execute()
            execution_record["result"] = result
            execution_record["success"] = True

            logger.info(f"Schedule {self.id} executed successfully")

        except Exception as e:
            logger.exception(f"Error executing schedule {self.id}: {e}")
            execution_record["error"] = str(e)

        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            execution_record["end_time"] = end_time
            execution_record["duration"] = duration

            self.execution_history.append(execution_record)

            # Limit history size
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]

        return

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of this schedule.

        Returns:
            A dictionary containing the schedule status
        """
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "run_count": self.run_count,
            "paused": self.paused,
            "max_runs": self.max_runs,
            "trigger_type": self.trigger_type,
            "task_type": self.task.__class__.__name__,
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the schedule to a dictionary for serialization.

        Returns:
            A dictionary representation of the schedule
        """
        return {
            "id": self.id,
            "name": self.name,
            "task": self.task.to_dict(),
            "trigger_type": self.trigger_type,
            "trigger_args": self.trigger_args,
            "max_runs": self.max_runs,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "run_count": self.run_count,
            "paused": self.paused,
            "execution_history": [
                {
                    "id": record["id"],
                    "start_time": record["start_time"].isoformat() if record.get("start_time") else None,
                    "end_time": record["end_time"].isoformat() if record.get("end_time") else None,
                    "success": record["success"],
                    "error": record["error"],
                    "duration": record["duration"]
                }
                for record in self.execution_history[-10:]  # Only include the last 10 records
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], task_factory) -> 'Schedule':
        """
        Create a schedule from a dictionary representation.

        Args:
            data: Dictionary containing schedule data
            task_factory: Function to create a task from a dictionary

        Returns:
            A new Schedule instance
        """
        schedule = cls(
            task=task_factory(data["task"]),
            trigger_type=data["trigger_type"],
            trigger_args=data["trigger_args"],
            name=data.get("name"),
            max_runs=data.get("max_runs")
        )

        schedule.id = data["id"]
        schedule.created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        schedule.last_run = datetime.fromisoformat(data["last_run"]) if data.get("last_run") else None
        schedule.run_count = data.get("run_count", 0)
        schedule.paused = data.get("paused", False)

        # We don't restore execution history to save memory

        return schedule
