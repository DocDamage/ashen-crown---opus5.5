"""The eight ranches (tools/content/ranch.py RANCHES), hand-made from the Super Retro Ranch pack (16 px tiles).

Each ranch function lays out its farm on a cell plan (one char per cell), then dresses it with pack stamps; the
kit (tools/maps48/ranchkit.py) composes the ground, writes the Art48 files and the map text. Plan chars:
  .  open ground (the ranch's base: grass, soot soil, sand, dry dirt, snow)    ,  yard / path dirt
  p  a player plot (dirt bed; Confirm on it to hoe / plant / water / harvest)   h  a hand's bed (tilled, worked)
  ~  water (pond, stream, sea)          ^  raised cliff ledge             s  snow (on non-snow maps)
  g  grass patch (on non-grass maps)    X  thicket (solid; trees and bushes are stamped on it)
  f  fence    G  the pen gate (a block entity, shut by default)    =  kart rails
Seasons by kingdom: Crown March spring grass, Cinder Reach soot soil, Glass Coast grass and sand by the sea,
Skyspine snowy edges and cliffs, Pale Basin dry ground, Vermilion Reach autumn leaves, Mirewold dark wet grass and
pools, Hoarfrost March snow with snow cliffs and ice.
Usage: python3 tools/maps48/maps/ranch.py [--map-only]   (--map-only: write content_src/maps/ranch.map without art)
"""
import os, sys, random, importlib.util
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ranchkit as K
from ranchkit import RanchMap, Stamp, T

REPO = K.REPO
_spec = importlib.util.spec_from_file_location("ranch_content", os.path.join(REPO, "tools", "content", "ranch.py"))
RC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RC)

KINDS = {"a": "ash", "l": "grass", ".": "grass", ",": "path", "p": "plot", "h": "garden", "~": "water", "^": "cliff", "s": "snow", "g": "grass",
         "X": "tree", "f": "fence", "G": "path", "=": "rail", "d": "path"}

# ---------------------------------------------------------------- sheets (paths under ext/ranch/pack)
G1, G2, G3 = "tiles/ground_01_16x16.png", "tiles/ground_02_16x16.png", "tiles/ground_03_16x16.png"
SNOW = "tiles/snow_01_16x16.png"
TREE1, TREE2 = "tiles/tree_01_16x16.png", "tiles/tree_02_16x16.png"
CLIFF = {"rock": "tiles/cliff_01_16x16.png", "brown": "tiles/cliff_02_16x16.png", "red": "tiles/cliff_03_16x16.png",
         "snow": "tiles/cliff_snow_01_16x16.png"}
OBJ1, OBJ2 = "objects/objects_01_16x16.png", "objects/objects_02_16x16.png"
HOUSE = "buildings/building_01_16x16.png"
RAILS = "objects/kart/rails_16x16.png"

# tree_02: (x, y) offsets of each season's pair (small 2x2 at +0,+16; big 3x3 at +32,+0)
TREE_SEASON = {"spring": (0, 0), "summer": (0, 48), "blossom": (0, 96), "autumn": (128, 0), "fall": (128, 48), "snow": (128, 96)}


def big_tree(season):
    ox, oy = TREE_SEASON[season]
    return Stamp(TREE2, (ox + 32, oy, 48, 48), anchor=(-16, -32), solid=((0, 0),), kind="tree")


def small_tree(season):
    ox, oy = TREE_SEASON[season]
    return Stamp(TREE2, (ox, oy + 16, 32, 32), anchor=(-8, -16), solid=((0, 0),), kind="tree")


def bush(shade, size=0):
    """ground_03 round bushes: shade 0 (pale) .. 6 (darkest); size 0 big, 1 smaller, 2 tuft."""
    y = shade * 32
    r = [(128, y, 32, 32), (160, y, 32, 32), (192, y, 16, 16)][size]
    return Stamp(G3, r, anchor=(-8, -16) if size < 2 else (0, 0), solid=((0, 0),) if size < 2 else (), kind="hedge")


