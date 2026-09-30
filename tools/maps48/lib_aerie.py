"""Shared pieces for the 'aerie' group (High Aerie T05_*, Nacre T06_*).

Composed buildings: the owner's CuteSCKR packs have modular house kits (Medieval Siege sheet 5: timber panels, plank
and stone rows, windows, doors, roof tiles, gables; Roman Empire sheet 5: sandstone storeys and terracotta roofs).
Main buildings are assembled here from those pieces at 1:1 (pieces are cut, repeated and recoloured, never scaled)
and written once as sheets under tools/maps48/gen_aerie/ (pack alias "aeriegen"), so they are placed like any other
stamp (y-sorted, walk-behind)."""
import os
import numpy as np
from PIL import Image
import kit
from kit import st, Stamp, Mat, C

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "gen_aerie")
os.makedirs(GEN, exist_ok=True)
kit.PACKS["aeriegen"] = GEN


# ------------------------------------------------------------------------------------------ image helpers
def piece(alias, sheet, x, y, w, h):
    return kit.sheet_img(alias, sheet).crop((x, y, x + w, y + h))


def put(dst, im, x, y):
    """alpha_composite with clipping."""
    W, H = dst.size
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + im.width), min(H, y + im.height)
    if x1 <= x0 or y1 <= y0:
        return
    dst.alpha_composite(im.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def tile(dst, im, x0, y0, x1, y1):
    for y in range(y0, y1, im.height):
        for x in range(x0, x1, im.width):
            put(dst, im.crop((0, 0, min(im.width, x1 - x), min(im.height, y1 - y))), x, y)


def recolor(im, hue_from=((0, 30), (235, 256)), hue=150, sat=0.35, val=0.95, min_sat=50):
    """Hue-shift the saturated pixels in the given hue ranges (PIL HSV, 0..255): red tiles -> slate blue."""
    a = np.array(im)
    hsv = np.array(im.convert("RGB").convert("HSV")).astype(np.float32)
    h, s = hsv[..., 0], hsv[..., 1]
    m = np.zeros(h.shape, bool)
    for lo, hi in hue_from:
        m |= (h >= lo) & (h < hi)
    m &= s > min_sat
    hsv[..., 0] = np.where(m, hue, h)
    hsv[..., 1] = np.where(m, s * sat, s)
    hsv[..., 2] = np.where(m, np.clip(hsv[..., 2] * val, 0, 255), hsv[..., 2])
    rgb = np.array(Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB"))
    out = np.concatenate([rgb, a[..., 3:4]], axis=2)
    return Image.fromarray(out, "RGBA")


def tint(im, mul=(1, 1, 1), add=(0, 0, 0)):
    a = np.array(im).astype(np.float32)
    a[..., :3] = np.clip(a[..., :3] * np.array(mul, np.float32) + np.array(add, np.float32), 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


_SNOW = None


def snow_cap(im, x0, x1, y_of_x, depth=10, seed=1):
    """Paint snow over the opaque pixels from y_of_x(x) down `depth` (+-3) px (ridges, sills, wall tops)."""
    global _SNOW
    if _SNOW is None:
        from skins import lib_cold  # noqa: registers the generated snow swatch
        _SNOW = np.array(kit.sheet_img("dreamy", "gen_snow"))
    rng = np.random.default_rng(seed)
    a = np.array(im)
    d = depth + np.round(np.convolve(rng.normal(0, 2.2, x1 - x0 + 8), np.ones(5) / 5, "same")).astype(int)
    for i, x in enumerate(range(x0, x1)):
        if not (0 <= x < a.shape[1]):
            continue
        yt = y_of_x(x)
        if yt is None:
            continue
        dd = max(2, d[i + 4])
        for y in range(max(0, yt), min(a.shape[0], yt + dd)):
            if a[y, x, 3] > 0:
                a[y, x, :3] = _SNOW[y % 384, x % 384, :3]
        yb = yt + dd
        if 0 <= yb < a.shape[0] and a[yb, x, 3] > 0:
            a[yb, x, :3] = (a[yb, x, :3] * 0.55 + np.array([120, 136, 170]) * 0.45).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def shade_rect(im, x0, y0, x1, y1, k=0.6):
    a = np.array(im).astype(np.float32)
    a[y0:y1, x0:x1, :3] *= k
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def outline(im, color=(34, 28, 36, 255)):
    """1px dark outline around the opaque shape (pixel-art edge)."""
    a = np.array(im)
    op = a[..., 3] > 0
    edge = op & ~(np.roll(op, 1, 0) & np.roll(op, -1, 0) & np.roll(op, 1, 1) & np.roll(op, -1, 1))
    edge[0, :] |= op[0, :]
    a[edge] = color
    return Image.fromarray(a, "RGBA")


def save_sheet(name, im):
    """Write gen_aerie/<name>.png only when the pixels changed (keeps mtimes stable)."""
    p = os.path.join(GEN, name + ".png")
    if os.path.exists(p):
        try:
            old = np.array(Image.open(p).convert("RGBA"))
            if old.shape == np.array(im).shape and (old == np.array(im)).all():
                kit._img_cache[("aeriegen", name)] = im
                return
        except Exception:
            pass
    im.save(p)
    kit._img_cache[("aeriegen", name)] = im


def gen(name, im, solid=2, door=None, kind="house", cols=None, base=None):
    """Save a composed image (size in whole cells) and return its stamp."""
    save_sheet(name, im)
    return Stamp("aeriegen", name, 0, 0, px=(0, 0, im.width, im.height), solid=solid, door=door, kind=kind,
                 cols=cols, base=base)


# ------------------------------------------------------------------------------------------ Siege 5 house kit
S5 = ("siege", "5")
PANEL_TOP = (385, 0, 191, 48)      # timber-and-plaster, curved braces (1 row)
PANEL_ROW = (385, 192, 191, 48)    # timber panels, 1 row
PANEL_X = (481, 48, 95, 48)        # X-braced panel
PLANK = (385, 96, 143, 48)         # plank wall row
STONE = (385, 144, 191, 48)        # stone footing row
STONE2 = (385, 336, 143, 48)
ROOF_RED = (576, 96, 96, 45)
ROOF_BROWN = (576, 144, 96, 48)
GABLE = (576, 0, 96, 96)
GFRONT = [(672, 0, 96, 48), (672, 48, 96, 48), (672, 96, 96, 48), (672, 144, 96, 48)]
WINS = [(384, 240, 48, 48), (432, 240, 48, 48), (480, 240, 48, 48), (528, 240, 48, 48), (576, 240, 48, 48),
        (384, 288, 48, 48), (432, 288, 48, 48)]
DOORS = [(528, 312, 48, 72), (576, 312, 48, 72), (624, 312, 48, 72)]
CHIMNEY = ("forest", "4", 118, 14, 26, 48)


def p5(r):
    return piece(*S5, *r)


def timber_house(name, wc, storeys=1, roof_h=144, door=None, door_style=0, wins=None, gwins=None, dormer=True,
                 chimney=0.72, sign=None, roof="slate", walls="plaster", ground="plank", snow=True, seed=0,
                 roof_src=ROOF_RED, extra=None):
    """Two-level timber house, width wc cells: stone footing + plank/panel ground storey, `storeys` timber-and-plaster
    storeys with windows, hipped tile roof (recoloured slate for the Skyspine) with a gable dormer and a chimney.
    door: cell column of the door (or None: no door). Returns (stamp, height in rows)."""
    W = wc * C
    H = roof_h + storeys * 96 + 96
    hr = H // C
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, x1 = 4, W - 4
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # ground storey
    yg = H - 96
    tile(body, p5(STONE), x0, H - 48, x1, H)
    tile(body, p5(PLANK) if ground == "plank" else p5(PANEL_ROW), x0, yg, x1, H - 48)
    # upper storeys
    for s in range(storeys):
        ys = roof_h + s * 96
        if walls == "plaster":
            tile(body, p5(PANEL_TOP), x0, ys, x1, ys + 48)
            tile(body, p5(PANEL_ROW), x0, ys + 48, x1, ys + 96)
        else:
            tile(body, p5(PLANK), x0, ys, x1, ys + 96)
    # windows upstairs: every other cell, alternating styles
    rng = np.random.default_rng(seed)
    wlist = wins if wins is not None else [c for c in range(wc) if (c % 2 == (1 if wc % 2 else 0)) and 0 < c < wc - 1] or [wc // 2]
    for s in range(storeys):
        for i, c in enumerate(wlist):
            wsrc = WINS[(i + s + seed) % 5]
            put(body, p5(wsrc), c * C, roof_h + s * 96 + 30)
    # ground floor: door and windows
    if door is not None:
        put(body, p5(DOORS[door_style]), door * C, H - 74)
    for c in (gwins or []):
        put(body, p5(WINS[3 if c % 2 else 5]), c * C, yg + 12)
    # side posts (dark timber) to close the facade
    a = np.array(body)
    for x in (x0, x0 + 1, x1 - 2, x1 - 1):
        col = a[roof_h:, x]
        col[col[:, 3] > 0, :3] = (58, 40, 30)
    body = Image.fromarray(a, "RGBA")
    im.alpha_composite(body)
    # eave shadow on the top storey
    im = shade_rect(im, x0, roof_h, x1, roof_h + 7, 0.55)
    # roof: hipped rectangle of tiles
    rf = Image.new("RGBA", (W, roof_h + 8), (46, 40, 44, 255))
    tile(rf, p5(roof_src), 0, 0, W, roof_h + 8)
    ra = np.array(rf)
    hip = min(40, W // 4)
    for y in range(roof_h + 8):
        inset = max(0, hip - y) if y < hip else 0
        ra[y, :inset, 3] = 0
        ra[y, W - inset:, 3] = 0
    # ridge line and eave line
    ra[0:3, :, :3] = (ra[0:3, :, :3] * 0.5).astype(np.uint8)
    ra[roof_h + 4:roof_h + 8, :, :3] = (ra[roof_h + 4:roof_h + 8, :, :3] * 0.45).astype(np.uint8)
    # soft vertical shading: lighter to the left (top-left light)
    grad = np.linspace(1.08, 0.86, W)[None, :, None]
    ra[..., :3] = np.clip(ra[..., :3] * grad, 0, 255).astype(np.uint8)
    rf = Image.fromarray(ra, "RGBA")
    dor = None
    if dormer and wc >= 4:
        cx = W // 2 - 48 if isinstance(dormer, bool) else dormer * C - 48
        put(rf, p5(GABLE), cx, roof_h + 8 - 96)
        dor = cx
    rf = outline(rf)
    if roof == "slate":
        rf = recolor(rf)
    elif roof == "slate_dark":
        rf = recolor(rf, sat=0.25, val=0.75)
    if dor is not None:
        put(rf, p5(GFRONT[0] if seed % 2 else GFRONT[2]), dor, roof_h + 8 - 48)
    if chimney:
        put(rf, piece(*CHIMNEY), int(W * chimney), 2)
    im.alpha_composite(rf, (0, 0))
    if snow:
        ra = np.array(im)[..., 3]

        def top(x):
            ys = np.nonzero(ra[:, x])[0]
            return int(ys[0]) if len(ys) else None
        im = snow_cap(im, 0, W, top, depth=9, seed=seed + 3)
    if sign is not None:
        (sr, sx, sy) = sign
        put(im, piece(*sr), sx, sy)
    for (pr, px_, py_) in (extra or []):
        put(im, piece(*pr), px_, py_)
    return im, hr


# ------------------------------------------------------------------------------------------ High Aerie pieces
V1, V2, V3, V4, V5, V6 = "1 (1)", "2 (1)", "3 (1)", "4 (1)", "5 (1)", "6 (1)"
ROCK_FACE = ("dungeon", "1", 576, 4, 160, 88)
FIELDSTONE = ("town", "6", 0, 672, 192, 96)


def face_strip(name, wc, src, mul=(1, 1, 1), snow=True, rows=2, seed=0, top_shade=True):
    """A cliff / retaining-wall face `wc` cells wide and `rows` tall (flat), tiled from src, snow on the lip."""
    W, H = wc * C, rows * C
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pc = tint(piece(*src), mul)
    x = -(seed * 37) % pc.width
    tile(im, pc, -x if x else 0, 0, W, H)
    if pc.height < H:
        tile(im, pc, 0, pc.height - 8, W, H)
    a = np.array(im)
    a[..., 3] = 255
    im = Image.fromarray(a, "RGBA")
    # darker toward the foot (shadowed base), lit rim on top
    g = np.array(im).astype(np.float32)
    g[..., :3] *= np.linspace(1.05, 0.72, H)[:, None, None]
    im = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGBA")
    if snow:
        im = snow_cap(im, 0, W, lambda x: 0, depth=7, seed=seed + 11)
    return im


def cover_door(im, box, patch_box):
    """Paint over a door (box) with a patch of wall taken from patch_box of the same image (whole-house sprites
    whose door is not enterable)."""
    x0, y0, x1, y1 = box
    px0, py0 = patch_box
    patch = im.crop((px0, py0, px0 + (x1 - x0), py0 + (y1 - y0)))
    out = im.copy()
    out.paste(patch, (x0, y0))
    return out


_built = {}


def aerie_buildings():
    """Composed Skyspine buildings (timber and plaster over stone, slate roofs with snow)."""
    if "hall" in _built:
        return _built
    B = _built
    im, h = timber_house("aerie_hall", 8, storeys=2, door=4, door_style=1, gwins=[1, 2, 6], wins=[1, 3, 5, 6], seed=1)
    B["hall"] = gen("aerie_hall", im, solid=h - 1, door=(4, h - 1))
    B["hall_h"] = h
    im, h = timber_house("aerie_engine", 8, storeys=1, roof_h=144, door=None, walls="plank", gwins=[1, 2, 5, 6],
                         wins=[1, 3, 4, 6], seed=4, chimney=0.2)
    B["engine"] = gen("aerie_engine", im, solid=h - 2)
    B["engine_h"] = h
    for i, (wc, st_, rh, walls, gw, sd) in enumerate([(6, 1, 144, "plaster", [1, 2, 4], 2), (5, 1, 144, "plank", [1, 3], 3),
                                                      (5, 1, 96, "plaster", [1, 2, 3], 5), (6, 1, 96, "plank", [1, 4], 6),
                                                      (4, 1, 96, "plaster", [1, 2], 7)]):
        im, h = timber_house("aerie_house%d" % i, wc, storeys=st_, roof_h=rh, door=None, walls=walls, gwins=gw, seed=sd,
                             dormer=wc >= 5, chimney=0.7 if i % 2 else 0.25)
        B["house%d" % i] = gen("aerie_house%d" % i, im, solid=h - 2)
        B["house%d_h" % i] = h
    # log cabins (Forest Wilderness sheet 4) with the door boarded over by log wall and a window: outbuildings
    cab = piece("forest", "4", 0, 0, 192, 192)
    cab = cover_door(cab, (76, 114, 118, 170), (32, 114))
    put(cab, piece("forest", "4", 300, 116, 40, 34), 80, 120)
    cab = snow_cap(cab, 0, 192, lambda x: (lambda ys: int(ys[0]) if len(ys) else None)(np.nonzero(np.array(cab)[:, x, 3])[0]), depth=6, seed=21)
    B["cabin"] = gen("aerie_cabin", cab, solid=2, kind="house")
    cab2 = piece("forest", "4", 384, 0, 192, 192)
    cab2 = cover_door(cab2, (76, 110, 118, 170), (36, 110))
    cab2 = snow_cap(cab2, 0, 192, lambda x: (lambda ys: int(ys[0]) if len(ys) else None)(np.nonzero(np.array(cab2)[:, x, 3])[0]), depth=6, seed=22)
    B["cabin2"] = gen("aerie_cabin2", cab2, solid=2, kind="house")
    # faces
    for i in range(3):
        B["rock%d" % i] = gen("aerie_rock%d" % i, face_strip("r", 4, ROCK_FACE, mul=(0.78, 0.86, 1.02), seed=i), solid=0)
        B["wallf%d" % i] = gen("aerie_wallf%d" % i, face_strip("w", 4, FIELDSTONE, mul=(0.9, 0.95, 1.05), seed=i), solid=0)
        B["rock%d" % i].flat = True
        B["wallf%d" % i].flat = True
    B["rock_nosnow"] = gen("aerie_rock_ns", face_strip("r", 4, ROCK_FACE, mul=(0.7, 0.78, 0.95), snow=False, seed=5), solid=0)
    B["rock_nosnow"].flat = True
    return B


# props (Viking Age, Forest Wilderness, Medieval Town) -- the Skyspine list: timber, furs, rope, rune stones, pines
PINE_BIG = st("forest", "3", 3, 0, 2, 3, solid=1, cols=(1, 1), kind="tree")
PINES = [st("forest", "3", c, 0, 2, 4, solid=1, cols=(1, 1), kind="tree") for c in (10, 12, 14)]
PINE_S = [st("forest", "3", 9, 0, 1, 3, solid=1, kind="tree"), st("forest", "3", 8, 1, 1, 3, solid=1, kind="tree")]
RUNESTONES = [st("viking", V3, c, 6, 2, 2, kind="statue") for c in (0, 2, 4, 6, 8, 10)]
TOTEMS = [st("viking", V3, 12, 6, 1, 2, kind="statue"), st("viking", V3, 14, 6, 1, 2, kind="statue")]
FIREWOOD = [st("viking", V3, c, 10, 2, 2, kind="crate") for c in (6, 8, 10, 12)]
HAY_V = [st("viking", V3, 4, 10, 2, 2, kind="crate")]
LOGS = [st("viking", V3, 0, 13, 2, 1, kind="rock"), st("viking", V3, 2, 13, 2, 1, kind="rock")]
LOG_STACK = st("viking", V3, 4, 12, 2, 2, kind="crate")
STUMP_AXE = st("viking", V3, 7, 12, 1, 1, kind="rock")
STUMPS = [st("viking", V3, 11, 12, 1, 1, kind="rock"), st("viking", V3, 11, 13, 1, 1, kind="rock")]
WELL_V = st("viking", V3, 8, 12, 2, 2, kind="well")
FIREPIT = st("viking", V3, 0, 3, 2, 2, kind="brazier")
FIREBOWL = st("viking", V3, 0, 0, 2, 2, kind="brazier")
BRAZIER_S = st("viking", V3, 2, 5, 1, 1, kind="brazier")
BUCKET = st("viking", V3, 3, 5, 1, 1, kind="barrel")
TABLE_LONG = st("viking", V3, 4, 0, 4, 2, kind="table")
BENCH_L = st("viking", V3, 8, 4, 4, 1, kind="bench")
BENCH_S = st("viking", V3, 4, 5, 2, 1, kind="bench")
STOOLS = [st("viking", V3, c, 5, 1, 1, kind="bench") for c in (6, 7, 8)]
SIGNBOARD = [st("viking", V3, c, 8, 2, 2, kind="sign") for c in (2, 4, 6)]
ARROWS = [st("viking", V3, c, 8, 1, 2, kind="sign") for c in (12, 13, 14, 15)]
ARCH_SIGN = st("viking", V3, 0, 8, 2, 2, solid=0)
BARRELS_V = [st("viking", V2, 8, 4, 2, 2, kind="barrel"), st("viking", V2, 8, 6, 2, 2, kind="barrel"), st("viking", V2, 8, 12, 2, 2, kind="barrel")]
CRATES_V = [st("viking", V2, 10, 4, 2, 2, kind="crate"), st("viking", V2, 11, 6, 2, 2, kind="crate"), st("viking", V2, 10, 12, 2, 2, kind="crate")]
ROPE = [st("viking", V2, 13, 6, 1, 1, kind="crate"), st("viking", V2, 13, 8, 1, 1, kind="crate")]
ANCHORS = [st("viking", V2, 13, 9, 1, 1, kind="rock"), st("viking", V2, 13, 10, 1, 1, kind="rock")]
NET_PILE = st("viking", V2, 12, 4, 2, 2, kind="crate")
TENT_V = st("viking", V2, 14, 4, 2, 2, kind="tent")
WEAPON_RACK = [st("viking", V4, c, 0, 2, 2, kind="shelf") for c in (0, 2, 4)]
SPEAR_RACK = st("viking", V4, 6, 0, 2, 2, kind="shelf")
ARMOR_STAND = [st("viking", V4, 12, 4, 2, 2, kind="shelf"), st("viking", V4, 14, 4, 2, 2, kind="shelf")]
HELM_RACK = st("viking", V4, 12, 10, 2, 2, kind="shelf")
SACKS_V = [st("viking", V6, 0, 8, 2, 2, kind="crate"), st("viking", V6, 2, 10, 2, 2, kind="crate")]
BARRELS_6 = [st("viking", V6, c, 10, 2, 2, kind="barrel") for c in (8, 10, 12, 14)]
ROPES_6 = [st("viking", V6, c, 8, 2, 2, kind="crate") for c in (10, 12, 14)]
CAULDRON = st("viking", V6, 8, 4, 2, 2, kind="brazier")
SPIT = st("viking", V6, 10, 4, 2, 2, kind="brazier")
CANOPY = st("viking", V6, 12, 2, 4, 2, kind="tent")
TORCH_POST = [st("viking", V6, 10, 12, 1, 2, kind="lamp"), st("viking", V6, 11, 12, 1, 2, kind="lamp")]
LANTERNS = [st("viking", V6, 12, 1, 1, 1, kind="lamp"), st("viking", V6, 13, 1, 1, 1, kind="lamp")]
POTS_V = [st("viking", V6, c, 0, 1, 1, kind="barrel") for c in (0, 1, 2, 3)]
FENCE_V = [st("viking", V1, 8, r, 2, 1, kind="fence") for r in (10, 11, 12, 13, 14)]
WATCHTOWER = st("forest", "4", 10, 8, 2, 5, solid=1, kind="house")
LOG_STAIRS = st("forest", "4", 8, 5, 2, 3, solid=0, flat=True)
SHED_OPEN = st("forest", "4", 10, 5, 2, 2, solid=1, kind="house")
LOG_FENCE = [st("forest", "4", 12, r, 2, 1, kind="fence") for r in (9, 11, 13)]
PALISADE = st("forest", "4", 8, 4, 8, 1, kind="fence")
STONE_STAIRS = st("town", "1", 8, 8, 2, 2, solid=0, flat=True)
STONE_STAIRS2 = st("town", "1", 8, 12, 2, 2, solid=0, flat=True)
STALL_BLUE = st("town", "2", 4, 4, 2, 2, solid=1, kind="counter")
INN_SIGN = st("town", "6", 4, 0, 2, 2, kind="sign")
NOTICE_T = st("town", "2", 14, 6, 2, 2, kind="sign")
CHAIN_POSTS = [st("dungeon", "6", 12, 8, 1, 2, kind="lamp"), st("dungeon", "6", 13, 8, 1, 2, kind="lamp")]
LEVERS = [st("dungeon", "6", c, 8, 1, 2, kind="machine") for c in (12, 13, 14, 15)]
WINCH = st("pirate", "B1-1", 10, 10, 2, 2, kind="machine")          # capstan-style cable winch
CAPSTAN = st("pirate", "B1-1", 10, 10, 2, 2, kind="machine")
DRUM = st("pirate", "B1-1", 14, 8, 2, 1, kind="machine")
PULLEYS = [st("pirate", "B1-1", 8, 10, 1, 1, kind="machine"), st("pirate", "B1-1", 9, 10, 1, 1, kind="machine")]
SPOOLS = [st("pirate", "B1-1", 8, 11, 1, 1, kind="machine"), st("pirate", "B1-1", 9, 11, 1, 1, kind="machine")]
DAVIT = st("pirate", "B1-1", 14, 10, 1, 2, kind="machine")
PEBBLES = [st("dungeon", "3", c, r, flat=True, solid=0) for (c, r) in ((4, 0), (5, 0), (4, 1), (5, 1))]
ROCKS_S = [st("dungeon", "3", c, r, kind="rock") for (c, r) in ((4, 2), (5, 2), (6, 2), (7, 2), (0, 3), (4, 3))]
BOULDER = st("dungeon", "3", 0, 0, 2, 2, kind="rock")
GRAVE = [st("forest", "3", 14, 12, 2, 2, kind="statue"), st("forest", "3", 14, 14, 2, 2, kind="statue")]
LANTERN_POST = st("town", "7", 2, 0, 1, 2, kind="lamp")


def windmill():
    """Three windmills (Medieval Town sheet 3) with the door planked over and crew-coloured sails (post High Aerie)."""
    if "mills" in _built:
        return _built["mills"]
    out = []
    base = piece("town", "3", 192, 384, 192, 192)
    base = cover_door(base, (83, 158, 110, 192), (56, 158))
    for i, col in enumerate((None, (150, 178, 220), (214, 170, 110))):
        im = base.copy()
        if col is not None:
            a = np.array(im).astype(np.float32)
            rgb = a[..., :3]
            light = (rgb.min(axis=2) > 170) & (a[..., 3] > 0)
            k = rgb.mean(axis=2, keepdims=True) / 235.0
            a[..., :3] = np.where(light[..., None], np.clip(np.array(col, np.float32) * k * 1.05, 0, 255), rgb)
            im = Image.fromarray(a.astype(np.uint8), "RGBA")
        im = snow_cap(im, 60, 140, lambda x: (lambda ys: int(ys[0]) if len(ys) else None)(np.nonzero(np.array(im)[:, x, 3])[0]), depth=5, seed=40 + i)
        out.append(gen("aerie_mill%d" % i, im, solid=1, kind="house", cols=(1, 2)))
    _built["mills"] = out
    return out
HIDE_RACK = [st("desert", "6", 12, 6, 2, 2, kind="shelf"), st("desert", "6", 14, 6, 2, 2, kind="shelf")]
DESK = st("town", "15", 10, 4, 1, 1, kind="counter")


def ochre_cloths():
    """Wind-shrine cloths: the Siege sheet's cream hanging cloth, dyed ochre (three shades)."""
    if "cloth" in _built:
        return _built["cloth"]
    out = []
    for i, mul in enumerate(((1.0, 0.78, 0.42), (0.95, 0.7, 0.36), (1.02, 0.84, 0.5))):
        im = tint(piece("siege", "1", 576, 384, 48, 48), mul)
        out.append(gen("aerie_cloth%d" % i, im, solid=1, kind="sign"))
    _built["cloth"] = out
    return out


# ------------------------------------------------------------------------------------------ Nacre (Pale Basin) kit
R6_SAND = ("roman", "6", 576, 192, 192, 96)       # sandstone ashlar, two courses of 48
R6_PARAPET = ("roman", "6", 576, 104, 192, 30)    # crenellated sandstone parapet
R6_ARCH = ("roman", "6", 384, 0, 96, 96)          # arcade bay (arch opening ~1.1 H)
R6_ARCH2 = ("roman", "6", 480, 0, 96, 96)
R6_SLAB = ("roman", "6", 384, 386, 96, 44)        # plain cracked slab (flat roofs)
R6_FRIEZE = ("roman", "6", 480, 386, 96, 44)      # slab cut with lines of script (archive walls)
R5_TILES = ("roman", "5", 4, 389, 88, 24)         # terracotta roof courses
R5_EAVE = ("roman", "5", 4, 411, 88, 8)


def _tile_rows(dst, src, x0, y0, x1, y1):
    tile(dst, piece(*src), x0, y0, x1, y1)


def sand_house(name, wc, storeys=1, roof="tile", roof_h=96, door=None, door_style=1, wins=None, gwins=None,
               arcade=None, seed=0, frieze=False, parapet=True, ochre=(1.0, 0.97, 0.9)):
    """Pale Basin house: sandstone ashlar storeys (Roman sheet 6) on a darker plinth, a terracotta roof
    (roof="tile") or a flat slab roof behind a crenellated parapet (roof="flat"); Siege-kit doors and shuttered windows.
    arcade: list of cell columns (pairs) given an arched bay on the ground storey instead of wall."""
    W = wc * C
    H = roof_h + storeys * 96 + 96
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, x1 = 3, W - 3
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tile(body, tint(piece(*R6_SAND), ochre), x0, roof_h, x1, H)
    # string course between storeys, plinth at the foot
    b = np.array(body).astype(np.float32)
    for s in range(storeys + 1):
        yy = roof_h + s * 96
        if s:
            b[yy:yy + 3, x0:x1, :3] *= 0.7
            b[yy + 3:yy + 5, x0:x1, :3] = np.minimum(255, b[yy + 3:yy + 5, x0:x1, :3] * 1.18)
    b[H - 12:H, x0:x1, :3] *= 0.72
    b[H - 13, x0:x1, :3] = np.minimum(255, b[H - 13, x0:x1, :3] * 1.2)
    b[roof_h:, x0:x0 + 3, :3] *= 0.8
    b[roof_h:, x1 - 3:x1, :3] *= 0.8
    body = Image.fromarray(np.clip(b, 0, 255).astype(np.uint8), "RGBA")
    if arcade:
        for c in arcade:
            dark = Image.new("RGBA", (70, 80), (46, 34, 30, 255))
            put(body, dark, c * C + 13, H - 84)
            put(body, tint(piece(*(R6_ARCH if c % 4 == 0 else R6_ARCH2)), ochre), c * C, H - 96)
    wl = wins if wins is not None else [c for c in range(1, wc - 1) if c % 2 == 1] or [wc // 2]
    for s in range(storeys):
        for i, c in enumerate(wl):
            put(body, p5(WINS[4] if (i + seed) % 3 else WINS[(i + s) % 3]), c * C, roof_h + s * 96 + 26)
    for c in (gwins or []):
        put(body, p5(WINS[6] if c % 2 else WINS[5]), c * C, H - 80)
    if door is not None:
        put(body, p5(DOORS[door_style]), door * C, H - 76)
        # stone frame around the door
        fr = np.array(body)
        dx0, dx1 = door * C - 3, door * C + 51
        fr[H - 80:H - 77, max(0, dx0):dx1, :3] = (120, 96, 72)
        body = Image.fromarray(fr, "RGBA")
    im.alpha_composite(body)
    im = shade_rect(im, x0, roof_h, x1, roof_h + 6, 0.6)
    # roof
    if roof == "tile":
        rf = Image.new("RGBA", (W, roof_h + 6), (92, 44, 30, 255))
        tile(rf, piece(*R5_TILES), 0, 0, W, roof_h)
        tile(rf, piece(*R5_EAVE), 0, roof_h - 2, W, roof_h + 6)
        ra = np.array(rf)
        hip = min(36, W // 5)
        for y in range(hip):
            ra[y, :hip - y, 3] = 0
            ra[y, W - (hip - y):, 3] = 0
        ra[0:3, :, :3] = (ra[0:3, :, :3] * 0.55).astype(np.uint8)
        ra[..., :3] = np.clip(ra[..., :3] * np.linspace(1.06, 0.88, W)[None, :, None], 0, 255).astype(np.uint8)
        # hip ridges: lighter left slope edge, darker right
        for y in range(hip, roof_h):
            pass
        rf = outline(Image.fromarray(ra, "RGBA"))
        im.alpha_composite(rf, (0, 0))
    else:
        rf = Image.new("RGBA", (W, roof_h + 4), (0, 0, 0, 0))
        tile(rf, tint(piece(*(R6_FRIEZE if frieze else R6_SLAB)), (ochre[0] * 1.02, ochre[1], ochre[2] * 0.95)), 0, 0, W, roof_h + 4)
        ra = np.array(rf)
        ra[..., 3] = 255
        ra[:, :, :3] = (ra[:, :, :3] * 0.9).astype(np.uint8)
        rf = Image.fromarray(ra, "RGBA")
        if parapet:
            pp = tint(piece(*R6_PARAPET), ochre)
            tile(rf, pp, 0, roof_h + 4 - pp.height, W, roof_h + 4)
        rf = outline(rf, (70, 50, 38, 255))
        im.alpha_composite(rf, (0, 0))
    return im, H // C


def nacre_buildings():
    if "nacre" in _built:
        return _built["nacre"]
    B = {}
    # the cloister (T06_CLOISTER): arcade walk, arched door in the middle bay, terracotta roof - 9 x 8
    im, h = sand_house("n_cloister", 9, storeys=1, roof="tile", roof_h=192, door=4, door_style=1,
                       wins=[1, 3, 5, 7], arcade=[0, 2, 6], seed=1)
    B["cloister"] = gen("nacre_cloister", im, solid=h - 1, door=(4, h - 1))
    B["cloister_h"] = h
    im, h = sand_house("n_cloister_p", 9, storeys=1, roof="tile", roof_h=192, door=None,
                       wins=[1, 3, 5, 7], arcade=[0, 2, 4, 6], seed=1)
    B["cloister_post"] = gen("nacre_cloister_p", im, solid=h - 1)
    specs = [("n_house0", 8, 1, "flat", 96, [1, 3, 5, 6], [2, 5], None, 2),
             ("n_house1", 6, 1, "tile", 96, [1, 4], [2], None, 3),
             ("n_house2", 7, 1, "flat", 96, [1, 3, 5], [1, 5], None, 4),
             ("n_house3", 7, 1, "tile", 96, [2, 4], [1, 3, 5], None, 5),
             ("n_house4", 5, 1, "flat", 48, [1, 3], [3], None, 6)]
    for (nm, wc, stc, rf, rh, wl, gw, arc, sd) in specs:
        im, h = sand_house(nm, wc, storeys=stc, roof=rf, roof_h=rh, wins=wl, gwins=gw, arcade=arc, seed=sd,
                           frieze=(sd == 4), ochre=(1.02, 0.95, 0.84) if sd % 2 else (1.0, 0.97, 0.9))
        B[nm[2:]] = gen("nacre_" + nm[2:], im, solid=h - 1)
        B[nm[2:] + "_h"] = h
    # sandstone cliff faces (mesa edges and the salt basin wall)
    for i in range(3):
        s = gen("nacre_cliff%d" % i, face_strip("c", 4, ROCK_FACE, mul=(1.18, 0.98, 0.72), snow=False, seed=i), solid=0)
        s.flat = True
        B["rock%d" % i] = s
    s = gen("nacre_bwall", face_strip("b", 4, R6_SAND, mul=(0.98, 0.92, 0.8), snow=False, seed=0), solid=0)
    s.flat = True
    B["wallf0"] = B["wallf1"] = B["wallf2"] = s
    # archive wall: slabs cut with script on a sandstone footing (4 x 2)
    a = Image.new("RGBA", (192, 96), (0, 0, 0, 0))
    tile(a, tint(piece(*R6_SAND), (0.95, 0.9, 0.8)), 0, 44, 192, 96)
    tile(a, piece(*R6_FRIEZE), 0, 4, 192, 48)
    a = outline(a, (70, 50, 38, 255))
    B["record"] = gen("nacre_record", a, solid=1, kind="mural")
    _built["nacre"] = B
    return B


# Nacre props: Roman Empire, Desert Wasteland (neutral: rocks, dry shrubs, hides, fire rings, shelters), palms
PALMS = [st("island", "2", 0, 0, 2, 3, cols=(1, 1), kind="tree"), st("island", "2", 2, 0, 2, 3, cols=(1, 1), kind="tree")]
STATUE_R = [st("roman", "4", 8, 0, 2, 4, kind="statue", cols=(0, 1)), st("roman", "4", 11, 0, 2, 4, kind="statue")]
STELE = st("roman", "4", 13, 0, 2, 4, kind="statue")
PEDESTAL_R = st("roman", "4", 8, 5, 2, 3, kind="statue")
BLOCK_MOSS = st("roman", "4", 11, 5, 2, 3, kind="machine")
BENCH_R = [st("roman", "4", 0, 4, 2, 2, kind="bench"), st("roman", "4", 4, 5, 2, 1, kind="bench"), st("roman", "4", 0, 6, 2, 2, kind="bench")]
BENCH_M = st("roman", "8", 4, 4, 2, 2, kind="bench")
FOUNTAIN_R = st("roman", "4", 0, 0, 4, 4, kind="well")
JARS = [st("roman", "8", c, r, 1, 1, kind="barrel") for (c, r) in ((4, 10), (5, 10), (4, 11), (5, 11), (6, 11), (4, 12), (5, 12), (6, 12), (4, 13), (5, 13))]
AMPHORA = [st("roman", "3", 2, 14, 1, 1, kind="barrel"), st("roman", "3", 3, 14, 1, 1, kind="barrel"), st("roman", "3", 8, 14, 1, 1, kind="barrel"), st("roman", "3", 9, 14, 1, 1, kind="barrel")]
CRATE_R = [st("roman", "3", 0, 15, 1, 1, kind="crate"), st("roman", "3", 1, 15, 1, 1, kind="crate")]
AWNING_STALLS = [st("roman", "5", c, 6, 1, 2, kind="counter") for c in (0, 1, 2, 3)]
WHITE_STALLS = [st("roman", "5", c, 6, 1, 2, kind="counter") for c in (5, 6, 7)]
COLUMN = st("roman", "8", 14, 10, 1, 2, kind="pillar")
BROKEN_COL = [st("roman", "8", 7, 10, 1, 2, kind="pillar"), st("roman", "8", 9, 12, 1, 2, kind="pillar")]
MARBLE_BITS = [st("roman", "1", 12, 10, 1, 1, kind="rock"), st("roman", "1", 13, 10, 1, 1, kind="rock")]
SALT_ROCKS = [st("roman", "1", 12, 10, 1, 1, kind="rock", flat=False), st("roman", "1", 14, 10, 2, 2, kind="rock")]
SHRUBS = [st("desert", "5", 0, 4, 2, 2, kind="hedge"), st("desert", "5", 8, 4, 2, 2, kind="hedge"), st("desert", "5", 4, 6, 2, 2, kind="hedge")]
GREEN_SHRUB = st("desert", "5", 12, 4, 2, 2, kind="hedge")
DROCKS = [st("desert", "5", 10, 4, 2, 2, kind="rock"), st("desert", "5", 2, 6, 2, 2, kind="rock"), st("desert", "5", 8, 6, 2, 2, kind="rock"), st("desert", "5", 14, 6, 2, 2, kind="rock")]
SACKS_D = [st("desert", "5", 0, 14, 2, 2, kind="crate"), st("desert", "5", 2, 14, 2, 2, kind="crate")]
HIDES = [st("desert", "6", 12, 6, 2, 2, kind="shelf"), st("desert", "6", 14, 6, 2, 2, kind="shelf")]
FIRE_RING = [st("desert", "6", 8, 6, 2, 2, kind="brazier"), st("desert", "6", 10, 6, 2, 2, kind="brazier")]
SHELTER = [st("desert", "6", 8, 0, 2, 2, kind="tent"), st("desert", "6", 10, 0, 2, 2, kind="tent"), st("desert", "6", 10, 2, 2, 2, kind="tent")]
TENTS_D = [st("desert", "6", 0, 0, 2, 2, kind="tent"), st("desert", "6", 2, 2, 2, 2, kind="tent"), st("desert", "6", 4, 0, 2, 2, kind="tent")]
CRATES_D = [st("desert", "6", 0, 8, 1, 1, kind="crate"), st("desert", "6", 1, 8, 1, 1, kind="crate"), st("desert", "6", 2, 8, 1, 1, kind="crate")]
BARREL_D = [st("desert", "6", 12, 10, 1, 2, kind="barrel"), st("desert", "6", 14, 10, 1, 2, kind="barrel")]
CLOTH_FLAG = [st("desert", "6", 2, 12, 1, 2, kind="sign"), st("desert", "6", 6, 12, 1, 2, kind="sign")]
WATER_CHANNEL = st("roman", "8", 0, 12, 4, 3, kind="pool")
BASIN_R = st("roman", "4", 12, 13, 4, 3, kind="pool")
GARDEN = [st("town", "3", 12, 4, 4, 2, solid=2, kind="garden")]
STONE_STAIRS_S = st("town", "1", 8, 8, 2, 2, solid=0, flat=True)
STONE_STAIRS_S1 = st("town", "1", 8, 8, 1, 2, solid=0, flat=True)
RUIN_WALL = st("roman", "6", 12, 10, 3, 2, kind="rubble")
LAMP_R = st("town", "7", 2, 0, 1, 2, kind="lamp")
DESK_N = st("roman", "4", 4, 5, 1, 1, kind="counter")
PEBBLES_N = PEBBLES


def arcade_bays():
    if "arcade" in _built:
        return _built["arcade"]
    out = []
    extras = [None, None, ("town", "7", 4, 96, 48, 96), ("viking", V6, 576, 48, 48, 48), ("town", "7", 0, 480, 48, 96),
              ("roman", "3", 96, 672, 48, 48)]
    for i in range(6):
        src = (R6_ARCH, R6_ARCH2)[i % 2]
        im = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
        put(im, Image.new("RGBA", (70, 78), (60 + 6 * (i % 3), 44 + 4 * (i % 2), 36, 255)), 13, 16)
        ex = extras[i]
        if ex is not None:
            put(im, piece(*ex), 24, 96 - ex[3] - 2 if ex[3] < 90 else 0)
        put(im, tint(piece(*src), (1.0, 0.95 - 0.02 * (i % 3), 0.86 - 0.03 * (i % 2))), 0, 0)
        out.append(gen("nacre_arcade%d" % i, im, solid=2, kind="wall"))
    _built["arcade"] = out
    return out


ARCADE = arcade_bays()


def pool_rim(name, x0, y0, w, h, water_cells, cx, cy, rx, ry, ground_src, ground_mul=(1, 1, 1), rim_px=16,
             water_anim="water_deep"):
    """A smooth elliptical stone rim for a pool whose water is laid on whole cells: drawn just above the (flat)
    water animation. Inside the inner ellipse, cells without water get still-water pixels; outside the outer
    ellipse, water cells are painted back with ground; between the two, sandstone coping with a wet inner lip.
    (x0, y0, w, h): cell box of the stamp; water_cells: set of absolute cells; cx.. in cells (centre of cells = +0.5)."""
    W, H = w * C, h * C
    fa = Image.open(os.path.join(kit.EXT, "field_anim", water_anim + ".png")).convert("RGBA").crop((0, 0, C, C))
    wa = np.array(fa)
    gr = np.array(tint(piece(*ground_src), ground_mul))
    stone = np.array(tint(piece(*R6_SLAB), (1.05, 1.0, 0.9)))
    out = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    gx = (x0 * C + xx) / C
    gy = (y0 * C + yy) / C
    d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    k_in = 1.0 - (rim_px / C) / max(rx, ry) * 0.5
    k_out = 1.0 + (rim_px / C) / max(rx, ry) * 0.5
    wmask = np.zeros((H, W), bool)
    for (cxl, cyl) in water_cells:
        lx, ly = (cxl - x0) * C, (cyl - y0) * C
        if 0 <= lx < W and 0 <= ly < H:
            wmask[ly:ly + C, lx:lx + C] = True
    inner = d < k_in
    ring = (d >= k_in) & (d < k_out)
    outer = d >= k_out
    sel = inner & ~wmask
    out[sel] = wa[yy[sel] % C, xx[sel] % C]
    sel = outer & wmask
    out[sel] = gr[(y0 * C + yy[sel]) % gr.shape[0], (x0 * C + xx[sel]) % gr.shape[1]]
    out[ring] = stone[yy[ring] % stone.shape[0], xx[ring] % stone.shape[1]]
    out[ring, 3] = 255
    # wet lip (inner third of the ring) darker, outer edge highlight, 1px outline both sides
    t = (d - k_in) / (k_out - k_in)
    lip = ring & (t < 0.35)
    out[lip, :3] = (out[lip, :3] * 0.72).astype(np.uint8)
    hi = ring & (t > 0.8)
    out[hi, :3] = np.minimum(255, out[hi, :3].astype(np.int32) + 22).astype(np.uint8)
    edge = ring & ((t < 0.08) | (t > 0.94))
    out[edge, :3] = (70, 54, 42)
    im = Image.fromarray(out, "RGBA")
    return gen(name, im, solid=0, base=1)
FURS = [st("viking", V5, 8, 11, 1, 1, solid=0, flat=True), st("viking", V5, 5, 12, 2, 1, solid=0, flat=True),
        st("viking", V5, 0, 15, 1, 1, solid=0, flat=True), st("viking", V5, 1, 15, 1, 1, solid=0, flat=True)]


def sand_drifts():
    """Wind-blown sand decals for the paving (the Skyspine drift decals, dyed sand)."""
    if "sdrift" in _built:
        return _built["sdrift"]
    from skins import lib_cold  # noqa
    sh = kit.sheet_img("dreamy", "gen_drifts")
    im = tint(sh, (1.02, 0.86, 0.6))
    save_sheet("nacre_sdrift", im)
    out = [Stamp("aeriegen", "nacre_sdrift", i, 0, 1, 1, solid=0, flat=True) for i in range(8)] + \
          [Stamp("aeriegen", "nacre_sdrift", 2 * i, 1, 2, 1, solid=0, flat=True) for i in range(4)]
    _built["sdrift"] = out
    return out
