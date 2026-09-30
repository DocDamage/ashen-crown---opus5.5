"""Cinder Reach town pieces (group "cinder": Cinderwake T03_TOWN / T03_POST / T03_GARDEN / T03_YARD).
Steampunk pack (soot-brown brick, brass, copper pipes) + Factory Ruins (damage, scrap) + a few Medieval Town pieces.
Helpers: tall() composes a taller building from a whole-building sprite by repeating a wall row (all pieces share the
building's base line so actors walk behind the whole block); wall_face() lays retaining-wall panels; reach() checks
entity reachability with and without tileset_overs; coverage() estimates detail coverage."""
from collections import Counter, deque
import kit
from kit import st, Mat, Stamp, C
from skins.lib_d import TintMat
from skins.furnace import _sooty
from skins import common as K

S = "steam"
F = "factory"

# ------------------------------------------------------------------ ground (soot-stained swatches, never scaled)
kit._img_cache.setdefault((S, "gen_cw_cobble"), _sooty("town", "2", (0, 0, 96, 192), n=768, seed=21, soot=(46, 34, 28), amount=0.5, warm=0.12))
kit._img_cache.setdefault((S, "gen_cw_cobble2"), _sooty("town", "2", (0, 0, 96, 192), n=768, seed=33, soot=(40, 36, 34), amount=0.7))
kit._img_cache.setdefault((S, "gen_cw_cobwarm"), _sooty("town", "2", (96, 0, 96, 192), n=768, seed=27, soot=(52, 38, 30), amount=0.45))
kit._img_cache.setdefault((S, "gen_cw_plates"), _sooty(S, "5", (0, 384, 192, 192), n=768, seed=5, amount=0.35, warm=0.15))
kit._img_cache.setdefault((S, "gen_cw_ash"), _sooty("town", "2", (288, 0, 96, 192), n=768, seed=12, soot=(70, 62, 54), amount=0.55))
kit._img_cache.setdefault((S, "gen_cw_moss"), _sooty("town", "2", (288, 0, 96, 192), n=768, seed=19, soot=(60, 64, 48), amount=0.3))
kit._img_cache.setdefault((S, "gen_cw_dirt"), _sooty("town", "2", (192, 0, 96, 192), n=768, seed=14, soot=(58, 46, 40), amount=0.5))
kit._img_cache.setdefault((F, "gen_cw_cracked"), _sooty(F, "1", (0, 384, 384, 192), n=768, seed=17, soot=(46, 40, 36), amount=0.45))

MATS = dict(
    cob=Mat([(S, "gen_cw_cobble", 0, 0, 768, 768)], "path", organic=True, prio=2),
    cob2=Mat([(S, "gen_cw_cobble2", 0, 0, 768, 768)], "path", organic=True, prio=2),
    cobwarm=Mat([(S, "gen_cw_cobwarm", 0, 0, 768, 768)], "path", organic=True, prio=2),
    plates=Mat([(S, "gen_cw_plates", 0, 0, 768, 768)], "floor", prio=2),
    grate=Mat([(S, "10", 192, 384, 192, 192)], "floor2"),
    grate2=Mat([(S, "3", 0, 480, 192, 96)], "floor2"),
    deck=Mat([(S, "10", 192, 576, 192, 96)], "bridge"),
    ash=TintMat([(S, "gen_cw_ash", 0, 0, 768, 768)], "grass", mul=(0.86, 0.72, 0.56), organic=True, prio=3),
    moss=TintMat([(S, "gen_cw_moss", 0, 0, 768, 768)], "grass", mul=(0.72, 0.68, 0.5), organic=True, prio=3),
    pond=Mat([("fa", "water_deep", 0, 0, 48, 48)], "water", organic=True, prio=0),
    dirt=Mat([(S, "gen_cw_dirt", 0, 0, 768, 768)], "path", organic=True, prio=1),
    cracked=Mat([(F, "gen_cw_cracked", 0, 0, 768, 768)], "path", organic=True, prio=2),
    copper=TintMat([(S, "11", 0, 0, 192, 192)], "floor", mul=(0.8, 0.72, 0.66)),
    stairs=TintMat([("town", "1", 400, 384, 64, 96)], "stairs", mul=(0.8, 0.7, 0.62)),
    water=Mat([("fa", "water_deep", 0, 0, 48, 48)], "water"),
    soot=Mat([("color", (26, 21, 20))], "wall"),
)

