extends Node
## TestSupport: user args after `--` (Godot passes them via OS.get_cmdline_user_args()).
##   --qa-route <name>   run a normal-input route bot (src/qa/routes.gd)
##   --qa-capture        save screenshots at route checkpoints
##   --qa-out <dir>      screenshot/log directory (default user://qa)
##   --qa-speed <n>      Engine.time_scale for faster bots (simulation stays fixed-step)
## The bot only presses the same InputMap actions a player can press. No teleports, no flag edits.

var route = ""
var capture = false
var out_dir = "user://qa"
var active = false
var forced_dir = ""
var log_lines: Array = []
var main: Node
var shots: Array = []
var speed = 1.0
var watchdog = 900
var finished = false
var tests = false
var gallery = ""

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var args = OS.get_cmdline_user_args()
	var i = 0
	while i < args.size():
		match args[i]:
			"--qa-route":
				route = args[i + 1]
				i += 1
			"--qa-tests":
				tests = true
				active = true
			"--qa-gallery":
				gallery = "all"
				active = true
			"--qa-gallery-set":
				gallery = args[i + 1]
				active = true
				i += 1
			"--qa-capture":
				capture = true
			"--qa-out":
				out_dir = args[i + 1]
				i += 1
			"--qa-watchdog":
				watchdog = int(args[i + 1])
				i += 1
			"--qa-speed":
				speed = float(args[i + 1])
				i += 1
		i += 1
	if route != "":
		active = true
		Engine.time_scale = speed
		DirAccess.make_dir_recursive_absolute(out_dir)

func start(p_main: Node) -> void:
	main = p_main
	var scr = load("res://src/qa/routes.gd")
	if scr == null or not scr.can_instantiate():
		finish(false, "route script failed to load")
		return
	var r = scr.new()
	add_child(r)
	get_tree().create_timer(watchdog, true, false, true).timeout.connect(func(): finish(false, "watchdog timeout %ds" % watchdog))
	r.run(main, route)

func run_tests(p_main: Node) -> void:
	main = p_main
	var tr = load("res://tests/test_runner.gd").new()
	add_child(tr)
	var code: int = await tr.run_all()
	get_tree().quit(code)

func note(s: String) -> void:
	var line = "[%.2f] %s" % [Time.get_ticks_msec() / 1000.0, s]
	print("QA ", line)
	log_lines.append(line)

func shot(name: String) -> void:
	if not capture:
		return
	await RenderingServer.frame_post_draw
	var img = get_viewport().get_texture().get_image()
	var path = "%s/%s.png" % [out_dir, name]
	img.save_png(path)
	shots.append(path)
	note("capture " + path)

func finish(ok: bool, summary: String) -> void:
	if finished:
		return
	finished = true
	note(("ROUTE PASS: " if ok else "ROUTE FAIL: ") + summary)
	var f = FileAccess.open("%s/route_%s.log" % [out_dir, route], FileAccess.WRITE)
	if f:
		f.store_string("\n".join(log_lines) + "\n")
		f.close()
	get_tree().quit(0 if ok else 1)

# ---------------------------------------------------------------- dev-only visual gallery
## --qa-gallery / --qa-gallery-set field|battle|ui|all: loads maps and battles directly and screenshots them for
## art review. It edits state freely, so it is never gameplay evidence (routes are).
const GALLERY_MAPS := ["T01_PLATFORM", "T01_BAKERY", "D01_R01", "D02_R01", "D03_R02", "T03_TOWN", "D04_R02", "T04_QUAY",
	"D05_R01", "D06_R01", "T05_COURT", "T06_MARKET", "D07_R01", "D08_R01", "D09_R01", "D10_R01", "T07_MARKET",
	"D11_R01", "D12_R01", "WORLD", "T02_SQUARE", "W_DECK"]
const GALLERY_FORMS := ["D01_4", "D03_2", "B01", "B05", "D07_2", "B08", "OW1_1", "D09_4", "B12", "D12_2",
	# every battle backdrop and boss (art review)
	"D02_2", "B02", "B15", "B03", "B11", "D04_2", "B04", "D05_1", "D06_1", "B06", "B07", "D08_1", "B09", "B10",
	"D10_1", "B16", "D11_1", "B13", "B14", "OW2_1", "OW3_1", "OW4_1", "OW5_1", "OWP_1", "D03P_1", "D01_1", "D02_1"]


