"""Bellharbor (T04, Glass Coast) art for tools/maps48/maps/bell.py: sea-teal water, bleached planks and sun-washed
cobbles, sand, bells, nets, bollards, chart stalls, boats and the moored ferry.

Derived art (built once from the owner's CuteSCKR sheets, never scaled, 1 art px = 1 screen px) is written to
Assets/_processed/maps48_bell/ under the pack alias "bellx":
  town1b / town5b   Medieval Town sheets 1 and 5, sun-bleached (the Glass Coast "bleached wood" look)
  ship              Pirate Age B1-2 ship with the skull flags removed (the Ministry ferry)
  boats             Pirate Age B3 with the painted sea keyed out around the rowboats and floating planks
and one field animation, game/assets/ext/field_anim/water_teal (water_deep recoloured to the Glass Coast sea)."""
import os, json
import numpy as np
from PIL import Image
import kit
from kit import st, Mat, Stamp, C
from skins.lib_d import TintMat

kit.PACKS.setdefault("bellx", "_processed/maps48_bell")
OUTD = os.path.join(kit.ASSETS, kit.PACKS["bellx"])
_ME = os.path.abspath(__file__)


def _src(alias, sheet):
    return Image.open(kit.sheet_path(alias, sheet)).convert("RGBA")


def _bleach(im, k=0.24, add=(12, 14, 16)):
    a = np.array(im).astype(np.float32)
    rgb = a[..., :3]
    g = rgb.mean(axis=2, keepdims=True)
    a[..., :3] = np.clip(rgb * (1 - k) + g * k + np.array(add, dtype=np.float32), 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def _key_blue(im, box):
    """Painted sea around objects -> transparent (bluish pixels only; wood and rope stay)."""
    a = np.array(im)
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1].astype(np.int32)
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    blue = (b > r + 40) & (b > g + 5)
    sub[blue, 3] = 0
    a[y0:y1, x0:x1] = sub.astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def _erase_grey(im, boxes, sat=38):
    """Removes low-saturation pixels (black flags, white skulls) inside the boxes; brown masts stay."""
    a = np.array(im)
    for (x0, y0, x1, y1) in boxes:
        sub = a[y0:y1, x0:x1].astype(np.int32)
        mx, mn = sub[..., :3].max(axis=2), sub[..., :3].min(axis=2)
        grey = (mx - mn) < sat
        sub[grey, 3] = 0
        a[y0:y1, x0:x1] = sub.astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def _build():
    os.makedirs(OUTD, exist_ok=True)
    me = os.path.getmtime(_ME)
    jobs = {
        "town1b": lambda: _bleach(_src("town", "1")),
        "town5b": lambda: _bleach(_src("town", "5")),
        "ship": lambda: _erase_grey(_src("pirate", "B1-2"), [(396, 0, 480, 60), (590, 60, 650, 110), (726, 256, 784, 312)]),
        "boats": lambda: _key_blue(_src("pirate", "B3"), (384, 384, 576, 576)),
    }
    for name, fn in jobs.items():
        p = os.path.join(OUTD, name + ".png")
        if not os.path.exists(p) or os.path.getmtime(p) < me:
            fn().save(p)
    # teal sea animation (runtime: game/assets/ext/field_anim; bake: Assets/_processed/field_anim)
    pal = {(34, 85, 154): (40, 124, 132), (24, 58, 114): (26, 88, 100), (90, 162, 220): (92, 176, 176),
           (154, 210, 240): (170, 226, 218)}
    silt = {(34, 85, 154): (66, 122, 106), (24, 58, 114): (44, 88, 78), (90, 162, 220): (112, 160, 128),
            (154, 210, 240): (184, 214, 180)}
    for d, meta in ((os.path.join(kit.EXT, "field_anim"), True), (os.path.join(kit.ASSETS, "_processed", "field_anim"), False)):
        for name, pl in (("water_teal", pal), ("water_silt", silt)):
            _anim(d, meta, name, pl, me)
            _anim(d, meta, name.replace("water_", "glint_"), pl, me, glint=True)
    for name, pl in (("sea_teal", pal), ("sea_silt", silt)):
        p = os.path.join(OUTD, name + ".png")
        if not os.path.exists(p) or os.path.getmtime(p) < me:
            _sea_sheet(pl).save(p)


