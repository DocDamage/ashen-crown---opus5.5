class_name WeatherFx
extends Node2D
## Visual weather over the field (rain, snow, ash, fog, sandstorm): particles from shaders/weather.gdshader and a
## drifting haze from shaders/haze.gdshader, both on ColorRects covering the view. Fades between kinds; time
## pauses with the field. Kind comes from FieldSys.weather_at (Settings "weather" turns it off).

const PRESETS := {
	"rain": {"mode": 0, "amount": 170.0, "color": Color(0.72, 0.78, 0.92, 0.55), "speed": 0.9, "extra": 0.5, "slant": 0.18,
		"near_len": 0.12, "far_len": 0.06, "haze": Color(0.55, 0.6, 0.7, 1.0), "density": 0.14, "drift": Vector2(0.05, 0.0)},
	"snow": {"mode": 1, "amount": 110.0, "color": Color(0.96, 0.97, 1.0, 0.9), "speed": 0.07, "extra": 0.08, "slant": 0.12,
		"near_len": 0.9, "far_len": 0.6, "haze": Color(0.88, 0.9, 0.96, 1.0), "density": 0.12, "drift": Vector2(0.02, 0.0)},
	"ash": {"mode": 1, "amount": 150.0, "color": Color(0.86, 0.8, 0.76, 0.95), "speed": 0.05, "extra": 0.06, "slant": -0.3,
		"near_len": 1.0, "far_len": 0.7, "haze": Color(0.46, 0.36, 0.32, 1.0), "density": 0.32, "drift": Vector2(-0.03, 0.0)},
	"fog": {"mode": -1, "haze": Color(0.84, 0.86, 0.9, 1.0), "density": 0.42, "drift": Vector2(0.025, 0.004)},
	"sandstorm": {"mode": 0, "amount": 240.0, "color": Color(0.96, 0.86, 0.64, 0.8), "speed": 1.6, "extra": 0.6, "slant": 1.0,
		"near_len": 0.1, "far_len": 0.05, "haze": Color(0.84, 0.7, 0.48, 1.0), "density": 0.6, "drift": Vector2(0.22, 0.01)},
}

var kind := ""
var level := 0.0           # 0..1 fade
var t := 0.0
var drops: ColorRect
var haze: ColorRect
var _want := ""

func _init() -> void:
	name = "WeatherFx"
	z_index = 1
	haze = ColorRect.new()
	haze.size = Vector2(320, 240)
	haze.color = Color(1, 1, 1, 0)
	haze.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var hm = ShaderMaterial.new()
	hm.shader = load("res://shaders/haze.gdshader")
	haze.material = hm
	add_child(haze)
	drops = ColorRect.new()
	drops.size = Vector2(320, 240)
	drops.color = Color(1, 1, 1, 0)
	drops.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var dm = ShaderMaterial.new()
	dm.shader = load("res://shaders/weather.gdshader")
	drops.material = dm
	add_child(drops)
	visible = false

## Sets the wanted kind ("" = clear); `snap` skips the fade (map loads).
func want(k: String, snap: bool = false) -> void:
	_want = k
	if snap:
		kind = k
		level = 1.0 if k != "" else 0.0
		_apply()

func tick(delta: float, running: bool) -> void:
	if running:
		t += delta
	if _want != kind:
		level = maxf(0.0, level - delta * 0.8)
		if level <= 0.0:
			kind = _want
	elif kind != "" and level < 1.0:
		level = minf(1.0, level + delta * 0.6)
	_apply()

func _apply() -> void:
	visible = kind != "" and level > 0.0
	if not visible:
		return
	var p: Dictionary = PRESETS.get(kind, {})
	if p.is_empty():
		visible = false
		return
	var hm: ShaderMaterial = haze.material
	hm.set_shader_parameter("haze_color", p["haze"])
	hm.set_shader_parameter("density", float(p["density"]) * level)
	hm.set_shader_parameter("drift", p["drift"])
	hm.set_shader_parameter("script_time", t)
	var m: int = int(p["mode"])
	drops.visible = m >= 0
	if m >= 0:
		var dm: ShaderMaterial = drops.material
		var c: Color = p["color"]
		c.a *= level
		dm.set_shader_parameter("mode", m)
		dm.set_shader_parameter("amount", float(p["amount"]))
		dm.set_shader_parameter("drop_color", c)
		dm.set_shader_parameter("base_speed", float(p["speed"]))
		dm.set_shader_parameter("extra_speed", float(p["extra"]))
		dm.set_shader_parameter("slant", float(p["slant"]))
		dm.set_shader_parameter("near_length", float(p["near_len"]))
		dm.set_shader_parameter("far_length", float(p["far_len"]))
		dm.set_shader_parameter("pixel_size", 3.0)
		dm.set_shader_parameter("use_script_time", true)
		dm.set_shader_parameter("script_time", t)
