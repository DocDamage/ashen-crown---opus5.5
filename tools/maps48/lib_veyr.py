"""Veyr group art (T01_POST, Veyr T02_*): composed buildings and shared stamps.

Buildings are composed once from one pack's wall, window, door and roof pieces (Medieval Siege & Castle building kit,
native 48px) into a single image, baked flat into the map ground (every cell of a building is solid, so nothing walks
behind it). Roofs are hipped: the south slope, a lit west hip, a shaded east hip, ridge cap and eave fascia, tiled
from the shingle swatch and recoloured (slate for the Crown March, never scaled)."""
import numpy as np
from PIL import Image, ImageDraw
import kit
from kit import st, Mat, C
from skins.lib_d import TintMat
import lib_r01 as A

kit.PACKS.setdefault("siege", "CuteSCKR/Medieval Siege & Castle Tileset/medieval siege")


def crop(alias, sheet, x, y, w, h):
    return kit.sheet_img(alias, sheet).crop((x, y, x + w, y + h))


def cell(alias, sheet, c, r, w=1, h=1):
    return crop(alias, sheet, c * C, r * C, w * C, h * C)


def recolour(im, mul=(1, 1, 1), desat=0.0, add=(0, 0, 0)):
    a = np.array(im.convert("RGBA")).astype(np.float32)
    rgb = a[..., :3]
    if desat:
        lum = (rgb * np.array([0.3, 0.59, 0.11])).sum(axis=2, keepdims=True)
        rgb = rgb * (1 - desat) + lum * desat
    rgb = rgb * np.array(mul, dtype=np.float32) + np.array(add, dtype=np.float32)
    a[..., :3] = np.clip(rgb, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def tile(src, W, H):
    out = Image.new("RGBA", (W, H))
    for y in range(0, H, src.height):
        for x in range(0, W, src.width):
            out.alpha_composite(src.crop((0, 0, min(src.width, W - x), min(src.height, H - y))), (x, y))
    return out


class Flat:
    """A composed image baked into the ground (kit treats anything with image() in Map.flat)."""
    flat = True

    def __init__(self, im):
        self.im = im

    def image(self):
        return self.im


def put(m, im, x, y, dx=0, dy=0):
    m.flat.append((Flat(im), x * C + dx, y * C + dy))


# ------------------------------------------------------------------------------------------------ building kit
ROOFS = {
    "slate": lambda: recolour(crop("siege", "5", 576, 96, 96, 45), mul=(0.70, 0.80, 1.00), desat=0.92, add=(4, 8, 22)),
    "slate_dark": lambda: recolour(crop("siege", "5", 576, 144, 96, 45), mul=(0.66, 0.74, 0.92), desat=0.92, add=(4, 8, 20)),
    "red": lambda: crop("siege", "5", 576, 96, 96, 45),
    "brown": lambda: crop("siege", "5", 576, 144, 96, 45),
    "moss": lambda: recolour(crop("siege", "5", 576, 144, 96, 45), mul=(0.62, 0.78, 0.55), desat=0.6, add=(0, 6, 0)),
}
ROWS = {  # one facade row (48 px tall), tiled horizontally
    "timber": lambda: crop("siege", "5", 385, 0, 191, 48),
    "timber2": lambda: crop("siege", "5", 385, 192, 191, 48),
    "stone": lambda: crop("siege", "5", 385, 144, 191, 48),
    "plank": lambda: crop("siege", "5", 385, 96, 191, 48),
    "frieze": lambda: recolour(crop("roman", "11", 480, 198, 288, 48), mul=(1.02, 0.97, 0.88)),
    "wstone": lambda: recolour(crop("siege", "5", 385, 144, 191, 48), mul=(1.12, 1.02, 0.84)),
    "grey_hi": lambda: crop("town", "6", 0, 672, 192, 48),
    "grey_lo": lambda: crop("town", "6", 0, 720, 192, 48),
}
WIN = {  # siege sheet 5 window cells
    "arch": (8, 5), "arch2": (9, 5), "arch3": (10, 5), "glass": (11, 5), "shut_open": (12, 5), "shut": (13, 5),
    "narrow": (12, 4), "square": (13, 4), "small": (8, 6), "shut2": (9, 6), "frame": (10, 6),
}
DOORS = {"plain": (11, 7), "arch": (12, 7), "tavern": (13, 7)}
CHIMNEY = ("town", "1", 330, 20, 30, 40)


def roof_img(W, H, kind="slate", seed=0):
    src = ROOFS[kind]()
    im = tile(src, W, H)
    a = np.array(im).astype(np.float32)
    ys, xs = np.mgrid[0:H, 0:W]
    t = ys / max(1, H - 1)
    mult = 1.10 - 0.22 * t
    ins0 = min(W * 0.26, H * 0.95)
    ins = (1 - t) * ins0
    left = xs < ins
    right = xs >= W - ins
    mult = np.where(left, mult * 1.14, mult)
    mult = np.where(right, mult * 0.70, mult)
    a[..., :3] = np.clip(a[..., :3] * mult[..., None], 0, 255)
    edge_l = np.abs(xs - ins) < 1.5
    edge_r = np.abs(xs - (W - ins)) < 1.5
    a[edge_l & (ys > 6), :3] = a[edge_l & (ys > 6), :3] * 0.55 + 90
    a[edge_r & (ys > 6), :3] *= 0.45
    im = Image.fromarray(a.astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    dark = (34, 32, 42, 255)
    cap = tuple(int(v) for v in np.clip(np.array(src.getpixel((20, 20))[:3]) * 1.25 + 12, 0, 255)) + (255,)
    d.rectangle((0, 0, W - 1, 1), fill=dark)
    d.rectangle((int(ins0), 2, int(W - ins0), 7), fill=cap)
    d.line((int(ins0), 8, int(W - ins0), 8), fill=dark)
    d.rectangle((0, 0, 1, H - 1), fill=dark)
    d.rectangle((W - 2, 0, W - 1, H - 1), fill=dark)
    d.rectangle((0, H - 5, W - 1, H - 1), fill=(46, 40, 44, 255))
    d.line((0, H - 6, W - 1, H - 6), fill=tuple(min(255, c + 30) for c in cap[:3]) + (255,))
    return im


def roof_hole(im, cx, cy, w):
    """Punch a collapsed patch into a roof image: dark void, broken rafters, ragged shingle edge (cell coords)."""
    im = im.copy()
    d = ImageDraw.Draw(im)
    x0, y0 = int(cx * C), int(cy * C)
    x1, y1 = x0 + int(w * C), y0 + 40
    pts = [(x0, y0 + 14), (x0 + 12, y0 + 2), (x0 + int(w * C * 0.45), y0 + 8), (x1 - 10, y0), (x1, y0 + 18),
           (x1 - 6, y1), (x0 + int(w * C * 0.55), y1 - 6), (x0 + 6, y1 - 2)]
    d.polygon(pts, fill=(22, 18, 22, 255), outline=(70, 60, 58, 255))
    for i in range(3):
        bx = x0 + 10 + i * max(10, int(w * C / 3))
        d.line((bx, y0 + 4, bx + 10, y1 - 4), fill=(96, 70, 48, 255), width=4)
        d.line((bx + 1, y0 + 4, bx + 11, y1 - 4), fill=(140, 104, 70, 255), width=1)
    d.line((x0 + 4, y0 + 20, x1 - 4, y0 + 16), fill=(110, 80, 54, 255), width=4)
    return im


def stain(im, amount=0.3, seed=0):
    """Flood tide mark: darkens and greens the lower part of an image (water line), leaving alpha untouched."""
    a = np.array(im).astype(np.float32)
    H = a.shape[0]
    rng = np.random.default_rng(seed)
    line = int(H * (1 - amount))
    ys = np.arange(H)[:, None]
    wav = (np.sin(np.arange(a.shape[1]) / 7.0 + seed) * 3).astype(int)[None, :]
    mask = ys >= (line + wav)
    a[..., 0] = np.where(mask, a[..., 0] * 0.66, a[..., 0])
    a[..., 1] = np.where(mask, a[..., 1] * 0.78, a[..., 1])
    a[..., 2] = np.where(mask, a[..., 2] * 0.62, a[..., 2])
    edge = np.abs(ys - (line + wav)) < 2
    a[..., :3] = np.where(edge[..., None], a[..., :3] * 0.5 + np.array([60, 66, 44]), a[..., :3])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


class Building:
    """w x (roof_rows + len(rows)) cells: a hipped roof over a facade of 48 px rows (top to bottom, ROWS styles).
    wins: per facade row, window style names cycled along the row (None = blank column); the bottom row skips door
    columns and their neighbours. doors: facade columns with a door (bottom row)."""

    def __init__(self, w, roof_rows=3, roof="slate", rows=("timber", "stone"), doors=(), door="plain",
                 wins=(("glass", None), ("shut", None, None)), chimneys=(), gables=(), seed=0, ledge=True, holes=(),
                 grime=0.0):
        self.w, self.rr, self.doors = w, roof_rows, list(doors)
        self.h = roof_rows + len(rows)
        W, RH = w * C, roof_rows * C
        im = Image.new("RGBA", (W, self.h * C))
        for i, r in enumerate(rows):
            im.alpha_composite(tile(ROWS[r](), W, C), (0, RH + i * C))
        a = np.array(im).astype(np.float32)
        if ledge:
            for i in range(1, len(rows)):
                y0 = RH + i * C
                a[y0 - 3:y0 - 1, :, :3] = a[y0 - 3:y0 - 1, :, :3] * 0.5 + 110
                a[y0 - 1:y0 + 2, :, :3] *= 0.55
        a[RH:RH + 10, :, :3] *= np.linspace(0.45, 1.0, 10)[:, None, None]
        a[-4:, :, :3] *= 0.68
        im = Image.fromarray(a.astype(np.uint8), "RGBA")
        last = len(rows) - 1
        for i in range(len(rows)):
            wl = wins[i] if i < len(wins) else None
            for cx in range(w):
                if i == last and cx in self.doors:
                    im.alpha_composite(cell("siege", "5", *DOORS[door]), (cx * C, RH + i * C))
                    continue
                if not wl or not (0 < cx < w - 1):
                    continue
                if i == last and (cx - 1 in self.doors or cx + 1 in self.doors):
                    continue
                wn = wl[(cx + seed) % len(wl)]
                if wn:
                    im.alpha_composite(cell("siege", "5", *WIN[wn]), (cx * C, RH + i * C))
        rf = roof_img(W, RH + 6, roof, seed)
        for (hx, hy, hw) in holes:
            rf = roof_hole(rf, hx, hy, hw)
        im.alpha_composite(rf, (0, 0))
        if grime:
            im = stain(im, grime, seed)
        for gx in gables:
            im.alpha_composite(cell("siege", "5", 14, 2, 2, 1), (gx * C, RH - 30))
        self.smoke = []
        for cx in chimneys:
            px = cx * C + 9
            im.alpha_composite(crop(*CHIMNEY), (px, 2))
            self.smoke.append((px - 9, -60))
        self.im = im

    def place(self, m, x, y, smoke=True):
        put(m, self.im, x, y)
        for yy in range(y, y + self.h):
            for xx in range(x, x + self.w):
                m.solid(xx, yy, "roof" if yy < y + self.rr else "house")
        for d in self.doors:
            m.solid(x + d, y + self.h - 1, "door")
        if smoke:
            for (px, py) in self.smoke:
                m.anims.append(("chimney_smoke", x * C + px, y * C + py, y * C + self.h * C))
        return self


# ------------------------------------------------------------------------------------------------ shared stamps
TORCH_STAND = A.TORCH_STAND
LAMP_POST = st("siege", "5", 11, 8, 1, 2, kind="lamp")
LAMP_TORCH = st("siege", "5", 10, 8, 1, 2, kind="lamp")
NOTICE_B = st("siege", "5", 12, 8, 2, 2, kind="sign")
CARTS = [st("siege", "5", 8, 10, 2, 2, kind="cart"), st("siege", "5", 10, 10, 2, 2, kind="cart"), st("siege", "5", 12, 10, 2, 2, kind="cart")]
BASKETS = [st("siege", "5", c, r, kind="crate") for c in (8, 9, 10, 11) for r in (14, 15)]
BARREL_PILE = [st("siege", "5", 12, 12, 2, 2, kind="barrel"), st("siege", "5", 14, 12, 2, 2, kind="barrel")]
MUG_SIGN = st("siege", "5", 3, 9, 1, 1, solid=0)
STALLS_S = [st("siege", "5", 4, 12, 2, 2, kind="counter"), st("siege", "5", 6, 12, 2, 2, kind="counter"), st("siege", "5", 4, 14, 2, 2, kind="counter")]
SHED_HAY = [st("siege", "5", 8, 12, 2, 2, kind="house"), st("siege", "5", 10, 12, 2, 2, kind="house")]
# roman civic set (warm stone)
FOUNTAIN_BIG = st("roman", "4", 0, 0, 4, 4, solid=3, cols=(0, 3), kind="well")
FOUNTAIN_BROKEN = st("roman", "4", 4, 0, 4, 4, solid=3, cols=(0, 3), kind="well")
STATUE_A = st("roman", "4", 8, 0, 2, 4, solid=1, kind="statue")
STATUE_B = st("roman", "4", 11, 0, 2, 4, solid=1, kind="statue")
STELE = st("roman", "4", 13, 1, 2, 3, solid=1, kind="statue")
PLINTH = st("roman", "4", 8, 5, 2, 3, solid=1, kind="statue")
PLINTH_MOSS = st("roman", "4", 11, 5, 2, 3, solid=1, kind="statue")
STONE_BENCHES = [st("roman", "4", 0, 4, 4, 2, kind="bench"), st("roman", "4", 4, 5, 4, 1, kind="bench"), st("roman", "4", 0, 7, 4, 1, kind="bench")]
BROKEN_BENCH = [st("roman", "4", 4, 7, 2, 1, kind="rubble"), st("roman", "4", 6, 7, 2, 1, kind="rubble")]
ARCH = st("roman", "4", 0, 8, 4, 4, solid=1, kind="pillar")
ARCH_DMG = st("roman", "4", 4, 8, 4, 4, solid=1, kind="pillar")
ARCH_RUIN = st("roman", "4", 8, 8, 4, 4, solid=1, kind="pillar")
COLUMN = st("roman", "4", 13, 8, 2, 4, solid=1, cols=(0, 1), kind="pillar")
COLONNADE = st("roman", "11", 0, 6, 7, 2, solid=1, kind="pillar")
PLANTER = st("roman", "11", 3, 9, 3, 2, solid=1, kind="garden")
BENCH_BIG = st("roman", "11", 10, 9, 2, 2, solid=1, kind="bench")
PEDESTAL_BIG = st("roman", "11", 0, 12, 3, 3, solid=2, kind="statue")
STAIRS_R = st("roman", "11", 10, 6, 2, 2, solid=0, flat=True)
URNS = [st("roman", "16", c, r, kind="barrel") for (c, r) in ((10, 12), (11, 12), (10, 13), (11, 13), (12, 12), (15, 12))]
BUSTS = [st("roman", "16", 6, 2, 1, 2, kind="statue"), st("roman", "16", 7, 2, 1, 2, kind="statue")]
STATUES_S = [st("roman", "16", 6, 0, 1, 2, kind="statue"), st("roman", "16", 7, 0, 1, 2, kind="statue")]
FOUNTAINS_S = [st("roman", "16", 0, 0, 2, 2, kind="well"), st("roman", "16", 2, 0, 2, 2, kind="well"), st("roman", "16", 0, 4, 2, 2, kind="well")]
BASIN = [st("roman", "16", 0, 2, 2, 2, kind="well"), st("roman", "16", 4, 2, 2, 2, kind="well")]
COL_STUB = [st("roman", "16", 8, 8, 1, 2, kind="pillar"), st("roman", "16", 9, 8, 1, 2, kind="pillar"), st("roman", "16", 10, 8, 1, 2, kind="pillar")]
FLAGPOLES = [st("castle", "5", c, 10, 2, 4, solid=1, cols=(0, 0), kind="lamp") for c in (0, 2, 4, 6)]


# ------------------------------------------------------------------------------------------------ materials
MATS = dict(A.MATS)
MATS.update(
    flag=TintMat([("roman", "1", 480, 0, 288, 192)], "path", mul=(1.04, 1.0, 0.92), prio=2),
    flag_big=TintMat([("roman", "1", 288, 192, 96, 192)], "path", mul=(1.04, 1.0, 0.92), prio=2),
    cobble_r=TintMat([("roman", "1", 384, 192, 192, 192)], "path", mul=(1.02, 0.98, 0.9), prio=2),
    pebble=Mat([("roman", "1", 576, 384, 192, 96)], "path", prio=2),
    mossflag=Mat([("roman", "1", 0, 480, 384, 96)], "path", prio=2),
    stairs_w=TintMat([("roman", "11", 504, 288, 48, 96)], "stairs", mul=(1.02, 0.98, 0.9)),
    stairs_g=Mat([("town", "1", 408, 384, 48, 96)], "stairs"),
    canal=Mat([("fa", "water_deep", 0, 0, 48, 48)], "water"),
    shallow=Mat([("fa", "water_shallow", 0, 0, 48, 48)], "shallow", organic=True, prio=0),
    silt=TintMat([("town", "2", 192, 0, 96, 192)], "path", mul=(0.74, 0.74, 0.6), organic=True, prio=1),
    silt_d=TintMat([("town", "2", 192, 0, 96, 192)], "path", mul=(0.56, 0.58, 0.48), organic=True, prio=1),
    mud=TintMat([("forest", "3", 96, 672, 96, 96)], "path", mul=(0.7, 0.72, 0.6), organic=True, prio=1),
    wetgrass=TintMat([("town", "2", 288, 0, 96, 192)], "grass", mul=(0.84, 0.8, 0.5), add=(14, 10, 0), organic=True, prio=3),
    planks=Mat([("town", "6", 192, 576, 96, 96)], "bridge"),
    slabs=Mat([("town", "1", 0, 384, 336, 96)], "floor", prio=2),
    bridge_s=TintMat([("town", "1", 0, 384, 336, 96)], "bridge", mul=(1.02, 0.98, 0.9)),
    dark=Mat([("color", (16, 14, 20))], "void"),
    flag_o=TintMat([("roman", "1", 480, 0, 288, 192)], "path", mul=(0.9, 0.92, 0.84), organic=True, prio=2),
    cob_o=TintMat([("roman", "1", 384, 192, 192, 192)], "path", mul=(0.88, 0.9, 0.8), organic=True, prio=2),
    flood=Mat([("fa", "water_deep", 0, 0, 48, 48)], "water", organic=True, prio=0),
    stairs_o=TintMat([("roman", "11", 504, 288, 48, 96)], "stairs", mul=(0.9, 0.92, 0.84)),
)

STONE_FACE = lambda: crop("town", "6", 0, 672, 192, 96)
WALL_WARM = lambda: crop("castle", "2", 0, 384, 384, 96)      # crenellated warm curtain wall, 8 x 2


def roof_strip(m, x, y, w, h, kind="slate", chimneys=()):
    im = roof_img(w * C, h * C, kind)
    for cx in chimneys:
        im.alpha_composite(crop(*CHIMNEY), (cx * C + 9, 4))
    put(m, im, x, y)
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            m.solid(xx, yy, "roof")


def canal_h(m, x0, x1, ywall, yw1, bridges=()):
    """East-west canal: quay wall face on row ywall (solid), water rows ywall+1..yw1, coping on the south quay."""
    W = (x1 - x0 + 1) * C
    face = tile(STONE_FACE(), W, 96).crop((0, 30, W, 78))
    a = np.array(face).astype(np.float32)
    a[:6, :, :3] = a[:6, :, :3] * 0.6 + 80
    a[6:8, :, :3] *= 0.5
    a[-8:, :, :3] *= np.linspace(1.0, 0.45, 8)[:, None, None]
    put(m, Image.fromarray(a.astype(np.uint8), "RGBA"), x0, ywall)
    m.rect("canal", x0, ywall + 1, x1, yw1)
    for x in range(x0, x1 + 1):
        m.solid(x, ywall, "wall")
    lip = tile(crop("town", "6", 0, 672, 192, 12), W, 10)
    la = np.array(lip).astype(np.float32)
    la[:, :, :3] = la[:, :, :3] * 0.8 + 30
    la[-2:, :, :3] *= 0.5
    put(m, Image.fromarray(la.astype(np.uint8), "RGBA"), x0, yw1 + 1)
    skip = set()
    for (bx0, bx1) in bridges:
        bridge_v(m, bx0, bx1, ywall, yw1)
        skip |= {(x, y) for x in range(bx0, bx1 + 1) for y in range(ywall, yw1 + 1)}
    for y in range(ywall + 1, yw1 + 1):
        for x in range(x0, x1 + 1):
            if (x, y) not in skip:
                m.anim("water_deep", x, y, h=48, flat=True)


def bridge_v(m, x0, x1, y0, y1, mat="bridge_s"):
    m.rect(mat, x0, y0, x1, y1)
    Wd, Hd = (x1 - x0 + 1) * C, (y1 - y0 + 1) * C
    im = Image.new("RGBA", (Wd + 24, Hd + 12))
    d = ImageDraw.Draw(im)
    for (px, lit) in ((0, True), (Wd + 12, False)):
        d.rectangle((px, 0, px + 11, Hd + 11), fill=(150, 140, 124, 255) if lit else (118, 108, 96, 255))
        d.rectangle((px, 0, px + 11, 3), fill=(196, 186, 168, 255))
        d.rectangle((px + (11 if lit else 0), 0, px + (11 if lit else 0), Hd + 11), fill=(60, 54, 50, 255))
        for py in range(8, Hd, 48):
            d.rectangle((px - 1, py, px + 12, py + 12), fill=(170, 160, 140, 255), outline=(70, 62, 56, 255))
    put(m, im, x0, y0, dx=-12, dy=-6)


def warm_wall(m, x0, x1, y0, rows=3):
    """Crenellated warm curtain wall, rows tall (crenels + face), solid."""
    src = WALL_WARM()
    W = (x1 - x0 + 1) * C
    top = tile(src.crop((0, 0, 384, 96)), W, 96)
    im = Image.new("RGBA", (W, rows * C))
    im.alpha_composite(top, (0, 0))
    for r in range(2, rows):
        im.alpha_composite(tile(src.crop((0, 48, 384, 96)), W, 48), (0, r * C))
    put(m, im, x0, y0)
    for y in range(y0, y0 + rows):
        for x in range(x0, x1 + 1):
            m.solid(x, y, "wall")


def recoloured(alias, sheet, c, r, w, h, **kw):
    return recolour(cell(alias, sheet, c, r, w, h), **kw)


def flat_obj(m, im, x, y, solid_rows=None, kind="house", door=None, dx=0, dy=0):
    """Composite image baked flat; solid_rows from the bottom (None = all rows)."""
    put(m, im, x, y, dx, dy)
    w, h = im.width // C, im.height // C
    rows = h if solid_rows is None else solid_rows
    for yy in range(y + h - rows, y + h):
        for xx in range(x, x + w):
            m.solid(xx, yy, kind)
    if door:
        m.solid(x + door[0], y + door[1], "door")


# market stalls (Medieval Town sheet 11): 2 x 2, awning over a counter
STALL = {n: st("town", "11", c, r, 2, 2, solid=1, kind="counter") for n, (c, r) in {
    "cloth": (0, 0), "cloth2": (2, 0), "fruit": (4, 0), "pots": (6, 0), "herbs": (8, 0), "herbs2": (10, 0),
    "jars": (12, 0), "honey": (14, 0), "fabric": (0, 2), "fabric2": (2, 2), "produce": (4, 2), "veg": (6, 2),
    "meat": (8, 2), "bread": (10, 2), "grain": (12, 2), "jam": (14, 2), "cloth3": (0, 4), "cloth4": (2, 4),
    "veg2": (4, 4), "veg3": (6, 4), "meat2": (8, 4), "bread2": (10, 4), "fruit2": (12, 4), "greens": (14, 4),
    "jewel": (0, 8), "jewel2": (2, 8), "weapons": (8, 8), "blades": (10, 8), "arms": (12, 8), "tools": (14, 8),
    "pottery": (0, 10), "pottery2": (4, 10), "rugs": (10, 10), "baskets": (14, 10)}.items()}
BANNER = [st("town", "7", c, 10, 1, 2, solid=0) for c in range(0, 10)]
TAPESTRY = [st("town", "7", 10, 10, 2, 2, solid=0), st("town", "7", 12, 10, 2, 2, solid=0)]
SACKS2 = [st("town", "7", 4, 12, 2, 2, kind="crate"), st("town", "7", 0, 14, 2, 2, kind="crate")]
JARS = [st("town", "7", c, 12, 1, 2, kind="barrel") for c in (0, 1, 2, 3)]
LANTERNS = [st("town", "7", 6, 13, 1, 1, kind="lamp"), st("town", "7", 8, 13, 1, 1, kind="lamp")]
FLOWERPOTS = [st("castle", "7", 5, 12, 1, 1, kind="barrel"), st("castle", "7", 4, 12, 1, 2, kind="barrel"), st("castle", "7", 7, 8, 1, 2, kind="barrel")]
TOPIARY = [st("castle", "7", 5, 14, 1, 2, kind="hedge"), st("castle", "7", 6, 14, 1, 2, kind="hedge"), st("castle", "7", 7, 13, 1, 3, kind="hedge")]
SHIELD_SIGNS = [st("castle", "7", 8, 10, 1, 1, solid=0), st("castle", "7", 9, 10, 1, 1, solid=0), st("castle", "7", 10, 10, 1, 1, solid=0)]
ROWBOAT = st("sea", "2", 0, 14, 2, 1, solid=0)

GATE_FACADE = lambda: cell("castle", "5", 0, 0, 4, 3)          # double doors between banner towers
STATUES_K = [st("castle", "7", c, 6, 1, 2, kind="statue") for c in range(8, 16)]
THRONE = st("castle", "7", 0, 0, 4, 4, solid=2, kind="statue")


def parapet(m, x0, x1, y, shade=1.0):
    """One-row crenellated parapet (warm stone) along row y, solid."""
    src = WALL_WARM().crop((0, 0, 384, 60))
    W = (x1 - x0 + 1) * C
    im = tile(src, W, 60)
    if shade != 1.0:
        im = recolour(im, mul=(shade, shade, shade))
    put(m, im, x0, y, dy=-12)
    for x in range(x0, x1 + 1):
        m.solid(x, y, "wall")


def stairwell(m, x, y):
    """A stair going down into the paving (cellar entrance), one cell; the cell stays walkable."""
    im = Image.new("RGBA", (C, C))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, C - 1, C - 1), fill=(150, 138, 118, 255))
    d.rectangle((4, 4, C - 5, C - 1), fill=(24, 20, 24, 255))
    for i, yy in enumerate(range(8, C, 8)):
        v = max(30, 120 - i * 18)
        d.rectangle((5, yy, C - 6, yy + 3), fill=(v, v - 8, v - 16, 255))
    d.rectangle((0, 0, C - 1, 3), fill=(186, 174, 150, 255))
    d.rectangle((0, 0, 3, C - 1), fill=(170, 158, 136, 255))
    d.rectangle((C - 4, 0, C - 1, C - 1), fill=(96, 86, 76, 255))
    put(m, im, x, y)