def _sea_sheet(pal, n=384):
    """Static sea: the water_deep base colour over an 8 x 8 cell period, shaded with slow tileable swells (the moving
    ripples come from the glint_* animation drawn over every water cell)."""
    base = np.array(pal[(34, 85, 154)], dtype=np.float32)
    dark = np.array(pal[(24, 58, 114)], dtype=np.float32)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n * 2 * np.pi
    sw = (np.sin(xx * 2 + np.sin(yy * 1) * 1.3) * 0.5 + np.sin(yy * 3 + xx * 1) * 0.35 + np.sin((xx - yy) * 1) * 0.3)
    sw = (sw - sw.min()) / (sw.max() - sw.min())
    q = (np.round(sw * 5) / 5)[..., None]                       # banded, pixel-art style (no gradients)
    rgb = base[None, None, :] * (1 - 0.24 * q) + dark[None, None, :] * (0.24 * q)
    out = np.zeros((n, n, 4), dtype=np.uint8)
    out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[..., 3] = 255
    return Image.fromarray(out, "RGBA")


def _anim(d, meta, name, pal, me, glint=False):
    """water_deep recoloured with pal; glint=True keeps only the ripple pixels (transparent elsewhere).
    meta=True writes the runtime json format, else the Aseprite export."""
    p = os.path.join(d, name + ".png")
    if os.path.exists(p) and os.path.getmtime(p) >= me:
        return
    a = np.array(Image.open(os.path.join(d, "water_deep.png")).convert("RGBA"))
    out = a.copy()
    for k, v in pal.items():
        m = (a[..., 0] == k[0]) & (a[..., 1] == k[1]) & (a[..., 2] == k[2])
        out[m, :3] = v
    if glint:
        m = (a[..., 0] == 34) & (a[..., 1] == 85) & (a[..., 2] == 154)
        out[m, 3] = 0
    Image.fromarray(out, "RGBA").save(p)
    if meta:
        json.dump({"frames": 4, "fps": 4.55, "cell": [48, 48], "cols": 4}, open(os.path.join(d, name + ".json"), "w"))
    else:
        txt = json.dumps(json.load(open(os.path.join(d, "water_deep.json")))).replace("water_deep", name)
        open(os.path.join(d, name + ".json"), "w").write(txt)


_build()

P = "B1-1"
# ------------------------------------------------------------------------------------------------ ground
MATS = dict(
    cobble=TintMat([("town", "2", 0, 0, 96, 192)], "path", mul=(1.06, 1.05, 1.0), add=(10, 12, 12), prio=2),
    cobble2=TintMat([("town", "2", 96, 0, 96, 192)], "path", mul=(1.0, 1.0, 0.98), add=(18, 18, 16), prio=2),
    slabs=TintMat([("town", "1", 0, 384, 384, 48)], "floor", mul=(1.02, 1.02, 1.0), add=(8, 10, 10), prio=2),
    flags=TintMat([("castle", "3", 0, 0, 192, 192)], "floor", mul=(1.0, 1.0, 1.0), add=(10, 10, 8), prio=2),
    sand=TintMat([("pirate", "B8", 0, 0, 144, 192)], "sand", mul=(0.92, 0.93, 0.95), add=(8, 10, 44), organic=True, prio=1),
    grass=TintMat([("town", "2", 288, 0, 96, 192)], "grass", mul=(0.84, 0.98, 0.86), add=(6, 8, 10), organic=True, prio=3),
    planks=TintMat([("pirate", P, 0, 0, 192, 192)], "dock", mul=(1.06, 1.04, 1.0), add=(22, 22, 22)),
    planks2=TintMat([("pirate", "B4", 0, 0, 192, 192)], "dock", mul=(1.1, 1.08, 1.06), add=(34, 32, 30)),
    boards=TintMat([("town", "6", 96, 576, 96, 96)], "floor", mul=(1.0, 1.0, 1.0), add=(20, 20, 22)),
    silt_sea=Mat([("bellx", "sea_silt", 0, 0, 384, 384)], "water", organic=True, prio=0),
    sea=Mat([("bellx", "sea_teal", 0, 0, 384, 384)], "water", organic=True, prio=0),
    seawall=TintMat([("town", "6", 0, 690, 192, 48)], "wall", mul=(0.92, 0.96, 0.98), add=(4, 8, 10)),
    quayedge=TintMat([("castle", "1", 0, 48, 192, 48)], "wall", mul=(0.8, 0.86, 0.88)),
    stonewall=TintMat([("castle", "1", 0, 48, 192, 48)], "wall", mul=(1.0, 1.0, 1.0)),
    rubble=TintMat([("town", "2", 96, 0, 96, 192)], "rubble", mul=(0.8, 0.82, 0.8)),
    steps=TintMat([("town", "1", 402, 400, 56, 48)], "stairs", add=(8, 8, 8)),
    silt=TintMat([("pirate", "B8", 0, 0, 144, 192)], "floor2", mul=(0.6, 0.55, 0.44), add=(24, 20, 14), organic=True, prio=1),
    mud=TintMat([("pirate", "B8", 0, 0, 144, 192)], "floor2", mul=(0.62, 0.6, 0.5), add=(20, 22, 18)),
)

