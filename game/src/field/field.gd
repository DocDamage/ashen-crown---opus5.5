class_name Field
extends Node2D
## ExplorationController + map renderer: grid movement with smooth animation, collision at the feet,
## interaction selection, doorway/spawn transitions, encounter meter, y-sorted drawing.

signal request_battle(formation_id: String, opts: Dictionary)
signal request_scene(scene_id: String, ctx: Dictionary)
signal request_menu(kind: String, data: Dictionary)
signal map_entered(map_id: String)

const TS := 16
const VIEW := Vector2(320, 240)
const WALK := 1.0
const RUN := 2.0

var main: Node
var map: Dictionary = {}
var map_id = ""
var grid: Array = []
var legend: Dictionary = {}
var W = 0
var H = 0
var atlas: Texture2D
var props_tex: Texture2D
var objects_tex: Texture2D
var kinds_row = {}
var prop_col = {}
var tile_rules: Dictionary = {}
var solid_set = {}
var enc_set = {}
var tall_set = {}
# Library tileset (owner's licensed art, installed into assets/ext by tools/gen_art.py library): per-kind rules
var art: Art48 = null              # native 48px map art (tools/maps48), replaces tile drawing when present
var ext_tex: Texture2D = null
var ext_rules: Dictionary = {}     # kind -> {type: tile|auto|wall|stamp, ...}
var ext_group: Dictionary = {}     # kind -> autotile connection group
var _kc: Dictionary = {}           # per-draw kind cache (Vector2i -> kind)
var _ci: CanvasItem = null         # current draw target (self, or a cached ground layer)
# Library ground is recorded into 16x16-cell chunk nodes (culled off-screen): one static node per chunk plus three
# animation-frame nodes that are only toggled. Re-recorded when the map or its conditional tiles change.
const CHUNK := 16
var ground_root: Node2D
var chunk_static: Array = []
var chunk_anim: Array = []         # [chunk][3]
var _force_frame = -1
var _dry = false                   # collect tall objects without drawing
var _img: Image = null             # when set, cells are composited into this chunk image instead of drawn
var _img_org = Vector2.ZERO
var ext_img: Image = null
var atlas_img: Image = null
var _shadow_img: Image = null
const CHUNK_M := 0                 # no margin: anything overhanging a cell is a y-sorted stamp
var _chunk_fi = 0
var ext_anim: Dictionary = {}
var _static_talls: Array = []
var _bake_sig = ""
var _anim_sig = ""

# player
var p_tile = Vector2i(0, 0)
var p_pos = Vector2(0, 0)       # pixel position of tile origin
var p_dir = "down"
var p_moving = false
var p_target = Vector2i.ZERO
var p_anim = 0.0
var p_sprite = "C01"
var npcs: Array = []             # dicts {id,tile,pos,dir,sprite,talk,cond,wander,moving,target,timer,name,solid}
var cam = Vector2.ZERO
var enc_meter = 0.0
var enc_threshold = 80.0
var enc_grace = 8
var time = 0.0
var active = true              # accepts movement input
var busy = false               # scene running / transition
var banner_text = ""
var banner_t = 0.0
var vehicle = "foot"            # foot | ship
var ship_pos = Vector2i(-1, -1)
const HOME_BERTH := Vector2i(57, 45)   # Hearthward landing field on WORLD_POST
const WAYFARER_BERTH := Vector2i(52, 12)   # Nacre landing field on WORLD (pre-fault Wayfarer)
var steps = 0
var last_step_blocked = false
var tex_cache = {}
var hidden_actors = {}
var extra_actors: Array = []     # scene-staged actors {id,tile,pos,dir,sprite}
var tint = Color(0, 0, 0, 0)
var interact_hint = ""
var p_prev = Vector2i.ZERO

func hazard_on(e: Dictionary) -> bool:
	var per: float = float(e.get("period", 3.0))
	return fmod(time + float(e.get("phase", 0.0)), per) < float(e.get("on", 1.0))

func hazard_warn(e: Dictionary) -> bool:
	var per: float = float(e.get("period", 3.0))
	var t = fmod(time + float(e.get("phase", 0.0)), per)
	return t > per - 0.6

func _ready() -> void:
	var f = FileAccess.open("res://assets/tiles/kinds.json", FileAccess.READ)
	var kd = JSON.parse_string(f.get_as_text())
	for i in range(kd["kinds"].size()):
		kinds_row[kd["kinds"][i]] = i
	for i in range(kd["props"].size()):
		prop_col[kd["props"][i]] = i
	tile_rules = Content.data["tile_rules"]
	for s in tile_rules["solid"]:
		solid_set[s] = true
	for s in tile_rules["enc"]:
		enc_set[s] = true
	for s in tile_rules["tall"]:
		tall_set[s] = true
	objects_tex = _tex("res://assets/sprites/objects.png")
	_ci = self
	ground_root = Node2D.new()
	ground_root.show_behind_parent = true
	add_child(ground_root)

func _tex(path: String) -> Texture2D:
	if tex_cache.has(path):
		return tex_cache[path]
	var t: Texture2D = Content.load_art(path)
	tex_cache[path] = t
	return t

func sprite_tex(id: String) -> Texture2D:
	var t = _tex("res://assets/sprites/world/%s.png" % id)
	if t == null:
		t = _tex("res://assets/sprites/world/worker.png")
	return t

# ======================================================================
# Map loading
# ======================================================================
func load_map(id: String, spawn: String = "default", pos: Vector2i = Vector2i(-1, -1), dir: String = "") -> void:
	map = Content.map(id)
	if map.is_empty():
		push_error("Unknown map " + id)
		return
	map_id = id
	grid = map["grid"]
	legend = map["legend"]
	W = int(map["w"])
	H = int(map["h"])
	atlas = _tex("res://assets/tiles/%s.png" % map["tileset"])
	props_tex = _tex("res://assets/tiles/%s_props.png" % map["tileset"])
	art = Art48.load_for(id)
	_load_ext(map["tileset"] if art == null else "")
	var sp = pos
	var sdir = dir
	if sp.x < 0:
		for e in map["entities"]:
			if e["type"] == "spawn" and e["name"] == spawn:
				sp = Vector2i(e["x"], e["y"])
				if sdir == "":
					sdir = e["dir"]
		if sp.x < 0:
			for e in map["entities"]:
				if e["type"] == "spawn":
					sp = Vector2i(e["x"], e["y"])
					if sdir == "":
						sdir = e["dir"]
					break
	# Wayfarer: parked on the world map it was left on; "helm" spawn (or a saved flight) boards it
	vehicle = "foot"
	ship_pos = Vector2i(-1, -1)
	var vs: Dictionary = Game.S["vehicle"]
	if map.get("kind", "") == "world" and vs.get("ship", false) and str(vs.get("ship_map", "")) == id:
		ship_pos = Vector2i(int(vs["ship_x"]), int(vs["ship_y"]))
		if spawn == "helm" or (vs.get("mode", "foot") == "ship" and pos.x >= 0):
			vehicle = "ship"
			sp = ship_pos if spawn == "helm" else sp
			ship_pos = sp
	if vehicle != "ship" and vs.get("mode", "foot") == "ship" and map.get("kind", "") == "world":
		vs["mode"] = "foot"
	p_tile = sp
	p_pos = Vector2(sp * TS)
	p_dir = sdir if sdir != "" else "down"
	p_moving = false
	# the encounter meter carries across rooms (short rooms must not reset it); arrivals get a short grace
	enc_grace = 8
	hidden_actors = {}
	extra_actors = []
	tint = Color(0, 0, 0, 0)
	refresh_npcs()
	update_leader()
	Game.S["location"] = {"map": id, "spawn": spawn, "x": p_tile.x, "y": p_tile.y, "dir": p_dir}
	var zone: String = map.get("location", "")
	if zone != "":
		Game.discover(zone)
	if map.get("music", "") != "":
		Audio.music(map["music"])
	_snap_camera()
	emit_signal("map_entered", id)
	queue_redraw()

