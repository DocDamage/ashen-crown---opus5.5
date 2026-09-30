"""Slice the owner's airship sheets (Assets/Airships) into individual sprites.
Alpha is snapped to 0/255 (the sheets carry a faint background haze). Output: Assets/_processed/airships/_slices.
Run: python slice_airships.py <Assets folder>"""
import sys, os, json
import numpy as np, cv2
from PIL import Image

ROOT = sys.argv[1]
SRC = os.path.join(ROOT, 'Airships')
OUT = os.path.join(ROOT, '_processed', 'airships', '_slices')

def load(name):
    return np.array(Image.open(os.path.join(SRC, name)).convert('RGBA'))

def snap(a):
    a = a.copy(); keep = a[..., 3] >= 128
    a[..., 3] = np.where(keep, 255, 0); a[~keep, :3] = 0
    return a

def largest(a, dil=5, extra=0.2):
    m = (a[..., 3] >= 128).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(m, np.ones((dil, dil), np.uint8)), 8)
    if n <= 1: return a
    areas = st[1:, 4]; big = areas.max()
    keep = np.isin(lab, [i + 1 for i, s in enumerate(areas) if s >= big * extra])
    out = a.copy(); out[~(keep & (m > 0))] = 0
    return out

def trim(a, pad=2):
    ys, xs = np.nonzero(a[..., 3])
    if len(xs) == 0: return a
    y0, y1, x0, x1 = max(ys.min() - pad, 0), ys.max() + pad + 1, max(xs.min() - pad, 0), xs.max() + pad + 1
    return a[y0:y1, x0:x1]

def box(a, b, main=True):
    x, y, w, h = b
    c = snap(a[y:y + h, x:x + w])
    return trim(largest(c) if main else c)

def save(arr, group, name):
    d = os.path.join(OUT, group); os.makedirs(d, exist_ok=True)
    Image.fromarray(arr).save(os.path.join(d, name + '.png'))
    return f'{group}/{name} {arr.shape[1]}x{arr.shape[0]}'

log = []
# ---- Wayfarer ----
W = load('The Wayfarer.png')
cores = [66, 145, 224]            # the three south-facing frames (row 1, first group)
bounds = [4, (66 + 145) // 2, (145 + 224) // 2, 290]
for i in range(3):
    log.append(save(box(W, (bounds[i], 140, bounds[i + 1] - bounds[i], 215)), 'wayfarer', f'topdown_south_{i}'))
nb = [4, (65 + 145) // 2, (145 + 226) // 2, 290]
for i in range(3):
    log.append(save(box(W, (nb[i], 395, nb[i + 1] - nb[i], 210)), 'wayfarer', f'topdown_north_{i}'))
log.append(save(box(W, (13, 653, 172, 218)), 'wayfarer', 'parked_south'))
for i, b in enumerate([(4, 915, 290, 172), (288, 920, 278, 170), (560, 921, 272, 167), (830, 921, 281, 170)]):
    log.append(save(box(W, b), 'wayfarer', f'side_fly_{i}'))
log.append(save(box(W, (5, 1148, 253, 151)), 'wayfarer', 'side_damaged'))
for i, b in enumerate([(255, 1139, 224, 175), (467, 1138, 217, 161), (679, 1133, 223, 168), (892, 1124, 222, 176)]):
    log.append(save(box(W, b), 'wayfarer', f'side_burning_{i}'))

# ---- Lanternwake ----
L = load('The Second Light.png')
for i, b in enumerate([(57, 101, 93, 159), (155, 101, 94, 160), (253, 102, 94, 158), (352, 102, 94, 159)]):
    log.append(save(box(L, b), 'lanternwake', f'topdown_south_{i}'))
for i, b in enumerate([(60, 413, 91, 154), (164, 414, 91, 153), (268, 413, 91, 154), (372, 413, 91, 154)]):
    log.append(save(box(L, b), 'lanternwake', f'topdown_north_{i}'))
log.append(save(box(L, (31, 774, 121, 205)), 'lanternwake', 'landed_land'))     # stops above the caption box
log.append(save(box(L, (187, 774, 129, 205)), 'lanternwake', 'landed_water'))
for i, b in enumerate([(765, 780, 74, 181), (847, 780, 77, 181), (927, 780, 93, 181), (1020, 780, 93, 181)]):
    log.append(save(box(L, b), 'lanternwake', f'fold_{i}'))
for i, b in enumerate([(7, 1084, 215, 97), (224, 1083, 230, 101), (450, 1085, 228, 100), (679, 1085, 232, 100), (904, 1086, 218, 96)]):
    log.append(save(box(L, b), 'lanternwake', f'side_fly_{i}'))
for i, b in enumerate([(9, 1279, 180, 97), (188, 1273, 193, 103), (375, 1260, 184, 116), (561, 1253, 184, 123), (751, 1239, 187, 137), (938, 1217, 178, 159)]):
    log.append(save(box(L, b, main=False), 'lanternwake', f'rise_{i}'))

# ---- Deck sheet ----
D = load('Airship Deck Stage and Overworld Sprites.png')
x, y, w, h = 8, 97, 1105, 583
stage = D[y:y + h, x:x + w]
hole = (stage[..., 3] < 128).astype(np.uint8)
rgb = cv2.inpaint(np.ascontiguousarray(stage[..., :3]), hole, 9, cv2.INPAINT_TELEA)
full = np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)])
log.append(save(full, 'deck', 'deck_stage_full'))
for n, b in [('brackhorn_icon_s', (23, 802, 65, 90)), ('brackhorn_icon_m', (94, 778, 83, 125)), ('brackhorn_icon_l', (185, 746, 124, 177)),
             ('wayfarer_icon_s', (344, 782, 70, 103)), ('wayfarer_icon_m', (414, 782, 123, 103)), ('wayfarer_icon_l', (537, 746, 182, 144)),
             ('lanternwake_icon_s', (754, 829, 71, 63)), ('lanternwake_icon_m', (823, 796, 109, 109)), ('lanternwake_icon_l', (931, 777, 171, 128))]:
    log.append(save(box(D, b), 'icons', n))
fx = {'bell': [[(28, 1220, 29, 25)], [(83, 1217, 42, 39), (125, 1222, 17, 18)], [(157, 1210, 37, 52)], [(226, 1218, 44, 41)],
               [(281, 1250, 15, 17), (291, 1234, 17, 20), (303, 1215, 19, 20)]],
      'steam': [[(403, 1221, 35, 36)], [(458, 1214, 45, 44)], [(517, 1209, 62, 54)], [(593, 1192, 89, 88)]],
      'drive': [[(752, 1233, 28, 22)], [(796, 1228, 33, 29)], [(843, 1218, 48, 41)], [(907, 1201, 74, 72)], [(993, 1195, 92, 79), (1065, 1218, 23, 14)]]}
for name, frames in fx.items():
    for i, parts in enumerate(frames):
        x0 = min(b[0] for b in parts); y0 = min(b[1] for b in parts)
        x1 = max(b[0] + b[2] for b in parts); y1 = max(b[1] + b[3] for b in parts)
        log.append(save(trim(snap(D[y0:y1, x0:x1])), 'fx', f'{name}_{i}'))
print('\n'.join(log)); print(len(log), 'slices')
