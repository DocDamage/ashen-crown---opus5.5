"""Cut-out cleanup for sprite sheets: removes stray specks left from background removal and the light halo pixels
that hug the outline (leftovers of a pale background). Works per frame so neighbours never merge.
Usage: python3 cutclean.py vestiges vehicles [--dry]   (targets under game/assets/ext; see TARGETS)"""
import glob, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "game", "assets", "ext")


def clean_frame(f):
    a = f[..., 3] > 0
    if not a.any():
        return f, 0
    lab, n = ndimage.label(a, structure=np.ones((3, 3)))
    sizes = ndimage.sum(a, lab, range(1, n + 1))
    big = sizes.max()
    main_mask = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= big * 0.02])
    near = ndimage.binary_dilation(main_mask, iterations=2)
    keep = main_mask.copy()
    for i, s in enumerate(sizes, start=1):
        comp = lab == i
        if s >= 12 or (s >= 3 and (comp & near).any()):
            keep |= comp
    removed = int(a.sum() - keep.sum())
    g = f.copy()
    g[~keep] = 0
    # halo: outline pixels much lighter and greyer than the interior next to them
    a = keep
    edge = a & ~ndimage.binary_erosion(a)
    inner = a & ~edge
    rgb = g[..., :3].astype(np.float32)
    lum = rgb.mean(axis=2)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    k = np.ones((5, 5), np.float32)
    s_in = ndimage.convolve(lum * inner, k, mode="constant")
    c_in = ndimage.convolve(inner.astype(np.float32), k, mode="constant")
    mean_in = np.where(c_in > 0, s_in / np.maximum(c_in, 1), 0)
    halo = edge & (c_in > 2) & (lum - mean_in > 55) & (sat < 40)
    g[halo] = 0
    return g, removed + int(halo.sum())


def clean_sheet(png, cells):
    im = np.array(Image.open(png).convert("RGBA"))
    total = 0
    for (x, y, w, h) in cells:
        fr, n = clean_frame(im[y:y + h, x:x + w])
        im[y:y + h, x:x + w] = fr
        total += n
    return im, total


def targets(kind):
    if kind == "vestiges":
        for j in sorted(glob.glob(os.path.join(EXT, "vestiges", "V*.json"))):
            m = json.load(open(j))
            cw, ch = m["cell"]
            yield j[:-5] + ".png", [(f[0], f[1], cw, ch) for f in m["frames"]]
    elif kind == "vehicles":
        for j in sorted(glob.glob(os.path.join(EXT, "vehicles", "*.json"))):
            m = json.load(open(j))
            cw, ch = m["cell"]
            yield j[:-5] + ".png", [(c * cw, r * ch, cw, ch) for (r, n) in m["dirs"].values() for c in range(n)]
    elif kind == "npcs":
        for j in sorted(glob.glob(os.path.join(EXT, "npcs", "*", "field.json"))):
            m = json.load(open(j))
            cw, ch = m["cell"]
            n = m["rows"]["down"]["n"] + 1
            yield j[:-5] + ".png", [(c * cw, r * ch, cw, ch) for r in range(4) for c in range(n)]
    elif kind == "enemies":
        for j in sorted(glob.glob(os.path.join(EXT, "enemies", "*.json"))):
            m = json.load(open(j))
            if "cell" not in m:
                continue
            cw, ch = m["cell"]
            yield j[:-5] + ".png", [(c * cw, 0, cw, ch) for c in range(m["frames"])]


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    for kind in [a for a in sys.argv[1:] if not a.startswith("--")]:
        tot = 0
        for png, cells in targets(kind):
            im, n = clean_sheet(png, cells)
            tot += n
            if not dry and n:
                Image.fromarray(im).save(png)
        print(kind, "pixels removed:", tot)