func update_leader() -> void:
	var act = Game.active()
	p_sprite = act[0] if not act.is_empty() else "C01"

func refresh_npcs() -> void:
	var keep = {}
	for n in npcs:
		keep[n["id"]] = n
	npcs = []
	for e in map.get("entities", []):
		if e["type"] != "npc":
			continue
		if not Game.eval_cond(e["cond"]):
			continue
		var n: Dictionary
		if keep.has(e["id"]):
			n = keep[e["id"]]
		else:
			n = {"id": e["id"], "tile": Vector2i(e["x"], e["y"]), "pos": Vector2(e["x"] * TS, e["y"] * TS), "dir": e["dir"],
				"home": Vector2i(e["x"], e["y"]), "moving": false, "target": Vector2i(e["x"], e["y"]), "timer": randf_range(1.0, 3.0)}
		n["sprite"] = e["sprite"]
		n["talk"] = e["talk"]
		n["wander"] = e["wander"]
		n["name"] = e.get("name", "")
		n["solid"] = e.get("solid", true)
		npcs.append(n)

func _new_threshold() -> float:
	var r = Rng.new(Game.next_seed("enc"))
	return 55.0 + r.randf() * 40.0

# ======================================================================
# Tiles & collision
# ======================================================================
func kind_at(x: int, y: int) -> String:
	if x < 0 or y < 0 or x >= W or y >= H:
		return "void"
	var ch = String(grid[y][x])
	var k: String = legend.get(ch, "void")
	# conditional overrides
	for e in map["entities"]:
		if e["type"] == "tileset_over" and x >= e["x1"] and x <= e["x2"] and y >= e["y1"] and y <= e["y2"] and Game.eval_cond(e["cond"]):
			k = e["tile"]
	return k

func block_at(x: int, y: int) -> Dictionary:
	for e in map["entities"]:
		if e["type"] == "block" and x >= e["x1"] and x <= e["x2"] and y >= e["y1"] and y <= e["y2"] and Game.eval_cond(e["cond"]):
			return e
	return {}

func solid_at(x: int, y: int, for_npc: bool = false) -> bool:
	var k = kind_at(x, y)
	if vehicle == "ship":
		return k == "void"
	if solid_set.has(k):
		return true
	if not block_at(x, y).is_empty():
		return true
	for e in map["entities"]:
		if e["type"] in ["chest", "save", "switch", "sign", "shop", "inn", "heal", "prop"] and e.get("x", -99) == x and e.get("y", -99) == y:
			if e["type"] == "prop" and not e.get("solid", true):
				continue
			if e["type"] == "sign":
				continue
			if e["type"] == "chest" and e.get("hidden", false) and not Game.S["chests"].has(e["id"]):
				continue
			if not Game.eval_cond(e["cond"]):
				continue
			return true
	for n in npcs:
		if n["solid"] and (n["tile"] == Vector2i(x, y) or (n["moving"] and n["target"] == Vector2i(x, y))):
			return true
	if for_npc and (p_tile == Vector2i(x, y) or (p_moving and p_target == Vector2i(x, y))):
		return true
	return false

# ======================================================================
# Update
# ======================================================================
func _process(delta: float) -> void:
	time += delta
	if banner_t > 0:
		banner_t -= delta
	_update_npcs(delta)
	if p_moving:
		var spd = RUN if (_running() or vehicle == "ship") else WALK
		if vehicle == "ship":
			spd *= 1.5
		elif riding():
			spd = RUN * 1.35
		var tgt = Vector2(p_target * TS)
		p_pos = p_pos.move_toward(tgt, spd * 60.0 * delta)
		p_anim += delta * (10.0 if _running() else 7.0)
		if p_pos.distance_to(tgt) < 0.01:
			p_pos = tgt
			p_tile = p_target
			p_moving = false
			_on_arrive()
			# route bots release the key when a step starts; at bot speed a step can start and finish inside one
			# frame, so never chain a new step in the arrival frame for them
			if QA.route != "":
				_update_camera()
				queue_redraw()
				return
	if not p_moving and can_move():
		var d = _input_dir()
		if d != "":
			try_step(d)
		else:
			p_anim = 0.0
	_update_camera()
	queue_redraw()

func can_move() -> bool:
	return active and not busy and main != null and main.router.top() == self

func _running() -> bool:
	var held = Input.is_action_pressed("g_run")
	if Settings.get_v("run_toggle"):
		return not held
	return held

func _input_dir() -> String:
	if QA.forced_dir != "":
		return QA.forced_dir
	for d in ["up", "down", "left", "right"]:
		if Input.is_action_pressed("g_" + d):
			return d
	return ""

const DV := {"up": Vector2i(0, -1), "down": Vector2i(0, 1), "left": Vector2i(-1, 0), "right": Vector2i(1, 0)}

func try_step(d: String) -> bool:
	p_dir = d
	var nt: Vector2i = p_tile + DV[d]
	if solid_at(nt.x, nt.y) or not _in_bounds_or_exit(nt):
		last_step_blocked = true
		return false
	last_step_blocked = false
	p_prev = p_tile
	p_target = nt
	p_moving = true
	return true

func _in_bounds_or_exit(t: Vector2i) -> bool:
	if t.x >= 0 and t.y >= 0 and t.x < W and t.y < H:
		return true
	return false

func _on_arrive() -> void:
	steps += 1
	Game.S["location"]["x"] = p_tile.x
	Game.S["location"]["y"] = p_tile.y
	Game.S["location"]["dir"] = p_dir
	if vehicle == "ship":
		ship_pos = p_tile
		Game.S["vehicle"]["ship_x"] = p_tile.x
		Game.S["vehicle"]["ship_y"] = p_tile.y
		return
	# doors / exits
	for e in map["entities"]:
		if e["type"] in ["door", "exit"] and p_tile.x >= e["x1"] and p_tile.x <= e["x2"] and p_tile.y >= e["y1"] and p_tile.y <= e["y2"]:
			if not Game.eval_cond(e["cond"]):
				if e.get("locked_msg", "") != "":
					main.toast(e["locked_msg"])
				continue
			main.transition_to(e["dest"], e["spawn"], e.get("sfx", ""))
			return
	# periodic hazards (steam bursts): push back to the previous tile, never damage
	for e in map["entities"]:
		if e["type"] == "hazard" and p_tile.x >= e["x1"] and p_tile.x <= e["x2"] and p_tile.y >= e["y1"] and p_tile.y <= e["y2"] and hazard_on(e) and Game.eval_cond(e["cond"]):
			Audio.sfx("FX019" if map["tileset"] != "sky" else "FX013")
			main.toast("A burst of steam pushes you back." if map["tileset"] != "sky" else "A gust shoves you back to the last anchor point.")
			place_player(p_prev.x, p_prev.y, p_dir)
			return
	# world locations
	for e in map["entities"]:
		if e["type"] == "location" and e["x"] == p_tile.x and e["y"] == p_tile.y and Game.eval_cond(e["cond"]) and vehicle == "foot":
			Game.discover(e["id"])
			if Content.data["maps"].has(e["dest"]):
				main.transition_to(e["dest"], e["spawn"], "")
			else:
				main.toast("(Not yet built: " + e["dest"] + ")")
			return
	# touch triggers
	for e in map["entities"]:
		if e["type"] == "trigger" and e.get("touch", true) and p_tile.x >= e["x1"] and p_tile.x <= e["x2"] and p_tile.y >= e["y1"] and p_tile.y <= e["y2"]:
			if Game.eval_cond(e["cond"]):
				var sc = Content.scene(e["scene"])
				if sc.get("once", false) and Game.event_applied(e["scene"]):
					continue
				emit_signal("request_scene", e["scene"], {"trigger": true})
				return
	_encounter_step()

