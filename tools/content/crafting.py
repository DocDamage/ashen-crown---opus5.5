"""Crafting, materials, gathering and hunting parts (expansion systems, branch s2).

Materials (MT01-MT46) come from gathering nodes (`node x y kind=mine|herb|salvage table=<id>` in content_src/maps) and
from enemy parts (new enemies E041-E120 drop a family part and their home's material). Crafters are the NPCs whose id
starts with `crafter_`: talking to one opens the crafting bench after their lines. A crafter works at its place's
region tier (gear2.TIER_ORDER); it offers every recipe of that tier or an earlier one.

Recipe kinds:
  make     materials (+ crowns) -> item x count
  reforge  one owned item + materials (+ crowns) -> a better item of the same class (the upgrade path for tier gear)
Recipe ids: RC001... (stable; generated from tables below, order never changes).
"""

# ---------------------------------------------------------------- materials
# id: (name, price, source kind, description)
MATERIALS = {
    # ores and stone (mining)
    "MT01": ("Slag Iron", 90, "mine", "Iron pulled from the slag heaps. Brittle until it is folded."),
    "MT02": ("Geode Shard", 160, "mine", "A crystal from the Geode Wood. It rings when struck."),
    "MT03": ("Salt Crystal", 180, "mine", "Pale Basin salt, hard as glass. It keeps things."),
    "MT04": ("Rime Quartz", 260, "mine", "Quartz that never warms. Hoarfrost smiths quench blades in it."),
    "MT05": ("Emberstone", 220, "mine", "A stone that holds heat for a year. Delvers carry it for luck."),
    "MT06": ("Grave Silver", 420, "mine", "Silver mined by the dead. It does not tarnish."),
    "MT07": ("Coral Branch", 170, "salvage", "Red coral from the Ember Sea reefs. Tough, and light."),
    "MT08": ("Skysteel Shard", 380, "mine", "A splinter of the fallen host's steel. It weighs almost nothing."),
    # herbs (herbalism)
    "MT10": ("Millreed", 30, "herb", "A pond reed. Millers bind cuts with it."),
    "MT11": ("Fen Nettle", 70, "herb", "Mirewold nettle. It stings, then it cleans."),
    "MT12": ("Lilac Bloom", 110, "herb", "A mineral lilac from the Seep. It calms the blood."),
    "MT13": ("Maple Resin", 140, "herb", "Red resin from the Vermilion maples. Lacquer and salve."),
    "MT14": ("Glowcap", 120, "herb", "A cave mushroom that lights the Fungal Terraces."),
    "MT15": ("Frostmoss", 200, "herb", "Moss that grows under ice. It slows a fever."),
    "MT16": ("Sunless Bloom", 300, "herb", "A builder garden flower that never saw the sun."),
    "MT17": ("Grave Lily", 360, "herb", "It grows on the honoured dead. The mourners let it."),
    "MT18": ("Cliff Thyme", 90, "herb", "Skyspine thyme. Shepherds chew it against the wind."),
    # salvage
    "MT20": ("Crown Scrap", 40, "salvage", "Stamped Crown iron. The Ministry says it is still theirs."),
    "MT21": ("Hull Iron", 100, "salvage", "Riveted plate from a wreck. Salt has tempered it."),
    "MT22": ("Sea-Glass", 120, "salvage", "Glass the sea has worn smooth. Bellharbor lensmakers pay well."),
    "MT23": ("Relay Wire", 240, "salvage", "Builder wire. It still carries a little current."),
    "MT24": ("Builder Alloy", 320, "salvage", "A metal nobody alive can make. It remembers its shape."),
    "MT25": ("Lantern Glass", 280, "salvage", "Glass from a keeper's lamp, blown thick against the fault winds."),
    # hunting parts (enemy drops)
    "MT30": ("Rough Hide", 30, "part", "A beast's hide. Good for straps and not much else."),
    "MT31": ("Sharp Fang", 60, "part", "A hunter's tooth. It still wants to bite."),
    "MT32": ("Hard Chitin", 80, "part", "Shell plate. It turns a blade if it is layered."),
    "MT33": ("Swift Feather", 70, "part", "A flight feather. Fletchers and charm-makers want it."),
    "MT34": ("Ember Gland", 90, "part", "It burns in the hand. Bombs and fire charms."),
    "MT35": ("Frost Gland", 150, "part", "Cold enough to hurt. Handle with gloves."),
    "MT36": ("Brine Scale", 90, "part", "A sea creature's scale, salt-hard."),
    "MT37": ("Static Coil", 140, "part", "A crackling organ. Storm-touched things grow them."),
    "MT38": ("Grave Dust", 160, "part", "What the dead leave behind. Priests and poisoners both buy it."),
    "MT39": ("Wisp Essence", 120, "part", "A little of a spirit's light, caught in glass."),
    "MT40": ("Gear Core", 260, "part", "The heart of a builder machine. It ticks."),
    "MT41": ("Dragon Scale", 300, "part", "A scale from a dragon's kin. It remembers fire."),
    "MT42": ("Venom Sac", 70, "part", "Keep it closed."),
    "MT43": ("Brute Sinew", 80, "part", "Tendon from something large. Bowyers prize it."),
    "MT44": ("Leech Ichor", 90, "part", "Thin, red, and not all of it the leech's own."),
    "MT45": ("Seraph Down", 340, "part", "Soft feathers from the fallen host. They glow faintly."),
    "MT46": ("Wyrm Heart", 2400, "part", "The heart of an ancient dragon. It is still warm."),
}
ICON_OF_SOURCE = {"mine": "M001", "herb": "I009", "salvage": "M002", "part": "I011"}
ICON_OVERRIDE = {"MT06": "M003", "MT08": "M003", "MT24": "M003", "MT46": "I024", "MT41": "M002", "MT45": "I006",
                 "MT39": "I005", "MT40": "M003", "MT17": "I006", "MT16": "I005"}

