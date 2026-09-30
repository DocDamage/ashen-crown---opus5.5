class_name DialogueBox
extends Control
## Bottom text window with portrait, speaker name, typed text and a confirm indicator.
## sys s4: text size (Settings "text_size"), window opacity, per-speaker voice blips while text types out,
## auto-advance, and a confirm-button prompt in the current glyph set.

signal finished

var speaker = ""
var portrait_key = ""
var expr = "neutral"
var full = ""
var shown = 0.0
var lines: Array = []
var page = 0
var waiting = false
var skip_all = false
var portrait_cache = {}
var voice_key = ""        # speaker key for blips (director sets it before say; reset after each line)
var _blip_n = 0
var _auto_t = 0.0
var _px = UI.FONT_PX
const BOX := Rect2(4, 170, 312, 66)

func _ready() -> void:
	size = Vector2(320, 240)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false

## Box rectangle for the current text size (taller window for larger text, same FF6 bottom placement).
func box() -> Rect2:
	if _px <= UI.FONT_PX:
		return BOX
	return Rect2(4, 150, 312, 86)

func lines_per_page() -> int:
	return 4 if _px <= 32 else 3

func say(p_speaker: String, p_text: String, p_portrait: String = "", p_expr: String = "neutral") -> void:
	speaker = p_speaker
	portrait_key = p_portrait
	expr = p_expr
	_px = UI.size_px("dialogue")
	UI.push_px(_px)
	var w = box().size.x - 16 - (48 if _has_portrait() else 0)
	lines = UI.wrap(p_text, w)
	UI.pop_px()
	page = 0
	_start_page()
	visible = true
	waiting = true

func _has_portrait() -> bool:
	return Portraits.has(portrait_key)

func _page_text() -> String:
	var n = lines_per_page()
	var ls = lines.slice(page * n, page * n + n)
	return "\n".join(ls)

func _start_page() -> void:
	full = _page_text()
	shown = 0.0 if not skip_all else float(full.length())
	_blip_n = 0
	_auto_t = 0.0

func _process(delta: float) -> void:
	if not visible:
		return
	if shown < full.length():
		var before = int(shown)
		shown = minf(full.length(), shown + Settings.text_cps() * delta)
		_blips(before, int(shown))
	elif waiting and int(Settings.get_v("auto_text") if Settings.get_v("auto_text") != null else 0) > 0 and not QA.active:
		_auto_t += delta
		var hold = [0.0, 3.2, 2.0, 1.1][clampi(int(Settings.get_v("auto_text")), 0, 3)] + full.length() * 0.015
		if _auto_t >= hold:
			handle("confirm")
	queue_redraw()

## One short blip every other letter (never on spaces or punctuation), pitched per speaker.
func _blips(a: int, b: int) -> void:
	if not Settings.get_v("blips") or skip_all or speaker == "":
		return
	for i in range(a, b):
		var ch = full[i] if i < full.length() else " "
		if ch in [" ", "\n", ".", ",", "!", "?", "-", "'", "\""]:
			continue
		_blip_n += 1
		if _blip_n % 2 == 1:
			Audio.blip(voice_key if voice_key != "" else speaker)
			return

func handle(ev: String) -> void:
	if not waiting:
		return
	if ev == "confirm" or ev == "cancel":
		if shown < full.length():
			shown = full.length()
			return
		if (page + 1) * lines_per_page() < lines.size():
			page += 1
			Audio.ui("FX005")
			_start_page()
			return
		waiting = false
		visible = false
		voice_key = ""
		emit_signal("finished")

func is_complete() -> bool:
	return shown >= full.length()

func _draw() -> void:
	var bx = box()
	UI.win_alpha = clampf(float(Settings.get_v("dialogue_opacity") if Settings.get_v("dialogue_opacity") != null else 1.0), 0.2, 1.0)
	UI.win(self, bx)
	UI.win_alpha = 1.0
	UI.push_px(_px)
	var lh = UI.line_h()
	var tx = bx.position.x + 9
	if _has_portrait():
		var fw = 40
		var pr = Rect2(bx.position + Vector2(7, 7), Vector2(fw + 4, fw + 4))
		UI.inset(self, pr, Color8(20, 26, 70))
		Portraits.draw(self, portrait_key, Rect2(pr.position + Vector2(2, 2), Vector2(fw, fw)), expr)
		tx += 48
	var ty = bx.position.y + 5
	if speaker != "":
		UI.text(self, Vector2(tx, ty), speaker, UI.C_GOLD)
		ty += lh + 1
	var vis = full.substr(0, int(shown))
	var yy = ty
	for ln in vis.split("\n"):
		UI.text(self, Vector2(tx, yy), ln)
		yy += lh
	UI.pop_px()
	if is_complete():
		UI.arrow(self, bx.end - Vector2(15, 11), 1)
		if Settings.last_device == "pad" or str(Settings.get_v("glyphs")) not in ["auto", "keyboard"]:
			Glyphs.draw(self, bx.end - Vector2(29, 13), "confirm")