func _encounter_step() -> void:
	if vehicle == "ship" or riding():
		return
	var group: String = map.get("encounters", "")
	for e in map["entities"]:
		if e["type"] == "zone" and p_tile.x >= e["x1"] and p_tile.x <= e["x2"] and p_tile.y >= e["y1"] and p_tile.y <= e["y2"]:
			group = e["encounters"]
	if group == "" or group == "none":
		return
	var mode: String = Settings.get_v("encounters")
	if mode == "off":
		return
	if enc_grace > 0:
		enc_grace -= 1
		return
	var k = kind_at(p_tile.x, p_tile.y)
	if not enc_set.has(k):
		return
	# suppressed near save points
	for e in map["entities"]:
		if e["type"] == "save" and absi(e["x"] - p_tile.x) + absi(e["y"] - p_tile.y) <= 3:
			return
	var inc = float(map.get("rate", 1.0))
	if mode == "reduced":
		inc *= 0.5
	for cid in Game.active():
		var s = Game.stats(cid)
		if s["passives"].has("encounter_mult"):
			inc *= float(s["passives"]["encounter_mult"])
			break
	enc_meter += inc
	if enc_meter >= enc_threshold:
		enc_meter = 0.0
		enc_threshold = _new_threshold()
		enc_grace = 6
		var forms = Content.group(group)
		if forms.is_empty():
			return
		var r = Rng.new(Game.next_seed("enc"))
		emit_signal("request_battle", forms[r.next_u32() % forms.size()], {"random": true})

func _update_npcs(delta: float) -> void:
	for n in npcs:
		if n["moving"]:
			var tgt = Vector2(n["target"] * TS)
			n["pos"] = n["pos"].move_toward(tgt, 0.6 * 60.0 * delta)
			if n["pos"].distance_to(tgt) < 0.01:
				n["pos"] = tgt
				n["tile"] = n["target"]
				n["moving"] = false
		elif n["wander"] and not busy:
			n["timer"] -= delta
			if n["timer"] <= 0:
				n["timer"] = randf_range(1.5, 4.0)
				var d: String = ["up", "down", "left", "right"][randi() % 4]
				var nt: Vector2i = n["tile"] + DV[d]
				n["dir"] = d
				if (nt - n["home"]).length() <= 2.0 and not solid_at(nt.x, nt.y, true) and nt != p_tile:
					n["target"] = nt
					n["moving"] = true

# ======================================================================
# Interaction
# ======================================================================
func handle(ev: String) -> void:
	if busy:
		return
	match ev:
		"confirm":
			if not p_moving:
				interact()
		"menu":
			if not p_moving:
				emit_signal("request_menu", "main", {})
		"skip":
			pass

func facing_tile() -> Vector2i:
	return p_tile + DV[p_dir]

var interactions = 0

func interact() -> void:
	interactions += 1
	var ft = facing_tile()
	if vehicle == "ship":
		emit_signal("request_scene", "SHIP_HELM", {})
		return
	if ship_pos.x >= 0 and ft == ship_pos:
		emit_signal("request_scene", "SHIP_BOARD", {})
		return
	# counters: talk across one counter tile
	var across = ft + DV[p_dir]
	for n in npcs:
		if n["tile"] == ft or (kind_at(ft.x, ft.y) in ["counter", "window", "gate"] and n["tile"] == across):
			n["dir"] = {"up": "down", "down": "up", "left": "right", "right": "left"}[p_dir]
			if n["talk"] != "":
				emit_signal("request_scene", n["talk"], {"npc": n["id"]})
			return
	for e in map["entities"]:
		if not e.has("x") or not Game.eval_cond(e["cond"]):
			continue
		var at = Vector2i(e["x"], e["y"])
		if at != ft and not (e["type"] in ["shop", "inn"] and at == across and kind_at(ft.x, ft.y) == "counter"):
			continue
		match e["type"]:
			"chest":
				if Game.S["chests"].has(e["id"]):
					main.toast("Empty.")
				else:
					_open_chest(e)
				return
			"sign", "read":
				if e.get("scene", "") != "":
					emit_signal("request_scene", e["scene"], {})
				else:
					main.show_text("", e["text"])
				return
			"save":
				emit_signal("request_menu", "savepoint", {})
				return
			"shop":
				emit_signal("request_menu", "shop", {"id": e["id"]})
				return
			"inn":
				emit_signal("request_menu", "inn", {"id": e["id"], "scene": e.get("scene", "")})
				return
			"heal":
				Game.heal_all()
				Audio.sfx("FX022")
				main.toast("The party is fully restored.")
				return
			"switch":
				if e.get("scene", "") != "":
					emit_signal("request_scene", e["scene"], {"switch": e["id"]})
				elif e.get("flag", "") != "":
					Audio.sfx("FX010")
					Game.set_flag(e["flag"], not Game.flag(e["flag"]) if e.get("toggle", false) else true)
					refresh_npcs()
				return
	# floor plaques and readable markers under the player's feet
	for e in map["entities"]:
		if e["type"] in ["read", "sign"] and e.get("x", -99) == p_tile.x and e.get("y", -99) == p_tile.y and Game.eval_cond(e["cond"]):
			if e.get("scene", "") != "":
				emit_signal("request_scene", e["scene"], {})
			else:
				main.show_text("", e["text"])
			return
	# non-touch triggers (inspect)
	for e in map["entities"]:
		if e["type"] == "trigger" and not e.get("touch", true) and ft.x >= e["x1"] and ft.x <= e["x2"] and ft.y >= e["y1"] and ft.y <= e["y2"] and Game.eval_cond(e["cond"]):
			emit_signal("request_scene", e["scene"], {})
			return
	var bl = block_at(ft.x, ft.y)
	if not bl.is_empty() and bl.get("msg", "") != "":
		main.show_text("", bl["msg"])
		return
	if map.get("kind", "") == "world" and Game.S["vehicle"].get("ship", false) and not landing_at(p_tile).is_empty():
		if ship_pos.x < 0 or (ship_pos - p_tile).length() > 1.5:
			emit_signal("request_scene", "SHIP_RECALL", {})

# ======================================================================
# Wayfarer (airship): board, land at marked fields, recall on foot
# ======================================================================
func landing_at(t: Vector2i) -> Dictionary:
	for e in map["entities"]:
		if e["type"] == "landing" and t.x >= e["x1"] - 1 and t.x <= e["x2"] + 1 and t.y >= e["y1"] - 1 and t.y <= e["y2"] + 1:
			return e
	return {}

func _foot_free(t: Vector2i) -> bool:
	if t.x < 0 or t.y < 0 or t.x >= W or t.y >= H:
		return false
	var v = vehicle
	vehicle = "foot"
	var ok = not solid_at(t.x, t.y)
	vehicle = v
	if ok:
		for e in map["entities"]:
			if e["type"] == "location" and e["x"] == t.x and e["y"] == t.y:
				return false
	return ok

func _free_near(c: Vector2i, rmax: int) -> Vector2i:
	for r in range(1, rmax + 1):
		for dy in range(-r, r + 1):
			for dx in range(-r, r + 1):
				if absi(dx) + absi(dy) > r:
					continue
				var t = c + Vector2i(dx, dy)
				if t != c and _foot_free(t):
					return t
	return Vector2i(-1, -1)

