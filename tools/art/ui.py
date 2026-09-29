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


def logo():
    from PIL import ImageFont
    W, H = 240, 80
    c = Canvas(W, H)
    # crown emblem
    gold, ember, ash = hexc("e0b040"), hexc("e05a30"), hexc("5a5058")
    c.poly([(96, 30), (104, 10), (112, 24), (120, 4), (128, 24), (136, 10), (144, 30)], gold, 1)
    c.rect(96, 30, 144, 36, shade(gold, -0.2), 1)
    for x in (104, 120, 136):
        c.ellipse(x, 33, 2, 2, ember, 2)
    for i in range(24):
        x = 96 + (i * 7) % 48
        y = 38 + (i * 5) % 8
        c.put(x, y, ash, 3)
    fin(c)
    img = c.image()
    # title lettering from the project font atlas, scaled 2x (nearest) for a chunky pixel wordmark
    font = Image.open(__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "..", "game", "assets", "fonts", "ashen8.png"))
    fnt = open(__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "..", "game", "assets", "fonts", "ashen8.fnt")).read()
    glyphs = {}
    for ln in fnt.splitlines():
        if ln.startswith("char id="):
            kv = dict(p.split("=") for p in ln.split()[1:])
            glyphs[chr(int(kv["id"]))] = (int(kv["x"]), int(kv["y"]), int(kv["width"]), int(kv["xadvance"]))
    text = "THE ASHEN CROWN"
    wpx = sum(glyphs[ch][3] for ch in text) * 2
    x = (W - wpx) // 2
    for ch in text:
        gx, gy, gw, adv = glyphs[ch]
        g = font.crop((gx, gy, gx + max(gw, 1), gy + 10)).resize((max(gw, 1) * 2, 20), Image.NEAREST)
        shadow = Image.new("RGBA", g.size, (40, 10, 10, 255))
        img.paste(shadow, (x + 2, 48 + 2), g)
        goldimg = Image.new("RGBA", g.size, (240, 200, 90, 255))
        img.paste(goldimg, (x, 48), g)
        x += adv * 2
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
    save(logo(), "ui/title.png", "ui", "240x80 wordmark from project font")
    for vid, (k, a, b) in VEST.items():
        save(vestige(k, a, b), f"sprites/vestiges/{vid}.png", "summon", "96x80", k)
