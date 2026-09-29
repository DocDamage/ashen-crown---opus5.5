"""Post-state Crown March: T01_POST (flooded Brackenford), D01_MEMORIAL (surface memorial; underground sealed),
D03P (flooded Rootward, CH14: reconnect visible safe routes, Ash-Tide Warden B11)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T01 = dict(tileset="town_r01", music="M010", zone="T01", region="R01", location="L_T01", phase="post")
D03 = dict(tileset="grove_flood", music="M021", zone="D03P", region="R01", location="L_D03", phase="post")


def t01_post():
    g = Grid(44, 30, "~")
    g.rect(2, 2, 18, 27, '"')            # west bank (bunkhouse shelter)
    g.rect(26, 2, 41, 27, '"')           # east bank (bakery depot)
    g.rect(18, 12, 26, 13, "=")          # the bakery footbridge
    g.rect(18, 22, 26, 22, "=")          # new route (after CH14)
    g.e("block 18..26 22 tile=water if=!ch:CH14 msg=\"Nera's survivors are meant to rebuild this crossing. Not yet.\"")
    g.house(4, 3, 9, 4, chimney=3)       # bunkhouse (shelter)
    g.house(29, 3, 8, 3, chimney=6)      # bakery (depot)
    g.text(30, 8, "cc2rr")
    g.text(5, 10, "]] ]]")
    g.text(4, 18, "gggg")
    g.text(32, 18, "3333")
    g.rect(0, 13, 2, 16, ":")
    g.rect(41, 13, 43, 16, ":")
    g.put(10, 22, "y")                   # workers' memorial stone (Q01 inscription)
    g.e("spawn world 1 14 right")
    g.e("spawn east 42 14 left")
    g.e("spawn default 1 14 right")
    g.e("exit 0 13..16 WORLD_POST l_t01")
    g.e("exit 43 13..16 WORLD_POST l_t01")
    g.e("npc forewoman 8 13 right sprite=mara talk=T01P_MARA")
    g.e("npc shelter_keep 12 9 down sprite=elder talk=T01P_SHELTER")
    g.e("inn 7 8 scene=T01P_INN")
    g.e("npc depot 33 12 left sprite=baker talk=T01P_DEPOT")
    g.e("shop 32 12 SHOP_T01")
    g.e("npc camp_west 6 20 right sprite=farmer talk=T01P_CAMP_WEST")
    g.e("npc camp_east 36 21 left sprite=worker talk=T01P_CAMP_EAST")
    g.e("npc storekeeper 28 16 down sprite=keeper talk=T01P_STOREKEEPER")
    g.e("npc salvager 38 9 left sprite=worker talk=T01P_SALVAGE if=ch:CH14")
    g.e("read 10 23 \"A memorial stone. The quarry ledger's numbers have been chiselled off; names are being cut in their place, one at a time.\"")
    g.e("save 14 15")
    g.decorate("cr31g", 20, 88, '"')
    return g.emit("T01_POST", name="Brackenford - Divided by the Flood", save="true", **T01)


def d01_memorial():
    g = Grid(36, 24, '"')
    g.rect(2, 2, 33, 21, ":")
    g.rect(10, 3, 25, 6, "#")
    g.rect(16, 6, 19, 6, "G")            # sealed quarry gate
    g.text(8, 12, "y.y.y.y.y")
    g.put(26, 16, "x"); g.put(27, 16, "x"); g.put(28, 17, "x")
    g.rect(15, 21, 20, 23, ":")
    g.e("spawn world 17 22 up")
    g.e("spawn default 17 22 up")
    g.e("exit 15..20 23 WORLD_POST l_d01")
    g.e("read 17 7 \"The quarry gate is sealed with poured stone. The underground stays shut.\"")
    g.e("read 12 13 \"Memorial stones. Some bear names; most still bear numbers.\"")
    g.e("switch record1 8 16 scene=Q01_RECORD1 if=q:Q01:ACTIVE")
    g.e("switch record2 27 18 scene=Q01_RECORD2 if=q:Q01:ACTIVE")
    g.e("switch record3 30 8 scene=Q01_RECORD3 if=q:Q01:ACTIVE")
    g.e("npc family1 22 15 left sprite=elder talk=Q01_FAMILY")
    return g.emit("D01_MEMORIAL", name="Crown Quarry - Surface Memorial", tileset="quarry", music="M017", zone="D01", region="R01",
                  location="L_D01", encounters="none", phase="post")


def d03p_r01():
    g = Grid(40, 28, "~")
    g.blob(20, 20, 16, 7, ";")
    g.rect(17, 23, 22, 27, ";")
    g.rect(4, 14, 14, 20, ".")            # survivors' camp on high roots
    g.text(5, 15, "]] ]]")
    g.put(12, 18, "!")
    g.rect(24, 6, 27, 18, "w")            # shallow ford north
    g.rect(24, 0, 27, 6, "w")
    g.e("spawn world 19 26 up")
    g.e("spawn from_r02 25 1 down")
    g.e("spawn default 19 26 up")
    g.e("exit 17..22 27 WORLD_POST l_d03")
    g.e("exit 24..27 0 D03P_R02 from_r01")
    g.e("trigger 14..22 16..18 scene=CH14_CAMP if=ch:CH13,!event:CH14_CAMP")
    g.e("npc nera_camp 9 17 right sprite=C05 talk=CH14_NERA_CAMP if=!ch:CH14")
    g.e("npc mara_camp 11 16 down sprite=mara talk=CH14_MARA if=event:CH14_CAMP,!ch:CH14")
    g.e("npc camp_child 6 18 up sprite=child talk=CH14_CHILD")
    g.e("npc camp_elder 13 15 left sprite=elder talk=CH14_ELDER")
    g.e("save 8 20")
    g.e("heal 10 20")
    g.decorate("%;x", 10, 89, ";")
    return g.emit("D03P_R01", name="Flooded Rootward - Survivors' Rise", encounters="none", save="true", **D03)


def d03p_r02():
    g = Grid(40, 32, "~")
    g.rect(24, 28, 27, 31, "w")           # south: back to camp
    g.rect(2, 22, 37, 27, ";")
    g.rect(2, 4, 37, 9, ";")
    g.rect(18, 0, 21, 4, "w")             # north: warden's current
    # three crossings (visible routes) - each reconnected by its own sluice lever
    for i, x in enumerate((7, 19, 31)):
        g.rect(x, 10, x + 1, 21, "~")
        g.e(f"tileset_over {x}..{x+1} 10..21 bridge if=flag:d03p_route{i+1}")
        g.e(f"switch route{i+1} {x + 3} 24 flag=d03p_route{i+1} scene=CH14_ROUTE{i+1}")
    g.e("read 12 25 \"Nera's chalk on a stump: three crossings, three sluice levers. 'Lift each lever to raise its walkway. The current eats whichever route stays low.'\" if=!q:Q05:ACTIVE")
    g.e("read 12 25 \"x\" scene=Q05_SURVEY if=q:Q05:ACTIVE")
    g.e("chest D03P_C_R02 35 5 I002 2")
    g.e("save 16 5")
    g.e("heal 23 5")
    g.e("spawn from_r01 25 29 up")
    g.e("spawn from_r03 19 1 down")
    g.e("exit 24..27 31 D03P_R01 from_r02")
    g.e("exit 18..21 0 D03P_R03 from_r02 if=flag:d03p_route1,flag:d03p_route2,flag:d03p_route3 "
        "locked=\"The current is too strong while any crossing is down. Raise all three walkways.\"")
    return g.emit("D03P_R02", name="Flooded Rootward - Three Crossings", encounters="D03P", rate="0.8", **D03)


def d03p_r03():
    g = Grid(36, 28, "~")
    g.blob(18, 14, 14, 10, ";")
    g.rect(16, 24, 19, 27, "w")
    g.rect(15, 3, 20, 6, "&")             # the diverted sluice gate
    g.e("trigger 12..23 12..13 scene=CH14_WARDEN if=!flag:b11_done")
    g.e("trigger 12..23 18..19 scene=CH14_NERA if=flag:b11_done,!ch:CH14")
    g.e("spawn from_r02 17 25 up")
    g.e("spawn default 17 25 up")
    g.e("exit 16..19 27 D03P_R02 from_r03")
    return g.emit("D03P_R03", name="Flooded Rootward - Warden's Current", encounters="none", **D03)


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "post_r01.map"),
          [t01_post(), d01_memorial(), d03p_r01(), d03p_r02(), d03p_r03()], "Post-state Crown March")
    print("post_r01 written")
