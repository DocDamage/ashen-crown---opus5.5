extends Node
## Player settings persisted independently of save slots (docs/07 accessibility).

const PATH := "user://settings.json"
const ACTIONS := ["up", "down", "left", "right", "confirm", "cancel", "menu", "run", "page_l", "page_r", "skip"]
const DEFAULT_KEYS := {
	"up": [KEY_UP, KEY_W], "down": [KEY_DOWN, KEY_S], "left": [KEY_LEFT, KEY_A], "right": [KEY_RIGHT, KEY_D],
	"confirm": [KEY_Z, KEY_ENTER, KEY_SPACE], "cancel": [KEY_X, KEY_ESCAPE, KEY_BACKSPACE], "menu": [KEY_C, KEY_TAB],
	"run": [KEY_SHIFT], "page_l": [KEY_Q], "page_r": [KEY_E], "skip": [KEY_V],
}
const DEFAULT_PAD := {
	"up": [JOY_BUTTON_DPAD_UP], "down": [JOY_BUTTON_DPAD_DOWN], "left": [JOY_BUTTON_DPAD_LEFT], "right": [JOY_BUTTON_DPAD_RIGHT],
	"confirm": [JOY_BUTTON_A], "cancel": [JOY_BUTTON_B], "menu": [JOY_BUTTON_Y], "run": [JOY_BUTTON_X],
	"page_l": [JOY_BUTTON_LEFT_SHOULDER], "page_r": [JOY_BUTTON_RIGHT_SHOULDER], "skip": [JOY_BUTTON_BACK],
}

var v = {
	"text_speed": 2,          # 0 slow, 1 normal, 2 fast, 3 instant
	"run_toggle": false,
	"battle_mode": "wait",     # wait | active
	"battle_speed": 1.0,       # 0.75, 1.0, 1.25
	"reduced_flash": false,
	"shake": true,
	"short_summons": false,
	"vol_master": 0.8, "vol_music": 0.7, "vol_sfx": 0.8, "vol_ambience": 0.7, "vol_ui": 0.8,
	"encounters": "normal",    # normal | reduced | off
	"pause_on_focus_loss": true,
	"window_scale": 4,
	"fullscreen": false,
	"bindings": {},            # action -> [keycodes]
}

func _ready() -> void:
	load_settings()
	apply_bindings()
	apply_audio()

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
	if k.begins_with("vol_"):
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
		for bt in DEFAULT_PAD[a]:
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
	save_settings()
	apply_bindings()

func apply_audio() -> void:
	var buses = {"Master": "vol_master", "Music": "vol_music", "SFX": "vol_sfx", "Ambience": "vol_ambience", "UI": "vol_ui"}
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

func text_cps() -> float:
	return [30.0, 60.0, 120.0, 100000.0][clampi(int(v["text_speed"]), 0, 3)]
