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
	"dark": [Color8(44, 50, 96), Color8(6, 7, 26)],
	"blue": [Color8(86, 104, 222), Color8(12, 16, 84)],
	"ash": [Color8(116, 116, 136), Color8(22, 22, 32)],
	"crimson": [Color8(176, 70, 84), Color8(38, 8, 24)],
	"verdant": [Color8(62, 146, 116), Color8(8, 36, 34)],
	"violet": [Color8(132, 96, 206), Color8(26, 12, 62)],
	"contrast": [Color8(0, 0, 0), Color8(0, 0, 0)],
}
const THEME_ORDER := ["dark", "blue", "ash", "crimson", "verdant", "violet", "contrast"]

static var _font: Font
static var _hand: Texture2D

## 960x720 rendering: UI layouts stay in 320x240 "units"; every UI layer is scaled by U. Text and window frames are
## drawn at native resolution (transform 1/U) so they stay crisp; FONT_PX is the native pixel size of the UI font
## (Pixelated Elegance, GGBotNet CC0, designed on an 8px grid, drawn at 3x its grid).
const U := 3
const FONT_PX := 24
const INV := Vector2(1.0 / U, 1.0 / U)

static func font() -> Font:
	if _font == null:
		var f: FontFile = load("res://assets/fonts/pixelated_elegance.ttf")
		f.antialiasing = TextServer.FONT_ANTIALIASING_NONE
		f.hinting = TextServer.HINTING_NONE
		f.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
		f.multichannel_signed_distance_field = false
		var fb = load("res://assets/fonts/ashen8.fnt")
		if fb != null:
			f.fallbacks = [fb]
		_font = f
	return _font

## Native-resolution drawing inside a unit-scaled layer: sets the item's draw transform so that native pixels map
## 1:1 to the screen from `origin` (in units). Call native_end() afterwards.
## `base` (normally identity) is composed in front: the Mode-7 world map sets it per sprite so that the regular
## drawing code comes out scaled by depth around the sprite's foot.
static var base := Transform2D.IDENTITY

static func native_begin(ci: CanvasItem, origin: Vector2) -> void:
	ci.draw_set_transform_matrix(base * Transform2D(0.0, INV, 0.0, origin))

static func native_end(ci: CanvasItem) -> void:
	ci.draw_set_transform_matrix(base)

