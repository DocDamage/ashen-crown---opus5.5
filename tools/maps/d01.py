"""D01 Crown Quarry — six rooms (docs/05). Mechanic: drain routes, then release the rail brake without
opening the occupied lift. Seven workers, all recoverable in any order; no timers."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMMON = dict(tileset="quarry", music="M020", zone="D01", region="R01", location="L_D01")


def worker(g, n, x, y, d="down"):
    g.e(f"npc worker{n} {x} {y} {d} sprite=worker talk=D01_W{n} if=!flag:d01_w{n}")


def r01():
    g = Grid(40, 28)
    g.blob(20, 15, 17, 10, ",")
    g.rect(4, 6, 35, 23, ",")
    g.path([(19, 3), (19, 27)], ":", 2)
    g.rect(17, 2, 22, 3, "+")
    g.rect(16, 1, 23, 1, "^")
    g.hline(4, 3, 16, "^"); g.hline(4, 23, 36, "^")
    g.rect(18, 25, 21, 27, ":")
    # guard hut and supply shed
    g.house(5, 6, 6, -1, chimney=4)
    g.house(26, 6, 5, -1)
    g.text(5, 9, "cc.r")
    g.text(27, 9, "rr")
    # lift headframe (machinery) east
    g.rect(32, 8, 34, 11, "m")
    g.put(33, 12, "E")
    g.path([(24, 13), (33, 13)], ":")
    # lamps along the road
    for (x, y) in ((16, 8), (23, 8), (16, 16), (23, 16), (16, 22), (23, 22)):
        g.put(x, y, "l")
    g.scatter("o", 0.05, ",", 11, (4, 6, 35, 23))
    g.scatter("x", 0.03, ",", 12, (4, 6, 35, 23))
    # tutorial pump: flooded alcove with a payoff chest
    g.rect(29, 17, 34, 21, "~")
    g.rect(28, 16, 35, 16, "#")
    g.put(27, 19, ",")
    g.e("tileset_over 29..34 17..21 floor2 if=flag:d01_pump0")
    g.e("switch pump0 27 18 flag=d01_pump0 scene=D01_PUMP0")
    g.e("chest D01_C_R01 33 20 I001 2")
    g.e("spawn from_town 19 25 up")
    g.e("spawn from_r02 19 4 down")
    g.e("spawn default 19 25 up")
    g.e("exit 18..21 27 T01_PLATFORM from_quarry")
    g.e("exit 17..22 2 D01_R02 from_r01 if=flag:sc01_done")
    g.e("block 17..22 3 tile=gate if=!flag:sc01_done msg=\"The quarry gate is barred.\"")
    g.e("npc mara 20 5 down sprite=mara talk=D01_MARA_GATE if=!flag:sc01_done")
    g.e("npc inspector 18 6 down sprite=inspector talk=D01_INSPECTOR if=!ch:CH01")
    g.e("npc guard_g 15 10 right sprite=guard talk=D01_GATE_GUARD if=!ch:CH01")
    g.e("trigger 17..22 9..10 scene=D01_SC01 if=!flag:sc01_done")
    g.e("save 25 22")
    g.e("sign 21 24 \"CROWN QUARRY - Ministry of Relays. Lift yard: north-east. Pump handles restore the drains.\"")
    return g.emit("D01_R01", name="Crown Quarry - Gatehouse", encounters="none", save="true", **COMMON)


def r02():
    g = Grid(32, 32)
    g.rect(3, 3, 28, 28, ".")
    g.blob(16, 16, 12, 12, ".")
    g.rect(14, 28, 17, 31, ":")
    g.rect(28, 13, 31, 16, ":")
    g.rect(14, 0, 17, 3, ":")
    # lunch tables and benches
    for (x, y) in ((8, 16), (14, 16), (20, 16), (8, 21), (14, 21), (20, 21)):
        g.text(x, y, "btt\n.tt")
    g.text(5, 5, "rrc")
    g.text(24, 4, "cc")
    # Tessa's failing circuit
    g.rect(5, 9, 7, 9, "m")
    g.put(6, 8, "p")
    # rubble corner holding a worker
    g.text(23, 6, "xx.\nx..\n..x")
    g.scatter("o", 0.03, ".", 21, (3, 3, 28, 28))
    for (x, y) in ((4, 12), (27, 12), (4, 25), (27, 25)):
        g.put(x, y, "l")
    worker(g, 1, 24, 7, "down")
    g.e("npc tessa 7 11 up sprite=C02 talk=D01_TESSA if=!recruited:C02")
    g.e("npc guard_t 9 11 left sprite=guard talk=D01_TESSA_GUARD if=!recruited:C02")
    g.e("read 15 17 \"A lunch pail sits on the table. The shift is two hours late.\"")
    g.e("trigger 20..21 21 scene=D01_LIST touch=0 if=!item:K_WORKER_LIST")
    g.e("chest D01_C_R02 5 26 I004 1")
    g.e("spawn from_r01 15 29 up")
    g.e("spawn from_r03 29 14 left")
    g.e("spawn from_r04 15 2 down")
    g.e("exit 14..17 31 D01_R01 from_r02")
    g.e("exit 31 13..16 D01_R03 from_r02 if=recruited:C02 locked=\"Dain: The spur floods past here. We need someone who understands the pumps.\"")
    g.e("exit 14..17 0 D01_R04 from_r02 if=flag:d01_loftgate")
    g.e("block 14..17 1 tile=gate if=!flag:d01_loftgate msg=\"A service gate, latched from the loft side.\"")
    return g.emit("D01_R02", name="Crown Quarry - Lunch Gallery", encounters="D01E", rate="0.7", **COMMON)


def r03():
    g = Grid(40, 24)
    g.rect(1, 3, 38, 20, ",")
    g.blob(20, 12, 17, 8, "~")
    # shallow wading path (safe, visible)
    g.path([(1, 11), (8, 11), (8, 6), (20, 6), (20, 16), (30, 16), (30, 11), (39, 11)], "w", 2)
    g.blob(14, 14, 3, 2, ",", only="~")      # island with a worker
    g.path([(8, 11), (8, 14), (13, 14)], "w")
    g.rect(0, 11, 1, 12, "w")
    g.path([(33, 7), (33, 11)], "w")
    g.blob(33, 5, 4, 2, ",")                 # dry ledge
    # ore carts hiding the old drain (secret, clue-led)
    g.rect(34, 17, 38, 21, "#")
    g.text(33, 17, "2222")
    g.rect(34, 18, 37, 20, ",")
    g.put(33, 20, ",")
    g.path([(31, 17), (31, 20), (33, 20)], "w")
    g.e("chest D01_SECRET_CHEST 36 19 A001 1 acq=D01_SECRET")
    g.e("read 37 18 \"Scratched on the drain wall: 'Cale's crew was here. The stone hums at night.'\"")
    for (x, y) in ((2, 8), (2, 15), (37, 8)):
        g.put(x, y, "l")
    g.scatter("o", 0.05, ",", 31, (1, 3, 38, 20))
    worker(g, 2, 14, 13, "left")
    worker(g, 3, 34, 5, "down")
    g.e("chest D01_C_R03 31 4 I016 1")
    g.e("spawn from_r02 1 12 right")
    g.e("spawn from_r04 38 12 left")
    g.e("exit 0 11..12 D01_R02 from_r03")
    g.e("exit 39 11..12 D01_R04 from_r03")
    return g.emit("D01_R03", name="Crown Quarry - Flooded Spur", encounters="D01", rate="1.0", **COMMON)


def r04():
    g = Grid(32, 28)
    g.rect(2, 2, 29, 25, ".")
    g.rect(0, 11, 2, 12, ".")
    g.rect(14, 0, 17, 2, ".")
    g.rect(14, 25, 17, 27, ".")
    # drain channel (water) blocking the north passage until both pumps run together
    g.rect(10, 3, 21, 5, "~")
    g.e("tileset_over 10..21 3..5 floor2 if=flag:d01_drained")
    # ore cart parked on the track north (released by the rail brake)
    g.path([(15, 0), (15, 9)], ":", 2)
    g.e("block 15..16 7 tile=cart if=!flag:d01_brake msg=\"A loaded ore cart, held by the rail brake.\"")
    # pumps and gauge
    g.text(8, 8, "p")
    g.text(23, 8, "p")
    g.put(15, 10, "S")
    g.e("switch pump1 8 9 flag=d01_p1 scene=D01_PUMP1")
    g.e("switch pump2 23 9 flag=d01_p2 scene=D01_PUMP2")
    g.e("sign 15 10 \"Gauge: both pumps must run together. One crew holds a handle; the other pulls.\"")
    # levers: rail brake (left) and lift gate (right), with an explicit warning plate
    g.e("switch brake 24 19 flag=d01_brake scene=D01_BRAKE")
    g.e("switch liftlever 27 19 scene=D01_LIFTLEVER")
    g.e("sign 25 21 \"LEFT: rail brake. RIGHT: lift gate. Never open the lift with a crew aboard.\"")
    g.rect(26, 14, 29, 17, "E")
    g.text(4, 14, "cc\nr")
    g.text(19, 21, "tt")
    for (x, y) in ((3, 3), (28, 3), (3, 24), (28, 24)):
        g.put(x, y, "l")
    worker(g, 4, 5, 18, "right")
    worker(g, 5, 28, 12, "left")
    g.e("chest D01_C_R04 20 13 I017 2")
    g.e("save 5 22")
    g.e("heal 7 22")
    g.e("switch loftgate 13 25 flag=d01_loftgate scene=D01_LOFTGATE")
    g.e("spawn from_r03 1 12 right")
    g.e("spawn from_r05 15 1 down")
    g.e("spawn from_r02 15 26 up")
    g.e("exit 0 11..12 D01_R03 from_r04")
    g.e("exit 14..17 0 D01_R05 from_r04 if=flag:d01_drained,flag:d01_brake")
    g.e("exit 14..17 27 D01_R02 from_r04 if=flag:d01_loftgate")
    g.e("block 14..17 26 tile=gate if=!flag:d01_loftgate msg=\"The service gate to the gallery. A latch is on this side.\"")
    return g.emit("D01_R04", name="Crown Quarry - Pump Loft", encounters="D01", rate="0.8", save="true", **COMMON)


def r05():
    g = Grid(40, 32)
    g.blob(20, 16, 16, 12, ",")
    g.rect(17, 26, 22, 31, ":")
    g.rect(34, 6, 39, 9, ":")
    # heartglass face
    for (x, y) in ((8, 6), (12, 4), (28, 4), (32, 7), (6, 12), (34, 13), (10, 22), (30, 23)):
        g.put(x, y, "*")
    g.rect(16, 6, 23, 9, "m")   # extractor housing
    g.put(19, 10, "v"); g.put(20, 10, "v")
    g.scatter("x", 0.03, ",", 51, (5, 5, 34, 26))
    # side alcove with a worker
    g.rect(3, 17, 6, 20, ",")
    worker(g, 6, 4, 18, "right")
    g.e("read 30 20 \"A surveyor's note: 'Fossil organs show no response to stimulus.' Someone has underlined 'no' twice.\"")
    g.e("trigger 17..22 18 scene=D01_SC02 if=!flag:b01_done")
    g.e("spawn from_r04 19 29 up")
    g.e("spawn from_r06 37 7 left")
    g.e("exit 17..22 31 D01_R04 from_r05")
    g.e("exit 39 6..9 D01_R06 from_r05 if=flag:b01_done locked=\"The yard passage is sealed by the extractor's pressure door.\"")
    return g.emit("D01_R05", name="Crown Quarry - Heartglass Face", encounters="none", dark="true", **COMMON)


def r06():
    g = Grid(32, 24)
    g.rect(2, 3, 29, 20, ",")
    g.rect(0, 7, 2, 9, ":")
    g.rect(20, 5, 25, 10, "E")   # the lift platform
    g.path([(3, 8), (19, 8)], ":")
    g.text(6, 13, "cc.c\nr..r")
    g.text(12, 4, "mm")
    for (x, y) in ((4, 4), (27, 4), (4, 19), (27, 19)):
        g.put(x, y, "l")
    worker(g, 7, 8, 15, "up")
    # rescued workers gather here
    for n, (x, y) in enumerate(((17, 12), (18, 13), (16, 14), (19, 15), (15, 12), (18, 16), (16, 16)), start=1):
        g.e(f"npc rescued{n} {x} {y} up sprite=worker talk=D01_RESCUED if=flag:d01_w{n},!ch:CH01")
    g.e("npc mara_yard 13 10 right sprite=mara talk=D01_MARA_YARD if=flag:b01_done,!ch:CH01")
    g.e("trigger 3..5 7..9 scene=D01_YARD_ARRIVE if=flag:b01_done,!event:D01_YARD_ARRIVE")
    g.e("spawn from_r05 3 8 right")
    g.e("exit 0 7..9 D01_R05 from_r06")
    return g.emit("D01_R06", name="Crown Quarry - Lift Yard", encounters="none", **COMMON)


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "d01_quarry.map"), [r01(), r02(), r03(), r04(), r05(), r06()],
          "D01 Crown Quarry (generated by tools/maps/d01.py)")
    print("d01 written")
