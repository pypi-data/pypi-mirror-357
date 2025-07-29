"""
Main window for ZScheduler application
"""

import sys
import logging
from typing import Optional
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenu, QMenuBar, QToolBar, QStatusBar,
    QMessageBox, QFileDialog, QSystemTrayIcon, QApplication
)
from PyQt6.QtCore import Qt, QSize, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QCloseEvent

from zscheduler_app.scheduler.scheduler import Scheduler, Schedule
from zscheduler_app.data.json_store import JsonStore

from zscheduler_app.config.app_config import AppConfig
from zscheduler_app.themes.theme_manager import ThemeManager
from zscheduler_app.ui.schedule_list_view import ScheduleListView
from zscheduler_app.ui.calendar_view import CalendarView
from zscheduler_app.ui.timeline_view import TimelineView
from zscheduler_app.ui.statistics_dashboard import StatisticsDashboard
from zscheduler_app.ui.new_schedule_dialog import NewScheduleDialog
from zscheduler_app.ui.settings_dialog import SettingsDialog
from zscheduler_app.ui.about_dialog import AboutDialog
from zscheduler_app.ui.system_tray import SystemTrayManager
from zscheduler_app.ui.icons import IconProvider, IconManager
from zscheduler_app.themes.stylesheet import StylesheetManager

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Main window for ZScheduler application.

    This is the primary UI component, managing the layout and actions
    of the main application window.
    """
    # Define signals for thread-safe communication
    schedule_run_signal = pyqtSignal(str)
    schedule_complete_signal = pyqtSignal(str, bool)

    def __init__(self, app_config, scheduler, json_store):
        """
        Initialize the main window.

        Args:
            app_config: The application configuration
            scheduler: The scheduler instance
            json_store: The schedule store
        """
        super().__init__()

        self.app_config = app_config
        self.scheduler = scheduler
        self.json_store = json_store
        self._is_app_exiting = False

        # Connect signals to slots
        self.schedule_run_signal.connect(self._on_schedule_run)
        self.schedule_complete_signal.connect(self._on_schedule_complete)

        # Initialize icon provider
        self.icon_provider = IconProvider.get_instance()

        # Apply the stylesheet
        StylesheetManager.apply_theme()

        # Set window properties
        self.setWindowTitle("ZScheduler")

        # Set a fixed size appropriate for laptops - no dynamic sizing
        # These dimensions should work well on most displays
        fixed_width = 800
        fixed_height = 600

        # Set fixed size constraints for the window
        self.setMinimumSize(fixed_width, fixed_height)
        self.setMaximumSize(fixed_width, fixed_height)
        self.resize(fixed_width, fixed_height)

        # Center the window on screen
        screen_size = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen_size.width() - fixed_width) // 2,
            (screen_size.height() - fixed_height) // 2
        )

        # Set application icon and theme
        current_theme = app_config.get("ui.theme", "dark")
        self.icon_provider.set_window_icon(self, current_theme)

        # Initialize system tray if enabled
        if app_config.get("ui.minimize_to_tray", True):
            self.tray_manager = SystemTrayManager()
            self.tray_manager.show_signal.connect(self.show)
            self.tray_manager.hide_signal.connect(self.hide)
            self.tray_manager.exit_signal.connect(self._on_tray_exit)
        else:
            self.tray_manager = None

        # Initialize additional components
        self._setup_ui()
        self._create_statusbar()
        self._create_menu()
        self._create_toolbar()
        self._setup_shortcuts()

        # Update UI with current schedules
        self._update_schedules()

        # Connect scheduler callbacks using lambdas to emit signals
        if hasattr(self.scheduler, 'set_on_schedule_run_callback'):
            self.scheduler.set_on_schedule_run_callback(
                lambda schedule_id: self.schedule_run_signal.emit(schedule_id)
            )
        if hasattr(self.scheduler, 'set_on_schedule_complete_callback'):
            self.scheduler.set_on_schedule_complete_callback(
                lambda schedule_id, success: self.schedule_complete_signal.emit(schedule_id, success)
            )

        # Show status message
        self.statusBar().showMessage("Ready")

    def _setup_ui(self):
        """Set up the main UI components."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Tab widget for different views
        self.tab_widget = QTabWidget()

        # List view
        self.list_view = ScheduleListView(self.scheduler)
        self.tab_widget.addTab(self.list_view, "List View")

        # Calendar view
        self.calendar_view = CalendarView(self.scheduler)
        self.tab_widget.addTab(self.calendar_view, "Calendar View")

        # Timeline view
        self.timeline_view = TimelineView(self.scheduler)
        self.tab_widget.addTab(self.timeline_view, "Timeline")

        # Statistics dashboard
        self.stats_dashboard = StatisticsDashboard(self.scheduler)
        self.tab_widget.addTab(self.stats_dashboard, "Statistics")

        # Connect tab changed signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)

    def _create_menu(self):
        """Create the main menu."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")

        # New schedule action
        new_action = QAction("&New Schedule...", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new_schedule)
        file_menu.addAction(new_action)

        # Import/Export actions
        import_action = QAction("&Import Schedules...", self)
        import_action.triggered.connect(self._on_import_schedules)
        file_menu.addAction(import_action)

        export_action = QAction("&Export Schedules...", self)
        export_action.triggered.connect(self._on_export_schedules)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Settings action
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self._on_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")

        # Edit schedule action
        self.edit_action = QAction("&Edit Schedule...", self)
        self.edit_action.setShortcut(QKeySequence.StandardKey.Open)
        self.edit_action.triggered.connect(self._on_edit_schedule)
        edit_menu.addAction(self.edit_action)

        # Duplicate schedule action
        self.duplicate_action = QAction("&Duplicate Schedule", self)
        self.duplicate_action.triggered.connect(self._on_duplicate_schedule)
        edit_menu.addAction(self.duplicate_action)

        # Delete schedule action
        self.delete_action = QAction("&Delete Schedule", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.triggered.connect(self._on_delete_schedule)
        edit_menu.addAction(self.delete_action)

        # View menu
        view_menu = self.menuBar().addMenu("&View")

        # Refresh action
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self._update_schedules)
        view_menu.addAction(refresh_action)

        view_menu.addSeparator()

        # Theme submenu
        theme_menu = view_menu.addMenu("&Theme")

        # Light theme action
        light_theme_action = QAction("&Light", self)
        light_theme_action.triggered.connect(lambda: self._on_theme_change("light"))
        theme_menu.addAction(light_theme_action)

        # Dark theme action
        dark_theme_action = QAction("&Dark", self)
        dark_theme_action.triggered.connect(lambda: self._on_theme_change("dark"))
        theme_menu.addAction(dark_theme_action)

        # System theme action
        system_theme_action = QAction("&System", self)
        system_theme_action.triggered.connect(lambda: self._on_theme_change("system"))
        theme_menu.addAction(system_theme_action)

        # Scheduler menu
        scheduler_menu = self.menuBar().addMenu("&Scheduler")

        # Start scheduler action
        self.start_action = QAction("&Start Scheduler", self)
        self.start_action.triggered.connect(self._on_start_scheduler)
        scheduler_menu.addAction(self.start_action)

        # Stop scheduler action
        self.stop_action = QAction("S&top Scheduler", self)
        self.stop_action.triggered.connect(self._on_stop_scheduler)
        scheduler_menu.addAction(self.stop_action)

        scheduler_menu.addSeparator()

        # Pause schedule action
        self.pause_action = QAction("&Pause Schedule", self)
        self.pause_action.triggered.connect(self._on_pause_schedule)
        scheduler_menu.addAction(self.pause_action)

        # Resume schedule action
        self.resume_action = QAction("&Resume Schedule", self)
        self.resume_action.triggered.connect(self._on_resume_schedule)
        scheduler_menu.addAction(self.resume_action)

        # Run now action
        self.run_now_action = QAction("Run &Now", self)
        self.run_now_action.triggered.connect(self._on_run_now)
        scheduler_menu.addAction(self.run_now_action)

        # Help menu
        help_menu = self.menuBar().addMenu("&Help")

        # About action
        about_action = QAction("&About ZScheduler", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

        # Update action states
        self._update_action_states()

    def _create_toolbar(self):
        """Create the main toolbar."""
        # Main toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(24, 24))  # Increased icon size
        self.toolbar.setObjectName("mainToolbar")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        # New schedule action
        new_action = QAction(IconManager.new_icon(), "", self)
        new_action.setToolTip("New Schedule")
        new_action.triggered.connect(self._on_new_schedule)
        self.toolbar.addAction(new_action)

        # Edit schedule action
        edit_action = QAction(IconManager.edit_icon(), "", self)
        edit_action.setToolTip("Edit Schedule")
        edit_action.triggered.connect(self._on_edit_schedule)
        self.toolbar.addAction(edit_action)

        # Delete schedule action
        delete_action = QAction(IconManager.delete_icon(), "", self)
        delete_action.setToolTip("Delete Schedule")
        delete_action.triggered.connect(self._on_delete_schedule)
        self.toolbar.addAction(delete_action)

        self.toolbar.addSeparator()

        # Start scheduler action
        start_action = QAction(IconManager.start_icon(), "", self)
        start_action.setToolTip("Start Scheduler")
        start_action.triggered.connect(self._on_start_scheduler)
        self.toolbar.addAction(start_action)
        self.start_action = start_action

        # Stop scheduler action
        stop_action = QAction(IconManager.stop_icon(), "", self)
        stop_action.setToolTip("Stop Scheduler")
        stop_action.triggered.connect(self._on_stop_scheduler)
        self.toolbar.addAction(stop_action)
        self.stop_action = stop_action

        self.toolbar.addSeparator()

        # Pause schedule action
        pause_action = QAction(IconManager.pause_icon(), "", self)
        pause_action.setToolTip("Pause Schedule")
        pause_action.triggered.connect(self._on_pause_schedule)
        self.toolbar.addAction(pause_action)
        self.pause_action = pause_action

        # Resume schedule action
        resume_action = QAction(IconManager.resume_icon(), "", self)
        resume_action.setToolTip("Resume Schedule")
        resume_action.triggered.connect(self._on_resume_schedule)
        self.toolbar.addAction(resume_action)
        self.resume_action = resume_action

        # Run now action
        run_now_action = QAction(IconManager.run_now_icon(), "", self)
        run_now_action.setToolTip("Run Now")
        run_now_action.triggered.connect(self._on_run_now)
        self.toolbar.addAction(run_now_action)
        self.run_now_action = run_now_action

        # Show/hide toolbar based on config
        self.toolbar.setVisible(self.app_config.get("ui.show_toolbar", True))

    def _create_statusbar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Show/hide status bar based on config
        self.status_bar.setVisible(self.app_config.get("ui.show_statusbar", True))

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Add Ctrl+Q to quit application
        quit_shortcut = QKeySequence("Ctrl+Q")
        quit_action = QAction(self)
        quit_action.setShortcut(quit_shortcut)
        quit_action.triggered.connect(self.close)
        self.addAction(quit_action)

    def _update_schedules(self):
        """Update the UI with current schedules."""
        schedules = self.scheduler.get_schedules()

        # Update each view
        self.list_view.update_schedules(schedules)
        self.calendar_view.update_schedules(schedules)
        self.timeline_view.update_schedules(schedules)
        self.stats_dashboard.update_statistics(schedules)

        # Update status bar
        self.status_bar.showMessage(str(len(schedules)) + " schedules loaded")

        # Update action states
        self._update_action_states()

    def _update_action_states(self):
        """Update the enabled state of actions based on current state."""
        # Get the currently selected schedule
        selected_schedule = self._get_selected_schedule()

        # Update edit/delete/duplicate actions
        has_selection = selected_schedule is not None
        self.edit_action.setEnabled(has_selection)
        self.delete_action.setEnabled(has_selection)
        self.duplicate_action.setEnabled(has_selection)

        # Update pause/resume actions
        if has_selection:
            # Check if paused, handling both Schedule objects and dictionaries
            if isinstance(selected_schedule, dict):
                is_paused = selected_schedule.get('paused', False)
            else:
                is_paused = getattr(selected_schedule, 'paused', False)

            self.pause_action.setEnabled(not is_paused)
            self.resume_action.setEnabled(is_paused)
            self.run_now_action.setEnabled(True)
        else:
            self.pause_action.setEnabled(False)
            self.resume_action.setEnabled(False)
            self.run_now_action.setEnabled(False)

        # Update scheduler actions
        is_running = self.scheduler.running
        self.start_action.setEnabled(not is_running)
        self.stop_action.setEnabled(is_running)

        # Update system tray if available
        if self.tray_manager:
            self.tray_manager.update_scheduler_state(is_running)

    def _get_selected_schedule(self) -> Optional[Schedule]:
        """
        Get the currently selected schedule from the active view.

        Returns:
            Optional[Schedule]: The selected schedule, or None if no selection
        """
        current_tab = self.tab_widget.currentIndex()

        if current_tab == 0:  # List view
            return self.list_view.get_selected_schedule()
        elif current_tab == 1:  # Calendar view
            return self.calendar_view.get_selected_schedule()
        elif current_tab == 2:  # Timeline view
            return self.timeline_view.get_selected_schedule()

        return None

    def _on_tab_changed(self, index):
        """
        Handle tab change event.

        Args:
            index: The new tab index
        """
        # Update action states for the new tab
        self._update_action_states()

    def _on_new_schedule(self):
        """Handle new schedule action."""
        dialog = NewScheduleDialog(self.scheduler, self)
        if dialog.exec():
            self._update_schedules()

    def _on_edit_schedule(self):
        """Handle edit schedule action."""
        schedule = self._get_selected_schedule()
        if schedule:
            # If we got a dictionary, we need to convert it to a Schedule object
            if isinstance(schedule, dict):
                from zscheduler_app.scheduler.scheduler import Schedule
                schedule_obj = Schedule.from_dict(schedule)
            else:
                schedule_obj = schedule

            dialog = NewScheduleDialog(self.scheduler, self, schedule_obj)
            if dialog.exec():
                self._update_schedules()

    def _on_duplicate_schedule(self):
        """Handle duplicate schedule action."""
        schedule = self._get_selected_schedule()
        if schedule:
            # Handle both Schedule objects and dictionaries
            if isinstance(schedule, dict):
                # For dictionaries, get values directly
                name = schedule.get('name', 'Unknown')
                schedule_type = schedule.get('schedule_type', 'interval')
                command = schedule.get('command', '')
                interval = schedule.get('interval', 60)
                cron_expression = schedule.get('cron_expression', '')

                # Create a new schedule with the same settings
                new_schedule_data = {
                    "name": f"Copy of {name}",
                    "command": command,
                    "schedule_type": schedule_type,
                    "interval": interval,
                    "cron_expression": cron_expression,
                    "enabled": True
                }

                self.scheduler.add_schedule(new_schedule_data)
                logger.info(f"Duplicated schedule: {name}")
            else:
                # For Schedule objects, use the existing code
                if hasattr(schedule, 'task') and schedule.task.__class__.__name__ == "CommandTask":
                    target = schedule.task.command
                else:
                    # For Python tasks, this is a simplified approach
                    target = f"{schedule.task.module_name}.{schedule.task.callable_name}" if hasattr(schedule, 'task') and schedule.task.module_name else ""

                # Create new schedule builder
                builder = self.scheduler.schedule(target).name(f"Copy of {schedule.name}")

                # Set the same trigger type
                if schedule.trigger_type == "date":
                    # For one-time schedules, set it for tomorrow at the same time
                    tomorrow = datetime.now() + timedelta(days=1)
                    builder.at(tomorrow)
                elif schedule.trigger_type == "interval":
                    # For recurring schedules, use the same interval
                    builder.every(**schedule.trigger_args)
                    if schedule.max_runs:
                        builder.repeat(schedule.max_runs)
                    builder.start_now()
                elif schedule.trigger_type == "cron":
                    # For cron schedules, use the same expression
                    cron_args = schedule.trigger_args
                    expr = f"{cron_args.get('minute', '*')} {cron_args.get('hour', '*')} {cron_args.get('day', '*')} {cron_args.get('month', '*')} {cron_args.get('day_of_week', '*')}"
                    builder.cron(expr)

                logger.info(f"Duplicated schedule: {schedule.id}")

            self._update_schedules()

    def _on_delete_schedule(self):
        """Handle delete schedule action."""
        schedule = self._get_selected_schedule()
        if schedule:
            # Get the schedule name, handling both Schedule objects and dictionaries
            schedule_name = schedule.name if hasattr(schedule, 'name') else schedule.get('name', 'Unknown')
            schedule_id = schedule.id if hasattr(schedule, 'id') else schedule.get('id')

            confirm = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete schedule '{schedule_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                # Remove the schedule from the scheduler
                if self.scheduler.remove_schedule(schedule_id):
                    # Get the updated schedules list (without the deleted schedule)
                    updated_schedules = self.scheduler.get_schedules()

                    # Save changes to the JSON store immediately
                    try:
                        # Force overwrite the entire JSON file with the updated schedules
                        self.json_store.save(updated_schedules)

                        # Double-check that the file was updated correctly
                        # This will reload the file to verify the schedule is gone
                        loaded_schedules = self.json_store.load()
                        deleted = all(s.get('id') != schedule_id for s in loaded_schedules)

                        if deleted:
                            self.status_bar.showMessage(f"Deleted schedule: {schedule_name}")
                        else:
                            logger.error(f"Schedule {schedule_id} still exists in JSON store after deletion")
                            self.status_bar.showMessage(f"Warning: Schedule may not be fully deleted")

                    except Exception as e:
                        logger.exception(f"Error saving schedules after deletion: {e}")
                        self.status_bar.showMessage(f"Error saving after deletion: {str(e)}")

                    # Update UI
                    self._update_schedules()

    def _on_import_schedules(self):
        """Handle import schedules action."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Schedules",
            "",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                # Import schedules from JSON file
                import_store = JsonStore(file_path)
                imported_schedules = import_store.load_schedules()

                # Check for schedules with same name
                current_names = {s.name for s in self.scheduler.get_schedules() if s.name}
                duplicates = [s for s in imported_schedules if s.name in current_names]

                if duplicates:
                    # Ask how to handle duplicates
                    duplicate_msg = f"Found {len(duplicates)} schedules with existing names. How would you like to proceed?"
                    duplicate_dialog = QMessageBox(
                        QMessageBox.Icon.Question,
                        "Duplicate Schedules",
                        duplicate_msg,
                        QMessageBox.StandardButton.NoButton,
                        self
                    )
                    skip_button = duplicate_dialog.addButton("Skip Duplicates", QMessageBox.ButtonRole.AcceptRole)
                    rename_button = duplicate_dialog.addButton("Rename", QMessageBox.ButtonRole.ActionRole)
                    replace_button = duplicate_dialog.addButton("Replace", QMessageBox.ButtonRole.DestructiveRole)
                    cancel_button = duplicate_dialog.addButton("Cancel Import", QMessageBox.ButtonRole.RejectRole)

                    duplicate_dialog.exec()
                    clicked = duplicate_dialog.clickedButton()

                    if clicked == cancel_button:
                        return
                    elif clicked == skip_button:
                        imported_schedules = [s for s in imported_schedules if s.name not in current_names]
                    elif clicked == rename_button:
                        for schedule in duplicates:
                            schedule.name = f"Imported {schedule.name}"
                    # If replace, we'll let them overwrite

                # Add the imported schedules
                for schedule in imported_schedules:
                    self.scheduler.add_schedule(schedule)

                self._update_schedules()
                self.status_bar.showMessage(f"Imported {len(imported_schedules)} schedules from {file_path}")

            except Exception as e:
                logger.exception(f"Error importing schedules: {e}")
                QMessageBox.critical(
                    self,
                    "Import Error",
                    f"Failed to import schedules: {str(e)}"
                )

    def _on_export_schedules(self):
        """Handle export schedules action."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Schedules",
            "",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                # Create an export JSON store and save schedules
                export_store = JsonStore(file_path)
                schedules = self.scheduler.get_schedules()
                export_store.save_schedules(schedules)

                self.status_bar.showMessage(f"Exported {len(schedules)} schedules to {file_path}")

            except Exception as e:
                logger.exception(f"Error exporting schedules: {e}")
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export schedules: {str(e)}"
                )

    def _on_settings(self):
        """Handle settings action."""
        dialog = SettingsDialog(self.app_config, self)
        if dialog.exec():
            # Update UI based on new settings
            self.toolbar.setVisible(self.app_config.get("ui.show_toolbar", True))
            self.status_bar.setVisible(self.app_config.get("ui.show_statusbar", True))

            # Apply the stylesheet with any theme changes
            StylesheetManager.apply_theme()

    def _on_theme_change(self, theme_name):
        """
        Handle theme change.

        Args:
            theme_name: The name of the theme to apply
        """
        # Apply the stylesheet
        StylesheetManager.apply_theme()

        # Save the theme preference
        self.app_config.set("ui.theme", theme_name)
        self.app_config.save()

        # Update system tray icon if available
        if self.tray_manager:
            self.tray_manager.update_icon(theme_name == "dark")

        # Update application icon
        self.icon_provider.set_window_icon(self, theme_name)

    def _on_start_scheduler(self):
        """Handle start scheduler action."""
        self.scheduler.start()
        self._update_action_states()
        self.status_bar.showMessage("Scheduler started")

        if self.tray_manager and self.app_config.get("notifications.enabled", True):
            self.tray_manager.show_notification(
                "ZScheduler",
                "Scheduler started",
                QSystemTrayIcon.MessageIcon.Information
            )

    def _on_stop_scheduler(self):
        """Handle stop scheduler action."""
        self.scheduler.stop()
        self._update_action_states()
        self.status_bar.showMessage("Scheduler stopped")

        if self.tray_manager and self.app_config.get("notifications.enabled", True):
            self.tray_manager.show_notification(
                "ZScheduler",
                "Scheduler stopped",
                QSystemTrayIcon.MessageIcon.Information
            )

    def _on_pause_schedule(self):
        """Handle pause schedule action."""
        schedule = self._get_selected_schedule()
        if schedule:
            # Get the schedule name and id, handling both Schedule objects and dictionaries
            schedule_name = schedule.name if hasattr(schedule, 'name') else schedule.get('name', 'Unknown')
            schedule_id = schedule.id if hasattr(schedule, 'id') else schedule.get('id')

            self.scheduler.pause_schedule(schedule_id)
            self._update_schedules()
            self.status_bar.showMessage(f"Paused schedule: {schedule_name}")

    def _on_resume_schedule(self):
        """Handle resume schedule action."""
        schedule = self._get_selected_schedule()
        if schedule:
            # Get the schedule name and id, handling both Schedule objects and dictionaries
            schedule_name = schedule.name if hasattr(schedule, 'name') else schedule.get('name', 'Unknown')
            schedule_id = schedule.id if hasattr(schedule, 'id') else schedule.get('id')

            self.scheduler.resume_schedule(schedule_id)
            self._update_schedules()
            self.status_bar.showMessage(f"Resumed schedule: {schedule_name}")

    def _on_run_now(self):
        """Handle run now action."""
        schedule = self._get_selected_schedule()
        if schedule:
            # Get the schedule name and id, handling both Schedule objects and dictionaries
            schedule_name = schedule.name if hasattr(schedule, 'name') else schedule.get('name', 'Unknown')

            # In a real implementation, this would execute the schedule immediately
            if hasattr(schedule, 'execute'):
                schedule.execute()
            else:
                # If it's a dictionary, we need to find the actual schedule object
                schedule_id = schedule.get('id')
                if schedule_id:
                    self.scheduler._execute_schedule(schedule_id)

            self.status_bar.showMessage(f"Running schedule: {schedule_name}")
            self._update_schedules()

    def _on_about(self):
        """Handle about action."""
        dialog = AboutDialog(self)
        dialog.exec()

    def _toggle_window_visibility(self):
        """Toggle the visibility of the main window."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()

        # Update tray icon text if available
        if self.tray_manager:
            self.tray_manager.update_show_hide_text(self.isVisible())

    def _toggle_scheduler(self):
        """Toggle the scheduler state."""
        if self.scheduler.running:
            self._on_stop_scheduler()
        else:
            self._on_start_scheduler()

    @pyqtSlot(str)
    def _on_schedule_run(self, schedule_id):
        """
        Handle schedule run event. This is a slot connected to a signal
        for thread-safe operation.

        Args:
            schedule_id: The ID of the schedule being run
        """
        self._update_schedules()

    @pyqtSlot(str, bool)
    def _on_schedule_complete(self, schedule_id, success):
        """
        Handle schedule complete event. This is a slot connected to a signal
        for thread-safe operation.

        Args:
            schedule_id: The ID of the completed schedule
            success: Whether the schedule executed successfully
        """
        self._update_schedules()

    def closeEvent(self, event: QCloseEvent):
        """
        Handle window close event.

        Args:
            event: The close event
        """
        if self.tray_manager and self.app_config.get("general.minimize_to_tray", True) and not self._is_app_exiting:
            # Minimize to tray instead of closing
            event.ignore()
            self.hide()

            # Show notification if first time
            if not hasattr(self, '_minimized_to_tray_before'):
                self._minimized_to_tray_before = True
                self.tray_manager.show_notification(
                    "ZScheduler",
                    "ZScheduler is still running in the background. Click the tray icon to restore.",
                    QSystemTrayIcon.MessageIcon.Information
                )
        else:
            # No need to save window size since we use fixed dimensions

            # Stop the scheduler first
            try:
                logger.info("Stopping scheduler from main window close event...")
                self.scheduler.stop()
            except Exception as e:
                logger.exception(f"Error stopping scheduler on exit: {e}")

            # Save schedules
            try:
                self.json_store.save(self.scheduler.get_schedules())
            except Exception as e:
                logger.exception(f"Error saving schedules on exit: {e}")

            # Accept the close event
            event.accept()

    def set_app_exiting(self):
        """Mark the application as exiting to prevent minimize to tray."""
        self._is_app_exiting = True

    def _on_tray_exit(self):
        """Handle exit signal from system tray."""
        self.set_app_exiting()
        self.close()
