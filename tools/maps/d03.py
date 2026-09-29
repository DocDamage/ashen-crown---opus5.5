"""D03 Rootward (pre) and its flooded post-state (D03P, CH14 Nera reunion, B11).
Mechanic: route irrigation through roots to reveal bridges; always leave a walking return path."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMMON = dict(tileset="grove", music="M021", zone="D03", region="R01", location="L_D03")
LEG = {"%": "vine", "Y": "tree2"}


def forest_edges(g, seed):
    g.scatter("T", 0.5, "#", seed)
    g.scatter("Y", 0.3, "#", seed + 1)
    g.scatter("h", 0.12, "#", seed + 2)


def r01():
    g = Grid(40, 28, "#")
    g.blob(20, 14, 17, 11, ",")
    g.blob(20, 14, 13, 8, '"', only=",")
    g.rect(18, 25, 21, 27, ":")
    g.rect(36, 12, 39, 15, ":")
    g.path([(20, 26), (20, 14), (38, 14)], ":", 2)
    # the displaced caravan: wagons (carts), tents, a cookfire
    for (x, y) in ((8, 8), (12, 7), (8, 18), (28, 19)):
        g.put(x, y, "]")
    g.text(14, 10, "22\n")
    g.text(24, 8, "2.2")
    g.put(18, 18, "!")
    g.text(6, 12, "rr\nc")
    forest_edges(g, 1)
    g.e("spawn world 20 26 up")
    g.e("spawn from_r02 37 13 left")
    g.e("spawn default 20 26 up")
    g.e("exit 18..21 27 WORLD l_d03")
    g.e("exit 39 12..15 D03_R02 from_r01 if=event:D03_NERA_MEET locked=\"Nera: That's our road you're about to trample. Talk first.\"")
    g.e("npc nera_camp 20 12 down sprite=C05 talk=D03_NERA_MEET if=!recruited:C05")
    g.e("npc camp_elder 10 10 right sprite=elder talk=D03_CAMP_ELDER if=!ch:CH03")
    g.e("npc camp_mother 25 17 left sprite=farmer talk=D03_CAMP_MOTHER if=!ch:CH03")
    g.e("npc camp_child 14 16 up sprite=child talk=D03_CAMP_CHILD wander=1 if=!ch:CH03")
    g.e("npc camp_carter 30 10 down sprite=worker talk=D03_CAMP_CARTER if=!ch:CH03")
    g.e("save 16 20")
    return g.emit("D03_R01", name="Rootward - Wagon Hollow", encounters="none", save="true", legend=LEG, **COMMON)


def r02():
    g = Grid(32, 32, "#")
    g.blob(16, 16, 14, 13, ",")
    g.rect(0, 11, 2, 14, ":")
    g.rect(14, 0, 17, 3, ",")
    g.rect(29, 22, 31, 25, ",")
    # the ford: a river across the middle with a shallow crossing
    g.rect(1, 16, 30, 19, "~")
    g.rect(6, 16, 8, 19, "w")
    g.e("tileset_over 22..23 16..19 bridge if=flag:d03_sluices")   # root bridge raised by the repaired irrigation
    g.put(12, 12, "&")
    g.e("switch shortcut 12 12 scene=D03_SHORTCUT")
    g.e("sign 14 11 \"Irrigation map: 'Ford sluice feeds the upper camp. Three Sluices feed the grove bridges.'\"")
    forest_edges(g, 11)
    g.e("chest D03_C_R02 5 24 I011 2")
    g.e("spawn from_r01 1 12 right")
    g.e("spawn from_r03 15 2 down")
    g.e("spawn from_r05 30 23 left")
    g.e("exit 0 11..14 D03_R01 from_r02")
    g.e("exit 14..17 0 D03_R03 from_r02")
    g.e("exit 31 22..25 D03_R05 from_r02 if=flag:d03_sluices")
    return g.emit("D03_R02", name="Rootward - Root Ford", encounters="D03", rate="0.9", legend=LEG, **COMMON)


def r03():
    g = Grid(40, 24, "#")
    g.blob(20, 12, 18, 10, ",")
    g.rect(18, 21, 21, 23, ",")
    g.rect(37, 9, 39, 12, ",")
    g.rect(4, 6, 35, 7, "~")        # irrigation channel with three valves
    for x in (8, 20, 32):
        g.put(x, 8, "&")
    g.rect(16, 2, 23, 3, "8")        # the mural (visible from the room)
    g.rect(15, 4, 24, 5, ",")
    forest_edges(g, 21)
    g.e("switch valve_a 8 8 scene=D03_VALVE_A")
    g.e("switch valve_b 20 8 scene=D03_VALVE_B")
    g.e("switch valve_c 32 8 scene=D03_VALVE_C")
    g.put(26, 9, "S")
    g.e("read 26 9 \"A plaque copies the mural across the channel: water leaves the hill at the RIGHT, turns through the LEFT field, and only then feeds the MIDDLE grove.\"")
    g.e("spawn from_r02 19 22 up")
    g.e("spawn from_r04 38 10 left")
    g.e("exit 18..21 23 D03_R02 from_r03")
    g.e("exit 39 9..12 D03_R04 from_r03 if=flag:d03_sluices locked=\"Roots hang too low to pass. Water would lift them.\"")
    return g.emit("D03_R03", name="Rootward - Three Sluices", encounters="D03", rate="0.6", legend=LEG, **COMMON)


def r04():
    g = Grid(32, 28, "#")
    g.blob(16, 14, 13, 12, ",")
    g.rect(0, 12, 2, 15, ",")
    g.rect(14, 25, 17, 27, ",")
    g.blob(22, 6, 5, 3, '"')     # canopy lookout
    g.put(22, 4, "S")
    forest_edges(g, 31)
    # clue-led secret: the lookout names a hollow tree; its base is open on the far side
    g.rect(4, 20, 7, 23, ",")
    g.rect(3, 19, 8, 19, "T")
    g.e("chest D03_SECRET_CHEST 5 21 A003 1 acq=D03_SECRET")
    g.e("read 22 5 \"From the lookout you see the whole grove - and a hollow elm in the south-west, open on its far side.\"")
    g.e("chest D03_C_R04 24 20 W026 1")
    g.e("save 10 8")
    g.e("heal 12 8")
    g.e("spawn from_r03 1 13 right")
    g.e("spawn from_r05 15 26 up")
    g.e("exit 0 12..15 D03_R03 from_r04")
    g.e("exit 14..17 27 D03_R05 from_r04")
    return g.emit("D03_R04", name="Rootward - Canopy Rise", encounters="D03", rate="0.7", save="true", legend=LEG, **COMMON)


def r05():
    g = Grid(40, 32, "#")
    g.blob(20, 16, 16, 12, '"')
    g.blob(20, 16, 6, 4, ",")
    g.rect(18, 0, 21, 4, ",")
    g.rect(0, 22, 3, 25, ",")
    g.rect(0, 22, 9, 25, ",")           # the west ford path into the grove
    g.rect(36, 14, 39, 17, ",")
    for (x, y) in ((10, 8), (30, 8), (10, 24), (30, 24), (6, 16), (34, 16)):
        g.put(x, y, "%")
    forest_edges(g, 41)
    g.e("trigger 14..25 12 scene=D03_STAG if=!flag:b03_done")
    g.e("trigger 14..25 20 scene=D03_STAG if=!flag:b03_done")
    g.e("spawn from_r04 19 1 down")
    g.e("spawn from_r02 1 23 right")
    g.e("spawn from_r06 38 15 left")
    g.e("exit 18..21 0 D03_R04 from_r05")
    g.e("exit 0 22..25 D03_R02 from_r05")
    g.e("exit 39 14..17 D03_R06 from_r05 if=flag:b03_done")
    return g.emit("D03_R05", name="Rootward - Hollow Grove", encounters="none", legend=LEG, **COMMON)


def r06():
    g = Grid(32, 24, "#")
    g.blob(16, 12, 13, 9, ",")
    g.rect(0, 10, 3, 13, ",")
    g.rect(14, 0, 17, 3, ":")
    g.path([(15, 0), (15, 12), (2, 12)], ":", 2)
    g.rect(20, 14, 26, 18, "^")
    forest_edges(g, 51)
    g.e("trigger 12..19 5..6 scene=CH03_VERGE if=!ch:CH03")
    g.e("spawn from_r05 1 11 right")
    g.e("spawn default 1 11 right")
    g.e("exit 0 10..13 D03_R05 from_r06")
    g.e("exit 14..17 0 WORLD l_d03 if=ch:CH03")
    return g.emit("D03_R06", name="Rootward - North Verge", encounters="none", legend=LEG, **COMMON)


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "d03_rootward.map"), [r01(), r02(), r03(), r04(), r05(), r06()], "D03 Rootward")
    print("d03 written")
