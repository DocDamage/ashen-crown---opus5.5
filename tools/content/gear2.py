"""Expansion equipment, sets, teaching gear, bestiary data and economy (systems branch s2).

Region tiers: every region / realm of docs/expansion/WORLD_V2.md has one tier of gear (8 weapons, one per weapon class
C01-C08 - the new heroes use a template class, see cast.EQUIP_AS -, 5 armour pieces: plate, mail, robe, leather, head,
and 2 accessories). Stats follow the existing tier curve at the region's level band (tier_x); prices follow the same
curve. Ids: WR001-WR112, GR001-GR070, AR001-AR028 (tier i: weapons WR(8i+1..8i+8), armour GR(5i+1..), acc AR(2i+1..)).
They are sold in the region's shops (SHOP_TIERS) once the region is reachable (TIERS[..]["gate"] chapter done).

Named items (WN/GN/AN): uniques from the new dungeons' chests and bosses and the superbosses. Many belong to an item set
(SETS: 2-4 pieces; the bonus for n pieces applies while n pieces are worn together; bonuses stack by threshold).
Items with `teach` [[ability, rate]] teach like a Vestige: after each won battle the wearer gains rate x AP progress
(AP 1, 3 against bosses); at 100 the ability is known for good.
"""
import math

CLASSES = ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08"]
FIRST_WEAPON = {"C01": 1, "C02": 7, "C03": 13, "C04": 19, "C05": 25, "C06": 31, "C07": 37, "C08": 43}
ARMOR_KINDS = ["plate", "mail", "robe", "leather", "head"]
ARMOR_BASES = {"plate": ["G013", "G014", "G015", "G016"], "mail": ["G009", "G010", "G011", "G012"],
               "robe": ["G001", "G002", "G003", "G004"], "leather": ["G005", "G006", "G007", "G008"],
               "head": ["G017", "G019", "G021", "G023"], "head_r": ["G018", "G020", "G022", "G024"],
               "shield": ["G025", "G026", "G027", "G028"]}
ARMOR_ALLOWED = {"plate": ["C01"], "mail": ["C03", "C04", "C07"], "robe": ["C02", "C06"], "leather": ["C05", "C08"],
                 "head": list(CLASSES), "shield": ["C01", "C07"]}
ARMOR_SLOT = {"plate": "body", "mail": "body", "robe": "body", "leather": "body", "head": "head", "shield": "offhand"}

# level -> position on the weapon / armour tier scale (anchors from the canon chapters' levels)
W_ANCHOR = [(1, 1.0), (12, 2.0), (20, 3.0), (32, 4.0), (42, 5.0), (52, 6.0)]
A_ANCHOR = [(1, 1.0), (14, 2.0), (30, 3.0), (40, 4.0)]


def _pos(level, anchors, per_level_after):
    if level <= anchors[0][0]:
        return anchors[0][1]
    for (l0, x0), (l1, x1) in zip(anchors, anchors[1:]):
        if level <= l1:
            return x0 + (x1 - x0) * (level - l0) / float(l1 - l0)
    l, x = anchors[-1]
    return x + (level - l) / float(per_level_after)


def weapon_x(level):
    return _pos(level, W_ANCHOR, 12)


def armor_x(level):
    return _pos(level, A_ANCHOR, 11)


# id, prefix, bands (lo, hi), gate chapter (stock once done), element theme, weapon nouns offset
TIERS = [
    ("R01", "Millstone", (1, 12), "CH01", ""),
    ("R02", "Slagiron", (10, 18), "CH03", "fire"),
    ("R03", "Wrackglass", (14, 22), "CH04", "water"),
    ("R08", "Fenwrought", (16, 24), "CH05", "poison"),
    ("R04", "Cliffsteel", (18, 26), "CH06", "storm"),
    ("U1", "Delverforged", (18, 30), "CH06", "earth"),
    ("R06", "Reefcoral", (20, 30), "CH06", "water"),
    ("R05", "Saltbloom", (22, 30), "CH08", "light"),
    ("R07", "Vermilion", (24, 32), "CH09", "fire"),
    ("R09", "Rimeforged", (28, 38), "CH09", "ice"),
    ("U2", "Lattice", (28, 40), "CH10", "storm"),
    ("WOR", "Ruinwright", (30, 40), "CH12", ""),
    ("SKY", "Choirsteel", (30, 42), "CH12", "light"),
    ("U3", "Gravesilver", (36, 50), "CH15", "shadow"),
]
TIER_ORDER = [t[0] for t in TIERS]
REGION_NAME = {"R01": "Crown March", "R02": "Cinder Reach", "R03": "Glass Coast", "R04": "Skyspine", "R05": "Pale Basin",
               "R06": "Ember Sea", "R07": "Vermilion Reach", "R08": "Mirewold", "R09": "Hoarfrost March",
               "SKY": "Shattered Choir", "U1": "Emberdeep", "U2": "The Lattice", "U3": "The Hollow Throne",
               "WOR": "World of Ruin"}
ITEM_LEVEL_F = 0.3   # an item sits 30% into its region's band: an upgrade on arrival, not an end state

W_NOUNS = {"C01": ["Blade", "Sword", "Edge", "Brand"], "C02": ["Rod", "Wand", "Scepter"], "C03": ["Spear", "Lance", "Pike"],
           "C04": ["Maul", "Hammer", "Mallet"], "C05": ["Bow", "Longbow", "Recurve"], "C06": ["Staff", "Crook", "Crozier"],
           "C07": ["Rune", "Runeblade", "Glyph"], "C08": ["Knife", "Dagger", "Stiletto"]}
A_NOUNS = {"plate": ["Plate", "Cuirass", "Harness"], "mail": ["Mail", "Hauberk", "Links"], "robe": ["Robe", "Mantle", "Vestment"],
           "leather": ["Jerkin", "Leathers", "Coat"], "head": ["Helm", "Cap", "Hood", "Circlet"]}

