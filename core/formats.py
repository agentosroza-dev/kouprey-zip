import enum


class ArchiveFormat(enum.Enum):
    KPZ = (".kpz", "application/x-kouprey-zip")
    SEVEN_ZIP = (".7z", "application/x-7z-compressed")
    ZIP = (".zip", "application/zip")
    TAR = (".tar", "application/x-tar")
    GZIP = (".tar.gz", "application/gzip")
    BZIP2 = (".tar.bz2", "application/x-bzip2")
    BZ2 = (".bz2", "application/x-bzip2")
    XZ = (".tar.xz", "application/x-xz")
    ZSTD = (".tar.zst", "application/zstd")
    RAR = (".rar", "application/vnd.rar")
    ISO = (".iso", "application/x-iso9660-image")

    def __init__(self, extension: str, mime: str):
        self._extension = extension
        self._mime = mime

    @property
    def extension(self) -> str:
        return self._extension

    @property
    def mime(self) -> str:
        return self._mime

    @property
    def display_name(self) -> str:
        return self._extension.lstrip(".").upper()

    @property
    def supports_password(self) -> bool:
        return self in (ArchiveFormat.KPZ, ArchiveFormat.ZIP, ArchiveFormat.SEVEN_ZIP, ArchiveFormat.RAR)

    @staticmethod
    def from_extension(path: str):
        lower = path.lower()
        for fmt in ArchiveFormat:
            if lower.endswith(fmt.extension):
                return fmt
        if lower.endswith(".tgz"):
            return ArchiveFormat.GZIP
        if lower.endswith(".tbz2"):
            return ArchiveFormat.BZIP2
        if lower.endswith(".txz"):
            return ArchiveFormat.XZ
        if lower.endswith(".tzst"):
            return ArchiveFormat.ZSTD
        if lower.endswith(".bz2"):
            return ArchiveFormat.BZ2
        if lower.endswith(".gz"):
            return ArchiveFormat.GZIP
        if lower.endswith(".xz"):
            return ArchiveFormat.XZ
        if lower.endswith(".zst"):
            return ArchiveFormat.ZSTD
        return None


SUPPORTED_EXTRACT_FORMATS = [
    ArchiveFormat.KPZ, ArchiveFormat.SEVEN_ZIP, ArchiveFormat.ZIP,
    ArchiveFormat.TAR, ArchiveFormat.GZIP, ArchiveFormat.BZIP2,
    ArchiveFormat.BZ2, ArchiveFormat.XZ, ArchiveFormat.ZSTD,
    ArchiveFormat.RAR, ArchiveFormat.ISO,
]

SUPPORTED_COMPRESS_FORMATS = [
    ArchiveFormat.KPZ, ArchiveFormat.ZIP, ArchiveFormat.SEVEN_ZIP,
    ArchiveFormat.TAR, ArchiveFormat.GZIP, ArchiveFormat.BZIP2,
    ArchiveFormat.XZ, ArchiveFormat.ZSTD, ArchiveFormat.RAR,
]
