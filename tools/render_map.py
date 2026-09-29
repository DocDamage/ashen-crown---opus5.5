"""Offline map preview (authoring aid): renders compiled maps with the generated tilesets plus entity markers.
The runtime renderer adds autotiling, Y-sorted actors and lighting; this is only for composition review."""
import json, os, sys
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(ROOT, "game", "content", "content.json")))
K = json.load(open(os.path.join(ROOT, "game", "assets", "tiles", "kinds.json")))
KIND_ROW = {k: i for i, k in enumerate(K["kinds"])}
PROP_COL = {k: i for i, k in enumerate(K["props"])}
COL = {"npc": (255, 220, 60), "chest": (200, 120, 40), "switch": (80, 200, 255), "save": (120, 255, 120), "trigger": (255, 80, 200),
       "exit": (255, 255, 255), "door": (255, 255, 255), "read": (180, 180, 255), "shop": (255, 160, 0), "inn": (160, 255, 200)}


def render(mid, out):
    m = C["maps"][mid]
    atlas = Image.open(os.path.join(ROOT, "game", "assets", "tiles", m["tileset"] + ".png")).convert("RGBA")
    props = Image.open(os.path.join(ROOT, "game", "assets", "tiles", m["tileset"] + "_props.png")).convert("RGBA")
    img = Image.new("RGBA", (m["w"] * 16, m["h"] * 16), (0, 0, 0, 255))
    for y, row in enumerate(m["grid"]):
        for x, ch in enumerate(row):
            k = m["legend"].get(ch, "void")
            if k in PROP_COL:
                base = "floor"
                img.paste(atlas.crop((0, KIND_ROW[base] * 16, 16, KIND_ROW[base] * 16 + 16)), (x * 16, y * 16))
                pc = PROP_COL[k]
                pr = props.crop((pc * 16, 16, pc * 16 + 16, 32))
                img.alpha_composite(pr, (x * 16, y * 16))
            elif k in KIND_ROW:
                v = (x * 7 + y * 13) % 4
                img.paste(atlas.crop((v * 16, KIND_ROW[k] * 16, v * 16 + 16, KIND_ROW[k] * 16 + 16)), (x * 16, y * 16))
    d = ImageDraw.Draw(img)
    for e in m["entities"]:
        c = COL.get(e["type"])
        if not c:
            continue
        if "x" in e:
            d.rectangle([e["x"] * 16 + 4, e["y"] * 16 + 4, e["x"] * 16 + 11, e["y"] * 16 + 11], outline=c, width=2)
        elif "x1" in e:
            d.rectangle([e["x1"] * 16, e["y1"] * 16, e["x2"] * 16 + 15, e["y2"] * 16 + 15], outline=c, width=1)
    img.save(out)


if __name__ == "__main__":
    os.makedirs("/tmp/qa/maps", exist_ok=True)
    for mid in sys.argv[1:]:
        render(mid, f"/tmp/qa/maps/{mid}.png")
    print("rendered", len(sys.argv) - 1)