# ruins and camp (Battlefield & Ruins, Army Camp; native 48px)
RUIN_SLATE_HOUSE = st("ruins", "9", 0, 8, 4, 4, solid=2, kind="rubble")
RUIN_STONE_HOUSE = st("ruins", "9", 4, 8, 4, 4, solid=2, kind="rubble")
RUIN_RED_HOUSE = st("ruins", "9", 0, 0, 4, 4, solid=2, kind="rubble")
RUIN_WALLS = [st("ruins", "9", 8, 0, 2, 4, solid=2, kind="wall"), st("ruins", "9", 10, 0, 2, 4, solid=2, kind="wall"),
              st("ruins", "9", 12, 0, 4, 4, solid=2, kind="wall"), st("ruins", "9", 8, 4, 2, 4, solid=2, kind="wall"),
              st("ruins", "9", 10, 4, 2, 4, solid=2, kind="wall")]
RUIN_LOW = [st("ruins", "1", 0, 0, 2, 2, kind="wall"), st("ruins", "1", 2, 0, 3, 2, kind="wall"), st("ruins", "1", 5, 0, 3, 2, kind="wall"),
            st("ruins", "1", 0, 6, 2, 2, kind="wall"), st("ruins", "1", 2, 6, 2, 2, kind="wall"), st("ruins", "9", 4, 12, 2, 2, kind="wall"),
            st("ruins", "9", 6, 12, 2, 2, kind="wall")]