# two accessories per tier: (name, passives, price factor on the tier's armour price)
TIER_ACC = {
    "R01": [("Miller's Charm", {"mhp_mult": 1.05}), ("Crossroads Token", {"encounter_mult": 0.85})],
    "R02": [("Slag Ward", {"elem_resist": {"fire": True}}), ("Pipefitter's Ring", {"atb_mult": 1.05})],
    "R03": [("Wrack Pearl", {"elem_resist": {"water": True}}), ("Salvager's Hook", {"acc_bonus": 8})],
    "R08": [("Quarantine Band", {"immune": ["poison", "bleed"]}), ("Fen Lantern", {"heal_mult": 1.08})],
    "R04": [("Cable Knot", {"atb_mult": 1.07}), ("Aerie Bell", {"immune": ["sleep", "silence"]})],
    "U1": [("Delver's Lamp", {"reveal_affinity": True}), ("Dragonbone Ring", {"elem_resist": {"fire": True, "earth": True}})],
    "R06": [("Coral Bead", {"mp_regen": 2}), ("Gull Feather", {"start_atb": 100})],
    "R05": [("Salt Rosette", {"mmp_mult": 1.1}), ("Mineral Eye", {"immune": ["blind"], "mag_bonus": 0.06})],
    "R07": [("Maple Talisman", {"lowhp_guard": 0.25}), ("Fox Bell", {"counter": 0.3})],
    "R09": [("Hoarfrost Clasp", {"elem_resist": {"ice": True}}), ("Rime Heart", {"mhp_mult": 1.1})],
    "U2": [("Relay Coil", {"mp_regen": 3}), ("Keeper Chip", {"atb_mult": 1.08})],
    "WOR": [("Beacon Ember", {"auto_revive": True}), ("Refuge Knot", {"reserve_scale": 0.03})],
    "SKY": [("Choir Feather", {"heal_mult": 1.12}), ("Host Sigil", {"elem_resist": {"light": True, "shadow": True}})],
    "U3": [("Grave-Candle", {"immune": ["doom", "sleep"], "phys_reduce": 0.05}), ("Mourner's Ring", {"lowhp_guard": 0.3, "mhp_mult": 1.08})],
}

# shops of each tier, and extra kinds a shop stocks for tier gear (where a region has no shop of that kind)
SHOP_TIERS = {
    "R01": ["SHOP_N01", "SHOP_N03", "SHOP_WEND"],
    "R02": ["SHOP_N06", "SHOP_N08", "SHOP_N09"],
    "R03": ["SHOP_N11", "SHOP_N43"],
    "R08": ["SHOP_N22", "SHOP_N22_ROW", "SHOP_N24"],
    "R04": ["SHOP_N16", "SHOP_T05"],
    "U1": ["SHOP_U02", "SHOP_U03", "SHOP_U07", "SHOP_U13", "SHOP_U15"],
    "R06": ["SHOP_N14"],
    "R05": ["SHOP_N19", "SHOP_T06"],
    "R07": ["SHOP_N27", "SHOP_N28", "SHOP_N28_MKT"],
    "R09": ["SHOP_N32"],
    "U2": ["SHOP_U17", "SHOP_U19", "SHOP_U26"],
    "WOR": ["SHOP_P05", "SHOP_T07"],
    "SKY": ["SHOP_SHIP"],
    "U3": ["SHOP_U29", "SHOP_U34", "SHOP_U37"],
}
SHOP_EXTRA_KINDS = {"SHOP_N14": ["weapons"], "SHOP_N32": ["accessories"], "SHOP_SHIP": ["weapons", "armor", "accessories"]}
# crafters: place -> tier (place region; post-fault surface places use the World of Ruin tier)
PLACE_TIER_OVERRIDE = {"P01": "WOR", "P02": "WOR", "P05": "WOR", "P09": "WOR"}

PASSIVE_TEXT = {
    "lowhp_guard": "less damage below 40% HP", "mp_regen": "MP +{v} per action", "atb_mult": "readiness +{pct}%",
    "mag_bonus": "magic +{pct}%", "reserve_scale": "stronger per reserve", "auto_revive": "survives one fatal blow",
    "elem_resist": "resists {elems}", "immune": "immune to {elems}", "weapon_element": "{v} attacks", "heal_mult": "healing +{pct}%",
    "start_atb": "starts battles ready", "mhp_mult": "max HP +{pct}%", "mmp_mult": "max MP +{pct}%", "acc_bonus": "accuracy +{v}",
    "phys_reduce": "physical damage -{pct}%", "encounter_mult": "fewer encounters", "reveal_affinity": "shows weaknesses",
    "counter": "counterattacks", "twohand_mult": "two-handed damage +15%", "mercy_barrier": "barrier below 30% HP",
    "concord_bonus": "Concord +{v}", "gather_bonus": "gathers one more material", "dispel_ward": "wards the first dispel",
}


def passive_text(p):
    out = []
    for k, v in p.items():
        t = PASSIVE_TEXT.get(k)
        if not t:
            continue
        if k.endswith("_mult"):
            pct = int(round((float(v) - 1) * 100))
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            pct = int(round(float(v) * 100))
        else:
            pct = 0
        elems = ", ".join(sorted(v)) if isinstance(v, (list, dict)) else ""
        out.append(t.format(pct=pct, v=v, elems=elems))
    s = "; ".join(out)
    return s[:1].upper() + s[1:] if s else ""


# ---------------------------------------------------------------- stat curves
def _lerp_list(vals, x):
    """vals: stats at tiers 1..n; x in [1, inf): lerp inside, extrapolate the last step (x 1.1 per tier) beyond."""
    n = len(vals)
    if x <= n:
        i = min(n - 2, int(math.floor(x)) - 1)
        f = x - (i + 1)
        return vals[i] + (vals[i + 1] - vals[i]) * f
    step = vals[-1] - vals[-2]
    k = x - n
    return vals[-1] + step * k * (1.0 + 0.1 * k)


def _price(prices, x):
    n = len(prices)
    if x <= n:
        return _lerp_list(prices, x)
    return prices[-1] * (1.9 ** (x - n))


def weapon_stats(items, cid, level, mult=1.0):
    x = weapon_x(level)
    base = [items["W%03d" % (FIRST_WEAPON[cid] + k)] for k in range(6)]
    atk = _lerp_list([b["atk"] for b in base], x) * mult
    mag = _lerp_list([b["mag"] for b in base], x) * mult
    price = _price([b["price"] for b in base[:5]], x)
    near = base[min(5, max(0, int(round(x)) - 1))]["id"]
    return int(round(atk)), int(round(mag)), int(round(price / 10.0)) * 10, near, base[0]


def armor_stats(items, kind, level, mult=1.0):
    x = armor_x(level)
    bases = [items[g] for g in ARMOR_BASES[kind]]
    d = _lerp_list([b["def"] for b in bases], x) * mult
    r = _lerp_list([b["res"] for b in bases], x) * mult
    price = _price([b["price"] for b in bases], x)
    near = bases[min(3, max(0, int(round(x)) - 1))]["id"]
    return int(round(d)), int(round(r)), int(round(price / 10.0)) * 10, near