func run_gallery(p_main: Node, which: String) -> void:
	main = p_main
	DirAccess.make_dir_recursive_absolute(out_dir)
	await _g_frames(10)
	if which in ["ui", "all"]:
		await _g_shot("ui_title")
	Game.new_game()
	if main.title_screen:
		main.router.pop(main.title_screen)
		main.title_screen.queue_free()
		main.title_screen = null
	if which == "sys_s4":
		await _g_sys_s4()
		get_tree().quit(0)
		return
	if which.begins_with("perf:"):
		# average field frame time (ms) per map: --qa-gallery-set perf:ID1,ID2
		for m in which.substr(5).split(","):
			main.enter_field(m, "default")
			await _g_frames(30)
			var t0 = Time.get_ticks_usec()
			for i in range(120):
				main.field.queue_redraw()
				await RenderingServer.frame_post_draw
			print("PERF %s %.2f ms/frame" % [m, (Time.get_ticks_usec() - t0) / 120000.0])
		get_tree().quit(0)
		return
	if which == "sys_s2":
		await _g_sys_s2()
		get_tree().quit(0)
		return
	if which == "m7":
		# world v2 review: the Mode-7 world maps on foot, mounted and flying (turned), surface and the Deep
		var shots = [["WORLD", "l_t01", "foot", 0.0], ["WORLD", "l_t02", "foot", 0.0], ["WORLD", "l_t03", "mount", 0.0],
			["WORLD", "l_t04", "ship", 0.0], ["WORLD", "l_t02", "ship", 0.9], ["WORLD", "l_n28", "foot", 0.0],
			["WORLD_POST", "l_t07", "foot", 0.0], ["WORLD_POST", "l_t02", "ship", -0.6], ["DEEP", "l_u02", "foot", 0.0],
			["DEEP", "l_u14", "mount", 0.0], ["DEEP_POST", "l_u30", "foot", 0.0]]
		for sh in shots:
			var md: Dictionary = Content.data["maps"][sh[0]]
			var at = Vector2i(-1, -1)
			for e in md["entities"]:
				if e["type"] == "spawn" and e["name"] == sh[1]:
					at = Vector2i(e["x"], e["y"])
			if at.x < 0:
				continue
			Game.S["vehicle"]["mount"] = sh[2] == "mount"
			Game.S["vehicle"]["mode"] = "foot"
			if sh[2] == "ship":
				Game.S["vehicle"]["ship"] = true
				Game.S["vehicle"]["ship_map"] = sh[0]
				Game.S["vehicle"]["ship_x"] = at.x
				Game.S["vehicle"]["ship_y"] = at.y
			else:
				Game.S["vehicle"]["ship"] = false
			main.enter_field(sh[0], "default", at, "down")
			main.field.banner_t = 0.0
			if sh[2] == "ship":
				main.field.ship_op("board")
			await _g_frames(4)
			if main.field.m7 != null:
				main.field.m7.snap(main.field.p_pos + Vector2(8, 12), main.field.m7.profile_key(main.field.vehicle, main.field.riding()))
				main.field.m7.yaw = sh[3]
			await _g_frames(6)
			await _g_shot("m7_%s_%s_%s" % [sh[0], sh[1], sh[2]])
			if sh[1] == "l_t02" and sh[2] == "foot" or sh[0] == "WORLD" and sh[1] == "l_t02" and sh[2] == "ship":
				for c in [["dusk", 1110.0], ["night", 1350.0]]:
					Game.S["clock"] = c[1]
					await _g_frames(4)
					await _g_shot("m7_%s_%s_%s_%s" % [sh[0], sh[1], sh[2], c[0]])
				Game.S["clock"] = 600.0
				main.field.hud.reveal(Vector2i(70, 90), 40)
				main.field.show_map = true
				await _g_frames(8)
				await _g_shot("m7_%s_fullmap" % sh[0])
				main.field.show_map = false
		get_tree().quit(0)
		return
	if which == "rescue":
		# CH12 rescue review: the lift cage, a rescuer arriving, and the Bound in the Rootwell (changed tints)
		Game.new_game()
		for cid in Game.CHAR_IDS:
			Game.recruit(cid)
		var team = ["C02", "C03", "C04", "C07", "C10"]
		main.enter_field(Rescue.LIFT_MAP, "start")
		Rescue.begin(team)
		main.field.update_leader()
		main.field.banner_t = 0.0
		await _g_frames(6)
		await _g_shot("rescue_lift")
		main.field.show_actor("resc", 15, 6, "right", "C03")
		main.field.move_actor("resc", ["right", "right", "right"])
		await _g_frames(20)
		await _g_shot("rescue_arrive")
		Game.S["rescue"]["arrived"] = ["C02", "C03"]
		Rescue.finish()
		Rescue.swap({"map": Rescue.LIFT_MAP, "x": 25, "y": 6, "dir": "left"})
		main.enter_field("BOUND_CAMP", "default")
		main.field.update_leader()
		main.field.banner_t = 0.0
		await _g_frames(8)
		await _g_shot("rescue_bound_camp")
		get_tree().quit(0)
		return
	if which == "ov":
		# overhaul review: vehicles on the world maps, and each new recruit / Vestige in its room
		Game.S["vehicle"]["mount"] = true
		for ch in ["CH14", "CH16", "CH19", "CH20"]:
			Game.complete_chapter(ch)
		Game.quest_set("Q09", "COMPLETED", "")
		main.enter_field("WORLD", "default", Vector2i(30, 50), "down")
		main.field.banner_t = 0.0
		main.field.p_moving = false
		await _g_frames(10)
		await _g_shot("ov_ride_down")
		main.field.p_dir = "right"
		await _g_frames(4)
		await _g_shot("ov_ride_right")
		Game.S["vehicle"]["ship"] = true
		Game.S["vehicle"]["ship_map"] = "WORLD"
		Game.S["vehicle"]["ship_x"] = 32
		Game.S["vehicle"]["ship_y"] = 50
		main.enter_field("WORLD", "default", Vector2i(30, 50), "down")
		main.field.banner_t = 0.0
		await _g_frames(10)
		await _g_shot("ov_wayfarer_parked")
		main.field.ship_op("board")
		main.field.p_dir = "left"
		await _g_frames(10)
		await _g_shot("ov_wayfarer_flying")
		Game.S["world_phase"] = "post"
		Game.S["vehicle"]["ship_map"] = "WORLD_POST"
		Game.S["vehicle"]["mode"] = "foot"
		main.enter_field("WORLD_POST", "default", Vector2i(30, 50), "down")
		main.field.banner_t = 0.0
		await _g_frames(10)
		await _g_shot("ov_lanternwake_parked")
		main.field.ship_op("board")
		main.field.p_dir = "up"
		await _g_frames(10)
		await _g_shot("ov_lanternwake_flying")
		main.field.vehicle = "foot"
		Game.S["vehicle"]["mode"] = "foot"
		for pair in [["T01_PLATFORM", "ov_namer"], ["D11_R05", "ov_lich"], ["T01_POST", "ov_maldrath"], ["D07P_R03", "ov_velkhar"],
				["D08P_R01", "ov_kael"], ["D04P_R01", "ov_rider"], ["D03P_R03", "ov_v09"], ["D03P_R02", "ov_v10"],
				["D10_ALCOVE", "ov_v11"], ["D11_R04", "ov_v12"]]:
			var md: Dictionary = Content.data["maps"][pair[0]]
			var at = Vector2i(-1, -1)
			for e in md["entities"]:
				if e["type"] == "npc" and e["id"] == pair[1]:
					at = Vector2i(e["x"], e["y"] + 2)
			main.enter_field(pair[0], "default", at, "up")
			main.field.banner_t = 0.0
			await _g_frames(12)
			await _g_shot("ov_" + pair[0])
		get_tree().quit(0)
		return
	if which == "sys_s3":
		# field and world systems review (src/qa/gallery_s3.gd)
		await GalleryS3.run(self, main)
		get_tree().quit(0)
		return
	if which.begins_with("map:"):
		# whole-map stitched captures for tile review: --qa-gallery-set map:ID1,ID2 (or map:ALL)
		var ids: Array = Array(which.substr(4).split(","))
		if ids == ["ALL"]:
			ids = Content.data["maps"].keys()
		for m in ids:
			main.enter_field(m, "default")
			main.field.banner_t = 0.0
			var mw = main.field.W * 16
			var mh = main.field.H * 16
			var full = Image.create(maxi(mw, 320) * UI.U, maxi(mh, 240) * UI.U, false, Image.FORMAT_RGBA8)
			var cy = 0
			while cy < mh:
				var cx = 0
				while cx < mw:
					var ox = mini(cx, maxi(mw - 320, 0))
					var oy = mini(cy, maxi(mh - 240, 0))
					main.field.cam_override = Vector2(ox, oy)
					await _g_frames(3)
					await RenderingServer.frame_post_draw
					var img = get_viewport().get_texture().get_image()
					img.convert(Image.FORMAT_RGBA8)
					full.blit_rect(img, Rect2i(0, 0, 320 * UI.U, 240 * UI.U), Vector2i(ox, oy) * UI.U)
					cx += 320
				cy += 240
			main.field.cam_override = Vector2(-1, -1)
			full.save_png("%s/map_%s.png" % [out_dir, m])
			print("GALLERY map_", m)
		get_tree().quit(0)
		return
	if which in ["field", "all", "ui"]:
		for m in GALLERY_MAPS:
			if not Content.data["maps"].has(m):
				continue
			main.enter_field(m, "default")
			main.field.banner_t = 0.0
			await _g_frames(8)
			await _g_shot("field_" + m)
	if which in ["ui", "all"]:
		main.enter_field("T01_PLATFORM", "default")
		main.field.banner_t = 0.0
		main.say("Morwen", "The quarry bell rang twice at dawn. That only happens when the lower gate floods.", "C02")
		await _g_frames(40)
		await _g_shot("ui_dialogue")
		main.dialogue.visible = false
		main.router.pop(main.dialogue)
		await _g_ui_screens()
	if which == "fx" or which == "cast":
		# overhaul review: all heroes in battle poses and spell effects mid-play
		var groups = [["C01", "C02", "C03", "C04", "C05"], ["C06", "C07", "C08", "C09", "C10"], ["C11", "C12", "C13", "C14", "C15"], ["C16", "C17", "C01", "C02", "C03"]]
		var fxn = [["fire_impact", "ice_area", "storm_pillar", "holy_nova"], ["shadow_nova", "earth_pillar", "water_area", "poison_aura"], ["green_heal", "gold_levelup", "blue_shield", "arcane_rune"], ["red_statdown", "white_shine", "purple_stun", "gold_buff"]]
		for gi in range(groups.size()):
			Game.S["party"]["active"] = []
			for cid in groups[gi]:
				Game.recruit(cid)
			Game.S["party"]["active"] = groups[gi].slice(0, 5)
			var bs = BattleScene.new()
			bs.main = main
			main.world.add_child(bs)
			main.field.visible = false
			bs.setup("D01_1", 1234, {})
			await _g_frames(20)
			var anims = ["idle", "attack", "cast", "victory", "hurt"]
			for i in range(bs.model.party_ids.size()):
				bs.anim[bs.model.party_ids[i]] = {"name": anims[i % anims.size()], "t": 0.35}
			var k = 0
			for nm in fxn[gi]:
				bs._fx(nm, Vector2(60 + k * 45, 110))
				k += 1
			await _g_frames(12)
			await _g_shot("cast_%d" % gi)
			bs.queue_free()
			await _g_frames(2)
		get_tree().quit(0)
		return
	if which == "sys_s1":
		await _g_sys_s1()
		get_tree().quit(0)
		return
	if which in ["battle", "all"] or which.begins_with("battle:"):
		for cid in ["C02", "C03", "C04", "C05"]:
			if Content.data["characters"].has(cid):
				Game.recruit(cid)
		var forms: Array = GALLERY_FORMS if not which.begins_with("battle:") else Array(which.substr(7).split(","))
		for f in forms:
			if Content.formation(f).is_empty():
				continue
			var bs = BattleScene.new()
			bs.main = main
			main.world.add_child(bs)
			main.field.visible = false
			bs.setup(f, 1234, {})
			await _g_frames(90)
			await _g_shot("battle_" + f)
			bs.queue_free()
			await _g_frames(2)
	get_tree().quit(0)