# ------------------------------------------------------------------ retaining-wall panels (1 wide x 2 tall, ledge on top)
PANELS = [st(S, "7", c, 14, 1, 2, flat=True, solid=0) for c in (0, 1, 2, 3, 8, 9)] + \
         [st(S, "7", c, 12, 1, 2, flat=True, solid=0) for c in (0, 1)]
PANEL_PIPE2 = st(S, "7", 10, 14, 2, 2, flat=True, solid=0)

# ------------------------------------------------------------------ buildings (alias, sheet, c, r, w, h)
B = dict(
    gearhall=(S, "9", 8, 0, 4, 4), brick_hall=(S, "9", 12, 0, 4, 4), works_red=(S, "9", 4, 4, 4, 4),
    furnace=(S, "9", 8, 4, 4, 4), dome_store=(S, "9", 12, 4, 4, 4), chapel_works=(S, "9", 0, 4, 4, 4),
    big_hall=(S, "9", 8, 8, 4, 4), clock2=(S, "9", 12, 8, 2, 4), narrow=(S, "9", 14, 8, 2, 4),
    factory_l=(S, "9", 0, 12, 4, 4), gear_dome=(S, "9", 4, 12, 4, 4), copper_hall=(S, "9", 8, 12, 4, 4),
    brick_long=(S, "9", 12, 12, 4, 4), clock1=(S, "9", 0, 0, 2, 4), clock_tower=(S, "9", 2, 0, 2, 4),
    dome_tower=(S, "9", 4, 0, 2, 4), brick_works=(S, "9", 6, 0, 2, 4),
    glass_house=(S, "3", 8, 12, 4, 4), stone_house=(S, "3", 12, 12, 4, 4),
    green_house=(S, "4", 12, 0, 4, 4), twin_house=(S, "4", 8, 4, 4, 4), gable_house=(S, "4", 12, 4, 4, 4),
    blue_house=(S, "4", 8, 8, 4, 4), arch_house=(S, "4", 4, 12, 4, 4), narrow_house=(S, "4", 12, 12, 2, 4),
    blue_works=(S, "4", 4, 0, 4, 4), green_works=(S, "4", 4, 4, 4, 4), clock_hall=(S, "4", 0, 0, 2, 4),
    tower4=(S, "4", 2, 0, 2, 4),
    t_gear=(S, "10", 0, 0, 3, 4), t_clock=(S, "10", 3, 0, 2, 4), t_pipes=(S, "10", 6, 0, 2, 4),
    t_dome=(S, "10", 8, 0, 3, 4), t_chimney=(S, "10", 11, 0, 2, 4), t_wheel=(S, "10", 0, 4, 3, 4),
    t_frame=(S, "10", 3, 4, 2, 4), t_small=(S, "10", 5, 4, 3, 4), t_tank=(S, "10", 8, 4, 3, 4),
    t_beacon=(S, "10", 11, 4, 2, 4), t_stacks=(S, "10", 13, 4, 3, 4),
    barn=(S, "8", 8, 4, 4, 4), barn2=(S, "8", 8, 8, 4, 4), farmhouse=(S, "8", 8, 0, 4, 4), shed=(S, "8", 14, 4, 2, 4),
    silo=(S, "8", 12, 4, 2, 4), watertower=(S, "8", 12, 8, 2, 4), barn3=(S, "8", 13, 12, 3, 4),
    store_front=(S, "11", 4, 13, 4, 3), ovens=(S, "11", 12, 12, 4, 2),
)


def tall(m, key, x, y, order=None, solid=2, door=None, kind="house", cols=None):
    """Place building B[key] with its top-left at (x, y); `order` lists source rows (0 = top) drawn top to bottom,
    e.g. (0, 1, 1, 2, 3) repeats the upper storey. The `solid` bottom rows block (columns `cols` rel, default all);
    door=(dx, dy) relative cell becomes kind "door". Returns the bottom row."""
    al, sh, c, r, w, h = B[key]
    order = order or tuple(range(h))
    n = len(order)
    for i, ro in enumerate(order):
        s = Stamp(al, sh, c, r + ro, w, 1, solid=0, base=(n - i) * C)
        m.place(s, x, y + i)
    c0, c1 = cols if cols else (0, w - 1)
    for rr in range(n - solid, n):
        for cc in range(c0, c1 + 1):
            m.solid(x + cc, y + rr, kind)
    if door:
        m.solid(x + door[0], y + door[1], "door")
    return y + n - 1


