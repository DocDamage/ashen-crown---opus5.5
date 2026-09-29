"""40x40 portraits, three expressions per character (neutral, concern, determined).

FF6-style small painted busts (doc 11, revision 2026-09-29): 3/4 view turned slightly to the viewer's left, light from
the upper left, every material shaded as a volume with a 5-step ramp (cool violet shadows, warm cream highlights),
hair drawn as shaded clumps with a sheen band, selective dark-colour outlines instead of flat black.
No licensed portrait set fits the Time Fantasy sprites and all 8 heroes, so these stay project-generated.
"""
import math
from PIL import Image
from art.pix import shade, hexc, mix
from art.figures import FIG, NPCS

S = 40
LX, LY, LZ = -0.55, -0.62, 0.56                     # light direction (upper left, toward viewer)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
T_BODY, T_SKIN, T_HAIR, T_ACC, T_EYE, T_METAL = 1, 2, 3, 4, 5, 6


def ramp5(c):
    return [shade(c, -0.58), shade(c, -0.3), c, shade(c, 0.2), shade(c, 0.42)]


class P:
    """Tiny paint buffer: colour + material tag per pixel."""

    def __init__(self):
        self.c = {}
        self.t = {}

    def put(self, x, y, col, tag):
        x, y = int(x), int(y)
        if 0 <= x < S and 0 <= y < S and col is not None:
            self.c[(x, y)] = col
            self.t[(x, y)] = tag

    def get(self, x, y):
        return self.c.get((int(x), int(y)))

    def tag(self, x, y):
        return self.t.get((int(x), int(y)))


def _tone(d, x, y, soft=0.9):
    """Lambert term -> ramp index 0..4 with a light ordered dither at band edges (2-4 px clusters, no noise)."""
    v = max(0.0, min(1.0, (d + 0.25) / 1.15)) * 4.0
    v += (BAYER[y % 4][x % 4] / 16.0 - 0.5) * 0.35 * soft
    return max(0, min(4, int(round(v))))


def vol(p, cx, cy, rx, ry, base, tag, clip=None, bias=0.0, rim=True):
    """Fill an ellipse shaded as a lit ellipsoid."""
    r = ramp5(base)
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            nx, ny = (x + 0.5 - cx) / (rx + 0.3), (y + 0.5 - cy) / (ry + 0.3)
            q = nx * nx + ny * ny
            if q > 1.0 or (clip and not clip(x, y)):
                continue
            nz = math.sqrt(max(0.0, 1.0 - q))
            d = LX * nx + LY * ny + LZ * nz + bias
            i = _tone(d, x, y)
            if rim and q > 0.86 and nx > 0.45:
                i = max(0, i - 1)
            p.put(x, y, r[i], tag)


def poly(p, pts, base, tag, grad=None):
    """Polygon; grad=(cx, cy, rx, ry) shades it as part of that ellipsoid."""
    xs = [a for a, _ in pts]
    ys = [b for _, b in pts]
    r = ramp5(base)
    for y in range(int(min(ys)), int(max(ys)) + 1):
        for x in range(int(min(xs)), int(max(xs)) + 1):
            if not _inside(x + 0.5, y + 0.5, pts):
                continue
            if grad:
                cx, cy, rx, ry = grad
                nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                nz = math.sqrt(max(0.05, 1.0 - min(0.95, nx * nx + ny * ny)))
                p.put(x, y, r[_tone(LX * nx + LY * ny + LZ * nz, x, y)], tag)
            else:
                p.put(x, y, base, tag)


def _inside(x, y, pts):
    ins = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            ins = not ins
        j = i
    return ins


