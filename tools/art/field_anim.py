"""Animated field scenery for The Ashen Crown, drawn frame by frame at 1px on the 48px grid.
Hard pixels, fixed palettes, no anti-aliasing. Every animation loops seamlessly.
"""
import math, os, json
import numpy as np
from PIL import Image

OUT = '/home/claude/scn/out'
T = 48

def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)

# ---------- palettes ----------
FIRE = [hexc(c) for c in ('#5a1414', '#a42a14', '#e0561c', '#f7922a', '#ffd04a', '#fff5c0')]
WOOD = [hexc(c) for c in ('#2a1a14', '#4a2e1e', '#6e4628', '#94643a')]
IRON = [hexc(c) for c in ('#16141c', '#2c2a36', '#4a4858', '#7a7890', '#b4b2c4')]
STONE = [hexc(c) for c in ('#26222a', '#403a44', '#5e5662', '#847a86')]
SMOKE = [hexc(c) for c in ('#3c3a44', '#5c5a66', '#8a8894', '#b8b6c0')]
WATER = [hexc(c) for c in ('#10244a', '#183a72', '#22559a', '#3478c0', '#5aa2dc', '#9ad2f0', '#e8f8ff')]
CLOTH_RED = [hexc(c) for c in ('#3a0e12', '#6e1a1e', '#a02a26', '#cc4a34')]
CLOTH_BLUE = [hexc(c) for c in ('#101838', '#1c2e66', '#2c4a98', '#4a70c4')]
GOLD = [hexc(c) for c in ('#5c3c10', '#a0701c', '#e0b030', '#fff08a')]
OUTLINE = hexc('#120e14')
CLEAR = (0, 0, 0, 0)

def canvas(w, h): return np.zeros((h, w, 4), np.uint8)
def put(a, x, y, c):
    if 0 <= x < a.shape[1] and 0 <= y < a.shape[0]: a[y, x] = c
