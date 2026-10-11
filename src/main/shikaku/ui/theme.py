import math
import os
import shutil
import tkinter as tk
from .. import config as cfg

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ==================== КОНТЕКСТЫ ====================

CONTEXTS = [
    "menu",
    "game_3", "game_6", "game_9", "game_15", "game_25", "game_30",
    "rules",
    "settings",
]

CONTEXT_LABELS = {
    "menu": "Главное меню",
    "game_3": "Игра 3×3",
    "game_6": "Игра 6×6",
    "game_9": "Игра 9×9",
    "game_15": "Игра 15×15",
    "game_25": "Игра 25×25",
    "game_30": "Игра 30×30",
    "rules": "Правила",
    "settings": "Настройки",
}


# ==================== УТИЛИТЫ ====================

def format_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def mix_colors(c1: str, c2: str, t: float) -> str:
    a = _hex_to_rgb(c1)
    b = _hex_to_rgb(c2)
    r = int(a[0] + (b[0] - a[0]) * t)
    g = int(a[1] + (b[1] - a[1]) * t)
    bl = int(a[2] + (b[2] - a[2]) * t)
    return _rgb_to_hex((r, g, bl))


def round_rect(canvas: tk.Canvas, x1, y1, x2, y2, r, **kwargs):
    r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def make_accent_bar(parent, height=3, color=None):
    color = color or cfg.C("COLOR_ACCENT")
    bar = tk.Frame(parent, bg=color, height=height)
    bar.pack(fill="x", side="top")
    return bar


def divider(parent, padx=0, pady=6, color=None):
    color = color or cfg.C("COLOR_PANEL_EDGE")
    line = tk.Frame(parent, bg=color, height=1)
    line.pack(fill="x", padx=padx, pady=pady)
    return line


# ==================== ОБОИ ====================

def wallpapers_dir() -> str:
    return os.path.join(os.getcwd(), cfg.WALLPAPERS_DIR)


def wallpaper_path(context: str, theme: str = None) -> str:
    if theme is None:
        theme = cfg.current_theme()
    filename = f"{context}.jpg"
    return os.path.join(wallpapers_dir(), theme, filename)


def has_wallpaper(context: str, theme: str = None) -> bool:
    return os.path.exists(wallpaper_path(context, theme))


def set_wallpaper(src_path: str, context: str, theme: str = None) -> bool:
    try:
        if theme is None:
            theme = cfg.current_theme()
        theme_dir = os.path.join(wallpapers_dir(), theme)
        os.makedirs(theme_dir, exist_ok=True)
        dst = os.path.join(theme_dir, f"{context}.jpg")
        shutil.copy(src_path, dst)
        clear_bg_cache()
        return True
    except (OSError, shutil.SameFileError):
        return False


def delete_wallpaper(context: str, theme: str = None) -> bool:
    try:
        if theme is None:
            theme = cfg.current_theme()
        path = wallpaper_path(context, theme)
        if os.path.exists(path):
            os.remove(path)
            clear_bg_cache()
        return True
    except OSError:
        return False


# ==================== ДЕКОРАТИВНЫЙ ФОН (PIL) ====================

_BG_CACHE = {}
_BG_CACHE_MAX = 16


def clear_bg_cache():
    _BG_CACHE.clear()


