extends TestCase
## Systems s2: region tier gear, named items and set bonuses, teaching gear, crafting, gathering, bestiary
## completion and scans, hunting parts, economy (tools/content/gear2.py, crafting.py).

func _g2() -> Dictionary:
	return Content.data["gear2"]

func test_region_tiers_complete() -> void:
	var t: Dictionary = _g2()["tiers"]
	eq(t.size(), 14, "one tier per region / realm (9 surface + sky + 3 deep + World of Ruin)")
	for tid in t:
		var ws = 0
		var owners = {}
		for iid in t[tid]["items"]:
			var it = Content.item(iid)
			check(not it.is_empty(), "%s exists" % iid)
			check(int(it.get("icon", -1)) >= 0, "%s has an icon cell" % iid)
			if it.get("kind", "") == "weapon":
				ws += 1
				owners[it["owner"]] = true
		eq(ws, 8, "tier %s has a weapon per class" % tid)
		eq(owners.size(), 8, "tier %s covers all 8 weapon classes" % tid)
		eq(t[tid]["items"].size(), 15, "tier %s: 8 weapons + 5 armour + 2 accessories" % tid)
	for sid in _g2()["shop_tiers"]:
		check(Content.data["shops"].has(sid), "tier shop %s exists" % sid)
	# stats rise with the tier order
	var prev = 0
	for tid in _g2()["tier_order"]:
		var w = Content.item(t[tid]["items"][0])
		check(int(w["atk"]) >= prev, "tier %s sword not weaker than the one before" % tid)
		prev = int(w["atk"])

func test_new_heroes_use_tier_gear() -> void:
	var w = Content.item(_g2()["tiers"]["R07"]["items"][6])   # C07 class weapon
	check(w["allowed"].has("C09"), "Kitsune (C07 class) can wield the Vermilion rune weapon")

func test_tier_shop_stock_gated_by_chapter() -> void:
	fresh_game()
	var r02: Array = _g2()["tiers"]["R02"]["items"]
	var before = Game.tier_stock("SHOP_N06")
	check(not before.has(r02[0]), "Kettle Row does not stock Slagiron before CH03 is done")
	Game.complete_chapter("CH03")
	var after = Game.tier_stock("SHOP_N06")
	check(after.has(r02[0]), "Slagiron sword stocked for Raven after CH03")
	check(not after.has(r02[1]), "no rod while Morwen is not recruited")
	check(after.has(r02[8]), "Slagiron armour stocked")
	check(not after.has(r02[13]), "Guild Smithy sells no accessories")
	check(not Game.tier_stock("SHOP_N09").has(r02[0]), "Wend's Agent sells no weapons")
	# full shop list includes the tier and still works
	var gm = GameMenu.new()
	var st = gm.shop_stock("SHOP_N06")
	check(st.has(r02[0]), "shop_stock includes the region tier")
	gm.free()
	# a region with no weapon shop gets one through the extra kinds
	Game.complete_chapter("CH06")
	check(Game.tier_stock("SHOP_N14").has(_g2()["tiers"]["R06"]["items"][0]), "Saltwhistle sells the Reefcoral blade")

func test_named_items_and_sets() -> void:
	var named = 0
	for iid in Content.data["items"]:
		if Content.item(iid).get("named", false):
			named += 1
	check(named >= 40, "40+ named items (%d)" % named)
	for sid in _g2()["sets"]:
		var s: Dictionary = _g2()["sets"][sid]
		check(s["pieces"].size() >= 2 and s["pieces"].size() <= 4, "set %s has 2-4 pieces" % sid)
		# someone can wear the whole set at once
		var who: Array = Game.CHAR_IDS.duplicate()
		var slots = {}
		var accs = 0
		for p in s["pieces"]:
			var it = Content.item(p)
			who = who.filter(func(c): return it["allowed"].has(c))
			var sl = it.get("slot", "weapon") if it["kind"] != "weapon" else "weapon"
			if sl == "accessory":
				accs += 1
			else:
				check(not slots.has(sl), "set %s: one piece per slot (%s)" % [sid, sl])
				slots[sl] = true
		check(accs <= 2, "set %s: at most two accessories" % sid)
		check(not who.is_empty(), "set %s wearable together by one hero" % sid)

