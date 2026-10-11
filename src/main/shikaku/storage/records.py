import json
import os
import time
from typing import Optional, List, Dict
from ..config import RECORDS_FILE


class Records:
    """Хранит лучшее время для каждого размера поля и режимов.

    Ключи:
      • "6"                        — обычный размер 6×6
      • "6_cascade"                — серия из 5 уровней 6×6
      • "6_timed"                  — timed 6×6
      • "3_cascade_growing"        — растущая серия (ключ хранится на стартовом размере)
    """

    def __init__(self, path: str = RECORDS_FILE):
        self.path = path
        self.data: Dict[str, dict] = self._load()

    def _load(self) -> Dict[str, dict]:
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def _key(self, size: int, cascade: bool = False,
             timed: bool = False, cascade_growing: bool = False) -> str:
        if cascade_growing:
            from ..config import CASCADE_GROWING_SUFFIX
            return f"{size}_{CASCADE_GROWING_SUFFIX}"
        if timed:
            from ..config import TIMED_RECORD_SUFFIX
            return f"{size}_{TIMED_RECORD_SUFFIX}"
        if cascade:
            from ..config import CASCADE_RECORD_SUFFIX
            return f"{size}_{CASCADE_RECORD_SUFFIX}"
        return str(size)

    def best(self, size: int, cascade: bool = False,
             timed: bool = False, cascade_growing: bool = False) -> Optional[float]:
        entry = self.data.get(self._key(size, cascade, timed, cascade_growing))
        return entry["time"] if entry else None

    def best_date(self, size: int, cascade: bool = False,
                  timed: bool = False, cascade_growing: bool = False) -> Optional[str]:
        entry = self.data.get(self._key(size, cascade, timed, cascade_growing))
        return entry["date"] if entry else None

    def submit(self, size: int, seconds: float, cascade: bool = False,
               timed: bool = False, cascade_growing: bool = False) -> bool:
        """Для обычных режимов меньше = лучше. Для timed — больше = лучше."""
        key = self._key(size, cascade, timed, cascade_growing)
        current = self.data.get(key)

        if current is None:
            is_record = True
        elif timed:
            is_record = seconds > current["time"]
        else:
            is_record = seconds < current["time"]

        if is_record:
            self.data[key] = {
                "time": seconds,
                "date": time.strftime("%Y-%m-%d %H:%M"),
            }
            self._save()
            return True
        return False

    def all_records(self) -> List[tuple]:
        result = []
        for k, v in self.data.items():
            result.append((k, v["time"], v["date"]))
        return result

    def reset(self, size: Optional[int] = None) -> None:
        if size is None:
            self.data = {}
        else:
            from ..config import (CASCADE_RECORD_SUFFIX, TIMED_RECORD_SUFFIX,
                                   CASCADE_GROWING_SUFFIX)
            self.data.pop(str(size), None)
            self.data.pop(f"{size}_{CASCADE_RECORD_SUFFIX}", None)
            self.data.pop(f"{size}_{TIMED_RECORD_SUFFIX}", None)
            self.data.pop(f"{size}_{CASCADE_GROWING_SUFFIX}", None)
        self._save()