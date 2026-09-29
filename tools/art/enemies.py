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
    c.light(0.16)
    c.outline(OUT)
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
def boss_extractor(fr, W=128, H=144):
    c = Canvas(W, H)
    p = pal("a8883a", "3a3430", "6a6058", "e04030", "ffd060")
    # tracked base
    c.rect(10, 118, 110, 138, p[1], 1)
    for x in range(14, 108, 10):
        c.ellipse(x, 128, 4, 4, p[2], 2)
    # body
    c.rect(24, 70, 96, 118, p[0], 3)
    c.rect(24, 70, 96, 76, shade(p[0], 0.25), 3)
    for x in (30, 50, 70, 90):
        c.ellipse(x, 110, 2, 2, shade(p[0], -0.4), 3)
    # pressure gauge
    gauge_fill = [0.3, 0.35, 0.95, 0.5][fr]
    c.ellipse(60, 92, 12, 12, (230, 226, 210, 255), 4)
    c.ellipse(60, 92, 9, 9, (40, 30, 30, 255), 4)
    a = math.pi * (1.2 - gauge_fill * 1.4)
    c.line(60, 92, 60 + math.cos(a) * 8, 92 - math.sin(a) * 8, p[3], 2, 4)
    # digging arm
    lift = [0, -3, -16, 4][fr]
    c.line(92, 76, 112, 48 + lift, p[1], 6, 5)
    c.line(112, 48 + lift, 120, 80 + lift * 0.5, p[1], 5, 5)
    c.poly([(114, 78 + lift * 0.5), (127, 84 + lift * 0.5), (120, 96 + lift * 0.5), (110, 90 + lift * 0.5)], (180, 180, 190, 255), 6)
    # stack and heartglass core
    c.rect(34, 40, 46, 70, p[2], 7)
    c.ellipse(40, 36, 8, 4, p[1], 7)
    if fr != 1:
        c.ellipse(40, 28 - fr, 6, 4, (180, 170, 170, 200), 8)
    c.ellipse(76, 60, 9, 12, (200, 60, 70, 255) if fr != 2 else (255, 110, 110, 255), 9)
    c.ellipse(74, 56, 3, 4, (255, 180, 180, 255), 9)
    return finish(c)


def boss_generic(bid, fr):
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
        fam = FAMILY[shape]
        frames = [fam(sz, p, 0), fam(sz, p, 1), fam(sz, p, 2), hurt_tint(fam(sz, p, 3))]
        save(strip(frames), f"sprites/enemies/{eid}.png", "enemy_sprite", f"{sz}x{sz} x4 (idle,idle,tell,hurt)", shape)
    frames = [boss_extractor(i) for i in range(3)] + [hurt_tint(boss_extractor(3))]
    save(strip(frames), "sprites/enemies/B01.png", "boss_sprite", "128x144 x4", "extractor")
    for bid in BOSS_KIND:
        frames = [boss_generic(bid, i) for i in range(3)] + [hurt_tint(boss_generic(bid, 3))]
        save(strip(frames), f"sprites/enemies/{bid}.png", "boss_sprite", f"{frames[0].w}x{frames[0].h} x4", BOSS_KIND[bid])
    parts = {"B01_P1": "valve", "B03_P1": "root", "B10_P1": "relay", "B10_P2": "relay", "B11_P1": "valve", "B13_P1": "lantern"}
    for pid, k in parts.items():
        frames = [part_sprite(k, i) for i in range(3)] + [hurt_tint(part_sprite(k, 3))]
        save(strip(frames), f"sprites/enemies/{pid}.png", "part_sprite", "32x32 x4", k)
