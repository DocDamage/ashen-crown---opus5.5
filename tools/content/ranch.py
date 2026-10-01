"""Ranching (one farm per major kingdom), built on the owner's "Super Retro Ranch" pack (premium v32, by Gif).
The pack is a 16x16 farming kit; docs/expansion/RANCH_PACK.md is its readme (sheets, frame orders, anchors).

Runtime: game/src/meta/ranch.gd (class Ranch), state in Game.S["ranch"][rid]; scene command `ranch <op>`
(content_src/scenes/ranch.scn). Maps: tools/maps48/maps/ranch.py writes content_src/maps/ranch.map (grid + entities)
and, where the pack is installed, the 48px map art. Sheets: tools/art/install_ranch.py.

Time: one quarter day = 360 in-game minutes = one "slot" (FieldSys.weather_slot: day * 4 + clock / 360). Weather is
deterministic per region and slot (FieldSys.region_weather), so growth can be caught up for slots the player missed.

Rules
  tools     the rancher lends a Hoe, a Watering Can and a Sickle (key items RT01-RT03) on the first talk.
  plots     cells of grid kind "plot" (walkable dirt beds). Face one and press Confirm for the next step:
            hoe the dirt -> plant a seed (the rancher's seed box sells seed) -> water it -> harvest with the sickle.
            A watered crop grows one stage at each of the next four quarter-day turns; rain waters every plot for that
            quarter; a dry crop stalls. Stages are frames of the crop's growth strip (CROPS: `stages`, last = ripe).
  hazards   Rimeholt (frost): on snowy nights a growing crop loses a stage (never below the first). Cinderwake (ember):
            in an ash storm a dry growing crop may scorch and lose a stage. High Aerie (wind): crops shake (visual).
            Mice: on a night with a ripe crop and no cat, mice may nibble one (it drops back a stage); with a cat the
            cat catches them instead (a dead mouse on the step). Foxes (Akagane, Harrowfen): a night with the pen
            gate left open costs every egg in the nest.
  animals   bought once per ranch (ANIMALS). Confirm while facing one pets it (once a day: +1 affection, 0-10 shown
            as five hearts) and takes what it has: cows milk daily, coneys wool every second day, pigs come as
            piglets and grow up after PIG_GROW_DAYS days, then root up a truffle every second day. Doves lay one egg
            a day each into the nest (at most 3 waiting); an egg left EGG_HATCH_DAYS days hatches into another dove
            (up to 3). Affection 6+ doubles the yield, 10 triples it. A day without petting after two costs a point.
            A cat (cheap) keeps the mice off.
  kart      the rail kart's chest takes ranch goods; send it and it rolls off down the line and comes back the next
            morning with coins (the goods' sell value plus KART_BONUS).
Map hooks (validated in _check_maps): rancher npc `rancher_<rid lower>` (its scene runs `ranch menu <RID>`),
`kart_<RID>` sprite=ranch:kart:<RID>, `nest_<RID>` sprite=ranch:nest:<RID>, owned animals `own_<RID>_<kind>`
(if=ranch:<RID>:own:<kind>; doves own_<RID>_bird1..3 if=ranch:<RID>:birds:<n>), a pen gate
`block x y tile=gate if=!ranch:<RID>:gate`, and at least MIN_PLOTS plot cells.
"""

PACK_ROOT = "ranch/pack/"      # under game/assets/ext/ (installed 16 px originals)

