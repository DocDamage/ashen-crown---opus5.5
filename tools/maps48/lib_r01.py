"""Crown March (R01) art: Medieval Fantasy Town + Forest Wilderness (CuteSCKR, native 48px)."""
from kit import st, Mat

MATS = dict(
    grass=Mat([("town", "2", 288, 0, 96, 192)], "grass", organic=True, prio=3),
    dirt=Mat([("town", "2", 192, 0, 96, 192)], "path", organic=True, prio=1),
    cobble=Mat([("town", "2", 0, 0, 96, 192)], "path", prio=2),
    cobble_warm=Mat([("town", "2", 96, 0, 96, 192)], "path", prio=2),
    slabs=Mat([("town", "1", 0, 384, 384, 96)], "floor", prio=2),
    sand=Mat([("town", "2", 96, 672, 96, 96)], "path", organic=True, prio=1),
    wood=Mat([("town", "6", 96, 576, 96, 96)], "floor"),
    stone_floor=Mat([("town", "6", 192, 384, 96, 96)], "floor"),
    water=Mat([("fa", "water_deep", 0, 0, 48, 48)], "water", organic=True, prio=0),
    roots=Mat([("forest", "3", 96, 672, 96, 96)], "path", organic=True, prio=1),
    moss=Mat([("forest", "3", 288, 672, 96, 96)], "grass", organic=True, prio=2),
)

# --- buildings (door = cell of the door, relative to the top-left)
H_THATCH_STONE = st("town", "1", 0, 0, 4, 4, solid=2, door=(1, 3), kind="house")
H_TIMBER = st("town", "1", 4, 0, 4, 4, solid=2, door=(2, 3), kind="house")
H_TIMBER_SHED = st("town", "1", 8, 0, 4, 4, solid=2, door=(2, 3), kind="house")
H_THATCH_TIMBER = st("town", "1", 0, 4, 4, 4, solid=2, door=(1, 3), kind="house")
TOWER = st("town", "1", 12, 0, 2, 4, solid=2, kind="house")
TOWER_DOOR = st("town", "1", 14, 0, 2, 4, solid=2, door=(1, 3), kind="house")
GUILD = st("town", "5", 8, 0, 4, 4, solid=2, door=(1, 3), kind="house")
TAVERN = st("town", "5", 12, 0, 4, 4, solid=2, door=(2, 3), kind="house")
CHURCH = st("town", "5", 4, 8, 2, 4, solid=2, door=(1, 3), kind="house")
CHAPEL = st("town", "5", 6, 8, 2, 4, solid=2, door=(1, 3), kind="house")
RTOWER = st("town", "5", 8, 8, 2, 4, solid=2, door=(1, 3), kind="house")
WATCHTOWER = st("town", "5", 12, 8, 2, 4, solid=1, kind="house")
WINDMILL = st("town", "3", 4, 8, 4, 4, solid=2, door=(2, 3), kind="house")
BARN = st("town", "3", 12, 8, 4, 4, solid=2, door=(1, 3), kind="house")
SHED_OPEN = st("town", "3", 8, 10, 3, 2, solid=1, kind="house")
FORGE = st("town", "5", 8, 4, 2, 2, solid=1, kind="anvil")
KILN = st("town", "5", 10, 4, 2, 2, solid=1, kind="machine")