# ------------------------------------------------------------------------------------------------ buildings
H_STONE = st("bellx", "town1b", 0, 0, 4, 4, solid=2, door=(1, 3), kind="house")
H_TIMBER = st("bellx", "town1b", 4, 0, 4, 4, solid=2, door=(2, 3), kind="house")
H_SHED = st("bellx", "town1b", 8, 0, 4, 4, solid=2, door=(2, 3), kind="house")
H_THATCH = st("bellx", "town1b", 0, 4, 4, 4, solid=2, door=(1, 3), kind="house")
TOWER = st("bellx", "town1b", 12, 0, 2, 4, solid=2, kind="house")
TOWER_DOOR = st("bellx", "town1b", 14, 0, 2, 4, solid=2, door=(1, 3), kind="house")
CHURCH = st("bellx", "town5b", 4, 8, 2, 4, solid=2, door=(1, 3), kind="house")
CHAPEL = st("bellx", "town5b", 6, 8, 2, 4, solid=2, door=(1, 3), kind="house")
SMITHY = st("bellx", "town5b", 8, 4, 2, 2, solid=1, kind="house")
TANNERY = st("bellx", "town5b", 12, 4, 2, 2, solid=1, kind="house")
HUT_TEAL = st("bellx", "town5b", 14, 4, 2, 2, solid=1, kind="house")
SHOP_A = st("bellx", "town5b", 8, 6, 2, 2, solid=1, kind="house")
SHOP_TEAL = st("bellx", "town5b", 10, 6, 2, 2, solid=1, kind="house")
SHOP_HERB = st("bellx", "town5b", 12, 6, 2, 2, solid=1, kind="house")
SHOP_PURPLE = st("bellx", "town5b", 14, 6, 2, 2, solid=1, kind="house")
WATCH = st("bellx", "town5b", 12, 8, 2, 4, solid=1, kind="house")
STILT_HUT = st("bellx", "town5b", 14, 8, 2, 4, solid=1, kind="house")
GATEHOUSE = st("castle", "2", 8, 0, 4, 4, solid=2, door=(2, 3), kind="house")       # the customs house
TOWN_GATE = st("castle", "2", 5, 12, 4, 4, solid=2, kind="wall")
WALL = st("castle", "1", 0, 0, 4, 2, solid=2, kind="wall")
WALL_MOSS = st("castle", "1", 4, 0, 4, 2, solid=2, kind="wall")
WALL_LOW = st("castle", "1", 0, 6, 4, 2, solid=1, kind="wall")
ARCHES = st("castle", "1", 0, 8, 4, 2, solid=2, kind="wall")
ARCHES_TOP = st("castle", "1", 0, 8, 4, 1, solid=0)
RTOWER = st("castle", "1", 2, 2, 2, 4, solid=2, kind="wall")
CABIN = st("island", "4", 5, 0, 3, 3, solid=2, kind="house")
HUT = st("island", "4", 6, 4, 2, 2, solid=1, kind="house")
SHED = st("island", "4", 11, 6, 2, 2, solid=1, kind="house")
LOOKOUT = st("island", "4", 14, 4, 2, 4, solid=1, kind="house")

