class_name UI
extends RefCounted
## Shared drawing helpers: pixel font text, window panels, gauges, colours.
## Look: 16-bit Square-style windows (docs/11 revision 2026-09-29) — vertical blue gradient fill, rounded
## bevelled silver border with a dark rim, white text with a dark drop shadow, pointing-hand cursor.
## Everything is drawn procedurally (no copied UI graphics).

const C_BG := Color8(18, 22, 40, 240)       # sentinel: "default themed window" for win()
const C_BG2 := Color8(28, 34, 60, 245)
const C_BORDER := Color8(232, 232, 244)
const C_BORDER_D := Color8(120, 128, 156)
const C_TEXT := Color8(248, 248, 248)
const C_DIM := Color8(138, 140, 160)
const C_HI := Color8(255, 232, 150)
const C_SEL := Color8(90, 110, 210, 120)
const C_RED := Color8(248, 104, 96)
const C_GREEN := Color8(128, 232, 128)
const C_BLUE := Color8(150, 196, 255)
const C_GOLD := Color8(248, 216, 112)
const C_LABEL := Color8(150, 190, 248)      # small stat labels: HP, MP, LV
const C_SHADOW := Color8(10, 10, 36, 230)
const C_RIM := Color8(12, 12, 28)
const LINE_H := 11

## Window colour themes: [top, bottom] of the vertical gradient. Chosen in Settings ("window_color").
const THEMES := {
	"blue": [Color8(86, 104, 222), Color8(12, 16, 84)],
	"ash": [Color8(116, 116, 136), Color8(22, 22, 32)],
	"crimson": [Color8(176, 70, 84), Color8(38, 8, 24)],
	"verdant": [Color8(62, 146, 116), Color8(8, 36, 34)],
	"violet": [Color8(132, 96, 206), Color8(26, 12, 62)],
}
const THEME_ORDER := ["blue", "ash", "crimson", "verdant", "violet"]

static var _font: Font
static var _hand: Texture2D

static func font() -> Font:
	if _font == null:
		_font = load("res://assets/fonts/ashen8.fnt")
	return _font

static func text(ci: CanvasItem, pos: Vector2, s: String, col: Color = C_TEXT, shadow: bool = true) -> void:
	var f = font()
	var p = Vector2(round(pos.x), round(pos.y) + 8)
	if shadow:
		# SNES-style hard shadow: right, below and diagonal, so thin strokes stay legible on the gradient
		var sc = Color(C_SHADOW, C_SHADOW.a * col.a)
		ci.draw_string(f, p + Vector2(1, 1), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, sc)
		ci.draw_string(f, p + Vector2(0, 1), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, sc)
		ci.draw_string(f, p + Vector2(1, 0), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, sc)
	ci.draw_string(f, p, s, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, col)

static func text_right(ci: CanvasItem, right_x: float, y: float, s: String, col: Color = C_TEXT) -> void:
	text(ci, Vector2(right_x - width(s), y), s, col)

static func text_center(ci: CanvasItem, cx: float, y: float, s: String, col: Color = C_TEXT) -> void:
	text(ci, Vector2(round(cx - width(s) / 2.0), y), s, col)

## Small pale-blue stat label (HP, MP, LV ...).
static func label(ci: CanvasItem, pos: Vector2, s: String) -> void:
	text(ci, pos, s, C_LABEL)

## Label at `pos` and a value right-aligned at `right_x` on the same line.
static func stat(ci: CanvasItem, pos: Vector2, lbl: String, value: String, right_x: float, col: Color = C_TEXT) -> void:
	label(ci, pos, lbl)
	text_right(ci, right_x, pos.y, value, col)

## Item icons (library build only: assets/ext/sprites/icons_11.png / icons_24.png, 32 per row, cell = item["icon"]).
static var _icons = {}

static func icon_tex(px: int) -> Texture2D:
	if not _icons.has(px):
		var path = "res://assets/ext/sprites/icons_%d.png" % px
		_icons[px] = load(path) if ResourceLoader.exists(path) else null
	return _icons[px]

## Draws an item's icon at `pos` (top-left). Returns false when no icon art is installed.
static func icon(ci: CanvasItem, pos: Vector2, iid: String, px: int = 11, dim: bool = false) -> bool:
	var t = icon_tex(px)
	if t == null or iid == "":
		return false
	var it: Dictionary = Content.item(iid)
	if not it.has("icon"):
		return false
	var i: int = int(it["icon"])
	ci.draw_texture_rect_region(t, Rect2(round(pos.x), round(pos.y), px, px), Rect2((i % 32) * px, (i / 32) * px, px, px),
		Color(1, 1, 1, 0.45) if dim else Color.WHITE)
	return true

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

