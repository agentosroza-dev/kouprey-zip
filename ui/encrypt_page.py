import os

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPlainTextEdit, QPushButton, QTabWidget,
    QToolBar, QVBoxLayout, QWidget,
)

from core.encryptor import decrypt_file, decrypt_text, encrypt_file, encrypt_text
from core.language import LanguageManager
from core.theme import ThemeManager


class EncryptWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, func, *args):
        super().__init__()
        self._func = func
        self._args = args

    def run(self):
        try:
            self._func(*self._args)
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))


class EncryptPage(QWidget):
    def __init__(self, lang: LanguageManager, theme: ThemeManager):
        super().__init__()
        self._lang = lang
        self._theme = theme
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_text_tab(), "")
        self._tabs.addTab(self._build_file_tab(), "")
        layout.addWidget(self._tabs)

    def _build_text_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)

        self._text_input_label = QLabel()
        self._text_input_label.setObjectName("captionLabel")
        card_layout.addWidget(self._text_input_label)

        self._text_input = QPlainTextEdit()
        self._text_input.setMinimumHeight(120)
        self._text_input.setPlaceholderText("")
        card_layout.addWidget(self._text_input)

        pwd_row = QHBoxLayout()
        self._text_pwd_label = QLabel()
        self._text_pwd_label.setObjectName("captionLabel")
        pwd_row.addWidget(self._text_pwd_label)
        self._text_password = QLineEdit()
        self._text_password.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_row.addWidget(self._text_password, 1)
        card_layout.addLayout(pwd_row)

        btn_row = QHBoxLayout()
        self._text_encrypt_btn = QPushButton()
        self._text_encrypt_btn.setObjectName("accentButton")
        self._text_encrypt_btn.clicked.connect(self._do_encrypt_text)
        btn_row.addWidget(self._text_encrypt_btn)
        self._text_decrypt_btn = QPushButton()
        self._text_decrypt_btn.clicked.connect(self._do_decrypt_text)
        btn_row.addWidget(self._text_decrypt_btn)
        btn_row.addStretch()
        card_layout.addLayout(btn_row)

        layout.addWidget(card)

        output_card = QFrame()
        output_card.setObjectName("card")
        output_layout = QVBoxLayout(output_card)
        output_layout.setSpacing(8)

        self._text_output_label = QLabel()
        self._text_output_label.setObjectName("captionLabel")
        output_layout.addWidget(self._text_output_label)

        self._text_output = QPlainTextEdit()
        self._text_output.setReadOnly(True)
        self._text_output.setMinimumHeight(120)
        output_layout.addWidget(self._text_output)

        layout.addWidget(output_card)
        return tab

    def _build_file_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        src_row = QHBoxLayout()
        self._file_src_label = QLabel()
        self._file_src_label.setObjectName("captionLabel")
        src_row.addWidget(self._file_src_label)
        self._file_src = QLineEdit()
        self._file_src.setReadOnly(True)
        src_row.addWidget(self._file_src, 1)
        self._file_src_btn = QPushButton()
        self._file_src_btn.clicked.connect(self._browse_src)
        src_row.addWidget(self._file_src_btn)
        card_layout.addLayout(src_row)

        dest_row = QHBoxLayout()
        self._file_dest_label = QLabel()
        self._file_dest_label.setObjectName("captionLabel")
        dest_row.addWidget(self._file_dest_label)
        self._file_dest = QLineEdit()
        dest_row.addWidget(self._file_dest, 1)
        self._file_dest_btn = QPushButton()
        self._file_dest_btn.clicked.connect(self._browse_dest)
        dest_row.addWidget(self._file_dest_btn)
        card_layout.addLayout(dest_row)

        pwd_row = QHBoxLayout()
        self._file_pwd_label = QLabel()
        self._file_pwd_label.setObjectName("captionLabel")
        pwd_row.addWidget(self._file_pwd_label)
        self._file_password = QLineEdit()
        self._file_password.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_row.addWidget(self._file_password, 1)
        card_layout.addLayout(pwd_row)

        btn_row = QHBoxLayout()
        self._file_encrypt_btn = QPushButton()
        self._file_encrypt_btn.setObjectName("accentButton")
        self._file_encrypt_btn.clicked.connect(self._do_encrypt_file)
        btn_row.addWidget(self._file_encrypt_btn)
        self._file_decrypt_btn = QPushButton()
        self._file_decrypt_btn.clicked.connect(self._do_decrypt_file)
        btn_row.addWidget(self._file_decrypt_btn)
        btn_row.addStretch()
        card_layout.addLayout(btn_row)

        layout.addWidget(card)
        return tab

    def populate_toolbar(self, toolbar: QToolBar):
        pass

    def _browse_src(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self._lang.tr("select_file", "Select File"),
        )
        if path:
            self._file_src.setText(path)

    def _browse_dest(self):
        path, _ = QFileDialog.getSaveFileName(
            self, self._lang.tr("save_as", "Save As"),
            "", "Encrypted Files (*.enc);;All Files (*.*)",
        )
        if path:
            self._file_dest.setText(path)

    def _do_encrypt_text(self):
        text = self._text_input.toPlainText()
        password = self._text_password.text()
        if not text:
            QMessageBox.warning(self, self._lang.tr("warning", "Warning"),
                                self._lang.tr("enter_text", "Please enter text to encrypt."))
            return
        if not password:
            QMessageBox.warning(self, self._lang.tr("warning", "Warning"),
                                self._lang.tr("enter_password", "Please enter a password."))
            return
        try:
            result = encrypt_text(text, password)
            self._text_output.setPlainText(result)
        except Exception as e:
            QMessageBox.critical(self, self._lang.tr("error", "Error"), str(e))

    def _do_decrypt_text(self):
        text = self._text_input.toPlainText().strip()
        password = self._text_password.text()
        if not text:
            QMessageBox.warning(self, self._lang.tr("warning", "Warning"),
                                self._lang.tr("enter_encrypted", "Please paste the encrypted text."))
            return
        if not password:
            QMessageBox.warning(self, self._lang.tr("warning", "Warning"),
                                self._lang.tr("enter_password", "Please enter a password."))
            return
        try:
            result = decrypt_text(text, password)
            self._text_output.setPlainText(result)
        except Exception as e:
            QMessageBox.critical(self, self._lang.tr("error", "Error"),
                                 self._lang.tr("decrypt_failed", "Decryption failed. Wrong password or corrupted data."))

    def _do_encrypt_file(self):
        src = self._file_src.text().strip()
        dest = self._file_dest.text().strip()
        password = self._file_password.text()
        if not src or not os.path.isfile(src):
            QMessageBox.warning(self, self._lang.tr("warning", "Warning"),
                                self._lang.tr("select_source", "Please select a source file."))
            return
        if not dest:
            QMessageBox.warning(self, self._lang.tr("warning", "Warning"),
                                self._lang.tr("specify_output", "Please specify an output file."))
            return
        if not password:
            QMessageBox.warning(self, self._lang.tr("warning", "Warning"),
                                self._lang.tr("enter_password", "Please enter a password."))
            return
        self._run_worker(encrypt_file, src, dest, password)

    def _do_decrypt_file(self):
        src = self._file_src.text().strip()
        dest = self._file_dest.text().strip()
        password = self._file_password.text()
        if not src or not os.path.isfile(src):
            QMessageBox.warning(self, self._lang.tr("warning", "Warning"),
                                self._lang.tr("select_source", "Please select a source file."))
            return
        if not dest:
            QMessageBox.warning(self, self._lang.tr("warning", "Warning"),
                                self._lang.tr("specify_output", "Please specify an output file."))
            return
        if not password:
            QMessageBox.warning(self, self._lang.tr("warning", "Warning"),
                                self._lang.tr("enter_password", "Please enter a password."))
            return
        self._run_worker(decrypt_file, src, dest, password)

    def _run_worker(self, func, *args):
        self._worker = EncryptWorker(func, *args)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(False)

    def _on_worker_finished(self, success: bool, message: str):
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(True)
        if success:
            QMessageBox.information(
                self, self._lang.tr("success", "Success"),
                self._lang.tr("operation_complete", "Operation completed successfully."),
            )
        else:
            QMessageBox.critical(
                self, self._lang.tr("error", "Error"), message,
            )

    def retranslate(self):
        self._tabs.setTabText(0, self._lang.tr("encrypt_text", "Encrypt Text"))
        self._tabs.setTabText(1, self._lang.tr("encrypt_file", "Encrypt File"))

        self._text_input_label.setText(self._lang.tr("input_text", "Input Text"))
        self._text_pwd_label.setText(self._lang.tr("password", "Password:"))
        self._text_output_label.setText(self._lang.tr("output", "Output"))
        self._file_src_label.setText(self._lang.tr("source_file", "Source File"))
        self._file_dest_label.setText(self._lang.tr("dest_file", "Destination"))
        self._file_pwd_label.setText(self._lang.tr("password", "Password:"))
        self._file_src_btn.setText(self._lang.tr("browse", "Browse..."))
        self._file_dest_btn.setText(self._lang.tr("browse", "Browse..."))
        self._text_encrypt_btn.setText(self._lang.tr("encrypt", "Encrypt"))
        self._text_decrypt_btn.setText(self._lang.tr("decrypt", "Decrypt"))
        self._file_encrypt_btn.setText(self._lang.tr("encrypt", "Encrypt"))
        self._file_decrypt_btn.setText(self._lang.tr("decrypt", "Decrypt"))

        self._text_input.setPlaceholderText(
            self._lang.tr("enter_text_hint", "Enter text to encrypt or paste encrypted text to decrypt...")
        )