def _make_gradient_bg(width: int, height: int,
                      context: str = "menu") -> "Image.Image | None":
    top = _hex_to_rgb(cfg.C("GRADIENT_TOP"))
    mid = _hex_to_rgb(cfg.C("GRADIENT_MID"))
    bottom = _hex_to_rgb(cfg.C("GRADIENT_BOTTOM"))

    darken = 0.0
    if context == "game_30":
        darken = 0.15
    elif context == "game_25":
        darken = 0.10
    elif context == "game_15":
        darken = 0.05
    elif context == "game_3":
        darken = -0.05

    def adjust(c):
        r, g, b = c
        if darken > 0:
            r = int(r * (1 - darken))
            g = int(g * (1 - darken))
            b = int(b * (1 - darken))
        elif darken < 0:
            r = min(255, int(r * (1 - darken)))
            g = min(255, int(g * (1 - darken)))
            b = min(255, int(b * (1 - darken)))
        return (r, g, b)

    top = adjust(top)
    mid = adjust(mid)
    bottom = adjust(bottom)

    grad = Image.new("RGB", (1, height))
    for y in range(height):
        t = y / max(1, height - 1)
        if t < 0.5:
            tt = t / 0.5
            c = tuple(int(top[i] + (mid[i] - top[i]) * tt) for i in range(3))
        else:
            tt = (t - 0.5) / 0.5
            c = tuple(int(mid[i] + (bottom[i] - mid[i]) * tt) for i in range(3))
        grad.putpixel((0, y), c)
    img = grad.resize((width, height), Image.NEAREST)

    blur_radius = max(30, width // 10)

    stripes = [
        (-0.30, 0.05, 0.55, 0.55, "BG_STRIPE1", 0.22),
        ( 0.45, -0.10, 1.20, 0.35, "BG_STRIPE2", 0.20),
        (-0.20, 0.55, 0.60, 1.15, "BG_STRIPE3", 0.14),
        ( 0.55,  0.45, 1.30, 0.95, "BG_STRIPE1", 0.16),
        ( 0.10,  0.30, 0.90, 0.75, "BG_STRIPE2", 0.10),
    ]
    for (x1r, y1r, x2r, y2r, color_key, blend) in stripes:
        layer = Image.new("RGB", (width, height), (0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse(
            [int(width * x1r), int(height * y1r),
             int(width * x2r), int(height * y2r)],
            fill=_hex_to_rgb(cfg.C(color_key))
        )
        layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        img = Image.blend(img, layer, blend)

    glows = [
        (-0.25, -0.35, 0.45, 0.35, "BG_GLOW1", 0.20),
        ( 0.60,  0.55, 1.30, 1.30, "BG_GLOW2", 0.20),
        (-0.35,  0.45, 0.35, 1.15, "BG_GLOW3", 0.12),
    ]
    for (x1r, y1r, x2r, y2r, color_key, blend) in glows:
        layer = Image.new("RGB", (width, height), (0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse(
            [int(width * x1r), int(height * y1r),
             int(width * x2r), int(height * y2r)],
            fill=_hex_to_rgb(cfg.C(color_key))
        )
        layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        img = Image.blend(img, layer, blend)

    img = img.convert("RGBA")

    sparks = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sparks)
    spark_color_hex = cfg.C("BG_SPARK_COLOR")
    sr, sg, sb = _hex_to_rgb(spark_color_hex)

    import random
    rng = random.Random(hash(context) & 0xffffffff)
    for _ in range(40):
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        r = rng.choice([1, 2, 2, 3, 3, 4])
        a = rng.randint(120, 230)
        if r >= 3:
            halo = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            hd = ImageDraw.Draw(halo)
            hd.ellipse([cx - r*3, cy - r*3, cx + r*3, cy + r*3],
                       fill=(sr, sg, sb, int(a * 0.3)))
            halo = halo.filter(ImageFilter.GaussianBlur(radius=r * 2))
            sparks = Image.alpha_composite(sparks, halo)
            sd = ImageDraw.Draw(sparks)
        sd.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=(sr, sg, sb, a))

    return Image.alpha_composite(img, sparks)


def _make_wallpaper_bg(width: int, height: int, theme: str,
                       context: str) -> "Image.Image | None":
    if not PIL_AVAILABLE:
        return None

    path = wallpaper_path(context, theme)

    if not os.path.exists(path):
        fallback = wallpaper_path("menu", theme)
        if os.path.exists(fallback):
            path = fallback
        else:
            return None

    try:
        img = Image.open(path).convert("RGB")
    except Exception:
        return None

    src_w, src_h = img.size
    src_ratio = src_w / src_h
    dst_ratio = width / height

    if src_ratio > dst_ratio:
        new_w = int(src_h * dst_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / dst_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))

    img = img.resize((width, height), Image.LANCZOS)
    return img


def make_decorated_bg(width: int, height: int,
                      context: str = "menu") -> "ImageTk.PhotoImage | None":
    if not PIL_AVAILABLE or width < 20 or height < 20:
        return None

    theme = cfg.current_theme()
    key = (width, height, theme, context)
    if key in _BG_CACHE:
        return _BG_CACHE[key]

    img = _make_wallpaper_bg(width, height, theme, context)
    if img is None:
        img = _make_gradient_bg(width, height, context)

    if img is None:
        return None

    result = ImageTk.PhotoImage(img.convert("RGB"))
    if len(_BG_CACHE) >= _BG_CACHE_MAX:
        _BG_CACHE.pop(next(iter(_BG_CACHE)))
    _BG_CACHE[key] = result
    return result


class BgCanvas(tk.Canvas):
    """Canvas с фоновой картинкой (по контексту)."""

    def __init__(self, master, context: str = "menu"):
        bg_color = cfg.C("COLOR_BG")
        super().__init__(master, bg=bg_color, highlightthickness=0, bd=0)

        self._bg_color = bg_color
        self._context = context
        self._img = None
        self._img_item = None
        self._job = None
        self._last_size = (0, 0)
        self._last_theme = cfg.current_theme()

        self._img_item = self.create_image(0, 0, anchor="nw", tags="bg_image")

        self.bind("<Configure>", self._on_resize, add="+")
        self.after(20, self.redraw_bg)

    def set_context(self, context: str):
        if context == self._context:
            return
        self._context = context
        self.redraw_bg()

    def _on_resize(self, event=None):
        w = self.winfo_width()
        h = self.winfo_height()
        theme = cfg.current_theme()
        if (w, h) == self._last_size and theme == self._last_theme:
            return
        if self._job:
            try:
                self.after_cancel(self._job)
            except tk.TclError:
                pass
        self._job = self.after(200, self.redraw_bg)

    def redraw_bg(self):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 20 or h < 20:
            return

        if not self.find_withtag("bg_image"):
            self._img_item = self.create_image(0, 0, anchor="nw",
                                               tags="bg_image")
        else:
            self._img_item = self.find_withtag("bg_image")[0]

        theme = cfg.current_theme()
        if (w, h) == self._last_size and theme == self._last_theme \
                and self._img is not None:
            return
        self._last_size = (w, h)
        self._last_theme = theme

        img = make_decorated_bg(w, h, context=self._context)
        if img is None:
            return
        self._img = img
        self.itemconfigure(self._img_item, image=img)
        self.tag_lower("bg_image")


class DecoratedBackground:
    """Совместимость со старым API — обёртка над BgCanvas."""

    def __init__(self, parent, context: str = "menu"):
        self.parent = parent
        self.canvas = BgCanvas(parent, context=context)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        # опускаем виджет ниже siblings (у Canvas свой lower() для тегов)
        tk.Misc.lower(self.canvas)

    def destroy(self):
        try:
            self.canvas.destroy()
        except tk.TclError:
            pass


# ==================== ЖИДКОЕ СТЕКЛО ====================

def make_glass_card(width: int, height: int, radius: int = 18,
                    alpha: float = 0.14,
                    glow_color: str = None) -> "ImageTk.PhotoImage | None":
    if not PIL_AVAILABLE or width < 4 or height < 4:
        return None

    glow_color = glow_color or cfg.C("COLOR_ACCENT")
    shadow_pad = 30
    cw = width + shadow_pad * 2
    ch = height + shadow_pad * 2

    glow = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle(
        [shadow_pad, shadow_pad,
         shadow_pad + width, shadow_pad + height],
        radius=radius,
        outline=_hex_to_rgb(glow_color) + (200,),
        width=2
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=12))

    glass = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(glass)
    gd2.rounded_rectangle(
        [shadow_pad, shadow_pad,
         shadow_pad + width, shadow_pad + height],
        radius=radius,
        fill=(255, 255, 255, int(255 * alpha))
    )

    border = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    bd = ImageDraw.Draw(border)
    bd.rounded_rectangle(
        [shadow_pad, shadow_pad,
         shadow_pad + width, shadow_pad + height],
        radius=radius,
        outline=_hex_to_rgb(glow_color) + (240,),
        width=2
    )

    highlight = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    hd = ImageDraw.Draw(highlight)
    hd.rounded_rectangle(
        [shadow_pad + 8, shadow_pad + 3,
         shadow_pad + width - 8, shadow_pad + 9],
        radius=4,
        fill=(255, 255, 255, 70)
    )
    highlight = highlight.filter(ImageFilter.GaussianBlur(radius=3))

    result = Image.alpha_composite(glow, glass)
    result = Image.alpha_composite(result, border)
    result = Image.alpha_composite(result, highlight)

    return ImageTk.PhotoImage(result)


class GlassCard(tk.Frame):
    def __init__(self, master, width: int, height: int,
                 radius: int = 18, alpha: float = 0.14,
                 bg: str | None = None,
                 glow_color: str | None = None):
        bg_color = bg or cfg.C("COLOR_BG")
        super().__init__(master, bg=bg_color, highlightthickness=0, bd=0)

        self._width = width
        self._height = height
        self._radius = radius
        self._alpha = alpha
        self._bg_color = bg_color
        self._glow_color = glow_color
        self._pad = 30

        total_w = width + self._pad * 2
        total_h = height + self._pad * 2

        self.canvas = tk.Canvas(self, bg=bg_color,
                                highlightthickness=0, bd=0)
        self.canvas.configure(width=total_w, height=total_h)
        self.canvas.pack()

        self._glass_img = None
        self._redraw()

        self.content = tk.Frame(self.canvas, bg=bg_color)
        self.canvas.create_window(
            total_w // 2, total_h // 2,
            window=self.content,
            anchor="center"
        )

    def _redraw(self):
        self.canvas.delete("glass")
        img = make_glass_card(self._width, self._height,
                              radius=self._radius,
                              alpha=self._alpha,
                              glow_color=self._glow_color)
        if img is None:
            return
        self._glass_img = img
        self.canvas.create_image(0, 0, image=img, anchor="nw", tags="glass")
        self.canvas.tag_lower("glass")


# ==================== КНОПКА ====================

class FlatButton(tk.Frame):
    def __init__(self, master, text, command=None,
                 width=120, height=40,
                 bg=None, fg=None,
                 hover_bg=None, accent=False, danger=False,
                 font=None):
        bg = bg or cfg.C("COLOR_PANEL")
        fg = fg or cfg.C("COLOR_TEXT")
        hover_bg = hover_bg or cfg.C("COLOR_PANEL_HOVER")

        if accent:
            self._base_bg = cfg.C("COLOR_ACCENT")
            self._hover_bg = cfg.C("COLOR_ACCENT_HOVER")
            self._fg = "#ffffff"
        elif danger:
            self._base_bg = mix_colors(cfg.C("COLOR_DANGER"), cfg.C("COLOR_BG"), 0.75)
            self._hover_bg = mix_colors(cfg.C("COLOR_DANGER"), cfg.C("COLOR_BG"), 0.6)
            self._fg = cfg.C("COLOR_DANGER")
        else:
            self._base_bg = bg
            self._hover_bg = hover_bg
            self._fg = fg

        self._command = command
        self._font = font or cfg.FONT_BODY_MED

        super().__init__(master, bg=self._base_bg,
                         highlightthickness=0, bd=0)
        self.configure(width=width, height=height)
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.label = tk.Label(self, text=text,
                              font=self._font,
                              fg=self._fg, bg=self._base_bg,
                              cursor="hand2")
        self.label.pack(expand=True, fill="both")

        for w in (self, self.label):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_click)

    def _on_enter(self, _):
        self.configure(bg=self._hover_bg)
        self.label.configure(bg=self._hover_bg)

    def _on_leave(self, _):
        self.configure(bg=self._base_bg)
        self.label.configure(bg=self._base_bg)

    def _on_click(self, _):
        if self._command:
            self._command()

    def set_text(self, text):
        self.label.configure(text=text)


