"""
Base Task class for ZScheduler
"""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Task(ABC):
    """
    Abstract base class for all task types.

    Tasks represent the actual work to be done when a schedule is triggered.
    Different task types handle different kinds of work (commands, Python functions, etc.).
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize a new task.

        Args:
            name: Optional name for the task
        """
        self.id = str(uuid.uuid4())
        self.name = name

    @abstractmethod
    def execute(self) -> Any:
        """
        Execute the task.

        This method is called when the schedule is triggered.

        Returns:
            The result of the task execution
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary for serialization.

        Returns:
            A dictionary representation of the task
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.__class__.__name__
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create a task from a dictionary representation.

        Args:
            data: Dictionary containing task data

        Returns:
            A new Task instance
        """
        pass
