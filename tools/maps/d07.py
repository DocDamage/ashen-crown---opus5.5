"""D07 Whitebone Redoubt (pre) + post-state sanctuary D07P (CH19 Sable reunion).
Mechanic: replace binding sigils with consent keys recorded from actual occupants."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMMON = dict(tileset="whitebone", music="M020", zone="D07", region="R05", location="L_D07")
PRISONERS = [("Hallen", 5), ("Ysa", 12), ("Corvin", 19)]


def r01():
    g = Grid(40, 28, "q") if False else Grid(40, 28, "#")
    g.rect(2, 10, 37, 25, "q")
    g.rect(2, 2, 37, 9, "#")
    g.rect(15, 2, 24, 9, ".")
    g.rect(17, 0, 22, 2, "+")
    g.rect(18, 25, 21, 27, "q")
    g.path([(19, 26), (19, 3)], ".", 2)
    for (x, y) in ((13, 8), (26, 8)):
        g.put(x, y, "u")
    g.e("spawn world 19 26 up")
    g.e("spawn from_r02 19 3 down")
    g.e("spawn default 19 26 up")
    g.e("exit 18..21 27 WORLD l_d07")
    g.e("exit 17..22 0 D07_R02 from_r01 if=event:D07_SABLE_GATE")
    g.e("npc sable_gate 20 12 down sprite=C07 talk=D07_SABLE_GATE if=!event:D07_SABLE_GATE")
    g.e("trigger 17..22 14..15 scene=D07_SABLE_GATE if=!event:D07_SABLE_GATE")
    g.e("save 8 20")
    return g.emit("D07_R01", name="Whitebone Redoubt - White Gate", encounters="none", save="true", **COMMON)


def r02():
    g = Grid(32, 32)
    g.rect(2, 2, 29, 29, ".")
    for y in range(4, 26, 4):
        g.text(4, y, "BB.BB.BB")
        g.text(20, y, "BB.BB.BB")
    g.rect(14, 29, 17, 31, ".")
    g.rect(14, 0, 17, 2, ".")
    g.rect(29, 14, 31, 17, ".")
    g.e("read 7 6 \"Identical grey uniforms on every bunk. Under one pillow: a child's drawing of a boat.\"")
    g.e("read 23 14 \"A footlocker: regulation kit, and a pressed flower nobody issued.\"")
    g.e("read 7 22 \"A bunk card: 'Warden 3'. Scratched beside it: 'Tam'.\"")
    g.e("chest D07_C_R02 26 26 I007 2")
    g.e("spawn from_r01 15 29 up")
    g.e("spawn from_r03 15 1 down")
    g.e("spawn from_r04 30 15 left")
    g.e("exit 14..17 31 D07_R01 from_r02")
    g.e("exit 14..17 0 D07_R03 from_r02")
    g.e("exit 31 14..17 D07_R04 from_r02")
    return g.emit("D07_R02", name="Whitebone Redoubt - Barracks", encounters="D07", rate="0.7", **COMMON)


def r03():
    g = Grid(40, 24)
    g.rect(2, 3, 37, 20, ".")
    g.rect(18, 20, 21, 23, ".")
    g.rect(37, 9, 39, 12, ".")
    for i, (name, x) in enumerate(PRISONERS):
        g.put(8 + i * 11, 4, "8")
        g.e(f"read {8 + i * 11} 5 scene=D07_SEAL{i + 1} \"x\"")
        g.put(8 + i * 11, 5, "S")
    g.rect(4, 12, 35, 12, "k")
    g.e("read 30 16 \"A standing order: 'Seals are keyed to warrant numbers. Names are not required.'\"")
    g.e("spawn from_r02 19 22 up")
    g.e("spawn from_r04 38 10 left")
    g.e("exit 18..21 23 D07_R02 from_r03")
    g.e("exit 39 9..12 D07_R04 from_r03")
    return g.emit("D07_R03", name="Whitebone Redoubt - Names Hall", encounters="D07", rate="0.5", **COMMON)


def r04():
    g = Grid(32, 28)
    g.rect(2, 2, 29, 25, ".")
    for i, (name, x) in enumerate(PRISONERS):
        cx = 4 + i * 9
        g.rect(cx, 3, cx + 6, 8, "#")
        g.rect(cx + 1, 4, cx + 5, 7, ",")
        g.put(cx + 3, 8, "{")
        g.e(f"tileset_over {cx + 3} 8 floor if=flag:d07_open{i + 1}")
        g.e(f"npc prisoner{i + 1} {cx + 3} 6 down sprite=survivor talk=D07_PRISONER{i + 1}")
        g.e(f"switch lock{i + 1} {cx + 2} 9 flag=d07_open{i + 1} scene=D07_LOCK{i + 1}")
    g.rect(0, 12, 2, 15, ".")
    g.rect(0, 20, 2, 23, ".")
    g.rect(14, 25, 17, 27, ".")
    g.e("chest D07_C_R04 26 22 G010 1")
    # clue-led secret behind the guard post
    g.rect(24, 16, 29, 19, "#")
    g.rect(25, 17, 28, 18, ".")
    g.put(24, 18, ".")
    g.e("chest D07_SECRET_CHEST 27 17 A007 1 acq=D07_SECRET")
    g.e("read 20 20 \"Guard roster: 'Night token in the post's back locker. Return by dawn.'\"")
    g.e("save 6 22")
    g.e("heal 8 22")
    g.e("spawn from_r03 1 13 right")
    g.e("spawn from_r02 1 21 right")
    g.e("spawn from_r05 15 26 up")
    g.e("exit 0 12..15 D07_R03 from_r04")
    g.e("exit 0 20..23 D07_R02 from_r04")
    g.e("exit 14..17 27 D07_R05 from_r04 if=flag:d07_open1,flag:d07_open2,flag:d07_open3 locked=\"Sable: Not until every cell is open. That was the agreement.\"")
    return g.emit("D07_R04", name="Whitebone Redoubt - Binding Cells", encounters="none", save="true", **COMMON)


def r05():
    g = Grid(40, 32)
    g.blob(20, 16, 15, 12, ".")
    g.blob(20, 16, 9, 7, "q")
    g.rect(18, 0, 21, 4, ".")
    g.rect(36, 14, 39, 17, ".")
    for a in ((10, 8), (30, 8), (10, 24), (30, 24)):
        g.put(a[0], a[1], "u")
    g.e("trigger 14..25 10 scene=D07_ADJUDICATOR if=!flag:b07_done")
    g.e("spawn from_r04 19 1 down")
    g.e("spawn from_r06 38 15 left")
    g.e("exit 18..21 0 D07_R04 from_r05")
    g.e("exit 39 14..17 D07_R06 from_r05 if=flag:b07_done")
    return g.emit("D07_R05", name="Whitebone Redoubt - Tribunal Ring", encounters="none", **COMMON)


def r06():
    g = Grid(32, 24, "q")
    g.rect(0, 0, 31, 3, "#")
    g.rect(0, 10, 2, 13, ".")
    g.rect(14, 20, 17, 23, "q")
    g.scatter("T", 0.05, "q", 91)
    g.e("trigger 3..5 10..13 scene=CH08_SNOW if=!ch:CH08")
    g.e("spawn from_r05 1 11 right")
    g.e("exit 0 10..13 D07_R05 from_r06")
    g.e("exit 14..17 23 WORLD l_d07 if=ch:CH08")
    return g.emit("D07_R06", name="Whitebone Redoubt - Snow Exit", encounters="none", **COMMON)


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "d07_whitebone.map"), [r01(), r02(), r03(), r04(), r05(), r06()], "D07 Whitebone")
    print("d07 written")
