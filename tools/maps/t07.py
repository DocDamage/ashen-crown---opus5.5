"""T07 Hearthward (post-only refugee harbor): ponton market, communal hearth, Wayfarer berth; W_DECK (Wayfarer).
Tents become cabins across a visible sequence: tileset_over entries keyed on chapter progress."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOWN = dict(tileset="harbor", music="M016", zone="T07", region="R06", location="L_T07", phase="post")


def market():
    g = Grid(46, 30, "~")
    g.rect(3, 4, 42, 25, "d")             # pontoons
    g.rect(0, 13, 3, 16, "d")             # west walkway -> world
    g.rect(20, 25, 25, 29, "d")           # south: hearth
    g.rect(42, 5, 45, 8, "d")             # east: berth
    for y in (9, 18):
        g.rect(5, y, 40, y, "~")
        g.rect(12, y, 13, y, "d"); g.rect(30, y, 31, y, "d"); g.rect(21, y, 22, y, "d")
    g.text(6, 5, "]]  ]]  ]]")             # tents (become cabins)
    g.text(26, 5, "]] ]]")
    g.text(6, 20, "]]  ]]")
    g.text(33, 20, "]]  ]]")
    g.text(18, 12, "aaaa\nnnnn")          # market stall
    g.text(28, 13, "cr2")
    g.put(9, 14, "l"); g.put(36, 14, "l")
    # tents -> cabins as the town grows
    for (x, y) in ((6, 5), (10, 5), (14, 5), (26, 5), (29, 5)):
        g.e(f"tileset_over {x}..{x+1} {y} house if=ch:CH16")
    for (x, y) in ((6, 20), (10, 20), (33, 20), (37, 20)):
        g.e(f"tileset_over {x}..{x+1} {y} house if=ch:CH20")
    g.e("spawn world 1 14 right")
    g.e("spawn from_hearth 22 27 up")
    g.e("spawn from_berth 43 6 left")
    g.e("spawn default 22 22 up")
    g.e("exit 0 13..16 WORLD_POST l_t07 if=ch:CH13 locked=\"Mara: 'Not yet - you can barely stand. Help at the hearth first.'\"")
    g.e("exit 20..25 29 T07_HEARTH from_market")
    g.e("exit 45 5..8 T07_BERTH from_market")
    g.e("npc mara_m 16 15 down sprite=mara talk=T07_MARA")
    g.e("npc sign_keeper 8 11 down sprite=elder talk=T07_SIGNS")
    g.e("npc argue_a 27 16 left sprite=worker talk=T07_ARGUE")
    g.e("npc argue_b 26 16 right sprite=farmer talk=T07_ARGUE")
    g.e("npc bell_child 38 11 left sprite=child talk=T07_BELL_CHILD")
    g.e("npc fuel_worker 12 22 up sprite=worker talk=T07_FUEL")
    g.e("npc stall 20 14 down sprite=keeper talk=T07_SHOP")
    g.e("shop 20 13 SHOP_T07")
    g.e("npc ferryman 40 16 left sprite=sailor talk=T07_FERRY")
    g.e("read 5 13 \"A sign nailed to a post: 'BRACKENFORD BAKERY - BEST RYE ON THE RIVER'. The river is somewhere under the sea now.\"")
    g.e("read 34 10 \"Painted board: 'CINDERWAKE CANTEEN - SHIFT STEW'. Someone has added: 'still open (sort of)'.\"")
    g.decorate("cr2l]$b", 38, 71, "d")
    return g.emit("T07_MARKET", name="Hearthward - Ponton Market", **TOWN)


def hearth():
    g = Grid(36, 26, "~")
    g.rect(3, 3, 32, 22, "d")
    g.rect(15, 0, 20, 3, "d")             # north: market
    g.blob(17, 12, 5, 4, ",")
    g.put(17, 12, "!")                    # the hearth
    g.text(5, 5, "BB.BB")                 # cots
    g.text(5, 8, "BB.BB")
    g.text(26, 5, "tt")
    g.text(24, 17, "$$")
    # CH13: a broken walkway plank to repair (east side) - a simple path
    g.rect(29, 12, 32, 13, "d")
    g.rect(33, 12, 35, 13, "d")
    g.e("block 30 12..13 tile=hole if=!flag:t07_path msg=\"A broken section of walkway. Planks are stacked by the cots.\"")
    g.e("trigger 30 12..13 scene=T07_FIX_PATH touch=0 if=!flag:t07_path")
    g.e("spawn wake 8 6 down")
    g.e("spawn from_market 17 1 down")
    g.e("spawn default 17 4 down")
    g.e("exit 15..20 0 T07_MARKET from_hearth")
    g.e("trigger 7..9 6..7 scene=CH13_WAKE if=!event:CH13_WAKE")
    g.e("npc oriel_h 10 7 left sprite=C06 talk=T07_ORIEL if=!ch:CH13")
    g.e("npc lamp_keeper 22 9 left sprite=elder talk=T07_LAMP if=!ch:CH13")
    g.e("npc plank_pile 12 10 up sprite=worker talk=T07_PLANKS if=!ch:CH13")
    g.e("npc stranded 34 12 left sprite=survivor talk=T07_STRANDED")
    g.e("npc cook_h 20 16 up sprite=baker talk=T07_COOK")
    g.e("npc medic 27 6 down sprite=monk talk=T07_MEDIC")
    g.e("chest T07_SUPPLIES 25 17 I002 4 acq=T07_SUPPLIES")
    g.e("chest T07_SUPPLIES2 24 17 I004 3 acq=T07_SUPPLIES2")
    g.e("switch salvage_chest 28 18 scene=T07_SALVAGE")
    g.e("inn 5 11 scene=T07_INN")
    g.e("npc cot_keeper 5 12 up sprite=keeper talk=T07_INN")
    g.e("trigger 12..22 13..15 scene=CH23_EPILOGUES if=ch:CH23,!event:CH23_EPILOGUES")
    g.e("save 14 18")
    g.decorate("cr$bt", 18, 72, "d")
    return g.emit("T07_HEARTH", name="Hearthward - Communal Hearth", save="true", **TOWN)


def berth():
    g = Grid(40, 26, "~")
    g.rect(0, 5, 14, 20, "d")
    g.rect(14, 10, 36, 14, "d")           # the long berth
    g.rect(0, 5, 2, 8, "d")
    g.text(18, 4, "666")                  # small boats
    g.text(6, 7, "cc\nrr")
    g.e("spawn from_market 1 6 right")
    g.e("spawn from_deck 30 12 left")
    g.e("spawn default 3 12 right")
    g.e("exit 0 5..8 T07_MARKET from_berth")
    g.e("npc berth_master 10 14 up sprite=sailor talk=T07_BERTH_MASTER")
    g.e("npc crew_berth 33 11 down sprite=pilot talk=T07_WAYFARER if=ch:CH16")
    g.e("trigger 34..36 10..14 scene=T07_BOARD if=ch:CH16,!flag:dawn")
    g.e("trigger 16..18 10..14 scene=CH24_MORNING if=flag:dawn,!event:CH24_MORNING")
    g.e("trigger 34..36 10..14 scene=CH24_BOARD if=flag:dawn,event:CH24_MORNING")
    g.e("npc lamp_w1 17 9 down sprite=worker talk=T07_LAMP_W if=flag:dawn")
    g.e("npc lamp_w2 19 15 up sprite=worker talk=T07_LAMP_W if=flag:dawn")
    g.decorate("cr6", 8, 73, "d")
    return g.emit("T07_BERTH", name="Hearthward - Wayfarer Berth", **TOWN)


def deck():
    g = Grid(30, 20)
    g.rect(2, 2, 27, 17, ".")
    g.rect(13, 0, 16, 2, ".")              # ladder to the helm
    g.text(3, 3, "kkk..tt..kkk")
    g.text(20, 12, "BB\nBB")
    g.text(4, 13, "t.t")
    g.put(14, 1, "L")
    g.e("spawn from_world 15 4 down")
    g.e("spawn from_berth 15 4 down")
    g.e("spawn default 15 4 down")
    g.e("exit 13..16 0 WORLD_POST helm")
    g.e("npc deck_ivo 8 8 right sprite=C04 talk=W_IVO if=party:C04")
    g.e("npc deck_crew 18 6 down sprite=pilot talk=W_CREW")
    g.e("npc rumor_board 6 12 up sprite=scholar talk=W_RUMORS if=ch:CH20")
    g.e("npc formation_mate 24 8 left sprite=sailor talk=W_FORMATION")
    g.e("shop 10 4 SHOP_SHIP")
    g.e("inn 22 11 scene=W_REST")
    g.e("save 25 15")
    g.e("heal 23 15")
    g.e("read 20 4 \"The deck log. Every entry is signed by two crew, not one.\"")
    return g.emit("W_DECK", name="Wayfarer - Common Deck", tileset="ship", music="M019", zone="SHIP", phase="post", save="true")


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "t07.map"), [market(), hearth(), berth(), deck()], "T07 Hearthward + Wayfarer deck")
    print("t07 written")