def piece(key, dc, dr, w, h, **kw):
    """A sub-rectangle of building B[key] (relative cells)."""
    al, sh, c, r, _, _ = B[key]
    return st(al, sh, c + dc, r + dr, w, h, **kw)


def wall_face(m, y, x0, x1, rng, kind="wall", skip=()):
    """Retaining wall 2 rows tall (rows y, y+1) from x0 to x1 with riveted soot panels; collision `kind`."""
    x = x0
    while x <= x1:
        if x in skip:
            x += 1
            continue
        w = 1
        if x + 1 <= x1 and (x + 1) not in skip and rng.random() < 0.18:
            m.place(PANEL_PIPE2, x, y)
            w = 2
        else:
            m.place(rng.choice(PANELS), x, y)
        for dx in range(w):
            m.solid(x + dx, y, kind)
            m.solid(x + dx, y + 1, kind)
        x += w


def waterfall(m, x, y_top, rows=2):
    """Animated cascade over a 2-row retaining wall at column x (lip at y_top, body, foam on the row below)."""
    m.anim("waterfall_top", x, y_top, h=48, flat=True)
    for r in range(1, rows):
        m.anim("waterfall_body", x, y_top + r, h=48, flat=True)
    m.anim("waterfall_base", x, y_top + rows, h=48, flat=True)
    for r in range(rows):
        m.solid(x, y_top + r, "water")


def smoke(m, x, y, dx=0, dy=0):
    m.anim("chimney_smoke", x, y, dx=dx, dy=dy, h=96)


# ------------------------------------------------------------------ props
RAIL = [st(S, "10", c, 8, 1, 1, kind="fence") for c in (8, 9, 10, 11)]
LAMP_S = [st(S, "10", c, 10, 1, 2, kind="lamp") for c in (10, 11, 12, 13)]
PIPE_ARCH = st(S, "6", 12, 8, 3, 3, kind="pipe", solid=1, cols=(0, 0))
LAMP = st(S, "1", 2, 5, 1, 3, kind="lamp")
LAMP2 = st(S, "1", 3, 5, 1, 3, kind="lamp")
LAMP_GAS = st(S, "3", 8, 1, 1, 3, kind="lamp")
LAMP_GAS2 = st(S, "3", 10, 1, 1, 3, kind="lamp")
LAMP_GREEN = st(S, "11", 14, 8, 1, 3, kind="lamp")
LAMP_GREEN2 = st(S, "11", 15, 8, 1, 3, kind="lamp")
LAMP_POST = st(S, "11", 8, 10, 1, 3, kind="lamp")
LAMP_SIGN = st(S, "4", 8, 10, 1, 2, kind="sign")        # lamp post with a hanging shop sign
LAMP_TRIPLE = st(S, "4", 8, 12, 1, 3, kind="lamp")
CLOCK_POST = st(S, "11", 8, 13, 1, 2, kind="lamp")
FOUNTAIN = st(S, "1", 0, 6, 2, 2, kind="well")
GRANDCLOCK = st(S, "3", 9, 0, 1, 4, kind="statue")
BIG_CLOCK = st(S, "1", 6, 6, 2, 2, kind="statue")
TUBES = st(S, "1", 4, 6, 2, 2, kind="machine")
WORKBENCH = st(S, "1", 0, 8, 2, 2, kind="table")
GAUGE = st(S, "1", 2, 8, 1, 2, kind="machine")
PIPE_MACHINE = st(S, "1", 4, 8, 2, 2, kind="machine")
TOOLBENCH = st(S, "1", 9, 12, 2, 2, kind="table")
TOOLSHELF = st(S, "1", 8, 12, 1, 1, kind="crate")
CRATES = [st(S, "1", c, r, 1, 1, kind="crate") for (c, r) in ((11, 12), (12, 12), (13, 12), (11, 13), (12, 13))]
PIPES_COPPER = st(S, "1", 9, 14, 3, 1, kind="pipe")
PIPES_STEEL = st(S, "1", 9, 15, 3, 1, kind="pipe")
LOCK_GATE = st(S, "1", 0, 14, 4, 2, kind="sluice")
STALLS = [st(S, "11", 8, 0, 2, 2, kind="counter"), st(S, "11", 10, 0, 2, 2, kind="counter"),
          st(S, "11", 12, 0, 2, 2, kind="counter"), st(S, "11", 14, 0, 2, 2, kind="counter"),
          st(S, "11", 14, 2, 2, 2, kind="counter"), st(S, "11", 9, 10, 2, 2, kind="counter"),
          st(S, "3", 12, 2, 2, 2, kind="counter")]