func test_set_bonus_applies_when_worn_together() -> void:
	party(["C01"], 20)
	var s0 = Game.stats("C01")
	for iid in ["WN01", "GN01", "GN02"]:
		Game.add_item(iid, 1)
	eq(Game.equip("C01", "weapon", "WN01")["ok"], true, "equip Hallam's Tidebrand")
	var s1 = Game.stats("C01")
	eq(s1.get("sets", []).size(), 0, "one piece: no set bonus")
	check(not s1["passives"].get("elem_resist", {}).has("water"), "no water resist from one piece")
	eq(Game.equip("C01", "head", "GN01")["ok"], true, "equip the helm")
	var s_pre = F.member_stats(Game.member("C01"), Content.ch("C01"), Content.data["items"], Game.S["upgrades"], float(Content.data["gear"]["step"]))
	var s2 = Game.stats("C01")
	eq(s2["sets"].size(), 1, "two pieces: Drowned Oath active")
	eq(s2["def"], s_pre["def"] + 4, "2-piece bonus: DEF +4")
	check(s2["passives"]["elem_resist"].has("water"), "2-piece bonus: resists water")
	check(not s2["passives"].has("lowhp_guard"), "3-piece bonus not yet")
	eq(Game.equip("C01", "offhand", "GN02")["ok"], true, "equip the kite shield")
	var s3 = Game.stats("C01")
	eq(s3["sets"][0][1], 3, "three pieces counted")
	eq(float(s3["passives"].get("lowhp_guard", 0)), 0.3, "3-piece bonus: low-HP guard")
	check(s3["atk"] > s2["atk"], "3-piece bonus: attack up")
	check(not Content.item("GN01").get("passives", {}).has("elem_resist"), "item data untouched by the set merge")
	# taking one piece off drops the 3-piece bonus
	Game.equip("C01", "offhand", "")
	check(not Game.stats("C01")["passives"].has("lowhp_guard"), "bonus goes with the piece")
	check(s0["def"] < s2["def"], "sanity")

func test_resistances_from_two_pieces_add_up() -> void:
	party(["C01"], 20)
	var fire = _g2()["tiers"]["R02"]["items"][13]      # Slag Ward (fire)
	var water = _g2()["tiers"]["R03"]["items"][13]     # Wrack Pearl (water)
	Game.add_item(fire, 1)
	Game.add_item(water, 1)
	Game.equip("C01", "acc1", fire)
	Game.equip("C01", "acc2", water)
	var er: Dictionary = Game.stats("C01")["passives"].get("elem_resist", {})
	check(er.has("fire") and er.has("water"), "fire and water resist both apply (%s)" % [er])
	check(not Content.item(fire)["passives"]["elem_resist"].has("water"), "accessory data untouched")

func test_teaching_gear_learns_for_good() -> void:
	party(["C01"], 12)
	Game.add_item("AN01", 1)     # Furnace Heart: teaches Kindle (S065) at 10 per AP
	eq(Game.equip("C01", "acc1", "AN01")["ok"], true, "equip Furnace Heart")
	check(not Game.learned_abilities("C01").has("S065"), "not known yet")
	for i in range(9):
		Game.gear_learning(1)
	eq(Game.gear_progress("C01", "S065"), 90, "90% after nine battles")
	var msgs = Game.gear_learning(1)
	check(Game.learned_abilities("C01").has("S065"), "learned at 100")
	check(msgs.size() == 1 and "Kindle" in msgs[0], "a message names the ability")
	Game.equip("C01", "acc1", "")
	check(Game.learned_abilities("C01").has("S065"), "kept after taking it off")
	check(Game.battle_party()[0]["abilities"].has("S065"), "usable in battle")
	# bosses give 3 AP
	Game.add_item("AN02", 1)
	Game.equip("C01", "acc1", "AN02")
	Game.gear_learning(3)
	eq(Game.gear_progress("C01", "S068"), 30, "boss AP x3")

