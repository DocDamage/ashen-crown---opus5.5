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