def tier_level(tid):
    lo, hi = [t for t in TIERS if t[0] == tid][0][2]
    return lo + ITEM_LEVEL_F * (hi - lo)


# ---------------------------------------------------------------- named items and sets
# (id, name, slot kind: weapon class | armour kind | "acc", level, source (chest id | boss id), set id, passives,
#  teach [[ability, rate]], grants, flavour)
NAMED = [
    # S01 Drowned Oath (N04 The Sunken Chapel)
    ("WN01", "Hallam's Tidebrand", "C01", 13, "BX01", "S01", {"weapon_element": "water"}, [["S001", 10]], "", "Ser Hallam's sword. It was never allowed to rust."),
    ("GN01", "Oath-Drowned Helm", "head", 13, "N04_C_ALTAR", "S01", {}, [], "", "Water still runs out of the visor."),
    ("GN02", "Chapel Kite", "shield", 13, "N04_C_GARDEN", "S01", {}, [], "", "A kite shield painted with a flooded nave."),
    # S02 Slagwright (N07 The Slagfalls)
    ("WN02", "Colossus Maul", "C04", 18, "BX02", "S02", {"weapon_element": "fire"}, [], "", "Cooled from the Slag Colossus's fist."),
    ("GN03", "Slagwright Mail", "mail", 18, "N07_C_CROWN", "S02", {}, [], "", "Links poured one at a time."),
    ("AN01", "Furnace Heart", "acc", 18, "N07_C_SHELF", "S02", {"mhp_mult": 1.06}, [["S065", 10]], "", "It beats when it is cold."),
    # S03 Sluicewife's Mourning (N42 The Weeping Dam)
    ("WN03", "Weeping Wand", "C02", 18, "BX11", "S03", {"mp_regen": 1}, [["S010", 8]], "", "Always wet at the tip."),
    ("GN04", "Floodwater Veil", "head", 18, "N42_C_CROWN", "S03", {}, [], "", "The Sluicewife's veil. It smells of the reservoir."),
    ("AN02", "Dam-Keeper's Key", "acc", 18, "N42_C_HIDDEN", "S03", {"elem_resist": {"water": True}}, [["S068", 10]], "", "It opens the sluices. Nobody has dared."),
    # S04 Brine Matriarch (N13 The Brine Stair)
    ("WN04", "Matriarch's Harpoon", "C03", 22, "BX03", "S04", {"weapon_element": "water"}, [], "", "Barbed with the Matriarch's own teeth."),
    ("GN05", "Brood-Shell Mail", "mail", 22, "N13_C_ALCOVE", "S04", {}, [], "", "Egg-case plates, riveted."),
    ("AN03", "Pearl of the Stair", "acc", 22, "N13_C_HIDDEN", "S04", {"mp_regen": 2}, [["S047", 6]], "", "The smugglers' last payment."),
    # S05 Roc Queen's Plumage (N18 Eyrie Hollow)
    ("WN05", "Aurelle's Talon", "C05", 25, "BX04", "S05", {"acc_bonus": 6}, [], "", "A bow strung with roc sinew."),
    ("GN06", "Roc-Feather Coat", "leather", 25, "N18_C_R02", "S05", {}, [], "", "It wants to lift in a high wind."),
    ("GN07", "Eyrie Crest", "head", 25, "N18_C_R03", "S05", {}, [], "", "The aerie guard's old crest."),
    ("AN04", "Windfall Plume", "acc", 25, "N18_C_HIDDEN", "S05", {"atb_mult": 1.05}, [["S067", 10]], "", "A roc queen's moulted plume."),
    # S06 Mere-Mother's Memory (N21 Sorrowmere)
    ("WN06", "Drowned Memory", "C06", 29, "BX05", "S06", {"heal_mult": 1.08}, [["S130", 4]], "", "Hold it and remember someone else's childhood."),
    ("GN08", "Sorrow Mantle", "robe", 29, "N21_C_R02", "S06", {}, [], "", "Woven from lake weed and grief."),
    ("AN05", "Lake-Glass Locket", "acc", 29, "N21_C_HIDDEN", "S06", {"immune": ["sleep"]}, [["S043", 8]], "", "A drowned villager's portrait, still dry inside."),
    # S07 Lamprey Vestments (N25 The Leech Cathedral)
    ("WN07", "Abbot's Lancet", "C08", 26, "BX06", "S07", {"immune": ["poison"]}, [], "", "It bled the faithful for a fee."),
    ("GN09", "Leech-Order Jerkin", "leather", 26, "N25_C_CLOISTER", "S07", {}, [], "", "Oiled against the leeches. Mostly."),
    ("GN10", "Plague Mask", "head", 26, "N25_C_RELIC", "S07", {"immune": ["poison"]}, [], "", "Beak stuffed with fen herbs."),
    ("AN06", "Cure-Seller's Vial", "acc", 26, "N25_C_SCRIPT", "S07", {"heal_mult": 1.06}, [["S127", 8]], "", "The cure, kept back from the people who paid."),
    # S08 Nine-Tailed Court (N29 Thousand Gates)
    ("WN08", "Magistrate's Verdict", "C07", 30, "BX07", "S08", {"weapon_element": "fire"}, [], "", "Every cut is a sentence."),
    ("GN11", "Court Lacquer Mail", "mail", 30, "N29_C_MAZE2", "S08", {}, [], "", "Red lacquer over fox-iron."),
    ("GN12", "Nine-Tail Mask", "head", 30, "N29_C_COURT", "S08", {}, [], "", "Nine faces, none of them yours."),
    ("AN07", "Foxfire Lantern", "acc", 30, "N29_C_MIRROR", "S08", {"mag_bonus": 0.06}, [["S102", 6]], "", "Lit at the fox wedding. It has not gone out."),
    # S09 Rimebound (N34 Glacier Spire, N35 Coldharbour)
    ("WN09", "Behemoth's Tusk", "C03", 34, "BX08", "S09", {"weapon_element": "ice"}, [], "", "Broken off the Rimebound Behemoth."),
    ("GN13", "Warden's Frost-Mail", "mail", 35, "BX09", "S09", {}, [], "", "Frost grows back on it overnight."),
    ("GN14", "Glacier Crown", "head", 34, "N34_C_GALLERY", "S09", {}, [], "", "The first climber's crown. She did not need it."),
    ("AN08", "Heart of the Spire", "acc", 34, "N34_C_HEART", "S09", {"elem_resist": {"ice": True}}, [["S135", 5]], "", "A shard of the spire's core."),
    # S10 Hollow Host (N39 Seraphel, N40 The Broken Organ)
    ("WN10", "Hollow Seraph's Blade", "C01", 38, "BX10", "S10", {"weapon_element": "light"}, [], "", "It still hums the last order."),
    ("GN15", "Host-Sentinel Plate", "plate", 38, "N39_C_W", "S10", {}, [], "", "Plate for a guard who never stood down."),
    ("GN16", "Choir Circlet", "head", 38, "N40_C_BELLOWS", "S10", {}, [], "", "Cut from an organ pipe."),
    ("AN09", "Broken Halo", "acc", 38, "N39_C_HIDDEN", "S10", {"heal_mult": 1.08}, [["S113", 4]], "", "Half a halo. The other half is still up there."),
    # S11 Ilyrath's Bones (P01 Spine of Ilyrath)
    ("WN11", "Marrow Tyrant's Jaw", "C04", 38, "BX12", "S11", {"twohand_mult": 1.15}, [], "", "It still closes when you are not looking."),
    ("GN17", "Spine-Ridge Mail", "mail", 38, "P01_C_HOLLOW", "S11", {}, [], "", "Vertebrae of a dragon, linked."),
    ("AN10", "Dragon-Knuckle", "acc", 38, "P01_C_HIDDEN", "S11", {"elem_resist": {"fire": True}}, [["S004", 6]], "", "A knuckle of Ilyrath's kin."),
    # S12 Mile Zero (P02 The Tessellate)
    ("WN12", "Mile-Zero Longbow", "C05", 38, "BX13", "S12", {"atb_mult": 1.05}, [], "", "Strung with highway cable."),
    ("GN18", "Traffic Warden's Coat", "leather", 38, "P02_C_CONTROL", "S12", {}, [], "", "It still has its reflective stripe."),
    ("AN11", "Dispatch Key", "acc", 38, "P02_C_HIDDEN", "S12", {"start_atb": 100}, [["S070", 8]], "", "It unlocks a console that no longer exists."),
    # S13 Geode (U04 The Geode Wood, U05 Ossuary of Wings)
    ("WN13", "Hydra Fang", "C08", 24, "BX14", "S13", {"weapon_element": "earth"}, [], "", "One of the Geode Hydra's many fangs."),
    ("GN19", "Wingless Bone Helm", "head", 26, "BX15", "S13", {}, [], "", "A dragon's brow-plate."),
    ("AN12", "Geode Heart", "acc", 24, "U04_C3", "S13", {"elem_resist": {"earth": True}}, [["S012", 8]], "", "It rings like a bell underground."),
    # S14 Deepforge (U08 The Crown Dig, U12 Deepforge Mines)
    ("WN14", "Excavator's Drill", "C04", 27, "BX16", "S14", {}, [], "", "Foreman Grisk's drill-head on a haft."),
    ("GN20", "Delver's Forge-Mail", "mail", 27, "U12_C3", "S14", {}, [], "", "Karag Dun make. Heavy, and worth it."),
    ("AN13", "Stonebeard Signet", "acc", 28, "U12_C4", "S14", {"phys_reduce": 0.05}, [["S029", 6]], "", "A royal signet, pawned and lost."),
    # S15 Assembler (U18, U20, U23 - The Lattice)
    ("WN15", "Prime-Cut Glyph", "C07", 34, "BX18", "S15", {"weapon_element": "storm"}, [], "", "An assembly-line cutter, repurposed."),
    ("GN21", "Kael-00 Shell", "mail", 37, "BX20", "S15", {}, [], "", "The first operative's armour. It still fits someone."),
    ("GN22", "Omega Visor", "head", 36, "U23_C_CAPSULE", "S15", {"reveal_affinity": True}, [], "", "It shows you what things are made of."),
    ("AN14", "Datum Core", "acc", 36, "U20_C_INDEX", "S15", {"mp_regen": 2}, [["SX_LIBRA", 10]], "", "A builder's memory, still reading."),
    # S16 Sepulchre (U30, U31, U32, U35 - The Hollow Throne)
    ("WN16", "Ossuan's Bridge-Staff", "C06", 42, "BX21", "S16", {"heal_mult": 1.1}, [], "", "A span of the bone bridges, carried."),
    ("GN23", "Sepulchre Veil", "robe", 44, "BX22", "S16", {}, [], "", "Mother Sepulchre's veil for the living."),
    ("AN15", "Debt-Warden's Ledger", "acc", 43, "BX23", "S16", {"mmp_mult": 1.08}, [["S151", 4]], "", "Every debt the dead are owed."),
    ("GN24", "Mourning Crown", "head", 45, "BX25", "S16", {}, [], "", "Worn by a court too long in mourning."),
    # S17 First Crown (U33 The First Crown's Tomb, U35 The Lich Stair)
    ("WN17", "Kingsgrave", "C01", 45, "BX24", "S17", {"lowhp_guard": 0.2}, [["S147", 3]], "", "The first crowned king's sword. It chose him."),
    ("GN25", "Barrow-King's Plate", "plate", 45, "U33_C_CASE", "S17", {}, [], "", "Plate with a crown worked into the gorget."),
    ("GN26", "Circlet of the First", "head", 45, "U35_C_THRONE", "S17", {}, [], "", "A tin circlet, older than the Crown."),
    # S18 Ancient Wyrm (superbosses SB01-SB04)
    ("AN16", "Cindermaw Heartscale", "acc", 62, "SB01", "S18", {"elem_resist": {"fire": True}}, [["S123", 3]], "", "Scale from over the Surface Wyrm's heart."),
    ("GN27", "Thalassar's Crown", "head", 66, "SB02", "S18", {"elem_resist": {"water": True}}, [["S137", 3]], "", "Coral grown round a sea-wyrm's horn."),
    ("AN17", "Vael's Pinion", "acc", 72, "SB03", "S18", {"atb_mult": 1.08}, [["S161", 3]], "", "A flight feather that never touched ground."),
    ("GN28", "Ossathrax Bone-Shield", "shield", 78, "SB04", "S18", {"elem_resist": {"earth": True}}, [["S153", 3]], "", "The Deep Wyrm's shoulder-blade."),
    # S19 Hollow Heart (SB09-SB11)
    ("AN18", "The Ledger", "acc", 95, "SB09", "S19", {"reveal_affinity": True, "mag_bonus": 0.08}, [], "", "Everything the Crown took."),
    ("AN19", "The Tally", "acc", 102, "SB10", "S19", {"heal_mult": 1.12}, [], "", "Everything it gave back."),
    ("GN29", "The Verdict", "head", 110, "SB11", "S19", {"lowhp_guard": 0.25}, [], "", "What the two sums mean."),
    # standalone uniques
    ("AN41", "Breathing Shell", "acc", 40, "S3_C_SANCTUM", "", {"mp_regen": 3}, [], "", "It breathes with the tide, and so do you."),
    ("GN42", "Oathwarden's Helm", "head", 44, "S3_C_OATH", "", {"immune": ["doom", "silence"]}, [], "", "It kept the district's oath long after the district forgot it."),
    ("WN41", "Customs Seal", "C08", 42, "S3_C_HOLD", "", {"acc_bonus": 8}, [], "", "The Tithe's customs seal, sharpened. Every pocket it touches is declared."),
    ("AN40", "The Right Bell", "acc", 95, "BX27", "", {"mhp_mult": 1.12, "immune": ["doom", "stun"]}, [], "", "It rings once, correctly, and then keeps quiet."),
    ("GN40", "Carillon Mantle", "robe", 90, "EP3_C_ROPES", "", {"mag_bonus": 0.08}, [], "", "Woven from bell-rope. It hums when magic passes through it."),
    ("GN41", "Nave-Warden Plate", "plate", 90, "EP2_C_WARDEN", "", {"elem_resist": {"water": True, "shadow": True}}, [], "", "Armour of the drowned cathedral's last guard."),
    ("WN40", "Veyr's Clapper", "C04", 92, "EP4_C_BELFRY", "", {"weapon_element": "storm"}, [], "", "The iron tongue of a lesser bell. The Golem swings it like a thought."),
    ("WN18", "Wurm-Gut Blade", "C01", 28, "BX17", "", {"weapon_element": "fire"}, [], "", "Recovered from the Forge-Wurm's gut. Branna wants it back."),
    ("WN19", "Index Stylus", "C02", 36, "BX19", "", {"mag_bonus": 0.1}, [["S163", 8]], "", "It writes in a hand nobody reads now."),
    ("WN20", "Sorrow's Gate-Key", "C08", 44, "BX26", "", {"immune": ["doom"]}, [["S154", 4]], "", "A key that locks the dead in, or the living out."),
    ("WN21", "Prime Directive", "C07", 80, "SB05", "", {"atb_mult": 1.1, "mag_bonus": 0.1}, [["S164", 3]], "", "CURATOR's last order, given edge."),
    ("AN20", "Veil of the Unveiled", "acc", 84, "SB06", "", {"immune": ["doom", "silence", "sleep"], "mhp_mult": 1.1}, [["S156", 3]], "", "She does not need it any more."),
    ("WN22", "Unbeaten", "C01", 70, "SB07", "", {"counter": 1, "lowhp_guard": 0.2}, [["S115", 4]], "", "Varro's sword. It never learned to lose."),
    ("AN21", "Choir's Last Note", "acc", 88, "SB08", "", {"concord_bonus": 2, "heal_mult": 1.15}, [["S048", 3]], "", "The note the Pale Choir silenced."),
    ("AN22", "Circlet of the Unmade", "acc", 130, "SB12", "", {"mhp_mult": 1.2, "mmp_mult": 1.2, "atb_mult": 1.1}, [], "", "What the Ashen Crown would have been. Nobody should wear it. Someone will."),
    ("AN23", "Hunter's Codex", "acc", 60, "BESTIARY", "", {"reveal_affinity": True, "acc_bonus": 15, "phys_reduce": 0.08}, [["SX_LIBRA", 20]], "", "Every creature you have met, and how it dies."),
]
NAMED_MULT = 1.12   # a named piece is ~12% stronger than tier gear at its level
# accessory base "power" for named accessories: price only (they carry passives, not stats)
ACC_ICON = {"S01": "A021", "S02": "A105", "S03": "A108", "S04": "A109", "S05": "A111", "S06": "A116", "S07": "A013",
            "S08": "A106", "S09": "A017", "S10": "A020", "S11": "A018", "S12": "A021", "S13": "A012", "S14": "A009",
            "S15": "A010", "S16": "A016", "S17": "A019", "S18": "A017", "S19": "A024", "": "A024"}

