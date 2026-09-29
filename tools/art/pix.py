"""Pixel canvas helpers for deterministic programmatic art (seeded, versioned)."""
import math, random
from PIL import Image

GEN_VERSION = "ashen-art-1.0"


def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mix(c1, c2, t):
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(3)) + (c1[3] if len(c1) > 3 else 255,)


def shade(c, f):
    """f<0 darken toward cool shadow, f>0 lighten toward warm light."""
    if f < 0:
        tgt = (20, 18, 40)
        return mix(c, tgt + (255,), -f)
    tgt = (255, 246, 214)
    return mix(c, tgt + (255,), f)


def ramp(base, n=4):
    """Return dark->light ramp around a base colour."""
    return [shade(base, -0.55), shade(base, -0.25), base, shade(base, 0.3)][:n]


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[None] * w for _ in range(h)]   # RGBA or None
        self.tag = [[0] * w for _ in range(h)]     # material id for outline/shading decisions

    def put(self, x, y, c, tag=1):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            if len(c) == 4 and c[3] == 0:
                self.px[y][x] = None
                return
            self.px[y][x] = c
            self.tag[y][x] = tag

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.px[y][x]
        return None

    def rect(self, x0, y0, x1, y1, c, tag=1):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.put(x, y, c, tag)

    def ellipse(self, cx, cy, rx, ry, c, tag=1):
        for y in range(int(math.floor(cy - ry)), int(math.ceil(cy + ry)) + 1):
            for x in range(int(math.floor(cx - rx)), int(math.ceil(cx + rx)) + 1):
                if rx <= 0 or ry <= 0:
                    continue
                if ((x - cx) / (rx + 0.35)) ** 2 + ((y - cy) / (ry + 0.35)) ** 2 <= 1.0:
                    self.put(x, y, c, tag)

    def line(self, x0, y0, x1, y1, c, thick=1, tag=1):
        steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        r = (thick - 1) / 2.0
        for i in range(steps + 1):
            t = i / steps
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            if thick <= 1:
                self.put(x, y, c, tag)
            else:
                for yy in range(int(math.floor(y - r)), int(math.ceil(y + r)) + 1):
                    for xx in range(int(math.floor(x - r)), int(math.ceil(x + r)) + 1):
                        if (xx - x) ** 2 + (yy - y) ** 2 <= (r + 0.45) ** 2:
                            self.put(xx, yy, c, tag)

    def poly(self, pts, c, tag=1):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            for x in range(int(min(xs)), int(max(xs)) + 1):
                if point_in_poly(x + 0.5, y + 0.5, pts):
                    self.put(x, y, c, tag)

    def outline(self, col=(24, 18, 30, 255), inner=True):
        """1px outline around the silhouette; interior material borders get a darker line when inner."""
        out = [row[:] for row in self.px]
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x] is None:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        n = self.get(x + dx, y + dy)
                        if n is not None:
                            out[y][x] = col
                            break
        self.px = out

    def light(self, strength=0.18):
        """Top-left light: lighten pixels whose upper-left neighbour is empty, darken lower-right edges."""
        out = [row[:] for row in self.px]
        for y in range(self.h):
            for x in range(self.w):
                c = self.px[y][x]
                if c is None:
                    continue
                t = self.tag[y][x]
                def edge(dx, dy):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < self.w and 0 <= ny < self.h):
                        return True
                    return self.px[ny][nx] is None or self.tag[ny][nx] != t
                if edge(0, -1) or edge(-1, 0):
                    out[y][x] = shade(c, strength)
                elif edge(0, 1) or edge(1, 0):
                    out[y][x] = shade(c, -strength)
        self.px = out

    def texture(self, seed, amount=0.08, tags=None):
        rnd = random.Random(seed)
        for y in range(self.h):
            for x in range(self.w):
                c = self.px[y][x]
                if c is None or (tags and self.tag[y][x] not in tags):
                    continue
                r = rnd.random()
                if r < amount:
                    self.px[y][x] = shade(c, -0.12)
                elif r > 1 - amount * 0.6:
                    self.px[y][x] = shade(c, 0.10)

    def flip(self):
        c = Canvas(self.w, self.h)
        for y in range(self.h):
            c.px[y] = self.px[y][::-1]
            c.tag[y] = self.tag[y][::-1]
        return c

    def image(self):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for y in range(self.h):
            for x in range(self.w):
                c = self.px[y][x]
                if c is not None:
                    img.putpixel((x, y), tuple(c) if len(c) == 4 else tuple(c) + (255,))
        return img

    def blit(self, other, ox, oy):
        for y in range(other.h):
            for x in range(other.w):
                c = other.px[y][x]
                if c is not None:
                    self.put(ox + x, oy + y, c, other.tag[y][x])


