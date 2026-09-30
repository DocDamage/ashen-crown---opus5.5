class_name MenuList
extends Control
## Cursor list used by every menu. Items: {text, enabled, reason, right, value, color}
## Unavailable entries stay visible with a specific reason (docs/06).

signal chosen(index: int, item: Dictionary)
signal cancelled
signal moved(index: int)

var items: Array = []
var index = 0
var scroll = 0
var rows = 6
var cols = 1
var col_w = 100
var title = ""
var framed = true
var active = true
var allow_cancel = true
var show_reason = true
var show_ghost = true      # dimmed hand on the remembered entry while a sub-menu has focus
var text_x = 20
var memory_key = ""
var large_ok = true        # sys s4: honour the large text setting (the battle command window opts out)
static var memory = {}

func setup(p_items: Array, p_rows: int = 6, p_title: String = "") -> MenuList:
	items = p_items
	rows = p_rows
	title = p_title
	if memory_key != "" and memory.has(memory_key):
		index = clampi(memory[memory_key], 0, maxi(0, items.size() - 1))
	index = clampi(index, 0, maxi(0, items.size() - 1))
	_fix_scroll()
	queue_redraw()
	return self

func current() -> Dictionary:
	if items.is_empty():
		return {}
	return items[index]

func handle(ev: String) -> void:
	if not active:
		return
	var n = items.size()
	match ev:
		"up":
			if n > 0:
				index = (index - cols + n) % n if cols == 1 else maxi(0, index - cols)
				_moved()
		"down":
			if n > 0:
				index = (index + cols) % n if cols == 1 else mini(n - 1, index + cols)
				_moved()
		"left":
			if cols > 1 and index % cols > 0:
				index -= 1
				_moved()
		"right":
			if cols > 1 and index % cols < cols - 1 and index + 1 < n:
				index += 1
				_moved()
		"page_l":
			index = maxi(0, index - vis_rows() * cols)
			_moved()
		"page_r":
			index = mini(n - 1, index + vis_rows() * cols)
			_moved()
		"confirm":
			if n == 0:
				return
			var it: Dictionary = items[index]
			if it.get("enabled", true):
				Audio.ui("FX002")
				if memory_key != "":
					memory[memory_key] = index
				emit_signal("chosen", index, it)
			else:
				Audio.ui("FX004")
		"cancel":
			if allow_cancel:
				Audio.ui("FX003")
				emit_signal("cancelled")

func _moved() -> void:
	Audio.ui("FX001")
	_fix_scroll()
	emit_signal("moved", index)
	queue_redraw()

func _fix_scroll() -> void:
	var line = index / cols
	var vr = vis_rows()
	if line < scroll:
		scroll = line
	if line >= scroll + vr:
		scroll = line - vr + 1

## sys s4: with larger list text (Settings "text_size") fewer rows fit; the list scrolls instead of overflowing.
func _lpx() -> int:
	return UI.size_px("list") if large_ok else UI.FONT_PX

func vis_rows() -> int:
	var p = _lpx()
	if p <= UI.FONT_PX:
		return rows
	var lh = int(ceil(p * 11.0 / UI.FONT_PX))
	var y0 = 5 + (int(ceil(p * 12.0 / UI.FONT_PX)) if title != "" else 0)
	return clampi(int((size.y - y0 - 3) / lh), 1, rows)

func _fit(s: String, w: float) -> String:
	if w <= 8 or UI.width(s) <= w:
		return s
	while s.length() > 1 and UI.width(s + "..") > w:
		s = s.substr(0, s.length() - 1)
	return s + ".."

func _process(_d: float) -> void:
	queue_redraw()

func _draw() -> void:
	var r = Rect2(Vector2.ZERO, size)
	if framed:
		UI.win(self, r)
	var lp = _lpx()
	UI.push_px(lp)
	var lh = UI.line_h()
	var vr = vis_rows()
	var y0 = 5
	if title != "":
		UI.label(self, Vector2(8, 4), _fit(title, size.x - 14) if lp > UI.FONT_PX else title)
		y0 += 12 if lp <= UI.FONT_PX else int(ceil(lp * 12.0 / UI.FONT_PX))
	var total_lines = (items.size() + cols - 1) / cols
	for i in range(items.size()):
		var line = i / cols
		if line < scroll or line >= scroll + vr:
			continue
		var it: Dictionary = items[i]
		var x = text_x + (i % cols) * col_w
		var y = y0 + (line - scroll) * lh
		var en: bool = it.get("enabled", true)
		if i == index:
			if active:
				UI.cursor(self, Vector2(x - 8, y))
			elif show_ghost:
				UI.cursor(self, Vector2(x - 8, y), false, true)
		var col: Color = it.get("color", UI.C_TEXT) if en else UI.C_DIM
		var tx = x
		if it.has("icon") and UI.icon(self, Vector2(x, y), str(it["icon"]), 11, not en):
			tx += 13
		elif it.has("spell") and UI.spell_icon(self, Vector2(x, y), str(it["spell"]), not en):
			tx += 13
		var rx = x + col_w - 12 if cols > 1 else size.x - 8
		var label: String = it.get("text", "")
		var rw = UI.width(str(it["right"])) + 6 if it.has("right") else 0.0
		if lp > UI.FONT_PX or (cols == 1 and UI.width(label) > rx - tx - rw):
			label = _fit(label, rx - tx - rw)
		UI.text(self, Vector2(tx, y), label, col)
		if it.has("right"):
			UI.text_right(self, rx, y, str(it["right"]), col)
	UI.pop_px()
	if scroll > 0:
		UI.arrow(self, Vector2(round(size.x / 2 - 3), 0), -1)
	if scroll + vr < total_lines:
		UI.arrow(self, Vector2(round(size.x / 2 - 3), size.y - 5), 1)
