"""Grid-labelled views of CuteSCKR sheets (cells of 48px, columns/rows 0-15) for choosing stamps by cell rectangle.
Usage: gridsheet.py <pack folder> [sheet names...] -> Claude outputs/tmp/grid/<pack>_<sheet>.png"""
import os, sys, glob
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
OUT = os.path.join(os.path.dirname(REPO), "Claude outputs", "tmp", "grid")
M = 16


def render(pack, names=None):
    pdir = os.path.join(ASSETS, "CuteSCKR", pack)
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(pdir, "**", "*.png"), recursive=True))
    outs = []
    for f in files:
        n = os.path.relpath(f, pdir)[:-4].replace(os.sep, "/")
        if names and n not in names:
            continue
        im = Image.open(f).convert("RGBA")
        W, H = im.size
        bg = Image.new("RGBA", (W + M, H + M), (20, 20, 28, 255))
        tile = Image.new("RGBA", (W, H), (70, 74, 96, 255))
        for y in range(0, H, 48):
            for x in range(0, W, 48):
                if (x // 48 + y // 48) % 2:
                    tile.paste((86, 90, 116, 255), (x, y, x + 48, y + 48))
        tile.alpha_composite(im)
        bg.paste(tile, (M, M))
        d = ImageDraw.Draw(bg)
        for i in range(W // 48):
            d.text((M + i * 48 + 18, 2), str(i), fill=(255, 230, 0, 255))
        for j in range(H // 48):
            d.text((1, M + j * 48 + 18), str(j), fill=(255, 230, 0, 255))
        slug = "".join(w[:4] for w in pack.replace("&", "").replace("-", " ").split()[:4])
        fn = os.path.join(OUT, "%s_%s.png" % (slug, n.replace("/", "_").replace(" ", "")))
        bg.convert("RGB").save(fn)
        outs.append(fn)
    return outs


if __name__ == "__main__":
    for o in render(sys.argv[1], sys.argv[2:] or None):
        print(os.path.basename(o))
