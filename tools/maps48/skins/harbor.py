"""Hearthward (T07): the post-catastrophe refugee harbour on the Ember Sea. Weathered pontoon planks over a dark,
ember-red sea; refugee tents, fish racks, nets and drying lines (Survival Island 4), crates and barrels (Pirate Age,
Viking Age), market stalls (Medieval Town), rowboats (Viking Age), camp fires and bedrolls (Army Camp)."""
from autoskin import Skin, WallStyle
from kit import st, Mat
from skins.lib_d import TintMat

MATS = dict(
    planks=TintMat([("pirate", "B1-1", 0, 0, 192, 192)], "dock", mul=(0.9, 0.82, 0.78)),
    planks_dark=Mat([("pirate", "B4", 0, 0, 192, 192)], "floor2"),
    deck=Mat([("pirate", "B4", 0, 0, 192, 192)], "floor"),
    sea=TintMat([("fa", "water_deep", 0, 0, 48, 48)], "water", mul=(0.7, 0.28, 0.24), add=(52, 8, 2), organic=True),
)

TENTS = [st("camp", "2", c, r, 2, 2) for (c, r) in ((0, 4), (2, 4), (4, 4), (8, 4), (10, 6), (12, 4))] + \
        [st("island", "4", 0, 10, 2, 2), st("island", "4", 2, 10, 3, 2)]
TENT1 = [st("camp", "2", 3, 8, 1, 1), st("camp", "2", 5, 8, 1, 1)]          # bedrolls for single cells
CRATES = [st("viking", "1 (1)", c, 13, 1, 1) for c in (10, 11, 12)] + [st("pirate", "B1-1", 7, 12, 1, 1), st("pirate", "B1-1", 8, 12, 1, 1), st("pirate", "B1-1", 7, 13, 1, 1)]
BARRELS = [st("pirate", "B1-1", c, 12, 1, 1) for c in (4, 5, 6)] + [st("pirate", "B1-1", c, 13, 1, 1) for c in (4, 5, 6)]
CHESTS = [st("pirate", "B1-1", 11, 12, 1, 1), st("pirate", "B1-1", 9, 13, 1, 1), st("pirate", "B1-1", 11, 13, 1, 1),
          st("pirate", "B1-1", 12, 12, 1, 1), st("pirate", "B1-1", 13, 12, 1, 1)]
BENCH3 = [st("camp", "5", 0, 3, 3, 1), st("camp", "5", 3, 3, 3, 1)]
BENCH2 = [st("town", "2", 8, 12, 2, 1), st("town", "2", 12, 11, 2, 1)]
STOOLS = [st("camp", "2", 5, 14, 1, 1), st("camp", "2", 6, 15, 1, 1), st("camp", "2", 4, 15, 1, 1)]
LAMPS = [st("pirate", "B1-1", 14, 14, 1, 2), st("pirate", "B7", 14, 8, 1, 2)]
BEDS = [st("camp", "2", 0, 8, 1, 2), st("camp", "2", 2, 8, 1, 2), st("camp", "2", 4, 8, 1, 2)]
BEDROLLS = [st("camp", "2", 3, 8, 1, 1), st("camp", "2", 3, 9, 1, 1), st("camp", "2", 5, 9, 1, 1)]
CARTS = [st("town", "2", 4, 10, 2, 2), st("town", "2", 8, 8, 2, 2), st("town", "2", 14, 4, 2, 2)]
BOATS = [st("viking", "1 (1)", 0, 0, px=(578, 528, 122, 48)), st("viking", "1 (1)", 0, 0, px=(576, 576, 124, 48))]
STALLS = [st("town", "2", c, 4, 2, 2) for c in (0, 2, 4, 6, 8)]
TABLES = [st("camp", "5", 6, 2, 2, 2), st("camp", "2", 4, 10, 2, 2)]
FIRE = [st("camp", "5", 2, 0, 2, 2), st("camp", "5", 0, 0, 2, 2)]
FISH_RACKS = [st("island", "4", 8, 4, 2, 2), st("island", "4", 8, 12, 2, 2), st("island", "4", 14, 12, 2, 3)]
LINES = [st("island", "4", 11, 4, 2, 2), st("island", "4", 10, 12, 2, 2)]
NETS = [st("island", "4", 12, 13, 2, 2)]
FLAT = [st("pirate", "B1-1", c, r, 1, 1, flat=True, solid=0) for (c, r) in ((10, 14), (11, 14), (10, 15), (11, 15), (14, 13), (15, 13))] + \
       [st("camp", "2", c, r, 1, 1, flat=True, solid=0) for (c, r) in ((3, 8), (3, 9), (5, 9))]

SKIN = Skin(
    mats=MATS,
    ground={"dock": "planks", "floor": "deck", "floor2": "planks_dark", "water": "sea", "bridge": "planks",
            "door": "planks", "doorway": "planks", "stairs": "planks", "awning": "planks", "boat": "sea"},
    default="planks",
    props={"tent": TENTS + TENT1, "crate": CRATES, "barrel": BARRELS, "chest_deco": CHESTS,
           "bench": BENCH3 + BENCH2 + STOOLS, "lamp": LAMPS, "bed": BEDS + BEDROLLS, "cart": CARTS, "boat": BOATS,
           "counter": STALLS, "table": TABLES, "brazier": FIRE},
    decals=FLAT, decal_density=0.045,
)
# note: autoskin never dresses dock cells (PASS_EXTRA), so the harbour relies on its grid props and flat decals.
