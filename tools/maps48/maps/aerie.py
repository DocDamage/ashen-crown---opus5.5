"""High Aerie (T05) and Nacre (T06) - hand-made 48px town maps (group "aerie").

High Aerie (Skyspine, town_r04): a cliff town hung on the mountain above open sky. Shape: valley spine / terraced
ledge (layout standard section 4) - the Skyspine rock closes the north edge, the town sits on two snow-paved
terraces joined by stone stairs, open sky on the other three sides; the road leaves south over a rope bridge and a
plank bridge leads east to the Wind Stair. Landmark on the axis: the Returners' Hall (north-west) and, pre-fall, the
cable engine house at the head of the stairs (post: three windmills). The memorial - a long wall of rune stones -
sits in front of the hall.

Nacre (Pale Basin, town_r05): ochre sandstone salt town of archivists and dragonborn families around the listening
pool. See the T06 functions for their notes."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Map, Mat, st, write_group
from skins.lib_cold import SNOW, SNOW_STONE, SKY, FROST_STONE, DRIFTS, ICE
from skins.lib_d import TintMat
import lib_r01 as T
import lib_aerie as L
from skins import common as K0


class K:
    RUBBLE_S = [K0.RUBBLE, K0.RUBBLE2]
    RUBBLE_B = K0.RUBBLE_BIG


def ents(m, text):
    for ln in text.strip("\n").split("\n"):
        m.ent(ln.strip())


# ============================================================================================ High Aerie
AMATS = dict(
    sky=SKY, snow=SNOW, court=SNOW_STONE, flags=FROST_STONE,
    planks=TintMat([("siege", "1", 192, 192, 192, 96)], "bridge", mul=(0.9, 0.9, 0.95)),
    rock=TintMat([("dungeon", "1", 576, 4, 160, 88)], "cliff", mul=(0.72, 0.78, 0.92), organic=True, prio=2),
    wallc=TintMat([("town", "6", 0, 672, 192, 96)], "wall", mul=(0.8, 0.85, 0.95)),
    stairs=Mat([("town", "6", 192, 384, 96, 96)], "stairs"),
    ice=ICE,
)


def face_row(m, B, y, x0, x1, kind, key="rock", skip=()):
    """Lay 4-wide flat face stamps (2 rows tall) from x0 to x1 on rows y, y+1; set their kind."""
    x = x0
    i = 0
    while x <= x1:
        w = min(4, x1 - x + 1)
        s = B["%s%d" % (key, i % 3)] if key != "rock_nosnow" else B[key]
        if w < 4:
            s = st(s.alias, s.sheet, 0, 0, px=(0, 0, w * 48, 96), solid=0, flat=True)
        m.place(s, x, y)
        i += 1
        x += 4
    for yy in (y, y + 1):
        for xx in range(x0, x1 + 1):
            if (xx, yy) not in skip:
                m.set(xx, yy, "rock" if kind == "cliff" else "wallc", kind)


def sprinkle(m, stamps, x0, y0, x1, y1, n, mats):
    """Decorate cells of the given materials (also solid ones such as rock faces) without touching collision."""
    done = 0
    for _ in range(n * 30):
        if done >= n:
            break
        s = m.rng.choice(stamps)
        x = m.rng.randint(x0, max(x0, x1 - s.w + 1))
        y = m.rng.randint(y0, max(y0, y1 - s.h + 1))
        if all(0 <= x + i < m.w and 0 <= y + j < m.h and m.mat[y + j][x + i] in mats for i in range(s.w) for j in range(s.h)):
            m.place(s, x, y, solid=0)
            done += 1


def smoke(m, stamp, x, y, frac):
    """Chimney smoke above a composed house placed at (x, y) whose chimney sits at `frac` of its width."""
    px = x * 48 + int(stamp.px[2] * frac) - 10
    py = y * 48 + 2 - 96
    m.anim("chimney_smoke", px // 48, py // 48, dx=px % 48, dy=py % 48)


def aerie_court(post=False):
    if post:
        m = Map("T05_POST", 44, 30, "High Aerie - Windmill Court", "town_r04", music="M014", zone="T05", location="L_T05",
                region="R04", phase="post", seed=502)
    else:
        m = Map("T05_COURT", 44, 30, "High Aerie - Cable Court", "town_r04", music="M014", zone="T05", location="L_T05",
                region="R04", seed=501)
    m.use(**AMATS)
    B = L.aerie_buildings()
    m.fill("sky")
    # --- the two terraces
    m.rect("court", 2, 3, 41, 16)
    m.rect("snow", 2, 19, 41, 25)
    # ragged sky edges west/east (never straight more than a few cells)
    for (x, y) in ((2, 3), (2, 4), (2, 8), (2, 9), (2, 14), (2, 15), (2, 16), (41, 5), (41, 6), (41, 15), (41, 16),
                   (2, 21), (2, 22), (41, 19), (41, 20), (41, 24), (41, 25), (2, 25), (3, 25)):
        m.set(x, y, "sky")
    for (x, y) in ((1, 11), (1, 12), (1, 5), (42, 7), (42, 8), (1, 23), (42, 22)):
        m.set(x, y, "snow")
    m.rect("snow", 2, 3, 41, 4)
    m.rect("snow", 3, 12, 4, 16)
    m.rect("snow", 38, 13, 41, 16)
    # paved streets on the upper court
    m.rect("flags", 3, 10, 41, 11)
    m.rect("flags", 17, 11, 22, 16)
    m.rect("flags", 7, 9, 9, 9)
    m.rect("flags", 25, 12, 33, 15)
    # lower terrace path from the stairs to the bridge and along the terrace
    m.rect("flags", 18, 19, 21, 25)
    m.rect("flags", 5, 23, 36, 24)
    m.rect("flags", 36, 19, 38, 22)
    # east plank bridge to the Wind Stair (collapsed after the fall)
    if not post:
        m.rect("planks", 41, 10, 43, 13)
    else:
        m.rect("planks", 41, 10, 41, 13)
    # south rope bridge
    m.rect("planks", 20, 26, 23, 29)
    # --- north: the Skyspine rock
    m.rect("snow", 0, 0, 43, 0, kind="cliff")
    face_row(m, B, 1, 0, 43, "cliff")
    # --- retaining wall between the terraces, stairs at 18-21 and 37-38 (post: a trader's kiosk at 26)
    skip = {(x, y) for x in (18, 19, 20, 21, 37, 38) for y in (17, 18)}
    face_row(m, B, 17, 2, 41, "wall", key="wallf", skip=skip)
    for x in (18, 20):
        m.place(L.STONE_STAIRS, x, 17)
    m.place(L.STONE_STAIRS2, 37, 17)
    m.rect("stairs", 18, 17, 21, 18)
    m.rect("stairs", 37, 17, 38, 18)
    if post:
        m.set(26, 18, "flags")
    # --- south cliff under the lower terrace
    face_row(m, B, 26, 2, 19, "cliff")
    face_row(m, B, 26, 24, 41, "cliff")
    for y in (26, 27, 28, 29):
        for x in (19, 24):
            m.set(x, y, "sky")
    # === buildings (upper terrace)
    m.place(B["hall"], 4, 1)                                   # Returners' Hall, door (8,9)  (rows 0..8 + door row)
    if not post:
        m.place(B["engine"], 13, 2)                            # cable engine house (rows 2..8)
    m.place(B["house0"], 24, 2)
    m.place(L.WATCHTOWER, 31, 4)
    m.place(B["house2"], 35, 3)
    # hall frontage: inn sign, lamps, benches, barrels
    m.place(L.INN_SIGN, 10, 8)
    m.place(L.TORCH_POST[0], 6, 8)
    m.place(L.BARRELS_V[0], 2, 8)
    m.place(L.FIREWOOD[0], 12, 7)
    # the memorial: a long wall of names (rune stones on a stone footing), read at (12,13)
    for i, x in enumerate((5, 7, 9, 11)):
        m.place(L.RUNESTONES[(i * 2 + 1) % 6], x, 12)
    m.place(L.BRAZIER_S, 4, 13)
    m.anim("brazier", 4, 12, h=96)
    if post:
        # the Returners' Wall: a clean stone beside the memorial (solid once the names are cut: tileset_over)
        m.place(st("roman", "4", 13, 0, 1, 3, kind="sign"), 14, 11)
        m.solid(14, 12, "sign")
        m.solid(14, 13, "sign")
    else:
        m.place(L.LANTERN_POST, 14, 12)
    # engine house / windmills
    if not post:
        m.place(L.DRUM, 14, 9)
        m.place(L.ROPES_6[0], 16, 8)
        m.place(L.BARRELS_6[0], 19, 8)
        m.place(L.CRATES_V[1], 21, 8)
        smoke(m, B["engine"], 13, 2, 0.2)
    else:
        mill = L.windmill()
        for i, x in enumerate((13, 17, 21)):
            m.place(mill[i % len(mill)], x, 4)
        m.place(L.ROPES_6[1], 25, 9)
        m.place(L.LOG_STACK, 12, 7)
        # the inn desk in front of the hall, the old engine footing, the broken east span
        m.place(L.DESK, 7, 10)
        for (x, y, r) in ((14, 8, 0), (16, 9, 1), (19, 8, 2), (41, 13, 0), (41, 9, 1)):
            m.place(K.RUBBLE_S[r % 2] if r < 2 else K.RUBBLE_B, x, y)
        m.place(L.ROPE[0], 40, 12)
    # house0 / tower / house2 frontage
    m.place(L.CRATES_V[0], 24, 8)
    m.place(L.SACKS_V[0], 28, 8)
    m.anim("flag_blue", 30, 7, h=96, solid=True)
    m.place(L.WEAPON_RACK[0], 35, 8)
    m.place(L.ARMOR_STAND[0], 37, 8)
    m.place(L.SPEAR_RACK, 39, 8)
    smoke(m, B["house0"], 24, 2, 0.25)
    smoke(m, B["house2"], 35, 3, 0.25)
    smoke(m, B["hall"], 4, 1, 0.72)
    # pines on the mountain shelf behind the roofs
    for x in (12, 21, 30, 33, 0):
        m.place(L.PINES[x % 3], x, -3)
    # north-east corner pines
    for (x, y) in ((40, 2), (38, -1), (1, 3)):
        m.place(L.PINES[(x + y) % 3], x, y)
    # plaza: fire bowl, benches, flags
    m.place(L.FIREBOWL, 28, 13)
    m.anim("brazier", 28, 12, dx=24, dy=4, h=96)
    m.place(L.BENCH_S, 25, 14)
    m.place(L.BENCH_S, 31, 14)
    m.anim("flag_blue", 26, 11, h=96, solid=True)
    m.anim("flag_blue", 33, 11, h=96, solid=True)
    # the traders' stall (shop at 22,15) with stock
    if not post:
        m.place(L.STALL_BLUE, 21, 14)
        m.place(L.BARRELS_6[1], 23, 14)
        m.place(L.SACKS_V[1], 15, 14)
    else:
        m.place(L.STALL_BLUE, 25, 16)
        m.solid(25, 17, "wall")
        m.place(L.CRATES_V[2], 27, 15)
    # west edge: pines and rocks along the drop
    for (x, y) in ((2, 11), (3, 13)):
        m.place(L.PINES[(x + y) % 3], x, y - 3)
    m.place(L.PINE_BIG, 2, 5)
    m.place(L.BOULDER, 3, 15)
    m.place(L.FIREWOOD[1], 12, 15)
    m.place(L.LOG_STACK, 15, 12)
    m.place(L.BARRELS_V[1], 38, 14)
    m.place(L.ROCKS_S[0], 40, 12)
    # === lower terrace
    m.place(B["cabin"], 3, 19)
    m.place(L.BENCH_S, 8, 19)
    m.place(L.FIREWOOD[2], 7, 21)
    m.place(L.TOTEMS[0], 12, 20)
    m.place(L.GRAVE[0], 13, 19)
    if not post:
        m.place(L.WINCH, 22, 19)                                # the cable post: winch, brake lever (switch 25,21)
        m.place(L.LEVERS[0], 25, 20)
        m.place(L.ROPE[0], 24, 19)
        m.place(L.ROPES_6[2], 26, 19)
        m.place(L.ANCHORS[0], 23, 22)
    else:
        m.place(L.ROPE[1], 22, 19)
        m.place(L.LOG_STACK, 23, 19)
        m.place(L.ANCHORS[1], 25, 20)
    m.place(L.BARRELS_6[2], 28, 19)
    m.place(L.CRATES_V[1], 31, 19)
    m.place(B["cabin2"], 38, 19)
    m.place(L.SACKS_V[0], 35, 19)
    for x in list(range(4, 18, 2)) + list(range(26, 40, 2)):
        m.place(L.FENCE_V[(x // 2) % 5], x, 25)
    m.place(L.CHAIN_POSTS[0], 19, 25)
    m.place(L.CHAIN_POSTS[1], 24, 25)
    m.anim("brazier", 17, 23, h=96, solid=True)
    m.anim("brazier", 25, 23, h=96, solid=True)
    # --- extra dressing: well and drying racks on the upper court, market canopy, lanterns, frozen puddles
    m.place(L.WELL_V, 8, 14)
    m.place(L.BUCKET, 10, 15)
    m.place(L.STUMP_AXE, 11, 14)
    m.place(L.LOGS[0], 13, 16)
    m.place(L.HIDE_RACK[0], 5, 15)
    m.place(L.POTS_V[0], 16, 13)
    m.place(L.TORCH_POST[1], 17, 13)
    m.place(L.TORCH_POST[0], 23, 13)
    m.place(L.CANOPY, 35, 14)
    m.place(L.BARRELS_6[3], 40, 13)
    m.place(L.ROPE[1], 34, 15)
    # against the retaining wall (lower side)
    m.place(L.CRATES_V[2], 14, 19)
    m.place(L.BARRELS_V[2], 16, 19)
    m.place(L.HIDE_RACK[1], 9, 21)
    m.place(L.ARROWS[1], 17, 21)
    m.place(L.LANTERN_POST, 32, 22)
    m.place(L.LANTERN_POST, 11, 22)
    m.place(L.SPIT, 32, 19)
    m.place(L.STOOLS[0], 34, 21)
    m.place(L.STOOLS[1], 30, 20)
    m.place(L.PINES[0], 39, 20)
    m.place(L.PINE_S[0], 2, 22)
    m.place(L.ROCKS_S[1], 36, 22)
    m.place(L.ROCKS_S[2], 13, 22)
    m.blob("ice", 27, 24, 2, 0.6, rough=0.2)
    m.blob("ice", 8, 4, 1.5, 0.5, rough=0.2)
    # decals
    m.scatter(L.PEBBLES, 2, 3, 41, 25, 40, on=["court", "snow"], gap=1, solid=0)
    m.scatter(DRIFTS, 2, 3, 41, 25, 50, on=["court", "flags", "snow"], gap=1, solid=0)
    if not post:
        ents(m, """spawn world 21 28 up
