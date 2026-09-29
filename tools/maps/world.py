"""Two authored overworld states with shared stable location IDs (docs/04).
Capital by the river, coast east, cliffs north-east, basin north; the central relay fault becomes
the Ember Sea after the catastrophe. Walking and vehicle edges are explicit (blocks/landings)."""
import os, sys, random, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 96, 72

LOC = {  # id: (x, y, glyph, pre_dest_map, spawn, post_dest_map)
    "L_T01": (24, 58, "Y", "T01_PLATFORM", "world", "T01_POST"),
    "L_D01": (19, 53, "X", "D01_R01", "from_town", "D01_MEMORIAL"),
    "L_T02": (40, 45, "C", "T02_MARKET", "world", "T02_SQUARE_POST"),
    "L_D03": (36, 30, "F", "D03_R01", "world", "D03P_R01"),
    "L_T03": (20, 18, "Y", "T03_TOWN", "world", "T03_POST"),
    "L_D04": (13, 12, "X", "D04_R01", "world", "D04P_R01"),
    "L_T04": (79, 44, "Y", "T04_QUAY", "world", "T04_UPPER"),
    "L_D05": (86, 51, "X", "D05_R01", "world", "D05P_R01"),
    "L_D06": (70, 22, "X", "D06_R01", "world", "D06P_R01"),
    "L_T05": (80, 13, "Y", "T05_COURT", "world", "T05_POST"),
    "L_D07": (38, 7, "X", "D07_R01", "world", "D07P_R01"),
    "L_T06": (50, 10, "Y", "T06_MARKET", "world", "T06_POST"),
    "L_D08": (57, 5, "X", "D08_R01", "world", "D08P_R01"),
    "L_D09": (46, 41, "X", "D09_R01", "world", ""),
}


