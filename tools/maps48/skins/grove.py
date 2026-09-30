"""Rootward (D03_R01..R06, Crown March): an old forest of huge roots, wagon hollows, sluices and a canopy rise.
Walls are the forest mass itself (leaf canopy on top, giant trunks as the face); trees overhang in layers."""
from autoskin import Skin, WallStyle
from skins.common import VOID, BARREL, BARREL2, CRATE, CRATE2
from skins.lib_nature import *
from kit import st

TENTS = [st("camp", "2", 0, 4, 2, 2), st("camp", "2", 2, 4, 2, 2)]
CARTS = [st("town", "2", 14, 4, 2, 2), st("town", "2", 4, 10, 2, 2)]
SIGN = [st("forest", "10", 14, 6, 1, 2), st("forest", "10", 8, 8, 2, 2)]
SLUICE = [st("forest", "8", 12, 2, 2, 2)]
BRAZIER = [st("castle", "8", 0, 0)]
MURAL = [st("forest", "3", 14, 12, 2, 2, hgrid=2), st("forest", "3", 6, 12, 2, 2, hgrid=2), st("dungeon", "3", 0, 14, 1, 2, hgrid=2)]

SKIN = Skin(
    mats=dict(void=VOID, moss=FOREST_MOSS, grass=FOREST_GRASS, dirt=FOREST_DIRT, roots=FOREST_ROOTS,
              canopy=CANOPY, vinerock=VINE_ROCK, water=WATER, shallow=SHALLOW),
    ground={"floor2": "moss", "grass": "grass", "path": "dirt", "floor": "dirt", "roots": "roots",
            "water": "water", "shallow": "shallow"},
    default="moss",
    walls={"wall": WallStyle(face=("jungle", "10", 480, 0, 288, 96), cap="canopy", face_h=2),
           "cliff": WallStyle(face=("jungle", "1", 0, 288, 192, 96), cap="vinerock", face_h=2)},
    props={"hedge": BUSHES_1, "mural": MURAL, "vine": VINES, "tent": TENTS, "cart": CARTS, "sluice": SLUICE,
           "barrel": [BARREL, BARREL2], "crate": [CRATE, CRATE2], "sign": SIGN, "brazier": BRAZIER,
           "water": spread([REEDS3, FLOAT_LOG, REEDS3, REEDS3]) + [EMPTY1] * 6 + PADS + REEDS},
    trees=OAKS + [DARK_PINE],
    decals=TUFTS + TUFTS + FERNS + MUSHROOMS + TWIGS, decal_density=0.1,
    water_anim={"water": "water_deep", "shallow": "water_shallow"},
)
SKIN.dress_wall = STUMPS + MOSS_ROCKS + BUSHES_1 + [ROOT_KNOT]
SKIN.dress_open = SMALL_ROCKS + STUMPS + LOGS[:2] + BUSHES_1
SKIN.dress_target = 0.05
SKIN.dress_kind = "rock"
