"""HD-2D battle backdrops from the owner's parallax packs (Assets/Parallax).

Builds layered sets for render3d/battle_stage3d.gd into game/assets/ext/parallax/<set>/ (0.png ... + set.json),
farthest layer first. The painted layers are pixelated to the game's look: scaled to 600 px tall (the battle view is
504 px; the rest is headroom for camera moves), then reduced to a 48-colour palette without dithering, keeping alpha.
The generic/ruins zips are unpacked beside themselves the first time.

Usage (owner's PC, from the repo root): python3 tools/art/install_parallax.py
ASHEN_ASSETS overrides the Assets folder (default: the Assets folder beside the repo).
"""
import glob, json, os, sys, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
SRC = os.path.join(ASSETS, "Parallax")
OUT = os.path.join(REPO, "game", "assets", "ext", "parallax")
H = 600
COLOURS = 48

CN = "Parallax (Country side, city night, city destroyed)/parallax/"
FD = "Parallax (Forest, desert, sky, moon)/Parallax (Forest, desert, sky, moon)/parallax/"
WI = "Winter night + Arctic + Ocean parallax/Iceberg + winter night + ocean/Iceberg + winter night + ocean/"
# set -> [(file, depth 0..1 (1 = farthest), vertical offset in plane heights (+ = up))], farthest first
SETS = {
    "rural": [(CN + "rural area/ruralparallaxsky.png", 1.0, 0.0), (CN + "rural area/ruralparallaxclouds.png", 0.9, 0.05),
              (CN + "rural area/ruralparallaxmountainback2.png", 0.75, 0.0), (CN + "rural area/ruralparallaxmountainback.png", 0.6, 0.0),
              (CN + "rural area/ruralparallaxmountain.png", 0.45, 0.0), (CN + "rural area/ruralparallaxvillage.png", 0.3, 0.0),
              (CN + "rural area/ruralparallaxriver.png", 0.15, 0.0), (CN + "rural area/ruralparallaxriverfront.png", 0.02, 0.0)],
    "city_night": [(CN + "city night/parallaxcitysky.png", 1.0, 0.0), (CN + "city night/parallaxcitybackgroundmountain2.png", 0.8, 0.0),
                   (CN + "city night/parallaxcitybackgroundmountain.png", 0.65, 0.0), (CN + "city night/parallaxcitybuildings.png", 0.4, 0.0),
                   (CN + "city night/parallaxcitywater.png", 0.2, 0.0), (CN + "city night/parallaxcitywaterreflexion.png", 0.18, 0.0),
                   (CN + "city night/parallaxcityfront.png", 0.02, 0.0)],
    "city_destroyed": [(CN + "city destroyed/parallaxcitydestroyedsky.png", 1.0, 0.0),
                       (CN + "city destroyed/parallaxcitydestroyedbuildingssmoke.png", 0.7, 0.0),
                       (CN + "city destroyed/parallaxcitydestroyedbuildings.png", 0.5, 0.0),
                       (CN + "city destroyed/parallaxcitydestroyedwater.png", 0.25, 0.0),
                       (CN + "city destroyed/parallaxcitydestroyedbuildingreflexion.png", 0.24, 0.0),
                       (CN + "city destroyed/parallaxcitydestroyedfrontsmoke.png", 0.02, 0.0)],
    "forest": [(FD + "forest/forest_sky.png", 1.0, 0.0), (FD + "forest/forest_moon.png", 0.95, 0.0),
               (FD + "forest/forest_mountain.png", 0.8, 0.0), (FD + "forest/forest_back.png", 0.6, 0.0),
               (FD + "forest/forest_mid.png", 0.4, 0.0), (FD + "forest/forest_long.png", 0.2, 0.0),
               (FD + "forest/forest_short.png", 0.02, 0.0)],
    "desert": [(FD + "desert/desert_sky.png", 1.0, 0.0), (FD + "desert/desert_moon.png", 0.95, 0.0),
               (FD + "desert/desert_cloud.png", 0.85, 0.05), (FD + "desert/desert_mountain.png", 0.6, 0.0),
               (FD + "desert/desert_dunemid.png", 0.3, 0.0), (FD + "desert/desert_dunefrontt.png", 0.02, 0.0)],
    "skies": [(FD + "skies/Sky_sky.png", 1.0, 0.0), (FD + "skies/sky_moon.png", 0.95, 0.0), (FD + "skies/sky_clouds.png", 0.8, 0.0),
              (FD + "skies/Sky_back_mountain.png", 0.6, 0.0), (FD + "skies/sky_front_mountain.png", 0.4, 0.0),
              (FD + "skies/Sky_cloud_single.png", 0.3, 0.1), (FD + "skies/sky_cloud_floor_2.png", 0.15, 0.0),
              (FD + "skies/sky_cloud_floor.png", 0.05, 0.0), (FD + "skies/Sky_front_cloud.png", 0.01, 0.0)],
    "moon": [(FD + "moon/moon_sky.png", 1.0, 0.0), (FD + "moon/moon_earth.png", 0.9, 0.1), (FD + "moon/moon_back.png", 0.7, 0.0),
             (FD + "moon/moon_mid.png", 0.4, 0.0), (FD + "moon/moon_front.png", 0.15, 0.0), (FD + "moon/moon_floor.png", 0.02, 0.0)],
    "winter": [(WI + "Winternight/4-sky.png", 1.0, 0.0), (WI + "Winternight/3-backmountain.png", 0.75, 0.0),
               (WI + "Winternight/2-midmountain.png", 0.5, 0.0), (WI + "Winternight/1-midforest.png", 0.25, 0.0),
               (WI + "Winternight/0-frontfloor.png", 0.02, 0.0)],
    "ocean": [(WI + "Ocean/0 ocean sky and sun.png", 1.0, 0.0), (WI + "Ocean/3 ocean clouds.png", 0.85, 0.05),
              (WI + "Ocean/4 ocean back mountain.png", 0.7, 0.0), (WI + "Ocean/1 ocean sea.png", 0.4, 0.0),
              (WI + "Ocean/2 ocean sun light.png", 0.38, 0.0), (WI + "Ocean/6 ocean wave.png", 0.15, 0.0),
              (WI + "Ocean/5 ocean sand.png", 0.02, 0.0)],
    "arctic": [(WI + "Iceberg/1-Sky.png", 1.0, 0.0), (WI + "Iceberg/2-cloud.png", 0.85, 0.05), (WI + "Iceberg/3-mountains.png", 0.65, 0.0),
               (WI + "Iceberg/0-water.png", 0.4, 0.0), (WI + "Iceberg/2-2-water reflex back.png", 0.38, 0.0),
               (WI + "Iceberg/4-icebergreflex.png", 0.2, 0.0), (WI + "Iceberg/5-iceberg.png", 0.18, 0.0),
               (WI + "Iceberg/2-1-water reflex.png", 0.02, 0.0)],
}


