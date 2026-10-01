class_name Stage3D
extends RefCounted
## HD-2D stage for field maps (towns, dungeons, interiors). A real 3D scene renders the map's baked ground art on a
## lit ground plane, under a tilted perspective Camera3D driven by Phantom Camera 3D (addons/phantom_camera). The
## field keeps drawing every upright thing (heroes, NPCs, props, buildings, trees, chests) with its own 2D code; each is
## placed through project() at its foot point so it stands upright, scales with depth and sorts by distance - the
## HD-2D look - while all the existing art, logic and QA routes stay as they are.
##
## Units: field units (16 per map cell, 320x240 view). World: 1 unit per map cell; x = east, z = south, y = up.

const VIEW := Vector2(320, 240)
const CHUNK := 8                     # ground chunk size in cells (each chunk gets the nearest lights)

var vp: SubViewport                  # ground and lights
var vp_over: SubViewport             # the map's "over" layer (canopies, bridges overhead), drawn above actors
var root: Node3D
var cam: Camera3D
var cam_over: Camera3D
var host: Node
var pcam: Node3D
var focus: Node3D
var shot_focus: Node3D
var pcam_shot: Node3D
var sun: DirectionalLight3D
var env: Environment
var ground_root: Node3D
var over_mesh: MeshInstance3D
var lamps: Array = []                # OmniLight3D
var w := 0
var h := 0
var profile := {}
var ref_dist := 1.0

## Camera framing per map kind: pitch (degrees below horizontal), vertical FOV, distance to the focus point.
const PROFILES := {
	"town": {"pitch": 52.0, "fov": 30.0, "dist": 29.0},
	"dungeon": {"pitch": 56.0, "fov": 28.0, "dist": 30.0},
	"interior": {"pitch": 60.0, "fov": 26.0, "dist": 33.0},
}

static func make(parent: Node) -> Stage3D:
	var s = Stage3D.new()
	s._build(parent)
	return s

func _build(parent: Node) -> void:
	vp = SubViewport.new()
	vp.name = "HD2DStage"
	vp.size = Vector2i(960, 720)
	vp.own_world_3d = true
	vp.transparent_bg = false
	vp.msaa_3d = Viewport.MSAA_DISABLED
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	parent.add_child(vp)
	root = Node3D.new()
	vp.add_child(root)
	var we = WorldEnvironment.new()
	env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color8(8, 7, 12)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(1, 1, 1)
	env.ambient_light_energy = 1.0
	env.fog_enabled = true
	env.fog_light_color = Color8(20, 18, 28)
	env.fog_density = 0.012
	env.glow_enabled = true
	env.glow_intensity = 0.55
	env.glow_bloom = 0.08
	env.glow_hdr_threshold = 0.9
	we.environment = env
	root.add_child(we)
	sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-60, -30, 0)
	sun.light_energy = 0.0
	root.add_child(sun)
	ground_root = Node3D.new()
	root.add_child(ground_root)
	cam = Camera3D.new()
	cam.cull_mask = 1
	cam.current = true
	root.add_child(cam)
	focus = Node3D.new()
	focus.name = "Focus"
	root.add_child(focus)
	# Phantom Camera: a host on the real camera and one follow camera on the focus point (scenes can add more and
	# raise their priority for framed shots; the host tweens between them)
	var host_script = load("res://addons/phantom_camera/scripts/phantom_camera_host/phantom_camera_host.gd")
	var pcam_script = load("res://addons/phantom_camera/scripts/phantom_camera/phantom_camera_3d.gd")
	if host_script != null and pcam_script != null and Engine.has_singleton("PhantomCameraManager"):
		host = host_script.new()
		host.name = "PhantomCameraHost"
		cam.add_child(host)
		pcam = pcam_script.new()
		pcam.name = "FieldPCam"
		root.add_child(pcam)
		_prio(pcam, 10)
		pcam.set("follow_mode", 2)            # SIMPLE: follow with an offset
		pcam.set("follow_target", focus)
		pcam.set("follow_damping", true)
		pcam.set("follow_damping_value", Vector3(0.12, 0.12, 0.12))
		pcam.set("tween_on_load", false)
		# scripted shots (director "camera" command): a second camera the host tweens to and back
		shot_focus = Node3D.new()
		root.add_child(shot_focus)
		pcam_shot = pcam_script.new()
		pcam_shot.name = "ShotPCam"
		root.add_child(pcam_shot)
		_prio(pcam_shot, 0)
		pcam_shot.set("follow_mode", 2)
		pcam_shot.set("follow_target", shot_focus)
		pcam_shot.set("tween_on_load", false)
		var tw = pcam_shot.get("tween_resource")
		if tw != null:
			tw.set("duration", 1.1)
	# the over layer: a second viewport sharing the world, seeing only layer 2
	vp_over = SubViewport.new()
	vp_over.name = "HD2DOver"
	vp_over.size = vp.size
	vp_over.world_3d = vp.world_3d
	vp_over.transparent_bg = true
	vp_over.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	parent.add_child(vp_over)
	cam_over = Camera3D.new()
	cam_over.cull_mask = 2
	cam_over.current = true
	vp_over.add_child(cam_over)
	set_profile("town")

