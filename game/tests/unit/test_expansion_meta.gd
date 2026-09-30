extends TestCase
## sys s4: saves (12 slots, autosave, quicksave, old saves), achievements, New Game+, Mature markup, fishing, strings.
## Saves go to user://test_meta_saves and achievements to user://test_meta_profile.json, never the player's files.

const TDIR := "user://test_meta_saves"

func _saves_sandbox() -> void:
	Game.save_root = TDIR
	DirAccess.make_dir_recursive_absolute(TDIR)
	var da = DirAccess.open(TDIR)
	if da:
		for f in da.get_files():
			DirAccess.remove_absolute(TDIR + "/" + f)

func _saves_done() -> void:
	Game._autosave_reason = ""
	Game.save_root = Game.SAVE_DIR
	Game.fixture_label = "unit-fixture"

func _profile_sandbox() -> void:
	Achievements.reset_profile("user://test_meta_profile.json")
	Achievements.quiet = true

func _profile_done() -> void:
	Achievements.reset_profile("user://test_meta_profile.json")
	Achievements.path = "user://profile.json"
	Achievements._loaded = false
	Achievements.quiet = false

# ---------------------------------------------------------------- saves
func test_twelve_slots_with_detail() -> void:
	_saves_sandbox()
	fresh_game()
	Game.recruit("C02")
	check(Game.SLOTS >= 12, "at least 12 manual slots")
	check(Game.save_slot(12)["ok"], "slot 12 saves")
	var info = Game.slot_info(12)
	check(info.get("ok", false), "slot 12 readable")
	check(str(info.get("chapter", "")) != "", "detail: chapter")
	check(str(info.get("location", "")) != "", "detail: location")
	eq(info.get("party", []).size(), 2, "detail: party of two")
	eq(str(info["party"][1]["cid"]), "C02", "detail: party ids")
	check(info.has("playtime"), "detail: playtime")
	eq(Game.slot_info(11).get("reason", ""), "missing", "empty slot reported as missing")
	_saves_done()

func test_autosave_and_quicksave() -> void:
	_saves_sandbox()
	fresh_game()
	Game.fixture_label = ""
	var keep = Settings.v["autosave"]
	Settings.v["autosave"] = true
	Game.request_autosave("boss")
	check(Game.autosave_pending(), "autosave requested")
	check(Game.flush_autosave()["ok"], "autosave written")
	check(not Game.autosave_pending(), "request cleared")
	var ai = Game.path_info(Game.auto_path())
	check(ai.get("ok", false), "autosave readable")
	eq(ai.get("reason", ""), "boss", "autosave remembers why")
	eq(str(Game.S.get("save_id", "")), "", "autosave does not claim the run's slot")
	Settings.v["autosave"] = false
	Game.request_autosave("map")
	check(not Game.autosave_pending(), "autosave off: no request")
	Settings.v["autosave"] = keep
	Game.add_gold(77)
	check(Game.save_quick()["ok"], "quicksave written")
	check(Game.save_quick()["ok"], "quicksave overwrites its one slot")
	var qi = Game.path_info(Game.quick_path())
	eq(int(qi.get("gold", 0)), Game.gold(), "quicksave holds the latest state")
	var latest = Game.latest_save()
	check(not latest.is_empty(), "latest save found")
	check(Game.load_from(Game.quick_path())["ok"], "quicksave loads")
	_saves_done()

func test_unit_fixtures_never_autosave() -> void:
	_saves_sandbox()
	fresh_game()
	Game.request_autosave("map")
	check(not Game.autosave_pending(), "labelled unit fixtures skip autosave")
	_saves_done()

func test_arrival_autosave_from_world() -> void:
	_saves_sandbox()
	fresh_game()
	Game.fixture_label = ""
	var keep = Settings.v["autosave"]
	Settings.v["autosave"] = true
	QA.main.enter_field("N14_R01", "world")
	QA.main._arrival_autosave("world")
	check(Game.autosave_pending(), "arriving at a town from the world map requests an autosave")
	QA.main.flush_autosave()
	check(FileAccess.file_exists(Game.auto_path()), "autosave file written on arrival")
	QA.main._arrival_autosave("room")
	check(not Game.autosave_pending(), "room to town (not from the world) does not autosave")
	Settings.v["autosave"] = keep
	_saves_done()

