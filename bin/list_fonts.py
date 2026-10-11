#!/usr/bin/env python3
"""Печатает имена всех шрифтов, доступных Tkinter после регистрации.

Запускать так:
    python bin/list_fonts.py
"""
import ctypes
import os
import sys
import tkinter as tk
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
FONTS_DIR = os.path.join(PROJECT_ROOT, "data", "fonts")


def register_fonts(fonts_dir: str):
    if not os.path.isdir(fonts_dir):
        print(f"папка не найдена: {fonts_dir}")
        return 0
    FR_PRIVATE = 0x10
    loaded = 0
    for path in Path(fonts_dir).glob("*"):
        if path.suffix.lower() in (".ttf", ".otf"):
            try:
                r = ctypes.windll.gdi32.AddFontResourceExW(
                    str(path), FR_PRIVATE, 0
                )
                if r:
                    loaded += 1
            except Exception:
                pass
    return loaded


def main():
    n = register_fonts(FONTS_DIR)
    print(f"Загружено файлов: {n}\n")

    root = tk.Tk()
    root.withdraw()  # окно не показываем

    import tkinter.font as tkfont
    families = sorted(set(tkfont.families(root)))

    # показываем только те, что похожи на наши
    keywords = ["jost", "clash", "schueler"]
    print("=== Наши шрифты ===")
    for f in families:
        if any(k in f.lower() for k in keywords):
            print(f"  {f}")

    print("\n=== Все шрифты (для справки) ===")
    for f in families:
        print(f"  {f}")

    root.destroy()


if __name__ == "__main__":
    main()