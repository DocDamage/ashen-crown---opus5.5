class_name NameEntry
extends Control
## FF6-style name entry: a letter grid, the hero's portrait and the name so far. Confirm adds the letter under the
## cursor, Cancel deletes the last letter, "End" (or Menu) finishes. An empty name restores the hero's own name.

signal done(new_name: String)

const MAX_LEN := 10
const ROWS := [
	"ABCDEFGHIJKLM",
	"NOPQRSTUVWXYZ",
	"abcdefghijklm",
	"nopqrstuvwxyz",
	"0123456789-'.",
]
const COLS := 13

var cid = ""
var cur_name = ""
var cx = 0
var cy = 0

func setup(p_cid: String) -> void:
	cid = p_cid
	cur_name = Game.short_name(cid)
	size = Vector2(320, 240)
	queue_redraw()

func _rows() -> int:
	return ROWS.size() + 1     # last row: Space, Default, End

func handle(ev: String) -> void:
	match ev:
		"up":
			cy = (cy - 1 + _rows()) % _rows()
		"down":
			cy = (cy + 1) % _rows()
		"left":
			cx = (cx - 1 + _cols()) % _cols()
		"right":
			cx = (cx + 1) % _cols()
		"confirm":
			_press()
		"cancel":
			if cur_name.length() > 0:
				cur_name = cur_name.substr(0, cur_name.length() - 1)
				Audio.ui("FX002")
		"menu":
			_finish()
	cx = mini(cx, _cols() - 1)
	Audio.ui("FX001") if ev in ["up", "down", "left", "right"] else null
	queue_redraw()

func _cols() -> int:
	return COLS if cy < ROWS.size() else 3

func _press() -> void:
	if cy < ROWS.size():
		if cur_name.length() < MAX_LEN:
			cur_name += ROWS[cy][cx]
			Audio.ui("FX001")
		else:
			Audio.ui("FX004")
		return
	match cx:
		0:
			if cur_name.length() < MAX_LEN and cur_name != "":
				cur_name += " "
		1:
			cur_name = str(Content.ch(cid).get("short", cid))
		2:
			_finish()

func _finish() -> void:
	var n = cur_name.strip_edges()
	Game.rename_hero(cid, n)
	Audio.ui("FX003")
	emit_signal("done", Game.short_name(cid))

func _draw() -> void:
	draw_rect(Rect2(0, 0, 320, 240), Color(0.02, 0.02, 0.08, 0.6))
	UI.win(self, Rect2(16, 16, 288, 56))
	UI.inset(self, Rect2(24, 22, 44, 44))
	Portraits.draw(self, cid, Rect2(26, 24, 40, 40))
	UI.label(self, Vector2(78, 26), "Name this hero")
	UI.text(self, Vector2(78, 42), str(Content.ch(cid).get("name", cid)), UI.C_DIM)
	var shown = cur_name + ("_" if cur_name.length() < MAX_LEN and (Time.get_ticks_msec() / 400) % 2 == 0 else "")
	UI.win(self, Rect2(180, 34, 116, 22), Color8(14, 18, 34, 235))
	UI.text(self, Vector2(188, 39), shown, UI.C_HI)
	UI.win(self, Rect2(16, 78, 288, 146))
	for r in range(ROWS.size()):
		for c in range(COLS):
			var p = Vector2(34 + c * 20, 88 + r * 20)
			UI.text(self, p, ROWS[r][c])
			if r == cy and c == cx:
				UI.cursor(self, p)
	var last = ["Space", "Default", "End"]
	for i in range(3):
		var p = Vector2(34 + i * 88, 196)
		UI.text(self, p, last[i], UI.C_HI if i == 2 else UI.C_TEXT)
		if cy == ROWS.size() and cx == i:
			UI.cursor(self, p)
	UI.text(self, Vector2(22, 226), "Confirm: add  Cancel: delete  Menu: done", UI.C_DIM)

func _process(_d: float) -> void:
	queue_redraw()