# ---------------------------------------------------------------- crafted consumables (IC01-IC12)
# id: (name, price, desc, spec as tables.CONSUMABLE)
CONSUMABLES = {
    "IC01": ("Millreed Poultice", 80, "Restores 400 HP to one ally and cures Poison.",
             dict(target="ally_one", ops=[{"op": "heal", "flat": 400}, {"op": "cleanse", "ids": ["poison"]}], field=True)),
    "IC02": ("Slag Bomb", 160, "Deals fire damage to one enemy.",
             dict(target="enemy_one", ops=[{"op": "damage", "power": 170, "type": "magical", "element": "fire", "fixed_mag": 45}])),
    "IC03": ("Brine Tonic", 220, "Restores 70 MP to one ally.",
             dict(target="ally_one", ops=[{"op": "mp", "amount": 70}], field=True)),
    "IC04": ("Fen Antidote", 260, "Cures Poison, Burn, Bleed, Blind, Sleep and Silence on the whole party.",
             dict(target="ally_all", ops=[{"op": "cleanse", "ids": ["poison", "burn", "bleed", "blind", "sleep", "silence"]}])),
    "IC05": ("Glowcap Draught", 420, "Restores 1300 HP to one ally.",
             dict(target="ally_one", ops=[{"op": "heal", "flat": 1300}], field=True)),
    "IC06": ("Frost Flask", 480, "Deals ice damage to one enemy and may Slow it.",
             dict(target="enemy_one", ops=[{"op": "damage", "power": 170, "type": "magical", "element": "ice", "fixed_mag": 90},
                                           {"op": "status", "id": "slow", "chance": 50}])),
    "IC07": ("Maple Salve", 520, "Grants Regen to the whole party.",
             dict(target="ally_all", ops=[{"op": "status", "id": "regen", "chance": 100, "dur": 4}])),
    "IC08": ("Lattice Stim", 640, "Grants Haste to one ally.",
             dict(target="ally_one", ops=[{"op": "status", "id": "haste", "chance": 100, "dur": 3}])),
    "IC09": ("Grave Lily Tincture", 900, "Revives one ally with half HP.",
             dict(target="ally_one", revive=True, ops=[{"op": "revive", "pct": 0.5}], field=True)),
    "IC10": ("Storm Canister", 760, "Deals storm damage to one enemy.",
             dict(target="enemy_one", ops=[{"op": "damage", "power": 170, "type": "magical", "element": "storm", "fixed_mag": 150}])),
    "IC11": ("Hearth Draught", 1400, "Restores 1500 HP to the whole party.",
             dict(target="ally_all", ops=[{"op": "heal", "flat": 1500}], field=True)),
    "IC12": ("Waking Salts", 120, "Cures Sleep, Blind and Silence on one ally.",
             dict(target="ally_one", ops=[{"op": "cleanse", "ids": ["sleep", "blind", "silence"]}])),
}
CONSUMABLE_ICON = {"IC01": "I001", "IC02": "I015", "IC03": "I004", "IC04": "I007", "IC05": "I002", "IC06": "I016",
                   "IC07": "I021", "IC08": "I019", "IC09": "I006", "IC10": "I017", "IC11": "I021", "IC12": "I010"}