spawn from_hall 8 10 down
spawn from_stair 41 11 left
spawn default 21 28 up
exit 19..24 29 WORLD l_t05
door 8 9 T05_HALL entry sfx=FX008
exit 43 10..13 T05_STAIR from_court
npc edda_court 18 12 down sprite=edda talk=T05_EDDA
npc old_pilot 13 13 left sprite=pilot talk=T05_OLD_PILOT
npc cable_op 22 21 up sprite=worker talk=T05_CABLE_OP
npc kid_aerie 30 22 left sprite=child talk=T05_KID wander=1
npc widow_aerie 10 20 right sprite=elder talk=T05_WIDOW
npc trainee 35 12 down sprite=soldier talk=T05_TRAINEE
shop 22 15 SHOP_T05
switch cable_brake 25 21 scene=CH10_AERIE_FIX if=ch:CH09,!flag:accord_aerie
read 12 13 "The memorial: a long wall of names. Every one of them fell. There is no wall for anyone who came back.\"""")
    else:
        ents(m, """tileset_over 14 12 floor if=!flag:q03_wall
spawn world 21 28 up
spawn default 21 28 up
exit 19..24 29 WORLD_POST l_t05
inn 7 10 scene=T05P_INN
npc hall_p 9 10 down sprite=elder talk=T05P_INN
npc edda_p 18 13 down sprite=edda talk=T05P_EDDA
npc pilot_p 13 14 left sprite=pilot talk=T05P_PILOT
npc windmill 22 11 down sprite=worker talk=T05P_WIND
npc kid_p 30 21 left sprite=child talk=T05P_KID wander=1
npc trader_p 26 18 up sprite=keeper talk=T05P_SHOP
shop 26 17 SHOP_T05
npc survivor_p 36 13 left sprite=survivor talk=T05P_SURVIVOR
read 12 13 "The memorial: a long wall of names. Every one of them fell."
read 14 13 "The Returners' Wall." scene=T05P_RETURN_WALL
save 20 22""")
    return m


