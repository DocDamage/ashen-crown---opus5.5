"""Shared stamps and materials for the stone-dungeon auto-skins (quarry, conduit, underways, interior_stone)."""
from kit import st, Mat

# ---------------------------------------------------------------- materials
ROCK_CAP = Mat([("color", (30, 24, 21))], "wall")
STONE_CAP = Mat([("color", (20, 19, 24))], "wall")
TEAL_CAP = Mat([("color", (14, 20, 22))], "wall")
CAVE_FLOOR = Mat([("ruins", "6", 0, 576, 240, 192)], "floor2", organic=True, prio=1)
CUT_SLABS = Mat([("dungeon", "4", 0, 576, 384, 96)], "floor", prio=2)
FLAGSTONE = Mat([("dungeon", "4", 0, 576, 384, 96)], "floor", prio=2)
TRACK = Mat([("dungeon", "1", 288, 384, 96, 192)], "path", organic=True, prio=2)
GRAVEL = Mat([("castle", "3", 480, 0, 192, 96)], "path", organic=True, prio=2)
GRASS_C = Mat([("town", "2", 288, 0, 96, 192)], "grass", organic=True, prio=3)
COBBLE_D = Mat([("dungeon", "1", 192, 384, 96, 288)], "floor", prio=1)
MOSSY_STONE = Mat([("dungeon", "1", 576, 384, 192, 96)], "floor2", prio=1)
MOSSY_COB = Mat([("dungeon", "1", 480, 480, 96, 96)], "floor2", prio=1)
DUNG_TILE = Mat([("dungeon", "1", 48, 96, 144, 192)], "floor")
PLAIN_TILE = Mat([("dungeon", "7", 0, 0, 96, 96)], "floor")
CRACKED = Mat([("factory", "4", 96, 384, 96, 96)], "floor")
SLAB_ROOM = Mat([("town", "1", 0, 384, 384, 96)], "floor", prio=2)
SLATE_ROOF = Mat([("town", "6", 0, 288, 96, 96)], "roof", solid=True)
PLANKS_M = Mat([("town", "6", 192, 576, 96, 96)], "floor")
WOOD_M = Mat([("town", "6", 96, 576, 96, 96)], "floor")
IRON_PLATE = Mat([("dungeon", "7", 480, 576, 96, 96)], "lift")
GRATE_M = Mat([("dungeon", "2", 96, 576, 48, 48)], "grate")
WATER_M = Mat([("fa", "water_deep", 0, 0, 48, 48)], "water", organic=True)
SHALLOW_M = Mat([("fa", "water_shallow", 0, 0, 48, 48)], "shallow", organic=True)
VOID_M = Mat([], "void")

# ---------------------------------------------------------------- wall faces (alias, sheet, x, y, w, h)
FACE_CAVE = ("dungeon", "1", 576, 0, 192, 96)          # rough brown cave rock
FACE_BRICK_MOSS = ("dungeon", "1", 48, 0, 288, 96)     # grey dungeon brick with moss and a lit rim
FACE_FIELDSTONE = ("town", "6", 0, 672, 192, 96)       # grey fieldstone
FACE_CASTLE_MOSS = ("castle", "1", 240, 96, 144, 96)   # mossy ashlar (aqueduct)
FACE_ARCHES = ("castle", "1", 0, 384, 192, 96)         # arcade with crenels (aqueduct arches)
FACE_TOWN_STONE = ("town", "1", 0, 576, 96, 96)        # dressed stone with coping
FACE_HOUSE = ("town", "6", 576, 144, 96, 48)           # timber over stone footing (1 row)
FACE_WINDOW = ("town", "6", 672, 192, 48, 48)          # timber wall with a window (1 row)