func ship_op(op: String) -> bool:
	var vs: Dictionary = Game.S["vehicle"]
	match op:
		"board":
			if ship_pos.x < 0:
				return false
			vehicle = "ship"
			vs["mode"] = "ship"
			place_player(ship_pos.x, ship_pos.y, "down")
			Game.S["location"]["x"] = ship_pos.x
			Game.S["location"]["y"] = ship_pos.y
			Audio.sfx("FX031")
			return true
		"land":
			if landing_at(p_tile).is_empty():
				main.toast("No landing field here. Fly to a marked field by a town or ruin.")
				return false
			var t = _free_near(p_tile, 3)
			if t.x < 0:
				main.toast("The field below is blocked. Try the other side of it.")
				return false
			vehicle = "foot"
			vs["mode"] = "foot"
			ship_pos = p_tile
			vs["ship_map"] = map_id
			vs["ship_x"] = p_tile.x
			vs["ship_y"] = p_tile.y
			place_player(t.x, t.y, "down")
			Game.S["location"]["x"] = t.x
			Game.S["location"]["y"] = t.y
			enc_grace = 8
			Audio.sfx("FX010")
			return true
		"recall":
			var l = landing_at(p_tile)
			if l.is_empty():
				return false
			var best = Vector2i(-1, -1)
			for y in range(l["y1"], l["y2"] + 1):
				for x in range(l["x1"], l["x2"] + 1):
					var t = Vector2i(x, y)
					if t != p_tile and (best.x < 0 or (t - p_tile).length() < (best - p_tile).length()):
						best = t
			ship_pos = best
			vs["ship_map"] = map_id
			vs["ship_x"] = best.x
			vs["ship_y"] = best.y
			Audio.sfx("FX031")
			return true
		"below":
			vs["mode"] = "deck"
			return true
		"wayfarer":
			# pre-fault Wayfarer (CH10): parked on the Nacre landing field of the pre-fault world
			vs["ship"] = true
			vs["ship_map"] = "WORLD"
			vs["ship_x"] = WAYFARER_BERTH.x
			vs["ship_y"] = WAYFARER_BERTH.y
			return true
		"home":
			vs["ship"] = true
			vs["ship_map"] = "WORLD_POST"
			vs["ship_x"] = HOME_BERTH.x
			vs["ship_y"] = HOME_BERTH.y
			return true
	return false

func _open_chest(e: Dictionary) -> void:
	var r = Game.open_chest(e["id"], e["item"], e["count"], e.get("gold", 0), e.get("acq", ""))
	if r["ok"]:
		Audio.sfx("FX007")
		var txt = ""
		if e.get("gold", 0) > 0:
			txt = "Found %d crowns." % e["gold"]
		if e["item"] != "gold" and e["item"] != "":
			txt = "Found %s%s." % [Content.item_name(e["item"]), " x%d" % e["count"] if e["count"] > 1 else ""]
		main.toast(txt)

func interact_target_name() -> String:
	var ft = facing_tile()
	for n in npcs:
		if n["tile"] == ft:
			return "talk"
	for e in map["entities"]:
		if e.has("x") and Vector2i(e["x"], e["y"]) == ft and Game.eval_cond(e["cond"]) and e["type"] in ["chest", "sign", "read", "save", "shop", "inn", "switch", "heal"]:
			return e["type"]
	return ""

# ======================================================================
# Staging helpers used by the StoryDirector
# ======================================================================
func actor(id: String) -> Dictionary:
	if id == "player" or id == "leader":
		return {"_player": true}
	for n in npcs:
		if n["id"] == id:
			return n
	for a in extra_actors:
		if a["id"] == id:
			return a
	return {}

func show_actor(id: String, x: int, y: int, dir: String, sprite: String) -> void:
	for a in extra_actors:
		if a["id"] == id:
			extra_actors.erase(a)
			break
	extra_actors.append({"id": id, "tile": Vector2i(x, y), "pos": Vector2(x * TS, y * TS), "dir": dir, "sprite": sprite,
		"moving": false, "target": Vector2i(x, y), "solid": true, "talk": "", "wander": false})
	hidden_actors.erase(id)

func hide_actor(id: String) -> void:
	hidden_actors[id] = true
	for a in extra_actors:
		if a["id"] == id:
			extra_actors.erase(a)
			break

func face(id: String, dir: String) -> void:
	if id in ["player", "leader"]:
		p_dir = dir
		return
	var a = actor(id)
	if not a.is_empty():
		a["dir"] = dir

## Move an actor by steps (blocking helper; returns when done)
func move_actor(id: String, path: Array) -> void:
	for d in path:
		if id in ["player", "leader"]:
			p_dir = d
			p_target = p_tile + DV[d]
			p_moving = true
			while p_moving:
				await get_tree().process_frame
		else:
			var a = actor(id)
			if a.is_empty():
				return
			a["dir"] = d
			a["target"] = a["tile"] + DV[d]
			a["moving"] = true
			while a["moving"]:
				_step_extra(a)
				await get_tree().process_frame

func _step_extra(a: Dictionary) -> void:
	if not npcs.has(a):
		var tgt = Vector2(a["target"] * TS)
		a["pos"] = a["pos"].move_toward(tgt, 1.0)
		if a["pos"].distance_to(tgt) < 0.01:
			a["pos"] = tgt
			a["tile"] = a["target"]
			a["moving"] = false

func place_player(x: int, y: int, dir: String) -> void:
	p_tile = Vector2i(x, y)
	p_pos = Vector2(p_tile * TS)
	p_dir = dir
	p_moving = false

func show_banner(t: String) -> void:
	banner_text = t
	banner_t = 2.5

# ======================================================================
# Camera & drawing
# ======================================================================
func _snap_camera() -> void:
	_update_camera()

var cam_override = Vector2(-1, -1)    # dev gallery only

func _update_camera() -> void:
	var c = p_pos + Vector2(8, 8) - VIEW / 2.0
	if cam_override.x >= 0:
		c = cam_override + VIEW / 2.0 - VIEW / 2.0
	var mw = W * TS
	var mh = H * TS
	c.x = (mw - VIEW.x) / 2.0 if mw <= VIEW.x else clampf(c.x, 0, mw - VIEW.x)
	c.y = (mh - VIEW.y) / 2.0 if mh <= VIEW.y else clampf(c.y, 0, mh - VIEW.y)
	cam = (c * UI.U).round() / UI.U

func _variant(x: int, y: int) -> int:
	var h = (x * 73856093) ^ (y * 19349663)
	h = absi(h) % 16
	if h < 7:
		return 0
	if h < 12:
		return 1
	if h < 15:
		return 2
	return 3

func _tile_kind_draw(x: int, y: int) -> String:
	var k = kind_at(x, y)
	match k:
		"wall":
			var below = kind_at(x, y + 1)
			return "wall_top" if (below == "wall" or below == "void") else "wall_face"
		"roof":
			var ab = kind_at(x, y - 1)
			var be = kind_at(x, y + 1)
			if be != "roof" and be != "chimney":
				return "roof_eave"
			if ab != "roof" and ab != "chimney":
				return "roof_ridge"
			return "roof"
		"cliff":
			return "cliff_top" if kind_at(x, y + 1) == "cliff" else "cliff"
	return k

func _draw_tile_kind(k: String, x: int, y: int, pos: Vector2) -> void:
	if _dry:
		return
	var row: int = kinds_row.get(k, -1)
	if row < 0 or atlas == null:
		if _img != null:
			_img.fill_rect(Rect2i(Vector2i(pos - _img_org), Vector2i(TS, TS)), Color8(20, 16, 28))
		elif not _dry:
			_ci.draw_rect(Rect2(pos, Vector2(TS, TS)), Color8(20, 16, 28))
		return
	var v = _variant(x, y)
	if k in ["water", "deep", "shallow", "puddle", "wheel", "boat"]:
		v = int(time * 2.0 + (x + y) * 0.0) % 2 if k != "boat" else 0
	_put(atlas, atlas_img, Rect2(v * TS, row * TS, TS, TS), pos)

