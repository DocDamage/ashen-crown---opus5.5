"""Build missing hero battle animations from each hero's own frames.
Victory: intro frames + looping pose from an existing animation, plus a small star glint.
Hurt: recoil frames taken from the start of the death animation (particles removed), then back.
Death: hurt recoil, then a rotsprite fall to the ground (or a power-down slump for the Rune Golem).
Outputs frame folders matching the hero pack layout, plus meta.json with durations/loop info.
"""
import os, glob, json, math
import numpy as np
from PIL import Image
from scipy import ndimage

OUT = '/home/claude/h/out'

def root(name, processed):
    base = '_processed/heroes' if processed else 'heroes'
    h = [x for x in os.listdir(base) if name in x][0]
    return glob.glob(os.path.join(base, h, '*'))[0], h

def load(hero, anim, d, processed=False, exact=False):
    r, _ = root(hero, processed)
    cands = sorted(glob.glob(r + '/animations/*'))
    a = [x for x in cands if (os.path.basename(x) == anim if exact else os.path.basename(x).startswith(anim))][0]
    if os.path.isdir(a + '/' + d):
        return [Image.open(f).convert('RGBA') for f in sorted(glob.glob(a + '/' + d + '/*.png'))], False
    fr = [Image.open(f).convert('RGBA') for f in sorted(glob.glob(a + '/east/*.png'))]
    return [f.transpose(Image.FLIP_LEFT_RIGHT) for f in fr], True

# ---------- helpers ----------
def scale2x(a):
    h, w = a.shape[:2]
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode='edge')
    B = p[0:h, 1:w+1]; D = p[1:h+1, 0:w]; E = p[1:h+1, 1:w+1]; F = p[1:h+1, 2:w+2]; H = p[2:h+2, 1:w+1]
    eq = lambda x, y: np.all(x == y, axis=2)
    c = (~eq(B, H)) & (~eq(D, F))
    E0 = np.where((c & eq(D, B))[..., None], D, E)
    E1 = np.where((c & eq(B, F))[..., None], F, E)
    E2 = np.where((c & eq(D, H))[..., None], D, E)
    E3 = np.where((c & eq(H, F))[..., None], F, E)
    out = np.zeros((h*2, w*2, a.shape[2]), a.dtype)
    out[0::2, 0::2] = E0; out[0::2, 1::2] = E1; out[1::2, 0::2] = E2; out[1::2, 1::2] = E3
    return out

def rotsprite(img, angle, pivot, canvas, dest):
    """Rotate img (RGBA) by angle degrees CCW around pivot (x,y in img), place pivot at dest on canvas size."""
    a = np.array(img)
    a[a[..., 3] < 128] = 0
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    for _ in range(3):
        a = scale2x(a)
    big = Image.fromarray(a)
    k = 8
    W, H = canvas
    # inverse mapping at canvas pixel centres
    ys, xs = np.mgrid[0:H, 0:W]
    dx = xs + 0.5 - dest[0]; dy = ys + 0.5 - dest[1]
    t = math.radians(angle)
    # screen coords y down; CCW visual rotation
    sx = dx * math.cos(t) - dy * math.sin(t)
    sy = dx * math.sin(t) + dy * math.cos(t)
    px = ((sx + pivot[0]) * k).astype(int); py = ((sy + pivot[1]) * k).astype(int)
    ok = (px >= 0) & (py >= 0) & (px < a.shape[1]) & (py < a.shape[0])
    out = np.zeros((H, W, 4), np.uint8)
    out[ok] = a[py[ok], px[ok]]
    return Image.fromarray(out)

def place(img, canvas, off):
    c = Image.new('RGBA', canvas, (0, 0, 0, 0)); c.alpha_composite(img, off); return c

def clean_particles(img, keep_ratio=0.02):
    a = np.array(img)
    m = a[..., 3] > 0
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    if n <= 1: return img
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    big = sizes.max()
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= big * keep_ratio])
    a[~keep] = 0
    return Image.fromarray(a)

def flash(img, amt=0.65):
    a = np.array(img).astype(float)
    a[..., :3] = a[..., :3] + (255 - a[..., :3]) * amt
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))

def feet(img):
    a = np.array(img)[..., 3] > 0
    ys, xs = np.nonzero(a)
    y = ys.max(); row = xs[ys >= y - 2]
    return (row.min(), row.max(), y)

STAR = ["..#..", "..#..", "##@##", "..#..", "..#.."]
STAR_S = ["...", ".@.", "..."]
STAR_M = [".#.", "#@#", ".#."]
def glint(img, t, x, y):
    shapes = [STAR_S, STAR_M, STAR, STAR_M]
    s = shapes[t % 4]
    a = img.copy(); px = a.load()
    o = len(s) // 2
    for j, row in enumerate(s):
        for i, ch in enumerate(row):
            X, Y = x + i - o, y + j - o
            if 0 <= X < a.width and 0 <= Y < a.height and ch != '.':
                px[X, Y] = (255, 255, 255, 255) if ch == '@' else (255, 244, 176, 255)
    return a

