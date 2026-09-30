"""Cinderwake (T03) - hand-made maps for the Cinder Reach industrial town (group "cinder").

Shape: terraced axis / vertical city (layout standard section 4). Three terraces step up toward the Furnace Spine,
joined by paired stairs. The town's cooling channel runs down the middle of the axis in a stone race, falls over each
retaining wall and ends in the lower sluice basin above the canal bridge (the south entrance). The landmark at the top
of the axis is the Regulator Works, the gear hall the channel issues from; the Spine gate closes the top terrace to the
east, the garden lane leaves it to the west.
T03_TOWN is the working town (regulators lit, steam everywhere). T03_POST (Shared Heat) keeps the plan after the fault:
regulators dark, a waterwheel on every terrace of the race, the canteen roof fallen in with its kitchen moved into the
street, the west retaining wall collapsed into a rubble ramp by the tally wall, the garden lane blocked, the works
scaffolded for repair and a warm-shelter counter at the clinic.
T03_GARDEN: the Old Cooling Garden west of town, beds over the old channel. T03_YARD: the Old Assembly Yard (slipway
over the three cooling channels, valves on the north wall) east of the post-fault town."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Map, write_group, Stamp, C, st
import lib_cinder as L


def comp(m, x, y, rows, solid=2, door=None, kind="house", cols=None):
    """Compose a building from rows of building sprites: rows = [(key, src_row), ...] top to bottom (same width).
    All rows share the building's base line. Returns the bottom row."""
    n = len(rows)
    w = 1
    for i, (key, ro) in enumerate(rows):
        al, sh, c, r, w, h = L.B[key]
        s = Stamp(al, sh, c, r + ro, w, 1, solid=0, base=(n - i) * C)
        m.place(s, x, y + i)
    c0, c1 = cols if cols else (0, w - 1)
    for rr in range(n - solid, n):
        for cc in range(c0, c1 + 1):
            m.solid(x + cc, y + rr, kind)
    if door:
        m.solid(x + door[0], y + door[1], "door")
    return y + n - 1


def R(key, *rows):
    return [(key, r) for r in rows]


def block(m, x0, y0, x1, y1, kind="wall"):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            m.solid(x, y, kind)


def rail(m, y, xs):
    for i, x in enumerate(xs):
        m.place(L.RAIL[(x * 3 + y) % len(L.RAIL)], x, y)


def put(m, items):
    for (s, x, y) in items:
        m.place(s, x, y)


# =====================================================================================================================
# Cinderwake (shared street plan of T03_TOWN and T03_POST)
# =====================================================================================================================
CH_X = (21, 22)          # cooling channel columns