def aerie_stair():
    """Wind Stair: timber flights bolted to the Skyspine face, three snow ledges, the wind shrine on top.
    The rock closes the west and north, open sky east and south; entry from the court bridge (west, bottom)."""
    m = Map("T05_STAIR", 24, 30, "High Aerie - Wind Stair", "town_r04", music="M014", zone="T05", location="L_T05",
            region="R04", seed=503)
    m.use(**AMATS)
    B = L.aerie_buildings()
    m.fill("sky")
    # the mountain face (rock, solid) over the west two thirds, ragged towards the sky
    edge = [19, 19, 20, 20, 21, 20, 20, 21, 21, 20, 21, 22, 21, 21, 20, 20, 21, 21, 21, 20, 20, 19, 20, 20, 23, 23, 23, 23, 22, 21]
    for y in range(30):
        for x in range(edge[y]):
            m.set(x, y, "rock")
    # ledges (walkable) - the original stair plan
    m.rect("court", 3, 1, 10, 4)               # shrine top
    m.rect("snow", 2, 1, 2, 3)
    m.rect("snow", 11, 2, 11, 4)
    m.rect("planks", 6, 5, 7, 9, kind="stairs")
    m.rect("snow", 6, 10, 19, 11)
    m.rect("flags", 8, 10, 17, 10)
    m.rect("planks", 18, 12, 19, 17, kind="stairs")
    m.rect("snow", 3, 18, 19, 19)
    m.rect("flags", 5, 18, 17, 18)
    m.rect("planks", 3, 20, 4, 23, kind="stairs")
    m.rect("snow", 0, 24, 21, 27)
    m.rect("flags", 2, 24, 19, 25)
    m.rect("planks", 0, 24, 1, 27)             # the plank span from the court
    for (x, y) in ((21, 24), (21, 27), (20, 27)):
        m.set(x, y, "sky")
    # rock faces under each ledge (2 rows, snow on the lip) where the drop shows
    for (x0, y, x1) in ((3, 5, 5), (8, 5, 11), (6, 12, 17), (5, 20, 19), (2, 28, 19)):
        face_row(m, B, y, x0, x1, "cliff")
    for y in (28, 29):
        for x in range(0, 24):
            if m.mat[y][x] != "rock":
                m.set(x, y, "sky")
    # timber flights: log stairs, rails and posts at top and bottom
    for (x, y) in ((6, 5), (6, 8), (18, 12), (18, 15), (3, 20)):
        m.place(L.LOG_STAIRS, x, y)
    for (x, y) in ((5, 9), (8, 9), (17, 12), (20, 12), (2, 20), (5, 20)):
        m.place(L.CHAIN_POSTS[(x + y) % 2], x, y - 1)
    # the wind shrine: rune stone (read at 6,2), cloth on poles streaming east, weighting stones
    m.place(L.RUNESTONES[5], 5, 1)
    m.place(L.TOTEMS[1], 3, 1)
    m.place(L.TOTEMS[0], 9, 1)
    cl = L.ochre_cloths()
    for i, (x, y) in enumerate(((4, 2), (7, 2), (8, 2))):
        m.place(cl[i % 3], x, y)
    m.anim("flag_blue", 4, 0, h=96, solid=True)
    m.anim("flag_blue", 8, 0, h=96, solid=True)
    m.anim("flag_blue", 10, 1, h=96, solid=True)
    m.anim("brazier", 3, 3, h=96, solid=True)
    m.anim("brazier", 10, 3, dy=0, h=96, solid=True)
    for (x, y) in ((7, 1), (2, 1), (11, 2)):
        m.place(L.ROCKS_S[(x + y) % 6], x, y)
    # middle ledges: pines, cairns, wind-bent racks, a rest bench and a lantern
    m.place(L.PINES[1], 15, 7)
    m.place(L.PINE_S[1], 11, 8)
    m.place(L.ROCKS_S[3], 12, 10)
    m.place(L.BENCH_S, 9, 10)
    m.place(L.LANTERN_POST, 14, 9)
    m.place(L.ROPE[0], 17, 10)
    m.place(L.ROCKS_S[0], 15, 18)
    m.place(L.LOGS[0], 8, 18)
    m.place(L.LANTERN_POST, 11, 17)
    m.place(L.ROCKS_S[4], 6, 18)
    m.place(L.STUMPS[0], 16, 18)
    # bottom landing: the cable pulley housing, crates, rune arrow sign
    m.place(L.CAPSTAN, 12, 24)
    m.place(L.PULLEYS[0], 14, 24)
    m.place(L.CRATES_V[0], 15, 24)
    m.place(L.BARRELS_V[0], 17, 24)
    m.place(L.ARROWS[2], 5, 24)
    m.place(L.ROPES_6[0], 8, 26)
    m.place(L.LANTERN_POST, 2, 23)
    m.place(L.PINES[0], 19, 20)
    m.place(L.ROCKS_S[5], 19, 26)
    m.anim("brazier", 10, 25, h=96, solid=True)
    m.scatter(DRIFTS, 0, 0, 23, 27, 30, on=["court", "flags", "snow"], gap=1, solid=0)
    sprinkle(m, DRIFTS, 0, 0, 21, 29, 26, ["rock"])
    sprinkle(m, L.PINE_S, 0, 0, 20, 23, 5, ["rock"])
    m.scatter(L.PEBBLES, 0, 0, 23, 27, 20, on=["court", "snow"], gap=1, solid=0)
    ents(m, """spawn from_court 1 25 right
exit 0 24..27 T05_COURT from_stair
trigger 4..9 3..4 scene=T05_SHRINE if=ch:CH07,!event:T05_SHRINE
read 6 2 "The wind shrine. Ochre cloth, weighted with stones, all streaming east.\"""")
    return m


