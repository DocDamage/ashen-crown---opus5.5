"""World v2 generator (docs/expansion/WORLD_V2.md): builds the collision/terrain grids and entities for
WORLD (pre-fault surface), WORLD_POST (World of Ruin), DEEP and DEEP_POST (the underground) at 176 x 132 cells.

Everything is authored as data here (coast polygons, mountain ranges, rivers, region areas, places, passes, ferries);
noise only roughens edges. Region borders are sealed with ridges except at authored passes, so chapter gates are
real. Roads are routed with A* over terrain cost plus noise, so they wind with the land. `validate()` checks that
each chapter's reachable set is exactly the places that chapter allows.

Output: content_src/maps/world2.map (raw grids + entities; tools/maps48/world.py bakes the art).
"""
import heapq, json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 176, 132
RNG = random.Random(1791)


# ---------------------------------------------------------------- noise helpers
def value_noise(h, w, cell, seed):
    rng = np.random.RandomState(seed)
    gh, gw = h // cell + 2, w // cell + 2
    g = rng.rand(gh, gw)
    ys = np.arange(h) / cell
    xs = np.arange(w) / cell
    y0 = ys.astype(int); x0 = xs.astype(int)
    fy = ys - y0; fx = xs - x0
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    top = a * (1 - fx) + b * fx
    bot = c * (1 - fx) + d * fx
    return top * (1 - fy[:, None]) + bot * fy[:, None]


def fbm(h, w, seed, cells=(24, 12, 6, 3)):
    out = np.zeros((h, w))
    amp, tot = 1.0, 0.0
    for i, c in enumerate(cells):
        out += amp * value_noise(h, w, c, seed + i * 17)
        tot += amp
        amp *= 0.5
    return out / tot


def poly_mask(polys, scale=4, warp=2.2, seed=0, blur=1.2):
    """Rasterise polygons (cell coords) at `scale`x with a noise-warped outline, return a bool (H, W) mask."""
    S = scale
    img = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(img)
    for p in polys:
        d.polygon([(x * S, y * S) for x, y in p], fill=255)
    a = np.asarray(img, dtype=np.float32) / 255.0
    # domain warp for ragged coasts
    nx = fbm(H * S, W * S, seed + 1, (48, 20, 8)) - 0.5
    ny = fbm(H * S, W * S, seed + 2, (48, 20, 8)) - 0.5
    yy, xx = np.mgrid[0:H * S, 0:W * S]
    sx = np.clip((xx + nx * warp * S * 4).astype(int), 0, W * S - 1)
    sy = np.clip((yy + ny * warp * S * 4).astype(int), 0, H * S - 1)
    a = a[sy, sx]
    im = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur * S / 2))
    a = np.asarray(im.resize((W, H), Image.BILINEAR), dtype=np.float32) / 255.0
    return a > 0.5


def line_cells(pts, width=1.0, jitter=0.0, seed=0):
    """Cells along a polyline (cell coords) with a radius; returns a set."""
    rng = random.Random(seed)
    out = set()
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) * 3))
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            r = width + (rng.random() - 0.5) * jitter
            ri = int(math.ceil(r))
            for dy in range(-ri, ri + 1):
                for dx in range(-ri, ri + 1):
                    if dx * dx + dy * dy <= r * r + 0.25:
                        cx, cy = int(round(x + dx)), int(round(y + dy))
                        if 0 <= cx < W and 0 <= cy < H:
                            out.add((cx, cy))
    return out


def meander(pts, amp=2.0, seed=0, step=3.0):
    """Subdivide a polyline and push points sideways with smooth noise so rivers and ridges wander."""
    rng = random.Random(seed)
    out = [pts[0]]
    phase = rng.random() * 6.28
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / step))
        nx, ny = (-(y1 - y0) / (L or 1), (x1 - x0) / (L or 1))
        for i in range(1, n + 1):
            t = i / n
            s = math.sin(phase + t * 3.1 + i * 0.7) * amp * math.sin(math.pi * t) + (rng.random() - 0.5) * amp * 0.4
            out.append((x0 + (x1 - x0) * t + nx * s, y0 + (y1 - y0) * t + ny * s))
        phase += 1.3
    return out


# ================================================================ SURFACE (pre-fault) specification
LANDMASSES = {
    "aurel": [(18, 34), (30, 28), (46, 27), (60, 30), (74, 28), (90, 27), (104, 30), (118, 28), (132, 31), (140, 38),
              (144, 50), (141, 62), (145, 74), (144, 88), (140, 98), (130, 104), (118, 108), (106, 110), (98, 116),
              (86, 121), (72, 121), (60, 124), (50, 119), (40, 123), (30, 127), (14, 125), (5, 116), (7, 104), (13, 96),
              (11, 84), (15, 72), (11, 60), (15, 47)],
    "hoarfrost": [(34, 5), (56, 2), (80, 3), (104, 2), (126, 5), (135, 12), (128, 20), (110, 22), (96, 19), (86, 21),
                  (78, 21), (70, 20), (54, 22), (40, 20), (30, 14)],
    "vermilion": [(152, 30), (164, 27), (173, 35), (172, 52), (168, 66), (172, 80), (166, 96), (157, 101), (150, 91),
                  (152, 75), (149, 60), (153, 46)],
    "saltwhistle": [(114, 114), (122, 111), (128, 115), (126, 122), (117, 123)],
    "gullrock": [(136, 111), (142, 110), (144, 115), (139, 118)],
    "winter_isle": [(6, 4), (16, 3), (20, 9), (14, 14), (5, 11)],
}

# region areas on the main continent (first match wins); islands take the region of their landmass
REGIONS_MAIN = [
    ("R08", [(0, 96), (34, 94), (38, 132), (0, 132)]),            # Mirewold, south-west
    ("R08", [(0, 78), (20, 78), (28, 96), (0, 96)]),
    ("R02", [(0, 0), (54, 0), (54, 66), (44, 74), (0, 76)]),      # Cinder Reach, west
    ("R05", [(54, 0), (100, 0), (100, 50), (80, 58), (54, 60)]),  # Pale Basin, north
    ("R04", [(100, 0), (150, 0), (150, 66), (104, 66), (100, 50)]),  # Skyspine, north-east
    ("R03", [(104, 66), (150, 66), (150, 132), (110, 132), (106, 90)]),  # Glass Coast, east
    ("R01", [(0, 0), (176, 0), (176, 132), (0, 132)]),            # Crown March, the rest
]
REGION_OF_LANDMASS = {"hoarfrost": "R09", "winter_isle": "R09", "vermilion": "R07", "saltwhistle": "R06", "gullrock": "R06"}

# base ground, forest density, hill density, forest overlay variant
BIOME = {
    "R01": ("plains", 0.24, 0.16, "forest"), "R02": ("ash", 0.10, 0.34, "forest_autumn"),
    "R03": ("plains", 0.18, 0.12, "forest"), "R04": ("rocky", 0.26, 0.30, "forest_snow"),
    "R05": ("salt", 0.06, 0.12, "forest"), "R06": ("sand", 0.40, 0.08, "jungle"),
    "R07": ("grass2", 0.44, 0.16, "forest_autumn"), "R08": ("olive", 0.30, 0.06, "forest_magic"),
    "R09": ("snow", 0.26, 0.20, "forest_snow"),
}

RANGES = [   # mountain ridges: points, width
    ([(100, 30), (106, 42), (112, 52), (122, 60), (136, 58)], 2.0),
    ([(118, 30), (126, 36), (138, 44)], 1.5),
    ([(20, 30), (26, 42), (22, 52), (16, 62)], 1.6),
    ([(40, 30), (46, 36), (50, 44)], 1.3),
    ([(44, 10), (58, 7), (74, 6), (96, 8), (114, 9), (126, 12)], 1.8),
    ([(160, 40), (166, 54), (164, 70), (160, 84)], 1.6),
    ([(56, 118), (64, 114), (76, 116)], 1.0),
    ([(58, 34), (64, 30), (72, 32)], 1.1),
]
RIVERS = [   # rivers (water cells), from source to mouth
    [(72, 60), (71, 70), (70, 80), (70, 88), (68, 98), (70, 110), (70, 121)],
    [(30, 38), (38, 50), (44, 60), (46, 70), (54, 80), (62, 88), (69, 92)],
    [(118, 64), (126, 72), (134, 80), (145, 84)],
    [(92, 60), (96, 72), (100, 84), (104, 98), (106, 110)],
    [(164, 58), (158, 64), (151, 66)],
]
LAKES = [((96, 50), 3.2), ((62, 104), 2.2), ((22, 104), 2.6), ((30, 116), 2.0), ((158, 88), 2.0)]

