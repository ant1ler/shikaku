import tkinter as tk
from .. import config as cfg
from .theme import FlatButton, round_rect, BgCanvas


class RulesScreen(tk.Frame):
    def __init__(self, master, on_close):
        super().__init__(master, bg=cfg.C("COLOR_BG"))
        self.on_close = on_close

        self.bg = BgCanvas(self, context="rules")
        self.bg.pack(fill="both", expand=True)

        self._refresh_job = None
        self._last_size = (0, 0)

        self.bg.bind("<Configure>", self._on_configure, add="+")
        self.after(50, self._refresh)

    # ------------------------------------------------------------------
    def _on_configure(self, event=None):
        w = self.bg.winfo_width()
        h = self.bg.winfo_height()
        if (w, h) == self._last_size:
            return
        if self._refresh_job:
            try:
                self.after_cancel(self._refresh_job)
            except tk.TclError:
                pass
        self._refresh_job = self.after(120, self._refresh)

    def _refresh(self):
        w = self.bg.winfo_width()
        h = self.bg.winfo_height()
        if w < 100 or h < 100:
            self.after(50, self._refresh)
            return

        self._last_size = (w, h)

        self.bg.delete("ui")
        self.bg.delete("rule")
        self.bg.delete("example")
        self.bg.delete("ui_bottom")
        self.bg.delete("ui_bottom_btn")

        self._draw_header(w)
        self._draw_rules(w, h)
        self._draw_example(w, h)
        self._draw_bottom(w, h)

    # ------------------------------------------------------------------
    def _draw_header(self, w):
        self.bg.create_rectangle(0, 0, w, 3,
                                 fill=cfg.C("COLOR_ACCENT"),
                                 outline="", tags="ui")

        self.bg.create_text(40, 30,
                            text="Как играть",
                            font=("Schueler SuperXP", 38),
                            fill=cfg.C("COLOR_TEXT"),
                            anchor="nw", tags="ui")

        self.bg.create_text(40, 100,
                            text="Правила шикаку — простые, но требуют логики",
                            font=("Jost* Medium", 13),
                            fill=cfg.C("COLOR_TEXT_DIM"),
                            anchor="nw", tags="ui")

    # ------------------------------------------------------------------
    def _draw_rules(self, w, h):
        rules = [
            ("Цель",
             "Разрезать всё поле на прямоугольники и квадраты так, "
             "чтобы каждый участок содержал ровно одну цифру."),
            ("Площадь",
             "Площадь прямоугольника должна точно совпадать с этой цифрой. "
             "Число 6 → прямоугольник 2×3 или 1×6."),
            ("Пересечения",
             "Прямоугольники не могут пересекаться и не могут оставлять "
             "пустых клеток. Всё поле должно быть покрыто."),
            ("Управление",
             "Зажми ЛКМ в одной клетке, потяни до противоположного угла "
             "и отпусти — появится прямоугольник. ПКМ — удалить."),
            ("Цвета",
             "Каждый прямоугольник получает свой цвет. Красный — ошибка: "
             "внутри не одна цифра или площадь не совпадает."),
        ]

        start_x = 40
        start_y = 170
        row_h = 110
        badge_size = 42
        text_x = start_x + badge_size + 20

        text_wrap = int(w * 0.55)

        for i, (title, text) in enumerate(rules, 1):
            y = start_y + (i - 1) * row_h

            round_rect(self.bg,
                       start_x, y,
                       start_x + badge_size, y + badge_size,
                       12,
                       fill=cfg.C("COLOR_ACCENT"), outline="",
                       tags="rule")
            self.bg.create_text(start_x + badge_size / 2,
                                y + badge_size / 2,
                                text=str(i),
                                font=("Jost* Semi", 18, "bold"),
                                fill="#ffffff",
                                anchor="center", tags="rule")

            self.bg.create_text(text_x, y - 2,
                                text=title,
                                font=("Jost* Semi", 16, "bold"),
                                fill=cfg.C("COLOR_TEXT"),
                                anchor="nw", tags="rule")

            self.bg.create_text(text_x, y + 28,
                                text=text,
                                font=("Jost*", 13),
                                fill=cfg.C("COLOR_TEXT_DIM"),
                                anchor="nw", justify="left",
                                width=text_wrap,
                                tags="rule")

    # ------------------------------------------------------------------
    def _draw_example(self, w, h):
        ex_w = 400
        ex_x = w - 40 - ex_w
        ex_y = 170

        self.bg.create_text(ex_x, ex_y,
                            text="Пример",
                            font=("Jost* Semi", 18, "bold"),
                            fill=cfg.C("COLOR_TEXT"),
                            anchor="nw", tags="example")

        example_y = ex_y + 40
        cell = 130
        pad = 4
        radius = 14

        rects = [
            (0, 0, 2, 1, "2", "#5e7ce2", "#4259a8"),
            (0, 1, 1, 2, "2", "#57d68a", "#3fa066"),
            (1, 1, 1, 2, "4", "#ef9f5b", "#b3713c"),
        ]

        self.bg.create_rectangle(
            ex_x, example_y,
            ex_x + 3 * cell, example_y + 2 * cell,
            fill=cfg.C("COLOR_CELL"), outline="", tags="example"
        )

        for i in range(4):
            self.bg.create_line(
                ex_x + i * cell, example_y,
                ex_x + i * cell, example_y + 2 * cell,
                fill=cfg.C("COLOR_GRID_NEON"), width=2, tags="example"
            )
        for i in range(3):
            self.bg.create_line(
                ex_x, example_y + i * cell,
                ex_x + 3 * cell, example_y + i * cell,
                fill=cfg.C("COLOR_GRID_NEON"), width=2, tags="example"
            )

        for (r, c, hgt, wdt, num, fill, stroke) in rects:
            x1 = ex_x + c * cell + pad
            y1 = example_y + r * cell + pad
            x2 = ex_x + (c + wdt) * cell - pad
            y2 = example_y + (r + hgt) * cell - pad
            round_rect(self.bg, x1, y1, x2, y2, radius,
                       fill=fill, outline=stroke, width=3,
                       tags="example")

        positions = [
            (0, 0, 2, 1, "2"),
            (0, 1, 1, 2, "2"),
            (1, 1, 1, 2, "4"),
        ]
        for (r, c, hgt, wdt, num) in positions:
            cx = ex_x + (c + wdt / 2) * cell
            cy = example_y + (r + hgt / 2) * cell
            self.bg.create_text(cx + 2, cy + 2, text=num,
                                font=("Jost* Semi", 32, "bold"),
                                fill="#0c0e14", tags="example")
            self.bg.create_text(cx, cy, text=num,
                                font=("Jost* Semi", 32, "bold"),
                                fill="#ffffff", tags="example")

        self.bg.create_text(ex_x, example_y + 2 * cell + 20,
                            text="Число 6 — площадь 2×3,\nчисло 2 — площадь 1×2",
                            font=("Jost* Medium", 13),
                            fill=cfg.C("COLOR_TEXT_DIM"),
                            anchor="nw", justify="left",
                            tags="example")

    # ------------------------------------------------------------------
    def _draw_bottom(self, w, h):
        panel_h = 70
        panel_y1 = h - panel_h

        self.bg.create_rectangle(0, panel_y1, w, h,
                                 fill=cfg.C("COLOR_PANEL"),
                                 outline="", tags="ui_bottom")
        self.bg.create_line(0, panel_y1, w, panel_y1,
                            fill=cfg.C("COLOR_PANEL_EDGE"),
                            width=1, tags="ui_bottom")

        btn = FlatButton(self.bg, "Понятно",
                         command=self.on_close,
                         width=180, height=48,
                         accent=True,
                         font=("Jost* Medium", 13))
        self.bg.create_window(w - 40, panel_y1 + panel_h / 2,
                              window=btn, anchor="e", tags="ui_bottom_btn")