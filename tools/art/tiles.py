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


# =================================================================================================================
# Library tilesets (owner's licensed Time Fantasy packs) -> game/assets/ext/tiles/<family>_ext.png + .json
# Rules per map kind are read by field.gd (_draw_ext). Specs below reference library-relative sheets; the builder
# copies only the referenced regions into one atlas per family. Unlisted kinds fall back to the generated atlas.
# =================================================================================================================
from art.pix import lib_img

FB = "finalbossblues/"
FF = FB + "tf_fairyforest_12.28.20/1x/tf_ff_tile"
SP = FB + "tf_steampunk/RPGMAKER_16x16/tileset/tfsteampunk_tile"
SW = FB + "tf_sewers/RPGMAKER_16x16/tfsewers_tile"
FU = FB + "FutureFantasy/100/tilesets/"
RU = FB + "16/tf_"
AS = FB + "1x/tf_"


class Src:
    """A rectangular region of a library sheet, optionally recoloured (fn: Image->Image)."""
    def __init__(self, sheet, x, y, w, h, fn=None):
        self.sheet, self.x, self.y, self.w, self.h, self.fn = sheet, x, y, w, h, fn

    def key(self):
        return (self.sheet, self.x, self.y, self.w, self.h, id(self.fn) if self.fn else 0)

    def image(self):
        src = lib_img(self.sheet.split("@")[0])
        if self.sheet.endswith("@2x"):      # RPG Maker VX (2x) sheet of 1x art: exact nearest halving
            src = src.resize((src.width // 2, src.height // 2), Image.NEAREST)
        im = src.crop((self.x, self.y, self.x + self.w, self.y + self.h))
        return self.fn(im) if self.fn else im


def a2(sheet, i, j, fn=None):
    """RPG Maker A2-layout autotile block (32x48) at block column i, row j."""
    return Src(sheet, i * 32, j * 48, 32, 48, fn)


def a1(sheet, j, cols=(0, 1, 2), fn=None):
    """Animated A1 water: the same block in 3 frame columns."""
    return [a2(sheet, c, j, fn) for c in cols]


def a4(sheet, i, k, fn=None):
    """A4 wall pair: (top 32x48, face 32x32) at column i, pair row k."""
    return Src(sheet, i * 32, k * 80, 32, 48, fn), Src(sheet, i * 32, k * 80 + 48, 32, 32, fn)


def t16(sheet, x, y, fn=None, w=1, h=1):
    return Src(sheet, x * 16, y * 16, 16 * w, 16 * h, fn)


class Synth:
    """An A2-layout 32x48 block synthesised from a 3x3 blob of 16x16 tiles (TL,T,TR / L,C,R / BL,B,BR) and an
    optional 2x2 inner-corner piece (32x32; the corners of the region are used as inner-corner quarters)."""
    def __init__(self, nine, inner=None, face=False):
        self.nine, self.inner, self.face = nine, inner, face

    def key(self):
        return ("synth", tuple(s.key() for s in self.nine), self.inner.key() if self.inner else None, self.face)

    def image(self):
        n = [s.image() for s in self.nine]
        TL, T, TR, L, C, R, BL, B, BR = n
        out = Image.new("RGBA", (32, 32 if self.face else 48), (0, 0, 0, 0))
        oy = 0 if self.face else 16
        if not self.face:
            out.paste(C, (0, 0))
            if self.inner is not None:
                inn = self.inner.image()   # 32x32 showing a 'hole': its outer quarters are inner corners
                out.paste(inn.crop((24, 24, 32, 32)), (16, 0))   # TL quarter inner corner: bottom-right of hole area
                out.paste(inn.crop((0, 24, 8, 32)), (24, 0))
                out.paste(inn.crop((24, 0, 32, 8)), (16, 8))
                out.paste(inn.crop((0, 0, 8, 8)), (24, 8))
            else:
                out.paste(C, (16, 0))
        # 2x2 island: TL|TR / BL|BR, with edge quarters taken from T/L/R/B and interior from C
        quad = [[TL, T, T, TR], [L, C, C, R], [L, C, C, R], [BL, B, B, BR]]
        for qy in range(4):
            for qx in range(4):
                src = quad[qy][qx]
                sx = 0 if qx in (0, 2) else 8
                sy = 0 if qy in (0, 2) else 8
                out.paste(src.crop((sx, sy, sx + 8, sy + 8)), (qx * 8, oy + qy * 8))
        return out


def tile(*srcs, w=None, fps=None, under=None, casts=False, g=None):
    return dict(type="tile", src=list(srcs), w=w, fps=fps, under=under, casts=casts, g=g)


def auto(src, under=None, g=None, casts=False, fps=None, pingpong=False):
    frames = src if isinstance(src, list) else [src]
    return dict(type="auto", src=frames, under=under, g=g, casts=casts, fps=fps, pingpong=pingpong)


def wall(pair, g=None, casts=True, under=None):
    top, face = pair
    return dict(type="wall", top=top, face=face, g=g, casts=casts, under=under)


def hrow(l, m, r, single=None, under=None, g=None, casts=False):
    return dict(type="hrow", src=[l, m, r, single or m], under=under, g=g, casts=casts)


def stamp(src, tall=False, under=None, alts=(), dx=0, dy=0, inner=None, g=None):
    """Object drawn bottom-centred on its cell. `inner`: variant used when the cell above is the same group
    (e.g. tall pines inside a forest mass, lower trees at its edge so rivers/paths above stay visible)."""
    return dict(type="stamp", src=src, alts=list(alts), tall=tall, under=under, dx=dx, dy=dy, inner=inner, g=g)


def grid9(tiles9, under=None, g=None, casts=False):
    return dict(type="grid9", src=list(tiles9), under=under, g=g, casts=casts)


class Fn:
    """A region composed in code from library pixels (fn() -> RGBA image). `srcs`: library sheets it reads."""
    def __init__(self, name, fn, srcs):
        self.name, self.fn, self.srcs = name, fn, list(srcs)
        self._im = None

    def key(self):
        return ("fn", self.name)

    def image(self):
        if self._im is None:
            self._im = self.fn()
        return self._im

    @property
    def w(self):
        return self.image().width

    @property
    def h(self):
        return self.image().height


def pair(src, single=None, under="@", g=None, dy=0):
    """Two-cell object (tent, awning): a horizontal run of this kind is split into pairs from its left end; each
    pair draws `src` centred over both cells, a leftover single cell draws `single` (default: `src`)."""
    return dict(type="pair", src=src, one=single or src, under=under, g=g, dy=dy)


LIB_TILESETS = {}   # family -> {kind: rule}; filled per family below


def _pack(regions):
    """Shelf-pack regions (list of (key, image)) into an atlas; returns atlas and key->(x, y)."""
    regions = sorted(regions, key=lambda r: (-r[1].height, -r[1].width))
    W = 512
    x = y = shelf = 0
    pos = {}
    for k, im in regions:
        if x + im.width > W:
            x, y, shelf = 0, y + shelf, 0
        pos[k] = (x, y)
        x += im.width
        shelf = max(shelf, im.height)
    atlas = Image.new("RGBA", (W, max(16, y + shelf)), (0, 0, 0, 0))
    ims = dict(regions)
    for k, (px, py) in pos.items():
        atlas.paste(ims[k], (px, py))
    return atlas, pos


def build_family(name):
    spec = LIB_TILESETS[name]
    regions, seen, sources = [], set(), set()

    def reg(s):
        k = s.key()
        if k not in seen:
            seen.add(k)
            regions.append((k, s.image()))
            if isinstance(s, Synth):
                sources.update(n.sheet.split("@")[0] for n in s.nine)
            elif isinstance(s, Fn):
                sources.update(x.split("@")[0] for x in s.srcs)
            else:
                sources.add(s.sheet.split("@")[0])
        return k

    for kind, r in spec.items():
        for key in ("src", "top", "face", "alts", "inner", "one"):
            v = r.get(key)
            if v is None:
                continue
            for s in (v if isinstance(v, list) else [v]):
                reg(s)
    atlas, pos = _pack(regions)
    rules = {}
    for kind, r in spec.items():
        o = {"type": r["type"]}
        for opt in ("under", "g", "fps", "w", "dx", "dy"):
            if r.get(opt) not in (None, 0):
                o[opt] = r[opt]
        if r.get("casts"):
            o["casts"] = True
        if r.get("pingpong"):
            o["pingpong"] = True
        if r["type"] in ("tile", "hrow", "grid9"):
            o["t"] = [list(pos[s.key()]) for s in r["src"]]
        elif r["type"] == "auto":
            o["b"] = [list(pos[s.key()]) for s in r["src"]]
        elif r["type"] == "wall":
            o["top"] = [list(pos[r["top"].key()])]
            o["face"] = [list(pos[r["face"].key()])]
        elif r["type"] == "pair":
            s, o1 = r["src"], r["one"]
            o["r"] = list(pos[s.key()]) + [s.w, s.h]
            o["one"] = list(pos[o1.key()]) + [o1.w, o1.h]
        elif r["type"] == "stamp":
            s = r["src"]
            o["r"] = list(pos[s.key()]) + [s.w, s.h]
            if r["alts"]:
                o["alt"] = [list(pos[a.key()]) + [a.w, a.h] for a in r["alts"]]
            if r["tall"] or s.w > 16 or s.h > 16:
                o["tall"] = True      # anything overhanging its cell is y-sorted (ground chunks have no margin)
            if r.get("inner") is not None:
                i = r["inner"]
                o["inner"] = list(pos[i.key()]) + [i.w, i.h]
        rules[kind] = o
    return atlas, {"family": name, "rules": rules}, sorted(sources)


def build_library(save_ext):
    # field objects strip: TF treasure chests (closed/open) over the generated strip (save lamp, switch, spring kept)
    import os
    base = Image.open(os.path.join(os.path.dirname(__file__), "..", "..", "game", "assets", "sprites", "objects.png")).convert("RGBA")
    ch = FB + "FutureFantasy/100/characters/chests.png"
    for i, y in enumerate((136, 232)):
        base.paste((0, 0, 0, 0), (i * 16, 0, i * 16 + 16, 16))
        base.alpha_composite(lib_img(ch).crop((0, y, 16, y + 16)), (i * 16, 0))
    save_ext(base, "sprites/objects.png", "objects", [ch], "chest closed/open from Future Fantasy chests")
    for name in LIB_TILESETS:
        atlas, rules, sources = build_family(name)
        save_ext(atlas, f"tiles/{name}_ext.png", "tileset_ext", sources, "16x16 rules atlas")
        save_ext(rules, f"tiles/{name}_ext.json", "tileset_rules", sources)


# ---- shared sheets ---------------------------------------------------------------------------------------------
WV = FB + "TimeFantasy_Winter/rpgmaker/RPGMAKER_VX/tf_winter_tile"      # 2x sheets -> "@2x"
W_A1, W_A2, W_B = WV + "A1.png@2x", WV + "A2.png@2x", WV + "B.png@2x"
FF_A1, FF_A2, FF_A5 = FF + "A1.png", FF + "A2.png", FF + "A5_a.png"
SP_A2, SP_A4, SP_A5D, SP_A5I = SP + "A2.png", SP + "A4.png", SP + "A5_dungeon.png", SP + "A5_int.png"
SP_C1, SP_C2, SP_I1, SP_I2, SP_D = SP + "B_city1.png", SP + "B_city2.png", SP + "B_int1.png", SP + "B_int2.png", SP + "B_dungeon.png"
SW_A1, SW_A2, SW_A4, SW_A5, SW_B = SW + "A1_1.png", SW + "A2_1.png", SW + "A4_1.png", SW + "A5_1.png", SW + "B_1.png"
RU_A1, RU_A2, RU_A4, RU_A5 = RU + "A1_ruins.png", RU + "A2_ruins.png", RU + "A4_ruins.png", RU + "A5_ruins1.png"
AS_A1, AS_A2, AS_A5, AS_B = AS + "A1_ashlands_1.png", AS + "A2_ashlands_1.png", AS + "A5_ashlands_1.png", AS + "B_ashlands_1.png"
FU_A1, FU_A2, FU_A4 = FU + "future_tileA1.png", FU + "future_tileA2.png", FU + "future_tileA4.png"
CL = FB + "rpgmaker_1/cloud_tile"
CL_A1, CL_A2, CL_A5, CL_B = CL + "A1_1.png", CL + "A2_1.png", CL + "A5_1.png", CL + "B_1.png"
AT_A2 = FB + "RPGMAKER-100/tf_A2_atlantis.png"
SP_C2B, SP_C2C = SP + "B_city2b.png", SP + "B_city2c.png"


def nine(sheet, x, y, cols=(0, 1, 3), rows=(0, 1, 2)):
    """3x3 tile coords from a rectangular piece: columns/rows offsets for left/mid/right and top/mid/bottom."""
    return [t16(sheet, x + cx, y + ry) for ry in rows for cx in cols]


# common street/room props (steampunk city/interior sets)
def props_kit(ground="@"):
    return {
        "crate": stamp(Src(SP_C1, 48, 192, 16, 32), tall=True, under=ground, alts=[Src(SP_C1, 0, 192, 16, 32)]),
        "barrel": stamp(Src(SP_C1, 48, 224, 16, 32), tall=True, under=ground, alts=[Src(SP_C1, 64, 224, 16, 32)]),
        "lamp": stamp(Src(SP_C1, 16, 16, 16, 64), tall=True, under=ground),
        "doorway": tile(t16(SP_C2, 1, 7)),
        "rubble": stamp(Src(AS_B, 35, 34, 11, 11), under=ground),
        "crystal": stamp(Src(W_B, 97, 66, 13, 14), under=ground),
    }


LIB_TILESETS["town_r01"] = {
    "grass": auto(a2(FF_A2, 0, 1)),
    "path": auto(a2(FF_A2, 2, 1)),
    "garden": auto(a2(W_A2, 1, 0)),
    "water": auto(a1(W_A1, 1), fps=3, pingpong=True),
    "floor": auto(a2(SP_A2, 1, 0)),
    "tree": stamp(Src(W_B, 227, 55, 26, 23), tall=True, under="grass", inner=Src(W_B, 4, 104, 40, 52)),
    "cliff": grid9(nine(FF_A5, 0, 10, cols=(1, 1, 2), rows=(0, 1, 3)), casts=True),
    "roof": auto(Synth(nine(SP_C2, 0, 1)), g="roof"),
    "chimney": tile(t16(SP_C2, 2, 0), under="roof", g="roof"),
    "house": hrow(t16(SP_C2, 0, 5), t16(SP_C2, 1, 5), t16(SP_C2, 3, 5), g="house", casts=True),
    "window": tile(t16(SP_C2, 14, 4), under="house", g="house", casts=True),
    "door": stamp(Src(SP_C2, 64, 96, 16, 32), under="house"),
    **props_kit(),
}


# ---- more shared sheets -----------------------------------------------------------------------------------------

_recol_cache = {}


def recolor(hue=0.0, sat=1.0, val=1.0):
    """Hue-rotate (turns) / saturation / value scale — returns a cached Image->Image function."""
    key = (hue, sat, val)
    if key in _recol_cache:
        return _recol_cache[key]
    import colorsys

    def fn(im):
        out = im.copy()
        px = out.load()
        for y in range(out.height):
            for x in range(out.width):
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                r2, g2, b2 = colorsys.hsv_to_rgb((h + hue) % 1.0, min(1, s * sat), min(1, v * val))
                px[x, y] = (int(r2 * 255), int(g2 * 255), int(b2 * 255), a)
        return out
    _recol_cache[key] = fn
    return fn


def tint(*stops, keep=0.25):
    """Gradient-map by luminance onto hex colour stops (dark->light), keeping `keep` of the original colour so
    texture and small accents survive. Cached Image->Image function."""
    key = ("tint", stops, keep)
    if key in _recol_cache:
        return _recol_cache[key]
    cs = [hexc(h)[:3] for h in stops]

    def ramp(l):
        t = l * (len(cs) - 1)
        i = min(int(t), len(cs) - 2)
        f = t - i
        return tuple(cs[i][k] + (cs[i + 1][k] - cs[i][k]) * f for k in range(3))

    def fn(im):
        out = im.copy()
        px = out.load()
        for y in range(out.height):
            for x in range(out.width):
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                l = (0.3 * r + 0.59 * g + 0.11 * b) / 255
                m = ramp(l)
                px[x, y] = tuple(int(m[k] * (1 - keep) + (r, g, b)[k] * keep) for k in range(3)) + (a,)
        return out
    _recol_cache[key] = fn
    return fn


# water flavours (A1 animated autotiles, 3 frames ping-pong)
def water(sheet, row, cols=(0, 1, 2), fn=None, g="water"):
    return auto(a1(sheet, row, cols, fn), fps=3, pingpong=True, g=g)


W_GRASS = lambda: water(W_A1, 1)
W_DIRT = lambda: water(W_A1, 3)
W_STONE = lambda: water(W_A1, 3, (4, 5, 6))
W_SNOW = lambda: water(W_A1, 1, (4, 5, 6))
W_OPEN = lambda: water(W_A1, 0)
TREE = stamp(Src(W_B, 227, 55, 26, 23), tall=True, under="grass", inner=Src(W_B, 4, 104, 40, 52), g="tree")
TREE2 = stamp(Src(W_B, 4, 161, 39, 47), tall=True, under="grass", g="tree")
PINE_SNOW = stamp(Src(W_B, 227, 87, 26, 23), tall=True, under="snow", inner=Src(W_B, 52, 104, 40, 52), g="tree")
CLIFF = grid9(nine(FF_A5, 0, 10, cols=(1, 1, 2), rows=(0, 1, 3)), casts=True)
WOOD_DECK = auto(a2(FU_A2, 0, 3))


def roofs(sheet, fn=None):
    """Roof autotile + house front/window/door + chimney from a steampunk city2-layout sheet."""
    t = lambda x, y: t16(sheet, x, y, fn)
    return {
        "roof": auto(Synth([t(0, 1), t(1, 1), t(3, 1), t(0, 2), t(1, 2), t(3, 2), t(0, 3), t(1, 3), t(3, 3)]), g="roof"),
        "chimney": tile(t(2, 0), under="roof", g="roof"),
        "house": hrow(t(0, 5), t(1, 5), t(3, 5), g="house", casts=True),
        "window": tile(t16(sheet, 14, 4, fn), under="house", g="house", casts=True),
        "door": stamp(Src(sheet, 64, 96, 16, 32, fn), under="house"),
    }


def room_kit(ground="@"):
    return {
        "shelf": stamp(Src(SP_I1, 208, 129, 16, 52), tall=True, under=ground),
        "book": stamp(Src(SP_I1, 96, 214, 15, 8), under=ground),
        "bed": stamp(Src(FU + "modern_tileB_inside2.png", 128, 176, 16, 32), tall=True, under=ground,
                     alts=[Src(FU + "modern_tileB_inside2.png", 128, 112, 16, 32)]),
        "table": stamp(Src(SP_I1, 195, 199, 26, 24), tall=True, under=ground),
        "bench": stamp(Src(SP_I1, 2, 100, 12, 24), tall=True, under=ground),
        "chest_deco": stamp(Src(SP_I2, 80, 224, 16, 15), under=ground),
        "machine": stamp(Src(SP_D, 0, 32, 16, 32), tall=True, under=ground, alts=[Src(SP_D, 32, 32, 16, 32)]),
        "gear": stamp(Src(SP_D, 240, 80, 16, 16), under=ground),
        "wheel": stamp(Src(SP_D, 128, 0, 32, 32), tall=True, under=ground),
        "pipe": tile(t16(SP_D, 0, 11), under=ground),
        "vent": tile(t16(SP_D, 5, 14), under=ground),
        **props_kit(ground),
    }


def dungeon(floor, wall_pair, floor2=None, water_rule=None, extra=None, ground="floor"):
    d = {"floor": floor, "wall": wall(wall_pair)}
    if floor2:
        d["floor2"] = floor2
    if water_rule:
        d["water"] = water_rule
    d.update(room_kit())
    d.update(extra or {})
    return d


LIB_TILESETS["town_r01"].update({"tree": TREE, "tree2": TREE2, "cliff": CLIFF, "bridge": WOOD_DECK})

LIB_TILESETS["capital"] = {
    "path": auto(a2(SP_A2, 1, 0)), "floor": auto(a2(SP_A2, 0, 2)), "grass": auto(a2(FF_A2, 0, 1)),
    "wall": wall(a4(SP_A4, 1, 0)), "water": W_STONE(), "stairs": tile(t16(FF_A5, 6, 10)),
    **roofs(SP_C2C), **room_kit(),
}
LIB_TILESETS["quarry"] = dungeon(auto(a2(AS_A2, 3, 0)), a4(SW_A4, 0, 0), floor2=auto(a2(AS_A2, 0, 0)), water_rule=W_DIRT(),
                                 extra={"path": auto(a2(FF_A2, 3, 1)), "rock": stamp(Src(AS_B, 100, 34, 23, 12), under="@"),
                                        "rubble": stamp(Src(AS_B, 35, 34, 11, 11), under="@"), "grass": auto(a2(FF_A2, 0, 1)), "cliff": CLIFF,
                                        "shallow": water(RU_A1, 0, (4, 5, 6), g="shallow"), **roofs(SP_C2)})
LIB_TILESETS["underways"] = dungeon(auto(a2(SW_A2, 0, 0)), a4(SW_A4, 0, 0), floor2=auto(a2(SW_A2, 1, 0)),
                                    water_rule=water(SW_A1, 0), extra={"dock": WOOD_DECK, "cliff": CLIFF})
LIB_TILESETS["grove"] = {
    "floor2": auto(a2(FF_A2, 1, 1)), "grass": auto(a2(FF_A2, 0, 1)), "path": auto(a2(FF_A2, 2, 1)), "floor": auto(a2(FF_A2, 3, 1)),
    "wall": CLIFF, "water": W_GRASS(), "shallow": water(RU_A1, 1, (4, 5, 6), g="shallow"), "tree": TREE, "tree2": TREE2,
    "hedge": stamp(Src(W_B, 227, 55, 26, 23), tall=True, under="grass"), "cliff": CLIFF, **props_kit(),
}
LIB_TILESETS["grove_flood"] = {
    "water": water(W_A1, 2), "roots": auto(a2(FF_A2, 3, 1)), "shallow": water(RU_A1, 1, (4, 5, 6), g="shallow"),
    "floor": auto(a2(FF_A2, 0, 0)), **props_kit(),
}
LIB_TILESETS["furnace"] = dungeon(auto(a2(SP_A2, 5, 1)), a4(SP_A4, 2, 0), floor2=auto(a2(SP_A2, 6, 1)),
                                  extra={"grass": auto(a2(FF_A2, 0, 1)), "garden": auto(a2(W_A2, 1, 0)),
                                         "ember": water(AS_A1, 2, g="ember"), "bridge": auto(a2(SP_A2, 7, 1)),
                                         "path": auto(a2(SP_A2, 7, 0)), "pool": water(AS_A1, 2, g="ember")})
LIB_TILESETS["town_r02"] = {
    "path": auto(a2(SP_A2, 1, 0)), "wall": wall(a4(SP_A4, 0, 0)), "grass": auto(a2(FF_A2, 0, 1)), "tree": TREE,
    "garden": auto(a2(W_A2, 1, 0)), "stairs": tile(t16(FF_A5, 6, 10)), "pool": W_STONE(), **roofs(SP_C2), **room_kit(),
}
LIB_TILESETS["archive"] = dungeon(auto(a2(RU_A2, 0, 0)), a4(RU_A4, 0, 0), floor2=auto(a2(RU_A2, 2, 0)), water_rule=water(RU_A1, 0),
                                  extra={"shallow": water(RU_A1, 1, g="shallow"), "dock": WOOD_DECK, "pool": water(RU_A1, 1, g="pool"),
                                         "bridge": WOOD_DECK, "puddle": water(RU_A1, 1, g="shallow")})
TEAL = tint("10201e", "1e4a48", "3a8a84", "a8e0d8", keep=0.3)
LIB_TILESETS["town_r03"] = {
    "path": auto(a2(SP_A2, 0, 2)), "water": W_STONE(), "wall": wall(a4(SP_A4, 1, 0)), "dock": WOOD_DECK, "bridge": WOOD_DECK,
    **roofs(SP_C2, TEAL), **room_kit(),
}
SKY_VOID = auto(a1(CL_A1, 0), fps=2, pingpong=True, g="void")
LIB_TILESETS["sky"] = dungeon(auto(a2(CL_A2, 0, 0)), a4(RU_A4, 0, 0), extra={"void": SKY_VOID, "bridge": WOOD_DECK,
                                                                           "path": auto(a2(CL_A2, 1, 0)), **roofs(SP_C2)})
LIB_TILESETS["town_r04"] = {"path": auto(a2(CL_A2, 0, 0)), "void": SKY_VOID, "floor": auto(a2(CL_A2, 1, 0)),
                            "stairs": tile(t16(FF_A5, 6, 10)), **roofs(SP_C2, tint("24160c", "7a4a1a", "c8943a", "f8e0a0", keep=0.3)), **room_kit()}
LILAC = tint("2a2238", "7a6a98", "c8bce0", "f4f0fa")
LIB_TILESETS["basin"] = dungeon(auto(a2(RU_A2, 0, 0, LILAC)), a4(RU_A4, 0, 0, LILAC), water_rule=water(RU_A1, 1),
                                extra={"salt": auto(a2(W_A2, 0, 1, LILAC)), "pool": water(RU_A1, 1, g="pool")})
LIB_TILESETS["town_r05"] = {"path": auto(a2(RU_A2, 0, 0, LILAC)), "salt": auto(a2(W_A2, 0, 1, LILAC)), "pool": water(RU_A1, 1, g="pool"),
                            "garden": auto(a2(FF_A2, 0, 1)), **roofs(SP_C2, tint("1a1428", "4a3a6a", "8a78b0", "e0d8f0", keep=0.3)), **room_kit()}
LIB_TILESETS["whitebone"] = dungeon(auto(a2(RU_A2, 0, 0)), a4(RU_A4, 0, 0), floor2=auto(a2(RU_A2, 1, 0)),
                                    extra={"snow": auto(a2(W_A2, 2, 2)), "tree": PINE_SNOW})
LIB_TILESETS["vault"] = dungeon(auto(a2(RU_A2, 0, 0, LILAC)), a4(RU_A4, 1, 0), floor2=auto(a2(RU_A2, 1, 0, LILAC)),
                                extra={"pool": water(RU_A1, 1, g="pool")})
DARK_VOID = tile(t16(SW_A5, 0, 0, tint("020206", "0a0a14", keep=0.0)), g="void")
LIB_TILESETS["conduit"] = dungeon(auto(a2(FU_A2, 2, 2)), a4(FU_A4, 0, 2), floor2=auto(a2(FU_A2, 1, 2)),
                                  water_rule=water(FU_A1, 0, (4, 5, 6)), extra={"bridge": auto(a2(FU_A2, 5, 1)), "lift": auto(a2(FU_A2, 4, 1)), "void": DARK_VOID})
CROWN = tint("120c18", "3a2238", "6a3a50", "b0707a")
LIB_TILESETS["crown"] = dungeon(auto(a2(SW_A2, 0, 0, CROWN)), a4(FU_A4, 5, 1), floor2=auto(a2(FU_A2, 7, 2, CROWN)),
                                water_rule=water(RU_A1, 3), extra={"dock": auto(a2(SP_A2, 5, 1, tint("140c14", "4a2a34", "8a5048", "d8a070", keep=0.3))),
                                       "bridge": auto(a2(SP_A2, 5, 1, tint("140c14", "4a2a34", "8a5048", "d8a070", keep=0.3))), "void": DARK_VOID})
LIB_TILESETS["winter"] = dungeon(auto(a2(W_A2, 0, 1)), a4(RU_A4, 0, 0), water_rule=W_SNOW(),
                                 extra={"snow": auto(a2(W_A2, 2, 2)), "ice": auto(a2(W_A2, 2, 3)), "rock": stamp(Src(W_B, 65, 48, 14, 15), under="snow")})
LIB_TILESETS["reef"] = dungeon(auto(a2(AT_A2, 5, 1)), a4(SW_A4, 0, 0), floor2=auto(a2(AT_A2, 1, 1)), water_rule=W_OPEN(),
                               extra={"reef": stamp(Src(AS_B, 100, 34, 23, 12, tint("2a0c1a", "8a2a4a", "e07a7a", "ffd0c0", keep=0.2)), under="@"),
                                      "rock": stamp(Src(AS_B, 100, 34, 23, 12), under="@"),"deep": water(W_A1, 0, fn=tint("050a20", "10245a", "2a5aa0", "8ac0f0", keep=0.3), g="deep"), "dock": WOOD_DECK})
LIB_TILESETS["interior"] = dungeon(auto(a2(SP_A2, 6, 0)), a4(SP_A4, 4, 0), extra={"counter": hrow(t16(SP_I1, 0, 8), t16(SP_I1, 1, 8), t16(SP_I1, 2, 8), under="floor")})
LIB_TILESETS["interior_stone"] = dungeon(auto(a2(SP_A2, 1, 0)), a4(SP_A4, 1, 0), floor2=auto(a2(SP_A2, 0, 2)),
                                         extra={"stairs": tile(t16(FF_A5, 6, 10)), "garden": auto(a2(FF_A2, 0, 1))})
LIB_TILESETS["ship"] = dungeon(auto(a2(FU_A2, 0, 3)), a4(SP_A4, 0, 1))
_world = lambda post: {
    "plains": auto(a2(FF_A2, 0, 1 if not post else 3)), "water": W_GRASS(), "deep": water(W_A1, 0, g="deep"),
    "path": auto(a2(FF_A2, 2, 1)), "sand": auto(a2(FF_A2, 5, 1)), "snow": auto(a2(W_A2, 2, 2)), "salt": auto(a2(W_A2, 0, 1, LILAC)),
    "ash": auto(a2(AS_A2, 1, 0)),
    "hills": auto(a2(FF_A2, 0, 0 if not post else 2)),
    "mountain": stamp(Src(AS_B, 53, 68, 24, 25), tall=True, under="plains", inner=Src(AS_B, 84, 64, 40, 31), g="mountain"),
    "forest": stamp(Src(W_B, 227, 55, 26, 23), tall=True, under="plains", inner=Src(W_B, 4, 104, 40, 52), g="forest"),
}
LIB_TILESETS["harbor"] = {"dock": WOOD_DECK, "water": W_OPEN(), "floor2": auto(a2(SP_A2, 1, 0)), "floor": auto(a2(SP_A2, 1, 0)),
                          **room_kit()}
LIB_TILESETS["world"] = _world(False)
LIB_TILESETS["world_post"] = _world(True)


# ---- props pass 2 (2026-09-29): remaining generated props -> library pieces ------------------------------------
# Sources are whole library objects (Time Fantasy winter tent, ruins statues/pillars, cloud-city angel and bells,
# Future Fantasy awnings, ashlands signposts). Rails, laundry lines and world-map mountains have no ready-made
# piece in the library, so they are composed in code from library pixels (steampunk fence posts/beams, awning
# fabric, fairy-forest cliff rock) — see _rail_img / _laundry_img / _mountain_img.
M2 = FU + "modern_tileB_outside2.png"
ST_B = FF + "B_stone.png"
RU_B1 = RU + "B_ruins1.png"
TENT = Src(W_B, 128, 120, 46, 56)
TENT_SNOW = Src(W_B, 175, 120, 46, 56)
AWN = {c: Src(M2, x, y, 34, 17) for c, (x, y) in
       {"green": (7, 102), "red": (55, 102), "blue": (7, 134), "yellow": (55, 134)}.items()}
ANGEL = Src(CL_B, 66, 134, 28, 38)
PILLAR = Src(RU_B1, 98, 1, 12, 46)
OBELISK = Src(ST_B, 168, 64, 16, 44)
SIGN = Src(AS_B, 16, 0, 16, 16)
SIGN_SNOW = Src(W_B, 0, 16, 16, 16)
BELL = Src(CL_B, 96, 224, 14, 15)
COUNTER = hrow(t16(SP_I1, 0, 8), t16(SP_I1, 1, 8), t16(SP_I1, 2, 8), under="@")


def _crop(sheet, x, y, w, h):
    return Src(sheet, x, y, w, h).image()


def _rail_img():
    """Track cell (one rail pair per row, sleepers across): steampunk fence posts as sleepers, its beam
    re-tinted to steel for the rails."""
    out = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    post = _crop(SP_C1, 138, 164, 5, 12)
    for x in (1, 9):
        out.alpha_composite(post, (x, 2))
    beam = tint("1a1c24", "4a5060", "8a94a4", "d0d8e0", keep=0.1)(_crop(SP_C1, 132, 155, 16, 5))
    for y in (3, 9):
        out.alpha_composite(beam.crop((0, 0, 16, 4)), (0, y))
    return out


def _laundry_img(left=False, right=False):
    """Clothes line: a sagging cord with cloth cut from the awning fabrics; run ends get a steampunk fence post."""
    out = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    cord = _crop(SP_C1, 138, 170, 1, 1).getpixel((0, 0))
    for x in range(16):
        out.putpixel((x, 3 + (1 if 4 <= x <= 11 else 0)), cord)
    cloths = [(M2, 9, 104), (M2, 58, 104), (M2, 11, 136)]
    xs = [x for x in (1, 6, 11) if not (left and x == 1) and not (right and x == 11)]
    for i, x in enumerate(xs):
        sh, sx, sy = cloths[(x // 5) % 3]
        pc = _crop(sh, sx + i * 4, sy + 1, 5, 8 + (x // 5 % 2) * 2)
        out.alpha_composite(pc, (x, 4 + (1 if 4 <= x <= 11 else 0)))
    post = _crop(SP_C1, 138, 164, 5, 13)
    if left:
        out.alpha_composite(post, (0, 2))
    if right:
        out.alpha_composite(post, (11, 2))
    return out


def _mountain_img(w, h, seed, ramp_stops, snow=False):
    """World-map peak (FF6-style): fairy-forest cliff rock gradient-mapped to an earth ramp, cut to a jagged
    peak, lit from the left with a shaded right flank and a dark outline."""
    import random
    rnd_ = random.Random(seed)
    tex = tint(*ramp_stops, keep=0.15)(_crop(FF_A5, 16, 176, 48, 32))
    big = Image.new("RGBA", (w, h))
    for oy in range(0, h, 32):
        for ox in range(0, w, 48):
            big.paste(tex, (ox, oy))
    cx = w / 2 + rnd_.uniform(-2, 2)
    mask = [[False] * w for _ in range(h)]
    ridge = []
    lj = rj = 0.0
    for y in range(h):
        t = (y + 1) / h
        half = max(1.0, t * (w / 2 - 1))
        lj = max(-1.5, min(1.5, lj + rnd_.uniform(-0.8, 0.8)))
        rj = max(-1.5, min(1.5, rj + rnd_.uniform(-0.8, 0.8)))
        x0, x1 = int(round(cx - half + lj)), int(round(cx + half + rj))
        rx = int(round(cx + (0.5 - t) * 3 + rnd_.uniform(-0.6, 0.6)))
        ridge.append(rx)
        for x in range(max(0, x0), min(w, x1 + 1)):
            mask[y][x] = True
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px, bp = out.load(), big.load()
    for y in range(h):
        for x in range(w):
            if not mask[y][x]:
                continue
            r, g, b, _ = bp[x, y]
            f = 1.18 if x < ridge[y] else 0.68
            if x == ridge[y]:
                f = 1.35
            if snow and y < h * 0.28 + rnd_.uniform(-1, 1):
                r, g, b = (236, 240, 248) if x < ridge[y] else (168, 180, 206)
                f = 1.0
            px[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), 255)
    edge = (28, 18, 16, 255)
    for y in range(h):
        for x in range(w):
            if mask[y][x] and (y == 0 or x == 0 or x == w - 1 or not mask[y - 1][x] or not mask[y][x - 1]
                               or not mask[y][x + 1]):
                px[x, y] = edge
    return out


def _statue_img():
    """Ruins statue: its head sits on the sheet between other loose heads, so clear the neighbours' pixels."""
    im = _crop(RU_B1, 12, 100, 24, 41)
    px = im.load()
    for y in range(12):
        for x in range(24):
            if x < 5 or x > 16:
                px[x, y] = (0, 0, 0, 0)
    return im


STATUE_R = Fn("ruins_statue", _statue_img, [RU_B1])
RAIL = Fn("rail_track", _rail_img, [SP_C1])
LAUNDRY = [Fn(f"laundry_{n}", (lambda l=l, r=r: _laundry_img(l, r)), [SP_C1, M2])
           for n, l, r in (("l", True, False), ("m", False, False), ("r", False, True), ("1", True, True))]
EARTH = ("20140e", "5a3c24", "9a7446", "dcc08a")
ASHEN = ("1a1014", "4a2c2a", "84564a", "c8a088")


def _mountains(post):
    st = ASHEN if post else EARTH
    mk = lambda n, w, h, sd, sn=False: Fn(f"mtn_{'p' if post else 'a'}_{n}", lambda: _mountain_img(w, h, sd, st, sn), [FF_A5])
    return stamp(mk("a", 28, 24, 11), tall=True, under="@", alts=[mk("b", 24, 22, 12), mk("c", 30, 26, 13)],
                 inner=mk("big", 34, 32, 14, not post), g="mountain")


PROPS2 = {
    "tent": pair(TENT), "rail": tile(RAIL, under="path"), "laundry": hrow(*LAUNDRY, under="@"),
    "statue": stamp(ANGEL, tall=True, under="@"), "sign": stamp(SIGN, under="@"), "pillar": stamp(PILLAR, tall=True, under="@"),
    "counter": COUNTER, "bell": stamp(BELL, under="@"), "grate": tile(t16(SP_A5D, 6, 1)),
    "awning": pair(AWN["red"], under="@"),
}
FAMILY_PROPS = {
    "town_r01": {"awning": pair(AWN["green"], under="@")},
    "town_r03": {"awning": pair(AWN["blue"], under="@")},
    "town_r04": {"awning": pair(AWN["yellow"], under="@")},
    "town_r05": {"awning": pair(AWN["blue"], under="@")},
    "quarry": {"statue": stamp(STATUE_R, tall=True, under="@")},
    "winter": {"statue": stamp(STATUE_R, tall=True, under="@")},
    "whitebone": {"tent": pair(TENT_SNOW), "sign": stamp(SIGN_SNOW, under="@")},
    "crown": {"pillar": stamp(OBELISK, tall=True, under="@", g="pillar")},
    "conduit": {"pillar": stamp(OBELISK, tall=True, under="@", g="pillar")},
}
for _fam, _spec in LIB_TILESETS.items():
    if _fam.startswith("world"):
        continue
    for _k, _r in list(PROPS2.items()) + list(FAMILY_PROPS.get(_fam, {}).items()):
        if _k not in _spec or _fam in FAMILY_PROPS and _k in FAMILY_PROPS[_fam]:
            _spec[_k] = _r
LIB_TILESETS["world"]["mountain"] = _mountains(False)
LIB_TILESETS["world_post"]["mountain"] = _mountains(True)
