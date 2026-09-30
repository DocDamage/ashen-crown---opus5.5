"""Cinder Reach towns (fallback until the hand redesign): soot-brown cobbles, rust roofs over brick-and-timber
facades, brass gears, boilers, pistons, gas lamps and steam machines (Steampunk + Medieval Fantasy Town)."""
from kit import st, Mat
from skins.lib_d import TintMat, town_skin
from skins import common as K
import lib_r01 as T

S3, S4 = "3", "4"
R = dict(
    mats=dict(
        path=TintMat([("steam", S3, 0, 384, 192, 96)], "path", mul=(0.82, 0.74, 0.68), prio=2),
        grass=TintMat([("town", "2", 288, 0, 96, 192)], "grass", mul=(0.62, 0.62, 0.45), organic=True, prio=3),
        floor=Mat([("steam", S4, 0, 384, 192, 192)], "floor"),
        water=K.WATER, pool=K.WATER,
        dock=TintMat([("town", "6", 192, 576, 96, 96)], "dock", mul=(0.7, 0.62, 0.55)),
        stairs=TintMat([("town", "1", 384, 384, 96, 96)], "stairs", mul=(0.78, 0.7, 0.62)),
        roof=TintMat([("town", "6", 0, 576, 96, 96)], "roof", mul=(0.72, 0.5, 0.36)),
        facade=TintMat([("town", "6", 576, 96, 192, 96)], "house", mul=(0.8, 0.66, 0.56)),
        wallcap=TintMat([("steam", S3, 0, 480, 192, 96)], "wall", mul=(0.5, 0.42, 0.36)),
    ),
    roof_src=("town", "6", 0, 576, 96, 48),
    house_face=("town", "6", 576, 144, 192, 48),
    wall_face=("steam", S3, 96, 0, 288, 96),
    windows=[st("town", "1", c, r, 1, 1) for (c, r) in ((4, 4), (6, 4), (7, 4), (7, 5))],
    doors=[st("town", "1", 5, 7, 1, 1)],
    chimneys=[st("steam", S4, 4, 8, 1, 2), st("steam", S4, 5, 8, 1, 2)],
    lamps=[st("steam", S4, 8, 8, 1, 2), st("steam", S3, 8, 1, 1, 3), st("steam", S3, 10, 1, 1, 3)],
    gears=[st("steam", S4, 4, 10, 1, 1), st("steam", S4, 5, 10, 1, 1), st("steam", S4, 6, 10, 1, 1), st("steam", S4, 0, 4, 2, 2)],
    wheels=[st("steam", S4, 0, 6, 2, 2), st("steam", S4, 9, 13, 3, 3, hgrid=1)],
    pipes=[st("steam", S4, 4, 8, 1, 2), st("steam", S4, 5, 8, 1, 2), st("steam", S3, 8, 8, 1, 2), st("steam", S3, 14, 8, 2, 3)],
    vents=[st("steam", S3, 13, 10, 1, 1), st("steam", S3, 7, 10, 1, 1)],
    machines=[st("steam", S3, 8, 10, 1, 2), st("steam", S3, 14, 8, 2, 3), K.FORGE],
    benches=[st("steam", S4, 14, 12, 2, 1), st("steam", S3, 12, 9, 1, 1)],
    trees=[st("forest", "2", c, 7, 2, 3, cols=(1, 1)) for c in (0, 2, 4, 6, 8)],
    decals=[st("steam", S3, 4, 11, 1, 1, flat=True, solid=0), st("steam", S3, 5, 11, 1, 1, flat=True, solid=0)],
    decal_density=0.02,
)
SKIN = town_skin(R)
