"""Hearthward (T07, Ember Sea) shared art for the hand-made maps in maps/hearth.py.

Hearthward is the survivors' town after the fault: pontoons and salvaged hulls lashed to black rock in the Ember Sea.
Palette: deep red sea (recoloured water swatches and animations), black basalt with lava glow, patched timber.
Adds:
  - ramp-recoloured materials (sea, lava, basalt) and two generated field animations, water_ember and lava_glow
    (written next to the stock ones in game/assets/ext/field_anim; frames are the stock water frames recoloured,
    never scaled);
  - dock dressing drawn in code (plank lip, shadow and pilings on the water below a pontoon edge, beams along the
    other edges), baked flat into the ground;
  - stamps from Pirate Age, Viking Age, Survival Island, Army Camp and Desert Wasteland (salvage camp sheet 6);
  - Hmap: kit.Map with checked placement (solid cells may never land on a reserved entity/route cell).
"""
import os, json
import numpy as np
from PIL import Image
import kit
from kit import st, Mat, Stamp, C, Map

FA = os.path.join(kit.EXT, "field_anim")

# ------------------------------------------------------------------------------------------------ colour ramps
SEA_RAMP = [(0, (34, 8, 12)), (50, (72, 14, 18)), (100, (122, 28, 22)), (150, (178, 58, 28)), (205, (236, 120, 50)),
            (255, (255, 204, 130))]
LAVA_RAMP = [(0, (70, 10, 4)), (80, (150, 30, 6)), (130, (222, 82, 14)), (180, (255, 150, 34)), (230, (255, 214, 96)),
             (255, (255, 244, 190))]
BASALT_RAMP = [(0, (10, 8, 10)), (70, (28, 22, 24)), (130, (50, 40, 40)), (190, (82, 66, 60)), (255, (120, 98, 88))]
ROCK_RAMP = [(0, (6, 5, 7)), (70, (20, 16, 18)), (130, (38, 30, 32)), (200, (66, 52, 50)), (255, (104, 84, 76))]


def _lum(rgb):
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def ramp(arr, stops, lo=None, hi=None):
    """Recolour an RGBA uint8 array by luminance through colour stops (luminance stretched to lo..hi -> 0..255)."""
    a = arr.copy()
    L = _lum(a[..., :3].astype(np.float32))
    if lo is None:
        lo, hi = np.percentile(L[a[..., 3] > 0], 2), np.percentile(L[a[..., 3] > 0], 99.5)
    L = np.clip((L - lo) / max(1.0, hi - lo) * 255.0, 0, 255)
    xs = np.array([s[0] for s in stops], dtype=np.float32)
    for ch in range(3):
        ys = np.array([s[1][ch] for s in stops], dtype=np.float32)
        a[..., ch] = np.interp(L, xs, ys).astype(np.uint8)
    return a


class RampMat(Mat):
    def __init__(self, sources, kind, stops, lohi=None, **kw):
        Mat.__init__(self, sources, kind, **kw)
        self.stops, self.lohi = stops, lohi

    def texture(self):
        if self._tex is None:
            tiles = Mat.texture(self)
            lo, hi = self.lohi if self.lohi else (None, None)
            self._tex = [ramp(t, self.stops, lo, hi) for t in tiles]
        return self._tex


