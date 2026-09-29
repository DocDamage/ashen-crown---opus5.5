class_name DialogueBox
extends Control
## Bottom text window with portrait, speaker name, typed text and a confirm indicator.

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
const BOX := Rect2(4, 170, 312, 66)

func _ready() -> void:
	size = Vector2(320, 240)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false

func say(p_speaker: String, p_text: String, p_portrait: String = "", p_expr: String = "neutral") -> void:
	speaker = p_speaker
	portrait_key = p_portrait
	expr = p_expr
	var w = BOX.size.x - 16 - (48 if _has_portrait() else 0)
	lines = UI.wrap(p_text, w)
	page = 0
	_start_page()
	visible = true
	waiting = true

func _has_portrait() -> bool:
	return portrait_key != "" and _portrait() != null

func _portrait() -> Texture2D:
	var path = "res://assets/sprites/portraits/%s.png" % portrait_key
	if not portrait_cache.has(path):
		portrait_cache[path] = Content.load_art(path)
	return portrait_cache[path]

func _page_text() -> String:
	var ls = lines.slice(page * 4, page * 4 + 4)
	return "\n".join(ls)

func _start_page() -> void:
	full = _page_text()
	shown = 0.0 if not skip_all else float(full.length())

func _process(delta: float) -> void:
	if not visible:
		return
	if shown < full.length():
		shown = minf(full.length(), shown + Settings.text_cps() * delta)
	queue_redraw()

func handle(ev: String) -> void:
	if not waiting:
		return
	if ev == "confirm" or ev == "cancel":
		if shown < full.length():
			shown = full.length()
			return
		if (page + 1) * 4 < lines.size():
			page += 1
			Audio.ui("FX005")
			_start_page()
			return
		waiting = false
		visible = false
		emit_signal("finished")

func is_complete() -> bool:
	return shown >= full.length()

func _draw() -> void:
	UI.win(self, BOX)
	var tx = BOX.position.x + 8
	if _has_portrait():
		var t = _portrait()
		var col = {"neutral": 0, "concern": 1, "determined": 2}.get(expr, 0)
		var fw = 40
		if t.get_width() < 120:
			col = 0
		draw_rect(Rect2(BOX.position + Vector2(6, 6), Vector2(42, 42)), Color8(10, 12, 24))
		draw_texture_rect_region(t, Rect2(BOX.position + Vector2(7, 7), Vector2(fw, fw)), Rect2(col * fw, 0, fw, fw))
		tx += 46
	var ty = BOX.position.y + 4
	if speaker != "":
		UI.text(self, Vector2(tx, ty), speaker, UI.C_GOLD)
		ty += 12
	var vis = full.substr(0, int(shown))
	var yy = ty
	for ln in vis.split("\n"):
		UI.text(self, Vector2(tx, yy), ln)
		yy += 11
	if is_complete() and int(Time.get_ticks_msec() / 300) % 2 == 0:
		UI.text(self, BOX.end - Vector2(12, 12), "▼", UI.C_HI)