static func text(ci: CanvasItem, pos: Vector2, s: String, col: Color = C_TEXT, shadow: bool = true) -> void:
	var f = font()
	col = pal(col)
	native_begin(ci, Vector2(round(pos.x * U) / U, round(pos.y * U) / U))
	var p = Vector2(0, f.get_ascent(px) + 3)
	if shadow:
		# SNES-style hard shadow (right, below, diagonal) so thin strokes stay legible on the gradient
		var sc = Color(C_SHADOW, C_SHADOW.a * col.a)
		ci.draw_string(f, p + Vector2(3, 3), s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, sc)
		ci.draw_string(f, p + Vector2(0, 3), s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, sc)
		ci.draw_string(f, p + Vector2(3, 0), s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, sc)
	ci.draw_string(f, p, s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
	native_end(ci)

static func text_right(ci: CanvasItem, right_x: float, y: float, s: String, col: Color = C_TEXT) -> void:
	text(ci, Vector2(right_x - width(s), y), s, col)

static func text_center(ci: CanvasItem, cx: float, y: float, s: String, col: Color = C_TEXT) -> void:
	text(ci, Vector2(cx - width(s) / 2.0, y), s, col)

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
	if it.has("icon_fish") and FishingGame.tex("icons") != null:
		# sys s4: fishing items use the Fishing Gear pack's icon sheet
		FishingGame.draw_icon(ci, pos.round(), int(it["icon_fish"]), px / 16.0)
		return true
	if not it.has("icon"):
		return false
	var i: int = int(it["icon"])
	if (i / 32 + 1) * px > t.get_height():
		return false   # cell beyond the installed atlas (run tools/art/icons_gear2.py)
	ci.draw_texture_rect_region(t, Rect2(round(pos.x), round(pos.y), px, px), Rect2((i % 32) * px, (i / 32) * px, px, px),
		Color(1, 1, 1, 0.45) if dim else Color.WHITE)
	return true

## Spell icons (owner's spell icon pack, one per ability): assets/ext/sprites/spell_icons_32.png + spell_icons.json.
static var _sp_meta = null
static var _sp_tex: Texture2D = null

static func spell_icon(ci: CanvasItem, pos: Vector2, aid: String, dim: bool = false) -> bool:
	if _sp_meta == null:
		var jp = "res://assets/ext/sprites/spell_icons.json"
		_sp_meta = JSON.parse_string(FileAccess.get_file_as_string(jp)) if FileAccess.file_exists(jp) else {}
		var tp = "res://assets/ext/sprites/spell_icons_32.png"
		_sp_tex = load(tp) if ResourceLoader.exists(tp) else null
	if _sp_tex == null or not _sp_meta.get("index", {}).has(aid):
		return false
	var i = int(_sp_meta["index"][aid])
	var c = int(_sp_meta["cols"])
	native_begin(ci, (pos * U).round() / U)
	ci.draw_texture_rect_region(_sp_tex, Rect2(0, -1, 32, 32), Rect2((i % c) * 32, (i / c) * 32, 32, 32), Color(1, 1, 1, 0.45) if dim else Color.WHITE)
	native_end(ci)
	return true

static func width(s: String) -> float:
	return font().get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x / U

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
	return THEMES[str(v)] if v != null and THEMES.has(str(v)) else THEMES["dark"]

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
		a = win_alpha
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
	# drawn at native resolution: 2px dark rim, 2px bright bevel, 1px silver groove, 2px inner shadow
	native_begin(ci, r.position)
	var w = r.size.x * U
	var h = r.size.y * U
	var hi = Color8(248, 248, 255)
	var lo = Color8(176, 182, 204)
	var mid = Color8(150, 158, 186)
	var sh = Color8(84, 90, 120)
	var c = 4    # rounded corner inset
	ci.draw_rect(Rect2(c, 0, w - c * 2, 2), C_RIM)
	ci.draw_rect(Rect2(c, h - 2, w - c * 2, 2), C_RIM)
	ci.draw_rect(Rect2(0, c, 2, h - c * 2), C_RIM)
	ci.draw_rect(Rect2(w - 2, c, 2, h - c * 2), C_RIM)
	for p in [Vector2(2, 2), Vector2(w - 4, 2), Vector2(2, h - 4), Vector2(w - 4, h - 4)]:
		ci.draw_rect(Rect2(p, Vector2(2, 2)), C_RIM)
	ci.draw_rect(Rect2(c, 2, w - c * 2, 2), hi)
	ci.draw_rect(Rect2(2, c, 2, h - c * 2), hi)
	ci.draw_rect(Rect2(c, h - 4, w - c * 2, 2), lo)
	ci.draw_rect(Rect2(w - 4, c, 2, h - c * 2), lo)
	ci.draw_rect(Rect2(4, 4, w - 8, 1), mid)
	ci.draw_rect(Rect2(4, 5, 1, h - 9), mid)
	ci.draw_rect(Rect2(5, h - 6, w - 10, 2), sh)
	ci.draw_rect(Rect2(w - 6, 5, 2, h - 10), sh)
	native_end(ci)

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
	col = pal(col)
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

# ======================================================================
# Accessibility: text size, window opacity, colour-blind palettes, high contrast, shape cues (sys s4)
# ======================================================================
## Native font pixel size used by text()/width(). 24 = the standard 3x grid; 32 (4x) and 40 (5x) stay pixel-crisp.
## Widgets that honour the "text_size" setting set it around their drawing with push_px()/pop_px().
static var px := FONT_PX
static var _px_stack: Array = []
## Themed-window fill opacity (the dialogue box sets it from the "dialogue_opacity" setting while it draws).
static var win_alpha := 1.0

static func push_px(p: int) -> void:
	_px_stack.append(px)
	px = p

static func pop_px() -> void:
	px = _px_stack.pop_back() if not _px_stack.is_empty() else FONT_PX

## Font size for a text surface: "dialogue" (dialogue, toasts, documents) or "list" (menu lists).
static func size_px(surface: String) -> int:
	var st = clampi(int(Settings.get_v("text_size") if Settings.get_v("text_size") != null else 0), 0, 2)
	if surface == "list":
		return [24, 32, 32][st]
	return [24, 32, 40][st]

## Line height (units) for the current px.
static func line_h() -> int:
	return int(ceil(px * 11.0 / FONT_PX))

## Colour-blind-safe highlight palettes (Okabe-Ito based). The UI's semantic colours are remapped at draw time.
const PALETTES := {
	"deuteranopia": {"green": Color8(86, 180, 233), "red": Color8(230, 159, 0), "hi": Color8(255, 240, 120), "gold": Color8(240, 228, 66)},
	"protanopia": {"green": Color8(0, 158, 255), "red": Color8(255, 176, 0), "hi": Color8(255, 244, 140), "gold": Color8(240, 228, 66)},
	"tritanopia": {"green": Color8(0, 200, 170), "red": Color8(240, 70, 110), "hi": Color8(255, 190, 220), "gold": Color8(250, 150, 190)},
}
const PALETTE_ORDER := ["off", "deuteranopia", "protanopia", "tritanopia"]

static func high_contrast() -> bool:
	return str(Settings.get_v("window_color")) == "contrast" or bool(Settings.get_v("high_contrast"))

static func pal(c: Color) -> Color:
	var p = str(Settings.get_v("colorblind")) if Settings.get_v("colorblind") != null else "off"
	if p != "off" and PALETTES.has(p):
		var t: Dictionary = PALETTES[p]
		if c == C_GREEN:
			return t["green"]
		if c == C_RED:
			return t["red"]
		if c == C_HI:
			return t["hi"]
		if c == C_GOLD:
			return t["gold"]
	if high_contrast():
		if c == C_DIM:
			return Color8(206, 206, 216)
		if c == C_LABEL:
			return Color8(170, 220, 255)
	return c

## Element cue: a small shape plus a letter, so affinities never rely on colour alone.
## fire ^ triangle F, ice <> diamond I, storm zigzag S, earth square E, water drop W, light + L, shadow crescent D, phys P.
const ELEM_LETTER := {"fire": "F", "ice": "I", "storm": "S", "earth": "E", "water": "W", "light": "L", "shadow": "D", "physical": "P"}

static func elem_badge(ci: CanvasItem, pos: Vector2, e: String) -> float:
	var c = elem_color(e)
	var p = pos.round()
	var dk = Color8(12, 12, 28)
	match e:
		"fire":
			for i in range(7):
				ci.draw_rect(Rect2(p.x + 3 - i / 2, p.y + 1 + i, 1 + (i / 2) * 2, 1), c)
		"ice":
			for i in range(4):
				ci.draw_rect(Rect2(p.x + 3 - i, p.y + 1 + i, 1 + i * 2, 1), c)
				ci.draw_rect(Rect2(p.x + 3 - i, p.y + 7 - i, 1 + i * 2, 1), c)
		"storm":
			for i in range(7):
				ci.draw_rect(Rect2(p.x + (i % 3) * 2, p.y + 1 + i, 2, 1), c)
		"earth":
			ci.draw_rect(Rect2(p.x, p.y + 2, 7, 6), c)
		"water":
			ci.draw_rect(Rect2(p.x + 3, p.y + 1, 1, 2), c)
			ci.draw_rect(Rect2(p.x + 2, p.y + 3, 3, 1), c)
			ci.draw_rect(Rect2(p.x + 1, p.y + 4, 5, 3), c)
			ci.draw_rect(Rect2(p.x + 2, p.y + 7, 3, 1), c)
		"light":
			ci.draw_rect(Rect2(p.x + 3, p.y + 1, 1, 7), c)
			ci.draw_rect(Rect2(p.x, p.y + 4, 7, 1), c)
		"shadow":
			ci.draw_rect(Rect2(p.x + 1, p.y + 2, 5, 5), c)
			ci.draw_rect(Rect2(p.x + 3, p.y + 1, 4, 5), dk)
		_:
			ci.draw_rect(Rect2(p.x + 1, p.y + 2, 5, 5), c)
	text(ci, p + Vector2(8, 0), ELEM_LETTER.get(e, "?"), c)
	return 8 + width(ELEM_LETTER.get(e, "?")) + 2

static func cues_on() -> bool:
	return Settings.get_v("shape_cues") != false