# ---------------------------------------------------------------- crops (19, all of the pack's growth strips)
# id: (crop item, seed item, name, growth strip (under crops/<id>/), frame w, frame h, stages (frames, last = ripe),
#      withered frame, yield, seed price, crop price, icon strip, icon frame, signpost cell on objects_01 (col, row))
CROPS = {
    "wheat": ("RV01", "RS01", "Wheat", "growth_basic/wheat_18x32_8frames.png", 18, 32, [0, 1, 2, 3, 4, 5], 7, 3, 20, 24,
              "icon/wheat_icon_16x16_9frames.png", 5, (3, 10)),
    "carrot": ("RV02", "RS02", "Carrot", "growth_basic/carrot_16x16_7frames.png", 16, 16, [0, 1, 2, 3, 4, 5], 6, 3, 20, 30,
               "icon/carrot_icon_16x16_2frames.png", 1, (1, 9)),
    "potato": ("RV03", "RS03", "Potato", "growth_basic/potato_16x32_7frames.png", 16, 32, [0, 1, 2, 3, 4, 5], 6, 4, 30, 30,
               "icon/potato_icon_16x16.png", 0, (4, 10)),
    "pumpkin": ("RV04", "RS04", "Pumpkin", "growth_basic/pumpkin_16x16_7frames.png", 16, 16, [0, 1, 2, 3, 4, 5], 6, 2, 60, 110,
                "icon/pumpkin_icon_16x16_3frames.png", 2, (6, 7)),
    "onion": ("RV05", "RS05", "Onion", "growth_basic/onion_16x32_7frames.png", 16, 32, [0, 1, 2, 3, 4, 5], 6, 3, 20, 26,
              "icon/onion_icon_16x16.png", 0, (2, 10)),
    "beetroot": ("RV06", "RS06", "Beetroot", "growth_basic/beetroot_16x16_7frames.png", 16, 16, [0, 1, 2, 3, 4, 5], 6, 3, 30, 40,
                 "icon/beetroot_icon_16x16.png", 0, (7, 7)),
    "leek": ("RV07", "RS07", "Leek", "growth_basic/leek_16x32_7frames.png", 16, 32, [0, 1, 2, 3, 4, 5], 6, 3, 30, 36,
             "icon/leek_icon_16x16.png", 0, (4, 8)),
    "radish": ("RV08", "RS08", "Radish", "growth_basic/radish_16x16_7frames.png", 16, 16, [0, 1, 2, 3, 4, 5], 6, 3, 25, 34,
               "icon/radish_icon_16x16_2frames.png", 1, (1, 10)),
    "tomato": ("RV09", "RS09", "Tomato", "growth_basic/tomato_16x32_23frames.png", 16, 32, [0, 2, 4, 6, 8, 10, 13, 16], 20, 4, 40, 40,
               "icon/tomato_icon_16x16_4frames.png", 3, (7, 8)),
    "cauliflower": ("RV10", "RS10", "Cauliflower", "growth_basic/cauliflower_16x16_7frames.png", 16, 16, [0, 1, 2, 3, 4, 5], 6, 2, 45, 70,
                    "icon/cauliflower_icon_16x16.png", 0, (5, 9)),
    "berry": ("RV11", "RS11", "Fen Berry", "growth_basic/berry_16x16_7frames.png", 16, 16, [0, 1, 2, 3, 4, 5], 6, 4, 40, 45,
              "icon/berry_icon_16x16.png", 0, (3, 7)),
    "pepper": ("RV12", "RS12", "Ember Pepper", "growth_basic/pepper_16x32_11frames.png", 16, 32, [0, 2, 4, 5, 6, 7, 8, 9], 10, 3, 60, 80,
               "icon/pepper_icon_16x16_2frames.png", 1, (3, 9)),
    "eggplant": ("RV13", "RS13", "Eggplant", "growth_basic/eggplant_16x32_7frames.png", 16, 32, [0, 1, 2, 3, 4], 6, 3, 40, 50,
                 "icon/eggplant_icon_16x16.png", 0, (5, 7)),
    "grape": ("RV14", "RS14", "Court Grapes", "growth_basic/grape_18x32_7frames.png", 18, 32, [0, 1, 2, 3, 4, 5], 6, 3, 70, 90,
              "icon/grape_icon_16x16_2frames.png", 1, (6, 8)),
    "bamboo": ("RV15", "RS15", "Bamboo Shoot", "growth_basic/bamboo_16x32_7frames.png", 16, 32, [0, 1, 2, 3, 4], 5, 3, 50, 70,
               "icon/bamboo_icon_16x16_2frames.png", 0, (0, 9)),
    # corn grows along its 29-frame growth_smooth strip; frozen / on_fire / shake / tempest strips show its hazards
    "corn": ("RV16", "RS16", "Corn", "growth_smooth/corn_16x32_29frames.png", 16, 32, [0, 3, 6, 10, 14, 18, 19], 27, 3, 35, 45,
             "icon/corn_icon_16x16_2frames.png", 1, (5, 10)),
    "broccoli": ("RV17", "RS17", "Broccoli", "growth_basic/broccoli_16x32_7frames.png", 16, 32, [0, 1, 2, 3, 4, 5], 6, 2, 45, 66,
                 "icon/broccoli_icon_16x16.png", 0, (6, 9)),
    "celery": ("RV18", "RS18", "Celery", "growth_basic/celery_16x32_7frames.png", 16, 32, [0, 1, 2, 3, 4, 5], 6, 3, 35, 42,
               "icon/celery_icon_16x16.png", 0, (4, 7)),
    "lettuce": ("RV19", "RS19", "Lettuce", "growth_basic/lettuce_16x16_7frames.png", 16, 16, [0, 1, 2, 3, 4, 5], 6, 2, 25, 38,
                "icon/lettuce_icon_16x16.png", 0, (7, 9)),
}
# corn's hazard strips (8 frames each matching growth_basic; tempest 12 loop frames)
CORN_STRIPS = {"frozen": "crops/corn/frozen/corn_frozen_16x32_8frames.png", "fire": "crops/corn/on_fire/corn_fire_16x32_8frames.png",
               "shake": "crops/corn/shake/corn_shake_16x32_8frames.png", "tempest": "crops/corn/tempest/corn_tempest_16x32_12frames.png"}

