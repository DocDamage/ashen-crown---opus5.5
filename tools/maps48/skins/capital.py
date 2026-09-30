"""Veyr, the Crown March capital (fallback until the hand redesign): pale flagstone squares and warm cobbles, dark
slate roofs over stone-and-timber facades, grand stairs, statues, columns, banners, market stalls, lamps
(Medieval Fantasy Town + Medieval Castle + Roman columns)."""
from kit import st, Mat
from skins.lib_d import TintMat, town_skin
from skins import common as K
import lib_r01 as T

R = dict(
    mats=dict(
        path=Mat([("town", "2", 96, 0, 96, 192)], "path", prio=2),
        grass=Mat([("town", "2", 288, 0, 96, 192)], "grass", organic=True, prio=3),
        floor=Mat([("town", "1", 0, 384, 384, 96)], "floor", prio=2),
        water=K.WATER,
        dock=Mat([("town", "6", 192, 576, 96, 96)], "dock"),
        stairs=Mat([("town", "1", 384, 384, 96, 96)], "stairs"),
        roof=TintMat([("town", "6", 192, 384, 96, 96)], "roof", mul=(0.5, 0.55, 0.72)),
        facade=Mat([("town", "6", 576, 96, 192, 96)], "house"),
        wallcap=TintMat([("town", "6", 0, 672, 192, 96)], "wall", mul=(0.55, 0.52, 0.5)),
    ),
    roof_src=("town", "6", 192, 384, 96, 48),
    house_face=("town", "6", 576, 144, 192, 48),
    wall_face=("town", "12", 0, 144, 192, 96),
    windows=[st("town", "1", c, r, 1, 1) for (c, r) in ((4, 4), (5, 4), (6, 4), (4, 5), (5, 5))],
    doors=[st("town", "1", 5, 7, 1, 1)],
    chimneys=[st("town", "1", 0, 0, px=(330, 20, 30, 40))],
    lamps=[T.TORCH_STAND],
    statues=T.STATUES,
    pillars=[st("roman", "4", 7, 6, 1, 3)],
    tents=[st("camp", "2", c, 4, 2, 2) for c in (0, 2, 4)] + [st("camp", "2", 3, 8, 1, 1)],
    trees=[T.OAK, T.OAK2, T.CYPRESS],
    wall_decor=[st("town", "7", c, 10, 1, 2, solid=0) for c in (0, 2, 4)], decor_every=6,
    decals=[], decal_density=0.0,
)
SKIN = town_skin(R)
