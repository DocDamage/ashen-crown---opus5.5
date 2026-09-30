"""Whitebone Redoubt / Sanctuary (Skyspine): a pale stone fortress-prison in the snow - white crenellated walls with
snow on the wall walks, grey flagstone yards and halls, darker cobbled cells, iron gates, fur-bunk barracks, rune
tablets in the names hall, sealed altars below, pines outside."""
from autoskin import Skin, WallStyle
from kit import st, Mat
from skins.common import FLAGS, CRATE, CRATE2, BARREL, BARREL2, PINES, CRACKS, BONES
from skins.lib_cold import SNOW, SNOW_CAP, FLAGS, DRIFTS

FLOOR = FLAGS                                                                        # grey flagstones
CELLS = Mat([("dungeon", "1", 192, 384, 96, 288)], "floor2")                       # worn cobbles in the cells
GRATE = Mat([("steam", "3", 0, 480, 192, 96)], "grate")
FACE = ("siege", "3", 0, 432, 336, 96)                                             # pale ashlar wall

BUNKS = [st("viking", "5 (1)", c, 0, 2, 2) for c in (0, 2, 4, 6)]
SHELF1 = [st("castle", "6", c, 8, 1, 2) for c in (5, 10, 13, 14, 15)]
SHELF2 = [st("castle", "6", c, 8, 2, 2) for c in (6, 8, 11)]
RUNE_PILLAR = st("castle", "4", 10, 13, 1, 3)
RUNESTONES = [st("dungeon", "3", c, 14) for c in (12, 13, 14)]
PILLAR = st("castle", "4", 14, 13, 1, 3)
PORTCULLIS = st("dungeon", "4", 6, 0, 2, 2)
PEDESTALS = [st("dungeon", "3", c, 14, 1, 2) for c in (0, 2, 4)]
SEAL = st("dungeon", "7", 10, 12, 2, 2, hgrid=2)
BRAZIER = st("castle", "9", 4, 0, 1, 2)
TENTS = [st("siege", "4", c, 8, 2, 2) for c in (8, 10, 12)]
CHAINS = [st("dungeon", "6", c, 8, 1, 2) for c in (12, 13)]
CAGE = st("dungeon", "7", 12, 2, 1, 2)
WEAPONS = st("castle", "5", 8, 12, 2, 2)
ARMOR = st("siege", "8", 8, 10, 1, 2)
PEBBLES = [st("dungeon", "3", c, r, flat=True) for (c, r) in ((4, 0), (5, 0), (4, 1))]
STATUES = [st("castle", "7", c, 6, 1, 2) for c in (8, 11)]

SKIN = Skin(
    mats=dict(floor=FLOOR, cells=CELLS, snow=SNOW, cap=SNOW_CAP, grate=GRATE),
    ground={"floor": "floor", "floor2": "cells", "snow": "snow", "doorway": "floor", "door": "floor",
            "stairs": "floor", "grate": "grate", "ice": "snow", "path": "floor"},
    default="floor",
    walls={"wall": WallStyle(face=FACE, cap="cap", face_h=2)},
    props={"bed": BUNKS, "shelf": SHELF2 + SHELF1, "mural": [RUNE_PILLAR], "sign": RUNESTONES, "pillar": [PILLAR],
           "gate": [PORTCULLIS], "altar": PEDESTALS, "machine": [SEAL], "brazier": [BRAZIER], "tent": TENTS,
           "barrel": [BARREL, BARREL2], "crate": [CRATE, CRATE2]},
    trees=[st("forest", "2", c, 0, 2, 3, cols=(1, 1)) for c in (6, 10, 12)],
    decals=PEBBLES + PEBBLES + DRIFTS, decal_density=0.035,
    wall_decor=["torch_wall", "banner_wall_blue"], decor_every=6,
)
SKIN.dress_wall = CHAINS + [CAGE, WEAPONS, ARMOR, BARREL, CRATE, BRAZIER] + STATUES
SKIN.dress_open = [BARREL2, CRATE2, BRAZIER]
SKIN.dress_target = 0.06
SKIN.dress_kind = "crate"
