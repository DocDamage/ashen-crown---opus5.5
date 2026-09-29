class_name DocView
extends Control
## Document overlay (letters, ledgers, testimony). Pages with confirm; cancel closes.

signal closed
var title = ""
var pages: Array = []
var page = 0

func setup(p_title: String, text: String) -> void:
	size = Vector2(320, 240)
	title = p_title
	var lines = UI.wrap(text, 256)
	pages = []
	for i in range(0, lines.size(), 13):
		pages.append(lines.slice(i, i + 13))
	if pages.is_empty():
		pages = [[""]]

func handle(ev: String) -> void:
	if ev == "confirm":
		if page + 1 < pages.size():
			page += 1
			Audio.ui("FX005")
			queue_redraw()
		else:
			emit_signal("closed")
	elif ev == "cancel":
		emit_signal("closed")

func _draw() -> void:
	draw_rect(Rect2(0, 0, 320, 240), Color(0, 0, 0, 0.5))
	var r = Rect2(24, 14, 272, 212)
	draw_rect(r, Color8(226, 214, 184))
	draw_rect(Rect2(r.position + Vector2(3, 3), r.size - Vector2(6, 6)), Color8(120, 96, 60), false)
	var ink = Color8(52, 38, 28)
	UI.text_center(self, 160, 22, title, Color8(120, 40, 30))
	var y = 40
	for ln in pages[page]:
		UI.text(self, Vector2(32, y), ln, ink, false)
		y += 13
	UI.text_right(self, 288, 212, "%d/%d" % [page + 1, pages.size()], Color8(120, 96, 60))
