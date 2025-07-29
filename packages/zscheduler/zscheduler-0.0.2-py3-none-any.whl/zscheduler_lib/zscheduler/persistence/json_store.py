"""
JSON storage implementation for persisting schedules
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

from ..core.schedule import Schedule
from ..tasks.task import Task
from ..tasks.command_task import CommandTask
from ..tasks.python_task import PythonTask

logger = logging.getLogger(__name__)

class JsonStore:
    """
    JSON-based storage for persisting schedules to disk.

    This class handles saving and loading schedules from a JSON file.
    """

    def __init__(self, file_path: str):
        """
        Initialize a new JSON store.

        Args:
            file_path: Path to the JSON file for storage
        """
        self.file_path = file_path
        self.makedirs()

    def makedirs(self) -> None:
        """Ensure the directory for the file exists."""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def save_schedules(self, schedules: List[Schedule]) -> None:
        """
        Save schedules to the JSON file.

        Args:
            schedules: List of schedules to save
        """
        try:
            data = {
                "version": 1,
                "schedules": [schedule.to_dict() for schedule in schedules]
            }

            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(schedules)} schedules to {self.file_path}")

        except Exception as e:
            logger.exception(f"Error saving schedules to {self.file_path}: {e}")

    def load_schedules(self) -> List[Schedule]:
        """
        Load schedules from the JSON file.

        Returns:
            List of loaded schedules
        """
        if not os.path.exists(self.file_path):
            logger.info(f"No schedules file found at {self.file_path}")
            return []

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)

            version = data.get("version", 1)
            schedules_data = data.get("schedules", [])

            schedules = []
            for schedule_data in schedules_data:
                try:
                    schedule = self._load_schedule(schedule_data)
                    schedules.append(schedule)
                except Exception as e:
                    logger.error(f"Error loading schedule {schedule_data.get('id')}: {e}")

            logger.info(f"Loaded {len(schedules)} schedules from {self.file_path}")
            return schedules

        except Exception as e:
            logger.exception(f"Error loading schedules from {self.file_path}: {e}")
            return []

    def _load_schedule(self, data: Dict[str, Any]) -> Schedule:
        """
        Load a single schedule from its dictionary representation.

        Args:
            data: Dictionary containing schedule data

        Returns:
            Loaded Schedule object
        """
        task_data = data["task"]
        task_type = task_data["type"]

        # Create the appropriate task type
        if task_type == "CommandTask":
            task = CommandTask.from_dict(task_data)
        elif task_type == "PythonTask":
            task = PythonTask.from_dict(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        # Create the schedule
        schedule = Schedule(
            task=task,
            trigger_type=data["trigger_type"],
            trigger_args=data["trigger_args"],
            name=data.get("name"),
            max_runs=data.get("max_runs")
        )

        # Set additional attributes
        schedule.id = data["id"]

        if data.get("created_at"):
            from datetime import datetime
            schedule.created_at = datetime.fromisoformat(data["created_at"])

        if data.get("last_run"):
            schedule.last_run = datetime.fromisoformat(data["last_run"])

        schedule.run_count = data.get("run_count", 0)
        schedule.paused = data.get("paused", False)

        return schedule
