"""Skychain Viaduct (Skyspine): stone landings and timber spans hung on chains over open sky - deep blue void with
distant clouds below, pale weathered flagstone ledges with ragged edges, plank bridges, mooring chains and cable
winches, timber huts with slate roofs, crates, barrels and camp tents."""
from autoskin import Skin, WallStyle
from kit import st, Mat
from skins.common import RUBBLE, RUBBLE2, GRASS_TUFTS
from skins.lib_cold import SKY, FLAGS, DRIFTS

LEDGE = FLAGS     # pale weathered flags
CAPSTONE = Mat([("town", "6", 192, 384, 96, 96)], "wall")                           # slate tower top
GRAVEL = Mat([("castle", "3", 480, 0, 192, 96)], "path", organic=True, prio=3)
PLANKS = Mat([("siege", "1", 192, 192, 192, 96)], "bridge")                         # timber deck
ROOF = Mat([("siege", "5", 576, 96, 96, 96)], "roof")                              # clay tile roof
FACE = ("castle", "1", 0, 0, 192, 96)
TIMBER = ("siege", "5", 384, 96, 192, 48)                                          # plank wall

CHAIN_POSTS = [st("dungeon", "6", 12, 8, 1, 2), st("dungeon", "6", 13, 8, 1, 2)]
COILS = [st("viking", "6 (1)", 10, 8, 2, 2), st("viking", "2 (1)", 13, 6, 1, 1)]
WINCH = st("siege", "1", 12, 6, 2, 2)
TENTS = [st("viking", "2 (1)", 14, 4, 2, 2), st("viking", "2 (1)", 14, 6, 2, 2)]
BARRELS = [st("castle", "9", c, 2, 1, 2) for c in (5, 6, 7)]
CRATES = [st("castle", "9", c, 2, 1, 2) for c in (9, 10)]
CRATE_STACK = st("viking", "2 (1)", 11, 6, 2, 2)
DOOR = st("castle", "5", 4, 0, 1, 2)
WINDOW = st("dungeon", "7", 14, 6, 1, 1)
PEBBLES = [st("dungeon", "3", c, r, flat=True) for (c, r) in ((4, 0), (5, 0), (4, 1), (5, 1))]
ANCHOR = st("viking", "2 (1)", 13, 9, 1, 1)

SKIN = Skin(
    mats=dict(void=SKY, ledge=LEDGE, gravel=GRAVEL, planks=PLANKS, roof=ROOF, cap=CAPSTONE),
    ground={"floor": "ledge", "path": "gravel", "bridge": "planks", "door": "ledge", "doorway": "ledge",
            "stairs": "planks", "floor2": "ledge", "dock": "planks", "snow": "ledge"},
    default="ledge",
    walls={"wall": WallStyle(face=FACE, cap="cap", face_h=2),
           "roof": WallStyle(face=TIMBER, cap="roof", face_h=1),
           "house": WallStyle(face=TIMBER, cap="roof", face_h=1),
           "window": WallStyle(face=TIMBER, cap="roof", face_h=1)},
    props={"chain": CHAIN_POSTS, "cable": COILS, "machine": [WINCH], "tent": TENTS, "barrel": BARRELS,
           "crate": CRATES, "rubble": [RUBBLE, RUBBLE2], "door": [DOOR], "window": [WINDOW]},
    decals=PEBBLES + GRASS_TUFTS[:2] + DRIFTS[:4] + DRIFTS[8:10], decal_density=0.04,
)
SKIN.dress_wall = BARRELS + CRATES + [CRATE_STACK]
SKIN.dress_open = BARRELS + CRATES + COILS[1:] + [ANCHOR]
SKIN.dress_target = 0.04
SKIN.dress_kind = "crate"
