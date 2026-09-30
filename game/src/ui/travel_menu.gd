class_name TravelMenu
extends Control
## Travel menu: the waystone roads (tabs Surface / The Deep, stones grouped by region) or one travel network
## (mine-rail, mag-rail, skiffs, barges). Emits `done` with the chosen row value ({} when cancelled).

signal done(value: Dictionary)

var main: Node
var title := ""
var tabs: Array = []          # [[label, rows], ...]
var tab := 0
var list: MenuList
var note := ""
var _finished := false

func setup(p_title: String, p_tabs: Array, p_note: String = "") -> void:
	size = Vector2(320, 240)
	title = p_title
	note = p_note
	tabs = p_tabs.filter(func(t): return not (t[1] as Array).is_empty())
	list = MenuList.new()
	list.position = Vector2(60, 44)
	list.size = Vector2(200, 156)
	list.text_x = 16
	add_child(list)
	list.chosen.connect(func(_i, it):
		if it.has("value") and it.get("enabled", true):
			_finish(it["value"]))
	list.cancelled.connect(func(): _finish({}))
	_show_tab(0)

func _show_tab(i: int) -> void:
	if tabs.is_empty():
		list.setup([{"text": "No destinations.", "enabled": false, "reason": ""}], 13)
		return
	tab = clampi(i, 0, tabs.size() - 1)
	var rows: Array = tabs[tab][1]
	list.index = 0
	list.scroll = 0
	list.setup(rows, 13)
	for j in range(rows.size()):
		if rows[j].get("enabled", true) and rows[j].has("value"):
			list.index = j
			break
	list._fix_scroll()
	queue_redraw()

func _finish(v: Dictionary) -> void:
	if _finished:
		return
	_finished = true
	emit_signal("done", v)

func handle(ev: String) -> void:
	if tabs.size() > 1 and ev in ["left", "right", "page_l", "page_r"]:
		Audio.ui("FX001")
		_show_tab((tab + (1 if ev in ["right", "page_r"] else -1) + tabs.size()) % tabs.size())
		return
	# skip header rows when moving
	if ev in ["up", "down"] and not list.items.is_empty():
		var n = list.items.size()
		for k in range(n):
			list.handle(ev)
			if list.current().has("value"):
				break
		return
	list.handle(ev)

func _process(_d: float) -> void:
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.02, 0.02, 0.06, 0.55))
	UI.win(self, Rect2(60, 8, 200, 32))
	UI.text_center(self, 160, 12, title, UI.C_HI)
	if tabs.size() > 1:
		var x = 160 - (tabs.size() * 70) / 2.0
		for i in range(tabs.size()):
			var lbl: String = tabs[i][0]
			UI.text_center(self, x + 35 + i * 70, 24, ("< " + lbl + " >") if i == tab else lbl, UI.C_TEXT if i == tab else UI.C_DIM)
	elif not tabs.is_empty():
		UI.text_center(self, 160, 24, tabs[0][0], UI.C_DIM)
	if note != "":
		UI.win(self, Rect2(40, 204, 240, 22))
		UI.text_center(self, 160, 209, note, UI.C_DIM)
