"""Starless Reef (D12_R01..R06): a dark undersea reef - silt-grey seabed paths between open water, coral and kelp
banks, moorings on old planking, lantern beacons, wrecked boats, a drowned wreck library and a black trench."""
from autoskin import Skin, WallStyle
from skins.common import VOID
from skins.lib_nature import WATER, EMPTY3, EMPTY1, spread
from kit import st, Mat

SEABED = Mat([("sea", "4", 216, 72, 96, 48), ("sea", "4", 240, 96, 96, 48)], "floor2", organic=True, prio=2)
ABYSS = Mat([("sea", "3", 96, 192, 96, 96)], "deep", organic=True, prio=0)
DOCK = Mat([("pirate", "B4", 0, 0, 144, 192)], "dock", prio=3)
DECK = Mat([("pirate", "B1-1", 0, 0, 144, 144)], "floor", prio=3)
RUIN_TILE = Mat([("sea", "4", 384, 96, 192, 96)], "wall")

CORAL_1 = [st("sea", "1", 8, 0), st("sea", "1", 10, 5), st("sea", "1", 11, 5), st("sea", "1", 12, 5), st("sea", "1", 13, 5),
           st("sea", "1", 14, 5), st("sea", "1", 15, 5), st("sea", "1", 13, 6), st("sea", "1", 14, 6)]
CORAL_2 = [st("sea", "5", 0, 0, 2, 2, hgrid=2), st("sea", "5", 2, 0, 2, 2, hgrid=2), st("sea", "5", 4, 0, 2, 2, hgrid=2),
           st("sea", "5", 6, 0, 2, 2, hgrid=2), st("sea", "5", 0, 2, 2, 2, hgrid=2), st("sea", "5", 4, 2, 2, 2, hgrid=2),
           st("sea", "1", 8, 3, 2, 2, hgrid=2)]
KELP = [st("sea", "1", 6, 3, 1, 2), st("sea", "1", 5, 3, 1, 2), st("sea", "1", 7, 3, 1, 2), st("sea", "3", 6, 4, 1, 2),
        st("sea", "6", 0, 0, 1, 2), st("sea", "6", 2, 0, 1, 2)]
ROCK_1 = [st("sea", "5", 8, 10), st("sea", "5", 9, 10), st("sea", "5", 10, 10), st("sea", "5", 11, 10), st("sea", "5", 9, 11)]
ROCK_2 = [st("sea", "6", 12, 0, 2, 2, hgrid=2), st("sea", "6", 14, 0, 2, 2, hgrid=2), st("sea", "5", 4, 4, 2, 2, hgrid=2),
          st("sea", "5", 8, 0, 2, 2, hgrid=2)]
REEF_BANK = st("sea", "1", 9, 6, 3, 2)
BOATS = [st("sea", "2", 0, 14, 2, 2), st("sea", "4", 12, 10, 2, 2), st("sea", "4", 10, 12, 2, 2)]
BEACON = [st("castle", "7", 14, 6, 1, 2), st("pirate", "B1-1", 14, 14)]
CRATES = [st("pirate", "B1-1", 6, 12), st("pirate", "B1-1", 7, 12), st("pirate", "B1-1", 6, 13)]
SHELVES = [st("castle", "6", 6, 8, 2, 2), st("castle", "6", 8, 8, 2, 2), st("castle", "6", 5, 8, 1, 2)]
RUBBLE = [st("sea", "5", 8, 11), st("sea", "5", 10, 11), st("sea", "1", 13, 13), st("sea", "5", 11, 11)]
SHELLS = [st("sea", "1", 0, 8, flat=True), st("sea", "1", 1, 8, flat=True), st("sea", "1", 0, 9, flat=True),
          st("sea", "1", 1, 9, flat=True), st("sea", "1", 7, 13, flat=True),
          st("sea", "1", 9, 13, flat=True), st("sea", "4", 12, 4, flat=True)]
BONES = [st("sea", "4", 12, 9, flat=True), st("sea", "4", 13, 9, flat=True), st("sea", "2", 5, 12, flat=True)]

SKIN = Skin(
    mats=dict(void=VOID, seabed=SEABED, abyss=ABYSS, water=WATER, dock=DOCK, deck=DECK, ruin=RUIN_TILE),
    ground={"floor2": "seabed", "floor": "deck", "dock": "dock", "water": "water", "deep": "abyss"},
    default="seabed",
    walls={"wall": WallStyle(face=("sea", "4", 384, 0, 192, 96), cap="ruin", face_h=2)},
    props={"reef": CORAL_1 + CORAL_2 + KELP[:4] + ROCK_1[:2], "rock": ROCK_1 + ROCK_2, "boat": BOATS, "lamp": BEACON, "crate": CRATES,
           "shelf": SHELVES, "rubble": RUBBLE,
           "water": spread([REEF_BANK, EMPTY3, REEF_BANK]) + [EMPTY1] * 7 + KELP + CORAL_1[:4] + ROCK_1[:2],
           "deep": spread([ROCK_2[0], EMPTY3, ROCK_2[2]], n=47) + [EMPTY1] * 9 + ROCK_1[:3] + KELP[4:]},
    decals=SHELLS + BONES, decal_density=0.05,
    water_anim={"water": "water_deep"},
)
SKIN.dress_wall = KELP + CORAL_1 + ROCK_1
SKIN.dress_open = KELP + CORAL_1 + ROCK_1 + CORAL_2[:3]
SKIN.dress_target = 0.09
SKIN.dress_kind = "reef"