# ============================================================================================ Nacre
NMATS = dict(
    sand=TintMat([("roman", "1", 480, 384, 96, 96)], "sand", mul=(1.0, 0.96, 0.9), organic=True, prio=1),
    dune=TintMat([("roman", "1", 288, 0, 192, 192)], "sand", mul=(1.0, 0.95, 0.88), organic=True, prio=1),
    pave=TintMat([("roman", "1", 672, 0, 96, 192), ("roman", "1", 672, 0, 96, 192), ("roman", "1", 288, 192, 96, 192)],
                 "floor", mul=(1.04, 0.98, 0.88), prio=3),
    terra=Mat([("roman", "1", 384, 480, 192, 96)], "floor", prio=3),
    cobble=TintMat([("roman", "1", 384, 192, 96, 192)], "path", mul=(1.05, 0.98, 0.86), prio=2),
    salt=TintMat([("desert", "1", 432, 192, 144, 144)], "salt", mul=(1.08, 1.08, 1.12), add=(36, 36, 38), organic=True, prio=2),
    brine=Mat([("fa", "water_shallow", 0, 0, 48, 48)], "pool"),
    water=Mat([("fa", "water_deep", 0, 0, 48, 48)], "water", organic=True, prio=0),
    shore=TintMat([("roman", "1", 480, 384, 96, 96)], "sand", mul=(0.92, 0.88, 0.8), organic=True, prio=1),
    rock=TintMat([("dungeon", "1", 576, 4, 160, 88)], "cliff", mul=(1.12, 0.92, 0.68), organic=True, prio=2),
    bwall=TintMat([("roman", "6", 576, 192, 192, 96)], "wall", mul=(0.95, 0.9, 0.8)),
    wallc=TintMat([("roman", "6", 576, 192, 192, 96)], "wall", mul=(0.95, 0.9, 0.8)),
    stairs=TintMat([("roman", "1", 672, 0, 96, 192)], "stairs", mul=(0.9, 0.86, 0.78)),
)


