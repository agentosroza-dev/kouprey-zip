from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFormLayout, QFrame, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from core.icons import lucide_icon
from core.language import LanguageManager
from core.theme import ThemeManager


class SettingsPage(QWidget):
    def __init__(self, lang: LanguageManager, theme: ThemeManager):
        super().__init__()
        self._lang = lang
        self._theme = theme
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(16)

        nav_panel = QFrame()
        nav_panel.setObjectName("card")
        nav_panel.setFixedWidth(200)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(2)

        self._page_buttons: list[QPushButton] = []
        pages_info = [
            ("page_general", "sliders-horizontal", "settings_general"),
            ("page_appearance", "palette", "settings_appearance"),
            ("page_integration", "wand", "settings_integration"),
        ]
        self._page_keys = [p[0] for p in pages_info]

        for page_key, icon_name, label_key in pages_info:
            btn = QPushButton()
            btn.setObjectName("navigationButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setIcon(lucide_icon(icon_name, 18))
            btn.clicked.connect(lambda _, pk=page_key: self._switch_page(pk))
            self._page_buttons.append(btn)
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        main_layout.addWidget(nav_panel)

        self._stack = QStackedWidget()
        self._general_page = self._build_general_page()
        self._appearance_page = self._build_appearance_page()
        self._integration_page = self._build_integration_page()
        self._stack.addWidget(self._general_page)
        self._stack.addWidget(self._appearance_page)
        self._stack.addWidget(self._integration_page)
        main_layout.addWidget(self._stack, 1)

        layout.addLayout(main_layout)

        if self._page_buttons:
            self._page_buttons[0].setChecked(True)

    def _build_general_page(self) -> QWidget:
        page = QFrame()
        page.setObjectName("card")
        page_layout = QVBoxLayout(page)
        page_layout.setSpacing(16)

        general_label = QLabel()
        general_label.setObjectName("titleLabel")
        page_layout.addWidget(general_label)

        info_label = QLabel()
        info_label.setObjectName("subtitleLabel")
        info_label.setWordWrap(True)
        page_layout.addWidget(info_label)

        page_layout.addStretch()
        return page

    def _build_appearance_page(self) -> QWidget:
        from core.theme import LIGHT, DARK
        page = QFrame()
        page.setObjectName("card")
        page_layout = QVBoxLayout(page)
        page_layout.setSpacing(16)

        appearance_label = QLabel()
        appearance_label.setObjectName("titleLabel")
        page_layout.addWidget(appearance_label)

        form = QFormLayout()
        form.setSpacing(12)

        self._theme_label = QLabel()
        self._theme_btn = QPushButton()
        self._theme_btn.setObjectName("dropdownButton")
        self._theme_btn.setMinimumWidth(180)
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.clicked.connect(self._show_theme_menu)
        self._theme_val = "dark" if self._theme.colors == DARK else "light"
        form.addRow(self._theme_label, self._theme_btn)

        self._lang_label = QLabel()
        self._lang_btn = QPushButton()
        self._lang_btn.setObjectName("dropdownButton")
        self._lang_btn.setMinimumWidth(180)
        self._lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._lang_btn.clicked.connect(self._show_lang_menu)
        self._lang_val = self._lang.current
        form.addRow(self._lang_label, self._lang_btn)

        page_layout.addLayout(form)
        page_layout.addStretch()

        save_btn = QPushButton()
        save_btn.setObjectName("accentButton")
        save_btn.clicked.connect(self._save_settings)
        page_layout.addWidget(save_btn, 0, Qt.AlignmentFlag.AlignRight)
        self._save_btn = save_btn

        return page

    def _show_theme_menu(self):
        from core.icons import lucide_icon
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        sun = menu.addAction(lucide_icon("sun", 16), self._lang.tr("light", "Light"))
        sun.setData("light")
        moon = menu.addAction(lucide_icon("moon", 16), self._lang.tr("dark", "Dark"))
        moon.setData("dark")
        if self._theme_val == "dark":
            moon.setChecked(True)
        else:
            sun.setChecked(True)
        for a in (sun, moon):
            a.setCheckable(True)
        chosen = menu.exec(self._theme_btn.mapToGlobal(
            self._theme_btn.rect().bottomLeft()))
        if chosen:
            self._theme_val = chosen.data()
            self._update_theme_btn()

    def _update_theme_btn(self):
        from core.icons import lucide_icon
        icon_name = "sun" if self._theme_val == "light" else "moon"
        label = self._lang.tr("light", "Light") if self._theme_val == "light" else self._lang.tr("dark", "Dark")
        self._theme_btn.setText(f"  {label}")
        self._theme_btn.setIcon(lucide_icon(icon_name, 16))

    def _show_lang_menu(self):
        from core.icons import lucide_icon
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        for lc in self._lang.available_languages:
            label = self._lang.tr(f"lang_{lc}", lc.upper())
            a = menu.addAction(lucide_icon("languages", 16), label)
            a.setData(lc)
            a.setCheckable(True)
            if lc == self._lang_val:
                a.setChecked(True)
        chosen = menu.exec(self._lang_btn.mapToGlobal(
            self._lang_btn.rect().bottomLeft()))
        if chosen:
            self._lang_val = chosen.data()
            self._update_lang_btn()

    def _update_lang_btn(self):
        from core.icons import lucide_icon
        label = self._lang.tr(f"lang_{self._lang_val}", self._lang_val.upper())
        self._lang_btn.setText(f"  {label}")
        self._lang_btn.setIcon(lucide_icon("languages", 16))

    def _build_integration_page(self) -> QWidget:
        from core.registry import is_registered
        page = QFrame()
        page.setObjectName("card")
        page_layout = QVBoxLayout(page)
        page_layout.setSpacing(16)

        integration_label = QLabel()
        integration_label.setObjectName("titleLabel")
        page_layout.addWidget(integration_label)

        info_label = QLabel()
        info_label.setObjectName("subtitleLabel")
        info_label.setWordWrap(True)
        page_layout.addWidget(info_label)

        self._reg_status = QLabel()
        self._reg_status.setObjectName("captionLabel")
        page_layout.addWidget(self._reg_status)

        btn_row = QHBoxLayout()
        self._reg_btn = QPushButton()
        self._reg_btn.clicked.connect(self._toggle_registration)
        btn_row.addWidget(self._reg_btn)
        btn_row.addStretch()
        page_layout.addLayout(btn_row)
        page_layout.addStretch()

        self._update_reg_status()
        return page

    def _update_reg_status(self):
        from core.registry import is_registered
        registered = is_registered()
        self._reg_status.setText(
            self._lang.tr("context_registered", "Context menu is registered.")
            if registered else
            self._lang.tr("context_not_registered", "Context menu is not registered.")
        )
        self._reg_btn.setText(
            self._lang.tr("context_unregister", "Unregister")
            if registered else
            self._lang.tr("context_register", "Register")
        )

    def _toggle_registration(self):
        from core.registry import is_registered, register_context_menu, unregister_context_menu
        if is_registered():
            unregister_context_menu()
        else:
            register_context_menu(
                compress_label="Add Archive with Kouprey",
                extract_label="Extract with Kouprey",
                open_label="Open with Kouprey-Zip",
                quick_kpz_label="Create *.kpz",
                quick_extract_here_label="Extract Here",
                quick_extract_to_label="Extract to Folder",
            )
        self._update_reg_status()

    def _switch_page(self, page_key: str):
        for btn, pk in zip(self._page_buttons, self._page_keys):
            btn.setChecked(pk == page_key)

        idx_map = {k: i for i, k in enumerate(self._page_keys)}
        idx = idx_map.get(page_key, 0)
        self._stack.setCurrentIndex(idx)

    def _save_settings(self):
        from core.theme import LIGHT, DARK
        from app_config import save_config, load_config

        config = load_config()

        if self._theme_val:
            is_light = self._theme.colors == LIGHT
            current_theme = "light" if is_light else "dark"
            if self._theme_val != current_theme:
                self._theme.set_mode(self._theme_val)
            config["theme"] = self._theme_val

        if self._lang_val and self._lang_val != self._lang.current:
            self._lang.set_language(self._lang_val)
            window = self.window()
            if hasattr(window, "_apply_font"):
                window._apply_font()
            if hasattr(window, "_retranslate"):
                window._retranslate()
            config["language"] = self._lang_val

        save_config(config)

    def populate_toolbar(self, toolbar):
        pass

    def retranslate(self):
        from core.theme import DARK
        nav_labels = [
            self._lang.tr("settings_general", "General"),
            self._lang.tr("settings_appearance", "Appearance"),
            self._lang.tr("settings_integration", "Integration"),
        ]
        for i, label in enumerate(nav_labels):
            if i < len(self._page_buttons):
                self._page_buttons[i].setText(
                    f"  {label}"
                )

        general_label = self._general_page.findChild(QLabel)
        if general_label:
            general_label.setText(
                self._lang.tr("settings_general", "General")
            )
            info = self._general_page.findChildren(QLabel)
            if len(info) > 1:
                info[1].setText(
                    self._lang.tr("settings_general_desc",
                                  "Configure application behavior and preferences.")
                )

        appearance_label = self._appearance_page.findChild(QLabel)
        if appearance_label:
            appearance_label.setText(
                self._lang.tr("settings_appearance", "Appearance")
            )

        integration_label = self._integration_page.findChildren(QLabel)
        if integration_label:
            integration_label[0].setText(
                self._lang.tr("settings_integration", "Integration")
            )
            if len(integration_label) > 1:
                integration_label[1].setText(
                    self._lang.tr("settings_integration_desc",
                                  "Integrate Kouprey-Zip into the Windows context menu.")
                )
        self._update_reg_status()

        self._theme_label.setText(
            self._lang.tr("theme", "Theme:")
        )
        self._lang_label.setText(
            self._lang.tr("language", "Language:")
        )

        self._theme_val = "dark" if self._theme.colors == DARK else "light"
        self._lang_val = self._lang.current
        self._update_theme_btn()
        self._update_lang_btn()

        self._save_btn.setText(
            self._lang.tr("save", "Save")
        )
