"""
Time parsing utilities for ZScheduler
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any

import dateutil.parser
from dateutil.relativedelta import relativedelta

class TimeParser:
    """
    Utility class for parsing various time formats into datetime objects.

    Supports:
    - Absolute dates and times ("May 25, 2025 at 10:00 PM")
    - Relative times ("3 hours from now", "19 hours from now")
    - Simple time formats ("10:30", "10:30 PM")
    """

    @staticmethod
    def parse(time_str: str) -> datetime:
        """
        Parse a time string into a datetime object.

        Args:
            time_str: Time string to parse

        Returns:
            Parsed datetime object

        Raises:
            ValueError: If the time string cannot be parsed
        """
        # Try natural language relative time first
        relative_time = TimeParser.parse_relative_time(time_str)
        if relative_time is not None:
            return relative_time

        # Try simple time format (just the time)
        simple_time = TimeParser.parse_simple_time(time_str)
        if simple_time is not None:
            return simple_time

        # Fall back to dateutil parser
        try:
            return dateutil.parser.parse(time_str)
        except (ValueError, OverflowError):
            raise ValueError(f"Could not parse time string: {time_str}")

    @staticmethod
    def parse_relative_time(time_str: str) -> Optional[datetime]:
        """
        Parse a relative time string like "3 hours from now".

        Args:
            time_str: Time string to parse

        Returns:
            Parsed datetime object or None if not a relative time
        """
        # Pattern for "X units from now"
        pattern = r"(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+from\s+now"
        match = re.match(pattern, time_str, re.IGNORECASE)
        if not match:
            return None

        value = int(match.group(1))
        unit = match.group(2).lower()

        now = datetime.now()

        # Handle different units
        if unit == "second":
            return now + timedelta(seconds=value)
        elif unit == "minute":
            return now + timedelta(minutes=value)
        elif unit == "hour":
            return now + timedelta(hours=value)
        elif unit == "day":
            return now + timedelta(days=value)
        elif unit == "week":
            return now + timedelta(weeks=value)
        elif unit == "month":
            return now + relativedelta(months=value)
        elif unit == "year":
            return now + relativedelta(years=value)

        return None

    @staticmethod
    def parse_simple_time(time_str: str) -> Optional[datetime]:
        """
        Parse a simple time format like "10:30" or "10:30 PM".

        Args:
            time_str: Time string to parse

        Returns:
            Parsed datetime object or None if not a simple time
        """
        # Pattern for "HH:MM" or "HH:MM AM/PM"
        pattern = r"(\d{1,2}):(\d{2})(?:\s*(AM|PM))?"
        match = re.match(pattern, time_str, re.IGNORECASE)
        if not match:
            return None

        hour = int(match.group(1))
        minute = int(match.group(2))
        am_pm = match.group(3)

        # Adjust hour for 12-hour clock
        if am_pm:
            if am_pm.upper() == "PM" and hour < 12:
                hour += 12
            elif am_pm.upper() == "AM" and hour == 12:
                hour = 0

        # Use today's date with the specified time
        now = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

        # If the time is already passed today, schedule for tomorrow
        if now < datetime.now():
            now += timedelta(days=1)

        return now
