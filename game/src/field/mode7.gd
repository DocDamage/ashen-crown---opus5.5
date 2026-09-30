class_name Mode7
extends RefCounted
## World-map camera and ground plane (FF6 Mode-7 feel, always on for the world maps).
## The ground is the baked world art (assets/ext/maps48/<MAP>.json "chunks") drawn by shaders/mode7.gdshader as a
## tilted plane; landmarks, actors and vehicles stay upright sprites, scaled by their depth (billboards).
## Tilt follows the vehicle: gentle on foot, stronger on the Brackhorn, full on the airship; the camera turns
## (page_l / page_r) only while flying. Units are field units (16 per map cell); z is height above the ground.

const VIEW := Vector2(320, 240)
const FOCAL := 240.0
const CENTER := Vector2(160, 124)
# pitch (degrees below the horizon), distance to the focus (scale at the focus = FOCAL / dist)
const PROFILE := {
	"foot": {"pitch": 58.0, "dist": 250.0},
	"mount": {"pitch": 46.0, "dist": 285.0},
	"ship": {"pitch": 27.0, "dist": 330.0},
	"flat": {"pitch": 90.0, "dist": 240.0},
}

static var _cache_id := ""
static var _cache_tex: Texture2DArray = null
static var _mat: ShaderMaterial = null
static var _cache_outside := Color(0.09, 0.17, 0.36)

var map_id := ""
var tex: Texture2DArray = null
var chunk_px := 2112
var chunks_x := 1
var chunks_y := 1
var world_units := Vector2.ZERO
var deep := false

var pitch := 58.0
var dist := 250.0
var yaw := 0.0             # radians; 0 = north up
var focus := Vector2.ZERO
var cam_pos := Vector3.ZERO
var fwd := Vector3.ZERO
var right := Vector3.ZERO
var up := Vector3.ZERO
var tint := Color(1, 1, 1, 1)

static func make(art: Art48, id: String) -> Mode7:
	if art == null or not art.data.get("mode7", false) or art.data.get("chunks", []).is_empty():
		return null
	var m = Mode7.new()
	m.map_id = id
	m.deep = id.begins_with("DEEP")
	m.world_units = Vector2(float(art.data["w"]) * 16.0, float(art.data["h"]) * 16.0)
	if not m._load(art):
		return null
	m._basis()
	return m

func _load(art: Art48) -> bool:
	var chunks: Array = art.data["chunks"]
	chunk_px = int(chunks[0][3])
	var xs = {}
	var ys = {}
	for c in chunks:
		xs[int(c[1])] = true
		ys[int(c[2])] = true
	chunks_x = xs.size()
	chunks_y = ys.size()
	if _cache_id == map_id and _cache_tex != null:
		tex = _cache_tex
		return true
	# one map's array at a time (the world maps are large): drop the previous one first
	_cache_tex = null
	_cache_id = ""
	var imgs: Array[Image] = []
	imgs.resize(chunks_x * chunks_y)
	for c in chunks:
		var p = "res://assets/ext/maps48/%s" % c[0]
		if not ResourceLoader.exists(p):
			push_warning("mode7: missing chunk %s" % p)
			return false
		var t: Texture2D = load(p)
		var im: Image = t.get_image()
		if im.is_compressed():
			im.decompress()
		im.convert(Image.FORMAT_RGBA8)
		if im.get_width() != chunk_px or im.get_height() != chunk_px:
			var full = Image.create(chunk_px, chunk_px, false, Image.FORMAT_RGBA8)
			full.blit_rect(im, Rect2i(0, 0, im.get_width(), im.get_height()), Vector2i.ZERO)
			im = full
		if int(c[1]) == 0 and int(c[2]) == 0:
			_cache_outside = im.get_pixel(4, 4)
		im.generate_mipmaps()
		var i = int(c[2]) / chunk_px * chunks_x + int(c[1]) / chunk_px
		imgs[i] = im
	tex = Texture2DArray.new()
	tex.create_from_images(imgs)
	_cache_tex = tex
	_cache_id = map_id
	return true

static func material() -> ShaderMaterial:
	if _mat == null:
		_mat = ShaderMaterial.new()
		_mat.shader = load("res://shaders/mode7.gdshader")
	return _mat

func profile_key(vehicle: String, riding: bool) -> String:
	if Settings.get_v("world_view") == "flat":
		return "flat"
	if vehicle == "ship":
		return "ship"
	return "mount" if riding else "foot"

