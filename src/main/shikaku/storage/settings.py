import json
import os
from typing import Dict, Any


DEFAULTS = {
    "theme": "dark",           # "dark" | "light"
    "cell_scale": "normal",    # "compact" | "normal" | "large"
    "animations": True,
    "autosave": True,
    "sound": True,
}


class Settings:
    """Хранит настройки в settings.json рядом с игрой."""

    def __init__(self, path: str = "settings.json"):
        self.path = path
        self.data: Dict[str, Any] = dict(DEFAULTS)
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            for k, v in loaded.items():
                if k in DEFAULTS:
                    self.data[k] = v
        except (json.JSONDecodeError, OSError):
            pass

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    # --- доступ ---
    def get(self, key: str):
        return self.data.get(key, DEFAULTS.get(key))

    def set(self, key: str, value):
        if key in DEFAULTS:
            self.data[key] = value

    def reset(self):
        self.data = dict(DEFAULTS)
        self.save()