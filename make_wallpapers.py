"""Генерирует 18 обоин: 9 контекстов × 2 темы.
Каждый контекст — СВОЯ палитра, чтобы они сильно различались.
Светлая тема — пары к тёмной: тот же характер, но светлее и бледнее.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080


# ============================================================
# ТЁМНАЯ ТЕМА — 9 палитр
# ============================================================

DARK_CONTEXTS = {
    "menu": {
        "top":     (74, 53, 112),
        "mid":     (58, 42, 92),
        "bottom":  (42, 30, 72),
        "stripes": [
            ((255, 127, 208), 0.30),
            ((127, 208, 255), 0.25),
            ((127, 255, 192), 0.15),
        ],
        "spark":   (255, 255, 255),
        "spark_count": 60,
    },
    "game_3": {
        "top":     (110, 50, 80),
        "mid":     (85, 40, 65),
        "bottom":  (55, 25, 45),
        "stripes": [
            ((255, 140, 90), 0.35),
            ((255, 100, 160), 0.30),
            ((255, 200, 120), 0.18),
        ],
        "spark":   (255, 230, 200),
        "spark_count": 40,
    },
    "game_6": {
        "top":     (120, 80, 45),
        "mid":     (95, 65, 40),
        "bottom":  (60, 40, 30),
        "stripes": [
            ((255, 200, 80), 0.40),
            ((255, 140, 80), 0.28),
            ((255, 230, 140), 0.20),
        ],
        "spark":   (255, 240, 200),
        "spark_count": 45,
    },
    "game_9": {
        "top":     (40, 90, 80),
        "mid":     (35, 75, 70),
        "bottom":  (20, 50, 50),
        "stripes": [
            ((80, 255, 180), 0.35),
            ((120, 255, 200), 0.28),
            ((80, 220, 200), 0.20),
        ],
        "spark":   (220, 255, 240),
        "spark_count": 50,
    },
    "game_15": {
        "top":     (40, 80, 140),
        "mid":     (30, 65, 120),
        "bottom":  (20, 45, 90),
        "stripes": [
            ((100, 180, 255), 0.35),
            ((80, 230, 255), 0.30),
            ((140, 200, 255), 0.20),
        ],
        "spark":   (220, 240, 255),
        "spark_count": 55,
    },
    "game_25": {
        "top":     (25, 35, 80),
        "mid":     (20, 25, 60),
        "bottom":  (10, 15, 40),
        "stripes": [
            ((80, 120, 255), 0.30),
            ((150, 100, 255), 0.25),
            ((60, 180, 255), 0.18),
        ],
        "spark":   (200, 220, 255),
        "spark_count": 70,
    },
    "game_30": {
        "top":     (55, 20, 40),
        "mid":     (40, 15, 30),
        "bottom":  (25, 8, 20),
        "stripes": [
            ((200, 40, 90), 0.35),
            ((140, 30, 140), 0.30),
            ((255, 80, 120), 0.20),
        ],
        "spark":   (255, 200, 220),
        "spark_count": 80,
    },
    "rules": {
        "top":     (70, 65, 60),
        "mid":     (55, 50, 48),
        "bottom":  (40, 35, 35),
        "stripes": [
            ((180, 160, 140), 0.20),
            ((150, 140, 130), 0.15),
            ((200, 180, 160), 0.10),
        ],
        "spark":   (230, 220, 210),
        "spark_count": 25,
    },
    "settings": {
        "top":     (55, 60, 75),
        "mid":     (45, 50, 60),
        "bottom":  (30, 35, 45),
        "stripes": [
            ((100, 120, 160), 0.20),
            ((140, 160, 200), 0.15),
            ((80, 100, 140), 0.12),
        ],
        "spark":   (200, 210, 230),
        "spark_count": 30,
    },
}


# ============================================================
# СВЕТЛАЯ ТЕМА — пары к тёмной, тот же характер, но светлее
# ============================================================

LIGHT_CONTEXTS = {
    "menu": {
        "top":     (250, 244, 255),
        "mid":     (242, 232, 250),
        "bottom":  (232, 216, 240),
        "stripes": [
            ((255, 184, 220), 0.35),
            ((184, 220, 255), 0.30),
            ((184, 240, 216), 0.25),
        ],
        "spark":   (184, 168, 216),
        "spark_count": 35,
    },
    "game_3": {
        "top":     (255, 244, 248),
        "mid":     (250, 234, 240),
        "bottom":  (242, 220, 230),
        "stripes": [
            ((255, 200, 170), 0.35),
            ((255, 180, 210), 0.30),
            ((255, 220, 190), 0.25),
        ],
        "spark":   (216, 160, 140),
        "spark_count": 25,
    },
    "game_6": {
        "top":     (255, 250, 240),
        "mid":     (252, 244, 228),
        "bottom":  (245, 232, 210),
        "stripes": [
            ((255, 230, 180), 0.40),
            ((255, 210, 170), 0.32),
            ((255, 240, 200), 0.28),
        ],
        "spark":   (216, 190, 140),
        "spark_count": 28,
    },
    "game_9": {
        "top":     (238, 250, 245),
        "mid":     (228, 245, 238),
        "bottom":  (215, 235, 226),
        "stripes": [
            ((184, 240, 210), 0.40),
            ((200, 245, 220), 0.32),
            ((180, 230, 215), 0.28),
        ],
        "spark":   (140, 190, 170),
        "spark_count": 30,
    },
    "game_15": {
        "top":     (240, 246, 255),
        "mid":     (230, 240, 252),
        "bottom":  (218, 232, 248),
        "stripes": [
            ((184, 220, 255), 0.40),
            ((168, 230, 255), 0.32),
            ((200, 235, 255), 0.28),
        ],
        "spark":   (140, 180, 220),
        "spark_count": 32,
    },
    "game_25": {
        "top":     (240, 240, 250),
        "mid":     (232, 232, 245),
        "bottom":  (222, 222, 238),
        "stripes": [
            ((200, 205, 245), 0.38),
            ((215, 200, 248), 0.32),
            ((205, 225, 245), 0.28),
        ],
        "spark":   (150, 150, 200),
        "spark_count": 35,
    },
    "game_30": {
        "top":     (250, 238, 244),
        "mid":     (245, 228, 236),
        "bottom":  (238, 215, 225),
        "stripes": [
            ((240, 180, 200), 0.38),
            ((225, 180, 220), 0.32),
            ((255, 200, 215), 0.28),
        ],
        "spark":   (200, 140, 170),
        "spark_count": 38,
    },
    "rules": {
        "top":     (248, 244, 240),
        "mid":     (242, 238, 234),
        "bottom":  (235, 230, 226),
        "stripes": [
            ((225, 210, 200), 0.28),
            ((215, 205, 200), 0.22),
            ((230, 218, 210), 0.20),
        ],
        "spark":   (180, 165, 160),
        "spark_count": 18,
    },
    "settings": {
        "top":     (240, 242, 250),
        "mid":     (233, 236, 245),
        "bottom":  (225, 228, 240),
        "stripes": [
            ((205, 215, 235), 0.30),
            ((215, 220, 240), 0.25),
            ((200, 212, 232), 0.22),
        ],
        "spark":   (160, 165, 190),
        "spark_count": 22,
    },
}


# ============================================================

def _adjust(color, darken):
    r, g, b = color
    if darken > 0:
        r = int(r * (1 - darken))
        g = int(g * (1 - darken))
        b = int(b * (1 - darken))
    elif darken < 0:
        f = 1 - darken
        r = min(255, int(r * f))
        g = min(255, int(g * f))
        b = min(255, int(b * f))
    return (r, g, b)


def make_wallpaper(palette):
    top = palette["top"]
    mid = palette["mid"]
    bottom = palette["bottom"]

    img = Image.new("RGB", (W, H))
    px = img.load()
    half = H // 2
    for y in range(H):
        if y < half:
            t = y / half
            c = tuple(int(top[i] + (mid[i] - top[i]) * t) for i in range(3))
        else:
            t = (y - half) / half
            c = tuple(int(mid[i] + (bottom[i] - mid[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = c

    blur = W // 10

    stripe_positions = [
        (-0.35, -0.10, 0.45, 0.45),
        ( 0.55, -0.20, 1.30, 0.35),
        (-0.30,  0.55, 0.50, 1.25),
        ( 0.60,  0.50, 1.40, 1.00),
        ( 0.20,  0.20, 0.80, 0.65),
        (-0.20,  0.20, 0.30, 0.60),
    ]

    rng = random.Random(hash(str(palette)) & 0xffffffff)
    rng.shuffle(stripe_positions)

    for i, (x1r, y1r, x2r, y2r) in enumerate(stripe_positions):
        color, blend = palette["stripes"][i % len(palette["stripes"])]
        layer = Image.new("RGB", (W, H), (0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse(
            [int(W * x1r), int(H * y1r), int(W * x2r), int(H * y2r)],
            fill=color
        )
        layer = layer.filter(ImageFilter.GaussianBlur(radius=blur))
        img = Image.blend(img, layer, blend)

    img = img.convert("RGBA")

    sparks = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sparks)
    sr, sg, sb = palette["spark"]
    count = palette["spark_count"]
    for _ in range(count):
        cx = rng.randint(0, W)
        cy = rng.randint(0, H)
        r = rng.choice([2, 2, 3, 3, 4, 5, 6])
        a = rng.randint(120, 240)
        if r >= 4:
            halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            hd = ImageDraw.Draw(halo)
            hd.ellipse([cx - r*4, cy - r*4, cx + r*4, cy + r*4],
                       fill=(sr, sg, sb, int(a * 0.25)))
            halo = halo.filter(ImageFilter.GaussianBlur(radius=r * 2))
            sparks = Image.alpha_composite(sparks, halo)
            sd = ImageDraw.Draw(sparks)
        sd.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=(sr, sg, sb, a))

    img = Image.alpha_composite(img, sparks)
    return img.convert("RGB")


def main():
    base = os.path.join("data", "wallpapers")
    os.makedirs(os.path.join(base, "dark"), exist_ok=True)
    os.makedirs(os.path.join(base, "light"), exist_ok=True)

    for theme_name, palettes in (("dark", DARK_CONTEXTS),
                                 ("light", LIGHT_CONTEXTS)):
        for context, palette in palettes.items():
            img = make_wallpaper(palette)
            path = os.path.join(base, theme_name, f"{context}.jpg")
            img.save(path, quality=90)
            print(f"✓ {theme_name}/{context}.jpg")

    print(f"\nГотово: 18 обоин в {base}/")


if __name__ == "__main__":
    main()