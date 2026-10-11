import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
from .. import config as cfg
from ..storage.settings import Settings
from .theme import (BgCanvas, round_rect, set_wallpaper, has_wallpaper,
                    delete_wallpaper, CONTEXTS, CONTEXT_LABELS)


class SettingsScreen(tk.Frame):
    def __init__(self, master, on_close, on_apply):
        super().__init__(master, bg=cfg.C("COLOR_BG"))
        self.on_close = on_close
        self.on_apply = on_apply
        self.settings = Settings()

        self.bg = BgCanvas(self, context="settings")
        self.bg.pack(fill="both", expand=True)

        self._refresh_job = None
        self._last_size = (0, 0)

        self.theme_var = tk.StringVar(value=self.settings.get("theme"))
        self.cell_var = tk.StringVar(value=self.settings.get("cell_scale"))
        self.anim_var = tk.BooleanVar(value=self.settings.get("animations"))
        self.autosave_var = tk.BooleanVar(value=self.settings.get("autosave"))
        self.sound_var = tk.BooleanVar(value=self.settings.get("sound"))

        self._context_var = tk.StringVar(value=CONTEXT_LABELS["menu"])

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
        self.bg.delete("setting")
        self.bg.delete("ui_bottom")
        self.bg.delete("ui_bottom_btn")

        self._draw_header(w)
        self._draw_body(w, h)
        self._draw_bottom(w, h)

    # ------------------------------------------------------------------
    def _draw_header(self, w):
        self.bg.create_rectangle(0, 0, w, 3,
                                 fill=cfg.C("COLOR_ACCENT"),
                                 outline="", tags="ui")

        self.bg.create_text(40, 30,
                            text="Настройки",
                            font=cfg.FONT_TITLE,
                            fill=cfg.C("COLOR_TEXT"),
                            anchor="nw", tags="ui")
        self.bg.create_text(40, 100,
                            text="Изменения вступят в силу после «Применить»",
                            font=cfg.FONT_BODY,
                            fill=cfg.C("COLOR_TEXT_DIM"),
                            anchor="nw", tags="ui")

    # ------------------------------------------------------------------
    def _draw_body(self, w, h):
        start_x = 40
        y = 175

        y = self._section(start_x, y, "Тема")
        y = self._radio_row(start_x, y, self.theme_var, [
            ("Тёмная", "dark"),
            ("Светлая", "light"),
        ], key="theme")

        y = self._section(start_x, y + 20, "Размер клетки")
        y = self._radio_row(start_x, y, self.cell_var, [
            ("Компактный", "compact"),
            ("Обычный", "normal"),
            ("Крупный", "large"),
        ], key="cell")

        y = self._section(start_x, y + 20, "Обои")
        y = self._wallpaper_row(start_x, y)

        y = self._section(start_x, y + 10, "Интерфейс")
        y = self._checkbox_row(start_x, y, self.anim_var, "anim",
                               "Анимации (карточка победы и т.д.)")
        y = self._checkbox_row(start_x, y, self.autosave_var, "autosave",
                               "Автосохранение партии")
        y = self._checkbox_row(start_x, y, self.sound_var, "sound",
                               "Звуки")

    # ------------------------------------------------------------------
    def _section(self, x, y, text):
        self.bg.create_text(x, y,
                            text=text,
                            font=("Jost* Semi", 14),
                            fill=cfg.C("COLOR_TEXT"),
                            anchor="nw", tags="setting")
        return y + 36

    def _radio_row(self, x, y, var, options, key):
        card_w = 140
        card_h = 52
        gap = 12

        for i, (label, value) in enumerate(options):
            cx1 = x + i * (card_w + gap)
            cy1 = y
            cx2 = cx1 + card_w
            cy2 = cy1 + card_h
            tag = f"radio_{key}_{value}"

            active = (var.get() == value)
            outline = cfg.C("COLOR_ACCENT") if active else cfg.C("COLOR_PANEL_EDGE")
            fill = cfg.C("COLOR_PANEL_HOVER") if active else cfg.C("COLOR_PANEL")

            round_rect(self.bg, cx1, cy1, cx2, cy2, 14,
                       fill=fill, outline=outline, width=2,
                       tags=("setting", tag))

            self.bg.create_text((cx1 + cx2) / 2, (cy1 + cy2) / 2,
                                text=label,
                                font=("Jost* Semi", 13),
                                fill=cfg.C("COLOR_TEXT"),
                                anchor="center",
                                tags=("setting", tag))

            self.bg.tag_bind(tag, "<Button-1>",
                             lambda e, v=value, k=key: self._select_radio(k, v))
            self.bg.tag_bind(tag, "<Enter>",
                             lambda e: self.bg.configure(cursor="hand2"))
            self.bg.tag_bind(tag, "<Leave>",
                             lambda e: self.bg.configure(cursor=""))

        return y + card_h + 20

    def _select_radio(self, key, value):
        if key == "theme":
            self.theme_var.set(value)
        elif key == "cell":
            self.cell_var.set(value)
        self._refresh()

    def _wallpaper_row(self, x, y):
        label = tk.Label(self.bg, text="Контекст:",
                         font=cfg.FONT_BODY,
                         fg=cfg.C("COLOR_TEXT"), bg=cfg.C("COLOR_BG"))
        self.bg.create_window(x, y + 12, window=label, anchor="w",
                              tags="setting")

        self._context_combo = ttk.Combobox(
            self.bg,
            textvariable=self._context_var,
            values=[CONTEXT_LABELS[c] for c in CONTEXTS],
            state="readonly",
            width=22,
            font=cfg.FONT_BODY,
        )
        self.bg.create_window(x + 90, y + 12, window=self._context_combo,
                              anchor="w", tags="setting")
        self._context_combo.bind("<<ComboboxSelected>>",
                                 lambda e: self._update_wp_status())

        btn_change = tk.Label(self.bg, text="Заменить",
                              font=("Jost* Medium", 11),
                              fg=cfg.C("COLOR_TEXT"),
                              bg=cfg.C("COLOR_PANEL"),
                              padx=14, pady=8,
                              cursor="hand2")
        self.bg.create_window(x + 320, y + 12, window=btn_change,
                              anchor="w", tags="setting")
        btn_change.bind("<Button-1>", lambda e: self._pick_wallpaper())

        btn_delete = tk.Label(self.bg, text="Сбросить",
                              font=("Jost* Medium", 11),
                              fg=cfg.C("COLOR_DANGER"),
                              bg=cfg.C("COLOR_PANEL"),
                              padx=14, pady=8,
                              cursor="hand2")
        self.bg.create_window(x + 420, y + 12, window=btn_delete,
                              anchor="w", tags="setting")
        btn_delete.bind("<Button-1>", lambda e: self._delete_wallpaper())

        self.wp_status = tk.Label(self.bg, text="",
                                  font=cfg.FONT_BODY,
                                  fg=cfg.C("COLOR_TEXT_DIM"),
                                  bg=cfg.C("COLOR_BG"))
        self.bg.create_window(x, y + 48, window=self.wp_status,
                              anchor="w", tags="setting")
        self._update_wp_status()

        return y + 84

    def _current_context(self):
        name = self._context_var.get()
        for k, v in CONTEXT_LABELS.items():
            if v == name:
                return k
        return "menu"

    def _update_wp_status(self):
        theme = cfg.current_theme()
        context = self._current_context()
        theme_name = "тёмной" if theme == "dark" else "светлой"

        if has_wallpaper(context, theme):
            self.wp_status.config(
                text=f"✓ обои для «{CONTEXT_LABELS[context]}» установлены ({theme_name} тема)",
                fg=cfg.C("COLOR_SUCCESS"))
        else:
            if context != "menu" and has_wallpaper("menu", theme):
                self.wp_status.config(
                    text="используется фоллбэк «Главное меню»",
                    fg=cfg.C("COLOR_TEXT_DIM"))
            else:
                self.wp_status.config(
                    text="используется градиент по умолчанию",
                    fg=cfg.C("COLOR_TEXT_DIM"))

    def _pick_wallpaper(self):
        path = filedialog.askopenfilename(
            title="Выберите обои",
            filetypes=[("Изображения JPG", "*.jpg *.jpeg"),
                       ("Все файлы", "*.*")],
        )
        if not path:
            return
        if not path.lower().endswith((".jpg", ".jpeg")):
            messagebox.showwarning("Не тот формат",
                                   "Поддерживаются только .jpg и .jpeg.")
            return
        context = self._current_context()
        theme = cfg.current_theme()
        if set_wallpaper(path, context, theme):
            self._update_wp_status()
            if self.on_apply:
                self.on_apply()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить обои.")

    def _delete_wallpaper(self):
        context = self._current_context()
        theme = cfg.current_theme()
        if not has_wallpaper(context, theme):
            messagebox.showinfo("Обои", "Для этого контекста обои не установлены.")
            return
        if messagebox.askyesno("Удалить обои",
                               f"Удалить обои для «{CONTEXT_LABELS[context]}»?\n"
                               "Будет использован фоллбэк или градиент."):
            delete_wallpaper(context, theme)
            self._update_wp_status()
            if self.on_apply:
                self.on_apply()

    def _checkbox_row(self, x, y, var, key, text):
        box_size = 22
        tag = f"check_{key}"

        round_rect(self.bg, x, y, x + box_size, y + box_size, 6,
                   fill=cfg.C("COLOR_ACCENT") if var.get() else cfg.C("COLOR_PANEL"),
                   outline=cfg.C("COLOR_ACCENT") if var.get() else cfg.C("COLOR_PANEL_EDGE"),
                   width=2,
                   tags=("setting", tag))

        if var.get():
            self.bg.create_line(x + 5, y + 11, x + 9, y + 15,
                                fill="#ffffff", width=2,
                                capstyle="round",
                                tags=("setting", tag))
            self.bg.create_line(x + 9, y + 15, x + 17, y + 7,
                                fill="#ffffff", width=2,
                                capstyle="round",
                                tags=("setting", tag))

        self.bg.create_text(x + box_size + 12, y + box_size / 2,
                            text=text,
                            font=cfg.FONT_BODY,
                            fill=cfg.C("COLOR_TEXT"),
                            anchor="w", tags=("setting", tag))

        self.bg.tag_bind(tag, "<Button-1>",
                         lambda e, v=var: self._toggle_check(v))
        self.bg.tag_bind(tag, "<Enter>",
                         lambda e: self.bg.configure(cursor="hand2"))
        self.bg.tag_bind(tag, "<Leave>",
                         lambda e: self.bg.configure(cursor=""))

        return y + box_size + 12

    def _toggle_check(self, var):
        var.set(not var.get())
        self._refresh()

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

        big_font = ("Jost* Medium", 12)

        self._draw_flat_button(
            text="Сбросить",
            x1=40, y1=panel_y1 + (panel_h - 44) / 2,
            width=160, height=44,
            on_click=self._reset,
            font=big_font,
            bg=cfg.C("COLOR_PANEL"), fg=cfg.C("COLOR_TEXT"),
        )

        self._draw_flat_button(
            text="Применить",
            x1=w - 40 - 180, y1=panel_y1 + (panel_h - 44) / 2,
            width=180, height=44,
            on_click=self._apply,
            font=big_font,
            bg=cfg.C("COLOR_ACCENT"), fg="#ffffff",
        )

        self._draw_flat_button(
            text="←  Назад",
            x1=w - 40 - 180 - 10 - 160, y1=panel_y1 + (panel_h - 44) / 2,
            width=160, height=44,
            on_click=self.on_close,
            font=big_font,
            bg=cfg.C("COLOR_PANEL"), fg=cfg.C("COLOR_TEXT"),
        )

    def _draw_flat_button(self, text, x1, y1, width, height,
                          on_click, font, bg, fg, radius=14):
        tag = f"btn_{text[:4]}"
        x2 = x1 + width
        y2 = y1 + height

        round_rect(self.bg, x1, y1, x2, y2, radius,
                   fill=bg, outline="", tags=("ui_bottom_btn", tag))

        self.bg.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                            text=text,
                            font=font,
                            fill=fg,
                            anchor="center",
                            tags=("ui_bottom_btn", tag))

        self.bg.tag_bind(tag, "<Button-1>", lambda e: on_click())
        self.bg.tag_bind(tag, "<Enter>",
                         lambda e: self.bg.configure(cursor="hand2"))
        self.bg.tag_bind(tag, "<Leave>",
                         lambda e: self.bg.configure(cursor=""))

    # ------------------------------------------------------------------
    def _apply(self):
        self.settings.set("theme", self.theme_var.get())
        self.settings.set("cell_scale", self.cell_var.get())
        self.settings.set("animations", self.anim_var.get())
        self.settings.set("autosave", self.autosave_var.get())
        self.settings.set("sound", self.sound_var.get())
        self.settings.save()

        cfg.set_theme(self.theme_var.get())
        if self.on_apply:
            self.on_apply()

    def _reset(self):
        self.settings.reset()
        self.theme_var.set(self.settings.get("theme"))
        self.cell_var.set(self.settings.get("cell_scale"))
        self.anim_var.set(self.settings.get("animations"))
        self.autosave_var.set(self.settings.get("autosave"))
        self.sound_var.set(self.settings.get("sound"))
        if self.on_apply:
            self.on_apply()