# ---------------------------------------------------------------- craft-only accessories (AC01-AC06)
# id: (name, price, passives, grants, icon base)
ACCESSORIES = {
    "AC01": ("Appraiser's Lens", 900, {}, "SX_LIBRA", "A010"),
    "AC02": ("Gatherer's Satchel", 1200, {"gather_bonus": 1}, "", "A022"),
    "AC03": ("Hunter's Tally", 1800, {"acc_bonus": 10, "reveal_affinity": True}, "", "A014"),
    "AC04": ("Fen Charm", 2400, {"immune": ["poison", "bleed", "blind"]}, "", "A013"),
    "AC05": ("Deepforge Band", 4200, {"phys_reduce": 0.08, "mhp_mult": 1.06}, "", "A009"),
    "AC06": ("Lantern of the Living", 9800, {"auto_revive": True, "heal_mult": 1.1}, "", "A020"),
}

# ---------------------------------------------------------------- hunting parts
ARCH_PART = {"swarm": "MT30", "hunter": "MT31", "brute": "MT43", "tank": "MT32", "drainer": "MT44", "healer": "MT39",
             "poisoner": "MT42", "charmer": "MT39", "thief": "MT20", "skirmisher": "MT31", "duelist": "MT20", "caster": "MT39"}
ELEM_PART = {"fire": "MT34", "ice": "MT35", "water": "MT36", "storm": "MT37", "earth": "MT02", "light": "MT45",
             "shadow": "MT38", "poison": "MT42"}
# the home's own material (ore/herb/salvage of the region), dropped now and then
HOME_MAT = {"R01": "MT10", "N04": "MT20", "R02": "MT01", "N07": "MT05", "N42": "MT21", "R03": "MT22", "N13": "MT36",
            "R06": "MT07", "R04": "MT18", "N18": "MT33", "R05": "MT03", "N21": "MT12", "R08": "MT11", "N22": "MT11",
            "N23": "MT38", "N25": "MT44", "R07": "MT13", "N29": "MT13", "N30": "MT13", "R09": "MT15", "N34": "MT04",
            "N35": "MT04", "SKY": "MT08", "N39": "MT45", "U1": "MT02", "U2": "MT23", "U3": "MT17", "SEA": "MT07",
            "NIGHT": "MT39"}
DRAGONS = {"E085", "E090", "E094", "E098"}
PART_CHANCE, ELEM_CHANCE, HOME_CHANCE = 30, 15, 12