# ==================== ПОЛЕ ====================

def draw_field_bg(canvas: tk.Canvas, n, cell):
    for r in range(n):
        for c in range(n):
            color = cfg.C("COLOR_CELL")
            canvas.create_rectangle(
                c * cell, r * cell, (c + 1) * cell, (r + 1) * cell,
                fill=color, outline=""
            )


def draw_grid(canvas: tk.Canvas, n, cell):
    for i in range(n + 1):
        canvas.create_line(i * cell, 0, i * cell, n * cell,
                           fill=cfg.C("COLOR_GRID_NEON"), width=1)
        canvas.create_line(0, i * cell, n * cell, i * cell,
                           fill=cfg.C("COLOR_GRID_NEON"), width=1)


# ==================== ОВЕРЛЕЙ ====================

class Overlay(tk.Frame):
    def __init__(self, parent, bg=None, context: str = "menu"):
        bg = bg or cfg.C("COLOR_OVERLAY_BG")
        super().__init__(parent, bg=bg)
        self._context = context
        self._bg_decoration = None

    def show(self):
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        self._bg_decoration = DecoratedBackground(self, context=self._context)

    def hide(self):
        self.place_forget()


class ErrorFlash:
    FRAME_MS = 16
    DURATION = 900
    EDGE_THICKNESS = 4

    def __init__(self, parent, color=None, bg=None):
        self.parent = parent
        self.color = color or cfg.C("COLOR_DANGER")
        self.bg = bg or cfg.C("COLOR_BG")
        self._edge_frames = []
        self._job = None
        self._start_ts = 0

    def flash(self, rect=None, board_view=None):
        self._cancel()
        self._create_edges()
        self._start_ts = self._now()
        self._tick()

    @staticmethod
    def _now():
        import time
        return time.time() * 1000

    def _cancel(self):
        if self._job:
            try:
                self.parent.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None
        for f in self._edge_frames:
            try:
                f.destroy()
            except tk.TclError:
                pass
        self._edge_frames = []

    def _create_edges(self):
        t = self.EDGE_THICKNESS
        p = self.parent
        color = self.color
        top = tk.Frame(p, bg=color)
        top.place(x=0, y=0, relwidth=1, height=t)
        bottom = tk.Frame(p, bg=color)
        bottom.place(x=0, rely=1.0, y=-t, relwidth=1, height=t)
        left = tk.Frame(p, bg=color)
        left.place(x=0, y=0, relheight=1, width=t)
        right = tk.Frame(p, bg=color)
        right.place(relx=1.0, x=-t, y=0, relheight=1, width=t)
        self._edge_frames = [top, bottom, left, right]
        for f in self._edge_frames:
            f.lift()

    def _mix_to_bg(self, color, fade):
        return mix_colors(color, self.bg, fade)

    def _tick(self):
        now = self._now()
        elapsed = now - self._start_ts
        t = elapsed / self.DURATION
        if t >= 1.0:
            self._cancel()
            return

        base = 1 - t
        pulse = 0.6 + 0.4 * math.cos(6 * math.pi * t)
        intensity = base * pulse
        fade = 1 - intensity

        color = self._mix_to_bg(self.color, fade)
        for f in self._edge_frames:
            try:
                f.configure(bg=color)
            except tk.TclError:
                pass

        self._job = self.parent.after(self.FRAME_MS, self._tick)


