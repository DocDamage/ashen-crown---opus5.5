"""Veyr group (hand-made 48px towns): T01_POST (Brackenford after the flood) and Veyr, the Crown's capital
(T02_MARKET, T02_SQUARE, T02_SQUARE_POST on the 'capital' set, T02_CANALS on 'underways').

Veyr shape: walled block (layout standard section 4) - slate-roofed stone-and-timber terraces sharing walls, formal
warm-stone squares, a canal level below the streets, the Oath Square and the Ministry of Relays on the high ground at
the north end of the main axis. Brackenford keeps the pilot's street plan; the flood has cut it in two."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Map, write_group, st, C
import lib_r01 as A
import lib_veyr as V
from lib_veyr import Building as B
from skins import lib_quarry as Q


def ents(m, block):
    for e in block.strip("\n").split("\n"):
        m.ent(e)


# ---------------------------------------------------------------------------------------------------------- market
def market():
    m = Map("T02_MARKET", 44, 30, "Veyr - South Market", "capital", music="M011", zone="T02", location="L_T02",
            region="R01", seed=211)
    m.use(**V.MATS)
    m.fill("cobble")
    m.rect("flag", 2, 9, 41, 18)                           # market floor
    m.rect("cobble_r", 18, 6, 25, 22)                      # the main axis
    m.rect("flag_big", 13, 12, 30, 17)                     # fountain court
    m.rect("stairs_w", 19, 0, 24, 2)                       # stair up to Oath Square
    m.rect("slabs", 18, 23, 25, 29)
    # ---- north terrace (rows 0-5), gap for the stair at 18-25
    B(7, 3, "slate", ("timber", "timber2", "stone"), chimneys=[1, 5], wins=(("glass", None), ("shut", "glass"), ("shut", None)), seed=1).place(m, 0, 0)
    B(6, 3, "slate_dark", ("wstone", "wstone"), wins=(("arch", None), ("arch2", None)), gables=[2], seed=2).place(m, 7, 1)
    V.roof_strip(m, 7, 0, 6, 1, "slate_dark")
    B(5, 3, "slate", ("timber", "stone"), chimneys=[3], wins=(("glass",), ("shut",)), seed=0).place(m, 13, 1)
    V.roof_strip(m, 13, 0, 5, 1, "slate")
    B(6, 3, "slate", ("timber2", "stone"), chimneys=[1], wins=(("glass", None),), gables=[3], seed=1).place(m, 26, 1)
    V.roof_strip(m, 26, 0, 6, 1, "slate")
    B(6, 3, "slate_dark", ("wstone", "wstone", "wstone"), wins=(("narrow",), ("arch", None), ("arch3", None)), seed=0).place(m, 32, 0)
    B(6, 3, "slate", ("timber", "timber2", "stone"), chimneys=[4], wins=(("glass", None), ("glass", "shut"), None), seed=0).place(m, 38, 0)
    # stair balustrade: statues on plinths either side of the stair head
    for x in (18, 25):
        for y in range(0, 4):
            m.solid(x, y, "wall")
    m.place(V.STATUE_A, 17, 0, solid=0)
    m.place(V.STATUE_B, 25, 0, solid=0)
    m.place(A.SIGNPOST, 22, 2)                              # sign 22,3
    # ---- side blocks (roof strips to the map edges)
    V.roof_strip(m, 0, 6, 2, 8, "slate", chimneys=[0])
    V.roof_strip(m, 42, 6, 2, 8, "slate_dark", chimneys=[1])
    B(3, 2, "slate", ("timber", "stone"), wins=(None, None), seed=0).place(m, 0, 14)
    V.roof_strip(m, 0, 18, 2, 5, "slate_dark")
    V.roof_strip(m, 42, 14, 2, 9, "slate", chimneys=[0])
    # ---- south block: the shop (door 7,19) and the relay office (closed)
    shop = B(8, 3, "slate", ("timber", "stone"), doors=[4], door="plain", chimneys=[1, 6],
             wins=(("glass", "shut_open"), ("shut", None)), gables=[3]).place(m, 3, 15)
    B(9, 3, "slate_dark", ("wstone", "wstone"), wins=(("arch", None), ("narrow", None)), gables=[3], seed=1).place(m, 32, 15)
    # ---- canal + south wall and gate
    V.canal_h(m, 0, 43, 23, 25, bridges=[(19, 24)])
    V.warm_wall(m, 0, 17, 27, rows=3)
    V.warm_wall(m, 26, 43, 27, rows=3)
    m.place(V.TOWER_BLUE, 17, 25)
    m.place(V.TOWER_BLUE, 25, 25)
    for (x, y) in ((18, 29), (25, 29)):
        m.solid(x, y, "wall")
    m.rect("slabs", 0, 26, 17, 26)
    m.rect("slabs", 26, 26, 43, 26)
    m.anim("flag_crown_red", 17, 23, dy=10)
    m.anim("flag_crown_red", 26, 23, dy=10)
    # ---- market: stalls, fountain, statues, lamps
    m.place(V.STALL["fruit"], 8, 10)
    m.place(V.STALL["veg"], 10, 10)
    m.place(V.STALL["jars"], 15, 10)                         # keeper's counter (shop 16,11)
    m.place(V.STALL["herbs"], 17, 10)
    m.place(V.STALL["bread"], 24, 10)
    m.place(V.STALL["meat"], 26, 10)
    m.place(V.STALL["fabric"], 31, 10)
    m.place(V.STALL["cloth2"], 33, 10)
    m.place(V.FOUNTAIN_BIG, 20, 13)
    m.place(V.STATUES_S[0], 10, 13)
    m.place(V.STATUES_S[1], 33, 13)
    for (x, y) in ((17, 13), (26, 13), (5, 8), (38, 8), (6, 21), (37, 21), (16, 21), (27, 21)):
        m.place(V.LAMP_POST, x, y)
    # ---- dressing against the north facades (row 5-6)
    m.place(A.BARREL, 1, 5)
    m.place(A.CRATE_STACK, 2, 5)
    m.place(V.SACKS2[0], 3, 5)
    m.place(A.BENCH, 8, 5)
    m.place(V.FLOWERPOTS[1], 10, 5)
    m.place(V.FLOWERPOTS[1], 12, 5)
    m.place(A.BARRELS, 14, 5)
    m.place(V.JARS[0], 16, 5)
    m.place(V.TOPIARY[0], 26, 5)
    m.place(V.TOPIARY[1], 31, 5)
    m.place(A.STONE_BENCH, 28, 5)
    m.place(V.BASKETS[0], 33, 5)
    m.place(V.BASKETS[3], 34, 5)
    m.place(A.CRATE, 36, 5)
    m.place(A.BARREL, 39, 4)
    m.place(V.SACKS2[1], 40, 5)
    for (x, y, b) in ((2, 2, 0), (5, 2, 3), (9, 3, 1), (11, 3, 4), (27, 3, 1), (30, 3, 3), (34, 3, 4), (36, 3, 1), (40, 2, 0)):
        m.place(V.BANNER[b], x, y)
    m.place(V.NOTICE_B, 24, 6)                              # the herald's proclamations
    m.place(V.CARTS[0], 3, 7)
    m.place(A.CRATE_S, 5, 7)
    m.place(V.BASKETS[7], 36, 7)
    m.place(A.BARREL, 40, 7)
    # stalls surroundings
    m.place(A.CRATE_S, 7, 11)
    m.place(V.BASKETS[1], 12, 11)
    m.place(A.SACKS, 13, 9)
    m.place(V.BASKETS[5], 19, 11)
    m.place(A.CRATE_S, 23, 11)
    m.place(V.BARREL_PILE[0], 28, 9)
    m.place(V.BASKETS[2], 30, 11)
    m.place(A.HANDCART, 35, 10)
    m.place(V.SACKS2[0], 38, 10)
    # east shrine for the pilgrim, west well
    m.place(V.STELE, 38, 11)
    m.place(V.FLOWERPOTS[2], 40, 13)
    m.place(A.WELL, 4, 11)
    m.place(A.BARREL, 3, 12)
    # south block dressing
    m.place(V.MUG_SIGN, 6, 18)
    m.place(A.BARREL, 8, 19)
    m.place(A.CRATE_STACK, 9, 19)
    m.place(V.FLOWERPOTS[0], 5, 19)
    m.place(A.CRATE, 3, 20)
    m.place(V.TOPIARY[2], 32, 19)
    m.place(V.TOPIARY[2], 40, 19)
    m.place(A.STONE_BENCH, 34, 20)
    m.place(A.STONE_BENCH, 37, 20)
    m.place(V.PLANTER, 13, 19)
    m.place(V.PLANTER, 28, 19)
    m.place(A.BENCH2, 11, 21)
    m.place(V.CARTS[1], 39, 21)
    m.place(A.BARRELS, 1, 21)
    # fountain court: benches, planters, flags, a second row of stalls
    m.place(A.STONE_BENCH, 17, 17)
    m.place(A.STONE_BENCH, 25, 17)
    m.place(V.STALL["pottery"], 12, 13)
    m.place(V.STALL["rugs"], 29, 13)
    m.place(V.STALL["baskets"], 29, 16)
    m.place(V.JARS[2], 31, 17)
    m.place(A.CRATE_S, 11, 14)
    m.anim("flag_blue", 15, 12, dy=-40)
    m.anim("flag_blue", 28, 12, dy=-40)
    m.solid(15, 12, "lamp")
    m.solid(28, 12, "lamp")
    # canal side: mooring crates and a moored boat
    m.place(V.BARREL_PILE[1], 2, 21)
    m.place(A.CRATE, 13, 22)
    m.place(A.BARREL, 14, 21)
    m.place(V.BASKETS[6], 33, 22)
    m.place(A.CRATE_STACK, 41, 21)
    m.place(V.ROWBOAT, 7, 24) if hasattr(V, "ROWBOAT") else None
    m.place(V.ROWBOAT, 34, 25) if hasattr(V, "ROWBOAT") else None
    m.reserve_rect(18, 0, 25, 29)
    ents(m, """spawn world 21 27 up
