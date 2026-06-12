from core.formats import ArchiveFormat


MAGIC_MAP: dict[bytes, ArchiveFormat] = {
    b"PK\x03\x04": ArchiveFormat.ZIP,
    b"PK\x05\x06": ArchiveFormat.ZIP,
    b"PK\x07\x08": ArchiveFormat.ZIP,
    b"\x37\x7a\xbc\xaf\x27\x1c": ArchiveFormat.SEVEN_ZIP,
    b"Rar!\x1a\x07": ArchiveFormat.RAR,
    b"\x1f\x8b": ArchiveFormat.GZIP,
    b"BZh": ArchiveFormat.BZIP2,
    b"\xfd7zXZ\x00": ArchiveFormat.XZ,
    b"ustar": ArchiveFormat.TAR,
}


def detect_format(file_path: str) -> ArchiveFormat | None:
    with open(file_path, "rb") as f:
        header = f.read(32)
    for magic, fmt in MAGIC_MAP.items():
        if header.startswith(magic):
            return fmt
    return ArchiveFormat.from_extension(file_path)


def is_archive(file_path: str) -> bool:
    return detect_format(file_path) is not None