func test_teaching_only_while_worn_and_conscious() -> void:
	party(["C01", "C02"], 12)
	Game.add_item("AN01", 1)
	Game.equip("C02", "acc1", "AN01")
	Game.member("C02")["hp"] = 0
	Game.gear_learning(1)
	eq(Game.gear_progress("C02", "S065"), 0, "knocked-out heroes learn nothing")
	eq(Game.gear_progress("C01", "S065"), 0, "others do not learn from it")

func test_crafting_make_and_reforge() -> void:
	fresh_game()
	var rs: Dictionary = _g2()["recipes"]
	check(rs.size() >= 60, "60+ recipes (%d)" % rs.size())
	var tiers = {}
	for rid in rs:
		tiers[rs[rid]["tier"]] = true
	check(tiers.size() >= 12, "recipes spread over the region tiers (%d)" % tiers.size())
	var lens = ""
	for rid in rs:
		if rs[rid]["result"] == "AC01":
			lens = rid
	check(lens != "", "Appraiser's Lens recipe exists")
	check(Game.craft_recipes("crafter_n01").has(lens), "Hollins Mill's crafter makes it")
	check(not Game.craft_recipes("crafter_n01").has(_first_recipe_of("U3")), "an R01 bench cannot make Hollow Throne work")
	check(Game.craft_recipes("crafter_u29").has(lens), "later benches know the early recipes")
	eq(Game.can_craft(lens)["ok"], false, "no materials: refused")
	Game.add_item("MT20", 3)
	Game.add_item("MT10", 2)
	var g0 = Game.gold()
	var r = Game.craft(lens)
	eq(r["ok"], true, "crafted with materials")
	eq(Game.count("AC01"), 1, "lens made")
	eq(Game.count("MT20"), 0, "scrap used")
	eq(Game.gold(), g0 - int(rs[lens]["gold"]), "crowns spent")
	# the lens grants Libra
	Game.equip("C01", "acc1", "AC01")
	check(Game.stats("C01")["grants"].has("SX_LIBRA"), "Appraiser's Lens grants Libra")
	# reforge: tier item + materials -> next tier item
	var rf = ""
	for rid in rs:
		if rs[rid]["kind"] == "reforge":
			rf = rid
			break
	var rec: Dictionary = rs[rf]
	for mt in rec["mats"]:
		Game.add_item(mt[0], int(mt[1]))
	Game.add_gold(int(rec["gold"]) + 10)
	eq(Game.can_craft(rf)["ok"], false, "reforge needs the input item")
	Game.add_item(rec["input"], 1)
	eq(Game.craft(rf)["ok"], true, "reforged")
	eq(Game.count(rec["input"]), 0, "input consumed")
	eq(Game.count(rec["result"]), 1, "result made")

func _first_recipe_of(tier: String) -> String:
	var rs: Dictionary = _g2()["recipes"]
	var ids = rs.keys()
	ids.sort()
	for rid in ids:
		if rs[rid]["tier"] == tier:
			return rid
	return ""

func test_every_crafter_has_a_bench() -> void:
	var n = 0
	for mid in Content.data["maps"]:
		for e in Content.data["maps"][mid]["entities"]:
			if e["type"] == "npc" and String(e["id"]).begins_with("crafter_"):
				n += 1
				check(_g2()["crafters"].has(e["id"]), "%s has a tier" % e["id"])
				check(Game.craft_recipes(e["id"]).size() >= 5, "%s offers recipes" % e["id"])
	check(n >= 20, "crafters found on the maps (%d)" % n)

