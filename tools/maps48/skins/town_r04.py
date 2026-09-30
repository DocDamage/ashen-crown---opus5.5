"""Skyspine towns (fallback until the hand redesign): cold blue-grey flagstones on cliff tops above an open sky,
dark timber roofs over stone-and-timber facades, rune stones, braziers, pines, racks and furs (Viking Age +
Medieval Fantasy Town + Dreamy World clouds for the drop)."""
from kit import st, Mat
from skins.lib_d import TintMat, town_skin
from skins import common as K
import lib_r01 as T

V1, V3, V6 = "1 (1)", "3 (1)", "6 (1)"
R = dict(
    mats=dict(
        path=TintMat([("town", "2", 0, 0, 96, 192)], "path", mul=(0.82, 0.9, 1.05), prio=2),
        grass=TintMat([("town", "2", 288, 0, 96, 192)], "grass", mul=(0.6, 0.78, 0.8), organic=True, prio=3),
        floor=TintMat([("town", "1", 0, 384, 384, 96)], "floor", mul=(0.85, 0.92, 1.05), prio=2),
        water=K.WATER,
        dock=TintMat([("town", "6", 192, 576, 96, 96)], "dock", mul=(0.7, 0.72, 0.8)),
        stairs=TintMat([("town", "1", 384, 384, 96, 96)], "stairs", mul=(0.85, 0.92, 1.05)),
        roof=TintMat([("pirate", "B4", 0, 0, 192, 192)], "roof", mul=(0.72, 0.72, 0.8)),
        facade=TintMat([("town", "6", 576, 96, 192, 96)], "house", mul=(0.8, 0.86, 0.98)),
        wallcap=TintMat([("town", "6", 0, 672, 192, 96)], "wall", mul=(0.6, 0.66, 0.78)),
        void=TintMat([("dreamy", "1", 384, 576, 384, 96)], "void", mul=(0.72, 0.84, 1.0)),
    ),
    roof_src=("pirate", "B4", 0, 0, 192, 48),
    house_face=("town", "6", 576, 144, 192, 48),
    wall_face=("town", "1", 192, 288, 48, 96),
    windows=[st("town", "1", c, r, 1, 1) for (c, r) in ((6, 4), (7, 4), (6, 5), (7, 5))],
    doors=[st("town", "1", 5, 7, 1, 1)],
    chimneys=[st("town", "1", 0, 0, px=(330, 20, 30, 40))],
    lamps=[T.TORCH_STAND],
    statues=[st("castle", "4", c, 8, 1, 2) for c in (4, 5, 6)] + [st("viking", V3, 14, 0, 1, 3)],
    cables=[st("viking", V1, 8, 10, 1, 1)],
    wheels=[st("viking", V3, 13, 11, 2, 2)],
    trees=T.TREES_M[3:4] + [T.PINE, T.PINE_TALL],
    decals=[], decal_density=0.0,
)
SKIN = town_skin(R)