# ---------------------------------------------------------------- animals
# kind: (name, good item, every n days, price, note)
ANIMALS = {
    "cow": ("Milk Cow", "RK01", 1, 900, "Milk every day, if you come for it. She leans into a brush and nothing else."),
    "bird": ("Doves", "RK02", 1, 350, "A pair of doves for the cote. They lay in the nest; leave an egg long enough and there are three of them."),
    "pig": ("Piglet", "RK04", 2, 1400, "A piglet. Feed it and it grows; a grown pig roots up a truffle every second day."),
    "bunny": ("Angora Coney", "RK03", 2, 700, "Combed every second day for a fistful of wool. It holds a grudge about the comb."),
    "cat": ("Barn Cat", "", 0, 150, "From the barn litter. It keeps the mice off the ripe beds and asks for nothing you'd give it."),
}
ANIMAL_ORDER = ["cow", "bird", "pig", "bunny", "cat"]
PIG_GROW_DAYS = 3
EGG_HATCH_DAYS = 3
MAX_EGGS = 3
MAX_BIRDS = 3
KART_BONUS = 0.10
MIN_PLOTS = 8
COW_COLOURS = ["black", "black_beige", "black_cyan", "black_lime", "black_pink", "black_yellow", "blue", "blue_beige",
               "blue_cyan", "blue_lime", "blue_pink", "blue_yellow", "brown", "brown_beige", "brown_cyan", "brown_lime",
               "brown_pink", "brown_yellow", "green", "green_beige", "green_cyan", "green_lime", "green_pink", "green_yellow",
               "purple", "purple_beige", "purple_cyan", "purple_lime", "purple_pink", "purple_yellow", "red", "red_beige",
               "red_cyan", "red_lime", "red_pink", "red_yellow"]
PIG_COLOURS = ["black", "cyan", "green", "orange", "pink", "purple"]
# ranch folk (pack farmers): look -> sheet prefix; tasks idle / walk / hoe / water / shovel
FOLK = {"m": "characters/males/male_01/%s/male_01_%s", "mh": "characters/males/male_01/%s/male_01_hat_%s",
        "f": "characters/females/female_01/%s/female_01_%s", "fh": "characters/females/female_01/%s/female_01_hat_%s"}
FOLK_TASKS = ["idle", "walk", "hoe", "water", "shovel"]