def unzip_once(name):
    z = os.path.join(SRC, name)
    d = os.path.join(SRC, os.path.splitext(name)[0])
    if os.path.exists(z) and not os.path.isdir(d):
        with zipfile.ZipFile(z) as f:
            f.extractall(SRC)


def pixelate(im):
    im = im.convert("RGBA")
    w = max(1, round(im.width * H / im.height))
    im = im.resize((w, H), Image.LANCZOS)
    a = im.getchannel("A")
    rgb = im.convert("RGB").quantize(colors=COLOURS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    a = a.point(lambda v: 0 if v < 96 else 255)
    out = rgb.convert("RGBA")
    out.putalpha(a)
    return out


def main():
    if not os.path.isdir(SRC):
        print("no Parallax folder at", SRC)
        return 1
    for z in ("generic.zip", "ruins.zip"):
        unzip_once(z)
    made = 0
    for name, layers in SETS.items():
        od = os.path.join(OUT, name)
        os.makedirs(od, exist_ok=True)
        meta = []
        for i, (rel, depth, yoff) in enumerate(layers):
            p = os.path.join(SRC, rel)
            if not os.path.exists(p):
                print("  missing", rel)
                continue
            fn = "%d.png" % i
            dst = os.path.join(od, fn)
            if not os.path.exists(dst) or os.path.getmtime(p) > os.path.getmtime(dst):
                pixelate(Image.open(p)).save(dst, optimize=True)
            meta.append({"file": fn, "depth": depth, "y": yoff})
        json.dump({"layers": meta}, open(os.path.join(od, "set.json"), "w"), indent=1)
        made += 1
        print(name, len(meta), "layers")
    print("built", made, "sets into", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