# places: id -> (x, y, kind, region). kind drives the landmark sprite; see LOC_SPRITES in bake.
PLACES = {
    # Crown March
    "L_T01": (52, 106, "town", "R01"), "L_D01": (44, 100, "cave", "R01"), "L_N01": (60, 113, "village", "R01"),
    "L_T02": (70, 88, "city", "R01"), "L_N41": (62, 96, "milestone", "R01"), "L_N02": (80, 96, "fort", "R01"),
    "L_N03": (86, 104, "village", "R01"), "L_N04": (92, 113, "chapel", "R01"), "L_N05": (38, 86, "barrow", "R01"),
    "L_D03": (66, 70, "bigtree", "R01"), "L_D09": (78, 80, "tower", "R01"),
    # Cinder Reach
    "L_T03": (34, 50, "town_ash", "R02"), "L_D04": (24, 40, "tower", "R02"), "L_N06": (40, 62, "village", "R02"),
    "L_N07": (22, 56, "cave", "R02"), "L_N08": (32, 34, "shrine", "R02"), "L_N09": (46, 44, "village", "R02"),
    "L_N10": (18, 68, "crater", "R02"), "L_N42": (47, 57, "dam", "R02"),
    # Glass Coast
    "L_T04": (132, 84, "port", "R03"), "L_D05": (136, 101, "tower", "R03"), "L_N11": (124, 98, "village", "R03"),
    "L_N12": (142, 76, "lighthouse", "R03"), "L_N13": (125, 103, "cave", "R03"), "L_N43": (120, 74, "village", "R03"),
    # Skyspine
    "L_D06": (116, 58, "tower", "R04"), "L_T05": (126, 42, "town_cliff", "R04"), "L_N16": (112, 45, "village", "R04"),
    "L_N17": (134, 34, "shrine", "R04"), "L_N18": (104, 37, "cave", "R04"),
    # Pale Basin
    "L_T06": (84, 42, "town_desert", "R05"), "L_D07": (66, 37, "castle", "R05"), "L_D08": (94, 32, "castle_magic", "R05"),
    "L_N19": (74, 49, "village", "R05"), "L_N20": (58, 45, "crystal", "R05"), "L_N21": (96, 46, "lake", "R05"),
    # Mirewold
    "L_N22": (26, 108, "city_dark", "R08"), "L_N23": (34, 99, "gibbet", "R08"), "L_N24": (16, 114, "village", "R08"),
    "L_N25": (12, 100, "cathedral", "R08"), "L_N26": (30, 121, "grove", "R08"),
    # Vermilion Reach
    "L_N27": (153, 62, "village", "R07"), "L_N28": (162, 47, "castle_red", "R07"), "L_N29": (166, 72, "gate", "R07"),
    "L_N30": (158, 86, "grove", "R07"), "L_N31": (158, 35, "ruin", "R07"),
    # Hoarfrost March
    "L_N32": (82, 15, "village", "R09"), "L_N33": (82, 24, "milestone", "R09"), "L_N34": (104, 12, "tower", "R09"),
    "L_N35": (60, 9, "castle_ice", "R09"), "L_N36": (118, 15, "pit", "R09"), "L_D11": (12, 8, "tower", "R09"),
    # Ember Sea isles
    "L_N14": (121, 117, "port", "R06"), "L_N15": (140, 114, "cave", "R06"),
    # the Shattered Choir (sky, reached by cable / airship): locations sit on the Skyspine peaks
    "L_N37": (138, 47, "sky", "R04"), "L_N38": (130, 52, "sky", "R04"),
}

# roads (pairs of places, routed by A*); "hw" = paved Crown highway
ROADS = [
    ("L_T01", "L_D01", "dirt"), ("L_T01", "L_N01", "dirt"), ("L_T01", "L_N41", "dirt"), ("L_N41", "L_T02", "hw"),
    ("L_T02", "L_N02", "hw"), ("L_N02", "L_N03", "dirt"), ("L_N03", "L_N04", "dirt"), ("L_N41", "L_N05", "dirt"),
    ("L_T02", "L_D09", "hw"), ("L_T02", "L_D03", "dirt"), ("L_D03", "L_N06", "dirt"), ("L_N06", "L_T03", "dirt"),
    ("L_T03", "L_D04", "dirt"), ("L_T03", "L_N07", "dirt"), ("L_T03", "L_N08", "dirt"), ("L_T03", "L_N09", "dirt"),
    ("L_N06", "L_N42", "dirt"), ("L_N07", "L_N10", "dirt"),
    ("L_N02", "L_N43", "hw"), ("L_N43", "L_T04", "hw"), ("L_T04", "L_N12", "dirt"), ("L_T04", "L_N11", "dirt"),
    ("L_N11", "L_D05", "dirt"), ("L_N11", "L_N13", "dirt"),
    ("L_D06", "L_N16", "dirt"), ("L_N16", "L_T05", "dirt"), ("L_T05", "L_N17", "dirt"), ("L_N16", "L_N18", "dirt"),
    ("L_T06", "L_D07", "dirt"), ("L_T06", "L_D08", "dirt"), ("L_T06", "L_N19", "dirt"), ("L_D07", "L_N20", "dirt"),
    ("L_T06", "L_N21", "dirt"), ("L_N19", "L_D03", "dirt"),
    ("L_N05", "L_N23", "dirt"), ("L_N23", "L_N22", "dirt"), ("L_N22", "L_N24", "dirt"), ("L_N22", "L_N25", "dirt"),
    ("L_N24", "L_N26", "dirt"),
    ("L_N27", "L_N28", "dirt"), ("L_N27", "L_N29", "dirt"), ("L_N29", "L_N30", "dirt"), ("L_N28", "L_N31", "dirt"),
    ("L_N33", "L_N32", "dirt"), ("L_N32", "L_N35", "dirt"), ("L_N32", "L_N34", "dirt"), ("L_N34", "L_N36", "dirt"),
    ("L_T06", "L_N33", "dirt"),
]

# passes through the sealed region borders: (x, y, width, dir, cond, msg). The road is forced through them.
PASSES = [
    ((69, 78), "v", "ch:CH02", "The north road to Rootward is closed by a ministry barricade."),
    ((50, 70), "h", "ch:CH03", "The Cinder Pass checkpoint turns back anyone without a work permit."),
    ((104, 94), "h", "ch:CH04", "A checkpoint on the east road. The party is wanted in Veyr."),
    ((74, 58), "v", "ch:CH09", "A salt slide blocks the south road from the basin."),
    ((44, 90), "h", "ch:CH06", "Quarantine wardens bar the fen causeway into Mirewold."),
    ((82, 24), "v", "ch:CH10", "The Ice Road has not frozen hard enough to cross."),
]
FERRIES = [   # scene, dock cell, spawn name, spawn cell, facing
    ("FERRY_BELLHARBOR", (144, 86), "ferry_bh", (143, 86), "left"),
    ("FERRY_SKYSPINE", (142, 60), "ferry_sky", (141, 60), "left"),
    ("FERRY_KAMINARI", (147, 64), "ferry_kam", (146, 64), "left"),
    ("FERRY_KAMINARI_BACK", (150, 64), "ferry_kam_e", (151, 64), "right"),
    ("FERRY_SALTWHISTLE", (130, 104), "ferry_salt", (130, 103), "up"),
    ("FERRY_SALTWHISTLE_BACK", (121, 113), "ferry_salt_s", (121, 114), "down"),
    ("CABLE_AERIE", (104, 48), "cable_aerie", (105, 48), "right"),
    ("CABLE_NACRE", (100, 48), "cable_nacre", (99, 48), "left"),
    ("CABLE_CHOIR", (135, 35), "cable_choir", (135, 36), "down"),
]

