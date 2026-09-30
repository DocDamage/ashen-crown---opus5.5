"""Enemy art v2, step 1 of 3: cut each enemy's source art out of the owner's packs (crop to content, flip) and write
Assets/_processed/enemies_v2/src/<id>.png plus manifest.json. Step 2 is the Aseprite job made by enemy_job.py
(resize, palette-reduce to hard-edged pixel art, build idle/attack/cast/hurt frames). Step 3 (install_overhaul.py
enemies) copies the results into game/assets/ext/enemies."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import install_overhaul as IO
from enemy_roster import ROSTER   # id -> (source code, height units, flip)

OUT = os.path.join(IO.PROC, "enemies_v2")


def main(ids=None):
    os.makedirs(os.path.join(OUT, "src"), exist_ok=True)
    man = {}
    for eid, (code, h_units, flip) in ROSTER.items():
        if ids and eid not in ids:
            continue
        im = IO._enemy_source(code).convert("RGBA")
        a = im.getchannel("A")
        bb = a.point(lambda v: 255 if v > 24 else 0).getbbox()
        im = im.crop(bb)
        if flip:
            im = im.transpose(0)   # FLIP_LEFT_RIGHT
        im.save(os.path.join(OUT, "src", eid + ".png"))
        th = h_units * 3
        tw = round(im.width * th / im.height)
        mw = IO.MAX_W["B" if eid.startswith(("B", "X", "SB")) else "E"] * 3
        if tw > mw:
            th, tw = round(th * mw / tw), mw
        painted = code.startswith("M")
        man[eid] = {"src": code, "w": tw, "h": th, "painted": painted, "colors": 40 if painted else 64,
                    "method": "bilinear" if (painted or tw < im.width * 0.5) else "rotsprite"}
    old = {}
    mp = os.path.join(OUT, "manifest.json")
    if os.path.exists(mp):
        old = json.load(open(mp))
    old.update(man)
    json.dump(old, open(mp, "w"), indent=1)
    print("prepared", len(man))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