RUBBLE = [st("ruins", "9", 14, 4, 2, 2, kind="rubble"), st("ruins", "9", 2, 14, 2, 2, kind="rubble"),
          st("ruins", "9", 8, 14, 1, 1, kind="rubble"), st("ruins", "1", 5, 6, 1, 2, kind="rubble")]
BROKEN_CART = [st("ruins", "9", 0, 12, 2, 2, kind="cart"), st("ruins", "9", 2, 12, 2, 2, kind="cart"), st("ruins", "9", 12, 4, 2, 2, kind="cart")]
COL_RUIN = [st("ruins", "1", 1, 14, 1, 2, kind="pillar"), st("ruins", "1", 2, 14, 1, 2, kind="pillar"), st("ruins", "1", 3, 14, 1, 2, kind="pillar")]
TENTS = [st("camp", "2", c, 0, 2, 2, solid=1, kind="tent") for c in (8, 10, 12, 14)] + [st("camp", "2", c, 4, 2, 2, solid=1, kind="tent") for c in (0, 2, 4)]
COTS = [st("camp", "2", c, 8, 1, 2, kind="bed") for c in (0, 2, 4)]
BEDROLLS = [st("camp", "2", c, 8, 1, 1, kind="bed") for c in (3, 5)]
CAULDRON = [st("camp", "2", 0, 10, 2, 2, kind="brazier"), st("camp", "2", 2, 10, 2, 2, kind="brazier")]
CAMPFIRE = st("camp", "2", 0, 12, 2, 2, kind="brazier")
MAP_TABLE = st("camp", "2", 4, 10, 2, 2, kind="table")
CANOPY = st("camp", "2", 8, 8, 4, 4, solid=0)
CAMP_CHESTS = [st("camp", "2", 0, 14, 1, 1, kind="crate"), st("camp", "2", 2, 14, 1, 1, kind="barrel"), st("camp", "2", 4, 14, 1, 1, kind="crate")]
LADDER = st("town", "6", 14, 12, 1, 2, solid=0, flat=True)

