"""Field objects, title logo, airship, ferry, summon (Vestige) sprites."""
import math
from PIL import Image, ImageDraw
from art.pix import Canvas, shade, hexc, mix

OUT = (22, 16, 28, 255)


def fin(c):
    c.light(0.15)
    c.outline(OUT)
    return c


def objects():
    img = Image.new("RGBA", (16 * 8, 16), (0, 0, 0, 0))
    wood, gold = hexc("8a5a30"), hexc("e0b040")
    # 0 chest closed
    c = Canvas(16, 16)
    c.rect(2, 5, 13, 14, wood, 1)
    c.rect(2, 5, 13, 8, shade(wood, 0.2), 2)
    c.rect(2, 8, 13, 8, shade(wood, -0.4), 2)
    c.rect(7, 7, 8, 10, gold, 3)
    img.paste(fin(c).image(), (0, 0))
    # 1 chest open
    c = Canvas(16, 16)
    c.rect(2, 8, 13, 14, wood, 1)
    c.rect(2, 3, 13, 6, shade(wood, 0.25), 2)
    c.rect(3, 7, 12, 8, (30, 20, 20, 255), 3)
    img.paste(fin(c).image(), (16, 0))
    # 2,3 save lamp (ashen lamp) two frames
    for i in range(2):
        c = Canvas(16, 16)
        c.rect(6, 10, 9, 15, hexc("5a5a64"), 1)
        c.rect(4, 14, 11, 15, hexc("3a3a44"), 1)
        c.ellipse(7.5, 6, 4, 4.5, hexc("f0c060") if i == 0 else hexc("ffe0a0"), 2)
        c.ellipse(7.5, 6, 2, 2.5, hexc("fff4d0"), 3)
        c.rect(5, 1, 10, 2, hexc("5a5a64"), 1)
        img.paste(fin(c).image(), (32 + i * 16, 0))
    # 4 lever off, 5 lever on
    for i in range(2):
        c = Canvas(16, 16)
        c.rect(3, 11, 12, 15, hexc("5a5a64"), 1)
        if i == 0:
            c.line(7, 12, 3, 4, hexc("a0a0a8"), 2, 2)
            c.ellipse(3, 4, 1.8, 1.8, hexc("c04030"), 3)
        else:
            c.line(8, 12, 12, 4, hexc("a0a0a8"), 2, 2)
            c.ellipse(12, 4, 1.8, 1.8, hexc("40c060"), 3)
        img.paste(fin(c).image(), (64 + i * 16, 0))
    # 6 recovery spring
    c = Canvas(16, 16)
    c.ellipse(8, 10, 7, 5, hexc("8a8a80"), 1)
    c.ellipse(8, 10, 5, 3.5, hexc("5ab0e0"), 2)
    c.put(6, 9, hexc("e0f8ff"), 3)
    c.put(10, 8, hexc("e0f8ff"), 3)
    img.paste(fin(c).image(), (96, 0))
    # 7 sparkle
    c = Canvas(16, 16)
    c.line(8, 3, 8, 13, hexc("fff0b0"), 1, 1)
    c.line(3, 8, 13, 8, hexc("fff0b0"), 1, 1)
    img.paste(c.image(), (112, 0))
    return img


def wayfarer():
    c = Canvas(48, 36)
    hull, wood, cloth = hexc("7a5232"), hexc("a07a4a"), hexc("d8d0b8")
    c.poly([(2, 22), (46, 22), (40, 32), (8, 32)], hull, 1)
    c.rect(4, 20, 44, 22, wood, 2)
    c.ellipse(24, 10, 20, 8, cloth, 3)
    c.line(6, 12, 42, 12, shade(cloth, -0.2), 1, 3)
    c.line(12, 16, 12, 22, wood, 1, 4)
    c.line(36, 16, 36, 22, wood, 1, 4)
    c.rect(20, 24, 28, 28, hexc("f0c060"), 5)
    c.rect(44, 18, 47, 26, hexc("8a8a90"), 6)
    return fin(c).image()


def ferry():
    c = Canvas(32, 20)
    c.poly([(1, 10), (31, 10), (27, 18), (5, 18)], hexc("7a5232"), 1)
    c.rect(12, 3, 20, 10, hexc("d8d0b8"), 2)
    c.line(16, 1, 16, 10, hexc("5a3a22"), 1, 3)
    return fin(c).image()