# ==================== КАРТОЧКИ ====================

class WinCard(tk.Frame):
    SLIDE_FRAMES = 40
    SLIDE_INTERVAL = 20
    COUNT_FRAMES = 60
    COUNT_INTERVAL = 24
    PULSE_FRAMES = 120
    PULSE_INTERVAL = 40

    def __init__(self, master, on_replay, on_menu):
        super().__init__(master, bg=cfg.C("COLOR_BG"))
        self.on_replay = on_replay
        self.on_menu = on_menu
        self._jobs = []
        self._pulsing = False

    def _schedule(self, ms, fn):
        job = self.after(ms, fn)
        self._jobs.append(job)

    def _cancel_all(self):
        for j in self._jobs:
            try:
                self.after_cancel(j)
            except tk.TclError:
                pass
        self._jobs.clear()
        self._pulsing = False

    def build(self, size, elapsed, is_record, best_before,
              best_after, rects_count, moves, ideal_count,
              cascade=False, cascade_total=0, timed=False, daily=False,
              daily_streak=0):
        self._cancel_all()
        for w in self.winfo_children():
            w.destroy()

        accent = cfg.C("COLOR_SUCCESS") if is_record else cfg.C("COLOR_ACCENT")

        self._accent_bar = tk.Frame(self, bg=accent, height=3)
        self._accent_bar.pack(fill="x", side="top")

        center = tk.Frame(self, bg=cfg.C("COLOR_BG"))
        center.pack(expand=True, fill="both")

        self._icon_canvas = tk.Canvas(center, width=72, height=72,
                                      bg=cfg.C("COLOR_BG"),
                                      highlightthickness=0, bd=0)
        self._icon_canvas.pack(pady=(0, 24))
        self._draw_icon(accent, is_record)

        if daily:
            title = "ЕЖЕДНЕВНЫЙ ВЫПОЛНЕН"
        elif cascade:
            title = "КАСКАД ПРОЙДЕН"
        elif timed:
            title = "УСПЕЛ!"
        elif is_record:
            title = "НОВЫЙ РЕКОРД"
        else:
            title = "ПОБЕДА"

        self._title_lbl = tk.Label(center, text=title,
                                   font=cfg.FONT_TITLE,
                                   fg=accent, bg=cfg.C("COLOR_BG"))
        self._title_lbl.pack()

        if daily:
            subtitle = f"ежедневный вызов · поле {size} × {size}"
        elif cascade:
            subtitle = f"{cascade_total} уровней · поле {size} × {size}"
        elif timed:
            subtitle = f"на время · поле {size} × {size}"
        else:
            subtitle = f"поле {size} × {size}"

        tk.Label(center, text=subtitle,
                 font=cfg.FONT_CAPTION,
                 fg=cfg.C("COLOR_TEXT_DIM"), bg=cfg.C("COLOR_BG")
                 ).pack(pady=(6, 40))

        self._time_lbl = tk.Label(center, text="00:00",
                                  font=cfg.FONT_NUM_BIG,
                                  fg=cfg.C("COLOR_TEXT"), bg=cfg.C("COLOR_BG"))
        self._time_lbl.pack()

        if timed:
            time_label = "ОСТАЛОСЬ ВРЕМЕНИ"
        elif cascade:
            time_label = "ОБЩЕЕ ВРЕМЯ"
        else:
            time_label = "ВАШЕ ВРЕМЯ"

        tk.Label(center, text=time_label,
                 font=cfg.FONT_CAPTION,
                 fg=cfg.C("COLOR_TEXT_DIM"), bg=cfg.C("COLOR_BG")
                 ).pack(pady=(2, 20))

        if daily and daily_streak > 0:
            sub = f"🔥  серия: {daily_streak} дней подряд"
            sub_color = cfg.C("COLOR_SUCCESS")
        elif is_record:
            if best_before is not None:
                sub = f"предыдущий рекорд — {format_time(best_before)}"
            else:
                sub = "первая победа на этом размере"
            sub_color = cfg.C("COLOR_SUCCESS")
        else:
            if best_after is not None:
                if timed:
                    diff = best_after - elapsed
                    sub = (f"до рекорда -{format_time(diff)}"
                           f"   ·   рекорд {format_time(best_after)}")
                else:
                    diff = elapsed - best_after
                    sub = (f"до рекорда +{format_time(diff)}"
                           f"   ·   рекорд {format_time(best_after)}")
            else:
                sub = "рекорд пока не установлен"
            sub_color = cfg.C("COLOR_TEXT_DIM")

        tk.Label(center, text=sub,
                 font=cfg.FONT_BODY,
                 fg=sub_color, bg=cfg.C("COLOR_BG")
                 ).pack(pady=(0, 50))

        efficiency = 0
        if ideal_count:
            efficiency = int(round(ideal_count / max(rects_count, 1) * 100))
        efficiency = min(efficiency, 100)

        stats_row = tk.Frame(center, bg=cfg.C("COLOR_BG"))
        stats_row.pack(pady=(0, 50))

        self._stat_card(stats_row, "ПРЯМОУГОЛЬНИКИ",
                        str(rects_count), icon="grid", accent=accent)
        self._stat_card(stats_row, "ХОДЫ",
                        str(moves), icon="refresh", accent=accent)
        self._stat_card(stats_row, "ЭФФЕКТИВНОСТЬ",
                        f"{efficiency}%", icon="target", accent=accent)

        btns = tk.Frame(center, bg=cfg.C("COLOR_BG"))
        btns.pack(pady=(0, 0))

        FlatButton(btns, "↻   ЕЩЁ РАЗ" if not daily else "↻   В МЕНЮ",
                   command=self.on_replay if not daily else self.on_menu,
                   width=260, height=56, accent=True).pack(side="left", padx=(0, 14))
        FlatButton(btns, "←   В МЕНЮ", command=self.on_menu,
                   width=260, height=56).pack(side="left")

        self._start_time_rollup(elapsed)
        if is_record or daily:
            self._schedule(400, lambda: self._start_pulse(accent))

    def _draw_icon(self, accent, is_record):
        cv = self._icon_canvas
        cv.delete("all")
        dark = cfg.C("COLOR_ICON_DARK")
        for i in range(6, 0, -1):
            r = 36 + i * 3
            col = mix_colors(accent, cfg.C("COLOR_BG"), i / 8)
            cv.create_oval(36 - r, 36 - r, 36 + r, 36 + r,
                           fill="", outline=col, width=2)
        cv.create_oval(2, 2, 70, 70, fill=accent, outline="")
        if is_record:
            cv.create_polygon(24, 24, 48, 24, 44, 42, 28, 42,
                              fill=dark, outline="")
            cv.create_rectangle(33, 42, 39, 50, fill=dark, outline="")
            cv.create_rectangle(26, 50, 46, 54, fill=dark, outline="")
            cv.create_arc(14, 24, 30, 44, start=90, extent=180,
                          style="arc", outline=dark, width=3)
            cv.create_arc(42, 24, 58, 44, start=270, extent=180,
                          style="arc", outline=dark, width=3)
        else:
            cv.create_line(24, 38, 34, 48, width=6,
                           fill=dark, capstyle="round")
            cv.create_line(34, 48, 50, 26, width=6,
                           fill=dark, capstyle="round")

    def _start_time_rollup(self, final_elapsed):
        total_frames = self.COUNT_FRAMES
        interval = self.COUNT_INTERVAL

        def tick(i=0):
            if i > total_frames:
                self._time_lbl.config(text=format_time(final_elapsed))
                return
            t = i / total_frames
            eased = 1 - (1 - t) ** 2
            current = final_elapsed * eased
            self._time_lbl.config(text=format_time(current))
            self._schedule(interval, lambda: tick(i + 1))

        tick(0)

    def _start_pulse(self, base_color):
        frames = self.PULSE_FRAMES
        interval = self.PULSE_INTERVAL
        br = _hex_to_rgb(base_color)
        tr = tuple(min(255, int(c + (255 - c) * 0.45)) for c in br)
        self._pulsing = True

        def tick(i=0):
            if not self._pulsing:
                return
            phase = math.sin(math.pi * i / frames)
            cr = int(br[0] + (tr[0] - br[0]) * phase)
            cg = int(br[1] + (tr[1] - br[1]) * phase)
            cb = int(br[2] + (tr[2] - br[2]) * phase)
            hex_color = f"#{cr:02x}{cg:02x}{cb:02x}"

            self._accent_bar.config(bg=hex_color)
            self._title_lbl.config(fg=hex_color)

            if i < frames:
                self._schedule(interval, lambda: tick(i + 1))
            else:
                self._accent_bar.config(bg=base_color)
                self._title_lbl.config(fg=base_color)
                self._pulsing = False

        tick(0)

    def _stat_card(self, parent, label, value, icon="grid", accent=None):
        accent = accent or cfg.C("COLOR_ACCENT")
        card_bg = cfg.C("COLOR_CARD_BG")
        card = tk.Frame(parent, bg=card_bg, padx=34, pady=22)
        card.pack(side="left", padx=8)

        cv = tk.Canvas(card, width=22, height=22,
                       bg=card_bg, highlightthickness=0, bd=0)
        cv.pack(anchor="w")

        if icon == "grid":
            for i in range(3):
                for j in range(3):
                    cv.create_rectangle(
                        2 + i * 7, 2 + j * 7,
                        2 + i * 7 + 5, 2 + j * 7 + 5,
                        fill=accent, outline=""
                    )
        elif icon == "refresh":
            cv.create_arc(3, 3, 19, 19, start=40, extent=280,
                          style="arc", outline=accent, width=3)
            cv.create_polygon(15, 3, 19, 6, 15, 9,
                              fill=accent, outline="")
        elif icon == "target":
            cv.create_oval(3, 3, 19, 19, outline=accent, width=3)
            cv.create_oval(8, 8, 14, 14, fill=accent, outline="")

        tk.Label(card, text=value,
                 font=cfg.FONT_NUM_MED,
                 fg=cfg.C("COLOR_TEXT"), bg=card_bg
                 ).pack(anchor="w", pady=(10, 0))

        tk.Label(card, text=label,
                 font=cfg.FONT_CAPTION,
                 fg=cfg.C("COLOR_TEXT_DIM"), bg=card_bg
                 ).pack(anchor="w", pady=(2, 0))


