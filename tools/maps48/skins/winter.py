"""Cradle of Winter (Skyspine dungeon): ice caverns and a frozen sleeping house - snowfields, sheet ice, blue-grey
frozen stone floors, frosted grey stone walls with snow on top, blue crystals, braziers keeping the warmth channels
alive, fur bunks and stained glass for the dawn window."""
from autoskin import Skin, WallStyle
from kit import st, Mat
from skins.common import SMALL_TABLE, TABLE_1, CRATE, CRATE2
from skins.lib_cold import SNOW, ICE, SNOW_CAP, FROST_STONE, DRIFTS

STONE = FROST_STONE                                                            # frosted flagstones
FACE = ("castle", "1", 0, 0, 192, 96)                                          # grey crenellated stone

CRYSTALS = [st("castle", "4", 14, 5), st("castle", "4", 15, 5), st("castle", "4", 14, 5)]
CRYSTAL_BIG = st("castle", "4", 14, 0, 2, 2)
ROCKS = [st("dungeon", "3", 4, 2), st("dungeon", "3", 5, 2), st("dungeon", "3", 0, 3), st("dungeon", "3", 4, 3)]
BOULDER = st("dungeon", "3", 0, 0, 3, 3, hgrid=2)
BRAZIER = st("castle", "9", 4, 0, 1, 2)
FIRE_BASKET = st("castle", "9", 2, 0, 2, 2)
BUNKS = [st("viking", "5 (1)", c, 0, 2, 2) for c in (2, 4, 6)]
SHELF = [st("castle", "6", c, 8, 1, 2) for c in (5, 10, 14)]
STATUES = [st("castle", "7", c, 6, 1, 2) for c in (9, 10, 13)]
GLASS1 = [st("castle", "7", c, 0, 1, 3) for c in (5, 6, 7, 14)]
GLASS2 = [st("castle", "7", 8, 0, 2, 3), st("castle", "7", 10, 0, 2, 3)]
FURS = [st("viking", "5 (1)", c, r, 1, 1) for (c, r) in ((8, 11),)] + [st("viking", "5 (1)", 5, 12, 2, 1)]
STOOLS = [st("viking", "5 (1)", 9, 3), st("viking", "5 (1)", 10, 3)]
CHESTS = [st("viking", "5 (1)", 8, 3, 2, 1), st("viking", "5 (1)", 12, 3, 2, 1)]
WARDROBE = st("viking", "5 (1)", 14, 0, 2, 2)
PEBBLES = [st("dungeon", "3", c, r, flat=True) for (c, r) in ((4, 0), (5, 0), (4, 1), (5, 1))]

SKIN = Skin(
    mats=dict(snow=SNOW, ice=ICE, stone=STONE, cap=SNOW_CAP),
    ground={"floor": "stone", "floor2": "stone", "snow": "snow", "ice": "ice", "door": "stone", "doorway": "stone",
            "stairs": "stone", "path": "stone"},
    default="stone",
    walls={"wall": WallStyle(face=FACE, cap="cap", face_h=2)},
    props={"crystal": CRYSTALS + [CRYSTAL_BIG], "rock": ROCKS, "brazier": [BRAZIER], "bed": BUNKS,
           "table": [SMALL_TABLE, TABLE_1], "shelf": SHELF, "statue": STATUES, "crate": [CRATE, CRATE2],
           "window": GLASS2 + GLASS1},
    decals=PEBBLES + DRIFTS + DRIFTS, decal_density=0.08,
    wall_decor=["torch_wall", "banner_wall_blue"], decor_every=7,
)
SKIN.dress_wall = SHELF + CHESTS + STOOLS + [WARDROBE, CRATE, BRAZIER] + CRYSTALS
SKIN.dress_open = CRYSTALS + ROCKS + [FIRE_BASKET]
SKIN.dress_target = 0.06
SKIN.dress_kind = "rock"
