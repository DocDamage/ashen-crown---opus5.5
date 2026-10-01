class_name BattleStage3D
extends RefCounted
## HD-2D battle stage: the background becomes layered planes in a 3D scene (the owner's parallax packs where a set
## fits the battle's background, otherwise the painted backdrop on one far plane), seen by a Camera3D driven by
## Phantom Camera 3D. The battle keeps its 2D layout: every battler's foot point is lifted onto the stage floor
## once (through the resting camera), and each frame it is projected back through the live camera, so at rest
## nothing moves, and when the camera pushes in on an attack the battlers, effects and backdrop layers all move with
## real perspective and parallax.
##
## Screen space is the battle's 320x168 area (logical units); the viewport is 960x504.

const AREA := Vector2(320, 168)
const VP := Vector2i(960, 504)
const PITCH := 28.0
const FOV := 40.0
const DIST := 14.0

var vp: SubViewport
var root: Node3D
var cam: Camera3D
var host: Node
var pcam_rest: Node3D
var pcam_act: Node3D
var focus_rest: Node3D
var focus_act: Node3D
var layers: Array = []
var rest_xf: Transform3D
var _floor_cache := {}
var acting := false

## background key (formation "bg") -> parallax set under assets/ext/parallax/<set>/ (tools/art/install_parallax.py)
const BG_SETS := {
	"field_r01": "rural", "field_r02": "rural", "field_r03": "ocean", "field_r04": "winter", "field_r05": "desert",
	"field_post": "city_destroyed", "grove": "forest", "grove_flood": "forest", "sky": "skies", "winter": "winter",
	"reef": "ocean", "crown": "city_night", "dais": "moon", "crown_core": "moon",
}

static func make(parent: Node, bg_key: String, fallback_bg: Texture2D) -> BattleStage3D:
	var s = BattleStage3D.new()
	s._build(parent, bg_key, fallback_bg)
	return s

func _build(parent: Node, bg_key: String, fallback_bg: Texture2D) -> void:
	vp = SubViewport.new()
	vp.name = "BattleStage3D"
	vp.size = VP
	vp.own_world_3d = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	parent.add_child(vp)
	root = Node3D.new()
	vp.add_child(root)
	var we = WorldEnvironment.new()
	var env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color8(10, 8, 14)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color.WHITE
	env.glow_enabled = true
	env.glow_intensity = 0.4
	env.glow_hdr_threshold = 0.95
	we.environment = env
	root.add_child(we)
	cam = Camera3D.new()
	cam.fov = FOV
	cam.near = 0.5
	cam.far = 400.0
	cam.current = true
	root.add_child(cam)
	focus_rest = Node3D.new()
	root.add_child(focus_rest)
	focus_act = Node3D.new()
	root.add_child(focus_act)
	var pr = deg_to_rad(PITCH)
	var off = Vector3(0, sin(pr) * DIST, cos(pr) * DIST)
	cam.position = off
	cam.rotation = Vector3(-pr, 0, 0)
	rest_xf = cam.global_transform if cam.is_inside_tree() else Transform3D(Basis.from_euler(Vector3(-pr, 0, 0)), off)
	var host_script = load("res://addons/phantom_camera/scripts/phantom_camera_host/phantom_camera_host.gd")
	var pcam_script = load("res://addons/phantom_camera/scripts/phantom_camera/phantom_camera_3d.gd")
	if host_script != null and pcam_script != null and Engine.has_singleton("PhantomCameraManager"):
		host = host_script.new()
		cam.add_child(host)
		pcam_rest = _pcam(pcam_script, focus_rest, off, pr, 10)
		pcam_act = _pcam(pcam_script, focus_act, off * 0.8, pr, 0)
	_backdrop(bg_key, fallback_bg)

func _pcam(script, target: Node3D, off: Vector3, pr: float, prio: int) -> Node3D:
	var p = script.new()
	root.add_child(p)
	p.rotation = Vector3(-pr, 0, 0)
	p.set("follow_mode", 2)
	p.set("follow_target", target)
	p.set("follow_offset", off)
	p.set("tween_on_load", false)
	p.set("priority", prio)
	var tw = p.get("tween_resource")
	if tw != null:
		tw.set("duration", 0.32)
	return p

