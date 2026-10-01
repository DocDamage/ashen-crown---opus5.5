"""Ranching (one ranch per major kingdom): livestock, crop plots, ranch goods, seed boxes and cooking recipes.

Runtime: game/src/meta/ranch.gd (class Ranch), state in Game.S["ranch"]; scene command `ranch <op>`
(content_src/scenes/ranch.scn); maps content_src/maps/ranch.map; art installed by tools/art/install_ranch.py.

Rules (time = Game.S.day * 1440 + Game.S.clock, in-game minutes; one in-game day = 1440 min, about 20 real minutes,
and a night at an inn moves the clock on):
  livestock  each ranch sells some ANIMALS, once per kind per ranch. An owned animal makes one unit of its good every
             `period` minutes, up to `cap` units waiting; the ranch's produce crate hands over everything waiting.
             Collecting at the cap restarts the count from now (a full crate is wasted time).
  plots      each ranch has `plots` crop plots. Seeds come from the rancher's seed box (a shop of the ranch's seeds).
             Planting uses one seed; the crop is ripe after `days` in-game days and harvests `yield` units.
  goods      raw goods (milk, eggs, wool, truffles) and crops are consumables or crafting materials; cooked dishes
             (RECIPES) are made at any crafter whose tier reaches the recipe's tier. Everything sells.
Map hooks (validated here): on a ranch map the rancher is npc `rancher_<rid lower>` (its scene ends with
`ranch menu <RID>`), the crate is npc `crate_<RID>` sprite=ranch:crate:<RID>, plots are npcs `plot_<RID>_<n>`
sprite=ranch:plot:<RID>:<n> on garden cells, owned animals are npcs `own_<RID>_<animal>` if=ranch:<RID>:own:<animal>.
Animal sprites are `ranch:<sprite key>` (ANIMAL_SPRITES; drawn by Ranch.draw_field, with a drawn fallback).
"""

# animal kind: (name, good item, period minutes, cap, price, default sprite, note)
ANIMALS = {
    "cow": ("Milk Cow", "RK01", 1440, 3, 900, "cow", "A day's milk, every day. She does not care who owns her."),
    "dove": ("Dovecote", "RK02", 1440, 4, 350, "dove", "Pale doves. They lay, and they come home, which is more than most."),
    "pig": ("Rooting Pig", "RK04", 2880, 2, 1400, "pig", "Turns up a truffle every second day, and ruins the ground doing it."),
    "bunny": ("Angora Coneys", "RK03", 2880, 2, 700, "bunny", "Combed every other day for a fistful of wool."),
}
# sprite keys installed under assets/ext/ranch/<key>/field.png (HeroArt field format)
ANIMAL_SPRITES = ["cow", "cow_black", "pig", "pig_black", "dove", "bunny", "cat", "fox", "mouse"]

# crop id: (crop item, seed item, crop name, days, yield, seed price, crop price, colour for the drawn fallback)
CROPS = {
    "wheat": ("RV01", "RS01", "Wheat", 1, 3, 20, 24, (214, 178, 84)),
    "carrot": ("RV02", "RS02", "Carrot", 1, 3, 20, 30, (232, 120, 40)),
    "potato": ("RV03", "RS03", "Potato", 2, 4, 30, 30, (150, 110, 70)),
    "pumpkin": ("RV04", "RS04", "Pumpkin", 3, 2, 60, 110, (236, 128, 30)),
    "onion": ("RV05", "RS05", "Onion", 1, 3, 20, 26, (220, 170, 110)),
    "beetroot": ("RV06", "RS06", "Beetroot", 2, 3, 30, 40, (150, 30, 70)),
    "leek": ("RV07", "RS07", "Leek", 2, 3, 30, 36, (120, 190, 90)),
    "radish": ("RV08", "RS08", "Radish", 1, 3, 25, 34, (230, 110, 150)),
    "tomato": ("RV09", "RS09", "Tomato", 2, 4, 40, 40, (220, 50, 40)),
    "cauliflower": ("RV10", "RS10", "Cauliflower", 2, 2, 45, 70, (236, 232, 210)),
    "berry": ("RV11", "RS11", "Fen Berry", 2, 4, 40, 45, (200, 40, 60)),
    "pepper": ("RV12", "RS12", "Ember Pepper", 3, 3, 60, 80, (230, 60, 20)),
    "eggplant": ("RV13", "RS13", "Eggplant", 2, 3, 40, 50, (110, 50, 130)),
    "grape": ("RV14", "RS14", "Court Grapes", 3, 3, 70, 90, (70, 80, 190)),
    "bamboo": ("RV15", "RS15", "Bamboo Shoot", 3, 3, 50, 70, (150, 200, 90)),
    "corn": ("RV16", "RS16", "Corn", 2, 3, 35, 45, (240, 200, 60)),
}

