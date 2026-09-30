"""Furnace Spine (Cinder Reach): steampunk furnace works - soot-brown panel walls, riveted plate floors, grated
boiler walks over hot copper, brass machinery, pipes and valves; a small cooling garden."""
from autoskin import Skin, WallStyle
from kit import st, Mat
import numpy as np
from PIL import Image
import kit
from skins.common import WATER, ANVIL, RUBBLE, RUBBLE2, BUSHES, BARREL, BARREL2
from skins.lib_cold import _fbm


def _sooty(alias, sheet, rect, n=384, seed=1, soot=(34, 26, 22), amount=0.45, warm=0.0):
    """Tile a pack swatch into an n x n block and stain it with seamless soot noise (and optional ember warmth),
    so big floors are not a uniform repeat. Registered in kit's sheet cache; only used for baked ground."""
    x, y, w, h = rect
    src = np.array(kit.sheet_img(alias, sheet).crop((x, y, x + w, y + h)).convert("RGBA")).astype(np.float32)
    a = np.tile(src, (n // h, n // w, 1))
    v = _fbm(n, np.random.default_rng(seed), ((6, 0.35), (12, 0.3), (32, 0.2), (96, 0.15)))
    t = np.clip((v - 0.45) / 0.55, 0, 1) * amount
    t = np.round(t * 4) / 4
    a[..., :3] = a[..., :3] * (1 - t[..., None]) + np.array(soot, np.float32) * t[..., None]
    if warm:
        u = np.clip((0.35 - v) / 0.35, 0, 1) * warm
        u = np.round(u * 3) / 3
        a[..., :3] = a[..., :3] * (1 - u[..., None]) + np.array((150, 96, 60), np.float32) * u[..., None]
    return Image.fromarray(a.astype(np.uint8), "RGBA")


kit._img_cache.setdefault(("steam", "gen_plates"), _sooty("steam", "5", (0, 384, 192, 192), n=768, seed=3, amount=0.3, warm=0.12))
kit._img_cache.setdefault(("steam", "gen_grass"), _sooty("town", "2", (288, 0, 96, 192), n=768, seed=8, soot=(74, 70, 60), amount=0.4))

# ---- materials (Steampunk pack)
PLATES = Mat([("steam", "gen_plates", 0, 0, 768, 768)], "floor")          # riveted plates, soot-stained
GRATING = Mat([("steam", "3", 0, 480, 192, 96)], "floor2")                # iron grating on wood frame
COBBLE = Mat([("steam", "3", 0, 384, 192, 96)], "path")                   # worn cobbles
HOTPLATE = Mat([("steam", "11", 0, 0, 192, 192)], "ember")                 # heated copper plating
DECK = Mat([("steam", "10", 0, 576, 384, 192)], "bridge")                 # plank platform with gear inlay
GRASS = Mat([("steam", "gen_grass", 0, 0, 768, 768)], "grass", organic=True, prio=3)   # ash-dusted lawn
SOOT = Mat([("color", (30, 24, 22))], "wall")
FACE = ("steam", "7", 0, 672, 192, 96)                                   # soot-brown panels with conduit

# ---- props
CRATES = [st("steam", "1", c, r) for (c, r) in ((11, 12), (12, 12), (13, 12), (11, 13), (12, 13))]
DRUMS = st("factory", "4", 10, 12, 2, 2, hgrid=1)
GEAR_S = [st("steam", "4", c, 10) for c in (4, 5, 6)] + [st("steam", "3", 10, 9), st("steam", "3", 11, 9)]
BIG_GEAR = st("steam", "3", 10, 10, 2, 2, hgrid=2)
WORKBENCH = st("steam", "1", 0, 8, 2, 2)
LAB = st("steam", "5", 8, 10, 2, 2)
LAB2 = st("steam", "5", 10, 10, 2, 2)
GAUGE = st("steam", "1", 2, 8, 1, 2)
CLOCKWORK = st("steam", "3", 8, 8, 1, 2)
VALVE_RED = st("steam", "3", 8, 10, 1, 2)
BOILER = st("steam", "3", 14, 8, 2, 3, hgrid=2)
BOILER2 = st("steam", "10", 8, 13, 2, 3, hgrid=2)
TWIN_BOIL = st("steam", "5", 6, 14, 2, 2)
TANKS = st("steam", "5", 10, 14, 2, 2)
STOVE = st("steam", "6", 8, 14, 2, 2)
PANEL = st("steam", "6", 10, 14, 2, 2)
CONTROL = st("steam", "6", 6, 8, 2, 2)
ENGINE = st("steam", "2", 14, 14, 2, 2)
ENGINE2 = st("steam", "2", 14, 12, 2, 2)
DOME = st("steam", "9", 4, 8, 2, 2)
ARCH = st("steam", "6", 13, 8, 3, 3, hgrid=2)
OVENS = [st("steam", "11", c, 12, 1, 2) for c in (13, 14, 15)]
COLUMN = st("steam", "6", 8, 8, 1, 3, hgrid=1)
RPIPE = [st("factory", "4", 8, 4, 1, 2, hgrid=2), st("factory", "4", 9, 4, 1, 2, hgrid=2)]
HPIPE = [st("steam", "6", 12, 12, 3, 1), st("steam", "1", 9, 14, 3, 1), st("steam", "1", 9, 15, 3, 1),
         st("factory", "4", 10, 5, 2, 1)]
STEAM_VENT = st("steam", "11", 11, 12, 1, 2)
PORTHOLE = st("steam", "6", 11, 6, 1, 1)
PLANTS = [st("steam", "11", c, 6, 1, 2) for c in (11, 12, 13)]
MANHOLES = [st("steam", "3", c, r, flat=True) for (c, r) in ((4, 11), (5, 11), (4, 12), (5, 12))]
GRILLE = st("steam", "11", 13, 10, 1, 1)
SCRAP = st("factory", "4", 12, 2, 2, 2, hgrid=1)

SKIN = Skin(
    mats=dict(plates=PLATES, grating=GRATING, cobble=COBBLE, hot=HOTPLATE, deck=DECK, soot=SOOT, grass=GRASS,
              water=WATER),
    ground={"floor": "plates", "floor2": "grating", "path": "cobble", "ember": "hot", "bridge": "deck",
            "door": "plates", "doorway": "plates", "stairs": "grating", "grass": "grass", "pool": "water",
            "grate": "grating"},
    default="plates",
    walls={"wall": WallStyle(face=FACE, cap="soot", face_h=2),
           "window": WallStyle(face=FACE, cap="soot", face_h=2)},
    props={"crate": CRATES, "barrel": [BARREL, BARREL2, DRUMS], "gear": GEAR_S, "wheel": [BIG_GEAR, GEAR_S[0]],
           "machine": [BOILER, BOILER2, TWIN_BOIL, TANKS, STOVE, PANEL, CONTROL, ENGINE, ENGINE2, DOME, ARCH, GAUGE,
                       CLOCKWORK],
           "anvil": [ANVIL], "table": [WORKBENCH, LAB, LAB2, GAUGE], "pipe": HPIPE + RPIPE,
           "pipe_tall": [COLUMN] + RPIPE, "vent": [STEAM_VENT], "window": [PORTHOLE], "sluice": [VALVE_RED],
           "garden": PLANTS + BUSHES[:3], "rubble": [RUBBLE, RUBBLE2]},
    decals=MANHOLES, decal_density=0.02,
    wall_decor=["torch_wall", GRILLE], decor_every=5,
    water_anim={"pool": "water_deep"},
)
SKIN.dress_wall = [GAUGE, CLOCKWORK, VALVE_RED, STEAM_VENT, CRATES[0], CRATES[2], BARREL, GAUGE, VALVE_RED] + OVENS
SKIN.dress_open = [CRATES[1], GEAR_S[0], BARREL2, WORKBENCH]
SKIN.dress_target = 0.08
SKIN.dress_kind = "machine"