def parts_for(row):
    """row: bestiary2 ROWS tuple -> [(material id, chance %)] (deterministic, from the enemy's family)."""
    eid, home, arch, elem, tags = row[0], row[2], row[8], row[9], row[10]
    out = []
    p = ARCH_PART.get(arch)
    if "flying" in tags:
        p = "MT33"
    if "undead" in tags:
        p = "MT38"
    if home == "U2":
        p = "MT40"
    if eid in DRAGONS:
        p = "MT41"
    if p:
        out.append((p, PART_CHANCE))
    e = ELEM_PART.get(elem)
    if e and e != p:
        out.append((e, ELEM_CHANCE))
    h = HOME_MAT.get(home)
    if h and h not in (p, e):
        out.append((h, HOME_CHANCE))
    return out


# ---------------------------------------------------------------- gathering tables
# id: kind, rolls, refresh (steps, battles), drops [(item, weight, min, max)]
GATHER = {
    "herb_r01": dict(kind="herb", rolls=1, steps=100, battles=3, drops=[("MT10", 70, 1, 3), ("I009", 20, 1, 1), ("MT12", 10, 1, 1)]),
    "mine_r02": dict(kind="mine", rolls=1, steps=120, battles=3, drops=[("M001", 45, 1, 2), ("MT01", 40, 1, 2), ("MT05", 15, 1, 1)]),
    "salvage_r03": dict(kind="salvage", rolls=1, steps=120, battles=3, drops=[("MT21", 45, 1, 2), ("MT22", 35, 1, 2), ("MT20", 20, 1, 3)]),
    "salvage_r06": dict(kind="salvage", rolls=1, steps=120, battles=3, drops=[("MT07", 50, 1, 2), ("MT22", 35, 1, 2), ("MT36", 15, 1, 1)]),
    "herb_r04": dict(kind="herb", rolls=1, steps=120, battles=3, drops=[("MT18", 60, 1, 3), ("MT10", 25, 1, 2), ("MT33", 15, 1, 1)]),
    "herb_r05": dict(kind="herb", rolls=1, steps=140, battles=4, drops=[("MT12", 55, 1, 2), ("MT03", 30, 1, 1), ("MT39", 15, 1, 1)]),
    "herb_r08": dict(kind="herb", rolls=1, steps=120, battles=3, drops=[("MT11", 60, 1, 3), ("MT42", 25, 1, 1), ("MT12", 15, 1, 1)]),
    "herb_r07": dict(kind="herb", rolls=1, steps=140, battles=4, drops=[("MT13", 60, 1, 2), ("MT12", 25, 1, 2), ("MT39", 15, 1, 1)]),
    "mine_r09": dict(kind="mine", rolls=1, steps=160, battles=4, drops=[("MT04", 50, 1, 2), ("MT15", 30, 1, 2), ("M002", 20, 1, 1)]),
    "salvage_wor": dict(kind="salvage", rolls=1, steps=160, battles=4, drops=[("MT25", 45, 1, 2), ("MT21", 35, 1, 2), ("M002", 20, 1, 1)]),
    "mine_u1": dict(kind="mine", rolls=1, steps=140, battles=4, drops=[("MT02", 50, 1, 2), ("MT05", 30, 1, 2), ("M002", 20, 1, 1)]),
    "mine_u1b": dict(kind="mine", rolls=2, steps=160, battles=4, drops=[("M002", 40, 1, 2), ("MT01", 30, 1, 3), ("MT05", 25, 1, 2), ("M003", 5, 1, 1)]),
    "herb_u1": dict(kind="herb", rolls=1, steps=140, battles=4, drops=[("MT14", 60, 1, 3), ("MT11", 25, 1, 2), ("MT10", 15, 1, 3)]),
    "salvage_u2": dict(kind="salvage", rolls=1, steps=160, battles=4, drops=[("MT23", 45, 1, 2), ("MT24", 30, 1, 1), ("MT40", 25, 1, 1)]),
    "herb_u2": dict(kind="herb", rolls=1, steps=180, battles=5, drops=[("MT16", 50, 1, 2), ("MT14", 30, 1, 2), ("MT12", 20, 1, 2)]),
    "mine_u3": dict(kind="mine", rolls=1, steps=180, battles=5, drops=[("MT06", 45, 1, 2), ("M003", 20, 1, 1), ("MT17", 35, 1, 1)]),
    "mine_sky": dict(kind="mine", rolls=1, steps=180, battles=5, drops=[("MT08", 55, 1, 2), ("MT45", 25, 1, 1), ("M003", 20, 1, 1)]),
}
GATHER_VERB = {"mine": "Mined", "herb": "Gathered", "salvage": "Salvaged"}