# ----------------------------------------------------------------------
# Library tiles: RPG-Maker-style autotiles (A1/A2 32x48 blocks, A4 wall top + face) and plain/stamp tiles,
# pre-assembled into one atlas per tileset family. Kinds without a rule use the generated atlas.
func _load_ext(ts: String) -> void:
	ext_rules = {}
	ext_group = {}
	ext_anim = {}
	_static_talls = []
	_bake_sig = ""
	for c in ground_root.get_children():
		c.queue_free()
	chunk_static = []
	chunk_anim = []
	ext_tex = _tex("res://assets/tiles/%s_ext.png" % ts)
	if ext_tex == null:
		return
	var f = FileAccess.open(Content.art("res://assets/tiles/%s_ext.json" % ts), FileAccess.READ)
	if f == null:
		ext_tex = null
		return
	var d = JSON.parse_string(f.get_as_text())
	ext_rules = d.get("rules", {})
	ext_img = _rgba(ext_tex)
	atlas_img = _rgba(atlas)
	for k in ext_rules:
		ext_group[k] = ext_rules[k].get("g", k)
	ext_anim = {}
	for k in ext_rules:
		var kk = k
		for i in range(4):
			var rr: Dictionary = ext_rules.get(kk, {})
			if rr.has("fps"):
				ext_anim[k] = true
				break
			kk = rr.get("under", "")
			if kk == "" or kk == "@":
				break
	_bake_sig = ""
	_anim_sig = "none"
	for cy in range(ceili(H / float(CHUNK))):
		for cx in range(ceili(W / float(CHUNK))):
			var n = Node2D.new()
			n.show_behind_parent = true
			ground_root.add_child(n)
			n.set_meta("c", Vector3i(cx, cy, -1))
			n.draw.connect(_draw_chunk_tex.bind(n))
			chunk_static.append(n)


var _overs: Array = []            # active tileset_over entities for this draw

## kind_at() for drawing: same result, but conditions are evaluated once per frame instead of per call.
func _rgba(t: Texture2D) -> Image:
	if t == null:
		return null
	var im = t.get_image()
	if im == null:
		return null
	if im.is_compressed():
		im.decompress()
	if im.get_format() != Image.FORMAT_RGBA8:
		im.convert(Image.FORMAT_RGBA8)
	return im

func _kind_c(x: int, y: int) -> String:
	var key = Vector2i(x, y)
	if _kc.has(key):
		return _kc[key]
	var k := "void"
	if x >= 0 and y >= 0 and x < W and y < H:
		k = legend.get(String(grid[y][x]), "void")
		for e in _overs:
			if x >= e["x1"] and x <= e["x2"] and y >= e["y1"] and y <= e["y2"]:
				k = e["tile"]
	_kc[key] = k
	return k

func _same(g: String, x: int, y: int) -> bool:
	if x < 0 or y < 0 or x >= W or y >= H:
		return true
	return ext_group.get(_kind_c(x, y), "~") == g

func _hash(x: int, y: int) -> int:
	return absi((x * 73856093) ^ (y * 19349663) ^ 83492791)

## Draw one 16x16 cell from an A2-layout block (32x48 at `b`) given the 8 neighbour flags.
## face=true: a 32x32 block (A4 wall face) = the lower 2x2 part of an A2 block, no inner corners.
## Drawing primitives: direct CanvasItem draw, or CPU compositing into the current chunk image.
func _put(tex: Texture2D, img: Image, src: Rect2, dst: Vector2) -> void:
	if _dry:
		return
	if _img != null:
		if img != null:
			_img.blend_rect(img, Rect2i(src), Vector2i(dst - _img_org))
	else:
		_ci.draw_texture_rect_region(tex, Rect2(dst, src.size), src)

func _shade(r: Rect2) -> void:
	if _dry:
		return
	if _img != null:
		if _shadow_img == null:
			_shadow_img = Image.create(6, TS, false, Image.FORMAT_RGBA8)
			_shadow_img.fill(Color(0.05, 0.03, 0.12, 0.3))
		_img.blend_rect(_shadow_img, Rect2i(0, 0, int(r.size.x), int(r.size.y)), Vector2i(r.position - _img_org))
	else:
		_ci.draw_rect(r, Color(0.05, 0.03, 0.12, 0.3))

func _auto_cell(b: Vector2, n: bool, s: bool, w: bool, e: bool, nw: bool, ne: bool, sw: bool, se: bool, pos: Vector2, face: bool = false) -> void:
	if _dry:
		return
	var q = [[0, 0], [1, 0], [0, 1], [1, 1]]
	for i in range(4):
		var qx = q[i][0]
		var qy = q[i][1]
		var v = n if qy == 0 else s
		var h = w if qx == 0 else e
		var d = (nw if qx == 0 else ne) if qy == 0 else (sw if qx == 0 else se)
		var sx = 0
		var sy = 0
		if v and h and d:
			sx = 2 - qx
			sy = 4 - qy
		elif v and h and not d:
			if face:
				sx = 2 - qx
				sy = 4 - qy
			else:
				sx = 2 + qx
				sy = qy
		elif v and not h:
			sx = 0 if qx == 0 else 3
			sy = 4 - qy
		elif h and not v:
			sx = 2 - qx
			sy = 2 if qy == 0 else 5
		else:
			sx = 0 if qx == 0 else 3
			sy = 2 if qy == 0 else 5
		var src = b + Vector2(sx * 8, (sy - (2 if face else 0)) * 8)
		_put(ext_tex, ext_img, Rect2(src, Vector2(8, 8)), pos + Vector2(qx * 8, qy * 8))

func _frame_of(r: Dictionary, key: String) -> Vector2:
	var fr: Array = r[key]
	if fr.size() == 0:
		return Vector2.ZERO
	if _force_frame >= 0:
		var fv = fr[mini(_force_frame, fr.size() - 1)]
		return Vector2(fv[0], fv[1])
	var i = 0
	if r.has("fps") and fr.size() > 1:
		var n = fr.size()
		var t = int(time * float(r["fps"]))
		i = t % n if not r.get("pingpong", false) else [0, 1, 2, 1][t % 4] % n
	var v = fr[i]
	return Vector2(v[0], v[1])

## Ground kind to draw beneath an object: the first neighbour whose rule is a ground (auto/tile) rule.
func _ground_near(x: int, y: int) -> String:
	for d in [Vector2i(-1, 0), Vector2i(0, 1), Vector2i(1, 0), Vector2i(0, -1), Vector2i(-1, 1), Vector2i(1, 1)]:
		var nk = _kind_c(x + d.x, y + d.y)
		var nr: Dictionary = ext_rules.get(nk, {})
		if nr.get("type", "") == "auto" and not nr.get("casts", false) and not (nr.get("g", nk) in ["water", "void", "deep", "ember", "shallow", "pool"]):
			return nk
	if not ext_rules.has("floor") and ext_rules.has("plains"):
		return "plains"      # world map: mountain masses fall back to grassland
	return ext_rules.get("_ground", {}).get("kind", "floor")

