"""Shared cold-region pieces (Skyspine / Whitebone / Cradle of Winter): procedural snow, ice and sky swatches.
No CuteSCKR pack has snow, ice or open sky, so these are generated here as seamless textured swatches (flat colour
+ pixel noise, quantised to a few tones so they sit with the pixel art) and registered in kit's sheet cache under the
pseudo sheets ("dreamy", "gen_snow" | "gen_ice" | "gen_sky" | "gen_snowstone"). They are only used for ground
materials, which are baked into <ID>_ground.png, so no sheet file is ever needed at runtime."""
import numpy as np
from PIL import Image
import kit
from kit import Mat, st


def _pnoise(n, cells, rng):
    """Seamless (periodic) smooth value noise, n x n, `cells` lattice cells per side."""
    g = rng.random((cells, cells))
    t = np.arange(n) * cells / n
    i0 = t.astype(int)
    f = t - i0
    f = f * f * (3 - 2 * f)
    i1 = (i0 + 1) % cells
    a = g[i0][:, i0]
    b = g[i0][:, i1]
    c = g[i1][:, i0]
    d = g[i1][:, i1]
    fy = f[:, None]
    fx = f[None, :]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def _fbm(n, rng, octaves=((4, 0.55), (8, 0.28), (16, 0.12), (48, 0.05))):
    out = np.zeros((n, n))
    for cells, w in octaves:
        out += _pnoise(n, cells, rng) * w
    return (out - out.min()) / max(1e-6, out.max() - out.min())


def _ramp(v, colors):
    """Map v in [0,1] onto a list of colours in discrete bands (pixel-art quantisation)."""
    k = len(colors)
    idx = np.clip((v * k).astype(int), 0, k - 1)
    pal = np.array(colors, dtype=np.uint8)
    return pal[idx]


def _img(rgb):
    a = np.full(rgb.shape[:2] + (1,), 255, np.uint8)
    return Image.fromarray(np.concatenate([rgb, a], axis=2), "RGBA")


def make_snow(n=384, seed=11):
    rng = np.random.default_rng(seed)
    v = _fbm(n, rng, ((4, 0.25), (8, 0.3), (24, 0.28), (64, 0.17)))
    rgb = _ramp(v, [(212, 222, 238), (224, 232, 245), (234, 240, 250), (243, 247, 253)])
    s = rng.random((n, n))
    rgb[(s < 0.006) & (v > 0.45)] = (255, 255, 255)
    rgb[(s > 0.997) & (v < 0.5)] = (190, 202, 224)
    return _img(rgb)


