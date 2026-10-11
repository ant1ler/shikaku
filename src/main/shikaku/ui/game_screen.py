import time
import traceback
import tkinter as tk
from ..core.board import Board
from ..core.generator import PuzzleGenerator
from ..storage.records import Records
from ..storage.daily import Daily
from ..storage.savegame import SaveGame
from ..storage.settings import Settings
from .. import config as cfg
from .board_view import BoardView
from .theme import (FlatButton, Overlay, WinCard, LevelCard,
                    LoseCard, ErrorFlash, format_time,
                    BgCanvas)


class GameScreen(tk.Frame):
    AUTOSAVE_MS = 15000

    def __init__(self, master, size: int, board: Board | None = None,
                 on_back=None, on_save=None, records: Records | None = None,
                 cascade: bool = False, timed: bool = False,
                 daily: bool = False, blind: bool = False,
                 cascade_growing: bool = False,
                 meta: dict | None = None):
        super().__init__(master, bg=cfg.C("COLOR_BG"))
        self.on_back = on_back
        self.on_save = on_save
        self.records = records or Records()
        self.settings = Settings()
        self.savegame = SaveGame()
        self.size = size
        self.cascade = cascade
        self.timed = timed
        self.daily = daily
        self.blind = blind
        self.cascade_growing = cascade_growing
        self.daily_store = Daily() if daily else None

        meta = meta or {}

        # растущая серия имеет приоритет над обычной
        if cascade_growing:
            self._cascade_sizes = list(cfg.CASCADE_GROWING_SIZES)
            self._cascade_level = meta.get("cascade_level", 1)
            self._cascade_total = len(self._cascade_sizes)
        elif cascade:
            self._cascade_sizes = [size] * cfg.CASCADE_LEVELS
            self._cascade_level = meta.get("cascade_level", 1)
            self._cascade_total = cfg.CASCADE_LEVELS
        else:
            self._cascade_sizes = []
            self._cascade_level = 0
            self._cascade_total = 1

        self._cascade_elapsed_before = meta.get("cascade_elapsed_before", 0.0)

        # размер текущего уровня
        if cascade_growing and self._cascade_sizes:
            current_size = self._cascade_sizes[self._cascade_level - 1]
        else:
            current_size = size

        self.size = current_size

        self._time_limit = cfg.TIME_LIMITS.get(current_size, 60)
        self._time_used = meta.get("time_used", 0.0)
        self._paused = False
        self._pause_started = None

        if board is None:
            if daily:
                seed = Daily.seed_for(current_size)
                puzzle = PuzzleGenerator().generate_with_seed(current_size, seed)
            else:
                puzzle = PuzzleGenerator().generate_unique(current_size)
            board = Board(puzzle)
        self.board = board

        self._start_ts = time.time()
        self._elapsed = meta.get("elapsed", 0.0)
        if not self.timed:
            self._start_ts -= self._elapsed
        self._running = True
        self._timer_job = None
        self._autosave_job = None
        self._best_before = self._get_best()
        self._overlay = None
        self._hints_left = meta.get("hints_left", cfg.HINT_LIMIT)

        # ---------- фон-обои для игры ----------
        self.bg = BgCanvas(self, context=f"game_{current_size}")
        self.bg.pack(fill="both", expand=True)

        # ---------- BoardView ----------
        self.board_view = BoardView(
            self.bg, self.board,
            on_move=self._update_info,
            on_win=self._on_win,
            on_error=self._on_error,
            on_remove=self._on_remove,
            blind=self.blind,
        )

        # ---------- верхняя панель ----------
        top = tk.Frame(self.bg, bg=cfg.C("COLOR_PANEL"))
        self._top_window_id = self.bg.create_window(
            0, 0, window=top, anchor="nw",
            width=10000, height=52, tags="top_bar"
        )

        inner = tk.Frame(top, bg=cfg.C("COLOR_PANEL"))
        inner.pack(fill="x", padx=14, pady=6)

        FlatButton(inner, "←  Меню", command=self._back,
                   width=110, height=32).pack(side="left", padx=(0, 6))
        FlatButton(inner, "↻  Заново", command=self._restart,
                   width=120, height=32).pack(side="left", padx=6)
        FlatButton(inner, "✕  Очистить", command=self._clear,
                   width=130, height=32).pack(side="left", padx=6)
        FlatButton(inner, "↶  Отменить", command=self._undo,
                   width=140, height=32).pack(side="left", padx=6)
        FlatButton(inner, "💾  Сохранить", command=self._save,
                   width=150, height=32, accent=True).pack(side="left", padx=6)

        self.timer_label = tk.Label(inner, text="⏱ 00:00",
                                    font=cfg.FONT_TIMER,
                                    fg=cfg.C("COLOR_TEXT"),
                                    bg=cfg.C("COLOR_PANEL"))
        self.timer_label.pack(side="right")

        # ---------- вторая панель ----------
        tools = tk.Frame(self.bg, bg=cfg.C("COLOR_PANEL"))
        self._tools_window_id = self.bg.create_window(
            0, 53, window=tools, anchor="nw",
            width=10000, height=44, tags="tools_bar"
        )

        tools_inner = tk.Frame(tools, bg=cfg.C("COLOR_PANEL"))
        tools_inner.pack(fill="x", padx=14, pady=6)

        self.hint_btn = FlatButton(tools_inner,
                                   f"💡  Подсказка ({self._hints_left})  [H]",
                                   command=self._use_hint,
                                   width=230, height=32)
        self.hint_btn.pack(side="left")

        FlatButton(tools_inner, "✓  Проверить  [C]", command=self._check_solution,
                   width=200, height=32).pack(side="left", padx=(8, 0))

        self.penalty_label = tk.Label(tools_inner, text="",
                                      font=cfg.FONT_SMALL,
                                      fg=cfg.C("COLOR_DANGER"),
                                      bg=cfg.C("COLOR_PANEL"))
        self.penalty_label.pack(side="left", padx=(14, 0))

        # ---------- строка рекорда (на Canvas) ----------
        self.record_text_id = None
        self.info_text_id = None
        self._record_text = ""
        self._info_text = ""

        # ---------- нижняя панель ----------
        self._bottom = tk.Frame(self.bg, bg=cfg.C("COLOR_PANEL"))
        self._bottom.place(relx=0, rely=1.0, relwidth=1.0,
                           anchor="sw", height=36)

        bottom_inner = tk.Frame(self._bottom, bg=cfg.C("COLOR_PANEL"))
        bottom_inner.pack(fill="x", padx=16, pady=6)

        tk.Label(bottom_inner,
                 text=("Ctrl+Z — отмена   ·   Ctrl+N — новая   ·   "
                       "Ctrl+S — сохранить   ·   H — подсказка   ·   "
                       "C — проверка   ·   ПКМ — удалить   ·   Esc — меню"),
                 font=cfg.FONT_SMALL,
                 fg=cfg.C("COLOR_TEXT_DIM"), bg=cfg.C("COLOR_PANEL")
                 ).pack()

        self._error_flash = ErrorFlash(self)

        self._last_size = (0, 0)
        self.bg.bind("<Configure>", self._on_configure, add="+")

        self._bind_hotkeys()
        self.focus_set()

        self._update_info()
        self._update_record_label()
        self._tick()
        self._schedule_autosave()

        self.after(80, self._relayout)

    # ------------------------------------------------------------------
    def _on_configure(self, event=None):
        w = self.bg.winfo_width()
        h = self.bg.winfo_height()
        if (w, h) == self._last_size:
            return
        self._last_size = (w, h)
        self._relayout()

    def _relayout(self):
        w = self.bg.winfo_width()
        h = self.bg.winfo_height()
        if w < 100 or h < 100:
            self.after(50, self._relayout)
            return

        try:
            self.bg.itemconfigure(self._top_window_id, width=w)
            self.bg.itemconfigure(self._tools_window_id, width=w)
        except tk.TclError:
            pass

        top_h = 52
        tools_h = 44
        bottom_h = 36

        record_y = top_h + tools_h + 15
        field_top = record_y + 32
        field_bottom = h - bottom_h - 10

        avail_h = max(0, field_bottom - field_top - 20)
        avail_w = max(0, w - 40)

        self.board_view.set_available_space(avail_w, avail_h)

        bw, bh = self.board_view.get_size()

        fcx = w // 2
        fcy = (field_top + field_bottom) // 2

        x0 = fcx - bw // 2
        y0 = fcy - bh // 2

        if y0 < field_top:
            y0 = field_top
        if y0 + bh > field_bottom:
            y0 = max(field_top, field_bottom - bh)

        self.board_view.set_position(x0, y0)

        if self.record_text_id:
            self.bg.delete(self.record_text_id)
        if self.info_text_id:
            self.bg.delete(self.info_text_id)

        if cfg.current_theme() == "dark":
            record_color = "#e8e0f0"
        else:
            record_color = "#2a1e48"

        self.record_text_id = self.bg.create_text(
            20, record_y,
            text=self._record_text,
            font=cfg.FONT_BODY,
            fill=record_color,
            anchor="nw", tags="record_row"
        )
        self.info_text_id = self.bg.create_text(
            w - 20, record_y,
            text=self._info_text,
            font=cfg.FONT_BODY,
            fill=record_color,
            anchor="ne", tags="record_row"
        )

    # ---------------- автосохранение ----------------
    def _schedule_autosave(self):
        if not self.settings.get("autosave"):
            return
        self._autosave_job = self.after(self.AUTOSAVE_MS, self._autosave)

    def _autosave(self):
        self._persist()
        self._schedule_autosave()

    def _persist(self):
        if self.daily:
            return
        if self.board.won:
            return
        if self.cascade_growing:
            mode = "cascade_growing"
        elif self.cascade:
            mode = "cascade"
        elif self.timed:
            mode = "timed"
        else:
            mode = "normal"
        meta = {
            "mode": mode,
            "elapsed": self._elapsed,
            "cascade_level": self._cascade_level,
            "cascade_elapsed_before": self._cascade_elapsed_before,
            "time_used": self._time_used,
            "hints_left": self._hints_left,
            "size": self.size,
        }
        self.savegame.save(self.board, meta)

    # ---------------- горячие клавиши ----------------
    def _bind_hotkeys(self):
        root = self.winfo_toplevel()
        root.bind("<Control-z>", self._hotkey_undo)
        root.bind("<Control-Z>", self._hotkey_undo)
        root.bind("<Control-n>", self._hotkey_new)
        root.bind("<Control-N>", self._hotkey_new)
        root.bind("<Control-s>", self._hotkey_save)
        root.bind("<Control-S>", self._hotkey_save)
        root.bind("<Control-r>", self._hotkey_restart)
        root.bind("<Control-R>", self._hotkey_restart)
        root.bind("<h>", self._hotkey_hint)
        root.bind("<H>", self._hotkey_hint)
        root.bind("<c>", self._hotkey_check)
        root.bind("<C>", self._hotkey_check)
        root.bind("<space>", self._hotkey_pause)
        root.bind("<Escape>", self._hotkey_menu)

    def _unbind_hotkeys(self):
        root = self.winfo_toplevel()
        for seq in ("<Control-z>", "<Control-Z>",
                    "<Control-n>", "<Control-N>",
                    "<Control-s>", "<Control-S>",
                    "<Control-r>", "<Control-R>",
                    "<h>", "<H>", "<c>", "<C>",
                    "<space>", "<Escape>", "<Return>"):
            try:
                root.unbind(seq)
            except tk.TclError:
                pass

    def _hotkey_undo(self, _=None):
        self._undo()

    def _hotkey_new(self, _=None):
        self._restart()

    def _hotkey_save(self, _=None):
        self._save()

    def _hotkey_restart(self, _=None):
        self._restart()

    def _hotkey_hint(self, _=None):
        self._use_hint()

    def _hotkey_check(self, _=None):
        self._check_solution()

    def _hotkey_pause(self, _=None):
        if not self.timed:
            return
        self._toggle_pause()

    def _hotkey_menu(self, _=None):
        self._back()

    def _toggle_pause(self):
        if self._paused:
            if self._pause_started is not None:
                self._start_ts += time.time() - self._pause_started
                self._pause_started = None
            self._paused = False
            self._running = True
            self._tick()
        else:
            self._paused = True
            self._pause_started = time.time()
            self._running = False
            self.timer_label.config(text="⏸ ПАУЗА")

    def _on_error(self, rect):
        self._error_flash.flash()

    def _on_remove(self, rect):
        pass

    def _get_best(self):
        if self.daily:
            return None
        if self.cascade_growing:
            # ключ — стартовый размер серии
            start_size = cfg.CASCADE_GROWING_SIZES[0]
            return self.records.best(start_size, cascade_growing=True)
        return self.records.best(self.size,
                                 cascade=self.cascade,
                                 timed=self.timed)

    def _total_elapsed(self):
        if self.cascade or self.cascade_growing:
            return self._cascade_elapsed_before + self._elapsed
        return self._elapsed

    def _time_left(self):
        return max(0.0, self._time_limit - self._time_used)

    def _tick(self):
        if not self._running:
            return
        now = time.time() - self._start_ts

        if self.timed:
            self._time_used = self._time_used + (now - self._elapsed)
            self._elapsed = now

            left = self._time_left()
            self.timer_label.config(text=f"⏱ {format_time(left)}")

            if left <= 5:
                self.timer_label.config(fg=cfg.C("COLOR_DANGER"))
            elif left <= 15:
                self.timer_label.config(fg="#ffd07f")
            else:
                self.timer_label.config(fg=cfg.C("COLOR_TEXT"))

            if left <= 0:
                self._on_timeout()
                return
        else:
            self._elapsed = now
            shown = self._total_elapsed() if (self.cascade or self.cascade_growing) else self._elapsed
            self.timer_label.config(text=f"⏱ {format_time(shown)}")

        self._timer_job = self.after(200, self._tick)

    def _stop_timer(self):
        self._running = False
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

    def destroy(self):
        try:
            self._persist()
        except Exception:
            pass

        self._stop_timer()
        if self._autosave_job:
            try:
                self.after_cancel(self._autosave_job)
            except tk.TclError:
                pass
            self._autosave_job = None
        try:
            self.board_view.stop_flash()
        except Exception:
            pass
        self._unbind_hotkeys()
        self._hide_overlay()
        super().destroy()

    def _apply_penalty(self, seconds: int, reason: str):
        if self.timed:
            self._time_used += seconds
            self.penalty_label.config(text=f"−{seconds} сек · {reason}")
        else:
            self._start_ts -= seconds
            self.penalty_label.config(text=f"+{seconds} сек · {reason}")
        self.after(1800, lambda: self.penalty_label.config(text=""))

    def _back(self):
        self._persist()
        self._stop_timer()
        if self.on_back:
            self.on_back()

    def _restart(self):
        if self.daily:
            return
        self._hide_overlay()
        if self.cascade or self.cascade_growing:
            self._cascade_level = 1
            self._cascade_elapsed_before = 0.0
        if self.timed:
            self._time_used = 0.0
            self._paused = False
        self._new_puzzle(keep_hints=False)
        self.savegame.delete()

    def _new_puzzle(self, keep_hints=True):
        if self.cascade_growing:
            new_size = self._cascade_sizes[self._cascade_level - 1]
            self.size = new_size
            self.bg.set_context(f"game_{new_size}")
        else:
            new_size = self.size

        if self.daily:
            seed = Daily.seed_for(new_size)
            puzzle = PuzzleGenerator().generate_with_seed(new_size, seed)
        else:
            puzzle = PuzzleGenerator().generate_unique(new_size)

        self.board = Board(puzzle)
        self.board_view.board = self.board
        self.board_view.preview = None
        self.board_view.start = None
        self.board_view._flash_rects = []
        self.board_view.blind = self.blind
        self.board_view.redraw()

        # при смене размера нужно пересчитать размер клетки
        self._last_size = (0, 0)
        self._relayout()

        self._best_before = self._get_best()
        self._update_record_label()
        if not keep_hints:
            self._hints_left = cfg.HINT_LIMIT
            self.hint_btn.set_text(f"💡  Подсказка ({self._hints_left})  [H]")
        if self.timed and self._cascade_level == (1 if self.cascade else 0):
            self._time_used = 0.0
        self._start_ts = time.time()
        self._elapsed = 0.0
        self._running = True
        self._paused = False
        self.timer_label.config(fg=cfg.C("COLOR_TEXT"))
        self._tick()
        self._update_info()

    def _clear(self):
        self.board.clear()
        self.board_view.redraw()
        self._update_info()

    def _undo(self):
        if self.board.undo():
            self.board_view.redraw()
            self._update_info()

    def _save(self):
        self._persist()
        if self.on_save:
            self.on_save(self.board)
        self._flash_saved()

    def _flash_saved(self):
        self.timer_label.config(text="💾 сохранено")
        self.after(900, lambda: self.timer_label.config(
            text=f"⏱ {format_time(self._total_elapsed())}"
        ))

    def _use_hint(self):
        if self._hints_left <= 0:
            return
        placed = self.board.hint_from()
        if placed is None:
            self.penalty_label.config(text="нечего подсказывать")
            self.after(1500, lambda: self.penalty_label.config(text=""))
            return
        self._hints_left -= 1
        self.hint_btn.set_text(f"💡  Подсказка ({self._hints_left})  [H]")
        if self.timed:
            self._apply_penalty(cfg.TIMED_HINT_PENALTY, "подсказка")
        else:
            self._apply_penalty(cfg.HINT_PENALTY, "подсказка")
        self.board_view.redraw()
        self._update_info()
        if self.board.won:
            self._on_win()

    def _check_solution(self):
        if self.timed:
            self._apply_penalty(cfg.TIMED_CHECK_PENALTY, "проверка")
        else:
            self._apply_penalty(cfg.CHECK_PENALTY, "проверка")
        self.board_view.flash_invalid()

    def _update_info(self):
        n = self.board.puzzle.size
        covered = sum(r.area for r in self.board.rects)
        prefix = ""
        if self.daily:
            prefix = "📅 ежедневный  ·  "
        elif self.cascade_growing:
            prefix = f"Растущая серия · этап {self._cascade_level}/{self._cascade_total}  ·  "
        elif self.cascade:
            prefix = f"Этап {self._cascade_level}/{self._cascade_total}  ·  "
        elif self.timed:
            prefix = "⏱ на время  ·  "
        elif self.blind:
            prefix = "👁 слепой  ·  "
        self._info_text = f"{prefix}Заполнено: {covered} / {n * n}"

        if self.info_text_id:
            try:
                self.bg.itemconfigure(self.info_text_id, text=self._info_text)
            except tk.TclError:
                pass

    def _update_record_label(self):
        if self.daily:
            streak = self.daily_store.streak() if self.daily_store else 0
            if streak > 0:
                text = f"📅  Ежедневный {self.size}×{self.size}   ·   🔥 серия {streak}"
            else:
                text = f"📅  Ежедневный {self.size}×{self.size}"
            self._record_text = text
        else:
            if self.cascade_growing:
                label = f"🎯  Растущая серия"
            elif self.timed:
                label = f"🏆  На время {self.size}×{self.size}"
            elif self.cascade:
                label = f"🏆  Серия {self.size}×{self.size}"
            elif self.blind:
                label = f"👁  Слепой {self.size}×{self.size}"
            else:
                label = f"🏆  Рекорд {self.size}×{self.size}"
            if self._best_before is not None:
                self._record_text = f"{label}   ·   {format_time(self._best_before)}"
            else:
                self._record_text = f"{label}   ·   пока нет"

        if self.record_text_id:
            try:
                self.bg.itemconfigure(self.record_text_id,
                                      text=self._record_text)
            except tk.TclError:
                pass

    def _on_win(self):
        self._stop_timer()
        if not self.daily:
            self.savegame.delete()
        level_time = self._elapsed

        if self.blind:
            self.board_view.reveal()
            delay = 1200
        else:
            delay = 350

        if self.cascade or self.cascade_growing:
            self._cascade_elapsed_before += level_time

        if (self.cascade or self.cascade_growing) and \
                self._cascade_level < self._cascade_total:
            self.after(delay, lambda: self._show_level_overlay(level_time))
        else:
            self.after(delay, lambda: self._show_final_overlay(level_time))

    def _on_timeout(self):
        self._stop_timer()
        if not self.daily:
            self.savegame.delete()
        self.after(350, self._show_lose_overlay)

    def _show_level_overlay(self, level_time):
        try:
            self._hide_overlay()

            overlay = Overlay(self, context=f"game_{self.size}")
            overlay.show()

            # следующий размер — для растущей серии
            next_size = None
            if self.cascade_growing:
                if self._cascade_level < self._cascade_total:
                    next_size = self._cascade_sizes[self._cascade_level]

            card = LevelCard(overlay, on_continue=self._next_cascade_level)
            card.build(
                level=self._cascade_level,
                total=self._cascade_total,
                level_time=level_time,
                total_time=self._cascade_elapsed_before,
                is_last=(self._cascade_level + 1 == self._cascade_total),
                next_size=next_size,
            )

            total = 40
            step = 20
            card.place(relx=0, rely=1.0, relwidth=1, relheight=1)

            def slide(i=0):
                t = i / total
                eased = 1 - (1 - t) ** 2
                rely = 1.0 * (1 - eased)
                try:
                    card.place_configure(rely=rely)
                except tk.TclError:
                    return
                if i < total:
                    self.after(step, lambda: slide(i + 1))
                else:
                    card.place_configure(rely=0.0)

            slide(0)
            self._overlay = overlay

            self.winfo_toplevel().bind("<Return>",
                                       lambda e: self._next_cascade_level())
        except Exception:
            traceback.print_exc()

    def _next_cascade_level(self):
        try:
            self.winfo_toplevel().unbind("<Return>")
        except tk.TclError:
            pass
        self._hide_overlay()
        self._cascade_level += 1
        # в растущей серии сбрасываем подсказки на каждом этапе
        if self.cascade_growing:
            self._hints_left = cfg.HINT_LIMIT
            self.hint_btn.set_text(f"💡  Подсказка ({self._hints_left})  [H]")
        self._new_puzzle(keep_hints=True)
        self._persist()

    def _show_final_overlay(self, level_time):
        try:
            self._hide_overlay()

            overlay = Overlay(self, context=f"game_{self.size}")
            overlay.show()

            if self.timed:
                final_value = self._time_left()
            else:
                final_value = self._total_elapsed()

            size = self.board.puzzle.size
            best_before = self._best_before

            if self.daily:
                self.daily_store.submit(size, final_value)
                is_record = False
                best_after = None
                daily_streak = self.daily_store.streak()
            elif self.cascade_growing:
                start_size = cfg.CASCADE_GROWING_SIZES[0]
                is_record = self.records.submit(start_size, final_value,
                                                cascade_growing=True)
                best_after = self.records.best(start_size,
                                                cascade_growing=True)
                daily_streak = 0
            else:
                is_record = self.records.submit(size, final_value,
                                                cascade=self.cascade,
                                                timed=self.timed)
                best_after = self.records.best(size,
                                               cascade=self.cascade,
                                               timed=self.timed)
                daily_streak = 0

            self._best_before = best_after
            self._update_record_label()

            rects_count = len(self.board.rects)
            moves = self.board.moves
            ideal_count = len(self.board.puzzle.solution)

            card = WinCard(overlay,
                           on_replay=self._replay,
                           on_menu=self._menu)
            card.build(size, final_value, is_record, best_before,
                       best_after, rects_count, moves, ideal_count,
                       cascade=self.cascade,
                       cascade_total=self._cascade_total,
                       timed=self.timed,
                       daily=self.daily,
                       daily_streak=daily_streak)

            total = 40
            step = 20
            card.place(relx=0, rely=1.0, relwidth=1, relheight=1)

            def slide(i=0):
                t = i / total
                eased = 1 - (1 - t) ** 2
                rely = 1.0 * (1 - eased)
                try:
                    card.place_configure(rely=rely)
                except tk.TclError:
                    return
                if i < total:
                    self.after(step, lambda: slide(i + 1))
                else:
                    card.place_configure(rely=0.0)

            slide(0)
            self._overlay = overlay
        except Exception:
            traceback.print_exc()

    def _show_lose_overlay(self):
        try:
            self._hide_overlay()

            overlay = Overlay(self, context=f"game_{self.size}")
            overlay.show()

            n = self.board.puzzle.size
            total_cells = n * n
            solved = sum(r.area for r in self.board.rects)
            percent = int(round(solved / total_cells * 100)) if total_cells else 0

            card = LoseCard(overlay,
                            on_replay=self._replay,
                            on_menu=self._menu)
            card.build(
                size=n,
                rects_count=len(self.board.rects),
                moves=self.board.moves,
                solved=solved,
                total_cells=total_cells,
                percent=percent,
            )

            total = 40
            step = 20
            card.place(relx=0, rely=1.0, relwidth=1, relheight=1)

            def slide(i=0):
                t = i / total
                eased = 1 - (1 - t) ** 2
                rely = 1.0 * (1 - eased)
                try:
                    card.place_configure(rely=rely)
                except tk.TclError:
                    return
                if i < total:
                    self.after(step, lambda: slide(i + 1))
                else:
                    card.place_configure(rely=0.0)

            slide(0)
            self._overlay = overlay
        except Exception:
            traceback.print_exc()

    def _hide_overlay(self):
        if self._overlay:
            try:
                self._overlay.destroy()
            except tk.TclError:
                pass
            self._overlay = None

    def _replay(self):
        if self.daily:
            self._menu()
            return
        self._hide_overlay()
        if self.cascade or self.cascade_growing:
            self._cascade_level = 1
            self._cascade_elapsed_before = 0.0
        if self.timed:
            self._time_used = 0.0
        self._new_puzzle(keep_hints=False)

    def _menu(self):
        self._persist()
        self._hide_overlay()
        self._stop_timer()
        if self.on_back:
            self.on_back()