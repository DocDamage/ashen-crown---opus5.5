"""Snap alpha to 0/255 and reduce each processed parallax layer to at most 32 colours (no dithering).
Usage: python layer_clean.py <Assets/_processed/parallax>"""
import sys, glob, os
import numpy as np
from PIL import Image

for f in sorted(glob.glob(os.path.join(sys.argv[1], '**', '*.png'), recursive=True)):
    im = Image.open(f).convert('RGBA')
    a = np.array(im)
    alpha = np.where(a[..., 3] >= 128, 255, 0).astype(np.uint8)
    rgb = Image.fromarray(a[..., :3])
    q = rgb.quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    out = np.dstack([np.array(q), alpha])
    Image.fromarray(out, 'RGBA').save(f)
    print(im.size, os.path.relpath(f, sys.argv[1]))
