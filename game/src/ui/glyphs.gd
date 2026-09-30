class_name Glyphs
extends RefCounted
## Button prompts drawn as small labelled shapes (no glyph art needed): Xbox (coloured lettered discs), PlayStation
## (drawn cross/circle/square/triangle), Steam Deck (monochrome lettered keys) and keyboard keycaps.
## The set follows the last device used (Settings.last_device / pad name) unless the "glyphs" setting forces one.

const XBOX := {JOY_BUTTON_A: "A", JOY_BUTTON_B: "B", JOY_BUTTON_X: "X", JOY_BUTTON_Y: "Y", JOY_BUTTON_LEFT_SHOULDER: "LB",
	JOY_BUTTON_RIGHT_SHOULDER: "RB", JOY_BUTTON_BACK: "View", JOY_BUTTON_START: "Menu", JOY_BUTTON_LEFT_STICK: "LS",
	JOY_BUTTON_RIGHT_STICK: "RS", JOY_BUTTON_DPAD_UP: "Up", JOY_BUTTON_DPAD_DOWN: "Down", JOY_BUTTON_DPAD_LEFT: "Left",
	JOY_BUTTON_DPAD_RIGHT: "Right"}
const PS := {JOY_BUTTON_A: "Cross", JOY_BUTTON_B: "Circle", JOY_BUTTON_X: "Square", JOY_BUTTON_Y: "Triangle",
	JOY_BUTTON_LEFT_SHOULDER: "L1", JOY_BUTTON_RIGHT_SHOULDER: "R1", JOY_BUTTON_BACK: "Create", JOY_BUTTON_START: "Options",
	JOY_BUTTON_LEFT_STICK: "L3", JOY_BUTTON_RIGHT_STICK: "R3", JOY_BUTTON_DPAD_UP: "Up", JOY_BUTTON_DPAD_DOWN: "Down",
	JOY_BUTTON_DPAD_LEFT: "Left", JOY_BUTTON_DPAD_RIGHT: "Right"}
const DECK := {JOY_BUTTON_A: "A", JOY_BUTTON_B: "B", JOY_BUTTON_X: "X", JOY_BUTTON_Y: "Y", JOY_BUTTON_LEFT_SHOULDER: "L1",
	JOY_BUTTON_RIGHT_SHOULDER: "R1", JOY_BUTTON_BACK: "View", JOY_BUTTON_START: "Menu", JOY_BUTTON_LEFT_STICK: "L3",
	JOY_BUTTON_RIGHT_STICK: "R3", JOY_BUTTON_DPAD_UP: "Up", JOY_BUTTON_DPAD_DOWN: "Down", JOY_BUTTON_DPAD_LEFT: "Left",
	JOY_BUTTON_DPAD_RIGHT: "Right"}
const XBOX_COL := {"A": Color8(96, 184, 72), "B": Color8(220, 64, 56), "X": Color8(64, 120, 232), "Y": Color8(236, 196, 48)}
const STYLES := ["auto", "keyboard", "xbox", "playstation", "deck"]

## The active prompt style.
static func style() -> String:
	var forced = str(Settings.get_v("glyphs")) if Settings.get_v("glyphs") != null else "auto"
	if forced != "auto" and STYLES.has(forced):
		return forced
	if Settings.last_device != "pad":
		return "keyboard"
	var n: String = Settings.pad_name.to_lower()
	if n.find("steam deck") >= 0 or n.find("valve") >= 0 or n.find("steam") >= 0:
		return "deck"
	if n.find("ps") >= 0 or n.find("sony") >= 0 or n.find("dualsense") >= 0 or n.find("dualshock") >= 0 or n.find("playstation") >= 0:
		return "playstation"
	return "xbox"

## Short text label for an action's first binding in the current style ("A", "Cross", "Z", "Enter" ...).
static func label(action: String, st: String = "") -> String:
	if st == "":
		st = style()
	if st == "keyboard":
		var ks: Array = Settings.keys_for(action)
		if ks.is_empty():
			return "-"
		var k = OS.get_keycode_string(int(ks[0]))
		return {"Escape": "Esc", "BackSpace": "Bksp", "Space": "Space", "Shift": "Shift"}.get(k, k)
	var pb: Array = Settings.pad_for(action)
	if pb.is_empty():
		return "-"
	var b = int(pb[0])
	var tab: Dictionary = XBOX if st == "xbox" else (PS if st == "playstation" else DECK)
	return tab.get(b, "B%d" % b)

