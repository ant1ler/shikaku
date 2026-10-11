APP_NAME = "Shikaku"
APP_VERSION = "2.2.0"

BOARD_SIZES = [3, 6, 9, 15, 25, 30]

CELL_SIZES = {
    3: 130, 6: 84, 9: 62, 15: 44,
    25: 32, 30: 28,
}

CELL_SCALE = {
    "compact": 0.8,
    "normal": 1.0,
    "large": 1.25,
}


# ===================== ШРИФТЫ =====================

FONT_BODY       = ("Jost*", 11)
FONT_BODY_MED   = ("Jost* Medium", 11)
FONT_BODY_SEMI  = ("Jost* Semi", 12)
FONT_SMALL      = ("Jost*", 10)
FONT_CAPTION    = ("Jost* Medium", 9)

FONT_UI         = FONT_BODY
FONT_UI_BIG     = ("Jost* Semi", 13)

FONT_LOGO       = ("Clash", 44, "bold")
FONT_DISPLAY    = ("Clash", 22)
FONT_DISPLAY_B  = ("Clash", 22, "bold")

FONT_TITLE      = ("Schueler SuperXP", 32)
FONT_HEADLINE   = ("Schueler SuperXP", 22)

FONT_TIMER      = ("Jost* Semi", 16, "bold")
FONT_NUM_BIG    = ("Jost*", 72, "bold")
FONT_NUM_MED    = ("Jost*", 26, "bold")

FONT_CLUE       = "Jost*"


# ===================== ТЁМНАЯ ТЕМА =====================

DARK_THEME = {
    "COLOR_BG":           "#2a1e48",
    "COLOR_PANEL":        "#322452",
    "COLOR_PANEL_HOVER":  "#3f2d63",
    "COLOR_PANEL_EDGE":   "#4a3570",
    "COLOR_CELL":         "#1e1638",
    "COLOR_CELL_ALT":     "#221a3d",
    "COLOR_GRID":         "#1e1638",
    "COLOR_GRID_LIGHT":   "#5a4088",

    "COLOR_GRID_NEON":    "#ffd8ec",
    "COLOR_FIELD_GLOW":   "#8a5fd8",
    "COLOR_FIELD_BG":     "#1e1638",

    "COLOR_TEXT":         "#f8f4ff",
    "COLOR_TEXT_DIM":     "#b8a8d8",

    "COLOR_ACCENT":       "#ff7fd0",
    "COLOR_ACCENT_HOVER": "#ff9fdc",
    "COLOR_ACCENT2":      "#7fd0ff",
    "COLOR_SUCCESS":      "#7fffc0",
    "COLOR_DANGER":       "#ff7fa0",
    "COLOR_PREVIEW":      "#7fd0ff",
    "COLOR_CLUE":         "#ffffff",

    "COLOR_RECT_INVALID":        "#5a2a48",
    "COLOR_RECT_INVALID_STROKE": "#ff7fa0",
    "COLOR_OVERLAY_BG":   "#1e1438",
    "COLOR_CARD_BG":      "#4a3570",
    "COLOR_WIN_SHADOW":   "#1a1030",
    "COLOR_ICON_DARK":    "#2a1e48",

    "GRADIENT_TOP":       "#4a3570",
    "GRADIENT_MID":       "#3a2a5c",
    "GRADIENT_BOTTOM":    "#2a1e48",
    "BG_STRIPE1":         "#ff7fd0",
    "BG_STRIPE2":         "#7fd0ff",
    "BG_STRIPE3":         "#7fffc0",
    "BG_GLOW1":           "#ff7fd0",
    "BG_GLOW2":           "#7fd0ff",
    "BG_GLOW3":           "#7fffc0",
    "BG_SPARK_COLOR":     "#ffffff",

    "RECT_PALETTE": [
        "#ff9fd0", "#7fbfff", "#7fffc0", "#ffd07f",
        "#b89fff", "#9fd0ff", "#ffb8dc", "#9fffe0",
        "#ffc89f", "#c8b8ff", "#ff9fe8", "#b8e0ff",
    ],
    "RECT_STROKE_PALETTE": [
        "#ff7fd0", "#7fbfff", "#7fffc0", "#ffd07f",
        "#b89fff", "#9fd0ff", "#ffb8dc", "#9fffe0",
        "#ffc89f", "#c8b8ff", "#ff9fe8", "#b8e0ff",
    ],
}

# ===================== СВЕТЛАЯ ТЕМА =====================

