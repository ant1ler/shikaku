import json
import os
import time
from datetime import date
from typing import Optional, List


class Daily:
    """Хранит результаты ежедневного вызова и стрик.

    При каждом создании экземпляра данные читаются с диска заново —
    это гарантирует, что изменения, сделанные в другом экземпляре,
    видны здесь.
    """

    def __init__(self, path: str = "shikaku_daily.json"):
        self.path = path
        self.data = self._load()

    def _load(self) -> dict:
        if not os.path.exists(self.path):
            return {"streak": 0, "last_played_date": None, "results": {}}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                d = json.load(f)
            d.setdefault("streak", 0)
            d.setdefault("last_played_date", None)
            d.setdefault("results", {})
            return d
        except (json.JSONDecodeError, OSError):
            return {"streak": 0, "last_played_date": None, "results": {}}

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def reload(self) -> None:
        """Перечитывает данные с диска. Нужно вызывать после submit
        в другом экземпляре."""
        self.data = self._load()

    # ---------- дата ----------
    @staticmethod
    def today() -> str:
        return date.today().isoformat()

    # ---------- seed ----------
    @staticmethod
    def seed_for(size: int, day: str = None) -> int:
        if day is None:
            day = Daily.today()
        base = int(day.replace("-", ""))
        return base * 1000 + size

    # ---------- результаты ----------
    def result_for(self, size: int, day: str = None) -> Optional[float]:
        if day is None:
            day = self.today()
        day_results = self.data["results"].get(day, {})
        return day_results.get(str(size))

    def is_done(self, size: int, day: str = None) -> bool:
        return self.result_for(size, day) is not None

    def submit(self, size: int, seconds: float, day: str = None) -> bool:
        """Сохраняет результат, обновляет стрик. Возвращает True, если
        это первое прохождение размера сегодня."""
        if day is None:
            day = self.today()

        # перечитываем перед записью — на случай, если другой экземпляр
        # уже что-то записал
        self.reload()

        day_results = self.data["results"].setdefault(day, {})
        key = str(size)

        is_first = key not in day_results
        if is_first or seconds < day_results[key]:
            day_results[key] = seconds

        if is_first and self.data["last_played_date"] != day:
            prev = self.data["last_played_date"]
            if prev is None:
                self.data["streak"] = 1
            else:
                try:
                    from datetime import datetime
                    d_prev = datetime.fromisoformat(prev).date()
                    d_today = datetime.fromisoformat(day).date()
                    if (d_today - d_prev).days == 1:
                        self.data["streak"] += 1
                    elif (d_today - d_prev).days > 1:
                        self.data["streak"] = 1
                except Exception:
                    self.data["streak"] = 1
            self.data["last_played_date"] = day

        self._save()
        return is_first

    # ---------- стрик ----------
    def streak(self) -> int:
        from datetime import datetime
        prev = self.data.get("last_played_date")
        if prev is None:
            return 0
        try:
            d_prev = datetime.fromisoformat(prev).date()
            d_today = datetime.fromisoformat(self.today()).date()
            if (d_today - d_prev).days > 1:
                return 0
        except Exception:
            return 0
        return self.data.get("streak", 0)

    def reset(self) -> None:
        self.data = {"streak": 0, "last_played_date": None, "results": {}}
        self._save()