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
	_find_latest()
	menu = MenuList.new()
	menu.position = Vector2(110, 148)
	menu.size = Vector2(100, 76)
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

func _process(delta: float) -> void:
	t += delta
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(0, 0, 320, 240), Color8(10, 8, 18))
	# ember drift
	for i in range(40):
		var x = fmod(i * 53.7 + t * (6 + i % 5), 320.0)
		var y = 240.0 - fmod(i * 37.3 + t * (10 + i % 7), 240.0)
		var c = Color8(240, 120 + (i * 7) % 90, 50, 150 + (i * 13) % 100)
		draw_rect(Rect2(round(x), round(y), 1, 1), c)
	if logo:
		draw_texture(logo, Vector2(160 - logo.get_width() / 2.0, 22))
	else:
		UI.text_center(self, 160, 60, "THE ASHEN CROWN", UI.C_GOLD)
	if latest_slot >= 0 and menu.index == 1:
		var s = "Slot %d  %s" % [latest_slot, latest_info["chapter"]]
		var s2 = "%s  %s  Lv%d  %s" % [latest_info["location"], Game.fmt_time(latest_info["playtime"]), latest_info["level"], str(latest_info["date"]).replace("T", " ").substr(0, 16)]
		UI.text_center(self, 160, 118, s, UI.C_TEXT)
		UI.text_center(self, 160, 130, s2, UI.C_DIM)
	UI.text_right(self, 316, 228, "v0.1  original work", UI.C_DIM)
