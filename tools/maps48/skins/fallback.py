"""Fallback art for grid kinds a skin does not cover (the expansion places use many kinds in every tileset).

augment(skin, tileset) fills the gaps in place:
  * walls: house/roof/chimney/window/door (and cliff) from a donor town skin of the same region mood;
  * props: missing prop kinds from the donor town skin, then from EXTRA_PROPS (generic dungeon/town stamps);
  * ground: missing ground kinds from the donor's ground, then from FALLBACK_GROUND.
Nothing already in the skin is replaced, so hand-tuned skins keep their look."""
import copy
import kit
from kit import st, Mat
from skins import common as K

kit.PACKS.setdefault("winlu", "Winlu Fantasy Overworld/tilesets")

DONOR = {"conduit": "town_r02", "crown": "capital", "emberdeep": "town_r02", "furnace": "town_r02", "grove": "town_r01",
         "grove_flood": "town_r01", "harbor": "town_r03", "hollow": "town_r02", "interior": "town_r01",
         "interior_stone": "capital", "lattice": "capital", "quarry": "town_r02", "reef": "town_r03", "sky": "town_r04",
         "underways": "town_r02", "vault": "capital", "whitebone": "town_r04", "winter": "town_r04", "archive": "town_r03",
         "ship": "town_r03"}

LAVA = Mat([("winlu", "Fantasy_World_A1", 8 * 48 + 24, 3 * 48 + 48, 48, 48)], "lava")
HOLE = Mat([("color", (8, 6, 12))], "hole")


def _ground_table():
    from skins import lib_cold as LC
    return {
        "bone": K.DUNG_DIRT, "cave": K.DUNG_STONE, "cave_floor": K.DUNG_STONE, "crystal_floor": K.DUNG_GLASS,
        "rocky": K.DUNG_COBBLE, "ruin": K.FLAGS, "ruin_floor": K.FLAGS, "ember": K.DUNG_DIRT, "ash": K.DUNG_DIRT,
        "lava": LAVA, "hole": HOLE, "ice": LC.ICE, "snow": LC.SNOW, "moss": K.MOSS, "roots": K.ROOTS,
        "puddle": K.SHALLOW, "shallow": K.SHALLOW, "pool": K.SHALLOW, "water": K.WATER, "deep": K.WATER,
        "grass": K.GRASS, "path": K.DIRT, "road": K.COBBLE, "sand": K.DIRT, "salt": K.SLABS, "dock": K.PLANKS,
        "bridge": K.PLANKS, "ladder": K.PLANKS, "lift": K.PLANKS, "stairs": K.SLABS, "floor": K.FLAGS,
        "floor2": K.DUNG_MOSSY, "awning": K.DIRT, "doorway": K.FLAGS, "door": K.FLAGS, "carpet": K.WOOD_RED,
        "grate": Mat([("steam", "3", 0, 480, 192, 96)], "grate"), "cliff_top": K.GRASS, "rail": K.DUNG_COBBLE,
        "chest_deco": K.FLAGS,
    }


