"""
Theme Manager for ZScheduler UI
"""

from typing import Dict, Any, Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class ThemeManager:
    """
    Manages application theming and color schemes.

    This class provides functionality to apply dark and light themes
    with the specified color schemes to the entire application.
    """

    # Default theme colors
    DEFAULT_DARK_THEME = {
        "background": "#0a192f",
        "text": "#f1fa8c",
        "accent": "#50fa7b",
        "info": "#8be9fd",
        "warning": "#ffb86c",
        "error": "#ff5555"
    }

    DEFAULT_LIGHT_THEME = {
        "background": "#e0f2e9",
        "text": "#0a192f",
        "accent": "#1a365d",
        "info": "#3182ce",
        "warning": "#dd6b20",
        "error": "#e53e3e"
    }

    def __init__(self, config):
        """
        Initialize the theme manager.

        Args:
            config: Application configuration object
        """
        self.config = config
        self.current_theme = config.get("ui.theme", "dark")

    def get_theme_colors(self) -> Dict[str, str]:
        """
        Get the current theme colors.

        Returns:
            Dictionary of color values for the theme
        """
        if self.current_theme == "dark":
            colors = self.DEFAULT_DARK_THEME.copy()
            # Override with any config-specific colors if available
            config_colors = self.config.get("ui.theme.dark_colors", {})
            colors.update(config_colors)
        else:
            colors = self.DEFAULT_LIGHT_THEME.copy()
            # Override with any config-specific colors if available
            config_colors = self.config.get("ui.theme.light_colors", {})
            colors.update(config_colors)

        return colors

    def apply_theme(self, theme_name: str) -> None:
        """
        Apply the specified theme to the application.

        Args:
            theme_name: Theme name ('dark', 'light', or 'system')
        """
        # Handle system theme
        if theme_name == "system":
            # Default to dark theme for now - could detect system theme in a real implementation
            theme_name = "dark"

        self.current_theme = theme_name

        # Get theme colors
        colors = self.get_theme_colors()

        # Apply the theme
        if theme_name == "dark":
            self._apply_dark_theme(colors)
        else:
            self._apply_light_theme(colors)

    def _apply_dark_theme(self, colors: Dict[str, str]) -> None:
        """
        Apply the dark theme to the application.

        Args:
            colors: Dictionary of color values for the theme
        """
        app = QApplication.instance()
        if not app:
            return

        # Create a dark palette
        palette = QPalette()

        # Set colors based on the theme
        bg_color = QColor(colors.get("background", "#0a192f"))
        text_color = QColor(colors.get("text", "#f1fa8c"))
        accent_color = QColor(colors.get("accent", "#50fa7b"))

        # Base colors
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QPalette.ColorRole.Base, QColor(bg_color).darker(110))
        palette.setColor(QPalette.ColorRole.AlternateBase, bg_color)
        palette.setColor(QPalette.ColorRole.ToolTipBase, bg_color)
        palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.Button, bg_color)
        palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.white)

        # Disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(text_color).darker(150))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(text_color).darker(150))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(text_color).darker(150))

        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, accent_color)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(bg_color))

        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(colors.get("info", "#8be9fd")))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(colors.get("info", "#8be9fd")).darker(120))

        # Apply palette to application
        app.setPalette(palette)

        # Apply stylesheet for additional styling
        app.setStyleSheet(self._get_dark_stylesheet(colors))

    def _apply_light_theme(self, colors: Dict[str, str]) -> None:
        """
        Apply the light theme to the application.

        Args:
            colors: Dictionary of color values for the theme
        """
        app = QApplication.instance()
        if not app:
            return

        # Create a light palette
        palette = QPalette()

        # Set colors based on the theme
        bg_color = QColor(colors.get("background", "#e0f2e9"))
        text_color = QColor(colors.get("text", "#0a192f"))
        accent_color = QColor(colors.get("accent", "#1a365d"))

        # Base colors
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QPalette.ColorRole.Base, QColor(bg_color).lighter(110))
        palette.setColor(QPalette.ColorRole.AlternateBase, bg_color)
        palette.setColor(QPalette.ColorRole.ToolTipBase, bg_color)
        palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.Button, bg_color)
        palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.black)

        # Disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(text_color).lighter(150))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(text_color).lighter(150))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(text_color).lighter(150))

        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, accent_color)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(bg_color))

        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(colors.get("info", "#3182ce")))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(colors.get("info", "#3182ce")).darker(120))

        # Apply palette to application
        app.setPalette(palette)

        # Apply stylesheet for additional styling
        app.setStyleSheet(self._get_light_stylesheet(colors))

    def _get_dark_stylesheet(self, colors: Dict[str, str]) -> str:
        """
        Get the dark theme stylesheet.

        Args:
            colors: Dictionary of color values for the theme

        Returns:
            CSS stylesheet string
        """
        return f"""
        QMainWindow, QDialog, QWidget {{
            background-color: {colors.get("background", "#0a192f")};
            color: {colors.get("text", "#f1fa8c")};
        }}

        QMenuBar, QMenu {{
            background-color: {QColor(colors.get("background", "#0a192f")).darker(110).name()};
            color: {colors.get("text", "#f1fa8c")};
        }}

        QMenuBar::item:selected, QMenu::item:selected {{
            background-color: {colors.get("accent", "#50fa7b")};
            color: {colors.get("background", "#0a192f")};
        }}

        QTabWidget::pane {{
            border: 1px solid {QColor(colors.get("accent", "#50fa7b")).darker(150).name()};
        }}

        QTabBar::tab {{
            background-color: {QColor(colors.get("background", "#0a192f")).darker(120).name()};
            color: {colors.get("text", "#f1fa8c")};
            padding: 8px 12px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background-color: {colors.get("accent", "#50fa7b")};
            color: {colors.get("background", "#0a192f")};
        }}

        QPushButton {{
            background-color: {QColor(colors.get("background", "#0a192f")).darker(120).name()};
            color: {colors.get("text", "#f1fa8c")};
            border: 1px solid {colors.get("accent", "#50fa7b")};
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QPushButton:hover {{
            background-color: {QColor(colors.get("accent", "#50fa7b")).darker(120).name()};
            color: {colors.get("background", "#0a192f")};
        }}

        QPushButton:pressed {{
            background-color: {colors.get("accent", "#50fa7b")};
            color: {colors.get("background", "#0a192f")};
        }}

        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDateTimeEdit {{
            background-color: {QColor(colors.get("background", "#0a192f")).darker(110).name()};
            color: {colors.get("text", "#f1fa8c")};
            border: 1px solid {QColor(colors.get("accent", "#50fa7b")).darker(150).name()};
            border-radius: 4px;
            padding: 4px;
        }}

        QTableView, QTreeView, QListView {{
            background-color: {QColor(colors.get("background", "#0a192f")).darker(110).name()};
            color: {colors.get("text", "#f1fa8c")};
            alternate-background-color: {QColor(colors.get("background", "#0a192f")).darker(120).name()};
            border: 1px solid {QColor(colors.get("accent", "#50fa7b")).darker(150).name()};
        }}

        QHeaderView::section {{
            background-color: {QColor(colors.get("background", "#0a192f")).darker(130).name()};
            color: {colors.get("text", "#f1fa8c")};
            padding: 4px;
            border: 1px solid {QColor(colors.get("accent", "#50fa7b")).darker(150).name()};
        }}

        QScrollBar {{
            background-color: {QColor(colors.get("background", "#0a192f")).darker(110).name()};
            border-radius: 4px;
        }}

        QScrollBar::handle {{
            background-color: {QColor(colors.get("accent", "#50fa7b")).darker(150).name()};
            border-radius: 4px;
        }}

        QToolTip {{
            background-color: {colors.get("background", "#0a192f")};
            color: {colors.get("text", "#f1fa8c")};
            border: 1px solid {colors.get("accent", "#50fa7b")};
            padding: 4px;
        }}
        """

    def _get_light_stylesheet(self, colors: Dict[str, str]) -> str:
        """
        Get the light theme stylesheet.

        Args:
            colors: Dictionary of color values for the theme

        Returns:
            CSS stylesheet string
        """
        return f"""
        QMainWindow, QDialog, QWidget {{
            background-color: {colors.get("background", "#e0f2e9")};
            color: {colors.get("text", "#0a192f")};
        }}

        QMenuBar, QMenu {{
            background-color: {QColor(colors.get("background", "#e0f2e9")).darker(110).name()};
            color: {colors.get("text", "#0a192f")};
        }}

        QMenuBar::item:selected, QMenu::item:selected {{
            background-color: {colors.get("accent", "#1a365d")};
            color: {colors.get("background", "#e0f2e9")};
        }}

        QTabWidget::pane {{
            border: 1px solid {QColor(colors.get("accent", "#1a365d")).lighter(150).name()};
        }}

        QTabBar::tab {{
            background-color: {QColor(colors.get("background", "#e0f2e9")).darker(110).name()};
            color: {colors.get("text", "#0a192f")};
            padding: 8px 12px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background-color: {colors.get("accent", "#1a365d")};
            color: {colors.get("background", "#e0f2e9")};
        }}

        QPushButton {{
            background-color: {QColor(colors.get("background", "#e0f2e9")).darker(110).name()};
            color: {colors.get("text", "#0a192f")};
            border: 1px solid {colors.get("accent", "#1a365d")};
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QPushButton:hover {{
            background-color: {QColor(colors.get("accent", "#1a365d")).lighter(120).name()};
            color: {colors.get("background", "#e0f2e9")};
        }}

        QPushButton:pressed {{
            background-color: {colors.get("accent", "#1a365d")};
            color: {colors.get("background", "#e0f2e9")};
        }}

        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDateTimeEdit {{
            background-color: {QColor(colors.get("background", "#e0f2e9")).lighter(110).name()};
            color: {colors.get("text", "#0a192f")};
            border: 1px solid {QColor(colors.get("accent", "#1a365d")).lighter(150).name()};
            border-radius: 4px;
            padding: 4px;
        }}

        QTableView, QTreeView, QListView {{
            background-color: {QColor(colors.get("background", "#e0f2e9")).lighter(105).name()};
            color: {colors.get("text", "#0a192f")};
            alternate-background-color: {QColor(colors.get("background", "#e0f2e9")).darker(105).name()};
            border: 1px solid {QColor(colors.get("accent", "#1a365d")).lighter(150).name()};
        }}

        QHeaderView::section {{
            background-color: {QColor(colors.get("background", "#e0f2e9")).darker(110).name()};
            color: {colors.get("text", "#0a192f")};
            padding: 4px;
            border: 1px solid {QColor(colors.get("accent", "#1a365d")).lighter(150).name()};
        }}

        QScrollBar {{
            background-color: {QColor(colors.get("background", "#e0f2e9")).lighter(105).name()};
            border-radius: 4px;
        }}

        QScrollBar::handle {{
            background-color: {QColor(colors.get("accent", "#1a365d")).lighter(150).name()};
            border-radius: 4px;
        }}

        QToolTip {{
            background-color: {colors.get("background", "#e0f2e9")};
            color: {colors.get("text", "#0a192f")};
            border: 1px solid {colors.get("accent", "#1a365d")};
            padding: 4px;
        }}
        """

    def toggle_theme(self) -> None:
        """
        Toggle between dark and light themes.
        """
        next_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(next_theme)