# display names (full map, signposts); from docs/expansion/WORLD_V2.md
PLACE_NAMES = {
    "D01": "Crown Quarry", "D02": "Veyr Underways", "D03": "Rootward", "D04": "Furnace Spine",
    "D05": "Drowned Archive", "D06": "Skychain Viaduct", "D07": "Whitebone Redoubt", "D08": "Memory Vault",
    "D09": "Sable Conduit", "D10": "Crown Heart", "D11": "Cradle of Winter", "D12": "Starless Reef",
    "N01": "Hollins Mill", "N02": "Gallowgate Toll", "N03": "Wren's Orchard", "N04": "The Sunken Chapel",
    "N05": "Ashward Barrows", "N06": "Kettle Row", "N07": "The Slagfalls", "N08": "Anvil Cairn",
    "N09": "Pipewright's Rest", "N10": "Cindermaw Caldera", "N11": "Tidewrack", "N12": "Belltower Point",
    "N13": "The Brine Stair", "N14": "Saltwhistle Isle", "N15": "Gullrock", "N16": "Windrest",
    "N17": "The Ninefold Shrine", "N18": "Eyrie Hollow", "N19": "Lilac Seep", "N20": "The Glass Orchard",
    "N21": "Sorrowmere", "N22": "Harrowfen", "N23": "The Gibbet Road", "N24": "Sickle Hamlet",
    "N25": "The Leech Cathedral", "N26": "Moth Hollow", "N27": "Kaminari Ford", "N28": "Akagane, the Fox Court",
    "N29": "Thousand Gates", "N30": "The Whispering Maples", "N31": "Shiroyama Watch", "N32": "Rimeholt",
    "N33": "The Ice Road", "N34": "Glacier Spire", "N35": "Coldharbour Citadel", "N36": "The Aurora Pit",
    "N37": "Choir Anchorage", "N38": "The Crucible Isle (Arena)", "N39": "Seraphel, Fallen Host",
    "N40": "The Broken Organ", "N41": "Oathstone Crossroads", "N42": "The Weeping Dam", "N43": "Lanternfall",
    "P01": "Spine of Ilyrath", "P02": "The Tessellate", "P05": "Refuge Rock", "P09": "The Last Beacon",
    "T01": "Brackenford", "T02": "Veyr", "T03": "Cinderwake", "T04": "Bellharbor", "T05": "High Aerie",
    "T06": "Nacre", "T07": "Hearthward", "U01": "The Breach (quarry floor)", "U02": "Karag Dun", "U03": "Emberwell",
    "U04": "The Geode Wood", "U05": "Ossuary of Wings", "U06": "Magma Ferry", "U07": "Cinderlake Isles",
    "U08": "The Crown Dig", "U09": "Hearthroot Shrine", "U10": "Drakesleep Hollow", "U11": "Vaultmouth Rail",
    "U12": "Deepforge Mines", "U13": "Scaleward", "U14": "The Singing Chasm", "U15": "Fungal Terraces",
    "U16": "Lattice Gate", "U17": "Meridian", "U18": "The Assembly Floors", "U19": "Railhead Nine",
    "U20": "The Datum Archive", "U21": "Glasswater Reservoir", "U22": "The Highway That Was", "U23": "Vault Omega",
    "U24": "Prime Relay", "U25": "Shutdown Town", "U26": "Mag-rail Terminus", "U27": "The Sunless Garden",
    "U28": "Styx Landing", "U29": "Cenotaph", "U30": "The Bone Bridges", "U31": "Sepulchre Court",
    "U32": "Abyss Gate", "U33": "The First Crown's Tomb", "U34": "Mourner's Vale", "U35": "The Lich Stair",
    "U36": "Velkhar's Crypt-Gate", "U37": "Weeping Mines", "U38": "The Silent Choir", "U39": "Hollow Heart",
    "U40": "Undersea Throat",
}


# ================================================================ generation
SOLID_K = {"mountain", "water", "deep", "lava", "chasm", "wall_rock", "void"}
COST = {"plains": 1.0, "grass2": 1.1, "sand": 1.2, "salt": 1.1, "snow": 1.4, "ash": 1.3, "olive": 1.3, "rocky": 1.4,
        "forest": 2.4, "hills": 2.8, "swamp": 3.0, "ice": 1.6, "path": 0.35, "road": 0.3, "bridge": 0.35, "cave_floor": 1.0,
        "moss": 1.2, "ruin_floor": 1.0, "bone": 1.2, "crystal_floor": 1.4, "cinder": 1.3}


def in_poly(poly, x, y):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside


class World:
    def __init__(self, mid, name, music, enc_default):
        self.id, self.name, self.music, self.enc = mid, name, music, enc_default
        self.kind = [["deep"] * W for _ in range(H)]
        self.region = [[None] * W for _ in range(H)]
        self.ents = []
        self.road = set()
        self.keep_open = set()

    def set(self, x, y, k):
        if 0 <= x < W and 0 <= y < H:
            self.kind[y][x] = k

    def get(self, x, y):
        return self.kind[y][x] if 0 <= x < W and 0 <= y < H else "deep"

    def walkable(self, x, y):
        return self.get(x, y) not in SOLID_K