# ---------------------------------------------------------------- ranches
# hazard: frost | ember | wind | "" ; foxes: a night with the gate open costs the nest's eggs
RANCHES = {
    "R01": dict(name="Fallowmere Ranch", map="T01_RANCH", town="Brackenford", rancher="Agna Fallow", look="fh", region="R01",
                seeds=["wheat", "carrot", "potato", "lettuce"], cow="brown", pig="pink", hazard="", foxes=False),
    "R02": dict(name="Soot Paddock", map="T03_RANCH", town="Cinderwake", rancher="Brann Coker", look="m", region="R02",
                seeds=["onion", "beetroot", "pepper"], cow="black", pig="black", hazard="ember", foxes=False),
    "R03": dict(name="Gullbank Croft", map="T04_RANCH", town="Bellharbor", rancher="Maude Tiller", look="f", region="R03",
                seeds=["radish", "tomato", "cauliflower"], cow="brown_beige", pig="pink", hazard="", foxes=False),
    "R04": dict(name="Windbreak Fold", map="T05_RANCH", town="High Aerie", rancher="Sefton Crag", look="mh", region="R04",
                seeds=["leek", "corn", "pumpkin"], cow="black_beige", pig="pink", hazard="wind", foxes=False),
    "R05": dict(name="Brinewell Steading", map="T06_RANCH", town="Nacre", rancher="Yara Saltmarrow", look="fh", region="R05",
                seeds=["eggplant", "celery", "wheat"], cow="red_beige", pig="orange", hazard="", foxes=False),
    "R07": dict(name="Maple Gate Farm", map="N28_RANCH", town="Akagane", rancher="Okuni Hara", look="f", region="R07",
                seeds=["bamboo", "grape", "radish"], cow="red", pig="orange", hazard="", foxes=True),
    "R08": dict(name="Lazar Fields", map="N22_RANCH", town="Harrowfen", rancher="Gideon Marl", look="m", region="R08",
                seeds=["berry", "leek", "broccoli"], cow="black_yellow", pig="black", hazard="", foxes=True),
    "R09": dict(name="Rimefold", map="N32_RANCH", town="Rimeholt", rancher="Hild Ulfsdottir", look="fh", region="R09",
                seeds=["potato", "carrot", "berry"], cow="black", pig="black", hazard="frost", foxes=False),
}
RANCH_ORDER = ["R01", "R02", "R03", "R04", "R05", "R07", "R08", "R09"]


def _heal(n):
    return dict(target="ally_one", ops=[{"op": "heal", "flat": n}], battle=True, field=True)