## Returns true when the cell was handled by a library rule.
func _draw_ext(k: String, x: int, y: int, pos: Vector2, talls: Array) -> bool:
	var r: Dictionary = ext_rules.get(k, {})
	if r.is_empty():
		return false
	var u: String = r.get("under", "")
	if u == "@":
		u = _ground_near(x, y)
	if u != "" and u != k:
		if not _draw_ext(u, x, y, pos, talls):
			_draw_tile_kind(u, x, y, pos)
	var g: String = ext_group.get(k, k)
	match r["type"]:
		"tile":
			var vs: Array = r["t"]
			var h = _hash(x, y)
			var idx = 0
			if vs.size() > 1:
				var wts: Array = r.get("w", [])
				if wts.size() == vs.size():
					var tot = 0
					for wv in wts:
						tot += int(wv)
					var roll = h % maxi(tot, 1)
					for j in range(wts.size()):
						roll -= int(wts[j])
						if roll < 0:
							idx = j
							break
				else:
					idx = h % vs.size()
			var v = vs[idx]
			if r.has("fps"):
				v = r["t"][int(time * float(r["fps"])) % vs.size()]
			_put(ext_tex, ext_img, Rect2(Vector2(v[0], v[1]), Vector2(TS, TS)), pos)
		"auto":
			var b = _frame_of(r, "b")
			_auto_cell(b, _same(g, x, y - 1), _same(g, x, y + 1), _same(g, x - 1, y), _same(g, x + 1, y),
				_same(g, x - 1, y - 1), _same(g, x + 1, y - 1), _same(g, x - 1, y + 1), _same(g, x + 1, y + 1), pos)
		"wall":
			var below = _same(g, x, y + 1) and y + 1 < H
			if below:
				_auto_cell(_frame_of(r, "top"), _same(g, x, y - 1), true, _same(g, x - 1, y), _same(g, x + 1, y),
					_same(g, x - 1, y - 1), _same(g, x + 1, y - 1), _same(g, x - 1, y + 1), _same(g, x + 1, y + 1), pos)
			else:
				var wl = _same(g, x - 1, y) and not _same(g, x - 1, y + 1)
				var wr = _same(g, x + 1, y) and not _same(g, x + 1, y + 1)
				_auto_cell(_frame_of(r, "face"), true, false, wl, wr, wl, wr, false, false, pos, true)
		"grid9":
			# 3x3 piece set chosen by same-group neighbours (no inner corners): cliffs, platforms, counters
			var t9: Array = r["t"]
			var cx = 1
			var cy = 1
			if not _same(g, x - 1, y):
				cx = 0
			elif not _same(g, x + 1, y):
				cx = 2
			if not _same(g, x, y - 1):
				cy = 0
			elif not _same(g, x, y + 1):
				cy = 2
			var v9 = t9[cy * 3 + cx]
			_put(ext_tex, ext_img, Rect2(Vector2(v9[0], v9[1]), Vector2(TS, TS)), pos)
		"hrow":
			# one-row structure (house front, fence, counter): left end / middle / right end / single
			var tl: Array = r["t"]
			var l = _same(g, x - 1, y)
			var rr = _same(g, x + 1, y)
			var v = tl[1]
			if l and not rr:
				v = tl[2]
			elif rr and not l:
				v = tl[0]
			elif not l and not rr:
				v = tl[3] if tl.size() > 3 else tl[1]
			_put(ext_tex, ext_img, Rect2(Vector2(v[0], v[1]), Vector2(TS, TS)), pos)
		"pair":
			# two-cell objects (tents, awnings): runs pair up from their left end; a leftover cell draws "one"
			var n = 0
			while n < 64 and _same(g, x - 1 - n, y) and x - 1 - n >= 0:
				n += 1
			if n % 2 == 0:
				var two = _same(g, x + 1, y) and x + 1 < W
				var pr: Array = r["r"] if two else r["one"]
				var prect = Rect2(pr[0], pr[1], pr[2], pr[3])
				var cxo = TS if two else 8
				var ppos = pos + Vector2(cxo - prect.size.x / 2.0, TS - prect.size.y + r.get("dy", 0))
				talls.append([y * TS + 15, "ext", prect, ppos])
		"stamp":
			var st: Array = r["r"]
			if r.has("inner") and _same(g, x, y - 1):
				st = r["inner"]
			var vi = 0
			if r.has("alt") and not (r.has("inner") and _same(g, x, y - 1)):
				var alts: Array = r["alt"]
				vi = _hash(x, y) % (alts.size() + 1)
				if vi > 0:
					st = alts[vi - 1]
			var rect = Rect2(st[0], st[1], st[2], st[3])
			var dpos = pos + Vector2(8 - rect.size.x / 2.0, TS - rect.size.y) + Vector2(r.get("dx", 0), r.get("dy", 0))
			if r.get("tall", false):
				talls.append([y * TS + 15, "ext", rect, dpos])
			else:
				_put(ext_tex, ext_img, rect, dpos)
	if not (r["type"] in ["stamp", "pair"]) and not r.get("casts", false):
		# FF-style soft drop shadow cast onto the ground right of a wall/structure
		var lk = _kind_c(x - 1, y)
		if ext_rules.get(lk, {}).get("casts", false):
			_shade(Rect2(pos, Vector2(6, TS)))
	return true

func _active_overs() -> Array:
	var out = []
	for e in map["entities"]:
		if e["type"] == "tileset_over" and Game.eval_cond(e["cond"]):
			out.append(e)
	return out

func _draw_chunk_tex(node: Node2D) -> void:
	var frames: Array = node.get_meta("frames", [])
	var t = null
	if frames.size() == 3:
		t = frames[_chunk_fi]
	elif node.has_meta("tex"):
		t = node.get_meta("tex")
	if t != null:
		var c: Vector3i = node.get_meta("c")
		node.draw_texture(t, Vector2(c.x * CHUNK * TS - CHUNK_M, c.y * CHUNK * TS - CHUNK_M))

## Composite every chunk (static + 3 animation frames) into textures; called when the map or its conditional
## tiles change. Each chunk is then a single quad per frame.
func _rebuild_chunks() -> void:
	chunk_anim = []
	for n in chunk_static:
		var c: Vector3i = n.get_meta("c")
		var base: Image = _build_chunk(c.x, c.y, -1, null)
		if base == null:
			continue
		var frames = []
		for i in range(3):
			var im: Image = _build_chunk(c.x, c.y, i, base)
			if im == null:
				break
			frames.append(ImageTexture.create_from_image(im))
		if frames.size() == 3:
			n.set_meta("frames", frames)
			chunk_anim.append(n)
		else:
			n.set_meta("frames", [])
			n.set_meta("tex", ImageTexture.create_from_image(base))
		n.queue_redraw()

## One ground chunk image: static cells (frame < 0), or `base` plus the animated cells for one animation frame
## (null when the chunk has no animated cells).
func _build_chunk(cx: int, cy: int, frame: int, base: Image) -> Image:
	if map.is_empty() or ext_tex == null or ext_img == null:
		return null
	var xa = cx * CHUNK
	var ya = cy * CHUNK
	var xb = mini(W, xa + CHUNK)
	var yb = mini(H, ya + CHUNK)
	if frame >= 0:
		var any = false
		for y in range(ya, yb):
			for x in range(xa, xb):
				if ext_anim.has(_kind_c(x, y)):
					any = true
					break
			if any:
				break
		if not any:
			return null
	if base != null:
		_img = base.duplicate()
	else:
		_img = Image.create(CHUNK * TS + CHUNK_M * 2, CHUNK * TS + CHUNK_M * 2, false, Image.FORMAT_RGBA8)
	_img_org = Vector2(xa * TS - CHUNK_M, ya * TS - CHUNK_M)
	_force_frame = frame
	var dummy = []
	if frame < 0:
		var pad = TS * 2
		var r0 = Vector2(xa * TS - (pad if xa == 0 else 0), ya * TS - (pad if ya == 0 else 0))
		var r1 = Vector2(xb * TS + (pad if xb == W else 0), yb * TS + (pad if yb == H else 0))
		_img.fill_rect(Rect2i(Vector2i(r0 - _img_org), Vector2i(r1 - r0)), Color8(12, 10, 18))
	for y in range(ya, yb):
		for x in range(xa, xb):
			var k = _kind_c(x, y)
			if frame < 0:
				if not ext_anim.has(k):
					_draw_cell_any(k, x, y, Vector2(x * TS, y * TS), dummy)
			elif ext_anim.has(k):
				_draw_ext(k, x, y, Vector2(x * TS, y * TS), dummy)
	if frame < 0:
		for e in map["entities"]:
			if e["type"] == "block" and Game.eval_cond(e["cond"]):
				for by in range(maxi(e["y1"], ya), mini(e["y2"] + 1, yb)):
					for bx in range(maxi(e["x1"], xa), mini(e["x2"] + 1, xb)):
						if not _draw_ext(e["tile"], bx, by, Vector2(bx * TS, by * TS), dummy):
							_draw_tile_kind(e["tile"], bx, by, Vector2(bx * TS, by * TS))
	var out = _img
	_img = null
	_force_frame = -1
	return out