# ---------------------------------------------------------------- props
CRATES = [st("dungeon", "2", c, 0) for c in (8, 9, 10, 11)] + [st("dungeon", "2", 8, 1), st("dungeon", "2", 9, 1)]
IRON_CRATES = [st("dungeon", "2", 10, 1), st("dungeon", "2", 11, 1), st("dungeon", "2", 12, 1)]
BARRELS = [st("dungeon", "2", c, 4) for c in (8, 9, 10, 11)] + [st("dungeon", "2", 12, 3), st("dungeon", "2", 13, 3)]
BUCKETS = [st("dungeon", "2", 12, 4), st("dungeon", "2", 13, 4)]
SACKS = [st("dungeon", "2", 4, 3), st("dungeon", "2", 6, 3), st("dungeon", "2", 7, 3)]
POTS = [st("dungeon", "2", c, 3) for c in (0, 1, 2)]
ORE = [st("dungeon", "2", c, 8) for c in (12, 13, 14, 15)]
STONES = [st("dungeon", "2", c, 10) for c in (0, 1, 2, 3)] + [st("dungeon", "2", c, 11) for c in (0, 1)]
INGOTS = [st("dungeon", "2", 12, 9), st("dungeon", "2", 13, 9)]
LANTERN_G = [st("dungeon", "2", 8, 11), st("dungeon", "2", 9, 11)]
LANTERN_HOOK = st("dungeon", "2", 15, 2)
ROCKS_S = [st("dungeon", "3", 3, 0), st("dungeon", "3", 0, 3), st("dungeon", "3", 1, 3), st("dungeon", "3", 3, 3),
           st("dungeon", "3", 4, 2), st("dungeon", "3", 5, 2)]
ROCKS_M = [st("dungeon", "3", 6, 2), st("dungeon", "3", 7, 2), st("dungeon", "3", 6, 3), st("dungeon", "3", 7, 3)]
BOULDER_2 = [st("dungeon", "3", 2, 4, 2, 2, hgrid=1), st("dungeon", "5", 8, 0, 2, 2), st("dungeon", "3", 0, 4, 2, 2)]
PEBBLES = [st("dungeon", "3", c, r, flat=True) for c in (4, 5) for r in (0, 1)]
RUBBLE_S = [st("dungeon", "1", 12, 12), st("dungeon", "1", 13, 12)]
RUBBLE_2 = [st("dungeon", "5", 4, 0, 2, 2), st("dungeon", "7", 0, 10, 2, 2), st("dungeon", "7", 4, 10, 2, 2),
            st("dungeon", "6", 12, 6, 2, 2)]