# Title wordmark: hand-authored serif capitals (13 px, 2 px stems), scaled 2x with EPX edge smoothing.
BIG = {
    "A": [".....##.....", ".....##.....", "....####....", "....#.##....", "...##..##...", "...#...##...",
          "..##....##..", "..########..", ".##......##.", ".#.......##.", "##.......###", "##........##",
          "####....####"],
    "T": ["############", "##...##...##", "#....##....#", ".....##.....", ".....##.....", ".....##.....",
          ".....##.....", ".....##.....", ".....##.....", ".....##.....", ".....##.....", "....####....",
          "...######..."],
    "H": ["####....####", ".##......##.", ".##......##.", ".##......##.", ".##......##.", ".##########.",
          ".##......##.", ".##......##.", ".##......##.", ".##......##.", ".##......##.", ".##......##.",
          "####....####"],
    "E": ["##########", ".##.....##", ".##......#", ".##.......", ".##...#...", ".#######..", ".##...#...",
          ".##.......", ".##.......", ".##.......", ".##......#", ".##.....##", "##########"],
    "S": ["..######.#", ".##....###", "##......##", "##.......#", "###.......", ".#####....", "...#####..",
          "......###.", ".......###", "#.......##", "##......##", "###....##.", "#.######.."],
    "N": ["###.....####", ".###.....##.", ".####....##.", ".##.##...##.", ".##.##...##.", ".##..##..##.",
          ".##..##..##.", ".##...##.##.", ".##...##.##.", ".##....####.", ".##....####.", ".##.....###.",
          "####.....##."],
    "C": ["...######.#", ".###....###", ".##......##", "##........#", "##.........", "##.........",
          "##.........", "##.........", "##.........", "##........#", ".##......##", ".###....##.",
          "...######.."],
    "R": ["#########..", ".##....###.", ".##.....##.", ".##.....##.", ".##.....##.", ".##....###.",
          ".#######...", ".##..###...", ".##...###..", ".##....##..", ".##....###.", ".##.....###",
          "####.....##"],
    "O": ["...#####...", ".###...###.", ".##.....##.", "##.......##", "##.......##", "##.......##",
          "##.......##", "##.......##", "##.......##", "##.......##", ".##.....##.", ".###...###.",
          "...#####..."],
    "W": ["####..##..####", ".##...##...##.", ".##...##...##.", ".##..####..##.", ".##..####..##.",
          ".##..#..#..##.", "..##.#..#.##..", "..##.#..#.##..", "..####..####..", "..###....###..",
          "..###....###..", "...#......#...", "...#......#..."],
}


def _word_mask(text, gap=2, space=7):
    cols = []
    for i, ch in enumerate(text):
        if ch == " ":
            cols += [[0] * 13] * space
            continue
        g = BIG[ch]
        w = max(len(r) for r in g)
        for x in range(w):
            cols.append([1 if x < len(g[y]) and g[y][x] == "#" else 0 for y in range(13)])
        if i + 1 < len(text) and text[i + 1] != " ":
            cols += [[0] * 13] * gap
    w = len(cols)
    return [[cols[x][y] for x in range(w)] for y in range(13)]


def _epx(m):
    h, w = len(m), len(m[0])
    g = lambda x, y: m[y][x] if 0 <= x < w and 0 <= y < h else 0
    out = [[0] * (w * 2) for _ in range(h * 2)]
    for y in range(h):
        for x in range(w):
            p = m[y][x]
            A, B, C, D = g(x, y - 1), g(x + 1, y), g(x - 1, y), g(x, y + 1)
            q = [p, p, p, p]
            if C == A and C != D and A != B: q[0] = A
            if A == B and A != C and B != D: q[1] = B
            if D == C and D != B and C != A: q[2] = C
            if B == D and B != A and D != C: q[3] = D
            out[y * 2][x * 2], out[y * 2][x * 2 + 1], out[y * 2 + 1][x * 2], out[y * 2 + 1][x * 2 + 1] = q
    return out


