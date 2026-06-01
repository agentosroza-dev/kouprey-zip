import os
import shutil
import tarfile
import tempfile
import zipfile

import py7zr
import rarfile

from PyQt6.QtCore import Qt, QThread, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMenu, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QToolBar, QVBoxLayout, QWidget,
)

from core.archive import Archive, ArchiveEntry, _ensure_unrar, archive_requires_password
from core.compressor import Compressor
from core.extractor import Extractor, ExtractResult
from core.formats import ArchiveFormat
from core.icons import lucide_icon
from core.language import LanguageManager
from core.theme import ThemeManager
from tools.file_utils import human_readable_size


class ExtractWorker(QThread):
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


class SingleEntryExtractWorker(QThread):
    result = pyqtSignal(ExtractResult)

    def __init__(self, archive_path: str, entry_name: str, output_dir: str, password: str = ""):
        super().__init__()
        self._archive_path = archive_path
        self._entry_name = entry_name
        self._output_dir = output_dir
        self._password = password

    def run(self):
        tmp_dir = tempfile.mkdtemp(prefix="kouprey_sext_")
        try:
            fmt = ArchiveFormat.from_extension(self._archive_path)
            if fmt == ArchiveFormat.KPZ:
                pwd = self._password.encode("utf-8") if self._password else None
                try:
                    with zipfile.ZipFile(self._archive_path, "r") as zf:
                        zf.extract(self._entry_name, tmp_dir, pwd=pwd)
                except zipfile.BadZipFile:
                    kwargs = {"password": self._password} if self._password else {}
                    with py7zr.SevenZipFile(self._archive_path, "r", **kwargs) as sz:
                        sz.extract(targets=[self._entry_name], path=tmp_dir)
            elif fmt == ArchiveFormat.ZIP:
                pwd = self._password.encode("utf-8") if self._password else None
                with zipfile.ZipFile(self._archive_path, "r") as zf:
                    zf.extract(self._entry_name, tmp_dir, pwd=pwd)
            elif fmt in (ArchiveFormat.TAR, ArchiveFormat.GZIP,
                         ArchiveFormat.BZIP2, ArchiveFormat.XZ, ArchiveFormat.ZSTD):
                with tarfile.open(self._archive_path, "r:*") as tf:
                    tf.extract(self._entry_name, tmp_dir)
            elif fmt in (ArchiveFormat.SEVEN_ZIP, ArchiveFormat.ISO):
                kwargs = {"password": self._password} if self._password else {}
                with py7zr.SevenZipFile(self._archive_path, "r", **kwargs) as sz:
                    sz.extract(targets=[self._entry_name], path=tmp_dir)
            elif fmt == ArchiveFormat.RAR:
                _ensure_unrar()
                pwd = self._password if self._password else None
                with rarfile.RarFile(self._archive_path) as rf:
                    rf.extract(self._entry_name, tmp_dir, pwd=pwd)
            else:
                import patoolib
                patoolib.extract_archive(self._archive_path, outdir=tmp_dir)
            src = os.path.join(tmp_dir, self._entry_name)
            if os.path.isfile(src):
                dst = os.path.join(self._output_dir, os.path.basename(self._entry_name))
                os.makedirs(self._output_dir, exist_ok=True)
                shutil.copy2(src, dst)
                self.result.emit(ExtractResult(True, 1))
            else:
                self.result.emit(ExtractResult(False, 0, f"File not found: {self._entry_name}"))
        except Exception as e:
            self.result.emit(ExtractResult(False, 0, str(e)))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


class DirectoryExtractWorker(QThread):
    result = pyqtSignal(ExtractResult)

    def __init__(self, archive_path: str, entry_name: str, output_dir: str, password: str = ""):
        super().__init__()
        self._archive_path = archive_path
        self._entry_name = entry_name
        self._output_dir = output_dir
        self._password = password

    def run(self):
        tmp_dir = tempfile.mkdtemp(prefix="kouprey_dext_")
        try:
            extractor = Extractor(self._archive_path, tmp_dir, self._password)
            res = extractor.extract_all()
            if not res.success:
                self.result.emit(res)
                return
            prefix = self._entry_name.rstrip("/")
            src = os.path.join(tmp_dir, prefix)
            if os.path.isdir(src):
                shutil.copytree(
                    src,
                    os.path.join(self._output_dir, os.path.basename(prefix)),
                    dirs_exist_ok=True,
                )
                self.result.emit(ExtractResult(True, res.extracted_count))
            else:
                self.result.emit(ExtractResult(False, 0, f"Folder not found: {prefix}"))
        except Exception as e:
            self.result.emit(ExtractResult(False, 0, str(e)))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


