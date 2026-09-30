"""maps48 kit: author native-48px maps (overhaul step 5-6) in Python.

A map script builds a Map: materials per cell (ground), stamps (multi-cell sprites cut from the owner's CuteSCKR sheets
by cell rectangle), field animations and entities. save() writes
  game/assets/ext/maps48/<ID>_ground.png   baked ground (materials with ragged organic edges + flat stamps)
  game/assets/ext/maps48/<ID>.json         y-sorted objects, animations, used sheets (runtime: field/art48.gd)
  content_src/maps/z48_<group>.map         the collision grid (kinds), header and entities (read by compile_content;
                                            later files override the old definitions of the same map id)
Coordinates: cells (x right, y down); one cell = 48 px = 16 game units.
"""
import os, json, random, shutil, math
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
EXT = os.path.join(REPO, "game", "assets", "ext")
C = 48

PACKS = {
    "town": "CuteSCKR/Medieval Fantasy Town Pixel Art Tileset Pack",
    "castle": "CuteSCKR/Medieval Castle Fantasy - Pixel Art Tileset",
    "siege": "CuteSCKR/Medieval Siege & Castle Tileset/medieval siege",
    "steam": "CuteSCKR/Steampunk Pixel Art Tileset",
    "pirate": "CuteSCKR/Pirate Age Pixel Tileset Pack",
    "viking": "CuteSCKR/Viking Age Pixel Art Tileset Pack",
    "roman": "CuteSCKR/Roman Empire Pixel Art Tileset",
    "camp": "CuteSCKR/Medieval Army Camp Tileset Pack",
    "sea": "CuteSCKR/Underwater World & Sunken Ruins Pixel Art Tileset",
    "forest": "CuteSCKR/Forest Wilderness Pixel Art Tileset Pack",
    "dungeon": "CuteSCKR/Medieval Fantasy Dungeon & Prison Pixel Art Tileset Pack",
    "plague": "CuteSCKR/Medieval Plague Town Tileset/plague age",
    "ruins": "CuteSCKR/Medieval Battlefield & Ruins Pixel Art Tileset Pack",
    "farm": "CuteSCKR/Farm Tileset - Pixel Art/farm",
    "desert": "CuteSCKR/Desert Wasteland Pixel Tileset",
    "gothic": "CuteSCKR/Dark Gothic City Pixel Art Tileset Pack",
    "factory": "CuteSCKR/Factory Ruins Pixel Art Tileset Pack",
    "dreamy": "CuteSCKR/Dreamy World Pixel Art Tileset Pack",
    "island": "CuteSCKR/Survival Island Pixel Art Tileset",
    "jungle": "CuteSCKR/Rainforest Survival Pixel Art Tileset Pack",
    "mansion": "CuteSCKR/Haunted Mansion Pixel Art Tileset Pack",
    "fa": "_processed/field_anim",
    "cursed": "_processed/land_objects/cursed",
    "undead": "_processed/land_objects/undead",
}

_img_cache = {}
_gen_written = set()


def sheet_path(alias, sheet):
    return os.path.join(ASSETS, PACKS[alias], sheet + ".png")


def sheet_img(alias, sheet):
    k = (alias, sheet)
    if k not in _img_cache:
        _img_cache[k] = Image.open(sheet_path(alias, sheet)).convert("RGBA")
    return _img_cache[k]


class Stamp:
    """A sprite cut from a sheet. rect in cells (c, r, w, h) unless px=(x, y, w, h) is given.
    solid: rows (counted from the bottom, 1 = bottom row) that block movement; 0 = none. cols: optional (c0, c1)
    column span (relative) that is solid. flat: baked into the ground (never drawn over actors).
    kind: collision kind written into the grid for solid cells. door: (dx, dy) cell of the door, relative."""

    def __init__(self, alias, sheet, c, r, w=1, h=1, px=None, solid=1, cols=None, flat=False, kind="block", door=None,
                 base=None, name="", hgrid=1):
        self.alias, self.sheet = alias, str(sheet)
        self.px = px if px else (c * C, r * C, w * C, h * C)
        self.w = max(1, round(self.px[2] / C))
        self.h = max(1, round(self.px[3] / C))
        self.solid, self.cols, self.flat, self.kind, self.door, self.name = solid, cols, flat, kind, door, name
        self.base = base
        self.hgrid = hgrid      # grid rows the stamp stands on (auto-skin); the rest overhangs upwards

    def auto_base(self):
        a = np.array(self.image())[..., 3]
        ys = np.nonzero(a.sum(axis=1))[0]
        return int(ys.max()) + 1 if len(ys) else self.px[3]

    def image(self):
        x, y, w, h = self.px
        return sheet_img(self.alias, self.sheet).crop((x, y, x + w, y + h))