def nacre_market(post=False):
    """Nacre, the salt market. Shape: walled block around a sunken salt basin (layout standard 4, 'walled block' with
    a lower level): sandstone mesa walls close the north, west and east, the town wall and the road close the south.
    The basin of brine pans is the centrepiece and second ground level (stairs north and south); the archive
    record walls and the statue at the head of the basin stairs end the main axis, the cloister stands north-east.
    Post (the Assembly): the listening pool has risen into the basin, benches ring it for the Ash Accord; the
    house by the archive walls and the south-east house are ruins with a delegates' camp; the pool road is blocked."""
    if post:
        m = Map("T06_POST", 44, 30, "Nacre - The Assembly", "town_r05", music="M015", zone="T06", location="L_T06",
                region="R05", save=True, phase="post", seed=602)
    else:
        m = Map("T06_MARKET", 44, 30, "Nacre - Salt Market", "town_r05", music="M015", zone="T06", location="L_T06",
                region="R05", seed=601)
    m.use(**NMATS)
    B = L.nacre_buildings()
    m.fill("rock")
    # --- the upper town (inside the mesa rim)
    m.rect("sand", 2, 3, 41, 26)
    m.rect("dune", 2, 22, 13, 26)
    m.rect("dune", 30, 22, 41, 26)
    for (x, y) in ((2, 3), (2, 4), (41, 3), (41, 4), (41, 5), (2, 25), (2, 26), (41, 26), (3, 26), (40, 26)):
        m.set(x, y, "rock")
    m.rect("pave", 16, 6, 29, 8)                    # the archive walk along the basin's north rim
    m.rect("terra", 18, 7, 26, 8)
    m.rect("cobble", 0, 12, 14, 14)                 # the road west to the listening pool
    m.rect("cobble", 30, 8, 40, 9)                  # cloister forecourt
    m.rect("pave", 32, 10, 38, 13)
    m.rect("cobble", 19, 20, 24, 29)                # south street to the gate
    m.rect("pave", 14, 22, 29, 25)                  # the lower market / assembly street
    if post:
        for y in range(12, 15):
            m.set(0, y, "rock")
            m.set(1, y, "rock")
    # --- mesa faces and borders
    face_row(m, B, 0, 0, 43, "cliff")
    m.rect("rock", 0, 0, 43, 0, kind="cliff")
    face_row(m, B, 27, 2, 18, "cliff")
    face_row(m, B, 27, 25, 41, "cliff")
    # --- the salt basin: north face (rows 9-10) with stairs at 21-23, lip walls west/east/south, stairs south
    skip = {(x, y) for x in (21, 22, 23) for y in (9, 10)}
    face_row(m, B, 9, 16, 28, "wall", key="wallf", skip=skip)
    m.rect("stairs", 21, 9, 23, 10)
    m.place(L.STONE_STAIRS_S, 21, 9)
    m.place(L.STONE_STAIRS_S1, 23, 9)
    m.rect("salt", 16, 11, 28, 18)
    for y in range(11, 19):
        m.set(15, y, "bwall")
        m.set(29, y, "bwall")
    m.rect("bwall", 15, 19, 29, 19)
    m.rect("stairs", 21, 19, 22, 19)
    if not post:
        # brine pans (shallow, animated) between salt walkways
        for (x0, y0, x1, y1) in ((16, 14, 18, 15), (16, 17, 18, 18), (24, 12, 27, 13), (23, 15, 25, 16)):
            m.rect("brine", x0, y0, x1, y1)
        m.water_anims(mat="brine", name="water_shallow")
    else:
        m.rect("water", 16, 11, 28, 13)
        m.rect("shore", 16, 14, 28, 14)
        for (x, y) in ((16, 14), (28, 14), (17, 14), (27, 14)):
            m.set(x, y, "water")
        m.water_anims(mat="water", name="water_deep")
    # === buildings
    m.place(B["house0"], 2, 1)                      # north-west row house (flat roof)
    if not post:
        m.place(B["house1"], 10, 1)                 # the archivist's house by the record walls
    else:
        for (x, y, k) in ((10, 5, 0), (12, 6, 1), (14, 5, 2), (11, 3, 3)):
            m.place([L.RUIN_WALL, K.RUBBLE_B, L.BROKEN_COL[0], K.RUBBLE_S[0]][k], x, y)
        m.rect("sand", 10, 1, 15, 6)
        for x in range(10, 16):
            for y in range(1, 7):
                if m.kind[y][x] == "cliff":
                    m.set(x, y, "sand")
    m.place(B["cloister"] if not post else B["cloister_post"], 31, 0)   # door (35,7)
    m.place(B["house2"], 3, 14)                     # south-west house (rows 14..19)
    if not post:
        m.place(B["house3"], 34, 14)                # south-east house (rows 14..19)
    # --- the archive: record walls and the statue at the head of the basin stairs
    m.place(B["record"], 16, 4)
    m.place(B["record"], 25, 4)
    m.place(L.STATUE_R[0], 21, 2)
    m.place(L.PALMS[0], 19, 3)
    m.place(L.PALMS[1], 23, 3)
    m.place(L.JARS[0], 20, 5)
    m.place(L.JARS[3], 24, 5)
    m.anim("brazier", 29, 4, h=96, solid=True)
    m.anim("brazier", 15, 4, h=96, solid=True)
    # --- the salt stall in the basin (shop 20,13; the seller stands in front at 20,14)
    if not post:
        m.place(L.WHITE_STALLS[0], 19, 12)
        m.place(L.WHITE_STALLS[2], 20, 12)
        m.place(L.SALT_ROCKS[1], 26, 17)
        m.place(L.SALT_ROCKS[0], 19, 17)
        m.place(L.SALT_ROCKS[0], 28, 11)
        m.place(L.JARS[5], 16, 11)
        m.place(L.JARS[6], 17, 11)
        m.place(L.SACKS_D[1], 24, 17)
    else:
        m.place(L.BENCH_R[1], 17, 16)
        m.place(L.BENCH_R[1], 25, 16)
        m.place(L.BENCH_R[1], 19, 18)
        m.place(L.BENCH_R[1], 23, 18)
        m.place(L.LAMP_R, 16, 17)
        m.place(L.LAMP_R, 28, 17)
    # --- north-west: water jars, a shelter, the west road
    m.place(L.AMPHORA[0], 2, 7)
    m.place(L.AMPHORA[1], 3, 7)
    m.place(L.SHELTER[0], 5, 7) if not post else m.place(L.TENTS_D[0], 5, 7)
    m.place(L.CRATE_R[0], 9, 7)
    m.place(L.PALMS[0], 11, 7) if post else m.place(L.PALMS[0], 12, 7)
    m.place(L.SHRUBS[0], 12, 18)
    m.place(L.DROCKS[1], 2, 20)
    m.place(L.HIDES[0], 10, 17)
    # --- gardens south-west (gardener 14,22 / post 8,22)
    m.place(L.GARDEN[0], 11, 20)
    m.place(L.GARDEN[0], 16, 20)
    if post:
        m.place(L.GARDEN[0], 6, 20)
    m.place(L.JARS[8], 10, 21)
    m.place(L.GREEN_SHRUB, 3, 21) if not post else m.place(L.SHRUBS[2], 3, 21)
    # --- cloister forecourt: fountain, benches
    m.place(L.FOUNTAIN_R, 33, 10)
    m.place(L.BENCH_R[2], 38, 11)
    m.place(L.PALMS[1], 40, 7)
    m.place(L.JARS[1], 30, 7)
    m.place(L.JARS[9], 31, 11)
    if post:
        m.place(L.DESK_N, 34, 8)
    # --- the lower market street: awning stalls, jars and crates
    if not post:
        for i, x in enumerate((25, 26, 27, 28)):
            m.place(L.AWNING_STALLS[i], x, 20)
        m.place(L.CRATE_R[1], 29, 21)
    else:
        m.place(L.WHITE_STALLS[1], 27, 20)
        m.place(L.WHITE_STALLS[0], 28, 20)
        for x in (15, 17, 25, 27):
            m.place(L.BENCH_R[1], x, 25)
        m.place(L.BENCH_R[1], 15, 22)
        m.place(L.BENCH_R[1], 17, 22)
        m.anim("brazier", 14, 23, h=96, solid=True)
        m.anim("brazier", 29, 23, h=96, solid=True)
    m.anim("brazier", 18, 26, h=96, solid=True)
    m.anim("brazier", 25, 26, h=96, solid=True)
    # --- south-east: house (market) or the delegates' camp in the ruin (post)
    if not post:
        m.place(L.BARREL_D[0], 33, 18)
        m.place(L.SACKS_D[0], 32, 20)
        m.place(L.HIDES[1], 36, 20)
        m.place(L.DROCKS[2], 40, 21)
    else:
        m.place(L.RUIN_WALL, 34, 15)
        m.place(K.RUBBLE_B, 39, 17)
        m.place(L.TENTS_D[1], 34, 18)
        m.place(L.TENTS_D[2], 35, 21)
        m.anim("campfire", 37, 18, h=48, solid=True)
        m.place(L.SACKS_D[1], 40, 22)
        m.place(L.BROKEN_COL[1], 40, 14)
    m.place(L.DROCKS[3], 39, 24) if not post else m.place(L.DROCKS[3], 40, 24)
    m.place(L.SHRUBS[1], 3, 24)
    m.place(L.PALMS[1], 31, 23)
    m.place(L.PALMS[0], 10, 23)
    # --- more dressing (both versions): the cistern trough, jar clusters against walls, shade shelters
    m.place(L.WATER_CHANNEL, 9, 8)
    m.place(L.JARS[4], 13, 9)
    m.place(L.CRATE_R[1], 2, 11)
    m.place(L.AMPHORA[3], 3, 11)
    m.place(L.JARS[7], 2, 20)
    m.place(L.CRATES_D[0], 9, 20)
    m.place(L.SACKS_D[1], 5, 23)
    m.place(L.PALMS[1], 7, 23)
    m.place(L.DROCKS[2], 12, 25)
    m.place(L.SHRUBS[1], 15, 26)
    m.place(L.SHELTER[1], 31, 20) if not post else m.place(L.SHELTER[2], 31, 20)
    m.place(L.JARS[2], 33, 22)
    m.place(L.CRATES_D[1], 30, 22)
    m.place(L.PALMS[0], 36, 23)
    m.place(L.DROCKS[0], 33, 25)
    if not post:
        m.place(L.SHRUBS[0], 38, 25)
    m.place(L.HIDES[0], 40, 9) if not post else m.place(L.HIDES[1], 40, 9)
    if not post:
        m.place(L.SALT_ROCKS[1], 30, 14)
    m.place(L.JARS[5], 31, 16)
    m.place(L.CRATE_R[0], 31, 17)
    if not post:
        m.place(L.SHELTER[0], 14, 23)
        m.place(L.SHELTER[2], 27, 23)
        m.place(L.AMPHORA[2], 16, 24)
        m.place(L.CRATE_R[1], 28, 25)
    else:
        m.place(K.RUBBLE_B, 2, 12)
        m.place(K.RUBBLE_S[1], 3, 14)
        m.place(L.BROKEN_COL[0], 4, 12)
    m.scatter(L.PEBBLES_N, 2, 3, 41, 26, 30, on=["sand", "dune", "salt"], gap=1, solid=0)
    m.scatter(L.sand_drifts(), 2, 3, 41, 26, 45, on=["pave", "terra", "cobble"], gap=0, solid=0)
    if not post:
        ents(m, """spawn world 21 28 up
spawn from_cloister 35 8 down
spawn from_pool 1 13 right
spawn default 21 28 up
exit 19..24 29 WORLD l_t06
door 35 7 T06_CLOISTER entry sfx=FX009
exit 0 12..15 T06_POOL from_market
npc sen 22 9 down sprite=sen talk=T06_SEN
npc gardener_n 14 22 up sprite=farmer talk=T06_GARDENER
npc family_a 28 16 left sprite=elder talk=T06_FAMILY
npc family_b 27 17 up sprite=survivor talk=T06_FAMILY
npc salt_seller 20 14 down sprite=keeper talk=T06_SALT
npc water_carrier 8 11 right sprite=worker talk=T06_WATER wander=1
npc pilgrim_n 38 22 left sprite=monk talk=T06_PILGRIM
shop 20 13 SHOP_T06""")
    else:
        ents(m, """spawn world 21 28 up
spawn default 21 28 up
exit 19..24 29 WORLD_POST l_t06
inn 34 8 scene=T06P_INN
npc house_keeper 36 9 left sprite=monk talk=T06P_INN
npc sen_p 22 16 down sprite=sen talk=T06P_SEN
npc family_p1 12 16 right sprite=elder talk=T06P_FAMILY
npc family_p2 13 17 up sprite=survivor talk=T06P_FAMILY
npc gardener_p 8 22 up sprite=farmer talk=T06P_GARDENER
npc salt_p 28 22 left sprite=keeper talk=T06P_SHOP
shop 28 21 SHOP_T06
npc listener_p 30 12 left sprite=scholar talk=T06P_LISTENER
npc patient_p 6 10 right sprite=patient talk=Q06_HOOK if=ch:CH20
npc survivor_n 38 20 left sprite=survivor talk=Q07_HOOK if=ch:CH20
npc winter_pilgrim 38 16 left sprite=monk talk=Q09_HOOK if=ch:CH20
npc pool_voice 22 14 down sprite=monk talk=Q12_HOOK if=ch:CH20
trigger 16..27 23..24 scene=CH20_ACCORD if=ch:CH17,ch:CH18,ch:CH19,!ch:CH20
save 38 24""")
    return m


