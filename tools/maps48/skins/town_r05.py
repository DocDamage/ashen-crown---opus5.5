"""Pale Basin towns (fallback until the hand redesign): ochre sandstone paving, white salt flats and shallow brine
pools, terracotta roofs over sandstone facades, columns, statues, fountains, marble benches, salt crystals
(Roman Empire + Medieval Fantasy Town)."""
from kit import st, Mat
from skins.lib_d import TintMat, town_skin
from skins import common as K
import lib_r01 as T

R1 = "1"
R = dict(
    mats=dict(
        path=Mat([("roman", R1, 480, 192, 96, 192)], "path", organic=True, prio=2),
        grass=TintMat([("roman", R1, 0, 384, 96, 96)], "grass", mul=(0.9, 0.9, 0.7), organic=True, prio=3),
        floor=Mat([("roman", R1, 288, 192, 96, 96)], "floor"),
        salt=TintMat([("town", "6", 96, 480, 96, 96)], "salt", mul=(1.02, 0.99, 0.92), organic=True, prio=1),
        water=K.WATER, pool=K.SHALLOW,
        dock=TintMat([("town", "6", 192, 576, 96, 96)], "dock", mul=(1.05, 0.95, 0.8)),
        stairs=Mat([("roman", R1, 480, 0, 96, 192)], "stairs"),
        roof=Mat([("roman", R1, 384, 480, 96, 96)], "roof"),
        facade=Mat([("roman", R1, 0, 0, 96, 96)], "house"),
        wallcap=TintMat([("roman", R1, 0, 0, 96, 96)], "wall", mul=(0.62, 0.58, 0.52)),
    ),
    roof_src=("roman", R1, 384, 480, 96, 48),
    house_face=("roman", R1, 0, 48, 96, 48),
    wall_face=("roman", R1, 96, 0, 96, 96),
    windows=[st("town", "1", c, r, 1, 1) for (c, r) in ((6, 4), (7, 4), (6, 5), (7, 5))],
    doors=[st("town", "1", 5, 7, 1, 1)],
    chimneys=[st("town", "1", 0, 0, px=(330, 20, 30, 40))],
    lamps=[T.TORCH_STAND],
    statues=[st("roman", "4", 4, 0, 1, 3), st("roman", "4", 5, 0, 1, 3), st("roman", "4", 6, 0, 1, 3)],
    benches=[st("roman", "4", 0, 4, 2, 1), st("roman", "4", 2, 4, 2, 1), st("roman", "8", 2, 4, 2, 1)],
    pillars=[st("roman", "4", 7, 6, 1, 3)],
    wells=[st("roman", "4", 0, 0, 2, 2), st("roman", "4", 2, 0, 2, 2)],
    crystals=[st("castle", "4", c, 5, 1, 1) for c in (12, 13)] + [st("roman", R1, 12, 10, 1, 1), st("roman", R1, 13, 10, 1, 1)],
    trees=[st("island", "2", 0, 0, 2, 3, cols=(1, 1)), st("island", "2", 2, 0, 2, 3, cols=(1, 1))],
    water_anim={"water": "water_deep", "pool": "water_shallow"},
    decals=[], decal_density=0.0,
)
SKIN = town_skin(R)