def _extra_props():
    PILLAR = st("roman", "6", 0, 0, 1, 3)
    TENTS = [st("camp", "2", c, 4, 2, 2) for c in (0, 2, 4)]
    return {
        "bed": [K.BED, K.BED2, K.BED3], "shelf": [K.BOOKSHELF, K.CUPBOARD, K.CUPBOARD2, K.SHELF_LOW],
        "book": [K.BOOKSHELF, K.BOOKS], "brazier": [K.TORCH_STAND, K.CANDLES], "banner": [K.BANNER],
        "chain": [st("dungeon", "6", 12, 8, 1, 2), st("dungeon", "6", 13, 8, 1, 2)], "gate": [st("dungeon", "4", 6, 0, 2, 2)],
        "lever_deco": [K.RUNESTONE, K.RUNESTONE2], "mast": [PILLAR], "shelter": TENTS, "tent": TENTS,
        "sluice": [st("castle", "1", 6, 8, 2, 2, hgrid=2)], "vine": [K.BUSHES[0], K.BUSHES[1]], "block": [K.CRATE_IRON],
        "lantern_post": [K.TORCH_STAND], "lamp": [K.TORCH_STAND, K.LANTERN], "arch": [PILLAR], "crystal_tall": [K.CRYSTAL],
        "crystal": [K.CRYSTAL], "statue": [K.STATUE, K.STATUE2], "pillar": [PILLAR], "table": [K.TABLE_1, K.SMALL_TABLE],
        "counter": [K.COUNTER2, K.COUNTER4], "bench": [K.BENCH2, K.BENCH2B], "anvil": [K.ANVIL, K.FORGE],
        "altar": [K.ALTAR, K.PEDESTAL], "crate": [K.CRATE, K.CRATE2], "barrel": [K.BARREL, K.BARREL2],
        "rubble": [K.RUBBLE, K.RUBBLE2, K.RUBBLE_BIG], "rock": [K.ROCK, K.ROCK2, K.ROCK3], "mural": [K.TAPESTRY, K.TAPESTRY2],
        "machine": [K.FORGE], "gear": [st("steam", "4", 0, 4, 2, 2)], "wheel": [st("steam", "4", 0, 4, 2, 2)],
        "pipe": [st("steam", "5", 13, 7, 1, 3)], "pipe_tall": [st("steam", "5", 13, 7, 1, 3)],
        "vent": [st("aship", "tile-B-06", 8, 3, 1, 1)], "bell": [st("pirate", "B1-1", 10, 8, 1, 1)],
        "sign": [K.RUNESTONE], "fence": [st("town", "1", 14, 8, 2, 1)], "hedge": K.BUSHES, "garden": K.BUSHES,
        "flower": K.BUSHES[:2], "cart": [K.SACK, K.POT], "chest_deco": [K.CHEST],
        "cable": [st("pirate", "B1-1", 9, 8, 1, 1)],
    }


HOUSE_KINDS = ("house", "roof", "chimney", "window", "door")


def augment(skin, tileset, used=None):
    """used: optional set of kinds the maps actually use (only those are filled)."""
    from autoskin import WallStyle, load_skin
    donor = None
    dn = DONOR.get(tileset)
    if dn and dn != tileset:
        try:
            donor = load_skin(dn)
        except Exception:
            donor = None
    need = lambda k: (used is None or k in used) and k not in skin.ground and k not in skin.walls and k not in skin.props

    def take_mat(name):
        key = "fb_" + name
        if key not in skin.mats:
            skin.mats[key] = donor.mats[name]
        return key
    # walls from the donor (houses in caves, cliffs everywhere)
    if donor is not None:
        for k in HOUSE_KINDS + ("cliff", "wall"):
            if need(k) and k in donor.walls:
                ws = donor.walls[k]
                skin.walls[k] = WallStyle(face=ws.face, cap=take_mat(ws.cap), face_h=ws.face_h)
        for k in ("window", "door", "chimney"):
            if k in donor.props and k not in skin.props and (used is None or k in used):
                skin.props[k] = donor.props[k]
    if need("cliff") and "wall" in skin.walls:
        skin.walls["cliff"] = skin.walls["wall"]
    # props: donor first, then generic
    extra = _extra_props()
    for k in set(extra) | (set(donor.props) if donor is not None else set()):
        if not need(k):
            continue
        if donor is not None and k in donor.props and donor.props[k]:
            skin.props[k] = donor.props[k]
        elif extra.get(k):
            skin.props[k] = extra[k]
    # ground
    table = _ground_table()
    for k, mat in table.items():
        if not need(k):
            continue
        if donor is not None and k in donor.ground:
            skin.ground[k] = take_mat(donor.ground[k])
        else:
            key = "fb_k_" + k
            skin.mats.setdefault(key, mat)
            skin.ground[k] = key
    return skin


def clone(skin):
    """A shallow copy with its own dicts (so an alias skin can be augmented without touching the original)."""
    s = copy.copy(skin)
    s.mats, s.ground, s.walls, s.props = dict(skin.mats), dict(skin.ground), dict(skin.walls), dict(skin.props)
    return s
