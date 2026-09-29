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
const GALLERY_FORMS := ["D01_4", "D03_2", "B01", "B05", "D07_2", "B08", "OW1_1", "D09_4", "B12", "D12_2"]


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
		var m = GameMenu.new()
		m.main = main
		main.ui.add_child(m)
		main.router.push(m)
		m.open("main", {})
		await _g_frames(10)
		await _g_shot("ui_menu")
		main.router.pop(m)
		m.queue_free()
	if which in ["battle", "all"]:
		for f in GALLERY_FORMS:
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

func _g_frames(n: int) -> void:
	for i in range(n):
		await get_tree().process_frame

func _g_shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	var img = get_viewport().get_texture().get_image()
	img.save_png("%s/%s.png" % [out_dir, name])
	print("GALLERY ", name)
