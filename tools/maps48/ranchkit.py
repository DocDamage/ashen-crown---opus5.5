"""Ranch map kit: composes the eight ranch maps entirely from the Super Retro Ranch pack (16 px, installed by
tools/art/install_ranch.py into game/assets/ext/ranch) and writes them in the Art48 format the field and the HD-2D
stage read (game/src/field/art48.gd): <MAP>_ground.png (the 16 px ground composed, then x3 nearest = 48 px per cell),
<MAP>.json (upright objects on x3 copies of the pack sheets in ext/ranch/x3, plus a "ranch" block the runtime reads:
animated water cells, the farmhouse doors, campfires, fireflies, the hands' beds, the kart rails). The same plan
writes the map's grid and entities (content_src/maps/ranch.map), so collision always matches the art.

Terrain tools (see docs/expansion/RANCH_PACK.md for the sheet layouts):
  blob      Godot 3x3 minimal sheets (12x4 tiles, ext/ranch/autotiles): one tile per 8-neighbour mask, decoded from
            template_godot_3x3.png (red = the terrain's corner/edge bits)
  block     the pack's own 3x5 terrain blocks on the 256x256 tiles sheets (ground, snow, cliff): 2x2 inner corners
            (rows 0-1), the fill (col 2 row 0), and a 3x3 patch (rows 2-4); composed per 8x8 quarter
Usage: python3 tools/maps48/maps/ranch.py [--map-only]"""
import json, os, random
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EXT = os.path.join(REPO, "game", "assets", "ext")
RANCH = os.path.join(EXT, "ranch")
PACK = os.path.join(RANCH, "pack")
AUTO = os.path.join(RANCH, "autotiles")
T = 16
U = 3

_cache = {}


def have_art():
    return os.path.isdir(PACK) and os.path.isdir(AUTO)


def img(rel):
    """A pack sheet (path under ext/ranch/pack, or 'auto:<name>' for an autotile sheet)."""
    if rel not in _cache:
        p = os.path.join(AUTO, rel[5:] + ".png") if rel.startswith("auto:") else os.path.join(PACK, rel)
        _cache[rel] = Image.open(p).convert("RGBA")
    return _cache[rel]


def tile(rel, c, r, w=1, h=1):
    return img(rel).crop((c * T, r * T, (c + w) * T, (r + h) * T))


# ---------------------------------------------------------------- Godot 3x3 minimal (47-tile blob)
_BLOB = None
N, NE, E, SE, S, SW, W, NW = 1, 2, 4, 8, 16, 32, 64, 128


def _norm(m):
    if not (m & N and m & E):
        m &= ~NE
    if not (m & S and m & E):
        m &= ~SE
    if not (m & S and m & W):
        m &= ~SW
    if not (m & N and m & W):
        m &= ~NW
    return m


def blob_table():
    global _BLOB
    if _BLOB is None:
        t = img("auto:template_godot_3x3")
        px = t.load()
        red = lambda x, y: px[x, y][0] > 200 and px[x, y][1] < 150
        _BLOB = {}
        for r in range(4):
            for c in range(12):
                ox, oy = c * T, r * T
                if not red(ox + 8, oy + 8):
                    continue
                m = 0
                for bit, (a, b) in ((N, (8, 3)), (NE, (13, 3)), (E, (13, 8)), (SE, (13, 13)), (S, (8, 13)), (SW, (3, 13)),
                                    (W, (3, 8)), (NW, (3, 3))):
                    if red(ox + a, oy + b):
                        m |= bit
                _BLOB.setdefault(_norm(m), (c, r))
    return _BLOB


def mask_at(cells, x, y, w, h, edge=True):
    def has(xx, yy):
        if xx < 0 or yy < 0 or xx >= w or yy >= h:
            return edge
        return (xx, yy) in cells
    m = 0
    for bit, (dx, dy) in ((N, (0, -1)), (NE, (1, -1)), (E, (1, 0)), (SE, (1, 1)), (S, (0, 1)), (SW, (-1, 1)), (W, (-1, 0)),
                          (NW, (-1, -1))):
        if has(x + dx, y + dy):
            m |= bit
    return _norm(m)


def blob_cell(mask):
    tb = blob_table()
    if mask in tb:
        return tb[mask]
    for drop in (NE | SE | SW | NW, 0xff):
        mm = _norm(mask & ~drop) if drop != 0xff else 0
        if mm in tb:
            return tb[mm]
    return tb.get(0, (0, 3))