# ---------------------------------------------------------------------------------------------------------------
def _body(p, f):
    top = f["top"]
    g = (19, 44, 19, 14)
    poly(p, [(1, 40), (4, 32), (12, 28), (27, 28), (35, 32), (39, 40)], top, T_BODY, g)
    if f.get("cape"):
        cp = f["cape"]
        poly(p, [(1, 40), (3, 31), (10, 28), (13, 31), (8, 40)], cp, T_ACC, g)
        poly(p, [(39, 40), (36, 31), (29, 28), (26, 31), (31, 40)], cp, T_ACC, g)
        vol(p, 20, 31, 2, 1.6, f.get("accent", hexc("d0a040")), T_METAL)
    if f.get("coat"):
        dk = shade(top, -0.35)
        for y in range(30, 40):
            p.put(15 + (y - 30) * 0.45, y, dk, T_BODY)
            p.put(25 - (y - 30) * 0.45, y, dk, T_BODY)
        poly(p, [(12, 28), (16, 27), (15, 32)], shade(top, 0.15), T_BODY)
        poly(p, [(28, 28), (24, 27), (25, 32)], shade(top, -0.1), T_BODY)
    if f.get("armor"):
        vol(p, 7, 33, 6.5, 4.5, top, T_METAL)
        vol(p, 33, 33, 6.5, 4.5, top, T_METAL)
        for x in range(13, 28):
            p.put(x, 35, shade(top, -0.4), T_METAL)
        if f.get("accent"):
            for y in range(30, 40):
                p.put(20, y, f["accent"], T_ACC)
    if f.get("waistcoat"):
        w = f["waistcoat"]
        poly(p, [(5, 40), (9, 31), (15, 30), (18, 40)], w, T_ACC, g)
        poly(p, [(35, 40), (31, 31), (25, 30), (22, 40)], w, T_ACC, g)
    if f.get("apron"):
        poly(p, [(14, 31), (26, 31), (27, 40), (13, 40)], f["apron"], T_ACC, g)
        p.put(14, 30, shade(f["apron"], 0.2), T_ACC)
        p.put(26, 30, shade(f["apron"], -0.1), T_ACC)
    if f.get("harness"):
        for i in range(12):
            p.put(26 - i, 29 + i, f["harness"], T_ACC)
            p.put(27 - i, 29 + i, shade(f["harness"], -0.3), T_ACC)
    if f.get("stole"):
        st = f["stole"]
        poly(p, [(4, 40), (9, 30), (15, 28), (17, 33), (12, 40)], st, T_ACC, g)
        poly(p, [(36, 40), (31, 30), (25, 28), (23, 33), (28, 40)], st, T_ACC, g)
    if f.get("scarf"):
        sc = f["scarf"]
        vol(p, 20, 30, 9, 3.2, sc, T_ACC)
        poly(p, [(25, 31), (29, 31), (30, 40), (26, 40)], sc, T_ACC, (27, 33, 4, 9))
    if f.get("sash"):
        for i in range(24):
            for k in (0, 1):
                p.put(8 + i, 38 - i * 0.25 + k, shade(f["sash"], 0.15 if k == 0 else -0.2), T_ACC)
    if f.get("bell"):
        vol(p, 31, 36, 2.6, 2.8, f["bell"], T_METAL)
        p.put(31, 39, shade(f["bell"], -0.5), T_METAL)


def _neck(p, f):
    sk = f["skin"]
    r = ramp5(sk)
    for y in range(24, 31):
        for x in range(16, 24):
            p.put(x, y, r[1] if x > 19 or y < 27 else r[2], T_SKIN)


def _head(p, f):
    sk = f["skin"]
    cx, cy = 19.5, 17.0
    if f.get("scales"):
        # dragonborn: longer skull + snout toward the viewer's left, brow ridge, jaw frills
        vol(p, 21, 16, 8.5, 9.5, sk, T_SKIN)
        vol(p, 13, 21, 7.5, 4.6, sk, T_SKIN, bias=0.05)
        for (x, y) in ((24, 10), (27, 14), (26, 19), (22, 22), (18, 12), (28, 9), (29, 17)):
            p.put(x, y, shade(sk, -0.35), T_SKIN)
            p.put(x + 1, y, shade(sk, -0.2), T_SKIN)
            p.put(x, y - 1, shade(sk, 0.25), T_SKIN)
        for i in range(5):                              # horn / frill sweeping back
            p.put(26 + i, 8 - i * 0.6, shade(f.get("hair", sk), 0.1 - i * 0.05), T_HAIR)
            p.put(26 + i, 9 - i * 0.6, shade(f.get("hair", sk), -0.2), T_HAIR)
        for i in range(4):
            p.put(28 + i, 21 + i * 0.5, shade(sk, -0.25), T_SKIN)
        p.put(7, 20, shade(sk, -0.55), T_SKIN)          # nostril
        for x in range(8, 17):                          # mouth line
            p.put(x, 24 - (x < 10), shade(sk, -0.5), T_SKIN)
        return (14, 15, 22, 15)
    vol(p, cx, cy, 8.3, 9.8, sk, T_SKIN, bias=0.22)
    vol(p, cx - 1, 24.5, 5.2, 2.6, sk, T_SKIN, clip=lambda x, y: y > 22, bias=0.22)   # chin / jaw
    return (15, 17, 23, 17)                             # eye anchors (left, right)