## Far planes facing the camera; layer 0 is the farthest. Each plane is sized to fill the resting view at its depth,
## a little wider so camera moves never show its edge.
func _backdrop(bg_key: String, fallback_bg: Texture2D) -> void:
	var set_name: String = BG_SETS.get(bg_key, "")
	var files: Array = []
	if set_name != "":
		var jp = "res://assets/ext/parallax/%s/set.json" % set_name
		if FileAccess.file_exists(jp):
			var d = JSON.parse_string(FileAccess.get_file_as_string(jp))
			for L in d.get("layers", []):
				var tp = "res://assets/ext/parallax/%s/%s" % [set_name, L["file"]]
				if ResourceLoader.exists(tp):
					files.append([load(tp), float(L.get("depth", 1.0)), float(L.get("y", 0.0))])
	if files.is_empty() and fallback_bg != null:
		files.append([fallback_bg, 1.0, 0.0])
	var n = files.size()
	for i in range(n):
		var tex: Texture2D = files[i][0]
		# depth 1.0 = farthest (60 units behind the stage centre), nearer layers come forward to 6 units
		var dep = lerpf(6.0, 60.0, clampf(files[i][1], 0.0, 1.0))
		_plane(tex, dep, files[i][2], i)

func _plane(tex: Texture2D, depth_back: float, y_off: float, order: int) -> void:
	var pr = deg_to_rad(PITCH)
	var fwd = Vector3(0, -sin(pr), -cos(pr))
	var centre = rest_xf.origin + fwd * (DIST + depth_back)
	var dist = DIST + depth_back
	var vh = 2.0 * dist * tan(deg_to_rad(FOV) / 2.0) * 1.25
	var aspect = float(tex.get_width()) / maxf(1.0, float(tex.get_height()))
	var vw = maxf(vh * aspect, vh * float(VP.x) / VP.y * 1.25)
	var vh2 = vw / aspect
	var mat = StandardMaterial3D.new()
	mat.albedo_texture = tex
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	mat.render_priority = order
	mat.no_depth_test = true
	var q = QuadMesh.new()
	q.size = Vector2(vw, vh2)
	var mi = MeshInstance3D.new()
	mi.mesh = q
	mi.material_override = mat
	mi.basis = rest_xf.basis
	mi.position = centre + rest_xf.basis.y * (y_off * vh2)
	root.add_child(mi)
	layers.append(mi)

## Stage floor point (y = 0) under a battle-screen point, through the resting camera.
func floor_of(p: Vector2) -> Vector3:
	var key = Vector2i(roundi(p.x * 4.0), roundi(p.y * 4.0))
	if _floor_cache.has(key):
		return _floor_cache[key]
	var sp = p * 3.0
	var f = cam.fov
	var vfov = deg_to_rad(f)
	var fy = (VP.y / 2.0) / tan(vfov / 2.0)
	var dir_cam = Vector3((sp.x - VP.x / 2.0) / fy, -(sp.y - VP.y / 2.0) / fy, -1.0).normalized()
	var dirw = rest_xf.basis * dir_cam
	var o = rest_xf.origin
	var t = -o.y / dirw.y if absf(dirw.y) > 0.0001 else 1000.0
	if t <= 0.0:
		t = 1000.0
	var hit = o + dirw * t
	_floor_cache[key] = hit
	return hit

## The live-camera transform for something standing at battle-screen point p (identity while the camera rests).
func xf(p: Vector2) -> Transform2D:
	var w = floor_of(p)
	var ct = cam.global_transform
	var d_now = -(w - ct.origin).dot(ct.basis.z)
	var d_rest = -(w - rest_xf.origin).dot(rest_xf.basis.z)
	if d_now <= 0.05:
		return Transform2D.IDENTITY
	var q = cam.unproject_position(w) / 3.0
	var s = d_rest / d_now
	if absf(s - 1.0) < 0.002 and q.distance_to(p) < 0.3:
		return Transform2D.IDENTITY
	return Transform2D(0.0, Vector2(s, s), 0.0, q - p * s)

func point(p: Vector2) -> Vector2:
	return xf(p) * p

## Push in on an action: the action camera frames the midpoint of attacker and target; release returns to rest.
func act(a: Vector2, b: Vector2) -> void:
	if pcam_act == null:
		return
	var fa = floor_of(a)
	var fb = floor_of(b)
	focus_act.position = (fa + fb) * 0.5
	pcam_act.set("priority", 20)
	acting = true

func release() -> void:
	if pcam_act == null:
		return
	pcam_act.set("priority", 0)
	acting = false

func texture() -> Texture2D:
	return vp.get_texture()