LIGHT_THEME = {
    "COLOR_BG":           "#f0e8f5",
    "COLOR_PANEL":        "#e8dff0",
    "COLOR_PANEL_HOVER":  "#ddd0e8",
    "COLOR_PANEL_EDGE":   "#c8b8d8",
    "COLOR_CELL":         "#f9f4fc",
    "COLOR_CELL_ALT":     "#f2ecf6",
    "COLOR_GRID":         "#e8d8f0",
    "COLOR_GRID_LIGHT":   "#e8d8f0",

    "COLOR_GRID_NEON":    "#6a2a9c",
    "COLOR_FIELD_GLOW":   "#e0c8f0",
    "COLOR_FIELD_BG":     "#f9f4fc",

    "COLOR_TEXT":         "#1a0e2e",
    "COLOR_TEXT_DIM":     "#5a4a78",

    "COLOR_ACCENT":       "#d6338f",
    "COLOR_ACCENT_HOVER": "#e84ba5",
    "COLOR_ACCENT2":      "#2a7acc",
    "COLOR_SUCCESS":      "#1faa6e",
    "COLOR_DANGER":       "#d63a5a",
    "COLOR_PREVIEW":      "#2a7acc",
    "COLOR_CLUE":         "#ffffff",

    "COLOR_RECT_INVALID":        "#fbe0ec",
    "COLOR_RECT_INVALID_STROKE": "#d63a5a",
    "COLOR_OVERLAY_BG":   "#ede0f5",
    "COLOR_CARD_BG":      "#f9f4fc",
    "COLOR_WIN_SHADOW":   "#d0c0e0",
    "COLOR_ICON_DARK":    "#ffffff",

    "GRADIENT_TOP":       "#faf4ff",
    "GRADIENT_MID":       "#f0e4f8",
    "GRADIENT_BOTTOM":    "#e8d8f0",

    "BG_STRIPE1":         "#ffb8dc",
    "BG_STRIPE2":         "#b8dcff",
    "BG_STRIPE3":         "#b8f0d8",
    "BG_GLOW1":           "#ffc8e0",
    "BG_GLOW2":           "#c8e0ff",
    "BG_GLOW3":           "#c8f0dc",
    "BG_SPARK_COLOR":     "#b8a8d8",

    "RECT_PALETTE": [
        "#ff9fd0", "#7fbfff", "#7fffc0", "#ffd07f",
        "#b89fff", "#9fd0ff", "#ffb8dc", "#9fffe0",
        "#ffc89f", "#c8b8ff", "#ff9fe8", "#b8e0ff",
    ],
    "RECT_STROKE_PALETTE": [
        "#d6338f", "#2a7acc", "#1faa6e", "#c88a1f",
        "#7a4fd6", "#4f7fd6", "#d65f95", "#4fc8a8",
        "#d6805a", "#7f8fd6", "#d62aa8", "#5fb8d6",
    ],
}

THEMES = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
}

_active_theme_name = "dark"


def set_theme(name: str):
    global _active_theme_name
    if name in THEMES and _active_theme_name != name:
        _active_theme_name = name
        try:
            from .ui.theme import clear_bg_cache
            clear_bg_cache()
        except Exception:
            pass


def current_theme() -> str:
    return _active_theme_name


def C(key: str):
    return THEMES[_active_theme_name].get(key, "#ff00ff")


# ===================== НАЗВАНИЯ РЕЖИМОВ =====================

MODE_LABELS = {
    "normal": "Обычная игра",
    "cascade": "Серия из 5",
    "cascade_growing": "Растущая серия",
    "timed": "На время",
    "blind": "Слепой режим",
    "daily": "Ежедневный вызов",
}

MODE_DESCRIPTIONS = {
    "normal": (
        "Решай один пазл выбранного размера. Время идёт, рекорд сохраняется. "
        "Идеально для тренировки."
    ),
    "cascade": (
        "Пройди 5 уровней выбранного размера подряд. Время не сбрасывается "
        "между уровнями — все 5 идут в общий рекорд. Отдыхать некогда."
    ),
    "cascade_growing": (
        "Шесть уровней с растущим размером: 3×3 → 6×6 → 9×9 → 15×15 → 25×25 → 30×30. "
        "Время копится, подсказки обновляются на каждом этапе. Настоящий марафон."
    ),
    "timed": (
        "Тот же пазл, но с ограничением по времени. На 3×3 — 15 секунд, "
        "на 30×30 — 8 минут. Успел — рекорд по остатку. Не успел — экран проигрыша."
    ),
    "blind": (
        "Прямоугольники не подсвечиваются цветом — только контуры. "
        "Настоящее испытание на внимательность. Цвета проявляются "
        "после победы."
    ),
    "daily": (
        "Один пазл в день на каждый размер. Пазл одинаковый у всех игроков "
        "и меняется в полночь. Проходи каждый день, чтобы поддерживать серию."
    ),
}


# ===================== ОСТАЛЬНОЕ =====================

SAVE_FILE = "shikaku_save.json"
RECORDS_FILE = "shikaku_records.json"
DAILY_FILE = "shikaku_daily.json"
SETTINGS_FILE = "settings.json"

WALLPAPERS_DIR = "wallpapers"
WALLPAPER_DARK = "dark.jpg"
WALLPAPER_LIGHT = "light.jpg"

HISTORY_LIMIT = 100

HINT_LIMIT = 3
HINT_PENALTY = 15
CHECK_PENALTY = 5
FLASH_TIMES = 6
FLASH_INTERVAL = 130

CASCADE_LEVELS = 5
CASCADE_RECORD_SUFFIX = "cascade"

# растущая серия — 6 уровней разных размеров
CASCADE_GROWING_SIZES = [3, 6, 9, 15, 25, 30]
CASCADE_GROWING_SUFFIX = "cascade_growing"

TIME_LIMITS = {
    3: 15, 6: 40, 9: 90, 15: 180,
    25: 360, 30: 480,
}
TIMED_RECORD_SUFFIX = "timed"
TIMED_HINT_PENALTY = 5
TIMED_CHECK_PENALTY = 2