# rid: name, map, town map(s) it hangs off, rancher npc name, plots, animals for sale (kind, sprite), seeds
RANCHES = {
    "R01": dict(name="Fallowmere Ranch", map="T01_RANCH", town="Brackenford", rancher="Agna Fallow", plots=3,
                animals=[("cow", "cow"), ("dove", "dove"), ("pig", "pig")], seeds=["wheat", "carrot", "potato"]),
    "R02": dict(name="Soot Paddock", map="T03_RANCH", town="Cinderwake", rancher="Brann Coker", plots=3,
                animals=[("pig", "pig_black"), ("dove", "dove"), ("bunny", "bunny")], seeds=["onion", "beetroot", "pepper"]),
    "R03": dict(name="Gullbank Croft", map="T04_RANCH", town="Bellharbor", rancher="Maude Tiller", plots=3,
                animals=[("cow", "cow"), ("dove", "dove"), ("bunny", "bunny")], seeds=["radish", "tomato", "cauliflower"]),
    "R04": dict(name="Windbreak Fold", map="T05_RANCH", town="High Aerie", rancher="Sefton Crag", plots=3,
                animals=[("bunny", "bunny"), ("dove", "dove"), ("cow", "cow_black")], seeds=["leek", "corn", "pumpkin"]),
    "R05": dict(name="Brinewell Steading", map="T06_RANCH", town="Nacre", rancher="Yara Saltmarrow", plots=3,
                animals=[("pig", "pig"), ("dove", "dove"), ("cow", "cow")], seeds=["eggplant", "onion", "wheat"]),
    "R07": dict(name="Maple Gate Farm", map="N28_RANCH", town="Akagane", rancher="Okuni Hara", plots=3,
                animals=[("bunny", "bunny"), ("dove", "dove"), ("pig", "pig")], seeds=["bamboo", "grape", "radish"]),
    "R08": dict(name="Lazar Fields", map="N22_RANCH", town="Harrowfen", rancher="Gideon Marl", plots=3,
                animals=[("pig", "pig_black"), ("dove", "dove"), ("bunny", "bunny")], seeds=["berry", "leek", "beetroot"]),
    "R09": dict(name="Rimefold", map="N32_RANCH", town="Rimeholt", rancher="Hild Ulfsdottir", plots=3,
                animals=[("cow", "cow_black"), ("bunny", "bunny"), ("pig", "pig_black")], seeds=["potato", "carrot", "berry"]),
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
}
CROP_DESC = {
    "wheat": "A sheaf of wheat. Millers and bakers pay for it.", "potato": "Fist-sized and dirty. Better in a stew.",
    "pumpkin": "Heavy as a child. Bakers want it for loaves.", "onion": "It makes the cook weep, and the stew worth eating.",
    "leek": "Long and pale. Broth needs it.", "cauliflower": "A tight white head. The salt cooks pickle it.",
    "eggplant": "Purple and glossy. Basin cooks roast it on stones.", "bamboo": "A tender shoot. The fox court eats it in spring.",
    "corn": "A full ear. Fodder, flour or supper.",
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
]

# icon sheet cells (assets/ext/ranch/icons.png, 16x16, 8 per row), written by tools/art/install_ranch.py
ICON_ORDER = (["RK01", "RK02", "RK03", "RK04"] + ["RV%02d" % i for i in range(1, 17)] + ["RS%02d" % i for i in range(1, 17)]
              + ["RF01", "RF02", "RF03", "RF04", "RF05", "RF06", "RA01"])