spawn from_square 21 2 down
spawn from_shop 7 20 down
spawn default 21 27 up
exit 19..24 29 WORLD t02
exit 19..24 0 T02_SQUARE from_market
door 7 19 T02_SHOP entry sfx=FX008
npc herald 21 8 down sprite=noble talk=T02_HERALD if=!ch:CH02
npc guard_a 19 12 right sprite=guard talk=T02_GUARDS
npc guard_b 20 12 left sprite=soldier talk=T02_GUARDS
npc vendor1 9 9 down sprite=keeper talk=T02_VENDOR1
npc vendor2 25 9 down sprite=baker talk=T02_VENDOR2
npc lampman 26 15 left sprite=worker talk=T02_LAMPMAN
npc child_v 30 22 up sprite=child talk=T02_CHILD wander=1
npc clerk_m 14 16 down sprite=clerk talk=T02_CLERK_M
npc pilgrim 37 12 left sprite=monk talk=T02_PILGRIM
shop 16 11 SHOP_T02
sign 22 3 "Oath Square. Ministry of Relays. Crown Records below.\"""".replace('\\"', '"'))
    return m


# ---------------------------------------------------------------------------------------------------------- square
def square():
    m = Map("T02_SQUARE", 40, 28, "Veyr - Oath Square", "capital", music="M011", zone="T02", location="L_T02",
            region="R01", seed=212)
    m.use(**V.MATS)
    m.fill("flag")
    m.rect("cobble_r", 2, 5, 37, 8)
    m.rect("stairs_w", 11, 6, 28, 8)                       # ceremonial stair up to the Ministry
    m.rect("cobble_r", 6, 9, 33, 21)
    m.rect("flag_big", 9, 10, 30, 20)
    m.rect("flag", 14, 11, 25, 18)
    m.rect("stairs_w", 17, 22, 22, 27)                     # stair down to the South Market
    # ---- the Ministry of Relays (landmark at the head of the axis)
    B(20, 2, "slate_dark", ("frieze", "wstone", "wstone", "wstone"), wins=(None, ("arch", None), ("arch2", None, None), ("narrow", None)),
      chimneys=[2, 17], seed=0).place(m, 10, 0)
    V.flat_obj(m, V.GATE_FACADE(), 18, 3, kind="house")
    m.place(V.COLONNADE, 11, 4, solid=0)
    m.place(V.COLONNADE, 22, 4, solid=0)
    m.anim("flag_crown_red", 10, 0, dy=-40)
    m.anim("flag_crown_red", 29, 0, dy=-40)
    # wings
    B(10, 3, "slate", ("timber2", "wstone"), chimneys=[2, 7], wins=(("glass", None), ("shut", None)), gables=[4], seed=1).place(m, 0, 0)
    B(10, 3, "slate", ("timber", "wstone"), chimneys=[3, 8], wins=(("glass", None), ("shut", None)), gables=[4], seed=0).place(m, 30, 0)
    for (x, b) in ((2, 1), (7, 3), (32, 3), (37, 1)):
        m.place(V.BANNER[b], x, 3)
    # stair cheeks: statues on plinths
    m.place(V.STATUE_A, 9, 5)
    m.place(V.STATUE_B, 29, 5)
    for y in (6, 7, 8):
        m.solid(10, y, "wall")
        m.solid(29, y, "wall")
    # ---- west and east edges
    V.roof_strip(m, 0, 5, 2, 17, "slate_dark", chimneys=[0])
    V.roof_strip(m, 38, 5, 2, 17, "slate_dark", chimneys=[1])
    # ---- the Oath Statue at the centre
    ped = st("roman", "11", 0, 12, 3, 3, solid=0, base=15 * 48 - 12 * 48 + 2)
    m.place(ped, 18, 13)
    for x in (18, 19, 20):
        m.solid(x, 14, "statue")
        m.solid(x, 15, "statue")
    oath = st("roman", "4", 8, 0, 2, 4, solid=0, base=332)
    m.place(oath, 18, 10, dx=24, dy=-14)
    # lamps, benches, oath statues along the square
    for (x, y) in ((13, 11), (26, 11), (13, 18), (26, 18), (6, 10), (33, 10), (6, 20), (33, 20)):
        m.place(V.LAMP_POST, x, y - 1)
    for (x, y) in ((3, 8), (3, 11), (35, 8), (35, 11)):
        m.place(A.STONE_BENCH, x, y)
    for i, (x, y) in enumerate(((8, 12), (8, 15), (31, 12), (31, 15), (8, 18), (31, 18))):
        m.place(V.STATUES_K[i], x, y - 1)
    m.place(V.FOUNTAINS_S[1], 11, 14)
    m.place(V.FOUNTAINS_S[1], 27, 14)
    m.place(V.PLANTER, 15, 20)
    m.place(V.PLANTER, 22, 20)
    m.place(V.TOPIARY[0], 11, 9)
    m.place(V.TOPIARY[0], 28, 9)
    m.place(V.TOPIARY[1], 2, 5)
    m.place(V.TOPIARY[1], 37, 5)
    m.place(V.FLOWERPOTS[2], 5, 5)
    m.place(V.FLOWERPOTS[2], 34, 5)
    m.place(A.BENCH, 4, 16)
    m.place(A.BENCH, 34, 16)
    # ---- south: terrace parapet over the lower town, the Records stair, flanking blocks
    V.parapet(m, 8, 16, 22)
    V.parapet(m, 23, 31, 22)
    for (x0, w, k, ch) in ((8, 9, "slate", [2, 6]), (23, 9, "slate_dark", [3, 7])):
        V.roof_strip(m, x0, 23, w, 5, k, chimneys=ch)
    B(8, 3, "slate_dark", ("wstone", "wstone"), wins=(("arch", None), ("narrow", None)), chimneys=[5], seed=0).place(m, 0, 22)
    B(8, 3, "slate", ("timber2", "wstone"), wins=(("glass", None), ("shut", None)), chimneys=[2], seed=1).place(m, 32, 22)
    V.stairwell(m, 3, 21)
    m.solid(3, 21, "door")
    m.place(A.SIGN_S, 2, 20)
    m.place(V.LANTERNS[0], 4, 20)
    m.place(A.CRATE, 6, 21)
    m.place(V.JARS[1], 7, 21)
    m.place(A.BARREL, 33, 21)
    m.place(V.SACKS2[0], 34, 20)
    m.place(V.TOPIARY[2], 16, 21)
    m.place(V.TOPIARY[2], 23, 21)
    m.reserve_rect(17, 9, 22, 27)
    ents(m, """spawn from_market 19 25 up
spawn from_records 3 20 down
spawn default 19 25 up
exit 18..21 27 T02_MARKET from_square
door 3 21 T02_RECORDS entry sfx=FX009 if=ch:CH02
npc minister_aide 19 9 down sprite=noble talk=T02_AIDE if=!ch:CH02
npc guard_s1 17 9 down sprite=guard talk=T02_GUARD_S if=!ch:CH02
npc guard_s2 22 9 down sprite=guard talk=T02_GUARD_S if=!ch:CH02
npc ansel_sq 30 12 left sprite=ansel talk=T02_ANSEL_SQ if=!ch:CH02
npc widow 8 16 right sprite=elder talk=T02_WIDOW
trigger 17..22 11..12 scene=CH02_ARREST if=!ch:CH02,ch:CH01
read 19 15 "The Oath Statue: 'I shall carry the Crown's orders.' Someone has scratched 'whose?' beneath.\"""".replace('\\"', '"'))
    return m