class LevelCard(tk.Frame):
    def __init__(self, master, on_continue):
        super().__init__(master, bg=cfg.C("COLOR_BG"))
        self.on_continue = on_continue

    def build(self, level: int, total: int, level_time: float,
              total_time: float, is_last: bool):
        for w in self.winfo_children():
            w.destroy()

        accent = cfg.C("COLOR_ACCENT")

        tk.Frame(self, bg=accent, height=3).pack(fill="x", side="top")

        center = tk.Frame(self, bg=cfg.C("COLOR_BG"))
        center.pack(expand=True, fill="both")

        icon = tk.Canvas(center, width=72, height=72,
                         bg=cfg.C("COLOR_BG"), highlightthickness=0, bd=0)
        icon.pack(pady=(0, 24))
        for i in range(5, 0, -1):
            r = 36 + i * 3
            col = mix_colors(accent, cfg.C("COLOR_BG"), i / 7)
            icon.create_oval(36 - r, 36 - r, 36 + r, 36 + r,
                             fill="", outline=col, width=2)
        icon.create_oval(2, 2, 70, 70, fill=accent, outline="")
        icon.create_text(36, 36, text=str(level),
                         font=("Jost* Semi", 26, "bold"),
                         fill=cfg.C("COLOR_ICON_DARK"))

        tk.Label(center, text="УРОВЕНЬ ПРОЙДЕН",
                 font=cfg.FONT_TITLE,
                 fg=accent, bg=cfg.C("COLOR_BG")).pack()

        tk.Label(center, text=f"этап {level} из {total}",
                 font=cfg.FONT_BODY,
                 fg=cfg.C("COLOR_TEXT_DIM"), bg=cfg.C("COLOR_BG")
                 ).pack(pady=(6, 40))

        tk.Label(center, text=format_time(level_time),
                 font=cfg.FONT_NUM_BIG,
                 fg=cfg.C("COLOR_TEXT"), bg=cfg.C("COLOR_BG")).pack()

        tk.Label(center, text="ВРЕМЯ ЭТАПА",
                 font=cfg.FONT_CAPTION,
                 fg=cfg.C("COLOR_TEXT_DIM"), bg=cfg.C("COLOR_BG")
                 ).pack(pady=(2, 20))

        tk.Label(center,
                 text=f"общее время: {format_time(total_time)}",
                 font=cfg.FONT_BODY,
                 fg=cfg.C("COLOR_TEXT"), bg=cfg.C("COLOR_BG")
                 ).pack(pady=(0, 50))

        btn_text = "🏁   ФИНИШ   [Enter]" if is_last else "▶   ПРОДОЛЖИТЬ   [Enter]"
        FlatButton(center, btn_text, command=self.on_continue,
                   width=320, height=56, accent=True).pack()


