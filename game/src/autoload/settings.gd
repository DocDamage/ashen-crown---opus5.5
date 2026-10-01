extends Node
## Player settings persisted independently of save slots (docs/07 accessibility).

const PATH := "user://settings.json"
const ACTIONS := ["up", "down", "left", "right", "confirm", "cancel", "menu", "run", "page_l", "page_r", "skip", "map"]
const DEFAULT_KEYS := {
	"up": [KEY_UP, KEY_W], "down": [KEY_DOWN, KEY_S], "left": [KEY_LEFT, KEY_A], "right": [KEY_RIGHT, KEY_D],
	"confirm": [KEY_Z, KEY_ENTER, KEY_SPACE], "cancel": [KEY_X, KEY_ESCAPE, KEY_BACKSPACE], "menu": [KEY_C, KEY_TAB],
	"run": [KEY_SHIFT], "page_l": [KEY_Q], "page_r": [KEY_E], "skip": [KEY_V], "map": [KEY_M],
}
const DEFAULT_PAD := {
	"up": [JOY_BUTTON_DPAD_UP], "down": [JOY_BUTTON_DPAD_DOWN], "left": [JOY_BUTTON_DPAD_LEFT], "right": [JOY_BUTTON_DPAD_RIGHT],
	"confirm": [JOY_BUTTON_A], "cancel": [JOY_BUTTON_B], "menu": [JOY_BUTTON_Y, JOY_BUTTON_START], "run": [JOY_BUTTON_X],
	"page_l": [JOY_BUTTON_LEFT_SHOULDER], "page_r": [JOY_BUTTON_RIGHT_SHOULDER], "skip": [JOY_BUTTON_BACK],
	"map": [JOY_BUTTON_LEFT_STICK, JOY_BUTTON_BACK],
}
## Steam Deck / pad-friendly defaults (sys s4): every action sits on a face, shoulder or system button (Menu = Y or
## Start; Map = L3 or View, which is also Skip - skip only acts in scenes and the map only outside them).
const WINDOW_SIZES := ["960x720", "1280x800", "1280x720", "1440x1080", "1920x1080"]

var v = {
	"text_speed": 2,          # 0 slow, 1 normal, 2 fast, 3 instant
	"run_toggle": false,
	"ride_mount": true,        # ride the Brackhorn on the world map once the party has it
	"world_view": "mode7",     # mode7 (tilted world map) | flat (top-down, for motion comfort)
	"minimap": true,           # world-map minimap (top right)
	"hd2d": true,              # towns, dungeons and interiors in HD-2D (3D ground, Phantom Camera); false = flat 2D
	"hd2d_dof": true,          # HD-2D tilt-shift depth of field
	"battle_camera": true,     # HD-2D battles: the camera pushes in on attacks
	"weather": true,           # visual weather (rain, snow, ash, fog, sandstorm) on the world and outdoor maps
	"battle_mode": "wait",     # wait | active
	"battle_speed": 1.0,       # 0.75, 1.0, 1.25
	"reduced_flash": false,
	"shake": true,
	"short_summons": false,
	"vol_master": 0.8, "vol_music": 0.7, "vol_sfx": 0.8, "vol_ambience": 0.7, "vol_ui": 0.8,
	"encounters": "normal",    # normal | reduced | off
	"pause_on_focus_loss": true,
	"window_scale": 4,
	"window_color": "dark",   # UI window gradient theme (UI.THEMES); new settings files start dark, old files keep theirs
	"fullscreen": false,
	"mature": false,           # Mature content (nudity uncovered); off by default
	"mature_ok": false,        # one-time 18+ confirmation given
	"difficulty_default": "normal",   # difficulty for new games (each save keeps its own)
	"bindings": {},            # action -> [keycodes]
	# ---- sys s4: saves, accessibility, input, dialogue audio (all optional; defaults keep the old behaviour)
	"autosave": true,          # autosave slot on town/world arrivals and after boss wins
	"text_size": 0,            # 0 standard, 1 large (dialogue + menu lists), 2 largest (dialogue)
	"dialogue_opacity": 1.0,   # dialogue window fill opacity
	"colorblind": "off",       # off | deuteranopia | protanopia | tritanopia (UI highlight palette)
	"shape_cues": true,        # element/status shapes and letters next to colours
	"high_contrast": false,    # brighter secondary text (the "contrast" window theme turns it on too)
	"auto_battle": "off",      # off | attack | repeat (repeat each hero's last command, else Attack)
	"hold_confirm": false,     # holding Confirm repeats it (text, menus) instead of tapping
	"auto_text": 0,            # 0 off, 1 slow, 2 normal, 3 fast: dialogue pages advance by themselves
	"captions": false,         # "[bell tolls]" captions for key sound cues
	"mono": false,             # fold stereo to mono
	"encounter_rate": 1.0,     # random-encounter rate multiplier (on top of "encounters")
	"glyphs": "auto",          # auto | keyboard | xbox | playstation | deck
	"window_size": "960x720",  # windowed size (the 4:3 view letterboxes inside it)
	"blips": true,             # dialogue voice blips
	"vol_voice": 0.7,
	"pad_bindings": {},        # action -> [joypad buttons]
	"reel_toggle": false,      # fishing: press to start / stop reeling instead of holding
	"fish_assist": false,      # fishing: wider bite window, slower line tension (always on with Easy)
}
var last_device = "keyboard"
var pad_name = ""

