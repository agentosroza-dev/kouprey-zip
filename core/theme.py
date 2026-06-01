from __future__ import annotations

from dataclasses import dataclass, field

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


@dataclass(frozen=True)
class WinUIColorTokens:
    surface: str = "#F2F2F2"
    surface_alt: str = "#FFFFFF"
    surface_card: str = "#FFFFFF"
    surface_elevated: str = "#FFFFFF"
    base: str = "#EAEAEA"
    base_alt: str = "#D9D9D9"
    text_primary: str = "#1A1A1A"
    text_secondary: str = "#616161"
    text_tertiary: str = "#8B8B8B"
    text_disabled: str = "#A0A0A0"
    accent: str = "#005FB8"
    accent_light: str = "#E0EFFA"
    accent_hover: str = "#004A93"
    accent_pressed: str = "#00376E"
    border: str = "#E0E0E0"
    border_subtle: str = "#EFEFEF"
    border_input: str = "#C0C0C0"
    red: str = "#C42B1C"
    green: str = "#0E8341"
    orange: str = "#CC7000"
    yellow: str = "#FCE100"
    mica_background: str = "#F3F3F3"
    acrylic_background: str = "rgba(255, 255, 255, 0.85)"
    shadow: str = "rgba(0, 0, 0, 0.08)"
    shadow_elevated: str = "rgba(0, 0, 0, 0.14)"
    tab_selected_bg: str = "#E0EFFA"
    nav_hover_bg: str = "rgba(0, 0, 0, 0.04)"
    nav_pressed_bg: str = "rgba(0, 0, 0, 0.06)"
    nav_selected_bg: str = "#E0EFFA"
    progress_track: str = "#D9D9D9"
    scrollbar_thumb: str = "rgba(0, 0, 0, 0.15)"
    scrollbar_hover: str = "rgba(0, 0, 0, 0.25)"
    info_bar_info: str = "#E0EFFA"
    info_bar_success: str = "#DFF6DD"
    info_bar_warning: str = "#FFF4CE"
    info_bar_error: str = "#FDE7E9"
    accent_text: str = "#FFFFFF"


@dataclass(frozen=True)
class DarkWinUIColorTokens:
    surface: str = "#1F1F1F"
    surface_alt: str = "#2C2C2C"
    surface_card: str = "#333333"
    surface_elevated: str = "#383838"
    base: str = "#454545"
    base_alt: str = "#505050"
    text_primary: str = "#F2F2F2"
    text_secondary: str = "#ABABAB"
    text_tertiary: str = "#8B8B8B"
    text_disabled: str = "#6F6F6F"
    accent: str = "#60CDFF"
    accent_light: str = "#1A3A4A"
    accent_hover: str = "#7FD8FF"
    accent_pressed: str = "#A0E4FF"
    border: str = "#454545"
    border_subtle: str = "#383838"
    border_input: str = "#555555"
    red: str = "#E74856"
    green: str = "#13A10E"
    orange: str = "#FF8C00"
    yellow: str = "#FCE100"
    mica_background: str = "#202020"
    acrylic_background: str = "rgba(44, 44, 44, 0.85)"
    shadow: str = "rgba(0, 0, 0, 0.32)"
    shadow_elevated: str = "rgba(0, 0, 0, 0.48)"
    tab_selected_bg: str = "#1A3A4A"
    nav_hover_bg: str = "rgba(255, 255, 255, 0.06)"
    nav_pressed_bg: str = "rgba(255, 255, 255, 0.08)"
    nav_selected_bg: str = "#1A3A4A"
    progress_track: str = "#505050"
    scrollbar_thumb: str = "rgba(255, 255, 255, 0.15)"
    scrollbar_hover: str = "rgba(255, 255, 255, 0.25)"
    info_bar_info: str = "#1A3A4A"
    info_bar_success: str = "#1A3A1A"
    info_bar_warning: str = "#3A3A1A"
    info_bar_error: str = "#3A1A1A"
    accent_text: str = "#1A1A1A"