# ash-silver above an ember reflection, split by a dark horizon line (metallic 16-bit logo ramp)
TEXT_RAMP = [(252, 252, 255), (240, 242, 250), (226, 230, 244), (212, 218, 236), (198, 206, 228), (184, 192, 218),
             (168, 176, 206), (152, 160, 194), (134, 142, 178), (116, 122, 160), (96, 100, 140), (74, 74, 110),
             (52, 44, 70), (70, 36, 44), (255, 214, 130), (252, 196, 106), (246, 176, 86), (238, 154, 70),
             (228, 132, 58), (214, 110, 48), (196, 90, 42), (176, 72, 38), (154, 56, 34), (132, 44, 32),
             (110, 34, 30), (90, 26, 28)]
GOLD_RAMP = [(255, 248, 200), (252, 228, 140), (240, 196, 84), (214, 158, 56), (170, 112, 40), (118, 70, 30)]


def _stamp(img, mask, ox, oy, colour_of, outline=(20, 10, 18, 255), shadow=(6, 2, 10, 200)):
    h, w = len(mask), len(mask[0])
    on = lambda x, y: 0 <= x < w and 0 <= y < h and mask[y][x]
    for y in range(-1, h + 2):
        for x in range(-1, w + 2):
            if on(x, y):
                continue
            if on(x - 1, y - 2) or on(x - 2, y - 2) or on(x - 1, y - 1):
                img.putpixel((ox + x, oy + y), shadow)
    for y in range(-1, h + 1):
        for x in range(-1, w + 1):
            if on(x, y):
                continue
            if any(on(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                img.putpixel((ox + x, oy + y), outline)
    for y in range(h):
        for x in range(w):
            if on(x, y):
                c = colour_of(x, y)
                if not on(x, y - 1) or not on(x - 1, y):
                    c = mix(c + (255,), (255, 255, 255, 255), 0.35)[:3]
                elif not on(x, y + 1) or not on(x + 1, y):
                    c = mix(c + (255,), (20, 10, 30, 255), 0.25)[:3]
                img.putpixel((ox + x, oy + y), c + (255,))


def _crown(W, k=1.3):
    """Gothic crown, gold on the left crumbling to ash on the right. Authored at 1x, laid out at scale k."""
    H = int(50 * k)
    c = Canvas(W, H)
    cx = W // 2
    S = lambda v: v * k
    velvet = hexc("7a1c2c")
    metal = (1, 1, 1, 255)
    c.ellipse(cx, S(30), S(30), S(12), velvet, 5)
    for (x0, xt, x1, yt) in ((-36, -31, -24, 18), (-24, -15, -7, 11), (-8, 0, 8, 7), (7, 15, 24, 11), (24, 31, 36, 18)):
        c.poly([(cx + S(x0), S(36)), (cx + S(xt) - 1, S(yt)), (cx + S(xt) + 1, S(yt)), (cx + S(x1), S(36))], metal, 2)
    for (x, y, r) in ((-31, 15, 2.2), (-15, 8, 2.6), (15, 8, 2.6), (31, 15, 2.2)):
        c.ellipse(cx + S(x), S(y), S(r), S(r), metal, 3)
    c.rect(cx - 1, 0, cx + 1, S(7), metal, 3)
    c.rect(cx - S(4), S(2), cx + S(4), S(2) + 1, metal, 3)
    c.poly([(cx - S(38), S(34)), (cx + S(38), S(34)), (cx + S(37), S(45)), (cx, S(47)), (cx - S(37), S(45))], metal, 1)
    for y in range(c.h):
        for x in range(c.w):
            p = c.px[y][x]
            if p is not None and p[:3] == (1, 1, 1):
                t = y / S(47)
                i = min(len(GOLD_RAMP) - 1, int(t * (len(GOLD_RAMP) - 1) + 0.5))
                c.px[y][x] = GOLD_RAMP[i] + (255,)
    # band rims, pearls and jewels
    for x in range(int(cx - S(37)), int(cx + S(38))):
        c.put(x, S(35), GOLD_RAMP[0] + (255,), 1)
        c.put(x, S(44) if abs(x - cx) > S(20) else S(45), GOLD_RAMP[4] + (255,), 1)
    c.ellipse(cx, S(40), 4, 3.6, hexc("d02838"), 4)
    c.put(cx - 1, S(40) - 2, hexc("ffb0b0"), 4)
    for dx, col in ((-17, "2c70d0"), (17, "2c70d0"), (-30, "30a060"), (30, "30a060")):
        c.ellipse(cx + S(dx), S(40), 2.4, 2.4, hexc(col), 4)
        c.put(cx + S(dx) - 1, S(40) - 1, hexc("e0f0ff"), 4)
    for dx in range(-35, 36, 3):
        if abs(dx) > 4 and abs(abs(dx) - 17) > 3 and abs(abs(dx) - 30) > 3:
            c.put(cx + S(dx), S(37), GOLD_RAMP[0] + (255,), 1)
    c.light(0.2)
    # ash: the right side greys out and crumbles
    rnd = __import__("random").Random(7)
    for y in range(c.h):
        for x in range(c.w):
            p = c.px[y][x]
            if p is None:
                continue
            t = (x - (cx + S(6))) / S(30)
            if t > 0:
                g = int(sum(p[:3]) / 3)
                ash = (int(g * 0.8 + 30), int(g * 0.78 + 28), int(g * 0.8 + 34), 255)
                c.px[y][x] = mix(p, ash, min(1.0, t * 1.2))
                if t > 0.55 and rnd.random() < (t - 0.55) * 0.9 and y < S(36):
                    c.px[y][x] = None
    c.outline((20, 10, 18, 255))
    for i in range(34):
        x = cx + S(24) + int(rnd.random() * S(34))
        y = int(rnd.random() * S(32))
        g = 90 + int(rnd.random() * 80)
        col = (g, g - 4, g + 6, 255) if i % 5 else (250, 150, 70, 255)
        c.put(x, y, col, 6)
        if i % 3 == 0:
            c.put(x + 1, y, col, 6)
    return c.image()


def logo():
    W, H = 300, 112
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.alpha_composite(_crown(W), (0, 0))
    # "THE" in small silver capitals from the project font, flanked by gold rules
    root = __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "..", "game", "assets", "fonts")
    font = Image.open(__import__("os").path.join(root, "ashen8.png")).convert("RGBA")
    glyphs = {}
    for ln in open(__import__("os").path.join(root, "ashen8.fnt")).read().splitlines():
        if ln.startswith("char id="):
            kv = dict(p.split("=") for p in ln.split()[1:])
            glyphs[chr(int(kv["id"]))] = (int(kv["x"]), int(kv["y"]), int(kv["width"]), int(kv["xadvance"]))
    small = "THE"
    sw = sum(glyphs[ch][3] + 2 for ch in small) - 3
    x = (W - sw) // 2
    ty = 64
    for ch in small:
        gx, gy, gw, adv = glyphs[ch]
        g = font.crop((gx, gy + 1, gx + gw, gy + 8))
        m = [[1 if g.getpixel((xx, yy))[3] > 0 else 0 for xx in range(gw)] for yy in range(7)]
        _stamp(img, m, x, ty, lambda xx, yy: TEXT_RAMP[yy * 2], shadow=(0, 0, 0, 0))
        x += adv + 2
    for side in (-1, 1):
        x0 = W // 2 + side * (sw // 2 + 8)
        for k in range(38):
            xx = x0 + side * k
            a = 255 if k < 30 else 255 - (k - 30) * 30
            img.putpixel((xx, ty + 3), GOLD_RAMP[1] + (a,))
            img.putpixel((xx, ty + 4), GOLD_RAMP[4] + (a,))
    # main wordmark
    m = _epx(_word_mask("ASHEN CROWN"))
    mw = len(m[0])
    _stamp(img, m, (W - mw) // 2, 76, lambda xx, yy: TEXT_RAMP[min(len(TEXT_RAMP) - 1, yy)])
    # ornament rule with a centre diamond
    oy = 107
    for k in range(-110, 111):
        a = 255 if abs(k) < 90 else max(0, 255 - (abs(k) - 90) * 12)
        img.putpixel((W // 2 + k, oy), GOLD_RAMP[1] + (a,))
        img.putpixel((W // 2 + k, oy + 1), GOLD_RAMP[4] + (a,))
    for dy in range(-3, 4):
        for dx in range(-(3 - abs(dy)), 4 - abs(dy)):
            img.putpixel((W // 2 + dx, oy + dy), (GOLD_RAMP[0] if dy < 0 else GOLD_RAMP[3]) + (255,))
    return img


VEST = {
    "V01": ("moth", hexc("f08a3a"), hexc("ffd080")), "V02": ("stag", hexc("6a8a3a"), hexc("e0c080")),
    "V03": ("whale", hexc("3a6aa0"), hexc("c0e0f0")), "V04": ("manta", hexc("3a4a8a"), hexc("f0e060")),
    "V05": ("fox", hexc("f0e0a0"), hexc("fff8e0")), "V06": ("tortoise", hexc("8a6a3a"), hexc("c0a060")),
    "V07": ("hind", hexc("c8e0f0"), hexc("ffffff")), "V08": ("leviathan", hexc("1a2a4a"), hexc("80e0ff")),
}


def vestige(kind, a, b):
    c = Canvas(96, 80)
    if kind == "moth":
        c.poly([(48, 44), (8, 10), (4, 50), (40, 60)], a, 1)
        c.poly([(48, 44), (88, 10), (92, 50), (56, 60)], shade(a, 0.1), 1)
        c.ellipse(48, 48, 6, 18, b, 2)
    elif kind == "stag":
        c.ellipse(44, 52, 28, 14, a, 1)
        for lx in (24, 36, 54, 64):
            c.line(lx, 60, lx, 78, shade(a, -0.2), 4, 2)
        c.ellipse(76, 34, 9, 8, a, 3)
        c.line(74, 28, 62, 6, b, 2, 4)
        c.line(80, 28, 92, 6, b, 2, 4)
    elif kind == "whale":
        c.ellipse(46, 46, 40, 20, a, 1)
        c.ellipse(46, 54, 32, 10, b, 2)
        c.poly([(8, 40), (0, 26), (0, 56)], a, 1)
        c.ellipse(74, 40, 2, 2, (20, 20, 30, 255), 3)
    elif kind == "manta":
        c.poly([(48, 30), (2, 50), (48, 62), (94, 50)], a, 1)
        c.line(48, 62, 48, 78, a, 2, 2)
        c.ellipse(40, 44, 2, 2, b, 3)
        c.ellipse(56, 44, 2, 2, b, 3)
    elif kind == "fox":
        c.ellipse(46, 54, 20, 12, a, 1)
        c.ellipse(70, 40, 10, 9, a, 2)
        c.poly([(64, 34), (66, 22), (72, 32)], a, 2)
        c.poly([(72, 32), (78, 22), (78, 36)], a, 2)
        c.ellipse(20, 44, 14, 8, b, 3)
    elif kind == "tortoise":
        c.ellipse(48, 50, 32, 20, a, 1)
        for (x, y) in ((36, 44), (52, 40), (62, 50), (42, 56)):
            c.ellipse(x, y, 6, 5, b, 2)
        c.ellipse(84, 52, 8, 6, shade(a, 0.1), 3)
    elif kind == "hind":
        c.ellipse(44, 50, 24, 12, a, 1)
        for lx in (28, 38, 52, 60):
            c.line(lx, 58, lx, 78, a, 3, 2)
        c.line(64, 44, 76, 22, a, 5, 3)
        c.ellipse(78, 20, 7, 6, a, 3)
        c.line(76, 14, 70, 2, b, 1, 4)
        c.line(80, 14, 86, 2, b, 1, 4)
    elif kind == "leviathan":
        for i in range(10):
            c.ellipse(8 + i * 8, 56 - math.sin(i * 0.7) * 14, 10, 9, a if i % 2 else shade(a, 0.1), 1)
        c.ellipse(88, 34, 8, 8, a, 2)
        c.ellipse(90, 32, 2, 2, b, 3)
    return fin(c).image()


def build(save):
    save(objects(), "sprites/objects.png", "objects", "16x16 x8: chest,chest_open,lamp_a,lamp_b,lever_off,lever_on,spring,sparkle")
    save(wayfarer(), "sprites/wayfarer.png", "vehicle", "48x36")
    save(ferry(), "sprites/ferry.png", "vehicle", "32x20")
    save(logo(), "ui/title.png", "ui", "300x112 crown + serif wordmark (EPX 2x), metallic ramp")
    for vid, (k, a, b) in VEST.items():
        save(vestige(k, a, b), f"sprites/vestiges/{vid}.png", "summon", "96x80", k)