STALL_S = [st(S, "3", 4, 8, 1, 2, kind="counter"), st(S, "3", 5, 8, 1, 2, kind="counter")]
CART_STALL = st(S, "11", 8, 2, 2, 2, kind="cart")
BOILER_S = st(S, "3", 8, 8, 1, 2, kind="machine")
BENCH = st(S, "3", 9, 8, 2, 1, kind="bench")
BENCH_S = st(S, "3", 12, 9, 1, 1, kind="bench")
VALVE = st(S, "3", 11, 8, 1, 1, kind="machine")
GEAR_S = [st(S, "3", 13, 8, 1, 1, kind="crate"), st(S, "4", 4, 10, 1, 1, kind="crate"), st(S, "4", 5, 10, 1, 1, kind="crate")]
BOILER_BIG = st(S, "3", 14, 8, 2, 3, kind="machine")
RED_TANK = st(S, "3", 8, 10, 1, 2, kind="machine")
BIG_GEAR = st(S, "3", 10, 10, 2, 2, kind="wheel")
VENT = st(S, "3", 13, 10, 1, 1, kind="vent")
GRILLE = st(S, "3", 7, 10, 1, 1, solid=0, flat=True)
MANHOLES = [st(S, "3", c, r, 1, 1, solid=0, flat=True) for (c, r) in ((4, 11), (5, 11), (4, 12), (5, 12))]
DRAIN = st(S, "11", 13, 10, 1, 1, solid=0, flat=True)
GEAR_WHEEL = st(S, "4", 9, 13, 3, 3, kind="wheel")          # big brass gear, used as the terrace waterwheels
GEAR_BIG2 = st(S, "4", 0, 4, 2, 2, kind="wheel")
GEAR_BIG3 = st(S, "4", 0, 6, 2, 2, kind="wheel")
PISTONS = st(S, "4", 4, 8, 2, 2, kind="machine")
TRACTOR = st(S, "4", 2, 5, 2, 3, kind="cart")
BENCH_IRON = st(S, "4", 14, 12, 2, 1, kind="bench")
BENCH_IRON2 = st(S, "4", 14, 13, 2, 1, kind="bench")
BENCH_CLOCK = st(S, "11", 9, 14, 3, 2, kind="bench")
BENCH_CLOCK2 = st(S, "11", 12, 14, 2, 2, kind="bench")
COPPER_TANK = st(S, "6", 8, 8, 1, 3, kind="machine")
CONTROL = st(S, "6", 6, 8, 2, 2, kind="machine")
STOVE = st(S, "6", 8, 14, 2, 2, kind="machine")
PANEL = st(S, "6", 10, 14, 2, 2, kind="machine")
TANKS = st(S, "5", 10, 14, 2, 2, kind="machine")
TWIN_BOIL = st(S, "5", 6, 14, 2, 2, kind="machine")
BOILER_RED = st(S, "5", 12, 8, 2, 3, kind="machine")
STEAM_VENT = st(S, "11", 11, 12, 1, 2, kind="vent")
PLANTS = [st(S, "11", c, 6, 1, 2, kind="garden") for c in (11, 12, 13)] + [st(S, "11", 11, 10, 1, 2, kind="garden")]
NEWSSTAND = st(S, "11", 11, 8, 2, 2, kind="sign")
PHONE = st(S, "11", 14, 6, 1, 2, kind="sign")
GEAR_BOARD = st(S, "11", 8, 5, 3, 3, kind="counter")
BARRELS_W = [st(S, "8", 3, 12, 1, 1, kind="barrel"), st(S, "8", 3, 13, 1, 1, kind="barrel"),
             st(S, "8", 7, 13, 1, 1, kind="barrel")]