# ------------------------------------------------------------------------------------------------ underways (canals)
from skins import lib_quarry as Q
UMATS = dict(
    quay=Mat([("dungeon", "4", 0, 576, 384, 96)], "floor", prio=2),
    mossy=Mat([("dungeon", "1", 480, 480, 96, 96)], "floor2", prio=1),
    cob=Mat([("dungeon", "1", 192, 384, 96, 288)], "floor", prio=1),
    tiles=Mat([("dungeon", "1", 48, 96, 144, 192)], "floor", prio=2),
    cap=TintMat([("dungeon", "1", 192, 384, 96, 288)], "wall", mul=(0.32, 0.33, 0.38)),
    void=Mat([("color", (12, 10, 16))], "void"),
    canal=Mat([("fa", "water_deep", 0, 0, 48, 48)], "water"),
    archive=TintMat([("dungeon", "1", 192, 96, 192, 192)], "floor2", mul=(0.8, 0.84, 0.8), prio=1),
)
BRICK_FACE = lambda: crop("dungeon", "1", 48, 0, 288, 96)
ARCADE_BARS = lambda: crop("dungeon", "7", 384, 0, 384, 96)
GRATE_WALL = lambda: crop("dungeon", "7", 0, 288, 384, 96)
FILING = [st("town", "9", 8, 2, 2, 2, kind="shelf"), st("town", "9", 10, 2, 2, 2, kind="shelf")]
IRON_FENCE = st("dungeon", "6", 4, 6, 4, 2, solid=1, kind="fence")
PORTCULLIS_D = lambda: cell("dungeon", "4", 6, 0, 2, 2)
DOOR_D = lambda: cell("dungeon", "4", 4, 0, 2, 2)
PILLAR_D = st("dungeon", "6", 8, 12, 1, 2, kind="pillar")
ARCH_D = st("dungeon", "6", 12, 12, 2, 2, solid=1, kind="pillar")
ARCH_BROKEN_D = st("dungeon", "6", 9, 12, 2, 2, solid=1, kind="pillar")
PILLAR_STUB_D = st("dungeon", "6", 11, 12, 1, 2, kind="pillar")


