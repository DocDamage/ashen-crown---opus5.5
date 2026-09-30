"""Mirewold (R08): plague-fen towns - black mud lanes, rotting boardwalks, moss-grey thatch, stilted houses over
still water, dead willows and toadstools (Medieval Fantasy Town and Forest Wilderness, stained and darkened)."""
import kit
from kit import st, Mat
from skins.lib_d import TintMat, town_skin
from skins import common as K
import lib_r01 as T

DEADWOOD = kit.tinted("forest", "2", (0.62, 0.66, 0.52))
TREES = [st("forest", DEADWOOD, c, 0, 2, 3, cols=(1, 1)) for c in (0, 2, 4, 10, 12)] + [K.DEAD_TREE]

R = dict(
    mats=dict(
        path=TintMat([("town", "2", 192, 0, 96, 192)], "path", mul=(0.62, 0.6, 0.52), organic=True, prio=2),
        grass=TintMat([("town", "2", 288, 0, 96, 192)], "grass", mul=(0.62, 0.72, 0.52), organic=True, prio=3),
        floor=TintMat([("town", "6", 192, 576, 96, 96)], "floor", mul=(0.7, 0.66, 0.58), prio=2),
        water=K.WATER,
        dock=TintMat([("town", "6", 192, 576, 96, 96)], "dock", mul=(0.7, 0.66, 0.58)),
        stairs=Mat([("town", "1", 384, 384, 96, 96)], "stairs"),
        roof=TintMat([("town", "6", 192, 384, 96, 96)], "roof", mul=(0.5, 0.56, 0.44)),
        facade=TintMat([("town", "6", 576, 0, 192, 96)], "house", mul=(0.72, 0.7, 0.6)),
        wallcap=TintMat([("town", "6", 0, 672, 192, 96)], "wall", mul=(0.42, 0.44, 0.38)),
    ),
    roof_src=("town", "6", 192, 384, 96, 48),
    house_face=("town", "6", 576, 48, 192, 48),
    wall_face=("town", "1", 192, 288, 48, 96),
    cliff_face=("town", "1", 528, 576, 96, 96),
    cliff_cap="grass",
    windows=[st("town", "1", c, r, 1, 1) for (c, r) in ((4, 4), (5, 4), (6, 4))],
    doors=[st("town", "1", 5, 7, 1, 1)],
    chimneys=[st("town", "1", 0, 0, px=(330, 20, 30, 40))],
    lamps=[K.LANTERN, T.TORCH_STAND],
    trees=TREES,
    decals=[K.MUSHROOM, K.MUSHROOM2] + T.GRASS_TUFTS[:3], decal_density=0.07,
)
SKIN = town_skin(R)
