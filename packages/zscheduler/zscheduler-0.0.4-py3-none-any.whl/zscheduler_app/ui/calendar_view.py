"""
Calendar view for ZScheduler application
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QCalendarWidget, QListWidget,
    QListWidgetItem, QLabel, QSplitter
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal

from zscheduler_app.scheduler.scheduler import Scheduler

logger = logging.getLogger(__name__)

class CalendarView(QWidget):
    """
    Calendar view component for ZScheduler.

    Displays schedules on a calendar interface, allowing users to
    see scheduled tasks by date and select them for viewing or editing.
    """

    # Signal emitted when a schedule is selected
    schedule_selected = pyqtSignal(str)

    def __init__(self, scheduler=None, parent=None):
        """
        Initialize the calendar view.

        Args:
            scheduler: Scheduler instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.scheduler = scheduler
        self.schedules = []
        self.selected_schedule = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)

        # Splitter for calendar and task list
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

        # Use SingleSelection instead of SingleDate which may not be available in some PyQt6 versions
        try:
            self.calendar.setSelectionMode(QCalendarWidget.SelectionMode.SingleDate)
        except AttributeError:
            try:
                self.calendar.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)
            except AttributeError:
                # Fallback to integer value if enum is not available
                self.calendar.setSelectionMode(1)  # 1 corresponds to SingleSelection/SingleDate

        self.calendar.clicked.connect(self.on_date_selected)

        # Current date is selected by default
        self.selected_date = QDate.currentDate()
        self.calendar.setSelectedDate(self.selected_date)

        # Task list for selected day
        self.task_list_container = QWidget()
        task_list_layout = QVBoxLayout(self.task_list_container)

        self.day_label = QLabel(self.selected_date.toString("dddd, MMMM d, yyyy"))
        task_list_layout.addWidget(self.day_label)

        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        self.task_list.itemClicked.connect(self.on_task_selected)
        task_list_layout.addWidget(self.task_list)

        # Add widgets to splitter
        splitter.addWidget(self.calendar)
        splitter.addWidget(self.task_list_container)

        # Set splitter sizes
        splitter.setSizes([2, 1])  # 2:1 ratio

        # Add splitter to main layout
        layout.addWidget(splitter)

    def update_schedules(self, schedules: List[dict]) -> None:
        """
        Update the view with new schedules.

        Args:
            schedules: List of schedule dictionaries to display
        """
        self.schedules = schedules

        # Update the calendar
        self._highlight_dates_with_schedules()

        # Update the task list for the currently selected date
        self._update_task_list()

    def on_date_selected(self, date: QDate):
        """
        Handle date selection event.

        Args:
            date: Selected date
        """
        self.selected_date = date
        self.day_label.setText(date.toString("dddd, MMMM d, yyyy"))
        self._update_task_list()

    def on_task_selected(self, item: QListWidgetItem):
        """
        Handle task selection event.

        Args:
            item: Selected task item
        """
        schedule_id = item.data(Qt.ItemDataRole.UserRole)
        for schedule in self.schedules:
            if schedule.get('id') == schedule_id:
                self.selected_schedule = schedule
                self.schedule_selected.emit(schedule_id)
                break

    def _highlight_dates_with_schedules(self):
        """Highlight dates that have scheduled tasks."""
        # In a real implementation, we would highlight dates on the calendar
        # that have scheduled tasks. This is a placeholder.
        pass

    def _update_task_list(self):
        """Update the task list for the selected date."""
        self.task_list.clear()

        if not self.schedules:
            return

        # Get Python date from QDate
        py_date = datetime(
            self.selected_date.year(),
            self.selected_date.month(),
            self.selected_date.day()
        )

        # Find schedules for the selected date
        for schedule in self.schedules:
            next_run = schedule.get('next_run')
            if not next_run:
                continue

            try:
                next_run_dt = datetime.fromisoformat(next_run)
                if py_date.date() == next_run_dt.date():
                    name = schedule.get('name', '')
                    if not name:
                        schedule_id = schedule.get('id', '')
                        if schedule_id:
                            name = "Task-" + schedule_id[:8]
                        else:
                            name = "Task"
                    time_str = next_run_dt.strftime('%H:%M:%S')
                    item = QListWidgetItem(name + " - " + time_str)
                    item.setData(Qt.ItemDataRole.UserRole, schedule.get('id'))
                    self.task_list.addItem(item)
            except (ValueError, TypeError) as e:
                logger.error("Error parsing next_run time: " + str(e))

    def get_selected_schedule(self) -> Optional[dict]:
        """
        Get the currently selected schedule.

        Returns:
            The selected schedule dictionary or None if no schedule is selected
        """
        return self.selected_schedule
