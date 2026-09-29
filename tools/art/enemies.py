"""Enemy and boss battle sprites (facing right toward the party). 4 frames: idle A, idle B, tell/charge, hurt.
Families (quadruped, bug, floater, blob, construct, winged, humanoid, serpent, plant) with per-identity
silhouette parameters, so identities differ in shape, not only colour."""
import json, math, os, random
from PIL import Image
from art.pix import Canvas, shade, hexc, mix

OUT = (20, 14, 24, 255)


def pal(*hexes):
    return [hexc(h) for h in hexes]


def finish(c, glow=None):
    return paint(c)


# ---------------------------------------------------------------- FF6-style painterly shading
# Every material region (Canvas tag) is treated as a rounded volume: a height field from the distance transform
# (own region blended with the whole silhouette) gives a surface normal, lit from the upper left. The light value
# is quantised into a 5-step ramp per base colour (cool shadows, warm highlights) with 2x2 cluster dithering only
# at ramp borders. The hard black outline is replaced by a selective dark edge (lower/right) and a rim light
# (upper/left). Tag 8 = effects (left flat), tag 9 = emissive eyes/cores (lit softly, never darkened much).
RAMP = (-0.62, -0.36, -0.14, 0.0, 0.2, 0.4)
_LIGHT = None


def _ramp_col(c, lv):
    f = RAMP[max(0, min(len(RAMP) - 1, lv))]
    return shade(c, f) if f else tuple(c)