func test_old_save_still_loads() -> void:
	_saves_sandbox()
	fresh_game()
	# a pre-s4 save: none of the meta keys, only the original eight heroes, a 3-slot era file name
	var old = Game.S.duplicate(true)
	for k in ["stats", "fish", "achievements", "ng"]:
		old.erase(k)
	for cid in ["C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17"]:
		old["party"]["members"].erase(cid)
	Game.S = old
	check(Game.save_to(Game.slot_path(1))["ok"], "old-shape state written to slot 1")
	Game.new_game()
	var r = Game.load_from(Game.slot_path(1))
	check(r.get("ok", false), "old save loads")
	eq(typeof(Game.S.get("stats")), TYPE_DICTIONARY, "stats added")
	check(Game.S.get("fish", {}).has("log"), "fish log added")
	eq(Game.S.get("achievements"), [], "achievement mirror added")
	eq(int(Game.S.get("ng", -1)), 0, "NG cycle 0")
	check(Game.S["party"]["members"].has("C17"), "overhaul heroes added")
	eq(Game.stat("battles"), 0, "counters read with defaults")
	check(Game.slot_info(1).get("ok", false), "old save shows in the list")
	_saves_done()

func test_boss_win_counts_and_requests_autosave() -> void:
	_saves_sandbox()
	var m = model_with(["C01"], ["E001"], 10)
	Game.fixture_label = ""
	var keep = Settings.v["autosave"]
	Settings.v["autosave"] = true
	m.is_boss_battle = true
	m.party_kos = 0
	Game._battle_stats(m)
	eq(Game.stat("boss_wins"), 1, "boss win counted")
	eq(Game.stat("boss_nokos"), 1, "no-KO boss win counted")
	check(Game.autosave_pending(), "boss victory requests an autosave")
	Game._autosave_reason = ""
	m.party_kos = 2
	Game._battle_stats(m)
	eq(Game.stat("boss_nokos"), 1, "a KO spoils the no-KO record")
	Settings.v["autosave"] = keep
	_saves_done()

func test_waylamp_item_and_shops() -> void:
	var it = Content.item("Y08")
	eq(str(it.get("special", "")), "save_lantern", "Waylamp is the portable save item")
	check(it.get("field", false) and not it.get("battle", true), "field only")
	var n = 0
	for sid in Content.data["shops"]:
		if Content.data["shops"][sid].get("extra", []).has("Y08"):
			n += 1
	check(n >= 2 and n <= 3, "sold in 2-3 shops (%d)" % n)
	var boss_rooms = 0
	for mid in Content.data["maps"]:
		if Content.data["maps"][mid].get("boss_room", false):
			boss_rooms += 1
	check(boss_rooms > 5, "boss rooms are marked for the Waylamp (%d)" % boss_rooms)

# ---------------------------------------------------------------- achievements
func test_achievement_definitions() -> void:
	var d = Achievements.defs()
	check(d.size() >= 40 and d.size() <= 60, "40-60 achievements (%d)" % d.size())
	fresh_game()
	for id in d:
		var ok = typeof(Game.eval_cond(d[id]["cond"])) == TYPE_BOOL
		check(ok, "conditions evaluate for " + id)
	var groups = {}
	for id in d:
		groups[d[id]["group"]] = true
	for g in ["Story", "Superbosses", "Collection", "Crafts", "Fishing", "Battle", "Secrets"]:
		check(groups.has(g), "group present: " + g)

func test_achievements_unlock_and_progress() -> void:
	_profile_sandbox()
	fresh_game()
	check(not Achievements.is_unlocked("ST01"), "locked at start")
	Game.complete_chapter("CH01")
	var got = Achievements.evaluate()
	check(got.has("ST01"), "chapter milestone unlocks by evaluation")
	check(Game.S["achievements"].has("ST01"), "mirrored into the save")
	check(Achievements.evaluate().is_empty() or not Achievements.evaluate().has("ST01"), "no double unlock")
	check(Game.achieve("FS07"), "direct unlock via Game.achieve")
	check(not Game.achieve("FS07"), "second unlock is a no-op")
	check(not Game.achieve("NOPE"), "unknown id refused")
	Game.stat_add("battles", 10)
	var pr = Achievements.progress("BT01")
	eq(pr, [10.0, 50.0], "progress from a numeric condition")
	Game.stat_add("battles", 40)
	Achievements.evaluate()
	check(Achievements.is_unlocked("BT01"), "counter achievement unlocks at the target")
	# profile persistence: a fresh game still shows profile unlocks
	fresh_game()
	check(Achievements.is_unlocked("ST01"), "profile keeps unlocks across saves")
	_profile_done()