# set id: (name, {pieces worn: bonus}); a bonus has stat adds (atk, matk, def, res, spd, mhp, mmp), passives, grants
SETS = {
    "S01": ("Drowned Oath", {2: {"def": 4, "passives": {"elem_resist": {"water": True}}}, 3: {"atk": 5, "passives": {"lowhp_guard": 0.3}}}),
    "S02": ("Slagwright", {2: {"atk": 5, "passives": {"elem_resist": {"fire": True}}}, 3: {"passives": {"phys_reduce": 0.06, "counter": 1}}}),
    "S03": ("Sluicewife's Mourning", {2: {"passives": {"mp_regen": 2}}, 3: {"matk": 6, "passives": {"mag_bonus": 0.1}}}),
    "S04": ("Brine Matriarch", {2: {"res": 6, "passives": {"elem_resist": {"water": True}}}, 3: {"passives": {"mhp_mult": 1.1}}}),
    "S05": ("Roc Queen's Plumage", {2: {"spd": 2}, 3: {"passives": {"acc_bonus": 10, "start_atb": 100}}, 4: {"passives": {"auto_revive": True}}}),
    "S06": ("Mere-Mother's Memory", {2: {"passives": {"heal_mult": 1.1}}, 3: {"mmp": 20, "passives": {"mmp_mult": 1.12}}}),
    "S07": ("Lamprey Vestments", {2: {"passives": {"immune": ["poison", "bleed"]}}, 3: {"passives": {"mp_regen": 3}}, 4: {"atk": 8, "grants": "S125"}}),
    "S08": ("Nine-Tailed Court", {2: {"matk": 5, "passives": {"elem_resist": {"fire": True}}}, 3: {"passives": {"mag_bonus": 0.1}}, 4: {"passives": {"atb_mult": 1.08, "immune": ["blind"]}}}),
    "S09": ("Rimebound", {2: {"passives": {"elem_resist": {"ice": True}}}, 3: {"def": 10, "res": 6}, 4: {"passives": {"immune": ["slow"], "mhp_mult": 1.12}}}),
    "S10": ("Hollow Host", {2: {"passives": {"elem_resist": {"light": True}}}, 3: {"passives": {"mercy_barrier": True}}, 4: {"passives": {"heal_mult": 1.12, "concord_bonus": 2}}}),
    "S11": ("Ilyrath's Bones", {2: {"passives": {"elem_resist": {"fire": True}}}, 3: {"atk": 10, "def": 6}}),
    "S12": ("Mile Zero", {2: {"passives": {"atb_mult": 1.05}}, 3: {"spd": 3, "passives": {"acc_bonus": 10}}}),
    "S13": ("Geode", {2: {"def": 5, "passives": {"elem_resist": {"earth": True}}}, 3: {"passives": {"phys_reduce": 0.08}}}),
    "S14": ("Deepforge", {2: {"passives": {"elem_resist": {"fire": True}}}, 3: {"atk": 6, "def": 6, "passives": {"counter": 1}}}),
    "S15": ("Assembler", {2: {"passives": {"elem_resist": {"storm": True}}}, 3: {"passives": {"mp_regen": 2, "reveal_affinity": True}}, 4: {"passives": {"atb_mult": 1.1, "mag_bonus": 0.1}}}),
    "S16": ("Sepulchre", {2: {"passives": {"immune": ["doom"]}}, 3: {"matk": 10, "passives": {"elem_resist": {"shadow": True}}}, 4: {"passives": {"auto_revive": True, "heal_mult": 1.12}}}),
    "S17": ("First Crown", {2: {"atk": 8, "def": 8}, 3: {"passives": {"lowhp_guard": 0.35, "counter": 1}}}),
    "S18": ("Ancient Wyrm", {2: {"passives": {"elem_resist": {"fire": True, "water": True, "earth": True}}}, 3: {"mhp": 300, "passives": {"mhp_mult": 1.15}}, 4: {"passives": {"auto_revive": True, "atb_mult": 1.1}}}),
    "S19": ("Hollow Heart", {2: {"atk": 15, "matk": 15}, 3: {"passives": {"auto_revive": True, "lowhp_guard": 0.3}, "spd": 5}}),
}