LIGHT = WinUIColorTokens()
DARK = DarkWinUIColorTokens()


class ThemeManager:
    def __init__(self, app: QApplication):
        self._app = app
        self._current = LIGHT

    @property
    def colors(self) -> WinUIColorTokens | DarkWinUIColorTokens:
        return self._current

    def set_mode(self, mode: str) -> None:
        self._current = DARK if mode == "dark" else LIGHT
        from core.icons import set_icon_color
        set_icon_color(self._current.text_primary)
        self._apply_palette()
        self._apply_stylesheet()

    def _apply_palette(self) -> None:
        c = self._current
        p = QPalette()

        p.setColor(QPalette.ColorRole.Window, QColor(c.surface))
        p.setColor(QPalette.ColorRole.WindowText, QColor(c.text_primary))
        p.setColor(QPalette.ColorRole.Base, QColor(c.surface_card))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor(c.surface_alt))
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor(c.surface_elevated))
        p.setColor(QPalette.ColorRole.ToolTipText, QColor(c.text_primary))
        p.setColor(QPalette.ColorRole.Text, QColor(c.text_primary))
        p.setColor(QPalette.ColorRole.Button, QColor(c.surface_alt))
        p.setColor(QPalette.ColorRole.ButtonText, QColor(c.text_primary))
        p.setColor(QPalette.ColorRole.BrightText, QColor(c.text_primary))
        p.setColor(QPalette.ColorRole.Link, QColor(c.accent))
        p.setColor(QPalette.ColorRole.Highlight, QColor(c.accent))
        p.setColor(
            QPalette.ColorRole.HighlightedText,
            QColor(c.accent_text),
        )

        self._app.setPalette(p)

    def _apply_stylesheet(self) -> None:
        self._app.setStyleSheet(build_winui_stylesheet(self._current))