# ---------------------------------------------------------------- recipes
# signature materials of each tier: (metal, herb/soft, part)
TIER_MATS = {
    "R01": ("M001", "MT10", "MT30"), "R02": ("MT01", "MT20", "MT34"), "R03": ("MT21", "MT22", "MT36"),
    "R08": ("M001", "MT11", "MT44"), "R04": ("M002", "MT18", "MT33"), "U1": ("MT02", "MT05", "MT41"),
    "R06": ("MT07", "MT22", "MT36"), "R05": ("MT03", "MT12", "MT39"), "R07": ("M002", "MT13", "MT31"),
    "R09": ("MT04", "MT15", "MT35"), "U2": ("MT24", "MT23", "MT40"), "WOR": ("MT25", "MT21", "M002"),
    "SKY": ("MT08", "MT45", "MT33"), "U3": ("MT06", "MT17", "MT38"),
}
# consumable recipes: (result, count, tier, mats)
ITEM_RECIPES = [
    ("I001", 2, "R01", [("MT10", 2)]),
    ("IC01", 1, "R01", [("MT10", 2), ("I009", 1)]),
    ("IC12", 2, "R01", [("MT10", 1), ("MT30", 1)]),
    ("IC02", 2, "R02", [("MT34", 1), ("MT20", 2)]),
    ("I004", 1, "R02", [("MT10", 2), ("MT05", 1)]),
    ("IC03", 1, "R03", [("MT36", 2), ("MT22", 1)]),
    ("IC04", 1, "R08", [("MT11", 3), ("MT42", 1)]),
    ("I006", 1, "R04", [("MT33", 2), ("MT18", 2)]),
    ("IC05", 1, "U1", [("MT14", 3)]),
    ("IC06", 2, "R09", [("MT35", 1), ("MT15", 1)]),
    ("IC07", 1, "R07", [("MT13", 2), ("MT12", 1)]),
    ("IC08", 1, "U2", [("MT37", 1), ("MT23", 1)]),
    ("IC09", 1, "U3", [("MT17", 2), ("MT45", 1)]),
    ("IC10", 2, "U2", [("MT37", 2), ("MT24", 1)]),
    ("IC11", 1, "WOR", [("IC05", 2), ("MT16", 1)]),
    ("I024", 1, "U3", [("MT46", 1), ("MT17", 2)]),
]
# craft-only accessories: (result, tier, mats, crowns)
ACC_RECIPES = [
    ("AC01", "R01", [("MT20", 3), ("MT10", 2)], 150),
    ("AC02", "R02", [("MT30", 4), ("MT01", 2)], 300),
    ("AC03", "R04", [("MT31", 4), ("MT33", 3)], 600),
    ("AC04", "R08", [("MT11", 4), ("MT44", 3), ("MT42", 2)], 800),
    ("AC05", "U1", [("M002", 3), ("MT41", 2), ("MT05", 3)], 1500),
    ("AC06", "U3", [("MT25", 3), ("MT17", 3), ("MT45", 2)], 4000),
]
# which classes / armour pieces each tier's crafters can make (indices into gear2.CLASSES / gear2.ARMOR_KINDS)
GEAR_RECIPE_PICKS = {"weapons": 2, "armor": 1}