## Expansion battle systems (branch s1): limit gauge + Limit menu, Lore (blue magic), Swap with the bench, Capture,
## the Formation page with bench and row depth.
func _g_sys_s1() -> void:
	var act = ["C04", "C08", "C09", "C12", "C13"]
	var bench = ["C01", "C02", "C03"]
	for cid in act + bench:
		Game.recruit(cid)
		var m = Game.member(cid)
		m["level"] = 42
		m["xp"] = F.xp_total_for_level(42)
	Game.S["party"]["roster"] = act + bench + Game.S["party"]["roster"].filter(func(c): return not (act + bench).has(c))
	Game.set_active(act)
	Game.heal_all()
	Game.S["blue"] = ["S301", "S303", "S306", "S313", "S315", "S317", "S321", "S323"]
	Game.member("C04")["limit_gauge"] = 100.0
	Game.member("C04")["limit_uses"] = {"S413": 3, "S414": 5}
	Game.member("C08")["limit_gauge"] = 55.0
	Game.member("C09")["limit_gauge"] = 20.0
	Game.member("C12")["limit_gauge"] = 85.0
	Game.member("C13")["limit_gauge"] = 100.0
	await _g_menu("main", {}, "sys_s1_formation", func(m): m._formation_menu(); m.lists[-1].index = 5)
	await _g_menu("main", {}, "sys_s1_abilities", func(m): m._abilities_menu("C04"); m.lists[-1].index = m.lists[-1].items.size() - 9; m.lists[-1]._fix_scroll())
	for vid in ["V13", "V24"]:
		Game.grant_vestige(vid)
	Game.link_vestige("V24", "C13")
	await _g_menu("main", {}, "sys_s1_vestiges", func(m): m._vestige_menu(); m.lists[-1].index = 1)
	var bs = BattleScene.new()
	bs.main = main
	main.world.add_child(bs)
	main.field.visible = false
	bs.setup("D09_4", 1234, {})
	bs.hint_t = 0.0
	for bid in bs.model.party_ids:
		bs.model.battlers[bid].atb = 0.0
	bs.model.battlers[bs.model.party_ids[0]].atb = 990.0
	for eid in bs.model.enemy_ids:
		bs.model.battlers[eid].atb = 0.0
	var g = 0
	while bs.cmd_menu == null and g < 300:
		await _g_frames(1)
		g += 1
	await _g_frames(20)
	await _g_shot("sys_s1_commands_limit")
	bs._on_cmd(0, {"value": "limit"})
	await _g_frames(8)
	await _g_shot("sys_s1_limit_menu")
	bs.sub_menu.emit_signal("cancelled")
	await _g_frames(2)
	bs._on_cmd(0, {"value": "lore"})
	await _g_frames(8)
	await _g_shot("sys_s1_lore_menu")
	bs.sub_menu.emit_signal("cancelled")
	await _g_frames(2)
	bs._on_cmd(0, {"value": "swap"})
	await _g_frames(8)
	await _g_shot("sys_s1_swap_menu")
	bs.sub_menu.chosen.emit(0, bs.sub_menu.items[0])
	g = 0
	while g < 240 and (bs.cmd_menu == null or bs.selecting == null):
		await _g_frames(1)
		g += 1
	await _g_frames(10)
	await _g_shot("sys_s1_after_swap")
	# Capture: Sak on a weakened enemy
	if bs.selecting != null and bs.selecting.ref != "C08":
		bs._close_menus()
	var sak = null
	for bid in bs.model.party_ids:
		if bs.model.battlers[bid].ref == "C08":
			sak = bs.model.battlers[bid]
	if sak != null:
		for bid in bs.model.ready_order.duplicate():
			if bid != sak.id:
				bs.model.cancel_select(bs.model.battlers[bid])
				bs.model.ready_order.erase(bid)
				bs.model.battlers[bid].state = "FILLING"
				bs.model.battlers[bid].atb = 0.0
		bs._close_menus()
		sak.atb = 999.0
		var e0 = bs.model.battlers[bs.model.enemy_ids[0]]
		e0.hp = int(e0.mhp * 0.2)
		g = 0
		while g < 300 and (bs.selecting == null or bs.selecting != sak):
			await _g_frames(1)
			g += 1
		await _g_frames(6)
		await _g_shot("sys_s1_capture_command")
	bs.queue_free()
	await _g_frames(2)

