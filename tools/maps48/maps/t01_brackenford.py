"""Brackenford (T01) - pilot map for the overhaul. Crown March, quarry town on the rail line.
Shape: valley spine (layout standard section 4): wooded ridge and the quarry gap to the north, the rail halt across
the middle, a market square south of the platform, farm plots and the river to the south."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Map, write_group
import lib_r01 as A


def platform():
    m = Map("T01_PLATFORM", 40, 25, "Brackenford", "town_r01", music="M010", zone="T01", location="L_T01", region="R01", save=False)
    m.use(**A.MATS)
    m.fill("grass")
    # roads: quarry road north, main street, south road to the bridge
    m.path("dirt", [(20, 0), (20, 7)], width=3)
    m.path("dirt", [(4, 6), (36, 6)], width=2)
    m.rect("slabs", 1, 10, 38, 11)                      # the halt platform
    m.rect("cobble", 1, 12, 38, 13)                     # main street
    m.rect("cobble_warm", 16, 14, 27, 19)               # market square
    m.path("dirt", [(18, 19), (18, 24)], width=2)
    m.path("dirt", [(7, 14), (7, 17)], width=1)
    m.path("dirt", [(33, 14), (33, 17)], width=1)
    m.rect("water", 0, 21, 39, 22)
    m.rect("wood", 17, 21, 19, 22, kind="bridge")
    m.water_anims(skip={(x, y) for x in range(17, 20) for y in (21, 22)})
    m.rails_h(8, 0, 39)
    m.rails_h(9, 0, 39)
    for x in (19, 20, 21):
        for y in (8, 9):
            m.kind[y][x] = "path"                          # level crossing
    # north ridge: trees along the top, broken by the quarry gap
    for x in list(range(-1, 17, 2)) + list(range(24, 40, 2)):
        m.place(A.TREES_M[(x * 7) % len(A.TREES_M)], x, -1, solid=1)
    m.place(A.PINE_TALL, 15, -2)
    m.place(A.PINE_TALL, 23, -2)
    # houses on the north side
    m.place(A.H_THATCH_STONE, 2, 2)                     # Forewoman's house, door (3,5)
    m.place(A.H_TIMBER, 33, 2)                          # Clerk's rooms, door (35,5)
    m.place(A.VEG_PLOTS, 9, 3)
    m.place(A.VEG_PLOTS, 25, 3)
    m.place(A.HAYSTACK, 14, 3)
    m.place(A.BARREL, 7, 4)
    m.place(A.CRATE_STACK, 8, 4)
    m.place(A.CART, 30, 3)
    m.place(A.SCARECROW, 29, 2)
    # platform dressing
    for x in (6, 14, 26, 34):
        m.place(A.TORCH_STAND, x, 9, solid=1, kind="lamp")
    m.place(A.BENCH, 9, 10)
    m.place(A.BENCH2, 30, 10)
    m.place(A.SIGNPOST, 24, 10)
    m.place(A.CRATE, 2, 10)
    m.place(A.BARRELS, 3, 10)
    m.place(A.SACKS, 36, 10)
    # south side: bakery and bunkhouse, market stalls, well
    m.place(A.H_TIMBER_SHED, 5, 13)                     # bakery, door (7,16)
    m.place(A.GUILD, 32, 13)                            # bunkhouse, door (33,16)
    m.place(A.STALLS[1], 21, 14)                        # the keeper's stall (shop at the counter)
    m.place(A.STALLS[2], 16, 14)
    m.place(A.STALLS[4], 25, 14)
    m.place(A.FOUNTAIN, 21, 17)
    m.place(A.CRATE_S, 18, 16)
    m.place(A.BARREL_ROW[0], 26, 17)
    m.place(A.WELL, 11, 17)
    m.place(A.HANDCART, 12, 14)
    m.place(A.NOTICE, 29, 14)
    m.place(A.BARREL, 4, 15)
    m.place(A.CRATE_STACK, 9, 15)
    m.place(A.BARREL, 36, 15)
    m.place(A.HAY, 37, 17)
    # farm plots and orchard south-west, flowers south-east
    m.place(A.WHEAT, 1, 17)
    m.place(A.SCARECROW, 3, 18)
    for (x, y) in ((7, 18), (13, 19), (27, 19), (37, 19)):
        m.place(A.TREES_M[(x + y) % len(A.TREES_M)], x, y - 2)
    # river banks, south woods (exit gap at 18-19)
    for x in list(range(-1, 16, 2)) + list(range(21, 40, 2)):
        m.place(A.TREES_M[(x * 5) % len(A.TREES_M)], x, 22, solid=1)
    m.reserve_rect(16, 18, 20, 24)
    m.scatter(A.GRASS_TUFTS, 0, 2, 39, 20, 26, on=["grass"], gap=1)
    m.scatter(A.BUSHES + A.FLOWER_BUSH, 0, 14, 39, 20, 10, on=["grass"], gap=1)
    m.scatter(A.BUSHES + A.FLOWER_BUSH, 0, 2, 39, 7, 8, on=["grass"], gap=1)
    # entities (ids, spawn names and scenes unchanged)
    for e in """spawn start 19 11 up
spawn world 18 23 up
spawn from_quarry 20 1 down
spawn from_bakery 7 17 down
spawn from_bunk 33 17 down
spawn from_left 3 6 down
spawn from_right 35 6 down
exit 19..21 0 D01_R01 from_town if=flag:sc00_done locked="Holt: The inspection waits for no one, Captain. Talk to the crew first."
exit 18..19 24 WORLD t01 if=ch:CH01 locked="Mara: Not before the lift. People are down there."
door 7 16 T01_BAKERY entry sfx=FX008
door 33 16 T01_BUNKHOUSE entry sfx=FX008
door 3 5 T01_HOUSE_W entry sfx=FX008
door 35 5 T01_HOUSE_E entry sfx=FX008
npc inspector 20 10 down sprite=inspector talk=T01_INSPECTOR if=!event:OPENING
npc worker_list 14 11 down sprite=worker talk=T01_WORKER_LIST if=!ch:CH01
npc keeper 22 14 down sprite=keeper talk=T01_KEEPER solid=1
npc child 28 7 left sprite=child talk=T01_CHILD wander=1
npc farmer 5 19 right sprite=farmer talk=T01_FARMER
npc elder 11 11 down sprite=elder talk=T01_ELDER
npc laundress 12 6 down sprite=noble talk=T01_LAUNDRESS
npc guard_t 27 11 left sprite=guard talk=T01_GUARD if=!ch:CH01
npc mara_town 20 16 down sprite=mara talk=T01_MARA_AFTER if=ch:CH01
npc cartman 32 11 left sprite=worker talk=T01_CARTMAN
shop 22 15 SHOP_T01
sign 24 11 "Brackenford Halt. Crown Quarry: north road. Veyr: south over the river.\"""".split("\n"):
        m.ent(e.replace('\\"', '"'))
    return m


if __name__ == "__main__":
    texts = [platform().save()]
    print(write_group("t01", texts))
