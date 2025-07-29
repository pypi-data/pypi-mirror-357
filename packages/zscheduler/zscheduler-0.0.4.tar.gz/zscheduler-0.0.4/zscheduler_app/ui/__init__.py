"""
UI components for ZScheduler application
"""

from zscheduler_app.ui.main_window import MainWindow
from zscheduler_app.ui.schedule_list_view import ScheduleListView
from zscheduler_app.ui.calendar_view import CalendarView
from zscheduler_app.ui.timeline_view import TimelineView
from zscheduler_app.ui.statistics_dashboard import StatisticsDashboard
from zscheduler_app.ui.new_schedule_dialog import NewScheduleDialog
from zscheduler_app.ui.settings_dialog import SettingsDialog
from zscheduler_app.ui.about_dialog import AboutDialog
from zscheduler_app.ui.system_tray import SystemTrayManager

__all__ = [
    'MainWindow',
    'ScheduleListView',
    'CalendarView',
    'TimelineView',
    'StatisticsDashboard',
    'NewScheduleDialog',
    'SettingsDialog',
    'AboutDialog',
    'SystemTrayManager'
]