STALAG = [st("dungeon", "5", 6, 8, 1, 2), st("dungeon", "5", 8, 8, 1, 2)]
CRYSTALS = [st("castle", "4", c, 5) for c in (12, 13, 14, 15)]
CRYSTAL_BIG = st("castle", "4", 14, 0, 2, 2)
CRYSTAL_P = st("dungeon", "3", 5, 9)
TORCHES = [st("town", "7", 2, 0, 1, 2), st("town", "7", 3, 0, 1, 2)]
CANDLE_STAND = [st("castle", "9", 5, 0, 1, 2), st("castle", "9", 6, 0, 1, 2)]
BRAZIER = st("castle", "9", 4, 0, 1, 2)
SIGN_DANGER = st("dungeon", "3", 14, 12)
SIGN_RUNES = st("dungeon", "3", 14, 10)
CART = st("ruins", "2", 12, 2, 2, 2)
SPOOL = st("factory", "4", 2, 6, 2, 2, hgrid=2)
SPOOL_BIG = st("factory", "4", 6, 6, 2, 2, hgrid=2)
WINCH = st("factory", "3", 2, 12, 1, 2)
RUST_MACHINE = st("factory", "3", 0, 12, 2, 2, hgrid=2)
PIPE_V = [st("factory", "4", 8, 4, 1, 2), st("factory", "4", 9, 4, 1, 2)]
PIPE_VG = [st("factory", "4", 14, 4, 1, 2), st("factory", "4", 15, 4, 1, 2)]
PIPE_H = [st("factory", "4", 10, 4, 2, 1), st("factory", "4", 10, 5, 2, 1)]
PIPE_ELBOW = st("factory", "4", 12, 4, 2, 1)
TOOL_SHELF = [st("factory", "4", 10, 0, 2, 2, hgrid=1), st("factory", "4", 12, 0, 2, 2, hgrid=1)]
CRATE_STACK = st("factory", "4", 6, 0, 2, 2)
GRATE_PLATE = st("dungeon", "6", 0, 3)
CHIMNEY_S = st("castle", "6", 12, 12, 1, 2)
STATUE_K = [st("town", "7", 12, 6, 1, 2), st("town", "7", 10, 6, 1, 2), st("town", "7", 0, 8, 1, 2), st("town", "7", 2, 8, 1, 2)]
GATE_WOOD = st("town", "1", 2, 12, 2, 2)
GATE_WOOD2 = st("town", "1", 6, 12, 2, 2)
PORTCULLIS = st("dungeon", "4", 6, 4, 2, 2)
BENCH_STONE = [st("dungeon", "4", 8, 8, 2, 1), st("dungeon", "4", 10, 8, 2, 1)]
TABLE_2 = st("town", "15", 10, 8, 2, 2, hgrid=2)
STOOL_W = st("town", "15", 11, 3)
BONES_F = [st("dungeon", "4", 8, 11, flat=True), st("dungeon", "4", 9, 11, flat=True), st("dungeon", "4", 10, 10, flat=True)]
COBWEB = st("dungeon", "6", 8, 15, flat=True)
PILLAR = [st("dungeon", "6", 8, 12, 1, 2), st("dungeon", "7", 6, 10, 1, 2), st("dungeon", "7", 5, 12, 1, 2)]
PILLAR_BROKEN = [st("dungeon", "7", 4, 12, 1, 2), st("dungeon", "6", 11, 12, 1, 2)]
FALLEN_COL = [st("dungeon", "7", 0, 12, 2, 2), st("dungeon", "7", 6, 12, 2, 2)]
MECH_PLATE = st("dungeon", "7", 10, 12, 2, 2, hgrid=2)
LEVERS = [st("dungeon", "6", 12, 8, 1, 2), st("dungeon", "6", 13, 8, 1, 2), st("dungeon", "6", 14, 8, 1, 2), st("dungeon", "6", 15, 8, 1, 2)]
RUNE_STONES = [st("dungeon", "6", c, r) for c in (14, 15) for r in (12, 13)]
RUNE_PILLARS = [st("castle", "4", 9, 7, 1, 3), st("castle", "4", 10, 7, 1, 3), st("castle", "4", 11, 7, 1, 3)]
RUNE_STUBS = [st("castle", "4", 4, 8, 1, 2), st("castle", "4", 5, 8, 1, 2), st("castle", "4", 6, 8, 1, 2)]
BOOKCASE_1 = [st("castle", "6", 5, 8, 1, 2), st("castle", "6", 10, 8, 1, 2)]
BOOKCASE_2 = [st("castle", "6", 6, 8, 2, 2), st("castle", "6", 8, 8, 2, 2)]
CUPBOARD_2 = st("castle", "6", 11, 8, 2, 2)
CUPBOARD_1 = [st("castle", "6", 13, 8, 1, 2), st("castle", "6", 15, 8, 1, 2)]
SCROLLS = [st("town", "7", 5, 2), st("town", "7", 6, 2), st("town", "7", 7, 2), st("town", "7", 6, 3)]
BOOK_OPEN = st("town", "7", 8, 3)
SCROLL_JAR = st("town", "7", 9, 3)
ARCH = st("town", "1", 10, 8, 2, 2)
ROWBOAT = st("sea", "2", 0, 14, 2, 1)

# record stacks: freestanding 2-row bookcases (hgrid 2) with 1-row fallbacks
BOOKCASE_2G = [st("castle", "6", 6, 8, 2, 2, hgrid=2), st("castle", "6", 8, 8, 2, 2, hgrid=2)]
BOOKCASE_1G = [st("castle", "6", 5, 8, 1, 2, hgrid=2), st("castle", "6", 10, 8, 1, 2, hgrid=2)]
SHELF_LOW_1 = [st("town", "6", 8, 4, 1, 2)]
BELL = st("ruins", "1", 8, 8, 2, 2)
GEAR_BOX = st("factory", "3", 14, 3)
CHEST_W = st("dungeon", "2", 0, 0)
BED_S = st("town", "6", 10, 4, 1, 2)
SLIME = [st("dungeon", "6", 9, 15, flat=True), st("dungeon", "6", 10, 15, flat=True)]