def paint(c, rim=True, texture=0.025, seed=7, contrast=1.15):
    import numpy as np
    from scipy import ndimage
    H, W = c.h, c.w
    sil = np.array([[c.px[y][x] is not None for x in range(W)] for y in range(H)])
    if not sil.any():
        return c
    tag = np.array(c.tag) * sil
    dsil = ndimage.distance_transform_edt(np.pad(sil, 1))[1:-1, 1:-1]
    rs = max(2.0, float(dsil.max()))
    hsil = np.sqrt(np.clip(1 - (1 - np.clip(dsil / rs, 0, 1)) ** 2, 0, 1))
    h = np.zeros((H, W))
    for t in np.unique(tag[sil]):
        m = tag == t
        lab, n = ndimage.label(m)
        d = ndimage.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
        for k in range(1, n + 1):
            mk = lab == k
            r = max(1.5, float(d[mk].max()))
            h[mk] = np.sqrt(np.clip(1 - (1 - np.clip(d[mk] / r, 0, 1)) ** 2, 0, 1))
    h = 0.55 * h + 0.45 * hsil
    h = ndimage.gaussian_filter(h, 0.7) * sil
    gy, gx = np.gradient(h * min(W, H) * 0.09)
    nz = np.ones_like(h)
    n = np.stack([-gx, -gy, nz * 0.9])
    n /= np.linalg.norm(n, axis=0)
    L = np.array([-0.55, -0.7, 0.75])
    L /= np.linalg.norm(L)
    I = (n * L[:, None, None]).sum(0)
    ys = np.nonzero(sil.any(1))[0]
    y0, y1 = ys.min(), ys.max() + 1
    yy = (np.arange(H)[:, None] - y0) / max(1, y1 - y0)
    I = I + 0.18 * (0.5 - yy)                        # ambient: tops catch more light, bellies/feet sink
    I = (I - 0.62) * 2.6 * contrast                   # centre so a flat face lit head-on is the base colour
    lvl_f = 3 + I
    out = [row[:] for row in c.px]
    for y in range(H):
        for x in range(W):
            if not sil[y, x]:
                continue
            base = c.px[y][x]
            t = c.tag[y][x]
            if t == 8:
                continue
            v = lvl_f[y, x]
            lv = int(math.floor(v))
            fr = v - lv
            if fr > 0.6 and ((x >> 1) + (y >> 1)) % 2 == 0 and fr < 0.82:
                lv += 1
            elif fr >= 0.82:
                lv += 1
            if texture and t != 9:
                # 2x2 clusters of texture, never single-pixel noise
                hsh = random.Random(seed * 7919 + (x // 2) * 131 + (y // 2) * 977).random()
                if hsh < texture:
                    lv -= 1
                elif hsh > 1 - texture * 0.6:
                    lv += 1
            if t == 9:
                lv = max(3, min(5, lv + 1))
            lv = max(0, min(5, lv))
            out[y][x] = _ramp_col(base, lv)
    if rim:
        for y in range(H):
            for x in range(W):
                if not sil[y, x] or c.tag[y][x] == 8:
                    continue
                def empty(dx, dy):
                    nx, ny = x + dx, y + dy
                    return not (0 <= nx < W and 0 <= ny < H) or not sil[ny, nx]
                base = c.px[y][x]
                if empty(1, 0) or empty(0, 1) or empty(1, 1):
                    out[y][x] = mix(_ramp_col(base, 0), (26, 20, 44, 255), 0.35)
                elif empty(-1, 0) or empty(0, -1):
                    if c.tag[y][x] != 9:
                        out[y][x] = _ramp_col(base, 5)
                else:
                    # interior material seams get a soft darker line on their lower/right side
                    for dx, dy in ((1, 0), (0, 1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < W and 0 <= ny < H and sil[ny, nx] and c.tag[ny][nx] != c.tag[y][x] \
                                and c.tag[ny][nx] not in (8, 9) and c.tag[y][x] != 9:
                            if h[ny, nx] > h[y, x]:
                                out[y][x] = _ramp_col(base, 1)
                            break
    c.px = out
    return c


def eye(c, x, y, col=(255, 230, 120, 255), r=1.2):
    c.ellipse(x, y, r, r, col, 9)


# ---------------------------------------------------------------- families
def quadruped(sz, p, fr, body=(0.5, 0.28), head=0.22, ears=True, tail=True, mane=False, legs=4, snout=0.12):
    c = Canvas(sz, sz)
    s = sz / 48
    bob = [0, 1, -1, 2][fr]
    lean = 3 * s if fr == 2 else 0
    by = sz * 0.58 + bob
    bx = sz * 0.45 + lean
    bw, bh = sz * body[0] / 2, sz * body[1] / 2
    # legs
    for i in range(legs):
        lx = bx - bw * 0.7 + i * (bw * 1.4 / max(1, legs - 1))
        ph = (i % 2) * (1 if fr == 1 else 0)
        c.line(lx, by, lx + ph, sz - 3 * s, shade(p[1], -0.25) if i % 2 else p[1], max(2, int(3 * s)), 3)
    if tail:
        c.line(bx - bw, by - 2 * s, bx - bw - 8 * s, by - 7 * s + bob, p[1], max(1, int(2 * s)), 4)
    c.ellipse(bx, by, bw, bh, p[0], 1)
    c.ellipse(bx, by + bh * 0.4, bw * 0.8, bh * 0.45, p[2], 2)
    hx, hy = bx + bw * 0.95, by - bh * 0.9
    c.ellipse(hx, hy, sz * head / 2, sz * head / 2.2, p[0], 5)
    c.ellipse(hx + sz * snout * 0.8, hy + 2 * s, sz * snout * 0.7, sz * snout * 0.45, p[2], 5)
    if ears:
        c.poly([(hx - 3 * s, hy - 3 * s), (hx - 1 * s, hy - 9 * s), (hx + 2 * s, hy - 3 * s)], p[1], 6)
    if mane:
        for i in range(5):
            c.ellipse(bx + bw * 0.5 - i * 3 * s, by - bh * 0.8, 3 * s, 3 * s, p[3], 7)
    eye(c, hx + 2 * s, hy - 1 * s, p[4] if len(p) > 4 else (255, 220, 90, 255))
    if fr == 2:
        c.line(hx + sz * snout * 1.3, hy + 3 * s, hx + sz * snout * 1.3 + 3 * s, hy + 5 * s, (250, 250, 240, 255), 1, 8)
    return finish(c)


def bug(sz, p, fr, legs=6, shell=True, pincers=False, round_=0.6, spikes=0):
    c = Canvas(sz, sz)
    s = sz / 48
    bob = [0, 1, 0, 1][fr]
    bx, by = sz * 0.48, sz * 0.62 + bob
    bw, bh = sz * 0.34, sz * 0.22 * round_ / 0.6
    for i in range(legs // 2):
        lx = bx - bw * 0.6 + i * bw * 0.6
        k = 1 if (fr + i) % 2 else -1
        c.line(lx, by, lx - 4 * s + k, sz - 3 * s, p[1], max(1, int(2 * s)), 3)
        c.line(lx + 2 * s, by, lx + 6 * s - k, sz - 3 * s, shade(p[1], -0.3), max(1, int(2 * s)), 3)
    c.ellipse(bx, by, bw, bh, p[0], 1)
    if shell:
        c.ellipse(bx - 2 * s, by - bh * 0.3, bw * 0.9, bh * 0.8, p[2], 2)
        c.line(bx - 2 * s, by - bh, bx - 2 * s, by + bh * 0.5, shade(p[2], -0.35), 1, 2)
    for i in range(spikes):
        x = bx - bw * 0.6 + i * (bw * 1.2 / max(1, spikes - 1))
        c.poly([(x - 2 * s, by - bh * 0.8), (x, by - bh - 5 * s), (x + 2 * s, by - bh * 0.8)], p[3], 6)
    hx, hy = bx + bw * 0.95, by - 1 * s
    c.ellipse(hx, hy, 5 * s, 4.5 * s, p[1], 5)
    if pincers:
        o = 3 * s if fr == 2 else 0
        c.line(hx + 3 * s, hy - 2 * s, hx + 10 * s + o, hy - 7 * s, p[3], max(2, int(3 * s)), 6)
        c.line(hx + 3 * s, hy + 2 * s, hx + 10 * s + o, hy + 5 * s, p[3], max(2, int(3 * s)), 6)
    eye(c, hx + 2 * s, hy - 1 * s, p[4] if len(p) > 4 else (255, 90, 60, 255))
    return finish(c)


def floater(sz, p, fr, kind="wisp"):
    c = Canvas(sz, sz)
    s = sz / 48
    bob = [0, -2, -1, 1][fr] * s
    cx, cy = sz * 0.5, sz * 0.5 + bob
    if kind == "wisp":
        for i in range(4):
            c.ellipse(cx - 4 * s * i * 0.5, cy + 6 * s + i * 3 * s, (8 - i * 1.5) * s, (5 - i) * s, shade(p[0], -0.1 * i), 1)
        c.ellipse(cx, cy, 10 * s, 11 * s, p[0], 1)
        c.ellipse(cx - 2 * s, cy - 3 * s, 5 * s, 5 * s, p[3], 2)
        if fr == 2:
            c.ellipse(cx + 12 * s, cy - 4 * s, 4 * s, 4 * s, p[4] if len(p) > 4 else (255, 200, 80, 255), 8)
    elif kind == "eye":
        c.ellipse(cx, cy, 13 * s, 12 * s, p[0], 1)
        c.ellipse(cx + 2 * s, cy, 8 * s, 8 * s, (240, 236, 220, 255), 2)
        c.ellipse(cx + 4 * s, cy, 4 * s, 5 * s if fr != 1 else 1.5 * s, p[3], 3)
        for i in range(5):
            a = i * 1.2
            c.line(cx - 8 * s, cy + 6 * s, cx - 16 * s + i * 2 * s, cy + 14 * s + math.sin(a + fr) * 2 * s, p[1], max(1, int(2 * s)), 4)
    elif kind == "lantern":
        c.line(cx, cy - 16 * s, cx, cy - 10 * s, p[1], 1, 1)
        c.rect(cx - 7 * s, cy - 10 * s, cx + 7 * s, cy + 8 * s, p[1], 1)
        c.rect(cx - 5 * s, cy - 8 * s, cx + 5 * s, cy + 6 * s, p[3] if fr != 1 else shade(p[3], 0.3), 2)
        eye(c, cx - 2 * s, cy - 1 * s, (40, 20, 20, 255), 1.4 * s)
        eye(c, cx + 2 * s, cy - 1 * s, (40, 20, 20, 255), 1.4 * s)
    elif kind == "shard":
        pts = [(cx, cy - 16 * s), (cx + 8 * s, cy - 2 * s), (cx + 3 * s, cy + 16 * s), (cx - 6 * s, cy + 6 * s), (cx - 8 * s, cy - 6 * s)]
        c.poly(pts, p[0], 1)
        c.line(cx, cy - 14 * s, cx + 1 * s, cy + 12 * s, shade(p[0], 0.45), 1, 2)
        eye(c, cx + 2 * s, cy - 2 * s, p[3])
    elif kind == "sprite":
        c.ellipse(cx, cy, 8 * s, 8 * s, p[0], 1)
        for i in range(6):
            a = i * math.pi / 3 + fr * 0.3
            c.ellipse(cx + math.cos(a) * 10 * s, cy + math.sin(a) * 10 * s, 2.5 * s, 2.5 * s, shade(p[0], -0.2), 2)
        eye(c, cx + 2 * s, cy - 2 * s, p[3])
        eye(c, cx - 2 * s, cy - 2 * s, p[3])
    return finish(c)


def blob(sz, p, fr, kind="slime"):
    c = Canvas(sz, sz)
    s = sz / 48
    sq = [0, 1, 3, -1][fr] * s
    cx = sz * 0.5
    base = sz - 3 * s
    if kind == "slime":
        c.ellipse(cx, base - 10 * s + sq, 15 * s + sq, 11 * s - sq, p[0], 1)
        c.ellipse(cx - 4 * s, base - 14 * s + sq, 5 * s, 3 * s, shade(p[0], 0.35), 2)
        eye(c, cx + 5 * s, base - 12 * s + sq, (20, 20, 20, 255), 1.5 * s)
        eye(c, cx + 10 * s, base - 11 * s + sq, (20, 20, 20, 255), 1.5 * s)
    else:  # leech
        for i in range(5):
            c.ellipse(cx - 12 * s + i * 6 * s, base - 8 * s - math.sin(i + fr) * 3 * s, 6 * s, 6 * s, shade(p[0], -0.06 * i), 1)
        c.ellipse(cx + 14 * s, base - 10 * s, 5 * s, 5 * s, p[3], 2)
        c.ellipse(cx + 16 * s, base - 10 * s, 2 * s, 2 * s, (40, 10, 20, 255), 3)
    return finish(c)


def construct(sz, p, fr, kind="drone"):
    c = Canvas(sz, sz)
    s = sz / 48
    bob = [0, 1, 0, 1][fr] * s
    cx, cy = sz * 0.5, sz * 0.55 + bob
    if kind == "drone":
        c.ellipse(cx, cy - 4 * s, 12 * s, 9 * s, p[0], 1)
        c.rect(cx - 16 * s, cy - 6 * s, cx + 16 * s, cy - 4 * s, p[1], 2)
        c.ellipse(cx - 16 * s, cy - 7 * s, 4 * s, 1.5 * s, shade(p[1], 0.3), 2)
        c.ellipse(cx + 16 * s, cy - 7 * s, 4 * s, 1.5 * s, shade(p[1], 0.3), 2)
        eye(c, cx + 4 * s, cy - 3 * s, p[3], 2.5 * s)
    elif kind == "shell":
        c.poly([(cx - 14 * s, sz - 3 * s), (cx - 10 * s, cy - 14 * s), (cx + 10 * s, cy - 14 * s), (cx + 14 * s, sz - 3 * s)], p[0], 1)
        for y in range(int(cy - 10 * s), int(sz - 4 * s), int(max(2, 4 * s))):
            c.line(cx - 12 * s, y, cx + 12 * s, y, shade(p[0], -0.3), 1, 1)
        c.ellipse(cx + 3 * s, cy - 2 * s, 5 * s, 5 * s, p[3] if fr != 2 else shade(p[3], 0.4), 2)
    elif kind == "golem":
        c.rect(cx - 12 * s, cy - 14 * s, cx + 12 * s, cy + 8 * s, p[0], 1)
        c.rect(cx - 7 * s, cy - 22 * s, cx + 7 * s, cy - 14 * s, p[1], 2)
        c.rect(cx - 18 * s, cy - 12 * s - (4 * s if fr == 2 else 0), cx - 12 * s, cy + 4 * s, p[1], 3)
        c.rect(cx + 12 * s, cy - 12 * s - (6 * s if fr == 2 else 0), cx + 18 * s, cy + 4 * s, p[1], 3)
        c.rect(cx - 10 * s, cy + 8 * s, cx - 3 * s, sz - 3 * s, shade(p[0], -0.2), 4)
        c.rect(cx + 3 * s, cy + 8 * s, cx + 10 * s, sz - 3 * s, shade(p[0], -0.2), 4)
        eye(c, cx + 3 * s, cy - 18 * s, p[3], 1.6 * s)
    elif kind == "relay":
        c.rect(cx - 5 * s, cy - 4 * s, cx + 5 * s, sz - 3 * s, p[1], 1)
        c.ellipse(cx, cy - 10 * s, 9 * s, 9 * s, p[0], 2)
        c.ellipse(cx, cy - 10 * s, 5 * s, 5 * s, p[3] if fr % 2 == 0 else shade(p[3], 0.4), 3)
        for a in range(3):
            c.line(cx, cy - 10 * s, cx + math.cos(a * 2.1 + fr) * 14 * s, cy - 10 * s + math.sin(a * 2.1 + fr) * 14 * s, shade(p[3], 0.2), 1, 4)
    elif kind == "sentinel":
        c.poly([(cx - 10 * s, sz - 3 * s), (cx - 8 * s, cy - 18 * s), (cx + 8 * s, cy - 18 * s), (cx + 10 * s, sz - 3 * s)], p[0], 1)
        c.ellipse(cx, cy - 22 * s, 6 * s, 6 * s, p[1], 2)
        c.line(cx + 12 * s, cy - 26 * s, cx + 12 * s, sz - 3 * s, p[1], 2, 3)
        c.poly([(cx + 9 * s, cy - 26 * s), (cx + 16 * s, cy - 30 * s), (cx + 15 * s, cy - 22 * s)], (220, 220, 230, 255), 3)
        c.ellipse(cx, cy - 4 * s, 4 * s, 4 * s, p[3], 4)
    elif kind == "automaton":
        c.rect(cx - 10 * s, cy - 16 * s, cx + 10 * s, cy + 6 * s, p[0], 1)
        c.ellipse(cx, cy - 6 * s, 6 * s, 6 * s, p[3] if fr != 2 else (255, 240, 180, 255), 2)
        for i, gx in enumerate((-14, 14)):
            c.ellipse(cx + gx * s, cy - 8 * s, 5 * s, 5 * s, p[1], 3)
        c.rect(cx - 8 * s, cy + 6 * s, cx - 3 * s, sz - 3 * s, p[1], 4)
        c.rect(cx + 3 * s, cy + 6 * s, cx + 8 * s, sz - 3 * s, p[1], 4)
        c.rect(cx - 6 * s, cy - 22 * s, cx + 6 * s, cy - 16 * s, shade(p[0], 0.2), 5)
    return finish(c)


def winged(sz, p, fr, kind="moth"):
    c = Canvas(sz, sz)
    s = sz / 48
    flap = [0, 6, -3, 2][fr] * s
    cx, cy = sz * 0.5, sz * 0.5
    if kind in ("moth", "kite"):
        c.poly([(cx, cy), (cx - 18 * s, cy - 14 * s - flap), (cx - 20 * s, cy + 2 * s), (cx - 6 * s, cy + 8 * s)], p[1], 1)
        c.poly([(cx, cy), (cx + 16 * s, cy - 14 * s - flap), (cx + 18 * s, cy + 2 * s), (cx + 6 * s, cy + 8 * s)], shade(p[1], 0.1), 1)
        if kind == "moth":
            c.ellipse(cx - 12 * s, cy - 6 * s - flap * 0.5, 3 * s, 3 * s, p[3], 2)
            c.ellipse(cx + 11 * s, cy - 6 * s - flap * 0.5, 3 * s, 3 * s, p[3], 2)
        c.ellipse(cx, cy + 2 * s, 4 * s, 10 * s, p[0], 3)
        eye(c, cx + 2 * s, cy - 6 * s, p[4] if len(p) > 4 else (255, 90, 90, 255))
        if kind == "kite":
            c.line(cx, cy + 12 * s, cx - 6 * s, sz - 2 * s, p[3], 1, 4)
    elif kind == "seraph":
        for side in (-1, 1):
            for i in range(3):
                c.line(cx, cy - 4 * s, cx + side * (14 + i * 4) * s, cy - (18 - i * 6) * s - flap, shade(p[1], 0.1 * i), max(2, int(3 * s)), 1)
        c.poly([(cx - 5 * s, cy - 6 * s), (cx + 5 * s, cy - 6 * s), (cx + 7 * s, cy + 16 * s), (cx - 7 * s, cy + 16 * s)], p[0], 2)
        c.ellipse(cx, cy - 11 * s, 5 * s, 5 * s, shade(p[0], 0.2), 3)
        c.ellipse(cx, cy - 18 * s, 6 * s, 1.5 * s, p[3], 4)
        eye(c, cx + 2 * s, cy - 11 * s, p[3])
    return finish(c)


def humanoid(sz, p, fr, kind="knight"):
    c = Canvas(sz, sz)
    s = sz / 48
    bob = [0, 1, 0, 1][fr] * s
    cx = sz * 0.46
    feet = sz - 3 * s
    hip = feet - 14 * s
    neck = hip - 14 * s + bob
    swing = 8 * s if fr == 2 else 0
    if kind in ("knight", "lancer", "diver", "imp", "remnant", "page", "singer", "choirling"):
        if kind not in ("singer", "choirling", "page"):
            c.line(cx - 3 * s, hip, cx - 5 * s, feet, p[1], max(2, int(4 * s)), 4)
            c.line(cx + 3 * s, hip, cx + 5 * s, feet, shade(p[1], -0.2), max(2, int(4 * s)), 4)
        else:
            c.poly([(cx - 6 * s, neck + 2 * s), (cx + 6 * s, neck + 2 * s), (cx + 10 * s, feet), (cx - 10 * s, feet)], p[1], 4)
        c.poly([(cx - 7 * s, neck), (cx + 7 * s, neck), (cx + 6 * s, hip), (cx - 6 * s, hip)], p[0], 1)
        c.ellipse(cx, neck - 6 * s, 5.5 * s, 6 * s, p[2], 2)
        if kind == "knight":
            c.rect(cx - 6 * s, neck - 9 * s, cx + 6 * s, neck - 6 * s, shade(p[0], 0.2), 5)
            c.line(cx + 8 * s, neck + 2 * s, cx + 20 * s + swing, neck - 10 * s + swing, (200, 200, 210, 255), 2, 6)
            eye(c, cx + 3 * s, neck - 6 * s, p[3])
        elif kind == "lancer":
            c.line(cx - 4 * s, neck + 4 * s, cx + 24 * s + swing, neck - 2 * s, p[3], 2, 6)
            c.poly([(cx + 24 * s + swing, neck - 5 * s), (cx + 30 * s + swing, neck - 2 * s), (cx + 24 * s + swing, neck + 1 * s)], (230, 230, 240, 255), 6)
            eye(c, cx + 3 * s, neck - 6 * s, p[3])
        elif kind == "diver":
            c.ellipse(cx, neck - 6 * s, 7 * s, 7 * s, shade(p[2], -0.1), 2)
            c.ellipse(cx + 3 * s, neck - 6 * s, 3.5 * s, 3.5 * s, p[3], 3)
            c.line(cx + 7 * s, neck + 4 * s, cx + 16 * s + swing, neck + 8 * s, p[1], 2, 6)
        elif kind == "imp":
            c.poly([(cx - 4 * s, neck - 11 * s), (cx - 2 * s, neck - 16 * s), (cx, neck - 11 * s)], p[3], 5)
            c.poly([(cx + 1 * s, neck - 11 * s), (cx + 4 * s, neck - 16 * s), (cx + 5 * s, neck - 11 * s)], p[3], 5)
            eye(c, cx + 3 * s, neck - 6 * s, (255, 200, 60, 255))
            c.ellipse(cx + 12 * s + swing, neck + 2 * s, 2.5 * s, 2.5 * s, (170, 170, 180, 255), 6)
        elif kind == "remnant":
            c.poly([(cx - 8 * s, neck - 12 * s), (cx - 4 * s, neck - 18 * s), (cx, neck - 12 * s), (cx + 4 * s, neck - 18 * s), (cx + 8 * s, neck - 12 * s)], p[3], 5)
            eye(c, cx + 3 * s, neck - 6 * s, p[3])
        elif kind == "page":
            for i in range(4):
                c.rect(cx - 8 * s + i * 4 * s, neck - 2 * s + (i % 2) * 2 * s, cx - 5 * s + i * 4 * s, hip + 6 * s, (230, 225, 205, 255), 3)
            eye(c, cx + 3 * s, neck - 6 * s, p[3])
        elif kind in ("singer", "choirling"):
            c.ellipse(cx + 3 * s, neck - 4 * s, 2 * s, 2.5 * s if fr != 2 else 3.5 * s, (30, 10, 30, 255), 3)
            eye(c, cx + 3 * s, neck - 8 * s, p[3])
            if kind == "choirling":
                c.ellipse(cx, neck - 14 * s, 6 * s, 1.5 * s, p[3], 5)
    return finish(c)


def serpent(sz, p, fr):
    c = Canvas(sz, sz)
    s = sz / 48
    base = sz - 6 * s
    pts = []
    for i in range(10):
        x = sz * 0.15 + i * sz * 0.07
        y = base - math.sin(i * 0.8 + fr * 0.7) * 5 * s - (i * 1.5 * s if i > 6 else 0)
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        c.ellipse(x, y, (3 + i * 0.35) * s, (3 + i * 0.3) * s, p[0] if i % 2 else shade(p[0], 0.08), 1)
    hx, hy = pts[-1][0] + 5 * s, pts[-1][1] - 5 * s - (4 * s if fr == 2 else 0)
    c.ellipse(hx, hy, 7 * s, 5 * s, p[1], 2)
    eye(c, hx + 2 * s, hy - 2 * s, p[3])
    c.line(hx + 6 * s, hy + 1 * s, hx + 10 * s, hy + 2 * s, (220, 60, 60, 255), 1, 3)
    return finish(c)


def plant(sz, p, fr, kind="flower"):
    c = Canvas(sz, sz)
    s = sz / 48
    cx = sz * 0.5
    base = sz - 3 * s
    c.line(cx, base, cx + 2 * s, base - 18 * s, p[1], max(2, int(3 * s)), 1)
    c.ellipse(cx - 6 * s, base - 8 * s, 6 * s, 3 * s, p[1], 2)
    c.ellipse(cx + 8 * s, base - 12 * s, 6 * s, 3 * s, shade(p[1], 0.1), 2)
    hx, hy = cx + 2 * s, base - 22 * s + [0, 1, -2, 2][fr] * s
    for i in range(6):
        a = i * math.pi / 3 + fr * 0.2
        c.ellipse(hx + math.cos(a) * 6 * s, hy + math.sin(a) * 6 * s, 4 * s, 4 * s, p[0], 3)
    c.ellipse(hx, hy, 4 * s, 4 * s, p[3], 4)
    if fr == 2:
        for i in range(6):
            c.put(hx + 10 * s + i * 2 * s, hy - 4 * s + (i % 3) * 3 * s, (250, 240, 150, 255), 5)
    return finish(c)


def hand(sz, p, fr):
    c = Canvas(sz, sz)
    s = sz / 48
    rise = 10 * s if fr == 2 else 0
    cx, cy = sz * 0.5, sz * 0.6 - rise
    c.rect(cx - 6 * s, cy, cx + 6 * s, sz - 3 * s, p[1], 1)
    c.ellipse(cx, cy - 4 * s, 11 * s, 9 * s, p[0], 2)
    for i in range(4):
        c.rect(cx - 9 * s + i * 5 * s, cy - 14 * s, cx - 6 * s + i * 5 * s, cy - 6 * s, shade(p[0], 0.05 * i), 3)
    c.rect(cx + 10 * s, cy - 6 * s, cx + 14 * s, cy + 1 * s, p[0], 3)
    c.ellipse(cx, cy - 2 * s, 3 * s, 3 * s, p[3], 4)
    return finish(c)


def crab(sz, p, fr):
    return bug(sz, p, fr, legs=6, shell=True, pincers=True, round_=0.75)


FAMILY = {
    "rat": lambda sz, p, fr: quadruped(sz, p, fr, body=(0.46, 0.24), head=0.2, snout=0.1),
    "hound": lambda sz, p, fr: quadruped(sz, p, fr, body=(0.5, 0.26), head=0.22, snout=0.14),
    "wolf": lambda sz, p, fr: quadruped(sz, p, fr, body=(0.56, 0.3), head=0.24, mane=True, snout=0.14),
    "beetle": lambda sz, p, fr: bug(sz, p, fr, legs=6, shell=True, spikes=2),
    "mite": lambda sz, p, fr: bug(sz, p, fr, legs=8, shell=False, round_=0.9),
    "tick": lambda sz, p, fr: bug(sz, p, fr, legs=8, shell=True, round_=0.9, spikes=0),
    "widow": lambda sz, p, fr: bug(sz, p, fr, legs=8, shell=True, round_=0.8, spikes=3),
    "crab": crab,
    "wisp": lambda sz, p, fr: floater(sz, p, fr, "wisp"),
    "eye": lambda sz, p, fr: floater(sz, p, fr, "eye"),
    "lantern": lambda sz, p, fr: floater(sz, p, fr, "lantern"),
    "shard": lambda sz, p, fr: floater(sz, p, fr, "shard"),
    "sprite": lambda sz, p, fr: floater(sz, p, fr, "sprite"),
    "slime": lambda sz, p, fr: blob(sz, p, fr, "slime"),
    "leech": lambda sz, p, fr: blob(sz, p, fr, "leech"),
    "drone": lambda sz, p, fr: construct(sz, p, fr, "drone"),
    "shell": lambda sz, p, fr: construct(sz, p, fr, "shell"),
    "golem": lambda sz, p, fr: construct(sz, p, fr, "golem"),
    "relay": lambda sz, p, fr: construct(sz, p, fr, "relay"),
    "sentinel": lambda sz, p, fr: construct(sz, p, fr, "sentinel"),
    "automaton": lambda sz, p, fr: construct(sz, p, fr, "automaton"),
    "moth": lambda sz, p, fr: winged(sz, p, fr, "moth"),
    "kite": lambda sz, p, fr: winged(sz, p, fr, "kite"),
    "seraph": lambda sz, p, fr: winged(sz, p, fr, "seraph"),
    "knight": lambda sz, p, fr: humanoid(sz, p, fr, "knight"),
    "lancer": lambda sz, p, fr: humanoid(sz, p, fr, "lancer"),
    "diver": lambda sz, p, fr: humanoid(sz, p, fr, "diver"),
    "imp": lambda sz, p, fr: humanoid(sz, p, fr, "imp"),
    "remnant": lambda sz, p, fr: humanoid(sz, p, fr, "remnant"),
    "page": lambda sz, p, fr: humanoid(sz, p, fr, "page"),
    "singer": lambda sz, p, fr: humanoid(sz, p, fr, "singer"),
    "choirling": lambda sz, p, fr: humanoid(sz, p, fr, "choirling"),
    "viper": serpent,
    "flower": lambda sz, p, fr: plant(sz, p, fr),
    "hand": hand,
}

# per-identity: shape, size, palette (body, secondary, belly/detail, accent, eye)
EN = {
    "E001": ("rat", 32, pal("8a7a6a", "5a4a3e", "c8b0a0", "e0a080", "ff4040")),
    "E002": ("beetle", 32, pal("4a5a3a", "2a3020", "7a8a4a", "c0a040")),
    "E003": ("wisp", 32, pal("f08a3a", "c05020", "f0c080", "fff0b0", "ffe080")),
    "E004": ("hound", 48, pal("6a2e2e", "3a1a1a", "a86a5a", "c0a040", "ffd060")),
    "E005": ("slime", 32, pal("5a8a7a", "3a5a50", "8ab8a8", "d0f0e0")),
    "E006": ("drone", 32, pal("8a8e98", "5a5e68", "b0b4c0", "e04040")),
    "E007": ("moth", 32, pal("c8b8a0", "a89880", "e8dcc8", "4a3a2a", "202020")),
    "E008": ("shell", 48, pal("7a4a2a", "5a3a2a", "a07050", "f0c040")),
    "E009": ("wolf", 48, pal("5a4a3a", "3a2e24", "8a7a60", "3e5a2a", "ffd040")),
    "E010": ("mite", 32, pal("6a8a3a", "3a4a1a", "a0c060", "d0e080")),
    "E011": ("flower", 48, pal("d86a9a", "3a6a2a", "f0a0c0", "f0e060")),
    "E012": ("lantern", 32, pal("4a6a7a", "2e3e48", "6a9aaa", "a0f0d0")),
    "E013": ("imp", 32, pal("8a4a2a", "5a2e1a", "c07a4a", "e0a040")),
    "E014": ("crab", 48, pal("b85a2a", "7a3a1a", "e08a4a", "f0a060", "ffffff")),
    "E015": ("sprite", 32, pal("3a3438", "1e1a1e", "5a5058", "ffc060")),
    "E016": ("hand", 48, pal("8a6a4a", "5a4a3a", "b08a6a", "ff7a30")),
    "E017": ("page", 48, pal("5a8a8a", "3a6a6a", "e8e0c8", "2a6a9a")),
    "E018": ("leech", 48, pal("4a6a5a", "2a4a3a", "7a9a8a", "c04a5a")),
    "E019": ("diver", 48, pal("3a5a6a", "2a3a4a", "8aa0a8", "a0ffff")),
    "E020": ("eye", 48, pal("6a5a7a", "4a3a5a", "e8e0d0", "3a8a5a")),
    "E021": ("kite", 32, pal("d0a040", "b08030", "e8d8a8", "a02a2a", "202020")),
    "E022": ("viper", 48, pal("6a8a6a", "4a6a4a", "a8c0a0", "f0e040")),
    "E023": ("golem", 64, pal("8a8a86", "6a6a68", "a8a8a4", "60c0ff")),
    "E024": ("tick", 32, pal("5a5a8a", "3a3a5a", "8a8ab0", "e0e060")),
    "E025": ("sentinel", 64, pal("d8d8dc", "a8a8b0", "f0f0f4", "8a6ac8")),
    "E026": ("leech", 48, pal("c8c0d8", "8a80a0", "e8e0f0", "8a4ac8")),
    "E027": ("wolf", 48, pal("c8d8e8", "8a9ab0", "f0f4f8", "6aa0d0", "60c0ff")),
    "E028": ("hound", 48, pal("8a8aa0", "5a5a70", "b0b0c8", "8a6ac8", "e080ff")),
    "E029": ("shard", 32, pal("d8c8f0", "a898c8", "f0e8ff", "8a4ac8")),
    "E030": ("singer", 48, pal("e8e0f0", "b8a8d0", "f4f0f8", "a080e0")),
    "E031": ("widow", 48, pal("a8b8c8", "5a6a7a", "d8e8f0", "e04060", "ff4060")),
    "E032": ("knight", 64, pal("5a5a6a", "3a3a48", "8a8aa0", "a0ffe0")),
    "E033": ("relay", 48, pal("5a5a68", "3a3a44", "8a8a98", "ff4a4a")),
    "E034": ("lancer", 64, pal("6a2a2a", "3a1a1a", "c8a88a", "c0c0c8")),
    "E035": ("wisp", 32, pal("e05a4a", "a03020", "f0a080", "fff0c0", "ff8060")),
    "E036": ("shell", 64, pal("3a3a48", "22222c", "6a6a7a", "ff5a4a")),
    "E037": ("seraph", 64, pal("e8e0c8", "c8b890", "f8f4e8", "ffd070")),
    "E038": ("automaton", 64, pal("a8803a", "6a4a2a", "d0b070", "ff6a3a")),
    "E039": ("choirling", 48, pal("6a4a6a", "4a2e4a", "c8b8c8", "e05a8a")),
    "E040": ("remnant", 64, pal("8a2a3a", "5a1a24", "d8b8a0", "ffd060")),
}


# ---------------------------------------------------------------- bosses
# ---------------------------------------------------------------- boss construction kit
def cap(c, x0, y0, x1, y1, r0, r1, col, tag):
    """Tapered capsule (limb, pipe, neck): the painter shades it as a cylinder."""
    n = int(max(abs(x1 - x0), abs(y1 - y0), 1) * 1.5) + 1
    for i in range(n + 1):
        t = i / n
        r = r0 + (r1 - r0) * t
        c.ellipse(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, r, col, tag)


def path(c, pts, rs, col, tag):
    for i in range(len(pts) - 1):
        cap(c, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], rs[i], rs[i + 1], col, tag)


def seam(c, x0, y0, x1, y1, col, f=-0.42):
    c.line(x0, y0, x1, y1, shade(col, f), 1, 8)


def rivet(c, x, y, col):
    c.put(x, y, shade(col, 0.5), 8)
    c.put(x + 1, y + 1, shade(col, -0.55), 8)


def glow(c, x, y, rx, ry, col, lit=True):
    c.ellipse(x, y, rx, ry, col if lit else shade(col, -0.55), 9)
    if lit and rx >= 2:
        c.ellipse(x - rx * 0.35, y - ry * 0.35, max(0.6, rx * 0.35), max(0.6, ry * 0.35), shade(col, 0.6), 9)


def puff(c, x, y, r, a=190):
    c.ellipse(x, y, r, r * 0.8, (206, 200, 196, a), 8)
    c.ellipse(x - r * 0.3, y - r * 0.3, r * 0.5, r * 0.4, (236, 232, 226, a), 8)


def cloth(c, top, bot, x0, x1, bx0, bx1, col, tag, folds=4, sway=0):
    """Hanging robe/cape: trapezoid with vertical fold seams and a ragged hem."""
    c.poly([(x0, top), (x1, top), (bx1 + sway, bot), (bx0 + sway, bot)], col, tag)
    for i in range(1, folds):
        t = i / folds
        seam(c, x0 + (x1 - x0) * t, top + 6, bx0 + (bx1 - bx0) * t + sway, bot - 2, col, -0.3)
    for x in range(int(bx0 + sway), int(bx1 + sway), 4):
        c.put(x + 2, bot, None) if False else c.rect(x + 2, bot - 1, x + 3, bot, (0, 0, 0, 0), tag)


# ---------------------------------------------------------------- bosses (facing right, toward the party)
def boss_extractor(fr, W=136, H=144):
    c = Canvas(W, H)
    brass, iron, steel, red = hexc("b08a3c"), hexc("4a4240"), hexc("9a9aa2"), hexc("e04030")
    bob = [0, 1, -1, 1][fr]
    lift = [0, -3, -20, 3][fr]
    # track
    cap(c, 16, 126, 104, 126, 11, 11, iron, 10)
    for x in range(22, 100, 15):
        c.ellipse(x, 126, 6, 6, hexc("6a605a"), 11)
        c.ellipse(x, 126, 2, 2, iron, 8)
    for x in range(10, 110, 5):
        seam(c, x, 116, x, 117, iron, -0.6)
    # chassis + boiler
    c.poly([(18, 114 + bob), (104, 114 + bob), (98, 100 + bob), (24, 100 + bob)], hexc("7a5a2c"), 12)
    cap(c, 32, 78 + bob, 86, 78 + bob, 23, 23, brass, 13)
    for x in (46, 70):
        seam(c, x, 58 + bob, x, 99 + bob, brass)
        for y in range(62, 98, 7):
            rivet(c, x + 2, y + bob, brass)
    # smokestack and steam
    cap(c, 38, 58 + bob, 36, 28 + bob, 6, 5, iron, 14)
    c.ellipse(36, 27 + bob, 7, 3, shade(iron, 0.2), 15)
    if fr != 1:
        puff(c, 34 - fr, 17 + bob, 6)
        puff(c, 28, 8 + bob, 4, 150)
    # pressure gauge (tell: needle into the red, face glows)
    c.ellipse(58, 82 + bob, 12, 12, hexc("5a4020"), 16)
    face = hexc("ff9a80") if fr == 2 else hexc("ece4cc")
    c.ellipse(58, 82 + bob, 9, 9, face, 9 if fr == 2 else 17)
    c.poly([(58, 82 + bob), (66, 77 + bob), (65, 84 + bob)], (220, 60, 40, 150), 8)
    a = math.pi * (1.15 - [0.3, 0.38, 0.97, 0.5][fr] * 1.4)
    c.line(58, 82 + bob, 58 + math.cos(a) * 8, 82 + bob - math.sin(a) * 8, hexc("b01818"), 2, 8)
    c.ellipse(58, 82 + bob, 1.5, 1.5, iron, 8)
    # heartglass cab
    c.ellipse(80, 56 + bob, 11, 10, hexc("5a4020"), 18)
    glow(c, 80, 55 + bob, 7, 7, hexc("e0485a") if fr != 2 else hexc("ff8a8a"))
    # hydraulic arm and clamp
    sx, sy = 96, 70 + bob
    ex, ey = 120, 34 + lift + bob
    wx, wy = 127, 74 + lift // 2 + bob
    path(c, [(sx, sy), (ex, ey)], [6, 5], hexc("3e3834"), 19)
    cap(c, sx - 4, sy + 6, ex - 6, ey + 10, 2, 2, steel, 20)
    path(c, [(ex, ey), (wx, wy)], [5, 4], hexc("4a4440"), 21)
    c.ellipse(ex, ey, 5, 5, brass, 22)
    rivet(c, ex, ey, brass)
    jaw = 6 if fr == 2 else 3
    c.poly([(wx - 7, wy), (wx + 6, wy), (wx + 2 - jaw, wy + 16), (wx - 9, wy + 10)], steel, 23)
    c.poly([(wx - 1, wy + 1), (wx + 9, wy + 2), (wx + 8, wy + 14), (wx + 2 + jaw, wy + 18)], shade(steel, -0.1), 24)
    # hose
    path(c, [(86, 96 + bob), (100, 104 + bob), (108, 88 + bob), (104, 72 + bob)], [2, 2, 2, 2], hexc("2a2628"), 25)
    return finish(c)


def boss_bailiff(fr, W=112, H=150):
    """B02 Brass Bailiff: a constable automaton, lamp-eyed helm, baton, stamped warrant on its chest."""
    c = Canvas(W, H)
    brass, dk, paper, lamp = hexc("b8923e"), hexc("4a3a26"), hexc("ece0bc"), hexc("ffd060")
    bob = [0, 1, 0, 1][fr]
    base = H - 4
    # legs: pistons on a wide foot plate
    for lx, t in ((40, 10), (64, 11)):
        path(c, [(lx, base - 44), (lx - 2, base - 22), (lx, base - 6)], [7, 5, 6], dk, t)
        c.poly([(lx - 10, base), (lx + 12, base), (lx + 9, base - 7), (lx - 8, base - 7)], brass, t + 2)
    # coat tails and bell torso
    c.poly([(30, base - 60 + bob), (76, base - 60 + bob), (84, base - 30), (22, base - 30)], hexc("3a3a52"), 14)
    c.poly([(34, base - 104 + bob), (74, base - 104 + bob), (82, base - 58 + bob), (26, base - 58 + bob)], brass, 15)
    seam(c, 54, base - 102 + bob, 54, base - 60 + bob, brass)
    for y in range(base - 98, base - 60, 8):
        rivet(c, 57, y + bob, brass)
    c.rect(26, base - 62 + bob, 82, base - 57 + bob, dk, 16)
    c.rect(50, base - 62 + bob, 58, base - 57 + bob, hexc("d8c060"), 17)
    # warrant (tell: raised and stamped red)
    wy = base - 96 + bob - (22 if fr == 2 else 0)
    wx = 60 if fr != 2 else 84
    c.poly([(wx, wy), (wx + 20, wy - 2), (wx + 22, wy + 22), (wx + 2, wy + 24)], paper, 18)
    for k in range(4):
        seam(c, wx + 4, wy + 5 + k * 4, wx + 16, wy + 4 + k * 4, paper, -0.35)
    if fr == 2:
        glow(c, wx + 13, wy + 17, 4, 4, hexc("e03030"))
    # arms
    path(c, [(34, base - 98 + bob), (22, base - 76 + bob), (26, base - 56 + bob)], [7, 6, 5], brass, 19)
    ax = [(74, base - 98 + bob), (92, base - 84 + bob), (98, base - 66 + bob)] if fr != 2 else \
         [(74, base - 98 + bob), (88, base - 112 + bob), (86, wy + 20)]
    path(c, ax, [7, 6, 5], shade(brass, -0.08), 20)
    if fr != 2:
        cap(c, 98, base - 66 + bob, 106, base - 30 + bob, 3, 3, hexc("2a2230"), 21)   # baton
        c.ellipse(106, base - 29 + bob, 3, 3, hexc("d8c060"), 22)
    # helm with lamp eye
    c.ellipse(54, base - 114 + bob, 15, 13, brass, 23)
    c.poly([(36, base - 118 + bob), (72, base - 118 + bob), (66, base - 124 + bob), (42, base - 124 + bob)], dk, 24)
    c.rect(44, base - 142 + bob, 64, base - 123 + bob, hexc("2e2a3a"), 25)
    c.rect(44, base - 128 + bob, 64, base - 125 + bob, brass, 26)
    glow(c, 62, base - 113 + bob, 5, 4, lamp if fr != 2 else hexc("ff6040"))
    return finish(c)


def boss_stag(fr, W=148, H=164):
    """B03 Rootbound Stag: bark-plated stag, roots trailing into the ground, blossoming antlers (tell)."""
    c = Canvas(W, H)
    hide, bark, pale, bloom, root = hexc("7a5a3a"), hexc("4a3a2a"), hexc("d8c8a0"), hexc("f0a0c8"), hexc("5a4630")
    bob = [0, 1, 0, 1][fr]
    base = H - 4
    # roots across the ground
    for rx, k in ((20, 0), (54, 1), (96, 2), (122, 3)):
        path(c, [(rx, base - 4), (rx - 10 + k * 3, base), (rx - 22, base - 2)], [3, 2, 1], root, 10 + k)
    # far legs (darker)
    for lx, t in ((44, 14), (98, 15)):
        path(c, [(lx, base - 62), (lx + 2, base - 34), (lx - 2, base - 14), (lx, base - 2)], [7, 4, 3, 3], shade(hide, -0.25), t)
    # body
    c.ellipse(72, base - 72 + bob, 42, 22, hide, 16)
    c.ellipse(66, base - 60 + bob, 34, 12, pale, 17)       # belly
    c.ellipse(40, base - 76 + bob, 16, 18, hide, 18)       # haunch
    for i in range(6):
        seam(c, 46 + i * 9, base - 90 + bob, 42 + i * 9, base - 72 + bob, bark, -0.1)
    c.poly([(30, base - 88 + bob), (100, base - 94 + bob), (96, base - 84 + bob), (34, base - 80 + bob)], bark, 19)  # bark mantle
    # near legs
    for lx, t in ((36, 20), (92, 21)):
        path(c, [(lx, base - 60 + bob), (lx - 3, base - 34), (lx + 1, base - 14), (lx - 1, base - 2)], [8, 5, 3, 4], hide, t)
        c.ellipse(lx - 1, base - 2, 4, 2, bark, t + 10)
        path(c, [(lx + 1, base - 16), (lx + 8, base - 4), (lx + 14, base)], [2, 2, 1], root, t + 20)
    # neck and head (tell: head raised)
    hy = base - 112 + bob - (4 if fr == 2 else 0)
    path(c, [(96, base - 82 + bob), (108, base - 98 + bob), (116, hy + 8)], [14, 11, 9], hide, 22)
    c.ellipse(120, hy, 11, 9, hide, 23)
    path(c, [(124, hy + 2), (137, hy + 8)], [7, 4], hide, 24)
    c.ellipse(138, hy + 8, 3, 2, hexc("2a1e1e"), 8)
    c.poly([(112, hy - 6), (106, hy - 16), (116, hy - 8)], hide, 25)
    glow(c, 124, hy - 2, 1.6, 1.6, hexc("f0e070"))
    # antlers
    for side, t in ((-1, 26), (1, 27)):
        x0, y0 = 118 + side * 3, hy - 8
        pts = [(x0, y0), (x0 - 6 + side * 4, y0 - 16), (x0 - 12 + side * 8, y0 - 30)]
        path(c, pts, [3, 2.5, 2], pale, t)
        cap(c, pts[1][0], pts[1][1], pts[1][0] + 10, pts[1][1] - 8, 2, 1.5, pale, t)
        cap(c, pts[2][0], pts[2][1] + 6, pts[2][0] - 10, pts[2][1] - 2, 2, 1.5, pale, t)
        n = 6 if fr == 2 else 2
        for k in range(n):
            bx = pts[2][0] + (k % 3 - 1) * 5
            by = pts[2][1] + (k // 3) * 6 - 2
            glow(c, bx, by, 2.4, 2.4, bloom)
    return finish(c)


def boss_colossus(fr, W=140, H=156):
    """B04 Foundry Colossus: furnace-chested iron giant; three shoulder vents light left to right (tell)."""
    c = Canvas(W, H)
    iron, rust, dk, fire = hexc("6a4a3a"), hexc("9a5a34"), hexc("3a2a26"), hexc("ff8a30")
    bob = [0, 1, -1, 1][fr]
    base = H - 4
    for lx, t in ((46, 10), (88, 11)):
        path(c, [(lx, base - 50), (lx - 2, base - 24), (lx, base - 8)], [12, 10, 11], dk, t)
        c.poly([(lx - 16, base), (lx + 16, base), (lx + 12, base - 10), (lx - 12, base - 10)], iron, t + 2)
    # torso barrel
    c.poly([(34, base - 118 + bob), (106, base - 118 + bob), (114, base - 50 + bob), (26, base - 50 + bob)], iron, 14)
    for y in (base - 100, base - 76):
        c.rect(28, y + bob, 112, y + 4 + bob, rust, 15)
        for x in range(32, 110, 9):
            rivet(c, x, y + 1 + bob, rust)
    # furnace grate
    c.rect(52, base - 96 + bob, 88, base - 62 + bob, hexc("2a1612"), 16)
    for x in range(55, 87, 6):
        glow(c, x + 2, base - 79 + bob, 2, 14, fire if fr != 3 else hexc("ffd080"))
    c.rect(50, base - 98 + bob, 90, base - 96 + bob, dk, 8)
    # shoulders, vents
    for sx, t in ((28, 17), (112, 18)):
        c.ellipse(sx, base - 112 + bob, 18, 14, rust, t)
    for i in range(3):
        lit = fr == 2 or (fr == 1 and i == 0) or (fr == 3 and i < 2)
        vx = 34 + i * 36
        cap(c, vx, base - 124 + bob, vx, base - 140 + bob, 5, 5, dk, 19 + i)
        glow(c, vx, base - 141 + bob, 4, 2.5, fire, lit)
        if lit and fr == 2:
            puff(c, vx + 2, base - 150 + bob, 4, 160)
    # head
    c.ellipse(70, base - 126 + bob, 13, 11, iron, 23)
    c.rect(62, base - 128 + bob, 80, base - 124 + bob, hexc("1a0e0e"), 8)
    glow(c, 76, base - 126 + bob, 3, 1.5, fire)
    # arms (tell: right arm drawn back for the sweep)
    path(c, [(22, base - 110 + bob), (12, base - 82 + bob), (16, base - 56 + bob)], [11, 10, 9], iron, 24)
    c.ellipse(16, base - 50 + bob, 11, 10, dk, 25)
    ra = [(118, base - 110 + bob), (130, base - 84 + bob), (126, base - 58 + bob)] if fr != 2 else \
         [(118, base - 110 + bob), (132, base - 124 + bob), (134, base - 140 + bob)]
    path(c, ra, [11, 10, 9], shade(iron, 0.06), 26)
    c.ellipse(ra[-1][0], ra[-1][1] + (6 if fr != 2 else -4), 11, 10, dk, 27)
    return finish(c)


def boss_custodian(fr, W=128, H=156):
    """B05 Bell-Sworn Custodian: salt-crusted robed warden bearing a yoke of three bells (one rings = tell)."""
    c = Canvas(W, H)
    robe, salt, bronze, sea = hexc("3a6a66"), hexc("d8d4c0"), hexc("b8883a"), hexc("80f0f0")
    bob = [0, 1, 0, 1][fr]
    base = H - 4
    cloth(c, base - 92 + bob, base, 42, 82, 26, 100, robe, 10, folds=5, sway=[0, 1, 0, -1][fr])
    for i in range(7):
        c.ellipse(30 + i * 11, base - 4 - (i % 2) * 3, 5, 3, salt, 11)
    c.ellipse(62, base - 94 + bob, 20, 12, robe, 12)          # shoulders
    c.ellipse(62, base - 108 + bob, 11, 12, hexc("2a3a3a"), 13)   # hood
    c.ellipse(65, base - 106 + bob, 7, 8, hexc("121c20"), 8)
    glow(c, 67, base - 107 + bob, 2, 1.5, sea)
    # yoke above the hood, three bells
    Y = base - 146
    cap(c, 14, Y + bob, 110, Y + bob, 3, 3, hexc("5a4030"), 14)
    ring = 1
    for i, bx in enumerate((22, 62, 102)):
        sw = 3 if (fr == 2 and i == ring) else 0
        top = Y + 4 + bob
        cap(c, bx, Y + bob, bx + sw, top, 1, 1, hexc("3a3030"), 15 + i)
        c.poly([(bx - 6 + sw, top), (bx + 6 + sw, top), (bx + 10 + sw, top + 16), (bx - 10 + sw, top + 16)], bronze, 18 + i)
        c.ellipse(bx + sw, top, 6, 3, bronze, 18 + i)
        c.ellipse(bx + sw, top + 16, 10, 2.5, shade(bronze, -0.2), 21 + i)
        c.ellipse(bx + sw, top + 18, 1.5, 1.5, hexc("3a3030"), 8)
        if fr == 2 and i == ring:
            for k in range(3):
                seam(c, bx + 14 + k * 4, top + 2, bx + 14 + k * 4, top + 14, sea, 0.4)
    # arms holding the yoke
    path(c, [(46, base - 96 + bob), (34, base - 118 + bob), (38, base - 143 + bob)], [5, 4, 3], robe, 24)
    path(c, [(78, base - 96 + bob), (90, base - 118 + bob), (86, base - 143 + bob)], [5, 4, 3], shade(robe, 0.08), 25)
    return finish(c)


def boss_adjudicator(fr, W=112, H=160):
    """B07 Ivory Adjudicator: tall ivory judge, sigil halo announcing skill/item seals, gavel sceptre."""
    c = Canvas(W, H)
    ivory, gold, violet, dk = hexc("e8e4d8"), hexc("c8a048"), hexc("8a6ac8"), hexc("4a4458")
    bob = [0, 1, 0, 1][fr]
    base = H - 4
    cloth(c, base - 88 + bob, base, 38, 74, 18, 94, ivory, 10, folds=6)
    c.poly([(44, base - 88 + bob), (68, base - 88 + bob), (62, base), (50, base)], violet, 11)   # stole
    c.ellipse(56, base - 94 + bob, 20, 11, ivory, 12)
    c.poly([(40, base - 120 + bob), (72, base - 120 + bob), (74, base - 92 + bob), (38, base - 92 + bob)], ivory, 13)
    for x in (44, 56, 68):
        seam(c, x, base - 118 + bob, x, base - 94 + bob, ivory, -0.25)
    c.rect(38, base - 96 + bob, 74, base - 92 + bob, gold, 14)
    # mask-helm
    c.ellipse(56, base - 130 + bob, 11, 13, ivory, 15)
    c.rect(50, base - 131 + bob, 66, base - 128 + bob, dk, 8)
    glow(c, 62, base - 130 + bob, 2, 1, violet)
    c.poly([(44, base - 138 + bob), (56, base - 150 + bob), (68, base - 138 + bob)], gold, 16)
    # sigil halo (tell: bright and larger)
    r = 16 if fr != 2 else 20
    for a in range(24):
        ang = a * math.pi / 12
        c.ellipse(56 + math.cos(ang) * r, base - 136 + bob + math.sin(ang) * r * 0.35, 1.2, 1.2, violet if fr != 2 else hexc("d0b0ff"), 9)
    # arms: gavel-sceptre raised on tell
    path(c, [(40, base - 114 + bob), (30, base - 92 + bob), (36, base - 74 + bob)], [6, 5, 4], ivory, 17)
    ha = (86, base - 96 + bob) if fr != 2 else (88, base - 136 + bob)
    path(c, [(72, base - 114 + bob), (84, base - 104 + bob), ha], [6, 5, 4], shade(ivory, -0.05), 18)
    cap(c, ha[0], ha[1] + 14, ha[0] + 4, ha[1] - 26, 2, 2, gold, 19)
    c.poly([(ha[0] - 4, ha[1] - 32), (ha[0] + 12, ha[1] - 32), (ha[0] + 12, ha[1] - 22), (ha[0] - 4, ha[1] - 22)], ivory, 20)
    return finish(c)


def boss_choir(fr, W=140, H=140):
    """B08 Pale Choir: three pale masked singers rising from one shared robe; the echoing mask lights (tell)."""
    c = Canvas(W, H)
    robe, mask, lilac, dk = hexc("d8d0e8"), hexc("f4f0f8"), hexc("ff80c0"), hexc("3a2a4a")
    base = H - 4
    cloth(c, base - 70, base, 30, 110, 10, 130, hexc("b8a8d0"), 10, folds=8, sway=[0, 2, 0, -2][fr])
    for i, (ox, h) in enumerate(((30, 96), (70, 112), (110, 96))):
        y = base - h + int(math.sin(i * 1.7 + fr * 1.3) * 3)
        c.poly([(ox - 7, y + 12), (ox + 7, y + 12), (ox + 18, base - 40), (ox - 18, base - 40)], robe, 11 + i)
        c.ellipse(ox, y - 2, 15, 17, hexc("8a7aa8"), 23 + i)       # veil
        c.ellipse(ox + 2, y, 10, 13, mask, 14 + i)
        lit = fr == 2 and i == 1
        for ex in (-4, 5):
            c.rect(ox + ex, y - 3, ox + ex + 3, y - 2, lilac if lit else dk, 9 if lit else 8)
        c.rect(ox + 1, y + 6, ox + 4, y + (7 if fr != 2 else 9), dk, 8)
        seam(c, ox - 5, y + 2, ox - 3, y + 8, mask, -0.25)
        c.poly([(ox - 12, y - 14), (ox + 1, y - 26), (ox + 14, y - 14)], lilac if lit else shade(robe, -0.2), 17 + i)
        path(c, [(ox + 12, y + 20), (ox + 22, y + 34), (ox + 18, y + 44)], [3, 2.5, 2], robe, 20 + i)
    return finish(c)


def boss_voss(fr, W=120, H=158):
    """B09 Marshal Voss: armoured commander in a crimson cape; raises the command baton and points (tell)."""
    c = Canvas(W, H)
    armor, cape, skin, gold = hexc("5a5a6a"), hexc("8a1a22"), hexc("e0b89a"), hexc("d0a040")
    bob = [0, 1, 0, 1][fr]
    base = H - 4
    c.poly([(30, base - 118 + bob), (62, base - 118 + bob), (70, base - 2), (6, base - 8)], cape, 10)   # cape behind
    for x in (20, 32, 44):
        seam(c, x + 8, base - 110 + bob, x - 2, base - 12, cape, -0.3)
    for lx, t in ((48, 11), (66, 12)):
        path(c, [(lx, base - 60), (lx + 2, base - 32), (lx + 4, base - 6)], [8, 6, 6], armor, t)
        c.poly([(lx - 4, base), (lx + 14, base), (lx + 12, base - 8), (lx - 2, base - 8)], hexc("2a2a34"), t + 2)
    c.poly([(40, base - 112 + bob), (78, base - 112 + bob), (74, base - 58 + bob), (42, base - 58 + bob)], armor, 15)
    c.poly([(42, base - 70 + bob), (76, base - 70 + bob), (80, base - 46 + bob), (38, base - 46 + bob)], hexc("3a3a48"), 16)
    c.rect(40, base - 72 + bob, 78, base - 68 + bob, gold, 17)
    for sx, t in ((40, 18), (78, 19)):
        c.ellipse(sx, base - 110 + bob, 11, 8, shade(armor, 0.1), t)
    seam(c, 59, base - 108 + bob, 59, base - 74 + bob, armor)
    # head
    c.ellipse(60, base - 124 + bob, 9, 10, skin, 20)
    c.poly([(50, base - 128 + bob), (70, base - 132 + bob), (70, base - 124 + bob), (50, base - 122 + bob)], hexc("3a3040"), 21)
    c.ellipse(60, base - 132 + bob, 10, 5, hexc("4a4a58"), 22)
    c.put(65, base - 124 + bob, hexc("1a1420"), 8)
    # sword at hip, arms
    cap(c, 38, base - 64 + bob, 26, base - 22, 2, 1.5, hexc("c8c8d4"), 23)
    path(c, [(40, base - 106 + bob), (32, base - 84 + bob), (36, base - 66 + bob)], [6, 5, 4], armor, 24)
    ba = [(78, base - 106 + bob), (92, base - 90 + bob), (100, base - 80 + bob)] if fr != 2 else \
         [(78, base - 106 + bob), (94, base - 118 + bob), (110, base - 128 + bob)]
    path(c, ba, [6, 5, 4], shade(armor, 0.06), 25)
    tip = (ba[-1][0] + (10 if fr != 2 else 8), ba[-1][1] + (6 if fr != 2 else -10))
    cap(c, ba[-1][0], ba[-1][1], tip[0], tip[1], 1.5, 1.5, hexc("2a2030"), 26)
    glow(c, tip[0], tip[1], 2, 2, gold if fr != 2 else hexc("ffe080"))
    return finish(c)


def boss_rook(fr, W=128, H=156):
    """B10 Elian Rook: engineer in a long coat under a back-frame of three relay lights (all lit = pulse tell)."""
    c = Canvas(W, H)
    coat, skin, brass, light = hexc("5a5a42"), hexc("e0c0a0"), hexc("a88a48"), hexc("60e0ff")
    bob = [0, 1, 0, 1][fr]
    base = H - 4
    # back frame and relays
    cap(c, 40, base - 80 + bob, 30, base - 138 + bob, 3, 3, brass, 10)
    cap(c, 80, base - 80 + bob, 92, base - 138 + bob, 3, 3, brass, 10)
    cap(c, 30, base - 138 + bob, 92, base - 138 + bob, 3, 3, brass, 11)
    for i, (rx, ry) in enumerate(((26, base - 128), (61, base - 146), (96, base - 128))):
        on = fr == 2 or i < [1, 2, 3, 2][fr] - (0 if fr != 3 else 1)
        c.ellipse(rx, ry + bob, 8, 8, hexc("3a3a48"), 12 + i)
        glow(c, rx, ry + bob, 5, 5, light, on)
    cloth(c, base - 96 + bob, base - 6, 44, 76, 32, 92, coat, 15, folds=4)
    for lx, t in ((52, 16), (66, 17)):
        path(c, [(lx, base - 20), (lx + 1, base - 4)], [4, 4], hexc("2a2a30"), t)
    c.poly([(44, base - 112 + bob), (76, base - 112 + bob), (78, base - 90 + bob), (42, base - 90 + bob)], coat, 18)
    c.poly([(56, base - 112 + bob), (64, base - 112 + bob), (62, base - 90 + bob), (58, base - 90 + bob)], hexc("d8d0b8"), 19)
    c.ellipse(60, base - 122 + bob, 9, 10, skin, 20)
    c.poly([(50, base - 126 + bob), (70, base - 132 + bob), (70, base - 124 + bob), (52, base - 120 + bob)], hexc("8a8a8a"), 21)
    glow(c, 65, base - 122 + bob, 2.2, 1.6, hexc("f0d070"))   # lens
    path(c, [(46, base - 108 + bob), (38, base - 88 + bob), (40, base - 70 + bob)], [5, 4, 3], coat, 22)
    hand = (96, base - 96 + bob) if fr != 2 else (100, base - 118 + bob)
    path(c, [(74, base - 108 + bob), (86, base - 100 + bob), hand], [5, 4, 3], shade(coat, 0.06), 23)
    for k in range(3):
        c.line(hand[0], hand[1], hand[0] + 6 + k * 3, hand[1] - 4 - k * 4, light if fr == 2 else shade(light, -0.4), 1, 8)
    return finish(c)


def boss_tidewarden(fr, W=150, H=132):
    """B11 Ash-Tide Warden: shelled river beast; a flood gauge on its back rises one notch per action."""
    c = Canvas(W, H)
    shell, skin, ash, water = hexc("2e5a6a"), hexc("5a8a8a"), hexc("5a5454"), hexc("a0f0ff")
    bob = [0, 1, 0, 1][fr]
    base = H - 4
    for lx, t in ((32, 10), (58, 11), (98, 12), (120, 13)):
        path(c, [(lx, base - 36), (lx - 4, base - 16), (lx, base - 3)], [8, 7, 7], skin, t)
        for k in range(3):
            c.ellipse(lx - 5 + k * 5, base - 1, 2, 1.5, ash, 8)
    c.ellipse(76, base - 50 + bob, 60, 30, shell, 14)
    c.ellipse(72, base - 30 + bob, 54, 10, skin, 15)
    for i in range(7):
        c.ellipse(26 + i * 16, base - 64 + bob + (i % 2) * 6, 8, 7, shade(shell, 0.12), 16 + (i % 2))
    for a in range(5):
        seam(c, 30 + a * 22, base - 76 + bob, 22 + a * 24, base - 34 + bob, shell)
    # flood gauge on the back
    c.rect(66, base - 118 + bob, 80, base - 70 + bob, ash, 18)
    lvl = [2, 3, 5, 3][fr]
    for k in range(6):
        on = k < lvl
        c.rect(69, base - 76 - k * 7 + bob, 77, base - 72 - k * 7 + bob, water if on else hexc("1e2a30"), 9 if on else 8)
    c.rect(64, base - 106 + bob, 82, base - 105 + bob, hexc("ff5040"), 8)   # surge notch
    # head
    path(c, [(126, base - 50 + bob), (140, base - 60 + bob)], [16, 12], skin, 19)
    c.poly([(132, base - 56 + bob), (149, base - 52 + bob), (134, base - 44 + bob)], hexc("e8e0d0"), 20)
    glow(c, 140, base - 66 + bob, 2.5, 2, water)
    if fr == 2:
        for k in range(4):
            puff(c, 100 + k * 10, base - 88 - k * 4, 3, 140)
    return finish(c)


def boss_vessel(fr, W=150, H=164):
    """B12 Crown Vessel: armoured shell under a coercive crown; tether chains, core, three pressure rings (tell)."""
    c = Canvas(W, H)
    plate, dk, gold, core = hexc("6a3a4a"), hexc("2e1a26"), hexc("d0a040"), hexc("ff5a4a")
    bob = [0, 2, -2, 2][fr]
    base = H - 4
    # tether chains to the ground
    for x0, x1 in ((20, 6), (130, 146)):
        for k in range(14):
            t = k / 13
            c.ellipse(x0 + (x1 - x0) * t, base - 88 + t * 86 + bob * (1 - t), 2, 1.4, hexc("8a8a96") if k % 2 else hexc("5a5a66"), 10)
    for lx, t in ((50, 11), (100, 12)):
        path(c, [(lx, base - 50), (lx - 3, base - 22), (lx, base - 4)], [13, 10, 11], dk, t)
        c.poly([(lx - 16, base), (lx + 16, base), (lx + 12, base - 9), (lx - 12, base - 9)], plate, t + 2)
    c.ellipse(75, base - 88 + bob, 50, 44, plate, 15)
    for a in range(6):
        ang = -math.pi / 2 + (a - 2.5) * 0.45
        seam(c, 75 + math.cos(ang) * 16, base - 88 + bob + math.sin(ang) * 16,
             75 + math.cos(ang) * 46, base - 88 + bob + math.sin(ang) * 40, plate)
    for sx, t in ((28, 16), (122, 17)):
        c.ellipse(sx, base - 112 + bob, 18, 14, shade(plate, 0.1), t)
        for k in range(3):
            c.poly([(sx - 10 + k * 8, base - 120 + bob), (sx - 6 + k * 8, base - 134 + bob), (sx - 2 + k * 8, base - 120 + bob)], gold, t + 2)
    # pressure rings (tell: all three lit)
    for i in range(3):
        lit = fr == 2 or (fr == 3 and i < 2)
        r = 22 + i * 7
        for a in range(28):
            ang = a * math.pi / 14
            c.ellipse(75 + math.cos(ang) * r, base - 84 + bob + math.sin(ang) * r * 0.8, 1.1, 1.1,
                      hexc("ff9a60") if lit else hexc("5a2a2a"), 9 if lit else 8)
    glow(c, 75, base - 84 + bob, 13, 15, core if fr != 3 else hexc("ffb0a0"))
    # head under the crown
    c.ellipse(75, base - 132 + bob, 15, 13, dk, 22)
    c.rect(66, base - 134 + bob, 88, base - 131 + bob, hexc("100808"), 8)
    glow(c, 82, base - 133 + bob, 3, 1.5, core)
    c.poly([(56, base - 142 + bob), (62, base - 160 + bob), (68, base - 146 + bob), (75, base - 163 + bob), (82, base - 146 + bob),
            (88, base - 160 + bob), (94, base - 142 + bob)], gold, 23)
    for x in (62, 75, 88):
        glow(c, x, base - 148 + bob, 1.5, 1.5, hexc("80e0ff"))
    return finish(c)


def boss_leviathan(fr, W=156, H=140):
    """B14 Heartless Leviathan: sea serpent coiled from the water with a hollow, beacon-lit chest cavity."""
    c = Canvas(W, H)
    scale_, belly, fin, beacon = hexc("1e3448"), hexc("6a8a8a"), hexc("2a5060"), hexc("80ffff")
    base = H - 4
    pts = []
    for i in range(16):
        t = i / 15
        x = 10 + t * 118
        y = base - 14 - math.sin(t * 5.2 + fr * 0.5) * 12 - t * 70
        pts.append((x, y))
    rs = [8 + 10 * math.sin(min(1, i / 11) * math.pi * 0.9) for i in range(16)]
    for i in range(15):
        cap(c, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], rs[i], rs[i + 1], scale_, 10 + (i // 4))
    for i in range(2, 14, 2):
        c.poly([(pts[i][0] - 5, pts[i][1] - rs[i] + 2), (pts[i][0] + 2, pts[i][1] - rs[i] - 10), (pts[i][0] + 6, pts[i][1] - rs[i] + 2)], fin, 15)
        c.ellipse(pts[i][0] + 2, pts[i][1] + rs[i] * 0.5, rs[i] * 0.55, rs[i] * 0.3, belly, 16)
    # hollow chest cavity with beacon lights
    cx, cy = pts[9]
    c.ellipse(cx, cy + 2, 8, 9, hexc("080e16"), 8)
    for k in range(3):
        glow(c, cx - 3 + k * 3, cy + 6 - k * 4, 1.5, 1.5, beacon, fr == 2 or k <= fr)
    hx, hy = pts[-1][0] + 8, pts[-1][1] - (8 if fr == 2 else 0)
    c.ellipse(hx, hy, 17, 12, scale_, 17)
    c.poly([(hx + 4, hy + 2), (hx + 26, hy + 6), (hx + 6, hy + 12)], hexc("15222e"), 18)
    for k in range(4):
        c.put(hx + 8 + k * 4, hy + 4, hexc("e8e8e0"), 8)
    glow(c, hx + 6, hy - 4, 2.5, 2, beacon)
    for k in range(3):
        c.poly([(hx - 10 + k * 5, hy - 8), (hx - 16 + k * 5, hy - 20), (hx - 6 + k * 5, hy - 10)], fin, 19)
    # water line
    for x in range(0, W, 2):
        yy = base - 4 + int(math.sin(x * 0.2 + fr) * 1.5)
        c.rect(x, yy, x + 1, base, (80, 160, 180, 200) if (x // 2) % 3 else (200, 240, 240, 220), 8)
    return finish(c)


def boss_echo(fr, W=128, H=150):
    """B15 Regent's Echo: a crowned spectral regent before a floating command screen naming the taxed action."""
    c = Canvas(W, H)
    ghost, robe, screen, dk = hexc("9a9aa8"), hexc("4a4a58"), hexc("60ff90"), hexc("1a1a20")
    bob = [0, -2, -1, 1][fr]
    base = H - 4
    # screen
    c.rect(78, base - 124, 124, base - 88, hexc("2e2e38"), 10)
    c.rect(81, base - 121, 121, base - 91, hexc("0e2016") if fr != 2 else hexc("123a22"), 11)
    for k in range(4):
        w = [30, 22, 34, 16][k]
        c.rect(84, base - 117 + k * 7, 84 + w, base - 116 + k * 7, screen if fr == 2 or k == 0 else shade(screen, -0.5), 8)
    cap(c, 100, base - 88, 100, base - 60, 2, 2, hexc("2e2e38"), 12)
    # spectral body tapering into mist
    c.poly([(30, base - 96 + bob), (70, base - 96 + bob), (78, base - 30 + bob), (52, base - 4), (22, base - 30 + bob)], robe, 13)
    for k in range(6):
        c.ellipse(30 + k * 9, base - 10 - (k % 2) * 6, 7, 5, (150, 150, 170, 150), 8)
    c.ellipse(50, base - 98 + bob, 22, 10, hexc("6a2030"), 14)   # mantle
    for x in range(30, 72, 5):
        c.ellipse(x, base - 92 + bob, 2, 2, hexc("e8e0d0"), 15)
    c.ellipse(50, base - 112 + bob, 10, 12, ghost, 16)
    c.rect(44, base - 113 + bob, 58, base - 110 + bob, dk, 8)
    glow(c, 55, base - 112 + bob, 2, 1, screen)
    c.poly([(38, base - 120 + bob), (42, base - 134 + bob), (47, base - 124 + bob), (50, base - 136 + bob), (53, base - 124 + bob),
            (58, base - 134 + bob), (62, base - 120 + bob)], hexc("a88a3a"), 17)
    path(c, [(66, base - 90 + bob), (76, base - 80 + bob), (80, base - 96 + bob) if fr == 2 else (82, base - 70 + bob)], [5, 4, 3], ghost, 18)
    return finish(c)


def boss_cantor(fr, W=132, H=160):
    """B16 Null Cantor: faceless choir-master in black robes; a four-beat ring widens for the silence window."""
    c = Canvas(W, H)
    robe, pale, ring = hexc("2a2438"), hexc("d0c8e0"), hexc("c0a0ff")
    bob = [0, 1, 0, 1][fr]
    base = H - 4
    cloth(c, base - 100 + bob, base, 46, 86, 22, 110, robe, 10, folds=7, sway=[0, 2, 0, -2][fr])
    c.ellipse(66, base - 102 + bob, 24, 12, robe, 11)
    c.poly([(54, base - 100 + bob), (78, base - 100 + bob), (74, base - 40), (58, base - 40)], hexc("4a3a6a"), 12)
    c.ellipse(66, base - 118 + bob, 12, 14, pale, 13)
    c.ellipse(68, base - 112 + bob, 4, 2 if fr != 2 else 5, hexc("140c20"), 8)
    c.poly([(52, base - 124 + bob), (66, base - 140 + bob), (80, base - 124 + bob), (66, base - 130 + bob)], robe, 14)   # cowl
    for sx, t, raise_ in ((40, 15, 0), (92, 16, 1)):
        up = (fr == 2) * 18
        path(c, [(sx + (8 if sx < 60 else -8), base - 98 + bob), (sx, base - 84 - up * raise_ + bob), (sx + (-4 if sx < 60 else 6), base - 70 - up * 2 * raise_ + bob)],
             [6, 5, 3], robe, t)
    # four-beat ring
    rr = [30, 34, 44, 34][fr]
    for i in range(4):
        ang = i * math.pi / 2 + fr * 0.2
        glow(c, 66 + math.cos(ang) * rr, base - 104 + bob + math.sin(ang) * rr * 0.45, 3.5, 3.5, ring, fr == 2 or i <= fr)
    for a in range(40):
        ang = a * math.pi / 20
        c.put(66 + math.cos(ang) * rr, base - 104 + bob + math.sin(ang) * rr * 0.45, shade(ring, -0.3), 8)
    return finish(c)


# ---------------------------------------------------------------- bespoke ordinary enemies (painted with the kit)
def en_wolf(fr, W=76, H=58, p=None):
    """E009 Briar Wolf: lean wolf wrapped in thorned briar; the coordinated bite lowers the head."""
    c = Canvas(W, H)
    fur, dk, belly, briar = p or (hexc("6a5a46"), hexc("3a3028"), hexc("a89478"), hexc("4a6a2a"))
    bob = [0, 1, 0, 1][fr]
    base = H - 3
    crouch = 4 if fr == 2 else 0
    for lx, t, f in ((20, 10, -0.25), (50, 11, -0.25)):
        path(c, [(lx, base - 22 + crouch), (lx + 2, base - 11), (lx - 1, base - 1)], [4, 2.5, 2.5], shade(fur, f), t)
    path(c, [(12, base - 30 + bob), (2, base - 40 + bob), (4, base - 46 + bob)], [4, 5, 3], fur, 12)   # tail
    cap(c, 18, base - 26 + bob + crouch, 50, base - 28 + bob + crouch, 10, 11, fur, 13)
    c.ellipse(36, base - 20 + bob + crouch, 14, 5, belly, 14)
    for lx, t in ((16, 15), (46, 16)):
        path(c, [(lx, base - 22 + crouch), (lx - 3, base - 11), (lx + 1, base - 1)], [5, 3, 3], fur, t)
        c.ellipse(lx + 2, base - 1, 3, 1.5, dk, 8)
    hx, hy = 62, base - 40 + bob + (10 if fr == 2 else 0)
    path(c, [(50, base - 32 + bob + crouch), (hx, hy + 4)], [9, 7], fur, 17)
    c.ellipse(hx, hy, 8, 7, fur, 18)
    path(c, [(hx + 4, hy + 2), (hx + 13, hy + 4)], [4, 2.5], belly, 19)
    c.poly([(hx - 5, hy - 5), (hx - 3, hy - 14), (hx + 1, hy - 5)], dk, 20)
    c.poly([(hx - 1, hy - 5), (hx + 2, hy - 13), (hx + 5, hy - 5)], fur, 21)
    glow(c, hx + 4, hy - 1, 1.3, 1.1, hexc("ffd040"))
    if fr == 2:
        c.line(hx + 7, hy + 6, hx + 12, hy + 7, hexc("f4f0e0"), 1, 8)
    # briar vines with thorns
    for k in range(3):
        pts = [(14 + k * 12, base - 34 + bob + crouch), (22 + k * 12, base - 24 + bob + crouch), (28 + k * 12, base - 36 + bob + crouch)]
        path(c, pts, [1.2, 1.2, 1.2], briar, 22)
        for q in pts:
            c.put(q[0], q[1] - 2, hexc("c8d890"), 8)
    return finish(c)


def en_beetle(fr, W=64, H=50):
    """E002 Clamp Beetle: brass-green carapace and heavy clamp mandibles (shell-up pulls the legs in)."""
    c = Canvas(W, H)
    shell, dk, leg, gold = hexc("4a6a3a"), hexc("243020"), hexc("3a3428"), hexc("c8a040")
    bob = [0, 1, 0, 1][fr]
    base = H - 3
    tuck = 3 if fr == 2 else 0
    for i in range(3):
        lx = 18 + i * 12
        path(c, [(lx, base - 14), (lx - 5 + tuck, base - 8), (lx - 7 + tuck * 2, base)], [2, 1.6, 1.2], shade(leg, -0.2), 10)
    c.ellipse(30, base - 18 + bob, 24, 14, shell, 11)
    seam(c, 12, base - 22 + bob, 50, base - 26 + bob, shell, -0.5)
    for k in range(4):
        c.ellipse(20 + k * 9, base - 26 + bob, 2, 1.2, shade(shell, 0.35), 8)
    c.ellipse(52, base - 16 + bob, 8, 7, dk, 12)
    open_ = 5 if fr == 2 else 1
    path(c, [(56, base - 18 + bob), (64, base - 22 - open_ + bob), (60, base - 28 - open_ + bob)], [2.5, 2, 1.5], gold, 13)
    path(c, [(56, base - 13 + bob), (64, base - 10 + open_ + bob), (60, base - 4 + open_ + bob)], [2.5, 2, 1.5], shade(gold, -0.1), 14)
    glow(c, 55, base - 19 + bob, 1.4, 1.2, hexc("ff5a3a"))
    for i in range(3):
        lx = 22 + i * 12
        path(c, [(lx, base - 10), (lx + 4 - tuck, base - 5), (lx + 3 - tuck, base)], [2, 1.6, 1.2], leg, 15)
    return finish(c)


def en_wisp(fr, W=48, H=60):
    """E003 Quarry Wisp: a lick of quarry fire over a slag core; the charge swells a bolt in front of it."""
    c = Canvas(W, H)
    bob = [0, -2, -1, 1][fr]
    cx, cy = 22, 34 + bob
    flame = [hexc("c0401c"), hexc("f07a2a"), hexc("ffc050"), hexc("fff0b0")]
    for i, (dx, dy, r) in enumerate(((0, 0, 13), (-2, -8, 10), (1, -15, 7), (-1, -21, 4))):
        c.poly([(cx + dx - r, cy + dy), (cx + dx + 1 + math.sin(fr + i) * 2, cy + dy - r * 2.2),
                (cx + dx + r, cy + dy)], flame[min(3, i)], 9)
        c.ellipse(cx + dx, cy + dy, r, r * 0.9, flame[min(3, i)], 9)
    c.ellipse(cx, cy + 4, 7, 6, hexc("3a2a26"), 10)            # slag core
    glow(c, cx + 3, cy + 2, 1.5, 1.5, hexc("fff0b0"))
    glow(c, cx - 2, cy + 2, 1.5, 1.5, hexc("fff0b0"))
    for k in range(4):
        c.ellipse(cx - 8 + k * 5, cy + 16 + (k % 2) * 3, 1.2, 1.2, hexc("f07a2a"), 8)
    if fr == 2:
        glow(c, 40, cy - 6, 6, 6, hexc("ffc050"))
    return finish(c)


def en_moth(fr, W=68, H=56):
    """E007 Ledger Moth: parchment wings ruled like a ledger, ink eye-spots; steals coins."""
    c = Canvas(W, H)
    wing, ink, body = hexc("d8c8a4"), hexc("4a3a2a"), hexc("8a7458")
    flap = [0, 6, -3, 2][fr]
    cx, cy = 34, 28
    for side, t in ((-1, 10), (1, 11)):
        tip = (cx + side * 32, cy - 20 - flap)
        c.poly([(cx, cy - 2), tip, (cx + side * 30, cy + 4), (cx + side * 6, cy + 6)], wing if side < 0 else shade(wing, -0.06), t)
        c.poly([(cx, cy + 2), (cx + side * 22, cy + 8), (cx + side * 18, cy + 20), (cx + side * 4, cy + 10)], shade(wing, -0.12), t + 2)
        for k in range(4):
            y0 = cy - 12 + k * 4 - flap * (0.6 - k * 0.1)
            seam(c, cx + side * 6, y0 + 6, cx + side * (26 - k * 2), y0, wing, -0.35)
        c.ellipse(cx + side * 18, cy - 6 - flap * 0.4, 3.5, 3.5, ink, 8)
        c.ellipse(cx + side * 18, cy - 6 - flap * 0.4, 1.5, 1.5, hexc("c8a040"), 8)
    path(c, [(cx, cy - 8), (cx, cy + 14)], [4, 3], body, 14)
    c.ellipse(cx + 1, cy - 11, 4, 4, body, 15)
    for s in (-1, 1):
        path(c, [(cx + s * 2, cy - 14), (cx + s * 6, cy - 22)], [1, 1], ink, 16)
    glow(c, cx + 3, cy - 12, 1.2, 1.2, hexc("ff5a4a"))
    if fr == 2:
        for k in range(3):
            glow(c, cx + 20 + k * 5, cy + 16 - k * 3, 1.8, 1.8, hexc("f0c848"))
    return finish(c)


def en_mite(fr, W=60, H=44):
    """E010 Root Mite: bark-coloured mite trailing rootlets; its sap sac swells green before Poison (tell)."""
    c = Canvas(W, H)
    body, leg, sap = hexc("6a5a3a"), hexc("3e3222"), hexc("8ae04a")
    bob = [0, 1, 0, 1][fr]
    base = H - 3
    for i in range(4):
        lx = 16 + i * 9
        k = 1 if (fr + i) % 2 else -1
        path(c, [(lx, base - 12), (lx - 8 + k, base - 16), (lx - 10 + k, base)], [1.6, 1.4, 1], leg, 10)
    c.ellipse(26, base - 14 + bob, 18, 12, body, 11)
    for k in range(5):
        c.ellipse(16 + k * 5, base - 22 + bob + (k % 2), 2.5, 1.8, shade(body, 0.25), 12)
    sac = 6 if fr == 2 else 4
    glow(c, 14, base - 12 + bob, sac, sac * 0.8, sap if fr == 2 else shade(sap, -0.35))
    c.ellipse(44, base - 12 + bob, 7, 6, shade(body, -0.2), 13)
    path(c, [(48, base - 10 + bob), (54, base - 6 + bob)], [1.5, 1], leg, 14)
    glow(c, 47, base - 14 + bob, 1.2, 1.2, hexc("e0ff80"))
    for i in range(4):
        lx = 20 + i * 9
        k = -1 if (fr + i) % 2 else 1
        path(c, [(lx, base - 10), (lx + 6 + k, base - 14), (lx + 8 + k, base)], [1.8, 1.5, 1.1], leg, 15)
    for k in range(3):
        path(c, [(8, base - 8 + k * 2), (2, base - 4 + k * 3), (0, base)], [1, 1, 1], hexc("5a4630"), 16)
    return finish(c)


def en_lantern(fr, W=48, H=64):
    """E012 Bog Lantern: a drowned lantern on a hooked reed with a marsh-light face; the lure brightens (tell)."""
    c = Canvas(W, H)
    iron, moss, light = hexc("3e4a4a"), hexc("4a6a3a"), hexc("a0f0d0")
    bob = [0, -2, -1, 1][fr]
    cx = 24
    path(c, [(cx - 12, 4), (cx, 2), (cx + 4, 8 + bob)], [1.5, 1.5, 1.2], hexc("5a4a30"), 10)
    c.poly([(cx - 10, 14 + bob), (cx + 10, 14 + bob), (cx + 13, 44 + bob), (cx - 13, 44 + bob)], iron, 11)
    c.rect(cx - 8, 18 + bob, cx + 8, 40 + bob, hexc("1a2a2a"), 12)
    lit = light if fr != 2 else hexc("f0fff0")
    glow(c, cx, 30 + bob, 7, 9, lit)
    for x in (cx - 3, cx + 3):
        c.ellipse(x, 28 + bob, 1.4, 2, hexc("16302a"), 8)
    c.rect(cx - 2, 34 + bob, cx + 2, 35 + bob, hexc("16302a"), 8)
    c.poly([(cx - 12, 14 + bob), (cx, 6 + bob), (cx + 12, 14 + bob)], shade(iron, 0.1), 13)
    c.rect(cx - 14, 43 + bob, cx + 14, 47 + bob, shade(iron, -0.1), 14)
    for k in range(5):
        path(c, [(cx - 12 + k * 6, 46 + bob), (cx - 13 + k * 6, 52 + bob + (k % 2) * 4)], [1.5, 1], moss, 15)
    for k in range(3):
        c.ellipse(cx - 6 + k * 6, 58 + ((fr + k) % 3), 1, 1, hexc("6a9aaa"), 8)
    return finish(c)


def en_crab(fr, W=76, H=56):
    """E014 Boiler Crab: riveted boiler shell with a pressure valve; vents steam as pressure builds (tell)."""
    c = Canvas(W, H)
    shell, dk, claw = hexc("b85a2a"), hexc("5a2a1a"), hexc("d87a3a")
    bob = [0, 1, 0, 1][fr]
    base = H - 3
    for i in range(3):
        lx = 20 + i * 10
        path(c, [(lx, base - 12), (lx - 8, base - 8), (lx - 10, base)], [2, 1.6, 1.2], dk, 10)
    c.ellipse(34, base - 18 + bob, 24, 14, shell, 11)
    c.rect(14, base - 20 + bob, 54, base - 18 + bob, dk, 8)
    for x in range(16, 54, 6):
        rivet(c, x, base - 25 + bob, shell)
    cap(c, 30, base - 30 + bob, 30, base - 40 + bob, 2.5, 2.5, hexc("7a7a80"), 12)
    glow(c, 30, base - 42 + bob, 3, 2, hexc("ff4a3a") if fr == 2 else hexc("a03020"))
    if fr == 2:
        puff(c, 26, base - 50 + bob, 5)
        puff(c, 20, base - 46 + bob, 3, 150)
    for s, t in ((0, 13), (1, 14)):
        oy = s * 10
        path(c, [(50, base - 16 + oy + bob), (60, base - 24 + oy + bob), (66, base - 30 + oy + bob)], [3, 3, 3], claw, t)
        c.ellipse(68, base - 30 + oy + bob, 6, 5, claw, t + 2)
        c.poly([(68, base - 34 + oy + bob), (76, base - 36 + oy + bob), (72, base - 30 + oy + bob)], shade(claw, 0.1), t + 4)
    glow(c, 52, base - 26 + bob, 1.5, 1.5, hexc("fff4d0"))
    glow(c, 56, base - 24 + bob, 1.5, 1.5, hexc("fff4d0"))
    for i in range(3):
        lx = 24 + i * 10
        path(c, [(lx, base - 10), (lx + 6, base - 6), (lx + 5, base)], [2, 1.6, 1.2], shade(dk, 0.15), 17)
    return finish(c)


def en_hand(fr, W=60, H=70):
    """E016 Furnace Hand: an iron gauntlet risen from slag; raises its fist before the strike (tell)."""
    c = Canvas(W, H)
    iron, slag, fire = hexc("7a6a5a"), hexc("3a2a26"), hexc("ff7a30")
    rise = 12 if fr == 2 else [0, 1, 0, 1][fr]
    base = H - 3
    c.ellipse(28, base - 4, 26, 6, slag, 10)
    for k in range(5):
        glow(c, 10 + k * 9, base - 5 + (k % 2), 2, 1, fire)
    path(c, [(28, base - 6), (28, base - 30 - rise)], [8, 9], iron, 11)
    for y in range(base - 26 - rise, base - 6, 5):
        c.rect(20, y, 36, y, shade(iron, -0.35), 8)
    c.ellipse(28, base - 40 - rise, 13, 11, iron, 12)
    for i in range(4):
        fx = 18 + i * 6
        path(c, [(fx, base - 48 - rise), (fx + 1, base - 58 - rise + (i % 2) * 2), (fx + 3, base - 60 - rise + (i % 2) * 2)] if fr != 2 else
             [(fx, base - 48 - rise), (fx + 2, base - 54 - rise), (fx + 5, base - 50 - rise)], [3, 2.6, 2.2], shade(iron, 0.05 * i), 13 + i)
    path(c, [(40, base - 40 - rise), (48, base - 48 - rise), (50, base - 54 - rise)], [3.5, 3, 2.5], iron, 17)
    glow(c, 28, base - 38 - rise, 3, 3, fire)
    return finish(c)


def en_diver(fr, W=60, H=76):
    """E019 Bell Diver: drowned diver in a brass bell helm, hose trailing; undead light behind the porthole."""
    c = Canvas(W, H)
    suit, brass, dk, light = hexc("3a5a6a"), hexc("b8903e"), hexc("1e2a34"), hexc("a0ffff")
    bob = [0, 1, 0, 1][fr]
    base = H - 3
    for lx, t in ((22, 10), (34, 11)):
        path(c, [(lx, base - 26), (lx - 1, base - 12), (lx, base - 4)], [6, 5, 5], suit, t)
        c.rect(lx - 6, base - 5, lx + 6, base, dk, t + 2)
    c.ellipse(28, base - 36 + bob, 14, 14, suit, 14)
    c.rect(16, base - 30 + bob, 40, base - 27 + bob, brass, 15)
    path(c, [(16, base - 44 + bob), (10, base - 30 + bob), (12, base - 20 + bob)], [5, 4, 4], suit, 16)
    hand = (48, base - 32 + bob) if fr != 2 else (50, base - 54 + bob)
    path(c, [(40, base - 44 + bob), (46, base - 38 + bob), hand], [5, 4, 4], shade(suit, 0.08), 17)
    cap(c, hand[0] - 4, hand[1] + 16, hand[0] + 6, hand[1] - 20, 1.2, 1.2, hexc("8a8a92"), 18)
    c.poly([(hand[0] + 4, hand[1] - 24), (hand[0] + 9, hand[1] - 18), (hand[0] + 5, hand[1] - 18)], hexc("d8d8e0"), 19)
    c.ellipse(28, base - 56 + bob, 13, 13, brass, 20)
    c.ellipse(31, base - 56 + bob, 6, 6, dk, 21)
    glow(c, 32, base - 56 + bob, 4, 4, light if fr != 3 else hexc("e0ffff"))
    for k in range(4):
        rivet(c, 19 + k * 6, base - 45 + bob, brass)
    path(c, [(16, base - 60 + bob), (6, base - 50 + bob), (4, base - 30 + bob), (8, base - 10)], [2, 2, 2, 2], hexc("4a4a44"), 22)
    for k in range(3):
        c.ellipse(40 + k * 3, base - 70 - k * 4 + bob, 1.2, 1.2, hexc("c0f0ff"), 8)
    return finish(c)


def en_leech(fr, W=68, H=40, p=None):
    """E026 Seal Leech: pale segmented leech marked with a violet seal; the sucker opens to strip buffs."""
    c = Canvas(W, H)
    skin, seal, mouth = p or (hexc("c8c0d8"), hexc("8a4ac8"), hexc("5a2040"))
    base = H - 3
    for i in range(7):
        x = 8 + i * 8
        y = base - 9 - math.sin(i * 0.9 + fr * 0.9) * 3
        c.ellipse(x, y, 6 + min(i, 3), 6 + min(i, 3) * 0.6, shade(skin, -0.04 * (i % 2)), 10 + i)
    hx, hy = 62, base - 12 - (4 if fr == 2 else 0)
    c.ellipse(hx - 2, hy, 7, 8, skin, 17)
    c.ellipse(hx + 2, hy, 3, 4 if fr == 2 else 2.5, mouth, 8)
    glow(c, 34, base - 14 - math.sin(3 * 0.9 + fr * 0.9) * 3, 3.5, 3.5, seal)
    return finish(c)


def en_shard(fr, W=52, H=68):
    """E029 Memory Shard: a floating crystal cluster with a remembered scene glinting inside."""
    c = Canvas(W, H)
    cry, glint = hexc("c8b8ec"), hexc("8a4ac8")
    bob = [0, -2, -1, 1][fr]
    cx, cy = 26, 32 + bob
    for i, (dx, h, w) in enumerate(((0, 26, 8), (-10, 16, 6), (10, 18, 6), (-4, 12, 4), (6, 10, 4))):
        c.poly([(cx + dx - w, cy + 8), (cx + dx, cy + 8 - h), (cx + dx + w, cy + 8), (cx + dx, cy + 8 + h * 0.4)],
               shade(cry, -0.08 * i), 10 + i)
        seam(c, cx + dx, cy + 8 - h, cx + dx, cy + 8 + h * 0.4, cry, 0.35)
    glow(c, cx + 1, cy, 3 if fr != 2 else 5, 3 if fr != 2 else 5, glint if fr != 2 else hexc("f0d0ff"))
    for k in range(4):
        c.ellipse(cx - 12 + k * 8, cy + 26 + (k % 2) * 3, 1, 1, cry, 8)
    return finish(c)


def en_lancer(fr, W=80, H=80):
    """E034 Ash Lancer: ash-cloaked lancer; levels the lance for a full charge (tell)."""
    c = Canvas(W, H)
    armor, cloak, lance = hexc("6a2a2a"), hexc("6a6466"), hexc("c8c8d0")
    bob = [0, 1, 0, 1][fr]
    base = H - 3
    cloth(c, base - 50 + bob, base - 6, 20, 34, 8, 40, cloak, 10, folds=3, sway=-2)
    for lx, t in ((26, 11), (36, 12)):
        path(c, [(lx, base - 26), (lx + (4 if fr == 2 else 1), base - 12), (lx + 2, base - 2)], [5, 4, 4], armor, t)
    c.poly([(20, base - 52 + bob), (40, base - 52 + bob), (42, base - 26 + bob), (18, base - 26 + bob)], armor, 13)
    c.rect(18, base - 30 + bob, 42, base - 27 + bob, hexc("c8a86a"), 14)
    c.ellipse(30, base - 60 + bob, 7, 8, armor, 15)
    c.poly([(26, base - 68 + bob), (34, base - 76 + bob), (36, base - 66 + bob)], hexc("c8a86a"), 16)
    c.rect(30, base - 62 + bob, 37, base - 60 + bob, hexc("1a0e10"), 8)
    glow(c, 35, base - 61 + bob, 1.5, 1, hexc("ffb060"))
    if fr == 2:
        cap(c, 10, base - 40 + bob, 76, base - 42 + bob, 1.8, 1.4, lance, 17)
        c.poly([(70, base - 46 + bob), (80, base - 42 + bob), (70, base - 38 + bob)], shade(lance, 0.2), 18)
        path(c, [(40, base - 48 + bob), (46, base - 42 + bob)], [4, 3.5], armor, 19)
    else:
        cap(c, 44, base - 2, 56, base - 74 + bob, 1.8, 1.4, lance, 17)
        c.poly([(53, base - 72 + bob), (57, base - 80 + bob), (60, base - 72 + bob)], shade(lance, 0.2), 18)
        path(c, [(40, base - 48 + bob), (48, base - 44 + bob), (50, base - 40 + bob)], [4, 3.5, 3], armor, 19)
    c.poly([(16, base - 54 + bob), (4, base - 46 + bob), (10, base - 34 + bob), (20, base - 40 + bob)], shade(cloak, 0.1), 20)
    return finish(c)


EN_FN = {"E002": en_beetle, "E003": en_wisp, "E007": en_moth, "E009": en_wolf, "E010": en_mite, "E012": en_lantern,
         "E014": en_crab, "E016": en_hand, "E019": en_diver, "E026": en_leech, "E029": en_shard, "E034": en_lancer}


BOSS_FN = {"B02": boss_bailiff, "B03": boss_stag, "B04": boss_colossus, "B05": boss_custodian, "B06": None,
           "B07": boss_adjudicator, "B08": boss_choir, "B09": boss_voss, "B10": boss_rook, "B11": boss_tidewarden,
           "B12": boss_vessel, "B13": None, "B14": boss_leviathan, "B15": boss_echo, "B16": boss_cantor}


def boss_generic(bid, fr):
    fn = BOSS_FN.get(bid)
    if fn is not None:
        return fn(fr)
    return boss_generic_old(bid, fr)



def boss_generic_old(bid, fr):
    rnd = random.Random(bid)
    W, H = {"B12": (128, 160), "B14": (128, 128), "B04": (112, 144), "B06": (128, 128)}.get(bid, (112, 128))
    c = Canvas(W, H)
    P = BOSS_PAL[bid]
    bob = [0, 2, -4, 3][fr]
    cx, base = W * 0.5, H - 6
    kind = BOSS_KIND[bid]
    if kind == "humanoid":
        # tall armored figure (Voss, Bailiff, Adjudicator, Rook, Echo)
        c.poly([(cx - 20, base - 70 + bob), (cx + 20, base - 70 + bob), (cx + 28, base), (cx - 28, base)], P[0], 1)
        c.rect(cx - 16, base - 96 + bob, cx + 16, base - 70 + bob, P[1], 2)
        c.ellipse(cx, base - 106 + bob, 11, 12, P[2], 3)
        c.ellipse(cx + 5, base - 107 + bob, 2, 2, P[3], 4)
        arm_y = base - 92 + bob - (18 if fr == 2 else 0)
        c.line(cx + 16, base - 90 + bob, cx + 40, arm_y, P[1], 6, 5)
        c.line(cx + 40, arm_y, cx + 52, arm_y - 20, P[3], 3, 6)
        c.line(cx - 16, base - 90 + bob, cx - 26, base - 60 + bob, P[1], 6, 5)
        if bid in ("B02", "B15"):
            c.rect(cx - 12, base - 88 + bob, cx + 12, base - 74 + bob, (230, 220, 190, 255), 7)
            c.line(cx - 8, base - 84 + bob, cx + 8, base - 84 + bob, (80, 40, 30, 255), 1, 7)
            c.line(cx - 8, base - 80 + bob, cx + 4, base - 80 + bob, (80, 40, 30, 255), 1, 7)
        if bid == "B07":
            c.ellipse(cx, base - 124 + bob, 16, 4, P[3], 8)
        if bid == "B10":
            for i, a in enumerate((-0.6, 0.0, 0.6)):
                on = fr == 2 or i <= fr
                c.ellipse(cx + math.sin(a) * 34, base - 126 + math.cos(a) * 6, 5, 5, P[3] if on else shade(P[3], -0.5), 9)
        if bid == "B09":
            c.poly([(cx - 22, base - 94 + bob), (cx - 30, base - 20), (cx - 18, base - 20)], P[4], 1)
    elif kind == "beast":
        # large quadruped / stag / roc-like
        c.ellipse(cx - 6, base - 40 + bob, 42, 24, P[0], 1)
        for lx in (cx - 34, cx - 18, cx + 10, cx + 26):
            c.line(lx, base - 30, lx + (3 if fr == 1 else 0), base, P[1], 7, 2)
        hx, hy = cx + 40, base - 66 + bob - (8 if fr == 2 else 0)
        c.line(cx + 26, base - 50 + bob, hx, hy, P[0], 12, 3)
        c.ellipse(hx + 4, hy - 4, 12, 9, P[0], 4)
        c.ellipse(hx + 14, hy - 1, 6, 5, P[2], 4)
        c.ellipse(hx + 6, hy - 8, 2, 2, P[3], 5)
        if bid == "B03":
            for side in (-1, 1):
                x0 = hx + side * 2
                c.line(x0, hy - 12, x0 - 12 * side, hy - 36, P[2], 3, 6)
                c.line(x0 - 6 * side, hy - 24, x0 - 18 * side, hy - 28, P[2], 2, 6)
                c.line(x0 - 9 * side, hy - 31, x0 + 2 * side, hy - 42, P[2], 2, 6)
                if fr == 2:
                    for k in range(4):
                        c.ellipse(x0 - (12 - k * 3) * side, hy - 36 + k * 3, 2.5, 2.5, P[3], 7)
        if bid == "B11":
            for i in range(5):
                c.ellipse(cx - 30 + i * 14, base - 58 + bob + (i % 2) * 4, 6, 8, P[2], 6)
            c.ellipse(cx - 6, base - 40 + bob, 10, 10, P[3] if fr != 3 else shade(P[3], 0.3), 7)
    elif kind == "bird":
        flap = [0, 14, -10, 6][fr]
        c.ellipse(cx, base - 56, 18, 26, P[0], 1)
        c.poly([(cx - 8, base - 70), (cx - 60, base - 100 - flap), (cx - 56, base - 50), (cx - 10, base - 40)], P[1], 2)
        c.poly([(cx + 8, base - 70), (cx + 60, base - 100 - flap), (cx + 56, base - 50), (cx + 10, base - 40)], shade(P[1], 0.1), 2)
        c.ellipse(cx + 8, base - 86, 10, 9, P[2], 3)
        c.poly([(cx + 16, base - 88), (cx + 30, base - 84), (cx + 16, base - 80)], P[3], 4)
        c.ellipse(cx + 11, base - 89, 2, 2, (20, 20, 20, 255), 5)
        c.line(cx - 4, base - 30, cx - 20, base, (140, 140, 150, 255), 2, 6)  # tether chain
        for i in range(6):
            c.ellipse(cx - 6 - i * 3, base - 28 + i * 5, 2, 2, (160, 160, 170, 255), 6)
    elif kind == "machine":
        # colossus / vessel / custodian (towering constructs)
        c.rect(cx - 34, base - 90 + bob, cx + 34, base - 30 + bob, P[0], 1)
        c.rect(cx - 22, base - 116 + bob, cx + 22, base - 90 + bob, P[1], 2)
        c.rect(cx - 30, base - 30, cx - 12, base, P[1], 3)
        c.rect(cx + 12, base - 30, cx + 30, base, P[1], 3)
        c.rect(cx - 48, base - 86 + bob - (10 if fr == 2 else 0), cx - 34, base - 40 + bob, P[2], 4)
        c.rect(cx + 34, base - 86 + bob - (12 if fr == 2 else 0), cx + 48, base - 40 + bob, P[2], 4)
        c.ellipse(cx, base - 104 + bob, 6, 4, P[3], 5)
        for i in range(3):
            lit = fr == 2 or (fr == 3 and i < 2)
            c.ellipse(cx - 18 + i * 18, base - 60 + bob, 5, 5, P[3] if lit else shade(P[3], -0.55), 6)
        if bid == "B05":
            for i in range(3):
                c.poly([(cx - 30 + i * 30, base - 126), (cx - 24 + i * 30, base - 126), (cx - 20 + i * 30, base - 116), (cx - 34 + i * 30, base - 116)], (200, 160, 70, 255), 7)
        if bid == "B12":
            c.poly([(cx - 30, base - 118 + bob), (cx - 20, base - 140 + bob), (cx - 8, base - 122 + bob), (cx, base - 146 + bob), (cx + 8, base - 122 + bob), (cx + 20, base - 140 + bob), (cx + 30, base - 118 + bob)], (220, 180, 70, 255), 7)
            c.ellipse(cx, base - 64 + bob, 12, 14, (230, 70, 60, 255) if fr != 3 else (255, 150, 120, 255), 8)
    elif kind == "choir":
        for i, off in enumerate((-30, 0, 30)):
            y = base - 70 + math.sin(i + fr) * 4
            c.poly([(cx + off - 12, y - 16), (cx + off + 12, y - 16), (cx + off + 14, y + 40), (cx + off - 14, y + 40)], P[0], 1)
            c.ellipse(cx + off, y - 24, 10, 12, P[2], 2)
            lit = fr == 2 and i == 1
            c.ellipse(cx + off + 3, y - 26, 2, 3, P[3] if lit else (30, 20, 40, 255), 3)
            c.ellipse(cx + off - 3, y - 26, 2, 3, P[3] if lit else (30, 20, 40, 255), 3)
            c.ellipse(cx + off, y - 18, 3, 2 if fr != 2 else 4, (30, 20, 40, 255), 3)
    elif kind == "serpent":
        for i in range(14):
            x = 10 + i * 8
            y = base - 20 - math.sin(i * 0.6 + fr * 0.8) * 16 - i * 3
            c.ellipse(x, y, 10 + i * 0.6, 9 + i * 0.5, P[0] if i % 2 else shade(P[0], 0.1), 1)
        hx, hy = 118, base - 76 - (10 if fr == 2 else 0)
        c.ellipse(hx - 6, hy, 16, 12, P[1], 2)
        c.ellipse(hx, hy - 4, 3, 3, P[3], 3)
        c.poly([(hx - 2, hy + 6), (hx + 10, hy + 14), (hx - 12, hy + 12)], (240, 240, 230, 255), 4)
    elif kind == "lantern":
        c.ellipse(cx, base - 50 + bob, 34, 36, P[0], 1)
        c.ellipse(cx + 10, base - 56 + bob, 18, 12 if fr != 2 else 18, (20, 10, 20, 255), 2)
        for i in range(4):
            c.poly([(cx + 2 + i * 6, base - 62 + bob), (cx + 5 + i * 6, base - 54 + bob), (cx + 8 + i * 6, base - 62 + bob)], (240, 240, 230, 255), 3)
        c.ellipse(cx - 10, base - 74 + bob, 4, 4, P[3], 4)
        c.line(cx - 30, base - 20, cx - 40, base, P[1], 5, 5)
        c.line(cx + 30, base - 20, cx + 40, base, P[1], 5, 5)
    elif kind == "cantor":
        c.poly([(cx - 26, base - 90), (cx + 26, base - 90), (cx + 36, base), (cx - 36, base)], P[0], 1)
        c.ellipse(cx, base - 104 + bob, 14, 16, P[2], 2)
        ring = [16, 20, 26, 20][fr]
        for a in range(16):
            ang = a * math.pi / 8
            c.put(cx + math.cos(ang) * ring * 2, base - 104 + math.sin(ang) * ring, P[3], 3)
        c.ellipse(cx, base - 100 + bob, 5, 2 if fr != 2 else 6, (20, 10, 30, 255), 4)
    return finish(c)


BOSS_KIND = {"B02": "humanoid", "B03": "beast", "B04": "machine", "B05": "machine", "B06": "bird", "B07": "humanoid",
             "B08": "choir", "B09": "humanoid", "B10": "humanoid", "B11": "beast", "B12": "machine", "B13": "lantern",
             "B14": "serpent", "B15": "humanoid", "B16": "cantor"}
BOSS_PAL = {
    "B02": pal("a8883a", "6a5a3a", "d8c8a0", "e0c060", "3a2a1a"), "B03": pal("5a4a2e", "3a2e1e", "c8b890", "f0a0c0"),
    "B04": pal("8a4a2a", "5a3020", "a0603a", "ff8a3a"), "B05": pal("5a8a7a", "3a6a5a", "c8b890", "80f0f0"),
    "B06": pal("7a7a86", "a8a8b0", "c8c8d0", "e0a040"), "B07": pal("e8e8ec", "b8b8c0", "f4f4f8", "8a6ac8"),
    "B08": pal("e8e0f0", "b8a8d0", "f0e8f8", "ff80c0"), "B09": pal("8a1a1a", "4a4a54", "e8c8b0", "d0a040", "5a0e14"),
    "B10": pal("6a6a4a", "4a4a3a", "e0c0a0", "60e0ff"), "B11": pal("2e5a6a", "1e3a48", "5a9aaa", "a0f0ff"),
    "B12": pal("6a3a4a", "3a2030", "a8883a", "ff5a4a"), "B13": pal("2a3040", "1a1e28", "6a7a90", "ffc060"),
    "B14": pal("1a2a3a", "2a4050", "4a6a7a", "80ffff"), "B15": pal("4a4a58", "2e2e38", "9a9aa8", "60ff90", "1a1a20"),
    "B16": pal("2a2438", "1a1628", "d0c8e0", "c0a0ff"),
}


def part_sprite(kind, fr):
    c = Canvas(32, 32)
    if kind == "valve":
        c.rect(12, 14, 20, 30, (90, 80, 70, 255), 1)
        c.ellipse(16, 12, 9, 9, (200, 60, 40, 255) if fr != 2 else (255, 120, 80, 255), 2)
        c.line(8, 12, 24, 12, (230, 220, 200, 255), 2, 3)
        c.line(16, 4, 16, 20, (230, 220, 200, 255), 2, 3)
    elif kind == "root":
        c.line(4, 30, 14, 8, (110, 80, 40, 255), 4, 1)
        c.line(14, 8, 26, 2, (110, 80, 40, 255), 3, 1)
        c.line(10, 20, 26, 24, (90, 66, 34, 255), 3, 1)
        c.ellipse(24, 3, 3, 3, (220, 120, 170, 255), 2)
    elif kind == "relay":
        c.rect(12, 12, 20, 30, (70, 70, 80, 255), 1)
        c.ellipse(16, 10, 7, 7, (90, 220, 255, 255) if fr != 2 else (200, 255, 255, 255), 2)
    elif kind == "lantern":
        c.rect(10, 8, 22, 26, (40, 40, 50, 255), 1)
        c.rect(12, 10, 20, 24, (30, 30, 60, 255) if fr != 2 else (255, 190, 80, 255), 2)
        c.line(16, 2, 16, 8, (90, 90, 100, 255), 1, 3)
    return finish(c)


def strip(frames):
    w, h = frames[0].w, frames[0].h
    img = Image.new("RGBA", (w * 4, h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        img.paste(f.image(), (i * w, 0))
    return img


def hurt_tint(c):
    # frame 3: pale flash silhouette
    for y in range(c.h):
        for x in range(c.w):
            px = c.px[y][x]
            if px is not None and px != OUT:
                c.px[y][x] = mix(px, (255, 240, 230, 255), 0.35)
    return c


def build(save):
    for eid, (shape, sz, p) in EN.items():
        if eid in EN_FN:
            frames = [EN_FN[eid](i) for i in range(3)] + [hurt_tint(EN_FN[eid](3))]
        else:
            fam = FAMILY[shape]
            frames = [fam(sz, p, 0), fam(sz, p, 1), fam(sz, p, 2), hurt_tint(fam(sz, p, 3))]
        fw, fh = frames[0].w, frames[0].h
        save(strip(frames), f"sprites/enemies/{eid}.png", "enemy_sprite", f"{fw}x{fh} x4 (idle,idle,tell,hurt)", shape)
    frames = [boss_extractor(i) for i in range(3)] + [hurt_tint(boss_extractor(3))]
    save(strip(frames), "sprites/enemies/B01.png", "boss_sprite", "128x144 x4", "extractor")
    for bid in BOSS_KIND:
        frames = [boss_generic(bid, i) for i in range(3)] + [hurt_tint(boss_generic(bid, 3))]
        save(strip(frames), f"sprites/enemies/{bid}.png", "boss_sprite", f"{frames[0].w}x{frames[0].h} x4", BOSS_KIND[bid])
    parts = {"B01_P1": "valve", "B03_P1": "root", "B10_P1": "relay", "B10_P2": "relay", "B11_P1": "valve", "B13_P1": "lantern"}
    for pid, k in parts.items():
        frames = [part_sprite(k, i) for i in range(3)] + [hurt_tint(part_sprite(k, 3))]
        save(strip(frames), f"sprites/enemies/{pid}.png", "part_sprite", "32x32 x4", k)


# =================================================================================================================
# Library-derived battlers (owner's licensed 2D library, see pix.LICENSES). Output -> game/assets/ext/ (git-ignored)
# in exactly the generated layout: 4 frames side by side (idle A, idle B, tell/charge, hurt), facing right.
# Every source goes through one unifying pass so packs by different artists read as one FF6-like cast:
# baked drop-shadows removed, integer nearest scaling only (x2 up, or a palette-preserving 2:1 reduction for
# oversized sprites), hard black outlines replaced by a selective dark edge, a region colour grade, and an
# upper-left light falloff with a warm rim on lit edges.
# =================================================================================================================
TR = "ansimuz/Legacy Collection/Assets/TinyRPG/Characters/Battle Sprites/"
GV = "ansimuz/Legacy Collection/Assets/Gothicvania/Characters/"
WP = "ansimuz/Legacy Collection/Assets/Warped/Characters/"
HF = "haydeos/Factory Monster Pack 1/"
LM = "characters/"

REGION = {"D01": "quarry", "D02": "underways", "D03": "grove", "D04": "furnace", "D05": "archive", "D06": "sky",
          "D07": "whitebone", "D08": "vault", "D09": "conduit", "D10": "crown"}
GRADE = {  # shadow, mid, light (gradient map the sprite is pulled toward)
    "quarry": ("2a1e2e", "8a6a54", "f4dcac"), "underways": ("141c30", "4a6070", "d0e0d4"),
    "grove": ("162a22", "5a7a42", "ece4a4"), "furnace": ("2c1018", "9a4c2e", "ffd488"),
    "archive": ("10283a", "4a8a8a", "eaf2dc"), "sky": ("202c5c", "7890ba", "fff4e0"),
    "whitebone": ("2c2c48", "a8a8ba", "fffaf0"), "vault": ("2a1a40", "8a72aa", "f8e8d4"),
    "conduit": ("1c0e22", "6a3a4c", "ffb4a0"), "crown": ("1c0e2c", "6c4a6c", "ffe2a4"),
}


def _region(eid):
    n = int(eid[1:]) if eid[0] == "E" else 0
    return REGION.get("D%02d" % ((n - 1) // 4 + 1), "quarry")


# id: source spec. kind "files": [idleA, idleB, tell, hurt] file paths (None = derive from idle A);
# kind "sheet": {"idle": (path, frameA, frameB), "tell": (path, i), "hurt": (path, i)} with frames split on
# empty columns; kind "still": one image, frames synthesised. scale: 2 = x2 nearest, -2 = 2:1 reduction.
# hue: degrees, k: grade strength, flip: mirror so the enemy faces right (toward the party).
LIB_EN = {
    "E001": dict(kind="still", src=HF + "Trash_Rat.png", scale=1, k=0.25, flip=False),
    "E004": dict(flip=True, kind="files", src=[GV + "Hell-Hound-Files/Sprites/Idle/frame1.png", GV + "Hell-Hound-Files/Sprites/Idle/frame6.png",
                                    GV + "Hell-Hound-Files/Sprites/Jump/frame2.png", None], scale=2, k=0.35, hue=20),
    "E005": dict(kind="files", src=[TR + "Living Pack 1/Slime/Sprites/slime1.png", TR + "Living Pack 1/Slime/Sprites/slime3.png",
                                    TR + "Living Pack 1/Slime/Sprites/slime4.png", None], scale=1, k=0.3, hue=60),
    "E006": dict(kind="still", src=TR + "Mechanic/Drone.png", scale=1, k=0.3, hue=0),
    "E008": dict(kind="still", src=TR + "Mechanic/Metal-Slug.png", scale=1, k=0.35, hue=150),
    "E011": dict(kind="files", src=[TR + "Monster Pack Files/Sprites/Treant/Treant1.png", TR + "Monster Pack Files/Sprites/Treant/Treant2.png",
                                    TR + "Monster Pack Files/Sprites/Treant/Treant4.png", None], scale=1, k=0.2),
    "E013": dict(kind="still", src=HF + "Scrap_Bandit.png", scale=-2, k=0.3),
    "E015": dict(kind="sheet", idle=(LM + "Imp/Sprites/no_outline/IDLE.png", 0, 3), tell=(LM + "Imp/Sprites/no_outline/ATTACK.png", 2),
                 hurt=(LM + "Imp/Sprites/no_outline/HURT.png", 0), scale=2, k=0.55, sat=0.35),
    "E017": dict(kind="files", src=[TR + "Living Pack 1/Wizard/Sprites/wizard1.png", TR + "Living Pack 1/Wizard/Sprites/wizard3.png",
                                    TR + "Living Pack 1/Wizard/Sprites/wizard5.png", None], scale=1, k=0.35, hue=-90),
    "E018": dict(kind="still", src=HF + "Rust_Slug.png", scale=-2, k=0.6, hue=150, sat=0.6, region="whitebone"),
    "E020": dict(kind="still", src=TR + "Mechanic/observer.png", scale=1, k=0.35, hue=40),
    "E021": dict(kind="still", src=TR + "Mechanic/steel-eagle.png", scale=1, k=0.3, hue=160),
    "E022": dict(kind="still", src=HF + "Volt_Viper.png", scale=-2, k=0.35),
    "E023": dict(kind="sheet", idle=(LM + "Stone Golem/new version/Sprites/without_outline/IDLE.png", 0, 6),
                 tell=(LM + "Stone Golem/new version/Sprites/without_outline/ATTACK.png", 3),
                 hurt=(LM + "Stone Golem/new version/Sprites/without_outline/HURT.png", 0), scale=1, k=0.3),
    "E024": dict(kind="files", src=[WP + "alien-flying-enemy/sprites/alien-enemy-flying1.png", WP + "alien-flying-enemy/sprites/alien-enemy-flying4.png",
                                    WP + "alien-flying-enemy/sprites/alien-enemy-flying6.png", None], scale=1, k=0.4, hue=200),
    "E025": dict(flip=True, kind="sheet", idle=(LM + "Huge Knight/Sprites/without_outline/IDLE.png", 0, 4),
                 tell=(LM + "Huge Knight/Sprites/without_outline/ATTACK.png", 2), hurt=(LM + "Huge Knight/Sprites/without_outline/HURT.png", 0),
                 scale=1, k=0.45, sat=0.5),
    "E027": dict(kind="files", src=[GV + "wolf-runing-cycle/Sprites/wolf-runing-cycle-skin1.png", GV + "wolf-runing-cycle/Sprites/wolf-runing-cycle-skin3.png",
                                    GV + "wolf-runing-cycle/Sprites/wolf-runing-cycle-skin4.png", None], scale=2, k=0.4),
    "E028": dict(kind="sheet", idle=(LM + "Cerberus/New Version/Sprites/no_outline/IDLE.png", 0, 7),
                 tell=(LM + "Cerberus/New Version/Sprites/no_outline/ATTACK.png", 3), hurt=(LM + "Cerberus/New Version/Sprites/no_outline/HURT.png", 0),
                 scale=1, k=0.4),
    "E030": dict(kind="sheet", idle=(LM + "Witch/Sprite/IDLE.png", 0, 4), tell=(LM + "Witch/Sprite/ATTACK.png", 3),
                 hurt=(LM + "Witch/Sprite/HURT.png", 0), scale=1, k=0.5, sat=0.5),
    "E031": dict(kind="still", src=TR + "Mechanic/Sentinel.png", scale=1, k=0.45, hue=-30),
    "E032": dict(flip=True, kind="sheet", idle=(LM + "Headless Horseman/Sprites/without_outline/IDLE.png", 0, 2),
                 tell=(LM + "Headless Horseman/Sprites/without_outline/ATTACK.png", 2),
                 hurt=(LM + "Headless Horseman/Sprites/without_outline/HURT.png", 0), scale=1, k=0.35),
    "E033": dict(kind="still", src=HF + "Magnet_Maw.png", scale=-2, k=0.35, hue=-150),
    "E035": dict(kind="files", src=[GV + "Fire-Skull-Files/Sprites/Fire/frame1.png", GV + "Fire-Skull-Files/Sprites/Fire/frame4.png",
                                    GV + "Fire-Skull-Files/Sprites/Fire/frame7.png", None], scale=1, k=0.2),
    "E036": dict(kind="still", src=HF + "Defective_Turret.png", scale=-2, k=0.45),
    "E037": dict(flip=True, kind="sheet", idle=(LM + "Gargoyle/New Version/Sprites/no_outline/IDLE.png", 0, 3),
                 tell=(LM + "Gargoyle/New Version/Sprites/no_outline/ATTACK 1.png", 3),
                 hurt=(LM + "Gargoyle/New Version/Sprites/no_outline/HURT.png", 0), scale=1, k=0.55, sat=0.3),
    "E038": dict(kind="still", src=HF + "Boiler_Golem.png", scale=-2, k=0.3),
    "E039": dict(kind="files", src=[TR + "Monster Pack Files/Sprites/Witch/witch1.png", TR + "Monster Pack Files/Sprites/Witch/witch3.png",
                                    TR + "Monster Pack Files/Sprites/Witch/witch5.png", None], scale=1, k=0.3),
    "E040": dict(kind="files", src=[TR + "Monster Pack Files/Sprites/Demon/demon1.png", TR + "Monster Pack Files/Sprites/Demon/demon3.png",
                                    TR + "Monster Pack Files/Sprites/Demon/demon5.png", None], scale=1, k=0.4),
    "B06": dict(kind="sheet", idle=(LM + "Gryphon/NEW VERSION/Sprites/without_outline/IDLE.png", 0, 2),
                tell=(LM + "Gryphon/NEW VERSION/Sprites/without_outline/ATTACK 1.png", 2),
                hurt=(LM + "Gryphon/NEW VERSION/Sprites/without_outline/HURT.png", 0), scale=2, k=0.3, region="sky", chain=True),
    "B13": dict(kind="files", src=[GV + "demon-Files/Sprites/Idle/idle1.png", GV + "demon-Files/Sprites/Idle/idle2.png",
                                   GV + "demon-Files/Sprites/DemonAttack/frame8.png", None], scale=1, k=0.35, region="winter"),
}
GRADE["winter"] = ("1a2448", "6a88b0", "f4fbff")


def _np():
    import numpy as np
    return np


def _cells(path):
    """Split a horizontal strip into frame cells. Cell width = sheet width / number of content runs when that
    divides evenly (keeps in-cell alignment), else each run is cropped on its own."""
    from art.pix import lib_img
    im = lib_img(path)
    a = _np().array(im)[:, :, 3] > 0
    cols = a.any(0)
    runs, s = [], None
    for x, c in enumerate(list(cols) + [False]):
        if c and s is None:
            s = x
        elif not c and s is not None:
            if runs and s - runs[-1][1] <= 3:
                runs[-1] = (runs[-1][0], x)
            else:
                runs.append((s, x))
            s = None
    W = im.width
    maxrun = max(r1 - r0 for r0, r1 in runs)
    for w in range(max(16, maxrun), W + 1):
        if W % w:
            continue
        cells = [(i * w, (i + 1) * w) for i in range(W // w)]
        if any(not cols[c0:c1].any() for c0, c1 in cells):
            continue
        if any(r0 // w != (r1 - 1) // w for r0, r1 in runs):
            continue
        return [im.crop((c0, 0, c1, im.height)) for c0, c1 in cells]
    return [im.crop((r0, 0, r1, im.height)) for r0, r1 in runs]


def _strip_shadow(im):
    """Remove an opaque black drop-shadow ellipse baked under a sprite (TinyRPG battlers)."""
    np = _np()
    a = np.array(im).copy()
    op = a[:, :, 3] > 0
    blk = op & (a[:, :, :3].max(2) < 12)
    if not op.any():
        return im
    rows = np.nonzero(op.any(1))[0]
    bot = rows.max()
    for x in range(a.shape[1]):
        col = np.nonzero(op[:, x])[0]
        if not len(col) or col.max() < bot - 16:
            continue
        y = col.max()
        while y >= 0 and blk[y, x] and y > bot - 16:
            a[y, x, 3] = 0
            y -= 1
    return Image.fromarray(a)


def _reduce2(im):
    """2:1 reduction that keeps the source palette: each 2x2 block becomes its member closest to the block mean
    (transparent when fewer than two members are opaque). No smoothing, no new colours."""
    np = _np()
    a = np.array(im).astype(int)
    H, W = a.shape[0] // 2 * 2, a.shape[1] // 2 * 2
    out = np.zeros((H // 2, W // 2, 4), dtype=np.uint8)
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            blk = a[y:y + 2, x:x + 2].reshape(4, 4)
            opq = blk[blk[:, 3] > 0]
            if len(opq) < 2:
                continue
            m = opq[:, :3].mean(0)
            best = opq[np.argmin(((opq[:, :3] - m) ** 2).sum(1))]
            out[y // 2, x // 2] = best
    return Image.fromarray(out)


def _hue(rgb, deg, sat):
    import colorsys
    r, g, b = [v / 255 for v in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + deg / 360.0) % 1.0
    s = min(1.0, s * sat)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))


def unify(im, region, k=0.3, hue=0, sat=1.0):
    """Colour grade + selective edge + upper-left light on an RGBA sprite (any source)."""
    np = _np()
    a = np.array(im).astype(float)
    op = a[:, :, 3] > 40
    a[:, :, 3] = np.where(op, 255, 0)
    H, W = op.shape
    g = [hexc(v) for v in GRADE[region]]
    ys, xs = np.nonzero(op)
    if len(ys) == 0:
        return im
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    out = a.copy()
    for y, x in zip(ys, xs):
        rgb = tuple(int(v) for v in a[y, x, :3])
        if hue or sat != 1.0:
            rgb = _hue(rgb, hue, sat)
        lum = (0.3 * rgb[0] + 0.59 * rgb[1] + 0.11 * rgb[2]) / 255
        gm = mix(g[0], g[1], lum / 0.5) if lum < 0.5 else mix(g[1], g[2], (lum - 0.5) / 0.5)
        c = mix(rgb + (255,), gm, k)
        # upper-left light falloff (FF6 battlers are lit from the upper left)
        fx = (x - x0) / max(1, x1 - x0)
        fy = (y - y0) / max(1, y1 - y0)
        f = 0.10 - 0.16 * (fx * 0.45 + fy * 0.55)
        c = shade(c, f) if abs(f) > 0.01 else c
        out[y, x, :3] = c[:3]
    # selective edge: pure/near-black outline pixels become a coloured dark taken from the inside neighbour;
    # lower/right silhouette edge darkened, upper/left edge gets a warm rim
    lumA = out[:, :, :3] @ np.array([0.3, 0.59, 0.11])
    res = out.copy()
    for y, x in zip(ys, xs):
        def isin(dx, dy):
            nx, ny = x + dx, y + dy
            return 0 <= nx < W and 0 <= ny < H and op[ny, nx]
        edge = not (isin(1, 0) and isin(-1, 0) and isin(0, 1) and isin(0, -1))
        if lumA[y, x] < 34:
            # find the brightest-ish inner neighbour to tint the dark line with
            best = None
            for dx, dy in ((-1, -1), (0, -1), (-1, 0), (1, 0), (0, 1), (1, 1), (-1, 1), (1, -1)):
                if isin(dx, dy) and lumA[y + dy, x + dx] >= 34:
                    best = out[y + dy, x + dx, :3]
                    break
            if best is not None:
                lr = not isin(1, 0) or not isin(0, 1)
                d = shade(tuple(int(v) for v in best) + (255,), -0.72 if (edge and lr) else -0.6)
                res[y, x, :3] = d[:3]
            elif not edge:
                res[y, x, :3] = hexc(GRADE[region][0])[:3]
        elif edge and (not isin(-1, 0) or not isin(0, -1)) and isin(1, 0) and isin(0, 1):
            res[y, x, :3] = shade(tuple(int(v) for v in out[y, x, :3]) + (255,), 0.22)[:3]
    return Image.fromarray(res.clip(0, 255).astype(np.uint8))


def _synth_frames(base):
    """idle A / idle B (1px breathing squash) / tell (raised 3px, brighter) for single-image sources."""
    w, h = base.size
    b = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sq = base.resize((w, h - 1), Image.NEAREST) if h > 20 else base  # drops one row: nearest, integer-exact rows
    b.paste(sq, (0, 1), sq)
    t = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lit = base.point(lambda v: min(255, int(v * 1.12)))
    lit.putalpha(base.split()[3])
    t.paste(lit, (0, -3), lit)
    return [base, b, t]


def _hurt(im):
    np = _np()
    a = np.array(im).astype(float)
    m = a[:, :, 3] > 0
    a[m, :3] = a[m, :3] * 0.62 + np.array([255, 240, 230]) * 0.38
    return Image.fromarray(a.astype(np.uint8))


def _scale(im, s):
    if s == 2:
        return im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    if s == -2:
        return _reduce2(im)
    return im


def lib_frames(eid, spec):
    from art.pix import lib_img
    region = spec.get("region") or _region(eid)
    srcs = []
    if spec["kind"] == "still":
        raw = [lib_img(spec["src"])]
        srcs = [spec["src"]]
    elif spec["kind"] == "files":
        raw = [lib_img(p) if p else None for p in spec["src"]]
        srcs = [p for p in spec["src"] if p]
    else:
        ia = _cells(spec["idle"][0])
        raw = [ia[spec["idle"][1] % len(ia)], ia[spec["idle"][2] % len(ia)]]
        tc = _cells(spec["tell"][0])
        raw.append(tc[spec["tell"][1] % len(tc)])
        hc = _cells(spec["hurt"][0])
        hf = hc[spec["hurt"][1] % len(hc)]
        ha = _np().array(hf.convert("RGBA"))
        opq = ha[:, :, 3] > 0
        # several packs flash the first hurt frame pure white; use our own tint instead
        raw.append(None if (not opq.any() or ha[opq][:, :3].mean() > 200) else hf)
        srcs = [spec["idle"][0], spec["tell"][0], spec["hurt"][0]]
    proc = []
    for r in raw:
        if r is None:
            proc.append(None)
            continue
        r = _strip_shadow(r.convert("RGBA"))
        if spec.get("flip"):
            r = r.transpose(Image.FLIP_LEFT_RIGHT)
        r = _scale(r, spec.get("scale", 1))
        proc.append(unify(r, region, spec.get("k", 0.3), spec.get("hue", 0), spec.get("sat", 1.0)))
    if spec["kind"] == "still":
        proc = _synth_frames(proc[0]) + [None]
    if proc[3] is None:
        proc[3] = _hurt(proc[0])
    # common canvas, frames aligned on the bottom-centre of their source cells, then cropped to the union
    W = max(p.width for p in proc)
    H = max(p.height for p in proc)
    cells = []
    for p in proc:
        c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        c.paste(p, ((W - p.width) // 2, H - p.height), p)
        cells.append(c)
    bb = None
    for c in cells:
        b = c.getbbox()
        if b:
            bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    x0, y0, x1, y1 = bb
    x0, x1 = max(0, x0 - 2), min(W, x1 + 2)
    y0 = max(0, y0 - 2)
    fw, fh = x1 - x0, y1 - y0 + 2
    out = Image.new("RGBA", (fw * 4, fh), (0, 0, 0, 0))
    for i, c in enumerate(cells):
        out.paste(c.crop((x0, y0, x1, y1)), (i * fw, 0))
    if spec.get("chain"):
        out = _add_chain(out, fw, fh)
    return out, srcs, f"{fw}x{fh} x4 (idle,idle,tell,hurt)"


def _add_chain(img, fw, fh):
    """Chain Roc: an iron tether from the bird's feet down-left to the ground (drawn over each frame)."""
    np = _np()
    for i in range(4):
        fr = img.crop((i * fw, 0, (i + 1) * fw, fh))
        a = np.array(fr)
        op = a[:, :, 3] > 0
        ys, xs = np.nonzero(op)
        lowy = ys.max()
        lx = int(xs[ys >= lowy - 6].mean())
        c = Canvas(fw, fh)
        for k in range(0, 40):
            t = k / 39
            x = lx - t * 26
            y = lowy - 4 + t * (fh - lowy + 2) + math.sin(t * 3.1) * 3
            col = (150, 150, 162, 255) if k % 3 else (96, 96, 110, 255)
            c.ellipse(x, y, 1.4, 1.0, col, 2)
        ch = c.image()
        base = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        base.alpha_composite(ch)
        base.alpha_composite(fr)
        img.paste(base, (i * fw, 0))
    return img


def build_library(save_ext):
    for eid, spec in LIB_EN.items():
        try:
            img, srcs, fr = lib_frames(eid, spec)
        except FileNotFoundError as e:
            print("enemies: library source missing for", eid, e)
            continue
        save_ext(img, f"sprites/enemies/{eid}.png", "boss_sprite" if eid[0] == "B" else "enemy_sprite", srcs, fr,
                 "library battler, unified (shadow strip, integer scale, edge/grade/light pass)")
