"""Timber-and-plaster interiors (Crown March homes, shops, canteens, halls)."""
from autoskin import Skin, WallStyle
from skins.common import *

SKIN = Skin(
    mats=dict(wood=WOOD, dark=DARK, void=VOID, planks=PLANKS),
    ground={"floor": "wood", "floor2": "planks", "door": "wood", "doorway": "wood", "stairs": "wood", "carpet": "wood"},
    default="wood",
    walls={"wall": WallStyle(face=("town", "16", 384, 0, 192, 96), cap="dark", face_h=2)},
    props={"shelf": [BOOKSHELF, CUPBOARD, CUPBOARD2, WARDROBE], "table": [TABLE_2x2, TABLE_FOOD, TABLE_1],
           "counter": [COUNTER4, COUNTER2], "bench": [BENCH2, BENCH2B, STOOL], "bed": [BED, BED2, BED3],
           "crate": [CRATE, CRATE2], "barrel": [BARREL, BARREL2], "machine": [HEARTH], "book": [BOOKS],
           "pipe": [BARREL], "gear": [CRATE_IRON], "anvil": [ANVIL], "mural": [TAPESTRY, TAPESTRY2],
           "altar": [ALTAR], "bell": [PEDESTAL], "garden": [POT], "chest_deco": [CHEST]},
    wall_decor=[WALL_CANDLE, PAINTING, BANNER], decor_every=4,
)
SKIN.dress_wall = [BOOKSHELF, CUPBOARD, CUPBOARD2, WARDROBE, SHELF_LOW, BARREL, CRATE, POT, SACK]
SKIN.dress_open = [TABLE_1, SMALL_TABLE, BARREL, CRATE]
SKIN.dress_target = 0.22
SKIN.dress_kind = "shelf"