func test_achievement_meta_values() -> void:
	fresh_game()
	eq(Achievements.meta_value("recruited"), 1.0, "one recruit")
	Game.recruit("C02")
	eq(Achievements.meta_value("recruited"), 2.0, "two recruits")
	check(Game.eval_cond(["meta:recruited>=2"]), "meta condition true")
	check(not Game.eval_cond(["meta:recruited>=3"]), "meta condition false")
	check(Game.eval_cond(["!stat:battles>=1"]), "negated stat condition")
	check(Achievements.meta_value("bestiary_pct") == 0.0, "empty bestiary")

# ---------------------------------------------------------------- New Game+
func test_new_game_plus_carry_over() -> void:
	_profile_sandbox()
	fresh_game()
	Game.recruit("C02")
	for cid in ["C01", "C02"]:
		Game.member(cid)["level"] = 42
		Game.member(cid)["xp"] = F.xp_total_for_level(42)
	Game.add_item("W010", 1)
	var key_id = ""
	for iid in Content.data["items"]:
		if Content.item(iid)["kind"] == "key":
			key_id = iid
			break
	Game.add_item(key_id, 1)
	Game.grant_vestige("V01")
	Game.link_vestige("V01", "C02")
	Game.bestiary_seen("E001", "defeated")
	Game.complete_chapter("CH01")
	Game.set_flag("some_story_flag")
	Game.S["difficulty"] = "hard"
	Game.add_gold(5000)
	Game.S["fish"]["log"]["F01"] = {"n": 3, "best": 50.0, "kg": 2.0}
	Game.achieve("ST10")
	Game.S["clear"] = true
	var gold = Game.gold()
	var before = Game.battle_difficulty()["hp"]
	Game.new_game_plus(Game.S.duplicate(true))
	eq(int(Game.S["ng"]), 1, "NG+ cycle 1")
	eq(int(Game.member("C01")["level"]), 42, "leader level carried")
	eq(int(Game.member("C02")["level"]), 42, "other heroes keep their levels for when they rejoin")
	eq(Game.S["party"]["roster"], ["C01"], "story roster resets")
	eq(Game.count("W010"), 1, "gear carried")
	eq(Game.count(key_id), 0, "key items reset")
	check(Game.has_vestige("V01"), "Vestiges carried")
	eq(Game.S["links"], {}, "links cleared")
	check(int(Game.S["bestiary"].get("E001", {}).get("defeated", 0)) > 0, "bestiary carried")
	check(Game.S["fish"]["log"].has("F01"), "fish log carried")
	check(Game.S["achievements"].has("ST10"), "achievements carried")
	eq(Game.S["chapters"], [], "chapters reset")
	check(not Game.flag("some_story_flag"), "story flags reset")
	eq(Game.gold(), gold, "crowns carried")
	eq(Game.difficulty(), "hard", "difficulty choice kept")
	check(not bool(Game.S.get("clear", false)), "not cleared yet in the new cycle")
	check(Game.battle_difficulty()["hp"] > before, "enemies scale up")
	check(Game.eval_cond(["ng"]), "ng condition")
	Achievements.evaluate()
	check(Achievements.is_unlocked("ST11"), "NG+ achievement")
	_profile_done()

# ---------------------------------------------------------------- Mature
func test_mature_markup_filter() -> void:
	eq(Game.mature_filter("Stand aside{m:, you bastards|}.", false), "Stand aside.", "mild: empty side")
	eq(Game.mature_filter("Stand aside{m:, you bastards|}.", true), "Stand aside, you bastards.", "strong side")
	eq(Game.mature_filter("the {m:bastard|man} said", false), "the man said", "mild wording")
	eq(Game.mature_filter("Don't {m:fucking |}distract me.", false), "Don't distract me.", "no double space")
	eq(Game.mature_filter("No markup here.", true), "No markup here.", "plain lines unchanged")
	var keep = [Settings.v["mature"], Settings.v["mature_ok"]]
	Settings.v["mature"] = false
	check(not Game.eval_cond(["mature"]), "mature condition off by default")
	Settings.v["mature"] = true
	Settings.v["mature_ok"] = false
	check(not Game.mature(), "needs the 18+ confirmation too")
	Settings.v["mature_ok"] = true
	check(Game.eval_cond(["mature"]) and Game.eval_cond(["!mature"]) == false, "mature condition on")
	Settings.v["mature"] = keep[0]
	Settings.v["mature_ok"] = keep[1]
	var n = 0
	var branches = 0
	for sid in Content.data["scenes"]:
		for c in Content.data["scenes"][sid]["cmds"]:
			if c["c"] == "say" and str(c.get("text", "")).find("{m:") >= 0:
				n += 1
				check(Game.mature_filter(c["text"], false).find("{") < 0, "mild render clean in " + sid)
				check(Game.mature_filter(c["text"], true).find("}") < 0, "strong render clean in " + sid)
			if c["c"] == "if" and str(c["a"][0]).find("mature") >= 0:
				branches += 1
	check(n >= 20 and n <= 30, "20-30 marked lines (%d)" % n)
	check(branches >= 2, "scene-level mature branches (%d)" % branches)