# a few reforges into named items at the crafters (the "upgrade" recipes for uniques)
UNIQUE_REFORGES = [
    ("WN01", "WN17", "U3", [("MT06", 4), ("MT38", 4), ("M003", 1)], 6000),   # Hallam's Tidebrand -> Kingsgrave (second copy)
    ("AN01", "AN10", "WOR", [("MT41", 3), ("MT05", 4)], 3000),              # Furnace Heart -> Dragon-Knuckle
    ("AN05", "AN09", "SKY", [("MT45", 3), ("MT12", 4)], 4000),              # Lake-Glass Locket -> Broken Halo
    ("GN07", "GN22", "U2", [("MT24", 3), ("MT40", 3)], 3500),               # Eyrie Crest -> Omega Visor
]

# new ability: Libra (scan) - taught by the Datum Core and the Hunter's Codex, granted by the Appraiser's Lens
NEW_ABILITIES = {
    "SX_LIBRA": {"id": "SX_LIBRA", "name": "Libra", "owner": "", "mp": 2, "power": 0, "kind": "utility", "target": "enemy_one",
                 "desc": "Reads one enemy: level, HP, weaknesses and loot. Fills its bestiary entry.",
                 "ops": [{"op": "reveal", "what": "scan"}], "family": "skill", "anim": "cast", "element": "none",
                 "elemental_spell": False, "revive": False, "field": False, "concord": True},
}

