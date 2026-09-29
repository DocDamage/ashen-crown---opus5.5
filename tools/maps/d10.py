"""D10 Crown Heart (CH22). Two four-person teams release alternating locks (west: pressure, east: names).
Neither team can trap the other: each lung has a swap bell that hands control to the other team at any time.
R04 reunites both teams (rest point, optional B16 alcove); R05 Crown Vessel (B12); R06 Open Sky."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUN = dict(tileset="crown", music="M028", zone="D10", region="R06", location="L_D10", phase="post")


def r01():
    g = Grid(40, 28, "~")
    g.rect(4, 8, 35, 23, "d")
    g.rect(17, 23, 22, 27, "d")           # south: Wayfarer / world
    g.rect(2, 12, 4, 15, ".")             # west lung door
    g.rect(35, 12, 37, 15, ".")           # east lung door
    g.rect(16, 3, 23, 8, ".")             # north: Concord Bridge (opens after both lungs)
    g.text(8, 10, "cc  rr")
    g.put(19, 13, "!")
    g.e("spawn world 19 26 up")
    g.e("spawn from_r02 5 13 right")
    g.e("spawn from_r03 34 13 left")
    g.e("spawn from_r04 19 4 down")
    g.e("spawn default 19 26 up")
    g.e("exit 17..22 27 WORLD_POST l_d10")
    g.e("trigger 16..23 18..19 scene=D10_DOCK if=!event:D10_DOCK")
    g.e("npc crew_d 14 20 right sprite=pilot talk=D10_CREW")
    g.e("switch split 24 15 scene=D10_SPLIT if=!flag:d10_done_lungs")
    g.e("exit 2 12..15 D10_R02 from_r01 if=flag:d10_split")
    g.e("exit 37 12..15 D10_R03 from_r01 if=flag:d10_split")
    g.e("exit 16..23 3 D10_R04 from_r01 if=flag:d10_done_lungs")
    g.e("save 8 20")
    g.e("heal 10 20")
    # clue-led secret: the dock master's locker
    g.rect(29, 18, 34, 22, "#"); g.rect(30, 19, 33, 21, "d"); g.put(29, 20, "d")
    g.e("chest D10_SECRET_CHEST 32 20 A010 1 acq=D10_SECRET")
    g.e("read 12 21 \"A tally on a crate: 'Dock master keeps a spare glass in the locker past the east bollards.'\"")
    g.decorate("cr", 8, 91, "d")
    return g.emit("D10_R01", name="Crown Heart - Accord Dock", encounters="none", save="true", **DUN)


def lung(mid, name, side, flags, scenes):
    g = Grid(32, 32)
    g.rect(3, 3, 28, 28, ".")
    if side == "west":
        g.rect(28, 14, 31, 17, ".")
        g.e("spawn from_r01 30 15 left")
        g.e("exit 31 14..17 D10_R01 from_r02 if=flag:d10_done_lungs")
    else:
        g.rect(0, 14, 3, 17, ".")
        g.e("spawn from_r01 1 15 right")
        g.e("exit 0 14..17 D10_R01 from_r03 if=flag:d10_done_lungs")
    g.e("spawn default 15 15 down")
    g.blob(15, 15, 5, 5, ",")
    # bone ribs arch over the lung; gaps keep every lock and door reachable
    for x in (6, 10, 20, 24):
        g.rect(x, 4, x, 10, "#"); g.rect(x, 20, x, 27, "#")
    g.text(12, 3, "*.*.*.*")
    g.decorate("vux*", 10, len(mid), ".")
    for (x, y) in ((8, 8), (22, 8), (8, 22), (22, 22)):
        g.put(x, y, "u")
    g.e(f"switch lockA {7} {15} scene={scenes[0]}")
    g.e(f"switch lockB {23} {15} scene={scenes[1]}")
    g.e(f"switch swapbell 15 5 scene=D10_SWAP")
    g.e("save 15 26")
    return g.emit(mid, name=name, encounters="D10", rate="0.6", save="true", **DUN)


def r04():
    g = Grid(32, 28, "~")
    g.rect(13, 0, 18, 27, "=")            # Concord Bridge
    g.rect(4, 10, 27, 17, ".")            # rest platform
    g.rect(0, 12, 4, 15, ".")             # west: B16 alcove (Q12)
    g.put(22, 12, "!")
    g.e("spawn from_r01 15 26 up")
    g.e("spawn from_r05 15 1 down")
    g.e("spawn from_alcove 1 13 right")
    g.e("spawn default 15 20 up")
    g.e("exit 13..18 27 D10_R01 from_r04")
    g.e("exit 13..18 0 D10_R05 from_r04")
    g.e("exit 0 12..15 D10_ALCOVE from_r04 if=item:K_LISTENING_PHRASE locked=\"A sealed alcove. Something inside is singing with no words. You'd need a phrase to be let in.\"")
    g.e("trigger 12..19 18..19 scene=D10_REUNITE if=!event:D10_REUNITE")
    g.e("save 8 12")
    g.e("heal 10 12")
    g.e("npc formation_d 24 14 left sprite=pilot talk=W_FORMATION")
    g.decorate("u", 4, 92, ".")
    return g.emit("D10_R04", name="Crown Heart - Concord Bridge", encounters="none", save="true", **DUN)


def alcove():
    g = Grid(24, 18)
    g.rect(3, 3, 20, 14, ".")
    g.rect(20, 7, 23, 10, ".")
    g.put(10, 5, "@")
    g.e("trigger 8..14 8..9 scene=Q12_CANTOR if=!flag:b16_done")
    g.e("spawn from_r04 22 8 left")
    g.e("spawn default 22 8 left")
    g.e("exit 23 7..10 D10_R04 from_alcove")
    return g.emit("D10_ALCOVE", name="Crown Heart - Silent Alcove", encounters="none", **DUN)


def r05():
    g = Grid(40, 32, "_")
    g.blob(20, 15, 16, 12, ".")
    g.rect(18, 26, 21, 31, ".")
    g.rect(18, 0, 21, 4, ".")
    g.text(15, 6, "*.m.m.*")
    g.e("trigger 14..25 16..17 scene=CH22_VESSEL if=!flag:b12_done")
    g.e("spawn from_r04 19 29 up")
    g.e("spawn from_r06 19 2 down")
    g.e("exit 18..21 31 D10_R04 from_r05")
    g.e("exit 18..21 0 D10_R06 from_r05 if=flag:b12_done")
    return g.emit("D10_R05", name="Crown Heart - Crown Vessel", encounters="none", legend={"_": "void"}, **DUN)


def r06():
    g = Grid(32, 24, "_")
    g.blob(16, 12, 12, 8, ".")
    g.rect(14, 19, 17, 23, ".")
    g.e("trigger 10..21 10..13 scene=CH22_SC11 if=!ch:CH22")
    g.e("spawn from_r05 15 21 up")
    g.e("spawn default 15 21 up")
    g.e("exit 14..17 23 D10_R05 from_r06")
    return g.emit("D10_R06", name="Crown Heart - Open Sky", encounters="none", legend={"_": "void"}, **DUN)


if __name__ == "__main__":
    maps = [r01(),
            lung("D10_R02", "Crown Heart - West Lung", "west", None, ["D10_W1", "D10_W2"]),
            lung("D10_R03", "Crown Heart - East Lung", "east", None, ["D10_E1", "D10_E2"]),
            r04(), alcove(), r05(), r06()]
    write(os.path.join(ROOT, "content_src", "maps", "d10_crown.map"), maps, "D10 Crown Heart")
    print("d10 written")
