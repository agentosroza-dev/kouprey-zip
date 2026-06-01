import os


def safe_filename(name: str) -> str:
    for c in '<>:"/\\|?*':
        name = name.replace(c, "_")
    return name.strip()


def human_readable_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path