## Follows the focus; eases pitch/distance toward the vehicle's profile; turns only while flying.
func update(delta: float, focus_units: Vector2, key: String, turn: float) -> void:
	focus = focus_units
	var p: Dictionary = PROFILE.get(key, PROFILE["foot"])
	var k = clampf(delta * 3.0, 0.0, 1.0)
	pitch = lerpf(pitch, float(p["pitch"]), k)
	dist = lerpf(dist, float(p["dist"]), k)
	if key == "ship":
		yaw = wrapf(yaw + turn * delta * 1.6, -PI, PI)
	else:
		yaw = lerp_angle(yaw, 0.0, k)
	_basis()

func snap(focus_units: Vector2, key: String) -> void:
	var p: Dictionary = PROFILE.get(key, PROFILE["foot"])
	pitch = float(p["pitch"])
	dist = float(p["dist"])
	if key != "ship":
		yaw = 0.0
	focus = focus_units
	_basis()

func _basis() -> void:
	var ph = deg_to_rad(pitch)
	var fh = Vector2(sin(yaw), -cos(yaw))
	fwd = Vector3(fh.x * cos(ph), fh.y * cos(ph), -sin(ph))
	right = Vector3(cos(yaw), sin(yaw), 0.0)
	up = Vector3(fh.x * sin(ph), fh.y * sin(ph), cos(ph))
	cam_pos = Vector3(focus.x, focus.y, 0.0) - fwd * dist

## World point (units, height z) -> [screen position (units), scale, depth]; depth <= 0 means behind the camera.
func project(p: Vector2, z: float = 0.0) -> Array:
	var d = Vector3(p.x, p.y, z) - cam_pos
	var zc = d.dot(fwd)
	if zc <= 1.0:
		return [Vector2(-9999, -9999), 0.0, zc]
	var s = FOCAL / zc
	return [CENTER + Vector2(d.dot(right), -d.dot(up)) * s, s, zc]

## Screen point (units) -> ground point (units), or null above the horizon.
func unproject(s: Vector2):
	var ray = fwd * FOCAL + right * (s.x - CENTER.x) - up * (s.y - CENTER.y)
	if ray.z >= -0.001:
		return null
	var t = -cam_pos.z / ray.z
	return Vector2(cam_pos.x + ray.x * t, cam_pos.y + ray.y * t)

## Map-relative step direction for a screen-relative input while the camera is turned.
func turn_dir(d: String) -> String:
	if absf(yaw) < 0.01:
		return d
	var v = {"up": Vector2(0, -1), "down": Vector2(0, 1), "left": Vector2(-1, 0), "right": Vector2(1, 0)}[d]
	var r = v.rotated(yaw)
	if absf(r.x) > absf(r.y):
		return "right" if r.x > 0 else "left"
	return "down" if r.y > 0 else "up"

func apply(mat: ShaderMaterial) -> void:
	mat.set_shader_parameter("ground", tex)
	mat.set_shader_parameter("cam_pos", cam_pos)
	mat.set_shader_parameter("fwd", fwd)
	mat.set_shader_parameter("right", right)
	mat.set_shader_parameter("up", up)
	mat.set_shader_parameter("focal", FOCAL)
	mat.set_shader_parameter("center", CENTER)
	mat.set_shader_parameter("view", VIEW)
	mat.set_shader_parameter("world_units", world_units)
	mat.set_shader_parameter("chunk_units", float(chunk_px) / 3.0)
	mat.set_shader_parameter("chunks_x", chunks_x)
	mat.set_shader_parameter("chunks_y", chunks_y)
	if deep:
		mat.set_shader_parameter("outside", _cache_outside)
		mat.set_shader_parameter("sky_top", Color(0.02, 0.01, 0.02))
		mat.set_shader_parameter("sky_low", Color(0.10, 0.05, 0.05))
		mat.set_shader_parameter("haze", Color(0.10, 0.05, 0.05))
		mat.set_shader_parameter("haze_near", 500.0)
		mat.set_shader_parameter("haze_far", 1500.0)
		mat.set_shader_parameter("haze_max", 0.9)
	else:
		mat.set_shader_parameter("outside", _cache_outside)
		mat.set_shader_parameter("sky_top", Color(0.30, 0.46, 0.72))
		mat.set_shader_parameter("sky_low", Color(0.74, 0.82, 0.90))
		mat.set_shader_parameter("haze", Color(0.62, 0.72, 0.84))
		mat.set_shader_parameter("haze_near", 900.0)
		mat.set_shader_parameter("haze_far", 2600.0)
		mat.set_shader_parameter("haze_max", 0.75)
	mat.set_shader_parameter("tint", tint)
