"""Sable Conduit: an old aqueduct that houses builder-era relay machinery (mossy arches, iron, teal rune glow)."""
from autoskin import Skin, WallStyle
from skins.lib_quarry import *
from kit import Mat

RELAY_FLOOR = Mat([("castle", "4", 96, 528, 96, 96)], "floor2", prio=3)
BRIDGE_STONE = Mat([("dungeon", "1", 192, 384, 96, 288)], "bridge", prio=2)

SKIN = Skin(
    mats=dict(void=VOID_M, cap=TEAL_CAP, flags=MOSSY_STONE, relay=RELAY_FLOOR, water=WATER_M, bridge=BRIDGE_STONE,
              plate=IRON_PLATE, cob=MOSSY_COB),
    ground={"floor": "flags", "floor2": "relay", "water": "water", "bridge": "bridge", "lift": "plate",
            "doorway": "flags", "door": "flags", "stairs": "flags", "path": "flags"},
    default="flags",
    walls={"wall": WallStyle(face=FACE_ARCHES, cap="cap", face_h=2),
           "cliff": WallStyle(face=FACE_CASTLE_MOSS, cap="cap", face_h=2)},
    props={"pillar": PILLAR, "pipe": PIPE_V, "rubble": RUBBLE_S + RUBBLE_2 + FALLEN_COL, "machine": RUNE_STUBS + [MECH_PLATE],
           "crystal": [CRYSTALS[2], CRYSTALS[1]], "vent": [GRATE_PLATE], "altar": [st("dungeon", "3", 4, 14, 1, 2)],
           "crate": IRON_CRATES + CRATES[:2], "barrel": BARRELS[:4]},
    decals=[COBWEB] + BONES_F[:2] + PEBBLES[:2], decal_density=0.03,
    wall_decor=["torch_wall"] + LEVERS[:2], decor_every=5,
    water_anim={"water": "water_deep"},
)
SKIN.dress_wall = IRON_CRATES + PIPE_VG + LEVERS + RUNE_STUBS[:2] + BARRELS[:2] + PILLAR_BROKEN
SKIN.dress_open = PILLAR_BROKEN + RUBBLE_S + [RUNE_STONES[0], RUNE_STONES[2]]
SKIN.dress_target = 0.08
SKIN.dress_kind = "machine"
