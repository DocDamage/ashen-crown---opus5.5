class_name UI
extends RefCounted
## Shared drawing helpers: pixel font text, window panels, gauges, colours.

const C_BG := Color8(18, 22, 40, 240)
const C_BG2 := Color8(28, 34, 60, 245)
const C_BORDER := Color8(184, 154, 90)
const C_BORDER_D := Color8(92, 72, 40)
const C_TEXT := Color8(240, 236, 223)
const C_DIM := Color8(128, 128, 140)
const C_HI := Color8(255, 226, 140)
const C_SEL := Color8(70, 84, 140, 255)
const C_RED := Color8(232, 88, 80)
const C_GREEN := Color8(120, 216, 120)
const C_BLUE := Color8(120, 170, 250)
const C_GOLD := Color8(240, 200, 90)
const C_SHADOW := Color8(0, 0, 0, 200)
const LINE_H := 11

static var _font: Font

static func font() -> Font:
	if _font == null:
		_font = load("res://assets/fonts/ashen8.fnt")
	return _font

static func text(ci: CanvasItem, pos: Vector2, s: String, col: Color = C_TEXT, shadow: bool = true) -> void:
	var f = font()
	var p = Vector2(round(pos.x), round(pos.y) + 8)
	if shadow:
		ci.draw_string(f, p + Vector2(1, 1), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, C_SHADOW)
	ci.draw_string(f, p, s, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, col)

static func text_right(ci: CanvasItem, right_x: float, y: float, s: String, col: Color = C_TEXT) -> void:
	text(ci, Vector2(right_x - width(s), y), s, col)

static func text_center(ci: CanvasItem, cx: float, y: float, s: String, col: Color = C_TEXT) -> void:
	text(ci, Vector2(round(cx - width(s) / 2.0), y), s, col)

static func width(s: String) -> float:
	return font().get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x

static func wrap(s: String, max_w: float) -> Array:
	var out = []
	for para in s.split("\n"):
		var line = ""
		for w in para.split(" "):
			var trial = w if line == "" else line + " " + w
			if width(trial) > max_w and line != "":
				out.append(line)
				line = w
			else:
				line = trial
		out.append(line)
	return out

static func win(ci: CanvasItem, r: Rect2, bg: Color = C_BG) -> void:
	r = Rect2(r.position.round(), r.size.round())
	ci.draw_rect(r, bg)
	# double border: outer dark, inner gold, with notched corners
	ci.draw_rect(Rect2(r.position, Vector2(r.size.x, 1)), C_BORDER)
	ci.draw_rect(Rect2(r.position + Vector2(0, r.size.y - 1), Vector2(r.size.x, 1)), C_BORDER)
	ci.draw_rect(Rect2(r.position, Vector2(1, r.size.y)), C_BORDER)
	ci.draw_rect(Rect2(r.position + Vector2(r.size.x - 1, 0), Vector2(1, r.size.y)), C_BORDER)
	ci.draw_rect(Rect2(r.position + Vector2(2, 2), Vector2(r.size.x - 4, 1)), C_BORDER_D)
	ci.draw_rect(Rect2(r.position + Vector2(2, 2), Vector2(1, r.size.y - 4)), C_BORDER_D)
	for c in [r.position, r.position + Vector2(r.size.x - 1, 0), r.position + Vector2(0, r.size.y - 1), r.end - Vector2(1, 1)]:
		ci.draw_rect(Rect2(c, Vector2(1, 1)), Color(0, 0, 0, 0.9))

static func gauge(ci: CanvasItem, r: Rect2, frac: float, col: Color, back: Color = Color8(20, 20, 26)) -> void:
	ci.draw_rect(r, back)
	var w = int(round(clampf(frac, 0.0, 1.0) * (r.size.x - 2)))
	if w > 0:
		ci.draw_rect(Rect2(r.position + Vector2(1, 1), Vector2(w, r.size.y - 2)), col)
		ci.draw_rect(Rect2(r.position + Vector2(1, 1), Vector2(w, 1)), col.lightened(0.35))

static func cursor(ci: CanvasItem, pos: Vector2, blink: bool = true) -> void:
	var t = Time.get_ticks_msec() / 250
	var off = 1 if (blink and t % 2 == 0) else 0
	text(ci, pos + Vector2(off, 0), "▶", C_HI)

static func elem_label(e: String) -> String:
	return {"fire": "Fire", "ice": "Ice", "storm": "Storm", "earth": "Earth", "water": "Water", "light": "Light",
		"shadow": "Shadow", "physical": "Phys", "none": "-"}.get(e, e)

static func elem_color(e: String) -> Color:
	return {"fire": Color8(250, 120, 60), "ice": Color8(140, 210, 250), "storm": Color8(240, 230, 110), "earth": Color8(190, 150, 90),
		"water": Color8(80, 150, 240), "light": Color8(255, 245, 200), "shadow": Color8(170, 110, 220), "physical": C_TEXT}.get(e, C_TEXT)
