"""CuteSCKR object catalog: splits each 768x768 sheet (16x16 cells of 48px, 1 art px = 1 screen px) into objects.

Two neighbouring non-empty cells belong to the same object when opaque pixels continue across their shared edge
(at least MIN_TOUCH pixel pairs). Each object gets its cell rectangle, pixel bounding box and a few measurements;
tags are added by hand in tags/<pack>.json (see tag.py). Output: catalog/<pack>.json
Usage: python tools/maps48/catalog.py "<pack folder name>" [...]   (default: the region packs)
"""
import os, sys, json, glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
CUTE = os.path.join(ASSETS, "CuteSCKR")
OUT = os.path.join(HERE, "catalog")
C = 48
MIN_TOUCH = 3

REGION_PACKS = [
    "Medieval Fantasy Town Pixel Art Tileset Pack", "Medieval Castle Fantasy - Pixel Art Tileset",
    "Medieval Siege & Castle Tileset", "Steampunk Pixel Art Tileset", "Pirate Age Pixel Tileset Pack",
    "Viking Age Pixel Art Tileset Pack", "Roman Empire Pixel Art Tileset", "Medieval Army Camp Tileset Pack",
    "Underwater World & Sunken Ruins Pixel Art Tileset", "Forest Wilderness Pixel Art Tileset Pack",
    "Medieval Fantasy Dungeon & Prison Pixel Art Tileset Pack", "Haunted Mansion Pixel Art Tileset Pack",
    "Medieval Plague Town Tileset", "Medieval Battlefield & Ruins Pixel Art Tileset Pack", "Desert Wasteland Pixel Tileset",
    "Farm Tileset - Pixel Art", "Survival Island Pixel Art Tileset", "Rainforest Survival Pixel Art Tileset Pack",
    "Dark Gothic City Pixel Art Tileset Pack", "Factory Ruins Pixel Art Tileset Pack", "Dreamy World Pixel Art Tileset Pack",
]


def sheet_objects(path):
    a = np.array(Image.open(path).convert("RGBA"))
    H, W = a.shape[:2]
    op = a[..., 3] > 0
    if op.mean() > 0.97:
        # opaque sheet: the colour filling the corners is the background
        corners = [tuple(a[0, 0]), tuple(a[0, -1]), tuple(a[-1, 0]), tuple(a[-1, -1])]
        bg = max(set(corners), key=corners.count)
        op = ~np.all(a == np.array(bg, dtype=a.dtype), axis=-1)
    nr, nc = H // C, W // C
    filled = np.zeros((nr, nc), bool)
    for r in range(nr):
        for c in range(nc):
            filled[r, c] = op[r * C:(r + 1) * C, c * C:(c + 1) * C].sum() > 6
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)
    for r in range(nr):
        for c in range(nc):
            if not filled[r, c]:
                continue
            find((r, c))
            if c + 1 < nc and filled[r, c + 1]:
                e1 = op[r * C:(r + 1) * C, (c + 1) * C - 1]
                e2 = op[r * C:(r + 1) * C, (c + 1) * C]
                if (e1 & e2).sum() >= MIN_TOUCH:
                    union((r, c), (r, c + 1))
            if r + 1 < nr and filled[r + 1, c]:
                e1 = op[(r + 1) * C - 1, c * C:(c + 1) * C]
                e2 = op[(r + 1) * C, c * C:(c + 1) * C]
                if (e1 & e2).sum() >= MIN_TOUCH:
                    union((r, c), (r + 1, c))
    groups = {}
    for r in range(nr):
        for c in range(nc):
            if filled[r, c]:
                groups.setdefault(find((r, c)), []).append((r, c))
    objs = []
    for cells in groups.values():
        rs = [x[0] for x in cells]
        cs = [x[1] for x in cells]
        r0, r1, c0, c1 = min(rs), max(rs), min(cs), max(cs)
        sub = op[r0 * C:(r1 + 1) * C, c0 * C:(c1 + 1) * C]
        ys, xs = np.nonzero(sub)
        full = sub.mean()
        objs.append({"cells": [c0, r0, c1 - c0 + 1, r1 - r0 + 1],
                     "px": [int(c0 * C + xs.min()), int(r0 * C + ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)],
                     "n": len(cells), "fill": round(float(full), 2),
                     "solid_rect": bool(full > 0.97 and len(cells) == (r1 - r0 + 1) * (c1 - c0 + 1))})
    objs.sort(key=lambda o: (o["cells"][1], o["cells"][0]))
    return objs


def main():
    packs = sys.argv[1:] or REGION_PACKS
    os.makedirs(OUT, exist_ok=True)
    tot = 0
    for p in packs:
        pdir = os.path.join(CUTE, p)
        sheets = sorted(glob.glob(os.path.join(pdir, "**", "*.png"), recursive=True),
                        key=lambda f: (os.path.dirname(f), int(os.path.basename(f)[:-4]) if os.path.basename(f)[:-4].isdigit() else 999))
        cat = {"pack": p, "sheets": {}}
        for s in sheets:
            name = os.path.relpath(s, pdir).replace(os.sep, "/")
            if Image.open(s).size != (768, 768):
                continue
            objs = sheet_objects(s)
            for i, o in enumerate(objs):
                o["id"] = "%s:%d" % (name[:-4], i)
            cat["sheets"][name] = objs
            tot += len(objs)
        json.dump(cat, open(os.path.join(OUT, p.split(" Pixel")[0].split(" -")[0].split(" Tileset")[0].replace(" ", "_").replace("&", "and") + ".json"), "w"), indent=0)
        print(p, sum(len(v) for v in cat["sheets"].values()), "objects in", len(sheets), "sheets")
    print("total", tot)


if __name__ == "__main__":
    main()