# enemies that scan the party (their first move); the battle shows the reading as a message
SCANNERS = {"E099": "Keeper Drone", "E101": "Volt Turret", "E105": "Datum Ghost", "E106": "Chrome Hound",
            "BX13": "", "BX18": "", "BX19": "", "SB05": ""}

# ---------------------------------------------------------------- bestiary completion rewards
BESTIARY_REWARDS = {
    "seen": {25: [["I002", 3], ["IC03", 2]], 50: [["AC03", 1]], 75: [["I024", 1], ["M003", 2]], 100: [["AN23", 1]]},
    "defeated": {25: [["M002", 2], ["IC05", 2]], 50: [["I003", 3], ["IC09", 2]], 75: [["AC06", 1]], 100: [["MT46", 1], ["I024", 3]]},
}

# ---------------------------------------------------------------- economy (docs/expansion/ECONOMY.md)
GOLD_FLAT_UNTIL = 14          # enemies up to this level keep the canon gold (CH01-CH04 unchanged)
GOLD_SLOPE = 0.035            # +3.5% per level above it
INN_BY_REGION = {"R01": 0, "R02": 0, "R03": 60, "R08": 80, "R06": 90, "R04": 100, "U1": 110, "R05": 120, "R07": 140,
                 "R09": 160, "U2": 180, "SKY": 200, "U3": 250}
INN_POST = 200                # World of Ruin surface inns (post-fault)


def gold_mult(level):
    return 1.0 if level <= GOLD_FLAT_UNTIL else 1.0 + GOLD_SLOPE * (level - GOLD_FLAT_UNTIL)


# ---------------------------------------------------------------- build
def _slot_of(kind):
    if kind in CLASSES:
        return "weapon"
    if kind == "acc":
        return "accessory"
    return ARMOR_SLOT[kind]


def _teach_text(abilities, teach):
    if not teach:
        return ""
    return "Teaches " + ", ".join(abilities[a]["name"] for a, _ in teach if a in abilities) + "."


def _named_desc(nid, abilities):
    n = [x for x in NAMED if x[0] == nid][0]
    bits = [n[9]]
    pt = passive_text(n[6])
    if pt:
        bits.append(pt + ".")
    tt = _teach_text(abilities, n[7])
    if tt:
        bits.append(tt)
    if n[5]:
        bits.append("Set: %s." % SETS[n[5]][0])
    return " ".join(bits)