class LoseCard(tk.Frame):
    def __init__(self, master, on_replay, on_menu):
        super().__init__(master, bg=cfg.C("COLOR_BG"))
        self.on_replay = on_replay
        self.on_menu = on_menu

    def build(self, level: int, total: int, level_time: float,
              total_time: float, is_last: bool,
              next_size: int = None):
        for w in self.winfo_children():
            w.destroy()

        accent = cfg.C("COLOR_ACCENT")

        tk.Frame(self, bg=accent, height=3).pack(fill="x", side="top")

        center = tk.Frame(self, bg=cfg.C("COLOR_BG"))
        center.pack(expand=True, fill="both")

        icon = tk.Canvas(center, width=72, height=72,
                         bg=cfg.C("COLOR_BG"), highlightthickness=0, bd=0)
        icon.pack(pady=(0, 24))
        for i in range(5, 0, -1):
            r = 36 + i * 3
            col = mix_colors(accent, cfg.C("COLOR_BG"), i / 7)
            icon.create_oval(36 - r, 36 - r, 36 + r, 36 + r,
                             fill="", outline=col, width=2)
        icon.create_oval(2, 2, 70, 70, fill=accent, outline="")
        icon.create_text(36, 36, text=str(level),
                         font=("Jost* Semi", 26, "bold"),
                         fill=cfg.C("COLOR_ICON_DARK"))

        tk.Label(center, text="УРОВЕНЬ ПРОЙДЕН",
                 font=cfg.FONT_TITLE,
                 fg=accent, bg=cfg.C("COLOR_BG")).pack()

        tk.Label(center, text=f"этап {level} из {total}",
                 font=cfg.FONT_BODY,
                 fg=cfg.C("COLOR_TEXT_DIM"), bg=cfg.C("COLOR_BG")
                 ).pack(pady=(6, 20))

        # следующий уровень — если есть
        if next_size is not None and not is_last:
            tk.Label(center,
                     text=f"дальше: поле {next_size} × {next_size}",
                     font=("Jost* Semi", 14),
                     fg=cfg.C("COLOR_TEXT"),
                     bg=cfg.C("COLOR_BG")
                     ).pack(pady=(0, 20))
        else:
            tk.Label(center,
                     text="финальный уровень",
                     font=("Jost* Semi", 14),
                     fg=cfg.C("COLOR_TEXT_DIM"),
                     bg=cfg.C("COLOR_BG")
                     ).pack(pady=(0, 20))

        tk.Label(center, text=format_time(level_time),
                 font=cfg.FONT_NUM_BIG,
                 fg=cfg.C("COLOR_TEXT"), bg=cfg.C("COLOR_BG")).pack()

        tk.Label(center, text="ВРЕМЯ ЭТАПА",
                 font=cfg.FONT_CAPTION,
                 fg=cfg.C("COLOR_TEXT_DIM"), bg=cfg.C("COLOR_BG")
                 ).pack(pady=(2, 20))

        tk.Label(center,
                 text=f"общее время: {format_time(total_time)}",
                 font=cfg.FONT_BODY,
                 fg=cfg.C("COLOR_TEXT"), bg=cfg.C("COLOR_BG")
                 ).pack(pady=(0, 50))

        btn_text = "🏁   ФИНИШ   [Enter]" if is_last else "▶   ПРОДОЛЖИТЬ   [Enter]"
        FlatButton(center, btn_text, command=self.on_continue,
                   width=320, height=56, accent=True).pack()

    def _stat_card(self, parent, label, value, icon="grid"):
        accent = cfg.C("COLOR_DANGER")
        card_bg = cfg.C("COLOR_CARD_BG")
        card = tk.Frame(parent, bg=card_bg, padx=34, pady=22)
        card.pack(side="left", padx=8)

        cv = tk.Canvas(card, width=22, height=22,
                       bg=card_bg, highlightthickness=0, bd=0)
        cv.pack(anchor="w")

        if icon == "grid":
            for i in range(3):
                for j in range(3):
                    cv.create_rectangle(
                        2 + i * 7, 2 + j * 7,
                        2 + i * 7 + 5, 2 + j * 7 + 5,
                        fill=accent, outline=""
                    )
        elif icon == "refresh":
            cv.create_arc(3, 3, 19, 19, start=40, extent=280,
                          style="arc", outline=accent, width=3)
            cv.create_polygon(15, 3, 19, 6, 15, 9, fill=accent, outline="")

        tk.Label(card, text=value,
                 font=cfg.FONT_NUM_MED,
                 fg=cfg.C("COLOR_TEXT"), bg=card_bg
                 ).pack(anchor="w", pady=(10, 0))

        tk.Label(card, text=label,
                 font=cfg.FONT_CAPTION,
                 fg=cfg.C("COLOR_TEXT_DIM"), bg=card_bg
                 ).pack(anchor="w", pady=(2, 0))


