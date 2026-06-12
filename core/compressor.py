import os
import sys
import subprocess
import tarfile
import zipfile

import py7zr

from core.formats import ArchiveFormat

if sys.platform == "win32":
    _RAR_PATHS = [
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "WinRAR", "rar.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "WinRAR", "rar.exe"),
    ]
else:
    _RAR_PATHS = []


def _find_rar() -> str | None:
    import shutil
    exe = shutil.which("rar")
    if exe:
        return exe
    for p in _RAR_PATHS:
        if os.path.isfile(p):
            return p
    return None


class CompressResult:
    def __init__(self, success: bool, message: str = ""):
        self.success = success
        self.message = message


class Compressor:
    def __init__(self, output_path: str, source_paths: list[str], password: str = ""):
        self.output_path = output_path
        self.source_paths = source_paths
        self._password = password
        self._fmt = ArchiveFormat.from_extension(output_path)

    def compress(self, progress_callback=None) -> CompressResult:
        try:
            if self._password:
                if self._fmt and not self._fmt.supports_password:
                    return CompressResult(False, "Password not supported for this format.")
                self._compress_encrypted(progress_callback)
            elif self._fmt in (ArchiveFormat.KPZ, ArchiveFormat.ZIP):
                self._compress_zip(progress_callback)
            elif self._fmt in (ArchiveFormat.TAR, ArchiveFormat.GZIP,
                               ArchiveFormat.BZIP2, ArchiveFormat.XZ, ArchiveFormat.ZSTD):
                self._compress_tar(progress_callback)
            elif self._fmt == ArchiveFormat.SEVEN_ZIP:
                self._compress_sevenzip(progress_callback)
            elif self._fmt == ArchiveFormat.RAR:
                self._compress_rar(progress_callback)
            else:
                return CompressResult(False, f"Format not supported: {self._fmt}")
            return CompressResult(True)
        except Exception as e:
            return CompressResult(False, str(e))

    def _compress_encrypted(self, progress_callback=None) -> None:
        files = self._all_files()
        total = len(files)
        if self._fmt == ArchiveFormat.ZIP:
            import patoolib
            patoolib.create_archive(self.output_path, files, password=self._password)
            if progress_callback:
                progress_callback(total, total)
            return
        if self._fmt == ArchiveFormat.RAR:
            self._compress_rar(progress_callback)
            return
        with py7zr.SevenZipFile(self.output_path, "w", password=self._password) as sz:
            base = self._common_base()
            for i, file_path in enumerate(files):
                arcname = os.path.relpath(file_path, base)
                sz.write(file_path, arcname)
                if progress_callback:
                    progress_callback(i + 1, total)

    def _compress_zip(self, progress_callback=None) -> None:
        with zipfile.ZipFile(self.output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            files = self._all_files()
            total = len(files)
            for i, file_path in enumerate(files):
                arcname = os.path.relpath(file_path, self._common_base())
                zf.write(file_path, arcname)
                if progress_callback:
                    progress_callback(i + 1, total)

    def _compress_tar(self, progress_callback=None) -> None:
        mode_map = {
            ArchiveFormat.TAR: "w",
            ArchiveFormat.GZIP: "w:gz",
            ArchiveFormat.BZIP2: "w:bz2",
            ArchiveFormat.XZ: "w:xz",
            ArchiveFormat.ZSTD: "w:zst",
        }
        with tarfile.open(self.output_path, mode_map.get(self._fmt, "w")) as tf:
            files = self._all_files()
            total = len(files)
            for i, file_path in enumerate(files):
                arcname = os.path.relpath(file_path, self._common_base())
                tf.add(file_path, arcname)
                if progress_callback:
                    progress_callback(i + 1, total)

    def _compress_rar(self, progress_callback=None) -> None:
        rar_exe = _find_rar()
        if not rar_exe:
            raise RuntimeError("RAR compression requires rar installed on your system.")
        if os.path.exists(self.output_path):
            os.unlink(self.output_path)
        files = self._all_files()
        total = len(files)
        pw_args = [f"-p{self._password}"] if self._password else []
        result = subprocess.run(
            [rar_exe, "a", "-ep1", *pw_args, self.output_path, *files],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"RAR compression failed: {result.stderr.strip()}")
        if progress_callback:
            progress_callback(total, total)

    def _compress_sevenzip(self, progress_callback=None) -> None:
        files = self._all_files()
        total = len(files)
        with py7zr.SevenZipFile(self.output_path, "w") as sz:
            base = self._common_base()
            for i, file_path in enumerate(files):
                arcname = os.path.relpath(file_path, base)
                sz.write(file_path, arcname)
                if progress_callback:
                    progress_callback(i + 1, total)

    def _all_files(self) -> list[str]:
        files: list[str] = []
        for path in self.source_paths:
            if os.path.isfile(path):
                files.append(path)
            elif os.path.isdir(path):
                for root, _, filenames in os.walk(path):
                    for f in filenames:
                        files.append(os.path.join(root, f))
        return files

    def _common_base(self) -> str:
        if not self.source_paths:
            return ""
        if len(self.source_paths) == 1:
            return os.path.dirname(self.source_paths[0])
        common = os.path.commonpath(self.source_paths)
        if os.path.isdir(common):
            return common
        return os.path.dirname(common)
