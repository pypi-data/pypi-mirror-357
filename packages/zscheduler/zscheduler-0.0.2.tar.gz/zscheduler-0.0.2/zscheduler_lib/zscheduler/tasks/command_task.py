"""
CommandTask class for executing OS commands
"""

import subprocess
import logging
from typing import Any, Dict, Optional

from .task import Task

logger = logging.getLogger(__name__)

class CommandTask(Task):
    """
    Task for executing operating system commands.

    This task runs shell commands and captures their output.
    """

    def __init__(self, command: str, shell: bool = True, name: Optional[str] = None):
        """
        Initialize a new command task.

        Args:
            command: The command to execute
            shell: Whether to run the command in a shell
            name: Optional name for the task
        """
        super().__init__(name or f"Command: {command[:30]}...")
        self.command = command
        self.shell = shell

    def execute(self) -> Dict[str, Any]:
        """
        Execute the command.

        Returns:
            A dictionary with the command output and status
        """
        logger.info(f"Executing command: {self.command}")

        try:
            # Run the command and capture output
            result = subprocess.run(
                self.command,
                shell=self.shell,
                capture_output=True,
                text=True,
                check=False  # Don't raise an exception on non-zero exit code
            )

            # Collect the results
            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode

            logger.debug(f"Command completed with exit code {exit_code}")

            if exit_code != 0:
                logger.warning(f"Command failed with exit code {exit_code}: {stderr}")

            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr
            }

        except Exception as e:
            logger.exception(f"Error executing command: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e)
            }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary for serialization.

        Returns:
            A dictionary representation of the task
        """
        data = super().to_dict()
        data.update({
            "command": self.command,
            "shell": self.shell
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandTask':
        """
        Create a task from a dictionary representation.

        Args:
            data: Dictionary containing task data

        Returns:
            A new CommandTask instance
        """
        task = cls(
            command=data["command"],
            shell=data.get("shell", True),
            name=data.get("name")
        )

        if "id" in data:
            task.id = data["id"]

        return task