def cinderwake(m, post):
    rng = m.rng
    m.use(**L.MATS)
    m.fill("cob2" if post else "cob")
    # --------------------------------------------------------------- ground
    m.rect("soot", 0, 0, 43, 3)                                         # behind the Spine works
    m.rect("plates", 0, 4, 43, 4, kind="wall")
    m.rect("plates", 27, 5, 43, 9)                                      # pipe yard below the Spine
    m.rect("plates", 27, 13, 43, 19)                                    # workshop yard (middle east)
    m.blob("cobwarm", 10, 18.5, 5, 1.6)                                # shop street
    m.blob("cobwarm", 9, 27, 6, 1.8)                                   # canteen street
    m.blob("cobwarm", 21.5, 14.5, 5.5, 2.2)                            # middle landing around the race
    m.blob("cobwarm", 21.5, 27.5, 5, 1.6)                              # sluice square
    m.blob("cobwarm", 9, 7, 6, 1.4)
    m.blob("dirt", 3, 9, 2.5, 1.3)
    m.blob("dirt", 14, 9, 2.2, 1.0)
    m.blob("dirt", 3, 18.5, 1.6, 1.0)
    m.blob("dirt", 39.5, 18.5, 1.8, 1.0)
    m.blob("dirt", 2.5, 28, 2.0, 1.0)
    m.blob("dirt", 41, 28, 2.0, 1.0)
    m.blob("dirt", 33, 23, 2.2, 1.2)
    if post:
        m.blob("cracked", 12, 24, 3, 1.6, rough=0.5)
        m.blob("cracked", 33, 8, 3, 1.5, rough=0.5)
        m.blob("dirt", 6, 22.5, 2.5, 1.5)
        m.blob("cracked", 30, 17, 2.5, 1.5)
        m.blob("dirt", 3, 7, 2, 1.2)
    else:
        m.blob("dirt", 2, 7, 2.2, 1.1)                                   # the garden lane
    # --------------------------------------------------------------- retaining walls, stairs, channel
    stairs_top = (17, 18, 19, 24, 25, 26)
    stairs_mid = (17, 18, 19, 24, 25, 26, 33, 34, 35) + ((5, 6, 7) if post else ())
    L.wall_face(m, 11, 0, 43, rng, skip=stairs_top + CH_X)
    L.wall_face(m, 20, 0, 43, rng, skip=stairs_mid + CH_X)
    for x in stairs_top:
        m.rect("stairs", x, 11, x, 12)
    for x in stairs_mid:
        if post and x in (5, 6, 7):
            m.rect("cracked", x, 20, x, 21)
        else:
            m.rect("stairs", x, 20, x, 21)
    if post:                                                            # the collapsed wall: rubble on both sides
        put(m, [(L.RUBBLE_S[0], 4, 20), (L.RUBBLE_S[1], 8, 21), (L.RUBBLE[5], 3, 20)])
    # the race: out of the Regulator Works arch (row 7) down to the lower sluice basin (rows 25-27)
    for x in CH_X:
        m.rect("water", x, 7, x, 27)
    m.rect("water", 20, 25, 20, 27)
    m.rect("grate", 20, 28, 23, 28)                                     # culvert grate to the canal
    for by in (10, 17, 23):
        m.rect("deck", 21, by, 22, by, kind="bridge")
    # the canal along the south edge and the town bridge (exit 19..24)
    m.rect("water", 0, 30, 43, 31)
    m.rect("deck", 19, 30, 24, 31, kind="bridge")
    skip = {(x, y) for x in range(19, 25) for y in range(30, 32)}
    skip |= {(x, y) for x in CH_X for y in (10, 11, 12, 17, 20, 21, 23)}
    m.water_anims(skip=skip)
    for x in CH_X:
        L.waterfall(m, x, 11)
        L.waterfall(m, x, 20)
    # --------------------------------------------------------------- top terrace: the Spine works, the Regulator Works
    if post:
        comp(m, 2, 2, R("works_red", 2, 2, 3))                           # gutted by the fault
        put(m, [(L.RUBBLE[2], 2, 1), (L.RUBBLE[0], 4, 1)])
    else:
        comp(m, 2, 0, R("works_red", 0, 1, 2, 2, 3))
    comp(m, 6, 0, R("t_chimney", 0, 1, 1, 2, 3))
    comp(m, 8, 0, R("brick_hall", 0, 1, 1, 2, 3))
    comp(m, 12, 0, R("t_clock", 0, 1, 2, 2, 3))
    comp(m, 14, 0, R("t_dome", 0, 1, 2, 2, 3))
    comp(m, 17, 1, R("t_gear", 0, 1, 1, 2, 2, 3), solid=3)
    comp(m, 20, 1, R("gearhall", 0, 1, 1, 2, 2, 3), solid=4)
    comp(m, 24, 1, R("t_tank", 0, 1, 1, 2, 2, 3), solid=3)
    comp(m, 27, 0, R("furnace", 0, 1, 2, 2, 3))
    comp(m, 31, 0, R("dome_store", 0, 1, 2, 2, 3))
    comp(m, 35, 0, R("factory_l", 0, 1, 2, 2, 3))
    comp(m, 39, 0, R("t_stacks", 0, 1, 2, 2, 3))
    comp(m, 42, 0, R("narrow", 0, 1, 2, 2, 3))
    for (x, y, dx) in ((6, -1, 0), (40, -1, 0), (41, -1, 6)):
        L.smoke(m, x, y, dx=dx)
    if not post:
        for (x, y, dx) in ((28, -1, 0), (18, 0, 0), (25, 0, 12), (9, -1, 0)):
            L.smoke(m, x, y, dx=dx)
    # west: the garden lane (x0, rows 6-8), framed by boilers; post: blocked by the collapse
    block(m, 0, 4, 1, 5)
    block(m, 0, 9, 1, 10)
    put(m, [(L.BOILER_BIG, 0, 3), (L.COPPER_TANK, 1, 3), (L.CRATES_F[0], 0, 9)])
    if post:
        put(m, [(L.RUBBLE[0], 0, 6), (L.RUBBLE[3], 0, 7), (L.RUBBLE_S[2], 2, 8)])
        block(m, 0, 6, 1, 8, "rubble")
    else:
        put(m, [(L.SIGNPOST, 3, 4)])
    # regulator stack beside the landmark: lit before the fault, dark after
    put(m, [(L.TANKS if post else L.STOVE, 18, 7), (L.GAUGE, 17, 7)])
    put(m, [(L.PANEL if not post else L.TWIN_BOIL, 25, 7)])
    put(m, [(L.LAMP_GAS2, 23, 7)] + ([] if post else [(L.LAMP_GAS, 20, 7)]))
    # west half (elder 12,8)
    put(m, [(L.SACKS, 4, 4), (L.BARREL_T, 6, 4), (L.CRATES[1], 7, 5), (L.BENCH_IRON, 9, 5), (L.NEWSSTAND, 11, 4),
            (L.PLANTS[0], 13, 4), (L.PLANTS[1], 14, 4), (L.CRATES[2], 15, 5), (L.PHONE, 16, 4)])
    rail(m, 10, [2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 14, 15])
    put(m, [(L.LAMP_S[0], 6, 9), (L.LAMP_S[1], 11, 9), (L.LAMP_GAS, 16, 8), (L.LAMP_GAS2, 27, 8)])
    put(m, [(L.TANKS, 2, 8), (L.BARRELS_W[0], 4, 9), (L.CRATES[3], 8, 9), (L.BARRELS_W[1], 9, 9),
            (L.CRATES_W[1], 13, 9), (L.WATER_BARREL, 14, 9), (L.CRATES[4], 15, 9)])
    # east: pipe yard (pipefitter 28,8; foreman 38,7) and the Spine gate (x43 rows 5-7)
    put(m, [(L.PIPES_COPPER, 29, 5), (L.PIPES_STEEL, 32, 5), (L.PIPES_COPPER, 35, 5), (L.BOILER_S, 38, 4),
            (L.GAUGE, 39, 4), (L.STEAM_VENT, 27, 4)])
    if not post:
        m.anim("chimney_smoke", 27, 2, h=96)
    put(m, [(L.WORKBENCH, 29, 7), (L.TOOLSHELF, 31, 8), (L.CRATES_F[1], 33, 8), (L.DRUMS, 35, 8), (L.VALVE, 39, 9),
            (L.GEAR_S[0], 32, 9)])
    rail(m, 10, [28, 29, 30, 31, 32, 33, 34, 35, 36, 38, 39, 40])
    put(m, [(L.LAMP_S[2], 37, 9)])
    m.rect("grate2", 40, 5, 43, 7)
    block(m, 41, 8, 43, 10)
    put(m, [(L.BOILER_RED, 41, 8), (L.LAMP_POST, 41, 2), (L.CRATES[0], 43, 9)])
    # --------------------------------------------------------------- middle terrace
    comp(m, 0, 12, R("clock_hall", 0, 1, 2, 2, 3))
    block(m, 0, 17, 1, 19)
    put(m, [(L.CRATES_F[0], 0, 18), (L.TWIN_BOIL, 2, 13), (L.CRATES[0], 4, 14), (L.BARREL_T, 2, 16), (L.CRATES[1], 3, 17),
            (L.VENT, 4, 13)])
    # the Regulator Shop (door 8,17): brick upper floor over the storefront; post: shuttered, goods to the canteen
    comp(m, 6, 12, R("brick_long", 0, 1) + R("store_front", 0, 1, 2), door=None if post else (2, 5))
    put(m, [(L.LAMP_SIGN, 10, 16), (L.CRATES[2], 5, 17)])
    if post:
        put(m, [(L.CRATES_F[2], 7, 16)])
        m.solid(8, 17, "house")
    put(m, [(L.RED_TANK, 10, 13)])
    if post:
        comp(m, 11, 12, R("green_works", 0, 1, 2, 2, 3))
        put(m, [(L.PALLET, 11, 15), (L.CABLE[0], 13, 15)])
    else:
        comp(m, 11, 12, R("green_works", 0, 1, 2, 2, 3))
    put(m, [(L.PIPE_MACHINE, 15, 13), (L.CRATES_F[3], 15, 16)])
    rail(m, 19, [10, 11, 12, 13, 14, 15])
    put(m, [(L.LAMP_S[3], 16, 15)])
    # the race: sluice valves at the lips, lamps at the fall
    put(m, [(L.LAMP_GAS2, 23, 12), (L.GAUGE, 20, 18), (L.RED_TANK if not post else L.GAUGE, 23, 18)] + ([] if post else [(L.LAMP_GAS, 20, 12)]))
    # east workshops (worker_t2 33,17; child_p 27,17) and the clinic
    comp(m, 28, 12, R("blue_works", 0, 1, 2, 2, 3))
    comp(m, 32, 12, R("t_pipes" if post else "t_beacon", 0, 1, 2, 3))
    comp(m, 35, 12, R("big_hall", 0, 1, 2, 2, 3))
    comp(m, 39, 12, R("t_frame", 0, 1, 2, 3))
    comp(m, 42, 12, R("narrow", 0, 1, 2, 2, 3))
    block(m, 41, 17, 43, 19)
    put(m, [(L.BOILER_BIG, 41, 16), (L.COPPER_TANK, 40, 16), (L.CRATES[3], 27, 13), (L.GEAR_S[1], 27, 14)])
    put(m, [(L.WORKBENCH, 29, 17), (L.CRATES[4], 31, 18), (L.DRUMS, 37, 17), (L.BARREL_OIL[1], 39, 19),
            (L.LAMP_S[0], 32, 17), (L.LAMP_S[1], 36, 17)])
    rail(m, 19, [27, 28, 29, 30, 36, 37, 38])
    # --------------------------------------------------------------- bottom terrace
    comp(m, 0, 21, R("silo", 0, 1, 2, 2, 3), solid=5)
    block(m, 0, 26, 1, 29)
    put(m, [(L.CRATES_F[2], 0, 26), (L.BARRELS_T, 2, 27), (L.CRATES[0], 2, 22), (L.BARREL_T, 3, 22)])
    if post:
        put(m, [(L.RUBBLE[1], 2, 24)])
    # the Shift Canteen (door 7,26); post: roof fallen in, kitchen moved into the street
    if post:
        comp(m, 5, 23, R("brick_hall", 2, 2, 3))
        put(m, [(L.RUBBLE_S[0], 8, 22), (L.CRATES[1], 6, 27)])
        # the fallen roof lies across the shell
        m.place(Stamp("factory", "3", 6, 8, 4, 2, solid=0, base=4 * C + 1), 5, 22)
        m.solid(7, 25, "house")
    else:
        comp(m, 5, 21, R("brick_hall", 0, 1, 1, 2, 2, 3), door=(2, 5))
        put(m, [(L.LAMP_SIGN, 4, 25), (L.BARRELS_W[2], 8, 27)])
    comp(m, 9, 21, R("t_chimney", 0, 1, 2, 3))
    put(m, [(st("steam", "11", 12, 12, 3, 2, kind="machine", solid=1), 11, 24), (L.FIREWOOD, 14, 25),
            (L.BARREL_T, 14, 22), (L.POTS[1], 15, 23), (L.CRATES_W[0], 16, 23)])
    if not post:
        L.smoke(m, 9, 19)
        L.smoke(m, 12, 22, dx=-6)
        put(m, [(L.BENCH, 11, 26), (L.BENCH_S, 13, 26)])
    else:
        L.smoke(m, 12, 22, dx=-6)
    # the lower sluice: in the town, a lock gate at the basin mouth; lamps at the bridge heads
    put(m, [(L.LAMP_GAS, 17, 26), (L.LAMP_GAS2, 25, 26), (L.RED_TANK, 19, 24)])
    # east: bunkhouse, the clinic annex
    comp(m, 27, 21, R("twin_house", 0, 1, 2, 2, 3))
    comp(m, 37, 21, R("stone_house", 0, 1, 2, 2, 3))
    comp(m, 41, 21, R("clock2", 0, 1, 2, 2, 3), solid=5)
    block(m, 42, 26, 43, 29)
    put(m, [(L.CRATES[4], 31, 24), (L.BARRELS_W[1], 31, 25), (L.BARREL_T, 36, 23), (L.CRATES_F[3], 42, 26),
            (L.CRATES_W[1], 35, 24)])
    # quay (row 29) and canal side
    put(m, [(L.CRATES[0], 4, 29), (L.BARRELS_W[0], 11, 29), (L.CRATES[2], 14, 29), (L.CRATES[3], 27, 29),
            (L.BARRELS_W[1], 30, 29), (L.CRATES_W[1], 39, 29), (L.LAMP_S[2], 15, 28), (L.LAMP_S[3], 27, 27)])
    # boats moored on the canal
    put(m, [(L.TUG, 4, 30), (L.BOAT, 31, 30)])
    # middle landing: benches and the shift clock by the race
    put(m, [(L.BENCH_S, 17, 16), (L.BENCH_S, 26, 16), (L.CLOCK_POST, 26, 13)])
    if not post:
        # the lower plaza market (bunkhouse side)
        put(m, [(L.STALLS[0], 31, 26), (L.CART_STALL, 33, 26), (L.NOTICE, 13, 27), (L.CRATES[1], 16, 26)])
    put(m, [(L.BENCH_CLOCK2, 28, 27), (L.BARREL_OIL[0], 26, 22), (L.CRATES[0], 23, 24)])
    return m


