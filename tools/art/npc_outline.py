"""Add a 1px dark outline to upscaled NPC sheets where the edge is not already dark.
Run after tools/aseprite job 3. Usage: python npc_outline.py <folder>"""
import sys, glob, os
import numpy as np
from PIL import Image

OUT = np.array([20, 16, 22, 255], dtype=np.uint8)

def outline(path):
    a = np.array(Image.open(path).convert('RGBA'))
    op = a[..., 3] > 0
    lum = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])
    bright_edge = op & (lum > 70)
    add = np.zeros_like(op)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        add |= np.roll(bright_edge, (dy, dx), axis=(0, 1))
    add &= ~op
    a[add] = OUT
    Image.fromarray(a).save(path)
    return int(add.sum())

if __name__ == '__main__':
    for p in sorted(glob.glob(os.path.join(sys.argv[1], '*.png'))):
        print(outline(p), os.path.basename(p))
