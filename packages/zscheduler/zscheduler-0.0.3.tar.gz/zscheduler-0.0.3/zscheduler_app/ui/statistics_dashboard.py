"""
Statistics dashboard for ZScheduler application
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QTableWidget, QTableWidgetItem,
    QComboBox, QFrame, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

from zscheduler_app.scheduler.scheduler import Scheduler, Schedule

logger = logging.getLogger(__name__)

class StatsCard(QFrame):
    """A card displaying a single statistic with label"""

    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Value label with large font
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = value_label.font()
        font.setPointSize(24)
        font.setBold(True)
        value_label.setFont(font)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

class PieChart(QWidget):
    """Simple pie chart widget"""

    def __init__(self, data: Dict[str, float], colors: Dict[str, str], parent=None):
        super().__init__(parent)
        self.data = data
        self.colors = colors
        self.setMinimumSize(200, 200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate total value
        total = sum(self.data.values())
        if total <= 0:
            return

        # Calculate center and radius
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 10

        # Draw pie slices
        start_angle = 0
        for label, value in self.data.items():
            span_angle = 360 * (value / total)

            # Create and set brush color
            color = QColor(self.colors.get(label, "#CCCCCC"))
            painter.setBrush(QBrush(color))

            # Draw pie slice
            painter.drawPie(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2),
                int(start_angle * 16),
                int(span_angle * 16)
            )

            start_angle += span_angle

class BarChart(QWidget):
    """Simple bar chart widget"""

    def __init__(self, data: Dict[str, float], color: str, parent=None):
        super().__init__(parent)
        self.data = data
        self.color = color
        self.setMinimumSize(300, 200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get max value for scaling
        values = list(self.data.values())
        if not values:
            return

        max_value = max(values)
        if max_value <= 0:
            return

        # Calculate sizes
        width = self.width()
        height = self.height()
        bar_width = width / (len(self.data) * 2)
        bottom = height - 20
        scale_factor = (height - 40) / max_value

        # Draw bars
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(QColor(self.color)))

        x = bar_width
        for label, value in self.data.items():
            bar_height = value * scale_factor
            painter.drawRect(
                int(x),
                int(bottom - bar_height),
                int(bar_width),
                int(bar_height)
            )

            # Draw label
            painter.drawText(
                int(x),
                int(bottom + 15),
                int(bar_width),
                20,
                Qt.AlignmentFlag.AlignCenter,
                label
            )

            x += bar_width * 2

class StatisticsDashboard(QWidget):
    """
    Widget displaying statistics and analytics about scheduled tasks.

    Shows execution success rates, frequency of runs, and other metrics
    to provide insights into the scheduler's performance.
    """

    def __init__(self, scheduler: Scheduler, parent=None):
        """
        Initialize the statistics dashboard.

        Args:
            scheduler: The scheduler instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.scheduler = scheduler
        self.schedules = []  # Ensure schedules attribute always exists
        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)

        # Period selection
        period_layout = QHBoxLayout()
        period_label = QLabel("Time Period:")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"])
        self.period_combo.currentIndexChanged.connect(self._update_statistics)

        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_combo)
        period_layout.addStretch()

        main_layout.addLayout(period_layout)

        # Stats cards
        stats_layout = QHBoxLayout()

        self.total_tasks_card = StatsCard("Total Tasks", "0")
        self.active_tasks_card = StatsCard("Active Tasks", "0")
        self.executions_card = StatsCard("Total Executions", "0")
        self.success_rate_card = StatsCard("Success Rate", "0%")

        stats_layout.addWidget(self.total_tasks_card)
        stats_layout.addWidget(self.active_tasks_card)
        stats_layout.addWidget(self.executions_card)
        stats_layout.addWidget(self.success_rate_card)

        main_layout.addLayout(stats_layout)

        # Tabs for different charts
        self.chart_tabs = QTabWidget()

        # Task status tab
        status_tab = QWidget()
        status_layout = QVBoxLayout(status_tab)

        # Placeholder for charts
        self.status_chart = PieChart({
            "Active": 0,
            "Paused": 0,
            "Completed": 0
        }, {
            "Active": "#50fa7b",
            "Paused": "#ffb86c",
            "Completed": "#8be9fd"
        })

        status_layout.addWidget(self.status_chart)
        self.chart_tabs.addTab(status_tab, "Task Status")

        # Execution history tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        # Placeholder for execution history
        self.history_chart = BarChart({
            "Mon": 0,
            "Tue": 0,
            "Wed": 0,
            "Thu": 0,
            "Fri": 0,
            "Sat": 0,
            "Sun": 0
        }, "#50fa7b")

        history_layout.addWidget(self.history_chart)
        self.chart_tabs.addTab(history_tab, "Execution History")

        # Task types tab
        types_tab = QWidget()
        types_layout = QVBoxLayout(types_tab)

        # Placeholder for task types chart
        self.types_chart = PieChart({
            "Command": 0,
            "Python": 0
        }, {
            "Command": "#8be9fd",
            "Python": "#bd93f9"
        })

        types_layout.addWidget(self.types_chart)
        self.chart_tabs.addTab(types_tab, "Task Types")

        # Add tabs to main layout
        main_layout.addWidget(self.chart_tabs)

        # Recent executions table
        main_layout.addWidget(QLabel("Recent Executions"))

        self.executions_table = QTableWidget(0, 4)
        self.executions_table.setHorizontalHeaderLabels(["Task Name", "Status", "Execution Time", "Duration"])
        self.executions_table.horizontalHeader().setStretchLastSection(True)

        main_layout.addWidget(self.executions_table)

    def update_statistics(self, schedules):
        """
        Update the statistics dashboard with data from schedules.

        Args:
            schedules: List of schedules to analyze
        """
        self.schedules = schedules if schedules is not None else []
        self._update_statistics()

    def _update_statistics(self):
        """Update all statistics based on current data and selected period."""
        if not hasattr(self, 'schedules') or not self.schedules:
            # Defensive: clear UI if no schedules
            self._update_card_value(self.total_tasks_card, "0")
            self._update_card_value(self.active_tasks_card, "0")
            self._update_card_value(self.executions_card, "0")
            self._update_card_value(self.success_rate_card, "0%")
            self.status_chart.data = {"Active": 0, "Paused": 0, "Completed": 0}
            self.history_chart.data = {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0}
            self.types_chart.data = {"Command": 0, "Python": 0}
            self.executions_table.setRowCount(0)
            self.status_chart.update()
            self.history_chart.update()
            self.types_chart.update()
            return

        # Get current time period
        period_index = self.period_combo.currentIndex()
        cutoff_date = datetime.now()

        if period_index == 0:  # Last 24 Hours
            cutoff_date -= timedelta(days=1)
        elif period_index == 1:  # Last 7 Days
            cutoff_date -= timedelta(days=7)
        elif period_index == 2:  # Last 30 Days
            cutoff_date -= timedelta(days=30)
        else:  # All Time
            cutoff_date = datetime.min

        # Calculate statistics
        total_tasks = len(self.schedules)
        active_tasks = sum(1 for s in self.schedules if not s.get('paused', False))

        # Count executions
        total_executions = 0
        success_count = 0

        for schedule in self.schedules:
            total_executions += schedule.get('execution_count', 0)
            success_count += schedule.get('success_count', 0)

        # Calculate success rate
        if total_executions > 0:
            success_rate = (success_count / total_executions) * 100
        else:
            success_rate = 0

        # Update stats cards
        self._update_card_value(self.total_tasks_card, str(total_tasks))
        self._update_card_value(self.active_tasks_card, str(active_tasks))
        self._update_card_value(self.executions_card, str(total_executions))
        self._update_card_value(self.success_rate_card, f"{success_rate:.1f}%")

        # Update status chart
        paused_tasks = sum(1 for s in self.schedules if s.get('paused', False))
        completed_tasks = 0  # No concept of "completed" in our simplified model

        self.status_chart.data = {
            "Active": active_tasks,
            "Paused": paused_tasks,
            "Completed": completed_tasks
        }

        # Create execution history data - using a simplified approach
        day_counts = {
            "Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0,
            "Fri": 0, "Sat": 0, "Sun": 0
        }

        # In a real implementation, this would analyze actual execution timestamps
        # For now, just distribute executions evenly
        if total_executions > 0:
            base_count = total_executions // 7
            remainder = total_executions % 7

            for i, day in enumerate(day_counts.keys()):
                day_counts[day] = base_count + (1 if i < remainder else 0)

        self.history_chart.data = day_counts

        # Update task types chart - all are command tasks in our implementation
        self.types_chart.data = {
            "Command": total_tasks,
            "Python": 0
        }

        # Update executions table
        self.executions_table.setRowCount(0)

        # Add recent executions (simplified)
        row_count = min(10, total_tasks)  # Show up to 10 rows

        for i in range(row_count):
            if i >= len(self.schedules):
                break

            schedule = self.schedules[i]

            # Insert new row
            self.executions_table.insertRow(i)

            # Task name
            name_item = QTableWidgetItem(schedule.get('name', f"Task-{i+1}"))
            self.executions_table.setItem(i, 0, name_item)

            # Status - simplified
            status_text = "Paused" if schedule.get('paused', False) else "Active"
            status_item = QTableWidgetItem(status_text)
            status_color = "#ffb86c" if schedule.get('paused', False) else "#50fa7b"
            status_item.setForeground(QColor(status_color))
            self.executions_table.setItem(i, 1, status_item)

            # Execution time - use last_run if available
            last_run = schedule.get('last_run', None)
            if last_run:
                try:
                    dt = datetime.fromisoformat(last_run)
                    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    time_str = "Never"
            else:
                time_str = "Never"

            time_item = QTableWidgetItem(time_str)
            self.executions_table.setItem(i, 2, time_item)

            # Duration - not tracked in our model
            duration_item = QTableWidgetItem("N/A")
            self.executions_table.setItem(i, 3, duration_item)

        # Repaint charts
        self.status_chart.update()
        self.history_chart.update()
        self.types_chart.update()

        # Update status bar (defensive)
        main_window = self.window()
        if hasattr(main_window, "statusBar"):
            try:
                main_window.statusBar().showMessage(str(len(self.schedules)) + " schedules loaded")
            except Exception:
                pass  # Don't let status bar errors break the dashboard

    def _update_card_value(self, card, value):
        """Update the value displayed on a stats card"""
        # Find the QLabel child that shows the value (second label)
        labels = card.findChildren(QLabel)
        if len(labels) >= 2:
            labels[1].setText(value)