def town():
    m = Map("T03_TOWN", 44, 32, "Cinderwake", "town_r02", music="M012", zone="T03", location="L_T03", region="R02",
            group="cinder", seed=303)
    cinderwake(m, post=False)
    for e in """tileset_over 20..22 26..27 wheel if=ch:CH04
spawn world 21 29 up
spawn from_canteen 7 27 down
spawn from_shop 8 18 down
spawn from_garden 3 7 right
spawn from_spine 40 6 left
spawn default 21 29 up
exit 19..24 31 WORLD l_t03
door 7 26 T03_CANTEEN entry sfx=FX008
door 8 17 T03_SHOP entry sfx=FX008
exit 0 6..8 T03_GARDEN from_town
exit 43 5..7 D04_R01 from_town if=event:T03_IVO_SHOP locked="A foreman: 'Spine's closed to visitors. Talk to Quill at the regulator shop.'"
npc worker_t1 18 27 up sprite=worker talk=T03_CLINIC
npc worker_t2 33 17 left sprite=worker talk=T03_HEAT
npc child_t 26 24 down sprite=child talk=T03_CHILD wander=1
npc foreman 38 7 left sprite=soldier talk=T03_FOREMAN
npc pipefitter 28 8 down sprite=worker talk=T03_PIPEFITTER
npc elder_t 12 8 right sprite=elder talk=T03_ELDER""".split("\n"):
        m.ent(e)
    return m


