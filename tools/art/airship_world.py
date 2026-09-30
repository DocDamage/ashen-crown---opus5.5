"""Build 8-direction world-map airship frames from the pixelated top-down art (Aseprite job 8).
South frames are rotated in 45-degree steps with a RotSprite-style method (Scale2x three times,
nearest rotation, 1/8 sample) so no new colours appear; the drawn north frames are used for north.
Also writes one black silhouette shadow per direction (engine draws it at ~40% opacity).
Usage: python airship_world.py <Assets/_processed/airships>"""
import sys, os, glob
import numpy as np
from PIL import Image

def scale2x(a):
    h, w = a.shape[:2]
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode='edge')
    B, D, E, F, H = p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 1:-1], p[1:-1, 2:], p[2:, 1:-1]
    eq = lambda x, y: np.all(x == y, axis=-1)
    c = (~eq(B, H)) & (~eq(D, F))
    e0 = np.where((c & eq(D, B))[..., None], D, E)
    e1 = np.where((c & eq(B, F))[..., None], F, E)
    e2 = np.where((c & eq(D, H))[..., None], D, E)
    e3 = np.where((c & eq(H, F))[..., None], F, E)
    out = np.zeros((h * 2, w * 2, a.shape[2]), a.dtype)
    out[0::2, 0::2], out[0::2, 1::2], out[1::2, 0::2], out[1::2, 1::2] = e0, e1, e2, e3
    return out

def rotsprite(img, angle):
    a = np.array(img.convert('RGBA'))
    for _ in range(3): a = scale2x(a)
    big = Image.fromarray(a).rotate(angle, resample=Image.NEAREST, expand=True)
    w, h = big.size
    small = big.resize((max(1, w // 8), max(1, h // 8)), Image.NEAREST)
    b = np.array(small); b[..., 3] = np.where(b[..., 3] >= 128, 255, 0)
    return Image.fromarray(b)

def place(img, size):
    c = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    c.alpha_composite(img, ((size - img.width) // 2, (size - img.height) // 2))
    return c

ANG = {'south': 0, 'southeast': 45, 'east': 90, 'northeast': 135, 'west': -90, 'southwest': -45, 'northwest': -135}
root = sys.argv[1]
for ship, size in (('wayfarer', 200), ('lanternwake', 192)):
    src = os.path.join(root, ship, 'world_src')
    south = sorted(glob.glob(os.path.join(src, 'topdown_south_*.png')))
    north = sorted(glob.glob(os.path.join(src, 'topdown_north_*.png')))
    for d, ang in list(ANG.items()) + [('north', None)]:
        frames = [Image.open(f).convert('RGBA') for f in north] if ang is None else [rotsprite(Image.open(f), ang) for f in south]
        od = os.path.join(root, ship, 'world', d); os.makedirs(od, exist_ok=True)
        for i, fr in enumerate(frames):
            place(fr, size).save(os.path.join(od, f'frame_{i}.png'))
        sil = np.array(place(frames[0], size)); sil[..., :3] = 0
        sd = os.path.join(root, ship, 'world', 'shadow'); os.makedirs(sd, exist_ok=True)
        Image.fromarray(sil).save(os.path.join(sd, f'{d}.png'))
        print(ship, d, len(frames), 'frames', size)
