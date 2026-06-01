import os
import time

from PyQt6.QtCore import QThread, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMenu, QMessageBox, QProgressBar, QPushButton,
    QTableWidget, QTableWidgetItem, QToolBar, QVBoxLayout, QWidget,
)

from core.compressor import CompressResult, Compressor
from core.formats import ArchiveFormat, SUPPORTED_COMPRESS_FORMATS
from core.icons import lucide_icon
from core.language import LanguageManager
from core.theme import ThemeManager
from tools.file_utils import human_readable_size


class CompressWorker(QThread):
    progress = pyqtSignal(int, int)
    result = pyqtSignal(CompressResult)

    def __init__(self, compressor: Compressor):
        super().__init__()
        self._compressor = compressor

    def run(self):
        res = self._compressor.compress(
            progress_callback=lambda c, t: self.progress.emit(c, t),
        )
        self.result.emit(res)


class CompressPage(QWidget):
    def __init__(self, lang: LanguageManager, theme: ThemeManager):
        super().__init__()
        self._lang = lang
        self._theme = theme
        self._files: list[str] = []
        self.setAcceptDrops(True)
        self._setup_ui()

    @staticmethod
    def _icon_for_file(path: str):
        ext = os.path.splitext(path)[1].lower()
        if os.path.isdir(path):
            return lucide_icon("folder-open")
        if ext == ".pdf":
            return lucide_icon("file-text")
        if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"):
            return lucide_icon("file-image")
        if ext in (".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".zst", ".kpz", ".iso"):
            return lucide_icon("file-archive")
        if ext in (".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"):
            return lucide_icon("file-audio")
        if ext in (".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm"):
            return lucide_icon("file-video")
        if ext in (".py", ".js", ".ts", ".html", ".css", ".cpp", ".c", ".h", ".rs", ".go", ".java", ".kt"):
            return lucide_icon("file-code")
        if ext in (".xls", ".xlsx", ".csv"):
            return lucide_icon("file-spreadsheet")
        if ext in (".doc", ".docx", ".txt", ".md", ".rtf"):
            return lucide_icon("file-text")
        return lucide_icon("file")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)

        output_label = QLabel()
        output_label.setObjectName("captionLabel")
        card_layout.addWidget(output_label)
        self._output_label = output_label

        output_row = QHBoxLayout()
        self._output_path = QLineEdit()
        self._output_path.textChanged.connect(self._update_password_visibility)
        output_row.addWidget(self._output_path)
        self._browse_btn = QPushButton()
        self._browse_btn.clicked.connect(self._browse_output)
        output_row.addWidget(self._browse_btn)
        card_layout.addLayout(output_row)

        self._table = QTableWidget(0, 4)
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        self._table.cellDoubleClicked.connect(self._open_entry)
        self._table.setHorizontalHeaderLabels([
            self._lang.tr("col_name", "Name"),
            self._lang.tr("col_size", "Size"),
            "",
            self._lang.tr("col_type", "Type"),
        ])
        self._table.setMinimumHeight(200)
        card_layout.addWidget(self._table)

        btn_row = QHBoxLayout()
        self._add_files_btn = QPushButton()
        self._add_files_btn.clicked.connect(self._add_files)
        btn_row.addWidget(self._add_files_btn)
        self._add_folder_btn = QPushButton()
        self._add_folder_btn.clicked.connect(self._add_folder)
        btn_row.addWidget(self._add_folder_btn)
        self._clear_btn = QPushButton()
        self._clear_btn.clicked.connect(self._clear_files)
        btn_row.addWidget(self._clear_btn)
        btn_row.addStretch()
        card_layout.addLayout(btn_row)

        layout.addWidget(card)

        self._pwd_container = QWidget()
        pwd_row = QHBoxLayout(self._pwd_container)
        pwd_row.setContentsMargins(0, 0, 0, 0)
        self._pwd_label = QLabel()
        self._pwd_label.setObjectName("captionLabel")
        pwd_row.addWidget(self._pwd_label)
        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_row.addWidget(self._password, 1)
        layout.addWidget(self._pwd_container)

        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        self._compress_btn = QPushButton()
        self._compress_btn.setObjectName("accentButton")
        self._compress_btn.clicked.connect(self._do_compress)
        layout.addWidget(self._compress_btn, 0, Qt.AlignmentFlag.AlignRight)

    def populate_toolbar(self, toolbar: QToolBar):
        pass

    def _browse_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            self._lang.tr("save_archive_title", "Save Archive"),
            "",
            "KPZ (*.kpz);;ZIP (*.zip);;7z (*.7z);;RAR (*.rar);;TAR (*.tar);;TarGZip (*.tar.gz);;BZip2 (*.tar.bz2);;XZ (*.tar.xz);;Zstd (*.tar.zst);;All Files (*.*)",
        )
        if path:
            self._output_path.setText(path)

    def _update_password_visibility(self):
        path = self._output_path.text().strip()
        fmt = ArchiveFormat.from_extension(path)
        supported = fmt is not None and fmt.supports_password
        self._pwd_container.setVisible(supported)
        if not supported:
            self._password.clear()

    def _refresh_table(self):
        headers = [
            self._lang.tr("col_name", "Name"),
            self._lang.tr("col_size", "Size"),
            "",
            self._lang.tr("col_type", "Type"),
        ]
        self._table.setHorizontalHeaderLabels(headers)
        self._table.setRowCount(0)
        for path in self._files:
            row = self._table.rowCount()
            self._table.insertRow(row)
            name = os.path.basename(path)
            is_dir = os.path.isdir(path)
            name_item = QTableWidgetItem(self._icon_for_file(path), name)
            name_item.setData(Qt.ItemDataRole.UserRole, path)
            name_item.setToolTip(path)
            self._table.setItem(row, 0, name_item)
            if is_dir:
                self._table.setItem(row, 1, QTableWidgetItem(""))
                self._table.setItem(row, 2, QTableWidgetItem(""))
            else:
                try:
                    st = os.stat(path)
                    self._table.setItem(
                        row, 1,
                        QTableWidgetItem(human_readable_size(st.st_size)),
                    )
                    modified = time.strftime(
                        "%Y-%m-%d %H:%M", time.localtime(st.st_mtime)
                    )
                    self._table.setItem(row, 2, QTableWidgetItem(modified))
                except OSError:
                    self._table.setItem(row, 1, QTableWidgetItem(""))
                    self._table.setItem(row, 2, QTableWidgetItem(""))
            ext = os.path.splitext(path)[1].upper().lstrip(".") or "File"
            self._table.setItem(
                row, 3,
                QTableWidgetItem(self._lang.tr("folder", "Folder") if is_dir else ext),
            )

    def _add_item_path(self, path: str):
        self._files.append(path)
        self._refresh_table()

    def set_files(self, paths: list[str]):
        for f in paths:
            if f not in self._files:
                self._add_item_path(f)

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, self._lang.tr("select_files", "Select Files"),
        )
        for f in files:
            if f not in self._files:
                self._add_item_path(f)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, self._lang.tr("select_folder", "Select Folder"),
        )
        if folder and folder not in self._files:
            self._add_item_path(folder)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path and os.path.exists(path) and path not in self._files:
                self._add_item_path(path)

    def _clear_files(self):
        self._files.clear()
        self._table.setRowCount(0)

    def _open_entry(self, row: int, col: int):
        item = self._table.item(row, 0)
        if not item:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _show_context_menu(self, pos):
        item = self._table.itemAt(pos)
        if not item:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        row = self._table.row(item)
        menu = QMenu(self)
        open_act = menu.addAction(self._lang.tr("context_open_file", "Open"))
        open_act.triggered.connect(lambda: self._open_entry(row, 0))
        menu.addSeparator()
        delete_act = menu.addAction(self._lang.tr("context_delete", "Delete"))
        delete_act.triggered.connect(lambda: self._delete_entry(row))
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _delete_entry(self, row: int):
        item = self._table.item(row, 0)
        if not item:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        self._table.removeRow(row)
        if path in self._files:
            self._files.remove(path)

    def _do_compress(self):
        output = self._output_path.text().strip()
        if not output:
            QMessageBox.warning(
                self, self._lang.tr("warning", "Warning"),
                self._lang.tr("specify_output", "Please specify an output file."),
            )
            return
        if not self._files:
            QMessageBox.warning(
                self, self._lang.tr("warning", "Warning"),
                self._lang.tr("add_files_warn", "Please add at least one file."),
            )
            return

        password = self._password.text()
        compressor = Compressor(output, list(self._files), password)
        self._worker = CompressWorker(compressor)
        self._worker.progress.connect(self._on_progress)
        self._worker.result.connect(self._on_result)
        self._worker.start()
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._compress_btn.setEnabled(False)

    def _on_progress(self, current: int, total: int):
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(current)

    def _on_result(self, res: CompressResult):
        self._progress_bar.setVisible(False)
        self._compress_btn.setEnabled(True)
        if res.success:
            QMessageBox.information(
                self, self._lang.tr("success", "Success"),
                self._lang.tr("compress_complete", "Compression complete."),
            )
        else:
            QMessageBox.critical(
                self, self._lang.tr("error", "Error"), res.message,
            )

    def retranslate(self):
        self._output_label.setText(
            self._lang.tr("output_path_hint", "Select output path..."),
        )
        self._pwd_label.setText(self._lang.tr("password", "Password:"))
        self._browse_btn.setText(self._lang.tr("browse", "Browse..."))
        self._add_files_btn.setText(self._lang.tr("add_files", "Add Files"))
        self._add_folder_btn.setText(self._lang.tr("add_folder", "Add Folder"))
        self._clear_btn.setText(self._lang.tr("clear", "Clear"))
        self._compress_btn.setText(
            self._lang.tr("compress", "Compress"),
        )
        self._refresh_table()
