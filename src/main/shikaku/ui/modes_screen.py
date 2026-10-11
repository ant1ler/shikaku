import tkinter as tk
from .. import config as cfg
from .theme import FlatButton, round_rect, BgCanvas


class ModesScreen(tk.Frame):
    """Экран с описаниями всех игровых режимов."""

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
        self.bg.delete("mode")
        self.bg.delete("ui_bottom")
        self.bg.delete("ui_bottom_btn")

        self._draw_header(w)
        self._draw_modes(w, h)
        self._draw_bottom(w, h)

    # ------------------------------------------------------------------
    def _draw_header(self, w):
        self.bg.create_rectangle(0, 0, w, 3,
                                 fill=cfg.C("COLOR_ACCENT"),
                                 outline="", tags="ui")

        self.bg.create_text(40, 30,
                            text="Режимы игры",
                            font=("Schueler SuperXP", 38),
                            fill=cfg.C("COLOR_TEXT"),
                            anchor="nw", tags="ui")

        self.bg.create_text(40, 100,
                            text="Шесть способов играть в шикаку",
                            font=("Jost* Medium", 13),
                            fill=cfg.C("COLOR_TEXT_DIM"),
                            anchor="nw", tags="ui")

    # ------------------------------------------------------------------
    def _draw_modes(self, w, h):
        modes = [
            ("🎯", "Обычная игра", cfg.MODE_DESCRIPTIONS["normal"],
             cfg.C("COLOR_ACCENT")),
            ("⚡", "Серия из 5", cfg.MODE_DESCRIPTIONS["cascade"],
             cfg.C("COLOR_ACCENT2")),
            ("📈", "Растущая серия", cfg.MODE_DESCRIPTIONS["cascade_growing"],
             cfg.C("COLOR_ACCENT")),
            ("⏱", "На время", cfg.MODE_DESCRIPTIONS["timed"],
             cfg.C("COLOR_DANGER")),
            ("👁", "Слепой режим", cfg.MODE_DESCRIPTIONS["blind"],
             cfg.C("COLOR_SUCCESS")),
            ("📅", "Ежедневный вызов", cfg.MODE_DESCRIPTIONS["daily"],
             cfg.C("COLOR_ACCENT2")),
        ]

        start_x = 40
        start_y = 170
        block_w = w - 80
        text_x = start_x + 60

        y = start_y
        for icon, title, desc, color in modes:
            round_rect(self.bg,
                       start_x, y + 6,
                       start_x + 4, y + 46,
                       2,
                       fill=color, outline="",
                       tags="mode")

            self.bg.create_text(start_x + 30, y + 26,
                                text=icon,
                                font=("Segoe UI Emoji", 22),
                                fill=color,
                                anchor="center", tags="mode")

            self.bg.create_text(text_x, y + 4,
                                text=title,
                                font=("Jost* Semi", 18, "bold"),
                                fill=color,
                                anchor="nw", tags="mode")

            item = self.bg.create_text(text_x, y + 34,
                                       text=desc,
                                       font=("Jost*", 12),
                                       fill=cfg.C("COLOR_TEXT_DIM"),
                                       anchor="nw", justify="left",
                                       width=block_w - 60,
                                       tags="mode")

            bbox = self.bg.bbox(item)
            text_h = (bbox[3] - bbox[1]) if bbox else 40

            y += max(90, 40 + text_h + 30)

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