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
			var full = Image.create(maxi(mw, 320), maxi(mh, 240), false, Image.FORMAT_RGBA8)
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
					full.blit_rect(img, Rect2i(0, 0, 320, 240), Vector2i(ox, oy))
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
		main.say("Tessa", "The quarry bell rang twice at dawn. That only happens when the lower gate floods.", "C02")
		await _g_frames(40)
		await _g_shot("ui_dialogue")
		main.dialogue.visible = false
		main.router.pop(main.dialogue)
		await _g_ui_screens()
	if which in ["battle", "all"]:
		for cid in ["C02", "C03", "C04"]:
			if Content.data["characters"].has(cid):
				Game.recruit(cid)
		for f in GALLERY_FORMS:
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
	await _g_menu("inn", {"price": 20}, "ui_inn")
	var old_theme = Settings.v.get("window_color", "blue")
	Settings.v["window_color"] = "crimson"
	await _g_menu("main", {}, "ui_menu_theme_crimson")
	Settings.v["window_color"] = old_theme
	# dialogue with a choice
	main.say("Tessa", "Do we take the flooded gate, or wait for the pumps?", "C02")
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

func _g_frames(n: int) -> void:
	for i in range(n):
		await get_tree().process_frame

func _g_shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	var img = get_viewport().get_texture().get_image()
	img.save_png("%s/%s.png" % [out_dir, name])
	print("GALLERY ", name)
