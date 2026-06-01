import json
import os

from PyQt6.QtCore import QLocale


class LanguageManager:
    KHMER_FONT_FAMILIES = [
        "Noto Sans Khmer",
        "Khmer OS",
        "Khmer OS System",
        "Khmer OS Battambang",
        "Khmer OS Siemreap",
        "Leelawadee UI",
        "DaunPenh",
        "MoolBoran",
        "Segoe UI",
        "sans-serif",
    ]

    def __init__(self, lang_dir: str):
        self._lang_dir = lang_dir
        self._strings: dict[str, str] = {}
        self._current = "en"
        self._available: list[str] = []
        self._scan_available()
        self.set_language(self.system_language())

    def _scan_available(self) -> None:
        if not os.path.isdir(self._lang_dir):
            self._available = ["en"]
            return
        for f in sorted(os.listdir(self._lang_dir)):
            if f.endswith(".json"):
                self._available.append(f.replace(".json", ""))

    @property
    def available_languages(self) -> list[str]:
        return list(self._available)

    @property
    def current(self) -> str:
        return self._current

    def set_language(self, lang: str) -> None:
        if lang not in self._available:
            lang = "en"
        path = os.path.join(self._lang_dir, f"{lang}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self._strings = json.load(f)
        else:
            self._strings = {}
        self._current = lang

    def get(self, key: str, default: str = "") -> str:
        return self._strings.get(key, default)

    def tr(self, key: str, default: str = "") -> str:
        return self.get(key, default)

    def is_khmer(self) -> bool:
        return self._current == "km"

    def font_families(self) -> list[str]:
        if self.is_khmer():
            return ["AgentosUI", "Noto Sans Khmer", *self.KHMER_FONT_FAMILIES]
        return ["AgentosUI", "Segoe UI Variable Display", "Segoe UI", "sans-serif"]

    def system_language(self) -> str:
        locale = QLocale.system()
        lang = locale.language()
        code = QLocale.languageToCode(lang)
        if code in self._available:
            return code
        return "en"