def build(content, crafting, check_ops, next_icon):
    """Adds tier gear, named items, materials, crafted items and the Libra ability; returns content['gear2']."""
    items, ab = content["items"], content["abilities"]
    for aid, a in NEW_ABILITIES.items():
        check_ops(aid, a["ops"])
        ab[aid] = dict(a)
    tier_items = {}
    added = []
    for ti, (tid, prefix, band, gate, elem) in enumerate(TIERS):
        lv = tier_level(tid)
        rec = {"weapons": [], "armor": [], "acc": [], "price": {}}
        for ci, cid in enumerate(CLASSES):
            wid = "WR%03d" % (ti * 8 + ci + 1)
            atk, mag, price, near, first = weapon_stats(items, cid, lv)
            nouns = W_NOUNS[cid]
            it = {"id": wid, "name": "%s %s" % (prefix, nouns[ti % len(nouns)]), "kind": "weapon", "owner": cid,
                  "tier": ti + 1, "atk": atk, "mag": mag, "price": price, "two_handed": first["two_handed"],
                  "ranged": first["ranged"], "allowed": [cid], "sellable": True, "src": "gear2", "region_tier": tid,
                  "level": int(round(lv)), "icon_base": near}
            p = {}
            if elem and ci % 2 == ti % 2 and elem not in ("poison",):
                p["weapon_element"] = elem
            if p:
                it["passives"] = p
            it["desc"] = "%s make. %s" % (REGION_NAME[tid], passive_text(p) or "No passive; plain good steel.")
            items[wid] = it
            rec["weapons"].append(wid)
            rec["price"][wid] = price
        for ai, kind in enumerate(ARMOR_KINDS):
            gid = "GR%03d" % (ti * 5 + ai + 1)
            bk = kind if kind != "head" else ("head" if ti % 2 == 0 else "head_r")
            d, r, price, near = armor_stats(items, bk, lv)
            nouns = A_NOUNS[kind]
            p = {}
            if elem and ai == ti % 5 and elem != "poison":
                p["elem_resist"] = {elem: True}
            if elem == "poison" and ai == ti % 5:
                p["immune"] = ["poison"]
            it = {"id": gid, "name": "%s %s" % (prefix, nouns[ti % len(nouns)]), "kind": "armor", "slot": ARMOR_SLOT[kind],
                  "allowed": list(ARMOR_ALLOWED[kind]), "def": d, "res": r, "price": price, "tier": ti + 1, "sellable": True,
                  "src": "gear2", "region_tier": tid, "level": int(round(lv)), "icon_base": near}
            if p:
                it["passives"] = p
            it["desc"] = "%s make. %s" % (REGION_NAME[tid], passive_text(p) or "No passive.")
            items[gid] = it
            rec["armor"].append(gid)
            rec["price"][gid] = price
        a_price = armor_stats(items, "robe", lv)[2]
        for k, (name, pas) in enumerate(TIER_ACC[tid]):
            aid = "AR%03d" % (ti * 2 + k + 1)
            price = max(300, int(round(a_price * (1.1 + 0.2 * k) / 10.0)) * 10)
            items[aid] = {"id": aid, "name": name, "kind": "accessory", "slot": "accessory", "price": price,
                          "allowed": list(CLASSES), "sellable": True, "passives": dict(pas), "src": "gear2",
                          "region_tier": tid, "level": int(round(lv)), "desc": "%s make. %s" % (REGION_NAME[tid], passive_text(pas)),
                          "icon_base": ["A101", "A104", "A107", "A110", "A113", "A116"][(ti + k) % 6]}
            rec["acc"].append(aid)
            rec["price"][aid] = price
        tier_items[tid] = rec
        added += rec["weapons"] + rec["armor"] + rec["acc"]
    # named items
    sources = {}
    for (nid, name, kind, lv, src, set_id, pas, teach, grants, flavour) in NAMED:
        slot = _slot_of(kind)
        it = {"id": nid, "name": name, "kind": "weapon" if slot == "weapon" else ("accessory" if slot == "accessory" else "armor"),
              "unique": True, "sellable": False, "src": "gear2", "level": lv, "named": True}
        if slot == "weapon":
            atk, mag, price, near, first = weapon_stats(items, kind, lv, NAMED_MULT)
            it.update(owner=kind, tier=6, atk=atk, mag=mag, price=price, two_handed=first["two_handed"], ranged=first["ranged"],
                      allowed=[kind], icon_base=near)
        elif slot == "accessory":
            price = min(60000, max(500, armor_stats(items, "robe", lv)[2]))
            it.update(slot="accessory", price=price, allowed=list(CLASSES), icon_base=ACC_ICON.get(set_id, "A024"))
        else:
            d, r, price, near = armor_stats(items, kind, lv, NAMED_MULT)
            it.update(slot=ARMOR_SLOT[kind], allowed=list(ARMOR_ALLOWED[kind]), **{"def": d, "res": r}, price=price, tier=6,
                      icon_base=near)
        if pas:
            it["passives"] = dict(pas)
        if teach:
            it["teach"] = [list(t) for t in teach]
        if grants:
            it["grants"] = grants
        if set_id:
            it["set"] = set_id
        it["desc"] = _named_desc(nid, ab)
        it["found"] = src
        items[nid] = it
        added.append(nid)
        sources[nid] = src
    added += crafting.add_items(items, check_ops)
    for aid in crafting.ACCESSORIES:
        it = items[aid]
        t = passive_text(it.get("passives", {}))
        if it.get("grants"):
            t = ("Grants %s. " % ab[it["grants"]]["name"]) + t
        it["desc"] = (t or "A crafted charm.").strip()
    # icons: new items take cells after the base atlas, in sorted id order; art = tinted copy of icon_base
    icon = next_icon
    for iid in sorted(added):
        items[iid]["icon"] = icon
        icon += 1
    unique_reforges = [dict(kind="reforge", input=a, result=b, count=1, tier=t, mats=list(m), gold=g)
                       for (a, b, t, m, g) in UNIQUE_REFORGES]
    recipes = crafting.recipes(TIER_ORDER, tier_items, unique_reforges)
    sets = {}
    for sid, (name, bonus) in SETS.items():
        pieces = [n[0] for n in NAMED if n[5] == sid]
        sets[sid] = {"id": sid, "name": name, "pieces": pieces,
                     "bonus": {str(k): v for k, v in bonus.items()}}
    shop_tiers = {}
    for tid, shops in SHOP_TIERS.items():
        for sh in shops:
            shop_tiers.setdefault(sh, []).append(tid)
    tiers = {tid: {"id": tid, "name": REGION_NAME[tid], "prefix": prefix, "band": list(band), "gate": gate,
                   "level": round(tier_level(tid), 1), "items": tier_items[tid]["weapons"] + tier_items[tid]["armor"] + tier_items[tid]["acc"]}
             for (tid, prefix, band, gate, elem) in TIERS}
    return {"tiers": tiers, "tier_order": TIER_ORDER, "shop_tiers": shop_tiers, "shop_extra_kinds": SHOP_EXTRA_KINDS,
            "sets": sets, "recipes": recipes, "sources": sources, "gather": {k: dict(v, drops=[list(d) for d in v["drops"]])
                                                                            for k, v in crafting.GATHER.items()},
            "gather_verb": crafting.GATHER_VERB, "bestiary_rewards": {k: {str(p): r for p, r in v.items()} for k, v in BESTIARY_REWARDS.items()},
            "inn": INN_BY_REGION, "inn_post": INN_POST, "crafters": {}, "added": len(added)}