def top_point(img):
    a = np.array(img)[..., 3] > 0
    ys, xs = np.nonzero(a)
    y = ys.min(); x = int(xs[ys == y].mean())
    return x, y

def save(hero_dir, anim, d, frames, meta):
    p = os.path.join(OUT, hero_dir, anim, d)
    os.makedirs(p, exist_ok=True)
    for i, f in enumerate(frames):
        f.save(os.path.join(p, f'frame_{i:03d}.png'))
    json.dump(meta, open(os.path.join(OUT, hero_dir, anim, 'meta.json'), 'w'), indent=1)

# ---------- victory ----------
VICTORY = [
    # hero key, processed, anim, exact, intro idx, loop idx
    ('Archangel', False, 'Wings_of_Judgment', False, [0, 1, 2, 3, 4, 5], [5, 6, 7, 6]),
    ('CORVUS', False, '6._RAVEN_SWARM', False, [0, 1, 2, 3, 4, 5, 6, 7, 8], [9, 10, 11, 12, 11, 10]),
    ('MALDRATH', False, '7._SOUL_NOVA', False, [0, 1, 2, 3, 4, 5], [6, 7, 8, 7]),
    ('Crimson Kitsune', True, 'Special_Skill_Foxfire_Step', False, [0, 1], [2, 3, 2, 1]),
    ('Crimson Oni', True, 'DEMONIC_COUNTERSTANCE', False, [0, 1, 2, 3, 4], [5, 6, 7, 8, 7, 6]),
    ('VELKHAR', False, '8._DEATH_NOVA', False, [0, 1, 2, 3], [4, 5, 6, 7, 6, 5]),
    ('KAEL', False, '4._ENERGY_SLASH', False, [0, 1, 2, 3, 4], [5, 6]),
    ('AUREX', False, '128x128_pixel_art_animation_AUREX_Dragonblood_Cham', True, [0, 10, 11, 12, 13, 14], [15, 16]),
    ('MORWEN', False, '7._MOON_RITUAL', False, [0, 1, 2, 3, 4, 5, 6, 7, 8], [9, 10, 11, 12, 11, 10]),
]

def build_victory(spec):
    key, proc, anim, exact, intro, loop = spec
    _, hdir = root(key, proc)
    for d in ('east', 'west'):
        fr, mirrored = load(key, anim, d, proc, exact)
        seq = [fr[i] for i in intro] + [fr[i] for i in loop]
        # glint on the first pass of the loop, at the highest point of the pose
        out = []
        for n, f in enumerate(seq):
            if len(intro) <= n < len(intro) + 4:
                x, y = top_point(fr[loop[0]])
                f = glint(f, n - len(intro), x, max(2, y - 1))
            out.append(f)
        durations = [90] * len(intro) + [160] * len(loop)
        meta = dict(source=anim, intro=intro, loop=loop, loop_from=len(intro),
                    durations_ms=durations, mirrored_from_east=mirrored,
                    note='Frames 0..loop_from-1 play once; the rest loop. Glint drawn on the first loop pass only for frames loop_from..loop_from+3; engine may loop from loop_from+4 wrap.')
        save(hdir, 'Victory_generated', d, out, meta)
    return hdir

# ---------- hurt ----------
HURT = [
    ('Crimson Oni', True, 'EPIC_DEATH_FALL_OF_THE_CRIMSON_LEGEND', [1, 2, 3]),
    ('Crimson Kitsune', True, 'Death_Animation_Fallen_Empress', [1, 2, 3]),
]
IDLE = {'Crimson Oni': 'Breathing_Idle', 'Crimson Kitsune': 'Breathing_Idle'}

def build_hurt(spec):
    key, proc, anim, idx = spec
    _, hdir = root(key, proc)
    for d in ('east', 'west'):
        fr, mirrored = load(key, anim, d, proc)
        idle, _ = load(key, IDLE[key], d, proc)
        rec = [clean_particles(fr[i]) for i in idx]
        back = -1 if d == 'east' else 1
        sh = lambda im, n: place(im, im.size, (back * n, 0))
        seq = [flash(sh(rec[0], 1), 0.55), sh(rec[1], 3), sh(rec[2], 4), sh(rec[2], 4), sh(rec[1], 2), sh(rec[0], 1), idle[0]]
        durations = [60, 70, 90, 110, 80, 80, 90]
        meta = dict(source=anim, frames=idx, durations_ms=durations, mirrored_from_east=mirrored,
                    note='White hit-flash, recoil from the death animation start (blood specks removed), recover to idle.')
        save(hdir, 'Hurt_generated', d, seq, meta)
    return hdir

