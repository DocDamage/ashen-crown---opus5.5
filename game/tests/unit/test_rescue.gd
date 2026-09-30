extends TestCase
## CH12 rescue (story/rescue.gd): the hidden timer, arrivals and hints, changed heroes, and the Bound party
## (swap, reunion hold, merge on a superboss). Fixture set-up edits state directly (test scaffolding).

func _skip(scene_id: String) -> String:
	var main = QA.main
	main.director.skipping = true
	main.dialogue.skip_all = true
	var r = await main.director.run(scene_id)
	main.director.skipping = false
	main.dialogue.skip_all = false
	return str(r)

func _ready_ch12() -> void:
	fresh_game()
	for cid in Game.CHAR_IDS:
		Game.recruit(cid)
		Game.member(cid)["level"] = 30
	for ch in ["CH01", "CH02", "CH03", "CH04", "CH05", "CH06", "CH07", "CH08", "CH09", "CH10", "CH11"]:
		Game.complete_chapter(ch)

func _run_timer(until: float) -> Array:
	var scenes = []
	var t = 0.0
	while t < until:
		var s = Rescue.tick(0.5)
		t += 0.5
		if s != "":
			scenes.append(s)
	return scenes

func test_timer_arrivals_and_hints() -> void:
	_ready_ch12()
	var team = ["C02", "C03", "C04", "C05", "C07"]
	Rescue.begin(team)
	for c in team:
		check(not Game.is_available(c), "%s leaves for the cells" % c)
	var sc = _run_timer(60.0)
	check(sc.has("CH12_HINT1"), "first hint at 15s")
	check(sc.has("CH12_ARRIVE_C02") and sc.has("CH12_ARRIVE_C03"), "first two arrive by 60s")
	check(not sc.has("CH12_ARRIVE_C04"), "third not yet")
	eq(Game.S["vars"]["rescue_left"], 3, "three still below")
	check(Game.is_available("C02"), "arrived hero is back in the party")
	var lost = Rescue.finish()
	eq(lost, ["C04", "C05", "C07"], "the late three are lost")
	eq(Rescue.form("C07"), "undead", "Oni returns undead")
	eq(Rescue.form("C04"), "rebuilt", "Golem is rebuilt")
	eq(Rescue.form("C05"), "fragment", "Elowen is fragment-bound")
	eq(Rescue.form("C02"), "", "a survivor is unchanged")
	check(Game.flag("bound_formed") and not Game.flag("rescue_all"), "the Bound form")
	check(Game.eval_cond(["changed:C07:undead", "bound", "bound_member:C02", "!bound_on"]), "conditions")

func test_waiting_brings_everyone_and_the_deadline_crushes() -> void:
	_ready_ch12()
	Rescue.begin(["C02", "C03", "C04", "C05", "C07"])
	var sc = _run_timer(97.0)
	check(Rescue.all_arrived(), "all five arrive by 96s")
	eq(Game.S["vars"]["rescue_left"], 0, "none left")
	check(Rescue.finish().is_empty(), "nobody is lost")
	check(Game.flag("rescue_all") and not Game.flag("bound_formed"), "no Bound when everyone lives")
	_ready_ch12()
	Rescue.begin(["C02", "C03", "C04", "C05", "C07"])
	var sc2 = _run_timer(101.0)
	check(sc2.has("CH12_LIFT_CRUSH"), "the cable goes at 100s")
	Rescue.retry()
	check(Rescue.running() and float(Rescue.state()["t"]) == 0.0, "retry restarts the timer")

func test_small_team_keeps_late_slots() -> void:
	eq(Rescue.arrival_times(2), [81.0, 96.0], "two rescuers take the last two slots")

func test_changed_passives() -> void:
	_ready_ch12()
	var before = Game.stats("C07")
	Game.S["changed"] = {"C07": "undead", "C04": "rebuilt", "C02": "fragment"}
	var st = Game.stats("C07")
	check(st["atk"] > before["atk"], "undead hit harder")
	check(st["passives"]["immune"].has("poison"), "undead ignore poison")
	check(Game.stats("C04")["passives"]["immune"].has("sleep"), "rebuilt cannot sleep")
	check(Game.stats("C02")["passives"]["elem_resist"].has("fire"), "fragment-bound resist fire")
	check(Rescue.tint("C07") != Color.WHITE and Rescue.tint("C01") == Color.WHITE, "tints")

