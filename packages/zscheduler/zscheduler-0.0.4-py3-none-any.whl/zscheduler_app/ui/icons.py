"""
Icon resources for ZScheduler application
"""

import os
import sys
import base64
import tempfile
from pathlib import Path

from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QFont, QPen, QBrush
from PyQt6.QtCore import QSize, Qt


# Base64 encoded icon data - created with a simple clock icon
ICON_DARK = """
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
"""

ICON_LIGHT = """
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
"""


class IconProvider:
    """
    Provides application icons in various formats and themes
    """

    _instance = None
    _icons = {}

    @staticmethod
    def get_instance():
        """Get the singleton instance of IconProvider"""
        if IconProvider._instance is None:
            IconProvider._instance = IconProvider()
        return IconProvider._instance

    def __init__(self):
        """Initialize the icon provider"""
        if IconProvider._instance is not None:
            raise RuntimeError("IconProvider is a singleton. Use get_instance() instead.")

        # Create icons from base64 data
        self._icons['app_dark'] = self._create_icon_from_base64(ICON_DARK)
        self._icons['app_light'] = self._create_icon_from_base64(ICON_LIGHT)

    def _create_icon_from_base64(self, base64_data):
        """
        Create a QIcon from base64 encoded data

        Args:
            base64_data: The base64 encoded image data

        Returns:
            QIcon object created from the data
        """
        try:
            # Clean up the base64 data - remove whitespace and newlines
            clean_data = ''.join(base64_data.strip().split())

            # Create a pixmap from the base64 data
            pixmap = QPixmap()
            if not pixmap.loadFromData(base64.b64decode(clean_data)):
                # If loading fails, create a simple colored square as fallback
                pixmap = QPixmap(64, 64)
                pixmap.fill(QColor("#50fa7b"))

            # Create an icon from the pixmap
            return QIcon(pixmap)
        except Exception as e:
            # Log the error and return a fallback icon
            print(f"Error creating icon: {e}")
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("#50fa7b"))
            return QIcon(pixmap)

    def get_app_icon(self, theme='dark'):
        """
        Get the application icon for the specified theme

        Args:
            theme: 'dark' or 'light'

        Returns:
            QIcon object for the application
        """
        key = 'app_dark' if theme == 'dark' else 'app_light'
        return self._icons[key]

    def set_window_icon(self, window, theme='dark'):
        """
        Set the icon for a window

        Args:
            window: The window to set the icon for
            theme: 'dark' or 'light'
        """
        window.setWindowIcon(self.get_app_icon(theme))

    def save_system_tray_icon(self, theme='dark'):
        """
        Save the icon to a temporary file for system tray use

        Args:
            theme: 'dark' or 'light'

        Returns:
            Path to the temporary icon file
        """
        # Create a temporary file
        fd, path = tempfile.mkstemp(suffix='.png')
        os.close(fd)

        # Save the icon as PNG
        key = 'app_dark' if theme == 'dark' else 'app_light'
        self._icons[key].pixmap(48, 48).save(path, 'PNG')

        return path

class IconManager:
    """
    Manages application icons based on the style guide.
    """

    # Icon sizes
    SMALL = QSize(16, 16)
    MEDIUM = QSize(24, 24)
    LARGE = QSize(32, 32)

    @staticmethod
    def get_icon_path(icon_name):
        """Get the path to an icon file."""
        # In a real implementation, this would look for SVG files
        # For now, we'll use text-based icons
        return None

    @staticmethod
    def get_icon(icon_name):
        """Get a QIcon for the specified icon name."""
        path = IconManager.get_icon_path(icon_name)
        if path and os.path.exists(path):
            return QIcon(path)
        else:
            # Return a text icon
            return IconManager.create_text_icon(icon_name[0].upper() if icon_name else "?")

    @staticmethod
    def create_text_icon(text, size=SMALL, bg_color="#d1ffd1", text_color="#00008B"):
        """Create a text-based icon when an image is not available."""
        # Create a pixmap
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter and draw the text
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background circle
        painter.setPen(QPen(QColor(bg_color)))
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.drawEllipse(0, 0, size.width(), size.height())

        # Draw text
        font = QFont("Arial", size.width() // 2)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(text_color)))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)

        painter.end()

        return QIcon(pixmap)

    # Define methods for common icons
    @staticmethod
    def new_icon():
        return IconManager.create_text_icon("N")

    @staticmethod
    def edit_icon():
        return IconManager.create_text_icon("E")

    @staticmethod
    def delete_icon():
        return IconManager.create_text_icon("D")

    @staticmethod
    def start_icon():
        return IconManager.create_text_icon("S")

    @staticmethod
    def stop_icon():
        return IconManager.create_text_icon("X")

    @staticmethod
    def pause_icon():
        return IconManager.create_text_icon("P")

    @staticmethod
    def resume_icon():
        return IconManager.create_text_icon("R")

    @staticmethod
    def run_now_icon():
        return IconManager.create_text_icon("►")

    @staticmethod
    def settings_icon():
        return IconManager.create_text_icon("⚙")

    @staticmethod
    def about_icon():
        return IconManager.create_text_icon("?")
