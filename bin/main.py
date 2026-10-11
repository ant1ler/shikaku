#!/usr/bin/env python3
"""Точка входа в игру.

Работает в двух режимах:
  • запуск из Python (python bin/shikaku.py) — ресурсы и данные в проекте;
  • запуск из .exe (PyInstaller) — ресурсы во временной папке, данные рядом с .exe.
"""
import ctypes
import os
import sys
from pathlib import Path

# ---------- определяем пути ----------

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)

# если запущено из .exe (frozen), меняем логику
IS_FROZEN = getattr(sys, "frozen", False)


def resource_path(relative_path: str) -> str:
    """Путь к ресурсу: во временной папке .exe или в проекте."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(PROJECT_ROOT, relative_path)


# статические ресурсы (шрифты, иконка) — читаются из .exe или проекта
FONTS_DIR = resource_path(os.path.join("data", "fonts"))
ICON_PATH = resource_path("shikaku.ico")

# путь к исходникам
SRC_MAIN = os.path.join(PROJECT_ROOT, "src", "main")
if SRC_MAIN not in sys.path:
    sys.path.insert(0, SRC_MAIN)

# пользовательские данные (рекорды, сохранения) — рядом с .exe
if IS_FROZEN:
    DATA_DIR = os.path.join(os.path.dirname(sys.executable), "data")
else:
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")

os.makedirs(DATA_DIR, exist_ok=True)
os.chdir(DATA_DIR)

import tkinter as tk
from shikaku.ui.app import ShikakuApp


# ---------- регистрация шрифтов ----------

def _register_fonts(fonts_dir: str):
    """Регистрирует все .ttf/.otf из папки в системе на время процесса.

    Использует gdi32.AddFontResourceExW с флагом FR_PRIVATE — шрифт виден
    только текущему процессу, не остаётся в системе после закрытия.
    """
    if not os.path.isdir(fonts_dir):
        print(f"[warn] папка шрифтов не найдена: {fonts_dir}")
        return 0

    FR_PRIVATE = 0x10
    loaded = 0
    for path in Path(fonts_dir).glob("*"):
        if path.suffix.lower() in (".ttf", ".otf"):
            try:
                result = ctypes.windll.gdi32.AddFontResourceExW(
                    str(path), FR_PRIVATE, 0
                )
                if result:
                    loaded += 1
            except Exception as e:
                print(f"[warn] не удалось загрузить {path.name}: {e}")
    return loaded


# ---------- главная функция ----------

def main():
    n = _register_fonts(FONTS_DIR)
    print(f"[fonts] загружено шрифтов: {n}")

    root = tk.Tk()
    root.title("Shikaku")

    if os.path.exists(ICON_PATH):
        try:
            root.iconbitmap(ICON_PATH)
        except tk.TclError:
            pass

    root.attributes("-fullscreen", True)

    def _exit_fullscreen(_event=None):
        root.attributes("-fullscreen", False)
        root.destroy()

    root.bind("<Escape>", _exit_fullscreen)

    def _toggle_fullscreen(_event=None):
        current = root.attributes("-fullscreen")
        root.attributes("-fullscreen", not current)

    root.bind("<F11>", _toggle_fullscreen)

    ShikakuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()