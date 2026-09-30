"""Drowned Archive (D05P_R01, D05_R01..R06, T04_GALLERY): a half-flooded archive of records - mossy flagstones and
cracked tiles under standing water, tall bookshelves, a bell nave with pillars, lantern stations, galleries with
stained glass, a witness vault and a roof pier. Water uses the animated field surfaces."""
from autoskin import Skin, WallStyle
from skins.common import VOID, DARK, DUNG_MOSSY, DUNG_TILES, CRATE, CRATE2, BARREL, BARREL2, POT, SACK
from skins.lib_nature import WATER, SHALLOW, EMPTY3, EMPTY1, spread
from kit import st, Mat

PLANKS = Mat([("pirate", "B4", 0, 0, 144, 192)], "dock")
FLAGS_MOSS = Mat([("castle", "3", 48, 192, 96, 96)], "floor", organic=True, prio=2)
FLAGS_GREY = Mat([("dungeon", "4", 0, 384, 144, 96)], "floor", organic=True, prio=1)
PUDDLE = Mat([("fa", "water_shallow", 0, 0, 48, 48)], "puddle", organic=True)

SHELVES_2 = [st("castle", "6", 6, 8, 2, 2, hgrid=2), st("castle", "6", 8, 8, 2, 2, hgrid=2)]
SHELVES_1 = [st("castle", "6", 5, 8, 1, 2, hgrid=2), st("castle", "6", 10, 8, 1, 2, hgrid=2), st("castle", "5", 12, 0, 1, 2)]
BOOKS = [st("town", "7", 8, 3), st("town", "7", 9, 3), st("town", "7", 6, 2), st("town", "7", 8, 3)]
SCROLLS = [st("town", "7", 5, 2, flat=True), st("town", "7", 7, 2, flat=True), st("town", "7", 5, 3, flat=True)]
PILLARS = [st("castle", "4", 12, 13, 1, 3), st("castle", "4", 15, 13, 1, 3)]
BELLS = [st("pirate", "B1-1", 10, 8)]
LAMPS = [st("castle", "7", 14, 6, 1, 2), st("castle", "9", 6, 0, 1, 2)]
MACHINE = [st("castle", "9", 2, 0, 2, 2), st("castle", "9", 4, 0, 1, 2)]
CRYSTALS = [st("town", "7", 6, 0, 1, 2, hgrid=2), st("town", "7", 7, 0, 1, 2, hgrid=2), st("town", "7", 8, 0, 1, 2, hgrid=2),
            st("forest", "2", 15, 15, 1, 2, hgrid=2), st("castle", "7", 15, 0, 1, 2, hgrid=2), st("forest", "2", 15, 15, 1, 2, hgrid=2)]
BOATS = [st("sea", "4", 12, 10, 2, 2), st("sea", "2", 0, 14, 2, 2)]
POOL_EDGE = [st("castle", "4", 7, 7, 2, 2, hgrid=2)]
STAINED = [st("castle", "7", 5, 0, 1, 3), st("castle", "7", 6, 0, 1, 3), st("castle", "7", 7, 0, 1, 3), st("castle", "7", 14, 0, 1, 3)]
CANDLE_WALL = st("castle", "9", 7, 0, 1, 2)
RUBBLE = [st("dungeon", "1", 12, 12), st("dungeon", "1", 13, 12)]
DEBRIS = [st("sea", "4", 12, 9, flat=True), st("sea", "4", 13, 9, flat=True)] + SCROLLS

SKIN = Skin(
    mats=dict(void=VOID, dark=DARK, flag=FLAGS_MOSS, tiles=FLAGS_GREY, planks=PLANKS, water=WATER, shallow=SHALLOW,
              puddle=PUDDLE),
    ground={"floor": "flag", "floor2": "tiles", "doorway": "flag", "door": "flag", "stairs": "flag", "bridge": "planks",
            "dock": "planks", "water": "water", "shallow": "shallow", "puddle": "puddle", "pool": "water"},
    default="flag",
    walls={"wall": WallStyle(face=("dungeon", "1", 96, 0, 192, 96), cap="dark", face_h=2)},
    props={"shelf": SHELVES_2 + SHELVES_1, "book": BOOKS, "pillar": PILLARS, "bell": BELLS, "lamp": LAMPS,
           "machine": MACHINE, "crystal": CRYSTALS, "boat": BOATS,
           "water": spread([st("castle", "6", 5, 8, 1, 2), EMPTY3, st("pirate", "B1-1", 6, 12)], n=47) + [EMPTY1] * 12
                    + [BARREL, CRATE] + RUBBLE},
    decals=DEBRIS, decal_density=0.02,
    wall_decor=STAINED + [CANDLE_WALL, "torch_wall"], decor_every=5,
    water_anim={"water": "water_deep", "pool": "water_deep", "shallow": "water_shallow", "puddle": "water_shallow"},
)
SKIN.dress_wall = SHELVES_1 + SHELVES_1 + [BARREL, BARREL2, CRATE, CRATE2, POT, SACK] + BOOKS[:2]
SKIN.dress_open = BOOKS + [BARREL, CRATE, BARREL2] + SHELVES_1[:2]
SKIN.dress_target = 0.10
SKIN.dress_kind = "shelf"