## Width in units a prompt takes (glyph plus 2 px gap).
static func width(action: String) -> float:
	var st = style()
	var l = label(action, st)
	if st == "playstation" and l in ["Cross", "Circle", "Square", "Triangle"]:
		return 11.0
	if (st == "xbox" or st == "deck") and l.length() == 1:
		return 11.0
	return UI.width(l) + 8.0

## Draws the prompt for `action` with its top-left at `pos` (units, 9 high). Returns its width.
static func draw(ci: CanvasItem, pos: Vector2, action: String) -> float:
	var st = style()
	var l = label(action, st)
	var p = pos.round()
	if st == "playstation" and l in ["Cross", "Circle", "Square", "Triangle"]:
		ci.draw_circle(p + Vector2(4.5, 5), 4.8, Color8(20, 20, 30))
		ci.draw_circle(p + Vector2(4.5, 5), 4.2, Color8(60, 62, 76))
		var c = {"Cross": Color8(140, 170, 255), "Circle": Color8(255, 120, 130), "Square": Color8(240, 150, 220), "Triangle": Color8(110, 220, 190)}[l]
		match l:
			"Cross":
				ci.draw_line(p + Vector2(2.5, 3), p + Vector2(6.5, 7), c, 1.0)
				ci.draw_line(p + Vector2(6.5, 3), p + Vector2(2.5, 7), c, 1.0)
			"Circle":
				ci.draw_arc(p + Vector2(4.5, 5), 2.3, 0, TAU, 12, c, 1.0)
			"Square":
				ci.draw_rect(Rect2(p + Vector2(2.5, 3), Vector2(4, 4)), c, false, 1.0)
			"Triangle":
				ci.draw_polyline(PackedVector2Array([p + Vector2(4.5, 2.5), p + Vector2(7, 7), p + Vector2(2, 7), p + Vector2(4.5, 2.5)]), c, 1.0)
		return 11.0
	if (st == "xbox" or st == "deck") and l.length() == 1:
		if st == "xbox":
			ci.draw_circle(p + Vector2(4.5, 5), 4.8, Color8(20, 20, 30))
			ci.draw_circle(p + Vector2(4.5, 5), 4.2, XBOX_COL.get(l, Color8(90, 90, 100)))
		else:
			ci.draw_rect(Rect2(p + Vector2(0, 0.5), Vector2(9, 9)), Color8(20, 20, 30))
			ci.draw_rect(Rect2(p + Vector2(1, 1.5), Vector2(7, 7)), Color8(70, 74, 88))
		UI.text(ci, p + Vector2(2.2, 0), l, Color.WHITE, false)
		return 11.0
	# keycap / labelled shoulder or system button
	var w = UI.width(l) + 6.0
	ci.draw_rect(Rect2(p + Vector2(0, 0), Vector2(w, 10)), Color8(20, 20, 30))
	ci.draw_rect(Rect2(p + Vector2(1, 1), Vector2(w - 2, 8)), Color8(206, 208, 220) if st == "keyboard" else Color8(70, 74, 88))
	ci.draw_rect(Rect2(p + Vector2(1, 8), Vector2(w - 2, 1)), Color8(120, 124, 140) if st == "keyboard" else Color8(40, 42, 54))
	UI.text(ci, p + Vector2(3, -0.5), l, Color8(20, 20, 30) if st == "keyboard" else Color.WHITE, false)
	return w + 2.0

## Draws a row of prompts: [[action, "text"], ...] from `pos`; returns the end x.
static func hints(ci: CanvasItem, pos: Vector2, pairs: Array) -> float:
	var x = pos.x
	for pr in pairs:
		x += draw(ci, Vector2(x, pos.y), pr[0]) + 1
		UI.text(ci, Vector2(x, pos.y), pr[1], UI.C_TEXT)
		x += UI.width(pr[1]) + 8
	return x