def st(alias, sheet, c, r, w=1, h=1, **kw):
    return Stamp(alias, sheet, c, r, w, h, **kw)


class RailStamp:
    """48x48 piece of railway: dark sleepers under two steel rails (drawn in code, palette matched to the town set)."""
    _img = None

    def image(self):
        if RailStamp._img is None:
            im = Image.new("RGBA", (C, C), (0, 0, 0, 0))
            px = im.load()
            for x0 in range(2, C, 12):
                for x in range(x0, x0 + 8):
                    for y in range(8, 42):
                        shade = (92, 66, 44, 255) if y not in (8, 41) and x not in (x0, x0 + 7) else (58, 40, 28, 255)
                        px[x, y] = shade
            for ry in (14, 33):
                for x in range(C):
                    px[x, ry] = (208, 212, 222, 255)
                    px[x, ry + 1] = (138, 142, 156, 255)
                    px[x, ry + 2] = (70, 72, 84, 255)
            RailStamp._img = im
        return RailStamp._img


class Mat:
    """Ground material: tiled texture from one or more source rectangles (px) on sheets.
    organic: edges against other organic materials are ragged; kind: collision/encounter kind for the grid."""

    def __init__(self, sources, kind, organic=False, prio=0, solid=False, edge=None):
        self.sources, self.kind, self.organic, self.prio, self.solid, self.edge = sources, kind, organic, prio, solid, edge
        self._tex = None

    def texture(self):
        if self._tex is None:
            tiles = []
            for src in self.sources:
                if src[0] == "color":
                    t = np.zeros((C, C, 4), dtype=np.uint8)
                    t[..., :3] = src[1]
                    t[..., 3] = 255
                    tiles.append(t)
                    continue
                (alias, sheet, x, y, w, h) = src
                tiles.append(np.array(sheet_img(alias, sheet).crop((x, y, x + w, y + h)).convert("RGBA")))
            self._tex = tiles
        return self._tex


def _value_noise(h, w, scale, seed):
    rng = np.random.default_rng(seed)
    gh, gw = h // scale + 3, w // scale + 3
    g = rng.random((gh, gw))
    ys = np.arange(h) / scale
    xs = np.arange(w) / scale
    y0 = ys.astype(int)
    x0 = xs.astype(int)
    fy = (ys - y0)[:, None]
    fx = (xs - x0)[None, :]
    fy = fy * fy * (3 - 2 * fy)
    fx = fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]
    b = g[y0][:, x0 + 1]
    c = g[y0 + 1][:, x0]
    d = g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


_ALPHA = {}
_RGBA = {}
_LABELS = {}


def _sheet_arrays(rel):
    """Sheet pixels plus an object segmentation: touching objects are split where they meet by eroding 2 px,
    labelling, then giving every pixel to its nearest eroded blob."""
    if rel not in _RGBA:
        import numpy as np
        from scipy import ndimage
        im = np.array(Image.open(os.path.join(EXT, rel)).convert("RGBA"))
        a = im[..., 3] > 0
        core = ndimage.binary_erosion(a, iterations=2)
        lab0, n = ndimage.label(core, structure=np.ones((3, 3)))
        if n:
            _, (iy, ix) = ndimage.distance_transform_edt(lab0 == 0, return_indices=True)
            lab = np.where(a, lab0[iy, ix], 0)
        else:
            lab, _ = ndimage.label(a, structure=np.ones((3, 3)))
        _RGBA[rel], _ALPHA[rel] = im, a
        _LABELS[rel] = (lab, ndimage.find_objects(lab))
    return _RGBA[rel], _ALPHA[rel], _LABELS[rel]


