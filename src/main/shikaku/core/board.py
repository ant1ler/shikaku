from typing import List, Dict, Tuple, Optional
from .types import Puzzle, Rect
from .validator import Validator
from .. import config as cfg


class Board:
    """Игровое состояние: прямоугольники, цвета, undo, победа, счётчик ходов."""

    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.validator = Validator(puzzle)
        self.rects: List[Rect] = []
        self._color_idx: Dict[int, int] = {}
        self._color_counter = 0
        self._history: List[Tuple[List[Rect], Dict[int, int], int]] = []
        self.won = False
        self.moves = 0

    # --- цвета ---
    def _palette(self):
        return cfg.C("RECT_PALETTE")

    def _stroke_palette(self):
        return cfg.C("RECT_STROKE_PALETTE")

    def _next_idx(self) -> int:
        idx = self._color_counter % len(self._palette())
        self._color_counter += 1
        return idx

    def color_of(self, rect: Rect) -> str:
        idx = self._color_idx.get(id(rect), 0)
        palette = self._palette()
        return palette[idx % len(palette)]

    def stroke_of(self, rect: Rect) -> str:
        idx = self._color_idx.get(id(rect), 0)
        palette = self._stroke_palette()
        return palette[idx % len(palette)]

    def _assign(self, rect: Rect) -> None:
        self._color_idx[id(rect)] = self._next_idx()

    # --- действия ---
    def add_rect(self, rect: Rect) -> None:
        self._push_history()
        kept: List[Rect] = []
        for r in self.rects:
            if r.overlaps(rect):
                self._color_idx.pop(id(r), None)
            else:
                kept.append(r)
        self.rects = kept
        self.rects.append(rect)
        self._assign(rect)
        self.moves += 1
        self._check_win()

    def remove_rect_at(self, row: int, col: int) -> Optional[Rect]:
        """Удаляет прямоугольник, покрывающий клетку (row, col)."""
        for r in list(self.rects):
            if (r.row <= row < r.row + r.height
                    and r.col <= col < r.col + r.width):
                self._push_history()
                self.rects.remove(r)
                self._color_idx.pop(id(r), None)
                self._check_win()
                return r
        return None

    def clear(self) -> None:
        self._push_history()
        self.rects = []
        self._color_idx = {}
        self.won = False

    def undo(self) -> bool:
        if not self._history:
            return False
        rects, colors, counter = self._history.pop()
        self.rects = list(rects)
        self._color_idx = dict(colors)
        self._color_counter = counter
        self.won = self.validator.is_solved(self.rects)
        return True

    # --- подсказки ---
    def hint_from(self) -> Optional[Rect]:
        for correct in self.puzzle.solution:
            if any(r == correct for r in self.rects):
                continue
            if self._is_covered(correct):
                continue
            self.add_rect(correct)
            return correct
        return None

    def _is_covered(self, rect: Rect) -> bool:
        for r, c in rect.cells():
            if self.cell_is_covered(r, c) is None:
                return False
        return True

    def cell_is_covered(self, row: int, col: int) -> Optional[Rect]:
        for r in self.rects:
            if r.row <= row < r.row + r.height and r.col <= col < r.col + r.width:
                return r
        return None

    # --- служебное ---
    def _push_history(self) -> None:
        self._history.append((list(self.rects),
                              dict(self._color_idx),
                              self._color_counter))
        if len(self._history) > cfg.HISTORY_LIMIT:
            self._history.pop(0)

    def _check_win(self) -> None:
        self.won = self.validator.is_solved(self.rects)

    def is_rect_valid(self, rect: Rect) -> bool:
        return self.validator.is_rect_valid(rect)

    # --- сериализация ---
    def to_dict(self):
        return {
            "puzzle": self.puzzle.to_dict(),
            "rects": [r.to_dict() for r in self.rects],
            "color_idx": [self._color_idx.get(id(r), 0) for r in self.rects],
            "color_counter": self._color_counter,
            "moves": self.moves,
        }

    @classmethod
    def from_dict(cls, d):
        board = cls(Puzzle.from_dict(d["puzzle"]))
        board.rects = [Rect.from_dict(r) for r in d["rects"]]
        for rect, idx in zip(board.rects, d.get("color_idx", [])):
            board._color_idx[id(rect)] = idx
        board._color_counter = d.get("color_counter", len(board.rects))
        board.moves = d.get("moves", len(board.rects))
        board.won = board.validator.is_solved(board.rects)
        return board