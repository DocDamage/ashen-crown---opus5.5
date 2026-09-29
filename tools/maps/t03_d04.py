"""T03 Cinderwake (terraces, shift canteen, regulator shop, old cooling garden) and D04 Furnace Spine.
D04 mechanic: balance three pressure lines, venting into empty chambers rather than occupied workshops."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOWN = dict(tileset="town_r02", music="M012", zone="T03", region="R02", location="L_T03")
DUN = dict(tileset="furnace", music="M022", zone="D04", region="R02", location="L_D04")
LEG = {"P": "pipe_tall", "%": "vine"}


def town():
    g = Grid(44, 32, "#")
    # three terraces stepping up to the north, joined by stairs
    g.rect(2, 22, 41, 29, ":")
    g.rect(2, 13, 41, 19, ":")
    g.rect(2, 4, 41, 10, ":")
    for (x, y) in ((10, 20), (30, 20), (20, 11)):
        g.rect(x, y, x + 2, y + 1, "s")
    g.rect(19, 30, 24, 31, ":")
    g.house(4, 23, 8, 3, chimney=6)       # canteen
    g.house(32, 23, 8, 4, chimney=1)      # workers' housing
    g.house(4, 14, 9, 4, chimney=2)       # regulator shop
    g.house(30, 14, 9, 5)
    g.house(14, 4, 7, 3, chimney=5)
    for x in range(24, 41, 4):
        g.put(x, 5, "P")                   # copper pipe runs
    g.text(24, 8, "vv  vv")
    g.put(2, 7, "+"); g.rect(0, 6, 1, 8, ":")   # west path to the old cooling garden
    g.rect(41, 5, 43, 7, ":")                   # east gate to the Furnace Spine
    g.text(16, 25, "cc.r")
    g.put(21, 16, "O")
    for (x, y) in ((14, 26), (28, 26), (16, 17), (26, 17), (10, 8), (34, 8)):
        g.put(x, y, "l")
    g.e("tileset_over 20..22 26..27 wheel if=ch:CH04")
    g.e("spawn world 21 29 up")
    g.e("spawn from_canteen 7 27 down")
    g.e("spawn from_shop 8 18 down")
    g.e("spawn from_garden 3 7 right")
    g.e("spawn from_spine 40 6 left")
    g.e("spawn default 21 29 up")
    g.e("exit 19..24 31 WORLD l_t03")
    g.e("door 7 26 T03_CANTEEN entry sfx=FX008")
    g.e("door 8 17 T03_SHOP entry sfx=FX008")
    g.e("exit 0 6..8 T03_GARDEN from_town")
    g.e("exit 43 5..7 D04_R01 from_town if=event:T03_IVO_SHOP locked=\"A foreman: 'Spine's closed to visitors. Talk to Quill at the regulator shop.'\"")
    g.e("npc worker_t1 18 27 up sprite=worker talk=T03_CLINIC")
    g.e("npc worker_t2 33 17 left sprite=worker talk=T03_HEAT")
    g.e("npc child_t 26 24 down sprite=child talk=T03_CHILD wander=1")
    g.e("npc foreman 38 7 left sprite=soldier talk=T03_FOREMAN")
    g.e("npc pipefitter 28 8 down sprite=worker talk=T03_PIPEFITTER")
    g.e("npc elder_t 12 8 right sprite=elder talk=T03_ELDER")
    return g.emit("T03_TOWN", name="Cinderwake", legend=LEG, **TOWN)


def canteen():
    g = Grid(20, 12)
    g.rect(1, 1, 18, 10, ".")
    g.text(1, 1, "kkk.nnnnnn.8888")
    g.text(3, 4, "tt.tt.tt\n\ntt.tt.tt")
    g.rect(9, 11, 10, 11, "+")
    g.e("spawn entry 9 10 up")
    g.e("exit 9..10 11 T03_TOWN from_canteen")
    g.e("npc cook 7 1 down sprite=baker talk=T03_COOK")
    g.e("npc tally_w 15 2 up sprite=worker talk=T03_TALLY_WALL")
    g.e("read 13 2 \"The canteen wall: a tally of injuries in chalk, row after row. No official ledger records it.\"")
    g.e("shop 8 2 SHOP_T03")
    g.e("inn 12 2 scene=T03_INN")
    g.e("npc innkeep 12 1 down sprite=keeper talk=T03_INN solid=1")
    return g.emit("T03_CANTEEN", name="Cinderwake - Shift Canteen", tileset="interior", music="M012", zone="T03", location="L_T03", save="true")


def shop():
    g = Grid(22, 14)
    g.rect(1, 1, 20, 12, ".")
    g.text(2, 2, "mm.mm.pp.mm")
    g.text(3, 7, "5.tt..>>")
    g.text(14, 9, "cc\nr")
    g.rect(10, 13, 11, 13, "+")
    g.e("spawn entry 10 12 up")
    g.e("exit 10..11 13 T03_TOWN from_shop")
    g.e("npc ivo_shop 10 5 down sprite=C04 talk=T03_IVO_SHOP if=!recruited:C04")
    g.e("npc pell 6 5 right sprite=pell talk=T03_PELL")
    g.e("read 13 2 \"A regulator on the bench: brass coils around a cup of red heartglass. Tessa goes very quiet looking at it.\"")
    g.e("save 18 11")
    return g.emit("T03_SHOP", name="Cinderwake - Regulator Shop", tileset="interior", music="M012", zone="T03", location="L_T03", save="true")


def garden():
    g = Grid(32, 22, "#")
    g.blob(16, 11, 14, 9, '"')
    g.rect(29, 9, 31, 11, ":")
    g.rect(6, 5, 12, 8, "g")
    g.rect(20, 13, 26, 16, "g")
    g.rect(14, 10, 17, 12, "9")
    g.scatter("T", 0.4, "#", 71)
    g.e("spawn from_town 30 10 left")
    g.e("exit 31 9..11 T03_TOWN from_garden")
    g.e("npc gardener 10 12 up sprite=farmer talk=T03_GARDENER")
    g.e("npc pell_garden 18 8 down sprite=pell talk=T03_PELL_GARDEN if=ch:CH04")
    g.e("chest T03_C_GARDEN 4 11 I021 1")
    g.put(24, 6, "<")
    g.e("switch bypass 23 7 scene=CH10_CINDER_FIX if=ch:CH09,!flag:accord_cinder")
    return g.emit("T03_GARDEN", name="Cinderwake - Old Cooling Garden", **TOWN)


# ------------------------------------------------------------------ D04 Furnace Spine
def chamber(g, x, y, occupied, label):
    g.rect(x, y, x + 5, y + 3, "#")
    g.rect(x + 1, y + 1, x + 4, y + 2, "." if occupied else ",")
    g.put(x + 2, y + 3, "Q")


def d_r01():
    g = Grid(40, 28)
    g.rect(2, 3, 37, 24, ".")
    g.rect(0, 12, 2, 15, ".")
    g.rect(36, 12, 39, 15, ".")
    for x in range(6, 36, 6):
        g.put(x, 4, "P")
        g.put(x, 22, "P")
    g.text(8, 10, "mm\nmm")
    g.text(28, 16, "cc\nrr")
    g.e("spawn from_town 1 13 right")
    g.e("spawn from_r02 38 13 left")
    g.e("spawn default 1 13 right")
    g.e("exit 0 12..15 T03_TOWN from_spine")
    g.e("exit 39 12..15 D04_R02 from_r01 if=recruited:C04 locked=\"Ivo: Wait. You don't walk into the Spine without someone who knows the lines.\"")
    g.e("trigger 5..7 12..15 scene=D04_SHIFT_GATE if=!recruited:C04")
    g.e("save 20 20")
    g.e("heal 22 20")
    return g.emit("D04_R01", name="Furnace Spine - Shift Gate", encounters="none", save="true", legend=LEG, **DUN)


def d_r02():
    g = Grid(32, 32)
    g.rect(2, 2, 29, 29, ",")
    g.rect(0, 14, 2, 17, ".")
    g.rect(14, 0, 17, 2, ".")
    g.rect(14, 29, 17, 31, ".")
    # boiler walk: a catwalk over burning floor, three vents burst in rhythm
    g.rect(3, 8, 28, 23, "e")
    g.path([(1, 15), (15, 15), (15, 1)], ".", 2)
    g.path([(15, 15), (15, 30)], ".", 2)
    for (x, y) in ((6, 14), (10, 17), (15, 10), (16, 20), (15, 25)):
        g.put(x, y - 1 if y < 15 else y, "v")
    g.e("hazard 8..9 15..16 period=3 on=0.9 phase=0")
    g.e("hazard 15..16 9..10 period=3 on=0.9 phase=1.2")
    g.e("hazard 15..16 22..23 period=3.4 on=1.0 phase=2.0")
    g.e("sign 3 13 \"Boiler walk: vents fire in turn. Watch the puff, then cross.\"")
    g.e("spawn from_r01 1 15 right")
    g.e("spawn from_r03 15 1 down")
    g.e("spawn from_r04 15 30 up")
    g.e("exit 0 14..17 D04_R01 from_r02")
    g.e("exit 14..17 0 D04_R03 from_r02")
    g.e("exit 14..17 31 D04_R04 from_r02")
    return g.emit("D04_R02", name="Furnace Spine - Boiler Walk", encounters="D04", rate="0.6", legend=LEG, **DUN)


def valve_room(mid, name, valve_flag, chamber_left_occupied, exits, spawns, extra):
    g = Grid(40, 24)
    g.rect(2, 3, 37, 20, ".")
    chamber(g, 4, 3, chamber_left_occupied, "L")
    chamber(g, 30, 3, not chamber_left_occupied, "R")
    g.path([(10, 5), (29, 5)], "p")
    g.put(19, 9, "&")
    for e in exits + spawns + extra:
        g.e(e)
    g.e(f"switch valve 19 9 flag={valve_flag} scene=D04_{valve_flag.upper()}")
    for (x, y) in ((6, 16), (33, 16)):
        g.put(x, y, "P")
    return g


def d_r03():
    g = valve_room("D04_R03", "Red Valve", "d04_red", True,
                   ["exit 14..17 23 D04_R02 from_r03", "exit 39 10..13 D04_R05 from_r03 if=flag:d04_red,flag:d04_blue locked=\"The regulator crown is still at full pressure.\""],
                   ["spawn from_r02 15 22 up", "spawn from_r05 38 11 left"],
                   ["npc red_worker1 6 5 down sprite=worker talk=D04_OCC_WORKERS", "npc red_worker2 7 5 down sprite=worker talk=D04_OCC_WORKERS",
                    "chest D04_C_R03 34 18 I016 2", "npc lost_worker 30 16 left sprite=worker talk=D04_LOST_WORKER if=!flag:d04_lost"])
    g.rect(14, 20, 17, 23, ".")
    g.rect(37, 10, 39, 13, ".")
    g.e("save 35 14")
    return g.emit("D04_R03", name="Furnace Spine - Red Valve", encounters="D04", rate="0.8", legend=LEG, **DUN)


def d_r04():
    g = valve_room("D04_R04", "Blue Valve", "d04_blue", False,
                   ["exit 14..17 0 D04_R02 from_r04", "exit 39 10..13 D04_R05 from_r04 if=flag:d04_red,flag:d04_blue locked=\"The bridge to the regulator crown is retracted until the pressure is balanced.\""],
                   ["spawn from_r02 15 4 down", "spawn from_r05 38 11 left"],
                   ["npc blue_worker1 32 5 down sprite=worker talk=D04_OCC_WORKERS",
                    "chest D04_C_R04 5 18 W020 1"])
    g.rect(14, 0, 17, 3, ".")
    g.rect(14, 5, 17, 5, "=")          # catwalk over the pipe run from the north door
    g.rect(37, 10, 39, 13, ".")
    # clue-led secret: a maintenance hatch the valve plaque mentions
    g.rect(2, 21, 8, 23, "#")
    g.rect(3, 21, 6, 22, ",")
    g.put(4, 20, ",")
    g.e("chest D04_SECRET_CHEST 5 22 A004 1 acq=D04_SECRET")
    g.e("save 35 14")
    g.e("read 21 9 \"Valve plaque: 'Cold spares in the south-west hatch. Refill before the shift ends.'\"")
    return g.emit("D04_R04", name="Furnace Spine - Blue Valve", encounters="D04", rate="0.8", legend=LEG, **DUN)


def d_r05():
    g = Grid(40, 32)
    g.blob(20, 16, 16, 12, ".")
    g.rect(0, 10, 4, 13, ".")
    g.rect(0, 20, 4, 23, ".")
    g.rect(36, 14, 39, 17, ".")
    g.rect(16, 4, 23, 8, "m")
    for (x, y) in ((8, 6), (31, 6), (8, 26), (31, 26)):
        g.put(x, y, "P")
    g.e("trigger 14..25 14..15 scene=D04_COLOSSUS if=!flag:b04_done")
    g.e("spawn from_r03 1 11 right")
    g.e("spawn from_r04 1 21 right")
    g.e("spawn from_r06 38 15 left")
    g.e("exit 0 10..13 D04_R03 from_r05")
    g.e("exit 0 20..23 D04_R04 from_r05")
    g.e("exit 39 14..17 D04_R06 from_r05 if=flag:b04_done")
    return g.emit("D04_R05", name="Furnace Spine - Regulator Crown", encounters="none", legend=LEG, **DUN)


def d_r06():
    g = Grid(32, 24, "#")
    g.blob(16, 12, 14, 10, '"')
    g.rect(0, 10, 2, 13, ",")
    g.rect(10, 8, 22, 15, "g")
    g.rect(14, 10, 18, 13, "9")
    g.e("trigger 3..5 10..13 scene=D04_SC04 if=!ch:CH04")
    g.e("spawn from_r05 1 11 right")
    g.e("exit 0 10..13 D04_R05 from_r06")
    return g.emit("D04_R06", name="Furnace Spine - Cooling Garden", encounters="none", tileset="furnace", music="M022", zone="D04", region="R02", location="L_D04")


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "t03_d04.map"),
          [town(), canteen(), shop(), garden(), d_r01(), d_r02(), d_r03(), d_r04(), d_r05(), d_r06()], "T03 Cinderwake + D04 Furnace Spine")
    print("t03/d04 written")