## Tall objects standing on the static ground (y-sorted with actors every frame).
func _collect_talls() -> void:
	_dry = true
	_kc = {}
	_overs = _active_overs()
	_static_talls = []
	for y in range(H):
		for x in range(W):
			var k = _kind_c(x, y)
			if not ext_anim.has(k):
				_draw_cell_any(k, x, y, Vector2(x * TS, y * TS), _static_talls)
	for e in map["entities"]:
		if e["type"] == "block" and Game.eval_cond(e["cond"]):
			for by in range(e["y1"], e["y2"] + 1):
				for bx in range(e["x1"], e["x2"] + 1):
					_draw_ext(e["tile"], bx, by, Vector2(bx * TS, by * TS), _static_talls)
	_dry = false

## Library rule or generated fallback for one cell (fallback tall props go to talls).
func _draw_cell_any(k: String, x: int, y: int, pos: Vector2, talls: Array) -> void:
	if _draw_ext(k, x, y, pos, talls):
		return
	var dk = _tile_kind_draw(x, y)
	if tall_set.has(dk):
		var under = "grass" if dk in ["tree", "tree2"] and kinds_row.has("grass") and _outdoor() else "floor"
		if not _draw_ext(under, x, y, pos, talls):
			_draw_tile_kind(under, x, y, pos)
		talls.append([y * TS + 15, "prop", dk, pos])
		return
	_draw_tile_kind(dk, x, y, pos)

func _draw() -> void:
	if map.is_empty():
		return
	_ci = self
	_kc = {}
	_overs = []
	for e in map["entities"]:
		if e["type"] == "tileset_over" and Game.eval_cond(e["cond"]):
			_overs.append(e)
	var ox = -cam
	var x0 = maxi(0, int(cam.x / TS) - 1)
	var y0 = maxi(0, int(cam.y / TS) - 1)
	var x1 = mini(W - 1, int((cam.x + VIEW.x) / TS) + 1)
	var y1 = mini(H - 1, int((cam.y + VIEW.y) / TS) + 2)
	var bg = Color8(12, 10, 18)
	var talls = []
	if art != null:
		draw_rect(Rect2(Vector2.ZERO, VIEW), bg)
		art.draw_ground(self, cam)
		art.collect(talls, cam, VIEW)
		y1 = y0 - 1
	elif ext_tex != null:
		# cached ground layers (drawn behind this node); only moved by the camera
		var sig = "%s|" % map_id
		for e in map["entities"]:
			if e["type"] in ["tileset_over", "block"] and Game.eval_cond(e["cond"]):
				sig += "%d," % e.get("x1", 0) + "%d;" % e.get("y1", 0)
		if sig != _bake_sig:
			_bake_sig = sig
			_kc = {}
			_overs = _active_overs()
			_rebuild_chunks()
			_collect_talls()
		var fi = [0, 1, 2, 1][int(time * 3.0) % 4]
		ground_root.position = ox
		if fi != _chunk_fi:
			_chunk_fi = fi
			for n in chunk_anim:
				n.queue_redraw()
		for t in _static_talls:
			var tp: Vector2 = t[3] + ox
			if tp.x > -64 and tp.x < VIEW.x + 64 and tp.y > -64 and tp.y < VIEW.y + 96:
				talls.append([t[0], t[1], t[2], tp])
		y1 = y0 - 1   # skip the per-frame ground loop
	else:
		draw_rect(Rect2(Vector2.ZERO, VIEW), bg)
	for y in range(y0, y1 + 1):
		for x in range(x0, x1 + 1):
			var pos = Vector2(x * TS, y * TS) + ox
			if ext_tex != null and _draw_ext(_kind_c(x, y), x, y, pos, talls):
				continue
			var k = _tile_kind_draw(x, y)
			if tall_set.has(k):
				var under = "grass" if k in ["tree", "tree2"] and kinds_row.has("grass") and _outdoor() else "floor"
				_draw_tile_kind(under, x, y, pos)
				talls.append([y * TS + 15, "prop", k, pos])
				continue
			_draw_tile_kind(k, x, y, pos)
			if k in ["water", "deep"]:
				var up = kind_at(x, y - 1)
				if up != k and up not in ["water", "deep", "void", "bridge", "boat", "wheel"]:
					draw_rect(Rect2(pos, Vector2(TS, 1)), Color(1, 1, 1, 0.35))
	# conditional blocks drawn as their tile
	for e in map["entities"]:
		if ext_tex != null or art != null:
			break
		if e["type"] == "block" and Game.eval_cond(e["cond"]):
			for by in range(e["y1"], e["y2"] + 1):
				for bx in range(e["x1"], e["x2"] + 1):
					if ext_tex == null or not _draw_ext(e["tile"], bx, by, Vector2(bx * TS, by * TS) + ox, talls):
						_draw_tile_kind(e["tile"], bx, by, Vector2(bx * TS, by * TS) + ox)
	# objects
	for e in map["entities"]:
		if not e.has("x") or not Game.eval_cond(e["cond"]):
			continue
		var pos = Vector2(e["x"] * TS, e["y"] * TS) + ox
		match e["type"]:
			"chest":
				if e.get("hidden", false) and not Game.S["chests"].has(e["id"]):
					continue
				talls.append([e["y"] * TS + 8, "obj", 1 if Game.S["chests"].has(e["id"]) else 0, pos])
			"save":
				talls.append([e["y"] * TS + 8, "obj", 2 + (int(time * 3) % 2), pos])
			"switch":
				var on = e.get("flag", "") != "" and Game.flag(e["flag"])
				talls.append([e["y"] * TS + 8, "obj", 5 if on else 4, pos])
			"heal":
				talls.append([e["y"] * TS + 8, "obj", 6, pos])
			"prop":
				talls.append([e["y"] * TS + 15, "sprite", e["sprite"], pos])
	for n in npcs:
		if hidden_actors.has(n["id"]):
			continue
		talls.append([n["pos"].y + 15, "actor", n, n["pos"] + ox])
	for a in extra_actors:
		talls.append([a["pos"].y + 15, "actor", a, a["pos"] + ox])
	if not hidden_actors.has("player") and vehicle != "ship":
		talls.append([p_pos.y + 15.5, "player", null, p_pos + ox])
	if vehicle == "ship" or ship_pos.x >= 0:
		var sp = Vector2(ship_pos * TS) + ox if vehicle != "ship" else p_pos + ox
		talls.append([sp.y + 15.6, "ship", null, sp])
	talls.sort_custom(func(a, b): return a[0] < b[0])
	for t in talls:
		match t[1]:
			"prop":
				var col: int = prop_col.get(t[2], 0)
				if props_tex:
					draw_texture_rect_region(props_tex, Rect2(t[3] + Vector2(0, -16), Vector2(16, 32)), Rect2(col * 16, 0, 16, 32))
			"ext":
				_ci.draw_texture_rect_region(ext_tex, Rect2(t[3], t[2].size), t[2])
			"a48":
				art.draw_object(self, t[2], cam)
			"a48anim":
				art.draw_anim(self, t[2], cam, time)
			"obj":
				if not _draw_obj48(int(t[2]), t[3]) and objects_tex:
					draw_texture_rect_region(objects_tex, Rect2(t[3], Vector2(16, 16)), Rect2(int(t[2]) * 16, 0, 16, 16))
			"sprite":
				var st = _tex("res://assets/sprites/props/%s.png" % t[2])
				if st:
					draw_texture(st, t[3] + Vector2(8 - st.get_width() / 2.0, 16 - st.get_height()))
			"actor":
				_draw_char(t[2]["sprite"], t[2]["dir"], 1 + int(time * 6) % 4 if t[2].get("moving", false) else 0, t[3], str(t[2].get("id", "")))
			"player":
				var fr = 0
				if p_moving:
					fr = 1 + int(p_anim) % 4
				if riding() and VehicleArt.has("brackhorn"):
					var d8 = VehicleArt.DIR8.get(p_dir, "south")
					var foot = t[3] + Vector2(8, 16)
					var gf = int(time * VehicleArt.fps("brackhorn")) if p_moving else 0
					var row = d8 if p_moving else "walk_" + d8
					draw_rect(Rect2(t[3] + Vector2(0, 13), Vector2(16, 3)), Color(0, 0, 0, 0.25))
					var bob = Vector2(0, -10 - (1 if p_moving and gf % 2 == 1 else 0))
					if p_dir == "up":
						VehicleArt.draw(self, "brackhorn", row, gf, foot + Vector2(0, 4), 0.85)
						_draw_char(p_sprite, p_dir, 0, t[3] + bob)
					else:
						_draw_char(p_sprite, p_dir, 0, t[3] + bob)
						VehicleArt.draw(self, "brackhorn", row, gf, foot + Vector2(0, 4), 0.85)
				else:
					_draw_char(p_sprite, p_dir, fr, t[3])
			"ship":
				_draw_ship(t[3])
	for e in map["entities"]:
		if e["type"] != "hazard" or not Game.eval_cond(e["cond"]):
			continue
		var on = hazard_on(e)
		var warn = hazard_warn(e)
		if not on and not warn:
			continue
		for hy in range(e["y1"], e["y2"] + 1):
			for hx in range(e["x1"], e["x2"] + 1):
				var hp = Vector2(hx * TS, hy * TS) - cam
				if on:
					for k in range(5):
						var px = hp + Vector2(2 + (k * 5 + int(time * 20)) % 12, 12 - (k * 3 + int(time * 30)) % 16)
						draw_rect(Rect2(px, Vector2(3, 3)), Color(0.95, 0.95, 1.0, 0.75))
				else:
					draw_rect(Rect2(hp + Vector2(6, 11), Vector2(4, 3)), Color(1, 1, 1, 0.45))
	if art != null:
		art.draw_over(self, cam)
	if map.get("dark", false):
		draw_rect(Rect2(Vector2.ZERO, VIEW), Color(0.02, 0.02, 0.08, 0.35))
	if tint.a > 0:
		draw_rect(Rect2(Vector2.ZERO, VIEW), tint)
	if banner_t > 0 and banner_text != "":
		# location name window; slides up out of view during its last half second
		var a = clampf(banner_t / 0.5, 0.0, 1.0)
		var w = UI.width(banner_text) + 28
		var r = Rect2(Vector2(round((320 - w) / 2.0), round(10 - (1.0 - a) * 34)), Vector2(w, 22))
		UI.win(self, r)
		UI.text(self, r.position + Vector2(14, 6), banner_text)