def build_surface_pre():
    w = World("WORLD", "The Crown March and Beyond", "M017", "OW1")
    land = np.zeros((H, W), bool)
    lm_of = np.full((H, W), "", dtype=object)
    for i, (name, poly) in enumerate(LANDMASSES.items()):
        m = poly_mask([poly], warp=2.4 if name in ("aurel", "hoarfrost", "vermilion") else 1.0, seed=31 + i * 7)
        land |= m
        lm_of[m] = name
    # sea: water near coasts, deep beyond
    from scipy import ndimage
    dist = ndimage.distance_transform_edt(~land)
    rwx = (fbm(H, W, 505, (24, 12, 6)) - 0.5) * 34
    rwy = (fbm(H, W, 606, (24, 12, 6)) - 0.5) * 34
    for y in range(H):
        for x in range(W):
            if land[y, x]:
                lm = lm_of[y, x]
                reg = REGION_OF_LANDMASS.get(lm)
                if reg is None:
                    for rid, poly in REGIONS_MAIN:
                        if in_poly(poly, x + 0.5 + rwx[y, x], y + 0.5 + rwy[y, x]):
                            reg = rid
                            break
                w.region[y][x] = reg
                w.kind[y][x] = BIOME[reg][0]
            else:
                w.kind[y][x] = "water" if dist[y, x] <= 3 else "deep"
    # every place sits inside its own region: a disc around it keeps the declared region (the warp only bends borders)
    for pid, (px, py, kind, preg) in PLACES.items():
        for yy in range(py - 6, py + 7):
            for xx in range(px - 6, px + 7):
                if 0 <= xx < W and 0 <= yy < H and land[yy, xx] and (xx - px) ** 2 + (yy - py) ** 2 <= 36 \
                        and REGION_OF_LANDMASS.get(lm_of[yy, xx]) is None and w.region[yy][xx] != preg:
                    w.region[yy][xx] = preg
                    w.kind[yy][xx] = BIOME[preg][0]
    # coast sand strip on sea-facing edges of temperate regions
    for y in range(H):
        for x in range(W):
            if land[y, x] and w.region[y][x] in ("R01", "R03", "R06", "R07") and dist[y, x] == 0:
                if any(0 <= x + dx < W and 0 <= y + dy < H and not land[y + dy, x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    if RNG.random() < 0.55:
                        w.kind[y][x] = "sand"
    # biome overlays: forests and hills by noise
    nf = fbm(H, W, 101, (9, 5, 2))
    nh = fbm(H, W, 202, (8, 4, 2))
    for y in range(H):
        for x in range(W):
            reg = w.region[y][x]
            if not reg:
                continue
            _, fd, hd, _ = BIOME[reg]
            if nf[y, x] > 0.70 - fd * 0.45:
                w.kind[y][x] = "forest"
            elif nh[y, x] > 0.72 - hd * 0.4:
                w.kind[y][x] = "hills"
    # Mirewold marsh pools and swamp ground
    ns = fbm(H, W, 303, (6, 3))
    for y in range(H):
        for x in range(W):
            if w.region[y][x] == "R08" and w.kind[y][x] not in ("forest",):
                if ns[y, x] > 0.7:
                    w.kind[y][x] = "water"
                elif ns[y, x] > 0.52:
                    w.kind[y][x] = "swamp"
    # mountain ranges with a hills fringe
    for i, (pts, wd) in enumerate(RANGES):
        core = line_cells(meander(pts, 2.0, 40 + i), wd, 1.2, 60 + i)
        fringe = line_cells(meander(pts, 2.0, 40 + i), wd + 1.6, 1.4, 80 + i)
        for (x, y) in fringe:
            if land[y, x] and w.kind[y][x] not in ("water",):
                w.kind[y][x] = "hills"
        for (x, y) in core:
            if land[y, x]:
                w.kind[y][x] = "mountain"
    # lakes and rivers
    river = set()
    for (cx, cy), r in LAKES:
        for y in range(H):
            for x in range(W):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and land[y, x]:
                    w.kind[y][x] = "water"
                    river.add((x, y))
    for i, pts in enumerate(RIVERS):
        cells = line_cells(meander(pts, 1.8, 90 + i, 2.5), 0.55, 0.2, 95 + i)
        river |= cells
    for (x, y) in river:
        if land[y, x]:
            w.kind[y][x] = "water"
    # the Ice Road: a frozen lane across the northern strait (gated until CH10)
    for y in range(18, 30):
        for x in (81, 82, 83):
            if not land[y, x] or w.kind[y][x] in ("water", "deep"):
                w.kind[y][x] = "ice"
                land[y, x] = True
                w.region[y][x] = "R09" if y < 24 else "R05"
    w.river = river
    w.land = land
    return w


REGION_GATES = {   # region pair -> (condition, message) for every road crossing that border
    ("R01", "R02"): ("ch:CH03", "The Cinder Pass checkpoint turns back anyone without a work permit."),
    ("R01", "R03"): ("ch:CH04", "A checkpoint on the east road. The party is wanted in Veyr."),
    ("R01", "R05"): ("ch:CH09", "A salt slide blocks the road up to the basin."),
    ("R01", "R08"): ("ch:CH05", "Quarantine wardens bar the fen causeway into Mirewold."),
    ("R02", "R05"): ("ch:CH09", "The basin trail is buried under a salt slide."),
    ("R01", "R04"): ("ch:CH07", "Skychain patrols close the mountain road."),
    ("R03", "R04"): ("ch:CH06", "The coast road into the Skyspine washed out in the storms."),
    ("R04", "R05"): ("ch:CH07", "The high road is closed until the cable is working."),
    ("R05", "R09"): ("ch:CH09", "The Ice Road has not frozen hard enough to cross."),
}


def seal_borders(w):
    """A ridge wherever two main-continent regions meet, except where a road crosses (gate blocks go there)."""
    gates = []
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            r = w.region[y][x]
            if not r:
                continue
            for dx, dy in ((1, 0), (0, 1)):
                r2 = w.region[y + dy][x + dx]
                if r2 and r2 != r:
                    for (cx, cy) in ((x, y), (x + dx, y + dy)):
                        if (cx, cy) in w.road:
                            key = tuple(sorted((r, r2)))
                            gates.append(((cx, cy), key))
                            continue
                        if w.kind[cy][cx] not in ("water", "deep", "bridge"):
                            w.kind[cy][cx] = "mountain"
    seen = set()
    for (c, key) in gates:
        if c in seen:
            continue
        seen.add(c)
        g = REGION_GATES.get(key)
        if g:
            w.ents.append({"t": "block", "x": c[0], "y": c[1], "cond": g[0], "msg": g[1]})
        else:
            print("ungated border crossing", key, c)


def astar(w, a, b, noise, prefer_road=True):
    """8-dir A* over terrain cost; river water can be crossed (becomes a bridge), sea cannot."""
    def cost(x, y):
        k = w.kind[y][x]
        if (x, y) in w.road:
            return 0.35
        if k in ("water",) and (x, y) in w.river:
            return 7.0
        if k in SOLID_K:
            return None
        return COST.get(k, 1.5) * (0.7 + 0.8 * noise[y, x])
    openh = [(0, a)]
    g = {a: 0.0}
    came = {}
    while openh:
        _, cur = heapq.heappop(openh)
        if cur == b:
            break
        cx, cy = cur
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = cx + dx, cy + dy
            if not (0 <= nx < W and 0 <= ny < H):
                continue
            c = cost(nx, ny)
            if c is None:
                continue
            if dx and dy:
                # a diagonal must be walkable through at least one side (4-dir movement)
                if cost(cx + dx, cy) is None and cost(cx, cy + dy) is None:
                    continue
                c *= 1.42
            ng = g[cur] + c
            if ng < g.get((nx, ny), 1e18):
                g[(nx, ny)] = ng
                came[(nx, ny)] = cur
                heapq.heappush(openh, (ng + 0.9 * math.hypot(b[0] - nx, b[1] - ny), (nx, ny)))
    if b not in came and a != b:
        return None
    path = [b]
    while path[-1] != a:
        path.append(came[path[-1]])
    path.reverse()
    # 4-connect diagonal steps (pick the side that is cheaper / walkable)
    out = [path[0]]
    for p in path[1:]:
        q = out[-1]
        if p[0] != q[0] and p[1] != q[1]:
            s1, s2 = (p[0], q[1]), (q[0], p[1])
            k1, k2 = w.get(*s1), w.get(*s2)
            s = s1 if (k1 not in SOLID_K or (k1 == "water" and s1 in w.river)) else s2
            out.append(s)
        out.append(p)
    return out


def place_roads(w, places, roads, passes):
    noise = fbm(H, W, 777, (10, 5, 2))
    for a, b, kind in roads:
        pa = places[a][:2]; pb = places[b][:2]
        path = astar(w, pa, pb, noise)
        if path is None:
            print("NO ROAD", a, b)
            continue
        for (x, y) in path:
            k = w.get(x, y)
            if (x, y) in w.river or k == "water":
                w.set(x, y, "bridge")
            elif (x, y) not in [pp[:2] for pp in places.values()]:
                w.set(x, y, "road" if kind == "hw" else "path")
            w.road.add((x, y))


def add_places(w, places, conds):
    for lid, (x, y, kind, reg) in places.items():
        if kind == "sky":
            continue
        # clear a small clearing around the landmark (arrival spawn south of it)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                cx, cy = x + dx, y + dy
                if abs(dx) + abs(dy) > 3:
                    continue
                if w.get(cx, cy) in ("mountain", "forest", "hills", "swamp") or (w.get(cx, cy) == "water" and (cx, cy) in getattr(w, "river", set())):
                    w.set(cx, cy, BIOME.get(reg, ("plains",))[0])
        w.keep_open |= {(x, y), (x, y + 1)}


COLORS = {"wall_rock": (40, 34, 30), "ruin_floor": (120, 120, 130), "bone": (150, 140, 160), "crystal_floor": (140, 90, 190), "deep": (18, 40, 96), "water": (40, 92, 160), "plains": (96, 160, 72), "grass2": (150, 150, 60), "sand": (220, 204, 140),
          "salt": (226, 220, 232), "snow": (238, 242, 250), "ash": (110, 96, 88), "olive": (100, 120, 60), "rocky": (140, 140, 120),
          "forest": (30, 100, 40), "hills": (150, 130, 80), "mountain": (100, 80, 60), "swamp": (70, 90, 70), "path": (190, 150, 90),
          "road": (200, 200, 200), "bridge": (160, 110, 60), "ice": (170, 220, 240), "lava": (230, 90, 20), "cave_floor": (90, 70, 60)}


def preview(w, places, path, scale=5):
    img = Image.new("RGB", (W * scale, H * scale))
    d = ImageDraw.Draw(img)
    for y in range(H):
        for x in range(W):
            k = w.kind[y][x]
            c = COLORS.get(k, (255, 0, 255))
            if k == "forest" and w.region[y][x] in ("R07",):
                c = (170, 70, 30)
            if k == "forest" and w.region[y][x] in ("R09", "R04"):
                c = (60, 110, 90)
            d.rectangle((x * scale, y * scale, x * scale + scale - 1, y * scale + scale - 1), fill=c)
    for lid, (x, y, kind, reg) in places.items():
        d.rectangle((x * scale - 3, y * scale - 3, x * scale + scale + 2, y * scale + scale + 2), outline=(255, 0, 0), width=2)
        d.text((x * scale + 6, y * scale - 4), lid[2:], fill=(255, 255, 255))
    for e in w.ents:
        if e.get("t") == "block":
            x, y = e["x"], e["y"]
            d.rectangle((x * scale, y * scale, x * scale + scale, y * scale + scale), fill=(255, 0, 255))
    img.save(path)



# ================================================================ entities
OPENS = {"N01": "CH01", "N02": "CH02", "N03": "CH03", "N04": "CH03", "N05": "CH06", "N06": "CH04", "N07": "CH04",
         "N08": "CH04", "N09": "CH05", "N10": "CH10", "N11": "CH05", "N12": "CH05", "N13": "CH06", "N14": "CH06",
         "N15": "CH06", "N16": "CH07", "N17": "CH07", "N18": "CH08", "N19": "CH09", "N20": "CH09", "N21": "CH09",
         "N22": "CH06", "N23": "CH06", "N24": "CH06", "N25": "CH10", "N26": "CH10", "N27": "CH10", "N28": "CH10",
         "N29": "CH10", "N30": "CH10", "N31": "CH11", "N32": "CH10", "N33": "CH10", "N34": "CH11", "N35": "CH11",
         "N36": "CH11", "N37": "CH07", "N38": "CH08", "N41": "CH02", "N42": "CH05", "N43": "CH06"}
PREV = {"CH01": None, "CH02": "CH01", "CH03": "CH02", "CH04": "CH03", "CH05": "CH04", "CH06": "CH05", "CH07": "CH06",
        "CH08": "CH07", "CH09": "CH08", "CH10": "CH09", "CH11": "CH10"}


def old_entities(mid):
    import re
    txt = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "world_old.map")).read()
    for sec in re.split(r"(?m)^=== ", txt)[1:]:
        if sec.split("\n")[0].strip() == mid:
            return [l for l in sec.split("entities:\n", 1)[1].split("\n") if l.strip() and not l.startswith("#")]
    return []