func test_gathering_node_and_refresh() -> void:
	fresh_game()
	var node := {}
	var maps = 0
	for mid in Content.data["maps"]:
		var m = Content.data["maps"][mid]
		var here = 0
		for e in m["entities"]:
			if e["type"] == "node":
				here += 1
				var k: String = m["legend"][m["grid"][e["y"]][e["x"]]]
				check(not Content.data["tile_rules"]["solid"].has(k), "%s node on a floor cell" % e["id"])
				check(_g2()["gather"].has(e["table"]), "%s table exists" % e["id"])
				if node.is_empty():
					node = e
		if here > 0:
			maps += 1
			check(here >= 3 and here <= 6, "%s has 3-6 nodes" % mid)
	check(maps >= 3, "nodes in several places (%d)" % maps)
	var t: Dictionary = _g2()["gather"][node["table"]]
	var inv0 = Game.S["inventory"]["items"].duplicate()
	var r = Game.gather(node["id"], node["table"])
	eq(r["ok"], true, "first harvest works: %s" % r.get("text", ""))
	check(r["text"].begins_with(_g2()["gather_verb"][t["kind"]]), "message names the harvest")
	var got = 0
	for iid in r["got"]:
		got += int(r["got"][iid])
		check(Game.count(iid) > int(inv0.get(iid, 0)), "%s added" % iid)
	check(got >= 1, "something gathered")
	eq(Game.gather(node["id"], node["table"])["ok"], false, "spent right after")
	Game.S["steps"] = int(Game.S["steps"]) + int(t["steps"]) - 1
	check(not Game.node_ready(node["id"], node["table"]), "not yet refreshed")
	Game.S["steps"] = int(Game.S["steps"]) + 1
	check(Game.node_ready(node["id"], node["table"]), "refreshed after N steps")
	Game.gather(node["id"], node["table"])
	Game.S["battles"] = int(Game.S["battles"]) + int(t["battles"])
	check(Game.node_ready(node["id"], node["table"]), "refreshed after N battles")

func test_gatherers_satchel_adds_one() -> void:
	party(["C01"], 10)
	Game.add_item("AC02", 1)
	Game.equip("C01", "acc1", "AC02")
	var r = Game.gather("TEST@1,1", "mine_r02")
	var total = 0
	for iid in r["got"]:
		total += int(r["got"][iid])
	check(total >= 2, "satchel: at least 2 per draw (%d)" % total)

func test_hunting_parts_and_gold_curve() -> void:
	var e = Content.enemy("E041")
	var parts = e["drops"].filter(func(d): return Content.item(d["item"]).get("kind", "") == "material")
	check(parts.size() >= 1, "Mill Rat Swarm drops a part")
	var drake = Content.enemy("E094")
	check(drake["drops"].any(func(d): return d["item"] == "MT41"), "Bone Drakeling drops a Dragon Scale")
	var any_variant = false
	for eid in Content.data["enemies"]:
		var v = Content.enemy(eid)
		if v.get("variant_of", "") == "E081":
			any_variant = true
			check(v["drops"].any(func(d): return Content.item(d["item"]).get("kind", "") == "material"), "level variants keep their parts")
	check(any_variant, "E081 has level variants")
	eq(int(Content.enemy("E001")["gold"]), 10 + 6 * int(Content.enemy("E001")["level"]), "early gold unchanged")
	var hi = Content.enemy("E109")
	check(int(hi["gold"]) > 10 + 6 * int(hi["level"]), "late gold raised")
	check(Content.enemy("BX01")["drops"].any(func(d): return d["item"] == "WN01" and int(d["chance"]) == 100), "BX01 drops its named sword")
	check(Content.enemy("SB01")["drops"].any(func(d): return d["item"] == "AN16"), "Cindermaw drops its heartscale")

func test_inn_prices_by_region() -> void:
	fresh_game()
	eq(Game.inn_price_for("R01", 25), 25, "Crown March keeps the canon price")
	eq(Game.inn_price_for("U3", 25), 250, "Hollow Throne inn")
	check(Game.inn_price_for("R09", 150) >= 160, "Hoarfrost inn above the canon cap")

