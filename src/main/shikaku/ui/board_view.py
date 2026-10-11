import tkinter as tk
from typing import Optional, Tuple, List, Callable
from ..core.board import Board
from ..core.types import Rect
from .. import config as cfg
from .theme import round_rect, mix_colors


MIN_CELL = 14


class BoardView:
    """Рисует поле ПРЯМО на родительском Canvas — без вложенных Frame."""

    def __init__(self, canvas: tk.Canvas, board: Board,
                 on_move: Optional[Callable] = None,
                 on_win: Optional[Callable] = None,
                 on_error: Optional[Callable[[Rect], None]] = None,
                 on_remove: Optional[Callable[[Rect], None]] = None,
                 blind: bool = False):
        self.canvas = canvas
        self.board = board

        settings = None
        try:
            from ..storage.settings import Settings
            settings = Settings()
        except Exception:
            pass

        self._base_cell = cfg.CELL_SIZES.get(board.puzzle.size, 40)
        if settings is not None:
            scale_name = settings.get("cell_scale")
            scale = cfg.CELL_SCALE.get(scale_name, 1.0)
            self._base_cell = max(6, int(self._base_cell * scale))

        self.cell = self._base_cell

        self.on_move = on_move
        self.on_win = on_win
        self.on_error = on_error
        self.on_remove = on_remove
        self.blind = blind

        self.start: Optional[Tuple[int, int]] = None
        self.preview: Optional[Rect] = None

        self._flash_rects: List[Rect] = []
        self._flash_on = False
        self._flash_left = 0
        self._flash_job = None

        self._x0 = 0
        self._y0 = 0

        self.tag = "board"

        c = self.canvas
        c.bind("<Button-1>", self._on_down, add="+")
        c.bind("<B1-Motion>", self._on_drag, add="+")
        c.bind("<ButtonRelease-1>", self._on_up, add="+")
        c.bind("<Button-3>", self._on_right_click, add="+")
        c.bind("<Control-Button-1>", self._on_right_click, add="+")

        self.redraw()

    # ------------------------------------------------------------------
    def set_available_space(self, available_w: int, available_h: int):
        n = self.board.puzzle.size
        if n < 1:
            return

        max_by_w = available_w // n
        max_by_h = available_h // n

        new_cell = min(self._base_cell, max_by_w, max_by_h)
        new_cell = max(MIN_CELL, new_cell)

        if new_cell == self.cell:
            return
        self.cell = new_cell
        self.redraw()

    def set_position(self, x0: int, y0: int):
        self._x0 = x0
        self._y0 = y0
        self.redraw()

    def get_size(self) -> Tuple[int, int]:
        n = self.board.puzzle.size
        return n * self.cell, n * self.cell

    def reveal(self):
        """Проявляет цвета (для слепого режима — после победы)."""
        self.blind = False
        self.redraw()

    # ------------------------------------------------------------------
    def _in_field(self, x: int, y: int) -> bool:
        n = self.board.puzzle.size
        x_local = x - self._x0
        y_local = y - self._y0
        return 0 <= x_local < n * self.cell and 0 <= y_local < n * self.cell

    def _canvas_to_cell(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        if not self._in_field(x, y):
            return None
        x_local = x - self._x0
        y_local = y - self._y0
        c = int(x_local // self.cell)
        r = int(y_local // self.cell)
        n = self.board.puzzle.size
        if 0 <= r < n and 0 <= c < n:
            return r, c
        return None

    # ------------------------------------------------------------------
    def _on_down(self, event):
        if self.board.won:
            return
        cell = self._canvas_to_cell(event.x, event.y)
        if cell:
            self.start = cell
            self.preview = None

    def _on_drag(self, event):
        if not self.start:
            return
        cell = self._canvas_to_cell(event.x, event.y)
        if cell:
            self.preview = self._rect_between(self.start, cell)
            self.redraw()

    def _on_up(self, event):
        if not self.start:
            return
        cell = self._canvas_to_cell(event.x, event.y)
        if cell:
            rect = self._rect_between(self.start, cell)
            self.board.add_rect(rect)
            if not self.board.is_rect_valid(rect) and self.on_error:
                self.on_error(rect)
            if self.on_move:
                self.on_move()
            if self.board.won and self.on_win:
                self.on_win()
        self.start = None
        self.preview = None
        self.redraw()

    def _on_right_click(self, event):
        if self.board.won:
            return
        cell = self._canvas_to_cell(event.x, event.y)
        if not cell:
            return
        r, c = cell
        removed = self.board.remove_rect_at(r, c)
        if removed is not None:
            if self.on_remove:
                self.on_remove(removed)
            if self.on_move:
                self.on_move()
            self.redraw()

    def _rect_between(self, a, b) -> Rect:
        r1, c1 = a
        r2, c2 = b
        return Rect(min(r1, r2), min(c1, c2),
                    abs(r1 - r2) + 1, abs(c1 - c2) + 1)

    # ------------------------------------------------------------------
    def flash_invalid(self, times: int = None):
        if times is None:
            times = cfg.FLASH_TIMES
        self._flash_rects = [r for r in self.board.rects
                             if not self.board.is_rect_valid(r)]
        if not self._flash_rects:
            return
        self._flash_left = times * 2
        self._flash_on = True
        self._do_flash()

    def _do_flash(self):
        if self._flash_left <= 0:
            self._flash_rects = []
            self._flash_on = False
            self.redraw()
            return
        self._flash_on = not self._flash_on
        self._flash_left -= 1
        self.redraw()
        self._flash_job = self.canvas.after(cfg.FLASH_INTERVAL, self._do_flash)

    def stop_flash(self):
        if self._flash_job:
            try:
                self.canvas.after_cancel(self._flash_job)
            except tk.TclError:
                pass
            self._flash_job = None

    # ------------------------------------------------------------------
    def redraw(self):
        c = self.canvas
        c.delete(self.tag)

        n = self.board.puzzle.size
        C = self.cell
        x0 = self._x0
        y0 = self._y0
        pad = max(2, C // 14)
        radius = max(4, C // 6)

        # 1. Прямоугольники
        flash_set = set(id(r) for r in self._flash_rects) if self._flash_on else set()

        for rect in self.board.rects:
            valid = self.board.is_rect_valid(rect)
            x1 = x0 + rect.col * C
            y1 = y0 + rect.row * C
            x2 = x0 + (rect.col + rect.width) * C
            y2 = y0 + (rect.row + rect.height) * C

            inset = max(2, C // 14)
            rx1, ry1 = x1 + inset, y1 + inset
            rx2, ry2 = x2 - inset, y2 - inset
            r_rad = max(4, C // 6)

            if id(rect) in flash_set:
                round_rect(c, rx1, ry1, rx2, ry2, r_rad,
                           fill="#ef5b7e", outline="#ff8aa3", width=2,
                           tags=(self.tag,))
                continue

            if self.blind:
                # слепой режим — только контур
                if valid:
                    stroke = self.board.stroke_of(rect)
                else:
                    stroke = cfg.C("COLOR_RECT_INVALID_STROKE")
                # для слепого используем светлый акцент
                if cfg.current_theme() == "dark":
                    blind_stroke = "#e8e0f0"
                else:
                    blind_stroke = "#2a1e48"
                round_rect(c, rx1, ry1, rx2, ry2, r_rad,
                           fill="", outline=blind_stroke, width=3,
                           tags=(self.tag,))
                continue

            if valid:
                fill = self.board.color_of(rect)
                stroke = self.board.stroke_of(rect)
                round_rect(c, rx1, ry1, rx2, ry2, r_rad,
                           fill=fill, outline=stroke, width=2,
                           tags=(self.tag,))
            else:
                round_rect(c, rx1, ry1, rx2, ry2, r_rad,
                           fill=cfg.C("COLOR_RECT_INVALID"),
                           outline=cfg.C("COLOR_RECT_INVALID_STROKE"),
                           width=2,
                           tags=(self.tag,))

        # 2. Превью
        if self.preview:
            p = self.preview
            x1 = x0 + p.col * C
            y1 = y0 + p.row * C
            x2 = x0 + (p.col + p.width) * C
            y2 = y0 + (p.row + p.height) * C
            inset = max(2, C // 14)
            rx1, ry1 = x1 + inset, y1 + inset
            rx2, ry2 = x2 - inset, y2 - inset
            r_rad = max(4, C // 6)
            round_rect(c, rx1, ry1, rx2, ry2, r_rad,
                       fill="", outline=cfg.C("COLOR_PREVIEW"), width=3,
                       tags=(self.tag,))

        # 3. Сетка
        grid_color = cfg.C("COLOR_GRID_NEON")
        for i in range(n + 1):
            x = x0 + i * C
            y = y0 + i * C
            c.create_line(x, y0, x, y0 + n * C,
                          fill=grid_color, width=3 if C >= 20 else 2,
                          tags=(self.tag,))
            c.create_line(x0, y, x0 + n * C, y,
                          fill=grid_color, width=3 if C >= 20 else 2,
                          tags=(self.tag,))

        # 4. Цифры
        font_size = max(7, int(C * 0.42))

        for r, cc, v in self.board.puzzle.clues():
            cx = x0 + cc * C + C / 2
            cy = y0 + r * C + C / 2
            c.create_text(cx + 2, cy + 2, text=str(v),
                          font=(cfg.FONT_CLUE, font_size, "bold"),
                          fill="#0c0e14",
                          tags=(self.tag,))
            c.create_text(cx, cy, text=str(v),
                          font=(cfg.FONT_CLUE, font_size, "bold"),
                          fill="#ffffff",
                          tags=(self.tag,))