def free_near(w, x, y, avoid=()):
    for r in range(1, 6):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if abs(dx) + abs(dy) != r:
                    continue
                c = (x + dx, y + dy)
                if w.walkable(*c) and c not in avoid:
                    return c
    return (x, y + 1)


def zone_rects(w, group_of):
    """Greedy rectangles covering land cells by encounter group."""
    done = [[False] * W for _ in range(H)]
    out = []
    for y in range(H):
        for x in range(W):
            if done[y][x]:
                continue
            g = group_of(x, y)
            if not g:
                done[y][x] = True
                continue
            x1 = x
            while x1 + 1 < W and not done[y][x1 + 1] and group_of(x1 + 1, y) == g:
                x1 += 1
            y1 = y
            while y1 + 1 < H and all(not done[y1 + 1][xx] and group_of(xx, y1 + 1) == g for xx in range(x, x1 + 1)):
                y1 += 1
            for yy in range(y, y1 + 1):
                for xx in range(x, x1 + 1):
                    done[yy][xx] = True
            out.append((x, x1, y, y1, g))
    return out


def ferry_dock(w, dock, spawn, cable=False):
    """A ferry pier: the walkable shore cell nearest the planned spawn, and the water cell beside it made a plank
    pier (the trigger). Cable stations stand on land: trigger on the spawn's neighbour cell."""
    best = None
    for r in range(0, 9):
        for yy in range(spawn[1] - r, spawn[1] + r + 1):
            for xx in range(spawn[0] - r, spawn[0] + r + 1):
                if not (1 <= xx < W - 1 and 1 <= yy < H - 1) or not w.walkable(xx, yy) or w.kind[yy][xx] == "bridge":
                    continue
                nbw = [(xx + ax, yy + ay) for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1))
                       if w.kind[yy + ay][xx + ax] in ("water", "deep")]
                if cable:
                    nbw = [(xx + ax, yy + ay) for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)) if w.walkable(xx + ax, yy + ay)]
                if nbw:
                    d = min(nbw, key=lambda c: abs(c[0] - dock[0]) + abs(c[1] - dock[1]))
                    cand = (abs(xx - spawn[0]) + abs(yy - spawn[1]), (d, (xx, yy)))
                    if best is None or cand[0] < best[0]:
                        best = cand
        if best:
            break
    if not best:
        return dock, spawn
    d, sp = best[1]
    if not cable:
        w.kind[d[1]][d[0]] = "bridge"
    return d, sp


def surface_entities(w, post=False):
    lines = []
    places = PLACES_POST if post else PLACES
    old = old_entities("WORLD_POST" if post else "WORLD")
    old_loc = {}
    for l in old:
        p = l.split()
        if p[0] == "location":
            old_loc[p[1]] = l
    occupied = {(v[0], v[1]) for v in places.values()}
    for lid, (x, y, kind, reg) in places.items():
        key = lid[2:]
        if lid in old_loc:
            p = old_loc[lid].split()
            rest = " ".join(p[4:])
            lines.append("location %s %d %d %s" % (lid, x, y, rest))
        else:
            ch = OPENS.get(key)
            dest = "%s_R01" % key
            cond = (" if=ch:%s" % PREV[ch]) if (ch and PREV.get(ch)) else ""
            if post and key in POST_ONLY_OPENS:
                cond = " if=ch:%s" % POST_ONLY_OPENS[key]
            lines.append("location %s %d %d dest=%s spawn=world%s" % (lid, x, y, dest, cond))
        if kind != "sky":
            sx, sy = free_near(w, x, y, occupied)
            lines.append("spawn l_%s %d %d down" % (key.lower(), sx, sy))
    # gate scenes that fired at the old location cells follow their location
    for l in old:
        p = l.split()
        if p[0] == "trigger" and "scene=GATE_" in l:
            gate = l.split("scene=")[1].split()[0]
            lid = "L_" + gate[5:]
            if lid in places:
                x, y = places[lid][:2]
                lines.append("trigger %d %d scene=%s" % (x, y, gate))
    # old custom spawns (town exits use them) -> next to their place
    alias = {"t01": "L_T01", "t02": "L_T02", "default": "L_T07" if post else "L_T01"}
    for l in old:
        p = l.split()
        if p[0] == "spawn" and p[1] in alias and alias[p[1]] in places:
            x, y = places[alias[p[1]]][:2]
            sx, sy = free_near(w, x, y, occupied)
            lines.append("spawn %s %d %d down" % (p[1], sx, sy))
    for scene, (dx, dy), sp, (sx, sy), face in (FERRIES_POST if post else FERRIES):
        (dx, dy), (sx, sy) = ferry_dock(w, (dx, dy), (sx, sy), scene.startswith("CABLE"))
        lines.append("trigger %d %d scene=%s" % (dx, dy, scene))
        lines.append("spawn %s %d %d %s" % (sp, sx, sy, face))
    for e in w.ents:
        if e["t"] == "block":
            lines.append('block %d %d tile=gate if=!%s msg="%s"' % (e["x"], e["y"], e["cond"], e["msg"]))
        elif e["t"] == "line":
            lines.append(e["text"])
    # landing fields near the towns (airships)
    for lid in LANDINGS_POST if post else LANDINGS:
        if lid not in places:
            continue
        x, y = places[lid][:2]
        best = None
        for r in range(2, 9):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    cx, cy = x + dx, y + dy
                    if all(w.walkable(cx + i, cy + j) and (cx + i, cy + j) not in occupied for i in range(3) for j in range(2)):
                        best = (cx, cy)
                        break
                if best:
                    break
            if best:
                break
        if best:
            nm = LANDING_NAMES.get(lid, lid[2:])
            tag = "" if post else "  #! ov:wayfarer"
            lines.append('landing %d..%d %d..%d name="%s"%s' % (best[0], best[0] + 2, best[1], best[1] + 1, nm, tag))
            # the airship's home berth (field.gd parks it here; "helm" boards it)
            if lid == ("L_T07" if post else "L_T06"):
                lines.append("spawn berth %d %d down" % (best[0] + 1, best[1]))
                if post:
                    lines.append("spawn helm %d %d down" % (best[0] + 1, best[1]))
    # encounter zones by region (and terrain for forests/snow)
    def grp(x, y):
        r = w.region[y][x]
        if not r or not w.walkable(x, y):
            return None
        return ("WP_" if post else "W_") + r
    for (x0, x1, y0, y1, g) in zone_rects(w, grp):
        lines.append("zone %d..%d %d..%d enc=%s" % (x0, x1, y0, y1, g))
    return lines


