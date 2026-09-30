"""Stone halls: records halls and registry (T02), the tide chapel (T04) and the quiet cloister (T06)."""
from autoskin import Skin, WallStyle
from skins.lib_quarry import *
from skins.common import DARK, WOOD, BENCH2, BENCH2B, COUNTER4, COUNTER2, BED, BED2, BANNER, WALL_CANDLE
from kit import Mat, st

STAIR_M = Mat([("town", "6", 288, 672, 96, 96)], "stairs")
BANNERS = [st("town", "7", c, 10, 1, 2) for c in (1, 3, 4)]
PLANTS = [st("dungeon", "2", 14, 0), st("dungeon", "2", 15, 0)]

SKIN = Skin(
    mats=dict(void=VOID_M, dark=DARK, slabs=CUT_SLABS, wood=WOOD, stairs=STAIR_M),
    ground={"floor": "slabs", "floor2": "wood", "stairs": "stairs", "doorway": "slabs", "door": "slabs",
            "carpet": "wood"},
    default="slabs",
    walls={"wall": WallStyle(face=FACE_FIELDSTONE, cap="dark", face_h=2)},
    props={"shelf": BOOKCASE_2G + BOOKCASE_1G + BOOKCASE_1, "bench": [BENCH2, BENCH2B], "bell": CANDLE_STAND,
           "altar": [st("dungeon", "3", 4, 14, 1, 2)], "bed": [BED, BED2], "garden": PLANTS,
           "table": [st("castle", "6", 0, 0, 4, 2), st("castle", "6", 5, 2, 3, 2), st("castle", "6", 8, 6, 2, 2), TABLE_2], "crate": CRATES[:2], "barrel": BARRELS[:2]},
    decals=SCROLLS[:2], decal_density=0.01,
    wall_decor=[WALL_CANDLE] + BANNERS, decor_every=4,
)
SKIN.dress_wall = CUPBOARD_1 + BOOKCASE_1 + POTS[:2] + [SCROLL_JAR] + PLANTS + CANDLE_STAND[:1]
SKIN.dress_open = []
SKIN.dress_target = 0.18
SKIN.dress_kind = "shelf"