WATER_BARREL = st(S, "8", 10, 13, 1, 1, kind="barrel")
CRATES_W = [st(S, "8", 11, 12, 1, 2, kind="crate"), st(S, "8", 12, 13, 1, 1, kind="crate")]
CISTERN = st(S, "8", 8, 12, 2, 2, kind="well")
FENCE = st(S, "8", 4, 12, 4, 1, kind="fence")
TOOLS = [st(S, "8", 5, 13, 1, 1, kind="crate"), st(S, "8", 6, 13, 1, 1, kind="crate")]
PLOT = st(S, "8", 3, 4, 5, 4, kind="garden")
VEG = st("town", "3", 12, 4, 4, 2, kind="garden", solid=2)
PLOT_IRR = st(S, "8", 0, 8, 8, 4, kind="garden")
BOAT = st(S, "1", 4, 10, 3, 2, kind="boat")
TUG = st(S, "1", 4, 12, 3, 2, kind="boat")
STEAMCAR = st(S, "1", 8, 8, 3, 2, kind="cart")
COACH = st(S, "1", 11, 8, 3, 2, kind="cart")

# factory ruins
SCRAP = [st(F, "4", c, 0, 2, 2, kind="rubble") for c in (0, 2, 4)] + [st(F, "4", c, 2, 2, 2, kind="rubble") for c in (8, 10)]
CRATES_F = [st(F, "4", 0, 2, 2, 2, kind="crate"), st(F, "4", 2, 2, 2, 2, kind="crate"), st(F, "4", 4, 2, 2, 2, kind="crate"),
            st(F, "4", 6, 0, 2, 2, kind="crate")]
PALLET = st(F, "4", 6, 2, 2, 2, kind="crate")
DRUMS = st(F, "4", 10, 12, 2, 2, kind="barrel")
TOOLCHEST = st(F, "4", 8, 12, 2, 2, kind="crate")
CABLE = [st(F, "4", 2, 6, 2, 2, kind="crate"), st(F, "4", 6, 6, 2, 2, kind="crate")]
RUBBLE = [st(F, "4", c, 10, 2, 2, kind="rubble") for c in (8, 10, 12)] + [st(F, "3", 10, 10, 2, 2, kind="rubble"),
          st(F, "3", 8, 10, 2, 2, kind="rubble"), st(F, "3", 4, 12, 2, 2, kind="rubble")]
RUBBLE_S = [st(F, "3", 12, 10, 1, 1, kind="rubble"), st(F, "3", 13, 10, 1, 1, kind="rubble"), st(F, "3", 14, 7, 1, 1, kind="rubble")]
BRICK_RUIN = st(F, "3", 6, 8, 4, 2, kind="rubble")
IRON_GATE = st(F, "3", 0, 0, 4, 2, kind="gate")
BROKEN_GATE = st(F, "3", 0, 2, 4, 2, kind="gate")
BRICK_WALL = st(F, "3", 8, 6, 2, 2, kind="wall", flat=True, solid=0)
VPIPE = st(S, "5", 15, 8, 1, 4, kind="pipe", solid=4)
IBEAM = [st(F, "4", 14, 0, 1, 2, kind="pillar"), st(F, "4", 15, 0, 1, 2, kind="pillar")]
PRESSES = [st(F, "2", 8, 4, 2, 2, kind="machine"), st(F, "2", 10, 4, 2, 2, kind="machine")]
CONVEYOR = [st(F, "2", 0, 0, 2, 2, kind="machine"), st(F, "2", 4, 0, 2, 2, kind="machine")]
ANVIL = st("town", "10", 2, 0, 2, 2, kind="anvil")
FORGE = st("town", "10", 0, 0, 2, 2, kind="anvil")
ENGINE = st(S, "2", 14, 14, 2, 2, kind="machine")
ENGINE2 = st(S, "2", 14, 12, 2, 2, kind="machine")
SCAFFOLD = st(F, "3", 8, 2, 4, 4, kind="block", solid=0, base=5 * 48 + 2)
SHUTTER = st(F, "3", 4, 0, 2, 2, kind="wall")
BARREL_OIL = [st(F, "3", 4, 14, 1, 1, kind="barrel"), st(F, "3", 5, 14, 1, 1, kind="barrel")]
SHELVES_F = st(F, "4", 10, 0, 2, 2, kind="shelf")

# medieval town (neutral set)
BARREL_T = st("town", "2", 3, 6, 1, 2, kind="barrel")
BARRELS_T = st("town", "2", 6, 10, 2, 2, kind="barrel")
SACKS = st("town", "7", 4, 12, 2, 2, kind="crate")
POTS = [st("town", "7", c, 12, 1, 2, kind="barrel") for c in (0, 1, 2)]
BIG_BARREL = st("town", "7", 12, 12, 2, 2, kind="barrel")
NOTICE = st("town", "2", 14, 6, 2, 2, kind="sign")
SIGNPOST = st("town", "2", 12, 6, 1, 2, kind="sign")
INN_SIGN = st("town", "6", 4, 0, 2, 2, solid=0)
FIREWOOD = st("town", "6", 4, 5, 1, 1, kind="crate")
DEAD_TREES = [st("forest", "2", c, 7, 2, 3, cols=(1, 1), kind="tree") for c in (0, 2, 4, 6, 8)]
BUSHES = K.BUSHES
TUFTS = K.GRASS_TUFTS


