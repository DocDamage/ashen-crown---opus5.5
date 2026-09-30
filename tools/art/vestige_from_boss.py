"""Vestiges V13-V24 (superboss rewards): the tamed spirit of each superboss, built from its battle art.

Base = frame 0 of assets/ext/enemies/<SBxx>.png (the Aseprite-processed boss strip), fitted into 256 px, washed
toward the Vestige's element colour and lifted (a spirit, not the living boss); then the same appear / idle / vanish
frame builders as V01-V08 (vestige_kit). Writes Assets/_processed/vestiges/<art>.png/.json in the Aseprite sheet
format install_overhaul.vestiges() reads.  Usage: python3 tools/art/vestige_from_boss.py"""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import install_overhaul as IO
from vestige_kit import idle_frames, appear_frames, vanish_frames

ELEM = {"fire": ((255, 120, 50), (255, 220, 150)), "water": ((70, 180, 230), (200, 245, 255)),
        "storm": ((170, 180, 255), (235, 240, 255)), "earth": ((200, 150, 90), (255, 230, 180)),
        "light": ((255, 235, 150), (255, 255, 235)), "shadow": ((150, 90, 220), (225, 195, 255)),
        "ice": ((150, 215, 255), (240, 250, 255)), "none": ((200, 200, 210), (255, 255, 255)),
        "poison": ((150, 220, 90), (225, 255, 190))}


def base_of(sb, elem):
    meta = json.load(open(os.path.join(IO.EXT, "enemies", sb + ".json")))
    cw, ch = meta["cell"]
    im = Image.open(os.path.join(IO.EXT, "enemies", sb + ".png")).convert("RGBA").crop((0, 0, cw, ch))
    im = im.crop(im.getbbox())
    s = min(1.0, 256.0 / max(im.width, im.height))
    if s < 1.0:
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.BOX)
    a = np.array(im).astype(np.float32)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    tint = np.array(ELEM.get(elem, ELEM["none"])[1], np.float32)
    a[..., :3] = np.clip(a[..., :3] * 0.72 + tint * 0.28 + 10, 0, 255)
    return a.astype(np.uint8)


def main():
    content = json.load(open(os.path.join(IO.REPO, "game", "content", "content.json"), encoding="utf-8"))
    out = os.path.join(IO.PROC, "vestiges")
    os.makedirs(out, exist_ok=True)
    n = 0
    for vid in sorted(content["vestiges"]):
        v = content["vestiges"][vid]
        src = str(v.get("source", ""))
        if not src.startswith("SB") or not os.path.exists(os.path.join(IO.EXT, "enemies", src + ".png")):
            continue
        au, mo = ELEM.get(v.get("element", "none"), ELEM["none"])
        base = base_of(src, v.get("element", "none"))
        idle = idle_frames(base, 8, au, mo, seed=int(vid[1:]))
        ap = appear_frames(idle[0], 8, edge=np.array((255, 255, 255), np.uint8), glow=np.array(mo, np.uint8))
        va = vanish_frames(idle[0], 6, col=np.array(mo, np.uint8))
        frames = ap + idle + va
        fw, fh = frames[0].shape[1], frames[0].shape[0]
        sheet = Image.new("RGBA", (fw * len(frames), fh), (0, 0, 0, 0))
        for i, f in enumerate(frames):
            sheet.paste(Image.fromarray(f, "RGBA"), (i * fw, 0))
        art = v.get("art", vid)
        sheet.save(os.path.join(out, art + ".png"))
        durs = [70] * len(ap) + [120] * len(idle) + [80] * len(va)
        meta = {"frames": [{"filename": "%s %d.aseprite" % (art, i), "frame": {"x": i * fw, "y": 0, "w": fw, "h": fh},
                            "duration": durs[i]} for i in range(len(frames))],
                "meta": {"frameTags": [{"name": "appear", "from": 0, "to": len(ap) - 1},
                                       {"name": "idle", "from": len(ap), "to": len(ap) + len(idle) - 1},
                                       {"name": "vanish", "from": len(ap) + len(idle), "to": len(frames) - 1}]}}
        json.dump(meta, open(os.path.join(out, art + ".json"), "w"))
        n += 1
        print(vid, art, fw, fh)
    print("vestige_from_boss:", n)


if __name__ == "__main__":
    main()
