"""Hero importer (overhaul step 3): turns the owner's hero packs into game-ready sheets.

Reads tools/art/hero_cast.json and, for each cast id, writes to game/assets/ext/heroes/<cid>/ (git-ignored,
licensed art):
  field.png + field.json   4-direction field sheet. Rows down/left/right/up; column 0 = standing still,
                           columns 1..n = walk cycle. East/west walks come from the pack's walk clip; north/south
                           from the pack's own 4-direction walk when it has one, else built from the rotation
                           stills (walk_from_rotations.front_walk), as the owner agreed.
  battle.png + battle.json one strip per battle animation (idle, attack, cast, ult, hurt, death, victory, guard,
                           step), all on one cell size, facing west (south-only clips play facing the camera,
                           as FF6 victory poses do). Frames keep their pack alignment (canvas centres match).
  portrait.png             head-and-shoulders crop of the south rotation, 30px square x4 = 120px.
Usage: python tools/art/hero_import.py [--assets <Assets dir>] [C01 C02 ...]
"""
import json, os, sys, glob, re
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from walk_from_rotations import front_walk  # noqa: E402

ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
OUT = os.path.join(REPO, "game", "assets", "ext", "heroes")
ROLES = ["idle", "attack", "cast", "ult", "hurt", "death", "victory", "guard", "step"]
MAX_FRAMES = 17
FPS = {"idle": 8, "attack": 14, "cast": 12, "ult": 12, "hurt": 12, "death": 10, "victory": 10, "guard": 10, "step": 14}
LOOP = {"idle": True, "victory": True, "guard": True, "step": True}


def pack_root(folder, proc):
    base = os.path.join(ASSETS, "_processed" if proc else "", "heroes", folder) if proc else os.path.join(ASSETS, "heroes", folder)
    for d, subs, _ in os.walk(base):
        if "animations" in subs:
            return d
    raise SystemExit("no animations under " + base)


def rot_dir(folder, proc):
    for root in ([pack_root(folder, True)] if proc else []) + [pack_root(folder, False)]:
        r = os.path.join(root, "rotations")
        if os.path.isdir(r):
            return r, (root != pack_root(folder, False) if proc else False)
    return None, False


def clip_dir(root, folder, spec):
    if spec.startswith("gap:"):
        d = os.path.join(ASSETS, "_processed", "heroes_battle_gaps", folder, spec[4:] + "_generated")
        return d if os.path.isdir(d) else None
    anims = os.path.join(root, "animations")
    names = sorted(os.listdir(anims))
    if spec.startswith("id:"):
        key = spec[3:]
        hits = [n for n in names if n.endswith(key) or key in n]
    else:
        hits = [n for n in names if n == spec or n.rsplit("-", 1)[0] == spec]
    return os.path.join(anims, hits[0]) if hits else None


def frames_of(cdir, prefer=("west", "south")):
    if cdir is None:
        return [], None
    dirs = sorted(d for d in os.listdir(cdir) if os.path.isdir(os.path.join(cdir, d)))
    for p in prefer:
        for d in dirs:
            if d == p or d.startswith(p + "-"):
                fs = sorted(glob.glob(os.path.join(cdir, d, "*.png")))
                if fs:
                    return [Image.open(f).convert("RGBA") for f in fs], p
    return [], None


def snap(im):
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    return Image.fromarray(a)


def bbox(im):
    a = np.array(im)[..., 3]
    ys, xs = np.nonzero(a)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def sample(fr, n):
    if len(fr) <= n:
        return fr
    idx = [round(i * (len(fr) - 1) / (n - 1)) for i in range(n)]
    return [fr[i] for i in idx]


def synth_death(hurt):
    """KO built from the hurt clip: the recoil frames, then the last hurt frame laid on its back."""
    last = hurt[-1]
    bb = bbox(last)
    body = last.crop(bb)
    lying = body.rotate(90, expand=True)
    ko = Image.new("RGBA", last.size, (0, 0, 0, 0))
    x = (last.width - lying.width) // 2 + 6
    y = bb[3] - lying.height
    ko.alpha_composite(lying, (max(0, x), max(0, y)))
    return hurt + [ko, ko]