# ---------------------------------------------------------------- pack 3x5 blocks (quarters)
def block_tile(rel, bx, by, n, e, s, w, ne, nw, se, sw):
    sh = img(rel)
    q = 8
    out = Image.new("RGBA", (T, T))

    def quarter(c, r, qx, qy):
        x0, y0 = c * T + qx * q, r * T + qy * q
        return sh.crop((x0, y0, x0 + q, y0 + q))
    # top-left
    if n and w:
        src = (bx + 1, by + 3) if nw else (bx + 0, by + 0)
    elif n:
        src = (bx + 0, by + 3)
    elif w:
        src = (bx + 1, by + 2)
    else:
        src = (bx + 0, by + 2)
    out.paste(quarter(src[0], src[1], 0, 0), (0, 0))
    # top-right
    if n and e:
        src = (bx + 1, by + 3) if ne else (bx + 1, by + 0)
    elif n:
        src = (bx + 2, by + 3)
    elif e:
        src = (bx + 1, by + 2)
    else:
        src = (bx + 2, by + 2)
    out.paste(quarter(src[0], src[1], 1, 0), (q, 0))
    # bottom-left
    if s and w:
        src = (bx + 1, by + 3) if sw else (bx + 0, by + 1)
    elif s:
        src = (bx + 0, by + 3)
    elif w:
        src = (bx + 1, by + 4)
    else:
        src = (bx + 0, by + 4)
    out.paste(quarter(src[0], src[1], 0, 1), (0, q))
    # bottom-right
    if s and e:
        src = (bx + 1, by + 3) if se else (bx + 1, by + 1)
    elif s:
        src = (bx + 2, by + 3)
    elif e:
        src = (bx + 1, by + 4)
    else:
        src = (bx + 2, by + 4)
    out.paste(quarter(src[0], src[1], 1, 1), (q, q))
    return out


# ---------------------------------------------------------------- stamps (upright objects)
class Stamp:
    """A sprite cut from a 16 px pack sheet: rect (x, y, w, h) in pack pixels. solid: list of (dx, dy) cells
    relative to the anchor cell; anchor (ax, ay): where the stamp's top-left sits relative to the cell it is placed
    on, in pack pixels. base: y-sort line in pack pixels from the stamp top (default: bottom of its opaque part)."""

    def __init__(self, rel, rect, anchor=(0, 0), solid=((0, 0),), base=None, kind="block", flat=False):
        self.rel, self.rect, self.anchor, self.solid, self.base, self.kind, self.flat = rel, rect, anchor, solid, base, kind, flat

    def image(self):
        x, y, w, h = self.rect
        return img(self.rel).crop((x, y, x + w, y + h))

    def auto_base(self):
        if self.base is not None:
            return self.base
        bb = self.image().getbbox()
        return bb[3] if bb else self.rect[3]


def margin(rel, rect, m=1):
    """Grow a stamp rect by m transparent pixels where the sheet allows (the HD-2D stage lays stamps whose corners
    are opaque flat on the ground; uprights need clear corners)."""
    x, y, w, h = rect
    sw, shh = img(rel).size
    x0, y0 = max(0, x - m), max(0, y - m)
    x1, y1 = min(sw, x + w + m), min(shh, y + h + m)
    return (x0, y0, x1 - x0, y1 - y0)


