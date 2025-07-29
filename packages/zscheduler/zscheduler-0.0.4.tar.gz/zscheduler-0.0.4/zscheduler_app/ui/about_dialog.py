"""
About dialog for ZScheduler application
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox,
    QTabWidget, QWidget, QTextBrowser, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont

from zscheduler_app import __version__
from zscheduler_app.ui.icons import IconProvider

logger = logging.getLogger(__name__)

class AboutDialog(QDialog):
    """
    Dialog showing information about the application
    """

    def __init__(self, parent=None):
        """
        Initialize the about dialog

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("About ZScheduler")
        self.resize(500, 400)
        self.setModal(True)

        # Create UI
        self._setup_ui()

    def _setup_ui(self):
        """Set up the about UI"""
        layout = QVBoxLayout(self)

        # Header with app name and version
        header_layout = QHBoxLayout()

        # App icon
        icon_provider = IconProvider.get_instance()
        icon_label = QLabel()
        pixmap = icon_provider.get_app_icon().pixmap(64, 64)
        icon_label.setPixmap(pixmap)
        header_layout.addWidget(icon_label)

        # App name and version
        title_layout = QVBoxLayout()

        app_name = QLabel("ZScheduler")
        font = app_name.font()
        font.setPointSize(16)
        font.setBold(True)
        app_name.setFont(font)
        title_layout.addWidget(app_name)

        version = QLabel(f"Version {__version__}")
        title_layout.addWidget(version)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Tab widget for different sections
        tabs = QTabWidget()

        # About tab
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)

        about_text = QTextBrowser()
        about_text.setOpenExternalLinks(True)
        about_text.setHtml("""
        <p>ZScheduler is a high-performance task scheduling application with an intuitive user interface.</p>

        <p>Key features:</p>
        <ul>
            <li>Multiple visualization options: List, Calendar, and Timeline views</li>
            <li>Flexible scheduling: Interval-based, cron expressions, and one-time schedules</li>
            <li>Dark and light themes</li>
            <li>System tray integration</li>
            <li>Detailed statistics and insights</li>
        </ul>

        <p>Built with Python and PyQt6.</p>
        """)

        about_layout.addWidget(about_text)
        tabs.addTab(about_tab, "About")

        # License tab
        license_tab = QWidget()
        license_layout = QVBoxLayout(license_tab)

        license_text = QTextBrowser()
        license_text.setHtml("""
        <h3>MIT License</h3>

        <p>Copyright (c) 2024 ZScheduler Contributors</p>

        <p>Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:</p>

        <p>The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.</p>

        <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.</p>
        """)

        license_layout.addWidget(license_text)
        tabs.addTab(license_tab, "License")

        # Credits tab
        credits_tab = QWidget()
        credits_layout = QVBoxLayout(credits_tab)

        credits_text = QTextBrowser()
        credits_text.setHtml("""
        <h3>Credits</h3>

        <p>ZScheduler uses the following third-party libraries:</p>

        <ul>
            <li>PyQt6 - Licensed under GPL v3</li>
            <li>PyQtGraph - Licensed under MIT</li>
            <li>python-dateutil - Licensed under BSD-3-Clause</li>
        </ul>

        <p>Special thanks to all contributors and open source software that made this possible.</p>
        """)

        credits_layout.addWidget(credits_text)
        tabs.addTab(credits_tab, "Credits")

        layout.addWidget(tabs)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