class ArchivePage(QWidget):
    def __init__(self, lang: LanguageManager, theme: ThemeManager):
        super().__init__()
        self._lang = lang
        self._theme = theme
        self._current_archive: Archive | None = None
        self._current_prefix: str = ""
        self.setAcceptDrops(True)
        self._setup_ui()

    @staticmethod
    def _icon_for_entry(entry: ArchiveEntry):
        if entry.is_dir:
            return lucide_icon("folder-open")
        ext = entry.extension.lower()
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
        layout.setSpacing(12)

        empty_state = QFrame()
        empty_state.setObjectName("card")
        empty_layout = QVBoxLayout(empty_state)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_icon = QLabel()
        self._empty_icon.setPixmap(lucide_icon("file-archive", 48).pixmap(48, 48))
        self._empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self._empty_icon)
        self._empty_text = QLabel()
        self._empty_text.setObjectName("subtitleLabel")
        self._empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self._empty_text)
        self._open_btn = QPushButton()
        self._open_btn.setObjectName("accentButton")
        self._open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._open_btn.clicked.connect(lambda: self.open_archive())
        empty_layout.addWidget(self._open_btn, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(empty_state)
        self._empty_state = empty_state

        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        info_bar = QFrame()
        info_bar.setObjectName("infoBar")
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(16, 12, 16, 12)
        self._info_icon = QLabel()
        self._info_icon.setPixmap(lucide_icon("package", 18).pixmap(18, 18))
        info_layout.addWidget(self._info_icon)
        self._info_label = QLabel()
        info_layout.addWidget(self._info_label)
        content_layout.addWidget(info_bar)
        self._info_bar = info_bar

        self._path_bar = QFrame()
        self._path_bar.setObjectName("infoBar")
        path_layout = QHBoxLayout(self._path_bar)
        path_layout.setContentsMargins(16, 8, 16, 8)
        self._path_label = QLabel()
        self._path_label.setObjectName("captionLabel")
        path_layout.addWidget(self._path_label)
        content_layout.addWidget(self._path_bar)

        table_frame = QFrame()
        table_frame.setObjectName("card")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)

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
        table_layout.addWidget(self._table)
        content_layout.addWidget(table_frame)

        btn_layout = QHBoxLayout()
        self._add_files_btn = QPushButton()
        self._add_files_btn.clicked.connect(self._add_files_to_archive)
        btn_layout.addWidget(self._add_files_btn)
        self._add_folder_btn = QPushButton()
        self._add_folder_btn.clicked.connect(self._add_folder_to_archive)
        btn_layout.addWidget(self._add_folder_btn)
        btn_layout.addStretch()
        self._extract_btn = QPushButton()
        self._extract_btn.setObjectName("accentButton")
        self._extract_btn.clicked.connect(self._extract_archive)
        btn_layout.addWidget(self._extract_btn)
        content_layout.addLayout(btn_layout)

        layout.addWidget(content_area)
        self._content_area = content_area

        self._update_visibility()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path and os.path.isfile(path):
                self._load_archive(path)
                if self._current_archive:
                    break

    def _load_archive(self, path: str):
        try:
            archive = Archive(path)
            if archive.format is None:
                raise ValueError(
                    self._lang.tr("unsupported_format", "Unsupported archive format.")
                )
            self._current_archive = archive
            self._current_prefix = ""
            try:
                archive.list_entries()
                self._refresh_table()
            except Exception:
                self._table.setRowCount(0)
            self._update_visibility()
            self._update_info()
        except Exception as e:
            self._current_archive = None
            self._update_visibility()
            QMessageBox.critical(
                self, self._lang.tr("error", "Error"), str(e),
            )

    def _update_visibility(self):
        has_archive = self._current_archive is not None
        self._empty_state.setVisible(not has_archive)
        self._content_area.setVisible(has_archive)
        self._add_files_btn.setVisible(has_archive)
        self._add_folder_btn.setVisible(has_archive)
        self._path_bar.setVisible(has_archive)

    def populate_toolbar(self, toolbar: QToolBar):
        open_action = toolbar.addAction(lucide_icon("folder-open", 18), "")
        open_action.triggered.connect(lambda: self.open_archive())
        if self._current_archive:
            ext_action = toolbar.addAction(lucide_icon("file-output", 18), "")
            ext_action.triggered.connect(self._extract_archive)

    def open_archive(self, path: str | None = None):
        if path is None:
            path, _ = QFileDialog.getOpenFileName(
                self,
                self._lang.tr("open_archive_title", "Open Archive"),
                "",
                "Archives (*.kpz *.7z *.zip *.rar *.tar *.tar.gz *.tar.bz2 *.tar.xz *.tar.zst *.iso);;All Files (*.*)",
            )
            if not path:
                return
        self._load_archive(path)

    def _get_children(self):
        if not self._current_archive:
            return []
        all_entries = self._current_archive.list_entries()
        prefix = self._current_prefix
        if prefix and not prefix.endswith("/"):
            prefix += "/"
        child_map = {}
        for entry in all_entries:
            name = entry.name
            if prefix:
                if not name.startswith(prefix):
                    continue
                rel = name[len(prefix):]
            else:
                rel = name
            if not rel:
                continue
            parts = [p for p in rel.split("/") if p]
            child_name = parts[0]
            if len(parts) == 1:
                child_map[child_name] = entry
            elif child_name not in child_map:
                full_name = prefix + child_name + "/"
                child_map[child_name] = ArchiveEntry(
                    name=full_name, size=0, compressed_size=0, is_dir=True,
                )
        children = list(child_map.values())
        children.sort(key=lambda e: (not e.is_dir, e.name.lower()))
        return children

    def _display_name(self, entry: ArchiveEntry) -> str:
        name = entry.name
        if self._current_prefix and name.startswith(self._current_prefix):
            name = name[len(self._current_prefix):]
        return name.rstrip("/")

    def _update_path_label(self):
        path = self._current_prefix or "/"
        if not path.endswith("/"):
            path += "/"
        self._path_label.setText(
            f"{os.path.basename(self._current_archive.path)}  ▸  {path}"
        )

    def _refresh_table(self):
        if not self._current_archive:
            return
        children = self._get_children()
        headers = [
            self._lang.tr("col_name", "Name"),
            self._lang.tr("col_size", "Size"),
            self._lang.tr("col_compressed", "Compressed"),
            self._lang.tr("col_type", "Type"),
        ]
        self._table.setHorizontalHeaderLabels(headers)
        self._table.setRowCount(0)
        row = 0
        if self._current_prefix:
            self._table.insertRow(row)
            parent_item = QTableWidgetItem(lucide_icon("arrow-left"), "..")
            parent_item.setData(Qt.ItemDataRole.UserRole, "__parent__")
            parent_item.setData(Qt.ItemDataRole.UserRole + 1, False)
            self._table.setItem(row, 0, parent_item)
            self._table.setItem(row, 1, QTableWidgetItem(""))
            self._table.setItem(row, 2, QTableWidgetItem(""))
            self._table.setItem(row, 3, QTableWidgetItem(""))
            row += 1
        for entry in children:
            self._table.insertRow(row)
            display = self._display_name(entry)
            name_item = QTableWidgetItem(self._icon_for_entry(entry), display)
            name_item.setData(Qt.ItemDataRole.UserRole, entry.name)
            name_item.setData(Qt.ItemDataRole.UserRole + 1, entry.is_dir)
            self._table.setItem(row, 0, name_item)
            self._table.setItem(
                row, 1,
                QTableWidgetItem(
                    human_readable_size(entry.size) if not entry.is_dir else "",
                ),
            )
            self._table.setItem(
                row, 2,
                QTableWidgetItem(
                    human_readable_size(entry.compressed_size)
                    if not entry.is_dir else "",
                ),
            )
            self._table.setItem(
                row, 3,
                QTableWidgetItem(
                    self._lang.tr("folder", "Folder") if entry.is_dir
                    else (entry.extension.upper().lstrip(".") or "File"),
                ),
            )
            row += 1
        self._update_path_label()

    def _update_info(self):
        if not self._current_archive:
            return
        if not os.path.isfile(self._current_archive.path):
            self._current_archive = None
            self._update_visibility()
            return
        name = os.path.basename(self._current_archive.path)
        count = self._current_archive.entry_count
        total = human_readable_size(self._current_archive.total_size)
        self._info_label.setText(
            f"{name}  ·  {count} {self._lang.tr('entries', 'entries')}  ·  {total}"
        )

    def _extract_archive(self):
        if not self._current_archive:
            return
        output_dir = QFileDialog.getExistingDirectory(
            self,
            self._lang.tr("select_output_dir", "Select Output Directory"),
        )
        if not output_dir:
            return

        password = ""
        if self._current_archive and archive_requires_password(self._current_archive.path):
            from PyQt6.QtWidgets import QInputDialog
            password, ok = QInputDialog.getText(
                self, self._lang.tr("password", "Password"),
                self._lang.tr("enter_password_opt", "Enter password (leave empty if none):"),
                QLineEdit.EchoMode.Password,
            )
            if not ok:
                return

        extractor = Extractor(self._current_archive.path, output_dir, password)
        self._worker = ExtractWorker(extractor)
        self._worker.progress.connect(self._on_extract_progress)
        self._worker.result.connect(self._on_extract_result)
        self._worker.start()
        self._extract_btn.setEnabled(False)
        self._extract_btn.setText(
            f"{self._lang.tr('extracting', 'Extracting')}..."
        )

    def _on_extract_progress(self, current: int, total: int):
        window = self.window()
        if hasattr(window, "status_message"):
            window.status_message(
                f"{self._lang.tr('extracting', 'Extracting')}: {current}/{total}",
                0,
            )

    def _on_extract_result(self, res: ExtractResult):
        self._extract_btn.setEnabled(True)
        self._extract_btn.setText(
            self._lang.tr("action_extract", "Extract...")
        )
        if res.success:
            QMessageBox.information(
                self,
                self._lang.tr("success", "Success"),
                f"{self._lang.tr('extract_complete', 'Extraction complete.')}\n"
                f"{res.extracted_count} {self._lang.tr('entries', 'entries')}",
            )
        else:
            QMessageBox.critical(
                self,
                self._lang.tr("error", "Error"),
                res.message,
            )

    def _navigate_into(self, folder_name: str):
        prefix = folder_name
        if not prefix.endswith("/"):
            prefix += "/"
        self._current_prefix = prefix
        self._refresh_table()

    def _navigate_up(self):
        if not self._current_prefix:
            return
        parent = os.path.dirname(self._current_prefix.rstrip("/"))
        self._current_prefix = (parent + "/") if parent else ""
        self._refresh_table()

    def _open_entry(self, row: int, col: int):
        item = self._table.item(row, 0)
        if not item or not self._current_archive:
            return
        entry_name = item.data(Qt.ItemDataRole.UserRole)
        is_dir = item.data(Qt.ItemDataRole.UserRole + 1) or False
        if not entry_name:
            return
        if entry_name == "__parent__":
            self._navigate_up()
            return
        if is_dir:
            self._navigate_into(entry_name)
            return
        password = ""
        if archive_requires_password(self._current_archive.path):
            from PyQt6.QtWidgets import QInputDialog
            password, ok = QInputDialog.getText(
                self, self._lang.tr("password", "Password"),
                self._lang.tr("enter_password_opt", "Enter password (leave empty if none):"),
                QLineEdit.EchoMode.Password,
            )
            if not ok:
                return
        tmp_dir = tempfile.mkdtemp(prefix="kouprey_")
        opened = False
        try:
            self._extract_single_entry_sync(entry_name, tmp_dir, password)
            extracted = os.path.normpath(os.path.join(tmp_dir, entry_name))
            if os.path.exists(extracted):
                if QDesktopServices.openUrl(QUrl.fromLocalFile(extracted)):
                    opened = True
                else:
                    raise RuntimeError(f"Failed to open: {extracted}")
            else:
                found = None
                for root, _, files in os.walk(tmp_dir):
                    if files:
                        found = os.path.join(root, files[0])
                        break
                if found:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(found))
                    opened = True
                else:
                    QMessageBox.warning(
                        self, self._lang.tr("warning", "Warning"),
                        self._lang.tr("file_not_found", "Could not locate the extracted file."),
                    )
        except Exception as e:
            QMessageBox.critical(
                self, self._lang.tr("error", "Error"), str(e),
            )
        finally:
            if not opened:
                shutil.rmtree(tmp_dir, ignore_errors=True)

    def _extract_single_entry_sync(self, entry_name: str, output_dir: str, password: str = ""):
        path = self._current_archive.path
        fmt = self._current_archive.format
        if fmt is None:
            return
        if fmt == ArchiveFormat.KPZ:
            pwd = password.encode("utf-8") if password else None
            try:
                with zipfile.ZipFile(path, "r") as zf:
                    zf.extract(entry_name, output_dir, pwd=pwd)
            except zipfile.BadZipFile:
                kwargs = {"password": password} if password else {}
                with py7zr.SevenZipFile(path, "r", **kwargs) as sz:
                    sz.extract(targets=[entry_name], path=output_dir)
        elif fmt == ArchiveFormat.ZIP:
            pwd = password.encode("utf-8") if password else None
            with zipfile.ZipFile(path, "r") as zf:
                zf.extract(entry_name, output_dir, pwd=pwd)
        elif fmt in (ArchiveFormat.TAR, ArchiveFormat.GZIP,
                     ArchiveFormat.BZIP2, ArchiveFormat.XZ, ArchiveFormat.ZSTD):
            with tarfile.open(path, "r:*") as tf:
                tf.extract(entry_name, output_dir)
        elif fmt in (ArchiveFormat.SEVEN_ZIP, ArchiveFormat.ISO):
            kwargs = {"password": password} if password else {}
            with py7zr.SevenZipFile(path, "r", **kwargs) as sz:
                sz.extract(targets=[entry_name], path=output_dir)
        elif fmt == ArchiveFormat.RAR:
            _ensure_unrar()
            pwd = password if password else None
            with rarfile.RarFile(path) as rf:
                rf.extract(entry_name, output_dir, pwd=pwd)
        else:
            import patoolib
            patoolib.extract_archive(path, outdir=output_dir)

    def _show_context_menu(self, pos):
        item = self._table.itemAt(pos)
        if not item:
            return
        entry_name = item.data(Qt.ItemDataRole.UserRole)
        if entry_name == "__parent__":
            return
        menu = QMenu(self)
        open_act = menu.addAction(self._lang.tr("context_open_file", "Open"))
        open_act.triggered.connect(lambda: self._open_entry(self._table.row(item), 0))
        menu.addSeparator()
        copy_act = menu.addAction(self._lang.tr("context_copy", "Copy"))
        copy_act.triggered.connect(lambda: self._copy_entry(entry_name))
        paste_act = menu.addAction(self._lang.tr("context_paste", "Paste"))
        paste_act.triggered.connect(self._paste_entry)
        menu.addSeparator()
        extract_act = menu.addAction(self._lang.tr("context_extract", "Extract Item"))
        extract_act.triggered.connect(lambda: self._extract_single_entry(entry_name))
        delete_act = menu.addAction(self._lang.tr("context_delete", "Delete"))
        delete_act.triggered.connect(lambda: self._delete_entry(entry_name))
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_entry(self, entry_name: str):
        clipboard = QApplication.clipboard()
        from PyQt6.QtCore import QMimeData
        mime = QMimeData()
        mime.setText(entry_name)
        clipboard.setMimeData(mime)

    def _paste_entry(self):
        QMessageBox.information(
            self, self._lang.tr("info", "Info"),
            self._lang.tr("paste_not_supported", "Paste is not available for archive entries."),
        )

    def _delete_entry(self, entry_name: str):
        if not self._current_archive:
            return
        reply = QMessageBox.question(
            self, self._lang.tr("confirm_delete", "Confirm Delete"),
            self._lang.tr("delete_entry_confirm", "Delete '{name}' from the archive?").format(name=entry_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        temp_dir = tempfile.mkdtemp(prefix="kouprey_del_")
        try:
            archive_path = self._current_archive.path
            password = ""
            if archive_requires_password(archive_path):
                from PyQt6.QtWidgets import QInputDialog
                password, ok = QInputDialog.getText(
                    self, self._lang.tr("password", "Password"),
                    self._lang.tr("enter_password_opt", "Enter password (leave empty if none):"),
                    QLineEdit.EchoMode.Password,
                )
                if not ok:
                    return
            extractor = Extractor(archive_path, temp_dir, password)
            res = extractor.extract_all()
            if not res.success:
                QMessageBox.critical(
                    self, self._lang.tr("error", "Error"), res.message,
                )
                return
            entry_path = os.path.join(temp_dir, entry_name)
            if os.path.isfile(entry_path):
                os.remove(entry_path)
            elif os.path.isdir(entry_path):
                shutil.rmtree(entry_path)
            # Collect remaining paths after removal
            remaining = []
            for root, _, files in os.walk(temp_dir):
                for f in files:
                    remaining.append(os.path.join(root, f))
            if not remaining:
                QMessageBox.information(
                    self, self._lang.tr("info", "Info"),
                    self._lang.tr("archive_empty", "The archive would be empty. Deletion cancelled."),
                )
                return
            new_path = archive_path + ".tmp"
            compressor = Compressor(new_path, remaining, password)
            cres = compressor.compress()
            if not cres.success:
                QMessageBox.critical(
                    self, self._lang.tr("error", "Error"), cres.message,
                )
                return
            os.remove(archive_path)
            os.rename(new_path, archive_path)
            self._load_archive(archive_path)
        except Exception as e:
            QMessageBox.critical(
                self, self._lang.tr("error", "Error"), str(e),
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _extract_single_entry(self, entry_name: str):
        if not self._current_archive:
            return
        output_dir = QFileDialog.getExistingDirectory(
            self, self._lang.tr("select_output_dir", "Select Output Directory"),
        )
        if not output_dir:
            return
        password = ""
        if archive_requires_password(self._current_archive.path):
            from PyQt6.QtWidgets import QInputDialog
            password, ok = QInputDialog.getText(
                self, self._lang.tr("password", "Password"),
                self._lang.tr("enter_password_opt", "Enter password (leave empty if none):"),
                QLineEdit.EchoMode.Password,
            )
            if not ok:
                return
        if entry_name.endswith("/"):
            worker = DirectoryExtractWorker(
                self._current_archive.path, entry_name, output_dir, password,
            )
        else:
            worker = SingleEntryExtractWorker(
                self._current_archive.path, entry_name, output_dir, password,
            )
        self._single_extract_worker = worker
        worker.result.connect(self._on_single_extract_result)
        worker.start()

    def _on_single_extract_result(self, res: ExtractResult):
        if res.success:
            QMessageBox.information(
                self, self._lang.tr("success", "Success"),
                self._lang.tr("extract_complete", "Extraction complete."),
            )
        else:
            QMessageBox.critical(
                self, self._lang.tr("error", "Error"), res.message,
            )

    def _add_files_to_archive(self):
        if not self._current_archive:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, self._lang.tr("select_files", "Select Files"),
        )
        if not files:
            return
        self._add_to_archive(files)

    def _add_folder_to_archive(self):
        if not self._current_archive:
            return
        folder = QFileDialog.getExistingDirectory(
            self, self._lang.tr("select_folder", "Select Folder"),
        )
        if not folder:
            return
        self._add_to_archive([folder])

    def _add_to_archive(self, sources: list[str]):
        if not self._current_archive:
            return
        archive_path = self._current_archive.path
        password = ""
        if archive_requires_password(archive_path):
            from PyQt6.QtWidgets import QInputDialog
            password, ok = QInputDialog.getText(
                self, self._lang.tr("password", "Password"),
                self._lang.tr("enter_password_opt", "Enter password (leave empty if none):"),
                QLineEdit.EchoMode.Password,
            )
            if not ok:
                return
        temp_dir = tempfile.mkdtemp(prefix="kouprey_add_")
        try:
            extractor = Extractor(archive_path, temp_dir, password)
            res = extractor.extract_all()
            if not res.success:
                QMessageBox.critical(
                    self, self._lang.tr("error", "Error"), res.message,
                )
                return
            for src in sources:
                if os.path.isfile(src):
                    shutil.copy2(src, temp_dir)
                elif os.path.isdir(src):
                    dest = os.path.join(temp_dir, os.path.basename(src))
                    shutil.copytree(src, dest, dirs_exist_ok=True)
            new_path = archive_path + ".tmp"
            remaining = []
            for root, _, files in os.walk(temp_dir):
                for f in files:
                    remaining.append(os.path.join(root, f))
            if not remaining:
                QMessageBox.information(
                    self, self._lang.tr("info", "Info"),
                    self._lang.tr("archive_empty", "The archive would be empty. Operation cancelled."),
                )
                return
            compressor = Compressor(new_path, remaining, password)
            cres = compressor.compress()
            if not cres.success:
                QMessageBox.critical(
                    self, self._lang.tr("error", "Error"), cres.message,
                )
                return
            os.remove(archive_path)
            os.rename(new_path, archive_path)
            self._load_archive(archive_path)
        except Exception as e:
            QMessageBox.critical(
                self, self._lang.tr("error", "Error"), str(e),
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def retranslate(self):
        self._empty_text.setText(
            self._lang.tr("no_archive_open", "No archive is open.")
        )
        self._open_btn.setText(
            self._lang.tr("action_open", "Open Archive...")
        )
        self._add_files_btn.setText(self._lang.tr("add_files", "Add Files"))
        self._add_folder_btn.setText(self._lang.tr("add_folder", "Add Folder"))
        self._extract_btn.setText(
            self._lang.tr("action_extract", "Extract...")
        )
        if self._current_archive:
            self._update_info()
            self._refresh_table()
