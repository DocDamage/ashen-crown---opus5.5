"""16x16 environment tilesets (one atlas per family) + 16x32 tall props.

Atlas layout: row per tile kind (KINDS order), 4 columns = variants/animation frames.
Props atlas: one 16x32 cell per prop kind (PROPS order) per tileset.
"""
import random
from PIL import Image
from art.pix import Canvas, hexc, shade, mix, dither

KINDS = ["floor", "floor2", "path", "wall_top", "wall_face", "water", "shallow", "bridge", "grass", "roof", "roof_eave",
         "roof_ridge", "house", "window", "door", "doorway", "stairs", "sand", "snow", "ice", "ash", "salt", "moss",
         "roots", "puddle", "ember", "deep", "cliff", "cliff_top", "rubble", "fence", "hedge", "garden", "counter", "rail",
         "void", "dock", "ladder", "carpet", "grate", "reef", "plains", "forest", "hills", "mountain", "town_mark",
         "dungeon_mark", "city", "ruin", "cave", "island", "lift", "gate", "sluice", "pool", "hole", "mural", "awning", "chain",
         "cable", "vine", "rock", "crate", "barrel", "table", "bed", "machine", "pipe", "crystal", "bell", "vent", "cart",
         "anvil", "boat", "well", "sign", "bench", "laundry", "chest_deco", "book", "altar", "brazier", "wheel", "gear", "shelter",
         "tent", "lever_deco", "flower", "window_int", "arch", "stair_l", "stair_r", "chimney"]
PROPS = ["tree", "lamp", "pillar", "statue", "shelf", "tree2", "banner", "crystal_tall", "pipe_tall", "mast", "totem", "lantern_post"]

P = {}  # tileset palettes


def pal(**kw):
    d = {k: hexc(v) if isinstance(v, str) else v for k, v in kw.items()}
    return d


BASE = dict(floor="7a6a50", floor2="6e6048", path="9a8a68", wall="5a5048", wall_top="3e3834", water="2e5a8a", deep="1c3460",
            grass="4a7a3a", foliage="3a6a2e", roof="8a3a2a", house="c8b89a", wood="7a5232", metal="7a7e88", accent="c84a3a",
            light="f0d080", stone="8a8478", dark="2a2430", sand="d8c090", void="1a1a2a", ice="a8d0f0", moss="4a6a3a", crystal="c8b8e8", reef="6a3a4a", snow="e8eef4", salt="d8c8e0", ash="4a4448", ember="e06a2a",
            glass="9ad0e0", cloth="b04a4a", plant="5a8a3a", rock="6a6258")

P["town_r01"] = pal(**{**BASE, "floor": "8a7a52", "floor2": "7e7048", "path": "a89870", "grass": "5a8a3a", "foliage": "3e6e2c",
                       "roof": "8a4a2e", "house": "c8b08a", "wall": "6a6254", "wall_top": "3e3a30", "accent": "b8483a"})
P["capital"] = pal(**{**BASE, "floor": "5a5e58", "floor2": "4e5250", "path": "7a7a70", "wall": "3a4038", "wall_top": "22281e",
                      "roof": "2e3a30", "house": "8a8c80", "accent": "a82a2a", "grass": "3e5e32", "cloth": "a82a2a"})
P["quarry"] = pal(**{**BASE, "floor": "6a5e50", "floor2": "5e5446", "path": "7e7058", "wall": "5a4c40", "wall_top": "34281e",
                     "water": "3a5a6a", "rock": "7a6c5c", "accent": "c8a040", "light": "f0b040"})
P["underways"] = pal(**{**BASE, "floor": "4a4c52", "floor2": "40424a", "path": "5a5c62", "wall": "383a44", "wall_top": "1e2028",
                        "water": "2a4a5a", "deep": "1a2a3a", "accent": "a82a2a", "moss": "3a5a3a"})
P["grove"] = pal(**{**BASE, "floor": "5a6a3a", "floor2": "4e5e32", "path": "8a7a50", "wall": "4a3a28", "wall_top": "2a2016",
                    "grass": "4e8a3a", "foliage": "2e5e22", "water": "3a6a7a", "accent": "d0a050", "plant": "6a9a3a"})
P["grove_flood"] = pal(**{**P["grove"], "floor": "4e5e3e", "water": "2e5a6a", "deep": "1e3e50"})
P["furnace"] = pal(**{**BASE, "floor": "5a4638", "floor2": "4e3c30", "path": "6e5644", "wall": "4a3a30", "wall_top": "2a1e18",
                      "metal": "b0703a", "accent": "e06a2a", "light": "ffb050", "water": "3a4a5a", "roof": "5a3a2a"})
P["town_r02"] = pal(**{**P["furnace"], "floor": "6e5a46", "house": "a88a6a", "roof": "6a3a26", "grass": "5a6a3a"})
P["archive"] = pal(**{**BASE, "floor": "c8bc9e", "floor2": "b8ac8e", "path": "d8ccae", "wall": "a89a7e", "wall_top": "5a5040",
                      "water": "2a8a8a", "deep": "1a5a6a", "metal": "5a8a6a", "accent": "4a9a7a", "moss": "4a7a6a"})
P["town_r03"] = pal(**{**P["archive"], "roof": "3a7a74", "house": "e0d4b8", "grass": "5a8a5a", "wood": "8a6a4a", "cloth": "3a8a7a"})
P["sky"] = pal(**{**BASE, "floor": "a8a8a0", "floor2": "9a9a92", "path": "b8b0a0", "wall": "7a7a78", "wall_top": "4a4a58",
                  "void": "3a4a7a", "cloth": "c89a3a", "accent": "c89a3a", "wood": "6a5038"})
