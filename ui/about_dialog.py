import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from core.language import LanguageManager
from core.theme import LIGHT, ThemeManager


_ABOUT_DETAILS = (
    ("Developer", "Agentos"),
    ("Contact", "https://github.com/kouprey-zip"),

)


class AboutDialog(QDialog):
    def __init__(self, lang: LanguageManager, theme: ThemeManager, parent=None):
        super().__init__(parent)
        self._lang = lang
        self._theme = theme
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self._lang.tr("about_title", "About Kouprey-Zip"))
        self.setFixedSize(480, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 20)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        _base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icons_dir = os.path.join(_base, "assets", "icons")
        logo_file = "KoupreyTransparancy.png" if self._theme.colors == LIGHT else "Kouprey_Transparancy-White.png"
        logo_path = os.path.join(icons_dir, logo_file)
        icon_label = QLabel()
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        name_label = QLabel("Kouprey-Zip")
        name_font = QFont()
        name_font.setFamilies(["AgentosUI", "Segoe UI Variable Display", "Segoe UI", "sans-serif"])
        name_font.setPointSize(18)
        name_font.setWeight(QFont.Weight.DemiBold)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        desc_label = QLabel(
            self._lang.tr("app_desc", "A modern file archiver for Windows with WinUI 3-inspired design.")
        )
        desc_label.setObjectName("subtitleLabel")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        version_label = QLabel(self._lang.tr("version", "Version 1.1"))
        version_label.setObjectName("captionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        layout.addSpacing(8)

        for label, value in _ABOUT_DETAILS:
            row = QHBoxLayout()
            row.setSpacing(8)
            k = QLabel(f"{label}:")
            k.setObjectName("captionLabel")
            v = QLabel(value)
            v.setObjectName("captionLabel")
            v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            row.addStretch()
            row.addWidget(k)
            row.addWidget(v)
            layout.addLayout(row)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton(self._lang.tr("close", "Close"))
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