def post():
    m = Map("T03_POST", 44, 32, "Cinderwake - Shared Heat", "town_r02", music="M012", zone="T03", location="L_T03",
            region="R02", group="cinder", seed=304, save=True, phase="post")
    cinderwake(m, post=True)
    for (x, y) in ((20, 7), (20, 13), (20, 25)):                       # a waterwheel on every terrace
        m.place(L.GEAR_WHEEL, x, y)
    # fault damage: the brick hall above the garden lane is down to its ground floor, the works are scaffolded,
    # brick falls and scrap heaps in the streets
    put(m, [(L.SCAFFOLD, 28, 12), (L.RUBBLE[5], 31, 26), (L.RUBBLE[4], 2, 6), (L.RUBBLE_S[1], 30, 9),
            (L.RUBBLE_S[2], 24, 28), (L.RUBBLE_S[0], 4, 18), (L.RUBBLE_S[2], 34, 24)])
    put(m, [(L.STALL_S[0], 8, 27), (L.STALL_S[1], 36, 26), (L.STOVE, 10, 26)])
    for e in """spawn world 21 29 up
spawn from_yard 40 6 left
spawn default 21 29 up
exit 19..24 31 WORLD_POST l_t03
exit 43 5..7 T03_YARD from_town if=ch:CH15 locked="A crew chief: 'Yard's Quill's business. And Quill says he's waiting for someone who can light a lamp without burning down the street.'"
npc pell_p 18 24 up sprite=pell talk=T03P_PELL
npc rota 12 27 up sprite=worker talk=T03P_ROTA
npc clinic_n 34 20 up sprite=monk talk=T03P_CLINIC
npc tally 6 21 right sprite=worker talk=T03P_TALLY
npc child_p 27 17 left sprite=child talk=T03P_CHILD wander=1
npc wheelwright 24 8 down sprite=worker talk=T03P_WHEEL
npc cook_p 9 27 up sprite=baker talk=T03P_CANTEEN
shop 8 28 SHOP_T03
inn 36 27 scene=T03P_INN
npc inn_p 37 27 left sprite=keeper talk=T03P_INN
save 16 28""".split("\n"):
        m.ent(e)
    return m


