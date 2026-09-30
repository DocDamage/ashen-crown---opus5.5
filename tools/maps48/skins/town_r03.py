"""Glass Coast towns (fallback until the hand redesign): pale sea-washed cobbles and sand, bleached pier planks,
teal roofs over whitewashed timber facades, lanterns, nets, crates, barrels, bells and rowboats (Pirate Age +
Medieval Fantasy Town)."""
from kit import st, Mat
from skins.lib_d import TintMat, town_skin
from skins import common as K
import lib_r01 as T

P = "B1-1"
R = dict(
    mats=dict(
        path=TintMat([("town", "2", 0, 0, 96, 192)], "path", mul=(1.05, 1.02, 0.92), prio=2),
        grass=TintMat([("town", "2", 288, 0, 96, 192)], "grass", mul=(0.85, 1.0, 0.85), organic=True, prio=3),
        floor=TintMat([("town", "2", 96, 672, 96, 96)], "floor", mul=(1.05, 1.02, 0.95), organic=True, prio=1),
        water=K.WATER,
        dock=TintMat([("pirate", P, 0, 0, 192, 192)], "dock", mul=(1.12, 1.06, 1.0)),
        stairs=TintMat([("town", "1", 384, 384, 96, 96)], "stairs", mul=(1.05, 1.02, 0.95)),
        roof=TintMat([("town", "6", 192, 384, 96, 96)], "roof", mul=(0.5, 0.82, 0.84)),
        facade=TintMat([("town", "6", 576, 0, 192, 96)], "house", mul=(1.08, 1.06, 1.04)),
        wallcap=TintMat([("town", "6", 0, 672, 192, 96)], "wall", mul=(0.7, 0.75, 0.78)),
    ),
    roof_src=("town", "6", 192, 384, 96, 48),
    house_face=("town", "6", 576, 48, 192, 48),
    wall_face=("town", "1", 192, 288, 48, 96),
    windows=[st("town", "1", c, r, 1, 1) for (c, r) in ((4, 4), (5, 4), (4, 5), (5, 5))] + [st("pirate", "B7", 13, 10, 1, 1)],
    doors=[st("town", "1", 5, 7, 1, 1)],
    chimneys=[st("town", "1", 0, 0, px=(330, 20, 30, 40))],
    lamps=[st("pirate", P, 14, 14, 1, 2), st("pirate", "B7", 14, 8, 1, 2)],
    crates=[st("pirate", P, 7, 12, 1, 1), st("pirate", P, 8, 12, 1, 1), st("pirate", P, 7, 13, 1, 1)],
    barrels=[st("pirate", P, c, 12, 1, 1) for c in (4, 5, 6)],
    bells=[st("pirate", P, 10, 8, 1, 1)],
    chests=[st("pirate", P, 11, 12, 1, 1), st("pirate", P, 9, 13, 1, 1)],
    laundry=[st("island", "4", 11, 4, 2, 2), st("island", "4", 10, 12, 2, 2)],
    trees=[st("island", "2", 0, 0, 2, 3, cols=(1, 1)), st("island", "2", 2, 0, 2, 3, cols=(1, 1))],
    decals=[st("pirate", P, c, r, 1, 1, flat=True, solid=0) for (c, r) in ((10, 14), (11, 14), (14, 13), (15, 13))],
    decal_density=0.025,
)
SKIN = town_skin(R)