func _g_menu(kind: String, data: Dictionary, name: String, drive: Callable = Callable()) -> void:
	var m = GameMenu.new()
	m.main = main
	main.ui.add_child(m)
	m.open(kind, data)
	if drive.is_valid():
		drive.call(m)
	await _g_frames(10)
	await _g_shot(name)
	for l in m.lists:
		main.router.pop(l)
	main.router.pop(m)
	m.queue_free()
	await _g_frames(2)

func _g_top_menu() -> MenuList:
	for i in range(main.ui.get_child_count() - 1, -1, -1):
		var c = main.ui.get_child(i)
		if c is MenuList:
			return c
	return null

func _g_ui_screens() -> void:
	await _g_menu("main", {}, "ui_menu_solo")
	for cid in ["C02", "C03", "C05"]:
		Game.recruit(cid)
	Game.S["party"]["roster"].append("C04")
	for iid in ["I001", "I002", "I003", "I004", "I005", "W002", "W008"]:
		Game.add_item(iid, 3)
	Game.add_gold(1234)
	if Content.data["vestiges"].has("V01"):
		Game.grant_vestige("V01")
		Game.link_vestige("V01", "C02")
	var leader: String = Game.active()[0]
	await _g_menu("main", {}, "ui_menu")
	await _g_menu("main", {}, "ui_menu_items", func(m): m._items_menu())
	await _g_menu("main", {}, "ui_menu_pick", func(m): m._items_menu(); m._pick_member(func(_c): pass, "Use on whom?"))
	await _g_menu("main", {}, "ui_menu_equip", func(m): m._equip_menu(leader))
	await _g_menu("main", {}, "ui_menu_equip_pick", func(m): m._equip_menu(leader); m._equip_pick(leader, "weapon", func(): pass))
	await _g_menu("main", {}, "ui_menu_abilities", func(m): m._abilities_menu("C02"))
	await _g_menu("main", {}, "ui_menu_formation", func(m): m._formation_menu())
	await _g_menu("main", {}, "ui_menu_vestiges", func(m): m._vestige_menu())
	await _g_menu("main", {}, "ui_menu_journal", func(m): m._journal())
	await _g_menu("main", {}, "ui_menu_worldmap", func(m): m._worldmap())
	await _g_menu("main", {}, "ui_menu_bestiary", func(m): m._bestiary())
	await _g_menu("settings", {}, "ui_settings")
	await _g_menu("main", {}, "ui_save", func(m): m._save_menu(false))
	await _g_menu("main", {}, "ui_confirm", func(m): m._save_menu(false); m._confirm("Overwrite slot 1?", func(): pass))
	await _g_menu("shop", {"id": "SHOP_T01"}, "ui_shop", func(m): m._shop_list("SHOP_T01", true))
	await _g_menu("shop", {"id": "SHOP_T01"}, "ui_shop_gear", func(m): m._shop_list("SHOP_T01", true); m.lists[-1].index = m.lists[-1].items.size() - 1; m.lists[-1]._fix_scroll())
	# expansion Phase 2: regional stock at Veyr, the smith at Cinderwake
	Game.complete_chapter("CH01")
	Game.complete_chapter("CH03")
	Game.add_item("M001", 4)
	Game.add_item("W101", 1)
	await _g_menu("shop", {"id": "SHOP_T02"}, "ui_shop_regional", func(m): m._shop_list("SHOP_T02", true); m.lists[-1].index = m.lists[-1].items.size() - 3; m.lists[-1]._fix_scroll())
	await _g_menu("shop", {"id": "SHOP_T03"}, "ui_shop_smith_menu")
	await _g_menu("shop", {"id": "SHOP_T03"}, "ui_smith", func(m): m._smith_list())
	await _g_menu("inn", {"price": 20}, "ui_inn")
	var old_theme = Settings.v.get("window_color", "blue")
	Settings.v["window_color"] = "crimson"
	await _g_menu("main", {}, "ui_menu_theme_crimson")
	Settings.v["window_color"] = old_theme
	# dialogue with a choice
	main.say("Morwen", "Do we take the flooded gate, or wait for the pumps?", "C02")
	main.choose(["Take the gate", "Wait for the pumps"])
	await _g_frames(40)
	await _g_shot("ui_choice")
	var cm = _g_top_menu()
	if cm:
		cm.handle("confirm")
	main.dialogue.visible = false
	main.router.pop(main.dialogue)
	await _g_frames(4)
	main.toast("Obtained Tonic x3.")
	main.field.show_banner("Brackenford")
	main.field.banner_t = 2.0
	await _g_frames(6)
	await _g_shot("ui_toast_banner")
	main.toasts.clear()
	main.toast_box.queue_redraw()
	main.field.banner_t = 0.0
	var d = DocView.new()
	d.setup("Quarry Ledger", "Third bell: the lower gate took water at dawn. Pumps two and three seized. Foreman Hale ordered the crews up the east stair and sent word to the relay office. No one answered. The water is still rising, slowly, and it smells of copper.")
	main.ui.add_child(d)
	await _g_frames(4)
	await _g_shot("ui_doc")
	d.queue_free()
	main.paused_overlay.visible = true
	main.paused_overlay.queue_redraw()
	await _g_frames(4)
	await _g_shot("ui_paused")
	main.paused_overlay.visible = false
	main.defeat_menu()
	await _g_frames(10)
	await _g_shot("ui_defeat")
	var dm = _g_top_menu()
	if dm:
		dm.handle("confirm")
	await _g_frames(4)
	var cr = CreditsView.new()
	main.ui.add_child(cr)
	cr.t = 6.0
	await _g_frames(4)
	await _g_shot("ui_credits")
	cr.queue_free()
	await _g_frames(2)