def over_dark(im, colour=(14, 12, 18)):
    bg = Image.new("RGBA", im.size, colour + (255,))
    bg.alpha_composite(im)
    return bg


def wall_face(m, x0, x1, y, pattern, rows=2):
    """Brick face along rows y..y+rows-1 from segments: 'brick' (mossy brick), 'bars' (arcade of barred culverts)."""
    W = (x1 - x0 + 1) * C
    im = Image.new("RGBA", (W, rows * C))
    x = 0
    i = 0
    while x < W:
        seg = pattern[i % len(pattern)]
        src = over_dark(BRICK_FACE() if seg == "brick" else ARCADE_BARS() if seg == "bars" else GRATE_WALL())
        src = src.crop((0, 96 - rows * C, src.width, 96)) if rows < 2 else src
        im.alpha_composite(src, (x, 0))
        x += src.width
        i += 1
    a = np.array(im).astype(np.float32)
    a[:4, :, :3] = a[:4, :, :3] * 0.5 + 70
    a[-6:, :, :3] *= np.linspace(1.0, 0.5, 6)[:, None, None]
    put(m, Image.fromarray(a.astype(np.uint8), "RGBA"), x0, y)
    for yy in range(y, y + rows):
        for xx in range(x0, x1 + 1):
            m.solid(xx, yy, "wall")


