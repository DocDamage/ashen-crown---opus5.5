"""Make 4-direction walk cycles from SakPix 8-direction still rotations.
Frames per direction: step A, pass, step B, pass (4 frames).
Side views: the leg block is duplicated into a back leg (sheared back, darkened) and a front leg (sheared forward).
Front/back views: the leg block is split at the body centre; the stepping leg is lifted and shortened.
The upper body bobs 1px on the pass frames. Works at native resolution; scaling happens in Aseprite.
"""
import numpy as np
from PIL import Image

def bbox(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return xs.min(), ys.min(), xs.max(), ys.max()

def darken(a, f=0.78):
    b = a.copy(); b[..., :3] = (b[..., :3].astype(float) * f).astype(np.uint8); return b

def shear_block(block, hip_y, k):
    """shift each row below hip by round(k*(y-hip)) px (positive = right)."""
    out = np.zeros_like(block)
    H, W = block.shape[:2]
    for y in range(H):
        s = int(round(k * (y - hip_y))) if y > hip_y else 0
        row = block[y]
        if s > 0: out[y, s:] = row[:W - s]
        elif s < 0: out[y, :W + s] = row[-s:]
        else: out[y] = row
    return out

def over(dst, src):
    m = src[..., 3] > 0
    dst[m] = src[m]
    return dst

def split(img, leg_frac):
    a = np.array(img.convert('RGBA'))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    x0, y0, x1, y1 = bbox(a)
    h = y1 - y0 + 1
    hip = y1 - int(round(h * leg_frac))
    upper = a.copy(); upper[hip + 1:] = 0
    legs = a.copy(); legs[:hip + 1] = 0
    return a, upper, legs, hip, (x0, y0, x1, y1)

def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys = slice(max(dy, 0), H + min(dy, 0)); yd = slice(max(-dy, 0), H + min(-dy, 0))
    xs = slice(max(dx, 0), W + min(dx, 0)); xd = slice(max(-dx, 0), W + min(-dx, 0))
    out[ys, xs] = a[yd, xd]
    return out

def side_walk(img, facing):  # facing +1 east, -1 west
    a, upper, legs, hip, (x0, y0, x1, y1) = split(img, 0.30)
    reach = 4.0
    k = reach / max(1, (y1 - hip))
    frames = []
    for phase in ('A', 'P', 'B', 'P'):
        f = np.zeros_like(a)
        if phase == 'P':
            f = over(f, legs)
            f = over(f, shift(upper, 0, -1))
            # keep the torso attached: fill the 1px gap with the hip row
            f = over(f, shift(legs, 0, -1) * (np.arange(a.shape[0])[:, None, None] == hip))
        else:
            sgn = 1 if phase == 'A' else -1
            near = shear_block(legs, hip, sgn * k * facing)
            far = darken(shear_block(legs, hip, -sgn * k * facing))
            f = over(f, far); f = over(f, near); f = over(f, upper)
        frames.append(Image.fromarray(f))
    return frames

def front_walk(img):
    a, upper, legs, hip, (x0, y0, x1, y1) = split(img, 0.26)
    cx = (x0 + x1 + 1) // 2
    L = legs.copy(); L[:, cx:] = 0
    R = legs.copy(); R[:, :cx] = 0
    def lift(block, n=2):
        # shorten the leg by n rows (drop rows from the middle of the shin) = foot lifts n px
        H = block.shape[0]
        rows = list(range(hip + 1, y1 + 1))
        if len(rows) <= n + 2: return shift(block, 0, -n)
        mid = len(rows) // 2
        drop = set(rows[mid - n // 2: mid - n // 2 + n])
        keep = [r for r in range(H) if r not in drop]
        out = np.zeros_like(block)
        packed = block[keep]
        # rows above hip stay; everything below moves up by n
        out[:len(keep)] = packed
        return out
    frames = []
    for phase in ('A', 'P', 'B', 'P'):
        f = np.zeros_like(a)
        if phase == 'P':
            f = over(f, legs)
            f = over(f, shift(upper, 0, -1))
            f = over(f, shift(legs, 0, -1) * (np.arange(a.shape[0])[:, None, None] == hip))
        else:
            up, down = (L, R) if phase == 'A' else (R, L)
            f = over(f, down); f = over(f, lift(up)); f = over(f, upper)
        frames.append(Image.fromarray(f))
    return frames

def walk_set(rot_dir):
    out = {}
    for d in ('south', 'north'):
        out[d] = front_walk(Image.open(f'{rot_dir}/{d}.png'))
    out['east'] = side_walk(Image.open(f'{rot_dir}/east.png'), +1)
    out['west'] = side_walk(Image.open(f'{rot_dir}/west.png'), -1)
    return out