## Systems s2 review: crafting bench, a gathering node and its message, the bestiary (data, lore, rewards), set bonus.
func _g_sys_s2() -> void:
	for cid in ["C02", "C03", "C04", "C05"]:
		Game.recruit(cid)
	for ch in ["CH01", "CH02", "CH03", "CH04"]:
		Game.complete_chapter(ch)
	Game.add_gold(5000)
	for iid in ["M001", "MT01", "MT20", "MT34", "MT10", "MT30"]:
		Game.add_item(iid, 4)
	main.enter_field("N06_SMITH", "entry")
	main.field.banner_t = 0.0
	await _g_frames(20)
	await _g_menu("craft", {"id": "crafter_n06"}, "s2_craft_bench")
	await _g_menu("craft", {"id": "crafter_n06"}, "s2_craft_weapons", func(m): m._craft_list("weapon"))
	await _g_menu("craft", {"id": "crafter_n06"}, "s2_craft_items", func(m): m._craft_list("consumable"); m.lists[-1].index = 3; m.lists[-1]._fix_scroll())
	main.enter_field("N06_R01", "default")
	main.field.banner_t = 0.0
	# a gathering node, then its harvest message
	main.field.place_player(9, 24, "down")
	await _g_frames(20)
	await _g_shot("s2_node_field")
	main.field.interact()
	await _g_frames(12)
	await _g_shot("s2_gather_message")
	main.toasts.clear()
	main.toast_box.queue_redraw()
	# bestiary: some seen, some defeated, one scanned
	var ids = Game.bestiary_entries()
	for i in range(ids.size()):
		if i % 3 != 2:
			Game.bestiary_seen(ids[i], "seen")
		if i % 3 == 0:
			Game.bestiary_seen(ids[i], "defeated")
	Game.bestiary_seen("E047", "scan")
	var at = ids.find("E047") + 1
	await _g_menu("main", {}, "s2_bestiary_data", func(m): m._bestiary(); m.lists[-1].index = at; m.lists[-1]._fix_scroll())
	await _g_menu("main", {}, "s2_bestiary_lore", func(m): m._bestiary(); m.lists[-1].index = at; m.lists[-1]._fix_scroll(); m.best_tab = 1)
	await _g_menu("main", {}, "s2_bestiary_rewards", func(m): m._bestiary())
	# a two-piece set and a teaching accessory on Raven
	for iid in ["WN01", "GN01", "AN01"]:
		Game.add_item(iid, 1)
	Game.equip("C01", "weapon", "WN01")
	Game.equip("C01", "head", "GN01")
	Game.equip("C01", "acc1", "AN01")
	Game.gear_learning(4)
	await _g_menu("main", {}, "s2_equip_set", func(m): m._equip_menu("C01"))
	# region tier stock at Kettle Row
	await _g_menu("shop", {"id": "SHOP_N06"}, "s2_shop_tier", func(m): m._shop_list("SHOP_N06", true); m.lists[-1].index = m.lists[-1].items.size() - 4; m.lists[-1]._fix_scroll())