class TintMat(Mat):
    def __init__(self, sources, kind, mul=(1, 1, 1), add=(0, 0, 0), **kw):
        Mat.__init__(self, sources, kind, **kw)
        self.mul, self.add = mul, add

    def texture(self):
        if self._tex is None:
            out = []
            for t in Mat.texture(self):
                t = t.copy()
                rgb = t[..., :3].astype(np.float32) * np.array(self.mul, np.float32) + np.array(self.add, np.float32)
                t[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
                out.append(t)
            self._tex = out
        return self._tex


# the luminance window of the stock water sheets (shared by the material and its animation so frame 0 matches)
def _lohi(name):
    a = np.array(Image.open(os.path.join(FA, name + ".png")).convert("RGBA"))
    L = _lum(a[..., :3].astype(np.float32))
    return float(np.percentile(L, 2)), float(np.percentile(L, 99.5))


SEA_LOHI = _lohi("water_deep")
LAVA_LOHI = _lohi("water_shallow")


HOT_RAMP = [(0, (60, 12, 12)), (50, (110, 24, 18)), (100, (168, 50, 24)), (150, (220, 92, 34)), (205, (252, 150, 60)),
            (255, (255, 222, 150))]


def _save_anim(dst, img, meta):
    p = os.path.join(FA, dst + ".png")
    arr = np.array(img)
    old = np.array(Image.open(p).convert("RGBA")) if os.path.exists(p) else None
    if old is None or old.shape != arr.shape or (old != arr).any():
        img.save(p, optimize=True)
    jp = os.path.join(FA, dst + ".json")
    txt = json.dumps(meta)
    if not os.path.exists(jp) or open(jp).read() != txt:
        open(jp, "w").write(txt)


def make_anims():
    """water_ember(_b, _c, _d, _hot, _hot_b) / lava_glow: the stock water animations recoloured (same frames, fps and cell size).
    _b/_c/_d are the same strip mirrored/flipped and started at other frames (breaks the tiling), _hot is the sea
    lit by lava."""
    deep = np.array(Image.open(os.path.join(FA, "water_deep.png")).convert("RGBA"))
    meta = json.load(open(os.path.join(FA, "water_deep.json")))
    n, cw = int(meta["frames"]), int(meta["cell"][0])
    frames = [deep[:, i * cw:(i + 1) * cw] for i in range(n)]
    _save_anim("water_ember", Image.fromarray(ramp(deep, SEA_RAMP, *SEA_LOHI), "RGBA"), meta)
    b = np.concatenate([f[:, ::-1] for f in frames[2:] + frames[:2]], axis=1)
    _save_anim("water_ember_b", Image.fromarray(ramp(b, SEA_RAMP, *SEA_LOHI), "RGBA"), meta)
    c = np.concatenate([f[::-1, :] for f in frames[1:] + frames[:1]], axis=1)
    _save_anim("water_ember_c", Image.fromarray(ramp(c, SEA_RAMP, *SEA_LOHI), "RGBA"), meta)
    d = np.concatenate([f[::-1, ::-1] for f in frames[3:] + frames[:3]], axis=1)
    _save_anim("water_ember_d", Image.fromarray(ramp(d, SEA_RAMP, *SEA_LOHI), "RGBA"), meta)
    _save_anim("water_ember_hot", Image.fromarray(ramp(deep, HOT_RAMP, *SEA_LOHI), "RGBA"), meta)
    _save_anim("water_ember_hot_b", Image.fromarray(ramp(b, HOT_RAMP, *SEA_LOHI), "RGBA"), meta)
    _save_anim("water_ember_hot_c", Image.fromarray(ramp(c, HOT_RAMP, *SEA_LOHI), "RGBA"), meta)
    sh = np.array(Image.open(os.path.join(FA, "water_shallow.png")).convert("RGBA"))
    m2 = json.load(open(os.path.join(FA, "water_shallow.json")))
    m2["fps"] = 3.0
    _save_anim("lava_glow", Image.fromarray(ramp(sh, LAVA_RAMP, *LAVA_LOHI), "RGBA"), m2)


make_anims()

# ------------------------------------------------------------------------------------------------ materials
MATS = dict(
    sea=RampMat([("fa", "water_deep", 0, 0, 48, 48)], "water", SEA_RAMP, SEA_LOHI, organic=True, prio=0),
    lava=RampMat([("fa", "water_shallow", 0, 0, 48, 48)], "rock", LAVA_RAMP, LAVA_LOHI, organic=True, prio=1),
    rock=RampMat([("dungeon", "1", 576, 0, 192, 96)], "rock", ROCK_RAMP, organic=True, prio=4),
    basalt=RampMat([("desert", "1", 0, 192, 192, 192)], "floor2", BASALT_RAMP, organic=True, prio=3),
    planks=TintMat([("pirate", "B1-1", 0, 0, 192, 192)], "dock", mul=(0.92, 0.84, 0.8)),
    planks_old=TintMat([("pirate", "B4", 0, 0, 192, 192)], "dock", mul=(0.95, 0.88, 0.84)),
    planks_grey=TintMat([("pirate", "B1-1", 0, 0, 192, 192)], "dock", mul=(0.78, 0.72, 0.72), add=(6, 4, 4)),
    deck=TintMat([("pirate", "B4", 0, 0, 192, 192)], "dock", mul=(0.98, 0.9, 0.86), add=(10, 6, 4)),
    bridge=TintMat([("pirate", "B1-1", 0, 0, 192, 192)], "bridge", mul=(0.86, 0.78, 0.74)),
)
DOCKS = ("planks", "planks_old", "planks_grey", "deck", "bridge")


# ------------------------------------------------------------------------------------------------ generated stamps
class GenStamp(Stamp):
    """A stamp whose pixels are made in code (flat decals only: they are baked into the ground)."""

    def __init__(self, img):
        self._im = img
        Stamp.__init__(self, "pirate", "B1-1", 0, 0, px=(0, 0, img.width, img.height), solid=0, flat=True)

    def image(self):
        return self._im


class RampStamp(Stamp):
    """A sheet stamp recoloured through a ramp (flat decals only)."""

    def __init__(self, alias, sheet, c, r, w=1, h=1, stops=ROCK_RAMP, **kw):
        kw.setdefault("solid", 0)
        Stamp.__init__(self, alias, sheet, c, r, w, h, flat=True, **kw)
        self.stops = stops

    def image(self):
        a = np.array(Stamp.image(self))
        a2 = ramp(a, self.stops)
        return Image.fromarray(a2, "RGBA")


WOOD = [(58, 36, 26), (86, 56, 38), (112, 74, 48), (140, 96, 62), (36, 22, 18)]


def _lip_img(post_l, post_r):
    """Plank edge seen from the front (the pontoon's side face) plus its shadow and pilings, on a water cell."""
    im = np.zeros((C, C, 4), np.uint8)
    # shadow on the water under the pontoon
    for y in range(C):
        a = int(max(0, 170 - y * 7))
        im[y, :, :3] = (8, 2, 4)
        im[y, :, 3] = a
    # side face: two boards with dark seams
    for y in range(0, 11):
        col = WOOD[2] if y < 2 else (WOOD[1] if y < 6 else WOOD[0])
        if y in (5, 10):
            col = WOOD[4]
        im[y, :, :3] = col
        im[y, :, 3] = 255
    for x in range(0, C, 16):
        im[0:11, x, :3] = WOOD[4]
    # pilings: dark posts reaching into the water with a glowing ring where they enter it
    for px, on in ((5, post_l), (37, post_r)):
        if not on:
            continue
        for y in range(8, 26):
            for x in range(px, px + 6):
                c = WOOD[1] if x == px + 1 else (WOOD[0] if x < px + 4 else WOOD[4])
                im[y, x, :3] = c
                im[y, x, 3] = 255
        for x in range(px - 2, px + 8):
            im[26, x, :3] = (214, 96, 44)
            im[26, x, 3] = 200
            im[27, x, :3] = (120, 36, 20)
            im[27, x, 3] = 160
    return Image.fromarray(im, "RGBA")


def _beam_img(side):
    """Edge beam on a pontoon cell (north/west/east edge): a darker rope-lashed timber."""
    im = np.zeros((C, C, 4), np.uint8)
    if side == "n":
        for y in range(0, 7):
            im[y, :, :3] = WOOD[4] if y in (0, 6) else (WOOD[1] if y < 3 else WOOD[0])
            im[y, :, 3] = 255
        for x in (10, 34):          # rope lashings
            im[0:7, x:x + 3, :3] = (176, 150, 106)
            im[0:7, x + 1, :3] = (120, 98, 68)
    else:
        xs = range(0, 6) if side == "w" else range(C - 6, C)
        for x in xs:
            edge = x in (0, 5) if side == "w" else x in (C - 6, C - 1)
            im[:, x, :3] = WOOD[4] if edge else WOOD[0]
            im[:, x, 3] = 255
        for y in (12, 36):
            for x in xs:
                im[y:y + 3, x, :3] = (176, 150, 106)
    return Image.fromarray(im, "RGBA")


LIPS = {(a, b): GenStamp(_lip_img(a, b)) for a in (0, 1) for b in (0, 1)}
BEAMS = {s: GenStamp(_beam_img(s)) for s in "nwe"}


# ------------------------------------------------------------------------------------------------ the checked map
class Hmap(Map):
    """kit.Map that refuses to put solid cells on reserved cells (entity spots and routes)."""

    def __init__(self, *a, **kw):
        Map.__init__(self, *a, **kw)
        self._placed_sea = set()

    def place(self, s, x, y, dx=0, dy=0, solid=None, kind=None, over=False):
        rows = s.solid if solid is None else solid
        if rows and self._res:
            c0, c1 = s.cols if s.cols else (0, s.w - 1)
            for r in range(s.h - rows, s.h):
                for c in range(c0, c1 + 1):
                    if (x + c, y + r) in self._res:
                        print("  !! " + "%s: stamp %s,%s %s at (%d,%d) blocks reserved cell (%d,%d)"
                                         % (self.id, s.sheet, s.px[:2], s.name, x, y, x + c, y + r))
                        return None
        return Map.place(self, s, x, y, dx, dy, solid, kind, over)

    def try_place(self, s, x, y, **kw):
        try:
            return self.place(s, x, y, **kw)
        except ValueError:
            return None

    def solid_ok(self, x, y):
        return not self._reserved(x, y)

    def dock_edges(self, skip_anim, docks=DOCKS, water=("sea",)):
        """Bakes pontoon lips (on the water cell under each dock edge), beams on the other edges, and returns the
        water cells that keep the static baked lip (no surface animation there)."""
        W, H = self.w, self.h
        isd = lambda x, y: 0 <= x < W and 0 <= y < H and self.mat[y][x] in docks
        isw = lambda x, y: 0 <= x < W and 0 <= y < H and self.mat[y][x] in water
        for y in range(H):
            for x in range(W):
                if isd(x, y):
                    if isw(x, y - 1):
                        self.flat.append((BEAMS["n"], x * C, y * C))
                    if isw(x - 1, y):
                        self.flat.append((BEAMS["w"], x * C, y * C))
                    if isw(x + 1, y):
                        self.flat.append((BEAMS["e"], x * C, y * C))
                elif isw(x, y) and isd(x, y - 1):
                    left = not isd(x - 1, y - 1) or (x % 3 == 0)
                    right = not isd(x + 1, y - 1) or (x % 3 == 1)
                    self.flat.append((LIPS[(int(left), int(right))], x * C, y * C))
                    skip_anim.add((x, y))
        return skip_anim

    def sea_anims(self, skip=()):
        """Animated sea: two phases of the red water in a scattered pattern, and the lava-lit variant on sea cells
        next to the black rock (the reefs glow)."""
        skip = set(skip)
        for y in range(self.h):
            for x in range(self.w):
                if self.mat[y][x] != "sea" or (x, y) in skip:
                    continue
                near = any(0 <= x + dx < self.w and 0 <= y + dy < self.h and self.mat[y + dy][x + dx] in ("rock", "lava")
                           for dx in (-1, 0, 1) for dy in (-1, 0, 1))
                h = (x * 7919 + y * 104729 + x * y * 31) % 7
                if near:
                    name = ("water_ember_hot", "water_ember_hot_b", "water_ember_hot_c")[h % 3]
                else:
                    name = ("water_ember", "water_ember_b", "water_ember_c", "water_ember", "water_ember_d",
                            "water_ember_b", "water_ember_c")[h]
                self.anim(name, x, y, h=48, flat=True)
        # lava: animated only where a cell is surrounded by lava (the ragged baked edge stays visible)
        for y in range(self.h):
            for x in range(self.w):
                if self.mat[y][x] == "lava" and all(0 <= x + dx < self.w and 0 <= y + dy < self.h and
                                                    self.mat[y + dy][x + dx] == "lava" for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    self.anim("lava_glow", x, y, h=48, flat=True)


# ------------------------------------------------------------------------------------------------ stamps
P = "pirate"
V = "viking"
VK = "1 (1)"
V2 = "2 (1)"
V3 = "3 (1)"

# --- pirate age (sheet B1-1): cargo, rigging, dock hardware
BARRELS = [st(P, "B1-1", c, r, 1, 1, kind="barrel") for c in (4, 5, 6) for r in (12, 13)]
BARREL_WATER = st(P, "B1-1", 6, 13, 1, 1, kind="barrel")
CRATES = [st(P, "B1-1", 7, 12, 1, 1, kind="crate"), st(P, "B1-1", 8, 12, 1, 1, kind="crate"), st(P, "B1-1", 7, 13, 1, 1, kind="crate")]
CHESTS = [st(P, "B1-1", 9, 13, 1, 1, kind="crate"), st(P, "B1-1", 11, 13, 1, 1, kind="crate")]
FISH_CRATE = st(P, "B1-1", 10, 13, 1, 1, kind="crate")
BUCKETS = [st(P, "B1-1", c, 12, 1, 1, kind="barrel") for c in (12, 13, 14, 15)]
LIFE_RING = [st(P, "B1-1", 12, 13, 1, 1, solid=0), st(P, "B1-1", 13, 13, 1, 1, solid=0)]
ROPE = st(P, "B1-1", 14, 13, 1, 1, solid=0)
SACKS = st(P, "B1-1", 15, 13, 1, 1, kind="crate")
ROPE_BIG = [st(P, "B1-1", 10, 14, 1, 1, solid=0), st(P, "B1-1", 11, 14, 1, 1, solid=0)]
CLOTH = [st(P, "B1-1", 10, 15, 1, 1, solid=0, flat=True), st(P, "B1-1", 11, 15, 1, 1, solid=0, flat=True)]
PALLETS = [st(P, "B1-1", 12, 14, 1, 1, kind="bench"), st(P, "B1-1", 13, 14, 1, 1, kind="bench")]
LANTERN = st(P, "B1-1", 14, 14, 1, 1, kind="lamp")
LANTERN2 = st(P, "B1-1", 15, 14, 1, 1, kind="lamp")
LANTERN3 = st(P, "B1-1", 14, 15, 1, 1, kind="lamp")
BELL = st(P, "B1-1", 10, 8, 1, 1, kind="bell")
SIGNAL_FLAGS = st(P, "B1-1", 11, 8, 1, 2, kind="sign")
WINCH = st(P, "B1-1", 12, 8, 2, 2, kind="machine")
CABLE_DRUM = st(P, "B1-1", 14, 8, 2, 1, kind="machine")
PULLEYS = [st(P, "B1-1", 8, 10, 1, 1, solid=0), st(P, "B1-1", 9, 10, 1, 1, solid=0)]
SPOOLS = [st(P, "B1-1", 8, 11, 1, 1, kind="crate"), st(P, "B1-1", 9, 11, 1, 1, kind="crate")]
CAPSTAN = st(P, "B1-1", 10, 10, 2, 2, kind="machine")
ANCHOR = st(P, "B1-1", 12, 10, 2, 2, kind="block")
ANCHOR_CRANE = st(P, "B1-1", 14, 10, 2, 2, kind="block")
MAST = st(P, "B1-1", 0, 8, 2, 8, kind="mast", cols=(0, 1))
MAST_NEST = st(P, "B1-1", 8, 8, 2, 2, kind="mast")
RIG_NET = st(P, "B1-1", 4, 8, 2, 4, solid=0)
RIG_ROPES = st(P, "B1-1", 6, 8, 2, 4, solid=0)
LADDER = st(P, "B1-1", 3, 8, 1, 8, solid=0)
SAIL = st(P, "B1-1", 6, 14, 1, 2, kind="block")
HULL_BOW = st(P, "B1-1", 0, 4, 8, 4, kind="boat")                  # front half of a hull (deck view)
HULL_STERN = st(P, "B1-1", 12, 4, 4, 4, kind="boat")               # stern with cabin
# the moored hulk (sheet B1-2) without its black flags
HULK = Stamp(P, "B1-2", 0, 0, px=(0, 104, 722, 446), kind="boat", solid=0)
# sheet B4 (wreck pieces) and B6/B7/B8 (ship stores)
WRECK_MOSS = st(P, "B4", 4, 12, 8, 4, kind="boat")
HULL_HALF = st(P, "B4", 4, 12, 4, 4, kind="boat")                  # broken-off hull half (no deck patch)
WRECK_BOW = st(P, "B4", 0, 12, 4, 4, kind="boat")
SHIP_TOP = st(P, "B4", 12, 8, 4, 8, kind="boat")
BOW_TOP = st(P, "B4", 0, 8, 4, 4, kind="boat")
FRAME_RIBS = st(P, "B4", 4, 4, 4, 4, solid=0)                       # broken timber lattice (hull ribs)
PLANK_PATCH = st(P, "B4", 6, 1, 2, 2, solid=0, flat=True)
SMALL_CARGO = [st(P, "B4", 12, 0, 1, 1, kind="barrel"), st(P, "B4", 13, 0, 1, 1, kind="barrel"), st(P, "B4", 12, 1, 1, 1, kind="barrel"),
               st(P, "B4", 13, 1, 1, 1, kind="crate"), st(P, "B4", 13, 4, 1, 1, kind="crate"), st(P, "B4", 14, 4, 1, 1, kind="crate"),
               st(P, "B4", 13, 5, 1, 1, kind="crate"), st(P, "B4", 12, 4, 1, 1, kind="barrel")]
COILS = [st(P, "B4", 12, 3, 1, 1, solid=0), st(P, "B4", 13, 2, 1, 1, solid=0), st(P, "B4", 12, 5, 1, 1, solid=0)]
ANCHOR_S = st(P, "B4", 14, 3, 1, 1, solid=0)
CRATES_B7 = [st(P, "B5", c, 7, 1, 1, kind="crate") for c in (10, 11, 12, 13)]
CRATE_TALL = [st(P, "B5", 14, 6, 1, 2, kind="crate"), st(P, "B5", 15, 6, 1, 2, kind="crate")]
BARRELS_B7 = [st(P, "B5", c, 7, 1, 1, kind="barrel") for c in (4, 5, 8)]
PILLOWS = [st(P, "B5", c, 3, 1, 1, solid=0) for c in (3, 4, 5, 6)]
BLANKETS = st(P, "B5", 8, 2, 1, 1, solid=0)
STOOL = st(P, "B5", 1, 4, 1, 1, kind="bench")
BUCKET_W = st(P, "B5", 2, 4, 1, 1, kind="barrel")
TUB = st(P, "B5", 8, 4, 1, 1, kind="barrel")
LAMP_TABLE = st(P, "B5", 4, 4, 2, 2, kind="table")
LAMP_HANG = [st(P, "B5", 8, 12, 1, 1, kind="lamp"), st(P, "B5", 9, 12, 1, 1, kind="lamp")]
LAMP_POST = st(P, "B5", 10, 12, 1, 1, kind="lamp")
MAP_BOARD = st(P, "B5", 8, 14, 2, 2, kind="sign")
PLAN_RACK = st(P, "B5", 10, 8, 2, 2, kind="shelf")
BUNK = st(P, "B5", 0, 0, 2, 3, kind="bed")
BUNK2 = st(P, "B5", 3, 0, 2, 3, kind="bed")
STAIRS_B7 = st(P, "B5", 12, 8, 2, 3, solid=0)
LANTERN_B8 = [st(P, "B7", 10, 3, 1, 1, kind="lamp"), st(P, "B7", 11, 3, 1, 1, kind="lamp")]
JUG = st(P, "B7", 7, 3, 1, 1, kind="barrel")
PAILS = [st(P, "B7", 8, 3, 1, 1, kind="barrel"), st(P, "B7", 9, 3, 1, 1, kind="barrel")]
FOOD_BARRELS = [st(P, "B7", 4, 6, 1, 2, kind="barrel"), st(P, "B7", 5, 6, 1, 2, kind="barrel")]
CRATES_B8 = [st(P, "B7", c, 4, 1, 2, kind="crate") for c in (2, 3, 4, 5, 6)]
BARRELS_B8 = [st(P, "B7", 0, 4, 1, 2, kind="barrel"), st(P, "B7", 1, 4, 1, 2, kind="barrel")]
TORCH_B8 = [st(P, "B7", 14, 3, 1, 1, kind="lamp")]
WATCH = st(P, "B6", 14, 8, 2, 4, kind="block", cols=(0, 1))       # timber lookout
LOOKOUT = st(P, "B6", 12, 10, 2, 2, kind="block")
LOOKOUT_T = st(P, "B6", 12, 12, 2, 4, kind="block")
ROPE_LADDER = st(P, "B6", 14, 12, 2, 4, solid=0)
SHORT_LADDER = st(P, "B6", 10, 14, 2, 2, solid=0)
PANEL = [st(P, "B6", c, 10, 2, 2, kind="block") for c in (0, 2, 4, 6, 8)]
PANEL_BURNT = [st(P, "B6", 10, 10, 2, 2, kind="block"), st(P, "B6", 8, 12, 2, 2, kind="block"), st(P, "B6", 10, 12, 2, 2, kind="block")]
PLANK_STACK = [st(P, "B6", 0, 14, 2, 2, kind="crate"), st(P, "B6", 2, 14, 2, 2, kind="crate")]
POWDER_CRATES = [st(P, "B6", 10, 4, 2, 2, kind="crate"), st(P, "B6", 12, 4, 2, 2, kind="crate")]

# --- viking age
V_BOAT = st(V, VK, 0, 0, px=(578, 528, 122, 48), kind="boat")
V_BOAT2 = st(V, VK, 0, 0, px=(576, 576, 124, 48), kind="boat")
V_FENCE = [st(V, VK, 8, r, 2, 1, kind="fence") for r in (10, 11, 12)]
V_FENCE_B = st(V, VK, 8, 13, 2, 1, kind="fence")
V_CRATES = [st(V, VK, c, 10, 1, 1, kind="crate") for c in (10, 11, 12)] + [st(V, VK, c, 13, 1, 1, kind="crate") for c in (10, 11, 12)]
V_BARRELS = [st(V, VK, c, 11, 1, 1, kind="barrel") for c in (10, 11)] + [st(V, VK, c, 12, 1, 1, kind="barrel") for c in (10, 11, 12)]
V_FOODBOX = [st(V, VK, 10, 14, 1, 1, kind="crate"), st(V, VK, 11, 14, 1, 1, kind="crate")]
V_HUT = [st(V, VK, c, r, 2, 2, kind="house", solid=1) for (c, r) in ((8, 0), (8, 2), (4, 8), (6, 8), (8, 8), (10, 8))]
V_SHED = [st(V, VK, 12, 4, 2, 2, kind="house"), st(V, VK, 14, 4, 2, 2, kind="house"), st(V, VK, 12, 6, 2, 2, kind="house")]
V_TOWER = st(V, VK, 8, 4, 2, 4, kind="block", cols=(0, 1))
V_BARREL_PILE = st(V, V2, 8, 4, 2, 2, kind="barrel")
V_CRATE_PILE = st(V, V2, 10, 4, 2, 2, kind="crate")
V_BARREL_PILE2 = st(V, V2, 8, 6, 2, 2, kind="barrel")
V_CRATE_PILE2 = st(V, V2, 11, 6, 2, 2, kind="crate")
V_NET_PILE = st(V, V2, 12, 4, 2, 2, kind="crate")
V_ROPES = st(V, V2, 13, 6, 1, 2, solid=0)
V_ROPE_COIL = st(V, V2, 13, 8, 1, 1, solid=0)
V_BARRELS3 = st(V, V2, 8, 12, 2, 2, kind="barrel")
V_CRATES3 = st(V, V2, 10, 12, 2, 2, kind="crate")
V_CRATES4 = st(V, V2, 12, 12, 2, 2, kind="crate")
V_TENT = [st(V, V2, 14, 4, 2, 2, kind="tent"), st(V, V2, 14, 6, 2, 2, kind="tent"), st(V, V2, 14, 12, 2, 2, kind="tent"),
          st(V, V2, 14, 14, 2, 2, kind="tent"), st(V, V2, 12, 14, 2, 2, kind="tent")]
V_NET_HANG = st(V, V2, 8, 14, 1, 2, kind="block")
V_NET = st(V, V2, 9, 15, 1, 1, solid=0, flat=True)
V_OARS = st(V, V2, 14, 11, 2, 1, solid=0)
V_LONGSHIP = st(V, V2, 0, 12, 4, 4, kind="boat")                    # bare-mast longship (moored hulk)
V_LONGSHIP2 = st(V, V2, 4, 12, 4, 4, kind="boat")
V_LONGSHIP_SAIL = st(V, V2, 8, 8, 5, 4, kind="boat")
V_DOCK_POST = st(V, V2, 0, 0, 1, 1, solid=0)
FIREBOWL = st(V, V3, 0, 0, 2, 2, kind="brazier")
FIREBOWL2 = st(V, V3, 0, 2, 2, 2, kind="brazier")
EMBERS_RING = st(V, V3, 2, 2, 2, 1, kind="brazier")
FIREPIT = st(V, V3, 0, 3, 2, 2, kind="brazier")
FIREPIT2 = st(V, V3, 2, 3, 2, 2, kind="brazier")
EMBER_BOWL = st(V, V3, 0, 5, 2, 1, kind="brazier")
BRAZIER_S = st(V, V3, 2, 5, 1, 1, kind="brazier")
TUB_V = st(V, V3, 3, 5, 1, 1, kind="barrel")
LONG_TABLE = st(V, V3, 4, 0, 4, 2, kind="table")
LONG_TABLE2 = st(V, V3, 8, 0, 4, 2, kind="table")
LONG_TABLE3 = st(V, V3, 4, 2, 4, 2, kind="table")
GREY_TABLE = st(V, V3, 8, 2, 4, 2, kind="table")
BENCH_L = st(V, V3, 8, 4, 4, 1, kind="bench")
BENCH_S = st(V, V3, 4, 5, 2, 1, kind="bench")
STOOLS_V = [st(V, V3, c, 5, 1, 1, kind="bench") for c in (6, 7, 8, 9, 10)]
SIGN_ARCH = st(V, V3, 0, 8, 2, 2, kind="sign")
SIGNS = [st(V, V3, c, 8, 2, 2, kind="sign") for c in (2, 4, 6, 8, 10)]
ARROWS = [st(V, V3, c, 8, 1, 2, kind="sign") for c in (12, 13, 14, 15)]
FIREWOOD = [st(V, V3, c, 10, 2, 2, kind="crate") for c in (6, 8, 10, 12)]
LOGS = [st(V, V3, 4, 12, 2, 2, kind="crate"), st(V, V3, 0, 13, 2, 1, kind="crate"), st(V, V3, 2, 13, 2, 1, kind="crate")]
CHOP = [st(V, V3, 6, 12, 1, 1, kind="crate"), st(V, V3, 7, 12, 1, 1, kind="crate"), st(V, V3, 10, 12, 1, 1, kind="crate")]
STUMPS = [st(V, V3, 11, 12, 1, 1, kind="crate"), st(V, V3, 11, 13, 1, 1, kind="crate"), st(V, V3, 7, 13, 1, 1, kind="crate")]
CISTERN = st(V, V3, 8, 12, 2, 2, kind="well")
CISTERN2 = st(V, V3, 12, 12, 2, 2, kind="well")

# --- survival island sheet 4
FISH_RACK = st("island", "4", 8, 4, 2, 2, kind="laundry")
LAUNDRY = st("island", "4", 11, 4, 2, 2, kind="laundry")
FISH_RACK2 = st("island", "4", 8, 12, 2, 2, kind="laundry")
LAUNDRY2 = st("island", "4", 10, 12, 2, 2, kind="laundry")
NET_RACK = st("island", "4", 12, 13, 2, 2, kind="laundry")
FISH_HANG = st("island", "4", 14, 12, 2, 3, kind="laundry")
LAUNDRY3 = st("island", "4", 14, 13, 2, 2, kind="laundry")
LEANTO = st("island", "4", 8, 6, 2, 2, kind="tent")
SHED_TALL = st("island", "4", 11, 6, 2, 2, kind="house")
STOVE = st("island", "4", 4, 6, 2, 2, kind="brazier")
STOVE2 = st("island", "4", 6, 6, 2, 2, kind="brazier")
FIRE_RING = st("island", "4", 0, 6, 2, 2, kind="brazier", solid=1)
FIRE_RING_OUT = st("island", "4", 2, 6, 2, 2, kind="brazier", solid=1)
TIMBER_HEAP = st("island", "4", 6, 11, 2, 1, kind="rubble")
ROUNDHUT = st("island", "4", 0, 4, 2, 2, kind="house")
BARN = st("island", "4", 4, 0, 4, 3, kind="house", solid=2)
LOG_HUT = st("island", "4", 6, 4, 2, 2, kind="house")
WATCH_HUT = st("island", "4", 14, 4, 2, 4, kind="house", cols=(0, 1))
TOWER_OPEN = st("island", "4", 5, 12, 2, 4, kind="block", cols=(0, 1))
CANVAS_TENT = st("island", "4", 0, 10, 2, 2, kind="tent")
CANVAS_TENT3 = st("island", "4", 2, 10, 3, 2, kind="tent")
SMALL_TENT = st("island", "4", 8, 14, 2, 2, kind="tent")
PALISADE_BROKEN = [st("island", "4", c, 13, 1, 1, kind="fence") for c in (0, 1, 2, 3, 4)]

# --- army camp
AWNING = st("camp", "2", 8, 8, 4, 4, solid=0)                        # open canvas awning on poles
AWNING_S = st("camp", "2", 8, 0, 2, 2, kind="tent")
CANVAS_WALL = [st("camp", "2", 12, 2, 2, 1, kind="tent", solid=0), st("camp", "2", 14, 2, 2, 1, kind="tent", solid=0)]
CANOPY_RAILS = [st("camp", "2", 8, 2, 2, 1, solid=0), st("camp", "2", 10, 2, 2, 1, solid=0)]
TENTS_CAMP = [st("camp", "2", c, r, 2, 2, kind="tent") for (c, r) in ((0, 4), (2, 4), (4, 4), (8, 4), (10, 4), (12, 4), (14, 4),
                                                                     (0, 6), (2, 6), (4, 6), (8, 6), (10, 6), (12, 6), (14, 6))]
TENT_STORE = [st("camp", "2", 8, 0, 2, 2, kind="tent"), st("camp", "2", 14, 0, 2, 2, kind="tent")]
COTS = [st("camp", "2", 0, 8, 1, 2, kind="bed"), st("camp", "2", 2, 8, 1, 2, kind="bed"), st("camp", "2", 4, 8, 1, 2, kind="bed")]
BEDROLLS = [st("camp", "2", 3, 8, 1, 1, solid=0), st("camp", "2", 3, 9, 1, 1, solid=0), st("camp", "2", 5, 8, 1, 1, solid=0),
            st("camp", "2", 5, 9, 1, 1, solid=0)]
TRIPOD_POT = st("camp", "2", 0, 10, 2, 2, kind="brazier")
TRIPOD_POT2 = st("camp", "2", 2, 10, 2, 2, kind="brazier")
CAMP_FIRE = st("camp", "2", 0, 12, 2, 2, kind="brazier")
MAP_TABLE = st("camp", "2", 4, 10, 2, 2, kind="table")
CAMP_CHESTS = [st("camp", "2", 0, 14, 1, 1, kind="crate"), st("camp", "2", 1, 14, 1, 1, kind="crate")]
CAMP_BARRELS = [st("camp", "2", 2, 14, 1, 1, kind="barrel"), st("camp", "2", 3, 14, 1, 1, kind="barrel")]
CAMP_STOOLS = [st("camp", "2", c, r, 1, 1, kind="bench") for (c, r) in ((5, 14), (6, 14), (2, 15), (3, 15), (5, 15), (6, 15))]
PEN_BENCH = st("camp", "2", 8, 12, 4, 4, kind="block", solid=2)     # timber enclosure with bench and barrel
PEN_MAP = st("camp", "2", 12, 12, 4, 4, kind="block", solid=2)
CAMP5_FIRES = [st("camp", "5", 0, 0, 2, 2, kind="brazier"), st("camp", "5", 4, 0, 2, 2, kind="brazier")]
FIRE_BASKET = st("camp", "5", 2, 0, 2, 2, kind="brazier")
WELL_ROOF = st("camp", "5", 6, 0, 2, 2, kind="well")
WELL_ROOF2 = st("camp", "5", 4, 4, 2, 2, kind="well")
SUPPLY_CRATE = st("camp", "5", 5, 4, 1, 2, kind="crate")
OVEN = st("camp", "5", 6, 4, 2, 2, kind="brazier")
OVENS = [st("camp", "5", 8, 6, 1, 2, kind="brazier"), st("camp", "5", 9, 6, 1, 2, kind="brazier")]
CAULDRONS = [st("camp", "5", c, 5, 1, 1, kind="brazier") for c in (8, 9, 10)]
TRIPOD = st("camp", "5", 11, 4, 2, 2, kind="brazier")
CAMP_TABLE = st("camp", "5", 6, 2, 2, 2, kind="table")
TRESTLE = [st("camp", "5", 0, 2, 3, 2, kind="table"), st("camp", "5", 3, 2, 3, 2, kind="table")]
CAMP_CRATES = [st("camp", "5", c, 2, 1, 2, kind="crate") for c in (8, 9, 10, 11)]
CAMP_BARRELS5 = [st("camp", "5", 11, 6, 1, 2, kind="barrel"), st("camp", "5", 12, 6, 1, 2, kind="barrel")]
POT_PLANT = st("camp", "5", 12, 2, 1, 1, kind="barrel")
HAY_HUT = st("camp", "5", 13, 5, 3, 3, kind="house")
TOOL_SHED = st("camp", "5", 0, 11, 4, 3, kind="house", solid=2)
SUPPLY_SHED = st("camp", "5", 4, 11, 4, 3, kind="house", solid=2)
STALL_TOOLS = st("camp", "5", 13, 0, 3, 2, kind="counter")
STALL_AWNING = st("camp", "5", 13, 2, 3, 3, kind="counter", solid=2)
FIREWOOD_S = st("camp", "5", 2, 4, 2, 1, kind="crate", solid=0)
TRIPOD_FIRE = st("camp", "5", 8, 10, 1, 2, kind="brazier")
CAMP_LANTERN = st("camp", "5", 9, 10, 1, 1, kind="lamp")
BANNER_POLE = st("camp", "5", 10, 8, 1, 2, kind="sign")
HANG_LANTERN = st("camp", "5", 8, 0, 1, 1, kind="lamp")
WOODPILE = st("camp", "5", 2, 15, 1, 1, kind="crate")

# --- desert wasteland sheet 6: the salvage camp (tents patched with scrap, shacks, junk heaps)
D = "desert"
PATCH_TENTS = [st(D, "6", c, r, 2, 2, kind="tent") for (c, r) in ((0, 0), (2, 0), (0, 2), (2, 2), (0, 4), (2, 4))]
LOW_TENTS = [st(D, "6", 4, r, 2, 2, kind="tent") for r in (0, 2, 4)]
SCRAP_TENTS = [st(D, "6", 6, 0, 2, 2, kind="tent"), st(D, "6", 6, 2, 2, 2, kind="tent"), st(D, "6", 6, 4, 2, 2, kind="tent")]
SHELTERS = [st(D, "6", 8, 0, 2, 2, kind="tent"), st(D, "6", 8, 2, 2, 2, kind="tent")]
LEANTOS = [st(D, "6", 10, 0, 2, 2, kind="tent"), st(D, "6", 10, 2, 2, 2, kind="tent")]
WORKBENCH = st(D, "6", 8, 4, 2, 2, kind="table")
STALL_LEAN = st(D, "6", 10, 4, 2, 2, kind="counter")
SHACKS = [st(D, "6", c, r, 2, 2, kind="house") for (c, r) in ((12, 0), (14, 0), (12, 2), (14, 2), (12, 4), (14, 4))]
DFIRE = [st(D, "6", 0, 6, 2, 2, kind="brazier"), st(D, "6", 2, 6, 2, 2, kind="brazier"), st(D, "6", 4, 6, 2, 2, kind="brazier")]
GRILL = st(D, "6", 6, 6, 2, 2, kind="brazier")
PIT = st(D, "6", 8, 6, 2, 2, kind="brazier")
PIT_POT = st(D, "6", 10, 6, 2, 2, kind="brazier")
HIDE_RACK = [st(D, "6", 12, 6, 2, 2, kind="laundry"), st(D, "6", 14, 6, 2, 2, kind="laundry")]
D_CRATES = [st(D, "6", 0, 8, 1, 2, kind="crate"), st(D, "6", 1, 8, 1, 2, kind="crate"), st(D, "6", 2, 8, 1, 2, kind="crate"),
            st(D, "6", 3, 8, 1, 2, kind="crate")]
SANDBAGS = [st(D, "6", 4, 8, 2, 2, kind="block"), st(D, "6", 8, 8, 2, 2, kind="block"), st(D, "6", 10, 8, 2, 2, kind="block")]
SLEEPBAG = st(D, "6", 6, 8, 2, 2, solid=0)
SLEEP_GREEN = st(D, "6", 12, 8, 2, 2, solid=0)
SLEEP_ROLL = st(D, "6", 14, 8, 2, 2, solid=0)
CHEST_CRATE = st(D, "6", 0, 10, 2, 2, kind="crate")
SCRAP_FENCE = [st(D, "6", 2, 10, 2, 2, kind="fence"), st(D, "6", 4, 10, 2, 2, kind="fence"), st(D, "6", 8, 10, 2, 2, kind="fence"),
               st(D, "6", 10, 10, 2, 2, kind="fence")]
WATER_TUB = st(D, "6", 12, 10, 2, 2, kind="barrel")
WATER_BARRELS = st(D, "6", 14, 10, 2, 2, kind="barrel")
RAGFLAG = [st(D, "6", 2, 12, 2, 2, kind="sign"), st(D, "6", 8, 12, 2, 2, kind="sign")]
LOOKPOST = [st(D, "6", 4, 12, 2, 2, kind="block"), st(D, "6", 6, 12, 2, 2, kind="block")]
SALVAGE = [st(D, "6", 10, 12, 2, 2, kind="rubble"), st(D, "6", 6, 14, 2, 2, kind="rubble"), st(D, "6", 8, 14, 2, 2, kind="rubble"),
           st(D, "6", 10, 14, 2, 2, kind="rubble")]
TOOL_POST = st(D, "6", 14, 12, 2, 2, kind="block")
SCRAP_WALL = [st(D, "6", 12, 14, 2, 2, kind="fence"), st(D, "6", 14, 14, 2, 2, kind="fence")]
FLAGS_TORN = [st(D, "6", 0, 14, 2, 2, kind="sign"), st(D, "6", 2, 14, 2, 2, kind="sign"), st(D, "6", 4, 14, 2, 2, kind="sign")]
D5_SACKS = [st(D, "5", 14, 0, 2, 2, kind="crate"), st(D, "5", 14, 2, 2, 2, kind="crate")]
D5_PLANKS = st(D, "5", 4, 2, 2, 2, kind="rubble")
D5_SCRAP = [st(D, "5", 12, 0, 2, 2, kind="rubble"), st(D, "5", 12, 2, 2, 2, kind="rubble")]
D5_CRATE = st(D, "5", 2, 2, 2, 2, kind="crate")
D5_BROKEN_CRATE = st(D, "5", 6, 0, 2, 2, kind="crate")
D5_SACKPILE = [st(D, "5", 0, 14, 2, 2, kind="crate"), st(D, "5", 2, 14, 2, 2, kind="crate"), st(D, "5", 8, 14, 2, 2, kind="crate"),
               st(D, "5", 10, 14, 2, 2, kind="crate")]
D5_RUBBLE = [st(D, "5", 4, 14, 2, 2, kind="rubble"), st(D, "5", 6, 14, 2, 2, kind="rubble")]
D5_SIGNS = [st(D, "5", c, 8, 1, 2, kind="sign") for c in (2, 3, 4, 6, 7, 8, 9)]
D5_POTS = [st(D, "5", 12, 12, 1, 1, kind="barrel"), st(D, "5", 13, 12, 1, 1, kind="barrel")]

# medieval town sheet 2 market stalls (awning + counter)
STALLS = [st("town", "2", c, 4, 2, 2, kind="counter") for c in (0, 2, 4, 6, 8)]

# black rock and lava decals (baked flat)
ROCKS_BIG = [RampStamp(P, "B8", 8, 12, 2, 2), RampStamp(P, "B10", 12, 12, 2, 2), RampStamp(P, "B9", 14, 12, 2, 2)]
ROCKS_S = [RampStamp(P, "B8", c, 12, 1, 1) for c in (10, 11, 14, 15)] + [RampStamp(P, "B9", 14, 12, 1, 1), RampStamp(P, "B9", 15, 12, 1, 1)]
PEBBLES = [RampStamp(P, "B8", c, 13, 1, 1, stops=BASALT_RAMP) for c in (9, 10, 11, 12, 13, 14, 15)]
TUFTS_ASH = [RampStamp(D, "1", c, 14, 1, 1, stops=BASALT_RAMP) for c in (2, 3)]


# ------------------------------------------------------------------------------------------------ generated sheet
# Objects that must stand over the animated sea (so they cannot be baked into the ground): black rocks recoloured
# from the Pirate Age beach rocks, and timber pilings drawn in code. Written once to
# Assets/_processed/hearth/hearth_gen.png (1x, 48 px grid) and used like any other sheet (alias "hgen").
kit.PACKS.setdefault("hgen", "_processed/hearth")
GEN_ROCKS = [((0, 0, 2, 2), ("pirate", "B8", 8, 12, 2, 2)), ((2, 0, 2, 2), ("pirate", "B10", 12, 12, 2, 2)),
             ((4, 0, 1, 1), ("pirate", "B8", 10, 12, 1, 1)), ((5, 0, 1, 1), ("pirate", "B8", 11, 12, 1, 1)),
             ((6, 0, 1, 1), ("pirate", "B8", 14, 12, 1, 1)), ((7, 0, 1, 1), ("pirate", "B8", 15, 12, 1, 1)),
             ((8, 0, 1, 1), ("pirate", "B9", 14, 12, 1, 1)), ((9, 0, 1, 1), ("pirate", "B9", 15, 12, 1, 1)),
             ((4, 1, 1, 1), ("pirate", "B10", 4, 14, 1, 1)), ((5, 1, 1, 1), ("pirate", "B10", 5, 14, 1, 1)),
             ((6, 1, 1, 1), ("pirate", "B10", 6, 14, 1, 1)), ((7, 1, 1, 1), ("pirate", "B10", 7, 14, 1, 1)),
             ((8, 1, 1, 1), ("pirate", "B10", 4, 15, 1, 1)), ((9, 1, 1, 1), ("pirate", "B10", 5, 15, 1, 1)),
             ((10, 0, 2, 2), ("pirate", "B9", 14, 12, 2, 2))]


def _piling(n, rope):
    im = np.zeros((C, C, 4), np.uint8)
    xs = [21] if n == 1 else [12, 30]
    for px in xs:
        for y in range(6, 40):
            for x in range(px, px + 7):
                c = WOOD[2] if x == px + 1 else (WOOD[1] if x < px + 4 else (WOOD[0] if x < px + 6 else WOOD[4]))
                im[y, x, :3] = c
                im[y, x, 3] = 255
        im[6, px:px + 7, :3] = WOOD[3]
        im[7, px:px + 7, :3] = WOOD[3]
        for x in range(px - 2, px + 9):          # glow ring where the post meets the red water
            im[40, x, :3] = (236, 120, 50)
            im[40, x, 3] = 210
            im[41, x, :3] = (150, 40, 22)
            im[41, x, 3] = 170
        if rope:
            im[12:15, px:px + 7, :3] = (176, 150, 106)
            im[13, px:px + 7, :3] = (120, 98, 68)
    if n == 2 and rope:
        for x in range(19, 30):                    # sagging rope between the pair
            y = 14 + int(3 * np.sin((x - 19) / 11 * np.pi))
            im[y, x, :3] = (150, 124, 86)
            im[y, x, 3] = 255
    return im


def make_gen_sheet():
    out = np.zeros((16 * C, 16 * C, 4), np.uint8)
    for (c, r, w, h), (al, sh, sc, sr, sw, shh) in GEN_ROCKS:
        a = np.array(kit.sheet_img(al, sh).crop((sc * C, sr * C, (sc + sw) * C, (sr + shh) * C)))
        out[r * C:(r + h) * C, c * C:(c + w) * C] = ramp(a, ROCK_RAMP)
    for i, (n, rope) in enumerate(((1, False), (1, True), (2, False), (2, True))):
        out[2 * C:3 * C, i * C:(i + 1) * C] = _piling(n, rope)
    d = os.path.join(kit.ASSETS, kit.PACKS["hgen"])
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "hearth_gen.png")
    old = np.array(Image.open(p).convert("RGBA")) if os.path.exists(p) else None
    if old is None or old.shape != out.shape or (old != out).any():
        Image.fromarray(out, "RGBA").save(p, optimize=True)


make_gen_sheet()
G = "hgen"
GS = "hearth_gen"
REEF_BIG = [st(G, GS, 0, 0, 2, 2, kind="rock"), st(G, GS, 2, 0, 2, 2, kind="rock"), st(G, GS, 10, 0, 2, 2, kind="rock")]
REEF_S = [st(G, GS, c, r, 1, 1, kind="rock") for c in range(4, 10) for r in (0, 1)]
PILING = [st(G, GS, c, 2, 1, 1, kind="block") for c in range(4)]
# floating things (objects over the animated sea)
DRIFT = [st(P, "B8", 2, 12, 2, 1, kind="water"), st(P, "B8", 2, 13, 2, 1, kind="water"), st(P, "B9", 8, 12, 2, 1, kind="water"),
         st(P, "B9", 10, 12, 2, 1, kind="water")]
BUOYS = [st(P, "B9", 2, 12, 1, 1, kind="water"), st(P, "B9", 4, 12, 1, 1, kind="water"), st(P, "B9", 5, 12, 1, 1, kind="water")]

# flat decals for the pontoon boards: split/patched boards (Pirate Age broken deck), dropped cloth, nets, rope
DECK_DECALS = [st(P, "B1-1", 10, 15, 1, 1, flat=True, solid=0), st(P, "B1-1", 11, 15, 1, 1, flat=True, solid=0),
               st(V, V2, 9, 15, 1, 1, flat=True, solid=0), st(P, "B1-1", 14, 13, 1, 1, flat=True, solid=0),
               st(P, "B4", 6, 1, 1, 1, flat=True, solid=0), st(P, "B4", 7, 2, 1, 1, flat=True, solid=0),
               st("camp", "2", 3, 9, 1, 1, flat=True, solid=0), st("camp", "2", 5, 9, 1, 1, flat=True, solid=0),
               st(P, "B1-1", 10, 14, 1, 1, flat=True, solid=0), st(P, "B1-1", 11, 14, 1, 1, flat=True, solid=0)]