# ---------------------------------------------------------------- the map
class RanchMap:
    def __init__(self, mid, plan, hdr, legend_kinds):
        rows = [r for r in plan.strip("\n").split("\n")]
        self.id, self.rows = mid, rows
        self.h, self.w = len(rows), len(rows[0])
        for i, r in enumerate(rows):
            if len(r) != self.w:
                raise SystemExit("%s: plan row %d is %d wide, not %d" % (mid, i, len(r), self.w))
        self.hdr = hdr
        self.kind = [[legend_kinds.get(ch, "grass") for ch in r] for r in rows]
        self.layers = []         # (op, args)
        self.objects = []        # (stamp, x16, y16, base16)
        self.flat = []           # (image, x16, y16)
        self.ents = []
        self.extra = {"water": [], "doors": [], "fires": [], "fireflies": [], "beds": [], "rails": [], "lamps": []}
        self.rng = random.Random(mid)

    # cells
    def cells(self, chars):
        return {(x, y) for y, r in enumerate(self.rows) for x, ch in enumerate(r) if ch in chars}

    def all_cells(self):
        return {(x, y) for y in range(self.h) for x in range(self.w)}

    def at(self, x, y):
        return self.rows[y][x] if 0 <= x < self.w and 0 <= y < self.h else ""

    def solid(self, x, y, kind="block"):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.kind[y][x] = kind

    def walkable(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.kind[y][x] in WALK

    # ground ops
    def fill(self, rel, c, r):
        self.layers.append(("fill", (rel, c, r)))

    def fill_var(self, choices):
        """choices: [(rel, c, r, weight), ...] picked per cell."""
        self.layers.append(("fill_var", (choices,)))

    def blob(self, name, cells, frame=0, edge=True, keep_outside=True):
        self.layers.append(("blob", (name, set(cells), frame, edge, keep_outside)))

    def block(self, rel, bx, by, cells, edge=True, fill_out=False):
        """fill_out: also paint every other cell with the block's outside fill (col 2, row 1 of the block)."""
        self.layers.append(("block", (rel, bx, by, set(cells), edge, fill_out)))

    def slice9(self, rel, bx, by, cells, edge=True):
        """Whole-tile 9-slice of a block's 3x3 patch (rows by+2..by+4): cliffs, whose face is a full tile row."""
        self.layers.append(("slice9", (rel, bx, by, set(cells), edge)))

    def tiles(self, rel, c, r, cells):
        self.layers.append(("tiles", (rel, c, r, set(cells))))

    def decal(self, rel, rect, x16, y16):
        self.layers.append(("decal", (rel, rect, x16, y16)))

    # objects
    def place(self, st, x, y, dx=0, dy=0, solid=True, kind=None):
        px, py = x * T + st.anchor[0] + dx, y * T + st.anchor[1] + dy
        if st.flat:
            self.layers.append(("decal", (st.rel, st.rect, px, py)))
        else:
            self.objects.append((st, px, py, py + st.auto_base()))
        if solid:
            for (sx, sy) in st.solid:
                self.solid(x + sx, y + sy, kind or st.kind)

    def ent(self, line):
        self.ents.append(line)

    # ------------------------------------------------------------- output
    def compose(self):
        W, H = self.w * T, self.h * T
        g = Image.new("RGBA", (W, H), (12, 10, 18, 255))
        for op, a in self.layers:
            if op == "fill":
                t = tile(a[0], a[1], a[2])
                for y in range(self.h):
                    for x in range(self.w):
                        g.alpha_composite(t, (x * T, y * T))
            elif op == "fill_var":
                ch = a[0]
                tot = sum(c[3] for c in ch)
                rr = random.Random(self.id + "fill")
                for y in range(self.h):
                    for x in range(self.w):
                        v = rr.uniform(0, tot)
                        for (rel, c, r, wgt) in ch:
                            v -= wgt
                            if v <= 0:
                                break
                        g.alpha_composite(tile(rel, c, r), (x * T, y * T))
            elif op == "blob":
                name, cells, frame, edge, keep = a
                sh = img("auto:" + name)
                for (x, y) in cells:
                    c, r = blob_cell(mask_at(cells, x, y, self.w, self.h, edge))
                    t = sh.crop((frame * 192 + c * T, r * T, frame * 192 + (c + 1) * T, (r + 1) * T))
                    g.alpha_composite(t, (x * T, y * T))
            elif op == "block":
                rel, bx, by, cells, edge, fill_out = a
                if fill_out:
                    t_out = tile(rel, bx + 2, by + 1)
                    for y in range(self.h):
                        for x in range(self.w):
                            if (x, y) not in cells:
                                g.alpha_composite(t_out, (x * T, y * T))

                def has(xx, yy):
                    if xx < 0 or yy < 0 or xx >= self.w or yy >= self.h:
                        return edge
                    return (xx, yy) in cells
                for (x, y) in cells:
                    t = block_tile(rel, bx, by, has(x, y - 1), has(x + 1, y), has(x, y + 1), has(x - 1, y), has(x + 1, y - 1),
                                   has(x - 1, y - 1), has(x + 1, y + 1), has(x - 1, y + 1))
                    g.alpha_composite(t, (x * T, y * T))
            elif op == "slice9":
                rel, bx, by, cells, edge = a

                def has9(xx, yy):
                    if xx < 0 or yy < 0 or xx >= self.w or yy >= self.h:
                        return edge
                    return (xx, yy) in cells
                for (x, y) in cells:
                    cc = 0 if not has9(x - 1, y) else (2 if not has9(x + 1, y) else 1)
                    rr = 0 if not has9(x, y - 1) else (2 if not has9(x, y + 1) else 1)
                    g.alpha_composite(tile(rel, bx + cc, by + 2 + rr), (x * T, y * T))
            elif op == "tiles":
                rel, c, r, cells = a
                t = tile(rel, c, r)
                for (x, y) in cells:
                    g.alpha_composite(t, (x * T, y * T))
            elif op == "decal":
                rel, rect, px, py = a
                im = img(rel).crop((rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]))
                g.alpha_composite(im, (int(px), int(py)))
        return g

    def save(self):
        os.makedirs(os.path.join(EXT, "maps48"), exist_ok=True)
        os.makedirs(os.path.join(RANCH, "x3"), exist_ok=True)
        g = self.compose()
        g.convert("RGB").resize((g.width * U, g.height * U), Image.NEAREST).save(
            os.path.join(EXT, "maps48", self.id + "_ground.png"), optimize=True)
        sheets, sidx = [], {}

        def sheet_id(rel):
            if rel not in sidx:
                name = rel.replace("/", "_").replace(":", "_").replace(".png", "") + ".png"   # no ':' (Windows)
                dst = os.path.join(RANCH, "x3", name)
                im = img(rel)
                im.resize((im.width * U, im.height * U), Image.NEAREST).save(dst)
                sidx[rel] = len(sheets)
                sheets.append("ranch/x3/" + name)
            return sidx[rel]
        objs = []
        for (st, x, y, base) in sorted(self.objects, key=lambda o: o[3]):
            sx, sy, sw, shh = st.rect
            objs.append([sheet_id(st.rel), sx * U, sy * U, sw * U, shh * U, x * U, y * U, base * U])
        anims = [["ranch_campfire", f[0] * U, f[1] * U, (f[1] + 30) * U] for f in self.extra["fires"]]
        data = {"id": self.id, "w": self.w, "h": self.h, "ground": self.id + "_ground.png", "over": "", "sheets": sheets,
                "objects": objs, "anims": anims, "ranch": self.extra}
        json.dump(data, open(os.path.join(EXT, "maps48", self.id + ".json"), "w"))

    def map_text(self):
        kinds = sorted({k for row in self.kind for k in row})
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        legend = {k: chars[i] for i, k in enumerate(kinds)}
        lines = ["=== " + self.id]
        for k, v in self.hdr.items():
            if v != "" and v is not None:
                lines.append("%s: %s" % (k, v))
        lines.append("legend: " + " ".join("%s=%s" % (legend[k], k) for k in kinds))
        lines.append("grid:")
        for row in self.kind:
            lines.append("".join(legend[k] for k in row))
        lines.append("entities:")
        lines.extend(self.ents)
        return "\n".join(lines) + "\n"