def quay_edge(m, x0, x1, y, face=True):
    """Lit stone edge where a walkway meets the water below row y (drawn on the walkway's last 14 px)."""
    W = (x1 - x0 + 1) * C
    src = crop("dungeon", "1", 48, 60, 288, 36)
    im = tile(src, W, 14 if face else 6)
    a = np.array(im).astype(np.float32)
    a[:2, :, :3] = a[:2, :, :3] * 0.4 + 120
    a[-2:, :, :3] *= 0.4
    put(m, Image.fromarray(a.astype(np.uint8), "RGBA"), x0, y, dy=C - (14 if face else 6) if face else 0)


def submerged_walk(m, x0, x1, y0, y1):
    """A lowered plank walkway seen through the water (the crossing a lock gate raises)."""
    W, H = (x1 - x0 + 1) * C, (y1 - y0 + 1) * C
    water = tile(crop("fa", "water_deep", 0, 0, 48, 48), W, H)
    planks = recolour(tile(crop("town", "6", 192, 576, 96, 96), W - 12, H), mul=(0.45, 0.62, 0.8), add=(0, 10, 30))
    pa = np.array(planks)
    pa[..., 3] = 175
    water.alpha_composite(Image.fromarray(pa, "RGBA"), (6, 0))
    d = ImageDraw.Draw(water)
    for yy in range(0, H, 96):
        for xx in (4, W - 10):
            d.rectangle((xx, yy + 10, xx + 6, yy + 22), fill=(40, 56, 70, 255))
    put(m, water, x0, y0)