def nacre_pool():
    """The listening pool: a walled sandstone court west of the market, the pool sunk inside a ring of stone steps,
    arcades north and south, the trial relay's stone housing on the south-east shore (CH10), the gate east."""
    m = Map("T06_POOL", 32, 22, "Nacre - Listening Pool", "town_r05", music="M015", zone="T06", location="L_T06",
            region="R05", seed=603)
    m.use(**NMATS)
    m.use(steps=TintMat([("roman", "1", 384, 576, 96, 96)], "floor", mul=(0.96, 0.92, 0.84), prio=3))
    B = L.nacre_buildings()
    m.fill("rock")
    m.rect("pave", 2, 2, 29, 19)
    m.rect("sand", 2, 16, 8, 19)
    m.rect("sand", 23, 2, 29, 5)
    m.rect("cobble", 26, 9, 31, 12)
    m.rect("terra", 12, 16, 18, 17)
    # the pool: deep water inside, a ring of stone steps down to it
    cx, cy, rx, ry = 15.5, 10.5, 6.9, 4.7
    wc = set()
    for y in range(3, 18):
        for x in range(4, 27):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                m.set(x, y, "water")
                wc.add((x, y))
    m.water_anims(mat="water", name="water_deep")
    m.place(L.pool_rim("nacre_poolrim", 6, 3, 20, 16, wc, cx, cy, rx, ry, ("roman", "1", 672, 0, 96, 192),
                       (1.04, 0.98, 0.88), rim_px=26), 6, 3)
    # arcades north and south (the court walls), columns west
    for x in range(2, 30, 2):
        m.place(L.ARCADE[(x * 7 // 2) % 6], x, 0)
    for x in range(2, 30, 2):
        m.place(L.ARCADE[(x * 5 // 2 + 1) % 6], x, 19)
    m.rect("rock", 0, 20, 31, 21, kind="cliff")
    for y in (4, 7, 13, 16):
        m.place(L.COLUMN, 2, y - 1)
    # north shore: the stele (read 15,4), braziers, benches
    m.place(L.STELE, 14, 1)
    m.anim("brazier", 12, 2, h=96, solid=True)
    m.anim("brazier", 18, 2, h=96, solid=True)
    m.place(L.BENCH_R[1], 9, 3)
    m.place(L.BENCH_R[1], 20, 3)
    m.place(L.JARS[0], 5, 3)
    m.place(L.JARS[3], 6, 3)
    m.place(L.PALMS[0], 3, 1)
    m.place(L.PALMS[1], 26, 1)
    m.place(L.STATUE_R[1], 23, 1)
    # south shore: the keeper's walk, benches, lamps
    for (x, y) in ((10, 4), (21, 4), (8, 6), (23, 6), (7, 13), (24, 11), (12, 16), (19, 16)):
        m.place(L.FURS[(x + y) % len(L.FURS)], x, y)
    m.place(L.PEDESTAL_R, 3, 8)
    m.place(L.JARS[9], 6, 9)
    m.place(L.CRATE_R[1], 27, 17)
    m.place(L.SACKS_D[1], 5, 11)
    m.place(L.DROCKS[3], 3, 13)
    m.place(L.JARS[4], 25, 2)
    m.place(L.GREEN_SHRUB, 4, 5)
    m.place(L.AMPHORA[1], 5, 14)
    m.place(L.AMPHORA[2], 4, 15)
    m.place(L.BENCH_R[1], 9, 17)
    m.place(L.BENCH_R[1], 19, 17)
    m.place(L.LAMP_R, 11, 16)
    m.place(L.LAMP_R, 18, 15)
    m.place(L.SHRUBS[0], 3, 17)
    m.place(L.GREEN_SHRUB, 5, 16)
    m.place(L.DROCKS[1], 27, 16)
    # the trial relay: stone housing (24,14) with the cable drum and pulleys
    m.place(L.BLOCK_MOSS, 24, 12)
    m.place(L.DRUM, 26, 14)
    m.place(L.PULLEYS[0], 27, 13)
    m.place(L.SPOOLS[0], 23, 13)
    # the east gate: cloth flags, jars, crates
    m.place(L.CLOTH_FLAG[0], 28, 7)
    m.place(L.CLOTH_FLAG[1], 28, 13)
    m.place(L.CRATE_R[0], 27, 7)
    m.place(L.AMPHORA[0], 29, 14)
    m.place(L.JARS[6], 26, 6)
    m.place(L.SALT_ROCKS[0], 4, 8)
    m.place(L.SALT_ROCKS[1], 24, 3)
    m.anim("brazier", 26, 8, h=96, solid=True)
    m.anim("brazier", 4, 12, h=96, solid=True)
    m.scatter(L.PEBBLES_N, 2, 2, 29, 19, 16, on=["sand", "pave"], gap=1, solid=0)
    m.scatter(L.sand_drifts(), 2, 2, 29, 19, 70, on=["pave", "terra", "cobble"], gap=0, solid=0)
    for (x, y) in ((11, 7), (19, 12), (13, 13), (17, 8), (21, 10), (10, 11), (15, 9), (20, 7), (12, 10), (18, 13)):
        m.place(L.ROCKS_S[(x * y) % 6], x, y)
    ents(m, """spawn from_market 30 10 left
exit 31 9..12 T06_MARKET from_pool
npc pool_keeper 15 17 up sprite=sen talk=T06_POOL_KEEPER
trigger 22..26 15..16 scene=CH10_SC07 if=flag:accord_cinder,flag:accord_aerie,flag:accord_nacre,!ch:CH10
npc volunteer 22 15 up sprite=volunteer talk=CH10_VOLUNTEER if=ch:CH09,!ch:CH10
read 15 4 "The listening pool. When it is quiet, you can hear several people remembering the same morning differently.\"""")
    return m


if __name__ == "__main__":
    maps = [aerie_court(False), aerie_court(True), aerie_stair(), nacre_market(False), nacre_market(True), nacre_pool()]
    print(write_group("aerie", [m.save() for m in maps]))