def apply_enemies(EN):
    """Scanners: their cycle opens with a scan of one hero (a battle message)."""
    for eid in SCANNERS:
        spec = EN.E.get(eid) or EN.B.get(eid)
        if spec is None:
            continue
        base = EN.mv("Scan", [{"op": "scan_foe"}], anim="cast", element="none")
        spec["moves"]["scan"] = base
        if "cycle" in spec:
            spec["cycle"] = ["scan"] + list(spec["cycle"])
        if spec.get("phases"):
            spec["phases"][0]["cycle"] = ["scan"] + list(spec["phases"][0]["cycle"])


def finish(content, bestiary_rows, cat_bosses, crafting):
    """After enemies, formations and maps are built: parts/named drops, gold curve, bestiary locations, crafters,
    node validation. Returns a list of error strings."""
    errs = []
    for n in NAMED:   # teach names need the whole ability table (the overhaul cast adds its kits after build)
        content["items"][n[0]]["desc"] = _named_desc(n[0], content["abilities"])
    en = content["enemies"]
    g2 = content["gear2"]
    rows = {r[0]: r for r in bestiary_rows}
    # hunting parts (new enemies and their level variants) and the gold curve (every enemy)
    for eid, e in en.items():
        base = e.get("variant_of", eid)
        if base in rows and "part" not in e.get("tags", []):
            have = {d["item"] for d in e["drops"]}
            for mid, ch in crafting.parts_for(rows[base]):
                if mid not in have:
                    e["drops"].append({"item": mid, "chance": ch})
        lv = int(e.get("level", 1))
        if e.get("gold", 0) > 0:
            e["gold"] = int(round(e["gold"] * gold_mult(lv)))
    # named drops from bosses and superbosses
    for nid, src in g2["sources"].items():
        if src in en:
            en[src]["drops"].append({"item": nid, "chance": 100})
        elif src != "BESTIARY":
            pass   # chest ids are checked against the maps below
    # superbosses also leave a Wyrm Heart now and then
    for sb in ("SB01", "SB02", "SB03", "SB04"):
        if sb in en:
            en[sb]["drops"].append({"item": "MT46", "chance": 50})
    # bestiary locations: encounter groups on maps and zones -> place names; bosses -> their catalogue location
    locs = content.get("locations", {})
    forms = content["formations"]

    def label(m):
        L = m.get("location", "")
        if L and L in locs:
            return locs[L]["name"]
        return m.get("name", m["id"]).split(" - ")[0]
    where = {}

    def add_group(gid, lab):
        for fid in forms["groups"].get(gid, []):
            f = forms["formations"].get(fid, {})
            for s in f.get("enemies", []):
                if isinstance(s, dict):
                    continue
                b = en.get(s, {}).get("variant_of", s)
                lst = where.setdefault(b, [])
                if lab not in lst:
                    lst.append(lab)
    for mid, m in content["maps"].items():
        world = m.get("kind") == "world"
        if m.get("encounters") and m["encounters"] != "none":
            add_group(m["encounters"], REGION_NAME.get(m.get("region", ""), label(m)) if world else label(m))
        for e in m["entities"]:
            if e["type"] == "zone" and e.get("encounters"):
                g = e["encounters"]
                reg = g.split("_", 1)[1] if g.startswith(("W_", "WP_")) else m.get("region", "")
                lab = REGION_NAME.get(reg, label(m)) if world else label(m)
                if g.startswith("WP_"):
                    lab += " (ruin)"
                add_group(g, lab)
    dn = content.get("dungeons", {})
    for b in cat_bosses:
        loc = b.get("location", "")
        lab = locs.get("L_" + loc, {}).get("name") or dn.get(loc, {}).get("name") or REGION_NAME.get(loc, "")
        if lab:
            where.setdefault(b["id"], [lab])
    for eid, e in en.items():
        if "variant_of" in e or "part" in e.get("tags", []):
            continue
        e["where"] = where.get(eid, [])[:6]
    # crafters: every NPC whose id starts with crafter_ -> tier of its place
    places = {}
    for mid, m in content["maps"].items():
        pl = mid.split("_")[0]
        if m.get("region"):
            places.setdefault(pl, m["region"])
        for e in m["entities"]:
            if e["type"] == "npc" and e["id"].startswith("crafter_"):
                p = e["id"][8:].upper()
                g2["crafters"][e["id"]] = PLACE_TIER_OVERRIDE.get(p, None) or p
            if e["type"] == "node":
                if e["table"] not in g2["gather"]:
                    errs.append("%s: node at %d,%d unknown table %s" % (mid, e["x"], e["y"], e["table"]))
                elif g2["gather"][e["table"]]["kind"] != e["kind"]:
                    errs.append("%s: node at %d,%d kind %s does not match table %s" % (mid, e["x"], e["y"], e["kind"], e["table"]))
    for cid, p in list(g2["crafters"].items()):
        t = p if p in TIER_ORDER else places.get(p, "R01")
        g2["crafters"][cid] = t if t in TIER_ORDER else "R01"
    # sanity: every named chest source exists on a map, every recipe/reward item exists
    chests = {e["id"] for m in content["maps"].values() for e in m["entities"] if e["type"] == "chest"}
    chest_items = {e["id"]: e["item"] for m in content["maps"].values() for e in m["entities"] if e["type"] == "chest"}
    for nid, src in g2["sources"].items():
        if src.startswith(("BX", "SB")) or src == "BESTIARY":
            if src.startswith(("BX", "SB")) and src not in en:
                errs.append("named %s: unknown boss %s" % (nid, src))
            continue
        if src not in chests:
            errs.append("named %s: unknown chest %s" % (nid, src))
        elif chest_items[src] != nid:
            errs.append("named %s: chest %s holds %s" % (nid, src, chest_items[src]))
    items = content["items"]
    for rid, r in g2["recipes"].items():
        for iid in [r["result"]] + [m[0] for m in r["mats"]] + ([r["input"]] if r["kind"] == "reforge" else []):
            if iid not in items:
                errs.append("recipe %s: unknown item %s" % (rid, iid))
    for track in g2["bestiary_rewards"].values():
        for lst in track.values():
            for iid, n in lst:
                if iid not in items:
                    errs.append("bestiary reward: unknown item %s" % iid)
    for it in items.values():
        for a, _ in it.get("teach", []):
            if a not in content["abilities"]:
                errs.append("%s teaches unknown ability %s" % (it["id"], a))
    return errs
