"""Shared nature pieces for the grove / grove_flood / reef skins (Forest Wilderness, Rainforest Survival, Underwater)."""
from kit import st, Mat

# ---------------------------------------------------------------- ground
FOREST_MOSS = Mat([("forest", "6", 288, 192, 96, 192)],
                  "floor2", organic=True, prio=2)        # moss and undergrowth over dark soil
FOREST_GRASS = Mat([("town", "2", 288, 0, 96, 192)], "grass", organic=True, prio=3)
FOREST_DIRT = Mat([("town", "2", 192, 0, 96, 192)], "path", organic=True, prio=1)
FOREST_ROOTS = Mat([("forest", "3", 96, 672, 96, 96), ("forest", "3", 192, 672, 96, 96)], "roots", organic=True, prio=1)
FOREST_MOSSDIRT = Mat([("forest", "6", 192, 192, 96, 192)], "floor2", organic=True, prio=2)
LEAF_LITTER = Mat([("forest", "6", 384, 0, 96, 192)], "floor2", organic=True, prio=2)
CANOPY = Mat([("jungle", "1", 480, 384, 96, 96)], "wall", organic=True, prio=4)
VINE_ROCK = Mat([("jungle", "1", 0, 288, 192, 96)], "cliff")
PLANK_DECK = Mat([("pirate", "B4", 0, 0, 144, 192)], "floor")
WET_PLANKS = Mat([("pirate", "B4", 192, 384, 96, 192)], "dock")
WATER = Mat([("fa", "water_deep", 0, 0, 48, 48)], "water", organic=True)
SHALLOW = Mat([("fa", "water_shallow", 0, 0, 48, 48)], "shallow", organic=True)

# ---------------------------------------------------------------- trees (trunk column = cols)
OAKS = [st("forest", "1", 0, 0, 3, 4, cols=(1, 1)), st("forest", "1", 5, 0, 3, 4, cols=(1, 1)),
        st("forest", "1", 0, 4, 3, 4, cols=(1, 1)), st("forest", "1", 0, 8, 3, 4, cols=(1, 1)),
        st("forest", "7", 0, 0, 3, 4, cols=(1, 1)), st("forest", "7", 5, 0, 3, 4, cols=(1, 1)),
        st("forest", "7", 0, 4, 3, 4, cols=(1, 1)), st("forest", "3", 0, 0, 3, 3, cols=(1, 1))]
DARK_PINE = st("forest", "3", 3, 0, 3, 3, cols=(1, 1))
JUNGLE_OAK = st("jungle", "10", 0, 0, 4, 4, cols=(1, 2))
HOLLOW_TRUNKS = [st("forest", "7", 4, 4, 2, 4, cols=(0, 1)), st("forest", "7", 6, 4, 2, 4, cols=(0, 1))]

# ---------------------------------------------------------------- undergrowth
BUSHES_1 = [st("forest", "1", 13, 8), st("forest", "1", 14, 8), st("forest", "1", 15, 8), st("forest", "1", 14, 9),
            st("forest", "1", 15, 9), st("forest", "1", 13, 10), st("forest", "2", 0, 12), st("forest", "2", 1, 12)]
BUSHES_2 = [st("forest", "7", 0, 12, 2, 2), st("forest", "7", 2, 12, 2, 2), st("forest", "1", 6, 12, 2, 2)]
FERNS = [st("forest", "2", c, 13, flat=True) for c in (8, 9, 10, 11)] + [st("forest", "2", c, 14, flat=True) for c in (8, 9, 10)]
TUFTS = [st("forest", "2", c, 15, flat=True) for c in range(0, 6)]
MUSHROOMS = [st("forest", "2", 7, 14, flat=True), st("forest", "2", 15, 11, flat=True), st("forest", "10", 3, 13, flat=True)]
TWIGS = [st("forest", "7", 4, 8, 2, 1, flat=True), st("forest", "7", 6, 8, 2, 1, flat=True),
         st("forest", "7", 8, 8, 2, 1, flat=True), st("forest", "7", 10, 8, 2, 1, flat=True)]