# ------------------------------------------------------------------------------------------------ harbour props
BELL = st("pirate", P, 10, 8, 1, 1, kind="bell")
BELLS = [BELL, st("plague", "3", 15, 12, 1, 1, kind="bell"), st("plague", "3", 15, 13, 1, 1, kind="bell")]   # none match
FLAGPOST = st("pirate", P, 11, 8, 1, 2, kind="sign")
WINCH = st("pirate", P, 12, 8, 2, 2, kind="machine")
SPOOL = st("pirate", P, 14, 8, 2, 1, kind="machine")
CAPSTAN = st("pirate", P, 10, 10, 2, 2, kind="machine")
ANCHOR = st("pirate", P, 12, 10, 2, 2, kind="statue")
DAVIT = st("pirate", P, 14, 10, 2, 2, kind="machine")
BARRELS = [st("pirate", P, c, r, 1, 1, kind="barrel") for (c, r) in ((4, 12), (5, 12), (6, 12), (4, 13), (5, 13), (6, 13))]
CRATES = [st("pirate", P, c, r, 1, 1, kind="crate") for (c, r) in ((7, 12), (8, 12), (7, 13))]
CHESTS = [st("pirate", P, c, r, 1, 1, kind="crate") for (c, r) in ((9, 12), (11, 12), (9, 13), (11, 13))]
FISHBOX = [st("pirate", P, 10, 12, 1, 1, kind="crate"), st("pirate", P, 10, 13, 1, 1, kind="crate")]
BUCKETS = [st("pirate", P, c, 12, 1, 1, kind="barrel") for c in (12, 13, 14, 15)]
RINGS = [st("pirate", P, 12, 13, 1, 1, kind="crate"), st("pirate", P, 13, 13, 1, 1, kind="crate")]
ROPES = [st("pirate", P, 14, 13, 1, 1, kind="crate"), st("pirate", P, 10, 14, 1, 1, kind="crate"), st("pirate", P, 11, 14, 1, 1, kind="crate")]
SACKS = st("pirate", P, 15, 13, 1, 1, kind="crate")
LANTERN = st("pirate", P, 14, 14, 1, 1, kind="lamp")
LANTERN2 = st("pirate", P, 14, 15, 1, 1, kind="lamp")
LANTERN_S = st("pirate", P, 15, 14, 1, 1, kind="lamp")
BENCH_P = [st("pirate", P, 12, 14, 2, 1, kind="bench"), st("pirate", P, 12, 15, 2, 1, kind="bench")]
BOLLARD = [st("pirate", P, 7, 14, 1, 1, kind="block"), st("pirate", P, 7, 15, 1, 1, kind="block")]
CLOTH = [st("pirate", P, 6, 14, 1, 1, kind="crate"), st("pirate", P, 6, 15, 1, 1, kind="crate")]
BARREL_T = [st("pirate", P, 4, 14, 1, 2, kind="barrel"), st("pirate", P, 5, 14, 1, 2, kind="barrel")]
CANNONBALLS = st("pirate", "B3", 10, 5, 1, 1, kind="crate")
MAP_STALLS = [st("pirate", "B7", c, 6, 2, 2, kind="counter") for c in (8, 10, 12, 14)]
LAMP_STAND = [st("pirate", "B7", 14, 8, 1, 2, kind="lamp"), st("pirate", "B7", 15, 8, 1, 2, kind="lamp")]
B7_BARRELS = [st("pirate", "B7", c, 4, 1, 2, kind="barrel") for c in (0, 1)] + [st("pirate", "B7", c, 6, 1, 2, kind="barrel") for c in (3, 4, 5)]
B7_CRATES = [st("pirate", "B7", c, 4, 1, 2, kind="crate") for c in (2, 3, 4, 5, 6)]
SCROLLS = [st("pirate", "B5", 10, 8, 1, 2, kind="crate"), st("pirate", "B5", 11, 8, 1, 2, kind="crate")]
CHART_BOARD = [st("pirate", "B7", 8, 12, 2, 2, kind="sign"), st("pirate", "B7", 10, 12, 2, 2, kind="sign")]
FISH_RACK = st("island", "4", 8, 4, 2, 2, kind="laundry")
LAUNDRY = st("island", "4", 11, 4, 2, 2, kind="laundry")
LAUNDRY2 = st("island", "4", 10, 12, 2, 2, kind="laundry")
FISH_RACK2 = st("island", "4", 8, 12, 2, 2, kind="laundry")
NET_RACK = st("island", "4", 12, 13, 2, 2, kind="laundry")
FISH_HANG = st("island", "4", 14, 12, 2, 2, kind="laundry")