LANDINGS = ["L_T01", "L_T02", "L_D03", "L_T03", "L_T04", "L_T05", "L_T06", "L_D07", "L_D06", "L_D08", "L_N22", "L_N28",
            "L_N32", "L_N14", "L_N11"]
LANDING_NAMES = {"L_T01": "Brackenford", "L_T02": "Veyr", "L_D03": "Rootward", "L_T03": "Cinderwake", "L_T04": "Bellharbor",
                 "L_T05": "High Aerie", "L_T06": "Nacre", "L_D07": "Whitebone", "L_D06": "Skychain", "L_D08": "Vault Road",
                 "L_N22": "Harrowfen", "L_N28": "Akagane", "L_N32": "Rimeholt", "L_N14": "Saltwhistle", "L_N11": "Tidewrack",
                 "L_T07": "Hearthward", "L_D10": "Crown Heart", "L_D11": "Winter Island", "L_D12": "Reef Shoal",
                 "L_D05": "Archive Point", "L_P01": "Spine of Ilyrath", "L_P02": "Tessellate", "L_P05": "Refuge Rock",
                 "L_P09": "Last Beacon", "L_N38": "Crucible Isle", "L_N37": "Choir Anchorage", "L_N39": "Seraphel",
                 "L_N36": "Aurora Pit", "L_N35": "Coldharbour"}


# ================================================================ WORLD OF RUIN (post-fault surface)
DESTROYED = {"L_N06", "L_N09", "L_N43"}   # Kettle Row, Pipewright's Rest, Lanternfall
RIFT = [(97, 124), (95, 106), (90, 92), (84, 80), (76, 68), (64, 61), (52, 64), (44, 70)]
RIFT_W = [(58, 62), (48, 66)]
GLASS_CHANNELS = [[(116, 68), (124, 80), (132, 92), (138, 104)], [(130, 72), (142, 70)], [(122, 96), (146, 96)]]
HOAR_CRACK = [(96, 3), (106, 9), (118, 15), (128, 20)]
VEYR_MOAT = ((70, 88), 5.5)
RISEN = {   # new land: centre, radius, kind
    "L_P01": ((86, 84), 3.2, "ash"), "L_D10": ((100, 76), 3.0, "rocky"), "L_D12": ((132, 125), 2.6, "sand"),
    "L_T07": ((106, 116), 3.5, "ash"), "L_P05": ((112, 88), 2.6, "rocky"),
}
PLACES_POST = {k: v for k, v in PLACES.items() if k not in DESTROYED}
PLACES_POST.update({
    "L_T07": (106, 116, "port", "R06"), "L_D10": (100, 76, "relay", "R01"), "L_D12": (132, 125, "tower", "R06"),
    "L_P01": (86, 84, "bones", "R01"), "L_P02": (56, 80, "tower_builder", "R01"), "L_P05": (112, 88, "village", "R03"),
    "L_P09": (100, 60, "tower", "R04"), "L_N39": (126, 50, "sky", "R04"),
})
POST_ONLY_OPENS = {"P01": "CH16", "P02": "CH16", "P05": "CH13", "P09": "CH16", "N39": "CH16"}
FERRIES_POST = [
    ("FERRY_HEARTHWARD", (131, 88), "ferry_bh", (131, 87), "up"),
    ("FERRY_BELLHARBOR_POST", (105, 113), "ferry_hw", (105, 112), "up"),
]
LANDINGS_POST = ["L_N15", "L_T07", "L_T01", "L_T02", "L_D03", "L_T03", "L_T04", "L_T05", "L_T06", "L_D07", "L_D06", "L_D08",
                 "L_D10", "L_D11", "L_D12", "L_D05", "L_P01", "L_P02", "L_P05", "L_P09", "L_N22", "L_N28", "L_N32",
                 "L_N14", "L_N35", "L_N36"]


def build_surface_post(pre):
    import copy
    w = World("WORLD_POST", "The World of Ruin", "M018", "OWP")
    w.kind = copy.deepcopy(pre.kind)
    w.region = copy.deepcopy(pre.region)
    w.river = set(pre.river)
    carve = set()
    for i, pts in enumerate([RIFT, RIFT_W]):
        carve |= line_cells(meander(pts, 2.6, 300 + i, 3), 2.6 if i == 0 else 1.6, 1.4, 310 + i)
    for i, pts in enumerate(GLASS_CHANNELS):
        carve |= line_cells(meander(pts, 1.8, 330 + i, 3), 1.3, 0.8, 340 + i)
    carve |= line_cells(meander(HOAR_CRACK, 1.5, 350, 3), 1.4, 0.8, 351)
    (vx, vy), vr = VEYR_MOAT
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - vx, y - vy)
            if vr - 1.6 <= d <= vr:
                carve.add((x, y))
    for (x, y) in carve:
        if w.kind[y][x] not in ("deep",):
            w.kind[y][x] = "water"
    # the Scar: the collapsed causeway that still links the fens to the Cinder Reach across the rift's west end
    for y in range(58, 74):
        for x in (40, 41):
            if w.kind[y][x] == "water":
                w.kind[y][x] = "bridge"
    # destroyed places: flooded, burned
    for lid in DESTROYED:
        x, y = PLACES[lid][:2]
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= 9 and w.kind[y + dy][x + dx] not in ("deep", "water", "mountain"):
                    w.kind[y + dy][x + dx] = "water" if lid == "L_N06" else "ash"
    # risen land
    for lid, ((cx, cy), r, k) in RISEN.items():
        for y in range(H):
            for x in range(W):
                if math.hypot(x - cx, y - cy) <= r:
                    w.kind[y][x] = k
                    w.region[y][x] = w.region[y][x] or PLACES_POST[lid][3]
    # a bone ridge running through the rift (the Spine of Ilyrath)
    for (x, y) in line_cells([(82, 80), (86, 84), (90, 88)], 0.8, 0.4, 360):
        if (x, y) != (86, 84):
            w.kind[y][x] = "mountain"
    # the pre-fault roads survive where land survives; post blocks on the sealed sites
    for lid, msg in (("L_D10", "The Crown Heart relay is surrounded by a pressure storm."),
                     ("L_D11", "A winter island, far to the north. Nacre's listeners say its lantern never goes out."),
                     ("L_D12", "A starless shoal. Harbor bells ring when you pass it.")):
        x, y = PLACES_POST[lid][:2]
        w.ents.append({"t": "line", "text": 'block %d..%d %d..%d tile=reef if=!ch:CH20 msg="%s"' % (x - 1, x + 1, y - 1, y + 1, msg)})
    add_places(w, PLACES_POST, {})
    ensure_access(w, PLACES_POST)
    return w


