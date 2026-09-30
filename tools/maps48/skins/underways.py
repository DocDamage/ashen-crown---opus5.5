"""Veyr Underways: canals, cisterns and record stacks under the capital (damp grey brick, moss, water-stained records)."""
from autoskin import Skin, WallStyle
from skins.lib_quarry import *
from kit import Mat

LADDER = Mat([("town", "6", 672, 576, 48, 48)], "ladder")

SKIN = Skin(
    mats=dict(void=VOID_M, cap=STONE_CAP, tile=CUT_SLABS, mossy=MOSSY_COB, water=WATER_M, planks=PLANKS_M,
              grate=GRATE_M, ladder=LADDER, cob=COBBLE_D),
    ground={"floor": "tile", "floor2": "mossy", "water": "water", "dock": "planks", "grate": "grate",
            "ladder": "ladder", "doorway": "tile", "door": "tile", "stairs": "tile", "bridge": "planks", "path": "cob"},
    default="tile",
    walls={"wall": WallStyle(face=FACE_BRICK_MOSS, cap="cap", face_h=2),
           "cliff": WallStyle(face=FACE_BRICK_MOSS, cap="cap", face_h=2)},
    props={"shelf": BOOKCASE_2G + BOOKCASE_1G + SHELF_LOW_1, "machine": [MECH_PLATE] + RUNE_STUBS, "pillar": PILLAR,
           "gear": [GEAR_BOX], "chest_deco": [CHEST_W], "lamp": LANTERN_G, "table": [TABLE_2], "bench": [STOOL_W],
           "bed": [BED_S], "bell": [BELL], "crate": CRATES, "barrel": BARRELS, "boat": [ROWBOAT]},
    decals=RUBBLE_S + PEBBLES[:2] + SCROLLS[:1], decal_density=0.03,
    wall_decor=["torch_wall", LANTERN_HOOK], decor_every=6,
    water_anim={"water": "water_deep"},
)
SKIN.dress_wall = CRATES[:4] + BARRELS[:3] + SACKS[:2] + POTS + BOOKCASE_1 + CUPBOARD_1 + BUCKETS
SKIN.dress_open = CRATES[:2] + BARRELS[:2] + SCROLLS[:1]
SKIN.dress_target = 0.08
SKIN.dress_kind = "crate"