def make_snowstone(n=192, seed=5):
    """Packed snow over pale flagstones (courtyards): stone joints show through in the thin places."""
    rng = np.random.default_rng(seed)
    v = _fbm(n, rng)
    rgb = _ramp(v, [(200, 210, 226), (216, 225, 239), (230, 237, 247), (242, 246, 252)])
    yy, xx = np.mgrid[0:n, 0:n]
    joint = ((yy % 48) == 0) | (((xx + (yy // 48) * 24) % 48) == 0)
    thin = v < 0.42
    rgb[joint & thin] = (160, 170, 188)
    return _img(rgb)


def make_ice(n=192, seed=23):
    rng = np.random.default_rng(seed)
    v = _fbm(n, rng, ((3, 0.5), (6, 0.3), (32, 0.2)))
    rgb = _ramp(v, [(150, 200, 228), (164, 211, 235), (178, 222, 242), (194, 232, 247)])
    yy, xx = np.mgrid[0:n, 0:n]
    # diagonal sheen streaks (periodic in the swatch so it tiles)
    d = (xx + yy) % 64
    rgb[(d == 0) & (v > 0.35)] = (214, 240, 250)
    rgb[(d == 1) & (v > 0.55)] = (232, 248, 254)
    rgb[((xx - yy) % 96 == 40) & (v > 0.6)] = (214, 240, 250)
    # a few hairline cracks
    for _ in range(5):
        x, y = rng.integers(0, n, 2)
        dx, dy = rng.normal(0, 1, 2)
        for _ in range(int(rng.integers(25, 55))):
            dx, dy = dx + rng.normal(0, 0.35), dy + rng.normal(0, 0.35)
            l = max(1e-6, (dx * dx + dy * dy) ** 0.5)
            dx, dy = dx / l, dy / l
            x, y = (x + dx) % n, (y + dy) % n
            rgb[int(y), int(x)] = (116, 164, 204)
    s = rng.random((n, n))
    rgb[(s < 0.0015)] = (250, 254, 255)
    return _img(rgb)


# cloud sprites from the Dreamy World pack (sheet 6), composited translucent into the sky swatch


def make_sky(n=768, seed=7):
    rng = np.random.default_rng(seed)
    v = _fbm(n, rng, ((2, 0.5), (4, 0.3), (16, 0.2)))
    rgb = _ramp(v, [(50, 94, 160), (56, 101, 167), (62, 108, 174)])
    s = rng.random((n, n))
    rgb[s < 0.0012] = (120, 160, 210)
    img = _img(rgb)
    try:
        sheet = kit.sheet_img("dreamy", "6")
    except Exception:
        return img
    big = Image.new("RGBA", (2 * n, 2 * n), (0, 0, 0, 0))
    spots = [((0, 0, 6, 4), 40, 90), ((0, 12, 4, 2), 420, 20), ((0, 14, 4, 2), 330, 400), ((0, 4, 4, 2), 60, 560),
             ((4, 12, 2, 2), 600, 250), ((0, 6, 2, 2), 250, 300), ((2, 6, 2, 2), 640, 620), ((4, 14, 2, 2), 520, 520)]
    for (c, r, w, h), x, y in spots:
        big.alpha_composite(sheet.crop((c * 48, r * 48, (c + w) * 48, (r + h) * 48)), (x, y))
    layer = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    for qx in (0, n):
        for qy in (0, n):
            layer.alpha_composite(big.crop((qx, qy, qx + n, qy + n)))
    la = np.array(layer).astype(np.float32)
    la[..., 3] *= 0.38                      # distant: half transparent, cool tint
    la[..., :3] = la[..., :3] * np.array([0.86, 0.9, 1.0])
    base = np.array(img).astype(np.float32)
    al = la[..., 3:4] / 255.0
    base[..., :3] = base[..., :3] * (1 - al) + la[..., :3] * al
    return Image.fromarray(base.astype(np.uint8), "RGBA")


def make_frost(alias, sheet, rect, tint=(196, 220, 244), amount=0.3):
    """A pack swatch washed with pale frost blue (frozen flagstones)."""
    x, y, w, h = rect
    a = np.array(kit.sheet_img(alias, sheet).crop((x, y, x + w, y + h)).convert("RGBA")).astype(np.float32)
    a[..., :3] = a[..., :3] * (1 - amount) + np.array(tint, np.float32) * amount
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def make_drifts(seed=31):
    """Sheet of snow-drift decals (transparent background): row 0 = eight 48x48 patches, row 1 = four 96x48."""
    rng = np.random.default_rng(seed)
    sheet = np.zeros((96, 768, 4), np.uint8)
    snow = np.array(make_snow(192, seed))[..., :3]

    def patch(w, h, fill):
        v = _pnoise(max(w, h), 6, rng)[:h, :w] * 0.6 + _pnoise(max(w, h), 16, rng)[:h, :w] * 0.4
        yy, xx = np.mgrid[0:h, 0:w]
        cx, cy = w / 2 + rng.uniform(-4, 4), h / 2 + rng.uniform(-3, 3)
        d = ((xx - cx) / (w * 0.46)) ** 2 + ((yy - cy) / (h * 0.42)) ** 2
        f = v * 0.9 + (1 - d) * fill
        m = f > 0.75                 # packed core
        e = (f > 0.62) & ~m          # thin dusting around it
        out = np.zeros((h, w, 4), np.uint8)
        col = (snow[:h, :w].astype(np.float32) * 0.94).astype(np.uint8)
        out[m, :3] = col[m]
        out[m, 3] = 215
        dots = e & (rng.random((h, w)) < 0.45)
        out[dots, :3] = col[dots]
        out[dots, 3] = 120
        below = np.zeros_like(m)
        below[1:] = m[:-1] & ~m[1:]
        out[below, :3] = (150, 160, 182)
        out[below, 3] = 150
        return out
    for i in range(8):
        sheet[0:48, i * 48:(i + 1) * 48] = patch(48, 48, rng.uniform(0.55, 0.9))
    for i in range(4):
        sheet[48:96, i * 96:(i + 1) * 96] = patch(96, 48, rng.uniform(0.6, 0.9))
    return Image.fromarray(sheet, "RGBA")


_GEN = {"gen_snow": make_snow, "gen_ice": make_ice, "gen_sky": make_sky, "gen_snowstone": make_snowstone}
for _k, _f in _GEN.items():
    kit._img_cache.setdefault(("dreamy", _k), _f())
_FLAGS = ("dungeon", "4", (0, 576, 336, 96))
kit._img_cache.setdefault(("dreamy", "gen_froststone"), make_frost(*_FLAGS, amount=0.34))
kit._img_cache.setdefault(("dreamy", "gen_drifts"), make_drifts())

SNOW = Mat([("dreamy", "gen_snow", 0, 0, 384, 384)], "snow", organic=True, prio=4)
SNOW_STONE = Mat([("dreamy", "gen_snowstone", 0, 0, 192, 192)], "floor", organic=True, prio=3)
ICE = Mat([("dreamy", "gen_ice", 0, 0, 192, 192)], "ice", organic=True, prio=2)
SKY = Mat([("dreamy", "gen_sky", 0, 0, 768, 768)], "void", organic=True, prio=0)
SNOW_CAP = Mat([("dreamy", "gen_snow", 0, 0, 192, 192)], "wall")
FROST_STONE = Mat([("dreamy", "gen_froststone", 0, 0, 336, 96)], "floor", organic=True, prio=1)
FLAGS = Mat([("dungeon", "4", 0, 576, 336, 96)], "floor", organic=True, prio=1)
# flat snow-drift decals (baked into the ground) for stone floors in the snow
DRIFTS = [st("dreamy", "gen_drifts", i, 0, flat=True) for i in range(8)] + \
         [st("dreamy", "gen_drifts", 2 * i, 1, 2, 1, flat=True) for i in range(4)]