## Native field objects: chests (dungeon pack), save points (blue beam effect), healing springs (green aura).
var _chest_tex: Texture2D = null

func _draw_obj48(i: int, pos: Vector2) -> bool:
	if i <= 1:
		if _chest_tex == null:
			var p = "res://assets/ext/cute/dungeon/2.png"
			if not ResourceLoader.exists(p):
				return false
			_chest_tex = load(p)
		UI.native_begin(self, (pos * UI.U).round() / UI.U)
		draw_texture_rect_region(_chest_tex, Rect2(0, 0, 48, 48), Rect2((3 if i == 1 else 0) * 48, 6 * 48, 48, 48))
		UI.native_end(self)
		return true
	if i in [2, 3, 6] and BattleFX.ok():
		var nm = "blue_beam" if i != 6 else "green_aura"
		var ln = BattleFX.length(nm)
		if ln <= 0.0:
			return false
		draw_circle(pos + Vector2(8, 13), 6, Color(0.4, 0.7, 1.0, 0.25) if i != 6 else Color(0.4, 1.0, 0.5, 0.25))
		BattleFX.draw(self, nm, fmod(time, ln), pos + Vector2(8, 15))
		return true
	return false

func _outdoor() -> bool:
	return not String(map.get("tileset", "")).begins_with("interior")

const DIR_ROW := {"down": 0, "left": 1, "right": 2, "up": 3}

func _draw_char(sprite: String, dir: String, frame: int, pos: Vector2, npc_id: String = "") -> void:
	if sprite.begins_with("vestige:"):
		# a waiting Vestige: its idle loop at half the battle size, feet on the tile
		draw_rect(Rect2(pos + Vector2(-4, 13), Vector2(24, 4)), Color(0, 0, 0, 0.3))
		BattleFX.draw_vestige_idle(self, sprite.substr(8), time, pos + Vector2(8, 16), 0.5)
		return
	if not HeroArt.has_field(sprite):
		var nk = HeroArt.npc_key(sprite, npc_id)
		if nk != "" and HeroArt.has_field(nk):
			sprite = nk
	if HeroArt.has_field(sprite):
		draw_rect(Rect2(pos + Vector2(2, 14), Vector2(12, 2)), Color(0, 0, 0, 0.25))
		HeroArt.draw_field(self, sprite, dir if not dir.begins_with("pose") else "down", frame > 0, pos + Vector2(8, 15.67))
		return
	var t = sprite_tex(sprite)
	if t == null:
		return
	# soft shadow at the feet
	draw_rect(Rect2(pos + Vector2(3, 14), Vector2(10, 2)), Color(0, 0, 0, 0.25))
	var row: int = DIR_ROW.get(dir, 0)
	var col = frame
	if dir.begins_with("pose"):
		row = 4
		col = int(dir.substr(4))
	var cw = t.get_width() / 6
	var chh = t.get_height() / 5
	draw_texture_rect_region(t, Rect2(pos + Vector2(8 - cw / 2, 16 - chh), Vector2(cw, chh)), Rect2(col * cw, row * chh, cw, chh))

func ship_key() -> String:
	return "wayfarer" if map_id == "WORLD" else "lanternwake"

func riding() -> bool:
	## Brackhorn mount: on the world map, on foot, once the party has it (Settings can turn riding off)
	# route bots walk on foot: at bot speed a mounted step can finish inside one frame and chain an extra tile
	if QA.route != "":
		return false
	return vehicle == "foot" and map.get("kind", "") == "world" and bool(Game.S["vehicle"].get("mount", false)) \
		and Settings.get_v("ride_mount") != false and not hidden_actors.has("player")

func _draw_ship(pos: Vector2) -> void:
	var key = ship_key()
	if VehicleArt.has(key):
		var flying = vehicle == "ship"
		var d = VehicleArt.DIR8.get(p_dir, "south") if flying else "south"
		var mid = pos + Vector2(8, 8)
		var fr = int(time * VehicleArt.fps(key)) if flying else 0
		# shadow on the ground, hull lifted while aloft
		VehicleArt.draw(self, key, "shadow_" + d, 0, mid + Vector2(0, 4), 0.7, Color(1, 1, 1, 0.3 if flying else 0.45), true)
		var lift = (-18.0 + round(sin(time * 3.0))) if flying else -3.0
		VehicleArt.draw(self, key, d, fr, mid + Vector2(0, lift), 0.7, Color.WHITE, true)
		return
	var t = _tex("res://assets/sprites/wayfarer.png")
	if t:
		var bob = round(sin(time * 3.0))
		draw_texture(t, pos + Vector2(8 - t.get_width() / 2.0, 12 - t.get_height() + bob))

func screen_pos_of(tile: Vector2i) -> Vector2:
	return Vector2(tile * TS) - cam
