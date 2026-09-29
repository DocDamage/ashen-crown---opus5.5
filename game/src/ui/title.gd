class_name TitleScreen
extends Control
## Title: New Game, Continue, Load, Settings, Credits, Quit. Continue names slot, chapter, location, playtime, date.

var main: Node
var menu: MenuList
var t = 0.0
var latest_slot = -1
var latest_info = {}
var sub: Control = null
var logo: Texture2D

func _ready() -> void:
	size = Vector2(320, 240)
	logo = Content.load_art("res://assets/ui/title.png")
	_build_scenery()
	_find_latest()
	menu = MenuList.new()
	menu.position = Vector2(112, 150)
	menu.size = Vector2(96, 76)
	menu.allow_cancel = false
	var cont_txt = "Continue"
	var items = [
		{"text": "New Game"},
		{"text": cont_txt, "enabled": latest_slot >= 0},
		{"text": "Load", "enabled": latest_slot >= 0},
		{"text": "Settings"},
		{"text": "Credits"},
		{"text": "Quit"},
	]
	menu.setup(items, 6)
	if latest_slot >= 0:
		menu.index = 1
	add_child(menu)
	menu.chosen.connect(_on_choice)

func _find_latest() -> void:
	var best = ""
	for s in range(1, Game.SLOTS + 1):
		var info: Dictionary = Game.slot_info(s)
		if info.get("ok", false) and str(info["date"]) > best:
			best = str(info["date"])
			latest_slot = s
			latest_info = info

func handle(ev: String) -> void:
	if sub != null:
		return
	menu.handle(ev)

func _on_choice(i: int, _it: Dictionary) -> void:
	match i:
		0:
			main.start_new_game()
		1:
			var r: Dictionary = Game.load_from(Game.slot_path(latest_slot))
			if r["ok"]:
				main.continue_from_state()
			else:
				main.toast("Could not load: " + str(r.get("reason", "")))
		2:
			await main.open_menu_async("load")
		3:
			await main.open_menu_async("settings")
		4:
			await main.roll_credits()
		5:
			get_tree().quit()

var ridge: PackedFloat32Array = PackedFloat32Array()
var ridge2: PackedFloat32Array = PackedFloat32Array()
var clouds: Array = []

func _build_scenery() -> void:
	# deterministic silhouettes: far ridge, near ridge with a ruined keep, and cloud banks
	ridge.resize(320)
	ridge2.resize(320)
	for x in range(320):
		ridge[x] = 176.0 - 10.0 * sin(x * 0.021 + 1.3) - 6.0 * sin(x * 0.057) - 3.0 * sin(x * 0.13 + 0.5)
		var h = 192.0 - 7.0 * sin(x * 0.034 + 0.2) - 4.0 * sin(x * 0.09 + 2.0)
		if x >= 232 and x < 262:
			h = minf(h, 150.0 if (x < 238 or x >= 256) else 162.0)
			if (x >= 232 and x < 238 and x % 3 == 0) or (x >= 256 and x < 262 and x % 3 == 1):
				h -= 3.0
		if x >= 246 and x < 249:
			h = minf(h, 140.0)
		ridge2[x] = h
	var rnd = RandomNumberGenerator.new()
	rnd.seed = 41
	for i in range(9):
		var parts = []
		var n = rnd.randi_range(3, 6)
		for k in range(n):
			parts.append(Rect2(k * rnd.randi_range(10, 16) - 8, -rnd.randi_range(0, 5) + (2 if k % 2 == 0 else 0), rnd.randi_range(24, 44), rnd.randi_range(4, 7)))
		clouds.append({"x": rnd.randf_range(0, 400), "y": rnd.randf_range(20, 130), "v": rnd.randf_range(2.0, 6.0), "parts": parts,
			"c": Color8(48 + i * 4, 30 + i * 2, 70 + i * 3, 150)})

func _process(delta: float) -> void:
	t += delta
	queue_redraw()

func _draw() -> void:
	# night sky: navy at the top warming to an ember glow at the horizon, in hard 16-bit bands
	var stops = [[0.0, Color8(4, 4, 16)], [0.35, Color8(14, 12, 44)], [0.6, Color8(44, 18, 58)], [0.78, Color8(110, 34, 44)], [0.86, Color8(196, 82, 44)], [1.0, Color8(40, 10, 16)]]
	for i in range(48):
		var f = i / 47.0
		var c: Color = stops[0][1]
		for k in range(stops.size() - 1):
			if f >= stops[k][0] and f <= stops[k + 1][0]:
				c = stops[k][1].lerp(stops[k + 1][1], (f - stops[k][0]) / (stops[k + 1][0] - stops[k][0]))
		draw_rect(Rect2(0, i * 5, 320, 5), c)
	# stars (upper sky), a few twinkling
	for i in range(46):
		var sx = fmod(i * 97.3, 320.0)
		var sy = fmod(i * 41.7, 100.0)
		var tw = 0.5 + 0.5 * sin(t * (1.0 + i % 4) + i)
		var a = 0.35 + 0.55 * tw if i % 3 == 0 else 0.5
		draw_rect(Rect2(round(sx), round(sy), 1, 1), Color(0.85, 0.85, 1.0, a))
	# drifting cloud banks
	for cl in clouds:
		var x = fmod(cl["x"] + t * cl["v"], 420.0) - 60.0
		for r in cl["parts"]:
			draw_rect(Rect2(round(x + r.position.x), round(cl["y"] + r.position.y), r.size.x, r.size.y), cl["c"])
			draw_rect(Rect2(round(x + r.position.x + 2), round(cl["y"] + r.position.y), r.size.x - 4, 1), Color(cl["c"].lightened(0.25), 0.6))
	# silhouettes
	for x in range(320):
		draw_rect(Rect2(x, ridge[x], 1, 240 - ridge[x]), Color8(30, 14, 34))
	for x in range(320):
		draw_rect(Rect2(x, ridge2[x], 1, 240 - ridge2[x]), Color8(10, 6, 14))
	# a lit window in the ruined keep
	if int(t * 2.0) % 7 != 0:
		draw_rect(Rect2(247, 156, 1, 2), Color8(250, 170, 80))
	# embers rising from the ash plain
	for i in range(40):
		var ex = fmod(i * 53.7 + t * (6 + i % 5) + sin(t + i) * 4.0, 320.0)
		var ey = 240.0 - fmod(i * 37.3 + t * (10 + i % 7), 240.0)
		var c2 = Color8(250, 120 + (i * 7) % 100, 50, 110 + (i * 13) % 130)
		draw_rect(Rect2(round(ex), round(ey), 1 if i % 4 else 2, 1), c2)
	if logo:
		draw_texture(logo, Vector2(round(160 - logo.get_width() / 2.0), 8))
	else:
		UI.text_center(self, 160, 60, "THE ASHEN CROWN", UI.C_GOLD)
	if latest_slot >= 0 and menu.index == 1:
		var s = "Slot %d  %s" % [latest_slot, latest_info["chapter"]]
		var s2 = "%s  %s  Lv%d  %s" % [latest_info["location"], Game.fmt_time(latest_info["playtime"]), latest_info["level"], str(latest_info["date"]).replace("T", " ").substr(0, 16)]
		UI.text_center(self, 160, 124, s, UI.C_TEXT)
		UI.text_center(self, 160, 135, s2, UI.C_LABEL)
	UI.text_right(self, 316, 229, "v0.1  original work", UI.C_DIM)