# ---------------------------------------------------------------- fishing
func test_fish_content() -> void:
	var fd: Dictionary = FishCore.data()
	check(fd.get("fish", {}).size() >= 40, "40+ fish (%d)" % fd.get("fish", {}).size())
	var night = 0
	for fid in fd["fish"]:
		if fd["fish"][fid]["night"]:
			night += 1
	check(night >= 5, "night-only fish")
	for t in fd["tables"]:
		check(not FishCore.candidates(t, true).is_empty(), "table has fish: " + t)
	var spots = 0
	for mid in Content.data["maps"]:
		for e in Content.data["maps"][mid]["entities"]:
			if e["type"] == "fish":
				spots += 1
				check(fd["tables"].has(e["table"]), "spot table valid in " + mid)
				check(e.has("water"), "spot faces water in " + mid)
	check(spots >= 8 and spots <= 12, "8-12 fishing spots (%d)" % spots)

func test_fish_night_filter_and_determinism() -> void:
	var day = FishCore.candidates("river", false).map(func(f): return f["id"])
	var nightc = FishCore.candidates("river", true).map(func(f): return f["id"])
	check(not day.has("F04") and nightc.has("F04"), "catfish bites only at night")
	var a = FishCore.new()
	a.start("ember", 4242, false)
	var b = FishCore.new()
	b.start("ember", 4242, false)
	eq(a.autoplay("good"), b.autoplay("good"), "same seed, same outcome")
	eq(a.fish.get("id", ""), b.fish.get("id", ""), "same fish")
	eq(a.weight, b.weight, "same weight")
	check(FishCore.weight_of(FishCore.fish_def("F23"), 300.0) > FishCore.weight_of(FishCore.fish_def("F23"), 200.0), "weight grows with size")

func test_fishing_policies() -> void:
	var good = 0
	var greedy_snap = 0
	var early = 0
	for i in range(40):
		var c = FishCore.new()
		c.start("ember", 1000 + i * 7919, false)
		if c.autoplay("good") == "caught":
			good += 1
		var g = FishCore.new()
		g.start("ember", 1000 + i * 7919, false)
		g.autoplay("greedy")
		if g.reason == "snapped":
			greedy_snap += 1
		var e = FishCore.new()
		e.start("ember", 1000 + i * 7919, false)
		e.autoplay("early")
		if e.reason == "too_early":
			early += 1
	check(good >= 24, "careful reeling lands most fish (%d/40)" % good)
	check(greedy_snap >= 10, "holding the reel through runs snaps lines (%d/40)" % greedy_snap)
	eq(early, 40, "striking before the bite always spooks the fish")

