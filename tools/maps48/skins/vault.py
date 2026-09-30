"""Memory Vault (D08): a sealed vault of the builders' era. Ornate teal vault tiles and glowing rune-brick walls
(Medieval Castle sheet 4) around builder machines (Sci-Fi Spaceship Interior: consoles, holo tables, sleep pods,
server racks), rune pillars and crystals; a glowing still pool."""
from autoskin import Skin, WallStyle
from kit import st, Mat
from skins.lib_d import TintMat

MATS = dict(
    vault=TintMat([("castle", "4", 96, 528, 96, 96)], "floor", mul=(0.78, 0.84, 0.98)),
    vault2=TintMat([("castle", "4", 384, 528, 96, 96)], "floor2", mul=(0.9, 0.88, 1.0)),
    cap=TintMat([("castle", "4", 192, 528, 96, 96)], "wall", mul=(0.3, 0.3, 0.38)),
    pool=TintMat([("dreamy", "6", 0, 384, 192, 192)], "pool", mul=(0.62, 0.8, 0.95), organic=True),
)

C4 = "4"
CRYSTALS = [st("castle", C4, c, 5, 1, 1) for c in (12, 13, 14, 15)] + [st("castle", C4, 8, 6, 1, 1)]
BIG_CRYSTAL = st("castle", C4, 14, 0, 2, 2)
RUNE_PILLARS = [st("castle", C4, 9, 7, 1, 3), st("castle", C4, 10, 7, 1, 3), st("castle", C4, 11, 7, 1, 3)]
RUNE_STONES = [st("castle", C4, 4, 8, 1, 2), st("castle", C4, 5, 8, 1, 2), st("castle", C4, 6, 8, 1, 2)]
PILLARS = [st("castle", C4, c, 13, 1, 3) for c in (10, 11, 14)]
FOUNTAIN = st("castle", C4, 7, 7, 2, 3, hgrid=2)
GLOW_PLANTS = [st("castle", C4, c, 6, 1, 1) for c in (4, 5, 6, 7, 9, 10, 11)]
SHIELDS = [st("castle", C4, c, 11, 1, 2) for c in (11, 12, 13)]
# builder tech (Sci-Fi Spaceship Interior sheet 6 / 1)
HOLO = st("scifi", "6", 8, 0, 2, 2)
HOLO2 = st("scifi", "6", 6, 0, 2, 3, hgrid=2)
CONSOLE = st("scifi", "6", 0, 6, 2, 2)
MAINFRAME = st("scifi", "6", 2, 6, 2, 2)
TERMINAL = st("scifi", "6", 6, 6, 2, 2)
RACK = st("scifi", "6", 4, 6, 1, 2)
DIALS = st("scifi", "6", 10, 0, 2, 2)
PANEL = st("scifi", "6", 12, 0, 2, 2)
CAPSULES = [st("scifi", "6", c, 12, 1, 2) for c in (4, 5, 6)]
POD = st("scifi", "6", 0, 12, 2, 2)
POD2 = st("scifi", "6", 2, 12, 2, 2)
DATA = [st("scifi", "1", c, 12, 1, 1) for c in (12, 13, 14, 15)] + [st("scifi", "1", c, 14, 1, 1) for c in (10, 11, 12)]
LOCKERS = [st("scifi", "6", c, 6, 1, 2) for c in (10, 11, 12)]

SKIN = Skin(
    mats=MATS,
    ground={"floor": "vault", "floor2": "vault2", "pool": "pool", "door": "vault", "doorway": "vault", "stairs": "vault"},
    default="vault",
    walls={"wall": WallStyle(face=("castle", C4, 144, 0, 48, 96), cap="cap", face_h=2)},
    props={"crystal": CRYSTALS, "altar": RUNE_STONES, "shelf": [RACK, st("scifi", "6", 4, 12, 1, 2)], "book": DATA,
           "machine": [HOLO, CONSOLE, MAINFRAME, TERMINAL, RACK, st("scifi", "6", 7, 12, 1, 2)] + CAPSULES, "bed": [POD, POD2] + CAPSULES, "mural": SHIELDS},
    decals=[st("scifi", "1", c, r, 1, 1, flat=True, solid=0) for c in (12, 13, 14) for r in (4, 5)], decal_density=0.025,
    wall_decor=[st("castle", C4, 4, 0, 1, 3), st("castle", C4, 5, 0, 1, 3)] + SHIELDS, decor_every=5,
)
SKIN.dress_wall = RUNE_PILLARS + PILLARS + [RACK, RACK] + CAPSULES + GLOW_PLANTS + CRYSTALS
SKIN.dress_open = RUNE_STONES + CRYSTALS + GLOW_PLANTS
SKIN.dress_target = 0.1
SKIN.dress_kind = "machine"