# ---------------------------------------------------------------------------------------------------- square post
def square_post():
    m = Map("T02_SQUARE_POST", 44, 32, "Veyr - Distribution Square", "capital", music="M011", zone="T02",
            location="L_T02", region="R01", seed=213, save=True, phase="post")
    m.use(**V.MATS)
    m.fill("flag_o")
    m.rect("cob_o", 5, 9, 39, 24)
    m.rect("flag_o", 14, 14, 29, 22)
    m.rect("cob_o", 38, 13, 43, 18)                        # the east road through the breach
    # flood: the north (drowned Ministry) and the west, silt left on the paving
    m.rect("flood", 0, 0, 43, 2)
    m.rect("flood", 0, 0, 3, 31)
    m.rect("silt", 4, 3, 43, 3)
    m.rect("silt", 4, 3, 4, 28)
    for (cx, cy, rx, ry) in ((5, 12, 1.6, 2.5), (8, 27, 2.5, 1.2), (30, 10, 1.8, 1.0), (13, 25, 1.2, 0.8), (38, 22, 1.4, 1.2)):
        m.blob("silt", cx, cy, rx, ry)
    for (cx, cy, rx, ry) in ((5, 7, 1.2, 1.5), (4, 21, 1.0, 1.5)):
        m.blob("flood", cx, cy, rx, ry)
    m.rect("stairs_o", 16, 3, 27, 5)                        # the Ministry stair, now running into the water
    # the Ministry: only its gate stands, in the flood
    gate = V.stain(V.GATE_FACADE(), 0.45, 3)
    V.flat_obj(m, gate, 20, 0, kind="wall")
    for (s, x, y) in ((V.COL_RUIN[0], 15, 0), (V.COL_RUIN[1], 17, 1), (V.COL_RUIN[2], 26, 1), (V.COL_RUIN[0], 28, 0),
                      (V.COL_RUIN[1], 12, 1), (V.COL_RUIN[2], 32, 0)):
        m.place(s, x, y)
    m.place(V.RUIN_LOW[1], 7, 0)
    m.place(V.RUIN_LOW[2], 35, 0)
    # ---- north side: ruined houses (west), the old wing (east), damaged
    m.place(V.RUIN_SLATE_HOUSE, 6, 4)
    m.place(V.RUIN_STONE_HOUSE, 10, 4)
    B(8, 3, "slate", ("timber", "wstone"), chimneys=[6], wins=(("glass", None), ("shut", None)), gables=[3],
      holes=[(1.2, 0.9, 1.6)], grime=0.35, seed=2).place(m, 30, 4)
    m.place(V.RUIN_WALLS[2], 38, 5)
    # ---- the distribution line (where the soup table stands now)
    for i, k in enumerate(("bread", "grain", "veg", "produce", "bread2", "jam")):
        m.place(V.STALL[k], 16 + 2 * i, 12)
    m.place(V.CAULDRON[0], 17, 10)
    m.place(V.CAULDRON[1], 23, 10)
    m.place(A.SACKS, 19, 10)
    m.place(V.SACKS2[1], 21, 10)
    m.place(A.CRATE_STACK, 25, 10)
    m.place(A.BARREL, 26, 10)
    m.place(V.BASKETS[1], 27, 11)
    m.place(A.CRATE, 15, 13)
    m.place(V.BASKETS[4], 28, 13)
    m.place(A.NOTICE, 11, 11)
    # the old throne, dragged aside
    m.place(V.THRONE, 5, 12)
    m.place(V.RUBBLE[2], 9, 14)
    # the Oath Statue: an empty plinth, the statue in pieces
    m.place(V.PLINTH, 20, 17)
    m.place(V.BUSTS[0], 22, 18)
    m.place(V.RUBBLE[2], 19, 18)
    # tents, cots and fires of the refugees
    m.place(V.TENTS[0], 13, 18)
    m.place(V.TENTS[4], 5, 8)
    m.place(V.TENTS[1], 15, 25)
    m.place(V.TENTS[5], 26, 24)
    m.place(V.CAMPFIRE, 17, 20)
    m.place(V.CAMP_CHESTS[1], 12, 17)
    m.place(V.BEDROLLS[0], 16, 23)
    # ---- ex-barracks (the inn): cots outside, the desk at 9,25
    B(8, 3, "slate_dark", ("wstone", "wstone"), wins=(("narrow", None), ("arch", None)), chimneys=[1, 6], grime=0.25, seed=1).place(m, 5, 19)
    m.place(V.MAP_TABLE, 8, 24)
    for x in (5, 6, 12, 13):
        m.place(V.COTS[x % 3], x, 25)
    m.place(A.BARREL, 11, 24)
    m.place(V.LANTERNS[1], 7, 24)
    # ---- south-east house and the relocated market
    B(8, 3, "slate_dark", ("timber2", "stone"), chimneys=[2], wins=(("glass", None), ("shut", None)),
      holes=[(4.6, 0.8, 1.8)], grime=0.3, seed=0).place(m, 30, 21)
    m.place(V.STALL["bread"], 33, 16)
    m.place(V.STALL["veg"], 35, 16)
    m.place(V.STALL["pots"], 30, 16)
    m.place(A.CRATE_STACK, 37, 16)
    m.place(A.BARREL, 29, 17)
    m.place(V.SACKS2[0], 36, 19)
    # ---- east: the breach in the fallen wall
    for (s, x, y) in ((V.RUIN_WALLS[0], 40, 3), (V.RUIN_WALLS[1], 42, 3), (V.RUIN_WALLS[3], 40, 8), (V.RUIN_WALLS[4], 42, 8),
                      (V.RUIN_WALLS[0], 40, 19), (V.RUIN_WALLS[1], 42, 19), (V.RUIN_WALLS[3], 40, 23), (V.RUIN_WALLS[4], 42, 23)):
        m.place(s, x, y)
    for y in list(range(3, 12)) + list(range(20, 28)):
        for x in (40, 41, 42, 43):
            m.solid(x, y, "wall")
    m.place(V.RUBBLE[0], 40, 11)
    m.place(V.RUBBLE[1], 42, 17)
    m.place(V.RUBBLE[2], 41, 12)
    m.place(V.BROKEN_CART[2], 38, 11)
    # ---- south: parapet, ladder down to the canals, the drowned lower town
    m.rect("flood", 4, 29, 43, 31)
    V.parapet(m, 5, 21, 28, shade=0.86)
    V.parapet(m, 23, 39, 28, shade=0.86)
    m.rect("silt", 40, 28, 43, 28)
    for (x, w) in ((8, 6), (27, 7)):
        roof = V.roof_img(w * C, 96, "slate_dark").crop((0, 0, w * C, 40))
        V.put(m, V.recolour(roof, mul=(0.8, 0.9, 0.95)), x, 30, dy=4)
    m.place(V.LADDER, 22, 28)
    m.solid(22, 28, "ladder")
    m.place(A.TORCH_STAND, 21, 26)
    m.place(A.TORCH_STAND, 23, 26)
    m.place(V.ROWBOAT, 20, 29)
    # ---- lamps, carts, rubble
    for (x, y) in ((16, 7), (28, 7), (35, 12), (12, 15), (28, 16), (32, 27), (34, 27)):
        m.place(V.LAMP_POST, x, y - 1)
    m.place(V.BROKEN_CART[0], 24, 7)
    m.place(V.BROKEN_CART[1], 5, 16)
    m.place(V.RUBBLE[0], 13, 8)
    m.place(V.RUBBLE[2], 28, 5)
    m.place(V.CARTS[0], 27, 26)
    m.place(A.CRATE, 38, 26)
    m.place(A.BARREL, 39, 25)
    # the drowned lower streets west and north: roof ridges, wall stubs and debris in the water
    for (x, y, w) in ((0, 4, 3), (0, 10, 3), (0, 16, 3), (0, 23, 3), (37, 0, 3), (1, 0, 4)):
        ridge = V.roof_img(w * C, 96, "slate_dark" if y % 2 else "slate").crop((0, 0, w * C, 40))
        V.put(m, V.recolour(ridge, mul=(0.78, 0.88, 0.95)), x, y, dy=6)
    for (s, x, y) in ((V.COL_RUIN[1], 1, 7), (V.COL_RUIN[2], 2, 13), (V.COL_RUIN[0], 1, 20), (V.COL_RUIN[1], 2, 27),
                      (V.DEAD_TREE, 1, 28), (V.RUIN_LOW[0], 10, 0), (V.RUIN_LOW[5], 30, 0)):
        m.place(s, x, y)
    for (s, x, y) in ((A.BARREL, 3, 9), (A.CRATE, 2, 19), (A.LOGS[0], 1, 25), (A.CRATE_S, 25, 1), (A.LOGS[1], 13, 2),
                      (A.BARREL, 34, 1), (A.CRATE, 42, 30), (A.LOGS[0], 16, 31), (A.BARREL, 36, 31)):
        m.place(s, x, y, solid=0)
    wskip = set()
    for (x, y, w) in ((0, 4, 3), (0, 10, 3), (0, 16, 3), (0, 23, 3), (37, 0, 3), (1, 0, 4)):
        wskip |= {(xx, y) for xx in range(x, x + w)}
    m.water_anims(mat="flood", skip=wskip | {(x, y) for x in range(20, 24) for y in range(0, 3)} |
                  {(x, y) for x in range(8, 14) for y in (30,)} | {(x, y) for x in range(27, 34) for y in (30,)})
    # ground variety: moss and puddles where the water stood, patched paving
    for (cx, cy, rx, ry) in ((10, 16, 2.5, 1.5), (34, 9, 2.0, 1.2), (26, 25, 2.5, 1.2), (8, 9, 1.5, 1.0), (18, 26, 2.0, 1.0)):
        m.blob("mossflag", cx, cy, rx, ry)
    for (cx, cy) in ((12, 22), (29, 20), (36, 11), (24, 23)):
        m.blob("shallow", cx, cy, 0.9, 0.6)
    # sandbag line along the flood edge, clusters against every house and the parapet
    for y in (5, 9, 13, 17, 22, 26):
        m.place(V.SACKS2[y % 2], 5, y)
    for (s, x, y) in ((A.CRATE, 14, 7), (A.BARREL, 15, 8), (V.BASKETS[0], 30, 7), (A.CRATE_STACK, 38, 6),
                      (A.BARREL, 39, 8), (V.JARS[1], 13, 21), (A.CRATE_S, 14, 22), (V.SACKS2[1], 29, 24),
                      (A.BARREL, 38, 24), (V.BASKETS[3], 10, 27), (A.CRATE, 18, 27), (V.JARS[0], 25, 27),
                      (V.BASKETS[5], 36, 27), (A.CRATE_S, 26, 27), (V.CAMP_CHESTS[0], 14, 26), (V.CAMP_CHESTS[2], 12, 18)):
        m.place(s, x, y)
    m.reserve_rect(20, 13, 26, 16)
    m.reserve_rect(40, 13, 43, 18)
    m.reserve_rect(8, 16, 16, 17)
    m.reserve_rect(33, 17, 36, 27)
    m.reserve_rect(19, 25, 25, 28)
    m.reserve_rect(9, 24, 11, 27)
    m.scatter(V.RUBBLE[2:3] + Q.RUBBLE_S + Q.PEBBLES + A.GRASS_TUFTS[:4], 5, 4, 39, 27, 40, on=["flag_o", "cob_o", "silt", "mossflag"], gap=1)
    ents(m, """spawn world 42 15 left
spawn from_canals 22 27 up
spawn default 42 15 left
exit 43 14..17 WORLD_POST l_t02
exit 22 28 T02_CANALS from_square
npc ansel_p 20 15 up sprite=ansel talk=T02P_ANSEL
npc guard_p1 14 16 right sprite=guard talk=T02P_GUARDS
npc guard_p2 15 16 left sprite=soldier talk=T02P_GUARDS
npc jori_v 26 20 left sprite=jori talk=CH18_JORI if=ch:CH16,!ch:CH18
npc dist_worker 24 15 up sprite=worker talk=T02P_DIST
npc refugee_v 9 17 right sprite=survivor talk=T02P_REFUGEE
npc market_v 34 18 left sprite=keeper talk=T02P_SHOP
shop 34 17 SHOP_T02
inn 9 25 scene=T02P_INN
npc inn_v 10 26 left sprite=keeper talk=T02P_INN
save 36 26""")
    return m