# ---------- death ----------
def fall_sequence(fr, peak, face_east=True):
    base = fr[peak]
    W, H = base.size
    pad = int(W * 0.55)
    CW = W + 2 * pad
    x0, x1, fy = feet(base)
    # pivot: the back foot (fall backwards)
    pv = (x0, fy) if face_east else (x1, fy)
    sign = 1 if face_east else -1   # CCW = head to the left for east-facing
    frames = [place(f, (CW, H), (pad, 0)) for f in fr[:peak + 1]]
    steps = [(12, 0), (30, 1), (52, 2), (74, 3), (90, 3), (84, 1), (90, 0)]
    for ang, drop in steps:
        # as the body tips, the pivot slides slightly toward the head side
        slide = -sign * int(ang / 90 * 6)
        frames.append(rotsprite(base, sign * ang, pv, (CW, H), (pad + pv[0] + slide, pv[1] - 0 + 0)))
    # make sure the lying body sits on the ground line fy
    fixed = []
    for f in frames:
        a = np.array(f)[..., 3] > 0
        if a.any():
            yb = np.nonzero(a)[0].max()
            if yb != fy:
                g = Image.new('RGBA', f.size); g.alpha_composite(f, (0, fy - yb)); f = g
        fixed.append(f)
    durations = [80] * (peak + 1) + [70, 70, 60, 60, 90, 70, 400]
    return fixed, durations, pad

def build_death_fall(key, anim, peak, idle_anim):
    _, hdir = root(key, False)
    for d in ('east', 'west'):
        fr, mirrored = load(key, anim, d, False)
        seq, dur, pad = fall_sequence(fr, peak, face_east=(d == 'east'))
        meta = dict(source=anim, recoil=list(range(peak + 1)), durations_ms=dur, mirrored_from_east=mirrored,
                    canvas_pad_each_side=pad,
                    note='Recoil from the hurt animation, then a rotsprite fall backwards. Canvas widened by pad on both sides; the original frame centre is the canvas centre. Last frame = KO pose, hold it.')
        save(hdir, 'Death_generated', d, seq, meta)
    return hdir

def desat_runes(img, t):
    a = np.array(img).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    glow = (b > r + 30) & (g > r + 10) & (a[..., 3] > 0)
    grey = (r + g + b) / 3 * 0.55
    for c in range(3):
        a[..., c] = np.where(glow, a[..., c] * (1 - t) + grey * t, a[..., c])
    dim = 1 - 0.18 * t
    a[..., :3] *= dim
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))

def build_golem_death():
    key = 'RUNE_GOLEM'
    _, hdir = root(key, True)
    for d in ('east', 'west'):
        fr, mirrored = load(key, 'RUNE_GOLEM_hurt', d, True)
        base = fr[3]
        W, H = base.size
        pad = int(W * 0.3); CW = W + 2 * pad
        x0, x1, fy = feet(base)
        east = d == 'east'
        pv = (x1, fy) if east else (x0, fy)    # front foot: slump forward
        sign = -1 if east else 1
        seq = [place(f, (CW, H), (pad, 0)) for f in fr[:4]]
        for t in (0.35, 0.7, 1.0):
            seq.append(place(desat_runes(base, t), (CW, H), (pad, 0)))
        dead = desat_runes(base, 1.0)
        for ang in (8, 18, 28, 25, 28):
            f = rotsprite(dead, sign * ang, pv, (CW, H), (pad + pv[0], pv[1]))
            a = np.array(f)[..., 3] > 0; yb = np.nonzero(a)[0].max()
            g = Image.new('RGBA', f.size); g.alpha_composite(f, (0, fy - yb)); seq.append(g)
        dur = [80] * 4 + [140, 140, 200] + [90, 90, 90, 70, 400]
        meta = dict(source='RUNE_GOLEM_hurt', durations_ms=dur, mirrored_from_east=mirrored, canvas_pad_each_side=pad,
                    note='Stagger from the hurt animation, the rune glow drains to grey, then the golem slumps forward. Last frame = KO pose.')
        save(hdir, 'Death_generated', d, seq, meta)
    return hdir

if __name__ == '__main__':
    import shutil; shutil.rmtree(OUT, ignore_errors=True)
    for s in VICTORY: print('victory', build_victory(s))
    for s in HURT: print('hurt', build_hurt(s))
    print('death', build_death_fall('NIGHT_RIDER', 'Hurt_7_frames', 4, 'Idle'))
    print('death', build_death_fall('VESPERA', 'VESPERA_MOONHARE_WARRIOR_HURT', 4, 'Idle'))
    print('death', build_golem_death())