# =====================================================================================================================
# T03_GARDEN - the Old Cooling Garden (west of town)
# =====================================================================================================================
def garden():
    m = Map("T03_GARDEN", 32, 22, "Cinderwake - Old Cooling Garden", "town_r02", music="M012", zone="T03",
            location="L_T03", region="R02", group="cinder", seed=305)
    rng = m.rng
    m.use(**L.MATS)
    m.fill("moss")
    # north: the town's back wall with the valve house; row 0 dark
    m.rect("soot", 0, 0, 31, 0)
    L.wall_face(m, 1, 0, 31, rng)
    # upper bed terrace (x3-16 rows 3-7) on a brick retaining wall (rows 8-9), stairs at x15-16
    m.rect("dirt", 3, 7, 16, 7)
    L.wall_face(m, 8, 3, 14, rng)
    m.rect("stairs", 15, 8, 16, 9)
    m.place(L.PLOT_IRR, 4, 3)
    block(m, 4, 3, 11, 6, "garden")
    comp(m, 13, 2, R("shed", 0, 1, 2, 3), solid=2)
    put(m, [(L.BARRELS_W[0], 12, 5), (L.WATER_BARREL, 12, 6), (L.TOOLS[0], 15, 5), (L.TOOLS[1], 16, 5),
            (L.CRATES_W[1], 3, 6), (L.PLANTS[0], 3, 3), (L.LAMP_S[0], 17, 6)])
    # the valve house on the old channel's bypass (switch 23,7) and the water tower
    comp(m, 22, 2, R("t_tank", 0, 1, 2, 2, 3), solid=3)
    comp(m, 19, 2, R("watertower", 0, 1, 2, 2, 3), solid=2)
    m.place(L.VALVE, 23, 7)
    put(m, [(L.GAUGE, 25, 6), (L.PIPES_COPPER, 25, 4), (L.BOILER_S, 18, 5), (L.CRATES[1], 21, 7)])
    comp(m, 29, 1, R("silo", 0, 1, 1, 2, 2, 2, 3), solid=4)
    block(m, 29, 3, 31, 8)
    # east: the lane back to town (exit x31 rows 9-11)
    m.blob("dirt", 27, 10, 4.5, 1.3)
    m.rect("cob", 28, 9, 31, 11)
    put(m, [(L.LAMP_GAS, 28, 6), (L.LAMP_GAS2, 28, 12)])
    block(m, 29, 12, 31, 21)
    comp(m, 30, 12, R("t_chimney", 0, 1, 2, 3))
    # the old cooling channel (rows 15-16), entering the town culvert at the lock gate
    m.rect("water", 3, 15, 28, 16)
    m.place(L.LOCK_GATE, 25, 15)
    for bx in (8, 19):
        m.rect("deck", bx, 15, bx + 1, 16, kind="bridge")
    m.water_anims(skip={(x, y) for x in range(25, 29) for y in (15, 16)})
    # the cooling pond (centrepiece) and its benches
    m.blob("pond", 15, 11, 2.6, 1.4, rough=0.25)
    for y in range(9, 14):
        for x in range(12, 19):
            if m.mat[y][x] == "pond":
                m.anim("water_deep", x, y, h=48, flat=True)
    put(m, [(L.BENCH_S, 3, 14), (L.PLANTS[1], 18, 11), (L.PLANTS[2], 11, 10)])
    # beds on the east lawn and the dead winter plot
    m.place(L.PLOT, 20, 10)
    block(m, 20, 10, 24, 13, "garden")
    put(m, [(L.CISTERN, 25, 12), (L.BARRELS_W[1], 25, 11)])
    # exposed pipes across the lawn (the heat that no longer runs)
    put(m, [(L.PIPES_STEEL, 2, 17), (L.MANHOLES[0], 8, 12)])
    for (x, y) in ((6, 11), (17, 8), (26, 13), (10, 7)):
        m.place(L.MANHOLES[(x + y) % 4], x, y)
    # west and south: autumn-scorched trees closing the garden
    trees = [(-1, 0), (0, 2), (-1, 4), (0, 6), (-1, 8), (0, 10), (-1, 12), (0, 14), (-1, 16)]
    trees += [(x, 18) for x in range(1, 29, 3)] + [(x, 19) for x in range(-1, 31, 3)]
    for (x, y) in trees:
        m.place(L.DEAD_TREES[(x * 7 + y * 3) % 5], x, y)
    put(m, [(L.VEG, 6, 13)])
    block(m, 0, 2, 1, 21, "tree")
    block(m, 0, 19, 31, 21, "tree")
    put(m, [(L.FENCE, 3, 17), (L.FENCE, 11, 17), (L.CRATES_W[0], 16, 17), (L.BARRELS_W[2], 21, 17)])
    for (ex, ey) in ((10, 12), (4, 11), (18, 8), (23, 7), (30, 10)):
        m.reserve_rect(ex - 1, ey - 1, ex + 1, ey + 1)
    m.reserve_rect(2, 10, 28, 10)                                        # the lane under the bed terrace
    m.reserve_rect(17, 8, 31, 9)
    m.reserve_rect(7, 14, 10, 17)
    m.reserve_rect(18, 14, 21, 17)
    m.reserve_rect(5, 17, 28, 17)
    m.reserve_rect(11, 13, 19, 14)
    m.reserve_rect(2, 10, 13, 12)
    m.scatter(L.TUFTS, 2, 3, 28, 18, 26, on=["moss"], gap=1)
    m.scatter(L.BUSHES, 2, 9, 28, 18, 8, on=["moss"], gap=1)
    for e in """spawn from_town 30 10 left
exit 31 9..11 T03_TOWN from_garden
npc gardener 10 12 up sprite=farmer talk=T03_GARDENER
npc pell_garden 18 8 down sprite=pell talk=T03_PELL_GARDEN if=ch:CH04
chest T03_C_GARDEN 4 11 I021 1
switch bypass 23 7 scene=CH10_CINDER_FIX if=ch:CH09,!flag:accord_cinder""".split("\n"):
        m.ent(e)
    return m