def _items():
    out = {}
    for iid, (name, price, desc, spec) in GOODS.items():
        out[iid] = (name, price, desc, spec, "good")
    for cid, (crop, seed, name, days, yld, sp, cp, col) in CROPS.items():
        eff = CROP_EFFECT.get(cid)
        out[crop] = (name, cp, eff[0] if eff else CROP_DESC[cid], eff[1] if eff else None, "crop")
        out[seed] = (name + " Seed", sp, "Seed for a ranch plot. Ripe in %d day%s; yields %d." % (days, "" if days == 1 else "s", yld), None, "seed")
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
    animals = {k: {"id": k, "name": v[0], "good": v[1], "period": v[2], "cap": v[3], "price": v[4], "sprite": v[5], "note": v[6]}
               for k, v in ANIMALS.items()}
    crops = {k: {"id": k, "item": v[0], "seed": v[1], "name": v[2], "days": v[3], "yield": v[4], "color": list(v[7]),
                 "sprite_index": list(CROPS).index(k)} for k, v in CROPS.items()}
    ranches = {}
    for rid in RANCH_ORDER:
        r = RANCHES[rid]
        ranches[rid] = {"id": rid, "name": r["name"], "map": r["map"], "town": r["town"], "rancher": r["rancher"],
                        "plots": r["plots"], "animals": [a for a, _ in r["animals"]],
                        "sprites": {a: s for a, s in r["animals"]}, "seeds": list(r["seeds"]), "shop": "SHOP_RANCH_" + rid}
        for a, s in r["animals"]:
            if a not in ANIMALS or s not in ANIMAL_SPRITES:
                err("ranch %s: bad animal %s/%s" % (rid, a, s))
        for c in r["seeds"]:
            if c not in CROPS:
                err("ranch %s: unknown crop %s" % (rid, c))
    content["ranch"] = {"animals": animals, "crops": crops, "ranches": ranches, "order": RANCH_ORDER,
                        "sprites": ANIMAL_SPRITES, "seed_crop": {v[1]: k for k, v in CROPS.items()}}
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
        need = ["rancher_" + rid.lower(), "crate_" + rid] + ["plot_%s_%d" % (rid, i) for i in range(1, r["plots"] + 1)]
        need += ["own_%s_%s" % (rid, a) for a, _ in r["animals"]]
        for nid in need:
            if nid not in npcs:
                err("ranch %s: %s has no npc %s" % (rid, r["map"], nid))
        for nid, e in npcs.items():
            sp = e.get("sprite", "")
            if not sp.startswith("ranch:"):
                continue
            parts = sp.split(":")
            if parts[1] == "plot":
                if len(parts) != 4 or parts[2] != rid or not (1 <= int(parts[3]) <= r["plots"]):
                    err("%s: npc %s bad plot sprite %s" % (r["map"], nid, sp))
                elif m["legend"].get(m["grid"][e["y"]][e["x"]]) != "garden":
                    err("%s: plot %s is not on a garden cell" % (r["map"], nid))
            elif parts[1] == "crate":
                if len(parts) != 3 or parts[2] != rid:
                    err("%s: npc %s bad crate sprite %s" % (r["map"], nid, sp))
            elif parts[1] not in ANIMAL_SPRITES:
                err("%s: npc %s unknown animal sprite %s" % (r["map"], nid, sp))
        scn = content["scenes"].get(npcs.get("rancher_" + rid.lower(), {}).get("talk", ""), {})
        if scn and not any(c["c"] == "ranch" and c["a"][:2] == ["menu", rid] for c in scn["cmds"]):
            err("ranch %s: the rancher's scene never runs 'ranch menu %s'" % (rid, rid))
    # every `ranch` scene command is well formed
    ops = {"menu", "crate", "plot", "animal", "seeds", "buy"}
    for sid, s in content["scenes"].items():
        for c in s["cmds"]:
            if c["c"] == "ranch":
                if not c["a"] or c["a"][0] not in ops:
                    err("%s: ranch command needs one of %s" % (sid, sorted(ops)))
                elif c["a"][0] in ("menu", "seeds", "buy") and (len(c["a"]) < 2 or c["a"][1] not in RANCHES):
                    err("%s: ranch %s needs a ranch id" % (sid, c["a"][0]))