class DailyCard(tk.Frame):
    def __init__(self, master, daily, on_start, on_close):
        super().__init__(master, bg=cfg.C("COLOR_BG"))
        self.daily = daily
        self.on_start = on_start
        self.on_close = on_close

    def build(self):
        for w in self.winfo_children():
            w.destroy()

        self.daily.reload()

        accent = cfg.C("COLOR_ACCENT")

        tk.Frame(self, bg=accent, height=3).pack(fill="x", side="top")

        center = tk.Frame(self, bg=cfg.C("COLOR_BG"))
        center.pack(expand=True, fill="both", padx=30, pady=(20, 20))

        icon = tk.Canvas(center, width=64, height=64,
                         bg=cfg.C("COLOR_BG"), highlightthickness=0, bd=0)
        icon.pack(pady=(0, 20))
        dark = cfg.C("COLOR_ICON_DARK")
        icon.create_oval(0, 0, 64, 64, fill=accent, outline="")
        icon.create_rectangle(20, 22, 44, 44, fill=dark, outline="")
        icon.create_rectangle(20, 18, 44, 24, fill=dark, outline="")
        icon.create_line(26, 22, 26, 26, fill=accent, width=2)
        icon.create_line(32, 22, 32, 26, fill=accent, width=2)
        icon.create_line(38, 22, 38, 26, fill=accent, width=2)
        icon.create_line(22, 34, 28, 40, width=3,
                         fill=accent, capstyle="round")
        icon.create_line(28, 40, 42, 28, width=3,
                         fill=accent, capstyle="round")

        tk.Label(center, text="Ежедневный вызов",
                 font=cfg.FONT_TITLE,
                 fg=accent, bg=cfg.C("COLOR_BG")).pack()

        tk.Label(center, text="Один пазл в день на каждый размер",
                 font=cfg.FONT_BODY,
                 fg=cfg.C("COLOR_TEXT_DIM"), bg=cfg.C("COLOR_BG")
                 ).pack(pady=(6, 0))

        streak = self.daily.streak()
        if streak > 0:
            streak_color = cfg.C("COLOR_SUCCESS")
            streak_text = f"🔥  Серия: {streak} дней подряд"
        else:
            streak_color = cfg.C("COLOR_TEXT_DIM")
            streak_text = "Начните серию сегодня"

        tk.Label(center, text=streak_text,
                 font=cfg.FONT_BODY_SEMI,
                 fg=streak_color, bg=cfg.C("COLOR_BG")
                 ).pack(pady=(16, 30))

        grid = tk.Frame(center, bg=cfg.C("COLOR_BG"))
        grid.pack(pady=(0, 30))

        for i, size in enumerate(cfg.BOARD_SIZES):
            r, c = divmod(i, 3)
            self._size_button(grid, r, c, size)

        FlatButton(center, "Закрыть", command=self.on_close,
                   width=200, height=44).pack()

    def _size_button(self, parent, row, col, size):
        done = self.daily.is_done(size)
        result = self.daily.result_for(size)

        card = tk.Frame(parent, bg=cfg.C("COLOR_PANEL"),
                        highlightthickness=2,
                        highlightbackground=cfg.C("COLOR_PANEL"),
                        cursor="hand2")
        card.grid(row=row, column=col, padx=8, pady=8)

        inner = tk.Frame(card, bg=cfg.C("COLOR_PANEL"), padx=20, pady=14)
        inner.pack(fill="both", expand=True)

        title = tk.Label(inner, text=f"{size} × {size}",
                         font=cfg.FONT_BODY_SEMI,
                         fg=cfg.C("COLOR_TEXT"), bg=cfg.C("COLOR_PANEL"))
        title.pack()

        if done:
            status = tk.Label(inner,
                              text=f"✅  {format_time(result)}",
                              font=cfg.FONT_BODY_MED,
                              fg=cfg.C("COLOR_SUCCESS"),
                              bg=cfg.C("COLOR_PANEL"))
        else:
            status = tk.Label(inner,
                              text="Не пройден",
                              font=cfg.FONT_SMALL,
                              fg=cfg.C("COLOR_TEXT_DIM"),
                              bg=cfg.C("COLOR_PANEL"))
        status.pack(pady=(6, 0))

        def on_enter(_):
            card.configure(highlightbackground=cfg.C("COLOR_ACCENT"))
            for w in (card, inner, title, status):
                w.configure(bg=cfg.C("COLOR_PANEL_HOVER"))

        def on_leave(_):
            card.configure(highlightbackground=cfg.C("COLOR_PANEL"))
            for w in (card, inner, title, status):
                w.configure(bg=cfg.C("COLOR_PANEL"))

        def on_click(_):
            if not done:
                self.on_start(size)

        for w in (card, inner, title, status):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        if done:
            title.configure(fg=cfg.C("COLOR_TEXT_DIM"))