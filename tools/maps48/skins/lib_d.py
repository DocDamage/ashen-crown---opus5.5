"""Shared pieces for the crown / vault / harbor / ship skins and the town fallbacks (lib_d).

Adds pack aliases to kit.PACKS at import time, a tinted material (a swatch with its colours multiplied, used to
darken or recolour ground without scaling it) and helpers for the processed land objects (single 128px files)."""
import os
import numpy as np
from PIL import Image
import kit
from kit import st, Mat, Stamp, C

for _a, _p in {
    "infect": "CuteSCKR/Infected Spaceship Interior Horror Tileset Pack",
    "lab": "CuteSCKR/Modern Laboratory Pixel Art Tileset Pack",
    "scifi": "CuteSCKR/Sci-Fi Spaceship Interior Tileset Pack",
    "aship": "Airships/flying boat",
}.items():
    kit.PACKS.setdefault(_a, _p)


class TintMat(Mat):
    """Mat whose swatches are multiplied by mul=(r, g, b) (0..1.5) and then offset by add=(r, g, b)."""

    def __init__(self, sources, kind, mul=(1, 1, 1), add=(0, 0, 0), **kw):
        Mat.__init__(self, sources, kind, **kw)
        self.mul, self.add = mul, add

    def texture(self):
        if self._tex is None:
            tiles = Mat.texture(self)
            out = []
            for t in tiles:
                t = t.copy()
                rgb = t[..., :3].astype(np.float32) * np.array(self.mul, dtype=np.float32) + np.array(self.add, dtype=np.float32)
                t[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
                out.append(t)
            self._tex = out
        return self._tex


def obj(alias, sheet, **kw):
    """Stamp for a single-object file (processed land objects): the opaque bounding box, widened to whole cells
    where the file allows, bottom on the object's foot."""
    im = Image.open(kit.sheet_path(alias, sheet)).convert("RGBA")
    x0, y0, x1, y1 = im.getbbox()
    bw, bh = x1 - x0, y1 - y0
    W = max(C, int(round(bw / C)) * C)
    W = max(W, bw)
    W = min(W, im.width)
    cx = (x0 + x1) // 2
    nx = min(max(0, cx - W // 2), im.width - W)
    H = max(C, -(-bh // C) * C)
    ny = max(0, y1 - H)
    H = y1 - ny
    return Stamp(alias, sheet, 0, 0, px=(nx, ny, W, H), **kw)


def cur(name, n=1, **kw):
    """Cursed land object, shadow variant n (1 or 2)."""
    parts = name.rsplit("_", 1)
    fn = "%s_shadow%d_%s" % (parts[0], n, parts[1]) if len(parts) == 2 and parts[1].isdigit() else "%s_shadow%d" % (name, n)
    return obj("cursed", fn, **kw)


def flat1(stamp):
    """One-cell-high flat copy of an object stamp (for decals): the bottom 48 px, baked into the ground."""
    x, y, w, h = stamp.px
    if h > C:
        y, h = y + h - C, C
    return Stamp(stamp.alias, stamp.sheet, 0, 0, px=(x, y, w, h), solid=0, flat=True)


# ------------------------------------------------------------------------------------------------ town fallback kit
class RailMat(Mat):
    """Railway ground: kit.RailStamp (sleepers and steel) composited over a gravel/ground swatch."""

    def __init__(self, base, kind="rail"):
        Mat.__init__(self, [base], kind)

    def texture(self):
        if self._tex is None:
            (al, sh, x, y, w, h) = self.sources[0]
            g = kit.sheet_img(al, sh).crop((x, y, x + C, y + C)).convert("RGBA")
            g.alpha_composite(kit.RailStamp().image())
            self._tex = [np.array(g)]
        return self._tex


def town_skin(r):
    """Builds a town fallback Skin from a region dict r (see skins/town_r01.py). Houses are drawn from their grid:
    roof cells get the roof material, house/window/door/chimney cells a facade strip, then window/door/chimney
    stamps on top; everything else is ground + props."""
    from autoskin import Skin, WallStyle
    import lib_r01 as T
    from skins import common as K
    mats = dict(r["mats"])
    mats.setdefault("rail", RailMat(r.get("rail_base", ("town", "2", 192, 48, 48, 48))))
    g = {"path": "path", "floor": "floor", "floor2": "floor", "grass": "grass", "water": "water", "shallow": "water",
         "deep": "water", "dock": "dock", "bridge": "dock", "stairs": "stairs", "doorway": "floor", "ladder": "dock",
         "awning": "path", "salt": "salt", "pool": "pool", "sand": "path", "snow": "path", "rail": "rail",
         "carpet": "floor", "boat": "water", "cliff_top": "grass", "chest_deco": "path"}
    fb = {"salt": "path", "pool": "water", "dock": "path", "stairs": "path", "grass": "path", "floor": "path"}
    ground = {k: (v if v in mats else fb.get(v, "path")) for k, v in g.items()}
    ground.update(r.get("ground", {}))
    for k in list(ground):
        if ground[k] not in mats:
            del ground[k]
    face = r["house_face"]
    house = WallStyle(face=face, cap="facade", face_h=1)
    roof = WallStyle(face=r.get("eave", r["roof_src"]), cap="roof", face_h=1)
    walls = {"wall": WallStyle(face=r["wall_face"], cap="wallcap", face_h=2),
             "cliff": WallStyle(face=r.get("cliff_face", r["wall_face"]), cap=r.get("cliff_cap", "wallcap"), face_h=2),
             "roof": roof, "chimney": roof, "house": house, "window": house, "door": house}
    props = {
        "window": r["windows"], "door": r["doors"], "chimney": r["chimneys"],
        "counter": r.get("counters", [st("town", "2", c, 5, 2, 1) for c in (0, 2, 4, 6, 8)] + [st("town", "2", 10, 4, 1, 1)]),
        "awning": r.get("awnings", [st("town", "2", c, 4, 2, 1, solid=0) for c in (0, 2, 4, 6, 8)]),
        "lamp": r["lamps"], "garden": r.get("gardens", [T.VEG_PLOTS] + K.BUSHES),
        "flower": r.get("flowers", T.FLOWER_BUSH), "laundry": r.get("laundry", [st("island", "4", 11, 4, 2, 2), st("island", "4", 10, 12, 2, 2)]),
        "statue": r.get("statues", T.STATUES), "bench": r.get("benches", [T.BENCH, T.BENCH2, T.STONE_BENCH, K.STOOL]),
        "crate": r.get("crates", [T.CRATE, T.CRATE_S, T.CRATE_STACK]), "barrel": r.get("barrels", [T.BARREL] + T.POTS),
        "cart": r.get("carts", [T.CART, T.CART2, T.HANDCART]), "tent": r.get("tents", [st("camp", "2", c, 4, 2, 2) for c in (0, 2, 4, 8, 12)] + [st("camp", "2", 3, 8, 1, 1)]),
        "bell": r.get("bells", [st("pirate", "B1-1", 10, 8, 1, 1)]), "well": r.get("wells", [T.WELL, T.WELL2, T.FOUNTAIN]),
        "wheel": r.get("wheels", [st("steam", "4", 0, 4, 2, 2), st("steam", "4", 0, 6, 1, 1)]),
        "gear": r.get("gears", [st("steam", "4", 0, 4, 2, 2), st("steam", "4", 2, 4, 1, 1)]),
        "cable": r.get("cables", [st("pirate", "B1-1", 9, 8, 1, 1)]),
        "pipe_tall": r.get("pipes", [st("steam", "5", 13, 7, 1, 3)]), "pipe": r.get("pipes", [st("steam", "5", 13, 7, 1, 3)]),
        "vent": r.get("vents", [st("aship", "tile-B-06", 8, 3, 1, 1)]), "anvil": r.get("anvils", [K.ANVIL, K.FORGE]),
        "rubble": r.get("rubble", [K.RUBBLE, K.RUBBLE2, K.RUBBLE_BIG]), "mural": r.get("murals", [K.TAPESTRY, K.TAPESTRY2]),
        "altar": r.get("altars", [K.ALTAR]), "crystal": r.get("crystals", [st("castle", "4", c, 5, 1, 1) for c in (12, 13, 14, 15)]),
        "machine": r.get("machines", [K.FORGE, st("town", "5", 10, 4, 2, 2)]), "sign": r.get("signs", [T.SIGNPOST, T.SIGNPOST2, T.NOTICE, T.SIGN_S]),
        "fence": r.get("fences", [st("town", "1", 14, 8, 2, 1), st("town", "1", 14, 9, 2, 1)]),
        "hedge": r.get("hedges", T.BUSHES), "table": r.get("tables", [K.TABLE_2x2, K.TABLE_1, st("camp", "5", 6, 2, 2, 2)]),
        "pillar": r.get("pillars", [st("roman", "6", c, 0, 1, 3) for c in (0, 1, 2)]),
        "boat": r.get("boats", [st("viking", "1 (1)", 0, 0, px=(578, 528, 122, 48)), st("viking", "1 (1)", 0, 0, px=(576, 576, 124, 48))]),
        "chest_deco": r.get("chests", [K.CHEST]), "rock": r.get("rocks", T.ROCKS), "salt_rock": r.get("crystals", []),
    }
    props.update(r.get("props", {}))
    sk = Skin(mats=mats, ground=ground, default=r.get("default", "path"), walls=walls, props=props,
              trees=r["trees"], decals=r.get("decals", T.GRASS_TUFTS), decal_density=r.get("decal_density", 0.04),
              wall_decor=r.get("wall_decor", []), decor_every=r.get("decor_every", 7),
              water_anim=r.get("water_anim", {"water": "water_deep"}))
    sk.dress_wall = r.get("dress_wall", [])
    sk.dress_open = r.get("dress_open", [])
    sk.dress_target = r.get("dress_target", 0.0)
    sk.dress_kind = r.get("dress_kind", "crate")
    return sk
