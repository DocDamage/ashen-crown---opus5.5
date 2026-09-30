"""Item icons for the systems-s2 items (tools/content/gear2.py, crafting.py): run after tools/art/icons.py.

Each s2 item has `icon` (a cell after the base atlas) and `icon_base` (an existing item whose icon it reuses). This
appends rows to game/assets/ext/sprites/icons_11.png and icons_24.png and paints each new cell with the base item's
icon, hue-shifted by a stable per-item amount so tiers and named pieces read apart. No pack files are needed.
Usage: python3 tools/art/icons_gear2.py
"""
import colorsys, json, os, zlib
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def shift(im, dh, ds=0.0, dv=0.0):
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            h = (h + dh) % 1.0
            s = min(1.0, max(0.0, s + ds))
            v = min(1.0, max(0.0, v + dv))
            r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
            px[x, y] = (int(r2 * 255), int(g2 * 255), int(b2 * 255), a)
    return im


def main():
    items = json.load(open(os.path.join(ROOT, "game", "content", "content.json"), encoding="utf-8"))["items"]
    new = {k: v for k, v in items.items() if "icon_base" in v}
    top = max(int(v["icon"]) for v in items.values())
    rows = top // 32 + 1
    for px in (11, 24):
        path = os.path.join(ROOT, "game", "assets", "ext", "sprites", "icons_%d.png" % px)
        if not os.path.exists(path):
            print("missing", path)
            continue
        base = Image.open(path).convert("RGBA")
        out = Image.new("RGBA", (32 * px, rows * px), (0, 0, 0, 0))
        out.paste(base.crop((0, 0, base.size[0], min(base.size[1], rows * px))), (0, 0))
        for iid, it in sorted(new.items()):
            b = items.get(it["icon_base"])
            if b is None:
                continue
            bi = int(b["icon"])
            if (bi // 32 + 1) * px > base.size[1]:
                continue
            cell = base.crop(((bi % 32) * px, (bi // 32) * px, (bi % 32) * px + px, (bi // 32) * px + px))
            hsh = zlib.crc32(iid.encode())
            named = it.get("named", False)
            dh = ((hsh % 11) - 5) / 30.0 if not named else 0.5 + ((hsh % 7) - 3) / 40.0
            cell = shift(cell, dh, 0.15 if named else 0.0, 0.05 if named else 0.0)
            i = int(it["icon"])
            out.paste(cell, ((i % 32) * px, (i // 32) * px))
        out.save(path)
        print("icons_%d.png" % px, out.size, "cells", len(new))


if __name__ == "__main__":
    main()