func test_bound_swap_hold_and_merge() -> void:
	_ready_ch12()
	var team = ["C02", "C03", "C04", "C05", "C07"]
	Rescue.begin(team)
	_run_timer(55.0)
	Rescue.finish()
	Game.catastrophe_transaction()
	check(Rescue.bound_active(), "the Bound survive the catastrophe transaction")
	check(Rescue.holds("C05"), "a reunion with a bound hero holds her with the Bound")
	var dest = Rescue.swap({"map": "T07_HEARTH", "x": 5, "y": 5, "dir": "down"})
	eq(dest["map"], "BOUND_CAMP", "the Bound start in the Rootwell")
	eq(Game.active(), team, "the Bound are the party")
	check(not Game.is_available("C01") and Game.S["party"]["locked"], "Raven is away; formation locked")
	check(Rescue.bound_on() and not Rescue.holds("C05"), "while in control nobody is held")
	var back = Rescue.swap({"map": "BOUND_CAMP", "x": 9, "y": 6, "dir": "up"})
	eq(back["map"], "T07_HEARTH", "back to Raven")
	check(Game.is_available("C01") and not Game.is_available("C05"), "Raven's company again")
	eq(Rescue.bound()["loc"]["x"], 9, "the Bound keep their spot")
	Game.superboss_victory("SB01")
	check(Rescue.bound()["merged"] and Game.is_available("C05") and Game.is_available("C01"), "a superboss merges the Bound")
	check(not Game.S["party"]["locked"], "formation unlocked")

func test_drop_scene_skip_path() -> void:
	_ready_ch12()
	QA.main.enter_field("D09_ESC", "start")
	Rescue.begin(["C02", "C03", "C04", "C05", "C07"])
	_run_timer(40.0)
	await _skip("CH12_LIFT_DROP")
	eq(Game.S["world_phase"], "post", "the drop runs the fall")
	check(Game.flag("bound_formed"), "Bound formed")
	eq(QA.main.field.map_id, "T07_HEARTH", "Raven wakes at Hearthward after the Bound interlude")

func test_bonds_levels_edge_and_scenes() -> void:
	fresh_game()
	for cid in ["C01", "C02", "C06"]:
		Game.recruit(cid)
		Game.member(cid)["level"] = 40
	var base = Game.stats("C01")["atk"]
	var msgs = []
	for i in range(30):
		msgs.append_array(Bonds.after_battle(Game.active()))
	eq(Bonds.level("C01", "C02"), 2, "30 battles together: bond 2")
	check(msgs.size() >= 6, "level-up messages for each pair")
	check(Game.stats("C01")["atk"] > base, "bonded partners give an edge")
	eq(Bonds.ready_scene(), "BOND_C01_C02_2", "the first pair scene is ready")
	var all = Bonds.all_pair_scenes()
	check(all.size() >= 36, "pair scenes authored (%d)" % all.size())
	for id in all:
		var p = str(id).split("_")
		check(p[1] < p[2] and int(p[3]) in Bonds.SCENE_LEVELS, "pair scene id in order: %s" % id)

func test_postgame_belfry_and_completion() -> void:
	_ready_ch12()
	Game.set_flag("post_clear")
	QA.main.enter_field("T07_MARKET", "from_hearth")
	check(QA.main.field.npcs.any(func(n): return str(n.get("id", "")) == "bellwright"), "Anse appears after the clear")
	check(not Content.scene("EPI_BELLWRIGHT").is_empty() and not Content.map("EP1_NAVE").is_empty(), "the Belfry Below exists")
	await _skip("EPI_BELL2")
	check(not Game.flag("epi_b2"), "the second bell will not speak first")
	await _skip("EPI_BELL1")
	await _skip("EPI_BELL2")
	await _skip("EPI_BELL3")
	check(Game.flag("epi_open"), "three bells in order open the stair")
	var pc = Completion.percent()
	check(pc >= 0 and pc < 100, "completion is a percentage (%d)" % pc)
	eq(Completion.parts().size(), 6, "six completion parts")
