class_name Wyrms
extends RefCounted
## Roaming superbosses (FFVII Weapon style): the four ancient wyrms walk the world late in the game as visible
## sprites. They appear after the fault once CH16 is done, never before, and stop appearing once beaten
## (flag sb_<id>_down, set by their scene). Touching one runs scene WYRM_<id> (`battle <id> noflee`).
##   SB01 Cindermaw     WORLD_POST, the Cinder Reach around Cindermaw Caldera (N10); meets the party on the ground
##   SB03 Aerith-Vael   WORLD_POST, the sky lanes over the whole map; meets only the airship
##   SB02 Thalassar     WORLD_POST coastal water (ground or airship) and the UNDERSEA floor (the submarine)
##   SB04 Ossathrax     DEEP_POST, the Hollow Throne's floors; meets the party on the ground
## Drawn from the enemy art (assets/ext/enemies/<sprite>.png, frame 0) as billboards; a silhouette if missing.

const DEFS := {
	"SB01": [{"map": "WORLD_POST", "center": Vector2i(20, 66), "radius": 16, "move": "land", "meets": ["foot"]}],
	"SB03": [{"map": "WORLD_POST", "center": Vector2i(100, 60), "radius": 70, "move": "air", "meets": ["ship"]}],
	"SB02": [{"map": "WORLD_POST", "center": Vector2i(140, 96), "radius": 30, "move": "coast", "meets": ["foot", "ship"]},
		{"map": "UNDERSEA", "center": Vector2i(70, 58), "radius": 26, "move": "sea", "meets": ["sub"]}],
	"SB04": [{"map": "DEEP_POST", "center": Vector2i(110, 32), "radius": 26, "move": "land", "meets": ["foot"]}],
}
const SPEED := {"land": 1.4, "air": 2.6, "coast": 1.6, "sea": 1.8}     # cells per second
const HEIGHT := {"SB01": 58.0, "SB02": 60.0, "SB03": 64.0, "SB04": 60.0}  # billboard height (units)

var list: Array = []          # [{id, def, pos (cells, float), target, cool}]
static var _tex = {}

static func active(sb: String) -> bool:
	if Game.S.is_empty() or Game.S.get("world_phase", "pre") != "post":
		return false
	return Game.chapter_done("CH16") and not Game.flag("sb_%s_down" % sb)

static func for_map(field: Field) -> Wyrms:
	var w = Wyrms.new()
	for sb in DEFS:
		for d in DEFS[sb]:
			if d["map"] != field.map_id or not active(sb):
				continue
			var r = Rng.new(hash(sb + field.map_id) & 0x7fffffff)
			var p = w._pick(field, d, r)
			if p.x < 0:
				continue
			w.list.append({"id": sb, "def": d, "pos": Vector2(p), "target": Vector2(p), "cool": 2.0, "rng": r})
	return w

func _ok(field: Field, d: Dictionary, c: Vector2i) -> bool:
	if c.x < 1 or c.y < 1 or c.x >= field.W - 1 or c.y >= field.H - 1:
		return false
	if (c - d["center"]).length() > float(d["radius"]):
		return false
	var k = field.kind_at(c.x, c.y)
	match d["move"]:
		"air":
			return true
		"sea":
			return not FieldSys.sub_solid(k)
		"coast":
			if k != "water":
				return false
			for dv in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1), Vector2i(2, 0), Vector2i(-2, 0), Vector2i(0, 2), Vector2i(0, -2)]:
				var nk = field.kind_at(c.x + dv.x, c.y + dv.y)
				if nk != "water" and nk != "deep" and nk != "void":
					return true
			return false
		_:
			return not field.solid_set.has(k) and field.block_at(c.x, c.y).is_empty()

func _pick(field: Field, d: Dictionary, r: Rng) -> Vector2i:
	for i in range(80):
		var rad = int(d["radius"])
		var c = d["center"] + Vector2i(r.randi_range(-rad, rad), r.randi_range(-rad, rad))
		if _ok(field, d, c):
			return c
	return Vector2i(-1, -1)

## Moves every wyrm; returns the id of one the party touched this frame ("" otherwise).
func update(delta: float, field: Field) -> String:
	var hit = ""
	for w in list:
		w["cool"] = maxf(0.0, float(w["cool"]) - delta)
		var d: Dictionary = w["def"]
		var pos: Vector2 = w["pos"]
		var tgt: Vector2 = w["target"]
		if pos.distance_to(tgt) < 0.05:
			var t = _pick(field, d, w["rng"])
			if t.x >= 0:
				w["target"] = Vector2(t)
			continue
		var step = pos.move_toward(tgt, SPEED[d["move"]] * delta)
		var cell = Vector2i(roundi(step.x), roundi(step.y))
		if not _ok(field, d, cell):
			w["target"] = pos.round()
			continue
		w["pos"] = step
		var me = Vector2(field.p_pos) / Field.TS
		var mode = field.vehicle if field.vehicle != "foot" else "foot"
		if hit == "" and float(w["cool"]) <= 0.0 and d["meets"].has(mode) and me.distance_to(step) < 1.1 and field.can_move():
			hit = w["id"]
			w["cool"] = 4.0
	return hit