P["town_r04"] = pal(**{**P["sky"], "roof": "b88a3a", "house": "c0b8a8", "grass": "6a8a5a"})
P["basin"] = pal(**{**BASE, "floor": "b8a8c8", "floor2": "a898b8", "path": "c8bcd8", "wall": "7a6a8a", "wall_top": "3a2a4a",
                    "water": "6a8ab0", "salt": "d8cce8", "accent": "e8e0f0", "roof": "5a3a6a", "house": "d8d0e0", "grass": "8a9a7a"})
P["town_r05"] = P["basin"]
P["whitebone"] = pal(**{**BASE, "floor": "c8c8cc", "floor2": "b8b8be", "path": "d8d8dc", "wall": "a8a8b0", "wall_top": "5a5a68",
                        "accent": "6a4a8a", "snow": "eef2f8", "metal": "8a8a9a"})
P["vault"] = pal(**{**BASE, "floor": "8a7a9a", "floor2": "7e6e8e", "path": "9a8aaa", "wall": "5a4a6a", "wall_top": "2a1e3a",
                    "water": "5a7aa0", "light": "f0c070", "accent": "f0c070", "crystal": "d8c8f0"})
P["conduit"] = pal(**{**BASE, "floor": "3a3a44", "floor2": "32323c", "path": "4a4a54", "wall": "2a2a34", "wall_top": "14141c",
                      "metal": "6a6a78", "accent": "d83a3a", "light": "ff5a4a", "water": "2a3a5a"})
P["harbor"] = pal(**{**BASE, "floor": "7a5a3e", "floor2": "6a4e36", "path": "8a6a4a", "wall": "3a3a40", "wall_top": "1e1e26",
                     "water": "1e3e7a", "deep": "12245a", "roof": "5a5a64", "house": "8a7058", "accent": "e0503a", "light": "ff8a5a"})
P["crown"] = pal(**{**BASE, "floor": "4a3a4a", "floor2": "3e2e3e", "path": "5a4a5a", "wall": "3a2a3a", "wall_top": "1a121a",
                    "metal": "a88a3a", "accent": "e0503a", "light": "ffd080", "void": "12122a", "crystal": "e05a4a"})
P["winter"] = pal(**{**BASE, "floor": "c8d8e8", "floor2": "b8c8d8", "path": "d8e4f0", "wall": "8a9ab0", "wall_top": "4a5a78",
                     "water": "5a8ab0", "ice": "a8d0f0", "snow": "f0f4fa", "accent": "f0a040", "light": "ffc060"})
P["reef"] = pal(**{**BASE, "floor": "2a3a4a", "floor2": "22323e", "path": "3a4a5a", "wall": "1a2a36", "wall_top": "0e161e",
                   "water": "0e2a4a", "deep": "081a30", "accent": "e05a4a", "light": "80e0e0", "reef": "5a3a4a"})
P["interior"] = pal(**{**BASE, "floor": "8a6a44", "floor2": "7e603c", "path": "9a7a52", "wall": "c8b89a", "wall_top": "5a4a3a",
                       "house": "c8b89a", "accent": "a84a3a"})
P["interior_stone"] = pal(**{**BASE, "floor": "6a6a6e", "floor2": "5e5e62", "wall": "8a8680", "wall_top": "3a3634"})
P["ship"] = pal(**{**BASE, "floor": "9a7248", "floor2": "8a6440", "path": "a8805a", "wall": "5a4030", "wall_top": "2a1e16",
                   "metal": "a0703a", "void": "5a7ab0", "cloth": "d8d0b8"})
P["world"] = pal(**{**BASE, "water": "2e5a9a", "deep": "1e3a78", "grass": "5a9a42", "foliage": "2e6a2a", "sand": "d8c890",
                    "rock": "8a7a6a", "snow": "eef2f8", "salt": "d0c4e0", "ash": "5a5054"})
P["world_post"] = pal(**{**P["world"], "water": "2a4a8a", "deep": "1a2e68", "grass": "4e8a3e", "ash": "4a3a3e", "accent": "e0503a"})

TALL_SOLID_PROPS = PROPS


def rnd(seed):
    return random.Random(seed)


def noise_fill(c, base, seed, amt=0.18, speck=None):
    r = rnd(seed)
    for y in range(16):
        for x in range(16):
            v = r.random()
            col = base
            if v < amt * 0.5:
                col = shade(base, -0.10)
            elif v > 1 - amt * 0.4:
                col = shade(base, 0.08)
            c.put(x, y, col)
    if speck:
        for _ in range(3):
            c.put(r.randrange(16), r.randrange(16), speck)


def t_floor(p, v, key="floor"):
    c = Canvas(16, 16)
    noise_fill(c, p[key], 100 + v, 0.22, shade(p[key], -0.25))
    if key == "floor" and v == 1:
        # flagstone seams
        for x in range(16):
            c.put(x, 7, shade(p[key], -0.18))
        c.put(5, 0, shade(p[key], -0.18))
        for y in range(0, 7):
            c.put(5, y, shade(p[key], -0.18))
        for y in range(8, 16):
            c.put(11, y, shade(p[key], -0.18))
    if v == 2:
        c.put(3, 11, shade(p[key], 0.2))
        c.put(4, 11, shade(p[key], 0.15))
        c.put(12, 4, shade(p[key], -0.3))
    return c


def t_wall_face(p, v):
    c = Canvas(16, 16)
    base = p["wall"]
    for y in range(16):
        for x in range(16):
            row = y // 4
            off = 4 if row % 2 else 0
            edge = (y % 4 == 3) or ((x + off) % 8 == 7)
            col = shade(base, -0.28) if edge else base
            if y % 4 == 0 and not edge:
                col = shade(base, 0.12)
            c.put(x, y, col)
    r = rnd(300 + v)
    for _ in range(4):
        c.put(r.randrange(16), r.randrange(16), shade(base, -0.15))
    for x in range(16):
        c.put(x, 15, shade(base, -0.45))
    if v == 3:
        for y in range(4, 12):
            c.put(6, y, shade(p["moss"] if "moss" in p else p["grass"], 0.0))
    return c