WALK = {"grass", "path", "plot", "snow", "sand", "floor", "dirt", "ash", "bridge"}


CROPS_PREVIEW = {}


def preview(m, path, scale=2):
    """A flat 16 px look at a ranch map (ground, stamps by their base, the hands' crops, gates shut, solid cells
    tinted when RANCH_PREVIEW_SOLID is set) for reviewing layouts without the game."""
    g = m.compose()
    objs = [(base, st.image(), x, y) for (st, x, y, base) in m.objects]
    for (x, y, crop, fr) in m.extra.get("beds", []):
        v = CROPS_PREVIEW.get(crop)
        if v:
            st = img("crops/%s/%s" % (crop, v[0]))
            fw, fh = v[1], v[2]
            objs.append(((y + 1) * T, st.crop((fr * fw, 0, fr * fw + fw, fh)), x * T + (T - fw) // 2, (y + 1) * T - fh - 2))
    for (x, y, c, r) in m.extra.get("gates", []):
        sh = img("auto:" + os.path.basename(m.extra["fence_sheet"])[:-4])
        objs.append(((y + 1) * T, sh.crop((c * T, r * T, c * T + T, r * T + T)), x * T, y * T))
    for (base, im, x, y) in sorted(objs, key=lambda o: o[0]):
        g.alpha_composite(im, (int(x), int(y)))
    if os.environ.get("RANCH_PREVIEW_SOLID"):
        ov = Image.new("RGBA", g.size, (0, 0, 0, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(ov)
        for y in range(m.h):
            for x in range(m.w):
                if m.kind[y][x] not in WALK:
                    d.rectangle([x * T, y * T, x * T + T - 1, y * T + T - 1], fill=(255, 0, 0, 70))
        g.alpha_composite(ov)
    g.resize((g.width * scale, g.height * scale), Image.NEAREST).save(path)
