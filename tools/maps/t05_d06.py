"""D06 Skychain Viaduct and T05 High Aerie. D06 mechanic: ballast anchors change wind channels;
gusts push you back to the last anchor point (local reset, no damage, rewards kept)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUN = dict(tileset="sky", music="M021", zone="D06", region="R04", location="L_D06")
TOWN = dict(tileset="town_r04", music="M014", zone="T05", region="R04", location="L_T05")
LEG = {"_": "void", "}": "chain", "7": "cable"}


def r01():
    g = Grid(40, 28, "_")
    g.blob(20, 18, 16, 8, ".")
    g.rect(18, 25, 21, 27, ":")
    g.rect(36, 10, 39, 13, ".")
    g.path([(20, 26), (20, 12), (38, 12)], ":", 2)
    g.rect(8, 6, 12, 10, "#")
    g.text(24, 14, "cc\nr")
    g.put(14, 14, "7"); g.put(15, 14, "7")
    g.e("spawn world 20 26 up")
    g.e("spawn from_r02 37 12 left")
    g.e("spawn default 20 26 up")
    g.e("exit 18..21 27 WORLD l_d06")
    g.e("exit 39 10..13 D06_R02 from_r01 if=event:D06_CORREN_MEET")
    g.e("npc corren_foot 28 12 left sprite=C03 talk=D06_CORREN_MEET if=!event:D06_CORREN_MEET")
    g.e("npc crew1 16 17 up sprite=pilot talk=D06_CREW")
    g.e("npc crew2 18 18 left sprite=worker talk=D06_CREW")
    g.e("save 10 17")
    return g.emit("D06_R01", name="Skychain Viaduct - Cable Foot", encounters="none", save="true", legend=LEG, **DUN)


def r02():
    g = Grid(32, 32, "_")
    g.rect(4, 4, 27, 27, ".")
    g.rect(0, 14, 4, 17, ".")
    g.rect(27, 4, 31, 7, ".")      # to R03 (span)
    g.rect(27, 24, 31, 27, ".")    # to R04 (pilots' niche) - alternate route
    for (x, y) in ((8, 8), (22, 8), (8, 22), (22, 22)):
        g.put(x, y, "}")
    g.e("switch ballast1 10 12 flag=d06_b1 scene=D06_BALLAST1")
    g.e("switch ballast2 20 12 flag=d06_b2 scene=D06_BALLAST2")
    g.e("sign 15 10 \"Ballast locks: each lock steadies one lane of the span. Both locked: the middle lane goes calm.\"")
    g.e("spawn from_r01 1 15 right")
    g.e("spawn from_r03 30 5 left")
    g.e("spawn from_r04 30 25 left")
    g.e("exit 0 14..17 D06_R01 from_r02")
    g.e("exit 31 4..7 D06_R03 from_r02")
    g.e("exit 31 24..27 D06_R04 from_r02")
    return g.emit("D06_R02", name="Skychain Viaduct - Ballast Yard", encounters="D06", rate="0.7", legend=LEG, **DUN)


def r03():
    g = Grid(40, 24, "_")
    # three lanes across the span; gust cycles are slow and readable
    for y in (6, 11, 16):
        g.rect(1, y, 38, y + 1, "=")
    g.rect(1, 6, 2, 17, ".")
    g.rect(37, 6, 38, 17, ".")
    g.rect(0, 10, 1, 13, ".")
    g.rect(38, 10, 39, 13, ".")
    for x in (10, 20, 30):
        g.rect(x, 6, x, 17, "=")      # anchor cross-walks (safe)
        g.put(x, 5, "}")
    g.e("hazard 12..18 6..7 period=4 on=1.2 phase=0")
    g.e("hazard 22..28 16..17 period=4 on=1.2 phase=2")
    g.e("hazard 12..18 11..12 period=3.5 on=1.4 phase=1 if=!flag:d06_b1")
    g.e("hazard 22..28 11..12 period=3.5 on=1.4 phase=2.5 if=!flag:d06_b2")
    g.e("sign 3 9 \"Wind cues: pennants lift before each gust. Cross between gusts, or lock the ballast and take the calm middle lane.\"")
    g.e("chest D06_C_R03 20 16 I018 2")
    g.e("spawn from_r02 1 11 right")
    g.e("spawn from_r04 38 11 left")
    g.e("exit 0 10..13 D06_R02 from_r03")
    g.e("exit 39 10..13 D06_R04 from_r03")
    return g.emit("D06_R03", name="Skychain Viaduct - Crosswind Span", encounters="D06", rate="0.5", legend=LEG, **DUN)


def r04():
    g = Grid(32, 28, "_")
    g.rect(3, 3, 28, 24, ".")
    g.rect(0, 10, 3, 13, ".")
    g.rect(0, 20, 3, 23, ".")
    g.rect(14, 0, 17, 3, ".")
    g.house(8, 4, 6, 3)
    g.text(18, 16, "cc\nr")
    # optional rescue gear and a rest point
    g.e("chest D06_C_R04 20 6 G019 1")
    g.e("chest D06_C_R04B 24 20 I006 2")
    g.e("save 6 16")
    g.e("heal 8 16")
    # clue-led secret: the pilots' shelf
    g.rect(25, 8, 28, 11, "#")
    g.rect(26, 9, 27, 10, ".")
    g.put(25, 10, ".")
    g.e("chest D06_SECRET_CHEST 27 9 A006 1 acq=D06_SECRET")
    g.e("read 11 8 \"Pilots' board: 'Spare clock-token on the windward shelf, behind the niche. Put it back.'\"")
    g.e("spawn from_r03 1 11 right")
    g.e("spawn from_r02 1 21 right")
    g.e("spawn from_r05 15 1 down")
    g.e("exit 0 10..13 D06_R03 from_r04")
    g.e("exit 0 20..23 D06_R02 from_r04")
    g.e("exit 14..17 0 D06_R05 from_r04")
    return g.emit("D06_R04", name="Skychain Viaduct - Pilots' Niche", encounters="none", save="true", legend=LEG, **DUN)


def r05():
    g = Grid(40, 32, "_")
    g.blob(20, 16, 16, 12, ".")
    g.rect(18, 26, 21, 31, ".")
    g.rect(36, 14, 39, 17, ".")
    for (x, y) in ((6, 6), (34, 6), (6, 26), (34, 26)):
        g.put(x, y, "}")
    g.e("trigger 14..25 18..19 scene=D06_ROC if=!flag:b06_done")
    g.e("spawn from_r04 19 29 up")
    g.e("spawn from_r06 38 15 left")
    g.e("exit 18..21 31 D06_R04 from_r05")
    g.e("exit 39 14..17 D06_R06 from_r05 if=flag:b06_done")
    return g.emit("D06_R05", name="Skychain Viaduct - Chain Nest", encounters="none", legend=LEG, **DUN)


def r06():
    g = Grid(32, 24, "_")
    g.rect(2, 6, 29, 18, ".")
    g.rect(0, 10, 2, 13, ".")
    g.rect(14, 0, 17, 6, ":")
    g.text(20, 8, "mm\n77")
    g.e("trigger 3..5 10..13 scene=CH07_LANDING if=!ch:CH07")
    g.e("spawn from_r05 1 11 right")
    g.e("spawn default 1 11 right")
    g.e("exit 0 10..13 D06_R05 from_r06")
    g.e("exit 14..17 0 WORLD l_d06 if=ch:CH07")
    return g.emit("D06_R06", name="Skychain Viaduct - High Landing", encounters="none", legend=LEG, **DUN)


def court():
    g = Grid(44, 30, "_")
    g.rect(2, 4, 41, 25, ":")
    g.rect(19, 25, 24, 29, ":")
    g.house(4, 5, 8, 4, chimney=2)       # returners' hall
    g.house(16, 5, 6, 2)
    g.house(28, 5, 7, 3)
    g.house(4, 16, 7, 3)
    g.house(33, 16, 8, 4)
    g.text(20, 14, "aaaa\nnnnn")
    g.put(12, 12, "y")                   # memorial
    g.rect(40, 10, 43, 13, ":")          # wind stair east
    for (x, y) in ((14, 20), (28, 20), (26, 10)):
        g.put(x, y, "l")
    g.put(22, 22, "7"); g.put(23, 22, "7")
    g.e("spawn world 21 28 up")
    g.e("spawn from_hall 8 10 down")
    g.e("spawn from_stair 41 11 left")
    g.e("spawn default 21 28 up")
    g.e("exit 19..24 29 WORLD l_t05")
    g.e("door 8 9 T05_HALL entry sfx=FX008")
    g.e("exit 43 10..13 T05_STAIR from_court")
    g.e("npc edda_court 18 12 down sprite=edda talk=T05_EDDA")
    g.e("npc old_pilot 13 13 left sprite=pilot talk=T05_OLD_PILOT")
    g.e("npc cable_op 22 21 up sprite=worker talk=T05_CABLE_OP")
    g.e("npc kid_aerie 30 22 left sprite=child talk=T05_KID wander=1")
    g.e("npc widow_aerie 10 20 right sprite=elder talk=T05_WIDOW")
    g.e("npc trainee 35 12 down sprite=soldier talk=T05_TRAINEE")
    g.e("shop 22 15 SHOP_T05")
    g.e("switch cable_brake 25 21 scene=CH10_AERIE_FIX if=ch:CH09,!flag:accord_aerie")
    g.e("read 12 13 \"The memorial: a long wall of names. Every one of them fell. There is no wall for anyone who came back.\"")
    return g.emit("T05_COURT", name="High Aerie - Cable Court", legend=LEG, **TOWN)


def hall():
    g = Grid(20, 12)
    g.rect(1, 1, 18, 10, ".")
    g.text(1, 1, "88888888..kkk")
    g.text(3, 5, "bb.bb..bb.bb")
    g.rect(9, 11, 10, 11, "+")
    g.e("spawn entry 9 10 up")
    g.e("exit 9..10 11 T05_COURT from_hall")
    g.e("npc hallkeeper 14 2 down sprite=elder talk=T05_HALL_INN")
    g.e("inn 14 1 scene=T05_HALL_INN")
    g.e("save 17 8")
    return g.emit("T05_HALL", name="High Aerie - Returners' Hall", tileset="interior", music="M014", zone="T05", location="L_T05", save="true")


def stair():
    g = Grid(24, 30, "_")
    g.rect(2, 24, 21, 27, ":")
    g.path([(3, 25), (3, 18), (18, 18), (18, 10), (6, 10), (6, 3)], "s", 2)
    g.rect(3, 1, 10, 4, ".")
    g.put(6, 1, "@")
    g.rect(0, 24, 2, 27, ":")
    g.e("spawn from_court 1 25 right")
    g.e("exit 0 24..27 T05_COURT from_stair")
    g.e("trigger 4..9 3..4 scene=T05_SHRINE if=ch:CH07,!event:T05_SHRINE")
    g.e("read 6 2 \"The wind shrine. Ochre cloth, weighted with stones, all streaming east.\"")
    return g.emit("T05_STAIR", name="High Aerie - Wind Stair", legend=LEG, **TOWN)


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "t05_d06.map"), [r01(), r02(), r03(), r04(), r05(), r06(), court(), hall(), stair()],
          "D06 Skychain + T05 High Aerie")
    print("t05/d06 written")
