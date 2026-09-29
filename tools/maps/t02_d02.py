"""T02 Veyr (capital: south market, oath square, lower records hall) and D02 Veyr Underways.
D02 mechanic: reroute a signal bell to move patrols; no real-time stealth failure."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOWN = dict(tileset="capital", music="M011", zone="T02", region="R01", location="L_T02")
DUN = dict(tileset="underways", music="M020", zone="D02", region="R01", location="L_T02")


def market():
    g = Grid(44, 30, '"')
    g.rect(0, 0, 43, 1, "#")          # city wall north
    g.rect(0, 0, 1, 29, "#"); g.rect(42, 0, 43, 29, "#")
    g.rect(2, 2, 41, 27, ":")
    g.rect(19, 0, 24, 1, "+")          # gate north to oath square
    g.rect(19, 28, 24, 29, ":")        # south gate to the world
    g.rect(2, 26, 17, 29, "#"); g.rect(26, 26, 41, 29, "#")
    # houses and shops
    g.house(3, 3, 7, 3, chimney=1)
    g.house(12, 3, 6, 2)
    g.house(26, 3, 6, 3, chimney=4)
    g.house(34, 3, 7, 4)
    g.house(3, 16, 8, 4)
    g.house(33, 16, 8, 3, chimney=6)
    # market stalls with awnings and counters
    for x in (8, 15, 24, 31):
        g.text(x, 10, "aaaa\nnnnn")
    g.text(12, 20, "cc.r   t.t   cc")
    g.put(21, 14, "O")                  # public well
    for (x, y) in ((6, 9), (37, 9), (17, 14), (26, 14), (6, 23), (37, 23)):
        g.put(x, y, "l")
    for (x, y) in ((18, 6), (25, 6), (10, 14), (33, 14)):
        g.put(x, y, "y")               # banner poles use statue props? (heartglass lamp stands)
    g.e("spawn world 21 27 up")
    g.e("spawn from_square 21 2 down")
    g.e("spawn from_shop 7 20 down")
    g.e("spawn default 21 27 up")
    g.e("exit 19..24 29 WORLD t02")
    g.e("exit 19..24 0 T02_SQUARE from_market")
    g.e("door 7 19 T02_SHOP entry sfx=FX008")
    g.e("npc herald 21 8 down sprite=noble talk=T02_HERALD if=!ch:CH02")
    g.e("npc guard_a 19 12 right sprite=guard talk=T02_GUARDS")
    g.e("npc guard_b 20 12 left sprite=soldier talk=T02_GUARDS")
    g.e("npc vendor1 9 9 down sprite=keeper talk=T02_VENDOR1")
    g.e("npc vendor2 25 9 down sprite=baker talk=T02_VENDOR2")
    g.e("npc lampman 26 15 left sprite=worker talk=T02_LAMPMAN")
    g.e("npc child_v 30 22 up sprite=child talk=T02_CHILD wander=1")
    g.e("npc clerk_m 14 16 down sprite=clerk talk=T02_CLERK_M")
    g.e("npc pilgrim 37 12 left sprite=monk talk=T02_PILGRIM")
    g.e("shop 16 11 SHOP_T02")
    g.e("sign 22 3 \"Oath Square. Ministry of Relays. Crown Records below.\"")
    return g.emit("T02_MARKET", name="Veyr - South Market", **TOWN)


def shop():
    g = Grid(14, 9)
    g.rect(1, 1, 12, 7, ".")
    g.text(1, 1, "kkk.nnnn.kkk")
    g.text(2, 5, "c..t.t..r")
    g.rect(6, 8, 7, 8, "+")
    g.e("spawn entry 6 7 up")
    g.e("exit 6..7 8 T02_MARKET from_shop")
    g.e("npc smith 6 1 down sprite=keeper talk=T02_SMITH")
    g.e("shop 6 2 SHOP_T02")
    return g.emit("T02_SHOP", name="Veyr - Blades and Plate", tileset="interior", music="M011", zone="T02", location="L_T02")


def square():
    g = Grid(40, 28, ":")
    g.rect(0, 0, 39, 5, "#")
    g.rect(0, 0, 1, 27, "#"); g.rect(38, 0, 39, 27, "#")
    # ministry steps and facade
    g.rect(10, 2, 29, 5, "W")
    g.rect(10, 0, 29, 1, "R")
    for x in range(11, 29, 3):
        g.put(x, 5, "Q")
    g.rect(18, 5, 21, 5, "D")
    g.rect(14, 6, 25, 8, "s")
    for x in (12, 27):
        g.put(x, 6, "u")
    # oath statue and banners
    g.put(19, 14, "y")
    g.put(20, 14, "y")
    g.rect(16, 12, 23, 16, ".")
    g.put(19, 14, "y")
    for (x, y) in ((6, 10), (33, 10), (6, 20), (33, 20)):
        g.put(x, y, "l")
    g.text(3, 8, "bb\n\n\nbb")
    g.text(35, 8, "bb\n\n\nbb")
    g.rect(18, 26, 21, 27, ":")
    g.rect(2, 22, 5, 26, "#"); g.rect(34, 22, 37, 26, "#")
    g.put(3, 21, "D")                   # stair down to the records hall
    g.e("spawn from_market 19 25 up")
    g.e("spawn from_records 3 20 down")
    g.e("spawn default 19 25 up")
    g.e("exit 18..21 27 T02_MARKET from_square")
    g.e("door 3 21 T02_RECORDS entry sfx=FX009 if=ch:CH02")
    g.e("npc minister_aide 19 9 down sprite=noble talk=T02_AIDE if=!ch:CH02")
    g.e("npc guard_s1 17 9 down sprite=guard talk=T02_GUARD_S if=!ch:CH02")
    g.e("npc guard_s2 22 9 down sprite=guard talk=T02_GUARD_S if=!ch:CH02")
    g.e("npc ansel_sq 30 12 left sprite=ansel talk=T02_ANSEL_SQ if=!ch:CH02")
    g.e("npc widow 8 16 right sprite=elder talk=T02_WIDOW")
    g.e("trigger 17..22 11..12 scene=CH02_ARREST if=!ch:CH02,ch:CH01")
    g.e("read 19 15 \"The Oath Statue: 'I shall carry the Crown's orders.' Someone has scratched 'whose?' beneath.\"")
    return g.emit("T02_SQUARE", name="Veyr - Oath Square", **TOWN)


def records():
    g = Grid(30, 20)
    g.rect(1, 1, 28, 18, ".")
    for x in range(3, 27, 4):
        g.rect(x, 3, x + 1, 13, "k")
    g.rect(1, 16, 28, 18, ",")
    g.rect(2, 1, 4, 1, "s")
    g.e("spawn entry 3 2 down")
    g.e("exit 2..4 1 T02_SQUARE from_records")
    g.e("npc archivist_v 14 16 up sprite=scholar talk=T02_ARCHIVIST")
    g.e("chest T02_C_REC 26 16 I005 1")
    return g.emit("T02_RECORDS", name="Veyr - Lower Records Hall", tileset="interior_stone", music="M011", zone="T02", location="L_T02")


# ------------------------------------------------------------------ D02 Veyr Underways
def d_r01():
    g = Grid(40, 28)
    g.rect(2, 2, 37, 25, ".")
    # cells along the west
    for y in (3, 9, 15):
        g.rect(2, y, 9, y + 4, ",")
        g.rect(10, y, 10, y + 4, "#")
        g.put(10, y + 2, "{")
    g.put(10, 11, ",")
    g.text(4, 10, "B")
    g.text(15, 20, "tt.b\ntt")
    g.text(30, 4, "kkk\nkkk")
    g.rect(18, 0, 21, 2, ".")
    g.path([(12, 12), (19, 12), (19, 2)], ",", 2)
    for (x, y) in ((14, 3), (25, 3), (14, 24), (25, 24)):
        g.put(x, y, "l")
    g.e("spawn cell 6 11 right")
    g.e("spawn from_r02 19 3 down")
    g.e("spawn default 6 11 right")
    g.e("npc oriel_cell 12 11 left sprite=C06 talk=D02_ORIEL if=!recruited:C06")
    g.e("npc jailer 20 20 left sprite=guard talk=D02_JAILER if=!recruited:C06")
    g.e("chest D02_C_R01 35 24 I001 2")
    g.e("exit 18..21 0 D02_R02 from_r01 if=recruited:C06 locked=\"Dain: The door's barred. We need a way out that isn't this one.\"")
    g.e("save 33 12")
    return g.emit("D02_R01", name="Veyr Underways - Intake Hall", encounters="none", save="true", **DUN)


def d_r02():
    g = Grid(32, 32)
    g.rect(2, 2, 29, 29, ".")
    for y in range(4, 26, 5):
        for x in range(4, 28, 7):
            g.rect(x, y, x + 4, y + 1, "k")
    g.rect(14, 29, 17, 31, ".")
    g.rect(29, 14, 31, 17, ".")
    g.e("spawn from_r01 15 29 up")
    g.e("spawn from_r03 29 15 left")
    g.e("exit 14..17 31 D02_R01 from_r02")
    g.e("exit 31 14..17 D02_R03 from_r02 if=event:D02_SC03 locked=\"Oriel: The records first. All of them.\"")
    g.e("trigger 11..20 13..14 scene=D02_SC03 if=!event:D02_SC03")
    g.e("read 6 17 \"A ledger page: 'Unit 4419, dragonborn, Crown Quarry lift crew. Status: expendable material.' The unit has a name written in pencil: Wren.\"")
    g.e("read 25 22 \"Transport orders, stamped by the Marshal's office: heartglass cargo routed 'via Rootward sluices to the northern road.'\"")
    g.e("chest D02_C_R02 27 4 I004 2")
    return g.emit("D02_R02", name="Veyr Underways - Ledger Stacks", encounters="D02", rate="0.7", **DUN)


def d_r03():
    g = Grid(40, 24)
    g.rect(1, 9, 38, 14, ".")            # main junction hall
    g.rect(0, 10, 1, 13, ".")
    g.rect(17, 1, 22, 9, ".")            # north corridor -> R05 (direct)
    g.rect(17, 14, 22, 22, ".")          # south corridor -> R04 (cistern)
    g.rect(18, 0, 21, 1, ".")
    g.rect(18, 22, 21, 23, ".")
    g.rect(30, 3, 36, 8, ",")            # bell alcove
    g.path([(33, 8), (33, 9)], ",")
    g.put(33, 4, "j")
    g.rect(3, 15, 9, 20, ",")            # rest alcove
    g.path([(6, 14), (6, 15)], ",")
    # patrols: read their route off the floor chalk; the bell redirects them (toggle, always one route open)
    g.e("npc patrol_n1 19 4 down sprite=guard talk=D02_PATROL if=!flag:d02_bell")
    g.e("npc patrol_n2 20 4 down sprite=guard talk=D02_PATROL if=!flag:d02_bell")
    g.e("npc patrol_s1 19 19 up sprite=guard talk=D02_PATROL if=flag:d02_bell")
    g.e("npc patrol_s2 20 19 up sprite=guard talk=D02_PATROL if=flag:d02_bell")
    g.e("block 17..22 5 tile=grate if=!flag:d02_bell msg=\"Two guards hold the north corridor. Their chalk marks point to the bell alcove.\"")
    g.e("block 17..22 18 tile=grate if=flag:d02_bell msg=\"The guards moved to the south corridor, toward the echo.\"")
    g.e("switch bell 33 5 flag=d02_bell scene=D02_BELL")
    g.e("sign 26 9 \"Chalk on the floor: 'Signal bell = all posts report to the echo side.'\"")
    g.e("save 5 17")
    g.e("heal 7 17")
    g.e("spawn from_r02 1 11 right")
    g.e("spawn from_r04 19 21 up")
    g.e("spawn from_r05 19 2 down")
    g.e("exit 0 10..13 D02_R02 from_r03")
    g.e("exit 18..21 23 D02_R04 from_r03")
    g.e("exit 18..21 0 D02_R05 from_r03")
    return g.emit("D02_R03", name="Veyr Underways - Bell Junction", encounters="D02", rate="0.6", save="true", **DUN)


def d_r04():
    g = Grid(32, 28)
    g.rect(2, 2, 29, 12, ".")            # upper walk
    g.rect(2, 16, 29, 25, ",")           # lower cistern floor
    g.rect(2, 13, 29, 15, "~")
    g.rect(14, 0, 17, 2, ".")
    g.rect(26, 2, 29, 0, ".")
    # one-way drop (ledge) and the return ladder
    g.rect(8, 13, 9, 15, "^")            # ledge: a one-way drop down, never back up
    g.put(24, 13, "L"); g.put(24, 14, "L"); g.put(24, 15, "L")
    g.e("trigger 8..9 12 scene=D02_DROP if=!flag:d02_dropped")
    g.text(4, 18, "rr.c")
    g.text(20, 21, "cc\nc")
    g.text(12, 4, "kk.kk")
    # clue-led secret: a gap between barrels in the lower cistern
    g.rect(27, 22, 29, 25, "#")
    g.rect(27, 23, 28, 24, ",")
    g.put(26, 23, ",")
    g.e("chest D02_SECRET_CHEST 28 24 A002 1 acq=D02_SECRET")
    g.e("read 5 21 \"Maintenance note: 'Overflow valve behind the east barrels. Mind the step.'\"")
    g.e("chest D02_C_R04 20 23 I006 1")
    g.e("spawn from_r03 15 3 down")
    g.e("spawn from_r05 27 3 left")
    g.e("exit 14..17 0 D02_R03 from_r04")
    g.e("exit 29 2..4 D02_R05 from_r04")
    g.rect(29, 2, 29, 4, ".")
    return g.emit("D02_R04", name="Veyr Underways - Cistern Walk", encounters="D02", rate="1.0", **DUN)


def d_r05():
    g = Grid(40, 32)
    g.blob(20, 16, 16, 12, ".")
    g.rect(18, 26, 21, 31, ".")
    g.rect(0, 14, 4, 17, ".")
    g.rect(36, 14, 39, 17, ".")
    g.rect(16, 5, 23, 8, "m")
    for (x, y) in ((8, 8), (31, 8), (8, 24), (31, 24)):
        g.put(x, y, "u")
    g.e("trigger 14..25 20 scene=D02_BAILIFF if=!flag:b02_done")
    g.e("spawn from_r03 19 29 up")
    g.e("spawn from_r04 1 15 right")
    g.e("spawn from_r06 38 15 left")
    g.e("exit 18..21 31 D02_R03 from_r05")
    g.e("exit 0 14..17 D02_R04 from_r05")
    g.e("exit 39 14..17 D02_R06 from_r05 if=flag:b02_done locked=\"The canal door is sealed by the Bailiff's stamp.\"")
    return g.emit("D02_R05", name="Veyr Underways - Seal Chamber", encounters="none", **DUN)


def d_r06():
    g = Grid(32, 24)
    g.rect(1, 3, 30, 11, ".")
    g.rect(1, 12, 30, 20, "~")
    g.rect(0, 6, 1, 8, ".")
    g.rect(12, 12, 16, 13, "d")
    g.put(14, 14, "6")
    g.text(4, 4, "cc\nr")
    g.e("npc ansel 20 6 left sprite=ansel talk=D02_ANSEL if=!ch:CH02")
    g.e("trigger 12..16 11 scene=CH02_CANAL if=!ch:CH02")
    g.e("save 26 5")
    g.e("heal 27 5")
    g.e("spawn from_r05 1 7 right")
    g.e("exit 0 6..8 D02_R05 from_r06")
    return g.emit("D02_R06", name="Veyr Underways - Canal Exit", encounters="none", save="true", **DUN)


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "t02_d02.map"),
          [market(), shop(), square(), records(), d_r01(), d_r02(), d_r03(), d_r04(), d_r05(), d_r06()], "T02 Veyr + D02 Underways")
    print("t02/d02 written")