def t_wall_top(p, v):
    c = Canvas(16, 16)
    base = p["wall_top"]
    noise_fill(c, base, 400 + v, 0.15)
    for x in range(16):
        c.put(x, 15, shade(p["wall"], 0.2))
    return c


def t_water(p, v, key="water"):
    c = Canvas(16, 16)
    base = p[key]
    for y in range(16):
        for x in range(16):
            c.put(x, y, base)
    ph = v * 4
    for y in (3, 9, 14):
        for x in range(16):
            if (x + ph + y) % 8 < 3:
                c.put(x, y, shade(base, 0.22))
    for y in (6, 12):
        for x in range(16):
            if (x - ph + y * 2) % 10 < 2:
                c.put(x, y, shade(base, -0.18))
    return c


def t_shallow(p, v):
    c = t_floor(p, v % 3, "floor")
    wtr = p["water"]
    for y in range(16):
        for x in range(16):
            if dither(x, y, 0.7):
                c.put(x, y, mix(c.get(x, y), wtr, 0.55))
    for x in range(16):
        if (x + v * 3) % 7 < 2:
            c.put(x, 5, shade(wtr, 0.35))
    return c


def t_bridge(p, v):
    c = Canvas(16, 16)
    w = p["wood"]
    for y in range(16):
        for x in range(16):
            plank = (y // 4)
            col = shade(w, 0.08 if plank % 2 else -0.02)
            if y % 4 == 3:
                col = shade(w, -0.35)
            c.put(x, y, col)
    for y in range(16):
        c.put(0, y, shade(w, -0.5))
        c.put(15, y, shade(w, -0.5))
    c.put(3, 1, shade(p["metal"], 0.1))
    c.put(12, 9, shade(p["metal"], 0.1))
    return c


def t_grass(p, v):
    c = Canvas(16, 16)
    g = p["grass"]
    noise_fill(c, g, 500 + v, 0.3)
    r = rnd(510 + v)
    for _ in range(6):
        x, y = r.randrange(1, 15), r.randrange(2, 15)
        c.put(x, y, shade(g, 0.25))
        c.put(x, y - 1, shade(g, 0.15))
    if v == 3:
        c.put(4, 5, p["light"])
        c.put(11, 10, hexc("e0e0f0"))
    return c


def t_roof(p, v, part="mid"):
    c = Canvas(16, 16)
    r = p["roof"]
    for y in range(16):
        for x in range(16):
            row = y // 3
            off = 3 if row % 2 else 0
            col = r
            if y % 3 == 2:
                col = shade(r, -0.3)
            elif (x + off) % 6 == 0:
                col = shade(r, -0.18)
            elif y % 3 == 0:
                col = shade(r, 0.12)
            c.put(x, y, col)
    if part == "eave":
        for x in range(16):
            c.put(x, 13, shade(r, -0.45))
            c.put(x, 14, shade(p["wood"], -0.2))
            c.put(x, 15, shade(p["wood"], -0.5))
    if part == "ridge":
        for x in range(16):
            c.put(x, 0, shade(r, 0.35))
            c.put(x, 1, shade(r, 0.2))
    return c


def t_house(p, v):
    c = Canvas(16, 16)
    h = p["house"]
    noise_fill(c, h, 600 + v, 0.12)
    # timber frame
    wd = p["wood"]
    for y in range(16):
        c.put(0, y, shade(wd, -0.1))
        c.put(15, y, shade(wd, -0.3))
    for x in range(16):
        c.put(x, 0, shade(wd, -0.2))
        c.put(x, 15, shade(h, -0.4))
    if v == 1:
        c.line(1, 14, 14, 1, shade(wd, -0.15))
    return c


def t_window(p, v, lit=True):
    c = t_house(p, 0)
    g = p["light"] if lit else shade(p["glass"], -0.3)
    c.rect(4, 4, 11, 11, shade(p["wood"], -0.4))
    c.rect(5, 5, 10, 10, g)
    c.rect(5, 5, 10, 5, shade(g, 0.3))
    c.rect(7, 5, 8, 10, shade(p["wood"], -0.3))
    c.rect(5, 7, 10, 8, shade(p["wood"], -0.3))
    c.rect(3, 12, 12, 12, shade(p["wood"], 0.0))
    return c


def t_door(p, v):
    c = t_house(p, 0)
    wd = p["wood"]
    c.rect(4, 2, 11, 15, shade(wd, -0.45))
    c.rect(5, 3, 10, 15, wd)
    for x in (7,):
        for y in range(3, 16):
            c.put(x, y, shade(wd, -0.25))
    c.put(9, 9, p["light"])
    return c


def t_doorway(p, v):
    c = t_floor(p, 0)
    for y in range(16):
        for x in range(16):
            c.put(x, y, mix(c.get(x, y), p["dark"], 0.5))
    return c


def t_stairs(p, v):
    c = Canvas(16, 16)
    s = p["floor"]
    for y in range(16):
        for x in range(16):
            step = y // 4
            col = shade(s, 0.15 - step * 0.1)
            if y % 4 == 0:
                col = shade(s, 0.3)
            c.put(x, y, col)
    for y in range(16):
        c.put(0, y, shade(p["wall"], -0.2))
        c.put(15, y, shade(p["wall"], -0.2))
    return c


def t_simple(p, v, key, speck=None, amt=0.25):
    c = Canvas(16, 16)
    noise_fill(c, p.get(key, p["floor"]), hash(key) % 1000 + v, amt, speck)
    return c


def t_ice(p, v):
    c = t_simple(p, v, "ice", amt=0.1)
    c.line(2, 12, 7, 7, shade(p["ice"], 0.4))
    c.line(9, 4, 13, 2, shade(p["ice"], 0.4))
    return c


def t_ember(p, v):
    c = t_simple(p, v, "ash", amt=0.3)
    r = rnd(700 + v)
    for _ in range(5):
        x, y = r.randrange(16), r.randrange(16)
        c.put(x, y, p["ember"])
        if x + 1 < 16:
            c.put(x + 1, y, shade(p["ember"], -0.3))
    return c


def t_roots(p, v):
    c = t_floor(p, v % 3)
    rt = shade(p["wood"], -0.2)
    c.line(0, 4 + v, 15, 9 - v, rt, 2)
    c.line(5, 0, 9, 15, shade(rt, 0.1), 1)
    return c


def t_cliff(p, v, top=False):
    c = Canvas(16, 16)
    rk = p["rock"]
    if top:
        noise_fill(c, p["floor2"], 800 + v, 0.2)
        for x in range(16):
            c.put(x, 15, shade(rk, 0.3))
            c.put(x, 14, shade(rk, 0.1))
        return c
    for y in range(16):
        for x in range(16):
            col = rk
            if (x + y * 2 + v * 5) % 9 == 0:
                col = shade(rk, -0.3)
            if (x * 3 + y) % 11 == 0:
                col = shade(rk, 0.2)
            c.put(x, y, col)
    for x in range(16):
        c.put(x, 0, shade(rk, 0.35))
    return c


def t_rubble(p, v):
    c = t_floor(p, 0)
    r = rnd(900 + v)
    for _ in range(4):
        x, y = r.randrange(2, 13), r.randrange(3, 13)
        c.ellipse(x, y, 2, 1.5, p["rock"], 2)
        c.put(x - 1, y - 1, shade(p["rock"], 0.3), 2)
    c.outline((30, 26, 30, 255))
    return c


def overlay(base_fn, draw_fn):
    def f(p, v):
        c = base_fn(p, v)
        d = Canvas(16, 16)
        draw_fn(d, p, v)
        d.light(0.15)
        d.outline((28, 22, 28, 255))
        c.blit(d, 0, 0)
        return c
    return f


def _fence(d, p, v):
    wd = p["wood"]
    d.rect(0, 6, 15, 7, wd)
    d.rect(0, 11, 15, 12, wd)
    d.rect(2, 3, 3, 14, shade(wd, 0.1))
    d.rect(12, 3, 13, 14, shade(wd, 0.1))


def _hedge(d, p, v):
    d.ellipse(8, 8, 7.5, 6, p["foliage"])
    r = rnd(1000 + v)
    for _ in range(10):
        d.put(r.randrange(2, 14), r.randrange(3, 13), shade(p["foliage"], 0.3))


def _garden(d, p, v):
    d.rect(1, 3, 14, 14, shade(p["wood"], -0.3))
    d.rect(2, 4, 13, 13, hexc("5a3e2a"))
    for x in range(3, 13, 3):
        d.rect(x, 5, x + 1, 11, p["plant"])
        d.put(x, 4, shade(p["plant"], 0.3))


def _counter(d, p, v):
    d.rect(0, 2, 15, 13, p["wood"])
    d.rect(0, 2, 15, 4, shade(p["wood"], 0.25))


def _rail(d, p, v):
    d.rect(0, 3, 15, 4, p["metal"])
    d.rect(0, 11, 15, 12, p["metal"])
    for x in (1, 6, 11):
        d.rect(x, 2, x + 2, 13, shade(p["wood"], -0.2))


def _crate(d, p, v):
    d.rect(2, 3, 13, 14, p["wood"])
    d.rect(2, 3, 13, 5, shade(p["wood"], 0.25))
    d.line(3, 6, 12, 13, shade(p["wood"], -0.3))
    d.line(12, 6, 3, 13, shade(p["wood"], -0.3))


def _barrel(d, p, v):
    d.ellipse(8, 9, 5.5, 6, p["wood"])
    d.rect(3, 6, 13, 6, shade(p["metal"], -0.2))
    d.rect(3, 12, 13, 12, shade(p["metal"], -0.2))
    d.ellipse(8, 4, 4.5, 1.5, shade(p["wood"], 0.3))


def _table(d, p, v):
    d.rect(1, 4, 14, 10, p["wood"])
    d.rect(1, 4, 14, 5, shade(p["wood"], 0.3))
    d.rect(2, 11, 3, 14, shade(p["wood"], -0.3))
    d.rect(12, 11, 13, 14, shade(p["wood"], -0.3))
    if v % 2 == 0:
        d.ellipse(6, 6, 2, 1, hexc("e8e0d0"))
        d.ellipse(10, 7, 1.5, 1, p["accent"])


def _bed(d, p, v):
    d.rect(2, 1, 13, 14, p["wood"])
    d.rect(3, 2, 12, 5, hexc("e8e4d8"))
    d.rect(3, 6, 12, 13, p.get("cloth", p["accent"]))


def _machine(d, p, v):
    d.rect(1, 2, 14, 14, p["metal"])
    d.rect(1, 2, 14, 3, shade(p["metal"], 0.3))
    d.rect(4, 6, 11, 10, shade(p["metal"], -0.4))
    d.rect(5, 7, 6, 8, p["light"])
    d.rect(9, 7, 10, 8, p["accent"])


def _pipe(d, p, v):
    d.rect(5, 0, 10, 15, p["metal"])
    d.rect(5, 0, 6, 15, shade(p["metal"], 0.3))
    d.rect(4, 6, 11, 8, shade(p["metal"], -0.2))


def _crystal(d, p, v):
    cr = p.get("crystal", p["glass"])
    d.poly([(8, 1), (12, 7), (10, 14), (6, 14), (4, 7)], cr)
    d.line(8, 2, 8, 13, shade(cr, 0.4))


def _bell(d, p, v):
    d.rect(2, 1, 13, 2, p["wood"])
    d.poly([(5, 3), (10, 3), (13, 12), (2, 12)], hexc("c0983a"))
    d.rect(2, 12, 13, 13, shade(hexc("c0983a"), -0.3))


def _vent(d, p, v):
    d.rect(2, 3, 13, 13, shade(p["metal"], -0.3))
    for y in range(5, 12, 2):
        d.rect(3, y, 12, y, shade(p["metal"], 0.2))
    d.put(7, 2, p["light"])


def _cart(d, p, v):
    d.rect(1, 3, 14, 10, p["wood"])
    d.rect(1, 3, 14, 4, shade(p["wood"], 0.3))
    d.ellipse(4, 12, 2, 2, shade(p["metal"], -0.3))
    d.ellipse(11, 12, 2, 2, shade(p["metal"], -0.3))
    d.rect(3, 1, 12, 3, p["accent"])


def _anvil(d, p, v):
    d.poly([(2, 5), (14, 5), (11, 8), (5, 8)], shade(p["metal"], -0.2))
    d.rect(6, 8, 10, 13, shade(p["metal"], -0.4))


def _boat(d, p, v):
    d.poly([(0, 6), (15, 6), (13, 13), (2, 13)], p["wood"])
    d.rect(1, 6, 14, 7, shade(p["wood"], 0.3))


def _well(d, p, v):
    d.ellipse(8, 9, 6, 5, p["stone"])
    d.ellipse(8, 9, 4, 3, hexc("1a2a3a"))
    d.rect(2, 1, 3, 9, p["wood"])
    d.rect(12, 1, 13, 9, p["wood"])
    d.rect(2, 1, 13, 2, shade(p["wood"], 0.2))


def _sign(d, p, v):
    d.rect(7, 8, 8, 15, p["wood"])
    d.rect(2, 2, 13, 9, shade(p["wood"], 0.15))
    d.rect(4, 4, 11, 4, shade(p["wood"], -0.4))
    d.rect(4, 6, 9, 6, shade(p["wood"], -0.4))


def _bench(d, p, v):
    d.rect(0, 6, 15, 8, p["wood"])
    d.rect(0, 6, 15, 6, shade(p["wood"], 0.3))
    d.rect(2, 9, 3, 12, shade(p["wood"], -0.3))
    d.rect(12, 9, 13, 12, shade(p["wood"], -0.3))


def _laundry(d, p, v):
    d.line(0, 3, 15, 4, hexc("d8d0c0"))
    d.rect(2, 4, 5, 10, hexc("e8e4d8"))
    d.rect(7, 4, 10, 9, p["accent"])
    d.rect(12, 4, 14, 11, hexc("6a8ac0"))


def _chest(d, p, v):
    d.rect(2, 5, 13, 13, shade(p["wood"], -0.1))
    d.rect(2, 5, 13, 7, shade(p["wood"], 0.2))
    d.rect(7, 8, 8, 10, p["light"])


def _book(d, p, v):
    d.rect(1, 2, 14, 14, shade(p["wood"], -0.3))
    cols = [p["accent"], hexc("4a6a9a"), hexc("6a8a4a"), hexc("c0a050")]
    for i, x in enumerate(range(2, 14, 3)):
        d.rect(x, 3, x + 1, 7, cols[i % 4])
        d.rect(x, 9, x + 1, 13, cols[(i + 2) % 4])


def _altar(d, p, v):
    d.rect(2, 5, 13, 13, p["stone"])
    d.rect(1, 4, 14, 5, shade(p["stone"], 0.3))
    d.ellipse(8, 3, 2, 1.5, p["light"])


def _brazier(d, p, v):
    d.rect(4, 8, 11, 12, p["metal"])
    d.rect(7, 12, 8, 15, shade(p["metal"], -0.3))
    d.ellipse(8, 6, 3, 3, p["ember"])
    d.put(8, 3, p["light"])


def _wheel(d, p, v):
    d.ellipse(8, 8, 7, 7, p["wood"])
    d.ellipse(8, 8, 4.5, 4.5, shade(p["wood"], -0.4))
    d.line(8, 1, 8, 15, shade(p["wood"], 0.2))
    d.line(1, 8, 15, 8, shade(p["wood"], 0.2))


def _gear(d, p, v):
    d.ellipse(8, 8, 6, 6, p["metal"])
    for (x, y) in ((8, 1), (8, 15), (1, 8), (15, 8), (3, 3), (13, 13), (3, 13), (13, 3)):
        d.rect(x - 1, y - 1, x, y, p["metal"])
    d.ellipse(8, 8, 2, 2, shade(p["metal"], -0.4))


def _shelter(d, p, v):
    d.poly([(0, 14), (8, 2), (15, 14)], p.get("cloth", p["accent"]))
    d.poly([(5, 14), (8, 8), (11, 14)], hexc("2a2420"))


def _lever(d, p, v):
    d.rect(4, 10, 11, 14, shade(p["metal"], -0.3))
    d.line(7, 11, 11, 3, p["metal"], 2)
    d.ellipse(11, 3, 1.5, 1.5, p["accent"])


def _flower(d, p, v):
    r = rnd(1200 + v)
    for _ in range(6):
        x, y = r.randrange(2, 14), r.randrange(3, 14)
        d.put(x, y, [p["accent"], p["light"], hexc("e8e0f0")][r.randrange(3)])
        d.put(x, y + 1, p["plant"])


def _rock(d, p, v):
    d.ellipse(8, 9, 6, 5, p["rock"])
    d.ellipse(6, 7, 2.5, 2, shade(p["rock"], 0.25))


def _sluice(d, p, v):
    d.rect(1, 1, 14, 14, shade(p["metal"], -0.3))
    d.rect(3, 3, 12, 12, p["water"])
    d.rect(2, 6, 13, 8, p["metal"])
    d.ellipse(8, 7, 2, 2, p["accent"])


def _pool(d, p, v):
    d.ellipse(8, 8, 7, 6, p["stone"])
    d.ellipse(8, 8, 5.5, 4.5, p["water"])
    d.put(6, 6, shade(p["water"], 0.4))


def _mural(d, p, v):
    d.rect(0, 1, 15, 14, shade(p["wall"], 0.1))
    d.rect(2, 3, 13, 12, shade(p["wall"], -0.2))
    d.line(3, 10, 6, 5, p["accent"])
    d.line(6, 5, 9, 9, p["accent"])
    d.line(9, 9, 12, 4, p["light"])


def _awning(d, p, v):
    cl = p.get("cloth", p["accent"])
    for x in range(16):
        d.rect(x, 0, x, 9, cl if (x // 3) % 2 else hexc("e8e0d0"))
    for x in range(0, 16, 3):
        d.put(x + 1, 10, cl)


def _chain(d, p, v):
    for y in range(0, 16, 4):
        d.ellipse(8, y + 2, 2, 2, p["metal"])


def _cable(d, p, v):
    d.line(0, 7, 15, 8, shade(p["metal"], -0.2), 2)


def _vine(d, p, v):
    d.line(3, 0, 5, 15, p["plant"], 1)
    d.line(10, 0, 12, 15, p["plant"], 1)
    d.put(4, 5, shade(p["plant"], 0.3))
    d.put(11, 9, shade(p["plant"], 0.3))


def _gate(d, p, v):
    d.rect(0, 0, 15, 15, shade(p["metal"], -0.35))
    for x in range(1, 16, 3):
        d.rect(x, 0, x, 15, p["metal"])
    d.rect(0, 7, 15, 8, p["metal"])


def _lift(d, p, v):
    d.rect(1, 1, 14, 14, shade(p["metal"], -0.2))
    d.rect(2, 2, 13, 13, shade(p["wood"], -0.1))
    d.line(2, 2, 13, 13, shade(p["metal"], 0.1))
    d.line(13, 2, 2, 13, shade(p["metal"], 0.1))


def _hole(d, p, v):
    d.ellipse(8, 8, 6.5, 5.5, hexc("0e0a10"))


def _tent(d, p, v):
    d.poly([(1, 14), (8, 1), (14, 14)], hexc("c8b890"))
    d.line(8, 1, 8, 14, shade(hexc("c8b890"), -0.3))


def _chimney(d, p, v):
    d.rect(4, 2, 11, 15, shade(p["wall"], -0.1))
    d.rect(3, 1, 12, 3, shade(p["wall"], 0.2))


def _dock(p, v):
    c = t_bridge(p, v)
    return c


def _arch(d, p, v):
    d.rect(0, 0, 3, 15, p["wall"])
    d.rect(12, 0, 15, 15, p["wall"])
    d.rect(0, 0, 15, 3, shade(p["wall"], 0.2))


def world_tile(kind):
    def f(p, v):
        c = Canvas(16, 16)
        g = p["grass"]
        if kind in ("plains", "town_mark", "dungeon_mark", "city", "ruin", "cave", "forest", "hills"):
            noise_fill(c, g, 1300 + v, 0.25)
        d = Canvas(16, 16)
        if kind == "forest":
            for (x, y) in ((4, 5), (11, 4), (7, 10), (13, 11), (2, 12)):
                d.ellipse(x, y, 3, 3, p["foliage"])
                d.put(x - 1, y - 2, shade(p["foliage"], 0.3))
        elif kind == "hills":
            d.ellipse(6, 10, 5, 3.5, shade(g, -0.12))
            d.ellipse(12, 7, 4, 3, shade(g, -0.06))
        elif kind == "mountain":
            noise_fill(c, g, 1350 + v, 0.2)
            d.poly([(1, 15), (8, 1), (15, 15)], p["rock"])
            d.poly([(8, 1), (15, 15), (9, 15)], shade(p["rock"], -0.25))
            d.poly([(6, 5), (8, 1), (10, 5)], p["snow"])
        elif kind == "town_mark":
            d.rect(3, 7, 7, 12, hexc("c8b08a"))
            d.poly([(2, 7), (5, 3), (8, 7)], hexc("8a3a2a"))
            d.rect(9, 5, 13, 12, hexc("c8b08a"))
            d.poly([(8, 5), (11, 1), (14, 5)], hexc("8a3a2a"))
        elif kind == "city":
            d.rect(1, 5, 14, 13, hexc("7a7c78"))
            for x in range(1, 15, 3):
                d.rect(x, 3, x + 1, 5, hexc("7a7c78"))
            d.rect(6, 8, 9, 13, hexc("2a2a30"))
            d.rect(7, 0, 8, 3, hexc("a82a2a"))
        elif kind == "dungeon_mark":
            d.poly([(2, 14), (8, 3), (14, 14)], p["rock"])
            d.ellipse(8, 12, 2.5, 3, hexc("100c14"))
        elif kind == "cave":
            d.ellipse(8, 10, 6, 5, p["rock"])
            d.ellipse(8, 11, 3, 3, hexc("100c14"))
        elif kind == "ruin":
            d.rect(3, 6, 5, 13, p["stone"])
            d.rect(10, 4, 12, 13, p["stone"])
            d.rect(3, 6, 12, 7, shade(p["stone"], 0.1))
        elif kind == "island":
            for y in range(16):
                for x in range(16):
                    c.put(x, y, p["water"])
            d.ellipse(8, 8, 6, 5, p["sand"])
            d.ellipse(8, 7, 4, 3, g)
        elif kind == "reef":
            for y in range(16):
                for x in range(16):
                    c.put(x, y, p["deep"])
            for (x, y) in ((3, 4), (10, 6), (6, 12), (13, 12)):
                d.ellipse(x, y, 2, 1.5, p.get("reef", hexc("6a3a4a")))
        if not d.px == Canvas(16, 16).px:
            d.light(0.15)
            d.outline((30, 26, 34, 255))
        c.blit(d, 0, 0)
        return c
    return f


TILE_FN = {
    "floor": lambda p, v: t_floor(p, v, "floor"), "floor2": lambda p, v: t_floor(p, v, "floor2"),
    "path": lambda p, v: t_floor(p, v, "path"), "wall_top": t_wall_top, "wall_face": t_wall_face,
    "water": t_water, "shallow": t_shallow, "bridge": t_bridge, "grass": t_grass, "roof": t_roof,
    "roof_eave": lambda p, v: t_roof(p, v, "eave"), "roof_ridge": lambda p, v: t_roof(p, v, "ridge"),
    "house": t_house, "window": t_window, "door": t_door, "doorway": t_doorway, "stairs": t_stairs,
    "sand": lambda p, v: t_simple(p, v, "sand"), "snow": lambda p, v: t_simple(p, v, "snow", amt=0.12),
    "ice": t_ice, "ash": lambda p, v: t_simple(p, v, "ash"), "salt": lambda p, v: t_simple(p, v, "salt", amt=0.15),
    "moss": lambda p, v: t_simple(p, v, "moss"), "roots": t_roots, "puddle": t_shallow, "ember": t_ember,
    "deep": lambda p, v: t_water(p, v, "deep"), "cliff": t_cliff, "cliff_top": lambda p, v: t_cliff(p, v, True),
    "rubble": t_rubble, "void": lambda p, v: t_simple(p, v, "void", amt=0.05),
    "fence": overlay(lambda p, v: t_floor(p, v % 3, "floor2"), _fence),
    "hedge": overlay(t_grass, _hedge), "garden": overlay(t_grass, _garden),
    "counter": overlay(lambda p, v: t_floor(p, 0), _counter), "rail": overlay(lambda p, v: t_floor(p, 0, "path"), _rail),
    "dock": _dock, "ladder": overlay(t_wall_face, lambda d, p, v: [d.rect(4, 0, 5, 15, p["wood"]), d.rect(10, 0, 11, 15, p["wood"])] + [d.rect(4, y, 11, y, shade(p["wood"], 0.2)) for y in range(2, 16, 4)]),
    "carpet": lambda p, v: t_simple(p, v, "accent", amt=0.1),
    "grate": overlay(lambda p, v: t_floor(p, 0), lambda d, p, v: [d.rect(1, 1, 14, 14, shade(p["metal"], -0.3))] + [d.rect(x, 1, x, 14, p["metal"]) for x in range(2, 14, 3)]),
    "reef": world_tile("reef"), "plains": world_tile("plains"), "forest": world_tile("forest"), "hills": world_tile("hills"),
    "mountain": world_tile("mountain"), "town_mark": world_tile("town_mark"), "dungeon_mark": world_tile("dungeon_mark"),
    "city": world_tile("city"), "ruin": world_tile("ruin"), "cave": world_tile("cave"), "island": world_tile("island"),
    "lift": overlay(lambda p, v: t_floor(p, 0), _lift), "gate": overlay(lambda p, v: t_floor(p, 0), _gate),
    "sluice": overlay(lambda p, v: t_floor(p, 0), _sluice), "pool": overlay(lambda p, v: t_floor(p, 0), _pool),
    "hole": overlay(lambda p, v: t_floor(p, 0), _hole), "mural": overlay(t_wall_face, _mural),
    "awning": overlay(lambda p, v: t_floor(p, v % 3), _awning), "chain": overlay(lambda p, v: t_simple(p, v, "void", amt=0.05), _chain),
    "cable": overlay(lambda p, v: t_simple(p, v, "void", amt=0.05), _cable), "vine": overlay(t_wall_face, _vine),
    "rock": overlay(lambda p, v: t_floor(p, v % 3, "floor2"), _rock), "crate": overlay(lambda p, v: t_floor(p, 0), _crate),
    "barrel": overlay(lambda p, v: t_floor(p, 0), _barrel), "table": overlay(lambda p, v: t_floor(p, 0), _table),
    "bed": overlay(lambda p, v: t_floor(p, 0), _bed), "machine": overlay(lambda p, v: t_floor(p, 0), _machine),
    "pipe": overlay(lambda p, v: t_floor(p, 0), _pipe), "crystal": overlay(lambda p, v: t_floor(p, 0), _crystal),
    "bell": overlay(lambda p, v: t_floor(p, 0), _bell), "vent": overlay(lambda p, v: t_floor(p, 0), _vent),
    "cart": overlay(lambda p, v: t_floor(p, 0, "path"), _cart), "anvil": overlay(lambda p, v: t_floor(p, 0), _anvil),
    "boat": overlay(lambda p, v: t_water(p, v), _boat), "well": overlay(lambda p, v: t_floor(p, 0, "path"), _well),
    "sign": overlay(lambda p, v: t_floor(p, 0, "path"), _sign), "bench": overlay(lambda p, v: t_floor(p, 0), _bench),
    "laundry": overlay(lambda p, v: t_floor(p, 0, "path"), _laundry), "chest_deco": overlay(lambda p, v: t_floor(p, 0), _chest),
    "book": overlay(lambda p, v: t_floor(p, 0), _book), "altar": overlay(lambda p, v: t_floor(p, 0), _altar),
    "brazier": overlay(lambda p, v: t_floor(p, 0), _brazier), "wheel": overlay(lambda p, v: t_water(p, v), _wheel),
    "gear": overlay(lambda p, v: t_floor(p, 0), _gear), "shelter": overlay(lambda p, v: t_floor(p, 0), _shelter),
    "tent": overlay(lambda p, v: t_floor(p, v % 3, "floor2"), _tent), "lever_deco": overlay(lambda p, v: t_floor(p, 0), _lever),
    "flower": overlay(t_grass, _flower), "window_int": lambda p, v: t_window(p, v, False), "arch": overlay(lambda p, v: t_floor(p, 0), _arch),
    "stair_l": t_stairs, "stair_r": t_stairs, "chimney": overlay(t_roof, _chimney),
}


# ---------------------------------------------------------------- tall props (16x32)
def prop(kind, p, v=0):
    c = Canvas(16, 32)
    if kind in ("tree", "tree2"):
        fo = p["foliage"] if kind == "tree" else shade(p["foliage"], 0.12)
        c.rect(6, 20, 9, 30, shade(p["wood"], -0.2), 1)
        c.ellipse(8, 12, 7.5, 8, fo, 2)
        c.ellipse(5, 9, 3.5, 3.5, shade(fo, 0.15), 2)
        c.ellipse(11, 15, 3, 3, shade(fo, -0.15), 2)
        r = rnd(1400 + v)
        for _ in range(8):
            c.put(r.randrange(3, 13), r.randrange(6, 18), shade(fo, 0.3), 2)
    elif kind == "lamp":
        c.rect(7, 10, 8, 30, shade(p["metal"], -0.3), 1)
        c.rect(5, 28, 10, 30, shade(p["metal"], -0.4), 1)
        c.rect(5, 4, 10, 10, shade(p["metal"], -0.2), 2)
        c.rect(6, 5, 9, 9, p["light"], 3)
        c.rect(4, 3, 11, 4, shade(p["metal"], -0.4), 2)
    elif kind == "lantern_post":
        c.rect(7, 8, 8, 30, shade(p["wood"], -0.2), 1)
        c.rect(8, 8, 12, 8, shade(p["wood"], -0.2), 1)
        c.rect(10, 9, 13, 14, p["accent"], 3)
        c.rect(11, 10, 12, 13, p["light"], 3)
    elif kind == "pillar":
        c.rect(3, 2, 12, 5, shade(p["wall"], 0.2), 1)
        c.rect(4, 5, 11, 27, p["wall"], 1)
        c.rect(4, 5, 5, 27, shade(p["wall"], 0.2), 1)
        c.rect(3, 27, 12, 31, shade(p["wall"], -0.2), 1)
    elif kind == "statue":
        c.rect(3, 24, 12, 31, p["stone"], 1)
        c.ellipse(8, 8, 3, 3, shade(p["stone"], 0.1), 2)
        c.rect(5, 11, 10, 23, shade(p["stone"], 0.05), 2)
        c.line(10, 12, 13, 5, shade(p["stone"], 0.05), 2, 2)
    elif kind == "shelf":
        c.rect(1, 4, 14, 31, shade(p["wood"], -0.2), 1)
        cols = [p["accent"], hexc("4a6a9a"), hexc("6a8a4a"), hexc("c0a050"), hexc("8a5a8a")]
        for i, y in enumerate(range(6, 30, 6)):
            c.rect(2, y + 4, 13, y + 4, shade(p["wood"], 0.1), 1)
            for j, x in enumerate(range(2, 13, 2)):
                c.rect(x, y, x, y + 3, cols[(i + j) % 5], 2)
    elif kind == "banner":
        c.rect(7, 2, 8, 30, shade(p["wood"], -0.3), 1)
        cl = p.get("cloth", p["accent"])
        c.rect(3, 4, 12, 18, cl, 2)
        c.poly([(3, 18), (12, 18), (7.5, 23)], cl, 2)
        c.rect(6, 8, 9, 12, p["light"], 3)
    elif kind == "crystal_tall":
        cr = p.get("crystal", p["glass"])
        c.poly([(8, 2), (13, 14), (11, 30), (5, 30), (3, 14)], cr, 2)
        c.line(8, 3, 8, 29, shade(cr, 0.4), 1, 3)
    elif kind == "pipe_tall":
        c.rect(5, 0, 10, 31, p["metal"], 1)
        c.rect(5, 0, 6, 31, shade(p["metal"], 0.3), 1)
        for y in (6, 18):
            c.rect(4, y, 11, y + 2, shade(p["metal"], -0.25), 2)
        c.rect(7, 12, 8, 13, p["accent"], 3)
    elif kind == "mast":
        c.rect(7, 0, 8, 31, p["wood"], 1)
        c.rect(1, 6, 14, 7, p["wood"], 1)
        c.rect(2, 8, 13, 20, p.get("cloth", hexc("d8d0b8")), 2)
    elif kind == "totem":
        c.rect(5, 6, 10, 31, p["wood"], 1)
        c.rect(3, 4, 12, 7, p.get("cloth", p["accent"]), 2)
        c.ellipse(8, 14, 2, 2, p["light"], 3)
    c.light(0.15)
    c.outline((28, 22, 28, 255))
    return c


def build_tileset(name):
    p = P[name]
    p.setdefault("glass", hexc("9ad0e0"))
    atlas = Image.new("RGBA", (16 * 4, 16 * len(KINDS)), (0, 0, 0, 0))
    for r, k in enumerate(KINDS):
        for v in range(4):
            try:
                c = TILE_FN[k](p, v)
            except KeyError as e:
                raise KeyError(f"{name}:{k} missing palette {e}")
            atlas.paste(c.image(), (v * 16, r * 16))
    props = Image.new("RGBA", (16 * len(PROPS), 32), (0, 0, 0, 0))
    for i, k in enumerate(PROPS):
        props.paste(prop(k, p, i).image(), (i * 16, 0))
    return atlas, props
