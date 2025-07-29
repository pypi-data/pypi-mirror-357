"""
Schedule list view component for ZScheduler
"""

import logging
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView,
    QToolBar, QLabel
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, pyqtSlot
from PyQt6.QtGui import QColor

from zscheduler_lib.zscheduler import Scheduler
from zscheduler_lib.zscheduler.core.schedule import Schedule

logger = logging.getLogger(__name__)

class ScheduleTableModel(QAbstractTableModel):
    """Table model for displaying schedules in a table view."""

    COLUMNS = ["Name", "Type", "Next Run", "Status", "Runs", "Last Run"]

    def __init__(self, parent=None):
        """Initialize the model."""
        super().__init__(parent)
        self.schedules = []

    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows."""
        return len(self.schedules)

    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        """Return the data at the given index."""
        if not index.isValid():
            return QVariant()

        if index.row() >= len(self.schedules) or index.row() < 0:
            return QVariant()

        schedule = self.schedules[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:  # Name
                return schedule.get('name') or f"Task-{schedule.get('id', '')[:8]}"
            elif index.column() == 1:  # Type
                task = schedule.get('task')
                return task.__class__.__name__ if task else ''
            elif index.column() == 2:  # Next Run
                return str(schedule.get('next_run')) if schedule.get('next_run') else "Not scheduled"
            elif index.column() == 3:  # Status
                return "Paused" if schedule.get('paused', False) else "Active"
            elif index.column() == 4:  # Runs
                return str(schedule.get('run_count'))
            elif index.column() == 5:  # Last Run
                return str(schedule.get('last_run')) if schedule.get('last_run') else "Never"

        elif role == Qt.ItemDataRole.BackgroundRole:
            # Highlight paused schedules
            if schedule.get('paused', False) and index.column() == 3:
                return QColor(255, 200, 200)

        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        """Return the header data."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.COLUMNS[section]

        return QVariant()

    def update_schedules(self, schedules: List[Schedule]) -> None:
        """Update the model with new schedules."""
        self.beginResetModel()
        self.schedules = schedules
        self.endResetModel()

class ScheduleListView(QWidget):
    """Widget for displaying schedules in a table view."""

    def __init__(self, scheduler: Scheduler, parent=None):
        """Initialize the view."""
        super().__init__(parent)
        self.scheduler = scheduler

        # Create layout
        layout = QVBoxLayout(self)

        # Create table view
        self.table_view = QTableView()
        self.table_model = ScheduleTableModel()
        self.table_view.setModel(self.table_model)

        # Configure table view
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Add to layout
        layout.addWidget(self.table_view)

        # Set layout
        self.setLayout(layout)

    def update_schedules(self, schedules: List[Schedule]) -> None:
        """Update the view with new schedules."""
        self.table_model.update_schedules(schedules)

    def get_selected_schedule(self) -> Optional[Schedule]:
        """Return the currently selected schedule."""
        indexes = self.table_view.selectionModel().selectedIndexes()
        if not indexes:
            return None

        row = indexes[0].row()
        return self.table_model.schedules[row] if 0 <= row < len(self.table_model.schedules) else None