# ---------------------------------------------------------------------------------------------------------- canals
def canals():
    m = Map("T02_CANALS", 44, 28, "Veyr - Changed Canals", "underways", music="M011", zone="D02P", location="L_T02",
            region="R01", seed=214, encounters="D02P", rate="0.7", phase="post")
    m.use(**V.UMATS)
    m.fill("cap")
    m.rect("void", 0, 0, 43, 0)
    m.rect("quay", 2, 5, 41, 9)                             # north quay
    m.rect("mossy", 2, 8, 17, 9)
    m.rect("cob", 26, 8, 35, 9)
    m.rect("tiles", 20, 1, 24, 4)                           # the shaft down from the square
    m.rect("quay", 38, 8, 41, 11)                           # to the sealed clerks' door
    m.rect("canal", 2, 10, 41, 17)
    m.rect("quay", 38, 8, 41, 11)
    m.rect("quay", 2, 18, 41, 22)                           # south quay
    m.rect("mossy", 12, 20, 30, 22)
    m.rect("cob", 2, 18, 9, 19)
    m.rect("cob", 2, 23, 5, 26)                             # west passage (echo door)
    m.rect("cob", 38, 23, 41, 27)                           # east passage (lower registry)
    m.rect("archive", 7, 24, 36, 27)                        # the drowned record stacks behind the barricade
    # ---- walls
    V.wall_face(m, 0, 19, 3, ["brick", "bars"])
    V.wall_face(m, 25, 43, 3, ["bars", "brick"])
    V.wall_face(m, 20, 24, 0, ["brick"], rows=1)
    V.wall_face(m, 0, 19, 1, ["grate", "brick", "brick"])        # the upper gallery of the vault
    V.wall_face(m, 25, 43, 1, ["brick", "grate", "brick"])
    V.put(m, V.cell("town", "6", 14, 12, 1, 2), 22, 0, dy=-20)      # ladder up to the square
    for y in range(0, 3):
        for x in list(range(0, 20)) + list(range(25, 44)):
            m.solid(x, y, "wall")
    for y in range(1, 5):
        m.solid(19, y, "wall")
        m.solid(25, y, "wall")
    for y in range(5, 28):
        for x in (0, 1, 42, 43):
            m.solid(x, y, "wall")
    for y in range(23, 28):
        for x in range(6, 38):
            m.solid(x, y, "wall")
        m.solid(6, y, "wall")
        m.solid(37, y, "wall")
    m.solid(2, 27, "wall"); m.solid(3, 27, "wall"); m.solid(4, 27, "wall"); m.solid(5, 27, "wall")
    # sealed doors: the clerks' door (east), the service door (west passage), the registry stair (east passage)
    V.put(m, V.over_dark(V.DOOR_D()), 42, 8)
    V.put(m, V.over_dark(V.PORTCULLIS_D()), 42, 10)
    V.put(m, V.over_dark(V.cell("dungeon", "4", 2, 2, 2, 2)), 3, 25)
    m.rect("tiles", 38, 26, 41, 27)
    # ---- canal edges, crossings, cistern pillars
    V.quay_edge(m, 2, 37, 9)
    V.quay_edge(m, 38, 41, 11)
    V.quay_edge(m, 2, 41, 18, face=False)
    for x0 in (8, 22, 36):
        V.submerged_walk(m, x0, x0 + 1, 10, 17)
        for yy in (8, 9, 18, 19):
            m.set(x0, yy, "tiles")
            m.set(x0 + 1, yy, "tiles")
    skip = {(x, y) for x0 in (8, 22, 36) for x in (x0, x0 + 1) for y in range(8, 20)}
    for y in range(10, 18):
        for x in range(2, 42):
            if (x, y) not in skip and m.mat[y][x] == "canal":
                m.anim("water_deep", x, y, h=48, flat=True)
    for (s, x, y) in ((V.ARCH_D, 4, 12), (V.PILLAR_D, 14, 11), (V.ARCH_BROKEN_D, 16, 14), (V.PILLAR_D, 19, 12),
                      (V.ARCH_D, 27, 12), (V.PILLAR_STUB_D, 31, 15), (V.PILLAR_D, 33, 11), (V.PILLAR_STUB_D, 12, 15),
                      (V.PILLAR_D, 40, 14), (V.PILLAR_STUB_D, 5, 15), (V.ARCH_BROKEN_D, 29, 15), (V.PILLAR_D, 25, 14),
                      (V.PILLAR_STUB_D, 34, 15), (V.PILLAR_D, 11, 12)):
        m.place(s, x, y)
    for (s, x, y) in ((Q.SCROLLS[0], 13, 10), (Q.SCROLLS[2], 29, 16), (Q.BOOK_OPEN, 18, 16), (Q.SCROLLS[1], 34, 10),
                      (Q.CRATES[0], 6, 16), (Q.BARRELS[1], 24, 13), (Q.SCROLLS[3], 3, 11), (Q.CRATES[3], 38, 16),
                      (Q.SCROLLS[0], 20, 14), (Q.BOOK_OPEN, 32, 13), (V.ROWBOAT, 15, 10), (V.ROWBOAT, 28, 17)):
        m.place(s, x, y, solid=0)
    # mooring posts, rope and nets along both quays
    for x in (4, 12, 17, 27, 31, 34):
        m.place(V.MOOR, x, 9)
    for x in (5, 14, 19, 26, 30, 39):
        m.place(V.MOOR, x, 18)
    for (s, x, y) in ((Q.CRATES[1], 2, 9), (Q.BARRELS[0], 3, 9), (V.ROPE, 13, 9), (Q.SACKS[2], 28, 9), (Q.CRATES[4], 35, 9),
                      (V.ROPE, 6, 19), (Q.CRATES[2], 2, 19), (Q.BARRELS[3], 3, 18), (Q.POTS[1], 15, 19), (Q.CRATES[5], 33, 19),
                      (V.ROPE, 40, 19), (Q.RUBBLE_S[0], 24, 19), (Q.PEBBLES[0], 10, 7), (Q.PEBBLES[1], 30, 7),
                      (Q.SLIME[0], 16, 8), (Q.SLIME[1], 33, 21), (Q.BONES_F[0], 36, 20)):
        m.place(s, x, y)
    # ---- lock-gate machinery beside each lever (the game draws the levers at 11,6 25,6 39,6)
    for (gx, lx) in ((8, 10), (22, 24), (36, 38)):
        m.place(Q.WINCH, gx, 4, solid=0)
        m.place(Q.WINCH, gx + 1, 4, solid=0)
        m.place(Q.GEAR_BOX, lx, 5)
    m.solid(8, 5, "machine"); m.solid(9, 5, "machine")
    m.solid(22, 5, "machine"); m.solid(23, 5, "machine")
    m.solid(36, 5, "machine"); m.solid(37, 5, "machine")
    # ---- north quay dressing (against the wall)
    for (s, x, y) in ((Q.CRATES[0], 2, 5), (Q.CRATES[3], 3, 5), (Q.BARRELS[0], 4, 5), (Q.SACKS[0], 6, 5),
                      (V.FILING[0], 13, 4), (Q.BOOKCASE_1G[0], 15, 4), (Q.BARRELS[2], 17, 5), (Q.CRATES[1], 18, 5),
                      (Q.POTS[0], 26, 5), (Q.CRATES[4], 27, 5), (V.FILING[1], 29, 4), (Q.BARRELS[3], 31, 5),
                      (Q.SACKS[1], 32, 5), (Q.CRATES[2], 34, 5), (Q.BUCKETS[0], 35, 5), (Q.CRATES[5], 41, 5)):
        m.place(s, x, y)
    m.place(Q.SIGN_RUNES, 12, 4, solid=0)
    for x in (5, 16, 21, 28, 33, 40):
        m.place(Q.LANTERN_HOOK, x, 3, solid=0)
    m.anim("torch_wall", 20, 2, dy=-10)
    m.anim("torch_wall", 24, 2, dy=-10)
    m.anim("torch_wall", 7, 3, dy=-20)
    m.anim("torch_wall", 30, 3, dy=-20)
    # ---- south quay and the record stacks behind the filing-cabinet barricade
    m.place(V.FILING[0], 35, 22)
    for x in range(7, 35, 4):
        if x in (15, 27):
            m.place(V.FILING[(x // 4) % 2], x, 22)
            m.place(V.FILING[(x // 4 + 1) % 2], x + 2, 22)
        else:
            m.place(V.IRON_FENCE, x, 22)
    for x in range(7, 37):
        m.solid(x, 23, "fence")
    for (s, x, y) in ((Q.BOOKCASE_2G[0], 8, 25), (Q.BOOKCASE_2G[1], 11, 25), (Q.BOOKCASE_1G[0], 14, 25), (Q.RUBBLE_2[0], 16, 25),
                      (Q.BOOKCASE_2G[0], 19, 25), (Q.CUPBOARD_2, 22, 25), (Q.BOOKCASE_2G[1], 25, 25), (Q.RUBBLE_2[1], 28, 25),
                      (Q.BOOKCASE_2G[0], 31, 25), (Q.BOOKCASE_1G[1], 34, 25), (Q.SCROLLS[3], 13, 26), (Q.SCROLLS[0], 24, 26),
                      (Q.CRATES[1], 30, 26), (Q.SCROLLS[2], 35, 26)):
        m.place(s, x, y, solid=0)
    for (s, x, y) in ((Q.BARRELS[4], 2, 22), (Q.CRATES[2], 3, 22), (Q.BUCKETS[1], 2, 24),
                      (Q.CRATES[0], 41, 22), (Q.BARRELS[5], 40, 22), (Q.RUBBLE_S[1], 38, 24), (Q.SCROLLS[1], 20, 21)):
        m.place(s, x, y)
    for (s, x, y) in ((Q.CRATES[0], 7, 21), (Q.CRATES[3], 8, 21), (Q.SACKS[0], 7, 20), (Q.BARRELS[2], 12, 21),
                      (Q.SCROLLS[2], 13, 21), (Q.RUBBLE_2[3], 20, 20), (Q.CRATES[1], 29, 21), (Q.BARRELS[1], 30, 21),
                      (Q.POTS[2], 31, 21), (Q.BUCKETS[0], 36, 21), (Q.CRATES[4], 37, 21), (Q.SCROLLS[0], 26, 22)):
        m.place(s, x, y)
    m.place(Q.LANTERN_G[0], 5, 24)
    m.place(Q.LANTERN_G[1], 41, 24)
    m.reserve_rect(20, 1, 24, 7)
    ents(m, """tileset_over 8..9 8..19 bridge if=flag:t02c_gate1
switch gate1 11 6 flag=t02c_gate1 scene=CH18_GATE1
tileset_over 22..23 8..19 bridge if=flag:t02c_gate2
switch gate2 25 6 flag=t02c_gate2 scene=CH18_GATE2
tileset_over 36..37 8..19 bridge if=flag:t02c_gate3
switch gate3 39 6 flag=t02c_gate3 scene=CH18_GATE3
read 12 5 "Canal sign, repainted: 'LOCK GATES RAISE CROSSINGS. OPEN ONE, THE WATER SHIFTS.'"
chest T02C_C1 40 6 I003 2
spawn from_square 22 2 down
spawn from_registry 39 26 up
spawn from_echo 3 25 up
exit 22 1 T02_SQUARE_POST from_canals
exit 38..41 27 T02_REGISTRY_POST from_canals
spawn from_seals 40 9 left
exit 41 8..11 D02P_SEALS from_canals if=ch:CH20 locked="A clerk's door, bolted from inside. The registrar has the key - after the Accord."
exit 2..5 26 D02P_ECHO from_canals if=ch:CH20 locked="A sealed service door. Behind it, a machine is reading orders to no one."
""")
    return m


# ------------------------------------------------------------------------------------------------ Brackenford post
def brackenford_post():
    """The pilot's plan (T01_PLATFORM) after the flood: north houses and road, the railway, the halt platform and the
    main street, the market south of it, farms and the river at the bottom - now split by a flood channel where the
    quarry road and the market square ran. New crossings (the main footbridge; a second one being rebuilt), the
    shelter in the old bunkhouse, the footbridge depot at the platform, refugee camps on both banks, a memorial."""
    m = Map("T01_POST", 44, 30, "Brackenford - Divided by the Flood", "town_r01", music="M010", zone="T01",
            location="L_T01", region="R01", seed=101, save=True, phase="post")
    m.use(**V.MATS)
    m.fill("wetgrass")
    rng = m.rng
    # flood water: the drowned quarry gap (north), the channel through the middle, the swollen river (south)
    m.rect("flood", 0, 0, 43, 1)
    m.rect("flood", 0, 28, 43, 29)
    wb, eb = 18, 26
    for y in range(0, 30):
        wb = max(16, min(19, wb + rng.choice((-1, 0, 0, 1))))
        eb = max(25, min(28, eb + rng.choice((-1, 0, 0, 1))))
        if 12 <= y <= 14 or y == 22:
            wb, eb = 18, 26
        if y in (15, 16):
            wb = max(wb, 18)
        m.rect("silt_d", wb - 1, y, wb, y)
        m.rect("silt_d", eb, y, eb + 1, y)
        m.rect("flood", wb + 1, y, eb - 1, y)
    m.blob("flood", 22, 2, 5, 1.6)
    m.blob("flood", 22, 27, 6, 1.6)
    m.blob("flood", 9, 28, 5, 0.9)
    m.blob("flood", 36, 28, 5, 0.9)
    # roads: north road (8-9), the railway (10-11), the halt platform (12), the main street (13-16)
    m.path("silt", [(1, 8), (16, 8)], width=2)
    m.path("silt", [(28, 8), (42, 8)], width=2)
    m.path("silt", [(2, 7), (2, 8)], width=1)
    m.path("silt", [(35, 7), (35, 8)], width=1)
    m.rect("slabs", 1, 12, 16, 12)
    m.rect("slabs", 28, 12, 42, 12)
    m.rect("cobble", 0, 13, 17, 16)
    m.rect("cobble", 27, 13, 43, 16)
    m.rect("cobble_warm", 10, 17, 16, 21)                   # what is left of the market square (west bank)
    m.rect("cobble_warm", 27, 17, 29, 20)                   # ... and its east edge
    m.path("silt", [(4, 17), (4, 23)], width=1)
    m.path("silt", [(33, 21), (33, 25)], width=1)
    m.path("silt", [(12, 22), (10, 25)], width=1)
    for (cx, cy, rx, ry) in ((5, 25, 4, 1.8), (37, 25, 3.5, 1.6), (38, 18, 1.2, 1.0), (8, 10, 1, 0.6)):
        m.blob("silt_d", cx, cy, rx, ry)
    m.blob("shallow", 4, 26, 2.6, 0.9)
    m.blob("shallow", 38, 26, 2.2, 0.8)
    m.blob("shallow", 13, 25, 1.2, 0.7)
    # the railway: torn apart where the channel broke through
    m.rails_h(10, 0, 15)
    m.rails_h(11, 0, 14)
    m.rails_h(10, 29, 43)
    m.rails_h(11, 30, 43)
    for x in (7, 8, 36, 37):
        for y in (10, 11):
            m.kind[y][x] = "path"                               # level crossings
    # crossings over the channel
    V.bridge_h(m, 18, 26, 12, 14)                          # the new footbridge (main street)
    V.bridge_h(m, 18, 26, 22, 22, gaps=(21, 22, 24), posts_only=True)   # the second crossing, being rebuilt
    skip = {(x, y) for x in range(18, 27) for y in (12, 13, 14, 22)}
    # ---- north: the ridge (drowned at the channel), houses, gardens
    for x in list(range(-1, 15, 2)) + list(range(29, 44, 2)):
        m.place(A.TREES_M[(x * 7) % len(A.TREES_M)], x, 0, solid=1)
    m.place(A.PINE_TALL, 14, -1)
    m.place(V.DEAD_TREE, 16, 0)
    m.place(V.DEAD_TREE, 27, 1)
    m.place(A.H_THATCH_STONE, 1, 4)                         # the forewoman's house (sandbagged)
    m.solid(2, 7, "house")
    m.place(A.GUILD, 6, 4)                                  # the bunkhouse, now the shelter (desk at 7,8)
    m.place(V.RUIN_RED_HOUSE, 32, 4)                        # the clerk's rooms, half collapsed
    m.place(A.VEG_PLOTS, 11, 5)
    m.place(A.HAYSTACK, 15, 5)
    m.place(A.CART, 28, 5)
    m.place(A.SCARECROW, 30, 4)
    m.place(V.SACKS2[0], 2, 8)
    m.place(A.BARREL, 0, 6)
    m.place(A.BARREL, 5, 6)
    m.place(A.CRATE, 7, 8)                                  # the shelter's desk (inn 7,8)
    m.place(V.LAMP_TORCH, 8, 7)
    m.place(V.COTS[0], 10, 7)
    m.place(V.LAUNDRY[0], 12, 3)
    m.place(A.BUSHES[1], 5, 3)
    m.place(A.FLOWER_BUSH[2], 0, 3)
    # salvage pile beside the salvager (38,9)
    m.place(V.RUBBLE[0], 36, 6)
    m.place(V.RUBBLE[2], 31, 7)
    m.place(V.CAMP_CHESTS[2], 39, 8)                        # Hearthward's salvage chest
    m.place(A.CRATE_STACK, 40, 7)
    m.place(A.BARRELS, 41, 5)
    m.place(V.LOG_BIG, 38, 4)
    m.place(A.TREES_M[3], 41, 2)
    # ---- the halt: platform remains, the footbridge depot (counter 32,12), a derailed wagon
    for x in (4, 13, 31, 40):
        m.place(A.TORCH_STAND, x, 11, solid=1, kind="lamp")
    m.place(V.BROKEN_CART[0], 14, 9)
    m.place(A.STALLS[3], 31, 11)                            # depot counter: shop 32,12
    m.place(V.WOODPILE[0], 29, 12)
    m.place(V.WOODPILE[1], 30, 12)
    m.place(V.TOOLS, 34, 11)
    m.place(V.LOG_BIG, 38, 12)
    m.place(A.CRATE, 41, 12)
    m.place(A.BENCH, 9, 12)
    m.place(A.SIGNPOST, 15, 11)
    m.place(A.CRATE, 2, 12)
    # ---- south, west bank: market remains, the well, the ruined house, camp west, the memorial
    m.place(V.RUIN_STONE_HOUSE, 0, 16)
    m.place(A.WELL, 11, 19)
    m.place(A.STALLS[2], 14, 17)
    m.place(V.RUBBLE[2], 16, 18)
    m.place(A.BARREL_ROW[0], 10, 17)
    m.place(A.NOTICE, 5, 17)
    m.place(V.TENTS[4], 5, 20)
    m.place(V.TENTS[0], 1, 21)
    m.place(V.CAMPFIRE, 7, 18)
    m.place(V.CAULDRON[0], 8, 21)
    m.place(V.LAUNDRY[1], 13, 22)
    m.place(V.STELE, 9, 21)                                 # memorial (read 10,23)
    m.place(V.CANDLES, 11, 22)
    m.place(A.FLOWER_BUSH[0], 8, 23)
    m.place(A.SCARECROW, 6, 24)
    for x in range(0, 10, 2):
        m.place(st("town", "1", 14, 8, 2, 1, kind="fence"), x, 23) if x not in (4, 6) else None
    # ---- south, east bank: the storekeeper's stall (28,16), the bakery (sandbagged), camp east
    m.place(A.STALLS[4], 27, 17)
    m.place(A.H_TIMBER_SHED, 31, 17)                        # the bakery
    m.solid(33, 20, "house")
    m.place(V.SACKS2[1], 32, 21)
    m.place(V.TENTS[5], 38, 19)
    m.place(V.TENTS[1], 40, 22)
    m.place(V.TENTS[2], 35, 23)
    m.place(V.CAULDRON[1], 37, 22)
    m.place(V.LAUNDRY[0], 40, 17)
    m.place(A.CRATE_STACK, 30, 20)
    m.place(A.BARREL, 29, 21)
    m.place(A.HAY, 35, 17)
    m.place(A.TREES_M[5], 41, 24)
    m.place(A.TREES_M[9], 28, 23)
    m.place(A.TREES_M[12], 15, 23)
    m.place(V.DEAD_TREE, 1, 25)
    # flood debris in the water, the old south bridge's piles
    for (s, x, y) in ((V.LOG_BIG, 21, 5), (A.LOGS[0], 23, 18), (A.BARREL, 20, 25), (A.CRATE, 23, 9), (A.LOGS[1], 11, 28),
                      (A.CRATE_S, 34, 28)):
        m.place(s, x, y, solid=0)
    for x in (17, 19):
        m.place(st("forest", "2", 13, 10, 1, 1, solid=0), x, 28)
    # the main street: silt and puddles left by the water, sandbags and salvage along its edges
    for (x, y) in ((4, 15), (13, 14), (31, 15), (39, 13), (6, 14), (35, 16), (10, 16), (24, 15), (2, 13), (41, 15)):
        m.place(Q.PEBBLES[(x + y) % 4], x, y)
    for (x, y) in ((8, 15), (33, 14), (14, 13), (29, 13)):
        m.place(Q.SLIME[(x + y) % 2], x, y)
    for (s, x, y) in ((V.SACKS2[0], 16, 15), (A.CRATE_S, 30, 16), (V.SACKS2[0], 16, 12), (V.SACKS2[1], 27, 12),
                      (A.CRATE_S, 5, 16), (A.BARREL, 21, 16), (V.WOODPILE[0], 38, 16), (V.WOODPILE[1], 39, 16),
                      (A.CRATE, 42, 12), (A.BARREL, 1, 12)):
        m.place(s, x, y)
    # flood debris against the banks and in the channel
    for (s, x, y) in ((A.LOGS[1], 20, 7), (A.CRATE_S, 24, 4), (A.BARREL, 22, 16), (A.LOGS[0], 20, 20), (A.CRATE, 24, 25),
                      (A.LOGS[1], 22, 10), (V.RUBBLE[2], 21, 27)):
        m.place(s, x, y, solid=0)
    for x in (18, 19, 20):
        m.place(st("forest", "2", 13, 10, 1, 1, solid=0), x + 4 * (x % 2), 23)
    # rocks, stumps and wreckage breaking the water surface (river and channel)
    junk = A.ROCKS + [A.STUMP, A.LOGS[0], A.LOGS[1], A.CRATE_S, V.BROKEN_CART[1], A.BARREL]
    spots = [(1, 28), (4, 29), (7, 28), (13, 29), (15, 28), (27, 29), (30, 28), (33, 29), (37, 28), (40, 29), (42, 28),
             (20, 1), (23, 0), (25, 2), (21, 12 - 9), (19, 9), (24, 6), (23, 19), (19, 17), (25, 20), (21, 24), (19, 27),
             (24, 28), (22, 29), (2, 0), (6, 1), (11, 0), (32, 1), (38, 0), (42, 1), (9, 29), (18, 29), (26, 28),
             (35, 28), (20, 14 + 7), (24, 10), (21, 26), (3, 1)]
    for i, (x, y) in enumerate(spots):
        if m.mat[y][x] == "flood" and m.free(x, y) is False:
            m.place(junk[i % len(junk)], x, y, solid=0)
    # hedges, fences and trees closing the plots
    for (s, x, y) in ((A.TREES_M[6], 13, 23), (A.TREES_M[10], 0, 18), (A.TREES_M[2], 42, 19), (A.TREES_M[14], 29, 25),
                      (A.OAK2, 37, 1), (A.TREES_M[7], 9, 2)):
        m.place(s, x, y)
    for x in (28, 30):
        m.place(st("town", "1", 14, 8, 2, 1, kind="fence"), x, 22)
    for x in (38, 40):
        m.place(st("town", "1", 14, 9, 2, 1, kind="fence"), x, 24)
    m.place(A.FLOWER_BUSH[4], 10, 21)
    m.place(A.FLOWER_BUSH[1], 12, 21)
    # ground cover
    m.reserve_rect(17, 12, 27, 14)
    m.reserve_rect(0, 13, 43, 16)
    m.reserve_rect(6, 8, 13, 9)
    m.reserve_rect(4, 19, 7, 21)
    m.reserve_rect(35, 20, 37, 22)
    m.reserve_rect(9, 22, 11, 24)
    m.scatter(A.GRASS_TUFTS, 0, 2, 43, 27, 70, on=["wetgrass"], gap=1)
    m.scatter(V.DEAD_BUSH + A.BUSHES[:3], 0, 2, 43, 27, 22, on=["wetgrass"], gap=1)
    m.scatter(V.FERNS, 0, 2, 43, 27, 12, on=["wetgrass", "silt_d"], gap=1)
    m.scatter(A.ROCKS, 15, 2, 29, 27, 8, on=["silt_d"], gap=1)
    # ---- water surface
    m.water_anims(mat="flood", skip=skip)
    m.water_anims(mat="shallow", name="water_shallow")
    ents(m, """block 18..26 22 tile=water if=!ch:CH14 msg="Elowen's survivors are meant to rebuild this crossing. Not yet."
spawn world 1 14 right
spawn east 42 14 left
spawn default 1 14 right
exit 0 13..16 WORLD_POST l_t01
exit 43 13..16 WORLD_POST l_t01
npc forewoman 8 13 right sprite=mara talk=T01P_MARA
npc shelter_keep 12 9 down sprite=elder talk=T01P_SHELTER
inn 7 8 scene=T01P_INN
npc depot 33 12 left sprite=baker talk=T01P_DEPOT
shop 32 12 SHOP_T01
npc camp_west 6 20 right sprite=farmer talk=T01P_CAMP_WEST
npc camp_east 36 21 left sprite=worker talk=T01P_CAMP_EAST
npc storekeeper 28 16 down sprite=keeper talk=T01P_STOREKEEPER
npc salvager 38 9 left sprite=worker talk=T01P_SALVAGE if=ch:CH14
read 10 23 "A memorial stone. The quarry ledger's numbers have been chiselled off; names are being cut in their place, one at a time."
save 14 15
npc ov_maldrath 18 15 down sprite=C14 talk=OV_MALDRATH if=ch:CH20,!recruited:C14 #! ov:maldrath
""")
    return m


MAPS = [brackenford_post, market, square, square_post, canals]

if __name__ == "__main__":
    only = [a for a in sys.argv[1:]]
    texts = [f().save() for f in MAPS]
    print(write_group("veyr", texts))
