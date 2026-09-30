class_name VehicleArt
## World-map vehicles from assets/ext/vehicles/<key>.png/.json (one row per direction, frames across).
## Keys: wayfarer (pre-fault airship), lanternwake (post-fault airship), brackhorn (mount).

static var _cache = {}

static func info(key: String) -> Dictionary:
	if not _cache.has(key):
		var jp = "res://assets/ext/vehicles/%s.json" % key
		var tp = "res://assets/ext/vehicles/%s.png" % key
		if FileAccess.file_exists(jp) and ResourceLoader.exists(tp):
			var m: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(jp))
			m["tex"] = load(tp)
			_cache[key] = m
		else:
			_cache[key] = {}
	return _cache[key]

static func has(key: String) -> bool:
	return not info(key).is_empty()

const DIR8 = {"down": "south", "up": "north", "left": "west", "right": "east"}

## Draws one frame centred horizontally on foot.x with its bottom on foot.y (or centred on foot when center).
## scale is in native pixels per source pixel (1.0 = 1 source px per screen px).
static func draw(ci: CanvasItem, key: String, row_key: String, frame: int, foot: Vector2, scale: float = 1.0, mod: Color = Color.WHITE, center: bool = false) -> bool:
	var m = info(key)
	if m.is_empty() or not m["dirs"].has(row_key):
		return false
	var r: Array = m["dirs"][row_key]
	var cw = float(m["cell"][0])
	var chh = float(m["cell"][1])
	var f = posmod(frame, int(r[1]))
	UI.native_begin(ci, (foot * UI.U).round() / UI.U)
	ci.draw_texture_rect_region(m["tex"], Rect2(-cw * scale / 2.0, -chh * scale * (0.5 if center else 1.0), cw * scale, chh * scale), Rect2(f * cw, int(r[0]) * chh, cw, chh), mod)
	UI.native_end(ci)
	return true

static func fps(key: String) -> float:
	return float(info(key).get("fps", 8))
