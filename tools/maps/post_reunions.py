"""Post-state reunion destinations (CH17-CH19, any order after CH16) and Nacre for the Ash Accord (CH20).
D06P High Aerie mooring, T05_POST; T02_SQUARE_POST, T02_CANALS, T02_REGISTRY_POST, D02P_ECHO (Q11 alcove);
D07P Whitebone sanctuary; T06_POST Nacre."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKYLEG = {"_": "void", "}": "chain", "7": "cable"}


# ---------------------------------------------------------------- CH17 High Aerie
def d06p_r01():
    g = Grid(44, 30, "_")
    g.blob(10, 22, 8, 6, ".")              # landing island (south-west)
    g.rect(8, 27, 12, 29, ".")
    g.blob(33, 8, 8, 5, ".")               # cliff settlement island (north-east)
    g.blob(33, 22, 6, 4, ".")              # mooring island (south-east)
    # lanes between islands (changed topology: the snapped chain is now a pair of bridges)
    g.rect(17, 21, 28, 22, "=")
    g.rect(32, 13, 33, 18, "=")
    g.rect(10, 9, 26, 10, "=")
    g.blob(8, 9, 3, 3, ".")
    g.rect(8, 11, 9, 16, "=")
    g.e("hazard 20..25 21..22 period=4 on=1.2 phase=0")
    g.e("hazard 32..33 14..17 period=3.6 on=1.2 phase=1.5")
    g.e("hazard 14..22 9..10 period=4 on=1.3 phase=2.5")
    # three ballast anchors, each reachable
    g.e("switch anchor1 8 8 flag=d06p_a1 scene=CH17_ANCHOR1")
    g.e("switch anchor2 38 7 flag=d06p_a2 scene=CH17_ANCHOR2")
    g.e("switch anchor3 37 23 flag=d06p_a3 scene=CH17_ANCHOR3")
    g.put(34, 21, "}"); g.put(35, 21, "}")
    g.text(30, 5, "]]  ]]")
    g.e("sign 12 20 \"Pennants lift before each gust. Cross between them. Each ballast anchor steadies the mooring a little more.\"")
    g.e("trigger 6..14 23..25 scene=CH17_ARRIVE if=ch:CH16,!event:CH17_ARRIVE")
    g.e("npc corren_m 33 22 right sprite=C03 talk=CH17_CORREN if=!ch:CH17")
    g.e("npc edda_m 30 23 right sprite=edda talk=CH17_EDDA if=!ch:CH17")
    g.e("npc evac1 29 8 down sprite=child talk=CH17_EVAC")
    g.e("npc evac2 36 9 left sprite=elder talk=CH17_EVAC")
    g.e("npc crew_m 12 22 up sprite=pilot talk=CH17_CREW")
    g.e("save 6 20")
    g.put(4, 24, "x")
    g.e("read 5 24 \"Wreckage from a rescue basket.\" scene=Q03_RECORDER")
    g.e("npc q3_survivor 36 10 left sprite=survivor talk=Q03_SURVIVOR if=q:Q03:ACTIVE")
    g.e("switch marker 14 24 scene=Q03_MARKER if=q:Q03:ACTIVE")
    g.e("spawn world 10 28 up")
    g.e("spawn default 10 28 up")
    g.e("exit 8..12 29 WORLD_POST l_d06")
    g.decorate("cr", 6, 85, ".")
    return g.emit("D06P_R01", name="Skyspine - Broken Chain Mooring", tileset="sky", music="M014", zone="D06P", region="R04",
                  location="L_D06", encounters="D06P", rate="0.5", save="true", phase="post", legend=SKYLEG)


def t05_post():
    g = Grid(44, 30, "_")
    g.rect(2, 4, 41, 25, ":")
    g.rect(19, 25, 24, 29, ":")
    g.house(4, 5, 8, 4, chimney=2)         # returners' hall
    g.house(28, 5, 7, 3)
    g.house(33, 16, 8, 4)
    g.text(18, 8, "<  <  <")               # windmills replace the suspended engines
    g.put(12, 12, "y")                     # memorial
    g.put(14, 12, "8")                     # the returners' wall (added by Q03)
    g.e("tileset_over 14 12 floor if=!flag:q03_wall")
    for (x, y) in ((14, 20), (28, 20)):
        g.put(x, y, "l")
    g.e("spawn world 21 28 up")
    g.e("spawn default 21 28 up")
    g.e("exit 19..24 29 WORLD_POST l_t05")
    g.e("inn 7 10 scene=T05P_INN")
    g.e("npc hall_p 9 10 down sprite=elder talk=T05P_INN")
    g.e("npc edda_p 18 13 down sprite=edda talk=T05P_EDDA")
    g.e("npc pilot_p 13 14 left sprite=pilot talk=T05P_PILOT")
    g.e("npc windmill 22 11 down sprite=worker talk=T05P_WIND")
    g.e("npc kid_p 30 21 left sprite=child talk=T05P_KID wander=1")
    g.e("npc trader_p 26 18 up sprite=keeper talk=T05P_SHOP")
    g.e("shop 26 17 SHOP_T05")
    g.e("npc survivor_p 36 13 left sprite=survivor talk=T05P_SURVIVOR")
    g.e("read 12 13 \"The memorial: a long wall of names. Every one of them fell.\"")
    g.e("read 14 13 \"The Returners' Wall.\" scene=T05P_RETURN_WALL")
    g.e("save 20 22")
    g.decorate("lbc1", 16, 83, ":")
    return g.emit("T05_POST", name="High Aerie - Windmill Court", tileset="town_r04", music="M014", zone="T05", region="R04",
                  location="L_T05", phase="post", legend=SKYLEG)


# ---------------------------------------------------------------- CH18 Veyr
def t02_square_post():
    g = Grid(44, 32, ":")
    g.rect(0, 0, 43, 3, "~")               # outer walls fell into the river
    g.rect(0, 0, 3, 31, "~")
    g.put(10, 3, "x"); g.put(11, 3, "x"); g.put(30, 3, "x")
    g.text(16, 12, "aaaaaaaaaaaa\nnnnnnnnnnnnn")  # distribution point where the throne stood
    g.house(6, 6, 7, 3); g.house(30, 6, 8, 3)
    g.house(6, 21, 8, 4); g.house(30, 22, 8, 3)
    g.put(21, 18, "y")
    g.rect(40, 14, 43, 17, ":")
    g.put(22, 28, "L")                     # ladder down to the canals
    for (x, y) in ((16, 17), (27, 17)):
        g.put(x, y, "l")
    g.e("spawn world 42 15 left")
    g.e("spawn from_canals 22 27 up")
    g.e("spawn default 42 15 left")
    g.e("exit 43 14..17 WORLD_POST l_t02")
    g.e("exit 22 28 T02_CANALS from_square")
    g.e("npc ansel_p 20 15 up sprite=ansel talk=T02P_ANSEL")
    g.e("npc guard_p1 14 16 right sprite=guard talk=T02P_GUARDS")
    g.e("npc guard_p2 15 16 left sprite=soldier talk=T02P_GUARDS")
    g.e("npc jori_v 26 20 left sprite=jori talk=CH18_JORI if=ch:CH16,!ch:CH18")
    g.e("npc dist_worker 24 15 up sprite=worker talk=T02P_DIST")
    g.e("npc refugee_v 9 17 right sprite=survivor talk=T02P_REFUGEE")
    g.e("npc market_v 34 18 left sprite=keeper talk=T02P_SHOP")
    g.e("shop 34 17 SHOP_T02")
    g.e("inn 9 25 scene=T02P_INN")
    g.e("npc inn_v 10 26 left sprite=keeper talk=T02P_INN")
    g.e("save 36 26")
    g.decorate("cr2l]x", 26, 82, ":")
    return g.emit("T02_SQUARE_POST", name="Veyr - Distribution Square", tileset="capital", music="M011", zone="T02", region="R01",
                  location="L_T02", save="true", phase="post")


def t02_canals():
    g = Grid(44, 28, "~")
    g.rect(20, 1, 24, 5, "d")              # landing under the square
    g.rect(2, 5, 41, 7, "d")
    g.rect(2, 20, 41, 22, "d")
    for i, x in enumerate((8, 22, 36)):
        g.rect(x, 8, x + 1, 19, "~")
        g.e(f"tileset_over {x}..{x+1} 8..19 bridge if=flag:t02c_gate{i+1}")
        g.e(f"switch gate{i+1} {x + 3} 6 flag=t02c_gate{i+1} scene=CH18_GATE{i+1}")
    g.rect(2, 22, 5, 26, "d")              # west: the Underways echo chamber (post alcove)
    g.rect(38, 22, 41, 27, "d")            # south-east: registry
    g.e("read 12 5 \"Canal sign, repainted: 'LOCK GATES RAISE CROSSINGS. OPEN ONE, THE WATER SHIFTS.'\"")
    g.e("chest T02C_C1 40 6 I003 2")
    g.e("spawn from_square 22 2 down")
    g.e("spawn from_registry 39 26 up")
    g.e("spawn from_echo 3 25 up")
    g.e("exit 22 1 T02_SQUARE_POST from_canals")
    g.e("exit 38..41 27 T02_REGISTRY_POST from_canals")
    g.rect(38, 8, 41, 11, "d")
    g.e("spawn from_seals 40 9 left")
    g.e("exit 41 8..11 D02P_SEALS from_canals if=ch:CH20 locked=\"A clerk's door, bolted from inside. The registrar has the key - after the Accord.\"")
    g.e("exit 2..5 26 D02P_ECHO from_canals if=ch:CH20 locked=\"A sealed service door. Behind it, a machine is reading orders to no one.\"")
    return g.emit("T02_CANALS", name="Veyr - Changed Canals", tileset="underways", music="M011", zone="D02P", region="R01",
                  location="L_T02", encounters="D02P", rate="0.7", phase="post")


def t02_registry():
    g = Grid(32, 24)
    g.rect(2, 2, 29, 21, ".")
    g.text(3, 3, "kkkkk.kkkkk.kkkkk")
    g.text(3, 7, "kkkkk.kkkkk.kkkkk")
    g.rect(14, 21, 17, 23, ".")
    g.text(10, 14, "tttt")
    g.e("trigger 12..19 18..19 scene=CH18_REMNANTS if=ch:CH16,!flag:t02r_clear")
    g.e("npc pip_r 15 11 down sprite=C08 talk=CH18_PIP if=!ch:CH18")
    g.e("npc resident1 6 12 right sprite=survivor talk=CH18_RES")
    g.e("npc resident2 24 12 left sprite=elder talk=CH18_RES")
    g.e("npc registrar 12 15 up sprite=clerk talk=T02R_REGISTRAR if=ch:CH18")
    g.e("read 11 14 \"The original ledgers.\" scene=CH18_LEDGERS")
    g.e("save 26 19")
    g.e("spawn from_canals 15 22 up")
    g.e("spawn default 15 22 up")
    g.e("exit 14..17 23 T02_CANALS from_registry")
    return g.emit("T02_REGISTRY_POST", name="Veyr - Lower Registry", tileset="interior_stone", music="M009", zone="T02", region="R01",
                  location="L_T02", save="true", phase="post")


def d02p_echo():
    g = Grid(28, 20)
    g.rect(3, 3, 24, 16, ".")
    g.rect(12, 16, 15, 19, ".")
    g.text(11, 4, "m.m.m")
    g.e("read 9 4 \"The Command Ledger.\" scene=Q11_LEDGER")
    g.e("trigger 10..17 8..9 scene=Q11_ECHO if=q:Q11,!flag:b15_done")
    g.e("save 5 14")
    g.e("spawn from_canals 13 18 up")
    g.e("spawn default 13 18 up")
    g.e("exit 12..15 19 T02_CANALS from_echo")
    return g.emit("D02P_ECHO", name="Veyr Underways - Echo Chamber", tileset="underways", music="M025", zone="D02P", region="R01",
                  location="L_T02", encounters="none", save="true", phase="post")


# ---------------------------------------------------------------- CH19 Whitebone
def d07p_r01():
    g = Grid(40, 28, "q")
    g.rect(4, 4, 35, 23, ".")
    g.rect(17, 23, 22, 27, ".")
    g.rect(17, 0, 22, 4, ".")
    g.text(6, 6, "]] ]]")
    g.put(28, 18, "!")
    g.e("spawn world 19 26 up")
    g.e("spawn from_r02 19 1 down")
    g.e("spawn default 19 26 up")
    g.e("exit 17..22 27 WORLD_POST l_d07")
    g.e("exit 17..22 0 D07P_R02 from_r01 if=event:CH19_ARRIVE")
    g.e("trigger 16..23 18..20 scene=CH19_ARRIVE if=ch:CH16,!event:CH19_ARRIVE")
    g.e("npc sanct_keeper 26 18 right sprite=monk talk=CH19_KEEPER")
    g.e("npc survivor_w 12 12 down sprite=survivor talk=CH19_SURVIVOR_GATE")
    g.e("save 8 20")
    g.e("heal 10 20")
    g.decorate("]!cr", 12, 84, ".")
    return g.emit("D07P_R01", name="Whitebone Sanctuary - Gate", tileset="whitebone", music="M008", zone="D07P", region="R05",
                  location="L_D07", encounters="none", save="true", phase="post")


def d07p_r02():
    g = Grid(40, 28)
    g.rect(2, 2, 37, 25, ".")
    g.rect(17, 25, 22, 27, ".")
    for i, x in enumerate((6, 16, 26)):
        g.rect(x, 4, x + 6, 9, "#")
        g.rect(x + 1, 5, x + 5, 8, ",")
        g.put(x + 3, 9, "G")
        g.e(f"tileset_over {x+3} 9 doorway if=flag:d07p_open{i+1}")
        g.e(f"npc cell{i+1} {x+3} 8 down sprite={('survivor','elder','patient')[i]} talk=CH19_CELL{i+1}")
        g.e(f"switch lock{i+1} {x+3} 11 scene=CH19_LOCK{i+1}")
    g.e("npc sable_s 30 18 left sprite=C07 talk=CH19_SABLE if=!ch:CH19")
    g.rect(33, 2, 36, 3, ".")
    g.rect(33, 0, 36, 1, ".")
    g.e("spawn from_r03 34 1 down")
    g.e("exit 33..36 0 D07P_R03 from_r02 if=ch:CH20 locked=\"A sealed stair to the deep cells. The sanctuary keeps it shut until the Accord is signed.\"")
    g.e("trigger 17..22 22..23 scene=CH19_SC10 if=flag:d07p_open1,flag:d07p_open2,flag:d07p_open3,!ch:CH19")
    g.e("spawn from_r01 19 26 up")
    g.e("spawn default 19 26 up")
    g.e("exit 17..22 27 D07P_R01 from_r02")
    return g.emit("D07P_R02", name="Whitebone Sanctuary - The Cells", tileset="whitebone", music="M008", zone="D07P", region="R05",
                  location="L_D07", encounters="none", phase="post")


# ---------------------------------------------------------------- CH20 Nacre
def t06_post():
    g = Grid(44, 30, "N")
    g.rect(2, 3, 41, 26, ":")
    g.rect(19, 26, 24, 29, ":")
    g.house(3, 4, 8, 3)
    g.house(31, 4, 9, 4, chimney=7)       # listening house (was the cloister)
    g.house(3, 17, 7, 3)
    g.blob(22, 11, 6, 3, "9")             # the pool, now projecting memories
    g.text(16, 19, "bbbbbbbbbbbb")         # assembly benches
    g.put(24, 8, "*"); g.put(10, 13, "*"); g.put(34, 13, "*")
    g.e("spawn world 21 28 up")
    g.e("spawn default 21 28 up")
    g.e("exit 19..24 29 WORLD_POST l_t06")
    g.e("inn 34 8 scene=T06P_INN")
    g.e("npc house_keeper 36 9 left sprite=monk talk=T06P_INN")
    g.e("npc sen_p 22 16 down sprite=sen talk=T06P_SEN")
    g.e("npc family_p1 12 16 right sprite=elder talk=T06P_FAMILY")
    g.e("npc family_p2 13 17 up sprite=survivor talk=T06P_FAMILY")
    g.e("npc gardener_p 8 22 up sprite=farmer talk=T06P_GARDENER")
    g.e("npc salt_p 28 22 left sprite=keeper talk=T06P_SHOP")
    g.e("shop 28 21 SHOP_T06")
    g.e("npc listener_p 30 12 left sprite=scholar talk=T06P_LISTENER")
    g.e("npc patient_p 6 10 right sprite=patient talk=Q06_HOOK if=ch:CH20")
    g.e("npc survivor_n 38 20 left sprite=survivor talk=Q07_HOOK if=ch:CH20")
    g.e("npc winter_pilgrim 38 16 left sprite=monk talk=Q09_HOOK if=ch:CH20")
    g.e("npc pool_voice 22 14 down sprite=monk talk=Q12_HOOK if=ch:CH20")
    g.e("trigger 16..27 23..24 scene=CH20_ACCORD if=ch:CH17,ch:CH18,ch:CH19,!ch:CH20")
    g.e("save 38 24")
    g.decorate("1gyl*b", 22, 81, ":")
    return g.emit("T06_POST", name="Nacre - The Assembly", tileset="town_r05", music="M015", zone="T06", region="R05",
                  location="L_T06", save="true", phase="post")


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "post_reunions.map"),
          [d06p_r01(), t05_post(), t02_square_post(), t02_canals(), t02_registry(), d02p_echo(), d07p_r01(), d07p_r02(), t06_post()],
          "Post-state reunions and the Ash Accord")
    print("post_reunions written")
