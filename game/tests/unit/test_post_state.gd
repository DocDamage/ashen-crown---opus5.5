extends TestCase
## Post-catastrophe story integration (real director + field): the CH12 transition, order-independent reunions
## (AC050), once-only quest rewards (AC051/AC045), team locks (AC054) and the Wayfarer landing rule (AC014).
## Fixture set-up edits state directly; that is labelled test scaffolding, never route evidence.

func _skip(scene_id: String) -> String:
	var main = QA.main
	main.director.skipping = true
	main.dialogue.skip_all = true
	var r = await main.director.run(scene_id)
	main.director.skipping = false
	main.dialogue.skip_all = false
	return str(r)

func _all_recruited(level: int = 24) -> void:
	fresh_game()
	for cid in Game.CHAR_IDS:
		Game.recruit(cid)
		Game.member(cid)["level"] = level
	for ch in ["CH01", "CH02", "CH03", "CH04", "CH05", "CH06", "CH07", "CH08", "CH09", "CH10", "CH11"]:
		Game.complete_chapter(ch)

func _post_after_ch16() -> void:
	_all_recruited(28)
	Game.catastrophe_transaction()
	for ch in ["CH13", "CH14", "CH15", "CH16"]:
		Game.complete_chapter(ch)
	for cid in ["C05", "C02", "C04"]:
		Game.set_available(cid, true)
	Game.S["vehicle"]["ship"] = true

func test_catastrophe_scene_commits_post_state() -> void:
	_all_recruited()
	Game.add_item("W010", 1)
	QA.main.enter_field("D09_ESC", "start")
	var before_items = Game.count("W010")
	await _skip("CH12_FALL")
	eq(Game.S["world_phase"], "post", "phase is post after CH12_FALL")
	check(Game.S["chapters"].has("CH12"), "CH12 recorded")
	eq(QA.main.field.map_id, "T07_HEARTH", "arrive at Hearthward")
	check(Game.event_applied("CH13_WAKE"), "CH13 wake scene chained")
	eq(Game.available_members(), ["C01", "C06"], "only Dain and Oriel available")
	eq(Game.count("W010"), before_items, "inventory preserved")
	check(FileAccess.file_exists(Game.backup_path("pre_catastrophe")), "pre-transition backup written")
	var r = await QA.main.director.run("CH12_FALL")
	eq(str(r), "already", "transition cannot be applied twice")

func test_reunion_orders_all_six() -> void:
	var perms = [[17, 18, 19], [17, 19, 18], [18, 17, 19], [18, 19, 17], [19, 17, 18], [19, 18, 17]]
	var finals = {17: "CH17_CORREN", 18: "CH18_LEDGERS", 19: "CH19_SC10"}
	for p in perms:
		_post_after_ch16()
		QA.main.enter_field("T07_MARKET", "default")
		for flag in ["d06p_a1", "d06p_a2", "d06p_a3", "t02r_clear", "d07p_open1", "d07p_open2", "d07p_open3"]:
			Game.set_flag(flag, true)
		var n = 0
		for ch in p:
			n += 1
			await _skip(finals[ch])
			check(Game.S["chapters"].has("CH%d" % ch), "CH%d completes in order %s" % [ch, str(p)])
			var obj: String = Game.S["journal"]["objective"]
			if n < 3:
				check(obj.find("together again") < 0, "not reunited after %d in %s" % [n, str(p)])
		eq(Game.available_members().filter(func(c): return c <= "C08").size(), 8, "all eight originals available in order %s" % str(p))
		check(Game.is_available("C09") and Game.is_available("C10"), "Kitsune and Archangel back in order %s" % str(p))
		check(String(Game.S["journal"]["objective"]).find("together again") >= 0, "accord objective after %s" % str(p))