# --- town props
STALLS = [st("town", "2", c, 4, 2, 2, solid=1, kind="counter") for c in (0, 2, 4, 6, 8)] + [st("town", "2", 4, 6, 2, 2, solid=1, kind="counter")]
CRATE = st("town", "2", 10, 4, 1, 1, kind="crate")
CRATE_STACK = st("town", "2", 2, 6, 1, 2, kind="crate")
BARREL = st("town", "2", 3, 6, 1, 2, kind="barrel")
BARRELS = st("town", "2", 6, 10, 2, 2, kind="barrel")
CRATE_S = st("town", "2", 8, 10, 1, 1, kind="crate")
WELL = st("town", "2", 8, 6, 2, 2, kind="well")
WELL2 = st("town", "2", 4, 8, 2, 2, kind="well")
SIGNPOST = st("town", "2", 12, 6, 1, 2, kind="sign")
SIGNPOST2 = st("town", "2", 13, 6, 1, 2, kind="sign")
NOTICE = st("town", "2", 14, 6, 2, 2, kind="sign")
FOUNTAIN = st("town", "2", 10, 8, 2, 2, kind="well")
CART = st("town", "2", 14, 4, 2, 2, kind="cart")
CART2 = st("town", "2", 6, 8, 2, 2, kind="cart")
BARROW = st("town", "2", 8, 8, 2, 2, kind="cart")
HANDCART = st("town", "2", 4, 10, 2, 2, kind="cart")
BENCH = st("town", "2", 8, 12, 2, 1, kind="bench")
BENCH2 = st("town", "2", 12, 11, 2, 1, kind="bench")
STONE_BENCH = st("town", "2", 6, 12, 2, 1, kind="bench")
SIGN_S = st("town", "2", 12, 12, 1, 1, kind="sign")
POTS = [st("town", "7", 0, 12, 1, 2, kind="barrel"), st("town", "7", 1, 12, 1, 2, kind="barrel"), st("town", "7", 2, 12, 1, 2, kind="barrel")]
SACKS = st("town", "7", 4, 12, 2, 2, kind="crate")
HAY = st("town", "7", 10, 12, 2, 2, kind="crate")
BIG_BARREL = st("town", "7", 12, 12, 2, 2, kind="barrel")
BARREL_ROW = [st("town", "7", c, 14, 2, 2, kind="barrel") for c in (4, 6, 8, 10)]
TORCH_STAND = st("town", "7", 2, 0, 1, 2, kind="lamp")
STATUES = [st("town", "7", c, 6, 1, 2, kind="statue") for c in (10, 11, 12, 13, 14, 15)]
BANNERS = [st("town", "7", c, 10, 1, 2, solid=0) for c in range(0, 10)]
HAYSTACK = st("town", "3", 8, 4, 2, 2, kind="crate")
SCARECROW = st("town", "3", 13, 7, 1, 1, kind="statue")
WHEAT = st("town", "3", 4, 4, 4, 4, solid=0, flat=True)
CORN = st("town", "3", 12, 0, 4, 3, solid=3, kind="garden")
VEG_PLOTS = st("town", "3", 12, 4, 4, 2, solid=2, kind="garden")

# --- nature (Forest Wilderness)
OAK = st("forest", "1", 0, 0, 3, 4, solid=1, cols=(1, 1), kind="tree")
OAK2 = st("forest", "1", 5, 0, 3, 4, solid=1, cols=(1, 1), kind="tree")
OAK3 = st("forest", "1", 0, 4, 3, 4, solid=1, cols=(1, 1), kind="tree")
PINE = st("forest", "1", 10, 0, 2, 4, solid=1, cols=(1, 1), kind="tree")
PINE_TALL = st("forest", "1", 13, 0, 3, 4, solid=1, cols=(1, 1), kind="tree")
CYPRESS = st("forest", "1", 4, 0, 1, 4, solid=1, kind="tree")
TREES_M = [st("forest", "2", c, 0, 2, 3, solid=1, cols=(1, 1), kind="tree") for c in (0, 2, 4, 6, 8, 10, 12, 14)] + \
          [st("forest", "2", c, 3, 2, 3, solid=1, cols=(1, 1), kind="tree") for c in (0, 2, 4, 6, 8, 10, 12, 14)]
TREES_AUTUMN = [st("forest", "2", c, 7, 2, 3, solid=1, cols=(1, 1), kind="tree") for c in (0, 2, 4, 6, 8)]
GROVE = st("forest", "1", 4, 8, 4, 4, solid=2, kind="tree")
GROVE2 = st("forest", "1", 9, 8, 4, 4, solid=2, kind="tree")
BUSHES = [st("forest", "2", c, 12, 1, 1, kind="hedge") for c in range(0, 6)] + [st("forest", "2", 6, 10, 1, 1, kind="hedge"), st("forest", "2", 7, 10, 1, 1, kind="hedge")]
BUSH_BIG = [st("forest", "2", 0, 10, 2, 2, kind="hedge"), st("forest", "2", 2, 10, 2, 2, kind="hedge")]
FLOWER_BUSH = [st("forest", "3", c, 7, 1, 1, kind="hedge") for c in range(6, 12)]
ROCKS = [st("forest", "2", 14, 10, 1, 1, kind="rock"), st("forest", "2", 15, 10, 1, 1, kind="rock"), st("forest", "2", 14, 11, 1, 1, kind="rock"), st("forest", "2", 15, 13, 1, 1, kind="rock")]
LOGS = [st("forest", "2", 8, 10, 2, 1, kind="rock"), st("forest", "2", 10, 10, 2, 1, kind="rock")]
STUMP = st("forest", "2", 13, 10, 1, 1, kind="rock")
MUSHROOMS = [st("forest", "2", 15, 11, 1, 1, solid=0, flat=True), st("forest", "2", 7, 14, 1, 1, solid=0, flat=True)]
GRASS_TUFTS = [st("forest", "2", c, 15, 1, 1, solid=0, flat=True) for c in range(0, 6)] + [st("forest", "2", c, 14, 1, 1, solid=0, flat=True) for c in (5, 8, 9, 10)]
BIG_ROCK = st("forest", "3", 6, 10, 2, 2, kind="rock")
BIG_ROCK2 = st("forest", "3", 8, 10, 2, 2, kind="rock")