FLOWERS = [st("forest", "3", c, 7) for c in (6, 7, 8, 9)]
STUMPS = [st("forest", "2", 13, 10), st("forest", "3", 14, 6), st("forest", "3", 15, 6), st("forest", "10", 8, 0, 2, 2)]
MOSS_ROCKS = [st("forest", "3", 6, 10, 2, 2), st("forest", "3", 8, 10, 2, 2), st("forest", "3", 4, 12, 2, 2)]
SMALL_ROCKS = [st("forest", "2", 14, 10), st("forest", "2", 15, 10), st("forest", "2", 14, 11)]
LOGS = [st("forest", "2", 8, 10, 2, 1), st("forest", "2", 10, 10, 2, 1), st("forest", "3", 13, 4, 3, 2)]
VINES = [st("forest", "7", 12, 10, 1, 2), st("forest", "7", 14, 10, 1, 2), st("forest", "7", 15, 10, 1, 2)]
ROOT_KNOT = st("forest", "5", 12, 0, 2, 2)
UPROOTED = st("forest", "10", 10, 0, 6, 3)
ROCK_MOUNDS = [st("forest", "11", 0, 0, 4, 4, hgrid=4), st("forest", "11", 4, 0, 4, 4, hgrid=4)]
ROCKS_2 = [st("forest", "11", 4, 6, 2, 2, hgrid=2), st("forest", "11", 2, 8, 2, 2, hgrid=2), st("forest", "11", 4, 8, 2, 2, hgrid=2)]
ROCKS_1 = [st("forest", "11", 13, 7), st("forest", "11", 12, 6), st("forest", "11", 14, 7), st("forest", "2", 15, 13)]
DEAD_TRUNKS = [st("forest", "1", 12, 4, 1, 2), st("forest", "1", 13, 4, 1, 2), st("forest", "1", 14, 4, 1, 2),
               st("forest", "1", 15, 4, 1, 2), st("forest", "3", 11, 4, 1, 3), st("forest", "3", 12, 4, 1, 3),
               st("forest", "2", 12, 7, 1, 3), st("forest", "2", 13, 7, 1, 3)]
DEBRIS = [st("forest", "10", 2, 10, 2, 2), st("forest", "10", 6, 10, 2, 2), st("forest", "5", 8, 12, 2, 2)]

# water dressing: props on (impassable) water cells, drawn over the animated surface; collision never changes.
# Runs are filled with the widest stamps first, so 3-wide empties space out the 3-wide decor; 1-wide pieces fill the rest.
EMPTY3 = st("forest", "2", 13, 15, 3, 1)
EMPTY1 = st("forest", "2", 15, 15, 1, 1)
REEDS3 = st("jungle", "5", 0, 10, 3, 2)
REEDS = [st("jungle", "5", 4, 10), st("jungle", "5", 7, 10), st("jungle", "5", 2, 10, 1, 2)]
PADS = [st("jungle", "5", 5, 11), st("jungle", "5", 7, 11), st("jungle", "5", 2, 12), st("jungle", "5", 3, 12),
        st("jungle", "5", 2, 13), st("jungle", "5", 3, 13), st("jungle", "5", 4, 11)]
FLOAT_LOG = st("forest", "3", 13, 4, 3, 2)


def spread(pieces, n=43, seed=7):
    """n 3-wide water slots: empties except for `pieces` at scattered indices. autoskin picks a slot by
    (x*31 + y*17) % n; n=43 shifts each row's pattern by ~0.37 of a period, which keeps the decor from lining up."""
    import random
    out = [EMPTY3] * n
    idx = random.Random(seed).sample(range(n), len(pieces))
    for i, s in zip(idx, pieces):
        out[i] = s
    return out