func _g_frames(n: int) -> void:
	for i in range(n):
		await get_tree().process_frame

func _g_shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	var img = get_viewport().get_texture().get_image()
	img.save_png("%s/%s.png" % [out_dir, name])
	print("GALLERY ", name)

# ---------------------------------------------------------------- sys s4 gallery: saves, records, settings, fishing
func _g_sys_s4() -> void:
	var keep_settings = Settings.v.duplicate(true)
	Game.save_root = "user://gallery_saves"
	DirAccess.make_dir_recursive_absolute(Game.save_root)
	Achievements.reset_profile("user://gallery_profile.json")
	Achievements.quiet = true
	Settings.v["window_color"] = "dark"
	for cid in ["C02", "C03", "C07"]:
		Game.recruit(cid)
	for cid in Game.S["party"]["roster"]:
		Game.member(cid)["level"] = 18
	Game.complete_chapter("CH01")
	Game.complete_chapter("CH02")
	Game.S["playtime"] = 4 * 3600 + 17 * 60
	Game.fixture_label = ""
	Game.save_slot(1)
	Game.S["playtime"] += 1800.0
	Game.save_slot(3)
	Game.save_auto("map")
	Game.save_quick()
	Game.stat_add("battles", 31)
	Game.S["fish"]["log"]["F13"] = {"n": 4, "best": 71.2, "kg": 5.03}
	Game.S["fish"]["log"]["F23"] = {"n": 1, "best": 262.0, "kg": 71.9}
	Game.S["fish"]["log"]["F02"] = {"n": 9, "best": 21.0, "kg": 0.17}
	Achievements.evaluate()
	Game.achieve("FS01")
	main.enter_field("N14_R01", "world")
	main.field.banner_t = 0.0
	await _g_frames(6)
	await _g_menu("main", {}, "s4_menu_main")
	await _g_menu("main", {}, "s4_save_list", func(m): m._save_menu(false); m.lists[-1].index = 2; m.lists[-1]._fix_scroll())
	await _g_menu("load", {}, "s4_load_list", func(m): m.lists[-1].index = 12; m.lists[-1]._fix_scroll())
	await _g_menu("main", {}, "s4_records", func(m): m._records_menu())
	await _g_menu("main", {}, "s4_achievements", func(m): m._achievements_page(); m.lists[-1].index = 1)
	await _g_menu("main", {}, "s4_fishlog", func(m): m._fish_log_page(); m.lists[-1].index = 22; m.lists[-1]._fix_scroll())
	await _g_menu("settings", {}, "s4_settings_pages")
	await _g_menu("settings", {}, "s4_settings_access", func(m): m._settings_page("access"))
	await _g_menu("settings", {}, "s4_settings_text", func(m): m._settings_page("text"))
	Settings.v["glyphs"] = "xbox"
	await _g_menu("settings", {}, "s4_settings_pad_xbox", func(m): m._settings_page("pad"))
	Settings.v["glyphs"] = "playstation"
	await _g_menu("settings", {}, "s4_settings_pad_ps", func(m): m._settings_page("pad"))
	Settings.v["glyphs"] = "keyboard"
	await _g_menu("settings", {}, "s4_settings_keys", func(m): m._settings_page("keys"))
	# accessibility looks: large text dialogue at 70% opacity, colour-blind palette, high contrast
	Settings.v["glyphs"] = "deck"
	Settings.v["text_size"] = 1
	Settings.v["dialogue_opacity"] = 0.7
	main.say("Oni", "The seals remember every hand that wrote them. Mine too. Keep your weapons low in there; some of them flinch.", "C07")
	await _g_frames(80)
	await _g_shot("s4_dialogue_large")
	main.dialogue.handle("confirm")
	main.dialogue.handle("confirm")
	main.dialogue.handle("confirm")
	main.dialogue.visible = false
	main.router.pop(main.dialogue)
	Settings.v["text_size"] = 2
	main.say("Vespera", "If I cut the tether mid-leap, the span drops.", "C03")
	await _g_frames(60)
	await _g_shot("s4_dialogue_largest")
	main.dialogue.visible = false
	main.router.pop(main.dialogue)
	await _g_menu("main", {}, "s4_menu_largetext", func(m): m._items_menu())
	Settings.v["text_size"] = 0
	Settings.v["dialogue_opacity"] = 1.0
	Settings.v["colorblind"] = "deuteranopia"
	Game.bestiary_seen("E001", "seen")
	Game.bestiary_seen("E001", "affinity")
	await _g_menu("main", {}, "s4_bestiary_cues_deutan", func(m): m._bestiary())
	Settings.v["colorblind"] = "off"
	Settings.v["window_color"] = "contrast"
	await _g_menu("main", {}, "s4_theme_contrast", func(m): m._equip_menu("C01"))
	Settings.v["window_color"] = "dark"
	# fishing at the Saltwhistle pier (spot 4,24 faces the water to the left)
	main.enter_field("N14_R01", "world", Vector2i(4, 24), "left")
	main.field.banner_t = 0.0
	Settings.v["glyphs"] = "xbox"
	await _g_frames(6)
	main.open_fishing(main.field.fish_spot_here())
	var fg: FishingGame = main.fishing
	await _g_frames(4)
	fg.core._held = true
	fg.core.t = 0.5
	fg.core.power = 0.62
	await _g_shot("s4_fish_cast")
	fg.core.power = 0.62
	fg.core._cast()
	fg.core.wait_t = 99.0
	await _g_frames(10)
	await _g_shot("s4_fish_wait")
	fg.core.state = "reel"
	fg.core.line = 0.55
	fg.core.tension = 0.72
	fg.core.running = true
	fg.core.run_t = 99.0
	set_process_dummy(fg)
	await _g_frames(6)
	await _g_shot("s4_fish_reel")
	fg.core.state = "caught"
	fg.core.fish = FishCore.fish_def("F21")
	fg.core.size = 131.0
	fg.core.weight = FishCore.weight_of(fg.core.fish, 131.0)
	Game.set_flag("fishing_tournament_open")
	fg.result_msgs = FishingGame.record_catch(fg.core.fish, fg.core.size, fg.core.weight, "N14")
	fg.phase = "result"
	fg.queue_redraw()
	await _g_frames(6)
	await _g_shot("s4_fish_result")
	fg.handle("cancel")
	await _g_frames(4)
	# battle: auto-battle tab and an element cue
	Settings.v["auto_battle"] = "repeat"
	var bs = BattleScene.new()
	bs.main = main
	main.world.add_child(bs)
	main.field.visible = false
	bs.setup("D01_4", 1234, {})
	bs.auto_mode = "repeat"
	await _g_frames(60)
	bs._result_popup({"id": bs.model.enemy_ids[0], "kind": "damage", "amount": 412, "weak": true}, "fire", {})
	await _g_frames(10)
	await _g_shot("s4_battle_auto_cues")
	bs.queue_free()
	main.field.visible = true
	await _g_frames(2)
	Settings.v = keep_settings
	Game.save_root = Game.SAVE_DIR
	Achievements.path = "user://profile.json"
	Achievements._loaded = false

## Freeze the fishing overlay's simulation for a staged screenshot (drawing continues on request).
func set_process_dummy(fg: FishingGame) -> void:
	fg.phase = "play"
	fg.core.elapsed = 0.0
	fg.set_process(false)
	fg.queue_redraw()
