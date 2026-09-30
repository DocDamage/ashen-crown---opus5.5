"""Prepare Vestige sources: cutout cleanup, element recolour, re-pixelation to 256px base (shown at 2x),
1px outline. Output: out/<id>/base.png (RGBA, alpha snapped). Palette reduction happens in Aseprite."""
import os, colorsys
import numpy as np
from PIL import Image
from scipy import ndimage

SRC1 = '/home/claude/ves/cut/isnet-general-use_'
SRC2 = '/home/claude/ves/cut2/'
V = [
    # id, name, source cutout, recolour spec
    ('V01', 'Ember Moth', SRC1 + 'Fey_Pack_16_artsheet_02.png', dict(hue_map=[((230, 330), 20), ((330, 360), 12), ((0, 30), 16)], sat=1.45, val=1.18)),
    ('V02', 'Rootstag', SRC2 + 'Fey_Pack_13_artsheet_01.png', None),
    ('V03', 'Tide Serpent', SRC1 + 'Elemental_Pack_13_artsheet_02.png', None),
    ('V04', 'Sky Griffon', SRC2 + 'Beast_Pack_03_artsheet_01.png', dict(hue_map=[((0, 360), 218)], sat=0.9, val=1.0, min_sat=0.04, sat_mapped=1.7, spread=0.06)),
    ('V05', 'Lumen Fox', SRC1 + 'Fey_Pack_15_artsheet_00.png', dict(hue_map=[((0, 60), 44)], sat=0.55, val=1.25)),
    ('V06', 'Iron Tortoise', SRC1 + 'Dragon_Pack_17_artsheet_00.png', dict(hue_map=[((40, 120), 176)], sat=0.35, val=0.95)),
    ('V07', 'Winter Hind', SRC1 + 'Fey_Pack_09_artsheet_02.png', None),
    ('V08', 'Night Leviathan', SRC2 + 'Beast_Pack_09_artsheet_02.png', dict(hue_map=[((180, 260), 268)], sat=0.9, val=0.72)),
]

def clean_alpha(im):
    a = np.array(im.convert('RGBA'))
    m = a[..., 3] >= 128
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        keep = [i + 1 for i, s in enumerate(sizes) if s >= sizes.max() * 0.015]
        m = np.isin(lab, keep)
    holes = ndimage.binary_fill_holes(m) & ~m
    hl, hn = ndimage.label(holes)
    if hn:
        hs = ndimage.sum(holes, hl, range(1, hn + 1))
        small = np.isin(hl, [i + 1 for i, s in enumerate(hs) if s < 40])
        m |= small
    a[..., 3] = np.where(m, 255, 0)
    return a

def recolour(a, spec):
    if not spec: return a
    rgb = a[..., :3].astype(float) / 255
    import matplotlib.colors as mc
    hsv = mc.rgb_to_hsv(rgb)
    h = hsv[..., 0] * 360
    mapped = np.zeros(h.shape, bool)
    for (lo, hi), tgt in spec['hue_map']:
        m = (h >= lo) & (h < hi) & (hsv[..., 1] > spec.get('min_sat', 0.12))
        # keep local hue variation: offset relative to band centre, compressed
        centre = (lo + hi) / 2
        h = np.where(m, (tgt + (h - centre) * spec.get('spread', 0.35)) % 360, h)
        mapped |= m
    hsv[..., 0] = h / 360
    hsv[..., 1] = np.clip(hsv[..., 1] * spec.get('sat', 1) * np.where(mapped, spec.get('sat_mapped', 1), 1), 0, 1)
    hsv[..., 2] = np.clip(hsv[..., 2] * spec.get('val', 1), 0, 1)
    out = a.copy(); out[..., :3] = (mc.hsv_to_rgb(hsv) * 255).round().astype(np.uint8)
    return out

def repixel(a, size=256):
    """alpha-aware staged downscale 512 -> 256: premultiplied bilinear, then alpha snap."""
    im = Image.fromarray(a)
    ys, xs = np.nonzero(a[..., 3])
    pad = 6
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(a.shape[1], xs.max() + pad + 1), min(a.shape[0], ys.max() + pad + 1))
    im = im.crop(box)
    w, h = im.size
    s = size / 512
    tw, th = max(1, round(w * s)), max(1, round(h * s))
    arr = np.array(im).astype(float)
    arr[..., :3] *= arr[..., 3:4] / 255
    pre = Image.fromarray(arr.clip(0, 255).astype(np.uint8), 'RGBA')
    small = np.array(pre.resize((tw, th), Image.BILINEAR)).astype(float)
    al = small[..., 3:4]
    small[..., :3] = np.where(al > 0, small[..., :3] * 255 / np.maximum(al, 1), 0)
    small[..., 3] = np.where(small[..., 3] >= 110, 255, 0)
    return small.clip(0, 255).astype(np.uint8)

def outline(a, col=(14, 10, 20)):
    m = a[..., 3] > 0
    p = np.pad(m, 1)
    edge = (~m) & (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
    b = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    e = np.pad(edge, 1)
    b[e, :3] = col; b[e, 3] = 255
    return b

if __name__ == '__main__':
    import json
    os.makedirs('out', exist_ok=True)
    man = []
    for vid, name, src, spec in V:
        a = clean_alpha(Image.open(src))
        a = recolour(a, spec)
        s = repixel(a)
        s = outline(s)
        d = f'out/{vid}'; os.makedirs(d, exist_ok=True)
        Image.fromarray(s).save(f'{d}/base.png')
        man.append(dict(id=vid, name=name, source=os.path.basename(src).replace('isnet-general-use_', ''), size=[s.shape[1], s.shape[0]]))
        print(vid, name, s.shape)
    json.dump(man, open('out/manifest.json', 'w'), indent=1)