def point_in_poly(x, y, pts):
    inside = False
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside


def dither(x, y, t):
    """Ordered 2x2 dither threshold."""
    m = [[0.25, 0.75], [1.0, 0.5]]
    return t >= m[y % 2][x % 2]


# ---------------------------------------------------------------------------------------------------------------
# Owner's licensed 2D library (not redistributable: outputs go to git-ignored game/assets/ext/).
# ASHEN_LIB points at a mirror of "G:\All 2D Assets Stay Here" (same relative layout).
import os as _os

LIB_ROOT = _os.environ.get("ASHEN_LIB", "/home/claude/lib/root")
LICENSES = {
    "finalbossblues": "Time Fantasy (finalbossblues / timefantasy.net) - owner-licensed; use in games allowed, "
                      "raw files not redistributed; credit finalbossblues",
    # Only characters/Elements Character Generator (+ elements character expansion) is used from this folder:
    # Time Fantasy "Elements" character kit by Jason Perry (finalbossblues); its guide covers use in your own game
    # engine. Other packs in characters/ (e.g. the non-commercial Mystic Woods files) are NOT used.
    "characters/Elements Character Generator": "Time Fantasy Elements character kit (finalbossblues / timefantasy.net) - owner-licensed; use in "
                  "games in any engine allowed, raw files not redistributed; credit finalbossblues",
    "ansimuz": "Ansimuz Legacy Collection (ansimuz.itch.io/gothicvania-patreon-collection) - free for commercial games "
               "(creator's statement on the itch page: 'You can use it commercially'); credit ansimuz",
    "characters":  # monster packs in other characters/ subfolders
         "Pixel monster packs (Stone Golem, Huge Knight, Headless Horseman, Cerberus, Gargoyle, Gryphon, Imp, Witch) - "
                  "per-pack License.txt: 'You can use this asset in any game project, personal or commercial'; "
                  "no resale/redistribution as a game asset, no NFTs",
    "Fantasy_Overworld_-_Other_Engines.zip": "Winlu Fantasy Tileset - Overworld by WinLu (winlu.itch.io/fantasy-overworld), "
               "'Other Engines' edition - 'can be used in commercial projects', may be edited; no redistribution/resale; "
               "credit appreciated. 48px art reduced to 16px",
    "RPGMAKERASSETS/craftpix-net-169442-free-2d-top-down-pixel-dungeon-asset-pack.zip":
               "CraftPix.net free 2D top-down pixel dungeon pack - CraftPix file licence (craftpix.net/file-licenses): "
               "use in commercial games; no redistribution of the raw files",
    "SakPix": "SakPix Stage Assets (sakpix.itch.io) - owner-stated as usable; the store pages state no explicit licence "
              "(the SakPix character packs ship a CC0 licence); AI-assisted art, reduced to 16px scale. OWNER TO CONFIRM",
    "haydeos": "Factory Monster Pack 1 by Haydeos (haydeos.itch.io/factory-monster-pack-1) - 'You may use these assets in "
               "any commercial or non-commercial game project'; any engine; credit appreciated",
}


def lib_path(rel):
    return _os.path.join(LIB_ROOT, *rel.replace("\\", "/").split("/"))


_lib_cache = {}


def lib_img(rel):
    """Load a library image as RGBA (cached). Raises FileNotFoundError when the library is not installed.
    A path through an archive ("pack.zip/inner/file.png") is read from inside the zip without extracting it."""
    if rel not in _lib_cache:
        if ".zip/" in rel:
            import io, zipfile
            zp, inner = rel.split(".zip/", 1)
            with zipfile.ZipFile(lib_path(zp + ".zip")) as zf:
                _lib_cache[rel] = Image.open(io.BytesIO(zf.read(inner))).convert("RGBA")
        else:
            _lib_cache[rel] = Image.open(lib_path(rel)).convert("RGBA")
    return _lib_cache[rel]


def lib_available(rel="finalbossblues"):
    return _os.path.exists(lib_path(rel))


def pack_of(rel):
    """Most specific LICENSES key that prefixes the library-relative path (falls back to the top folder)."""
    rel = rel.replace("\\", "/")
    keys = [k for k in LICENSES if rel == k or rel.startswith(k.rstrip("/") + "/")]
    return max(keys, key=len) if keys else rel.split("/")[0]