FLOWERS = [Stamp(G2, (128 + 16 * i, 0, 16, 16), solid=()) for i in range(3)]
MUSHROOMS = [Stamp(G2, (128 + 16 * i, 16, 16, 16), solid=()) for i in range(4)]
STUMP = Stamp(G2, (176, 0, 16, 16), kind="rock")
PEBBLES = [Stamp(G2, (128 + 16 * (i % 4), 32 + 16 * (i // 4), 16, 16), solid=(), flat=True) for i in range(16)]
POTS = [Stamp(OBJ1, (16 * i, 16, 16, 16), kind="barrel") for i in range(5)]
CRATES = [Stamp(OBJ1, (16 * i, 32, 16, 16), kind="crate") for i in range(6)]
SACK = Stamp(OBJ1, (0, 48, 16, 16), kind="crate")
TABLE = Stamp(OBJ1, (32, 56, 32, 24), anchor=(0, -8), solid=((0, 0), (1, 0)), kind="table")
MAILBOX = [Stamp(OBJ1, (16 * i, 88, 16, 24), anchor=(0, -8), kind="sign") for i in range(3)]
LAMP_RED = Stamp(OBJ1, (48, 80, 16, 32), anchor=(0, -16), kind="lamp")
LAMP_BLUE = Stamp(OBJ1, (64, 80, 16, 32), anchor=(0, -16), kind="lamp")
BARRELS = {"orange": Stamp(OBJ2, (144, 8, 16, 24), anchor=(0, -8), kind="barrel"),
           "empty": Stamp(OBJ2, (160, 8, 16, 24), anchor=(0, -8), kind="barrel"),
           "low": Stamp(OBJ2, (176, 8, 16, 24), anchor=(0, -8), kind="barrel"),
           "water": Stamp(OBJ2, (192, 8, 16, 24), anchor=(0, -8), kind="barrel")}
BUCKETS = [Stamp(OBJ2, (128, 32, 16, 16), kind="barrel"), Stamp(OBJ2, (144, 32, 16, 16), kind="barrel")]
# stone rings (troughs / well heads), 2x2, by water level; roofed wells 2x3
TROUGH = [Stamp(OBJ2, (128 + 32 * i, 48, 32, 32), solid=((0, 0), (1, 0), (0, 1), (1, 1)), kind="well") for i in range(4)]
WELL = [Stamp(OBJ2, (128 + 32 * i, 80, 32, 48), anchor=(0, -16), solid=((0, 1), (1, 1), (0, 2), (1, 2)), kind="well") for i in range(4)]
PIPE_H = Stamp(OBJ2, (144, 160, 16, 16), solid=(), flat=True)
PIPE_V = Stamp(OBJ2, (160, 160, 16, 16), solid=(), flat=True)
PIPE_CAP = Stamp(OBJ2, (160, 176, 16, 8), solid=(), flat=True)
VALVE = Stamp(OBJ2, (224, 128, 16, 16), solid=(), flat=True)
GAUGE = Stamp(OBJ2, (192, 128, 16, 16), solid=(), flat=True)
ICE = [Stamp("objects/ice_blocs/ice_bloc_0%d_16x32.png" % i, (0, 0, 16, 32), anchor=(0, -16), kind="rock") for i in (1, 2, 3)] + \
      [Stamp("objects/ice_blocs/ice_bloc_0%d_16x16.png" % i, (0, 0, 16, 16), kind="rock") for i in (4, 5)]
CAMPFIRE_LOGS = Stamp("objects/campfires/campfire_04_16x32.png", (0, 0, 16, 32), anchor=(0, -16), kind="brazier")
RAIL_H = (RAILS, (41, 0, 16, 16))
RAIL_END_L = (RAILS, (39, 0, 16, 16))
RAIL_END_R = (RAILS, (59, 0, 16, 16))
TURNTABLE = Stamp(RAILS, (0, 0, 32, 32), solid=(), flat=True)


def sign_stamp(crop):
    c, r = RC.CROPS[crop][13]
    return Stamp(OBJ1, (c * 16, r * 16, 16, 16), kind="sign")


SIGN_BLANK = Stamp(OBJ1, (0, 112, 16, 16), kind="sign")
SIGN_BOARD = Stamp(OBJ1, (0, 128, 16, 16), kind="sign")


def house_stamp(rel=HOUSE):
    return Stamp(rel, (0, 15, 65, 50), anchor=(0, -1), solid=[(x, y) for y in range(3) for x in range(4)], kind="house")


_TINTS = {}


def tinted_house(name, roof, wall=None):
    """building_01 with its roof planks (and optionally its wall boards) recoloured: barns, longhouses."""
    key = "gen:" + name
    if key not in K._cache:
        im = K.img(HOUSE).copy()
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if not a:
                    continue
                if y < 48 and r > 150 and g > 90 and b < 140 and r > g:      # the orange roof planks
                    k = (r + g + b) / (238 + 161 + 96)
                    px[x, y] = tuple(min(255, int(c * k)) for c in roof) + (a,)
                elif wall and y >= 48 and abs(r - g) < 30 and abs(g - b) < 30 and r > 120:   # the pale wall boards
                    k = (r + g + b) / 600.0
                    px[x, y] = tuple(min(255, int(c * k)) for c in wall) + (a,)
        K._cache[key] = im
    return house_stamp(key)


# ---------------------------------------------------------------- plan helper
class Plan:
    def __init__(self, w, h, base="."):
        self.w, self.h = w, h
        self.g = [[base] * w for _ in range(h)]

    def rect(self, ch, x0, y0, x1, y1):
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.g[y][x] = ch

    def put(self, ch, pts):
        for (x, y) in pts:
            if 0 <= x < self.w and 0 <= y < self.h:
                self.g[y][x] = ch

    def hline(self, ch, y, x0, x1):
        self.rect(ch, x0, y, x1, y)

    def vline(self, ch, x, y0, y1):
        self.rect(ch, x, y0, x, y1)

    def frame(self, ch, x0, y0, x1, y1):
        self.hline(ch, y0, x0, x1)
        self.hline(ch, y1, x0, x1)
        self.vline(ch, x0, y0, y1)
        self.vline(ch, x1, y0, y1)

    def blob(self, ch, cx, cy, rx, ry, rng, rough=0.25):
        cells = set()
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                d = ((x - cx) / max(rx, 0.5)) ** 2 + ((y - cy) / max(ry, 0.5)) ** 2
                if d <= 1.0 + rng.uniform(-rough, rough) and 0 <= x < self.w and 0 <= y < self.h:
                    cells.add((x, y))
        # no one-cell spurs: keep cells with at least two orthogonal neighbours
        for _ in range(2):
            cells = {(x, y) for (x, y) in cells
                     if sum((x + dx, y + dy) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 2}
        for (x, y) in cells:
            self.g[y][x] = ch

    def text(self):
        return "\n".join("".join(r) for r in self.g)


# ---------------------------------------------------------------- shared dressing
class Ranch:
    """One ranch under construction: the plan, then the RanchMap with ground layers, stamps and entities."""

    def __init__(self, rid, w, h, base="."):
        self.rid = rid
        self.r = RC.RANCHES[rid]
        self.p = Plan(w, h, base)
        self.m = None
        self.npc_n = 0

    def build(self, hdr):
        self.m = RanchMap(self.r["map"], self.p.text(), hdr, KINDS)
        return self.m

    # --- ground recipes
    def ground(self, season):
        """Base ground and dirt for the kingdom's look (see the module doc). Plan chars: ',' 'p' 'h' 'G' 'd' dirt,
        'g' grass patches, 's' snow banks, 'l' leaf litter."""
        m = self.m
        dirt = m.cells(",pdhG")
        beds = m.cells("ph")
        if season in ("spring", "autumn"):
            m.fill(G1, 2, 2)                                   # light grass
            m.block(G1, 0, 6, m.cells("X"), edge=True)         # dark grass under the woods
            m.blob("grass_on_dirt_02", dirt)                   # orange dirt with a grass lip
        elif season == "soot":
            m.fill(G1, 5, 1)                                   # brown soil
            m.block(G1, 8, 10, m.cells("Xa"), edge=True)       # black cinder soil under the slag woods and ash heaps
            m.block(G1, 8, 5, m.cells(",dG"), edge=False)      # orange cinder tracks (the beds stay brown soil)
        elif season == "coast":
            m.fill(G1, 2, 2)
            m.blob("grass_on_dirt_01", m.cells(",dG"))         # pale sand
            m.blob("grass_on_dirt_02", beds)                   # orange beds
        elif season == "dry":
            m.fill(G1, 2, 1)                                   # dry orange ground
            # grass patches: the grass-ring-round-a-hole block with every other cell a hole (grass fill on the g cells)
            m.block(G1, 8, 0, m.all_cells() - m.cells("g"), edge=True, fill_out=True)
            m.block(G1, 11, 5, m.cells(",dG"), edge=False)     # brown trodden tracks
        elif season == "marsh":
            m.fill(G1, 5, 2)                                   # dark wet grass
            m.block(G1, 3, 6, m.cells("g"), edge=False)        # paler tussocks (round the pools)
            m.block(G1, 3, 1, m.cells(",dG") | beds, edge=False)   # brown mud tracks
            m.block(G1, 8, 5, beds, edge=False)                # orange beds in the mud
        elif season == "snow":
            m.fill(SNOW, 2, 2)                                 # snow
            m.block(SNOW, 0, 1, dirt, edge=False)              # dirt yards and beds in the snow
            m.blob("snow_on_grass_01", m.cells("g"), edge=False)   # grass where the snow has gone
        elif season == "alpine":
            m.fill(G1, 2, 2)
            m.blob("grass_on_snow_01", m.cells("sX^"), edge=True)  # snow banks along the edges and ledges
            m.blob("grass_on_dirt_02", dirt)

    def furrows(self, row=11):
        """Raked bed strips (ground_01 rows 11-12 on orange dirt, rows 13-14 on brown soil: left end, middle, right
        end) on plots whose ground is the beds' own colour (the dry basin, the soot paddock), so they read before
        they are hoed."""
        m = self.m
        cells = m.cells("p")
        for (x, y) in cells:
            c = 1
            if (x - 1, y) not in cells:
                c = 0
            elif (x + 1, y) not in cells:
                c = 2
            m.tiles(G1, c, row, {(x, y)})

    def leaves(self, tint=(214, 96, 40)):
        """Autumn leaf litter: the pack's leaf autotile (05_leaf) recoloured to the maple red of the Vermilion Reach."""
        key = "auto:leaf_autumn"
        if key not in K._cache:
            im = K.img("auto:leaf_01").copy()
            px = im.load()
            for y in range(im.height):
                for x in range(im.width):
                    r, g, b, a = px[x, y]
                    if a:
                        k = (r + g + b) / 300.0
                        px[x, y] = tuple(min(255, int(c * k)) for c in tint) + (a,)
            K._cache[key] = im
        self.m.blob("leaf_autumn", self.m.cells("l"), edge=False)

    def water(self, sheet="water_on_grass_01", chars="~", edge=True):
        m = self.m
        cells = m.cells(chars)
        m.blob(sheet, cells, edge=edge)
        tb = K.blob_table
        for (x, y) in sorted(cells):
            c, r = K.blob_cell(K.mask_at(cells, x, y, m.w, m.h, edge))
            m.extra["water"].append([x, y, c, r])
        m.extra["water_sheet"] = "ranch/autotiles/%s.png" % sheet

    def cliffs(self, style="rock", chars="^", trees=None):
        """Raised ledges: the cliff sheet's plateau patch as whole tiles (top rim, sides, a full rock face on the
        bottom row). trees: seasons for trees standing on the ledge top (never on the face row)."""
        m = self.m
        cells = m.cells(chars)
        m.slice9(CLIFF[style], 0, 1, cells, edge=True)
        if trees:
            tops = sorted((x, y) for (x, y) in cells if (x, y + 1) in cells and (x, y + 2) in cells)
            for (x, y) in tops:
                if m.rng.random() < 0.3 and (x + y) % 2 == 0:
                    m.place(small_tree(m.rng.choice(trees)) if m.rng.random() < 0.6 else bush(3, 1), x, y, solid=False)

    def beds(self, tilled_sheet="field_02"):
        """The hands' beds are tilled for good (baked); the player's plots are tilled at runtime (ranch.gd) with the
        same sheet (field_02: tilled soil on orange dirt; field_04: dark furrows on brown soil) and its wet copy."""
        m = self.m
        m.blob(tilled_sheet, m.cells("h"), edge=False)
        wet = {"field_02": "field_wet", "field_04": "field_04_wet"}.get(tilled_sheet, "field_wet")
        m.extra["tilled"] = ["ranch/autotiles/%s.png" % tilled_sheet, "ranch/autotiles/%s.png" % wet]

    def fences(self, sheet="fence_02"):
        m = self.m
        cells = m.cells("fG")
        gates = m.cells("G")
        for (x, y) in sorted(cells):
            if (x, y) in gates:
                continue
            c, r = K.blob_cell(K.mask_at(cells, x, y, m.w, m.h, edge=False))
            m.place(Stamp("auto:" + sheet, (c * T, r * T, T, T), kind="fence"), x, y)
        for (x, y) in gates:
            c, r = K.blob_cell(K.mask_at(cells, x, y, m.w, m.h, edge=False))
            m.extra.setdefault("gates", []).append([x, y, c, r])
        m.extra["fence_sheet"] = "ranch/autotiles/%s.png" % sheet

    def rails(self, y, x0, x1):
        m = self.m
        to_east = x1 >= m.w - 1
        for x in range(x0, x1 + 1):
            src = RAIL_H
            if to_east and x == x0:
                src = RAIL_END_L
            elif not to_east and x == x1:
                src = RAIL_END_R
            m.decal(src[0], src[1], x * T, y * T)
            m.solid(x, y, "rail")
        m.extra["rails"] = [y, x0, x1, 1 if to_east else -1]

    def thicket(self, seasons, shade=2, density=0.5, big=True, rows=None):
        """Trees and bushes on the X cells (solid woods). seasons: tree_02 season names picked at random."""
        m = self.m
        rng = m.rng
        if isinstance(seasons, str):
            seasons = [seasons]
        xs = [c for c in sorted(m.cells("X"), key=lambda c: (c[1], c[0])) if rows is None or c[1] in rows]
        xset = set(m.cells("X"))
        used = self._tused = getattr(self, "_tused", set())
        for (x, y) in xs:
            if (x, y) in used:
                continue
            free3 = all((x + dx, y) in xset and (x + dx, y) not in used for dx in (-1, 0, 1))
            v = rng.random()
            sea = rng.choice(seasons)
            if big and free3 and v < density:
                m.place(big_tree(sea), x, y)
                used.update({(x - 1, y), (x, y), (x + 1, y)})
            elif v < density + 0.3:
                m.place(small_tree(sea), x, y)
                used.add((x, y))
            else:
                m.place(bush(shade, rng.randint(0, 1)), x, y)
                used.add((x, y))

    def scatter(self, stamps, n, chars=".", gap=1, avoid=()):
        m = self.m
        rng = m.rng
        ok = [c for c in sorted(m.cells(chars)) if m.walkable(*c) and c not in avoid]
        placed = 0
        taken = set(avoid)
        for _ in range(n * 30):
            if placed >= n or not ok:
                break
            x, y = rng.choice(ok)
            if any((x + dx, y + dy) in taken for dx in range(-gap, gap + 1) for dy in range(-gap, gap + 1)):
                continue
            st = rng.choice(stamps)
            m.place(st, x, y, solid=bool(st.solid))
            taken.add((x, y))
            placed += 1

    def house(self, x, y, stamp=None, door_text=""):
        m = self.m
        # no fence posts under a building that stands on a pen's fence line
        m.objects = [o for o in m.objects if not (o[0].kind == "fence" and x * T <= o[1] < (x + 4) * T and y * T <= o[2] < (y + 3) * T)]
        m.place(stamp or house_stamp(), x, y)
        m.extra["doors"].append([x + 1, y + 2])
        if door_text:
            m.ent('read %d %d "%s"' % (x + 1, y + 2, door_text))

    def campfire(self, x, y):
        m = self.m
        m.extra["fires"].append([x * T, y * T - 16])
        m.solid(x, y, "brazier")

    def pipes_h(self, y, x0, x1):
        for x in range(x0, x1 + 1):
            self.m.place(PIPE_H, x, y, solid=False)

    def pipes_v(self, x, y0, y1):
        for y in range(y0, y1 + 1):
            self.m.place(PIPE_V, x, y, solid=False)

    # --- entities
    def folk(self, nid, x, y, d, look, task, talk, name="", cond="", wander=False):
        s = "npc %s %d %d %s sprite=ranch:folk:%s:%s talk=%s" % (nid, x, y, d, look, task, talk)
        if wander:
            s += " wander=1"
        if name:
            s += ' name="%s"' % name
        if cond:
            s += " if=" + cond
        self.m.ent(s)

    def beast(self, nid, x, y, d, sprite, talk, cond="", wander=True, name=""):
        s = "npc %s %d %d %s sprite=ranch:%s talk=%s" % (nid, x, y, d, sprite, talk)
        if wander:
            s += " wander=1"
        if name:
            s += ' name="%s"' % name
        if cond:
            s += " if=" + cond
        self.m.ent(s)

    def livestock(self, spots, nest, kart, gate, gate_msg):
        """spots: kind -> (x, y) home cells for the player's animals (bird: three cells)."""
        rid = self.rid
        for k in ("cow", "pig", "bunny", "cat"):
            x, y = spots[k]
            self.beast("own_%s_%s" % (rid, k), x, y, "down", "%s:%s" % (k, rid), "RANCH_ANIMAL", "ranch:%s:own:%s" % (rid, k),
                       name="Your " + RC.ANIMALS[k][0])
        for i, (x, y) in enumerate(spots["bird"]):
            self.beast("own_%s_bird%d" % (rid, i + 1), x, y, "left", "bird:" + rid, "RANCH_ANIMAL", "ranch:%s:birds:%d" % (rid, i + 1),
                       name="Your Dove")
        self.beast("nest_" + rid, nest[0], nest[1], "down", "nest:" + rid, "RANCH_NEST", wander=False, name="Nest")
        self.beast("kart_" + rid, kart[0], kart[1], "right", "kart:" + rid, "RANCH_KART", wander=False, name="Rail Kart")
        self.m.ent('block %d %d tile=gate if=!ranch:%s:gate msg="%s"' % (gate[0], gate[1], rid, gate_msg))

    def signs(self, spots):
        """Crop signposts by the beds: [(x, y, crop)], one per seed this ranch sells."""
        for (x, y, crop) in spots:
            self.m.place(sign_stamp(crop), x, y)
            self.m.ent('sign %d %d "%s. The seed box at the house sells it."' % (x, y, RC.CROPS[crop][2]))

    def hand_beds(self, crops):
        """Fills the h cells with the hands' crops: [(x, y, crop, frame)] or a crop list cycled over the cells."""
        m = self.m
        cells = sorted(m.cells("h"), key=lambda c: (c[1], c[0]))
        for i, (x, y) in enumerate(cells):
            crop = crops[(x // 2 + y) % len(crops)]
            st = RC.CROPS[crop][6]
            fr = st[min(len(st) - 1, 1 + (x * 7 + y * 3) % (len(st) - 1))]
            m.extra["beds"].append([x, y, crop, fr])

    def fireflies(self, pts):
        self.m.extra["fireflies"] = [[x, y] for (x, y) in pts]


def header(r, tileset, music):
    rid = [k for k, v in RC.RANCHES.items() if v is r][0]
    zone = r["map"].split("_")[0]
    return {"name": r["name"], "tileset": tileset, "music": music, "zone": zone, "region": r["region"],
            "location": "L_" + zone, "encounters": "none", "save": "false"}


# ================================================================ the ranches
def border(p, w, h, top=2, bottom=2, side=1):
    p.rect("X", 0, 0, w - 1, top - 1)
    p.rect("X", 0, h - bottom, w - 1, h - 1)
    p.rect("X", 0, 0, side - 1, h - 1)
    p.rect("X", w - side, 0, w - 1, h - 1)


def finish_common(R, season_trees, shade, south_rows):
    """Woods: big trees on the north and side bands, low trees and bushes on the south band (keeps the rails and
    beds in view), tufts on the open row above the south woods."""
    R.thicket(season_trees, shade=shade, big=False, rows=south_rows)
    R.thicket(season_trees, shade=shade)
    m = R.m
    y = min(south_rows) - 1
    for x in range(1, m.w - 1):
        if m.at(x, y) == "." and m.rng.random() < 0.45:
            m.place(bush(shade, 2), x, y, solid=False)


# ---------------------------------------------------------------- R01 Fallowmere (Crown March, spring)
def r01():
    R = Ranch("R01", 36, 26)
    p = R.p
    border(p, 36, 26, top=2, bottom=2)
    p.rect("X", 1, 2, 1, 4)
    p.rect("X", 33, 11, 34, 13)
    p.rect(".", 0, 13, 0, 14)                       # west entry from Brackenford
    p.rect(",", 0, 13, 20, 14)                      # the lane in
    p.rect(",", 3, 6, 9, 7)                         # farmhouse yard
    p.vline(",", 6, 7, 12)
    p.rect(",", 17, 6, 19, 12)
    p.rect(",", 19, 11, 28, 12)
    p.frame("f", 21, 3, 33, 10)                     # the pen; the barn sits on its north fence
    p.put("G", [(27, 10)])
    p.rect(",", 23, 4, 26, 5)
    p.rect(",", 2, 15, 17, 15)                      # bed paths
    p.rect("p", 3, 16, 8, 17)                       # player beds
    p.rect("p", 11, 16, 16, 17)
    p.rect(",", 2, 18, 17, 18)
    p.rect("h", 3, 19, 8, 20)                       # Ressa's and Mott's beds
    p.rect("h", 11, 19, 14, 20)
    p.rect(",", 2, 21, 17, 21)
    p.rect("~", 24, 16, 30, 18)                     # the pond
    p.rect("~", 25, 15, 28, 15)
    p.rect("~", 26, 19, 31, 19)
    p.rect("~", 31, 17, 31, 18)
    p.rect(",", 18, 21, 35, 21)
    p.rect("=", 19, 22, 35, 22)
    m = R.build(header(R.r, "town_r01", "M010"))
    R.ground("spring")
    R.water()
    R.beds()
    R.fences("fence_02")
    R.rails(22, 19, 35)
    m.solid(20, 22, "path")                          # the kart's cell
    finish_common(R, ["spring", "summer"], 1, south_rows=(24, 25))
    R.house(3, 3, door_text="The farmhouse door. Agna keeps it shut; the boys' boots are still by it.")
    R.house(23, 1, tinted_house("barn_r01", (176, 70, 52)), door_text="The barn. Hay to the rafters and a tally of debts chalked on the door.")
    m.place(WELL[3], 9, 10)
    R.pipes_v(10, 13, 14)
    R.pipes_h(15, 4, 15)
    m.place(VALVE, 10, 15, solid=False)
    m.place(TROUGH[2], 29, 4)
    m.place(BARRELS["water"], 8, 4)
    m.place(CRATES[3], 2, 6)
    m.place(SACK, 2, 7)
    m.place(MAILBOX[1], 8, 12)
    m.place(TABLE, 12, 7)
    m.place(BUCKETS[1], 20, 8)
    m.place(CRATES[0], 32, 13)
    R.campfire(14, 10)
    R.signs([(2, 16, "wheat"), (2, 17, "carrot"), (17, 16, "potato"), (17, 17, "lettuce")])
    R.hand_beds(["wheat", "carrot", "lettuce"])
    R.scatter(FLOWERS + [bush(0, 2)], 26, ".", gap=1)
    R.scatter(MUSHROOMS[:2] + [STUMP], 3, ".", gap=2)
    R.scatter(PEBBLES[:4], 6, ",", gap=2)
    R.fireflies([(27, 14), (31, 19), (23, 19), (5, 22), (12, 9), (33, 7)])
    for e in ("spawn from_town 1 13 right", "spawn default 1 13 right",
              "exit 0 13..14 T01_PLATFORM from_ranch if=!phase:post", "exit 0 13..14 T01_POST from_ranch if=phase:post"):
        m.ent(e)
    R.folk("rancher_r01", 5, 7, "down", "fh", "idle", "RANCH_R01_AGNA", "Agna Fallow")
    R.folk("hand_r01_ressa", 9, 19, "left", "f", "water", "RANCH_R01_RESSA", "Ressa")
    R.folk("hand_r01_mott", 15, 19, "left", "mh", "hoe", "RANCH_R01_MOTT", "Old Mott", "!phase:post")
    R.folk("hand_r01_drift", 15, 19, "left", "m", "shovel", "RANCH_R01_DRIFTER", "Flood Drifter", "phase:post")
    R.folk("hand_r01_tobin", 18, 8, "down", "m", "walk", "RANCH_R01_TOBIN", "Tobin", wander=True)
    R.beast("cow_r01a", 24, 7, "right", "cow:R01", "RANCH_COW")
    R.beast("pig_r01a", 31, 8, "left", "pig:R01:adult", "RANCH_PIG")
    R.beast("bird_r01a", 13, 12, "right", "bird:R01", "RANCH_DOVE")
    R.livestock({"cow": (28, 7), "pig": (25, 8), "bunny": (31, 6), "cat": (7, 6), "bird": [(23, 6), (26, 6), (32, 8)]},
                nest=(32, 4), kart=(20, 22), gate=(27, 10), gate_msg=GATE_MSG)
    m.ent('sign 6 12 "Fallowmere Ranch. Milk, eggs and seed. Close the gates. The quarry dogs come down at night."')
    return R


GATE_MSG = "The pen gate, shut. Confirm opens it; shut it again behind you."


# ---------------------------------------------------------------- R02 Soot Paddock (Cinder Reach, soot and slag)
def r02():
    R = Ranch("R02", 36, 26)
    p = R.p
    border(p, 36, 26, top=2, bottom=2)
    p.rect("^", 1, 2, 9, 3)                         # a slag ledge behind the house
    p.rect("X", 0, 0, 0, 25)
    p.rect("X", 35, 0, 35, 25)
    p.rect(".", 0, 13, 0, 14)
    p.rect(",", 0, 13, 21, 14)                      # the cinder track in
    p.rect(",", 3, 7, 9, 8)
    p.vline(",", 6, 8, 12)
    p.rect(",", 15, 6, 17, 12)
    p.frame("f", 20, 4, 33, 11)                     # the sty pen
    p.put("G", [(21, 11)])
    p.rect(",", 21, 12, 21, 12)
    p.rect("a", 26, 13, 31, 15)                     # ash heap
    p.rect(",", 2, 16, 18, 16)
    p.rect("p", 3, 17, 8, 18)
    p.rect("p", 11, 17, 16, 18)
    p.rect(",", 2, 19, 18, 19)
    p.rect("h", 3, 20, 7, 21)
    p.rect("h", 11, 20, 15, 21)
    p.rect(",", 2, 22, 18, 22)
    p.rect(",", 23, 17, 30, 20)                     # yard round the slag pool
    p.rect("~", 25, 18, 28, 19)
    p.rect("=", 19, 22, 35, 22)
    p.rect(",", 19, 21, 35, 21)
    m = R.build(header(R.r, "town_r02", "M012"))
    R.ground("soot")
    R.cliffs("rock", trees=["summer"])
    R.furrows(13)
    R.water("water_on_dirt_01")
    R.beds("field_04")
    R.fences("fence_01")
    R.rails(22, 19, 35)
    m.solid(20, 22, "path")
    finish_common(R, ["summer"], 5, south_rows=(24, 25))
    R.house(3, 4, door_text="Brann's house. The windows are black with soot on the inside, too.")
    R.house(25, 2, tinted_house("barn_r02", (88, 84, 92), (150, 140, 136)), door_text="The sty-barn. Something inside snores like a furnace.")
    m.place(WELL[1], 10, 10)
    R.pipes_v(11, 13, 15)
    R.pipes_h(16, 4, 15)
    m.place(GAUGE, 11, 16, solid=False)
    m.place(TROUGH[1], 30, 6)
    m.place(LAMP_RED, 2, 9)
    m.place(LAMP_RED, 18, 9)
    m.place(BARRELS["empty"], 8, 5)
    m.place(BARRELS["orange"], 2, 7)
    m.place(CRATES[1], 12, 6)
    m.place(CRATES[2], 13, 6)
    m.place(POTS[3], 19, 15)
    R.campfire(16, 9)                                 # the slag vent
    R.signs([(2, 17, "onion"), (2, 18, "beetroot"), (17, 17, "pepper")])
    R.hand_beds(["onion", "beetroot", "pepper"])
    R.scatter(PEBBLES[8:16], 16, ".a", gap=1)
    R.scatter([STUMP, bush(5, 2), MUSHROOMS[3]], 8, ".", gap=2)
    R.fireflies([(27, 16), (31, 19), (6, 23), (14, 10)])
    for e in ("spawn from_town 1 13 right", "spawn default 1 13 right",
              "exit 0 13..14 T03_TOWN from_ranch if=!phase:post", "exit 0 13..14 T03_POST from_ranch if=phase:post"):
        m.ent(e)
    R.folk("rancher_r02", 5, 8, "down", "m", "idle", "RANCH_R02_BRANN", "Brann Coker")
    R.folk("hand_r02_wisp", 8, 20, "left", "f", "hoe", "RANCH_R02_WISP", "Wisp")
    R.folk("hand_r02_kettle", 16, 20, "left", "m", "water", "RANCH_R02_KETTLE", "Kettle")
    R.folk("hand_r02_reg", 19, 13, "down", "mh", "idle", "RANCH_R02_REGULATOR", "Regulator's Man", "!phase:post")
    R.folk("hand_r02_lung", 31, 17, "left", "mh", "shovel", "RANCH_R02_ASHLUNG", "Ash-Lung Ped", "phase:post")
    R.beast("pig_r02a", 24, 8, "right", "pig:R02:adult", "RANCH_PIG")
    R.beast("pig_r02b", 31, 9, "left", "pig:R02:adult", "RANCH_PIG")
    R.beast("bunny_r02a", 13, 11, "down", "bunny", "RANCH_BUNNY")
    R.livestock({"cow": (27, 9), "pig": (24, 6), "bunny": (29, 9), "cat": (8, 8), "bird": [(22, 7), (26, 6), (32, 7)]},
                nest=(32, 5), kart=(20, 22), gate=(21, 11), gate_msg=GATE_MSG)
    m.ent('read 16 9 "A slag vent. Warm air rises from it day and night. The pigs sleep against it in winter." scene=RANCH_R02_VENT')
    m.ent('sign 2 12 "Soot Paddock. Pigs, coneys, doves. Truffles weighed at the gate, not after."')
    return R


# ---------------------------------------------------------------- R03 Gullbank Croft (Glass Coast, sand and sea)
def r03():
    R = Ranch("R03", 36, 26)
    p = R.p
    border(p, 36, 26, top=2, bottom=0)
    p.rect("X", 0, 0, 0, 25)
    p.rect(".", 0, 12, 0, 13)                       # west entry from Bellharbor
    p.blob("~", 30, 25, 14, 4.2, random.Random(3), rough=0.08)   # the inlet, south-east
    p.rect("~", 33, 14, 35, 25)
    p.rect("~", 0, 24, 35, 25)
    p.rect(",", 0, 12, 14, 13)                      # sand track
    p.rect(",", 14, 3, 15, 13)
    p.rect("=", 16, 2, 35, 2)                       # the line runs east along the top
    p.rect(",", 16, 3, 18, 4)
    p.rect(",", 3, 8, 8, 9)
    p.rect(",", 1, 22, 26, 23)                      # the tide line
    p.frame("f", 18, 6, 31, 13)
    p.put("G", [(24, 13)])
    p.rect(",", 22, 14, 26, 15)
    p.rect(",", 2, 15, 16, 15)
    p.rect("p", 3, 16, 8, 17)
    p.rect("p", 11, 16, 16, 17)
    p.rect(",", 2, 18, 16, 18)
    p.rect("h", 3, 19, 7, 20)
    p.rect("h", 11, 19, 14, 20)
    p.rect(",", 2, 21, 16, 21)
    m = R.build(header(R.r, "town_r03", "M013"))
    R.ground("coast")
    R.water("water_on_grass_02")
    R.beds()
    R.fences("fence_03")
    R.rails(2, 16, 35)
    m.solid(17, 2, "path")
    R.thicket(["spring", "blossom"], shade=0)
    R.house(3, 5, door_text="Maude's croft house. Nets dry in the window; nobody has fished from this house in years.")
    R.house(23, 4, tinted_house("barn_r03", (86, 120, 160), (220, 220, 210)), door_text="The byre. The door is swollen with salt and does not open for strangers.")
    m.place(WELL[2], 10, 12)
    R.pipes_h(15, 4, 15)
    R.pipes_v(10, 14, 14)
    m.place(TROUGH[3], 28, 7)
    m.place(BARRELS["water"], 8, 6)
    m.place(BUCKETS[0], 9, 9)
    m.place(CRATES[4], 2, 9)
    m.place(POTS[0], 27, 22)
    m.place(POTS[2], 28, 22)
    m.place(CRATES[5], 29, 21)
    R.campfire(12, 22)
    R.signs([(2, 16, "radish"), (2, 17, "tomato"), (17, 16, "cauliflower")])
    R.hand_beds(["radish", "tomato", "cauliflower"])
    R.scatter(FLOWERS[1:] + [bush(0, 2), bush(1, 2)], 22, ".", gap=1)
    R.scatter(PEBBLES[:8], 10, ",", gap=2)
    R.fireflies([(20, 17), (8, 23), (30, 16), (12, 10)])
    for e in ("spawn from_town 1 12 right", "spawn default 1 12 right",
              "exit 0 12..13 T04_QUAY from_ranch if=!phase:post", "exit 0 12..13 T04_UPPER from_ranch if=phase:post"):
        m.ent(e)
    R.folk("rancher_r03", 5, 9, "down", "f", "idle", "RANCH_R03_MAUDE", "Maude Tiller")
    R.folk("hand_r03_orrin", 8, 19, "left", "mh", "hoe", "RANCH_R03_ORRIN", "Orrin")
    R.folk("hand_r03_pim", 15, 19, "left", "f", "water", "RANCH_R03_PIM", "Pim")
    R.folk("hand_r03_clerk", 13, 8, "down", "mh", "idle", "RANCH_R03_TALLY", "Grazing Tallyman", "!phase:post")
    R.folk("hand_r03_widow", 20, 22, "down", "fh", "walk", "RANCH_R03_WIDOW", "Tide Widow", "phase:post", wander=True)
    R.beast("cow_r03a", 21, 9, "right", "cow:R03", "RANCH_COW")
    R.beast("bunny_r03a", 30, 11, "left", "bunny", "RANCH_BUNNY")
    R.livestock({"cow": (25, 10), "pig": (22, 11), "bunny": (28, 11), "cat": (7, 8), "bird": [(20, 8), (26, 8), (29, 9)]},
                nest=(30, 7), kart=(17, 2), gate=(24, 13), gate_msg=GATE_MSG)
    m.ent('sign 6 11 "Gullbank Croft. Salt-grass milk, sea-wind wool. Mind the tide line."')
    return R


# ---------------------------------------------------------------- R04 Windbreak Fold (Skyspine, snowy ledges, wind)
def r04():
    R = Ranch("R04", 36, 26)
    p = R.p
    border(p, 36, 26, top=1, bottom=2)
    p.rect("^", 0, 0, 35, 3)                        # the ledge face behind the fold
    p.rect("s", 0, 4, 35, 4)
    p.rect("s", 0, 4, 1, 25)
    p.rect("s", 34, 4, 35, 25)
    p.rect("X", 0, 4, 0, 25)
    p.rect("X", 35, 4, 35, 25)
    p.rect(".", 35, 12, 35, 13)                     # east entry from High Aerie
    p.rect("s", 34, 12, 34, 13)
    p.rect(",", 22, 12, 35, 13)
    p.frame("f", 2, 6, 14, 13)                      # the fold, west
    p.put("G", [(9, 13)])
    p.rect(",", 8, 14, 21, 14)
    p.vline(",", 21, 8, 14)
    p.rect(",", 18, 8, 26, 9)
    p.rect(",", 16, 15, 32, 15)
    p.rect("p", 17, 16, 22, 17)
    p.rect("p", 25, 16, 30, 17)
    p.rect(",", 16, 18, 32, 18)
    p.rect("h", 17, 19, 21, 20)
    p.rect("h", 25, 19, 29, 20)
    p.rect(",", 16, 21, 32, 21)
    p.blob("~", 7, 18, 3.2, 1.8, random.Random(4), rough=0.1)
    p.rect("=", 0, 22, 15, 22)
    p.rect(",", 0, 21, 15, 21)
    p.rect("s", 2, 23, 33, 25)
    p.rect("X", 2, 24, 33, 25)
    m = R.build(header(R.r, "town_r04", "M014"))
    R.ground("alpine")
    R.cliffs("snow", trees=["snow"])
    R.water("water_on_grass_02")
    R.beds()
    R.fences("fence_03")
    R.rails(22, 0, 15)
    m.solid(14, 22, "path")
    finish_common(R, ["snow", "summer"], 3, south_rows=(24, 25))
    R.house(18, 5, door_text="Sefton's house. The shutters are tied down with rope against the wind.")
    R.house(4, 4, tinted_house("barn_r04", (110, 96, 84)), door_text="The fold barn. The wind has worn the door boards smooth as bone.")
    m.place(WELL[3], 23, 10)
    R.pipes_v(24, 13, 14)
    R.pipes_h(15, 17, 30)
    m.place(TROUGH[2], 11, 8)
    m.place(BARRELS["low"], 17, 7)
    m.place(SACK, 26, 7)
    m.place(CRATES[0], 27, 7)
    m.place(ICE[3], 31, 9)
    m.place(LAMP_BLUE, 33, 11)
    R.campfire(28, 11)
    R.signs([(16, 16, "leek"), (16, 17, "corn"), (31, 16, "pumpkin")])
    R.hand_beds(["leek", "corn", "pumpkin"])
    R.scatter([bush(2, 2), bush(3, 2)] + FLOWERS[:1], 14, ".", gap=1)
    R.scatter(PEBBLES[4:8], 8, ",", gap=2)
    R.fireflies([(7, 16), (12, 19), (30, 10)])
    for e in ("spawn from_town 34 12 left", "spawn default 34 12 left",
              "exit 35 12..13 T05_COURT from_ranch if=!phase:post", "exit 35 12..13 T05_POST from_ranch if=phase:post"):
        m.ent(e)
    R.folk("rancher_r04", 20, 9, "down", "mh", "idle", "RANCH_R04_SEFTON", "Sefton Crag")
    R.folk("hand_r04_lisl", 22, 19, "left", "fh", "water", "RANCH_R04_LISL", "Lisl")
    R.folk("hand_r04_dunmore", 30, 19, "left", "m", "hoe", "RANCH_R04_DUNMORE", "Dunmore")
    R.folk("hand_r04_priest", 31, 13, "left", "mh", "idle", "RANCH_R04_PRIEST", "Wind-Priest", "!phase:post")
    R.folk("hand_r04_widower", 12, 15, "down", "m", "walk", "RANCH_R04_WIDOWER", "Cable Widower", "phase:post", wander=True)
    R.beast("cow_r04a", 5, 10, "right", "cow:R04", "RANCH_COW")
    R.beast("bunny_r04a", 12, 11, "left", "bunny", "RANCH_BUNNY")
    R.beast("bunny_r04b", 7, 9, "down", "bunny", "RANCH_BUNNY")
    R.livestock({"cow": (9, 10), "pig": (4, 11), "bunny": (12, 9), "cat": (19, 9), "bird": [(3, 8), (8, 8), (13, 12)]},
                nest=(3, 7), kart=(14, 22), gate=(9, 13), gate_msg=GATE_MSG)
    m.ent('sign 33 14 "Windbreak Fold. Wool, milk, message doves. Rope yourself on the cliff path."')
    return R


# ---------------------------------------------------------------- R05 Brinewell Steading (Pale Basin, dry ground)
def r05():
    R = Ranch("R05", 36, 26)
    p = R.p
    border(p, 36, 26, top=1, bottom=1)
    p.rect("^", 0, 0, 35, 2)                        # the basin rim
    p.rect("^", 0, 0, 1, 25)
    p.rect("X", 2, 24, 34, 25)
    p.rect("X", 35, 0, 35, 25)
    p.rect(".", 35, 13, 35, 14)                     # east entry from Nacre
    p.rect(",", 20, 13, 35, 14)
    p.rect(",", 4, 6, 11, 7)
    p.vline(",", 7, 7, 12)
    p.rect(",", 2, 12, 20, 12)
    p.frame("f", 20, 3, 33, 10)
    p.put("G", [(26, 10)])
    p.rect(",", 26, 11, 26, 12)
    p.rect("g", 12, 15, 18, 21)                     # the walled garden's green round the cistern
    p.rect("~", 14, 17, 16, 19)
    p.rect("p", 3, 15, 8, 16)
    p.rect("p", 3, 18, 8, 19)
    p.rect(",", 2, 14, 9, 14)
    p.rect(",", 2, 17, 9, 17)
    p.rect(",", 2, 20, 9, 20)
    p.rect("h", 22, 16, 27, 17)
    p.rect("h", 22, 19, 27, 20)
    p.rect(",", 21, 15, 28, 15)
    p.rect(",", 21, 18, 28, 18)
    p.rect(",", 21, 21, 28, 21)
    p.rect("=", 0, 22, 30, 22)                      # the line cuts west through the rim
    p.rect(",", 10, 21, 20, 21)
    m = R.build(header(R.r, "town_r05", "M015"))
    R.ground("dry")
    R.cliffs("brown", trees=["autumn"])
    R.furrows()
    R.water("water_on_grass_01", edge=False)
    R.beds()
    R.fences("fence_02")
    R.rails(22, 0, 30)
    m.solid(4, 22, "path")
    R.thicket(["autumn", "fall"], shade=2, big=False)
    R.house(4, 3, door_text="Yara's house. A salt crust has grown up the door like frost.")
    R.house(22, 1, tinted_house("barn_r05", (230, 226, 214), (236, 232, 222)), door_text="The steading barn, built of salt blocks. It sweats in the afternoons.")
    m.place(WELL[2], 12, 9)
    R.pipes_v(12, 12, 12)
    R.pipes_h(13, 3, 12)
    m.place(VALVE, 12, 13, solid=False)
    m.place(TROUGH[1], 30, 6)
    m.place(BARRELS["water"], 9, 4)
    m.place(BARRELS["low"], 10, 4)
    m.place(POTS[1], 2, 6)
    m.place(POTS[4], 3, 6)
    m.place(CRATES[3], 18, 8)
    m.place(STUMP, 31, 16)
    R.campfire(17, 7)
    R.signs([(2, 15, "eggplant"), (2, 18, "celery"), (29, 16, "wheat")])
    R.hand_beds(["eggplant", "celery", "wheat"])
    R.scatter(PEBBLES[4:12], 18, ".", gap=1)
    R.scatter([STUMP, bush(2, 2)], 5, ".", gap=2)
    R.scatter(FLOWERS, 5, "g", gap=1)
    R.fireflies([(15, 16), (13, 20), (18, 18)])
    for e in ("spawn from_town 34 13 left", "spawn default 34 13 left",
              "exit 35 13..14 T06_MARKET from_ranch if=!phase:post", "exit 35 13..14 T06_POST from_ranch if=phase:post"):
        m.ent(e)
    R.folk("rancher_r05", 6, 7, "down", "fh", "idle", "RANCH_R05_YARA", "Yara Saltmarrow")
    R.folk("hand_r05_kesh", 28, 16, "left", "f", "water", "RANCH_R05_KESH", "Kesh")
    R.folk("hand_r05_amon", 28, 19, "left", "m", "shovel", "RANCH_R05_AMON", "Amon")
    R.folk("hand_r05_clerk", 31, 13, "left", "mh", "idle", "RANCH_R05_TAXER", "Salt-Tax Clerk", "!phase:post")
    R.folk("hand_r05_survivor", 19, 13, "down", "m", "walk", "RANCH_R05_SURVIVOR", "Basin Survivor", "phase:post", wander=True)
    R.beast("pig_r05a", 23, 7, "right", "pig:R05:adult", "RANCH_PIG")
    R.beast("cow_r05a", 31, 8, "left", "cow:R05", "RANCH_COW")
    R.livestock({"cow": (27, 7), "pig": (24, 9), "bunny": (29, 9), "cat": (8, 7), "bird": [(21, 5), (25, 4), (32, 4)]},
                nest=(21, 4), kart=(4, 22), gate=(26, 10), gate_msg=GATE_MSG)
    m.ent('sign 33 12 "Brinewell Steading. Salt-fed pork, brine eggs. Water is sold by the cup."')
    return R


# ---------------------------------------------------------------- R07 Maple Gate Farm (Vermilion Reach, autumn)
def r07():
    R = Ranch("R07", 36, 26)
    p = R.p
    border(p, 36, 26, top=2, bottom=2)
    p.rect(".", 0, 13, 0, 14)                       # west entry from Akagane
    p.rect(",", 0, 13, 18, 14)
    p.rect(",", 3, 7, 10, 8)
    p.vline(",", 6, 8, 12)
    p.vline(",", 16, 4, 12)
    p.rect(",", 14, 4, 18, 5)                       # the fox gate's clearing
    p.frame("f", 20, 3, 33, 11)
    p.put("G", [(20, 7)])                           # gate on the west fence
    p.rect(",", 17, 7, 19, 7)
    # the stream from the north woods down to a pond, crossed by the bed paths
    p.rect("~", 29, 13, 30, 16)
    p.blob("~", 29, 18, 3.0, 1.8, random.Random(7), rough=0.1)
    p.rect(",", 2, 15, 18, 15)
    p.rect("p", 3, 16, 8, 17)
    p.rect("p", 11, 16, 16, 17)
    p.rect(",", 2, 18, 18, 18)
    p.rect("h", 3, 19, 6, 20)
    p.rect("h", 11, 19, 15, 20)
    p.rect(",", 2, 21, 18, 21)
    p.rect(",", 19, 21, 35, 21)
    p.rect("=", 20, 22, 35, 22)
    m = R.build(header(R.r, "vermilion", "M011"))
    # leaf litter under the maples (round the woods' edge)
    for (x, y) in sorted(m.cells(".")):
        if any(m.at(x + dx, y + dy) == "X" for dx in (-1, 0, 1) for dy in (-1, 0, 1)) and m.rng.random() < 0.35:
            m.rows[y] = m.rows[y][:x] + "l" + m.rows[y][x + 1:]
    R.ground("autumn")
    R.leaves()
    R.water("water_on_grass_01")
    R.beds()
    R.fences("fence_02")
    R.rails(22, 20, 35)
    m.solid(21, 22, "path")
    finish_common(R, ["fall", "autumn", "blossom"], 2, south_rows=(24, 25))
    R.house(3, 4, tinted_house("house_r07", (150, 46, 40)), door_text="Okuni's house. A paper charm is pasted across the door: do not disturb the sleeping.")
    R.house(24, 1, tinted_house("barn_r07", (120, 60, 44)), door_text="The barn. Lantern smoke has stained the beams the colour of tea.")
    m.place(LAMP_RED, 14, 3)
    m.place(LAMP_RED, 18, 3)
    m.place(SIGN_BOARD, 16, 3)                        # the fox gate shrine board
    m.place(WELL[0], 9, 10)
    R.pipes_v(10, 13, 14)
    R.pipes_h(15, 4, 15)
    m.place(TROUGH[2], 30, 5)
    m.place(BARRELS["water"], 2, 7)
    m.place(POTS[2], 8, 6)
    m.place(CRATES[1], 12, 8)
    R.campfire(13, 10)
    R.signs([(2, 16, "bamboo"), (2, 17, "grape"), (17, 16, "radish")])
    R.hand_beds(["bamboo", "grape", "radish"])
    R.scatter(MUSHROOMS + FLOWERS[2:], 14, ".l", gap=1)
    R.scatter(PEBBLES[:4], 6, ",", gap=2)
    R.fireflies([(30, 14), (27, 19), (32, 18), (8, 22), (17, 6)])
    for e in ("spawn from_town 1 13 right", "spawn default 1 13 right", "exit 0 13..14 N28_R01 from_ranch"):
        m.ent(e)
    R.folk("rancher_r07", 5, 8, "down", "f", "idle", "RANCH_R07_OKUNI", "Okuni Hara")
    R.folk("hand_r07_sumi", 7, 19, "left", "fh", "water", "RANCH_R07_SUMI", "Sumi")
    R.folk("hand_r07_taro", 16, 19, "left", "m", "shovel", "RANCH_R07_TARO", "Taro")
    R.folk("hand_r07_steward", 17, 12, "down", "mh", "idle", "RANCH_R07_STEWARD", "Masked Steward", "!phase:post")
    R.folk("hand_r07_exile", 24, 13, "left", "m", "walk", "RANCH_R07_EXILE", "Exiled Courtier", "phase:post", wander=True)
    R.beast("fox_r07a", 26, 17, "left", "fox", "RANCH_FOX")
    R.beast("fox_r07b", 12, 23 - 1, "right", "fox", "RANCH_FOX")
    R.beast("pig_r07a", 24, 8, "right", "pig:R07:adult", "RANCH_PIG")
    R.beast("bunny_r07a", 31, 9, "left", "bunny", "RANCH_BUNNY")
    R.livestock({"cow": (27, 8), "pig": (23, 10), "bunny": (30, 9), "cat": (9, 8), "bird": [(22, 6), (28, 5), (32, 7)]},
                nest=(32, 4), kart=(21, 22), gate=(20, 7), gate_msg=GATE_MSG)
    m.ent('read 16 3 "A small fox gate, red lacquer over grey wood. Rice and a coin are left at its foot every morning." scene=RANCH_R07_GATE')
    m.ent('sign 2 12 "Maple Gate Farm. By leave of the Court. Foxes are guests here; treat them so."')
    return R


# ---------------------------------------------------------------- R08 Lazar Fields (Mirewold, dark wet grass)
def r08():
    R = Ranch("R08", 36, 26)
    p = R.p
    border(p, 36, 26, top=2, bottom=2)
    p.rect(".", 0, 13, 0, 14)                       # west entry from Harrowfen
    p.rect(",", 0, 13, 19, 14)
    p.rect(",", 4, 7, 11, 8)
    p.vline(",", 7, 8, 12)
    p.frame("f", 21, 3, 33, 11)
    p.put("G", [(26, 11)])
    p.rect(",", 25, 12, 27, 14)
    p.rect(",", 20, 14, 27, 14)
    # pools ringed by paler tussock grass
    for (cx, cy, rx, ry, sd) in ((29, 18, 3.4, 2.0, 1), (15, 4, 2.4, 1.2, 2), (3, 21, 1.6, 1.2, 3)):
        p.blob("g", cx, cy, rx + 1.2, ry + 1.0, random.Random(sd), rough=0.15)
        p.blob("~", cx, cy, rx, ry, random.Random(sd + 9), rough=0.1)
    p.rect(",", 6, 15, 20, 15)
    p.rect(",", 6, 16, 6, 20)
    p.rect(",", 20, 16, 20, 20)
    p.rect("p", 7, 16, 12, 17)
    p.rect("p", 14, 16, 19, 17)
    p.rect(",", 7, 18, 19, 18)
    p.rect("h", 7, 19, 11, 20)
    p.rect("h", 14, 19, 19, 20)
    p.rect(",", 6, 21, 20, 21)
    p.rect(",", 21, 21, 35, 21)
    p.rect("=", 21, 22, 35, 22)
    m = R.build(header(R.r, "fen", "M012"))
    R.ground("marsh")
    R.water("water_on_grass_02", edge=False)
    R.beds()
    R.fences("fence_03")
    R.rails(22, 21, 35)
    m.solid(22, 22, "path")
    finish_common(R, ["summer"], 5, south_rows=(24, 25))
    R.house(4, 4, tinted_house("house_r08", (200, 196, 180), (236, 236, 228)), door_text="Gideon's house. Lime-washed, door and all. It smells of vinegar.")
    R.house(24, 1, tinted_house("barn_r08", (90, 86, 104)), door_text="The barn. A Board of Quarantine seal hangs on the latch, signed and resigned.")
    m.place(WELL[1], 11, 10)
    R.pipes_v(12, 13, 14)
    R.pipes_h(15, 8, 19)
    m.place(TROUGH[1], 30, 5)
    m.place(BARRELS["water"], 3, 7)
    m.place(BUCKETS[1], 3, 8)
    m.place(MAILBOX[0], 9, 12)
    m.place(LAMP_BLUE, 19, 12)
    R.campfire(15, 10)
    R.signs([(5, 16, "berry"), (5, 17, "leek"), (13, 16, "broccoli")])
    R.hand_beds(["berry", "leek", "broccoli"])
    R.scatter([bush(5, 2), bush(6, 2)] + MUSHROOMS[2:], 20, ".g", gap=1)
    R.scatter(PEBBLES[12:16], 6, ",", gap=2)
    R.fireflies([(29, 15), (26, 19), (32, 20), (15, 6), (3, 19), (12, 22), (18, 8)])
    for e in ("spawn from_town 1 13 right", "spawn default 1 13 right", "exit 0 13..14 N22_R01 from_ranch"):
        m.ent(e)
    R.folk("rancher_r08", 6, 8, "down", "m", "idle", "RANCH_R08_GIDEON", "Gideon Marl")
    R.folk("hand_r08_nell", 12, 19, "left", "f", "water", "RANCH_R08_NELL", "Nell")
    R.folk("hand_r08_ash", 20, 19, "left", "mh", "hoe", "RANCH_R08_ASH", "Brother Ash")
    R.folk("hand_r08_guard", 18, 13, "down", "mh", "idle", "RANCH_R08_GUARD", "Wall Warden", "!phase:post")
    R.folk("hand_r08_burned", 23, 15, "down", "m", "walk", "RANCH_R08_BURNED", "Burned-Out Tanner", "phase:post", wander=True)
    R.beast("pig_r08a", 23, 8, "right", "pig:R08:adult", "RANCH_PIG")
    R.beast("bunny_r08a", 31, 9, "left", "bunny", "RANCH_BUNNY")
    R.beast("mouse_r08", 17, 22 - 1, "left", "mouse", "RANCH_MOUSE")
    R.livestock({"cow": (27, 8), "pig": (24, 10), "bunny": (30, 7), "cat": (9, 8), "bird": [(22, 6), (28, 5), (32, 8)]},
                nest=(32, 4), kart=(22, 22), gate=(26, 11), gate_msg=GATE_MSG)
    m.ent('sign 3 12 "Lazar Fields. Clean meat, clean eggs, inspected by the Board. No one from the wards past this sign."')
    return R


# ---------------------------------------------------------------- R09 Rimefold (Hoarfrost March, snow and ice)
def r09():
    R = Ranch("R09", 36, 26)
    p = R.p
    border(p, 36, 26, top=1, bottom=2)
    p.rect("^", 1, 0, 34, 2)                        # snow cliffs along the north
    p.rect(",", 16, 0, 19, 2)                       # the road down from Rimeholt cuts through them
    p.rect(",", 16, 3, 19, 6)
    p.rect(",", 3, 7, 30, 8)
    p.frame("f", 21, 9, 33, 17)
    p.put("G", [(24, 9)])
    p.rect(",", 2, 10, 15, 10)
    p.rect("p", 3, 11, 8, 12)
    p.rect("p", 10, 11, 15, 12)
    p.rect(",", 2, 13, 15, 13)
    p.rect("h", 3, 14, 7, 15)
    p.rect("h", 10, 14, 14, 15)
    p.rect(",", 2, 16, 15, 16)
    p.rect("g", 2, 18, 12, 22)                      # the pond's thawed bank
    p.blob("~", 7, 20, 3.2, 1.6, random.Random(9), rough=0.08)
    p.rect(",", 16, 9, 18, 21)
    p.rect(",", 16, 21, 35, 21)
    p.rect("=", 17, 22, 35, 22)
    m = R.build(header(R.r, "winter", "M014"))
    R.ground("snow")
    R.cliffs("snow", trees=["snow"])
    R.water("water_on_grass_02", edge=False)
    R.beds()
    R.fences("fence_04")
    R.rails(22, 17, 35)
    m.solid(18, 22, "path")
    finish_common(R, ["snow"], 4, south_rows=(24, 25))
    R.house(3, 3, tinted_house("house_r09", (96, 78, 70)), door_text="Hild's longhouse. A cow skull is nailed above the door, horns waxed.")
    R.house(27, 4, tinted_house("barn_r09", (70, 58, 54)), door_text="The byre. Warm breath fogs through the gaps in the planks.")
    m.place(WELL[3], 12, 4)
    R.pipes_v(13, 7, 9)
    R.pipes_h(10, 4, 14)
    m.place(TROUGH[3], 30, 11)
    for (x, y, i) in ((9, 4, 0), (33, 19, 1), (2, 23 - 1, 4), (14, 19, 2), (21, 19, 3), (31, 3, 4)):
        m.place(ICE[i], x, y)
    m.place(BARRELS["empty"], 8, 4)
    m.place(CRATES[2], 20, 4)
    m.place(SACK, 21, 4)
    R.campfire(10, 6)
    R.signs([(2, 11, "potato"), (2, 12, "carrot"), (16, 12, "berry")])
    R.hand_beds(["potato", "carrot", "berry"])
    R.scatter([bush(4, 2), STUMP], 8, ".", gap=2)
    R.scatter(PEBBLES[:4], 6, ",", gap=2)
    R.fireflies([(7, 18), (11, 21), (4, 19)])
    for e in ("spawn from_town 17 1 down", "spawn default 17 1 down", "exit 16..19 0 N32_R01 from_ranch"):
        m.ent(e)
    R.folk("rancher_r09", 6, 7, "down", "fh", "idle", "RANCH_R09_HILD", "Hild Ulfsdottir")
    R.folk("hand_r09_ivar", 8, 14, "left", "mh", "shovel", "RANCH_R09_IVAR", "Ivar")
    R.folk("hand_r09_ketil", 15, 14, "left", "m", "water", "RANCH_R09_KETIL", "Ketil")
    R.folk("hand_r09_trader", 22, 6, "down", "mh", "idle", "RANCH_R09_TRADER", "Fur Buyer", "!phase:post")
    R.folk("hand_r09_refugee", 26, 19, "down", "f", "walk", "RANCH_R09_REFUGEE", "Pit Refugee", "phase:post", wander=True)
    R.beast("cow_r09a", 24, 13, "right", "cow:R09", "RANCH_COW")
    R.beast("cow_r09b", 30, 15, "left", "cow:R09", "RANCH_COW")
    R.beast("fox_r09a", 33, 7, "left", "fox", "RANCH_FOX")
    R.livestock({"cow": (27, 13), "pig": (23, 15), "bunny": (31, 13), "cat": (8, 8), "bird": [(22, 11), (26, 11), (32, 16)]},
                nest=(32, 10), kart=(18, 22), gate=(24, 9), gate_msg=GATE_MSG)
    m.ent('sign 19 4 "Rimefold. Cattle that do not die of cold. Shut the gate or they will walk to the Ice Road."')
    return R


RANCH_FUNCS = [r01, r02, r03, r04, r05, r07, r08, r09]



K.CROPS_PREVIEW.update({k: (v[3], v[4], v[5]) for k, v in RC.CROPS.items()})


def main():
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        os.makedirs(out, exist_ok=True)
        for f in RANCH_FUNCS:
            R = f()
            K.preview(R.m, os.path.join(out, R.m.id + ".png"), 2)
        return
    map_only = "--map-only" in sys.argv or not K.have_art()
    texts = []
    for f in RANCH_FUNCS:
        R = f()
        if not map_only:
            R.m.save()
        texts.append(R.m.map_text())
    out = os.path.join(REPO, "content_src", "maps", "ranch.map")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("#! Ranches: generated by tools/maps48/maps/ranch.py from its hand-made plans (do not edit by hand).\n")
        fh.write("#! Hooks for game/src/meta/ranch.gd (validated by tools/content/ranch.py): rancher_<rid>, kart_<RID>, nest_<RID>,\n")
        fh.write("#! own_<RID>_<animal>, the pen gate block, plot cells. Sprites ranch:<key> are the pack's (ranch.gd draws them).\n")
        for t in texts:
            fh.write(t)
    print("ranch maps: %d written%s -> %s" % (len(texts), " (map text only)" if map_only else " with art", out))


if __name__ == "__main__":
    main()