func test_bestiary_entries_and_where() -> void:
	var ids = Game.bestiary_entries()
	check(ids.size() >= 150, "every regular enemy, boss and superboss (%d)" % ids.size())
	check(not ids.any(func(i): return "@" in i), "no level variants")
	check(Content.enemy("E041").get("where", []).size() > 0, "Mill Rat Swarm has a location")
	check(Content.enemy("BX01").get("where", []).has("The Sunken Chapel"), "BX01 lives in the Sunken Chapel")
	check(str(Content.enemy("E041").get("lore", "")) != "", "lore present")

func test_bestiary_completion_rewards() -> void:
	fresh_game()
	var ids = Game.bestiary_entries()
	eq(Game.bestiary_rewards_pending().size(), 0, "nothing at 0%")
	var n = int(ceil(ids.size() * 0.25))
	for i in range(n):
		Game.bestiary_seen(ids[i], "seen")
	var pend = Game.bestiary_rewards_pending()
	eq(pend.size(), 1, "25% seen reached")
	eq(pend[0], ["seen", 25], "seen 25")
	var c0 = Game.count("I002")
	var msgs = Game.claim_bestiary_rewards()
	check(msgs.size() >= 1, "claim messages")
	eq(Game.count("I002"), c0 + 3, "reward items given")
	eq(Game.claim_bestiary_rewards().size(), 0, "each reward once")
	for eid in ids:
		Game.bestiary_seen(eid, "seen")
		Game.bestiary_seen(eid, "defeated")
	var pend2 = Game.bestiary_rewards_pending()
	eq(pend2.size(), 7, "all remaining milestones at 100% (3 seen + 4 defeated)")
	Game.claim_bestiary_rewards()
	eq(Game.count("AN23"), 1, "the Hunter's Codex at 100% seen")

func test_libra_scan_fills_entry_and_reports() -> void:
	var m = model_with(["C01"], ["E041"], 10)
	var b = m.battlers[m.party_ids[0]]
	var e = m.battlers[m.enemy_ids[0]]
	var ev = {"results": [], "msgs": []}
	m._apply_op(b, e, {"op": "reveal", "what": "scan"}, {"ev": ev, "depth": 0, "reactions": {}, "act": {"targets": [e.id]}})
	check(ev["msgs"].any(func(s): return String(s).begins_with("Weak:")), "Libra reports weaknesses: %s" % [ev["msgs"]])
	check(ev.get("reveal", []).any(func(r): return r["what"] == "scan"), "reveal pushed for the scene")
	Game.bestiary_seen("E041", "scan")
	var be: Dictionary = Game.S["bestiary"]["E041"]
	check(be["affinity"] and be["drops"] and be["scanned"], "scan fills the entry")
	check(Content.ability("SX_LIBRA").get("name", "") == "Libra", "Libra ability exists")

func test_enemies_scan_the_party() -> void:
	var d = Content.enemy("E105")
	eq(d["cycle"][0], "scan", "Datum Ghost opens with a scan")
	var m = model_with(["C01"], ["E105"], 30)
	var b = m.battlers[m.party_ids[0]]
	var e = m.battlers[m.enemy_ids[0]]
	var ev = {"results": [], "msgs": []}
	m._apply_op(e, b, {"op": "scan_foe"}, {"ev": ev, "depth": 0, "reactions": {}, "act": {"targets": [b.id]}})
	check(ev["msgs"].size() == 1 and "scans" in ev["msgs"][0], "battle message: %s" % [ev["msgs"]])

func test_named_chests_on_maps() -> void:
	var found = 0
	for mid in Content.data["maps"]:
		for e in Content.data["maps"][mid]["entities"]:
			if e["type"] == "chest" and Content.item(e["item"]).get("named", false):
				found += 1
	check(found >= 30, "named items placed in the new dungeons' chests (%d)" % found)
