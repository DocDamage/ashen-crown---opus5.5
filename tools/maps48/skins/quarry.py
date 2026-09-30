"""Crown Quarry: a working stone quarry / mine of the crown (Crown March: warm stone, timber, slate)."""
from autoskin import Skin, WallStyle
from skins.lib_quarry import *
from kit import Mat

SKIN = Skin(
    mats=dict(void=VOID_M, rockcap=Mat([("dungeon", "1", 576, 0, 192, 96)], "wall"), cave=CAVE_FLOOR, slabs=CUT_SLABS, track=TRACK, gravel=GRAVEL,
              grass=GRASS_C, water=WATER_M, shallow=SHALLOW_M, planks=PLANKS_M, slate=SLATE_ROOF),
    ground={"floor2": "cave", "floor": "slabs", "path": "gravel", "grass": "grass", "water": "water",
            "shallow": "shallow", "lift": "planks", "doorway": "gravel", "door": "gravel", "stairs": "slabs",
            "bridge": "planks"},
    default="cave",
    walls={"wall": WallStyle(face=FACE_CAVE, cap="rockcap", face_h=2),
           "cliff": WallStyle(face=FACE_CAVE, cap="rockcap", face_h=2),
           "roof": WallStyle(face=FACE_HOUSE, cap="slate", face_h=1),
           "house": WallStyle(face=FACE_HOUSE, cap="slate", face_h=1),
           "window": WallStyle(face=FACE_WINDOW, cap="slate", face_h=1)},
    props={"rock": ROCKS_S + BOULDER_2, "rubble": RUBBLE_S + ROCKS_S[:4] + STONES[:3] + RUBBLE_2, "machine": [SPOOL, SPOOL_BIG, WINCH, RUST_MACHINE],
           "crystal": CRYSTALS[:1] + [CRYSTAL_P], "vent": [GRATE_PLATE], "lamp": TORCHES, "crate": CRATES,
           "barrel": BARRELS, "table": [TABLE_2], "bench": [STOOL_W], "pipe": PIPE_V, "sign": [SIGN_DANGER],
           "cart": [CART], "chimney": [CHIMNEY_S], "statue": STATUE_K, "gate": [GATE_WOOD, GATE_WOOD2]},
    decals=PEBBLES, decal_density=0.05,
    wall_decor=["torch_wall", LANTERN_HOOK], decor_every=7,
    water_anim={"water": "water_deep", "shallow": "water_shallow"},
)
SKIN.dress_wall = CRATES[:4] + BARRELS[:3] + SACKS + ORE + STONES[:3] + BUCKETS[:1] + INGOTS[:1]
SKIN.dress_open = ROCKS_S + ORE[:2]
SKIN.dress_target = 0.08
SKIN.dress_kind = "crate"
