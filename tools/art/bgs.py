"""320x168 battle backgrounds: stepped-band backdrop, mid-ground silhouettes, perspective floor."""
import math, random
from PIL import Image
from art.pix import Canvas, shade, hexc, mix, dither

BG = {
    # id: (sky_top, sky_bottom, far, mid, floor, accent, feature)
    "quarry": ("1e1a1c", "4a3a30", "5a4a3e", "3a3028", "6a5a48", "f0b040", "quarry"),
    "underways": ("0e1016", "2a2e3a", "383c48", "22262e", "44484e", "a82a2a", "arches"),
    "grove": ("2a4a2a", "6a8a4a", "3a5a2a", "243a1a", "5a6a3a", "d0a050", "trees"),
    "grove_flood": ("1e3a3e", "4a7a6a", "2e4a3a", "1a2e24", "3a5a5a", "a0e0e0", "trees_water"),
    "furnace": ("1a0e0a", "5a2a14", "4a3026", "2a1a14", "5a4638", "ff7a30", "pipes"),
    "archive": ("0e2a30", "3a7a7a", "a89a7e", "6a5e4a", "c8bc9e", "40a0a0", "shelves"),
    "sky": ("2a3a7a", "a8c0e0", "c8d0e0", "6a6a78", "a8a8a0", "d09a38", "cables"),
    "whitebone": ("3a4458", "a8b0c0", "d8d8dc", "8a8a98", "c8c8cc", "8a6ac8", "cells"),
    "vault": ("1a1028", "4a3a6a", "7a6a9a", "3a2a4a", "8a7a9a", "f0c070", "vault"),
    "conduit": ("080810", "22222c", "2e2e38", "14141c", "3a3a44", "ff4a4a", "machines"),
    "dais": ("100810", "3a1a2a", "4a2a3a", "1a0e14", "4a3a4a", "ff5a4a", "dais"),
    "crown": ("0a0a1a", "2a1a3a", "4a3a4a", "1a121a", "4a3a4a", "ffd080", "crown"),
    "crown_core": ("140608", "4a1014", "5a2a2a", "1e0a0c", "3a2a2e", "ff6a4a", "core"),
    "winter": ("5a7aa0", "d0e0f0", "e8f0f8", "a0b8d0", "d8e4f0", "ffc060", "ice"),
    "reef": ("020810", "0e2a4a", "1a3a5a", "081a2a", "2a3a4a", "80e0e0", "reef"),
    "field_r01": ("4a7ab8", "b0d0e8", "6a9a5a", "4a7a3a", "7a9a4a", "f0e0a0", "hills"),
    "field_r02": ("5a4a5a", "c09070", "6a5040", "4a3830", "7a6048", "ff8a40", "ridges"),
    "field_r03": ("3a7aa8", "b8e0e8", "d8ccae", "5a8a7a", "d8c8a0", "40a0a0", "coast"),
    "field_r04": ("3a4a8a", "c0c8e0", "a8a8a8", "6a6a7a", "a8a898", "c89a3a", "cliffs"),
    "field_r05": ("3a2a5a", "c8b8e0", "d8cce8", "8a7aa0", "c8bcd8", "e8e0f0", "salt"),
    "field_post": ("2a2030", "7a5a5a", "4a3a3e", "2a2228", "5a4a48", "e05a3a", "ash"),
}