# raw goods, crops, cooked dishes and the one crafted wearable. Consumable specs as tables.CONSUMABLE.
GOODS = {
    "RK01": ("Fresh Milk", 40, "Warm from the pail. Restores 150 HP to one ally.", _heal(150)),
    "RK02": ("Dove Egg", 30, "Small and pale. Restores 90 HP to one ally.", _heal(90)),
    "RK03": ("Angora Wool", 140, "Combed coney wool, soft as smoke. Weavers and crafters want it.", None),
    "RK04": ("Black Truffle", 420, "Rooted up by a pig and fought over by cooks. Sells for a great deal.", None),
}
TOOLS = {   # lent by the ranchers (key items)
    "RT01": ("Ranch Hoe", "Lent by a rancher. Breaks dirt into a bed. Face a dirt plot and press Confirm."),
    "RT02": ("Watering Can", "Lent by a rancher. A watered crop grows a stage every quarter day for a day."),
    "RT03": ("Sickle", "Lent by a rancher. Takes a ripe crop off its bed."),
}
CROP_EFFECT = {   # crops that can be eaten raw; the rest are materials
    "carrot": ("Raw and crunchy. Restores 60 HP and cures Blind.",
               dict(target="ally_one", ops=[{"op": "heal", "flat": 60}, {"op": "cleanse", "ids": ["blind"]}], battle=True, field=True)),
    "beetroot": ("Earthy and red. Restores 80 HP to one ally.", _heal(80)),
    "radish": ("Sharp enough to clear the head. Cures Poison.",
               dict(target="ally_one", ops=[{"op": "cleanse", "ids": ["poison"]}], battle=True, field=True)),
    "tomato": ("Ripe and split. Restores 100 HP to one ally.", _heal(100)),
    "berry": ("Bitter fen berries. Restores 15 MP to one ally.",
              dict(target="ally_one", ops=[{"op": "mp", "amount": 15}], battle=True, field=True)),
    "pepper": ("Burns the tongue awake. Restores 40 HP and cures Sleep.",
               dict(target="ally_one", ops=[{"op": "heal", "flat": 40}, {"op": "cleanse", "ids": ["sleep"]}], battle=True, field=True)),
    "grape": ("The fox court's table grapes. Restores 25 MP to one ally.",
              dict(target="ally_one", ops=[{"op": "mp", "amount": 25}], battle=True, field=True)),
    "lettuce": ("Cold and crisp. Restores 50 HP to one ally.", _heal(50)),
}
CROP_DESC = {
    "wheat": "A sheaf of wheat. Millers and bakers pay for it.", "potato": "Fist-sized and dirty. Better in a stew.",
    "pumpkin": "Heavy as a child. Bakers want it for loaves.", "onion": "It makes the cook weep, and the stew worth eating.",
    "leek": "Long and pale. Broth needs it.", "cauliflower": "A tight white head. The salt cooks pickle it.",
    "eggplant": "Purple and glossy. Basin cooks roast it on stones.", "bamboo": "A tender shoot. The fox court eats it in spring.",
    "corn": "A full ear. Fodder, flour or supper.", "broccoli": "A green fist of a vegetable. The Board approves of it.",
    "celery": "Stringy and loud to eat. Good in broth.",
}
COOKED = {
    "RF01": ("Farmhouse Stew", 520, "Milk, potato and onion, boiled until it gives up. Restores 600 HP to the whole party.",
             dict(target="ally_all", ops=[{"op": "heal", "flat": 600}], battle=True, field=True)),
    "RF02": ("Truffle Tart", 900, "Too rich for a farmhand. Restores 40 MP to the whole party.",
             dict(target="ally_all", ops=[{"op": "mp", "amount": 40}], battle=True, field=True)),
    "RF03": ("Pumpkin Loaf", 300, "Dense, sweet, keeps a week. Restores 500 HP to one ally and cures Poison.",
             dict(target="ally_one", ops=[{"op": "heal", "flat": 500}, {"op": "cleanse", "ids": ["poison"]}], battle=True, field=True)),
    "RF04": ("Pepper Broth", 480, "It hurts going down and keeps you up. Grants Regen to the whole party.",
             dict(target="ally_all", ops=[{"op": "status", "id": "regen", "chance": 100, "dur": 4}], battle=True, field=False)),
    "RF05": ("Grape Cordial", 600, "The fox court's cordial, thick as syrup. Restores 90 MP to one ally.",
             dict(target="ally_one", ops=[{"op": "mp", "amount": 90}], battle=True, field=True)),
    "RF06": ("Rind Cheese", 260, "Pressed milk, rind and all. Restores 320 HP to one ally.", _heal(320)),
    "RF07": ("Green Broth", 340, "Leek, celery and broccoli, simmered thin. Restores 250 HP to the whole party.",
             dict(target="ally_all", ops=[{"op": "heal", "flat": 250}], battle=True, field=True)),
}
WEAR = {
    "RA01": ("Shepherd's Muffler", 1600, {"immune": ["sleep", "slow"]}, "A muffler of angora wool. Wards off Sleep and Slow."),
}
# cooking recipes (appended after every other recipe, so older recipe ids never move): result, count, tier, mats, crowns
RECIPES = [
    ("RF01", 2, "R01", [("RK01", 1), ("RV03", 2), ("RV05", 1)], 0),
    ("RF03", 2, "R01", [("RV04", 1), ("RV01", 2), ("RK02", 1)], 0),
    ("RF06", 1, "R01", [("RK01", 3)], 0),
    ("RF02", 1, "R02", [("RK04", 1), ("RV01", 2), ("RK02", 2)], 0),
    ("RF04", 1, "R04", [("RV12", 2), ("RV07", 1), ("RK01", 1)], 0),
    ("RF05", 1, "R07", [("RV14", 3), ("RK02", 1)], 0),
    ("RA01", 1, "R04", [("RK03", 4), ("MT30", 2)], 400),
    ("RF07", 2, "R08", [("RV07", 1), ("RV18", 1), ("RV17", 1)], 0),
]

# icon sheet cells (assets/ext/ranch/icons.png, 16x16, 8 per row), written by tools/art/install_ranch.py
ICON_ORDER = (["RK01", "RK02", "RK03", "RK04"] + ["RV%02d" % i for i in range(1, 20)] + ["RS%02d" % i for i in range(1, 20)]
              + ["RF01", "RF02", "RF03", "RF04", "RF05", "RF06", "RF07", "RA01", "RT01", "RT02", "RT03"])


def _items():
    out = {}
    for iid, (name, price, desc, spec) in GOODS.items():
        out[iid] = (name, price, desc, spec, "good")
    for cid, v in CROPS.items():
        crop, seed, name, stages, yld, sp, cp = v[0], v[1], v[2], v[6], v[8], v[9], v[10]
        eff = CROP_EFFECT.get(cid)
        out[crop] = (name, cp, eff[0] if eff else CROP_DESC[cid], eff[1] if eff else None, "crop")
        out[seed] = (name + " Seed", sp, "Seed for a ranch bed: hoe, plant, water. %d stages; yields %d." % (len(stages) - 1, yld), None, "seed")
    for iid, (name, price, desc, spec) in COOKED.items():
        out[iid] = (name, price, desc, spec, "cooked")
    return out


