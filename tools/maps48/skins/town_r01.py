"""Crown March towns (fallback until the hand redesign): warm cobbles, green verges, slate roofs over timber-and-
plaster facades, market stalls, carts, wells, oak trees (Medieval Fantasy Town + Forest Wilderness)."""
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
        roof=TintMat([("town", "6", 192, 384, 96, 96)], "roof", mul=(0.62, 0.7, 0.86)),
        facade=Mat([("town", "6", 576, 0, 192, 96)], "house"),
        wallcap=TintMat([("town", "6", 0, 672, 192, 96)], "wall", mul=(0.55, 0.52, 0.5)),
    ),
    roof_src=("town", "6", 192, 384, 96, 48),
    house_face=("town", "6", 576, 48, 192, 48),
    wall_face=("town", "1", 192, 288, 48, 96),
    cliff_face=("town", "1", 528, 576, 96, 96),
    cliff_cap="grass",
    windows=[st("town", "1", c, r, 1, 1) for (c, r) in ((4, 4), (5, 4), (6, 4), (4, 5), (5, 5))],
    doors=[st("town", "1", 5, 7, 1, 1)],
    chimneys=[st("town", "1", 0, 0, px=(330, 20, 30, 40))],
    lamps=[T.TORCH_STAND],
    trees=[T.OAK, T.OAK2, T.OAK3] + T.TREES_M[:8],
    decals=T.GRASS_TUFTS, decal_density=0.05,
    rail_base=("town", "2", 192, 48, 48, 48),
)
SKIN = town_skin(R)
