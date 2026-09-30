"""Hearthward (T07) - hand-made maps for the survivors' town on the Ember Sea (post-fault only).

Shape: port (layout standard section 4), built on water: pontoon rafts lashed together in strips, joined by plank
bridges over red-glowing channels, moored salvaged hulls, and black basalt reefs with lava seams closing the edges.
  T07_MARKET  Pontoon Market: three pontoon strips. North: the tent row under the moored hulk (the landmark ship
              seen from the entrance), gangway east to the berth. Middle: the market plaza (stalls, fire bowl, the
              sign wall of old shop boards, the Cinderwake canteen, the salvaged bell, the ferry). South: shacks,
              the lamp-fuel depot and salvage yard, gangway south to the hearth.
  T07_HEARTH  Communal Hearth: a black-rock islet carrying the great hearth drum, ringed by pontoons: cots under
              canvas (the inn), the infirmary awning, the cook fires and the hearth chest, the broken east walkway
              to the stranded family's raft.
  T07_BERTH   Airship Berth: the yard pontoon (timber, winches, the rescue-ship plans) and a long pier out to the
              mooring mast where the Lanternwake ties up after CH16.
Levels: water, pontoon deck and the raised black rock (hearth islet, reefs); the market and berth read their height
from the hulks and the mast rising out of the sea."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import write_group, Stamp, C
import lib_hearth as L
from lib_hearth import Hmap

MARKET_ENTS = r'''tileset_over 6..7 5 house if=ch:CH16
tileset_over 10..11 5 house if=ch:CH16
tileset_over 14..15 5 house if=ch:CH16
tileset_over 26..27 5 house if=ch:CH16
tileset_over 29..30 5 house if=ch:CH16
tileset_over 6..7 20 house if=ch:CH20
tileset_over 10..11 20 house if=ch:CH20
tileset_over 33..34 20 house if=ch:CH20
tileset_over 37..38 20 house if=ch:CH20
spawn world 1 14 right
spawn from_hearth 22 27 up
spawn from_berth 43 6 left
spawn default 22 22 up
exit 0 13..16 WORLD_POST l_t07 if=ch:CH13 locked="Mara: 'Not yet - you can barely stand. Help at the hearth first.'"
exit 20..25 29 T07_HEARTH from_market
exit 45 5..8 T07_BERTH from_market
npc mara_m 16 15 down sprite=mara talk=T07_MARA
npc sign_keeper 8 11 down sprite=elder talk=T07_SIGNS
npc argue_a 27 16 left sprite=worker talk=T07_ARGUE
npc argue_b 26 16 right sprite=farmer talk=T07_ARGUE
npc bell_child 38 11 left sprite=child talk=T07_BELL_CHILD
npc fuel_worker 12 22 up sprite=worker talk=T07_FUEL
npc stall 20 14 down sprite=keeper talk=T07_SHOP
shop 20 13 SHOP_T07
npc ferryman 40 16 left sprite=sailor talk=T07_FERRY
read 5 13 "A sign nailed to a post: 'BRACKENFORD BAKERY - BEST RYE ON THE RIVER'. The river is somewhere under the sea now."
read 34 10 "Painted board: 'CINDERWAKE CANTEEN - SHIFT STEW'. Someone has added: 'still open (sort of)'."'''

HEARTH_ENTS = r'''block 30 12..13 tile=hole if=!flag:t07_path msg="A broken section of walkway. Planks are stacked by the cots."
trigger 30 12..13 scene=T07_FIX_PATH touch=0 if=!flag:t07_path
spawn wake 8 6 down
spawn from_market 17 1 down
spawn default 17 4 down
exit 15..20 0 T07_MARKET from_hearth
trigger 7..9 6..7 scene=CH13_WAKE if=!event:CH13_WAKE
npc oriel_h 10 7 left sprite=C06 talk=T07_ORIEL if=!ch:CH13
npc lamp_keeper 22 9 left sprite=elder talk=T07_LAMP if=!ch:CH13
npc plank_pile 12 10 up sprite=worker talk=T07_PLANKS if=!ch:CH13
npc stranded 34 12 left sprite=survivor talk=T07_STRANDED
npc cook_h 20 16 up sprite=baker talk=T07_COOK
npc medic 27 6 down sprite=monk talk=T07_MEDIC
chest T07_SUPPLIES 25 17 I002 4 acq=T07_SUPPLIES
chest T07_SUPPLIES2 24 17 I004 3 acq=T07_SUPPLIES2
switch salvage_chest 28 18 scene=T07_SALVAGE
inn 5 11 scene=T07_INN
npc cot_keeper 5 12 up sprite=keeper talk=T07_INN
trigger 12..22 13..15 scene=CH23_EPILOGUES if=ch:CH23,!event:CH23_EPILOGUES
save 14 18
npc ov_namer 18 10 down sprite=scholar talk=OV_NAMER name="Name-Keeper" #! ov:namer_t07'''

BERTH_ENTS = r'''spawn from_market 1 6 right
spawn from_deck 30 12 left
spawn default 3 12 right
exit 0 5..8 T07_MARKET from_berth
npc berth_master 10 14 up sprite=sailor talk=T07_BERTH_MASTER
npc crew_berth 33 11 down sprite=pilot talk=T07_WAYFARER if=ch:CH16
trigger 34..36 10..14 scene=T07_BOARD if=ch:CH16,!flag:dawn
trigger 16..18 10..14 scene=CH24_MORNING if=flag:dawn,!event:CH24_MORNING
trigger 34..36 10..14 scene=CH24_BOARD if=flag:dawn,event:CH24_MORNING
npc lamp_w1 17 9 down sprite=worker talk=T07_LAMP_W if=flag:dawn
npc lamp_w2 19 15 up sprite=worker talk=T07_LAMP_W if=flag:dawn'''


def _rng(s):
    a, _, b = s.partition("..")
    return range(int(a), int(b or a) + 1)


def add_ents(m, text):
    """Adds the entity lines verbatim and reserves every cell an entity stands on (exits, spawns, npcs, triggers)."""
    for line in text.split("\n"):
        m.ent(line)
        t = line.split()
        if t[0] in ("spawn", "npc", "trigger", "exit"):
            if t[0] == "npc":
                xs, ys = _rng(t[2]), _rng(t[3])
            else:
                xs, ys = _rng(t[1] if t[0] != "spawn" else t[2]), _rng(t[2] if t[0] != "spawn" else t[3])
            if t[0] == "trigger" and len(xs) * len(ys) > 9:
                ys = ys[:1]                             # big touch areas: one row kept clear is enough
            m.reserve([(x, y) for x in xs for y in ys])


def rocks(m, cells_rect, n, seed_stamps=None):
    """Black rock decals (boulders, cracks glowing with lava) on rock cells in a rectangle."""
    x0, y0, x1, y1 = cells_rect
    stamps = seed_stamps or (L.ROCKS_BIG + L.ROCKS_S + L.ROCKS_S)
    placed = 0
    for i in range(n * 30):
        if placed >= n:
            break
        s = m.rng.choice(stamps)
        x = m.rng.randint(x0, max(x0, x1 - s.w + 1))
        y = m.rng.randint(y0, max(y0, y1 - s.h + 1))
        if all(0 <= x + dx < m.w and 0 <= y + dy < m.h and m.mat[y + dy][x + dx] == "rock" for dx in range(s.w) for dy in range(s.h)):
            m.place(s, x, y)
            placed += 1


def sea_dress(m, stamps, rect, n, margin=1):
    """Objects standing in the open sea (reefs, driftwood, buoys): every covered cell and a margin must be sea."""
    x0, y0, x1, y1 = rect
    placed = 0
    for i in range(n * 40):
        if placed >= n:
            break
        s = m.rng.choice(stamps)
        x = m.rng.randint(x0, max(x0, x1 - s.w + 1))
        y = m.rng.randint(y0, max(y0, y1 - s.h + 1))
        ok = True
        for yy in range(y - margin, y + s.h + margin):
            for xx in range(x - margin, x + s.w + margin):
                if 0 <= xx < m.w and 0 <= yy < m.h and (m.mat[yy][xx] != "sea" or (xx, yy) in m._placed_sea):
                    ok = False
        if ok and 0 <= x and x + s.w <= m.w and 0 <= y and y + s.h <= m.h:
            m.place(s, x, y)
            for yy in range(y, y + s.h):
                for xx in range(x, x + s.w):
                    m._placed_sea.add((xx, yy))
            placed += 1


def pilings(m, cells):
    """Timber pilings on water cells (usually just off a pontoon edge)."""
    for i, (x, y) in enumerate(cells):
        if m.mat[y][x] == "sea":
            m.place(L.PILING[(x * 3 + y) % 4], x, y)
            m._placed_sea.add((x, y))


def edge_pilings(m, every=4, off=0):
    """Pilings on the sea cells just below pontoon south edges, every few cells."""
    cells = []
    for y in range(1, m.h):
        for x in range(m.w):
            if m.mat[y][x] == "sea" and m.mat[y - 1][x] in L.DOCKS and (x + off) % every == 0:
                cells.append((x, y))
    pilings(m, cells)


def deck_decals(m, n):
    """Scatter flat board decals on open pontoon cells (no two side by side)."""
    used = set()
    cells = [(x, y) for y in range(m.h) for x in range(m.w) if m.mat[y][x] in L.DOCKS and m.free(x, y)]
    m.rng.shuffle(cells)
    for (x, y) in cells:
        if n <= 0:
            break
        if any((x + dx, y + dy) in used for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            continue
        m.place(m.rng.choice(L.DECK_DECALS), x, y)
        used.add((x, y))
        n -= 1


def lamp(m, x, y, anim="brazier"):
    """Standing fire basket (animated, 1x2, blocks its foot cell)."""
    m.anim(anim, x, y - 1, h=96, solid=True, kind="lamp")


# ================================================================================================ T07_MARKET
def market():
    m = Hmap("T07_MARKET", 46, 30, "Hearthward - Ponton Market", "harbor", music="M016", zone="T07",
             location="L_T07", region="R06", phase="post", seed=7071)
    m.use(**L.MATS)
    add_ents(m, MARKET_ENTS)
    m.fill("sea")
    # black rock reefs closing the west edge (the pontoon road leaves between them) and the east corners
    m.blob("rock", 0.6, 5.0, 2.4, 6.2, rough=0.3)
    m.blob("rock", 0.4, 24.0, 2.6, 6.0, rough=0.3)
    m.blob("rock", 44.8, 1.2, 2.2, 2.4, rough=0.3)
    m.blob("rock", 44.6, 26.5, 2.4, 4.0, rough=0.3)
    m.blob("lava", 0.4, 4.0, 0.9, 1.6, rough=0.2)
    m.blob("lava", 0.2, 25.0, 1.0, 1.4, rough=0.2)
    m.blob("lava", 45.2, 27.5, 0.8, 1.2, rough=0.2)
    # north pontoon strip (tent row) + gangway east to the berth
    m.rect("planks", 3, 4, 42, 8)
    m.rect("planks_old", 16, 4, 25, 8)
    m.rect("planks_grey", 31, 4, 36, 8)
    m.rect("planks_grey", 43, 5, 45, 8)
    # middle strip: the market
    m.rect("planks", 3, 10, 42, 17)
    m.rect("planks_old", 3, 10, 11, 17)
    m.rect("deck", 12, 14, 30, 17)
    m.rect("planks_grey", 0, 13, 2, 16)                # pontoon road west (world exit)
    # south strip
    m.rect("planks", 3, 19, 42, 25)
    m.rect("planks_old", 14, 19, 27, 25)
    m.rect("planks_grey", 3, 21, 8, 25)
    m.rect("planks_grey", 20, 26, 25, 29)               # gangway south to the hearth
    # plank bridges over the channels (rows 9 and 18)
    for x in (9, 21, 30, 40):
        m.rect("bridge", x, 9, x + 1, 9)
    for x in (15, 23, 30, 40):
        m.rect("bridge", x, 18, x + 1, 18)
    # walking lines kept clear
    m.reserve_rect(3, 6, 42, 7)                         # north walkway
    m.reserve_rect(12, 14, 30, 14)                      # market street in front of the stalls
    m.reserve_rect(3, 22, 42, 22)                       # south walkway
    m.reserve_rect(21, 21, 24, 29)                      # to the south gangway
    m.reserve_rect(20, 21, 25, 22)
    for x in (9, 21, 30, 40):
        m.reserve_rect(x, 8, x + 1, 10)
    for x in (15, 23, 30, 40):
        m.reserve_rect(x, 17, x + 1, 19)
    m.reserve_rect(0, 13, 3, 16)
    m.reserve_rect(42, 5, 45, 8)

    # ---- the moored hulk along the north edge (landmark; its hull meets the pontoon at row 4)
    hulk = Stamp(L.P, "B1-2", 0, 0, px=(0, 104, 722, 446), solid=0, base=440)
    m.place(hulk, 17, 0, dy=4 * C - 440 - 0)
    # ---- north strip dressing (tents on the CH16 cabin plots, cargo under the hulk)
    m.place(L.FISH_RACK, 3, 4)
    m.place(L.BUCKETS[1], 5, 5)
    m.place(L.PATCH_TENTS[0], 6, 4)
    m.place(L.BARRELS[0], 8, 5)
    m.place(L.CRATES[1], 9, 5)
    m.place(L.LANTERN, 9, 4)
    m.place(L.SCRAP_TENTS[0], 10, 4)
    m.place(L.LAUNDRY, 12, 4)
    m.place(L.LOW_TENTS[0], 14, 4)
    m.place(L.CRATE_TALL[0], 16, 4)
    m.place(L.WINCH, 17, 4)
    m.place(L.V_CRATE_PILE, 19, 4)
    m.place(L.V_NET_PILE, 21, 4)
    m.place(L.SACKS, 23, 5)
    m.place(L.SPOOLS[0], 24, 5)
    m.place(L.PLANK_STACK[1], 24, 3)
    m.place(L.PATCH_TENTS[1], 26, 4)
    m.place(L.V_BARRELS[2], 28, 5)
    m.place(L.CAMP_LANTERN, 28, 4)
    m.place(L.SCRAP_TENTS[2], 29, 4)
    m.place(L.WATER_TUB, 31, 4)
    m.place(L.FISH_HANG, 33, 3)
    m.place(L.NET_RACK, 35, 4)
    m.place(L.V_TENT[0], 37, 4)
    m.place(L.LANTERN2, 39, 5)
    m.place(L.V_BARREL_PILE, 40, 4)
    m.place(L.SACKS, 41, 5)
    # along the north strip's water edge (row 8)
    m.place(L.ROPE_BIG[0], 3, 8)
    m.place(L.CAPSTAN, 5, 7)
    m.place(L.BARRELS[3], 7, 8)
    m.place(L.CRATES[0], 12, 8)
    m.place(L.LIFE_RING[0], 13, 8)
    m.place(L.D_CRATES[0], 15, 7)
    m.place(L.SMALL_CARGO[0], 16, 8)
    m.place(L.ROPE, 17, 8)
    m.place(L.PALLETS[0], 24, 8)
    m.place(L.SMALL_CARGO[4], 25, 8)
    m.place(L.BUCKETS[3], 27, 8)
    m.place(L.ROPE_BIG[1], 28, 8)
    m.place(L.V_ROPE_COIL, 33, 8)
    m.place(L.CHESTS[0], 34, 8)
    m.place(L.BARRELS[4], 35, 8)
    m.place(L.LIFE_RING[1], 38, 8)
    lamp(m, 20, 8)
    lamp(m, 36, 5)

    # ---- middle strip: the market
    # sign wall of old shop boards (sign keeper at 8,11; the Brackenford bakery sign on its post at 5,13)
    m.place(L.SIGNS[0], 3, 10)
    m.place(L.SIGNS[2], 5, 10)
    m.place(L.ARROWS[0], 7, 10)
    m.place(L.D5_SIGNS[0], 5, 12)
    m.place(L.D5_SIGNS[4], 3, 11)
    m.place(L.CRATES[0], 4, 12)
    m.place(L.BARRELS[1], 3, 17)
    m.place(L.SACKS, 4, 17)
    m.place(L.V_FOODBOX[0], 5, 17)
    m.place(L.FIREWOOD[0], 7, 16)
    m.place(L.CAMP_STOOLS[0], 6, 15)
    lamp(m, 11, 11)
    # stall row (shop counter at 20,13, keeper in front)
    m.place(L.STALL_LEAN, 12, 12)
    m.place(L.CAMP_CRATES[0], 14, 12)
    m.place(L.STALLS[1], 16, 12)
    m.place(L.CRATES_B7[1], 18, 12)
    m.place(L.STALLS[0], 19, 12)
    m.place(L.STALLS[3], 22, 12)
    m.place(L.STALL_TOOLS, 25, 12)
    m.place(L.SMALL_CARGO[2], 28, 13)
    m.place(L.SMALL_CARGO[5], 29, 13)
    m.place(L.BARRELS_B7[0], 24, 11)
    m.place(L.CRATES_B7[2], 17, 11)
    m.place(L.D5_SACKPILE[0], 13, 10)
    m.place(L.V_CRATES3, 15, 10)
    m.place(L.BUCKETS[0], 23, 10)
    m.place(L.D_CRATES[2], 25, 10)
    m.place(L.CRATES_B7[3], 27, 11)
    # plaza: fire bowl, the roofs-or-water argument between the timber stack and the water butts
    m.place(L.FIREBOWL, 20, 15)
    m.place(L.CAMP_STOOLS[1], 19, 16)
    m.place(L.CAMP_STOOLS[2], 22, 16)
    m.place(L.PLANK_STACK[0], 24, 15)
    m.place(L.WATER_BARRELS, 28, 15)
    m.place(L.BUCKET_W, 30, 16)
    m.place(L.D5_PLANKS, 12, 16)
    m.place(L.PALLETS[1], 14, 17)
    m.place(L.CAMP_BARRELS[0], 17, 17)
    # Cinderwake canteen (board at 34,10), the salvaged bell (child at 38,11), the ferry (40,16)
    m.place(L.D5_SIGNS[3], 34, 9)
    m.place(L.STALL_AWNING, 35, 10)
    m.place(L.TRESTLE[0], 31, 12)
    m.place(L.STOOLS_V[0], 31, 14)
    m.place(L.STOOLS_V[2], 33, 14)
    m.place(L.TRIPOD_POT, 36, 13)
    m.place(L.CAULDRONS[1], 35, 14)
    m.place(L.FIREWOOD_S, 32, 11)
    m.place(L.SIGN_ARCH, 39, 10)
    m.place(L.BELL, 39, 10, dx=24, dy=14)
    m.place(L.CAPSTAN, 41, 13)
    m.place(L.ROPE, 42, 16)
    m.place(L.LANTERN3, 42, 17)
    m.place(L.V_BOAT2, 43, 16, solid=0)
    m.place(L.FISH_CRATE, 32, 17)
    m.place(L.BUCKETS[2], 33, 17)
    m.place(L.V_BARRELS[0], 36, 17)
    m.place(L.CRATES[1], 37, 17)
    m.place(L.SACKS, 38, 17)
    lamp(m, 12, 13)
    lamp(m, 30, 11)

    # ---- south strip
    m.place(L.SALVAGE[0], 3, 19)
    m.place(L.SCRAP_FENCE[0], 5, 19)
    m.place(L.PATCH_TENTS[2], 6, 19)
    m.place(L.D5_SCRAP[0], 8, 19)
    m.place(L.SCRAP_TENTS[1], 10, 19)
    m.place(L.BARRELS_B8[0], 12, 20)                   # lamp fuel (worker at 12,22)
    m.place(L.CRATES_B8[1], 13, 20)
    m.place(L.CRATES_B8[3], 14, 20)
    m.place(L.LAUNDRY2, 17, 19)
    m.place(L.BUCKETS[1], 19, 20)
    m.place(L.WORKBENCH, 27, 19)
    m.place(L.SHACKS[0], 29, 19)
    m.place(L.D_CRATES[1], 31, 19)
    m.place(L.D_CRATES[3], 32, 19)
    m.place(L.V_TENT[1], 33, 19)
    m.place(L.HIDE_RACK[0], 35, 19)
    m.place(L.PATCH_TENTS[4], 37, 19)
    m.place(L.FISH_RACK2, 39, 19)
    m.place(L.SACKS, 41, 20)
    m.place(L.V_BARRELS[3], 42, 20)
    m.place(L.CAMP_LANTERN, 26, 20)
    # below the walkway
    m.place(L.SALVAGE[1], 3, 23)
    m.place(L.D5_PLANKS, 5, 24)
    m.place(L.CHEST_CRATE, 7, 23)
    m.place(L.PIT_POT, 9, 23)
    m.place(L.CAMP_STOOLS[3], 11, 24)
    m.place(L.SHACKS[3], 13, 23)
    m.place(L.D5_SACKPILE[2], 15, 24)
    m.place(L.FIREWOOD[1], 17, 24)
    m.place(L.BARRELS[5], 19, 25)
    m.place(L.CRATES[2], 26, 25)
    m.place(L.SHACKS[4], 27, 23)
    m.place(L.GRILL, 29, 23)
    m.place(L.CAMP_STOOLS[4], 31, 24)
    m.place(L.NET_RACK, 32, 23)
    m.place(L.V_BOAT, 34, 24)
    m.place(L.V_OARS, 37, 25)
    m.place(L.SHACKS[5], 39, 23)
    m.place(L.CAMP_BARRELS[1], 41, 24)
    m.place(L.CRATES[0], 42, 25)
    lamp(m, 19, 23)
    lamp(m, 26, 23)
    m.place(L.LANTERN, 20, 26)
    m.place(L.LANTERN2, 25, 26)
    m.place(L.D_CRATES[2], 20, 24)
    m.place(L.SACKS, 25, 25)
    m.place(L.BARRELS[2], 18, 8)
    m.place(L.CRATES[1], 19, 8)
    m.place(L.D5_SIGNS[1], 4, 14)
    m.place(L.ARROWS[2], 10, 13)
    m.place(L.BARRELS[0], 9, 16)
    m.place(L.SACKS, 10, 16)
    m.place(L.CAMP_TABLE, 14, 15)
    m.place(L.D5_POTS[0], 15, 21)
    m.place(L.CAMP_CRATES[2], 16, 20)
    m.place(L.V_BARRELS[4], 27, 21)
    m.place(L.CRATES_B7[0], 32, 21)
    m.place(L.BUCKETS[3], 36, 21)
    m.place(L.LANTERN3, 6, 8)
    m.place(L.BUCKETS[0], 14, 8)
    m.place(L.SACKS, 26, 8)
    m.place(L.V_CRATES[1], 32, 8)
    m.place(L.BARRELS[1], 37, 8)
    m.place(L.BARRELS[2], 28, 10)
    m.place(L.CRATES[0], 29, 10)
    m.place(L.BUCKETS[1], 3, 21)
    m.place(L.CRATES[2], 41, 21)
    m.place(L.V_FOODBOX[1], 19, 10)
    m.place(L.BUCKETS[2], 38, 15)
    m.place(L.CAMP_BARRELS[1], 34, 16)
    m.place(L.SACKS, 18, 17)
    m.place(L.PAILS[0], 11, 17)
    m.place(L.CRATES_B7[3], 36, 24)
    m.anim("chimney_smoke", 13, 21, dx=24, h=96, flat=False)
    m.anim("chimney_smoke", 39, 21, dx=10, h=96, flat=False)

    # ---- rock and lava detail; animated sea
    rocks(m, (0, 0, 2, 12), 5)
    rocks(m, (0, 17, 2, 29), 5)
    rocks(m, (43, 0, 45, 4), 2)
    rocks(m, (42, 22, 45, 29), 3)
    edge_pilings(m, every=5, off=2)
    sea_dress(m, L.REEF_BIG, (0, 0, 16, 3), 3)
    sea_dress(m, L.REEF_BIG, (33, 0, 45, 3), 2)
    sea_dress(m, L.REEF_S + L.DRIFT + L.BUOYS, (0, 0, 16, 3), 4)
    sea_dress(m, L.REEF_S + L.BUOYS, (33, 0, 45, 3), 3)
    sea_dress(m, L.REEF_BIG + L.REEF_S + L.DRIFT, (0, 26, 19, 29), 9)
    sea_dress(m, L.REEF_BIG + L.REEF_S + L.DRIFT, (26, 26, 45, 29), 9)
    sea_dress(m, L.REEF_S + L.BUOYS + L.DRIFT, (43, 9, 45, 24), 4)
    sea_dress(m, L.BUOYS, (3, 9, 42, 9), 2, margin=0)
    sea_dress(m, L.DRIFT[:1] + L.BUOYS, (3, 18, 42, 18), 2, margin=0)
    deck_decals(m, 40)
    skip = m.dock_edges(set())
    m.sea_anims(skip)
    return m



# ================================================================================================ T07_HEARTH
def hearth():
    m = Hmap("T07_HEARTH", 36, 26, "Hearthward - Communal Hearth", "harbor", music="M016", zone="T07",
             location="L_T07", region="R06", save=True, phase="post", seed=7072)
    m.use(**L.MATS)
    add_ents(m, HEARTH_ENTS)
    m.fill("sea")
    m.blob("rock", 0.6, 3.0, 2.4, 4.2, rough=0.3)
    m.blob("rock", 0.8, 21.0, 2.8, 6.0, rough=0.3)
    m.blob("rock", 33.8, 3.0, 3.2, 4.0, rough=0.3)
    m.blob("rock", 33.0, 23.0, 4.0, 3.4, rough=0.3)
    m.blob("lava", 0.4, 22.0, 1.2, 1.8, rough=0.2)
    m.blob("lava", 34.5, 2.0, 1.2, 1.2, rough=0.2)
    m.blob("lava", 33.5, 24.0, 1.6, 1.0, rough=0.2)
    # the pontoon ring, its rafts, and the black-rock islet that carries the hearth
    m.rect("planks", 3, 3, 28, 22)
    m.rect("planks_old", 3, 3, 11, 10)                  # cot raft (the inn)
    m.rect("planks_grey", 23, 3, 28, 8)                 # infirmary raft
    m.rect("deck", 3, 17, 13, 22)
    m.rect("planks_old", 22, 17, 28, 22)
    m.blob("basalt", 17.5, 12.2, 6.2, 4.3, rough=0.25)
    m.rect("planks_grey", 15, 0, 20, 2)                 # gangway north to the market
    m.rect("bridge", 29, 12, 31, 13)                    # the east walkway (broken at 30 until CH13's fix)
    m.rect("planks_old", 32, 10, 35, 15)                # the stranded family's raft
    # routes
    m.reserve_rect(15, 0, 20, 5)
    m.reserve_rect(3, 6, 28, 7)
    m.reserve_rect(13, 16, 28, 16)
    m.reserve_rect(23, 12, 32, 13)
    m.reserve_rect(5, 7, 5, 13)
    m.reserve([(24, 16), (25, 16), (24, 18), (25, 18), (27, 18), (28, 17), (14, 17), (13, 18), (15, 18)])

    # ---- cots under canvas (the inn): the wake cot at 8,5-6, keeper at 5,12 by the blanket stack (inn at 5,11)
    m.place(L.AWNING, 3, 2)
    m.place(L.AWNING, 7, 2)
    for x in (4, 6):
        m.place(L.COTS[x % 3], x, 3)
    m.place(L.COTS[1], 9, 3)
    m.place(L.COTS[2], 10, 3)
    m.place(L.COTS[0], 8, 5, solid=0)
    m.place(L.PILLOWS[1], 3, 5)
    m.place(L.STOOL, 7, 4)
    m.place(L.LANTERN, 5, 4)
    m.place(L.BUCKET_W, 11, 4)
    for x in (3, 7, 9):
        m.place(L.COTS[(x + 1) % 3], x, 8)
    m.place(L.SLEEP_ROLL, 3, 10, solid=0)
    m.place(L.BLANKETS, 5, 11)
    m.place(L.CAMP_CHESTS[0], 4, 11)
    m.place(L.PILLOWS[2], 6, 11)
    m.place(L.STOVE2, 3, 12)
    m.place(L.CAMP_STOOLS[0], 6, 13)
    m.place(L.PLANK_STACK[0], 11, 8)                    # the plank pile (worker at 12,10) ...
    m.place(L.CRATES_B8[1], 13, 8)                      # ... and the lamp-fuel crates beside it
    m.place(L.CRATES_B8[3], 14, 8)
    m.place(L.D5_PLANKS, 9, 11)
    m.place(L.PALLETS[0], 11, 12)
    # ---- infirmary awning (medic at 27,6)
    m.place(L.AWNING, 24, 2)
    m.place(L.COTS[0], 24, 4)
    m.place(L.COTS[2], 25, 4)
    m.place(L.COTS[1], 28, 4)
    m.place(L.TUB, 26, 5)
    m.place(L.PAILS[0], 23, 5)
    m.place(L.LAMP_TABLE, 21, 3)
    m.place(L.CRATES_B7[0], 23, 3)
    m.place(L.SHELTERS[0], 12, 3)
    m.place(L.D_CRATES[0], 14, 3)
    # ---- the hearth drum on the rock (Name-Keeper at 18,10, lamp keeper at 22,9)
    m.place(L.DFIRE[0], 16, 11)
    m.anim("campfire", 16, 11, dx=24, dy=12, h=40)
    lamp(m, 15, 10)
    for (px, py) in ((15, 12), (18, 12), (16, 13), (17, 10)):
        m.place(L.PEBBLES[(px + py) % len(L.PEBBLES)], px, py)
    lamp(m, 13, 15)
    m.place(L.LOGS[1], 13, 11)
    m.place(L.LOGS[2], 19, 12)
    m.place(L.STOOLS_V[1], 14, 14)
    # (17,14) stays clear: the CH23 epilogue walk stops there
    # the long table west of the hearth
    m.place(L.LONG_TABLE, 6, 14)
    m.place(L.STOOLS_V[0], 7, 13)
    m.place(L.STOOLS_V[2], 9, 13)
    m.place(L.CAMP_BARRELS[1], 10, 15)
    m.place(L.BUCKETS[0], 11, 14)
    # the lamp stores east of it (lamp keeper at 22,9)
    m.place(L.V_BARREL_PILE, 25, 8)
    m.place(L.LANTERN_B8[1], 24, 9)
    m.place(L.CRATES_B7[2], 24, 10)
    m.place(L.D_CRATES[3], 26, 10)
    m.place(L.LANTERN3, 25, 11)
    m.place(L.FIREWOOD[2], 21, 11)
    m.place(L.LANTERN_B8[0], 23, 9)
    m.place(L.BARRELS_B8[0], 23, 7)
    m.place(L.LAMP_HANG[1], 21, 8)
    lamp(m, 13, 9)
    lamp(m, 20, 8)
    # ---- the cook fire (cook at 20,16) and the hearth chest (24-25,17)
    m.place(L.TRIPOD_POT, 19, 14)
    m.place(L.FOOD_BARRELS[0], 21, 14)
    m.place(L.CAULDRONS[0], 22, 15)
    m.place(L.CAMP_CRATES[1], 23, 14)
    m.place(L.FISH_CRATE, 26, 17)
    m.place(L.SACKS, 23, 17)
    m.place(L.CAMP_BARRELS[0], 26, 18)
    # salvage chest (switch at 28,18) among the salvage piles
    m.place(L.SALVAGE[2], 26, 20)
    m.place(L.D5_SCRAP[1], 24, 20)
    m.place(L.ANCHOR_S, 28, 20)
    m.place(L.RAGFLAG[0], 27, 21)
    # ---- south rafts: fishing, water, shacks
    m.place(L.SHACKS[1], 3, 17)
    m.place(L.FISH_RACK, 5, 17)
    m.place(L.WATER_TUB, 7, 17)
    m.place(L.CISTERN2, 9, 17)
    m.place(L.LAUNDRY3, 11, 16)
    m.place(L.BARRELS[2], 16, 19)
    m.place(L.CRATES[2], 17, 19)
    m.place(L.V_BOAT, 18, 21)
    m.place(L.NET_RACK, 3, 20)
    m.place(L.SHACKS[2], 6, 20)
    m.place(L.V_TENT[2], 9, 20)
    m.place(L.ROPE_BIG[0], 12, 21)
    m.place(L.CAMP_LANTERN, 15, 17)
    m.place(L.SHACKS[5], 21, 20)
    m.place(L.LIFE_RING[0], 23, 22)
    m.anim("chimney_smoke", 3, 15, dx=20, h=96)
    m.anim("chimney_smoke", 21, 18, dx=12, h=96)
    lamp(m, 12, 18)
    # east edge by the walkway and the far raft
    m.place(L.PLANK_PATCH, 30, 12)
    m.place(L.CAPSTAN, 27, 10)
    m.place(L.V_BARRELS[0], 28, 15)
    m.place(L.ROPE, 27, 14)
    m.place(L.BARRELS[5], 19, 18)
    m.place(L.PAILS[1], 20, 18)
    m.place(L.CRATES_B7[1], 16, 17)
    m.place(L.FIREWOOD[3], 13, 20)
    m.place(L.CAMP_BARRELS[0], 3, 15)
    m.place(L.SACKS, 4, 15)
    m.place(L.CRATES[1], 3, 16)
    m.place(L.CRATES[2], 22, 18)
    m.place(L.BARRELS[4], 21, 17)
    m.place(L.PILLOWS[3], 27, 4)
    m.place(L.BUCKETS[3], 23, 19)
    m.place(L.CRATES_B7[3], 12, 3)
    m.place(L.BARRELS[1], 22, 5)
    m.place(L.ROPE_BIG[1], 8, 10)
    m.place(L.CAMP_CHESTS[1], 10, 10)
    m.place(L.SPOOLS[1], 27, 15)
    m.place(L.LIFE_RING[1], 3, 22)
    m.place(L.V_CRATES[4], 14, 22)
    m.place(L.CRATES[0], 21, 5)
    m.place(L.BUCKETS[1], 11, 13)
    m.place(L.SACKS, 26, 14)
    m.place(L.BARRELS[3], 9, 22)
    m.place(L.CRATES_B7[2], 26, 22)
    m.place(L.SACKS, 15, 21)
    m.place(L.D_CRATES[1], 16, 20)
    m.place(L.BARRELS_B7[1], 12, 5)
    m.place(L.V_TENT[4], 33, 10)
    m.place(L.CRATES[0], 32, 10)
    m.place(L.SACKS, 35, 11)
    m.place(L.CAMP_FIRE, 33, 14)
    m.place(L.BUCKETS[2], 35, 13)
    m.place(L.LIFE_RING[1], 32, 15)
    # north gangway lamps
    m.place(L.CRATES[1], 14, 3)
    rocks(m, (0, 0, 2, 7), 3)
    rocks(m, (0, 15, 2, 25), 4)
    rocks(m, (30, 0, 35, 7), 4)
    rocks(m, (29, 19, 35, 25), 4)
    edge_pilings(m, every=4, off=1)
    pilings(m, [(29, 11), (31, 11), (29, 14), (31, 14)])
    sea_dress(m, L.REEF_BIG + L.REEF_S + L.DRIFT, (0, 23, 35, 25), 11)
    sea_dress(m, L.REEF_S + L.BUOYS + L.DRIFT, (29, 0, 35, 9), 4)
    sea_dress(m, L.REEF_S + L.BUOYS + L.DRIFT, (29, 15, 35, 22), 4)
    sea_dress(m, L.REEF_BIG + L.REEF_S + L.DRIFT, (0, 0, 14, 2), 4)
    sea_dress(m, L.REEF_S + L.DRIFT, (21, 0, 35, 2), 3)
    sea_dress(m, L.REEF_S + L.BUOYS, (0, 4, 2, 22), 6)
    sea_dress(m, L.REEF_BIG, (21, 0, 35, 2), 2)
    deck_decals(m, 40)
    skip = m.dock_edges(set())
    m.sea_anims(skip)
    return m


# ================================================================================================ T07_BERTH
def berth():
    m = Hmap("T07_BERTH", 40, 26, "Hearthward - Airship Berth", "harbor", music="M016", zone="T07",
             location="L_T07", region="R06", phase="post", seed=7073)
    m.use(**L.MATS)
    add_ents(m, BERTH_ENTS)
    m.fill("sea")
    # black rock shores north and south: the berth is a basin in the reef
    for x in range(0, 41, 3):
        m.blob("rock", x + m.rng.uniform(-0.5, 0.5), 0.3, 2.4, 1.6 + m.rng.uniform(0.0, 1.4), rough=0.3)
        m.blob("rock", x + m.rng.uniform(-0.5, 0.5), 25.6, 2.4, 1.0 + m.rng.uniform(0.0, 1.0), rough=0.3)
    m.blob("rock", 3.0, 0.8, 6.0, 2.4, rough=0.3)
    m.blob("rock", 36.5, 1.5, 4.0, 3.0, rough=0.3)
    m.blob("rock", 3.0, 24.0, 5.5, 2.4, rough=0.3)
    m.blob("rock", 37.5, 23.5, 3.0, 3.0, rough=0.3)
    m.blob("rock", 6.0, 23.2, 7.0, 1.6, rough=0.3)
    m.blob("rock", 34.5, 23.4, 5.5, 1.5, rough=0.3)
    for x in range(0, 41, 4):
        m.blob("rock", x + 1.0, 1.4, 1.8, 1.4, rough=0.3)
    for (lx, ly) in ((12, 0.4), (21, 0.2), (28, 0.5), (16, 25.4), (25, 25.3), (31, 25.6)):
        m.blob("lava", lx, ly, 1.3, 0.8, rough=0.2)
    m.blob("lava", 36.8, 1.2, 1.4, 1.2, rough=0.2)
    m.blob("lava", 2.5, 24.6, 1.6, 0.8, rough=0.2)
    m.blob("lava", 37.5, 24.0, 1.2, 1.2, rough=0.2)
    # the yard pontoon and the long pier to the mooring mast
    m.rect("planks", 0, 5, 14, 20)
    m.rect("planks_old", 0, 5, 6, 10)
    m.rect("deck", 7, 15, 14, 20)
    m.rect("planks_grey", 15, 10, 37, 14)
    m.rect("planks", 15, 11, 37, 13)
    m.rect("planks_grey", 16, 8, 18, 9)                 # lamp platforms off the pier
    m.rect("planks_grey", 18, 15, 20, 16)
    m.rect("planks_old", 33, 8, 36, 9)
    m.rect("planks_grey", 17, 17, 18, 21)               # finger pier south (skiffs)
    m.rect("planks_grey", 27, 6, 28, 9)                 # finger pier north (the longship)
    # routes
    m.reserve_rect(0, 5, 3, 8)
    m.reserve_rect(0, 11, 37, 12)
    m.reserve_rect(3, 6, 4, 8)
    m.reserve_rect(2, 9, 3, 13)
    m.reserve_rect(9, 14, 11, 16)
    m.reserve([(17, 10), (19, 14), (33, 12), (34, 11), (32, 11)])

    # ---- the yard: timber, plans for the rescue ship, winches
    m.place(L.TOOL_SHED, 1, 13)
    m.place(L.SUPPLY_SHED, 7, 5)
    m.place(L.FRAME_RIBS, 7, 16, solid=1)
    m.place(L.PLANK_STACK[0], 11, 16)
    m.place(L.PLANK_STACK[1], 11, 18)
    m.place(L.LOGS[0], 12, 5)
    m.place(L.LOGS[1], 12, 6)
    m.place(L.FIREWOOD[3], 4, 17)
    m.place(L.MAP_TABLE, 9, 12)                         # the Golem's plans (berth master at 10,14)
    m.place(L.PLAN_RACK, 12, 8)
    m.place(L.MAP_BOARD, 6, 8)
    m.place(L.WINCH, 13, 15)
    m.place(L.CABLE_DRUM, 13, 17)
    m.place(L.SPOOLS[0], 12, 10)
    m.place(L.SPOOLS[1], 13, 10)
    m.place(L.WORKBENCH, 1, 18)
    m.place(L.CHOP[1], 3, 19)
    m.place(L.STUMPS[0], 6, 20)
    m.place(L.V_CRATES3, 0, 9)
    m.place(L.CRATES_B8[2], 6, 5)
    m.place(L.BARRELS[3], 11, 5)
    m.place(L.LANTERN, 7, 10)
    m.place(L.CAMP_STOOLS[1], 8, 14)
    m.place(L.LAMP_HANG[0], 14, 14)
    lamp(m, 14, 10)
    lamp(m, 6, 13)
    # ---- the pier: bollards, coils and lamps along both edges, lamp stands off it (workers at 17,9 and 19,15)
    for x in (20, 26, 31):
        m.place(L.ROPE_BIG[x % 2], x, 10)
        m.place(L.SMALL_CARGO[(x // 3) % 4], x + 1, 14)
    m.place(L.BARRELS[4], 23, 14)
    m.place(L.V_CRATES3, 4, 9)
    m.place(L.BARRELS[1], 6, 10)
    m.place(L.CRATES_B7[1], 16, 14)
    m.place(L.CRATES_B7[2], 17, 14)
    m.place(L.CRATES[0], 27, 10)
    m.place(L.V_BARRELS[1], 28, 10)
    m.place(L.CHESTS[1], 29, 10)
    m.place(L.PALLETS[1], 33, 14)
    m.place(L.BUCKETS[2], 21, 10)
    m.place(L.V_FOODBOX[0], 37, 10)
    m.place(L.SPOOLS[1], 32, 10)
    m.place(L.CRATES_B7[0], 21, 13)
    m.place(L.BARRELS[5], 22, 13)
    m.place(L.CRATE_TALL[1], 26, 12)
    m.place(L.SACKS, 31, 13)
    m.place(L.CRATES[2], 13, 13)
    m.place(L.BARRELS_B7[2], 14, 13)
    m.place(L.BARRELS[0], 0, 16)
    m.place(L.CRATES[1], 0, 17)
    m.place(L.D5_SACKPILE[3], 5, 19)
    m.place(L.CAMP_CRATES[3], 6, 15)
    m.place(L.CRATES[0], 24, 13)
    m.place(L.ROPE, 29, 13)
    m.place(L.BUCKETS[0], 35, 13)
    m.place(L.LIFE_RING[1], 19, 13)
    m.place(L.SACKS, 2, 20)
    m.place(L.PAILS[1], 11, 20)
    m.place(L.CHOP[2], 7, 20)
    m.place(L.BARRELS[2], 13, 19)
    m.place(L.CRATES[2], 14, 20)
    m.place(L.SMALL_CARGO[3], 25, 14)
    m.place(L.CRATES[2], 24, 14)
    m.place(L.LIFE_RING[0], 28, 14)
    m.place(L.PULLEYS[0], 23, 10)
    lamp(m, 16, 9)
    lamp(m, 18, 8, anim="brazier")
    lamp(m, 20, 16)
    lamp(m, 25, 10)
    lamp(m, 30, 14)
    # ---- the mooring mast at the pier end, with its winch and ropes (the Lanternwake ties up here)
    m.place(L.MAST, 38, 5, solid=1)
    m.place(L.CAPSTAN, 37, 13)
    m.place(L.ANCHOR_CRANE, 34, 8)
    m.place(L.CRATES[0], 33, 8)
    # ---- ships at berth in the red water
    m.place(L.SHIP_TOP, 23, 16, solid=0)
    m.place(L.V_LONGSHIP, 29, 17, solid=0)
    for (bx, by, b) in ((20, 8, L.V_BOAT), (29, 8, L.V_BOAT2), (27, 16, L.V_BOAT2), (33, 16, L.V_BOAT)):
        m.place(b, bx, by, solid=0)
        m._placed_sea.update({(bx + i, by) for i in range(3)})
    m.place(L.V_BOAT2, 19, 20, solid=0)
    m.place(L.ROPE, 17, 21)
    m.place(L.LANTERN, 18, 21)
    m.place(L.BARRELS[0], 17, 18)
    m.place(L.CRATES[1], 27, 6)
    m.place(L.ROPE_BIG[1], 28, 7)
    m.place(L.LANTERN2, 28, 6)
    m.place(L.HULL_STERN, 30, 3, solid=0)
    m.place(L.V_LONGSHIP2, 23, 4, solid=0)
    m.place(L.V_BOAT2, 16, 5, solid=0)
    rocks(m, (0, 0, 39, 3), 30)
    rocks(m, (0, 21, 39, 25), 30)
    edge_pilings(m, every=3, off=0)
    pilings(m, [(x, 9) for x in range(19, 33, 3)] + [(x, 15) for x in range(22, 37, 3)] + [(38, 10), (38, 14)])
    sea_dress(m, L.REEF_BIG + L.REEF_S + L.DRIFT + L.BUOYS, (14, 0, 31, 4), 5)
    sea_dress(m, L.REEF_BIG + L.REEF_S + L.DRIFT + L.BUOYS, (14, 17, 21, 25), 5)
    sea_dress(m, L.REEF_BIG + L.REEF_S + L.DRIFT + L.BUOYS, (27, 15, 39, 25), 8)
    sea_dress(m, L.REEF_S + L.BUOYS + L.DRIFT, (19, 4, 39, 8), 8)
    sea_dress(m, L.REEF_BIG + L.REEF_S, (27, 15, 39, 22), 5)
    sea_dress(m, L.REEF_S + L.DRIFT, (15, 15, 22, 22), 4)
    sea_dress(m, L.REEF_BIG + L.REEF_S + L.DRIFT, (0, 21, 14, 25), 7)
    sea_dress(m, L.REEF_BIG + L.REEF_S, (15, 5, 21, 7), 2)
    sea_dress(m, L.REEF_BIG + L.REEF_S + L.DRIFT, (0, 20, 39, 24), 6, margin=0)
    sea_dress(m, L.REEF_S + L.BUOYS, (14, 2, 39, 8), 5, margin=0)
    sea_dress(m, L.REEF_S + L.BUOYS, (0, 0, 9, 4), 3)
    deck_decals(m, 40)
    skip = m.dock_edges(set())
    m.sea_anims(skip)
    return m


if __name__ == "__main__":
    only = sys.argv[1:]
    maps = [market, hearth, berth]
    print(write_group("hearth", [f().save() for f in maps]))
