"""
Scheduler implementation for ZScheduler application
"""

import time
import uuid
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)

class Schedule:
    """
    Represents a scheduled task
    """

    def __init__(self, name: str, command: str, schedule_type: str, interval: int = 0,
                 cron_expression: str = "", enabled: bool = True):
        """
        Initialize a schedule

        Args:
            name: The name of the schedule
            command: The command to execute
            schedule_type: Type of schedule ('interval', 'cron', 'once')
            interval: Interval in seconds (for interval type)
            cron_expression: Cron expression (for cron type)
            enabled: Whether the schedule is enabled
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.command = command
        self.schedule_type = schedule_type
        self.interval = interval
        self.cron_expression = cron_expression
        self.enabled = enabled
        self.last_run = None
        self.next_run = None
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.paused = False
        self.created_at = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()

        # Calculate next run time
        self._calculate_next_run()

    def _calculate_next_run(self):
        """Calculate the next run time based on the schedule type"""
        now = datetime.now()

        if self.schedule_type == "interval":
            next_run_time = now + timedelta(seconds=self.interval)
            self.next_run = next_run_time.isoformat()
        elif self.schedule_type == "once":
            # For 'once' schedules, the cron_expression contains the timestamp
            try:
                # Handle potential SingleDate objects by converting to string first
                if hasattr(self.cron_expression, "isoformat"):
                    self.cron_expression = self.cron_expression.isoformat()

                run_time = datetime.fromisoformat(self.cron_expression)
                if run_time > now:
                    self.next_run = self.cron_expression
                else:
                    self.next_run = None
            except (ValueError, TypeError, AttributeError) as e:
                logger.error("Invalid timestamp for once schedule: " + str(self.cron_expression) + " - " + str(e))
                self.next_run = None
        else:
            # For cron schedules, we would calculate the next run time using a cron parser
            # This is a simplified implementation that just sets it to 1 hour ahead
            next_run_time = now + timedelta(hours=1)
            self.next_run = next_run_time.isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the schedule to a dictionary

        Returns:
            Dictionary representation of the schedule
        """
        return {
            "id": self.id,
            "name": self.name,
            "command": self.command,
            "schedule_type": self.schedule_type,
            "interval": self.interval,
            "cron_expression": self.cron_expression,
            "enabled": self.enabled,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "paused": self.paused,
            "created_at": self.created_at,
            "last_modified": self.last_modified
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        """
        Create a schedule from a dictionary

        Args:
            data: Dictionary representation of a schedule

        Returns:
            Schedule instance
        """
        schedule = cls(
            name=data.get("name", "Unnamed Schedule"),
            command=data.get("command", ""),
            schedule_type=data.get("schedule_type", "interval"),
            interval=data.get("interval", 0),
            cron_expression=data.get("cron_expression", ""),
            enabled=data.get("enabled", True)
        )

        # Set additional properties
        schedule.id = data.get("id", schedule.id)
        schedule.last_run = data.get("last_run")
        schedule.next_run = data.get("next_run")
        schedule.execution_count = data.get("execution_count", 0)
        schedule.success_count = data.get("success_count", 0)
        schedule.failure_count = data.get("failure_count", 0)
        schedule.paused = data.get("paused", False)
        schedule.created_at = data.get("created_at", schedule.created_at)
        schedule.last_modified = data.get("last_modified", schedule.last_modified)

        # Calculate next run time if needed
        if not schedule.next_run:
            schedule._calculate_next_run()

        return schedule


class Scheduler:
    """
    Main scheduler class for ZScheduler
    """

    def __init__(self):
        """Initialize the scheduler"""
        self.schedules: Dict[str, Schedule] = {}
        self.running = False
        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

        # Callbacks
        self._on_schedule_run = None
        self._on_schedule_complete = None

    def start(self) -> bool:
        """
        Start the scheduler

        Returns:
            True if started, False otherwise
        """
        with self._lock:
            if self.running:
                logger.warning("Scheduler is already running")
                return False

            self.running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            logger.info("Scheduler started")
            return True

    def stop(self) -> bool:
        """
        Stop the scheduler

        Returns:
            True if stopped, False otherwise
        """
        with self._lock:
            if not self.running:
                logger.warning("Scheduler is not running")
                return False

            self.running = False
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                logger.info("Waiting for scheduler thread to stop...")
                self._thread.join(timeout=5.0)  # Increased timeout
                if self._thread.is_alive():
                    logger.warning("Scheduler thread did not stop within timeout")
                else:
                    logger.info("Scheduler thread stopped successfully")
            logger.info("Scheduler stopped")
            return True

    def is_running(self) -> bool:
        """
        Check if the scheduler is running

        Returns:
            True if running, False otherwise
        """
        return self.running

    def add_schedule(self, schedule_data: Dict[str, Any]) -> str:
        """
        Add a schedule

        Args:
            schedule_data: Schedule data dictionary

        Returns:
            ID of the added schedule
        """
        with self._lock:
            schedule = Schedule.from_dict(schedule_data)
            self.schedules[schedule.id] = schedule
            logger.info("Added schedule: " + schedule.name + " (ID: " + schedule.id + ")")
            return schedule.id

    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a schedule

        Args:
            schedule_id: ID of the schedule to remove

        Returns:
            True if removed, False otherwise
        """
        with self._lock:
            if schedule_id in self.schedules:
                del self.schedules[schedule_id]
                logger.info("Removed schedule with ID: " + schedule_id)
                return True
            return False

    def update_schedule(self, schedule_id: str, schedule_data: Dict[str, Any]) -> bool:
        """
        Update a schedule

        Args:
            schedule_id: ID of the schedule to update
            schedule_data: New schedule data

        Returns:
            True if updated, False otherwise
        """
        with self._lock:
            if schedule_id not in self.schedules:
                logger.warning("Cannot update non-existent schedule: " + schedule_id)
                return False

            # Preserve the ID
            schedule_data["id"] = schedule_id

            # Create new schedule and replace the old one
            schedule = Schedule.from_dict(schedule_data)
            schedule.last_modified = datetime.now().isoformat()
            self.schedules[schedule_id] = schedule

            logger.info(f"Updated schedule: {schedule.name} (ID: {schedule_id})")
            return True

    def get_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a schedule by ID

        Args:
            schedule_id: ID of the schedule

        Returns:
            Schedule dictionary or None if not found
        """
        with self._lock:
            if schedule_id in self.schedules:
                return self.schedules[schedule_id].to_dict()
            return None

    def get_schedules(self) -> List[Dict[str, Any]]:
        """
        Get all schedules

        Returns:
            List of schedule dictionaries
        """
        with self._lock:
            return [schedule.to_dict() for schedule in self.schedules.values()]

    def pause_schedule(self, schedule_id: str) -> bool:
        """
        Pause a schedule

        Args:
            schedule_id: ID of the schedule to pause

        Returns:
            True if paused, False otherwise
        """
        with self._lock:
            if schedule_id in self.schedules:
                self.schedules[schedule_id].paused = True
                logger.info(f"Paused schedule: {self.schedules[schedule_id].name}")
                return True
            return False

    def resume_schedule(self, schedule_id: str) -> bool:
        """
        Resume a paused schedule

        Args:
            schedule_id: ID of the schedule to resume

        Returns:
            True if resumed, False otherwise
        """
        with self._lock:
            if schedule_id in self.schedules:
                self.schedules[schedule_id].paused = False
                logger.info(f"Resumed schedule: {self.schedules[schedule_id].name}")
                return True
            return False

    def set_on_schedule_run_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set callback for when a schedule is about to run

        Args:
            callback: Function to call with schedule ID as argument
        """
        self._on_schedule_run = callback

    def set_on_schedule_complete_callback(self, callback: Callable[[str, bool], None]) -> None:
        """
        Set callback for when a schedule completes

        Args:
            callback: Function to call with schedule ID and success status as arguments
        """
        self._on_schedule_complete = callback

    def _run_loop(self) -> None:
        """Main scheduler loop"""
        logger.info("Scheduler loop started")

        while not self._stop_event.is_set():
            self._check_schedules()
            time.sleep(1)

        logger.info("Scheduler loop ended")

    def _check_schedules(self) -> None:
        """Check schedules for execution"""
        now = datetime.now()

        with self._lock:
            for schedule_id, schedule in list(self.schedules.items()):
                # Skip disabled or paused schedules
                if not schedule.enabled or schedule.paused:
                    continue

                # Check if it's time to run
                if schedule.next_run:
                    try:
                        next_run_time = datetime.fromisoformat(schedule.next_run)
                        if next_run_time <= now:
                            # Execute the schedule
                            self._execute_schedule(schedule_id)
                    except (ValueError, TypeError) as e:
                        logger.error("Error parsing next_run time for schedule " + schedule_id + ": " + str(e))
                        # Reset the next run time
                        schedule._calculate_next_run()

    def _execute_schedule(self, schedule_id: str) -> None:
        """
        Execute a schedule

        Args:
            schedule_id: ID of the schedule to execute
        """
        with self._lock:
            if schedule_id not in self.schedules:
                return

            schedule = self.schedules[schedule_id]

            # Notify that the schedule is about to run
            if self._on_schedule_run:
                try:
                    self._on_schedule_run(schedule_id)
                except Exception as e:
                    logger.error("Error in on_schedule_run callback: " + str(e))

            logger.info("Executing schedule: " + schedule.name + " (ID: " + schedule_id + ")")

            # Update statistics
            schedule.last_run = datetime.now().isoformat()
            schedule.execution_count += 1

            # Actually execute the command
            success = True
            try:
                logger.debug("Executing command: " + schedule.command)

                # Try to parse as JSON first (for structured commands)
                try:
                    import json
                    cmd_data = json.loads(schedule.command)

                    # Handle Python tasks
                    if isinstance(cmd_data, dict) and cmd_data.get("type") == "python":
                        module_name = cmd_data["module"]
                        function_name = cmd_data["function"]
                        args_list = cmd_data.get("args", [])
                        kwargs_dict = cmd_data.get("kwargs", {})

                        logger.info(f"Executing Python function: {module_name}.{function_name}")

                        # Import the module and get the function
                        import importlib
                        module = importlib.import_module(module_name)
                        func = getattr(module, function_name)

                        # Call the function
                        result = func(*args_list, **kwargs_dict)
                        logger.info(f"Python function executed successfully. Result: {result}")

                    # Handle browser tasks (would need browser_launcher)
                    elif isinstance(cmd_data, list) and cmd_data and cmd_data[0] == "launch_browser":
                        logger.info("Browser task execution not implemented in scheduler daemon")
                        # Could implement browser launching here if needed

                    else:
                        logger.warning(f"Unknown structured command format: {cmd_data}")

                except json.JSONDecodeError:
                    # Not JSON, treat as plain command
                    logger.info(f"Executing shell command: {schedule.command}")
                    import subprocess
                    # Execute command without capturing output - let it run naturally
                    result = subprocess.run(schedule.command, shell=True)
                    if result.returncode == 0:
                        logger.info(f"Command executed successfully")
                    else:
                        logger.error(f"Command failed with return code {result.returncode}")
                        success = False

            except Exception as e:
                logger.error("Error executing schedule " + schedule.name + ": " + str(e))
                success = False

            # Update success/failure counts
            if success:
                schedule.success_count += 1
            else:
                schedule.failure_count += 1

            # Handle schedule lifecycle based on type
            if schedule.schedule_type == "once":
                # Remove one-time schedules after execution
                logger.info("Removing one-time schedule: " + schedule.name)
                del self.schedules[schedule_id]
            else:
                # Calculate next run time for recurring schedules
                schedule._calculate_next_run()

            # Notify that the schedule completed
            if self._on_schedule_complete:
                try:
                    self._on_schedule_complete(schedule_id, success)
                except Exception as e:
                    logger.error("Error in on_schedule_complete callback: " + str(e))

            logger.info("Schedule " + schedule.name + " executed with " + ("success" if success else "failure"))

    def __del__(self):
        """Clean up when the scheduler is deleted"""
        self.stop()
