"""D09 Sable Conduit (CH11-CH12). Mechanic: disable three synchronization relays while keeping the
evacuation lifts powered. R04 writes the protected pre-transition backup. R06 is the Crown Dais."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUN = dict(tileset="conduit", music="M020", zone="D09", region="R01", location="L_D09")


def r01():
    g = Grid(40, 28)
    g.rect(3, 4, 36, 23, ".")
    g.rect(17, 23, 22, 27, ".")          # south: world
    g.rect(0, 6, 3, 9, ".")               # west: south relay
    g.rect(36, 6, 39, 9, ".")             # east: north relay
    g.rect(8, 11, 31, 14, "~")            # the old aqueduct channel
    g.rect(18, 11, 21, 14, "=")
    g.rect(6, 11, 7, 14, "=")
    for x in (10, 16, 24, 30):
        g.put(x, 5, "p")
    g.text(30, 18, "E\nE")                # evacuation lift, powered
    g.put(12, 20, "u"); g.put(27, 20, "u")
    g.e("spawn world 19 26 up")
    g.e("spawn from_r02 1 7 right")
    g.e("spawn from_r03 38 7 left")
    g.e("spawn default 19 26 up")
    g.e("exit 17..22 27 WORLD l_d09")
    g.e("exit 0 6..9 D09_R02 from_r01 if=event:D09_ENTER")
    g.e("exit 39 6..9 D09_R03 from_r01 if=event:D09_ENTER")
    g.e("trigger 17..22 20..21 scene=D09_ENTER if=!event:D09_ENTER")
    g.e("npc lift_crew 29 19 left sprite=worker talk=D09_LIFT_CREW")
    g.e("read 22 21 \"Aqueduct plate: 'Conduit service - three relay stations. Lift power is fed separately. Never cut the lifts.'\"")
    g.e("save 6 20")
    g.e("heal 8 20")
    g.decorate("ux", 8, 93, ".")
    return g.emit("D09_R01", name="Sable Conduit - Old Aqueduct", encounters="none", save="true", **DUN)


def r02():
    g = Grid(32, 32)
    g.rect(3, 3, 28, 28, ".")
    g.rect(28, 20, 31, 23, ".")           # east: back to R01
    g.rect(14, 0, 17, 3, ".")             # north: Soldiers' Walk
    g.blob(15, 15, 5, 4, ",")
    g.put(15, 13, "*")                    # the relay
    g.put(14, 13, "m"); g.put(16, 13, "m")
    for (x, y) in ((6, 6), (24, 6), (6, 24), (24, 24)):
        g.put(x, y, "v")
    g.e("switch relay_s 15 14 flag=d09_relay_s scene=D09_RELAY_S")
    g.e("chest D09_C_R02 5 26 I019 2")
    g.e("spawn from_r01 30 21 left")
    g.e("spawn from_r04 15 1 down")
    g.e("exit 31 20..23 D09_R01 from_r02")
    g.e("exit 14..17 0 D09_R04 from_r02")
    return g.emit("D09_R02", name="Sable Conduit - South Relay", encounters="D09", rate="0.8", **DUN)


def r03():
    g = Grid(40, 24)
    g.rect(2, 3, 37, 20, ".")
    g.rect(0, 16, 2, 19, ".")             # west: back to R01
    g.rect(18, 0, 21, 3, ".")             # north: Soldiers' Walk
    g.rect(24, 5, 33, 9, "#")             # lift shaft housing
    g.rect(26, 6, 31, 8, "E")
    g.put(28, 9, "+")
    g.rect(6, 6, 7, 17, "p")
    g.put(12, 12, "*"); g.put(12, 11, "m")
    g.e("switch lift_route 14 12 flag=d09_relay_n scene=D09_RELAY_N")
    g.e("npc lift_riders 28 10 up sprite=survivor talk=D09_LIFT_RIDERS if=!flag:d09_relay_n")
    g.e("npc lift_riders2 28 10 up sprite=survivor talk=D09_LIFT_SAFE if=flag:d09_relay_n")
    g.e("chest D09_C_R03 35 18 G022 1")
    g.e("spawn from_r01 1 17 right")
    g.e("spawn from_r04 19 1 down")
    g.e("exit 0 16..19 D09_R01 from_r03")
    g.e("exit 18..21 0 D09_R04 from_r03")
    return g.emit("D09_R03", name="Sable Conduit - North Relay", encounters="D09", rate="0.8", **DUN)


def r04():
    g = Grid(32, 28)
    g.rect(3, 4, 28, 24, ".")
    g.rect(0, 12, 3, 15, ".")             # west door -> R02 (the south relay route climbs here)
    g.rect(28, 12, 31, 15, ".")           # east door -> R03
    g.rect(14, 0, 17, 4, ".")             # north -> Marshal Bridge
    g.rect(5, 17, 12, 22, "#")            # collapsed barracks with the soldiers
    g.rect(6, 18, 11, 21, ",")
    g.put(12, 19, "+")
    # clue-led secret: behind the ration cage
    g.rect(22, 18, 27, 22, "#")
    g.rect(23, 19, 26, 21, ".")
    g.put(22, 20, ".")
    g.e("chest D09_SECRET_CHEST 25 20 A009 1 acq=D09_SECRET")
    g.e("read 18 21 \"Ration chit, pinned to a crate: 'Quartermaster's spare badge is in the cage by the east wall. Mind the loose bar on the west side.'\"")
    g.e("npc trapped 8 19 right sprite=soldier talk=D09_SOLDIERS if=!flag:d09_rescue")
    g.e("npc rescued 14 8 down sprite=soldier talk=D09_SOLDIERS_AFTER if=flag:d09_rescue")
    g.e("trigger 13..18 5..6 scene=D09_WARNING if=!event:D09_WARNING")
    g.e("save 20 8")
    g.e("heal 22 8")
    g.e("spawn from_r02 1 13 right")
    g.e("spawn from_r03 30 13 left")
    g.e("spawn from_r05 15 1 down")
    g.e("exit 0 12..15 D09_R02 from_r04")
    g.e("exit 31 12..15 D09_R03 from_r04")
    g.e("exit 14..17 0 D09_R05 from_r04 if=flag:d09_relay_s,flag:d09_relay_n,event:D09_WARNING "
        "locked=\"Two synchronization relays still hold the bridge doors. Release the south relay and reroute the north lift.\"")
    g.decorate("xcr", 10, 94, ".")
    return g.emit("D09_R04", name="Sable Conduit - Soldiers' Walk", encounters="none", save="true", **DUN)


def r05():
    g = Grid(40, 32)
    g.rect(0, 0, 39, 31, "_")
    g.rect(16, 3, 23, 28, "=")            # the Marshal Bridge
    g.rect(12, 12, 27, 19, ".")           # command platform
    g.rect(18, 28, 21, 31, ".")
    g.rect(18, 0, 21, 3, ".")
    g.put(13, 13, "*"); g.put(26, 13, "*")
    g.e("trigger 16..23 20..21 scene=D09_VOSS if=!flag:b09_done")
    g.e("switch relay_bridge 19 13 flag=d09_relay_b scene=D09_RELAY_B if=flag:b09_done")
    g.e("save 17 25")
    g.e("heal 22 25")
    g.e("spawn from_r04 19 29 up")
    g.e("spawn from_r06 19 2 down")
    g.e("exit 18..21 31 D09_R04 from_r05")
    g.e("exit 18..21 0 D09_R06 from_r05 if=flag:d09_relay_b locked=\"The third relay still drives the dais door.\"")
    return g.emit("D09_R05", name="Sable Conduit - Marshal Bridge", encounters="none", **DUN)


def r06():
    g = Grid(32, 24)
    g.rect(3, 3, 28, 20, ".")
    g.rect(14, 20, 17, 23, ".")
    g.blob(15, 9, 7, 4, ",")
    g.text(12, 5, "*.m.*")
    g.put(15, 4, "@")
    g.e("trigger 12..19 13..14 scene=CH12_DAIS if=!ch:CH12")
    g.e("spawn from_r05 15 22 up")
    g.e("exit 14..17 23 D09_R05 from_r06")
    return g.emit("D09_R06", name="Sable Conduit - Crown Dais", encounters="none", **DUN)


def esc():
    """CH12 escape: short playable collapse corridor. Falling stone pushes you back a step (local retry)."""
    g = Grid(44, 20)
    g.rect(2, 7, 41, 12, ".")
    g.rect(40, 5, 43, 14, ",")
    g.text(42, 9, "E\nE")
    for x in range(6, 40, 4):
        g.put(x, 6, "x"); g.put(x + 1, 13, "x")
    g.e("hazard 8..11 7..12 period=2.4 on=0.9 phase=0")
    g.e("hazard 16..19 7..12 period=2.4 on=0.9 phase=1.2")
    g.e("hazard 24..27 7..12 period=2.0 on=0.8 phase=0.4")
    g.e("hazard 32..35 7..12 period=2.0 on=0.8 phase=1.4")
    g.e("sign 4 7 \"The stone falls in waves. Shaking dust shows where the next fall will land.\"")
    g.e("trigger 40..41 7..12 scene=CH12_FALL if=!ch:CH12")
    g.e("spawn start 3 9 right")
    g.e("spawn default 3 9 right")
    return g.emit("D09_ESC", name="Sable Conduit - Collapsing Aqueduct", encounters="none", tileset="conduit",
                  music="M027", zone="D09", region="R01", location="L_D09")


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "d09_conduit.map"), [r01(), r02(), r03(), r04(), r05(), r06(), esc()],
          "D09 Sable Conduit")
    print("d09 written")