def ensure_access(w, places):
    """After the fault reshapes the coast: any place cut off from its road by new water gets a plank causeway."""
    import heapq
    for pid, (px, py, kind, reg) in places.items():
        if kind == "sky":
            continue
        if w.kind[py][px] in ("water", "deep", "mountain"):
            w.kind[py][px] = "bridge"   # a drowned site: the approach ends on a pier at its door
        dist = {(px, py): 0}
        prev = {}
        pq = [(0, px, py)]
        goal = None
        while pq:
            d, x, y = heapq.heappop(pq)
            if d > dist.get((x, y), 1e9):
                continue
            if (x, y) != (px, py) and w.kind[y][x] in ("road", "path"):
                goal = (x, y)
                break
            if d > 60:
                break
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < W and 0 <= ny < H):
                    continue
                k = w.kind[ny][nx]
                if k in ("water", "deep", "bridge"):
                    c = 6
                elif w.walkable(nx, ny):
                    c = 1
                else:
                    continue
                nd = d + c
                if nd < dist.get((nx, ny), 1e9):
                    dist[(nx, ny)] = nd
                    prev[(nx, ny)] = (x, y)
                    heapq.heappush(pq, (nd, nx, ny))
        if not goal:
            continue
        c = goal
        n = 0
        while c != (px, py):
            if w.kind[c[1]][c[0]] in ("water", "deep"):
                w.kind[c[1]][c[0]] = "bridge"
                n += 1
            c = prev[c]
        if n:
            print("causeway to", pid, n, "cells")


# ================================================================ writer
LEGEND_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def map_section(w, lines, extra_hdr):
    kinds = sorted({k for row in w.kind for k in row})
    legend = {k: LEGEND_CHARS[i] for i, k in enumerate(kinds)}
    out = ["=== " + w.id, "name: " + w.name, "tileset: world" + ("_post" if w.id.endswith("POST") else ""),
           "music: " + w.music, "kind: world", "save: true", "encounters: " + w.enc, "rate: 0.9"] + extra_hdr
    out.append("legend: " + " ".join("%s=%s" % (c, k) for k, c in legend.items()))
    out.append("grid:")
    for row in w.kind:
        out.append("".join(legend[k] for k in row))
    out.append("entities:")
    out += lines
    return "\n".join(out) + "\n"


def reach_by_chapter(w, lines):
    """Walkable reach from the Brackenford spawn with gates closed by chapter (for validate)."""
    from collections import deque
    blocks = []
    for l in lines:
        if l.startswith("block "):
            p = l.split()
            cond = [t for t in p if t.startswith("if=")][0][4:]
            xs, ys = p[1], p[2]
            x0, x1 = (int(xs.split("..")[0]), int(xs.split("..")[1])) if ".." in xs else (int(xs), int(xs))
            y0, y1 = (int(ys.split("..")[0]), int(ys.split("..")[1])) if ".." in ys else (int(ys), int(ys))
            blocks.append((x0, x1, y0, y1, cond))
    res = {}
    chs = ["CH01", "CH02", "CH03", "CH04", "CH05", "CH06", "CH07", "CH08", "CH09", "CH10", "CH11"]
    for i, ch in enumerate(chs):
        done = set(chs[:i])
        closed = set()
        for (x0, x1, y0, y1, cond) in blocks:
            c = cond.lstrip("!")
            active = c.split(":")[1] not in done if c.startswith("ch:") else True
            if active:
                for yy in range(y0, y1 + 1):
                    for xx in range(x0, x1 + 1):
                        closed.add((xx, yy))
        start = PLACES["L_T01"][:2]
        seen = {start}
        q = deque([start])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and w.walkable(*n) and n not in closed:
                    seen.add(n)
                    q.append(n)
        res[ch] = sorted(lid for lid, v in PLACES.items() if (v[0], v[1]) in seen)
    return res


# ================================================================ THE DEEP (underground)
DEEP_PLACES = {
    # U1 Emberdeep (dragon under-realm)
    "L_U01": (44, 100, "breach", "U1"), "L_U02": (30, 80, "city_delver", "U1"), "L_U03": (54, 110, "village", "U1"),
    "L_U04": (20, 96, "crystal", "U1"), "L_U05": (14, 70, "bones", "U1"), "L_U06": (40, 70, "dock", "U1"),
    "L_U07": (28, 56, "village", "U1"), "L_U08": (60, 92, "camp", "U1"), "L_U09": (12, 114, "shrine", "U1"),
    "L_U10": (6, 86, "cave", "U1"), "L_U11": (66, 78, "rail", "U1"), "L_U12": (36, 121, "mine", "U1"),
    "L_U13": (70, 112, "village", "U1"), "L_U14": (50, 84, "chasm", "U1"), "L_U15": (26, 108, "village", "U1"),
    # U2 The Lattice (builder cities)
    "L_U16": (80, 82, "gate_builder", "U2"), "L_U17": (100, 86, "city_builder", "U2"), "L_U18": (116, 96, "factory", "U2"),
    "L_U19": (92, 102, "rail", "U2"), "L_U20": (130, 80, "archive", "U2"), "L_U21": (120, 112, "dock", "U2"),
    "L_U22": (140, 96, "road", "U2"), "L_U23": (136, 66, "vault", "U2"), "L_U24": (112, 70, "relay", "U2"),
    "L_U25": (150, 110, "city_dead", "U2"), "L_U26": (104, 58, "rail", "U2"), "L_U27": (86, 64, "grove", "U2"),
    # U3 The Hollow Throne (realm of the dead)
    "L_U28": (70, 40, "dock", "U3"), "L_U29": (90, 30, "city_dead", "U3"), "L_U30": (110, 34, "bridge", "U3"),
    "L_U31": (130, 20, "palace", "U3"), "L_U32": (150, 30, "gate_abyss", "U3"), "L_U33": (58, 20, "tomb", "U3"),
    "L_U34": (80, 48, "village", "U3"), "L_U35": (100, 12, "tower_ice", "U3"), "L_U36": (42, 32, "crypt", "U3"),
    "L_U37": (120, 46, "mine", "U3"), "L_U38": (162, 14, "choir", "U3"), "L_U39": (144, 44, "heart", "U3"),
    "L_U40": (158, 56, "throat", "U3"),
}
DEEP_OPENS = {"U1": "CH06", "U2": "CH10"}   # location cond: ch:<done>  (CH07b sits inside CH07)
DEEP_LINKS = [   # tunnels between places: routed as 2-wide passages through rock
    ("L_U01", "L_U08"), ("L_U01", "L_U14"), ("L_U14", "L_U02"), ("L_U02", "L_U06"), ("L_U06", "L_U07"), ("L_U02", "L_U05"),
    ("L_U05", "L_U10"), ("L_U02", "L_U04"), ("L_U04", "L_U15"), ("L_U15", "L_U09"), ("L_U15", "L_U12"), ("L_U01", "L_U03"),
    ("L_U03", "L_U13"), ("L_U08", "L_U11"), ("L_U11", "L_U16"),
    ("L_U16", "L_U17"), ("L_U17", "L_U19"), ("L_U17", "L_U24"), ("L_U24", "L_U26"), ("L_U26", "L_U27"), ("L_U17", "L_U18"),
    ("L_U18", "L_U21"), ("L_U18", "L_U22"), ("L_U22", "L_U25"), ("L_U20", "L_U23"), ("L_U18", "L_U20"),
    ("L_U26", "L_U34"), ("L_U34", "L_U28"), ("L_U28", "L_U36"), ("L_U36", "L_U33"), ("L_U28", "L_U29"), ("L_U29", "L_U35"),
    ("L_U29", "L_U30"), ("L_U30", "L_U37"), ("L_U30", "L_U31"), ("L_U31", "L_U38"), ("L_U31", "L_U32"), ("L_U32", "L_U39"),
    ("L_U39", "L_U40"), ("L_U23", "L_U40"),
]
DEEP_REALM_GATES = {("U1", "U2"): ("ch:CH10", "A builder bulkhead seals the tunnel. It hums, and does not open."),
                    ("U2", "U3"): ("phase:post", "The tunnel ends in black water that swallows the lantern light.")}
DEEP_BIOME = {"U1": "cave_floor", "U2": "ruin_floor", "U3": "bone"}


