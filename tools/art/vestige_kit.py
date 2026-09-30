"""Pixel-art creature toolkit: parts (tubes, blobs, polygons) rasterised at 1px with no anti-aliasing,
shaded with fixed ramps from a distance field + top-left light, rim-lit, outlined, with a dithered spirit aura."""
import math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

def hexc(h): h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], np.uint8)
def ramp(*hs): return [hexc(h) for h in hs]

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16

class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts = []   # (z, mask, ramp, opts)
    # ---- shape makers (return boolean mask) ----
    def blank(self): return np.zeros((self.h, self.w), bool)
    def ellipse(self, cx, cy, rx, ry, rot=0.0):
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        x = xx + 0.5 - cx; y = yy + 0.5 - cy
        c, s = math.cos(rot), math.sin(rot)
        u = x * c + y * s; v = -x * s + y * c
        return (u / rx) ** 2 + (v / ry) ** 2 <= 1
    def poly(self, pts):
        im = Image.new('1', (self.w, self.h), 0)
        ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=1)
        return np.array(im, bool)
    def tube(self, pts, radii, step=0.35):
        """pts: list of (x,y) control points (Catmull-Rom through them); radii: list, same length."""
        m = self.blank()
        P = np.array(pts, float); R = np.array(radii, float)
        n = len(P)
        samples = []
        for i in range(n - 1):
            p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, n - 1)]
            seg = np.linalg.norm(p2 - p1)
            k = max(2, int(seg / step))
            for j in range(k):
                t = j / k
                t2, t3 = t * t, t * t * t
                q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
                r = R[i] * (1 - t) + R[i + 1] * t
                samples.append((q[0], q[1], r))
        samples.append((P[-1][0], P[-1][1], R[-1]))
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        for (x, y, r) in samples:
            if r <= 0.3:
                xi, yi = int(x), int(y)
                if 0 <= xi < self.w and 0 <= yi < self.h: m[yi, xi] = True
                continue
            x0, x1 = int(max(0, x - r - 1)), int(min(self.w, x + r + 2))
            y0, y1 = int(max(0, y - r - 1)), int(min(self.h, y + r + 2))
            sub = (xx[y0:y1, x0:x1] + 0.5 - x) ** 2 + (yy[y0:y1, x0:x1] + 0.5 - y) ** 2 <= r * r
            m[y0:y1, x0:x1] |= sub
        return m
    def add(self, z, mask, rmp, **opts):
        self.parts.append((z, mask, rmp, opts))
        return mask

    # ---- render ----
    def render(self, outline=hexc('#0c0a12'), aura=None, aura_r=4, light=(-0.6, -0.8)):
        H, W = self.h, self.w
        rgb = np.zeros((H, W, 3), np.uint8); alpha = np.zeros((H, W), bool)
        zbuf = np.full((H, W), -1e9)
        idmap = np.full((H, W), -1)
        for pid, (z, mask, rmp, o) in enumerate(sorted(self.parts, key=lambda p: p[0])):
            if not mask.any(): continue
            d = ndimage.distance_transform_edt(mask)
            depth = o.get('depth', 5.0)
            shade = np.clip(d / depth, 0, 1) ** o.get('gamma', 0.7)
            # directional light: compare distance to shifted mask edge
            lx, ly = light
            sh = np.roll(np.roll(mask, int(round(-lx * 2)), 1), int(round(-ly * 2)), 0)
            lit = mask & ~sh              # edge facing the light
            dark = mask & ~np.roll(np.roll(mask, int(round(lx * 2)), 1), int(round(ly * 2)), 0)
            ys, xs = np.nonzero(mask)
            ybias = np.zeros((H, W))
            if o.get('vgrad', 0.3):
                y0, y1 = ys.min(), ys.max()
                ybias[ys, xs] = -(ys - y0) / max(1, y1 - y0) * o.get('vgrad', 0.3)
            val = shade * 0.75 + 0.25 + ybias
            n = len(rmp)
            idx = np.clip((val * (n - 1) + BAYER[np.arange(H)[:, None] % 4, np.arange(W)[None, :] % 4] * o.get('dither', 0.0) - o.get('dither', 0.0) / 2).round().astype(int), 0, n - 1)
            idx[dark & mask] = np.maximum(idx[dark & mask] - 1, 0)
            idx[lit & mask] = np.minimum(idx[lit & mask] + o.get('rim', 1), n - 1)
            col = np.array(rmp)[idx]
            if 'pattern' in o:
                pm, pc = o['pattern']
                col[pm & mask] = pc
            rgb[mask] = col[mask]; alpha |= mask
            idmap[mask] = pid
        # internal outlines between parts: where a pixel's part differs from the one below/left and is on top
        sel = np.zeros((H, W), bool)
        for dy, dx in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            nb = np.roll(np.roll(idmap, dy, 0), dx, 1)
            sel |= (idmap >= 0) & (nb >= 0) & (nb < idmap)
        # darken selout pixels (the upper part's edge)
        rgb[sel] = (rgb[sel].astype(int) * 0.55).astype(np.uint8)
        # outer outline
        p = np.pad(alpha, 1)
        edge = (~alpha) & (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
        out = np.zeros((H, W, 4), np.uint8)
        out[alpha, :3] = rgb[alpha]; out[alpha, 3] = 255
        out[edge, :3] = outline; out[edge, 3] = 255
        if aura is not None:
            solid = alpha | edge
            d = ndimage.distance_transform_edt(~solid)
            B = BAYER[np.arange(H)[:, None] % 4, np.arange(W)[None, :] % 4]
            ring = (~solid) & (d <= aura_r) & (B < (1 - d / (aura_r + 1)) * 0.75)
            out[ring, :3] = aura; out[ring, 3] = 255
        return out

def dots(mask_shape, pts, r=0):
    h, w = mask_shape
    m = np.zeros((h, w), bool)
    for x, y in pts:
        xi, yi = int(x), int(y)
        m[max(0, yi - r):yi + r + 1, max(0, xi - r):xi + r + 1] = True
    return m

def line_mask(shape, pts, width=1):
    h, w = shape
    im = Image.new('1', (w, h), 0)
    ImageDraw.Draw(im).line([(float(x), float(y)) for x, y in pts], fill=1, width=width)
    return np.array(im, bool)

def motes(out, t, n, box, color, count=14, seed=0, rise=40):
    """floating light motes (2x2 / 1x1) that rise and loop"""
    rng = np.random.RandomState(seed)
    x0, y0, x1, y1 = box
    H, W = out.shape[:2]
    for i in range(count):
        bx = rng.uniform(x0, x1); by = rng.uniform(y0, y1); ph = rng.rand()
        s = (t / n + ph) % 1
        x = int(bx + math.sin(s * 6.28 + i) * 3); y = int(by - s * rise)
        size = 2 if s < 0.5 else 1
        c = color if s < 0.75 else (np.array(color) * 0.7).astype(np.uint8)
        for dy in range(size):
            for dx in range(size):
                if 0 <= y + dy < H and 0 <= x + dx < W and out[y + dy, x + dx, 3] == 0:
                    out[y + dy, x + dx, :3] = c; out[y + dy, x + dx, 3] = 255
    return out

def to_img(a): return Image.fromarray(a, 'RGBA')

def appear_frames(final, n=8, edge=hexc('#ffffff'), glow=hexc('#9ae0ff')):
    """FF6-style materialise: a scan band sweeps up from the bottom revealing the creature, leading rows glow."""
    H, W = final.shape[:2]
    ys = np.nonzero(final[..., 3])[0]; top, bot = ys.min(), ys.max()
    frames = []
    for i in range(1, n + 1):
        f = np.zeros_like(final)
        cut = int(bot - (bot - top + 6) * i / n)
        f[cut:] = final[cut:]
        for k, c in ((0, edge), (1, edge), (2, glow), (3, glow)):
            y = cut + k
            if 0 <= y < H:
                m = final[y, :, 3] > 0
                f[y, m, :3] = c
        frames.append(f)
    return frames

def vanish_frames(final, n=6, col=hexc('#ffffff')):
    """dissolve upward into flecks using an ordered-dither threshold that rises frame by frame"""
    H, W = final.shape[:2]
    B = BAYER[np.arange(H)[:, None] % 4, np.arange(W)[None, :] % 4]
    ys = np.nonzero(final[..., 3])[0]; top, bot = ys.min(), ys.max()
    yn = (np.arange(H)[:, None] - top) / max(1, bot - top)
    frames = []
    for i in range(1, n + 1):
        t = i / n
        keep = B > (t * 1.4 - (1 - yn) * 0.4)
        f = final.copy()
        f[~keep] = 0
        flash = (B > (t * 1.4 - (1 - yn) * 0.4)) & (B < (t * 1.4 - (1 - yn) * 0.4) + 0.12) & (final[..., 3] > 0)
        f[flash, :3] = col; f[flash, 3] = 255
        frames.append(f)
    return frames

def idle_frames(base, n=8, aura=(255, 200, 120), mote=(255, 240, 200), seed=0, pad=12, bob=2):
    """float bob, travelling shimmer on the brightest pixels, pulsing dithered aura ring, rising motes."""
    Hb, Wb = base.shape[:2]
    H, W = Hb + 2 * pad, Wb + 2 * pad
    lum = base[..., :3].astype(float) @ [0.3, 0.59, 0.11]
    op = base[..., 3] > 0
    thr = np.percentile(lum[op], 90) if op.any() else 255
    bright = op & (lum >= thr)
    yy, xx = np.mgrid[0:Hb, 0:Wb]
    frames = []
    B = BAYER[np.arange(H)[:, None] % 4, np.arange(W)[None, :] % 4]
    for t in range(n):
        ph = 2 * math.pi * t / n
        dy = int(round(-math.sin(ph) * bob))
        b = base.copy()
        wave = np.sin((xx + yy) * 0.08 - ph * 2) > 0.55
        m = bright & wave
        b[m, :3] = np.clip(b[m, :3].astype(int) * 1.18 + 18, 0, 255).astype(np.uint8)
        f = np.zeros((H, W, 4), np.uint8)
        f[pad + dy:pad + dy + Hb, pad:pad + Wb][b[..., 3] > 0] = b[b[..., 3] > 0]
        solid = f[..., 3] > 0
        d = ndimage.distance_transform_edt(~solid)
        r = 3 + math.sin(ph) * 1.0
        ring = (~solid) & (d <= r) & (B < (1 - d / (r + 1)) * 0.6)
        f[ring, :3] = aura; f[ring, 3] = 255
        motes(f, t, n, (pad, pad + Hb * 0.2, pad + Wb, pad + Hb), np.array(mote, np.uint8), count=16, seed=seed, rise=Hb * 0.35)
        frames.append(f)
    return frames