static func theme() -> Array:
	var v = Settings.get_v("window_color")
	return THEMES[str(v)] if v != null and THEMES.has(str(v)) else THEMES["blue"]

## Themed window. `bg` other than C_BG tints the gradient toward that colour (alpha kept).
static func win(ci: CanvasItem, r: Rect2, bg: Color = C_BG) -> void:
	r = Rect2(r.position.round(), r.size.round())
	if r.size.x < 8 or r.size.y < 8:
		ci.draw_rect(r, C_RIM)
		return
	var top: Color
	var bot: Color
	var a = 1.0
	if bg == C_BG:
		var th = theme()
		top = th[0]
		bot = th[1]
	else:
		top = Color(bg.r, bg.g, bg.b).lightened(0.42)
		bot = Color(bg.r, bg.g, bg.b).darkened(0.35)
		a = maxf(bg.a, 0.8)
	# gradient fill in hard bands (16-bit look), inside the 3 px frame
	var inner = r.grow(-2)
	var h = int(inner.size.y)
	var bands = clampi(h / 3, 2, 40)
	var y0 = 0
	for i in range(bands):
		var y1 = int(round(float(h) * (i + 1) / bands))
		var c = top.lerp(bot, float(i) / maxf(1.0, bands - 1))
		c.a = a
		ci.draw_rect(Rect2(inner.position.x, inner.position.y + y0, inner.size.x, y1 - y0), c)
		y0 = y1
	_frame(ci, r)

static func _frame(ci: CanvasItem, r: Rect2) -> void:
	var x0 = r.position.x
	var y0 = r.position.y
	var x1 = r.end.x - 1
	var y1 = r.end.y - 1
	var w = r.size.x
	var h = r.size.y
	var hi = Color8(248, 248, 255)
	var lo = Color8(176, 182, 204)
	var mid = Color8(150, 158, 186)
	var sh = Color8(84, 90, 120)
	# dark outer rim, rounded (corner pixels left open)
	ci.draw_rect(Rect2(x0 + 2, y0, w - 4, 1), C_RIM)
	ci.draw_rect(Rect2(x0 + 2, y1, w - 4, 1), C_RIM)
	ci.draw_rect(Rect2(x0, y0 + 2, 1, h - 4), C_RIM)
	ci.draw_rect(Rect2(x1, y0 + 2, 1, h - 4), C_RIM)
	for c in [Vector2(x0 + 1, y0 + 1), Vector2(x1 - 1, y0 + 1), Vector2(x0 + 1, y1 - 1), Vector2(x1 - 1, y1 - 1)]:
		ci.draw_rect(Rect2(c, Vector2(1, 1)), C_RIM)
	# bright bevel: top/left light, bottom/right silver
	ci.draw_rect(Rect2(x0 + 2, y0 + 1, w - 4, 1), hi)
	ci.draw_rect(Rect2(x0 + 1, y0 + 2, 1, h - 4), hi)
	ci.draw_rect(Rect2(x0 + 2, y1 - 1, w - 4, 1), lo)
	ci.draw_rect(Rect2(x1 - 1, y0 + 2, 1, h - 4), lo)
	# inner groove: silver on top/left, shadow on bottom/right
	ci.draw_rect(Rect2(x0 + 2, y0 + 2, w - 4, 1), mid)
	ci.draw_rect(Rect2(x0 + 2, y0 + 3, 1, h - 5), mid)
	ci.draw_rect(Rect2(x0 + 3, y1 - 2, w - 5, 1), sh)
	ci.draw_rect(Rect2(x1 - 2, y0 + 3, 1, h - 6), sh)

## Recessed inset (portrait frames, map panes): dark well with a 1 px bevel.
static func inset(ci: CanvasItem, r: Rect2, fill: Color = Color8(8, 10, 30)) -> void:
	r = Rect2(r.position.round(), r.size.round())
	ci.draw_rect(r, fill)
	ci.draw_rect(Rect2(r.position, Vector2(r.size.x, 1)), Color8(6, 6, 20))
	ci.draw_rect(Rect2(r.position, Vector2(1, r.size.y)), Color8(6, 6, 20))
	ci.draw_rect(Rect2(r.position.x, r.end.y - 1, r.size.x, 1), Color8(170, 178, 204))
	ci.draw_rect(Rect2(r.end.x - 1, r.position.y, 1, r.size.y), Color8(170, 178, 204))