def gear_recipes(tier_order, tier_items):
    """-> list of recipe dicts for the region-tier gear (make + reforge). tier_items[tid] = {"weapons": [8 ids],
    "armor": [5 ids], "acc": [2 ids], "price": {iid: price}}."""
    out = []
    for i, tid in enumerate(tier_order):
        metal, soft, part = TIER_MATS[tid]
        ti = tier_items[tid]
        n = 2 + i // 4                  # material counts grow with the tier
        for k in range(GEAR_RECIPE_PICKS["weapons"]):
            ci = (i * 3 + k * 4) % 8
            wid = ti["weapons"][ci]
            out.append(dict(kind="make", result=wid, count=1, tier=tid, mats=[(metal, n), (part, n)],
                            gold=_gold(ti["price"][wid], 0.25)))
        ai = i % 5
        gid = ti["armor"][ai]
        out.append(dict(kind="make", result=gid, count=1, tier=tid, mats=[(metal, n), (soft, n)],
                        gold=_gold(ti["price"][gid], 0.25)))
        aid = ti["acc"][i % 2]
        out.append(dict(kind="make", result=aid, count=1, tier=tid, mats=[(soft, n), (part, n + 1)],
                        gold=_gold(ti["price"][aid], 0.2)))
        if i > 0:
            prev = tier_items[tier_order[i - 1]]
            ci = (i * 5) % 8
            out.append(dict(kind="reforge", input=prev["weapons"][ci], result=ti["weapons"][ci], count=1, tier=tid,
                            mats=[(metal, n + 1), (part, 1)], gold=_gold(ti["price"][ti["weapons"][ci]], 0.12)))
    return out


def _gold(price, f):
    return max(20, int(round(price * f / 10.0)) * 10)


def recipes(tier_order, tier_items, unique_reforges):
    """All recipes, ids RC001.. in a fixed order: items, accessories, tier gear, unique reforges."""
    rs = []
    for (res, cnt, tier, mats) in ITEM_RECIPES:
        rs.append(dict(kind="make", result=res, count=cnt, tier=tier, mats=list(mats), gold=0))
    for (res, tier, mats, g) in ACC_RECIPES:
        rs.append(dict(kind="make", result=res, count=1, tier=tier, mats=list(mats), gold=g))
    rs += gear_recipes(tier_order, tier_items)
    rs += unique_reforges
    out = {}
    for i, r in enumerate(rs):
        rid = "RC%03d" % (i + 1)
        r["id"] = rid
        r["mats"] = [[m, n] for m, n in r["mats"]]
        out[rid] = r
    return out


def add_items(items, check_ops):
    """Materials, crafted consumables and craft-only accessories -> items (icon bases recorded as icon_base)."""
    added = []
    for mid, (name, price, src, desc) in MATERIALS.items():
        items[mid] = {"id": mid, "name": name, "kind": "material", "price": price, "desc": desc, "sellable": True,
                      "source": src, "src": "gear2", "icon_base": ICON_OVERRIDE.get(mid, ICON_OF_SOURCE[src])}
        added.append(mid)
    for iid, (name, price, desc, spec) in CONSUMABLES.items():
        check_ops(iid, spec["ops"])
        items[iid] = {"id": iid, "name": name, "kind": "consumable", "price": price, "desc": desc, "target": spec["target"],
                      "ops": spec["ops"], "battle": spec.get("battle", True), "field": spec.get("field", False),
                      "revive": spec.get("revive", False), "special": "", "sellable": True, "src": "gear2",
                      "icon_base": CONSUMABLE_ICON[iid]}
        added.append(iid)
    for aid, (name, price, pas, grants, base) in ACCESSORIES.items():
        it = {"id": aid, "name": name, "kind": "accessory", "slot": "accessory", "price": price, "sellable": True,
              "allowed": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08"], "passives": dict(pas), "src": "gear2",
              "icon_base": base, "crafted": True}
        if grants:
            it["grants"] = grants
        items[aid] = it
        added.append(aid)
    return added
