import os

from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QProgressBar, QPushButton, QToolBar,
    QVBoxLayout, QWidget,
)

from app_config import load_config, save_config
from core.archive import Archive
from core.extractor import ExtractResult, Extractor
from core.language import LanguageManager
from core.theme import ThemeManager
from tools.file_utils import human_readable_size


class ExtractPageWorker(QThread):
    progress = pyqtSignal(int, int)
    result = pyqtSignal(ExtractResult)

    def __init__(self, extractor: Extractor):
        super().__init__()
        self._extractor = extractor

    def run(self):
        res = self._extractor.extract_all(
            progress_callback=lambda c, t: self.progress.emit(c, t),
        )
        self.result.emit(res)


class ExtractPage(QWidget):
    def __init__(self, lang: LanguageManager, theme: ThemeManager):
        super().__init__()
        self._lang = lang
        self._theme = theme
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)

        source_row = QHBoxLayout()
        self._src_label = QLabel()
        self._src_label.setObjectName("captionLabel")
        source_row.addWidget(self._src_label)
        self._source_path = QLineEdit()
        self._source_path.setReadOnly(True)
        source_row.addWidget(self._source_path, 1)
        self._browse_src_btn = QPushButton()
        self._browse_src_btn.clicked.connect(self._browse_source)
        source_row.addWidget(self._browse_src_btn)
        card_layout.addLayout(source_row)

        dest_row = QHBoxLayout()
        self._dest_label = QLabel()
        self._dest_label.setObjectName("captionLabel")
        dest_row.addWidget(self._dest_label)
        self._dest_path = QLineEdit()
        dest_row.addWidget(self._dest_path, 1)
        self._browse_dest_btn = QPushButton()
        self._browse_dest_btn.clicked.connect(self._browse_dest)
        dest_row.addWidget(self._browse_dest_btn)
        card_layout.addLayout(dest_row)

        layout.addWidget(card)

        self._archive_info = QLabel()
        self._archive_info.setObjectName("subtitleLabel")
        self._archive_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._archive_info)

        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        btn_row = QHBoxLayout()
        self._save_preset_btn = QPushButton()
        self._save_preset_btn.clicked.connect(self._save_preset)
        btn_row.addWidget(self._save_preset_btn)
        btn_row.addStretch()
        self._extract_btn = QPushButton()
        self._extract_btn.setObjectName("accentButton")
        self._extract_btn.clicked.connect(self._do_extract)
        btn_row.addWidget(self._extract_btn)
        layout.addLayout(btn_row)
        self._load_preset()

    def populate_toolbar(self, toolbar: QToolBar):
        pass

    def _browse_source(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._lang.tr("open_archive_title", "Open Archive"),
            "",
            "Archives (*.kpz *.7z *.zip *.rar *.tar *.tar.gz *.tar.bz2 *.tar.xz *.tar.zst *.iso);;All Files (*.*)",
        )
        if path:
            self._source_path.setText(path)
            self._update_archive_info()

    def _update_archive_info(self):
        path = self._source_path.text().strip()
        if os.path.isfile(path):
            try:
                archive = Archive(path)
                count = archive.entry_count
                total = human_readable_size(archive.total_size)
                fmt = archive.format.display_name if archive.format else "?"
                self._archive_info.setText(
                    f"{fmt}  ·  {count} {self._lang.tr('entries', 'entries')}  ·  {total}"
                )
            except Exception:
                self._archive_info.setText("")

    def _browse_dest(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            self._lang.tr("select_output_dir", "Select Output Directory"),
        )
        if folder:
            self._dest_path.setText(folder)

    def _do_extract(self):
        src = self._source_path.text().strip()
        dest = self._dest_path.text().strip()
        if not src or not os.path.isfile(src):
            QMessageBox.warning(
                self, self._lang.tr("warning", "Warning"),
                self._lang.tr("select_source", "Please select a source archive."),
            )
            return
        if not dest:
            QMessageBox.warning(
                self, self._lang.tr("warning", "Warning"),
                self._lang.tr("select_dest", "Please select a destination folder."),
            )
            return

        extractor = Extractor(src, dest)
        self._worker = ExtractPageWorker(extractor)
        self._worker.progress.connect(self._on_progress)
        self._worker.result.connect(self._on_result)
        self._worker.start()
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._extract_btn.setEnabled(False)
        self._extract_btn.setText(
            f"{self._lang.tr('extracting', 'Extracting')}..."
        )

    def _on_progress(self, current: int, total: int):
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(current)
        window = self.window()
        if hasattr(window, "status_message"):
            window.status_message(
                f"{self._lang.tr('extracting', 'Extracting')}: {current}/{total}",
                0,
            )

    def _on_result(self, res: ExtractResult):
        self._progress_bar.setVisible(False)
        self._extract_btn.setEnabled(True)
        self._extract_btn.setText(self._lang.tr("extract", "Extract"))
        if res.success:
            QMessageBox.information(
                self, self._lang.tr("success", "Success"),
                f"{self._lang.tr('extract_complete', 'Extraction complete.')}\n"
                f"{res.extracted_count} {self._lang.tr('entries', 'entries')}",
            )
        else:
            QMessageBox.critical(
                self, self._lang.tr("error", "Error"), res.message,
            )

    def _save_preset(self):
        src = self._source_path.text().strip()
        dest = self._dest_path.text().strip()
        if not src:
            QMessageBox.warning(
                self, self._lang.tr("warning", "Warning"),
                self._lang.tr("select_source", "Please select a source archive."),
            )
            return
        config = load_config()
        config["extraction_preset"] = {"source": src, "dest": dest}
        save_config(config)
        QMessageBox.information(
            self, self._lang.tr("success", "Success"),
            self._lang.tr("preset_saved", "Extraction preset saved."),
        )

    def _load_preset(self):
        config = load_config()
        preset = config.get("extraction_preset")
        if preset:
            src = preset.get("source", "")
            dest = preset.get("dest", "")
            if src and os.path.isfile(src):
                self._source_path.setText(src)
                self._update_archive_info()
            if dest:
                self._dest_path.setText(dest)

    def retranslate(self):
        self._save_preset_btn.setText(self._lang.tr("save_preset", "Save Preset"))
        self._src_label.setText(self._lang.tr("source_archive", "Source Archive"))
        self._dest_label.setText(self._lang.tr("destination", "Destination"))
        self._browse_src_btn.setText(self._lang.tr("browse", "Browse..."))
        self._browse_dest_btn.setText(self._lang.tr("browse", "Browse..."))
        self._extract_btn.setText(self._lang.tr("extract", "Extract"))
        self._archive_info.setText("")