# ------------------------------------------------------------------ checks
SOLID_ALL = set(kit.SOLID_KINDS) | {"wheel", "gear", "pipe_tall", "vent", "block", "tree2"}


def _rng(s):
    if ".." in s:
        a, b = s.split("..")
        return int(a), int(b)
    return int(s), int(s)


def reach(m):
    """Reachability over the Map's kind grid for its entity lines, once as drawn and once with every tileset_over
    applied. Returns a list of problem strings (empty = fine)."""
    ents = [line.split() for line in m.ents]
    probs = []
    for apply_over in (False, True):
        g = [row[:] for row in m.kind]
        if apply_over:
            for t in ents:
                if t[0] == "tileset_over":
                    x1, x2 = _rng(t[1])
                    y1, y2 = _rng(t[2])
                    for yy in range(y1, y2 + 1):
                        for xx in range(x1, x2 + 1):
                            g[yy][xx] = t[3]
        blockers = set()
        for t in ents:
            if t[0] in ("npc", "chest", "save", "switch", "shop", "inn"):
                i = 2 if t[0] in ("npc", "switch", "chest") else 1
                blockers.add((int(t[i]), int(t[i + 1])))

        def bl(x, y):
            return not (0 <= x < m.w and 0 <= y < m.h) or g[y][x] in SOLID_ALL or g[y][x] is None or (x, y) in blockers
        spawns = [(int(t[2]), int(t[3])) for t in ents if t[0] == "spawn"]
        exits = [t for t in ents if t[0] in ("door", "exit")]
        for s0 in spawns:                                   # strict: every spawn reaches every exit and door
            sn = {s0}
            q = deque([s0])
            while q:
                x, y = q.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (x + dx, y + dy)
                    if n not in sn and not bl(*n):
                        sn.add(n)
                        q.append(n)
            for t in exits:
                x1, x2 = _rng(t[1])
                y1, y2 = _rng(t[2])
                if not any((x, y) in sn for x in range(x1, x2 + 1) for y in range(y1, y2 + 1)):
                    probs.append("spawn %s cannot reach %s over=%s" % (s0, " ".join(t[:4]), apply_over))
        seen = set()
        q = deque()
        for s in spawns:
            if bl(*s):
                probs.append("spawn blocked %s over=%s" % (s, apply_over))
            seen.add(s)
            q.append(s)
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in seen and not bl(*n):
                    seen.add(n)
                    q.append(n)
        for t in ents:
            if t[0] in ("door", "exit", "trigger"):
                x1, x2 = _rng(t[1])
                y1, y2 = _rng(t[2])
                pts = [(x, y) for x in range(x1, x2 + 1) for y in range(y1, y2 + 1)]
                if not any(p in seen for p in pts):
                    probs.append("unreachable %s over=%s" % (" ".join(t[:4]), apply_over))
                if t[0] == "door" and g[y1][x1] != "door":
                    probs.append("door not on a door cell %s" % " ".join(t[:4]))
            elif t[0] in ("npc", "chest", "switch", "save", "shop", "inn", "sign", "read"):
                i = 2 if t[0] in ("npc", "switch", "chest") else 1
                x, y = int(t[i]), int(t[i + 1])
                if t[0] == "npc" and not apply_over and g[y][x] in SOLID_ALL:
                    probs.append("npc on solid cell %s %s" % (t[1], (x, y)))
                if not any((x + dx, y + dy) in seen for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    probs.append("unreachable %s over=%s" % (" ".join(t[:4]), apply_over))
    return probs


def coverage(mid):
    """Detail coverage of the saved map art: share of 48px cells that are not one of the 16 most repeated cells."""
    import preview
    img = preview.preview(mid).convert("RGB")
    W, H = img.width // C, img.height // C
    keys = []
    for y in range(H):
        for x in range(W):
            keys.append(img.crop((x * C, y * C, x * C + C, y * C + C)).tobytes())
    cnt = Counter(keys)
    top = sum(n for _, n in cnt.most_common(16))
    return 1 - top / len(keys)