def bridge_h(m, x0, x1, y0, y1, mat="planks", gaps=(), posts_only=False):
    """East-west timber footbridge: planks on rows y0..y1, a rail along both edges; gaps = columns missing planks
    (drawn as open joists over the water, still marked as bridge for the grid when rebuilt)."""
    m.rect(mat, x0, y0, x1, y1)
    Wd, Hd = (x1 - x0 + 1) * C, (y1 - y0 + 1) * C
    im = Image.new("RGBA", (Wd, Hd + 20))
    d = ImageDraw.Draw(im)
    for gx in gaps:
        gx0 = (gx - x0) * C
        wat = crop("fa", "water_deep", 0, 0, 48, 48)
        for yy in range(y0, y1 + 1):
            im.paste(wat, (gx0, 12 + (yy - y0) * C))
        for jy in range(18, Hd + 10, 30):
            d.rectangle((gx0, jy, gx0 + C - 1, jy + 5), fill=(92, 64, 40, 255), outline=(52, 36, 24, 255))
    for (yy, h) in ((4, 8), (Hd + 8, 8)):
        if not posts_only:
            d.rectangle((0, yy, Wd - 1, yy + 4), fill=(126, 88, 54, 255), outline=(60, 40, 26, 255))
        for px in range(6, Wd, 48):
            d.rectangle((px, yy - 6, px + 7, yy + h), fill=(104, 72, 44, 255), outline=(52, 36, 24, 255))
    put(m, im, x0, y0, dy=-12)


