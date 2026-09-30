"""Quick preview of built map art without Godot: ground + objects (y-sorted) + first animation frames.
Usage: preview.py MAP_ID [...] [--half] [--out DIR]  -> <DIR>/<MAP_ID>.png (default Claude outputs/tmp/prev)"""
import os, sys, json
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EXT = os.path.join(REPO, "game", "assets", "ext")


def preview(mid, half=False):
    d = json.load(open(os.path.join(EXT, "maps48", mid + ".json")))
    img = Image.open(os.path.join(EXT, "maps48", d["ground"])).convert("RGBA")
    sheets = [Image.open(os.path.join(EXT, s)).convert("RGBA") for s in d["sheets"]]
    items = [(o[7], "o", o) for o in d["objects"]] + [(a[3], "a", a) for a in d["anims"]]
    for _, t, o in sorted(items, key=lambda x: x[0]):
        if t == "o":
            s = sheets[o[0]].crop((o[1], o[2], o[1] + o[3], o[2] + o[4]))
            img.alpha_composite(s, (int(o[5]), int(o[6])))
        else:
            mp = os.path.join(EXT, "field_anim", o[0] + ".json")
            if os.path.exists(mp):
                m = json.load(open(mp))
                fr = Image.open(os.path.join(EXT, "field_anim", o[0] + ".png")).convert("RGBA").crop((0, 0, m["cell"][0], m["cell"][1]))
                img.alpha_composite(fr, (int(o[1]), int(o[2])))
    if d.get("over"):
        img.alpha_composite(Image.open(os.path.join(EXT, "maps48", d["over"])).convert("RGBA"))
    if half:
        img = img.resize((img.width // 2, img.height // 2), Image.BOX)
    return img


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = os.path.join(os.path.dirname(REPO), "Claude outputs", "tmp", "prev")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
        args = [a for a in args if a != out]
    os.makedirs(out, exist_ok=True)
    for mid in args:
        p = os.path.join(out, mid + ".png")
        preview(mid, "--half" in sys.argv).convert("RGB").save(p)
        print(p)
