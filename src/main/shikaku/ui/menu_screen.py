import tkinter as tk
from tkinter import messagebox
from .. import config as cfg
from ..storage.records import Records
from ..storage.daily import Daily
from .theme import (FlatButton, format_time, BgCanvas, round_rect, mix_colors)


CARD_COLORS = {
    3:  "#ff9fd0",
    6:  "#7fbfff",
    9:  "#7fffc0",
    15: "#ffd07f",
    25: "#b89fff",
    30: "#9fd0ff",
}


class MenuScreen(tk.Frame):
    def __init__(self, master, on_start, on_continue, on_show_rules,
                 has_save: bool, on_rebuild=None,
                 on_cascade=None, on_timed=None, on_daily=None,
                 on_settings=None, on_modes=None, on_blind=None,
                 on_cascade_growing=None):
        super().__init__(master, bg=cfg.C("COLOR_BG"))
        self.on_start = on_start
        self.on_continue = on_continue
        self.on_show_rules = on_show_rules
        self.on_rebuild = on_rebuild
        self.on_cascade = on_cascade or on_start
        self.on_timed = on_timed or on_start
        self.on_daily = on_daily or on_start
        self.on_settings = on_settings or (lambda: None)
        self.on_modes = on_modes or (lambda: None)
        self.on_blind = on_blind or on_start
        self.on_cascade_growing = on_cascade_growing or on_start
        self.records = Records()
        self.daily = Daily()

        self.bg = BgCanvas(self, context="menu")
        self.bg.pack(fill="both", expand=True)

        self._card_w = 220
        self._card_h = 170
        self._card_gap_x = 30
        self._card_gap_y = 30

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
        self.bg.delete("card")
        self.bg.delete("card_bg")
        self.bg.delete("card_btn")
        self.bg.delete("ui_bottom")
        self.bg.delete("ui_bottom_btn")

        self._draw_header(w)
        self._draw_cards(w, h)
        self._draw_bottom(w, h)

    # ------------------------------------------------------------------
    def _draw_header(self, w):
        self.bg.create_text(40, 40, text=cfg.APP_NAME,
                            font=cfg.FONT_LOGO,
                            fill=cfg.C("COLOR_TEXT"),
                            anchor="nw", tags="ui")
        self.bg.create_text(40, 112,
                            text="Разрезай · Считай · Побеждай",
                            font=("Jost* Medium", 12),
                            fill=cfg.C("COLOR_ACCENT"),
                            anchor="nw", tags="ui")
        self.bg.create_text(w - 40, 40,
                            text=f"версия {cfg.APP_VERSION}",
                            font=cfg.FONT_SMALL,
                            fill=cfg.C("COLOR_TEXT_DIM"),
                            anchor="ne", tags="ui")

        streak = self.daily.streak()
        if streak > 0:
            if streak % 10 == 1 and streak % 100 != 11:
                day_word = "день"
            elif streak % 10 in (2, 3, 4) and streak % 100 not in (12, 13, 14):
                day_word = "дня"
            else:
                day_word = "дней"

            self.bg.create_text(w - 40, 68,
                                text=f"🔥  Серия: {streak} {day_word}",
                                font=("Jost* Semi", 14),
                                fill=cfg.C("COLOR_SUCCESS"),
                                anchor="ne", tags="ui")

        self.bg.create_text(40, 190,
                            text="Выберите размер поля",
                            font=cfg.FONT_HEADLINE,
                            fill=cfg.C("COLOR_TEXT"),
                            anchor="nw", tags="ui")

    # ------------------------------------------------------------------
    def _draw_cards(self, w, h):
        sizes = list(cfg.BOARD_SIZES)
        card_w = self._card_w
        card_h = self._card_h
        gap_x = self._card_gap_x
        gap_y = self._card_gap_y

        cx = w / 2
        cy = h / 2 + 30

        grid_w = 3 * card_w + 2 * gap_x
        grid_h = 2 * card_h + gap_y

        start_x = cx - grid_w / 2
        start_y = cy - grid_h / 2

        for i, size in enumerate(sizes):
            row = i // 3
            col = i % 3

            x1 = start_x + col * (card_w + gap_x)
            y1 = start_y + row * (card_h + gap_y)
            x2 = x1 + card_w
            y2 = y1 + card_h

            self._draw_one_card(size, x1, y1, x2, y2)

    def _draw_one_card(self, size, x1, y1, x2, y2):
        color = CARD_COLORS.get(size, cfg.C("COLOR_ACCENT"))
        bg_color = cfg.C("COLOR_BG")
        fill_color = mix_colors(color, bg_color, 0.84)
        radius = 22
        cx = (x1 + x2) / 2

        # подложка карточки — клик по ней = обычная игра
        bg_tag = f"card_bg_{size}"
        round_rect(self.bg, x1, y1, x2, y2, radius,
                   fill=fill_color, outline=color, width=2,
                   tags=(bg_tag, "card_bg"))

        # размер
        self.bg.create_text(cx, y1 + 26,
                            text=f"{size} × {size}",
                            font=("Jost* Semi", 22, "bold"),
                            fill=cfg.C("COLOR_TEXT"),
                            tags=(bg_tag, "card_bg"))

        # рекорды
        best = self.records.best(size)
        best_cascade = self.records.best(size, cascade=True)
        best_timed = self.records.best(size, timed=True)

        y_rows = [y1 + 56, y1 + 80, y1 + 104]

        self._draw_stat_row(bg_tag, cx, y_rows[0], "🏆", best)
        self._draw_stat_row(bg_tag, cx, y_rows[1], "⚡", best_cascade)
        self._draw_stat_row(bg_tag, cx, y_rows[2], "⏱", best_timed)

        # кнопки режимов
        y_btn = y2 - 20
        self._draw_mode_button(size, cx - 66, y_btn, "⚡ Серия",
                               color, self.on_cascade)
        self._draw_mode_button(size, cx, y_btn, "⏱ Время",
                               cfg.C("COLOR_DANGER"), self.on_timed)
        self._draw_mode_button(size, cx + 66, y_btn, "👁 Слепой",
                               cfg.C("COLOR_ACCENT2"), self.on_blind)

        # клик по подложке = обычная игра
        self.bg.tag_bind(bg_tag, "<Button-1>",
                         lambda e, s=size: self.on_start(s))
        self.bg.tag_bind(bg_tag, "<Enter>",
                         lambda e: self.bg.configure(cursor="hand2"))
        self.bg.tag_bind(bg_tag, "<Leave>",
                         lambda e: self.bg.configure(cursor=""))

    def _draw_stat_row(self, bg_tag, cx, y, icon, value):
        text = format_time(value) if value is not None else "—"
        color = cfg.C("COLOR_TEXT") if value is not None else cfg.C("COLOR_TEXT_DIM")

        icon_x = cx - 26
        value_x = cx - 6

        self.bg.create_text(icon_x, y, text=icon,
                            font=("Segoe UI Emoji", 12),
                            fill=cfg.C("COLOR_TEXT_DIM"),
                            anchor="center", tags=(bg_tag, "card_bg"))
        self.bg.create_text(value_x, y, text=text,
                            font=("Jost* Medium", 12),
                            fill=color,
                            anchor="w", tags=(bg_tag, "card_bg"))

    def _draw_mode_button(self, size, cx, cy, text, color, on_click):
        btn_tag = f"card_btn_{size}_{text[:2]}"

        self.bg.create_text(cx, cy, text=text,
                            font=("Jost* Medium", 9),
                            fill=color,
                            anchor="center",
                            tags=(btn_tag, "card_btn"))

        def handler(event):
            on_click(size)
            return "break"

        self.bg.tag_bind(btn_tag, "<Button-1>", handler)
        self.bg.tag_bind(btn_tag, "<Enter>",
                         lambda e: self.bg.configure(cursor="hand2"))

    # ------------------------------------------------------------------
    def _draw_bottom(self, w, h):
        panel_h = 70
        panel_y1 = h - panel_h
        panel_y2 = h

        self.bg.create_rectangle(0, panel_y1, w, panel_y2,
                                 fill=cfg.C("COLOR_PANEL"),
                                 outline="", tags="ui_bottom")
        self.bg.create_line(0, panel_y1, w, panel_y1,
                            fill=cfg.C("COLOR_PANEL_EDGE"),
                            width=1, tags="ui_bottom")

        self._bottom_buttons = []
        big_font = ("Jost* Medium", 12)
        cy = panel_y1 + panel_h / 2

        btn_exit = FlatButton(self.bg, "Выход",
                              command=self.winfo_toplevel().destroy,
                              width=120, height=44, font=big_font)
        self.bg.create_window(w - 20, cy, window=btn_exit, anchor="e",
                              tags="ui_bottom_btn")
        self._bottom_buttons.append(btn_exit)

        x_cursor = 20
        if self.on_continue and self._has_save():
            btn = FlatButton(self.bg, "▶  Продолжить",
                             command=self.on_continue,
                             width=170, height=44, accent=True, font=big_font)
            self.bg.create_window(x_cursor, cy, window=btn, anchor="w",
                                  tags="ui_bottom_btn")
            x_cursor += 170 + 8
            self._bottom_buttons.append(btn)

        for text, cmd, width in [
            ("📅  Ежедневный", self.on_daily, 180),
            ("🎯  Растущая серия", self.on_cascade_growing, 200),
            ("🎮  Режимы", self.on_modes, 130),
            ("📖  Правила", self.on_show_rules, 140),
            ("⚙  Настройки", self.on_settings, 160),
        ]:
            btn = FlatButton(self.bg, text, command=cmd,
                             width=width, height=44, font=big_font)
            self.bg.create_window(x_cursor, cy, window=btn, anchor="w",
                                  tags="ui_bottom_btn")
            x_cursor += width + 8
            self._bottom_buttons.append(btn)

        btn = FlatButton(self.bg, "🗑  Рекорды",
                         command=self._clear_records,
                         width=150, height=44, danger=True, font=big_font)
        self.bg.create_window(x_cursor, cy, window=btn, anchor="w",
                              tags="ui_bottom_btn")
        self._bottom_buttons.append(btn)

    # ------------------------------------------------------------------
    def _has_save(self):
        try:
            from ..storage.savegame import SaveGame
            return SaveGame().has_save()
        except Exception:
            return False

    def _clear_records(self):
        if not self.records.all_records():
            messagebox.showinfo("Рекорды", "Список рекордов уже пуст.")
            return
        if messagebox.askyesno("Удалить рекорды",
                               "Удалить все сохранённые рекорды?\n"
                               "Это действие нельзя отменить."):
            self.records.reset()
            if self.on_rebuild:
                self.on_rebuild()