## Adds y-sorted billboards (type "wyrm") in field screen coordinates.
func collect(talls: Array, cam: Vector2) -> void:
	for w in list:
		var pos: Vector2 = w["pos"] * Field.TS - cam
		talls.append([pos.y + 15.0, "wyrm", w, pos])

static func tex(sb: String) -> Array:
	## [texture, region] of frame 0 of the wyrm's enemy art, or [] when the art is missing
	if not _tex.has(sb):
		var key: String = str(Content.enemy(sb).get("sprite", sb)).split("@")[0]
		var p = "res://assets/ext/enemies/%s.png" % key
		var out = []
		if ResourceLoader.exists(p):
			var t: Texture2D = load(p)
			var reg = Rect2(Vector2.ZERO, t.get_size())
			var jp = "res://assets/ext/enemies/%s.json" % key
			if FileAccess.file_exists(jp):
				var m = JSON.parse_string(FileAccess.get_file_as_string(jp))
				if typeof(m) == TYPE_DICTIONARY and m.has("cell"):
					reg = Rect2(0, 0, float(m["cell"][0]), float(m["cell"][1]))
			out = [t, reg]
		_tex[sb] = out
	return _tex[sb]

## Draw one wyrm with its feet at pos + (8, 16) (field units, before the Mode-7 transform).
static func draw(ci: CanvasItem, w: Dictionary, pos: Vector2, time: float) -> void:
	var sb: String = w["id"]
	var air: bool = w["def"]["move"] == "air"
	var foot = pos + Vector2(8, 16)
	var h: float = HEIGHT.get(sb, 56.0)
	var lift = (-42.0 + sin(time * 1.7) * 3.0) if air else sin(time * 2.2) * 1.0
	# shadow
	var sw = h * (0.55 if air else 0.8)
	ci.draw_colored_polygon(_ellipse(foot, sw * 0.5, sw * 0.14), Color(0, 0, 0, 0.22 if air else 0.32))
	var tr: Array = tex(sb)
	var mod = Color(0.72, 0.8, 1.0) if w["def"]["move"] == "sea" else Color.WHITE
	if not tr.is_empty():
		var reg: Rect2 = tr[1]
		var s = h / reg.size.y
		var size = reg.size * s
		ci.draw_texture_rect_region(tr[0], Rect2(foot + Vector2(-size.x / 2.0, -size.y + lift), size), reg, mod)
		return
	# silhouette: a coiled body and a head with ember eyes
	var col = {"SB01": Color(0.25, 0.08, 0.05), "SB02": Color(0.05, 0.14, 0.24), "SB03": Color(0.62, 0.66, 0.76), "SB04": Color(0.14, 0.1, 0.16)}.get(sb, Color(0.1, 0.1, 0.1))
	var eye = {"SB01": Color(1, 0.6, 0.2), "SB02": Color(0.4, 1, 0.9), "SB03": Color(1, 1, 0.8), "SB04": Color(0.8, 0.4, 1)}.get(sb, Color.WHITE)
	var base = foot + Vector2(0, lift)
	ci.draw_colored_polygon(_ellipse(base + Vector2(0, -h * 0.22), h * 0.42, h * 0.22), col)
	ci.draw_colored_polygon(_ellipse(base + Vector2(h * 0.18, -h * 0.55), h * 0.16, h * 0.3), col)
	ci.draw_colored_polygon(_ellipse(base + Vector2(h * 0.26, -h * 0.86), h * 0.2, h * 0.12), col)
	if air:
		ci.draw_colored_polygon(PackedVector2Array([base + Vector2(-h * 0.1, -h * 0.4), base + Vector2(-h * 0.7, -h * 0.9), base + Vector2(-h * 0.3, -h * 0.3)]), col.darkened(0.2))
		ci.draw_colored_polygon(PackedVector2Array([base + Vector2(h * 0.1, -h * 0.4), base + Vector2(h * 0.75, -h * 0.95), base + Vector2(h * 0.35, -h * 0.28)]), col.darkened(0.2))
	ci.draw_rect(Rect2(base + Vector2(h * 0.3, -h * 0.9), Vector2(2, 1.5)), eye)
	ci.draw_rect(Rect2(base + Vector2(h * 0.36, -h * 0.88), Vector2(2, 1.5)), eye)

static func _ellipse(c: Vector2, rx: float, ry: float) -> PackedVector2Array:
	var pts = PackedVector2Array()
	for i in range(16):
		var a = TAU * i / 16.0
		pts.append(c + Vector2(cos(a) * rx, sin(a) * ry))
	return pts
