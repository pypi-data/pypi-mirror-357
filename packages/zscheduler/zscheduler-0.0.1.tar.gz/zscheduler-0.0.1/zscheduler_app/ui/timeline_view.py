"""
Timeline view component for ZScheduler
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
    QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen

from zscheduler_app.scheduler.scheduler import Scheduler

logger = logging.getLogger(__name__)

class TimelineView(QWidget):
    """
    Widget for displaying schedules in a timeline view.

    This view shows schedules on a horizontal timeline, with time
    periods represented visually.
    """

    # Signal emitted when a schedule is selected
    schedule_selected = pyqtSignal(str)

    def __init__(self, scheduler=None, parent=None):
        """
        Initialize the timeline view.

        Args:
            scheduler: The scheduler instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.scheduler = scheduler
        self.schedules = []
        self.selected_schedule = None

        # Timeline configuration
        self.hours_to_show = 24  # Show 24 hours by default
        self.start_time = datetime.now()
        self.hour_width = 100  # Pixels per hour

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)

        # Header with time labels
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # Add time labels
        for hour in range(self.hours_to_show):
            dt = self.start_time + timedelta(hours=hour)
            time_str = dt.strftime('%H:00')
            time_label = QLabel(time_str)
            time_label.setFixedWidth(self.hour_width)
            time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(time_label)

        # Add stretch to fill remaining space
        header_layout.addStretch()

        # Timeline content
        self.timeline_content = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_content)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.timeline_layout.setSpacing(5)

        # Scroll area for timeline
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.timeline_content)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Add to main layout
        layout.addWidget(self.header)
        layout.addWidget(self.scroll_area)

    def update_schedules(self, schedules: List[Dict[str, Any]]) -> None:
        """
        Update the view with new schedules.

        Args:
            schedules: List of schedule dictionaries to display
        """
        self.schedules = schedules

        # Clear existing timeline items
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add schedule items to timeline
        for schedule in schedules:
            # Create a timeline item for each schedule
            item = self._create_timeline_item(schedule)
            if item:
                self.timeline_layout.addWidget(item)

        # Add stretch to fill remaining space
        self.timeline_layout.addStretch()

    def _create_timeline_item(self, schedule: Dict[str, Any]) -> QWidget:
        """
        Create a timeline item widget for a schedule.

        Args:
            schedule: The schedule dictionary to create an item for

        Returns:
            A widget representing the schedule on the timeline
        """
        # In a real implementation, this would create a visual representation
        # of the schedule on the timeline. This is a simplified placeholder.

        item = QWidget()
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(0, 5, 0, 5)

        # Add label with schedule name
        schedule_id = schedule.get('id', '')
        if schedule.get('name'):
            name = schedule.get('name')
        else:
            if schedule_id:
                name = "Task-" + schedule_id[:8]
            else:
                name = "Task"

        name_label = QLabel(name)
        name_label.setFixedWidth(150)
        name_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        item_layout.addWidget(name_label)

        # Add timeline bar
        timeline_bar = QFrame()
        timeline_bar.setFrameShape(QFrame.Shape.StyledPanel)

        # Create style sheet
        bg_color = "#ffb86c" if schedule.get('paused', False) else "#50fa7b"
        style_sheet = "background-color: " + bg_color + "; border-radius: 4px;"
        timeline_bar.setStyleSheet(style_sheet)

        timeline_bar.setFixedHeight(30)

        # Calculate position based on schedule times
        # This is simplified - a real implementation would calculate exact positions
        timeline_bar.setFixedWidth(self.hour_width * 2)  # Placeholder width

        item_layout.addWidget(timeline_bar)
        item_layout.addStretch()

        # Store schedule ID in the widget
        item.setProperty("schedule_id", schedule_id)

        # Add click handler
        item.mousePressEvent = lambda event, s=schedule: self._on_item_clicked(s)

        return item

    def _on_item_clicked(self, schedule: Dict[str, Any]) -> None:
        """
        Handle click on a timeline item.

        Args:
            schedule: The clicked schedule dictionary
        """
        self.selected_schedule = schedule

        # Emit signal with selected schedule ID
        if schedule and 'id' in schedule:
            self.schedule_selected.emit(schedule['id'])

        # In a real implementation, we would highlight the selected item
        self.update_schedules(self.schedules)

    def get_selected_schedule(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently selected schedule.

        Returns:
            The selected schedule dictionary or None if no schedule is selected
        """
        return self.selected_schedule
