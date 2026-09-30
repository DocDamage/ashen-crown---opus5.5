class_name WorldHud
extends RefCounted
## World-map minimap (top right) and full map screen (Map button), both with fog of war and markers.
## The map image is baked by tools/world2/bake.py (<MAP>_mini.png, 3 native px per cell) with the named places.
## Fog: one byte per cell in Game.S["fog"][map] (base64), revealed around the party as it travels.

const MINI_RECT := Rect2(236, 6, 78, 58)       # units
const REVEAL := 7                                 # cells

var map_id := ""
var w := 0
var h := 0
var scale := 3
var tex: Texture2D = null
var places: Array = []
var fog: PackedByteArray = PackedByteArray()
var fog_img: Image = null
var fog_tex: ImageTexture = null
var _dirty := false
var _dirty_t := 0.0

static func make(art: Art48, id: String) -> WorldHud:
	if art == null or art.data.get("mini", "") == "":
		return null
	var p = "res://assets/ext/maps48/%s" % art.data["mini"]
	if not ResourceLoader.exists(p):
		return null
	var hd = WorldHud.new()
	hd.map_id = id
	hd.w = int(art.data["w"])
	hd.h = int(art.data["h"])
	hd.scale = int(art.data.get("mini_scale", 3))
	hd.tex = load(p)
	hd.places = art.data.get("places", [])
	hd._load_fog()
	return hd

## Fallback minimap from the collision grid (a world map without baked art, e.g. UNDERSEA before its bake);
## places are the map's location entities with a name.
static func make_grid(mp: Dictionary, id: String) -> WorldHud:
	if mp.is_empty() or int(mp.get("w", 0)) <= 0:
		return null
	var hd = WorldHud.new()
	hd.map_id = id
	hd.w = int(mp["w"])
	hd.h = int(mp["h"])
	hd.scale = 3
	var im = Image.create(hd.w * 3, hd.h * 3, false, Image.FORMAT_RGBA8)
	for y in range(hd.h):
		var row = String(mp["grid"][y])
		for x in range(hd.w):
			var c: Color = Mode7.GRID_COLORS.get(mp["legend"].get(row[x], "void"), Color8(60, 60, 70))
			if id == "UNDERSEA":
				c = c.lerp(Color8(16, 70, 96), 0.35)
			im.fill_rect(Rect2i(x * 3, y * 3, 3, 3), c)
	hd.tex = ImageTexture.create_from_image(im)
	for e in mp.get("entities", []):
		if e["type"] == "location":
			hd.places.append([e["id"], e.get("name", "") if e.get("name", "") != "" else e["id"], e["x"], e["y"], "town"])
	hd._load_fog()
	return hd

func _fog_key() -> String:
	# the World of Ruin keeps the old world's knowledge of the land: pre and post share their fog
	return map_id.replace("_POST", "")

func _load_fog() -> void:
	var all: Dictionary = Game.S.get("fog", {})
	var s: String = all.get(_fog_key(), "")
	fog = Marshalls.base64_to_raw(s) if s != "" else PackedByteArray()
	if fog.size() != w * h:
		fog = PackedByteArray()
		fog.resize(w * h)
	fog_img = Image.create(w, h, false, Image.FORMAT_LA8)
	for y in range(h):
		for x in range(w):
			fog_img.set_pixel(x, y, Color(0, 0, 0, 0.0 if fog[y * w + x] else 1.0))
	fog_tex = ImageTexture.create_from_image(fog_img)

func _save_fog() -> void:
	if not Game.S.has("fog"):
		Game.S["fog"] = {}
	Game.S["fog"][_fog_key()] = Marshalls.raw_to_base64(fog)

func reveal(t: Vector2i, r: int = REVEAL) -> void:
	var changed = false
	for y in range(maxi(0, t.y - r), mini(h, t.y + r + 1)):
		for x in range(maxi(0, t.x - r), mini(w, t.x + r + 1)):
			if (x - t.x) * (x - t.x) + (y - t.y) * (y - t.y) > r * r:
				continue
			var i = y * w + x
			if fog[i] == 0:
				fog[i] = 1
				fog_img.set_pixel(x, y, Color(0, 0, 0, 0))
				changed = true
	if changed:
		_dirty = true
		_save_fog()

func tick(delta: float) -> void:
	_dirty_t -= delta
	if _dirty and _dirty_t <= 0.0:
		fog_tex.update(fog_img)
		_dirty = false
		_dirty_t = 0.25

func known(x: int, y: int) -> bool:
	return x >= 0 and y >= 0 and x < w and y < h and fog[y * w + x] != 0

## Quest markers: active quests' locations, plus the journal destination when it names a place.
func markers() -> Array:
	var out = []
	var want = {}
	for qid in Game.S.get("quests", {}):
		var st = Game.S["quests"][qid]
		var status = str(st.get("state", "")) if typeof(st) == TYPE_DICTIONARY else str(st)
		if status != "ACTIVE" and status != "RESOLUTION_READY":
			continue
		var q = Content.data.get("quests", {}).get(qid, {})
		if q.get("location", "") != "":
			want["L_" + str(q["location"])] = true
	var dest: String = str(Game.S.get("journal", {}).get("destination", ""))
	for p in places:
		if want.has(p[0]) or (dest != "" and str(p[1]) == dest):
			out.append(p)
	return out