func test_tournament_scoring_and_log() -> void:
	eq(FishCore.tourney_rank(25.0), 1, "gold weight")
	eq(FishCore.tourney_rank(10.0), 2, "silver weight")
	eq(FishCore.tourney_rank(4.0), 3, "bronze weight")
	eq(FishCore.tourney_rank(1.0), 0, "no placing")
	fresh_game()
	var bass = FishCore.fish_def("F13")
	var msgs = FishingGame.record_catch(bass, 60.0, FishCore.weight_of(bass, 60.0), "N14")
	check(not msgs.is_empty(), "catch lines")
	eq(int(Game.S["fish"]["log"]["F13"]["n"]), 1, "logged")
	eq(Game.stat("fish_caught"), 1, "counter")
	check(not Game.flag("fishing_entered"), "no tournament before signing up")
	Game.set_flag("fishing_tournament_open")
	FishingGame.record_catch(bass, 70.0, 4.8, "N14")
	check(Game.flag("fishing_rank3"), "bronze placing flag")
	check(Game.flag("fishing_entered"), "entered flag")
	FishingGame.record_catch(bass, 50.0, 3.5, "N14")
	FishingGame.record_catch(FishCore.fish_def("F23"), 250.0, 62.5, "T04")
	check(not Game.flag("fishing_rank1"), "catches elsewhere do not count")
	FishingGame.record_catch(FishCore.fish_def("F23"), 250.0, 62.5, "N14")
	check(Game.flag("fishing_rank1"), "gold placing flag at Saltwhistle")
	eq(float(Game.S["fish"]["log"]["F13"]["best"]), 70.0, "best size kept")
	# the prize scenes run from the tourney master
	var sc = Content.scene("N14_TOURNEY")
	check(not sc.is_empty(), "tournament scene present")
	var sawg = false
	for c in sc["cmds"]:
		if c["c"] == "if" and str(c["a"][0]).begins_with("flag:fishing_rank1"):
			sawg = true
	check(sawg, "rank flag drives the prize branch")

# ---------------------------------------------------------------- strings, settings, cues
func test_string_table() -> void:
	eq(T.s("menu.Items"), "Items", "table lookup")
	eq(T.s("no.such.key", "Fallback"), "Fallback", "fallback for a missing key")
	eq(T.f("save.slot", [7]), "Slot 7", "formatted lookup")
	for n in GameMenu.MAIN_ITEMS:
		check(T.has("menu." + n), "main menu string " + n)
	for pg in GameMenu.SETTING_PAGES:
		for d in GameMenu.SETTING_PAGES[pg]:
			check(T.has("set." + d[0]), "settings label " + d[0])

func test_theme_and_palettes() -> void:
	check(UI.THEMES.has("dark") and UI.THEMES.has("contrast"), "dark and high-contrast themes")
	eq(UI.THEME_ORDER[0], "dark", "dark listed first")
	var keep = Settings.v["colorblind"]
	Settings.v["colorblind"] = "deuteranopia"
	check(UI.pal(UI.C_GREEN) != UI.C_GREEN and UI.pal(UI.C_RED) != UI.C_RED, "palette remaps green/red")
	Settings.v["colorblind"] = "off"
	eq(UI.pal(UI.C_GREEN), UI.C_GREEN, "palette off")
	Settings.v["colorblind"] = keep
	for e in ["fire", "ice", "storm", "earth", "water", "light", "shadow"]:
		check(UI.ELEM_LETTER.has(e), "shape cue letter for " + e)

func test_auto_battle_retarget() -> void:
	var bs = BattleScene.new()
	bs.model = model_with(["C01", "C02"], ["E001", "E001"], 12)
	var e0: String = bs.model.enemy_ids[0]
	var e1: String = bs.model.enemy_ids[1]
	var c = bs._retarget({"type": "attack", "targets": [e0]})
	eq(c["targets"], [e0], "living target kept")
	bs.model.battlers[e0].hp = 0
	bs.model.battlers[e0].state = "KO"
	c = bs._retarget({"type": "attack", "targets": [e0]})
	eq(c["targets"], [e1], "dead target replaced by a living enemy")
	var p1: String = bs.model.party_ids[1]
	bs.model.battlers[p1].hp = 1
	c = bs._retarget({"type": "item", "id": "I001", "targets": [bs.model.party_ids[0]]})
	eq(c["targets"], [bs.model.party_ids[0]], "ally target kept while alive")
	bs.free()

func test_new_game_plus_starts_in_the_field() -> void:
	_profile_sandbox()
	fresh_game()
	Game.member("C01")["level"] = 30
	Game.S["clear"] = true
	var st = Game.S.duplicate(true)
	var main = QA.main
	main.director.skipping = true
	main.dialogue.skip_all = true
	await main.start_new_game_plus(st)
	main.director.skipping = false
	main.dialogue.skip_all = false
	eq(int(Game.S.get("ng", 0)), 1, "cycle 1 started")
	eq(main.mode, "field", "in the field")
	eq(main.field.map_id, str(Game.S["location"]["map"]), "at the new game's start map")
	eq(int(Game.member("C01")["level"]), 30, "level carried into play")
	Game.fixture_label = "unit-fixture"
	_profile_done()
