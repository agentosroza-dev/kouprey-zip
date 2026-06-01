import os
import sys
import winreg


def _app_cmd() -> str:
    if getattr(sys, 'frozen', False):
        return sys.executable
    py = sys.executable
    script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
    return f'"{py}" "{script}"'


_ARCHIVE_EXTS = [
    ".kpz", ".zip", ".7z", ".rar",
    ".tar", ".tar.gz", ".tar.bz2", ".tar.xz", ".tar.zst", ".iso",
]


def register_context_menu(compress_label: str = "Add Archive with Kouprey",
                          extract_label: str = "Extract with Kouprey",
                          open_label: str = "Open with Kouprey-Zip",
                          quick_kpz_label: str = "Create *.kpz",
                          quick_extract_here_label: str = "Extract Here",
                          quick_extract_to_label: str = "Extract to Folder"):
    unregister_context_menu()
    app = _app_cmd()
    ico = sys.executable + ",0"

    def R(path, name, value):
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{path}") as k:
                if name is None:
                    winreg.SetValueEx(k, "", 0, winreg.REG_SZ, value)
                else:
                    winreg.SetValueEx(k, name, 0, winreg.REG_SZ, value)
        except Exception:
            pass

    def verbs(prefix, items):
        for vn, vl, vc in items:
            R(f"{prefix}\\{vn}", "MUIVerb", vl)
            R(f"{prefix}\\{vn}\\command", None, vc)
            R(f"{prefix}\\{vn}", "Icon", ico)

    all_verbs = [
        ("KoupreyZipArchive",     compress_label,          f'{app} --compress "%1"'),
        ("KoupreyZipKPZ",         quick_kpz_label,          f'{app} --quick-compress "%1"'),
        ("KoupreyZipExtractHere", quick_extract_here_label,  f'{app} --quick-extract-here "%1"'),
        ("KoupreyZipExtractTo",   quick_extract_to_label,    f'{app} --quick-extract-to "%1"'),
        ("KoupreyZipExtract",     extract_label,             f'{app} --extract "%1"'),
    ]
    compress_verbs = [
        ("KoupreyZipArchive", compress_label, f'{app} --compress "%1"'),
        ("KoupreyZipKPZ",     quick_kpz_label, f'{app} --quick-compress "%1"'),
    ]
    extract_verbs = [
        ("KoupreyZipExtractHere", quick_extract_here_label, f'{app} --quick-extract-here "%1"'),
        ("KoupreyZipExtractTo",   quick_extract_to_label,   f'{app} --quick-extract-to "%1"'),
        ("KoupreyZipExtract",     extract_label,            f'{app} --extract "%1"'),
    ]

    for p in [r"*\shell", r"Directory\shell"]:
        verbs(p, all_verbs)
    for p in [r"Directory\Background\shell", r"Drive\shell"]:
        verbs(p, compress_verbs)
    for p in [r"SystemFileAssociations\archive\shell"] + [f"{ext}\\shell" for ext in _ARCHIVE_EXTS]:
        verbs(p, extract_verbs)

    # ProgID + icon for .kpz files
    R(r".kpz", None, "KoupreyZip.Archive")
    R(r"KoupreyZip.Archive\DefaultIcon", None, ico)
    R(r"KoupreyZip.Archive\shell\open", "MUIVerb", open_label)
    R(r"KoupreyZip.Archive\shell\open", "Icon", ico)
    R(r"KoupreyZip.Archive\shell\open\command", None, f'{app} --open "%1"')
    _notify_shell()


def unregister_context_menu():
    cleaned = set()

    def D(root, path):
        full = f"Software\\Classes\\{path}"
        try:
            k = winreg.OpenKey(root, full, 0, winreg.KEY_READ | winreg.KEY_WRITE)
        except Exception:
            return
        subs = []
        i = 0
        while True:
            try:
                subs.append(winreg.EnumKey(k, i))
                i += 1
            except OSError:
                break
        winreg.CloseKey(k)
        for s in subs:
            D(root, f"{path}\\{s}")
        try:
            winreg.DeleteKey(root, full)
            cleaned.add(full)
        except Exception:
            pass

    base = winreg.HKEY_CURRENT_USER
    targets = [
        r"*\shell\KoupreyZip",
        r"*\shell\KoupreyZipMenu",
        r"*\shell\KoupreyZipArchive",
        r"*\shell\KoupreyZipKPZ",
        r"*\shell\KoupreyZipExtractHere",
        r"*\shell\KoupreyZipExtractTo",
        r"*\shell\KoupreyZipExtract",
        r"Directory\shell\KoupreyZip",
        r"Directory\shell\KoupreyZipMenu",
        r"Directory\shell\KoupreyZipArchive",
        r"Directory\shell\KoupreyZipKPZ",
        r"Directory\shell\KoupreyZipExtractHere",
        r"Directory\shell\KoupreyZipExtractTo",
        r"Directory\shell\KoupreyZipExtract",
        r"Directory\Background\shell\KoupreyZip",
        r"Directory\Background\shell\KoupreyZipMenu",
        r"Directory\Background\shell\KoupreyZipArchive",
        r"Directory\Background\shell\KoupreyZipKPZ",
        r"Drive\shell\KoupreyZip",
        r"Drive\shell\KoupreyZipMenu",
        r"Drive\shell\KoupreyZipArchive",
        r"Drive\shell\KoupreyZipKPZ",
        r"SystemFileAssociations\archive\shell\KoupreyZip",
        r"SystemFileAssociations\archive\shell\KoupreyZipMenu",
        r"SystemFileAssociations\archive\shell\KoupreyZipExtractHere",
        r"SystemFileAssociations\archive\shell\KoupreyZipExtractTo",
        r"SystemFileAssociations\archive\shell\KoupreyZipExtract",
        r"SystemFileAssociations\archive\shell\KoupreyZipExtract\command",
    ]
    for ext in _ARCHIVE_EXTS:
        targets.append(f"{ext}\\shell\\KoupreyZip")
        targets.append(f"{ext}\\shell\\KoupreyZipMenu")
        targets.append(f"{ext}\\shell\\KoupreyZipExtractHere")
        targets.append(f"{ext}\\shell\\KoupreyZipExtractTo")
        targets.append(f"{ext}\\shell\\KoupreyZipExtract")
    targets += [
        r"KoupreyZip.Archive\shell\open\command",
        r"KoupreyZip.Archive\shell\open",
        r"KoupreyZip.Archive\shell",
        r"KoupreyZip.Archive",
        r".kpz",
    ]

    for t in targets:
        D(base, t)
    _notify_shell()


def is_registered() -> bool:
    try:
        winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                       r"Software\Classes\Directory\shell\KoupreyZipArchive")
        return True
    except Exception:
        return False


def _notify_shell():
    try:
        import ctypes
        ctypes.windll.shell32.SHChangeNotify(0x0800, 0x0000, None, None)
    except Exception:
        pass