func _ready() -> void:
	load_settings()
	apply_bindings()
	apply_audio()

func _input(event: InputEvent) -> void:
	if event is InputEventJoypadButton or (event is InputEventJoypadMotion and absf(event.axis_value) > 0.5):
		if last_device != "pad":
			last_device = "pad"
			pad_name = Input.get_joy_name(event.device)
	elif event is InputEventKey and event.pressed:
		last_device = "keyboard"

func pad_for(action: String) -> Array:
	var b: Dictionary = v.get("pad_bindings", {})
	if b.has(action):
		return b[action]
	return DEFAULT_PAD.get(action, [])

func rebind_pad(action: String, button: int) -> void:
	var b: Dictionary = v.get("pad_bindings", {}).duplicate()
	b[action] = [button]
	v["pad_bindings"] = b
	save_settings()
	apply_bindings()

## Windowed size from "window_size" (e.g. 1280x800 for the Steam Deck); the 960x720 view keeps 4:3 and letterboxes.
func apply_window() -> void:
	if DisplayServer.get_name() == "headless":
		return
	var w = get_tree().root.get_window() if get_tree() != null else null
	if w == null or v.get("fullscreen", false):
		return
	var parts = str(v.get("window_size", "960x720")).split("x")
	if parts.size() == 2:
		var sz = Vector2i(int(parts[0]), int(parts[1]))
		if sz.x >= 640 and sz.y >= 480:
			w.mode = Window.MODE_WINDOWED
			w.size = sz
			var scr = DisplayServer.window_get_current_screen()
			var ss = DisplayServer.screen_get_size(scr)
			w.position = DisplayServer.screen_get_position(scr) + (ss - sz) / 2

func load_settings() -> void:
	if not FileAccess.file_exists(PATH):
		return
	var f = FileAccess.open(PATH, FileAccess.READ)
	var d = JSON.parse_string(f.get_as_text())
	if typeof(d) == TYPE_DICTIONARY:
		for k in d:
			if v.has(k):
				v[k] = d[k]

func save_settings() -> void:
	var f = FileAccess.open(PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(v, "\t"))

func get_v(k: String):
	return v.get(k)

func set_v(k: String, val) -> void:
	v[k] = val
	save_settings()
	if k.begins_with("vol_") or k == "mono":
		apply_audio()

func keys_for(action: String) -> Array:
	var b: Dictionary = v.get("bindings", {})
	if b.has(action):
		return b[action]
	return DEFAULT_KEYS[action]

func apply_bindings() -> void:
	for a in ACTIONS:
		var act = "g_" + a
		if not InputMap.has_action(act):
			InputMap.add_action(act, 0.4)
		InputMap.action_erase_events(act)
		for k in keys_for(a):
			var ev = InputEventKey.new()
			ev.physical_keycode = int(k)
			InputMap.action_add_event(act, ev)
		for bt in pad_for(a):
			var jb = InputEventJoypadButton.new()
			jb.button_index = bt
			InputMap.action_add_event(act, jb)
	# analog stick directions
	var axes = {"up": [JOY_AXIS_LEFT_Y, -1.0], "down": [JOY_AXIS_LEFT_Y, 1.0], "left": [JOY_AXIS_LEFT_X, -1.0], "right": [JOY_AXIS_LEFT_X, 1.0]}
	for a in axes:
		var jm = InputEventJoypadMotion.new()
		jm.axis = axes[a][0]
		jm.axis_value = axes[a][1]
		InputMap.action_add_event("g_" + a, jm)

func rebind(action: String, keycode: int) -> void:
	var b: Dictionary = v.get("bindings", {}).duplicate()
	b[action] = [keycode]
	v["bindings"] = b
	save_settings()
	apply_bindings()

func reset_bindings() -> void:
	v["bindings"] = {}
	v["pad_bindings"] = {}
	save_settings()
	apply_bindings()

func apply_audio() -> void:
	var buses = {"Master": "vol_master", "Music": "vol_music", "SFX": "vol_sfx", "Ambience": "vol_ambience", "UI": "vol_ui", "Voice": "vol_voice"}
	for bname in buses:
		var idx = AudioServer.get_bus_index(bname)
		if idx < 0 and bname != "Master":
			AudioServer.add_bus()
			idx = AudioServer.bus_count - 1
			AudioServer.set_bus_name(idx, bname)
			AudioServer.set_bus_send(idx, "Master")
		var vol: float = float(v[buses[bname]])
		AudioServer.set_bus_mute(idx, vol <= 0.001)
		AudioServer.set_bus_volume_db(idx, linear_to_db(maxf(vol, 0.0001)))
	# mono: a stereo enhancer with pan pull-out 0 folds both channels together on the master bus
	var mi = AudioServer.get_bus_index("Master")
	var have = -1
	for i in range(AudioServer.get_bus_effect_count(mi)):
		if AudioServer.get_bus_effect(mi, i) is AudioEffectStereoEnhance:
			have = i
	if bool(v.get("mono", false)) and have < 0:
		var fx = AudioEffectStereoEnhance.new()
		fx.pan_pullout = 0.0
		AudioServer.add_bus_effect(mi, fx)
	elif not bool(v.get("mono", false)) and have >= 0:
		AudioServer.remove_bus_effect(mi, have)

func text_cps() -> float:
	return [30.0, 60.0, 120.0, 100000.0][clampi(int(v["text_speed"]), 0, 3)]
