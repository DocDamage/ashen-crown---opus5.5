"""Crop every full-canvas frame (animation and effect frames) of each processed giant boss to the union of their bounds
(4px margin), so all layers stay aligned. Writes crop.json per boss with the offset removed.
Usage: python boss_crop.py <Assets/_processed/bosses>"""
import sys, os, json, glob
from PIL import Image

root = sys.argv[1]
for boss in sorted(glob.glob(os.path.join(root, '*', '*', 'Boss*'))):
    allf = [f for f in glob.glob(os.path.join(boss, '**', '*.png'), recursive=True)]
    if not allf: continue
    from collections import Counter
    size_of = {f: Image.open(f).size for f in allf}
    (w, h), _ = Counter(size_of.values()).most_common(1)[0]
    # only full-canvas frames (animation + effect frames) share the stage; part pieces and strip sheets are left as they are
    files = [f for f in allf if size_of[f] == (w, h)]
    box = None
    for f in files:
        bb = Image.open(f).convert('RGBA').getbbox()
        if bb: box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3]))
    if box is None: continue
    box = (max(0, box[0] - 4), max(0, box[1] - 4), min(w, box[2] + 4), min(h, box[3] + 4))
    for f in files:
        Image.open(f).convert('RGBA').crop(box).save(f)
    json.dump({'canvas': [w, h], 'crop': list(box), 'size': [box[2] - box[0], box[3] - box[1]], 'files': len(files)},
              open(os.path.join(boss, 'crop.json'), 'w'), indent=1)
    print(os.path.basename(boss), box[2] - box[0], 'x', box[3] - box[1], len(files))
