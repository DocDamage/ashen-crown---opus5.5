class_name BattleFX
extends RefCounted
## Sprite effects from the owner's spell and buff packs (tools/art/install_overhaul.py vfx -> assets/ext/vfx):
## fx.json lists every effect sheet (frames, fps, cell, anchor) and, per ability, the cast / bolt / hit effects.
## Drawn at native resolution; positions are in battle units.

static var db: Dictionary = {}
static var _tex = {}

static func ok() -> bool:
	if db.is_empty():
		var p = "res://assets/ext/vfx/fx.json"
		if FileAccess.file_exists(p):
			db = JSON.parse_string(FileAccess.get_file_as_string(p))
		else:
			db = {"effects": {}}
	return not db.get("effects", {}).is_empty()

static func has(name: String) -> bool:
	return ok() and db["effects"].has(name)

static func tex(name: String) -> Texture2D:
	if not _tex.has(name):
		var p = "res://assets/ext/vfx/%s.png" % name
		_tex[name] = load(p) if ResourceLoader.exists(p) else null
	return _tex[name]

static func for_ability(aid: String) -> Dictionary:
	return db.get("abilities", {}).get(aid, {}) if ok() else {}

static func for_status(sid: String) -> String:
	return str(db.get("statuses", {}).get(sid, "")) if ok() else ""

static func length(name: String) -> float:
	if not has(name):
		return 0.0
	var e: Dictionary = db["effects"][name]
	return float(e["frames"]) / float(e["fps"])

## Draws effect `name` at elapsed time `t` (seconds) at `pos` (units). Returns false when finished.
static func draw(ci: CanvasItem, name: String, t: float, pos: Vector2, scale: float = 1.0) -> bool:
	if not has(name):
		return false
	var e: Dictionary = db["effects"][name]
	var f = int(t * float(e["fps"]))
	if f >= int(e["frames"]):
		return false
	var tx = tex(name)
	if tx == null:
		return false
	var cw = float(e["cell"][0])
	var chh = float(e["cell"][1])
	var cols = int(e["cols"])
	var src = Rect2((f % cols) * cw, (f / cols) * chh, cw, chh)
	UI.native_begin(ci, (pos * UI.U).round() / UI.U)
	var dst = Rect2(-float(e["anchor"][0]) * cw * scale, -float(e["anchor"][1]) * chh * scale, cw * scale, chh * scale)
	ci.draw_texture_rect_region(tx, dst, src)
	UI.native_end(ci)
	return true

## Vestige summon art (assets/ext/vestiges/Vxx.png/.json: appear / idle / vanish tags), drawn on the 2x layer.
static var _ves = {}

static func vestige(vid: String) -> Dictionary:
	if not _ves.has(vid):
		var jp = "res://assets/ext/vestiges/%s.json" % vid
		var tp = "res://assets/ext/vestiges/%s.png" % vid
		if FileAccess.file_exists(jp) and ResourceLoader.exists(tp):
			var m: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(jp))
			m["tex"] = load(tp)
			_ves[vid] = m
		else:
			_ves[vid] = {}
	return _ves[vid]

static func _tag_frame(m: Dictionary, tag: String, t: float, loop: bool) -> int:
	var r: Array = m["tags"].get(tag, [0, 0])
	var total = 0.0
	for i in range(int(r[0]), int(r[1]) + 1):
		total += float(m["durations"][i]) / 1000.0
	var tt = fmod(t, total) if loop else minf(t, total - 0.001)
	for i in range(int(r[0]), int(r[1]) + 1):
		tt -= float(m["durations"][i]) / 1000.0
		if tt < 0:
			return i
	return int(r[1])

static func tag_length(m: Dictionary, tag: String) -> float:
	var r: Array = m["tags"].get(tag, [0, 0])
	var total = 0.0
	for i in range(int(r[0]), int(r[1]) + 1):
		total += float(m["durations"][i]) / 1000.0
	return total

## t: seconds since the summon started; dur: total time on screen. Feet at `foot` (units).
static func draw_vestige(ci: CanvasItem, vid: String, t: float, dur: float, foot: Vector2) -> bool:
	var m = vestige(vid)
	if m.is_empty():
		return false
	var ap = tag_length(m, "appear")
	var vn = tag_length(m, "vanish")
	var f: int
	if t < ap:
		f = _tag_frame(m, "appear", t, false)
	elif t < dur - vn:
		f = _tag_frame(m, "idle", t - ap, true)
	else:
		f = _tag_frame(m, "vanish", t - (dur - vn), false)
	var cw = float(m["cell"][0])
	var chh = float(m["cell"][1])
	var fr: Array = m["frames"][f]
	UI.native_begin(ci, (foot * UI.U).round() / UI.U)
	ci.draw_texture_rect_region(m["tex"], Rect2(-cw, -chh * 2.0, cw * 2.0, chh * 2.0), Rect2(fr[0], fr[1], cw, chh))
	UI.native_end(ci)
	return true


## Field version: the idle loop only, scale in native pixels per source pixel (battle uses 2.0).
static func draw_vestige_idle(ci: CanvasItem, vid: String, t: float, foot: Vector2, scale: float = 0.5) -> bool:
	var m = vestige(vid)
	if m.is_empty():
		return false
	var f = _tag_frame(m, "idle", t, true)
	var cw = float(m["cell"][0])
	var chh = float(m["cell"][1])
	var fr: Array = m["frames"][f]
	UI.native_begin(ci, (foot * UI.U).round() / UI.U)
	ci.draw_texture_rect_region(m["tex"], Rect2(-cw * scale / 2.0, -chh * scale, cw * scale, chh * scale), Rect2(fr[0], fr[1], cw, chh))
	UI.native_end(ci)
	return true
