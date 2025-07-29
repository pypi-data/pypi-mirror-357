"""
Dialog for creating and editing schedules
"""

import logging
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QDateTimeEdit,
    QPushButton, QDialogButtonBox, QTabWidget, QWidget,
    QTextEdit, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QIcon

from zscheduler_app.scheduler.scheduler import Scheduler, Schedule

logger = logging.getLogger(__name__)

class NewScheduleDialog(QDialog):
    """
    Dialog for creating or editing a schedule
    """

    def __init__(self, scheduler, parent=None, schedule=None):
        """
        Initialize the dialog

        Args:
            scheduler: The scheduler instance
            parent: Parent widget
            schedule: Schedule to edit, or None for new schedule
        """
        super().__init__(parent)
        self.scheduler = scheduler
        self.schedule = schedule
        self.edit_mode = schedule is not None

        # Set window properties
        self.setWindowTitle(f"{'Edit' if self.edit_mode else 'New'} Schedule")
        self.resize(500, 400)

        # Set up UI
        self._setup_ui()

        # Fill in existing data if editing
        if self.edit_mode:
            self._populate_form()

    def _setup_ui(self):
        """Set up the dialog UI"""
        main_layout = QVBoxLayout(self)

        # Form layout for basic info
        form_layout = QFormLayout()

        # Name field
        self.name_edit = QLineEdit()
        form_layout.addRow("Name:", self.name_edit)

        # Command field
        self.command_edit = QLineEdit()
        form_layout.addRow("Command:", self.command_edit)

        # Schedule type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Interval", "Cron", "Once"])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        form_layout.addRow("Schedule Type:", self.type_combo)

        # Add form to main layout
        main_layout.addLayout(form_layout)

        # Tab widget for schedule type specific settings
        self.tabs = QTabWidget()

        # Interval tab
        interval_widget = QWidget()
        interval_layout = QVBoxLayout(interval_widget)

        interval_form = QFormLayout()

        # Interval inputs
        self.interval_seconds = QSpinBox()
        self.interval_seconds.setRange(0, 59)
        self.interval_seconds.setSuffix(" seconds")

        self.interval_minutes = QSpinBox()
        self.interval_minutes.setRange(0, 59)
        self.interval_minutes.setSuffix(" minutes")

        self.interval_hours = QSpinBox()
        self.interval_hours.setRange(0, 23)
        self.interval_hours.setSuffix(" hours")

        self.interval_days = QSpinBox()
        self.interval_days.setRange(0, 365)
        self.interval_days.setSuffix(" days")

        # Add interval inputs to form
        interval_form.addRow("Days:", self.interval_days)
        interval_form.addRow("Hours:", self.interval_hours)
        interval_form.addRow("Minutes:", self.interval_minutes)
        interval_form.addRow("Seconds:", self.interval_seconds)

        # Set default interval
        self.interval_minutes.setValue(5)

        interval_layout.addLayout(interval_form)
        self.tabs.addTab(interval_widget, "Interval")

        # Cron tab
        cron_widget = QWidget()
        cron_layout = QVBoxLayout(cron_widget)

        cron_layout.addWidget(QLabel("Cron Expression:"))
        self.cron_edit = QLineEdit()
        self.cron_edit.setPlaceholderText("* * * * *")
        cron_layout.addWidget(self.cron_edit)

        cron_layout.addWidget(QLabel("Format: minute hour day_of_month month day_of_week"))
        cron_layout.addWidget(QLabel("Example: '*/5 * * * *' runs every 5 minutes"))

        self.tabs.addTab(cron_widget, "Cron")

        # Once tab
        once_widget = QWidget()
        once_layout = QVBoxLayout(once_widget)

        once_layout.addWidget(QLabel("Run Once At:"))
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.currentDateTime().addSecs(300))  # Default to 5 mins from now
        self.datetime_edit.setCalendarPopup(True)
        once_layout.addWidget(self.datetime_edit)

        self.tabs.addTab(once_widget, "Once")

        # Add tabs to main layout
        main_layout.addWidget(self.tabs)

        # Additional options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(True)
        options_layout.addWidget(self.enabled_check)

        main_layout.addWidget(options_group)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        # Set active tab based on initial type selection
        self._on_type_changed(0)

    def _on_type_changed(self, index):
        """Handle schedule type change"""
        self.tabs.setCurrentIndex(index)

    def _populate_form(self):
        """Populate the form with existing schedule data"""
        schedule_data = self.schedule.to_dict()

        # Set basic fields
        self.name_edit.setText(schedule_data.get("name", ""))
        self.command_edit.setText(schedule_data.get("command", ""))
        self.enabled_check.setChecked(schedule_data.get("enabled", True))

        # Set schedule type and related fields
        schedule_type = schedule_data.get("schedule_type", "interval")
        if schedule_type == "interval":
            self.type_combo.setCurrentIndex(0)

            # Set interval values
            interval = schedule_data.get("interval", 0)
            days = interval // 86400
            remainder = interval % 86400
            hours = remainder // 3600
            remainder = remainder % 3600
            minutes = remainder // 60
            seconds = remainder % 60

            self.interval_days.setValue(days)
            self.interval_hours.setValue(hours)
            self.interval_minutes.setValue(minutes)
            self.interval_seconds.setValue(seconds)

        elif schedule_type == "cron":
            self.type_combo.setCurrentIndex(1)
            self.cron_edit.setText(schedule_data.get("cron_expression", ""))

        elif schedule_type == "once":
            self.type_combo.setCurrentIndex(2)
            try:
                dt = datetime.fromisoformat(schedule_data.get("cron_expression", ""))
                self.datetime_edit.setDateTime(QDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))
            except (ValueError, TypeError):
                # If parsing fails, use current time + 5 minutes
                self.datetime_edit.setDateTime(QDateTime.currentDateTime().addSecs(300))

    def accept(self):
        """Handle dialog acceptance"""
        # Get data from form
        name = self.name_edit.text().strip()
        command = self.command_edit.text().strip()
        schedule_type = ["interval", "cron", "once"][self.type_combo.currentIndex()]
        enabled = self.enabled_check.isChecked()

        # Validate inputs
        if not name:
            name = "Unnamed Schedule"

        if not command:
            logger.warning("No command specified")
            command = "echo 'No command specified'"

        # Prepare schedule data
        schedule_data = {
            "name": name,
            "command": command,
            "schedule_type": schedule_type,
            "enabled": enabled,
        }

        # Get type-specific data
        if schedule_type == "interval":
            interval = (self.interval_days.value() * 86400 +
                       self.interval_hours.value() * 3600 +
                       self.interval_minutes.value() * 60 +
                       self.interval_seconds.value())

            if interval == 0:
                interval = 60  # Default to 1 minute

            schedule_data["interval"] = interval

        elif schedule_type == "cron":
            cron_expr = self.cron_edit.text().strip()
            if not cron_expr:
                cron_expr = "*/5 * * * *"  # Default to every 5 minutes

            schedule_data["cron_expression"] = cron_expr

        elif schedule_type == "once":
            dt = self.datetime_edit.dateTime().toPython()
            schedule_data["cron_expression"] = dt.isoformat()

        # Update or create schedule
        try:
            if self.edit_mode:
                self.scheduler.update_schedule(self.schedule.id, schedule_data)
                logger.info(f"Updated schedule: {name}")
            else:
                schedule_id = self.scheduler.add_schedule(schedule_data)
                logger.info(f"Created schedule: {name} (ID: {schedule_id})")

            # Accept dialog
            super().accept()

        except Exception as e:
            logger.error(f"Error saving schedule: {e}")
            # Keep dialog open