def base():
    g = Grid(W, H, "~")
    # continent
    g.blob(46, 36, 42, 31, "P")
    g.blob(14, 20, 14, 16, "P")
    g.blob(80, 20, 15, 14, "P")
    g.blob(50, 8, 26, 8, "P")
    g.blob(26, 62, 18, 9, "P")
    # coasts and shallows
    for y in range(H):
        for x in range(W):
            if g.get(x, y) == "~":
                far = all(g.get(x + dx, y + dy) == "~" for dx in (-2, 0, 2) for dy in (-2, 0, 2))
                if far:
                    g.put(x, y, "K")
    # R05 Pale Basin salt flats (north)
    g.blob(50, 9, 20, 6, "N", only="P")
    g.blob(40, 5, 6, 3, "q", only="PN")
    # R04 Skyspine cliffs and mountains (north-east), separated from the basin by a chasm
    g.blob(78, 18, 12, 9, "H", only="P")
    for i in range(40):
        r = random.Random(400 + i)
        g.put(r.randint(66, 92), r.randint(8, 30), "M")
    g.vline(64, 4, 26, "~")
    g.vline(65, 4, 26, "~")
    # R02 Cinder Reach basalt ridges (north-west)
    g.blob(15, 16, 11, 11, "A", only="P")
    for i in range(30):
        r = random.Random(200 + i)
        g.put(r.randint(4, 28), r.randint(4, 30), "M")
    # mountain wall between Crown March and Cinder Reach with the northern road pass
    g.path([(4, 32), (34, 32)], "M")
    g.path([(30, 26), (30, 33)], "M")
    # R01 Crown March farmland, forests, river
    g.blob(36, 30, 7, 5, "F", only="P")          # Rootward forest
    g.blob(22, 44, 5, 4, "F", only="P")
    g.blob(52, 52, 6, 4, "F", only="P")
    g.blob(30, 60, 5, 3, "H", only="P")
    river = [(28, 6), (30, 14), (34, 22), (38, 34), (41, 43), (40, 50), (34, 58), (30, 66), (28, 71)]
    for (x0, y0), (x1, y1) in zip(river, river[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            g.put(x, y, "~")
    # R03 Glass Coast sand
    g.blob(84, 46, 8, 12, "z", only="P")
    # central relay fault (pre: badlands)
    g.blob(62, 38, 8, 9, "H", only="P")
    g.put(61, 37, "U")
    # roads
    road = [(24, 58), (24, 56), (20, 56), (20, 53)]
    g.path(road, ":")
    g.path([(24, 58), (33, 58), (33, 50), (40, 50), (40, 45)], ":")
    g.path([(40, 45), (40, 36), (36, 36), (36, 30)], ":")
    g.path([(36, 30), (30, 30), (30, 34), (26, 34), (26, 22), (20, 22), (20, 18)], ":")
    g.path([(20, 18), (13, 18), (13, 12)], ":")
    g.path([(40, 45), (52, 45), (70, 45), (79, 45), (79, 44)], ":")
    g.path([(79, 45), (86, 45), (86, 51)], ":")
    g.path([(70, 22), (76, 22), (76, 13), (80, 13)], ":")
    g.path([(50, 10), (44, 10), (44, 7), (38, 7)], ":")
    g.path([(50, 10), (57, 10), (57, 5)], ":")
    g.path([(40, 45), (46, 45), (46, 41)], ":")
    # bridges where roads cross water
    for y in range(H):
        for x in range(W):
            pass
    return g


def bridge_roads(g, pre):
    # re-lay roads across the river as bridges
    for (x, y) in ((33, 58), (40, 47), (40, 48), (38, 36), (37, 36), (35, 30), (34, 30), (29, 14), (30, 14)):
        if g.get(x, y) in ("~", "K"):
            g.put(x, y, "=")


SOLIDW = set("~KMZ")


def free_near(g, x, y):
    for r in range(1, 7):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if g.get(x + dx, y + dy) not in SOLIDW and (dx, dy) != (0, 0) and g.get(x + dx, y + dy) not in "YXCU":
                    return x + dx, y + dy
    return x, y + 1


def spawns(g, extra=()):
    for lid, (x, y, *_r) in list(LOC.items()) + list(extra):
        fx, fy = free_near(g, x, y)
        g.e(f"spawn {lid.lower()} {fx} {fy} down")


# Pre-state location gates: the entrance works when the condition holds; otherwise an authored scene explains why.
# (The overworld is open country; story order is enforced at the doors, not by invisible walls.)
LOC_COND_PRE = {
    "L_T02": ("ch:CH01,!ch:CH02", "GATE_T02"),
    "L_D03": ("ch:CH02", "GATE_D03"),
    "L_T03": ("ch:CH03", "GATE_T03"),
    "L_D04": ("ch:CH03", "GATE_T03"),
    "L_T04": ("ch:CH04", "GATE_T04"),
    "L_D05": ("ch:CH05", "GATE_D05"),
    "L_D06": ("ch:CH06", "GATE_D06"),
    "L_T05": ("ch:CH07", "GATE_T05"),
    "L_D07": ("ch:CH07", "GATE_D07"),
    "L_T06": ("ch:CH07", "GATE_T06"),
    "L_D08": ("ch:CH08", "GATE_D08"),
    "L_D09": ("ch:CH10", "GATE_D09"),
}


def place_locations(g, post):
    for lid, (x, y, gl, pre_dest, sp, post_dest) in LOC.items():
        dest = post_dest if post else pre_dest
        if dest == "":
            g.put(x, y, "U")
            continue
        g.put(x, y, gl)
        cond = "" if post else LOC_COND_PRE.get(lid, ("", ""))[0]
        g.e(f"location {lid} {x} {y} dest={dest} spawn={sp}" + (f" if={cond}" if cond else ""))
        if cond:
            # locations are checked before triggers, so this only runs when the entrance is closed
            g.e(f"trigger {x} {y} scene={LOC_COND_PRE[lid][1]}")


def pre_world():
    g = base()
    bridge_roads(g, True)
    place_locations(g, False)
    # explicit walking edges (blocks lift as the story opens routes)
    g.e("block 29..31 33..34 tile=gate if=!ch:CH03 msg=\"The northern road is closed by a ministry barricade.\"")
    g.e("block 52..54 44..46 tile=gate if=!ch:CH04 msg=\"A checkpoint on the east road. The party is wanted in Veyr.\"")
    g.e("block 43..45 7..11 tile=rubble if=!ch:CH07 msg=\"Whitebone approach is sealed by redoubt patrols.\"")
    g.e("block 56..58 6..9 tile=rubble if=!ch:CH08 msg=\"The vault road is guarded until the redoubt falls.\"")
    g.e("block 45..47 42..43 tile=gate if=!ch:CH10 msg=\"The old aqueduct entrance. Not yet.\"")
    # ferries (after CH06) and cable ferry (after CH07) as dock scenes
    g.e("trigger 90 44 scene=FERRY_BELLHARBOR")
    g.e("trigger 90 22 scene=FERRY_SKYSPINE")
    g.e("trigger 66 12 scene=CABLE_AERIE")
    g.e("trigger 62 12 scene=CABLE_NACRE")
    g.rect(87, 44, 90, 44, ":")
    g.rect(86, 22, 90, 22, ":")
    g.path([(80, 13), (80, 12), (66, 12)], ":")
    g.path([(50, 10), (50, 12), (62, 12)], ":")
    g.rect(63, 12, 65, 12, "=")
    # northern basin to Rootward road opened by CH10 (return from the accord)
    g.path([(44, 12), (44, 26), (38, 26), (38, 30)], ":")
    g.e("block 43..45 20..22 tile=rubble if=!ch:CH09 msg=\"A salt slide blocks the south road from the basin.\"")
    for (x, y, sp) in ((24, 59, "t01"), (40, 46, "t02")):
        g.e(f"spawn {sp} {x} {y} down")
    spawns(g)
    g.e("spawn default 24 59 down")
    g.e("spawn ferry_bh 89 44 left")
    g.e("spawn ferry_sky 89 22 left")
    g.e("spawn cable_aerie 67 12 right")
    g.e("spawn cable_nacre 61 12 left")
    # encounter zones by region
    g.e("zone 0..34 34..71 enc=OW1")
    g.e("zone 34..60 30..71 enc=OW1")
    g.e("zone 0..30 0..33 enc=OW2")
    g.e("zone 60..95 30..71 enc=OW3")
    g.e("zone 66..95 0..29 enc=OW4")
    g.e("zone 31..63 0..29 enc=OW5")
    return g.emit("WORLD", name="The Crown March and Beyond", tileset="world", music="M017", kind="world", save="true",
                  encounters="OW1", rate="0.9", legend={"P": "plains", "F": "forest", "H": "hills", "M": "mountain",
                  "K": "deep", "z": "sand", "q": "snow", "N": "salt", "A": "ash", "Y": "town_mark", "X": "dungeon_mark",
                  "C": "city", "U": "ruin", ":": "path"})


def post_world():
    g = base()
    # the central relay fault breaks open: the Ember Sea
    g.blob(60, 40, 17, 14, "~")
    g.blob(60, 40, 12, 10, "K")
    g.blob(62, 34, 2, 2, "Z")                 # Crown Heart relay, exposed
    g.blob(62, 36, 3, 1, "z")
    g.put(62, 34, "X")
    g.blob(59, 45, 3, 2, "P")                 # Hearthward pontoons
    g.put(59, 45, "Y")
    for (cx, cy, r) in ((48, 30, 2), (72, 50, 2), (54, 52, 1), (68, 30, 1)):
        g.blob(cx, cy, r, r, "z")
        g.blob(cx, cy, r - 0.5, r - 0.5, "P")
    # coastline fractures along relay faults
    g.blob(84, 50, 4, 3, "~", only="zP:")
    g.blob(30, 64, 4, 2, "~", only="PH:")
    g.blob(30, 64, 2, 1, "K")
    g.blob(26, 64, 2, 1, "~")
    g.vline(40, 38, 44, "~")
    # Skyspine: the chain snaps, two new islands
    g.blob(70, 22, 3, 2, "~")
    g.blob(73, 26, 2, 2, "~")
    g.blob(69, 23, 2, 1, "H")                 # the mooring island where the snapped chain now ends
    # optional islands: Cradle of Winter (north, visible from Nacre) and Starless Reef (Ember Sea)
    g.blob(50, 1, 4, 1, "q")
    g.put(50, 1, "X")
    g.blob(72, 57, 3, 2, "Z")
    g.rect(70, 58, 74, 58, "z")               # a black-sand shoal to moor on
    g.put(72, 57, "X")
    bridge_roads(g, False)
    g.blob(86, 52, 2, 1, "z")                 # the archive's tide island keeps a strip of sand
    # Hearthward pontoon road west to the Veyr shore
    g.rect(44, 45, 56, 45, "=")
    g.rect(41, 45, 43, 45, ":")
    # Glass Coast ferry landing (post): the repaired ferry from Hearthward ties up here
    g.rect(76, 46, 78, 46, ":")
    g.e("trigger 77 46 scene=FERRY_HEARTHWARD")
    g.e("spawn ferry_bh 78 45 up")
    g.e("spawn helm 57 45 down")
    place_locations(g, True)
    g.e("location L_T07 59 45 dest=T07_MARKET spawn=world")
    g.e("location L_D10 62 34 dest=D10_R01 spawn=world")
    g.e("location L_D11 50 1 dest=D11_R01 spawn=world")
    g.e("location L_D12 72 57 dest=D12_R01 spawn=world")
    # landing zones (airship) - explicit, each with a walkable spawn beside it
    for (name, x1, x2, y1, y2) in (("Hearthward", 56, 58, 44, 46), ("Brackenford", 25, 27, 56, 58), ("Veyr", 41, 43, 45, 47),
                                   ("Rootward", 33, 35, 28, 29), ("Cinderwake", 21, 23, 19, 21), ("Bellharbor", 76, 78, 42, 44),
                                   ("High Aerie", 81, 83, 14, 16), ("Nacre", 51, 53, 11, 13), ("Whitebone", 39, 41, 8, 9),
                                   ("Winter Island", 49, 51, 0, 1), ("Reef Shoal", 71, 73, 56, 58), ("Crown Heart", 61, 63, 36, 37),
                                   ("Skychain", 68, 70, 23, 24), ("Vault Road", 56, 58, 6, 7), ("Archive Point", 85, 87, 52, 53)):
        g.e(f"landing {x1}..{x2} {y1}..{y2} name=\"{name}\"")
    g.e("block 61..63 33..35 tile=reef if=!ch:CH20 msg=\"The Crown Heart relay is surrounded by a pressure storm.\"")
    g.e("block 49..51 0..1 tile=snow if=!ch:CH20 msg=\"A winter island, far to the north. Nacre's listeners say its lantern never goes out.\"")
    g.e("block 71..73 56..58 tile=reef if=!ch:CH20 msg=\"A starless shoal. Harbor bells ring when you pass it.\"")
    spawns(g, [("L_T07", (59, 45)), ("L_D10", (62, 34)), ("L_D11", (50, 1)), ("L_D12", (72, 57))])
    g.e("spawn default 59 46 down")
    g.e("zone 0..95 0..71 enc=OWP")
    return g.emit("WORLD_POST", name="The Ember Sea", tileset="world_post", music="M018", kind="world", save="true",
                  encounters="OWP", rate="0.8", phase="post", legend={"P": "plains", "F": "forest", "H": "hills", "M": "mountain",
                  "K": "deep", "z": "sand", "q": "snow", "N": "salt", "A": "ash", "Y": "town_mark", "X": "dungeon_mark",
                  "C": "city", "U": "ruin", ":": "path", "Z": "reef"})


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "world.map"), [pre_world(), post_world()], "Overworld (tools/maps/world.py)")
    print("world written")
