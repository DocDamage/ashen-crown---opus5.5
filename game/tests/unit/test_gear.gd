extends TestCase
## Expansion Phase 2: regional gear lines, their passives, smith upgrades and specialist shop stock.

func test_regional_lines_complete() -> void:
	var items: Dictionary = Content.data["items"]
	var per_line = {}
	for iid in items:
		var it: Dictionary = items[iid]
		if it.has("line"):
			per_line[it["line"]] = per_line.get(it["line"], 0) + 1
			check(it.has("icon"), "%s has an icon cell" % iid)
			check(str(it.get("desc", "")) != "", "%s explains its passive" % iid)
	eq(per_line.size(), 6, "six regional lines")
	for l in per_line:
		eq(per_line[l], 15, "line %s has 8 weapons + 4 armour + 3 accessories" % l)

func test_every_item_has_icon_cell() -> void:
	var seen = {}
	for iid in Content.data["items"]:
		var c = int(Content.item(iid).get("icon", -1))
		check(c >= 0, "%s icon index" % iid)
		check(not seen.has(c), "icon cell %d is unique" % c)
		seen[c] = true

func test_weapon_element_and_mag_bonus() -> void:
	party(["C01", "C02"], 10)
	var base = Game.stats("C01")
	Game.add_item("W109", 1)            # Forgebrand (fire)
	eq(Game.equip("C01", "weapon", "W109")["ok"], true, "equip Forgebrand")
	eq(Game.stats("C01")["weapon_element"], "fire", "fire weapon element reaches stats")
	var m2 = Game.stats("C02")["matk"]
	Game.add_item("W134", 1)            # Salt Prism Rod (boneglass: +12% magic)
	eq(Game.equip("C02", "weapon", "W134")["ok"], true, "equip Salt Prism Rod")
	check(Game.stats("C02")["matk"] > m2, "boneglass rod raises magic")
	check(base["weapon_element"] == "physical", "starter weapon is physical")

func test_upgrade_costs_ore_and_raises_stats() -> void:
	party(["C01"], 10)
	var w: String = Game.member("C01")["equip"]["weapon"]
	var a0 = Game.stats("C01")["atk"]
	var r = Game.upgrade(w)
	eq(r["ok"], false, "no ore: refused")
	Game.add_item("M001", 2)
	Game.add_gold(1000)
	var g0 = Game.gold()
	r = Game.upgrade(w)
	eq(r["ok"], true, "upgrade with ore")
	eq(Game.upgrade_level(w), 1, "level +1")
	eq(Game.count("M001"), 0, "ore consumed")
	check(Game.gold() < g0, "crowns spent")
	check(Game.stats("C01")["atk"] >= a0, "attack not lower after upgrade")
	check(Content.item_name(w).ends_with("+1"), "name shows +1")

func test_reserve_scale_counts_reserves() -> void:
	party(["C01", "C02", "C03", "C05"], 20)
	Game.set_active(["C01", "C02"])
	Game.add_item("W141", 1)            # Salvaged Blade
	Game.equip("C01", "weapon", "W141")
	var with2 = Game.stats("C01")["atk"]
	Game.set_active(["C01", "C02", "C03", "C05"])
	var with0 = Game.stats("C01")["atk"]
	check(with2 > with0, "reserve members raise a Salvage weapon's attack")

func test_auto_revive_once() -> void:
	var m = model_with(["C02"], ["E001"], 10)
	var b = m.battlers[m.party_ids[0]]
	var e = m.battlers[m.enemy_ids[0]]
	b.passives = {"auto_revive": true}
	b.hp = 3
	var op = {"op": "damage", "power": 400, "type": "magical", "element": "none", "item": true, "fixed_mag": 300}
	var ev1 = {"results": [], "msgs": []}
	m._do_damage(e, b, op, {"ev": ev1, "depth": 0, "reactions": {}, "act": {"targets": [b.id]}})
	eq(b.hp, 1, "first fatal blow leaves 1 HP %s" % [ev1])
	check(b.alive(), "still standing")
	b.hp = 3
	m._do_damage(e, b, op, {"ev": {"results": [], "msgs": []}, "depth": 0, "reactions": {}, "act": {"targets": [b.id]}})
	eq(b.hp, 0, "second fatal blow knocks out")

func test_specialist_stock() -> void:
	fresh_game()
	var gm = GameMenu.new()
	check(not gm.shop_stock("SHOP_T02").has("A101"), "Oathguard line not stocked before CH01")
	Game.complete_chapter("CH01")
	check(gm.shop_stock("SHOP_T02").has("A101"), "Oathguard accessory at Veyr after CH01")
	check(not gm.shop_stock("SHOP_T01").has("A101"), "not in Brackenford")
	check(gm.shop_stock("SHOP_T01").has("M001"), "Brackenford smith sells Iron Ore")
	check(not gm.shop_stock("SHOP_T02").has("M001"), "Veyr has no smith")
	gm.free()