SHIP = st("bellx", "ship", 0, 0, 16, 11, solid=0, kind="boat")
ROWBOAT_V = st("bellx", "boats", 9, 8, 1, 3, solid=0, kind="boat")
SKIFF_V = st("bellx", "boats", 10, 8, 1, 2, solid=0, kind="boat")
ROWBOAT_H = st("bellx", "boats", 10, 10, 2, 1, solid=0, kind="boat")
PLANK_V = [st("bellx", "boats", 8, 8, 1, 2, solid=0), st("bellx", "boats", 11, 8, 1, 2, solid=0)]
LONGBOAT = [st("viking", "1 (1)", 0, 0, px=(578, 528, 122, 48), solid=0, kind="boat"),
            st("viking", "1 (1)", 0, 0, px=(576, 576, 124, 48), solid=0, kind="boat")]

# ------------------------------------------------------------------------------------------------ town props (Medieval Town)
STALL_FISH = st("town", "2", 2, 4, 2, 2, solid=1, kind="counter")
STALL_BW = st("town", "2", 8, 4, 2, 2, solid=1, kind="counter")
STALL_G = st("town", "2", 0, 4, 2, 2, solid=1, kind="counter")
STALL_VEG = st("town", "2", 4, 6, 2, 2, solid=1, kind="counter")
STALL_JARS = st("town", "2", 6, 6, 2, 2, solid=1, kind="counter")
WELL = st("town", "2", 8, 6, 2, 2, kind="well")
NOTICE = st("town", "2", 14, 6, 2, 2, kind="sign")
SIGNPOST = st("town", "2", 12, 6, 1, 2, kind="sign")
BENCH = st("town", "2", 8, 12, 2, 1, kind="bench")
BENCH2 = st("town", "2", 12, 11, 2, 1, kind="bench")
HANDCART = st("town", "2", 4, 10, 2, 2, kind="cart")
CART = st("town", "2", 14, 4, 2, 2, kind="cart")
BARREL_W = st("town", "2", 3, 6, 1, 2, kind="barrel")
CRATE_STACK = st("town", "2", 2, 6, 1, 2, kind="crate")
CRATE_PILE = st("town", "2", 10, 6, 2, 2, kind="crate")
POTS = [st("town", "7", 0, 12, 1, 2, kind="barrel"), st("town", "7", 1, 12, 1, 2, kind="barrel"), st("town", "7", 2, 12, 1, 2, kind="barrel")]
SACKS_T = st("town", "7", 4, 12, 2, 2, kind="crate")
BIG_BARREL = st("town", "7", 12, 12, 2, 2, kind="barrel")
TORCH = st("town", "7", 2, 0, 1, 2, kind="lamp")
FENCE = [st("town", "2", 12, 12, 2, 1, kind="fence"), st("town", "2", 14, 12, 2, 1, kind="fence")]
INN_SIGN = st("town", "6", 4, 0, 2, 1, solid=0)

