"""
System tray integration for ZScheduler application
"""

import logging
import os
from typing import Callable, Optional, Dict, Any

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction, QPixmap, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from zscheduler_app.ui.icons import IconProvider

logger = logging.getLogger(__name__)

class SystemTrayManager(QObject):
    """
    Manages the system tray icon and menu for ZScheduler.

    This class provides system tray functionality including:
    - Tray icon with context menu
    - Notifications
    - Application control from the tray
    """

    # Signals
    exit_signal = pyqtSignal()
    show_signal = pyqtSignal()
    hide_signal = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialize the system tray manager.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.tray_icon = None
        self.icon_provider = IconProvider.get_instance()
        self.current_theme = "dark"
        self.scheduler_running = False

        self._setup_tray()

    def _setup_tray(self):
        """Set up the system tray icon and menu."""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray is not available on this system")
            return

        # Create tray icon
        self.tray_icon = QSystemTrayIcon(parent=self.parent())

        # Set the icon
        self._update_tray_icon()

        # Create tray menu
        tray_menu = QMenu()

        # Show/Hide action
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_signal.emit)
        tray_menu.addAction(show_action)

        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide_signal.emit)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        # Scheduler control
        self.scheduler_action = QAction("Stop Scheduler")
        self.scheduler_action.triggered.connect(self._on_scheduler_toggle)
        tray_menu.addAction(self.scheduler_action)

        tray_menu.addSeparator()

        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_signal.emit)
        tray_menu.addAction(exit_action)

        # Set the tray menu
        self.tray_icon.setContextMenu(tray_menu)

        # Connect the tray icon activated signal
        self.tray_icon.activated.connect(self._on_tray_activated)

        # Show the tray icon
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        """
        Handle tray icon activation.

        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_signal.emit()

    def update_icon(self, theme="dark"):
        """
        Update the tray icon based on theme.

        Args:
            theme: The theme to use ('dark' or 'light')
        """
        self.current_theme = theme
        self._update_tray_icon()

    def _update_tray_icon(self):
        """Update the tray icon using the icon provider"""
        if self.tray_icon:
            try:
                # Get the appropriate icon path from icon provider
                icon_path = self.icon_provider.save_system_tray_icon(self.current_theme)
                icon = QIcon(icon_path)

                # If the icon is empty, create a fallback icon
                if icon.isNull():
                    logger.warning("Failed to load tray icon, using fallback")
                    pixmap = QPixmap(16, 16)
                    pixmap.fill(QColor("#50fa7b"))
                    icon = QIcon(pixmap)

                self.tray_icon.setIcon(icon)
            except Exception as e:
                logger.error(f"Error updating tray icon: {e}")
                # Create fallback icon
                pixmap = QPixmap(16, 16)
                pixmap.fill(QColor("#50fa7b"))
                self.tray_icon.setIcon(QIcon(pixmap))

    def update_scheduler_state(self, is_running: bool):
        """
        Update the scheduler state in the tray menu.

        Args:
            is_running: Whether the scheduler is currently running
        """
        self.scheduler_running = is_running
        if hasattr(self, 'scheduler_action'):
            self.scheduler_action.setText("Stop Scheduler" if is_running else "Start Scheduler")

    def show_notification(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information, timeout=3000):
        """
        Show a notification message in the system tray

        Args:
            title: Notification title
            message: Notification message
            icon: Icon type for the notification
            timeout: Display duration in milliseconds
        """
        if self.tray_icon and QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.showMessage(title, message, icon, timeout)

    def _on_scheduler_toggle(self):
        """Handle scheduler toggle action."""
        # This would be connected to the scheduler in the main window
        pass

    def is_available(self):
        """Check if system tray is available on this system"""
        return QSystemTrayIcon.isSystemTrayAvailable()
