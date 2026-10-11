import tkinter as tk
from ..core.board import Board
from ..storage.savegame import SaveGame
from ..storage.records import Records
from ..storage.daily import Daily
from ..storage.settings import Settings
from .. import config as cfg
from .menu_screen import MenuScreen
from .game_screen import GameScreen
from .rules_screen import RulesScreen
from .modes_screen import ModesScreen
from .settings_screen import SettingsScreen
from .theme import Overlay, DailyCard


class ShikakuApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Shikaku")
        self.root.configure(bg=cfg.C("COLOR_BG"))
        self.savegame = SaveGame()
        self.records = Records()
        self.daily = Daily()
        self.settings = Settings()

        cfg.set_theme(self.settings.get("theme"))

        self.current = None
        self._show_menu()

    def _swap(self, frame):
        if self.current is not None:
            self.current.destroy()
        self.current = frame
        self.current.pack(fill="both", expand=True)
        self.root.configure(bg=cfg.C("COLOR_BG"))

    def _show_menu(self):
        self._swap(MenuScreen(
            self.root,
            on_start=self._start_new_game,
            on_continue=self._continue_game,
            on_show_rules=self._show_rules,
            has_save=self.savegame.has_save(),
            on_rebuild=self._show_menu,
            on_cascade=self._start_cascade,
            on_timed=self._start_timed,
            on_daily=self._show_daily,
            on_settings=self._show_settings,
            on_modes=self._show_modes,
            on_blind=self._start_blind,
            on_cascade_growing=self._start_cascade_growing,
        ))

    def _show_modes(self):
        self._swap(ModesScreen(self.root, on_close=self._show_menu))

    def _show_settings(self):
        self._swap(SettingsScreen(
            self.root,
            on_close=self._show_menu,
            on_apply=self._show_menu,
        ))

    def _show_daily(self):
        if self.current is None:
            return
        overlay = Overlay(self.current)
        overlay.show()

        card = DailyCard(overlay,
                         daily=self.daily,
                         on_start=lambda size: self._start_daily(size, overlay),
                         on_close=overlay.hide)
        card.build()
        card.place(relx=0.5, rely=0.5, anchor="center")

    def _start_daily(self, size: int, overlay):
        overlay.hide()
        overlay.destroy()
        self._swap(GameScreen(
            self.root, size=size,
            on_back=self._show_menu,
            on_save=self._save_board,
            records=self.records,
            daily=True,
        ))

    def _show_rules(self):
        self._swap(RulesScreen(self.root, on_close=self._show_menu))

    def _start_new_game(self, size: int):
        self._swap(GameScreen(
            self.root, size=size,
            on_back=self._show_menu,
            on_save=self._save_board,
            records=self.records,
        ))

    def _start_cascade(self, size: int):
        self._swap(GameScreen(
            self.root, size=size,
            on_back=self._show_menu,
            on_save=self._save_board,
            records=self.records,
            cascade=True,
        ))

    def _start_cascade_growing(self, size: int = None):
        self._swap(GameScreen(
            self.root, size=3,  # старт всегда с 3×3
            on_back=self._show_menu,
            on_save=self._save_board,
            records=self.records,
            cascade_growing=True,
        ))

    def _start_timed(self, size: int):
        self._swap(GameScreen(
            self.root, size=size,
            on_back=self._show_menu,
            on_save=self._save_board,
            records=self.records,
            timed=True,
        ))

    def _start_blind(self, size: int):
        self._swap(GameScreen(
            self.root, size=size,
            on_back=self._show_menu,
            on_save=self._save_board,
            records=self.records,
            blind=True,
        ))

    def _continue_game(self):
        loaded = self.savegame.load()
        if loaded is None:
            return
        board = loaded["board"]
        meta = loaded.get("meta", {}) or {}

        mode = meta.get("mode", "normal")
        cascade = (mode == "cascade")
        timed = (mode == "timed")
        cascade_growing = (mode == "cascade_growing")

        self._swap(GameScreen(
            self.root,
            size=board.puzzle.size,
            board=board,
            on_back=self._show_menu,
            on_save=self._save_board,
            records=self.records,
            cascade=cascade,
            timed=timed,
            cascade_growing=cascade_growing,
            meta=meta,
        ))

    def _save_board(self, board: Board):
        pass