# ------------------------------------------------------------------------------------------------ coast nature
PALMS = [st("pirate", "B9", 6, 2, 2, 4, cols=(1, 1), kind="tree"), st("pirate", "B9", 8, 2, 2, 4, cols=(0, 0), kind="tree"),
         st("pirate", "B9", 10, 2, 2, 4, cols=(0, 0), kind="tree"), st("pirate", "B9", 12, 2, 2, 4, cols=(0, 0), kind="tree")]
BUSH = [st("pirate", "B9", c, r, 1, 1, kind="hedge") for (c, r) in ((8, 6), (9, 6), (10, 6), (11, 6), (12, 7), (13, 7))]
DUNE_GRASS = [st("pirate", "B8", 15, 14, 1, 1, solid=0, flat=True)]
SHELLS = [st("pirate", "B9", c, r, 1, 1, solid=0, flat=True) for (c, r) in ((6, 12), (7, 12), (6, 13), (7, 13), (4, 13))]
PEBBLES = [st("pirate", "B9", c, 14, 1, 1, solid=0, flat=True) for c in (0, 1, 4, 5, 6)]
ROCKS_S = [st("pirate", "B10", c, r, 1, 1, kind="rock") for (c, r) in ((4, 14), (5, 14), (6, 14), (7, 14), (4, 15), (5, 15))]
DRIFTWOOD = [st("pirate", "B9", 8, 12, 2, 1, solid=0, flat=True), st("pirate", "B9", 8, 13, 2, 1, solid=0, flat=True)]
SEAWEED = [st("pirate", "B8", c, 14, 1, 2, solid=0, flat=True) for c in (0, 1, 2)]
DECALS_Q = [st("pirate", P, c, r, 1, 1, flat=True, solid=0) for (c, r) in ((10, 14), (11, 14), (14, 13))]

# ------------------------------------------------------------------------------------------------ flood and ruin (post-fault)
ROOF_TIMBER = st("bellx", "town1b", 4, 0, 4, 2, solid=0)          # drowned houses: only the roof above the flood
ROOF_SHED = st("bellx", "town1b", 8, 0, 4, 2, solid=0)
ROOF_THATCH = st("bellx", "town1b", 0, 4, 4, 2, solid=0)
ROOF_TOWER = st("bellx", "town1b", 12, 0, 2, 2, solid=0)
RUIN_WALLS = [st("castle", "1", 4, 4, 2, 2, kind="rubble"), st("castle", "1", 7, 4, 3, 2, kind="rubble"),
              st("castle", "1", 5, 6, 3, 2, kind="rubble"), st("castle", "1", 8, 6, 3, 2, kind="rubble")]
RUIN_BITS = [st("castle", "1", 0, 10, 2, 2, kind="rubble"), st("castle", "1", 2, 10, 2, 2, kind="rubble")]
FLOTSAM = [st("pirate", "B9", 8, 12, 2, 1, solid=0), st("pirate", "B9", 8, 13, 2, 1, solid=0)] + PLANK_V
TENTS = [st("island", "4", 0, 10, 2, 2, kind="tent"), st("island", "4", 2, 10, 3, 2, kind="tent"), st("island", "4", 8, 6, 2, 2, kind="tent")]
BEDROLLS = [st("camp", "2", 3, 8, 1, 1, solid=0), st("camp", "2", 5, 9, 1, 1, solid=0)]
CAMPFIRE = st("island", "4", 0, 6, 2, 2, kind="brazier")
STONES = [st("pirate", "B9", c, r, 1, 1, solid=0, flat=True) for (c, r) in ((12, 12), (12, 13), (13, 13), (14, 13), (15, 13))]
WRECK = st("bellx", "ship", 0, 0, 16, 8, solid=0, kind="boat")    # the ferry's masts and upper deck above the flood
FOUNTAIN = st("town", "2", 10, 8, 2, 2, kind="well")
BUOYS = [st("pirate", P, 12, 13, 1, 1, solid=0), st("pirate", P, 13, 13, 1, 1, solid=0)]
BIG_ROCKS = [st("pirate", "B10", 12, 12, 2, 2, kind="rock"), st("pirate", "B8", 8, 12, 2, 2, kind="rock")]
