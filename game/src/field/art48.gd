class_name Art48
extends RefCounted
## Native 48px map art (overhaul): built by tools/maps48 into assets/ext/maps48/<MAP>.json + <MAP>_ground.png
## (+ optional <MAP>_over.png). One map cell = 16 units = 48 screen pixels, so collision, triggers and entities keep
## the map grid; only the drawing changes.
##   ground   baked floor layer (everything flat), drawn under actors
##   objects  [sheet, sx, sy, sw, sh, x, y, base]: sprites y-sorted with actors by `base` (native px)
##   anims    [name, x, y, base]: looping field animations (assets/ext/field_anim/<name>.png + .json)
##   over     layer drawn above actors (canopies, bridges overhead)

var data: Dictionary = {}
var ground: Texture2D = null
var over: Texture2D = null
var sheets: Array = []
var anims: Dictionary = {}

static func load_for(map_id: String) -> Art48:
	var jp = "res://assets/ext/maps48/%s.json" % map_id
	if not FileAccess.file_exists(jp):
		return null
	var a = Art48.new()
	a.data = JSON.parse_string(FileAccess.get_file_as_string(jp))
	var gp = "res://assets/ext/maps48/%s" % a.data.get("ground", "")
	a.ground = load(gp) if ResourceLoader.exists(gp) else null
	var op = "res://assets/ext/maps48/%s" % a.data.get("over", "")
	a.over = load(op) if a.data.get("over", "") != "" and ResourceLoader.exists(op) else null
	for s in a.data.get("sheets", []):
		var sp = "res://assets/ext/%s" % s
		a.sheets.append(load(sp) if ResourceLoader.exists(sp) else null)
	for an in a.data.get("anims", []):
		var nm: String = an[0]
		if not a.anims.has(nm):
			var ap = "res://assets/ext/field_anim/%s.json" % nm
			var tp = "res://assets/ext/field_anim/%s.png" % nm
			if FileAccess.file_exists(ap) and ResourceLoader.exists(tp):
				var m: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ap))
				m["tex"] = load(tp)
				a.anims[nm] = m
	return a

func draw_ground(ci: CanvasItem, cam: Vector2) -> void:
	if ground == null:
		return
	UI.native_begin(ci, -(cam * UI.U).round() / UI.U)
	ci.draw_texture(ground, Vector2.ZERO)
	UI.native_end(ci)

func draw_over(ci: CanvasItem, cam: Vector2) -> void:
	if over == null:
		return
	UI.native_begin(ci, -(cam * UI.U).round() / UI.U)
	ci.draw_texture(over, Vector2.ZERO)
	UI.native_end(ci)

## Adds visible objects and animations to the y-sorted draw list used by field.gd:
## entries [sort_y_units, "a48", payload, pos_units].
func collect(talls: Array, cam: Vector2, view: Vector2) -> void:
	var cx0 = cam.x * UI.U - 96
	var cy0 = cam.y * UI.U - 96
	var cx1 = (cam.x + view.x) * UI.U + 96
	var cy1 = (cam.y + view.y) * UI.U + 400
	for o in data.get("objects", []):
		var x = float(o[5])
		var y = float(o[6])
		if x + float(o[3]) < cx0 or x > cx1 or y + float(o[4]) < cy0 or y > cy1:
			continue
		talls.append([float(o[7]) / UI.U, "a48", o, Vector2.ZERO])
	for an in data.get("anims", []):
		var x2 = float(an[1])
		var y2 = float(an[2])
		if x2 < cx0 - 96 or x2 > cx1 or y2 < cy0 - 96 or y2 > cy1:
			continue
		talls.append([float(an[3]) / UI.U, "a48anim", an, Vector2.ZERO])

func draw_object(ci: CanvasItem, o: Array, cam: Vector2) -> void:
	var t: Texture2D = sheets[int(o[0])] if int(o[0]) < sheets.size() else null
	if t == null:
		return
	UI.native_begin(ci, -(cam * UI.U).round() / UI.U)
	ci.draw_texture_rect_region(t, Rect2(float(o[5]), float(o[6]), float(o[3]), float(o[4])), Rect2(float(o[1]), float(o[2]), float(o[3]), float(o[4])))
	UI.native_end(ci)

func draw_anim(ci: CanvasItem, an: Array, cam: Vector2, time: float) -> void:
	var m: Dictionary = anims.get(an[0], {})
	if m.is_empty():
		return
	var n = int(m["frames"])
	var f = int(time * float(m.get("fps", 8))) % n
	var cw = float(m["cell"][0])
	var chh = float(m["cell"][1])
	var cols = int(m.get("cols", n))
	UI.native_begin(ci, -(cam * UI.U).round() / UI.U)
	ci.draw_texture_rect_region(m["tex"], Rect2(float(an[1]), float(an[2]), cw, chh), Rect2((f % cols) * cw, (f / cols) * chh, cw, chh))
	UI.native_end(ci)