def _hair(p, f):
    hc = f["hair"]
    st = f.get("hair_style", "short_swept")
    if f.get("scales"):
        return
    cx, cy = 19.5, 17.0
    below = lambda lim: (lambda x, y: y <= lim)
    if st != "cropped":
        vol(p, cx + 0.5, cy - 4.5, 9.4, 7.2, hc, T_HAIR, clip=below(12))
    else:
        vol(p, cx + 0.5, cy - 5, 8.8, 6.0, hc, T_HAIR, clip=below(11))
    # side locks (the far side, right, in shadow)
    if st in ("short_swept", "short_messy", "curls_short", "tied", "bob", "long", "braid", "curls"):
        vol(p, 27, 14, 2.4, 5.5, hc, T_HAIR, bias=-0.2)
        vol(p, 11.5, 13, 2.0, 4.5, hc, T_HAIR)
    if st == "short_swept":
        poly(p, [(10, 11), (19, 7), (24, 9), (16, 14), (12, 15)], hc, T_HAIR, (19, 10, 10, 6))
    elif st == "short_messy":
        for x0 in (11, 15, 19, 23):
            poly(p, [(x0, 10), (x0 + 2, 15), (x0 + 4, 10)], hc, T_HAIR, (19, 10, 10, 6))
        for x0 in (12, 18, 25):
            p.put(x0, 5, hc, T_HAIR)
    elif st == "bob":
        vol(p, 11, 18, 2.8, 8, hc, T_HAIR, bias=0.05)
        vol(p, 27.5, 18, 2.8, 8, hc, T_HAIR, bias=-0.25)
        poly(p, [(11, 10), (28, 10), (27, 13), (12, 13)], hc, T_HAIR, (19, 9, 10, 6))
    elif st in ("long", "braid"):
        vol(p, 10.5, 22, 2.8, 11, hc, T_HAIR, bias=0.05)
        vol(p, 28, 22, 3, 11, hc, T_HAIR, bias=-0.25)
        poly(p, [(12, 9), (27, 9), (22, 13), (14, 13)], hc, T_HAIR, (19, 9, 10, 6))
        if st == "braid":
            for i in range(5):
                vol(p, 31 + (i % 2) * 0.5, 26 + i * 3, 2, 1.8, hc, T_HAIR, bias=-0.1)
            p.put(31, 39, f.get("accent", hc), T_ACC)
    elif st == "tied":
        vol(p, 29.5, 12, 2.2, 2.2, hc, T_HAIR, bias=-0.1)
        vol(p, 31, 19, 1.6, 6, hc, T_HAIR, bias=-0.3)
        p.put(30, 14, (236, 236, 244, 255), T_ACC)
        p.put(31, 14, (200, 200, 214, 255), T_ACC)
        poly(p, [(11, 11), (18, 8), (21, 13), (13, 14)], hc, T_HAIR, (19, 10, 10, 6))
    elif st in ("curls", "curls_short"):
        pts = [(11, 9), (15, 6), (20, 5), (25, 6), (28, 9), (29, 13), (10, 13), (13, 11)]
        if st == "curls":
            pts += [(29, 18), (10, 18), (28, 22)]
        for (x, y) in pts:
            vol(p, x, y, 2.8, 2.6, hc, T_HAIR)
    # sheen band across the crown (FF6 hair highlight)
    hi = shade(hc, 0.55 if sum(hc[:3]) < 200 else 0.4)
    for x in range(12, 21):
        y = int(8 - (x - 12) * 0.15 + (0 if st != "cropped" else 0))
        if p.tag(x, y) == T_HAIR and (x + y) % 3:
            p.put(x, y, hi, T_HAIR)
    # hair shadow on the forehead
    for x in range(10, 30):
        for y in range(8, 20):
            if p.tag(x, y) == T_HAIR and p.tag(x, y + 1) == T_SKIN:
                p.put(x, y + 1, shade(p.get(x, y + 1), -0.25), T_SKIN)
                break


def _face(p, f, expr, anchors):
    sk = f["skin"]
    eye = f.get("eye", hexc("2a1a14"))
    lx, ly, rx, ry = anchors
    dark = shade(sk, -0.62)
    brow = shade(f.get("hair", dark), -0.3) if not f.get("scales") else shade(sk, -0.5)
    for (ex, ey, far) in ((lx, ly, False), (rx, ry, True)):
        w = 2 if far else 3
        for i in range(w):                               # sclera + iris + pupil + catchlight
            p.put(ex + i, ey, (236, 232, 222, 255) if i == 0 else eye, T_EYE)
            p.put(ex + i, ey + 1, shade(eye, -0.35) if i else (210, 200, 196, 255), T_EYE)
        p.put(ex + w - 1, ey, shade(eye, 0.5), T_EYE)
        for i in range(-1, w + 1):                       # upper lid line
            p.put(ex + i, ey - 1, dark, T_EYE)
        # brows by expression
        if expr == "neutral":
            by = [ey - 3] * (w + 1)
        elif expr == "concern":
            by = [ey - 3 + (1 if (i < 1 if far else i > w - 1) else 0) - (1 if (i >= w - 1 if not far else i < 1) else 0)
                  for i in range(w + 1)]
        else:
            by = [ey - 3 + (1 if (i >= w - 1 if not far else i < 1) else 0) for i in range(w + 1)]
        for i in range(w + 1):
            p.put(ex - 1 + i + (0 if not far else 1), by[i], brow, T_EYE)
    if not f.get("scales"):
        nx = 18
        p.put(nx, 20, shade(sk, 0.3), T_SKIN)
        p.put(nx + 1, 21, shade(sk, -0.35), T_SKIN)
        p.put(nx, 22, shade(sk, -0.4), T_SKIN)
        my = 24
        m = shade(sk, -0.5)
        if expr == "neutral":
            for x in (17, 18, 19):
                p.put(x, my, m, T_SKIN)
        elif expr == "concern":
            for x in (17, 18, 19):
                p.put(x, my + (x != 18) * 0, m, T_SKIN)
            p.put(16, my + 1, m, T_SKIN)
            p.put(20, my + 1, m, T_SKIN)
        else:
            for x in (16, 17, 18, 19, 20):
                p.put(x, my, m, T_SKIN)
            p.put(18, my + 1, shade(sk, -0.15), T_SKIN)
        p.put(14, 22, mix(sk, hexc("d86a5a"), 0.35), T_SKIN)    # cheek warmth
        p.put(22, 22, mix(sk, hexc("d86a5a"), 0.25), T_SKIN)
    elif expr == "determined":
        for x in range(9, 14):
            p.put(x, 24, (240, 236, 220, 255), T_EYE)            # bared teeth


