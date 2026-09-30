class_name HeroArt
extends RefCounted
## Overhaul hero sprites (tools/art/hero_import.py -> res://assets/heroes/<cid>/, library build in assets/ext).
## Field: 4-direction sheet, column 0 standing, 1..n walk. Battle: one strip per animation, facing west.
## Everything is drawn at native resolution (1 art pixel = 1 screen pixel at 960x720) from unit coordinates.

static var _meta = {}
static var _tex = {}

static func _dir(cid: String) -> String:
	## heroes: "C01" -> res://assets/heroes/C01; townsfolk: "npcs/<stem>" -> res://assets/npcs/<stem>
	return "res://assets/" + (cid if cid.contains("/") else "heroes/" + cid)

static func _load(cid: String, kind: String) -> bool:
	var key = cid + "/" + kind
	if _meta.has(key):
		return _meta[key] != null
	var jp = Content.art("%s/%s.json" % [_dir(cid), kind])
	var tp = "%s/%s.png" % [_dir(cid), kind]
	var m = null
	if FileAccess.file_exists(jp) and ResourceLoader.exists(Content.art(tp)):
		m = JSON.parse_string(FileAccess.get_file_as_string(jp))
		_tex[key] = Content.load_art(tp)
	_meta[key] = m
	return m != null

static func has_field(cid: String) -> bool:
	return _load(cid, "field")

static func has_battle(cid: String) -> bool:
	return _load(cid, "battle")

static func field_meta(cid: String) -> Dictionary:
	return _meta.get(cid + "/field", {}) if has_field(cid) else {}

static func battle_meta(cid: String) -> Dictionary:
	return _meta.get(cid + "/battle", {}) if has_battle(cid) else {}

## Field sprite with its feet at `foot` (units). moving=false shows the standing frame.
static func draw_field(ci: CanvasItem, cid: String, dir: String, moving: bool, foot: Vector2, phase: float = -1.0, mod: Color = Color.WHITE) -> void:
	if not has_field(cid):
		return
	var m: Dictionary = _meta[cid + "/field"]
	var t: Texture2D = _tex[cid + "/field"]
	var d = dir if m["rows"].has(dir) else "down"
	var r: Dictionary = m["rows"][d]
	var col = 0
	if moving and int(r["n"]) > 0:
		var ph = phase if phase >= 0.0 else Time.get_ticks_msec() / 1000.0
		col = 1 + int(ph * float(m.get("fps", 10))) % int(r["n"])
	var cw = int(m["cell"][0])
	var chh = int(m["cell"][1])
	UI.native_begin(ci, (foot * UI.U).round() / UI.U)
	ci.draw_texture_rect_region(t, Rect2(-float(m["foot"][0]), -float(m["foot"][1]), cw, chh), Rect2(col * cw, int(r["row"]) * chh, cw, chh), mod)
	UI.native_end(ci)

## Height of the standing sprite in units (for labels above heads, menu rows).
static func field_height(cid: String) -> float:
	var m = field_meta(cid)
	return float(m["foot"][1]) / UI.U if not m.is_empty() else 16.0

## Battle animation frame count and speed.
static func anim_info(cid: String, anim: String) -> Dictionary:
	var m = battle_meta(cid)
	if m.is_empty():
		return {}
	var a = anim
	if not m["anims"].has(a):
		a = {"guard": "idle", "step": "idle", "ult": "cast", "ko": "death", "cast": "attack"}.get(anim, "idle")
		if not m["anims"].has(a):
			a = "idle"
	var info: Dictionary = m["anims"][a].duplicate()
	info["name"] = a
	return info

## Draws battle animation `anim` at time `t` (seconds since it started) with the feet at `foot` (units).
## Non-looping animations hold their last frame ("ko" = the death animation's last frame).
static func draw_battle(ci: CanvasItem, cid: String, anim: String, t: float, foot: Vector2, mod: Color = Color.WHITE, flip: bool = false) -> void:
	if not has_battle(cid):
		return
	var m: Dictionary = _meta[cid + "/battle"]
	var tex: Texture2D = _tex[cid + "/battle"]
	var info = anim_info(cid, "death" if anim == "ko" else anim)
	var n = int(info["n"])
	var f: int
	if anim == "ko":
		f = n - 1
	elif info.get("loop", false):
		f = int(t * float(info["fps"])) % n
	else:
		f = mini(int(t * float(info["fps"])), n - 1)
	var cw = int(m["cell"][0])
	var chh = int(m["cell"][1])
	UI.native_begin(ci, (foot * UI.U).round() / UI.U)
	var fx = float(m["foot"][0])
	var dst = Rect2(-fx, -float(m["foot"][1]), cw, chh)
	if flip:
		dst = Rect2(fx - cw, -float(m["foot"][1]), cw, chh)
		ci.draw_texture_rect_region(tex, Rect2(dst.position + Vector2(cw, 0), Vector2(-cw, chh)), Rect2(f * cw, int(info["row"]) * chh, cw, chh), mod)
	else:
		ci.draw_texture_rect_region(tex, dst, Rect2(f * cw, int(info["row"]) * chh, cw, chh), mod)
	UI.native_end(ci)

## Seconds a non-looping battle animation takes.
static func anim_length(cid: String, anim: String) -> float:
	var info = anim_info(cid, anim)
	return float(info.get("n", 1)) / float(info.get("fps", 10)) if not info.is_empty() else 0.4

## Townsfolk for an NPC sprite key (assets/ext/npcs/npc_map.json): one of the key's candidates, chosen by NPC id.
static var _npc_map = null

static func npc_key(sprite: String, npc_id: String = "") -> String:
	if _npc_map == null:
		var p = "res://assets/ext/npcs/npc_map.json"
		_npc_map = JSON.parse_string(FileAccess.get_file_as_string(p)) if FileAccess.file_exists(p) else {}
	var c: Array = _npc_map.get(sprite, [])
	if c.is_empty():
		return ""
	var h = absi(hash(npc_id)) if npc_id != "" else 0
	return "npcs/" + str(c[h % c.size()])