func set_profile(kind: String) -> void:
	profile = PROFILES.get(kind, PROFILES["town"])
	var pr = deg_to_rad(float(profile["pitch"]))
	var d = float(profile["dist"])
	cam.fov = float(profile["fov"])
	cam_over.fov = cam.fov
	cam.near = 1.0
	cam.far = 200.0
	cam_over.near = cam.near
	cam_over.far = cam.far
	var off = Vector3(0, sin(pr) * d, cos(pr) * d)
	cam.rotation = Vector3(-pr, 0, 0)
	if pcam != null:
		pcam.rotation = Vector3(-pr, 0, 0)
		pcam.set("follow_offset", off)
	ref_dist = d

## Scripted shot: frame a field point (units) closer or farther (zoom < 1 = closer), tilted by pitch_add degrees.
func shot(center_units: Vector2, zoom: float = 0.7, pitch_add: float = -8.0) -> void:
	if pcam_shot == null:
		return
	var pr = deg_to_rad(float(profile["pitch"]) + pitch_add)
	var d = float(profile["dist"]) * zoom
	shot_focus.position = Vector3(center_units.x / 16.0, 0.0, center_units.y / 16.0)
	pcam_shot.rotation = Vector3(-pr, 0, 0)
	pcam_shot.set("follow_offset", Vector3(0, sin(pr) * d, cos(pr) * d))
	_prio(pcam_shot, 30)

func end_shot() -> void:
	if pcam_shot != null:
		_prio(pcam_shot, 0)

## A map's ground (and over layer) as lit chunks; lamps = [[x_units, y_units, Color, radius_cells], ...].
func set_map(ground: Texture2D, over: Texture2D, w_cells: int, h_cells: int, lamp_list: Array, kind: String, dark: bool) -> void:
	w = w_cells
	h = h_cells
	end_shot()
	for c in ground_root.get_children():
		c.queue_free()
	if over_mesh != null:
		over_mesh.queue_free()
		over_mesh = null
	for l in lamps:
		l.queue_free()
	lamps.clear()
	set_profile(kind)
	if ground != null:
		var mat = StandardMaterial3D.new()
		mat.albedo_texture = ground
		mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		mat.roughness = 1.0
		mat.specular_mode = BaseMaterial3D.SPECULAR_DISABLED
		for cy in range(0, h, CHUNK):
			for cx in range(0, w, CHUNK):
				var cw = mini(CHUNK, w - cx)
				var chh = mini(CHUNK, h - cy)
				ground_root.add_child(_quad(cx, cy, cw, chh, mat, 0.0, 1))
	if over != null:
		var om = StandardMaterial3D.new()
		om.albedo_texture = over
		om.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		om.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
		om.alpha_scissor_threshold = 0.5
		om.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		over_mesh = _quad(0, 0, w, h, om, 0.0, 2)
		root.add_child(over_mesh)
	for L in lamp_list:
		var o = OmniLight3D.new()
		o.position = Vector3(float(L[0]) / 16.0, 0.9, float(L[1]) / 16.0)
		o.light_color = L[2]
		o.omni_range = float(L[3])
		o.omni_attenuation = 1.4
		o.light_energy = 1.6 if dark else 1.1
		root.add_child(o)
		lamps.append(o)

