"""
Event emitter for ZScheduler
"""

import logging
from typing import Any, Callable, Dict, List, Set

logger = logging.getLogger(__name__)

class EventEmitter:
    """
    Simple event emitter implementation for ZScheduler.

    Allows for subscribing to and emitting events throughout the system.
    Supports wildcard event listeners that receive all events.
    """

    def __init__(self):
        """Initialize a new event emitter."""
        self._listeners: Dict[str, List[Callable]] = {}
        self._wildcard_listeners: List[Callable] = []

    def on(self, event_name: str, callback: Callable) -> None:
        """
        Register an event listener.

        Args:
            event_name: Name of the event to listen for or "*" for all events
            callback: Function to call when the event occurs
        """
        if event_name == "*":
            self._wildcard_listeners.append(callback)
            return

        if event_name not in self._listeners:
            self._listeners[event_name] = []

        self._listeners[event_name].append(callback)

    def off(self, event_name: str, callback: Callable) -> bool:
        """
        Remove an event listener.

        Args:
            event_name: Name of the event to stop listening for or "*" for all events
            callback: The callback function to remove

        Returns:
            True if the listener was removed, False if not found
        """
        if event_name == "*":
            try:
                self._wildcard_listeners.remove(callback)
                return True
            except ValueError:
                return False

        if event_name not in self._listeners:
            return False

        try:
            self._listeners[event_name].remove(callback)
            return True
        except ValueError:
            return False

    def emit(self, event_name: str, *args, **kwargs) -> None:
        """
        Emit an event.

        Args:
            event_name: Name of the event to emit
            *args: Positional arguments to pass to listeners
            **kwargs: Keyword arguments to pass to listeners
        """
        # Call specific listeners
        for callback in self._listeners.get(event_name, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Error in event listener for {event_name}: {e}")

        # Call wildcard listeners, passing the event name as the first argument
        for callback in self._wildcard_listeners:
            try:
                callback(event_name, *args, **kwargs)
            except Exception as e:
                logger.exception(f"Error in wildcard event listener for {event_name}: {e}")

    def has_listeners(self, event_name: str) -> bool:
        """
        Check if an event has listeners.

        Args:
            event_name: Name of the event to check

        Returns:
            True if the event has listeners, False otherwise
        """
        return bool(self._listeners.get(event_name)) or bool(self._wildcard_listeners)

    def clear(self, event_name: str = None) -> None:
        """
        Clear all listeners for an event or all events.

        Args:
            event_name: Name of the event to clear or None for all events
        """
        if event_name is None:
            self._listeners = {}
            self._wildcard_listeners = []
        elif event_name == "*":
            self._wildcard_listeners = []
        else:
            self._listeners[event_name] = []