def _clipped_sides(a, sx, sy, sw, sh):
    H, W = a.shape
    return (sy > 0 and (a[sy, sx:sx + sw] & a[sy - 1, sx:sx + sw]).sum() > 2,
            sy + sh < H and (a[sy + sh - 1, sx:sx + sw] & a[sy + sh, sx:sx + sw]).sum() > 2,
            sx > 0 and (a[sy:sy + sh, sx] & a[sy:sy + sh, sx - 1]).sum() > 2,
            sx + sw < W and (a[sy:sy + sh, sx + sw - 1] & a[sy:sy + sh, sx + sw]).sum() > 2)


def _fixed_stamp(rel, sx, sy, sw, sh):
    """Returns (new_rel, dx, dy, w, h) for a stamp whose rectangle slices an object, or None. The stamp becomes the
    objects that mostly sit inside its rectangle (whole, masked), dropping bits of neighbours that poke in."""
    import numpy as np
    im, a, (lab, objs) = _sheet_arrays(rel)
    if not any(_clipped_sides(a, sx, sy, sw, sh)):
        return None
    inside = lab[sy:sy + sh, sx:sx + sw]
    keep = []
    for v in np.unique(inside):
        if not v:
            continue
        sl = objs[v - 1]
        total = int((lab[sl] == v).sum())
        ins = int((inside == v).sum())
        if ins >= 0.35 * total:
            keep.append(int(v))
    if not keep:
        return None
    # slivers of neighbours cut by the rectangle: small blobs lying against its edge
    sizes = {v: int((lab[objs[v - 1]] == v).sum()) for v in keep}
    big = max(sizes.values())
    def at_edge(v):
        sl = objs[v - 1]
        return sl[1].start <= sx or sl[1].stop >= sx + sw or sl[0].start <= sy or sl[0].stop >= sy + sh
    keep = [v for v in keep if sizes[v] >= 0.06 * big or not at_edge(v)]
    y0 = min(objs[v - 1][0].start for v in keep); y1 = max(objs[v - 1][0].stop for v in keep)
    x0 = min(objs[v - 1][1].start for v in keep); x1 = max(objs[v - 1][1].stop for v in keep)
    if x0 < sx - 72 or y0 < sy - 144 or x1 > sx + sw + 72 or y1 > sy + sh + 72:
        return None
    mask = np.isin(lab[y0:y1, x0:x1], keep)
    piece = im[y0:y1, x0:x1].copy()
    piece[~mask] = 0
    alias_sheet = rel[len("cute/"):-4].replace("/", "_")
    new_rel = "cute/_fix/%s_%d_%d_%d_%d.png" % (alias_sheet, sx, sy, sw, sh)
    dst = os.path.join(EXT, new_rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    Image.fromarray(piece).save(dst)
    return new_rel, sx - x0, sy - y0, x1 - x0, y1 - y0


def unclip(objs, sheets, reach=48):
    """Stamps are cut by cell rectangles, which can slice through an object that overhangs its cells (a rubble pile, a
    shelf side, a tree crown). Replace such stamps with a cleanly masked cut of the whole object (cute/_fix/...)."""
    out = []
    extra = {}
    for o in objs:
        si, sx, sy, sw, sh, x, y, base = o
        try:
            fx = _fixed_stamp(sheets[si], sx, sy, sw, sh)
        except Exception:
            fx = None
        if not fx:
            out.append(o); continue
        rel, dx, dy, w, h = fx
        if rel not in extra:
            extra[rel] = len(sheets)
            sheets.append(rel)
        out.append([int(extra[rel]), 0, 0, int(w), int(h), int(x - dx), int(y - dy), base])
    return out


class Map:
    def __init__(self, mid, w, h, name, tileset, music="", zone="", location="", region="", group="misc", seed=None, **hdr):
        self.id, self.w, self.h = mid, w, h
        self.hdr = {"name": name, "tileset": tileset, "music": music, "zone": zone, "location": location, "region": region}
        self.hdr.update({k: v for k, v in hdr.items() if v is not None})
        self.group = group
        self.mat = [[None] * w for _ in range(h)]
        self.kind = [[None] * w for _ in range(h)]
        self.objects = []      # (stamp, x_px, y_px, base_px)
        self.flat = []         # (stamp, x_px, y_px)
        self.anims = []        # (name, x_px, y_px, base_px)
        self.over = []         # (stamp, x_px, y_px) drawn above actors
        self.ents = []
        self.rng = random.Random(seed if seed is not None else hash(mid) & 0xffff)
        self.mats = {}

    # ------------------------------------------------------------- ground
    def use(self, **mats):
        self.mats.update(mats)

    def fill(self, m):
        for y in range(self.h):
            for x in range(self.w):
                self.set(x, y, m)

    def set(self, x, y, m, kind=None):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.mat[y][x] = m
            self.kind[y][x] = kind or self.mats[m].kind

    def rect(self, m, x0, y0, x1, y1, kind=None):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, m, kind)

    def blob(self, m, cx, cy, rx, ry, rough=0.35, kind=None):
        for y in range(int(cy - ry - 2), int(cy + ry + 3)):
            for x in range(int(cx - rx - 2), int(cx + rx + 3)):
                d = ((x - cx) / max(rx, 0.5)) ** 2 + ((y - cy) / max(ry, 0.5)) ** 2
                if d <= 1.0 + self.rng.uniform(-rough, rough):
                    self.set(x, y, m, kind)

    def path(self, m, pts, width=2, kind=None):
        """Polyline of cells with the given width (a road or corridor)."""
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = max(abs(bx - ax), abs(by - ay), 1)
            for i in range(n + 1):
                x = round(ax + (bx - ax) * i / n)
                y = round(ay + (by - ay) * i / n)
                for dy in range(width):
                    for dx in range(width):
                        self.set(x + dx - (width - 1) // 2, y + dy - (width - 1) // 2, m, kind)

    def solid(self, x, y, kind="block"):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.kind[y][x] = kind

    def free(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and not self._solid_kind(self.kind[y][x])

    @staticmethod
    def _solid_kind(k):
        return k in SOLID_KINDS

    # ------------------------------------------------------------- stamps
    def place(self, s, x, y, dx=0, dy=0, solid=None, kind=None, over=False):
        """Place stamp s with its top-left at cell (x, y) (+ pixel offset). Returns the base line (px)."""
        px, py = x * C + dx, y * C + dy
        if s.flat:
            self.flat.append((s, px, py))
        elif over:
            self.over.append((s, px, py))
        else:
            base = py + (s.auto_base() if s.base is None else s.base)
            self.objects.append((s, px, py, base))
        rows = s.solid if solid is None else solid
        if rows:
            c0, c1 = s.cols if s.cols else (0, s.w - 1)
            for r in range(s.h - rows, s.h):
                for c in range(c0, c1 + 1):
                    self.solid(x + c, y + r, kind or s.kind)
        if s.door and not dx and not dy:
            self.solid(x + s.door[0], y + s.door[1], "door")
        return py + s.px[3]

    def anim(self, name, x, y, dx=0, dy=0, h=96, solid=False, kind="lamp", flat=False):
        px, py = x * C + dx, y * C + dy
        self.anims.append((name, px, py, 0 if flat else py + h))
        if solid:
            self.solid(x, y + (h // C) - 1, kind)

    def scatter(self, stamps, x0, y0, x1, y1, n, on=None, gap=1, solid=None):
        """Places n random stamps on free cells in the rectangle (only on materials in `on`, if given)."""
        placed = 0
        tries = 0
        while placed < n and tries < n * 40:
            tries += 1
            s = self.rng.choice(stamps)
            x = self.rng.randint(x0, max(x0, x1 - s.w + 1))
            y = self.rng.randint(y0, max(y0, y1 - s.h + 1))
            ok = True
            for yy in range(y - gap + 1, y + s.h + gap - 1):
                for xx in range(x - gap + 1, x + s.w + gap - 1):
                    if not (0 <= xx < self.w and 0 <= yy < self.h):
                        ok = False
                        break
                    if not self.free(xx, yy) or self._reserved(xx, yy):
                        ok = False
                        break
                    if on and self.mat[yy][xx] not in on:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                self.place(s, x, y, solid=solid)
                placed += 1
        return placed

    _res = None

    def reserve(self, cells):
        """Cells kept clear (routes, entity spots): scatter and dressing never use them."""
        if self._res is None:
            self._res = set()
        self._res.update(cells)

    def reserve_rect(self, x0, y0, x1, y1):
        self.reserve([(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)])

    def _reserved(self, x, y):
        return self._res is not None and (x, y) in self._res

    def water_anims(self, mat="water", name="water_deep", skip=()):
        """Animated surface on every cell of material `mat` (flat, under actors)."""
        for y in range(self.h):
            for x in range(self.w):
                if self.mat[y][x] == mat and (x, y) not in skip:
                    self.anim(name, x, y, h=48, flat=True)

    def rails_h(self, y, x0, x1, kind="rail"):
        """A horizontal railway along row y (procedural sleepers and steel, baked flat); the cells get `kind`."""
        for x in range(x0, x1 + 1):
            self.flat.append((RailStamp(), x * C, y * C))
            if kind:
                self.solid(x, y, kind)

    # ------------------------------------------------------------- entities
    def ent(self, line):
        self.ents.append(line)

    # ------------------------------------------------------------- output
    def _ground(self):
        W, H = self.w * C, self.h * C
        names = sorted({m for row in self.mat for m in row if m})
        idx = {m: i for i, m in enumerate(names)}
        cellm = np.array([[idx[m] if m else -1 for m in row] for row in self.mat], dtype=np.int32)
        # per-pixel material index with ragged organic edges (domain warp only where organic meets organic)
        yy, xx = np.mgrid[0:H, 0:W]
        seed = hash(self.id) & 0xffff
        nx = (_value_noise(H, W, 20, seed) - 0.5) * 22 + (_value_noise(H, W, 7, seed + 1) - 0.5) * 7
        ny = (_value_noise(H, W, 20, seed + 2) - 0.5) * 22 + (_value_noise(H, W, 7, seed + 3) - 0.5) * 7
        wx = np.clip((xx + nx).astype(int), 0, W - 1) // C
        wy = np.clip((yy + ny).astype(int), 0, H - 1) // C
        base = cellm[yy // C, xx // C]
        warped = cellm[wy, wx]
        organic = np.array([self.mats[m].organic for m in names] + [False], dtype=bool)
        use = organic[base] & organic[np.where(warped >= 0, warped, len(names))] & (warped >= 0)
        pm = np.where(use, warped, base)
        out = np.zeros((H, W, 4), dtype=np.uint8)
        out[..., 3] = 255
        out[..., :3] = (12, 10, 18)
        for m, i in idx.items():
            mask = pm == i
            if not mask.any() or not self.mats[m].sources:
                continue
            tiles = self.mats[m].texture()
            t0 = tiles[0]
            th, tw = t0.shape[:2]
            tex = np.zeros((H, W, 4), dtype=np.uint8)
            # tile the texture; variant tiles are chosen per tile block with a hash
            for ty in range(0, H, th):
                for tx in range(0, W, tw):
                    t = tiles[((tx // tw) * 7919 + (ty // th) * 104729 + seed) % len(tiles)]
                    hh = min(th, H - ty)
                    ww = min(tw, W - tx)
                    tex[ty:ty + hh, tx:tx + ww] = t[:hh, :ww]
            a = tex[..., 3:4].astype(np.float32) / 255.0
            rgb = out[..., :3].astype(np.float32) * (1 - a) + tex[..., :3].astype(np.float32) * a
            out[..., :3] = np.where(mask[..., None], rgb.astype(np.uint8), out[..., :3])
        # soft shade on the lower-priority side of organic edges (grass lip over dirt)
        prio = np.array([self.mats[m].prio for m in names] + [0])
        pp = prio[np.where(pm >= 0, pm, len(names))]
        up = np.roll(pp, 2, axis=0)
        edge = (up > pp) & organic[np.where(pm >= 0, pm, len(names))]
        out[..., :3] = np.where(edge[..., None], (out[..., :3].astype(np.float32) * 0.72).astype(np.uint8), out[..., :3])
        img = Image.fromarray(out, "RGBA")
        for (s, x, y) in self.flat:
            img.alpha_composite(s.image(), (x, y))
        return img

    def save(self):
        os.makedirs(os.path.join(EXT, "maps48"), exist_ok=True)
        g = self._ground()
        g.convert("RGB").save(os.path.join(EXT, "maps48", self.id + "_ground.png"), optimize=True)
        sheets = []
        sidx = {}

        def sheet_id(s):
            k = (s.alias, s.sheet)
            if k not in sidx:
                rel = "cute/%s/%s.png" % (s.alias, s.sheet.replace("/", "_"))
                dst = os.path.join(EXT, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if k in GEN_SHEETS:
                    if k not in _gen_written:
                        _img_cache[k].save(dst)
                        _gen_written.add(k)
                else:
                    src = sheet_path(s.alias, s.sheet)
                    if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                        shutil.copy2(src, dst)
                sidx[k] = len(sheets)
                sheets.append(rel)
            return sidx[k]
        objs = []
        for (s, x, y, base) in sorted(self.objects, key=lambda o: o[3]):
            objs.append([sheet_id(s), s.px[0], s.px[1], s.px[2], s.px[3], x, y, base])
        objs = unclip(objs, sheets)
        over_name = ""
        if self.over:
            ov = Image.new("RGBA", g.size, (0, 0, 0, 0))
            for (s, x, y) in self.over:
                ov.alpha_composite(s.image(), (x, y))
            over_name = self.id + "_over.png"
            ov.save(os.path.join(EXT, "maps48", over_name), optimize=True)
        data = {"id": self.id, "w": self.w, "h": self.h, "ground": self.id + "_ground.png", "over": over_name,
                "sheets": sheets, "objects": objs, "anims": [list(a) for a in self.anims]}
        json.dump(data, open(os.path.join(EXT, "maps48", self.id + ".json"), "w"))
        return self._map_text()

    def _map_text(self):
        kinds = sorted({k for row in self.kind for k in row if k})
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        legend = {k: chars[i] for i, k in enumerate(kinds)}
        lines = ["=== " + self.id]
        for k, v in self.hdr.items():
            if v != "" and v is not None:
                lines.append("%s: %s" % (k, str(v).lower() if isinstance(v, bool) else v))
        lines.append("legend: " + " ".join("%s=%s" % (legend[k], k) for k in kinds))
        lines.append("grid:")
        for row in self.kind:
            lines.append("".join(legend[k] if k else "_" for k in row))
        lines.append("entities:")
        lines.extend(self.ents)
        return "\n".join(lines) + "\n"


# Collision kinds (must be in compile_content SOLID); "block" is added there for generic art.
SOLID_KINDS = {"block", "wall", "water", "tree", "rock", "roof", "house", "void", "cliff", "rail", "crate", "barrel", "lamp",
               "shelf", "machine", "table", "pipe", "bed", "rubble", "crystal", "fence", "hedge", "counter", "pillar",
               "bell", "vent", "statue", "mountain", "deep", "reef", "window", "cart", "chimney", "anvil", "boat", "pool",
               "sluice", "altar", "brazier", "wheel", "well", "sign", "bench", "garden", "laundry", "tent", "gate"}


def write_group(group, maps_text):
    p = os.path.join(REPO, "content_src", "maps", "z48_%s.map" % group)
    with open(p, "w", encoding="utf-8") as f:
        f.write("#! Generated by tools/maps48 (%s). Overrides the older definitions of these maps.\n" % group)
        for t in maps_text:
            f.write(t)
    return p
# appended to tools/maps48/kit.py
# ---------------------------------------------------------------- generated sheets (tinted copies of pack sheets)
GEN_SHEETS = set()


def gen_sheet(alias, name, img):
    """Register an in-memory sheet under (alias, name); Map.save writes it into ext/cute like a pack sheet."""
    _img_cache[(alias, name)] = img.convert("RGBA")
    GEN_SHEETS.add((alias, name))
    return name


def tinted(alias, sheet, mul, add=(0, 0, 0), name=None):
    """A recoloured copy of a pack sheet (rgb * mul + add), for regional variants of the same stamps."""
    name = name or "gen_%s_%d_%d_%d" % (sheet.replace("/", "_"), int(mul[0] * 100), int(mul[1] * 100), int(mul[2] * 100))
    if (alias, name) not in _img_cache:
        a = np.array(sheet_img(alias, sheet)).astype(np.float32)
        a[..., :3] = np.clip(a[..., :3] * np.array(mul, np.float32) + np.array(add, np.float32), 0, 255)
        gen_sheet(alias, name, Image.fromarray(a.astype(np.uint8), "RGBA"))
    return name
