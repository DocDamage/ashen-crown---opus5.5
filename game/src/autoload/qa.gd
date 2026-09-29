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