func _icon_col(kind: String) -> Color:
	if kind in ["town", "city", "village", "port", "town_ash", "town_cliff", "town_desert", "city_delver", "city_builder", "city_dead", "camp"]:
		return Color(0.98, 0.9, 0.55)
	if kind in ["cave", "tower", "castle", "castle_magic", "castle_red", "castle_ice", "crypt", "tomb", "mine", "pit", "vault", "palace", "heart", "throat", "gate_abyss", "chasm", "breach", "fort", "city_dark"]:
		return Color(0.95, 0.45, 0.4)
	return Color(0.7, 0.85, 1.0)

func draw_mini(ci: CanvasItem, player: Vector2, yaw: float, t: float) -> void:
	var r = MINI_RECT
	ci.draw_rect(r.grow(1), Color(0, 0, 0, 0.55))
	# area around the player, 1 unit per cell
	var src = Rect2(player.x - r.size.x / 2.0, player.y - r.size.y / 2.0, r.size.x, r.size.y)
	var cl = src.intersection(Rect2(0, 0, w, h))
	if cl.size.x > 0 and cl.size.y > 0:
		var dst = Rect2(r.position + (cl.position - src.position), cl.size)
		ci.draw_texture_rect_region(tex, dst, Rect2(cl.position * scale, cl.size * scale))
		ci.draw_texture_rect_region(fog_tex, dst, cl, Color(0.03, 0.03, 0.06, 0.92))
	for p in places:
		var pp = Vector2(p[2], p[3]) - src.position
		if pp.x < 1 or pp.y < 1 or pp.x > r.size.x - 2 or pp.y > r.size.y - 2 or not known(int(p[2]), int(p[3])):
			continue
		ci.draw_rect(Rect2(r.position + pp - Vector2(1, 1), Vector2(2, 2)), _icon_col(str(p[4])))
	for p in markers():
		var mp = Vector2(p[2], p[3]) - src.position
		mp = mp.clamp(Vector2(2, 2), r.size - Vector2(3, 3))
		if int(t * 3.0) % 2 == 0:
			ci.draw_rect(Rect2(r.position + mp - Vector2(1.5, 1.5), Vector2(3, 3)), Color(1, 0.35, 0.3))
	_arrow(ci, r.position + r.size / 2.0, yaw, 3.0)
	ci.draw_rect(r.grow(1), Color(0.8, 0.75, 0.6, 0.7), false, 1.0)

func _arrow(ci: CanvasItem, c: Vector2, yaw: float, s: float) -> void:
	var f = Vector2(sin(yaw), -cos(yaw))
	var rt = Vector2(cos(yaw), sin(yaw))
	ci.draw_colored_polygon(PackedVector2Array([c + f * s * 1.4, c - f * s + rt * s, c - f * s * 0.4, c - f * s - rt * s]), Color(1, 1, 1))

func draw_full(ci: CanvasItem, player: Vector2, t: float, region_name: String) -> void:
	ci.draw_rect(Rect2(0, 0, 320, 240), Color(0.02, 0.02, 0.05, 0.92))
	var fit = minf(300.0 / w, 200.0 / h)
	var size = Vector2(w, h) * fit
	var o = Vector2((320 - size.x) / 2.0, 30)
	ci.draw_texture_rect(tex, Rect2(o, size), false)
	ci.draw_texture_rect(fog_tex, Rect2(o, size), false, Color(0.03, 0.03, 0.06, 0.94))
	ci.draw_rect(Rect2(o, size).grow(1), Color(0.8, 0.75, 0.6, 0.6), false, 1.0)
	for p in places:
		if not known(int(p[2]), int(p[3])):
			continue
		var pp = o + Vector2(p[2] + 0.5, p[3] + 0.5) * fit
		ci.draw_rect(Rect2(pp - Vector2(1.5, 1.5), Vector2(3, 3)), _icon_col(str(p[4])))
	for p in markers():
		var mp = o + Vector2(p[2] + 0.5, p[3] + 0.5) * fit
		if int(t * 3.0) % 2 == 0:
			ci.draw_rect(Rect2(mp - Vector2(2.5, 2.5), Vector2(5, 5)), Color(1, 0.35, 0.3))
		UI.text(ci, mp + Vector2(4, -6), str(p[1]), Color(1, 0.8, 0.75))
	var pl = o + (player + Vector2(0.5, 0.5)) * fit
	if int(t * 4.0) % 2 == 0:
		ci.draw_rect(Rect2(pl - Vector2(2, 2), Vector2(4, 4)), Color(1, 1, 1))
	UI.text(ci, Vector2(12, 8), region_name)
	var near = _nearest_known(player)
	if not near.is_empty():
		UI.text(ci, Vector2(12, 222), "Nearest: " + str(near[1]))

func _nearest_known(player: Vector2) -> Array:
	var best = []
	var bd = 1e9
	for p in places:
		if not known(int(p[2]), int(p[3])) or not Game.S.get("discovered", []).has(p[0]):
			continue
		var d = Vector2(p[2], p[3]).distance_squared_to(player)
		if d < bd:
			bd = d
			best = p
	return best
