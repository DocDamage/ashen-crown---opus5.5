"""Vermilion Reach (R07): the Fox Court's towns - warm stone lanes, vermilion-lacquered roofs, red-maple groves,
lantern posts along the river, shrine arches (Medieval Fantasy Town recoloured + Roman columns as gate posts)."""
import kit
from kit import st, Mat
from skins.lib_d import TintMat, town_skin
from skins import common as K
import lib_r01 as T

MAPLE = kit.tinted("forest", "2", (1.5, 0.62, 0.42))           # green canopies turned to red maple
MAPLE_Y = kit.tinted("forest", "2", (1.45, 1.05, 0.38))        # and gold ginkgo
TREES = [st("forest", s, c, 0, 2, 3, cols=(1, 1)) for s in (MAPLE, MAPLE_Y) for c in (0, 2, 4, 10, 12)]
RED_POST = kit.tinted("roman", "6", (1.35, 0.5, 0.42))
GATE_POSTS = [st("roman", RED_POST, c, 0, 1, 3) for c in (0, 1, 2)]

R = dict(
    mats=dict(
        path=TintMat([("town", "2", 96, 0, 96, 192)], "path", mul=(1.02, 0.92, 0.82), prio=2),
        grass=TintMat([("town", "2", 288, 0, 96, 192)], "grass", mul=(1.08, 0.86, 0.6), organic=True, prio=3),
        floor=TintMat([("town", "1", 0, 384, 384, 96)], "floor", mul=(1.05, 0.9, 0.8), prio=2),
        water=K.WATER,
        dock=Mat([("town", "6", 192, 576, 96, 96)], "dock"),
        stairs=Mat([("town", "1", 384, 384, 96, 96)], "stairs"),
        roof=TintMat([("town", "6", 192, 384, 96, 96)], "roof", mul=(1.25, 0.46, 0.36)),
        facade=TintMat([("town", "6", 576, 0, 192, 96)], "house", mul=(1.05, 0.95, 0.85)),
        wallcap=TintMat([("town", "6", 0, 672, 192, 96)], "wall", mul=(0.62, 0.42, 0.38)),
    ),
    roof_src=("town", "6", 192, 384, 96, 48),
    house_face=("town", "6", 576, 48, 192, 48),
    wall_face=("town", "1", 192, 288, 48, 96),
    cliff_face=("town", "1", 528, 576, 96, 96),
    cliff_cap="grass",
    windows=[st("town", "1", c, r, 1, 1) for (c, r) in ((4, 4), (5, 4), (6, 4), (4, 5), (5, 5))],
    doors=[st("town", "1", 5, 7, 1, 1)],
    chimneys=[st("town", "1", 0, 0, px=(330, 20, 30, 40))],
    lamps=[T.TORCH_STAND, K.LANTERN],
    pillars=GATE_POSTS,
    props={"arch": GATE_POSTS, "mural": [K.TAPESTRY, K.TAPESTRY2]},
    trees=TREES,
    decals=T.GRASS_TUFTS, decal_density=0.05,
)
SKIN = town_skin(R)
