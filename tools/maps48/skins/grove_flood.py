"""Flooded Rootward (D03P_R01..R03): the Rootward after the catastrophe - dark water over the forest floor, only the
great roots stand above it; survivors camp on a trampled rise; a stone sluice holds the Warden's Current."""
from autoskin import Skin, WallStyle
from skins.common import VOID, RUBBLE, RUBBLE2
from skins.lib_nature import *
from kit import st, Mat

MUD = Mat([("town", "2", 192, 0, 96, 192)], "floor", organic=True, prio=2)
TENTS = [st("camp", "2", 0, 4, 2, 2), st("camp", "2", 2, 4, 2, 2), st("camp", "2", 4, 4, 2, 2)]
SLUICE = [st("castle", "1", 0, 8, 4, 2, hgrid=2), st("castle", "1", 6, 8, 2, 2, hgrid=2), st("castle", "1", 8, 8, 2, 2, hgrid=2)]
BRAZIER = [st("castle", "8", 0, 0)]

SKIN = Skin(
    mats=dict(void=VOID, roots=FOREST_ROOTS, mud=MUD, moss=FOREST_MOSS, water=WATER, shallow=SHALLOW),
    ground={"roots": "roots", "floor": "mud", "floor2": "moss", "water": "water", "shallow": "shallow"},
    default="roots",
    props={"sluice": SLUICE, "vine": VINES, "tent": TENTS, "rubble": [RUBBLE, RUBBLE2] + ROCKS_1,
           "brazier": BRAZIER,
           "water": spread([OAKS[0], OAKS[1], FLOAT_LOG, OAKS[2], REEDS3, OAKS[3], OAKS[6], REEDS3])
                    + [EMPTY1] * 5 + PADS + REEDS},
    decals=TUFTS + MUSHROOMS + TWIGS + FERNS[:3], decal_density=0.06,
    water_anim={"water": "water_deep", "shallow": "water_shallow"},
)
SKIN.dress_wall = DEAD_TRUNKS
SKIN.dress_open = DEAD_TRUNKS + STUMPS[:3] + SMALL_ROCKS + BUSHES_1[:4]
SKIN.dress_target = 0.18
SKIN.dress_kind = "tree"