def apply(content, err, check_ops=None):
    items = content["items"]
    nxt = max(int(i.get("icon", -1)) for i in items.values()) + 1
    for iid, (name, price, desc, spec, group) in sorted(_items().items()):
        if iid in items and items[iid].get("src") != "ranch":
            err("ranch item %s collides with an existing item" % iid)
            continue
        d = {"id": iid, "name": name, "price": price, "desc": desc, "sellable": True, "revive": False, "special": "",
             "allowed": [], "src": "ranch", "ranch": group, "icon_ranch": ICON_ORDER.index(iid), "icon": nxt}
        nxt += 1
        if spec:
            if check_ops:
                check_ops(iid, spec["ops"])
            d.update(kind="consumable", target=spec["target"], ops=spec["ops"], battle=spec.get("battle", True),
                     field=spec.get("field", False))
        else:
            d["kind"] = "material"
        items[iid] = d
    for aid, (name, price, pas, desc) in WEAR.items():
        items[aid] = {"id": aid, "name": name, "kind": "accessory", "slot": "accessory", "price": price, "sellable": True,
                      "allowed": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08"], "passives": dict(pas), "src": "ranch",
                      "desc": desc, "crafted": True, "icon_ranch": ICON_ORDER.index(aid), "icon": nxt}
        nxt += 1
    for tid, (name, desc) in TOOLS.items():
        items[tid] = {"id": tid, "name": name, "kind": "key", "price": 0, "desc": desc, "sellable": False, "src": "ranch",
                      "ranch": "tool", "icon_ranch": ICON_ORDER.index(tid), "icon": nxt}
        nxt += 1
    # seed boxes (the rancher's menu opens them)
    for rid, r in RANCHES.items():
        content["shops"]["SHOP_RANCH_" + rid] = {"name": r["name"] + " - Seed Box", "kinds": [], "town": "RANCH_" + rid,
                                                 "extra": [CROPS[c][1] for c in r["seeds"]]}
    # cooking recipes after every existing recipe
    g2 = content.get("gear2", {})
    recs = g2.setdefault("recipes", {})
    n = len(recs)
    for (res, cnt, tier, mats, gold) in RECIPES:
        n += 1
        rid = "RC%03d" % n
        while rid in recs:
            n += 1
            rid = "RC%03d" % n
        recs[rid] = {"kind": "make", "result": res, "count": cnt, "tier": tier, "mats": [[m, k] for m, k in mats],
                     "gold": gold, "id": rid}
        for iid in [res] + [m for m, _ in mats]:
            if iid not in items:
                err("ranch recipe %s: unknown item %s" % (rid, iid))
        if tier not in g2.get("tier_order", [tier]):
            err("ranch recipe %s: unknown tier %s" % (rid, tier))
    # runtime tables
    animals = {k: {"id": k, "name": v[0], "good": v[1], "every": v[2], "price": v[3], "note": v[4]} for k, v in ANIMALS.items()}
    crops = {}
    for k, v in CROPS.items():
        crops[k] = {"id": k, "item": v[0], "seed": v[1], "name": v[2], "strip": "crops/%s/%s" % (k, v[3]), "fw": v[4], "fh": v[5],
                    "stages": list(v[6]), "wither": v[7], "yield": v[8], "icon": "crops/%s/%s" % (k, v[11]), "icon_frame": v[12],
                    "sign": list(v[13])}
        if not v[6] or v[6][0] != 0 or sorted(v[6]) != list(v[6]):
            err("ranch crop %s: stages must start at frame 0 and rise" % k)
    ranches = {}
    for rid in RANCH_ORDER:
        r = RANCHES[rid]
        ranches[rid] = {"id": rid, "name": r["name"], "map": r["map"], "town": r["town"], "rancher": r["rancher"],
                        "look": r["look"], "region": r["region"], "seeds": list(r["seeds"]), "shop": "SHOP_RANCH_" + rid,
                        "cow": r["cow"], "pig": r["pig"], "hazard": r["hazard"], "foxes": r["foxes"], "animals": list(ANIMAL_ORDER)}
        for c in r["seeds"]:
            if c not in CROPS:
                err("ranch %s: unknown crop %s" % (rid, c))
        if r["cow"] not in COW_COLOURS or r["pig"] not in PIG_COLOURS or r["look"] not in FOLK:
            err("ranch %s: bad cow / pig colour or rancher look" % rid)
    content["ranch"] = {"animals": animals, "animal_order": ANIMAL_ORDER, "crops": crops, "ranches": ranches,
                        "order": RANCH_ORDER, "seed_crop": {v[1]: k for k, v in CROPS.items()}, "pack": PACK_ROOT,
                        "corn_strips": CORN_STRIPS, "folk": FOLK, "tools": sorted(TOOLS),
                        "rules": {"pig_grow_days": PIG_GROW_DAYS, "egg_hatch_days": EGG_HATCH_DAYS, "max_eggs": MAX_EGGS,
                                  "max_birds": MAX_BIRDS, "kart_bonus": KART_BONUS}}
    _check_maps(content, err)
    return content


