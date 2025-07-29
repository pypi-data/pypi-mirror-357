"""
Settings dialog for ZScheduler application
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout,
    QCheckBox, QComboBox, QSpinBox, QPushButton, QDialogButtonBox,
    QLabel, QGroupBox, QColorDialog, QHBoxLayout, QFontDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from zscheduler_app.config.app_config import AppConfig
from zscheduler_app.themes.stylesheet import StylesheetManager

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """
    Dialog for application settings
    """

    def __init__(self, config, parent=None):
        """
        Initialize the settings dialog

        Args:
            config: Application configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config

        # Set window properties
        self.setWindowTitle("Settings")
        self.resize(500, 400)

        # Create UI
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the settings UI"""
        layout = QVBoxLayout(self)

        # Tab widget for different setting categories
        self.tabs = QTabWidget()

        # General tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)

        # Minimize to tray option
        self.minimize_to_tray = QCheckBox("Minimize to system tray")
        general_layout.addRow("", self.minimize_to_tray)

        # Auto-start scheduler
        self.autostart_scheduler = QCheckBox("Start scheduler on launch")
        general_layout.addRow("", self.autostart_scheduler)

        # Notification settings
        self.enable_notifications = QCheckBox("Enable notifications")
        general_layout.addRow("", self.enable_notifications)

        # Add general tab
        self.tabs.addTab(general_tab, "General")

        # UI tab
        ui_tab = QWidget()
        ui_layout = QFormLayout(ui_tab)

        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        ui_layout.addRow("Theme:", self.theme_combo)

        # Show toolbar
        self.show_toolbar = QCheckBox("Show toolbar")
        ui_layout.addRow("", self.show_toolbar)

        # Show status bar
        self.show_statusbar = QCheckBox("Show status bar")
        ui_layout.addRow("", self.show_statusbar)

        # Add UI tab
        self.tabs.addTab(ui_tab, "User Interface")

        # Schedule tab
        schedule_tab = QWidget()
        schedule_layout = QFormLayout(schedule_tab)

        # Default interval
        self.default_interval = QSpinBox()
        self.default_interval.setRange(1, 1440)  # 1 minute to 24 hours
        self.default_interval.setSuffix(" minutes")
        schedule_layout.addRow("Default interval:", self.default_interval)

        # Auto-save interval
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 60)
        self.autosave_interval.setSuffix(" minutes")
        schedule_layout.addRow("Auto-save every:", self.autosave_interval)

        # Add schedule tab
        self.tabs.addTab(schedule_tab, "Schedules")

        # Add tabs to layout
        layout.addWidget(self.tabs)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_settings(self):
        """Load settings from config"""
        # General settings
        self.minimize_to_tray.setChecked(self.config.get("general.minimize_to_tray", True))
        self.autostart_scheduler.setChecked(self.config.get("general.start_scheduler_on_launch", True))
        self.enable_notifications.setChecked(self.config.get("notifications.enabled", True))

        # UI settings
        theme = self.config.get("ui.theme", "system").lower()
        theme_index = {"light": 0, "dark": 1, "system": 2}.get(theme, 2)
        self.theme_combo.setCurrentIndex(theme_index)

        self.show_toolbar.setChecked(self.config.get("ui.show_toolbar", True))
        self.show_statusbar.setChecked(self.config.get("ui.show_statusbar", True))

        # Schedule settings
        self.default_interval.setValue(self.config.get("scheduler.default_interval", 5))
        self.autosave_interval.setValue(self.config.get("scheduler.autosave_interval", 5))

    def accept(self):
        """Save settings and close dialog"""
        # General settings
        self.config.set("general.minimize_to_tray", self.minimize_to_tray.isChecked())
        self.config.set("general.start_scheduler_on_launch", self.autostart_scheduler.isChecked())
        self.config.set("notifications.enabled", self.enable_notifications.isChecked())

        # UI settings
        theme_index = self.theme_combo.currentIndex()
        theme = ["light", "dark", "system"][theme_index]

        if theme != self.config.get("ui.theme", "system"):
            # Apply the stylesheet
            StylesheetManager.apply_theme()
            self.config.set("ui.theme", theme)

        self.config.set("ui.show_toolbar", self.show_toolbar.isChecked())
        self.config.set("ui.show_statusbar", self.show_statusbar.isChecked())

        # Schedule settings
        self.config.set("scheduler.default_interval", self.default_interval.value())
        self.config.set("scheduler.autosave_interval", self.autosave_interval.value())

        # Save config
        self.config.save()

        super().accept()
