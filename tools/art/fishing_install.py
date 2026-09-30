"""Installs the Mana Seed "Fishing Gear 2.0" pack (Seliel the Shaper, owner-licensed) for the fishing minigame (sys s4).
Source: $ASHEN_ASSETS/Fishing/*.zip (the owner's folder: F:\\Ashen Crown\\The Ashen Crown\\Assets\\Fishing), or a zip or
folder given on the command line. Target: game/assets/ext/fishing/ (git-ignored licensed art), with stable names:
  icons.png        fishing icons 16x16 (8 per row; cell n = the pack's "Fishing Gear icon reference.txt" numbering)
  bobber.png       fishing anim 32x32 (4 frames: bobber on the water)
  objects.png, objects_16x32.png, objects_32x32.png, objects_32x48.png   props (racks, barrels, trophies, posts)
  school_<variant>.png   school-of-fish ripples, 32x32 x 4 frames (autumn, black, desert_v1, ..., winter)
  readme.txt, reference.txt   the pack's readme and icon reference (licence note)
The game draws clean fallbacks (drawn bobber, ripples, letter icons) when these files are missing.
After installing, run a Godot import once:  cd game && godot --headless --path . --import
Usage: python3 tools/art/fishing_install.py [ZIP_OR_DIR]"""
import glob, io, os, re, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
OUT = os.path.join(REPO, "game", "assets", "ext", "fishing")


def target(name):
    base = os.path.basename(name)
    low = base.lower()
    if low.endswith("readme.txt"):
        return "readme.txt"
    if low.startswith("fishing gear icon reference"):
        return "reference.txt"
    if not low.endswith(".png"):
        return None
    if low.startswith("fishing icons"):
        return "icons.png"
    if low.startswith("fishing anim"):
        return "bobber.png"
    if low.startswith("fishing objects"):
        m = re.search(r"(\d+x\d+)", low)
        return "objects_%s.png" % m.group(1) if m else "objects.png"
    if low.startswith("school of fish"):
        m = re.match(r"school of fish, (.+?) 32x32\.png", low)
        if m:
            return "school_%s.png" % re.sub(r"[^a-z0-9]+", "_", m.group(1)).strip("_")
    return None


def install_zip(zp):
    n = 0
    with zipfile.ZipFile(zp) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            t = target(info.filename)
            if t is None:
                continue
            os.makedirs(OUT, exist_ok=True)
            with open(os.path.join(OUT, t), "wb") as f:
                f.write(z.read(info))
            n += 1
    return n


def install_dir(d):
    n = 0
    for fp in glob.glob(os.path.join(d, "**", "*"), recursive=True):
        t = target(fp) if os.path.isfile(fp) else None
        if t:
            os.makedirs(OUT, exist_ok=True)
            with open(fp, "rb") as src, open(os.path.join(OUT, t), "wb") as dst:
                dst.write(src.read())
            n += 1
    return n


def main():
    srcs = sys.argv[1:] or sorted(glob.glob(os.path.join(ASSETS, "Fishing", "*.zip")))
    if not srcs:
        print("fishing_install: no pack found under", os.path.join(ASSETS, "Fishing"), "(set ASHEN_ASSETS)")
        return 1
    n = 0
    for s in srcs:
        n += install_zip(s) if s.lower().endswith(".zip") else install_dir(s)
    print("fishing_install:", n, "files ->", OUT)
    return 0 if n else 1


if __name__ == "__main__":
    sys.exit(main())