def _check_maps(content, err):
    maps = content["maps"]
    for rid, r in RANCHES.items():
        m = maps.get(r["map"])
        if m is None:
            err("ranch %s: map %s missing" % (rid, r["map"]))
            continue
        npcs = {e["id"]: e for e in m["entities"] if e["type"] == "npc"}
        need = ["rancher_" + rid.lower(), "kart_" + rid, "nest_" + rid] + ["own_%s_%s" % (rid, a) for a in ANIMAL_ORDER if a != "bird"]
        need += ["own_%s_bird%d" % (rid, i) for i in range(1, MAX_BIRDS + 1)]
        for nid in need:
            if nid not in npcs:
                err("ranch %s: %s has no npc %s" % (rid, r["map"], nid))
        for nid, e in npcs.items():
            sp = e.get("sprite", "")
            if not sp.startswith("ranch:"):
                err("%s: npc %s should use a pack sprite (ranch:...), not %s" % (r["map"], nid, sp))
                continue
            parts = sp.split(":")
            if parts[1] in ("kart", "nest") and (len(parts) != 3 or parts[2] != rid):
                err("%s: npc %s bad sprite %s" % (r["map"], nid, sp))
            elif parts[1] == "folk" and (len(parts) < 4 or parts[2] not in FOLK or parts[3] not in FOLK_TASKS):
                err("%s: npc %s bad folk sprite %s" % (r["map"], nid, sp))
            elif parts[1] not in ("kart", "nest", "folk", "cow", "pig", "bird", "bunny", "cat", "fox", "mouse"):
                err("%s: npc %s unknown ranch sprite %s" % (r["map"], nid, sp))
        gates = [e for e in m["entities"] if e["type"] == "block" and e.get("tile") == "gate"]
        if not any(("!ranch:%s:gate" % rid) in e["cond"] for e in gates):
            err("ranch %s: %s has no pen gate block (if=!ranch:%s:gate)" % (rid, r["map"], rid))
        plots = sum(1 for row in m["grid"] for ch in row if m["legend"].get(ch) == "plot")
        if plots < MIN_PLOTS:
            err("ranch %s: %s has %d plot cells (needs %d)" % (rid, r["map"], plots, MIN_PLOTS))
        scn = content["scenes"].get(npcs.get("rancher_" + rid.lower(), {}).get("talk", ""), {})
        if scn and not any(c["c"] == "ranch" and c["a"][:2] == ["menu", rid] for c in scn["cmds"]):
            err("ranch %s: the rancher's scene never runs 'ranch menu %s'" % (rid, rid))
    # every `ranch` scene command is well formed
    ops = {"menu", "seeds", "buy", "lend", "plant", "kart", "animal", "nest"}
    for sid, s in content["scenes"].items():
        for c in s["cmds"]:
            if c["c"] == "ranch":
                if not c["a"] or c["a"][0] not in ops:
                    err("%s: ranch command needs one of %s" % (sid, sorted(ops)))
                elif c["a"][0] in ("menu", "seeds", "buy", "lend") and (len(c["a"]) < 2 or c["a"][1] not in RANCHES):
                    err("%s: ranch %s needs a ranch id" % (sid, c["a"][0]))
