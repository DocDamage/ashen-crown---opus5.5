"""The Wayfarer's common deck (W_DECK): planked airship deck, porthole timber walls, bunks, chart tables, lockers,
brass instruments, crates and barrels (Airships/flying boat tile-B sheets)."""
from autoskin import Skin, WallStyle
from kit import st, Mat
from skins.lib_d import TintMat

A = "aship"
MATS = dict(
    deck=Mat([(A, "tile-B-06", 0, 0, 192, 144)], "floor"),
    deck2=Mat([(A, "tile-B-06", 0, 576, 96, 192)], "floor2"),
    cap=TintMat([(A, "tile-B-02", 384, 96, 192, 96)], "wall", mul=(0.38, 0.32, 0.3)),
)

BUNKS = [st(A, "tile-B-05", 0, 0, 2, 2, hgrid=2), st(A, "tile-B-05", 0, 2, 2, 2, hgrid=2), st(A, "tile-B-05", 2, 0, 2, 2, hgrid=2)]
BUNK1 = [st(A, "tile-B-05", c, r, 2, 1) for (c, r) in ((0, 4), (2, 3), (0, 6))]
CABINETS = [st(A, "tile-B-05", 8, 0, 2, 2), st(A, "tile-B-05", 10, 0, 1, 2), st(A, "tile-B-05", 11, 0, 1, 2)]
DRESSER = [st(A, "tile-B-05", 2, 5, 2, 2), st(A, "tile-B-05", 4, 5, 1, 2)]
TABLES = [st(A, "tile-B-05", 5, 5, 2, 1), st(A, "tile-B-05", 8, 5, 2, 1), st(A, "tile-B-05", 5, 7, 2, 1)]
TABLE1 = [st(A, "tile-B-05", 11, 5, 1, 1), st(A, "tile-B-05", 11, 7, 1, 1), st(A, "tile-B-05", 7, 10, 1, 1)]
CHAIRS = [st(A, "tile-B-05", 10, 5, 1, 1), st(A, "tile-B-05", 10, 6, 1, 1), st(A, "tile-B-05", 5, 10, 1, 1)]
BARRELS = [st(A, "tile-B-05", c, 8, 1, 1) for c in (11, 12, 13, 14)] + [st(A, "tile-B-05", 2, 10, 1, 1)]
CRATES = [st(A, "tile-B-05", 0, 8, 2, 2), st(A, "tile-B-05", 8, 8, 2, 2), st(A, "tile-B-05", 10, 9, 1, 1),
          st(A, "tile-B-05", 3, 10, 1, 1)]
CHESTS = [st(A, "tile-B-05", 5, 2, 1, 1), st(A, "tile-B-05", 6, 2, 1, 1), st(A, "tile-B-05", 7, 2, 1, 1), st(A, "tile-B-05", 0, 13, 1, 1)]
PLANTS = [st(A, "tile-B-05", c, 11, 1, 1) for c in (6, 7, 8, 9, 10, 11)]
LAMPS = [st(A, "tile-B-05", c, 3, 1, 1) for c in (12, 13, 14, 15)]
HELM = st(A, "tile-B-04", 9, 0, 2, 2)
CHART = st(A, "tile-B-04", 5, 0, 4, 2, hgrid=1)
CHART2 = st(A, "tile-B-04", 5, 3, 3, 2, hgrid=1)
DESK = st(A, "tile-B-04", 0, 6, 4, 2, hgrid=1)
LEVERS = [st(A, "tile-B-04", 7, 6, 1, 1), st(A, "tile-B-04", 8, 6, 1, 1), st(A, "tile-B-04", 4, 7, 1, 1)]
WINCH = st(A, "tile-B-04", 0, 14, 2, 2)
ENGINE = st(A, "tile-B-04", 0, 12, 2, 2)
LADDER = st(A, "tile-B-06", 10, 2, 1, 1, flat=True, solid=0)
HATCH = st(A, "tile-B-06", 4, 0, 1, 1, flat=True, solid=0)

SKIN = Skin(
    mats=MATS,
    ground={"floor": "deck", "floor2": "deck2", "door": "deck", "doorway": "deck", "stairs": "deck", "ladder": "deck"},
    default="deck",
    walls={"wall": WallStyle(face=(A, "tile-B-02", 384, 0, 192, 96), cap="cap", face_h=2)},
    props={"bed": BUNKS + BUNK1, "shelf": CABINETS + DRESSER, "table": TABLES + TABLE1, "ladder": [LADDER],
           "crate": CRATES, "barrel": BARRELS, "chest_deco": CHESTS, "lamp": LAMPS, "bench": CHAIRS,
           "machine": [ENGINE, WINCH]},
    decals=[HATCH], decal_density=0.008,
    wall_decor=[st(A, "tile-B-02", 14, 8, 2, 2), st(A, "tile-B-05", 12, 2, 1, 1)], decor_every=5,
)
SKIN.dress_wall = CABINETS + DRESSER + BARRELS + CRATES + CHESTS + PLANTS + [HELM, CHART2, WINCH, ENGINE] + LEVERS
SKIN.dress_open = [CRATES[0], CRATES[1], BARRELS[0], BARRELS[1], CHART]
SKIN.dress_target = 0.16
SKIN.dress_kind = "crate"
