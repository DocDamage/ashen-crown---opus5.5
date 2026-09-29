"""T04 Bellharbor (bell quay, chartmaker lane, tide chapel) + customs house and the chase alleys (CH05)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOWN = dict(tileset="town_r03", music="M013", zone="T04", region="R03", location="L_T04")


def quay():
    g = Grid(44, 30, "~")
    g.rect(0, 0, 43, 17, ":")
    g.rect(0, 0, 43, 1, "#")
    g.rect(0, 0, 1, 17, "#")
    g.rect(6, 18, 9, 26, "d"); g.rect(20, 18, 23, 24, "d"); g.rect(34, 18, 37, 26, "d")
    g.put(8, 27, "6"); g.put(36, 27, "6")
    g.house(3, 3, 8, 4, chimney=2)          # customs house
    g.house(14, 3, 6, 2)
    g.house(24, 3, 7, 3)
    g.house(34, 3, 8, 5, chimney=6)         # tide chapel
    g.text(4, 12, "cc.rr   cc")
    g.text(26, 12, "rr.c")
    g.text(14, 9, "aaaa\nnnnn")
    for (x, y) in ((12, 16), (30, 16), (2, 10)):
        g.put(x, y, "l")
    g.put(21, 12, "j")                      # the harbor bell post (bell removed by the state)
    g.rect(42, 8, 43, 11, ":")              # east road: chartmaker lane
    g.rect(19, 0, 22, 1, ":")               # north road to the world
    g.e("spawn world 20 2 down")
    g.e("spawn from_lane 41 9 left")
    g.e("spawn from_customs 7 8 down")
    g.e("spawn from_chapel 38 9 down")
    g.e("spawn from_chase 20 14 up")
    g.e("spawn default 20 2 down")
    g.e("exit 19..22 0 WORLD l_t04")
    g.e("exit 43 8..11 T04_LANE from_quay")
    g.e("door 7 7 T04_CUSTOMS entry sfx=FX008")
    g.e("door 38 8 T04_CHAPEL entry sfx=FX009")
    g.e("npc pip_quay 22 16 left sprite=C08 talk=T04_PIP_OFFER if=!event:T04_PIP_OFFER")
    g.e("npc pot_child 23 12 left sprite=child talk=T04_POT_CHILD")
    g.e("npc sailor1 21 20 down sprite=sailor talk=T04_SAILOR")
    g.e("npc dockhand 35 16 left sprite=worker talk=T04_DOCKHAND")
    g.e("npc refugee1 10 15 right sprite=survivor talk=T04_REFUGEE")
    g.e("npc customs_guard 5 9 down sprite=guard talk=T04_CUSTOMS_GUARD if=!ch:CH05")
    g.e("npc fishwife 16 11 down sprite=baker talk=T04_FISHWIFE")
    g.e("shop 16 10 SHOP_T04")
    g.e("sign 19 12 \"The harbor bell post. The bell was removed 'pending inspection'.\"")
    return g.emit("T04_QUAY", name="Bellharbor - Bell Quay", **TOWN)


def lane():
    g = Grid(36, 22, "W")
    g.rect(0, 6, 35, 13, ":")
    g.rect(0, 0, 35, 2, "R")
    g.rect(0, 19, 35, 21, "R")
    for x in range(2, 34, 6):
        g.house(x, 3, 5, 2, windows=True)
        g.house(x, 14, 5, -1, windows=True)
    g.text(20, 11, "aaa")
    g.e("spawn from_quay 1 10 right")
    g.e("spawn from_jori 16 6 down")
    g.e("exit 0 8..13 T04_QUAY from_lane")
    g.e("door 16 5 T04_JORI entry sfx=FX008")
    g.e("npc chartmaker 22 10 down sprite=scholar talk=T04_CHARTMAKER")
    g.e("npc lane_kid 9 12 up sprite=child talk=T04_LANE_KID wander=1")
    g.e("npc lamplighter 30 9 down sprite=worker talk=T04_LAMPLIGHTER")
    g.e("trigger 14..18 7..8 scene=CH05_SC05 if=flag:t04_ledger,!ch:CH05")
    return g.emit("T04_LANE", name="Bellharbor - Chartmaker Lane", **TOWN)


def jori():
    g = Grid(14, 9)
    g.rect(1, 1, 12, 7, ".")
    g.text(1, 1, "kk?.nnnn.?kk")
    g.text(3, 4, "tt...tt")
    g.rect(6, 8, 7, 8, "+")
    g.e("spawn entry 6 7 up")
    g.e("exit 6..7 8 T04_LANE from_jori")
    g.e("npc jori_shop 6 2 down sprite=jori talk=T04_JORI")
    g.e("chest T04_C_JORI 11 6 I012 2")
    return g.emit("T04_JORI", name="Bellharbor - Jori's Chart Office", tileset="interior", music="M013", zone="T04", location="L_T04")


def chapel():
    g = Grid(20, 14)
    g.rect(1, 1, 18, 12, ".")
    g.text(3, 1, "j.j...j..j.j")
    g.text(4, 5, "bb.bb..bb.bb")
    g.text(4, 8, "bb.bb..bb.bb")
    g.put(9, 2, "@")
    g.rect(9, 13, 10, 13, "+")
    g.e("spawn entry 9 12 up")
    g.e("exit 9..10 13 T04_QUAY from_chapel")
    g.e("npc chaplain 11 3 down sprite=monk talk=T04_CHAPLAIN")
    g.e("inn 7 3 scene=T04_CHAPEL_REST")
    g.e("npc rest_keeper 7 2 down sprite=elder talk=T04_CHAPEL_REST")
    g.e("save 16 10")
    return g.emit("T04_CHAPEL", name="Bellharbor - Tide Chapel", tileset="interior_stone", music="M013", zone="T04", location="L_T04", save="true")


def customs():
    g = Grid(22, 14)
    g.rect(1, 1, 20, 12, ".")
    g.text(1, 1, "kkkkk....kkkk.kkkk")
    g.rect(1, 6, 12, 6, "n")          # counter splitting public side / records side
    g.put(6, 6, ".")                  # gate in the counter (blocked by the clerk)
    g.text(14, 3, "cc\ncc")
    g.rect(10, 13, 11, 13, "+")
    g.e("spawn entry 10 12 up")
    g.e("exit 10..11 13 T04_QUAY from_customs")
    g.e("npc customs_clerk 6 6 down sprite=clerk talk=T04_CUSTOMS_CLERK if=!flag:t04_distracted")
    g.e("npc customs_guard2 16 8 left sprite=guard talk=T04_CUSTOMS_GUARD2 if=!flag:t04_ledger")
    g.e("trigger 3 3 scene=T04_TAKE_LEDGER touch=0 if=!flag:t04_ledger")
    g.e("read 12 3 \"A confiscation shelf. Tags: 'forged passage papers, dock 3.' One ledger is chained, the chain unlocked.\"")
    return g.emit("T04_CUSTOMS", name="Bellharbor - Customs House", tileset="interior", music="M013", zone="T04", location="L_T04")


def chase():
    """Short chase through the back alleys; being caught returns you to the alley mouth (local retry)."""
    g = Grid(30, 20, "W")
    g.rect(1, 1, 28, 18, ":")
    # three alleys with visible guard posts; only the middle-then-east route is open
    g.rect(1, 6, 28, 6, "W"); g.rect(1, 12, 28, 12, "W")
    for x in (6, 15, 24):
        g.put(x, 6, ":"); g.put(x, 12, ":")
    g.rect(0, 16, 1, 18, ":")
    g.rect(28, 1, 29, 3, ":")
    for (x, y) in ((6, 5), (24, 11)):
        g.e(f"npc chase_guard_{x}_{y} {x} {y} down sprite=guard talk=T04_CAUGHT")
    g.e("trigger 6 7 scene=T04_CAUGHT")
    g.e("trigger 24 13 scene=T04_CAUGHT")
    g.e("sign 3 15 \"Pip, whispering: 'Watch where they stand. They never leave their posts.'\"")
    g.e("trigger 26..27 2..3 scene=CH05_CHASE_END")
    g.e("spawn start 1 17 right")
    g.e("spawn end 28 2 left")
    g.e("exit 28..29 1..3 T04_QUAY from_chase")
    return g.emit("T04_CHASE", name="Bellharbor - Back Alleys", tileset="town_r03", music="M025", zone="T04", location="L_T04", encounters="none")


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "t04.map"), [quay(), lane(), jori(), chapel(), customs(), chase()], "T04 Bellharbor")
    print("t04 written")
