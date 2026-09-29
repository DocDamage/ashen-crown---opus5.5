"""40x40 portraits, three expressions per character (neutral, concern, determined)."""
from PIL import Image
from art.pix import Canvas, shade, hexc
from art.figures import FIG, NPCS

OUT = (22, 16, 28, 255)


def portrait(f, expr):
    c = Canvas(40, 40)
    skin, hair, top = f["skin"], f["hair"], f["top"]
    # shoulders / clothing
    c.ellipse(20, 42, 17, 10, top, 3)
    if f.get("armor"):
        c.ellipse(8, 36, 7, 5, shade(top, 0.2), 6)
        c.ellipse(32, 36, 7, 5, shade(top, 0.2), 6)
        if f.get("accent"):
            c.rect(19, 33, 20, 40, f["accent"], 6)
    if f.get("stole"):
        c.poly([(6, 40), (14, 31), (26, 31), (34, 40)], f["stole"], 6)
    if f.get("scarf"):
        c.ellipse(20, 32, 10, 4, f["scarf"], 6)
        c.rect(26, 32, 29, 40, f["scarf"], 6)
    if f.get("waistcoat"):
        c.poly([(6, 40), (12, 34), (18, 40)], f["waistcoat"], 6)
        c.poly([(34, 40), (28, 34), (22, 40)], f["waistcoat"], 6)
    if f.get("cape"):
        c.ellipse(6, 38, 6, 6, f["cape"], 6)
        c.ellipse(34, 38, 6, 6, f["cape"], 6)
    if f.get("apron"):
        c.rect(12, 34, 28, 40, f["apron"], 6)
    if f.get("coat"):
        c.poly([(8, 40), (16, 32), (20, 40)], shade(top, -0.2), 6)
        c.poly([(32, 40), (24, 32), (20, 40)], shade(top, -0.2), 6)
    # neck + head
    c.rect(17, 26, 23, 33, shade(skin, -0.15), 1)
    c.ellipse(20, 18, 9.5, 11, skin, 1)
    if f.get("scales"):
        for (x, y) in ((13, 15), (27, 14), (14, 22), (26, 23), (20, 10), (16, 11), (24, 11)):
            c.put(x, y, shade(skin, -0.3), 1)
            c.put(x + 1, y, shade(skin, -0.18), 1)
    # hair
    hc = hair
    st = f.get("hair_style", "short_swept")
    c.ellipse(20, 10, 10.5, 6, hc, 2)
    c.rect(10, 9, 12, 17, hc, 2)
    c.rect(28, 9, 30, 17, hc, 2)
    if st == "short_swept":
        c.poly([(11, 12), (22, 8), (16, 15)], hc, 2)
    elif st == "short_messy":
        for x in (12, 16, 21, 26):
            c.poly([(x, 12), (x + 2, 16), (x + 4, 12)], hc, 2)
    elif st == "bob":
        c.rect(9, 9, 12, 26, hc, 2)
        c.rect(28, 9, 31, 26, hc, 2)
        c.rect(12, 9, 28, 13, hc, 2)
    elif st in ("long", "braid"):
        c.rect(9, 9, 12, 32, hc, 2)
        c.rect(28, 9, 31, 32, hc, 2)
        if st == "braid":
            c.rect(30, 26, 32, 38, hc, 2)
    elif st == "tied":
        c.ellipse(31, 8, 3, 3, hc, 2)
    elif st == "cropped":
        c.ellipse(20, 10, 10, 4.5, hc, 2)
    elif st in ("curls", "curls_short"):
        for (x, y) in ((11, 9), (15, 6), (20, 5), (25, 6), (29, 9), (30, 14), (10, 14)):
            c.ellipse(x, y, 3, 3, hc, 2)
        if st == "curls":
            c.ellipse(30, 20, 3, 3, hc, 2)
            c.ellipse(10, 20, 3, 3, hc, 2)
    if f.get("hat"):
        c.ellipse(20, 8, 13, 3, f["hat"], 6)
        c.ellipse(20, 5, 8, 4, f["hat"], 6)
    # face
    eye = f.get("eye", (30, 20, 20, 255))
    ey = 19
    c.rect(15, ey, 16, ey + 1, eye, 7)
    c.rect(24, ey, 25, ey + 1, eye, 7)
    c.put(15, ey, (255, 255, 255, 255), 7)
    c.put(24, ey, (255, 255, 255, 255), 7)
    brow = shade(hair, -0.2)
    if expr == "neutral":
        c.line(14, ey - 3, 17, ey - 3, brow, 1, 7)
        c.line(23, ey - 3, 26, ey - 3, brow, 1, 7)
        c.line(18, 26, 22, 26, shade(skin, -0.4), 1, 7)
    elif expr == "concern":
        c.line(14, ey - 3, 17, ey - 4, brow, 1, 7)
        c.line(23, ey - 4, 26, ey - 3, brow, 1, 7)
        c.line(18, 27, 22, 27, shade(skin, -0.4), 1, 7)
        c.put(17, 26, shade(skin, -0.4), 7)
        c.put(23, 26, shade(skin, -0.4), 7)
    else:
        c.line(14, ey - 4, 17, ey - 2, brow, 1, 7)
        c.line(23, ey - 2, 26, ey - 4, brow, 1, 7)
        c.line(17, 26, 23, 26, shade(skin, -0.45), 1, 7)
    c.put(20, 23, shade(skin, -0.25), 7)
    if f.get("goggles"):
        c.rect(12, 11, 28, 13, f["goggles"], 6)
        c.ellipse(16, 12, 3, 2, shade(f["goggles"], 0.3), 6)
        c.ellipse(24, 12, 3, 2, shade(f["goggles"], 0.3), 6)
    if f.get("glasses"):
        c.rect(13, 18, 18, 21, f["glasses"], 6)
        c.rect(22, 18, 27, 21, f["glasses"], 6)
        c.rect(15, 19, 16, 20, eye, 7)
        c.rect(24, 19, 25, 20, eye, 7)
    if f.get("beard"):
        c.ellipse(20, 27, 7, 4, f["beard"], 2)
        c.line(18, 26, 22, 26, shade(skin, -0.4), 1, 7)
    if f.get("bell"):
        c.ellipse(33, 36, 3, 3, f["bell"], 6)
    c.light(0.14)
    c.outline(OUT)
    return c


def build(save):
    for key, f in list(FIG.items()) + list(NPCS.items()):
        img = Image.new("RGBA", (120, 40), (0, 0, 0, 0))
        for i, e in enumerate(["neutral", "concern", "determined"]):
            img.paste(portrait(f, e).image(), (i * 40, 0))
        save(img, f"sprites/portraits/{key}.png", "portrait", "40x40 x3 (neutral, concern, determined)")