def build(cid, cfg):
    folder = cfg["folder"]
    proc = cfg.get("proc", False)
    root = pack_root(folder, proc)
    out = os.path.join(OUT, cid)
    os.makedirs(out, exist_ok=True)
    report = {}
    # ---------------- battle ----------------
    clips = {}
    for role in ROLES:
        spec = cfg.get(role)
        if not spec:
            continue
        if spec == "synth":
            continue
        fr, d = frames_of(clip_dir(root, folder, spec))
        if not fr:
            report[role] = "MISSING " + spec
            continue
        clips[role] = (sample([snap(f) for f in fr], MAX_FRAMES), d)
        report[role] = "%s %s x%d" % (spec, d, len(fr))
    if cfg.get("death") == "synth" and "hurt" in clips:
        clips["death"] = (synth_death(clips["hurt"][0]), clips["hurt"][1])
        report["death"] = "synth from hurt"
    # align by canvas centre; union bbox
    boxes = []
    for role, (fr, _) in clips.items():
        for f in fr:
            b = bbox(f)
            if b:
                cx, cy = f.width / 2, f.height / 2
                boxes.append((b[0] - cx, b[1] - cy, b[2] - cx, b[3] - cy))
    x0 = int(np.floor(min(b[0] for b in boxes))) - 1
    y0 = int(np.floor(min(b[1] for b in boxes))) - 1
    x1 = int(np.ceil(max(b[2] for b in boxes))) + 1
    y1 = int(np.ceil(max(b[3] for b in boxes))) + 1
    cw, chh = x1 - x0, y1 - y0
    idle0 = clips["idle"][0][0]
    ib = bbox(idle0)
    foot = [int(round((ib[0] + ib[2]) / 2 - idle0.width / 2 - x0)), int(round(ib[3] - idle0.height / 2 - y0))]
    order = [r for r in ROLES if r in clips]
    ncol = max(len(clips[r][0]) for r in order)
    sheet = Image.new("RGBA", (cw * ncol, chh * len(order)), (0, 0, 0, 0))
    meta = {"cell": [cw, chh], "foot": foot, "anims": {}}
    for row, role in enumerate(order):
        fr, d = clips[role]
        for i, f in enumerate(fr):
            px = int(round(i * cw + (-x0 - f.width / 2)))
            py = int(round(row * chh + (-y0 - f.height / 2)))
            sheet.alpha_composite(f, (px + 0, py + 0)) if px >= 0 and py >= 0 else sheet.paste(f, (px, py), f)
        meta["anims"][role] = {"row": row, "n": len(fr), "fps": FPS[role], "loop": LOOP.get(role, False), "facing": d}
    sheet.save(os.path.join(out, "battle.png"))
    json.dump(meta, open(os.path.join(out, "battle.json"), "w"), indent=1)
    # ---------------- field ----------------
    rdir, rot_is_proc = rot_dir(folder, proc)
    scale = 1.2 if (proc and cid == "C04" and not rot_is_proc) else 1.0
    def rot(name):
        im = snap(Image.open(os.path.join(rdir, name + ".png")).convert("RGBA"))
        if scale != 1.0:
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.NEAREST)
        return im
    wdir = clip_dir(root, folder, cfg["walk"])
    rows = {}
    for d4, src in (("left", "west"), ("right", "east")):
        fr, _ = frames_of(wdir, (src,))
        if not fr:
            fr, _ = frames_of(wdir, ("west",))
            if src == "east":
                fr = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in fr]
        rows[d4] = [rot(src)] + sample([snap(f) for f in fr], 8)
    for d4, src in (("down", "south"), ("up", "north")):
        fr = []
        if cfg.get("walk4"):
            fr, _ = frames_of(wdir, (src,))
            fr = sample([snap(f) for f in fr], 8)
        if not fr:
            fr = [snap(f) for f in front_walk(rot(src))]
        rows[d4] = [rot(src)] + fr
    # align by feet (bbox bottom) and canvas centre x
    fboxes = []
    for d4, fr in rows.items():
        for f in fr:
            b = bbox(f)
            fboxes.append((b[0] - f.width / 2, b[1] - b[3], b[2] - f.width / 2, 0))
    fx0 = int(np.floor(min(b[0] for b in fboxes))) - 1
    fx1 = int(np.ceil(max(b[2] for b in fboxes))) + 1
    fh = int(max(-b[1] for b in fboxes)) + 2
    fw = fx1 - fx0
    order4 = ["down", "left", "right", "up"]
    fcol = max(len(rows[d]) for d in order4)
    fsheet = Image.new("RGBA", (fw * fcol, fh * 4), (0, 0, 0, 0))
    fmeta = {"cell": [fw, fh], "foot": [-fx0, fh - 1], "rows": {}}
    for r, d4 in enumerate(order4):
        for i, f in enumerate(rows[d4]):
            b = bbox(f)
            px = int(round(i * fw - fx0 - f.width / 2))
            py = int(round(r * fh + fh - 1 - b[3]))
            fsheet.paste(f, (px, py), f)
        fmeta["rows"][d4] = {"row": r, "n": len(rows[d4]) - 1}
    fmeta["fps"] = 10
    fsheet.save(os.path.join(out, "field.png"))
    json.dump(fmeta, open(os.path.join(out, "field.json"), "w"), indent=1)
    # ---------------- portrait ----------------
    s = rot("south")
    b = bbox(s)
    side = 30
    a = np.array(s)[..., 3]
    top = a[b[1]:b[1] + side, :]
    xs = np.nonzero(top.sum(axis=0))[0]
    cx = int((xs.min() + xs.max()) / 2) if len(xs) else (b[0] + b[2]) // 2
    crop = s.crop((cx - side // 2, b[1] - 1, cx - side // 2 + side, b[1] - 1 + side))
    crop.resize((side * 4, side * 4), Image.NEAREST).save(os.path.join(out, "portrait.png"))
    report["field"] = "%dx%d cells, %s" % (fw, fh, {d: len(rows[d]) - 1 for d in order4})
    report["battle"] = "%dx%d cells, foot %s" % (cw, chh, foot)
    return report


def main():
    cast = json.load(open(os.path.join(HERE, "hero_cast.json")))
    ids = [a for a in sys.argv[1:] if a.startswith("C")] or [k for k in cast if k.startswith("C")]
    for cid in ids:
        rep = build(cid, cast[cid])
        print(cid, json.dumps(rep))


if __name__ == "__main__":
    main()
