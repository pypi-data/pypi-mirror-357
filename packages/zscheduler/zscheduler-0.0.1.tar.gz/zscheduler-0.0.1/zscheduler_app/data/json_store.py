"""
JSON file-based storage for ZScheduler data
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class JsonStore:
    """
    JSON file-based storage for schedules
    """

    def __init__(self, file_path: str):
        """
        Initialize the JSON store

        Args:
            file_path: Path to the JSON file
        """
        self.file_path = Path(file_path)
        self._ensure_parent_dir()

    def _ensure_parent_dir(self) -> None:
        """Ensure the parent directory exists"""
        parent_dir = self.file_path.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created directory: " + str(parent_dir))

    def load(self) -> List[Dict[str, Any]]:
        """
        Load schedules from the JSON file

        Returns:
            List of schedule dictionaries
        """
        if not self.file_path.exists():
            logger.info(f"Store file does not exist: {self.file_path}")
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                logger.warning(f"Invalid data format in {self.file_path}. Expected list, got {type(data).__name__}")
                return []

            logger.info(f"Loaded {len(data)} schedules from {self.file_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {self.file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading from {self.file_path}: {e}")
            return []

    def save(self, schedules: List[Dict[str, Any]]) -> bool:
        """
        Save schedules to the JSON file

        Args:
            schedules: List of schedule dictionaries

        Returns:
            True if successful, False otherwise
        """
        self._ensure_parent_dir()

        try:
            # Make sure file is completely overwritten
            with open(self.file_path, 'w', encoding='utf-8') as f:
                # Clear the file contents first
                f.truncate(0)
                # Write the new schedules
                json.dump(schedules, f, indent=2)

            logger.info(f"Saved {len(schedules)} schedules to {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving to {self.file_path}: {e}")
            return False

    def get_file_path(self) -> str:
        """
        Get the file path

        Returns:
            String representation of the file path
        """
        return str(self.file_path)

    def delete_file(self) -> bool:
        """
        Delete the JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.file_path.exists():
                self.file_path.unlink()
                logger.info(f"Deleted file: {self.file_path}")
                return True
            else:
                logger.info(f"File does not exist, nothing to delete: {self.file_path}")
                return True
        except Exception as e:
            logger.error(f"Error deleting file {self.file_path}: {e}")
            return False