def build_bg(key):
    top, bot, far, mid, floor, acc, feat = [hexc(v) if i < 6 else v for i, v in enumerate(BG[key])]
    c = Canvas(320, 168)
    rnd = random.Random(key)
    horizon = 96
    # stepped dithered backdrop
    bands = 8
    for y in range(horizon):
        t = y / horizon
        b = int(t * bands) / bands
        b2 = min(1.0, b + 1.0 / bands)
        frac = (t - b) * bands
        for x in range(320):
            col = mix(top, bot, b2 if dither(x, y, frac) else b)
            c.put(x, y, col, 1)
    # far silhouettes
    for x in range(0, 320):
        h = 18 + int(10 * math.sin(x * 0.03 + len(key)) + 6 * math.sin(x * 0.11))
        for y in range(horizon - h, horizon):
            c.put(x, y, far if y > horizon - h + 1 else shade(far, 0.2), 2)
    # floor with perspective lines
    for y in range(horizon, 168):
        t = (y - horizon) / (168 - horizon)
        for x in range(320):
            col = shade(floor, -0.25 + t * 0.3)
            if (y - horizon) % max(2, int(3 + t * 10)) == 0:
                col = shade(col, -0.1)
            c.put(x, y, col, 3)
    for i in range(-8, 9):
        x0 = 160 + i * 14
        x1 = 160 + i * 60
        c.line(x0, horizon, x1, 167, shade(floor, -0.18), 1, 3)
    # features
    if feat == "quarry":
        for x in (20, 90, 250, 300):
            c.poly([(x - 16, horizon + 4), (x - 6, 20), (x + 10, 30), (x + 18, horizon + 4)], mid, 4)
        c.line(0, 70, 320, 64, (90, 80, 70, 255), 2, 5)
        for x in range(0, 320, 12):
            c.rect(x, 64, x + 2, 72, (70, 56, 40, 255), 5)
        for (x, y) in ((140, 40), (200, 30), (60, 50)):
            c.ellipse(x, y, 3, 5, (200, 70, 80, 255), 6)
            c.put(x - 1, y - 2, (255, 180, 180, 255), 6)
    elif feat == "arches":
        for x in range(0, 330, 64):
            c.rect(x, 10, x + 10, horizon + 6, mid, 4)
            for a in range(0, 54):
                y = 30 - int(18 * math.sin(a / 54 * math.pi))
                c.rect(x + 10 + a, y, x + 10 + a, y + 5, mid, 4)
        c.rect(0, horizon - 8, 320, horizon + 2, (30, 60, 80, 255), 5)
    elif feat in ("trees", "trees_water"):
        for i in range(9):
            x = 10 + i * 38 + rnd.randint(-8, 8)
            c.rect(x - 3, 30, x + 3, horizon + 6, shade(mid, -0.2), 4)
            c.ellipse(x, 30, 22, 20, mid, 4)
            c.ellipse(x - 6, 24, 10, 8, shade(mid, 0.15), 4)
        if feat == "trees_water":
            for y in range(120, 168):
                for x in range(320):
                    if dither(x, y, 0.5):
                        c.put(x, y, mix(c.get(x, y), hexc("2e5a6a"), 0.6), 3)
    elif feat == "pipes":
        for x in range(10, 320, 46):
            c.rect(x, 0, x + 10, horizon + 4, (120, 80, 50, 255), 4)
            c.rect(x, 0, x + 2, horizon + 4, (170, 120, 70, 255), 4)
            for y in (20, 60):
                c.rect(x - 2, y, x + 12, y + 3, (90, 60, 40, 255), 4)
        for i in range(30):
            c.put(rnd.randrange(320), rnd.randrange(horizon), acc, 6)
    elif feat == "shelves":
        for x in range(0, 320, 40):
            c.rect(x + 2, 16, x + 36, horizon, shade(mid, -0.1), 4)
            for y in range(20, horizon, 10):
                c.rect(x + 4, y, x + 34, y + 1, shade(mid, 0.2), 4)
                for bx in range(x + 5, x + 33, 3):
                    c.rect(bx, y - 7, bx + 1, y - 1, [acc, hexc("c05a3a"), hexc("d8c890")][rnd.randrange(3)], 5)
        for y in range(130, 168):
            for x in range(320):
                if dither(x, y, 0.35):
                    c.put(x, y, mix(c.get(x, y), hexc("2a8a8a"), 0.4), 3)
    elif feat == "cables":
        for i in range(4):
            c.line(0, 20 + i * 18, 320, 40 + i * 10, (60, 60, 70, 255), 2, 4)
        for x in (40, 280):
            c.rect(x, 10, x + 14, horizon + 10, (120, 120, 130, 255), 4)
        for i in range(12):
            x, y = rnd.randrange(320), rnd.randrange(60)
            c.ellipse(x, y, 14, 4, (230, 236, 244, 255), 5)
    elif feat == "cells":
        for x in range(0, 320, 50):
            c.rect(x + 4, 20, x + 44, horizon, mid, 4)
            for bx in range(x + 8, x + 42, 5):
                c.rect(bx, 24, bx + 1, horizon - 2, shade(mid, -0.35), 4)
        for i in range(40):
            c.put(rnd.randrange(320), rnd.randrange(horizon), (255, 255, 255, 255), 6)
    elif feat == "vault":
        for r in (140, 110, 80):
            for a in range(0, 180):
                x = 160 + int(r * math.cos(math.radians(a)))
                y = horizon + 10 - int(r * 0.5 * math.sin(math.radians(a)))
                if 0 <= y < horizon + 10:
                    c.rect(x, y, x + 1, y + 1, shade(mid, 0.2), 4)
        for x in (60, 160, 260):
            c.ellipse(x, 60, 5, 5, acc, 5)
    elif feat in ("machines", "dais", "crown", "core"):
        for x in range(0, 320, 36):
            c.rect(x, 20, x + 24, horizon + 4, mid, 4)
            c.rect(x + 8, 30, x + 16, 36, acc if (x // 36) % 2 == 0 else shade(acc, -0.5), 5)
        if feat == "dais":
            c.poly([(90, horizon + 20), (230, horizon + 20), (200, horizon - 10), (120, horizon - 10)], shade(floor, 0.1), 5)
        if feat in ("crown", "core"):
            for a in range(12):
                ang = a * math.pi / 6
                c.line(160, 50, 160 + math.cos(ang) * 150, 50 + math.sin(ang) * 60, shade(acc, -0.4), 1, 6)
            c.ellipse(160, 50, 18, 18, acc if feat == "core" else shade(acc, -0.3), 6)
    elif feat == "ice":
        for i in range(10):
            x = rnd.randrange(320)
            c.poly([(x - 8, horizon + 4), (x, horizon - 40 - rnd.randrange(30)), (x + 8, horizon + 4)], (220, 236, 250, 255), 4)
        for i in range(60):
            c.put(rnd.randrange(320), rnd.randrange(168), (255, 255, 255, 255), 6)
    elif feat == "reef":
        for i in range(14):
            x = rnd.randrange(320)
            c.ellipse(x, horizon + rnd.randrange(-10, 10), 12, 20, (60, 40, 60, 255), 4)
        for i in range(8):
            c.ellipse(rnd.randrange(320), rnd.randrange(80), 2, 2, acc, 6)
    elif feat in ("hills", "ridges", "coast", "cliffs", "salt", "ash"):
        for i in range(5):
            x = rnd.randrange(320)
            c.ellipse(x, horizon + 4, 50, 22, mid, 4)
        if feat == "coast":
            c.rect(0, horizon - 6, 320, horizon, hexc("2a8aa8"), 5)
        if feat == "ash":
            for i in range(50):
                c.put(rnd.randrange(320), rnd.randrange(horizon), acc if i % 5 == 0 else (120, 110, 110, 255), 6)
    return c.image()


def build(save):
    for k in BG:
        save(build_bg(k), f"sprites/bg/{k}.png", "battle_bg", "320x168", k)
