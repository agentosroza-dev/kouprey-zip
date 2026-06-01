import os
import tarfile
import zipfile

import py7zr

from core.formats import ArchiveFormat
from core.archive import _ensure_unrar


class ExtractResult:
    def __init__(self, success: bool, extracted_count: int, message: str = ""):
        self.success = success
        self.extracted_count = extracted_count
        self.message = message


class Extractor:
    def __init__(self, archive_path: str, output_dir: str, password: str = ""):
        self.archive_path = archive_path
        self.output_dir = output_dir
        self._password = password
        self._fmt = ArchiveFormat.from_extension(archive_path)

    def extract_all(self, progress_callback=None) -> ExtractResult:
        os.makedirs(self.output_dir, exist_ok=True)
        try:
            if self._fmt == ArchiveFormat.KPZ:
                return self._extract_kpz(progress_callback)
            if self._fmt == ArchiveFormat.ZIP:
                return self._extract_zip(progress_callback)
            if self._fmt in (ArchiveFormat.TAR, ArchiveFormat.GZIP,
                             ArchiveFormat.BZIP2, ArchiveFormat.XZ, ArchiveFormat.ZSTD):
                return self._extract_tar(progress_callback)
            if self._fmt in (ArchiveFormat.SEVEN_ZIP, ArchiveFormat.ISO):
                return self._extract_sevenzip(progress_callback)
            if self._fmt == ArchiveFormat.RAR:
                return self._extract_rar(progress_callback)
            return ExtractResult(False, 0, f"Format not supported: {self._fmt}")
        except Exception as e:
            return ExtractResult(False, 0, str(e))

    def _extract_kpz(self, progress_callback=None) -> ExtractResult:
        pwd = self._password.encode("utf-8") if self._password else None
        try:
            with zipfile.ZipFile(self.archive_path, "r") as zf:
                members = zf.infolist()
                total = len(members)
                if progress_callback:
                    progress_callback(0, total)
                zf.extractall(self.output_dir, pwd=pwd)
                if progress_callback:
                    progress_callback(total, total)
                return ExtractResult(True, total)
        except zipfile.BadZipFile:
            return self._extract_sevenzip(progress_callback)

    def _extract_zip(self, progress_callback=None) -> ExtractResult:
        pwd = self._password.encode("utf-8") if self._password else None
        try:
            with zipfile.ZipFile(self.archive_path, "r") as zf:
                members = zf.infolist()
                total = len(members)
                if progress_callback:
                    progress_callback(0, total)
                zf.extractall(self.output_dir, pwd=pwd)
                if progress_callback:
                    progress_callback(total, total)
                return ExtractResult(True, total)
        except zipfile.BadZipFile:
            return self._extract_sevenzip(progress_callback)

    def _extract_tar(self, progress_callback=None) -> ExtractResult:
        if self._password:
            import patoolib
            patoolib.extract_archive(self.archive_path, outdir=self.output_dir, password=self._password)
            count = sum(len(files) for _, _, files in os.walk(self.output_dir))
            if progress_callback:
                progress_callback(count, count)
            return ExtractResult(True, count)
        with tarfile.open(self.archive_path, "r:*") as tf:
            members = tf.getmembers()
            total = len(members)
            if progress_callback:
                progress_callback(0, total)
            tf.extractall(self.output_dir)
            if progress_callback:
                progress_callback(total, total)
            return ExtractResult(True, total)

    def _extract_sevenzip(self, progress_callback=None) -> ExtractResult:
        kwargs = {}
        if self._password:
            kwargs["password"] = self._password
        with py7zr.SevenZipFile(self.archive_path, "r", **kwargs) as sz:
            count = len(sz.list())
            if progress_callback:
                progress_callback(0, count)
            sz.extractall(self.output_dir)
            if progress_callback:
                progress_callback(count, count)
            return ExtractResult(True, count)

    def _extract_rar(self, progress_callback=None) -> ExtractResult:
        import rarfile
        try:
            _ensure_unrar()
            pwd = self._password if self._password else None
            with rarfile.RarFile(self.archive_path) as rf:
                members = rf.infolist()
                total = len(members)
                if progress_callback:
                    progress_callback(0, total)
                rf.extractall(self.output_dir, pwd=pwd)
                if progress_callback:
                    progress_callback(total, total)
                return ExtractResult(True, total)
        except rarfile.RarCannotExec:
            import patoolib
            kwargs = {"outdir": self.output_dir}
            if self._password:
                kwargs["password"] = self._password
            patoolib.extract_archive(self.archive_path, **kwargs)
            count = sum(len(files) for _, _, files in os.walk(self.output_dir))
            if progress_callback:
                progress_callback(count, count)
            return ExtractResult(True, count)
