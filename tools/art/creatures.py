"""Creature portraits and field sprites derived from the project's own generated Vestige and boss art
(no external sources): speakers such as the Winter Hind or Null Cantor get a 3-frame 40x40 portrait strip,
and the Iron Tortoise gets a field sheet so it can be staged in the assembly yard."""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPR = os.path.join(ROOT, "game", "assets", "sprites")
PORTRAITS = {"moth": "vestiges/V01", "stag": "vestiges/V02", "whale": "vestiges/V03", "manta": "vestiges/V04",
             "fox": "vestiges/V05", "tortoise": "vestiges/V06", "hind": "vestiges/V07", "leviathan": "vestiges/V08",
             "echo": "enemies/B15", "cantor": "enemies/B16"}
FIELD = {"tortoise": "vestiges/V06", "hind": "vestiges/V07", "leviathan": "vestiges/V08"}


def _crop(src):
    im = Image.open(os.path.join(SPR, src + ".png")).convert("RGBA")
    bb = im.getbbox() or (0, 0, im.width, im.height)
    return im.crop(bb)


def _fit(im, w, h):
    s = min(w / im.width, h / im.height)
    s = 1 / round(1 / s) if s < 1 else max(1, int(s))
    nw, nh = max(1, int(im.width * s)), max(1, int(im.height * s))
    return im.resize((nw, nh), Image.NEAREST)


def build(save):
    for key, src in PORTRAITS.items():
        c = _fit(_crop(src), 38, 38)
        strip = Image.new("RGBA", (120, 40), (0, 0, 0, 0))
        for i in range(3):
            strip.paste(c, (i * 40 + (40 - c.width) // 2, 40 - c.height - 1), c)
        save(strip, f"sprites/portraits/{key}.png", "portrait", "3x 40x40 (neutral/other/other)", "", f"derived from {src}")
    for key, src in FIELD.items():
        c = _fit(_crop(src), 24, 30)
        sheet = Image.new("RGBA", (144, 160), (0, 0, 0, 0))
        for row in range(5):
            for col in range(6):
                bob = 1 if (col % 2 and row < 4) else 0
                sheet.paste(c, (col * 24 + (24 - c.width) // 2, row * 32 + 31 - c.height - bob), c)
        save(sheet, f"sprites/world/{key}.png", "world_sprite", "24x32 sheet (single creature pose)", "", f"derived from {src}")