func _quad(cx: int, cy: int, cw: int, chh: int, mat: Material, y: float, layer: int) -> MeshInstance3D:
	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var u0 = float(cx) / w
	var v0 = float(cy) / h
	var u1 = float(cx + cw) / w
	var v1 = float(cy + chh) / h
	var p = [Vector3(cx, y, cy), Vector3(cx + cw, y, cy), Vector3(cx + cw, y, cy + chh), Vector3(cx, y, cy + chh)]
	var uv = [Vector2(u0, v0), Vector2(u1, v0), Vector2(u1, v1), Vector2(u0, v1)]
	for i in [0, 1, 2, 0, 2, 3]:
		st.set_normal(Vector3.UP)
		st.set_uv(uv[i])
		st.add_vertex(p[i])
	var mi = MeshInstance3D.new()
	mi.mesh = st.commit()
	mi.material_override = mat
	mi.layers = layer
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mi

## Lighting by the hour (outdoors) or the map's mood (indoors / dark dungeons).
func set_light(ambient: Color, energy: float, sun_color: Color, sun_energy: float) -> void:
	env.ambient_light_color = ambient
	env.ambient_light_energy = energy
	sun.light_color = sun_color
	sun.light_energy = sun_energy

## Moves the follow point (field units, the view centre the 2D camera would use). snap=true jumps without damping.
func update(center_units: Vector2, snap: bool = false) -> void:
	focus.position = Vector3(center_units.x / 16.0, 0.0, center_units.y / 16.0)
	if snap or pcam == null:
		_place_direct()
	cam_over.global_transform = cam.global_transform
	if OS.has_environment("HD2D_DEBUG"):
		print("HD focus ", focus.position, " cam ", cam.global_position, " rot ", cam.global_rotation_degrees, " pcam ", pcam.global_position if pcam else null)

func _place_direct() -> void:
	var pr = deg_to_rad(float(profile["pitch"]))
	var d = float(profile["dist"])
	cam.position = focus.position + Vector3(0, sin(pr) * d, cos(pr) * d)
	cam.rotation = Vector3(-pr, 0, 0)
	if pcam != null:
		pcam.position = cam.position

## Screen placement of a field point: [screen_units, scale, depth]. Depth is the view distance (bigger = farther).
func project(p_units: Vector2, z_units: float = 0.0) -> Array:
	var wp = Vector3(p_units.x / 16.0, z_units / 16.0, p_units.y / 16.0)
	var ct = cam.global_transform
	var rel = wp - ct.origin
	var depth = -rel.dot(ct.basis.z)
	if depth <= 0.05:
		return [Vector2(-9999, -9999), 0.0, 0.0]
	var sp = cam.unproject_position(wp) / 3.0
	return [sp, ref_dist / depth, depth * 16.0]

## Field point under a screen position (field units), on the ground plane.
func unproject(s_units: Vector2) -> Vector2:
	var o = cam.project_ray_origin(s_units * 3.0)
	var dirv = cam.project_ray_normal(s_units * 3.0)
	if absf(dirv.y) < 0.0001:
		return Vector2(-1, -1)
	var t = -o.y / dirv.y
	var hit = o + dirv * t
	return Vector2(hit.x * 16.0, hit.z * 16.0)

func ground_texture() -> Texture2D:
	return vp.get_texture()

func over_texture() -> Texture2D:
	return vp_over.get_texture()

func free_all() -> void:
	if is_instance_valid(vp):
		vp.queue_free()
	if is_instance_valid(vp_over):
		vp_over.queue_free()

## Phantom Camera warns when a priority is re-set to its current value; only set real changes.
func _prio(p, v: int) -> void:
	if p != null and int(p.get("priority")) != v:
		p.set("priority", v)