static func gauge(ci: CanvasItem, r: Rect2, frac: float, col: Color, back: Color = Color8(20, 20, 26)) -> void:
	r = Rect2(r.position.round(), r.size.round())
	if r.size.y <= 2:
		ci.draw_rect(r, back)
		var ww = int(round(clampf(frac, 0.0, 1.0) * r.size.x))
		if ww > 0:
			ci.draw_rect(Rect2(r.position, Vector2(ww, r.size.y)), col)
		return
	ci.draw_rect(r, C_RIM)
	var inner = r.grow(-1)
	ci.draw_rect(inner, Color8(34, 36, 70) if back == Color8(20, 20, 26) else back)
	var w = int(round(clampf(frac, 0.0, 1.0) * inner.size.x))
	if w > 0:
		ci.draw_rect(Rect2(inner.position, Vector2(w, inner.size.y)), col)
		ci.draw_rect(Rect2(inner.position, Vector2(w, 1)), col.lightened(0.45))
		if inner.size.y >= 3:
			ci.draw_rect(Rect2(inner.position + Vector2(0, inner.size.y - 1), Vector2(w, 1)), col.darkened(0.3))

const HAND := [
	"....KKKKK......",
	"KKKKWWWWWKKKKK.",
	"KWKWWWWWWWWWWWK",
	"KWKWWWWSKKKKKK.",
	"KWKWWWWWWWK....",
	"KWKWWWWSKK.....",
	"KWKWWWWWWWK....",
	"KWKSWWWSKK.....",
	"KKKKSSSKK......",
	"...KKKK........",
]

static func hand_tex() -> Texture2D:
	if _hand == null:
		var img = Image.create(15, 10, false, Image.FORMAT_RGBA8)
		var pal = {"K": Color8(20, 20, 40), "W": Color8(250, 250, 250), "S": Color8(166, 174, 204)}
		for y in range(HAND.size()):
			var row: String = HAND[y]
			for x in range(row.length()):
				var ch = row[x]
				img.set_pixel(x, y, pal[ch] if pal.has(ch) else Color(0, 0, 0, 0))
		_hand = ImageTexture.create_from_image(img)
	return _hand

## Pointing-hand cursor. `pos` is where a text glyph would start; the fingertip lands at pos + (5, 4).
## `ghost` draws a static, dimmed hand (the remembered choice of a menu that lost focus).
static func cursor(ci: CanvasItem, pos: Vector2, blink: bool = true, ghost: bool = false) -> void:
	var off = 0
	if blink and not ghost:
		off = 1 if (Time.get_ticks_msec() / 200) % 2 == 0 else 0
	var p = Vector2(round(pos.x) - 9 + off, round(pos.y) + 2)
	ci.draw_texture(hand_tex(), p, Color(1, 1, 1, 0.55) if ghost else Color.WHITE)

## Small bobbing "more" triangle (dialogue advance, scroll hints). dir: 1 down, -1 up.
static func arrow(ci: CanvasItem, pos: Vector2, dir: int = 1, bob: bool = true) -> void:
	var b = 1 if bob and (Time.get_ticks_msec() / 250) % 2 == 0 else 0
	var p = pos.round() + Vector2(0, b * dir)
	for i in range(4):
		var yy = p.y + (i if dir > 0 else 3 - i)
		ci.draw_rect(Rect2(p.x + i + 1, yy + 1, 7 - i * 2, 1), C_SHADOW)
		ci.draw_rect(Rect2(p.x + i, yy, 7 - i * 2, 1), C_TEXT)

static func elem_label(e: String) -> String:
	return {"fire": "Fire", "ice": "Ice", "storm": "Storm", "earth": "Earth", "water": "Water", "light": "Light",
		"shadow": "Shadow", "physical": "Phys", "none": "-"}.get(e, e)

static func elem_color(e: String) -> Color:
	return {"fire": Color8(250, 120, 60), "ice": Color8(140, 210, 250), "storm": Color8(240, 230, 110), "earth": Color8(190, 150, 90),
		"water": Color8(80, 150, 240), "light": Color8(255, 245, 200), "shadow": Color8(170, 110, 220), "physical": C_TEXT}.get(e, C_TEXT)
