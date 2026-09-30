extends TestCase
## StoryDirector integration: skipped scenes commit the same state as watched ones (AC044),
## once-scenes never re-apply (AC045). Uses the real main scene, field and director.

func _state_digest() -> String:
	var s = Game.S.duplicate(true)
	s.erase("playtime")
	s.erase("clock")   # the world clock runs with real time, like playtime
	s.erase("timestamp")
	s.erase("run_id")
	s["location"] = {}
	return JSON.stringify(s, "", true).md5_text()

func _watch(scene_id: String) -> void:
	var main = QA.main
	main.director.run(scene_id)
	var guard = 0
	while main.director.running and guard < 5000:
		var tp = main.router.top()
		if tp is DialogueBox or tp is DocView:
			tp.handle("confirm")
			tp.handle("confirm")
		elif tp is MenuList and tp.get_parent() == main.ui:
			tp.handle("confirm")
		await main.get_tree().process_frame
		guard += 1

func _skip(scene_id: String) -> void:
	var main = QA.main
	main.director.skipping = true
	main.dialogue.skip_all = true
	await main.director.run(scene_id)

func _fixture(map_id: String, spawn: String) -> void:
	fresh_game()
	QA.main.enter_field(map_id, spawn)

func test_skip_equivalence() -> void:
	for pair in [["D01_TESSA", "D01_R02", "from_r01"], ["D01_W3", "D01_R03", "from_r02"], ["V01_PACT", "T01_PLATFORM", "from_quarry"], ["D01_LIST", "D01_R02", "from_r01"]]:
		_fixture(pair[1], pair[2])
		await _watch(pair[0])
		var watched = _state_digest()
		_fixture(pair[1], pair[2])
		await _skip(pair[0])
		var skipped = _state_digest()
		eq(skipped, watched, "skip == watch for " + pair[0])

func test_once_scene_not_reapplied() -> void:
	_fixture("D01_R02", "from_r01")
	await _skip("D01_TESSA")
	var n = Game.S["party"]["roster"].size()
	var r = await QA.main.director.run("D01_TESSA")
	eq(r, "already", "once-scene refuses to run again")
	eq(Game.S["party"]["roster"].size(), n, "no duplicate party join")
	await _skip("D01_W3")
	var w = Game.var_get("workers")
	await _skip("D01_W3")
	eq(Game.var_get("workers"), w, "worker rescue counted once")