func test_personal_quest_reward_once() -> void:
	_post_after_ch16()
	Game.complete_chapter("CH20")
	QA.main.enter_field("T01_POST", "world")
	Game.quest_set("Q01", "RESOLUTION_READY")
	var w0 = Game.count("W006")
	await _skip("Q01_DECISION")
	eq(Game.quest_state("Q01"), "COMPLETED", "Q01 completed")
	eq(Game.count("W006"), w0 + 1, "Open Hand awarded")
	check(Game.learned_abilities("C01").has(Content.ch("C01")["ultimate"]), "final technique unlocked")
	await _skip("Q01_DECISION")
	eq(Game.count("W006"), w0 + 1, "reward not duplicated on re-trigger")
	Game.quest_set("Q01", "ACTIVE")
	eq(Game.quest_state("Q01"), "COMPLETED", "quest state never regresses")

func test_team_locks_alternate_without_trapping() -> void:
	_all_recruited(36)
	Game.catastrophe_transaction()
	for cid in Game.CHAR_IDS:
		Game.set_available(cid, true)
	Game.S["teams"] = {"A": ["C01", "C02", "C03", "C04"], "B": ["C05", "C06", "C07", "C08"]}
	QA.main.enter_field("D10_R03", "from_r01")
	await _skip("D10_E1")
	check(not Game.flag("d10_e1"), "east lock 1 waits for the west lock")
	QA.main.enter_field("D10_R02", "from_r01")
	await _skip("D10_W1")
	await _skip("D10_W2")
	check(not Game.flag("d10_w2"), "west lock 2 waits for east lock 1")
	QA.main.enter_field("D10_R03", "from_r01")
	await _skip("D10_E1")
	check(Game.flag("d10_e1"), "east lock 1 opens after west lock 1")
	QA.main.enter_field("D10_R02", "from_r01")
	await _skip("D10_W2")
	QA.main.enter_field("D10_R03", "from_r01")
	await _skip("D10_E2")
	check(Game.flag("d10_done_lungs"), "both lungs open")
	eq(QA.main.field.map_id, "D10_R04", "teams reunite on the Concord Bridge")
	check(not Game.S["party"]["locked"], "formation unlocked after reunion")
	# swap bells: every lung exit/bell is always usable, so neither team can be shut in
	for mid in ["D10_R02", "D10_R03"]:
		var bells = Content.map(mid)["entities"].filter(func(e): return e["type"] == "switch" and e["id"] == "swapbell" and e["cond"].is_empty())
		eq(bells.size(), 1, mid + " has an unconditional swap bell")

func test_landing_needs_marked_field() -> void:
	_post_after_ch16()
	var f = QA.main.field
	Game.S["vehicle"]["ship_map"] = "WORLD_POST"
	Game.S["vehicle"]["ship_x"] = 30
	Game.S["vehicle"]["ship_y"] = 40
	QA.main.enter_field("WORLD_POST", "helm")
	eq(f.vehicle, "ship", "boarded at the helm")
	check(not f.ship_op("land"), "landing refused away from a marked field")
	eq(f.vehicle, "ship", "ship still flying after refusal")
	f.place_player(25, 57, "down")
	check(f.ship_op("land"), "landing allowed at Brackenford field")
	eq(f.vehicle, "foot", "on foot after landing")
	check(not f.solid_at(f.p_tile.x, f.p_tile.y), "landed on walkable ground")
	eq(Vector2i(int(Game.S["vehicle"]["ship_x"]), int(Game.S["vehicle"]["ship_y"])), Vector2i(25, 57), "ship parked where it landed")

func test_every_shop_lists_stock_at_every_stage() -> void:
	var gm = GameMenu.new()
	for stage in [[], ["CH01", "CH04", "CH08"], ["CH01", "CH04", "CH06", "CH08", "CH16", "CH20"]]:
		fresh_game()
		for cid in Game.CHAR_IDS:
			Game.recruit(cid)
		for ch in stage:
			Game.complete_chapter(ch)
		for sid in Content.data["shops"]:
			var stock: Array = gm.shop_stock(sid)
			check(stock.size() > 0, "%s has stock at stage %s" % [sid, str(stage)])
			for iid in stock:
				check(not Content.item(iid).is_empty(), "%s stocks a real item %s" % [sid, iid])
	gm.free()
