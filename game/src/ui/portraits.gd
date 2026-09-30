class_name Portraits
extends RefCounted
## Dialogue / menu portraits. Overhaul heroes have a native-resolution head-and-shoulders crop
## (res://assets/heroes/<id>/portrait.png, square, drawn 1:1 at 960x720); other speakers keep the old 40px
## three-expression strips (res://assets/sprites/portraits/<key>.png, drawn at unit scale).

static var _cache = {}

static func _load(path: String) -> Texture2D:
	if not _cache.has(path):
		_cache[path] = Content.load_art(path) if ResourceLoader.exists(Content.art(path)) else null
	return _cache[path]

static func hero_tex(key: String) -> Texture2D:
	var t = _load("res://assets/heroes/%s/portrait.png" % key)
	return t if t != null else _load("res://assets/portraits/%s.png" % key)

static func old_tex(key: String) -> Texture2D:
	return _load("res://assets/sprites/portraits/%s.png" % key)

static func has(key: String) -> bool:
	return key != "" and (hero_tex(key) != null or old_tex(key) != null)

## Draws the portrait for `key` filling the square `r` (units).
static func draw(ci: CanvasItem, key: String, r: Rect2, expr: String = "neutral") -> void:
	var h = hero_tex(key)
	if h != null:
		UI.native_begin(ci, r.position)
		ci.draw_texture_rect(h, Rect2(Vector2.ZERO, r.size * UI.U), false)
		UI.native_end(ci)
		return
	var t = old_tex(key)
	if t == null:
		return
	var col = {"neutral": 0, "concern": 1, "determined": 2}.get(expr, 0)
	var fw = 40
	if t.get_width() < 120:
		col = 0
	ci.draw_texture_rect_region(t, r, Rect2(col * fw, 0, fw, fw))