def build_winui_stylesheet(c: WinUIColorTokens | DarkWinUIColorTokens) -> str:
    return f"""
QMainWindow {{
    background-color: {c.mica_background};
}}

QWidget {{
    color: {c.text_primary};
    font-family: "AgentosUI", "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-size: 11pt;
}}

QMenuBar {{
    background: transparent;
    border: none;
    padding: 2px 0;
    spacing: 4px;
}}
QMenuBar::item {{
    padding: 6px 12px;
    border-radius: 4px;
    background: transparent;
}}
QMenuBar::item:selected {{
    background: {c.nav_hover_bg};
}}
QMenuBar::item:pressed {{
    background: {c.nav_pressed_bg};
}}

QMenu {{
    background: {c.surface_elevated};
    border: 1px solid {c.border};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 8px 28px 8px 16px;
    border-radius: 4px;
    font-size: 11pt;
}}
QMenu::item:selected {{
    background: {c.accent_light};
    color: {c.text_primary};
}}
QMenu::separator {{
    height: 1px;
    background: {c.border_subtle};
    margin: 4px 8px;
}}

QPushButton {{
    background: {c.surface_alt};
    color: {c.text_primary};
    border: 1px solid {c.border};
    border-radius: 6px;
    padding: 6px 18px;
    font-size: 11pt;
    font-weight: 500;
    min-height: 28px;
}}
QPushButton:hover {{
    background: {c.nav_hover_bg};
    border-color: {c.border_input};
}}
QPushButton:pressed {{
    background: {c.nav_pressed_bg};
}}
QPushButton:disabled {{
    color: {c.text_disabled};
    background: {c.base};
    border-color: {c.border_subtle};
}}

QPushButton#accentButton {{
    background: {c.accent};
    color: {c.accent_text};
    border: 1px solid {c.accent};
    font-weight: 600;
}}
QPushButton#accentButton:hover {{
    background: {c.accent_hover};
    border-color: {c.accent_hover};
}}
QPushButton#accentButton:pressed {{
    background: {c.accent_pressed};
}}

QPushButton#dropdownButton {{
    text-align: left;
    padding: 6px 12px;
    min-height: 28px;
}}
QPushButton#dropdownButton::menu-indicator {{
    image: none;
}}

QPushButton#navigationButton {{
    background: transparent;
    border: none;
    border-radius: 6px;
    text-align: left;
    padding: 10px 16px;
    font-size: 11pt;
}}
QPushButton#navigationButton:hover {{
    background: {c.nav_hover_bg};
}}
QPushButton#navigationButton:checked {{
    background: {c.nav_selected_bg};
    border-left: 3px solid {c.accent};
}}
QPushButton#navigationButton:pressed {{
    background: {c.nav_pressed_bg};
}}

QToolBar {{
    background: {c.surface_alt};
    border: none;
    border-bottom: 1px solid {c.border};
    padding: 4px 8px;
    spacing: 4px;
}}

QLabel {{
    color: {c.text_primary};
    background: transparent;
}}
QLabel#titleLabel {{
    font-size: 18pt;
    font-weight: 600;
    color: {c.text_primary};
}}
QLabel#subtitleLabel {{
    font-size: 11pt;
    color: {c.text_secondary};
}}
QLabel#captionLabel {{
    font-size: 9pt;
    color: {c.text_tertiary};
}}

QLabel#appLogo {{
    font-size: 16pt;
    font-weight: 600;
    color: {c.accent};
    padding: 8px 12px 4px;
}}

QLabel#pageTitle {{
    font-size: 16pt;
    font-weight: 600;
    color: {c.text_primary};
    padding: 12px 24px 0;
}}

QLineEdit {{
    background: {c.surface_alt};
    color: {c.text_primary};
    border: 1px solid {c.border_input};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 11pt;
    selection-background-color: {c.accent_light};
}}
QLineEdit:focus {{
    border: 2px solid {c.accent};
    padding: 7px 11px;
}}
QLineEdit:disabled {{
    background: {c.base};
    color: {c.text_disabled};
}}

QTextEdit, QPlainTextEdit {{
    background: {c.surface_alt};
    color: {c.text_primary};
    border: 1px solid {c.border_input};
    border-radius: 6px;
    padding: 8px;
    font-size: 11pt;
    selection-background-color: {c.accent_light};
}}
QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {c.accent};
}}

QSpinBox, QDoubleSpinBox {{
    background: {c.surface_alt};
    color: {c.text_primary};
    border: 1px solid {c.border_input};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 11pt;
    min-height: 28px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {c.accent};
}}

QComboBox {{
    background: {c.surface_alt};
    color: {c.text_primary};
    border: 1px solid {c.border_input};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11pt;
    min-height: 24px;
}}
QComboBox:hover {{
    border-color: {c.border};
}}
QComboBox:focus {{
    border: 2px solid {c.accent};
    padding: 3px 7px;
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border: none;
}}
QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}
QComboBox QAbstractItemView {{
    background: {c.surface_elevated};
    border: 1px solid {c.border};
    border-radius: 0px;
    padding: 0px;
    outline: none;
    min-height: 48px;
    height: auto;
}}
QComboBox QAbstractItemView::item {{
    padding: 6px 12px;
    min-height: 48px;
    color: {c.text_primary};
}}
QComboBox QAbstractItemView::item {{
    padding: 4px 10px;
    min-height: 48px;
    color: {c.text_primary};
}}
QComboBox QAbstractItemView::item:selected {{
    background: {c.accent_light};
    color: {c.text_primary};
}}

QCheckBox {{
    spacing: 10px;
    font-size: 11pt;
    color: {c.text_primary};
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {c.base_alt};
    border-radius: 4px;
    background: {c.surface_alt};
}}
QCheckBox::indicator:checked {{
    background: {c.accent};
    border-color: {c.accent};
}}
QCheckBox::indicator:hover {{
    border-color: {c.accent};
}}

QRadioButton {{
    spacing: 8px;
    font-size: 11pt;
}}
QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {c.base_alt};
    border-radius: 10px;
    background: {c.surface_alt};
}}
QRadioButton::indicator:checked {{
    background: {c.accent};
    border-color: {c.accent};
}}

QTableWidget {{
    background: {c.surface_card};
    border: 1px solid {c.border};
    border-radius: 8px;
    gridline-color: transparent;
    selection-background-color: {c.accent_light};
    selection-color: {c.text_primary};
    font-size: 11pt;
}}
QTableWidget::item {{
    padding: 8px 12px;
    min-height: 36px;
    border-bottom: 1px solid {c.border_subtle};
}}
QTableWidget::item:selected {{
    background: {c.accent_light};
    color: {c.text_primary};
}}
QHeaderView::section {{
    background: transparent;
    color: {c.text_secondary};
    font-size: 8.5pt;
    font-weight: 600;
    text-transform: uppercase;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid {c.border};
}}

QTreeWidget {{
    background: {c.surface_card};
    border: 1px solid {c.border};
    border-radius: 8px;
    selection-background-color: {c.accent_light};
    selection-color: {c.text_primary};
}}
QTreeWidget::item {{
    padding: 6px 8px;
    min-height: 28px;
}}
QTreeWidget::item:selected {{
    background: {c.accent_light};
}}

QListWidget {{
    background: {c.surface_alt};
    color: {c.text_primary};
    border: 1px solid {c.border_input};
    border-radius: 6px;
    font-size: 11pt;
    outline: none;
}}
QListWidget::item {{
    padding: 6px 12px;
    border-radius: 4px;
}}
QListWidget::item:selected {{
    background: {c.accent_light};
    color: {c.text_primary};
}}
QListWidget::item:hover {{
    background: {c.nav_hover_bg};
}}

QProgressBar {{
    background: {c.progress_track};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    font-size: 8pt;
    color: transparent;
}}
QProgressBar::chunk {{
    background: {c.accent};
    border-radius: 4px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    border: none;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {c.scrollbar_thumb};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {c.scrollbar_hover};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {c.scrollbar_thumb};
    border-radius: 3px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {c.scrollbar_hover};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QTabWidget::pane {{
    background: transparent;
    border: none;
}}
QTabBar::tab {{
    background: transparent;
    color: {c.text_secondary};
    padding: 8px 16px;
    font-size: 11pt;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    color: {c.accent};
    border-bottom: 2px solid {c.accent};
}}
QTabBar::tab:hover {{
    color: {c.text_primary};
    background: {c.nav_hover_bg};
}}

QGroupBox {{
    background: {c.surface_card};
    border: 1px solid {c.border};
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px 16px 16px 16px;
    font-size: 11pt;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background: {c.surface_card};
    color: {c.text_primary};
}}

QFrame#card {{
    background: {c.surface_card};
    border: 1px solid {c.border};
    border-radius: 8px;
}}

QFrame#navPanel {{
    background: {c.surface_alt};
    border: none;
    border-right: 1px solid {c.border};
}}

QFrame#infoBar {{
    background: {c.info_bar_info};
    border: none;
    border-radius: 6px;
    padding: 12px 16px;
}}

QSplitter::handle {{
    background: {c.border};
    width: 1px;
    height: 1px;
}}

QStatusBar {{
    background: transparent;
    border-top: 1px solid {c.border};
    color: {c.text_secondary};
    font-size: 10pt;
    padding: 2px 8px;
}}

QFrame#footer {{
    background: transparent;
    border-top: 1px solid {c.border};
}}

QLabel#footerLabel {{
    color: {c.text_tertiary};
    font-size: 9pt;
}}

QDialog {{
    background: {c.mica_background};
}}
"""