# =====================================================================================================================
# T03_YARD - the Old Assembly Yard (east of the post-fault town)
# =====================================================================================================================
def yard():
    m = Map("T03_YARD", 44, 30, "Cinderwake - Old Assembly Yard", "furnace", music="M012", zone="T03",
            location="L_T03", region="R02", group="cinder", seed=306, encounters="none", save=True, phase="post")
    rng = m.rng
    m.use(**L.MATS)
    m.fill("plates")
    # north wall with the three channel valves (switches 8,3 / 22,3 / 36,3)
    m.rect("soot", 0, 0, 43, 0)
    L.wall_face(m, 1, 0, 43, rng)
    for vx in (8, 22, 36):
        m.place(L.RED_TANK, vx, 2)
        m.place(L.VPIPE, vx, 4)
        m.rect("grate2", vx, 8, vx, 19 if vx != 22 else 9)          # the channel culverts, frosting when opened
    # side walls, entrance from the town (x0 rows 12-15)
    block(m, 0, 3, 1, 11)
    block(m, 0, 16, 1, 29)
    block(m, 42, 3, 43, 29)
    m.rect("cob", 0, 12, 5, 15)
    put(m, [(L.LAMP_GAS, 2, 9), (L.LAMP_GAS2, 2, 16)])
    # dark side borders lined with stacks and works
    m.rect("soot", 0, 3, 1, 11)
    m.rect("soot", 0, 16, 1, 29)
    m.rect("soot", 42, 3, 43, 29)
    put(m, [(L.COPPER_TANK, 2, 3), (L.BOILER_S, 3, 4), (L.COPPER_TANK, 2, 25),
            (L.BOILER_S, 41, 22), (L.COPPER_TANK, 41, 3), (L.RED_TANK, 41, 7)])
    # worn ground: a cobble lane from the town gate to the workshop, soot and scorch on the plates
    m.blob("cob", 5, 13.5, 4, 1.6)
    m.path("cob", [(6, 14), (12, 20), (18, 22)], width=2)
    for (bx, by, rx, ry) in ((27, 5, 3, 1.2), (10, 24, 3, 1.4), (33, 23, 3, 1.4), (6, 6, 2, 1.2)):
        m.blob("cracked", bx, by, rx, ry, rough=0.4)
    # the slipway: timber deck with launch rails between steel ways, over the middle channel
    m.rect("grate", 14, 8, 34, 18)
    m.rect("deck", 16, 10, 32, 16, kind="bridge")
    for ry in (11, 15):
        m.rails_h(ry, 16, 32, kind=None)
    for (x, y) in ((14, 8), (34, 8), (14, 18), (34, 18)):
        m.place(L.IBEAM[(x + y) % 2], x, y - 1)
    # chalk lines, grease and drains on the deck (flat: the slipway is walked on before and after the launch)
    for (x, y) in ((18, 12), (24, 13), (30, 12), (21, 14), (27, 10), (19, 16), (29, 16)):
        m.place(L.MANHOLES[(x + y) % 4] if (x + y) % 3 else L.GRILLE, x, y)
    # hull plates, chains and winch posts stacked on the steel ways around the deck
    put(m, [(L.CRATES_F[0], 14, 10), (L.DRUMS, 14, 14), (L.CABLE[1], 33, 11),
            (L.CRATES_F[3], 33, 14), (L.VALVE, 34, 16)])
    # cradle blocks and chocks along the ways (walkable deck stays clear between the rails)
    put(m, [(L.PALLET, 17, 8), (L.CRATES_F[1], 30, 8), (L.CABLE[0], 27, 8), (L.PIPES_STEEL, 19, 8),
            (L.PIPES_COPPER, 17, 17), (L.CRATES_F[2], 29, 17)])
    # the old roof's columns still standing across the yard
    for x in (4, 12, 30, 38):
        for y in (5, 25):
            if (x, y) not in ((4, 25),):
                m.place(L.IBEAM[(x // 4) % 2], x, y - 1)
    # north work floor: engines, presses and gear racks between the valves
    put(m, [(L.PRESSES[0], 10, 4), (L.PRESSES[1], 24, 4), (L.ENGINE, 28, 4), (L.ENGINE2, 14, 4), (L.CONTROL, 32, 4),
            (L.BIG_GEAR, 17, 4), (L.GEAR_S[0], 19, 5), (L.TOOLBENCH, 39, 4), (L.DRUMS, 5, 4), (L.CRATES[0], 40, 6)])
    # the Iron Tortoise's bay (tortoise 38,13): clear floor, scorch and a hoist frame
    m.blob("cracked", 38, 13, 3, 3, rough=0.3)
    put(m, [(L.PISTONS, 40, 10), (L.CONVEYOR[0], 39, 17), (L.GAUGE, 40, 13)])
    # more kit on the floors: the paddle wheel waiting for the hull, a tractor, a steam car, parts
    put(m, [(L.GEAR_WHEEL, 14, 19), (L.TRACTOR, 3, 17), (L.STEAMCAR, 11, 12), (L.PIPES_COPPER, 25, 19),
            (L.GEAR_BIG2, 32, 19), (L.TOOLBENCH, 33, 22), (L.CRATES_F[1], 35, 23), (L.CRATES[3], 3, 20),
            (L.BARRELS_W[2], 2, 22), (L.GEAR_S[1], 16, 22), (L.CRATES[4], 13, 23), (L.TWIN_BOIL, 22, 26),
            (L.PIPES_STEEL, 10, 19), (L.DRUMS, 28, 19), (L.ENGINE2, 37, 6), (L.CRATES_F[2], 3, 6)])
    # west floor by the entrance: the crews' kit
    put(m, [(L.CRATES_F[3], 6, 9), (L.CRATES[1], 10, 10), (L.BARRELS_W[0], 11, 10), (L.SACKS, 6, 16), (L.TOOLCHEST, 10, 16)])
    # south: scrap piles blocking the assembly space until cleared (rows 20: x6-9 and x36-39)
    for x in (6, 8, 36, 38):
        m.place(L.SCRAP[(x // 2) % len(L.SCRAP)], x, 19)
    # the workshop bench (read 24,23), forge and anvils; save by the west wall; chest in the east corner
    m.rect("deck", 18, 21, 30, 25, kind="floor")
    m.place(L.WORKBENCH, 23, 22)
    put(m, [(L.FORGE, 19, 21), (L.ANVIL, 29, 23), (L.TOOLSHELF, 21, 21), (L.CRATES[2], 26, 21)])
    m.anim("brazier", 17, 22, h=96)
    m.solid(17, 23, "brazier")
    put(m, [(L.SHELVES_F, 6, 26), (L.CRATES_F[0], 10, 26), (L.DRUMS, 14, 26),
            (L.ENGINE, 32, 26), (L.CRATES_F[2], 36, 26), (L.BARRELS_T, 39, 26)])
    block(m, 0, 28, 43, 29)
    m.rect("soot", 0, 28, 43, 29)
    L.wall_face(m, 28, 2, 41, rng)
    for (x, y) in ((6, -1), (30, -1)):
        L.smoke(m, x, y)
    for e in """tileset_over 16..32 10..16 floor2 if=ch:CH16
switch channel1 8 3 flag=t03y_ch1 scene=CH16_CHANNEL1
switch channel2 22 3 flag=t03y_ch2 scene=CH16_CHANNEL2
switch channel3 36 3 flag=t03y_ch3 scene=CH16_CHANNEL3
tileset_over 6..9 20 floor if=flag:t03y_clear
tileset_over 36..39 20 floor if=flag:t03y_clear
trigger 3..5 12..15 scene=CH16_YARD if=ch:CH15,!event:CH16_YARD
npc ivo_y 24 20 up sprite=C04 talk=CH16_IVO if=!ch:CH16
npc crew_y1 10 22 up sprite=worker talk=CH16_CREW if=flag:t03y_ch1,flag:t03y_ch2,flag:t03y_ch3,!flag:t03y_clear
npc tortoise 38 13 left sprite=tortoise talk=CH16_TORTOISE if=flag:t03y_clear,!flag:v06_given
npc pell_y 26 22 up sprite=pell talk=CH16_PELL if=flag:v06_given,!ch:CH16
read 24 23 "The workshop bench." scene=CH16_BENCH
chest T03Y_C1 40 24 W022 1
save 4 24
spawn from_town 1 13 right
spawn default 1 13 right
exit 0 12..15 T03_POST from_yard""".split("\n"):
        m.ent(e)
    return m


MAPS = [town, post, garden, yard]

if __name__ == "__main__":
    texts = []
    for f in MAPS:
        m = f()
        texts.append(m.save())
        probs = L.reach(m)
        print(m.id, "reach problems:", probs if probs else 0)
    print(write_group("cinder", texts))
