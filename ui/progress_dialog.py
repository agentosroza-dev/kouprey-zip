import os

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QVBoxLayout, QMessageBox,
)

from core.compressor import CompressResult, Compressor
from core.language import LanguageManager


class _QuickCompressWorker(QThread):
    progress = pyqtSignal(int, int)
    result = pyqtSignal(CompressResult)

    def __init__(self, compressor: Compressor):
        super().__init__()
        self._compressor = compressor

    def run(self):
        res = self._compressor.compress(
            progress_callback=lambda c, t: self.progress.emit(c, t),
        )
        if not self.isInterruptionRequested():
            self.result.emit(res)


class QuickCompressDialog(QDialog):
    def __init__(self, compressor: Compressor, lang: LanguageManager, parent=None):
        super().__init__(parent)
        self._compressor = compressor
        self._lang = lang
        self._cancelled = False
        self._worker = None
        self._setup_ui()
        self._start_compression()

    def _setup_ui(self):
        self.setWindowTitle(self._lang.tr("quick_compress_title", "Creating *.kpz..."))
        self.setFixedSize(420, 200)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        self._file_label = QLabel()
        self._file_label.setWordWrap(True)
        layout.addWidget(self._file_label)

        self._progress_bar = QProgressBar()
        layout.addWidget(self._progress_bar)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._cancel_btn = QPushButton(self._lang.tr("quick_compress_cancel", "Cancel"))
        self._cancel_btn.clicked.connect(self._on_cancel)
        self._cancel_btn.setFixedWidth(100)
        btn_layout.addWidget(self._cancel_btn)
        layout.addLayout(btn_layout)

        out_name = os.path.basename(self._compressor.output_path)
        self._file_label.setText(
            self._lang.tr("quick_compress_output", "Output: {name}").format(name=out_name)
        )

    def _start_compression(self):
        self._worker = _QuickCompressWorker(self._compressor)
        self._worker.progress.connect(self._on_progress)
        self._worker.result.connect(self._on_result)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    def _on_progress(self, current: int, total: int):
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(current)

    def _on_result(self, res: CompressResult):
        if self._cancelled:
            return
        if res.success:
            self.accept()
        else:
            QMessageBox.critical(
                self,
                self._lang.tr("error", "Error"),
                self._lang.tr("quick_compress_error", "Compression failed: {message}").format(message=res.message),
            )
            self.reject()

    def _on_worker_finished(self):
        pass

    def _on_cancel(self):
        self._cancelled = True
        if self._worker and self._worker.isRunning():
            self._worker.requestInterruption()
            if not self._worker.wait(3000):
                self._worker.terminate()
                self._worker.wait()
        self.reject()
