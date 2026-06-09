import os

from PyQt6.QtCore import QSize, QTimer, Qt
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QStackedWidget, QStatusBar, QToolBar,
    QVBoxLayout, QWidget,
)

from core.icons import lucide_icon
from core.language import LanguageManager
from core.theme import ThemeManager
from ui.archive_page import ArchivePage
from ui.compress_page import CompressPage
from ui.encrypt_page import EncryptPage
from ui.settings_page import SettingsPage
from ui.about_dialog import AboutDialog


_NAV_ICONS: dict[str, str] = {
    "nav_archive": "folder-open",
    "nav_compress": "package",
    "nav_encrypt": "lock",
    "nav_settings": "settings",
}


class NavButton(QPushButton):
    def __init__(self, icon_name: str, text: str, parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._label = text
        self.setObjectName("navigationButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(44)
        self._update_display()

    def _update_display(self):
        self.setText(f"  {self._label}")
        self.setIcon(lucide_icon(self._icon_name, 18))

    def set_text(self, text: str):
        self._label = text
        self._update_display()

    def set_active(self, active: bool):
        self.setChecked(active)


class MainWindow(QMainWindow):
    NAV_ITEMS = [
        ("nav_archive", "archive_page"),
        ("nav_compress", "compress_page"),
        ("nav_encrypt", "encrypt_page"),
        ("nav_settings", "settings_page"),
    ]

    def __init__(self, lang: LanguageManager, theme: ThemeManager,
                 compress_paths: list[str] | None = None,
                 open_path: str | None = None,
                 extract_path: str | None = None):
        super().__init__()
        self._lang = lang
        self._theme = theme
        self._nav_buttons: list[NavButton] = []
        self._pages: dict[str, QWidget] = {}
        self._setup_ui()
        self._apply_font()
        self._build_pages()
        self._retranslate()
        self._navigate_to("archive_page")
        if compress_paths:
            self._navigate_to("compress_page")
            cp = self._pages.get("compress_page")
            if cp and hasattr(cp, "set_files"):
                cp.set_files(compress_paths)
        elif open_path:
            ap = self._pages.get("archive_page")
            if ap and hasattr(ap, "open_archive"):
                ap.open_archive(open_path)
        elif extract_path:
            ap = self._pages.get("archive_page")
            if ap and hasattr(ap, "open_archive"):
                ap.open_archive(extract_path)

    def _setup_ui(self):
        self.setMinimumSize(900, 600)
        self.resize(1100, 720)
        _icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "app.ico")
        if os.path.isfile(_icon_path):
            self.setWindowIcon(QIcon(_icon_path))

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._nav_panel = self._build_nav_panel()
        root_layout.addWidget(self._nav_panel)

        right_area = QWidget()
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._command_bar = QToolBar()
        self._command_bar.setObjectName("commandBar")
        self._command_bar.setMovable(False)
        self._command_bar.setIconSize(QSize(18, 18))
        right_layout.addWidget(self._command_bar)

        self._page_title = QLabel()
        self._page_title.setObjectName("pageTitle")
        right_layout.addWidget(self._page_title)

        self._stack = QStackedWidget()
        right_layout.addWidget(self._stack, 1)

        self._footer = QFrame()
        self._footer.setObjectName("footer")
        footer_layout = QHBoxLayout(self._footer)
        footer_layout.setContentsMargins(16, 6, 16, 6)
        self._footer_left = QLabel("Create by Agentos")
        self._footer_left.setObjectName("footerLabel")
        self._footer_right = QLabel("Copyright @ 2026 version 1.1")
        self._footer_right.setObjectName("footerLabel")
        footer_layout.addWidget(self._footer_left)
        footer_layout.addStretch()
        footer_layout.addWidget(self._footer_right)
        right_layout.addWidget(self._footer)

        root_layout.addWidget(right_area, 1)

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        self._build_menu_bar()

    def _build_nav_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("navPanel")
        panel.setFixedWidth(220)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(2)

        logo_label = QLabel("Kouprey-Zip")
        logo_label.setObjectName("appLogo")
        logo_font = QFont()
        logo_font.setFamilies(["AgentosUI", "Segoe UI Variable Display", "Segoe UI", "sans-serif"])
        logo_font.setPointSize(16)
        logo_font.setWeight(QFont.Weight.DemiBold)
        logo_label.setFont(logo_font)
        layout.addWidget(logo_label)

        layout.addSpacing(16)

        for nav_key, page_key in self.NAV_ITEMS:
            icon_name = _NAV_ICONS.get(nav_key, "")
            btn = NavButton(icon_name, "")
            btn.clicked.connect(lambda _, pk=page_key: self._navigate_to(pk))
            self._nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        bottom_frame = QFrame()
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        self._theme_btn = QPushButton()
        self._theme_btn.setObjectName("navigationButton")
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.setMinimumHeight(44)
        self._theme_btn.clicked.connect(self._toggle_theme)
        bottom_layout.addWidget(self._theme_btn)

        self._lang_btn = QPushButton()
        self._lang_btn.setObjectName("navigationButton")
        self._lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._lang_btn.setMinimumHeight(44)
        self._lang_btn.setIcon(lucide_icon("languages", 18))
        self._lang_btn.clicked.connect(self._cycle_language)
        bottom_layout.addWidget(self._lang_btn)

        layout.addWidget(bottom_frame)
        return panel

    def _build_pages(self):
        from core.archive import Archive
        from core.compressor import Compressor
        from core.extractor import Extractor

        archive_page = ArchivePage(self._lang, self._theme)
        compress_page = CompressPage(self._lang, self._theme)
        encrypt_page = EncryptPage(self._lang, self._theme)
        settings_page = SettingsPage(self._lang, self._theme)

        self._pages = {
            "archive_page": archive_page,
            "compress_page": compress_page,
            "encrypt_page": encrypt_page,
            "settings_page": settings_page,
        }
        for page in self._pages.values():
            self._stack.addWidget(page)

    def _build_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("")
        self._file_menu = file_menu
        self._open_action = QAction("")
        self._open_action.triggered.connect(self._open_archive)
        file_menu.addAction(self._open_action)
        file_menu.addSeparator()
        self._exit_action = QAction("")
        self._exit_action.triggered.connect(self.close)
        file_menu.addAction(self._exit_action)

        help_menu = menubar.addMenu("")
        self._help_menu = help_menu
        self._about_action = QAction("")
        self._about_action.triggered.connect(self._show_about)
        help_menu.addAction(self._about_action)

    def _navigate_to(self, page_key: str):
        if not self._pages:
            self._build_pages()

        for btn, (_, pk) in zip(self._nav_buttons, self.NAV_ITEMS):
            btn.set_active(pk == page_key)

        if page_key in self._pages:
            self._stack.setCurrentWidget(self._pages[page_key])
            page_titles = {
                "archive_page": "page_archive_title",
                "compress_page": "page_compress_title",
                "encrypt_page": "page_encrypt_title",
                "settings_page": "page_settings_title",
            }
            title_key = page_titles.get(page_key, "")
            self._page_title.setText(self._lang.tr(title_key, ""))
            self._command_bar.clear()
            if hasattr(self._pages[page_key], "populate_toolbar"):
                self._pages[page_key].populate_toolbar(self._command_bar)

    def receive_paths(self, compress_paths: list[str] | None = None,
                      open_path: str | None = None,
                      extract_path: str | None = None):
        self._navigate_to("archive_page")
        if compress_paths:
            self._navigate_to("compress_page")
            cp = self._pages.get("compress_page")
            if cp and hasattr(cp, "set_files"):
                cp.set_files(compress_paths)
        elif open_path:
            ap = self._pages.get("archive_page")
            if ap and hasattr(ap, "open_archive"):
                ap.open_archive(open_path)
        elif extract_path:
            ap = self._pages.get("archive_page")
            if ap and hasattr(ap, "open_archive"):
                ap.open_archive(extract_path)
        self.raise_()
        self.activateWindow()

    def _open_archive(self):
        ap = self._pages.get("archive_page")
        if ap and hasattr(ap, "open_archive"):
            ap.open_archive()

    def _toggle_theme(self):
        from core.theme import LIGHT, DARK
        is_light = self._theme.colors == LIGHT
        new_mode = "dark" if is_light else "light"
        self._theme.set_mode(new_mode)
        self._refresh_all_icons()
        from app_config import load_config, save_config
        config = load_config()
        config["theme"] = new_mode
        save_config(config)

    def _refresh_all_icons(self):
        for btn in self._nav_buttons:
            btn._update_display()
        self._lang_btn.setIcon(lucide_icon("languages", 18))
        self._update_theme_btn_text()
        self._command_bar.clear()
        page = self._stack.currentWidget()
        if page and hasattr(page, "populate_toolbar"):
            page.populate_toolbar(self._command_bar)

    def _update_theme_btn_text(self):
        from core.theme import LIGHT
        is_light = self._theme.colors == LIGHT
        icon_name = "moon" if is_light else "sun"
        label = self._lang.tr("nav_dark_mode", "Dark mode") if is_light else self._lang.tr("nav_light_mode", "Light mode")
        self._theme_btn.setText(f"  {label}")
        self._theme_btn.setIcon(lucide_icon(icon_name, 18))

    def _cycle_language(self):
        langs = self._lang.available_languages
        if not langs:
            return
        idx = (langs.index(self._lang.current) + 1) % len(langs) if self._lang.current in langs else 0
        new_lang = langs[idx]
        self._lang.set_language(new_lang)
        self._apply_font()
        self._retranslate()
        from app_config import load_config, save_config
        config = load_config()
        config["language"] = new_lang
        save_config(config)

    def _apply_font(self):
        font = QFont()
        font.setFamilies(self._lang.font_families())
        font.setPointSize(11)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
        self.setFont(font)

    def _retranslate(self):
        self.setWindowTitle(self._lang.tr("app_name", "Kouprey-Zip"))

        for (nav_key, _), btn in zip(self.NAV_ITEMS, self._nav_buttons):
            nav_labels = {
                "nav_archive": "nav_archive",
                "nav_compress": "nav_compress",
                "nav_encrypt": "nav_encrypt",
                "nav_settings": "nav_settings",
            }
            label = self._lang.tr(nav_labels.get(nav_key, ""), nav_key)
            btn.set_text(label)

        self._update_theme_btn_text()
        lang_label = self._lang.tr(f"lang_{self._lang.current}", self._lang.current.upper())
        self._lang_btn.setText(f"  {lang_label}")

        self._file_menu.setTitle(self._lang.tr("menu_file", "File"))
        self._open_action.setText(self._lang.tr("action_open", "Open Archive..."))
        self._exit_action.setText(self._lang.tr("action_exit", "Exit"))

        self._help_menu.setTitle(self._lang.tr("menu_help", "Help"))
        self._about_action.setText(self._lang.tr("action_about", "About"))

        for page in self._pages.values():
            if hasattr(page, "retranslate"):
                page.retranslate()

        current = self._stack.currentWidget()
        page_titles = {
            "archive_page": "page_archive_title",
            "compress_page": "page_compress_title",
            "encrypt_page": "page_encrypt_title",
            "settings_page": "page_settings_title",
        }
        for key, widget in self._pages.items():
            if widget is current:
                title_key = page_titles.get(key, "")
                self._page_title.setText(self._lang.tr(title_key, ""))
                break
        self._command_bar.clear()
        if current and hasattr(current, "populate_toolbar"):
            current.populate_toolbar(self._command_bar)

        self._status_bar.showMessage(self._lang.tr("ready", "Ready"))

    def _show_about(self):
        dialog = AboutDialog(self._lang, self._theme, self)
        dialog.exec()

    def status_message(self, message: str, timeout: int = 5000):
        self._status_bar.showMessage(message, timeout)