def build_deep(post=False):
    w = World("DEEP_POST" if post else "DEEP", "The Deep" if not post else "The Deep, Awake", "M023", "W_U1")
    w.kind = [["wall_rock"] * W for _ in range(H)]
    # realm areas: U3 north, U2 centre-east, U1 west/south-west
    wx = (fbm(H, W, 881, (14, 7)) - 0.5) * 16
    wy = (fbm(H, W, 882, (14, 7)) - 0.5) * 12
    for y in range(H):
        for x in range(W):
            xx, yy = x + wx[y, x], y + wy[y, x]
            if yy < 52 and not (xx < 36 and yy > 44):
                r = "U3"
            elif xx < 76:
                r = "U1"
            else:
                r = "U2"
            w.region[y][x] = r
    # caverns: noise blobs per realm, larger around places
    nc = fbm(H, W, 901, (14, 7, 3))
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if nc[y, x] > 0.60:
                w.kind[y][x] = DEEP_BIOME[w.region[y][x]]
    places = DEEP_PLACES
    for lid, (x, y, kind, r) in places.items():
        rad = 6 if kind.startswith("city") or kind in ("palace", "heart") else 4
        for yy in range(y - rad, y + rad + 1):
            for xx in range(x - rad - 1, x + rad + 2):
                if 0 < xx < W - 1 and 0 < yy < H - 1 and (xx - x) ** 2 / 1.3 + (yy - y) ** 2 <= rad * rad + nc[yy, xx] * 6:
                    w.kind[yy][xx] = DEEP_BIOME[r]
    # tunnels
    noise = fbm(H, W, 911, (8, 4, 2))
    road = set()
    for a, b in DEEP_LINKS:
        pa, pb = places[a][:2], places[b][:2]
        path = _tunnel(pa, pb, noise)
        for (x, y) in path:
            for dx, dy in ((0, 0), (1, 0), (0, 1)):
                xx, yy = x + dx, y + dy
                if 0 < xx < W - 1 and 0 < yy < H - 1 and w.kind[yy][xx] == "wall_rock":
                    w.kind[yy][xx] = DEEP_BIOME[w.region[yy][xx]]
            road.add((x, y))
    w.road = road
    # realm features
    nl = fbm(H, W, 921, (10, 5))
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            r = w.region[y][x]
            k = w.kind[y][x]
            if k == "wall_rock" or (x, y) in road:
                continue
            if r == "U1" and nl[y, x] > 0.68:
                w.kind[y][x] = "lava"
            elif r == "U1" and nl[y, x] < 0.30:
                w.kind[y][x] = "crystal_floor"
            elif r == "U3" and nl[y, x] > 0.66:
                w.kind[y][x] = "water"
            elif r == "U2" and (x % 9 in (0, 1) or y % 8 in (0, 1)) and nl[y, x] > 0.45:
                w.kind[y][x] = "road"    # builder streets
    # place cells clear
    for lid, (x, y, kind, r) in places.items():
        for dy in range(-1, 3):
            for dx in range(-1, 2):
                if w.kind[y + dy][x + dx] in ("wall_rock", "lava", "water"):
                    w.kind[y + dy][x + dx] = DEEP_BIOME[r]
    # the fault floods Emberdeep's west in the post-fault Deep
    if post:
        for y in range(40, 80):
            for x in range(8, 40):
                if w.kind[y][x] not in ("wall_rock",) and nl[y, x] > 0.55 and (x, y) not in road:
                    w.kind[y][x] = "lava"
    # realm borders: seal except tunnels (gated)
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            r = w.region[y][x]
            for dx, dy in ((1, 0), (0, 1)):
                r2 = w.region[y + dy][x + dx]
                if r2 != r:
                    for (cx, cy) in ((x, y), (x + dx, y + dy)):
                        if (cx, cy) in road:
                            key = tuple(sorted((r, r2)))
                            g = DEEP_REALM_GATES.get(key)
                            if g and not (post and key == ("U2", "U3")) and not (post and key == ("U1", "U2")):
                                w.ents.append({"t": "block", "x": cx, "y": cy, "cond": g[0], "msg": g[1]})
                        elif w.kind[cy][cx] != "wall_rock":
                            w.kind[cy][cx] = "wall_rock"
    w.river = set()
    return w


def _tunnel(a, b, noise):
    """A* through rock with a noisy cost so tunnels wind."""
    openh = [(0, a)]
    g = {a: 0.0}
    came = {}
    while openh:
        _, cur = heapq.heappop(openh)
        if cur == b:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cur[0] + dx, cur[1] + dy)
            if not (2 <= n[0] < W - 2 and 2 <= n[1] < H - 2):
                continue
            c = 0.5 + 2.2 * noise[n[1], n[0]]
            ng = g[cur] + c
            if ng < g.get(n, 1e18):
                g[n] = ng
                came[n] = cur
                heapq.heappush(openh, (ng + 0.6 * (abs(b[0] - n[0]) + abs(b[1] - n[1])), n))
    path = [b]
    while path[-1] != a:
        path.append(came[path[-1]])
    return path[::-1]


def deep_entities(w, post=False):
    lines = []
    occupied = {(v[0], v[1]) for v in DEEP_PLACES.values()}
    for lid, (x, y, kind, r) in DEEP_PLACES.items():
        key = lid[2:]
        if r == "U3" and not post:
            continue
        cond = "" if post else " if=ch:%s" % DEEP_OPENS[r]
        dest = "D01_R05" if lid == "L_U01" else "%s_R01" % key
        spawn = "from_deep" if lid == "L_U01" else "world"
        lines.append("location %s %d %d dest=%s spawn=%s%s" % (lid, x, y, dest, spawn, cond))
        sx, sy = free_near(w, x, y, occupied)
        lines.append("spawn l_%s %d %d down" % (key.lower(), sx, sy))
    x, y = DEEP_PLACES["L_U01"][:2]
    sx, sy = free_near(w, x, y, occupied)
    lines.append("spawn breach %d %d down" % (sx, sy))
    lines.append("spawn default %d %d down" % (sx, sy))
    for e in w.ents:
        if e["t"] == "block":
            lines.append('block %d %d tile=gate if=!%s msg="%s"' % (e["x"], e["y"], e["cond"], e["msg"]))
    def grp(x, y):
        if not w.walkable(x, y):
            return None
        return ("WP_" if post else "W_") + w.region[y][x]
    for (x0, x1, y0, y1, g) in zone_rects(w, grp):
        lines.append("zone %d..%d %d..%d enc=%s" % (x0, x1, y0, y1, g))
    return lines


def main():
    pre = build_surface_pre()
    add_places(pre, PLACES, {})
    place_roads(pre, PLACES, ROADS, PASSES)
    seal_borders(pre)
    for pid, (x, y, kind, reg) in PLACES.items():
        if pre.region[y][x] != reg:
            print("region mismatch", pid, "declared", reg, "cell", pre.region[y][x])
    pre_lines = surface_entities(pre)
    post = build_surface_post(pre)
    post_lines = surface_entities(post, post=True)
    deep = build_deep(False)
    deep_lines = deep_entities(deep, False)
    deepp = build_deep(True)
    deepp_lines = deep_entities(deepp, True)
    txt = "#! World v2 (tools/world2/wgen.py): surface, World of Ruin and the Deep at 176x132.\n"
    txt += map_section(pre, pre_lines, [])
    txt += map_section(post, post_lines, ["phase: post"])
    txt += map_section(deep, deep_lines, [])
    txt += map_section(deepp, deepp_lines, ["phase: post"])
    out = sys.argv[1] if len(sys.argv) > 1 else "world2.map"
    open(out, "w").write(txt)
    preview(pre, PLACES, "prev_pre.png"); preview(post, PLACES_POST, "prev_post.png")
    preview(deep, DEEP_PLACES, "prev_deep.png"); preview(deepp, DEEP_PLACES, "prev_deep_post.png")
    r = reach_by_chapter(pre, pre_lines)
    prev = set()
    for ch, v in r.items():
        print(ch, "new reach:", sorted(set(v) - prev)); prev = set(v)
    print("wrote", out, len(txt))


if __name__ == "__main__":
    main()