LAUNDRY = [st("island", "4", 11, 4, 2, 2, kind="laundry"), st("island", "4", 10, 12, 2, 2, kind="laundry")]
DEAD_TREE = st("dungeon", "3", 12, 0, 2, 3, solid=1, cols=(0, 1), kind="tree")
SMALL_TABLE = st("town", "15", 10, 4, 1, 1, kind="table")
CANDLES = st("town", "7", 4, 0, 1, 2, kind="lamp")

WOODPILE = [st("town", "3", 12, 14, 1, 1, kind="crate"), st("town", "3", 13, 14, 1, 1, kind="crate")]
TOOLS = st("town", "3", 13, 13, 2, 2, kind="crate")
LOG_BIG = st("forest", "2", 10, 11, 2, 1, kind="rock")
DEAD_BUSH = [st("forest", "3", 4, 7, 1, 1, kind="hedge"), st("forest", "3", 5, 7, 1, 1, kind="hedge")]
FERNS = [st("forest", "2", c, 13, 1, 1, solid=0) for c in (8, 9, 10, 11, 12)] + [st("forest", "2", c, 14, 1, 1, solid=0) for c in (8, 9, 10)]
TOWER_BLUE = st("town", "17", 0, 3, 2, 3, solid=3, kind="wall")
MOOR = st("pirate", "B1-1", 7, 14, 1, 1, kind="lamp")
ROPE = st("pirate", "B1-1", 10, 14, 1, 1, kind="crate")
