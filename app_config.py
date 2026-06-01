import json
import os

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_CONFIG = {
    "theme": "light",
    "language": "km",
    "recent_files": [],
}


def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)


def load_config():
    ensure_config_dir()
    base = dict(DEFAULT_CONFIG)
    if not os.path.exists(CONFIG_FILE):
        return base
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return {**base, **json.load(f)}
    except Exception:
        return base


def save_config(config):
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save config: {e}")
