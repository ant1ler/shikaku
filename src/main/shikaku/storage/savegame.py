import json
import os
import time
from typing import Optional, Dict, Any
from ..core.board import Board
from ..config import SAVE_FILE


class SaveGame:
    """Сохраняет состояние партии: сетка, прямоугольники, режим, таймер."""

    def __init__(self, path: str = SAVE_FILE):
        self.path = path

    def save(self, board: Board, meta: Dict[str, Any]) -> None:
        """meta содержит: mode, elapsed, cascade_level, cascade_elapsed_before,
        time_used, hints_left, size."""
        data = board.to_dict()
        data["_meta"] = meta
        data["_saved_at"] = time.strftime("%Y-%m-%d %H:%M")
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def load(self) -> Optional[Dict[str, Any]]:
        """Возвращает {'board': Board, 'meta': dict} или None."""
        if not os.path.exists(self.path):
            return None
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            meta = data.pop("_meta", {})
            data.pop("_saved_at", None)
            board = Board.from_dict(data)
            return {"board": board, "meta": meta}
        except (json.JSONDecodeError, KeyError, OSError):
            return None

    def has_save(self) -> bool:
        return os.path.exists(self.path)

    def delete(self) -> None:
        if os.path.exists(self.path):
            try:
                os.remove(self.path)
            except OSError:
                pass

    def saved_at(self) -> Optional[str]:
        if not os.path.exists(self.path):
            return None
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("_saved_at")
        except (json.JSONDecodeError, OSError):
            return None