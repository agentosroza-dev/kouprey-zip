import os
import sys
from zipfile import ZipFile
from xml.etree import ElementTree

from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

_icon_cache: dict[str, QIcon] = {}
_icon_svgs: dict[str, str] = {}
_icon_color: str = ""


def set_icon_color(color: str) -> None:
    global _icon_color
    _icon_color = color
    _icon_cache.clear()


def _ensure_icons_loaded():
    if _icon_svgs:
        return
    if getattr(sys, 'frozen', False):
        zip_path = os.path.join(sys._MEIPASS, "lucide", "lucide.zip")
    else:
        import lucide
        zip_path = os.path.join(os.path.dirname(lucide.__file__), "lucide.zip")
    with ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if name.endswith(".svg"):
                _icon_svgs[name[:-4]] = zf.read(name).decode("utf-8")


def _render_icon(name: str, size: int = 20, color: str = "") -> str:
    _ensure_icons_loaded()
    svg_src = _icon_svgs.get(name)
    if svg_src is None:
        return ""
    svg = ElementTree.fromstring(svg_src)
    svg.attrib["width"] = svg.attrib["height"] = str(size)
    if color:
        for elem in svg.iter():
            val = elem.get("stroke")
            if val and val in ("currentColor", "currentcolor"):
                elem.set("stroke", color)
    string = ElementTree.tostring(svg, encoding="unicode")
    return string.replace(' xmlns="http://www.w3.org/2000/svg"', "", 1)


def lucide_icon(name: str, size: int = 20, color: str | None = None) -> QIcon:
    c = color if color is not None else _icon_color
    cache_key = f"{name}_{size}_{c}"
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]

    svg_str = _render_icon(name, size, c)
    if not svg_str:
        return QIcon()
    svg_bytes = svg_str.encode("utf-8")
    renderer = QSvgRenderer(QByteArray(svg_bytes))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    icon = QIcon(pixmap)
    _icon_cache[cache_key] = icon
    return icon
