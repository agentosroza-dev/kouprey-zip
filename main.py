import argparse
import glob
import json
import os
import sys
import tempfile

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from app_config import load_config
from core.auth import load_env
from core.compressor import Compressor
from core.extractor import Extractor
from core.language import LanguageManager
from core.theme import ThemeManager
from ui.main_window import MainWindow
from ui.progress_dialog import QuickCompressDialog


_DEBUG_LOG = os.path.join(tempfile.gettempdir(), "kouprey_zip_debug.log")
_IPC_DIR = os.path.join(tempfile.gettempdir(), ".kouprey_zip_ipc")


def _debug(msg):
    try:
        with open(_DEBUG_LOG, "a") as f:
            f.write(f"{msg}\n")
    except Exception:
        pass


def _is_first_instance() -> bool:
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    mutex = kernel32.CreateMutexW(None, False, "KoupreyZip_SingleInstance")
    if not mutex:
        _debug("CreateMutexW returned NULL, assuming first instance")
        return True
    is_first = ctypes.get_last_error() != 183
    _debug(f"CreateMutexW: is_first={is_first}, last_error={ctypes.get_last_error()}")
    return is_first


def _write_ipc(compress_paths, open_path, extract_path):
    os.makedirs(_IPC_DIR, exist_ok=True)
    data = {"compress": compress_paths or [], "open": open_path or "", "extract": extract_path or ""}
    path = os.path.join(_IPC_DIR, f"cmd_{os.getpid()}.json")
    try:
        with open(path, "w") as f:
            json.dump(data, f)
        _debug(f"Wrote IPC: {path} -> {data}")
    except Exception as e:
        _debug(f"IPC write error: {e}")


def _collect_ipc():
    results = {"compress": [], "open": "", "extract": ""}
    for path in glob.glob(os.path.join(_IPC_DIR, "cmd_*.json")):
        try:
            with open(path) as f:
                data = json.load(f)
            _debug(f"IPC collect: {path} -> {data}")
            results["compress"].extend(data.get("compress") or [])
            if data.get("open") and not results["open"]:
                results["open"] = data["open"]
            if data.get("extract") and not results["extract"]:
                results["extract"] = data["extract"]
        except Exception as e:
            _debug(f"IPC collect error {path}: {e}")
        try:
            os.remove(path)
        except Exception:
            pass
    return results


def _quick_compress(paths: list[str], lang: LanguageManager) -> None:
    if not paths:
        print("No files specified.")
        sys.exit(1)
    name = os.path.splitext(os.path.basename(paths[0]))[0]
    output = os.path.join(os.path.dirname(paths[0]), f"{name}.kpz")
    compressor = Compressor(output, paths)
    dialog = QuickCompressDialog(compressor, lang)
    dialog.exec()


def _quick_extract(archive: str, subdir: bool = False) -> None:
    if not archive or not os.path.isfile(archive):
        print("Invalid archive file.")
        sys.exit(1)
    base = os.path.dirname(os.path.abspath(archive))
    if subdir:
        name = os.path.splitext(os.path.basename(archive))[0]
        out = os.path.join(base, name)
    else:
        out = base
    extractor = Extractor(archive, out)
    result = extractor.extract_all()
    if result.success:
        print(f"Extracted {result.extracted_count} entries to: {out}")
    else:
        print(f"Error: {result.message}")
        sys.exit(1)


def _flatten(groups):
    return [p for group in (groups or []) for p in group]

def _last(items):
    return items[-1] if items else None

def parse_args():
    parser = argparse.ArgumentParser(prog="Kouprey-Zip")
    parser.add_argument("--compress", action="append", nargs="+", help="Files/folders to compress")
    parser.add_argument("--quick-compress", action="append", nargs="+", help="Quick compress to .kpz without GUI")
    parser.add_argument("--quick-extract-here", action="append", help="Extract archive to current directory")
    parser.add_argument("--quick-extract-to", action="append", help="Extract archive to subfolder")
    parser.add_argument("--extract", action="append", help="Archive file to extract")
    parser.add_argument("--open", action="append", help="Archive file to open")
    args = parser.parse_args()
    args.compress = _flatten(args.compress)
    args.quick_compress = _flatten(args.quick_compress)
    args.open = _last(args.open)
    args.extract = _last(args.extract)
    args.quick_extract_here = _last(args.quick_extract_here)
    args.quick_extract_to = _last(args.quick_extract_to)
    return args


def main():
    _debug("=== Kouprey-Zip started ===")
    _debug(f"sys.argv: {sys.argv}")
    _debug(f"sys.executable: {sys.executable}")
    _debug(f"PID: {os.getpid()}")

    load_env()
    app = QApplication(sys.argv)
    _icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons", "Kouprey Logo Variations.ico")
    if os.path.isfile(_icon_path):
        app.setWindowIcon(QIcon(_icon_path))
    args = parse_args()

    config = load_config()

    _here = os.path.dirname(os.path.abspath(__file__))
    lang_dir = os.path.join(_here, "assets", "lang")
    lang = LanguageManager(lang_dir)
    theme = ThemeManager(app)
    theme_mode = config.get("theme", "light")
    theme.set_mode(theme_mode)
    lang.set_language(config.get("language", lang.current))

    _debug(f"args.compress: {args.compress}")
    _debug(f"args.open: {args.open}")
    _debug(f"args.extract: {args.extract}")

    if args.quick_compress:
        _quick_compress(args.quick_compress, lang)
        return
    if args.quick_extract_here:
        _quick_extract(args.quick_extract_here, subdir=False)
        return
    if args.quick_extract_to:
        _quick_extract(args.quick_extract_to, subdir=True)
        return

    has_args = bool(args.compress or args.open or args.extract)

    if has_args and not _is_first_instance():
        _debug("Another instance running, sending paths via IPC and exiting")
        _write_ipc(args.compress, args.open, args.extract)
        sys.exit(0)

    _ipc_compress, _ipc_open, _ipc_extract = [], None, None
    if has_args:
        _debug("First instance — waiting for IPC from co-launched processes...")
        import time
        for _ in range(4):
            time.sleep(0.3)
            _data = _collect_ipc()
            if _data["compress"]:
                _ipc_compress = _data["compress"]
                _ipc_open = _data["open"] or None
                _ipc_extract = _data["extract"] or None
                _debug(f"IPC collected on iter: compress={_ipc_compress}")
                break

    _all_compress = list(args.compress or []) + (_ipc_compress or [])
    _all_open = args.open or _ipc_open
    _all_extract = args.extract or _ipc_extract

    window = MainWindow(lang, theme,
                        compress_paths=_all_compress or None,
                        open_path=_all_open,
                        extract_path=_all_extract)

    for old in glob.glob(os.path.join(_IPC_DIR, "cmd_*.json")):
        try:
            os.remove(old)
        except Exception:
            pass

    def _poll():
        data = _collect_ipc()
        compress = data["compress"] or None
        open_path = data["open"] or None
        extract_path = data["extract"] or None
        if compress or open_path or extract_path:
            _debug(f"IPC poll received: compress={compress}, open={open_path}, extract={extract_path}")
            window.receive_paths(compress, open_path, extract_path)

    _timer = QTimer()
    _timer.timeout.connect(_poll)
    _timer.start(300)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        _debug(f"CRASH: {e}\n{traceback.format_exc()}")
        raise