def _extras(p, f):
    if f.get("beard"):
        vol(p, 19, 25, 6.5, 4.2, f["beard"], T_HAIR, clip=lambda x, y: y >= 23)
        for x in (17, 18, 19):
            p.put(x, 24, shade(f["skin"], -0.5), T_SKIN)
    if f.get("goggles"):
        g = f["goggles"]
        for x in range(11, 29):
            p.put(x, 10, shade(g, -0.45), T_ACC)
        vol(p, 15, 10, 2.8, 2.2, g, T_METAL)
        vol(p, 23, 10, 2.6, 2.2, g, T_METAL)
        p.put(14, 9, (255, 250, 220, 255), T_METAL)
        p.put(22, 9, (255, 250, 220, 255), T_METAL)
    if f.get("glasses"):
        gc = f["glasses"]
        for (x0, w) in ((13, 5), (21, 4)):
            for x in range(x0, x0 + w):
                p.put(x, 16, gc, T_ACC)
                p.put(x, 19, shade(gc, -0.3), T_ACC)
            p.put(x0, 17, gc, T_ACC)
            p.put(x0, 18, gc, T_ACC)
            p.put(x0 + w - 1, 17, gc, T_ACC)
            p.put(x0 + w - 1, 18, gc, T_ACC)
        p.put(18, 17, gc, T_ACC)
        p.put(19, 17, gc, T_ACC)
    if f.get("hat"):
        h = f["hat"]
        vol(p, 20, 9, 13, 2.6, h, T_ACC, bias=0.1)
        vol(p, 20.5, 5.5, 8, 4.5, h, T_ACC, clip=lambda x, y: y <= 8)
        for x in range(13, 28):
            p.put(x, 8, shade(h, -0.45), T_ACC)


def _outline(p):
    """Selective outline: silhouette edge pixels become a darkened version of themselves; one outer ring of a deep
    cool colour where the bust meets the background (FF6-like, never flat black)."""
    out = dict(p.c)
    for (x, y), c in p.c.items():
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in p.c and 0 <= n[0] < S and 0 <= n[1] < S and n not in out:
                out[n] = mix(shade(c, -0.8), (18, 14, 30, 255), 0.5)
    # interior material borders (hair vs skin, clothing vs skin) get a darker line on the shadow side
    for (x, y), c in p.c.items():
        t = p.t[(x, y)]
        for dx, dy in ((-1, 0), (0, -1)):
            nt = p.t.get((x + dx, y + dy))
            if nt is not None and nt != t and t in (T_SKIN,) and nt in (T_HAIR, T_BODY, T_ACC):
                out[(x, y)] = shade(c, -0.3)
    return out


def portrait(f, expr):
    p = P()
    _body(p, f)
    _neck(p, f)
    anchors = _head(p, f)
    _hair(p, f)
    _face(p, f, expr, anchors)
    _extras(p, f)
    px = _outline(p)
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    for (x, y), c in px.items():
        img.putpixel((x, y), tuple(c[:3]) + (255,))
    return img


def build(save):
    for key, f in list(FIG.items()) + list(NPCS.items()):
        img = Image.new("RGBA", (120, 40), (0, 0, 0, 0))
        for i, e in enumerate(["neutral", "concern", "determined"]):
            img.paste(portrait(f, e), (i * 40, 0))
        save(img, f"sprites/portraits/{key}.png", "portrait", "40x40 x3 (neutral, concern, determined)")
