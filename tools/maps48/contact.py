"""Numbered contact sheets of catalog objects (for choosing art). Usage: contact.py <catalog stem> [sheet ...]"""
import os, sys, json
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
OUT = os.path.join(os.path.dirname(REPO), "Claude outputs", "tmp", "cat")


def render(stem, sheets=None, scale=1):
    cat = json.load(open(os.path.join(HERE, "catalog", stem + ".json")))
    os.makedirs(OUT, exist_ok=True)
    outs = []
    for name, objs in cat["sheets"].items():
        if sheets and name[:-4] not in sheets and name not in sheets:
            continue
        im = Image.open(os.path.join(ASSETS, "CuteSCKR", cat["pack"], name)).convert("RGBA")
        bg = Image.new("RGBA", im.size, (70, 74, 96, 255))
        for y in range(0, im.height, 48):
            for x in range(0, im.width, 48):
                if (x // 48 + y // 48) % 2:
                    bg.paste((80, 84, 108, 255), (x, y, x + 48, y + 48))
        bg.alpha_composite(im)
        if scale != 1:
            bg = bg.resize((bg.width * scale, bg.height * scale), Image.NEAREST)
        d = ImageDraw.Draw(bg)
        for i, o in enumerate(objs):
            x, y, w, h = [v * scale for v in o["px"]]
            d.rectangle([x, y, x + w - 1, y + h - 1], outline=(255, 60, 200, 255))
            t = str(i)
            d.rectangle([x, y, x + 6 * len(t) + 2, y + 10], fill=(0, 0, 0, 255))
            d.text((x + 1, y), t, fill=(255, 255, 0, 255))
        fn = os.path.join(OUT, "%s_%s.png" % (stem, name[:-4].replace("/", "_")))
        bg.convert("RGB").save(fn)
        outs.append(fn)
    return outs


if __name__ == "__main__":
    for f in render(sys.argv[1], sys.argv[2:] or None):
        print(f)