def rect(a, x0, y0, x1, y1, c):
    a[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = c
def img(a): return Image.fromarray(a)

def outline(a, col=OUTLINE):
    m = a[..., 3] > 0
    p = np.pad(m, 1)
    edge = (~m) & (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
    b = a.copy(); b[edge] = col; return b

def bayer(x, y):
    M = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    return (M[y % 4][x % 4] + 0.5) / 16

# ---------- flame ----------
def flame(a, cx, base_y, w, h, t, n, seed=0, colors=FIRE):
    """teardrop flame; t/n phase; coloured in bands from the core outwards."""
    ph = 2 * math.pi * t / n
    for y in range(base_y - h - 3, base_y + 1):
        v = (base_y - y) / h               # 0 at base .. 1 at tip
        if v < 0: continue
        # half width: round base, tapering tip, with flicker
        hw = w / 2 * (math.sqrt(max(0, 1 - v)) * (1.0 if v > 0.25 else 0.75 + v))
        sway = (math.sin(ph + v * 3.2 + seed) * 1.6 * v + math.sin(2 * ph + v * 6 + seed * 2) * 0.6 * v)
        tipcut = 1 + 0.18 * math.sin(ph * 2 + seed) + 0.1 * math.sin(ph * 3 + 1 + seed)
        if v > tipcut: continue
        for x in range(int(cx - hw - 3), int(cx + hw + 4)):
            d = abs(x + 0.5 - (cx + sway)) / max(hw, 0.5)
            if d > 1: continue
            heat = (1 - d) * 0.7 + (1 - v) * 0.6 + 0.08 * math.sin(ph * 3 + x * 1.7 + y * 0.9 + seed)
            k = 0 if heat < 0.28 else 1 if heat < 0.45 else 2 if heat < 0.62 else 3 if heat < 0.8 else 4 if heat < 1.0 else 5
            put(a, x, y, colors[k])
    # sparks
    for s in range(2):
        sp = (t / n + s * 0.5 + seed * 0.13) % 1
        sx = int(round(cx + math.sin(sp * 6.28 * 2 + seed + s) * (w / 2)))
        sy = int(round(base_y - h * 0.8 - sp * h * 0.9))
        if sp < 0.85: put(a, sx, sy, colors[4] if sp < 0.5 else colors[2])

def glow(a, cx, cy, r, col, strength=0.35):
    """dithered warm light halo drawn only on transparent pixels"""
    H, W = a.shape[:2]
    for y in range(max(0, int(cy - r)), min(H, int(cy + r + 1))):
        for x in range(max(0, int(cx - r)), min(W, int(cx + r + 1))):
            if a[y, x, 3]: continue
            d = math.hypot(x - cx, (y - cy) * 1.1) / r
            if d < 1 and bayer(x, y) < (1 - d) * strength:
                a[y, x] = col[:3] + (110,)

# ---------- objects ----------
def wall_torch(t, n=6):
    a = canvas(T, T * 2)
    # iron sconce plate + cup, handle of wood
    rect(a, 21, 60, 26, 78, IRON[1]); rect(a, 22, 61, 25, 77, IRON[2]); put(a, 23, 62, IRON[3]); put(a, 23, 69, IRON[3])
    for i, y in enumerate(range(52, 64)):
        rect(a, 22, y, 25, y, WOOD[1 if i % 3 else 2]); put(a, 22, y, WOOD[0])
    rect(a, 19, 50, 28, 53, IRON[2]); rect(a, 20, 53, 27, 54, IRON[1]); rect(a, 19, 50, 28, 50, IRON[3])
    fl = canvas(T, T * 2)
    flame(fl, 23.5, 50, 9, 20, t, n, seed=0.4)
    m = fl[..., 3] > 0; a[m & (a[..., 3] == 0)] = fl[m & (a[..., 3] == 0)]
    return outline_keep_glow(a)

def outline_keep_glow(a):
    solid = a.copy(); solid[solid[..., 3] < 255] = 0
    o = outline(solid)
    m = (a[..., 3] > 0) & (a[..., 3] < 255) & (o[..., 3] == 0)
    o[m] = a[m]
    return o

def brazier(t, n=6):
    a = canvas(T, T * 2)
    # tripod legs
    for i in range(22):
        y = 95 - i
        put(a, 14 + i // 4, y, IRON[1]); put(a, 33 - i // 4, y, IRON[1]); put(a, 23, y, IRON[2]); put(a, 24, y, IRON[1])
    rect(a, 18, 72, 29, 73, IRON[2])
    # bowl
    for y in range(58, 72):
        v = (y - 58) / 13
        hw = int(13 - v * v * 7)
        for x in range(24 - hw, 24 + hw):
            c = IRON[3] if y < 60 else IRON[2] if x < 24 + hw * 0.2 else IRON[1]
            put(a, x, y, c)
    rect(a, 10, 57, 37, 58, IRON[4]); rect(a, 11, 59, 36, 59, IRON[2])
    for x in range(12, 37, 5): put(a, x, 64, GOLD[1]); put(a, x, 65, GOLD[1])
    fl = canvas(T, T * 2)
    flame(fl, 19, 57, 9, 16, t, n, seed=1.1); flame(fl, 29, 57, 9, 17, (t + 2) % n, n, seed=2.3); flame(fl, 24, 57, 13, 27, t, n, seed=0.2)
    for x in range(12, 37):
        if (x + t) % 3 == 0: put(fl, x, 56, FIRE[2])
    m = (fl[..., 3] > 0) & (a[..., 3] == 0); a[m] = fl[m]
    return outline_keep_glow(a)

def campfire(t, n=6):
    a = canvas(T, T)
    # stones ring
    for i in range(10):
        ang = math.pi * (0.05 + 0.9 * i / 9)
        sx = int(24 + math.cos(ang) * 16); sy = int(40 + math.sin(ang) * 5)
        rect(a, sx - 2, sy - 1, sx + 2, sy + 1, STONE[2]); rect(a, sx - 1, sy - 1, sx + 1, sy - 1, STONE[3]); rect(a, sx - 2, sy + 1, sx + 2, sy + 1, STONE[1])
    # logs crossed
    for i in range(18):
        put(a, 15 + i, 38 - i // 5, WOOD[2]); put(a, 15 + i, 39 - i // 5, WOOD[1])
        put(a, 33 - i, 38 - i // 5, WOOD[3] if i % 4 == 0 else WOOD[2]); put(a, 33 - i, 39 - i // 5, WOOD[1])
    rect(a, 14, 37, 15, 39, WOOD[3]); rect(a, 33, 37, 34, 39, WOOD[3])
    for x in range(19, 30):
        if (x * 7 + t) % 4 == 0: put(a, x, 36, FIRE[3])
    fl = canvas(T, T)
    flame(fl, 21, 36, 8, 13, (t + 1) % n, n, seed=3.0); flame(fl, 28, 36, 8, 12, (t + 3) % n, n, seed=4.1); flame(fl, 24.5, 37, 12, 22, t, n, seed=0.7)
    m = (fl[..., 3] > 0) & (a[..., 3] == 0); a[m] = fl[m]
    return outline_keep_glow(a)

def candles(t, n=4):
    a = canvas(T, T)
    # candelabra: base, stem, three arms
    rect(a, 17, 44, 30, 46, GOLD[1]); rect(a, 18, 43, 29, 43, GOLD[2]); rect(a, 22, 26, 25, 42, GOLD[1]); rect(a, 23, 26, 23, 42, GOLD[3])
    for dx in (-10, 0, 10):
        x = 24 + dx
        if dx: rect(a, min(x, 24), 30, max(x, 24), 31, GOLD[1]); rect(a, x - 1, 26, x + 1, 30, GOLD[1])
        rect(a, x - 3, 25, x + 3, 26, GOLD[2]); rect(a, x - 2, 15, x + 1, 24, hexc('#e8e0cc')); rect(a, x - 2, 15, x - 2, 24, hexc('#fffaf0')); rect(a, x + 1, 17, x + 1, 24, hexc('#b8ae98'))
        put(a, x, 14, hexc('#2a2020'))
    fl = canvas(T, T)
    for i, dx in enumerate((-10, 0, 10)):
        flame(fl, 24 + dx - 0.5, 13, 4, 7, (t + i) % n, n, seed=i * 1.7, colors=FIRE[1:] + [FIRE[5]])
    m = (fl[..., 3] > 0) & (a[..., 3] == 0); a[m] = fl[m]
    return outline_keep_glow(a)

def chimney_smoke(t, n=8):
    a = canvas(T, T * 2)
    puffs = 9
    for p in range(puffs):
        s = ((t / n) + p / puffs) % 1.0          # life 0..1
        y = 92 - s * 86
        x = 24 + math.sin(s * 5 + p) * 3 + s * 9
        r = 4.5 + s * 9
        dens = 1 - s ** 1.4
        for yy in range(int(y - r - 1), int(y + r + 2)):
            for xx in range(int(x - r - 1), int(x + r + 2)):
                d = math.hypot(xx - x, (yy - y) * 1.15) / r
                if d > 1: continue
                if bayer(xx, yy) > dens * (2.2 - d * 1.6): continue
                light = (1 - d) * 0.6 + (y - yy) / (2 * r) * 0.5 + 0.35 - s * 0.35
                k = 0 if light < 0.2 else 1 if light < 0.45 else 2 if light < 0.7 else 3
                if a[yy % a.shape[0], xx % T, 3] == 0 or k > 1:
                    put(a, xx, yy, SMOKE[k])
    return a

def flag_pole(t, n=6, cloth=CLOTH_RED, emblem=GOLD):
    a = canvas(T, T * 2)
    # pole
    rect(a, 8, 12, 9, 95, WOOD[2]); rect(a, 8, 12, 8, 95, WOOD[3]); rect(a, 6, 93, 11, 95, STONE[2])
    rect(a, 7, 8, 10, 11, GOLD[2]); put(a, 8, 7, GOLD[3]); put(a, 9, 7, GOLD[2]); put(a, 8, 6, GOLD[3])
    ph = 2 * math.pi * t / n
    W, Hh = 32, 20
    cloth_img = canvas(T, T * 2)
    for x in range(W):
        u = x / (W - 1)
        amp = 1 + u * 3.2
        off = amp * math.sin(ph - u * 5.0)
        slope = math.cos(ph - u * 5.0)
        top = 13 + off
        hh = Hh - u * 5  # swallow-ish taper
        for y in range(int(round(top)), int(round(top + hh))):
            yy = y - top
            if u > 0.82 and abs(yy - hh / 2) < (u - 0.82) * 22: continue   # swallowtail notch
            k = 2 + (1 if slope > 0.35 else 0) - (1 if slope < -0.35 else 0)
            if yy < 1: k = min(3, k + 1)
            put(cloth_img, 10 + x, y, cloth[k])
        # emblem: a small crown around u=0.35..0.55
    for (ex, ey) in [(0, 4), (4, 1), (8, 4), (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (0, 6), (8, 6), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (0, 3), (8, 3), (4, 0), (4, 2), (1, 6), (3, 6), (5, 6), (7, 6)]:
        x = 10 + 9 + ex
        u = (x - 10) / (W - 1)
        off = (1 + u * 3.2) * math.sin(ph - u * 5.0)
        y = int(round(13 + off + 4 + ey))
        if cloth_img[y, x, 3]: put(cloth_img, x, y, emblem[2] if ey < 5 else emblem[1])
    m = cloth_img[..., 3] > 0; a[m] = cloth_img[m]
    return outline(a)

def wall_banner(t, n=4, cloth=CLOTH_RED, emblem=GOLD):
    a = canvas(T, T * 2)
    rect(a, 8, 4, 39, 5, WOOD[2]); rect(a, 8, 4, 39, 4, WOOD[3]); rect(a, 6, 3, 8, 6, GOLD[2]); rect(a, 39, 3, 41, 6, GOLD[2])
    ph = 2 * math.pi * t / n
    for y in range(6, 84):
        v = (y - 6) / 78
        sway = math.sin(ph + v * 2.2) * v * 1.6
        for x in range(10, 38):
            if y > 74 and abs(x - 23.5) < (y - 74) * 1.5: continue   # pointed hem cut
            xx = int(round(x + sway))
            k = 2
            if x < 12: k = 3
            if x > 35: k = 1
            fold = math.sin((x - 10) / 27 * math.pi * 2 + ph * 0.5 + v)
            if fold > 0.75: k = min(3, k + 1)
            elif fold < -0.8: k = max(0, k - 1)
            put(a, xx, y, cloth[k])
        # gold trim
        if y in (8, 9):
            for x in range(10, 38): put(a, int(round(x + sway)), y, emblem[2 if y == 8 else 1])
    # emblem: crown + ember
    E = ["....#....", ".#..#..#.", ".#.###.#.", "#########", "#.#.#.#.#", "#########", ".........", "....#....", "...###...", "..#####..", "...###...", "....#...."]
    for j, row in enumerate(E):
        for i, ch in enumerate(row):
            if ch == '#':
                y = 26 + j; v = (y - 6) / 78; sway = math.sin(ph + v * 2.2) * v * 1.6
                put(a, int(round(19 + i + sway)), y, emblem[2] if j < 6 else FIRE[3])
    return outline(a)

# ---------- water ----------
def water_tile(t, n=4, shallow=False):
    """FF6-style: flat base, soft darker swells, short horizontal highlight dashes that shimmer."""
    a = canvas(T, T)
    base = WATER[3] if shallow else WATER[2]
    dark = WATER[2] if shallow else WATER[1]
    hi = WATER[4] if not shallow else WATER[5]
    top = WATER[5] if not shallow else WATER[6]
    ph = t / n
    for y in range(T):
        for x in range(T):
            v = math.sin(2 * math.pi * (y / 16) + 1.3 * math.sin(2 * math.pi * (x / 24 + ph)))
            seg = math.sin(2 * math.pi * (x / 16 + (y // 16) * 0.37 + ph * 0)) + math.sin(2 * math.pi * (x / 48 * 2 + (y // 16) * 0.61))
            a[y, x] = dark if (v > 0.88 and seg > 0.2) else base
    rng = np.random.RandomState(11 if shallow else 5)
    dashes = [(rng.randint(0, 48), rng.randint(0, 48), rng.randint(3, 7), rng.randint(0, n)) for _ in range(14)]
    for (x0, y0, L, p) in dashes:
        k = (t - p) % n
        if k == 3: continue                      # off
        LL = L if k == 1 else max(2, L - 2)       # grow then shrink
        xs = x0 + (k if k < 3 else 0)
        for i in range(LL):
            a[y0 % T, (xs + i) % T] = top if (k == 1 and 0 < i < LL - 1) else hi
    return a

def shore_foam(t, n=4):
    """foam overlay for the top edge of a water tile (rotate/flip for other edges)"""
    a = canvas(T, T)
    ph = 2 * math.pi * t / n
    for x in range(T):
        d = 3 + 2 * math.sin(2 * math.pi * x / 24 + ph) + math.sin(2 * math.pi * x / 16 - ph * 2) * 0.8
        for y in range(int(d) + 1):
            a[y, x] = WATER[6] if y < d - 1.5 else WATER[5]
        y2 = int(d + 3 + math.sin(ph + x * 0.4) * 1.2)
        if (x + t * 3) % 7 < 3: put(a, x, y2, WATER[5])
    return a

def waterfall_body(t, n=6):
    """vertical streak lanes (2-3px wide) falling at slightly different speeds; tiles both ways."""
    a = canvas(T, T)
    rng = np.random.RandomState(3)
    lanes = []
    x = 0
    while x < T:
        w = rng.choice([2, 3, 3, 4])
        w = min(w, T - x)
        lanes.append((x, w, rng.choice([1, 2]), rng.rand(), rng.choice([1, 2, 3])))
        x += w
    step = T / n
    for (x0, w, spd, off, f) in lanes:
        for y in range(T):
            yy = (y - t * step * spd) % T
            v = math.sin(2 * math.pi * (yy / T * f + off))
            v2 = math.sin(2 * math.pi * (yy / T * (f + 2) + off * 3))
            for x in range(x0, x0 + w):
                edge = (x == x0)
                c = WATER[3]
                if v > 0.55: c = WATER[4]
                if v > 0.85 and v2 > 0.3: c = WATER[5]
                if v < -0.6 and edge: c = WATER[2]
                if v > 0.97 and v2 > 0.8 and not edge: c = WATER[6]
                a[y, x] = c
    return a

def waterfall_top(t, n=6):
    a = canvas(T, T)
    body = waterfall_body(t, n)
    for y in range(T):
        for x in range(T):
            if y < 20:
                a[y, x] = WATER[2]
                if (y + (x // 8 + t) % 3) % 6 == 0 and (x + t * 3) % 12 < 5: a[y, x] = WATER[3]
                if y > 15: a[y, x] = WATER[4]
                if y in (18, 19): a[y, x] = WATER[5] if (x + t * 4) % 9 < 5 else WATER[4]
            else:
                a[y, x] = body[y, x]
    # lip highlight curls
    for x in range(T):
        if (x * 3 + t * 5) % 11 < 3: put(a, x, 20, WATER[6])
    return a

def waterfall_base(t, n=6):
    """falling water meets the pool: churning foam band with a jagged crest, spray flecks, rippling pool."""
    a = canvas(T, T)
    body = waterfall_body(t, n)
    ph = 2 * math.pi * t / n
    for y in range(T):
        for x in range(T):
            if y < 20:
                a[y, x] = body[y, x]
            else:
                w = math.sin(2 * math.pi * (x / 24) + y * 0.7 - ph)
                a[y, x] = WATER[3] if w > 0.6 else WATER[2]
    for x in range(T):
        crest = 14 + 3 * math.sin(2 * math.pi * x / 16 + ph) + 2 * math.sin(2 * math.pi * x / 12 - 2 * ph)
        bottom = 29 + 2 * math.sin(2 * math.pi * x / 24 - ph)
        for y in range(int(crest), int(bottom)):
            d = (y - crest) / max(1, bottom - crest)
            c = WATER[6] if d < 0.45 else WATER[5]
            if (x * 5 + y * 3 + t * 7) % 13 == 0: c = WATER[4]
            a[y, x] = c
        # spray flecks above the crest, rising and looping
        for k in range(2):
            s_ = ((t / n) + (x * 0.37 + k * 0.5)) % 1
            if (x + k * 5) % 6 == 0:
                yy = int(crest - 2 - s_ * 8)
                if 0 <= yy < T: a[yy, x] = WATER[6] if s_ < 0.6 else WATER[5]
        # trailing foam streaks in the pool
        if (x + t * 2) % 9 < 4: a[int(bottom) + 2, x] = WATER[5]
        if (x * 3 + t * 5) % 17 < 3: a[min(T - 1, int(bottom) + 7), x] = WATER[4]
    return a

# ---------- export ----------
def export(name, frames, dur_ms, note):
    d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
    for i, f in enumerate(frames):
        img(f).save(os.path.join(d, f'{name}_{i}.png'))
    w, h = frames[0].shape[1], frames[0].shape[0]
    sheet = np.concatenate(frames, axis=1)
    img(sheet).save(os.path.join(OUT, name + '_strip.png'))
    return dict(name=name, frames=len(frames), w=w, h=h, duration_ms=dur_ms, note=note)

if __name__ == '__main__':
    import shutil; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    man = []
    man.append(export('torch_wall', [wall_torch(t) for t in range(6)], 100, 'Wall sconce torch, 48x96, anchor bottom of sconce plate at y=78.'))
    man.append(export('brazier', [brazier(t) for t in range(6)], 100, 'Standing iron brazier, 48x96, feet on the bottom row.'))
    man.append(export('campfire', [campfire(t) for t in range(6)], 100, 'Campfire with stone ring, one 48x48 tile.'))
    man.append(export('candelabra', [candles(t) for t in range(4)], 140, 'Three-candle candelabra for tables/altars, 48x48.'))
    man.append(export('chimney_smoke', [chimney_smoke(t) for t in range(8)], 130, 'Smoke column, 48x96; place bottom at the chimney top. Dithered, drifts right.'))
    man.append(export('flag_crown_red', [flag_pole(t) for t in range(6)], 110, 'Pole pennant with the Crown emblem, 48x96.'))
    man.append(export('flag_blue', [flag_pole(t, cloth=CLOTH_BLUE) for t in range(6)], 110, 'Pole pennant, blue, 48x96.'))
    man.append(export('banner_wall_red', [wall_banner(t) for t in range(4)], 180, 'Hanging wall banner, crown and ember, 48x96.'))
    man.append(export('banner_wall_blue', [wall_banner(t, cloth=CLOTH_BLUE) for t in range(4)], 180, 'Hanging wall banner, blue, 48x96.'))
    man.append(export('water_deep', [water_tile(t) for t in range(4)], 220, 'Deep water, 48x48, tiles seamlessly both ways.'))
    man.append(export('water_shallow', [water_tile(t, shallow=True) for t in range(4)], 220, 'Shallow water, 48x48, tiles seamlessly.'))
    man.append(export('shore_foam_top', [shore_foam(t) for t in range(4)], 220, 'Foam overlay for a water tile edge (top); rotate for other sides.'))
    man.append(export('waterfall_top', [waterfall_top(t) for t in range(6)], 90, 'Waterfall lip, 48x48, tiles horizontally.'))
    man.append(export('waterfall_body', [waterfall_body(t) for t in range(6)], 90, 'Waterfall body, 48x48, tiles both ways.'))
    man.append(export('waterfall_base', [waterfall_base(t) for t in range(6)], 90, 'Waterfall splash pool, 48x48, tiles horizontally.'))
    json.dump(man, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
    print(len(man))
