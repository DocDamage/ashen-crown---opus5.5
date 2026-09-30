class_name StillView
extends Control
## Full-screen cutscene still (res://assets/stills/<id>.png, 4:3). Fades in; confirm or cancel closes it, or it
## closes by itself after `hold` seconds when hold > 0. Missing images are skipped by the caller (see exists()).

signal closed
var tex: Texture2D
var t = 0.0
var hold = 0.0
var done = false

static func path(id: String) -> String:
	return "res://assets/stills/%s.png" % id

static func exists(id: String) -> bool:
	return ResourceLoader.exists(path(id))

func setup(id: String, p_hold: float) -> void:
	size = Vector2(320, 240)
	tex = load(path(id))
	hold = p_hold

func handle(ev: String) -> void:
	if (ev == "confirm" or ev == "cancel") and t > 0.4:
		_close()

func _close() -> void:
	if not done:
		done = true
		emit_signal("closed")

func _process(d: float) -> void:
	t += d
	if hold > 0.0 and t >= hold:
		_close()
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(0, 0, 320, 240), Color.BLACK)
	if tex == null:
		return
	var a = clampf(t / 0.6, 0.0, 1.0)
	var ts = tex.get_size()
	var k = minf(320.0 / ts.x, 240.0 / ts.y)
	var sz = ts * k
	draw_texture_rect(tex, Rect2((Vector2(320, 240) - sz) / 2.0, sz), false, Color(1, 1, 1, a))
