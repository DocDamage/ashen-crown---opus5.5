"""Crown Heart (D10): the living interior of the Crown. Flesh floors and walls (Infected Spaceship sheet 1/6),
cursed land objects (tentacles, eyes, tooth mouths, horns), bone-grey gothic walkways over a dark ichor sea,
star-flecked void outside the vessel."""
from autoskin import Skin, WallStyle
from kit import st, Mat
from skins.lib_d import TintMat, cur, flat1

MATS = dict(
    flesh=TintMat([("infect", "1", 0, 0, 96, 96)], "floor", mul=(0.62, 0.55, 0.64)),
    flesh2=TintMat([("infect", "1", 0, 384, 144, 192)], "floor2", mul=(0.9, 0.85, 0.9), organic=True, prio=2),
    cap=TintMat([("infect", "1", 0, 0, 96, 96)], "wall", mul=(0.3, 0.2, 0.28)),
    ichor=TintMat([("fa", "water_deep", 0, 0, 48, 48)], "water", mul=(0.5, 0.22, 0.55), add=(26, 0, 6), organic=True),
    walk=TintMat([("gothic", "5", 0, 672, 96, 96)], "dock", mul=(1.05, 0.9, 1.05), organic=True, prio=1),
    bridge=Mat([("gothic", "4", 0, 192, 96, 96)], "bridge"),
    void=TintMat([("dreamy", "1", 384, 576, 384, 96)], "void", mul=(0.3, 0.2, 0.4)),
)

TENT = [cur("Tentacles_1"), cur("Tentacles_2"), cur("Tentacles_3"), cur("Tentacles_4")]
EYES = [cur("Eyes_1"), cur("Eyes_2")]
MOUTHS = [cur("Tooth_mouth_1"), cur("Tooth_mouth_2"), cur("Tooth_mouth_3"), cur("Tooth_mouth_4"), cur("Tooth_mouth_5")]
HORNS = [cur("Claw_monster_2"), cur("Claw_monster_3")]
SPIKES = [cur("Claw_eggs_1"), cur("Claw_eggs_2"), cur("Claw_eggs_3"), cur("Claw_eggs_4")]
EGGS = [cur("Eggs_1"), cur("Eggs_2"), cur("Eggs_3")]
RUNES = [cur("Rune_stone_1")]
NEURO = [cur("Neuro_monster_1"), cur("Neuro_monster_2")]
SHROOMS = [cur("Mushrooms_1"), cur("Mushrooms_2")]
STALKS = [cur("Tooth_monster_1"), cur("Tooth_monster_2"), cur("Tooth_monster_3")]
CRYSTALS = [st("castle", "4", c, 5, 1, 1) for c in (12, 13, 14, 15)] + [st("dreamy", "7", c, 13, 1, 1) for c in (12, 13, 14, 15)]
BIG_EYE = st("infect", "1", 10, 12, 2, 2, hgrid=1)
MAW = st("infect", "1", 8, 12, 2, 2, hgrid=1)

SKIN = Skin(
    mats=MATS,
    ground={"floor": "flesh", "floor2": "flesh2", "dock": "walk", "bridge": "bridge", "water": "ichor",
            "door": "flesh", "doorway": "flesh", "stairs": "walk"},
    default="flesh",
    walls={"wall": WallStyle(face=("infect", "6", 0, 288, 288, 96), cap="cap", face_h=2)},
    props={"crystal": CRYSTALS, "pillar": HORNS + NEURO, "barrel": EGGS, "crate": SPIKES, "vent": MOUTHS,
           "brazier": NEURO, "rubble": TENT, "machine": [BIG_EYE, MAW], "altar": RUNES},
    decals=[flat1(s) for s in EYES + [cur("Webbed_1"), cur("Webbed_2"), cur("Mushrooms_3"), cur("Tentacles_3"), cur("Tentacles_1"),
                                       cur("Tooth_mouth_3"), cur("Tooth_mouth_5"), cur("Eggs_3"), cur("Claw_eggs_4")]], decal_density=0.07,
    wall_decor=[st("infect", "6", 12, 6, 1, 2), st("infect", "6", 13, 0, 1, 1)], decor_every=5,
)
SKIN.dress_wall = TENT + SPIKES + SHROOMS + EGGS + STALKS
SKIN.dress_open = TENT + MOUTHS + EGGS + SHROOMS
SKIN.dress_target = 0.12
SKIN.dress_kind = "rubble"
