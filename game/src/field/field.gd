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

func _tex(path: String) -> Texture2D:
	if tex_cache.has(path):
		return tex_cache[path]
	var t: Texture2D = load(path) if ResourceLoader.exists(path) else null
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
		var tgt = Vector2(p_target * TS)
		p_pos = p_pos.move_toward(tgt, spd * 60.0 * delta)
		p_anim += delta * (10.0 if _running() else 7.0)
		if p_pos.distance_to(tgt) < 0.01:
			p_pos = tgt
			p_tile = p_target
			p_moving = false
			_on_arrive()
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
	if vehicle == "ship":
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

func _update_camera() -> void:
	var c = p_pos + Vector2(8, 8) - VIEW / 2.0
	var mw = W * TS
	var mh = H * TS
	c.x = (mw - VIEW.x) / 2.0 if mw <= VIEW.x else clampf(c.x, 0, mw - VIEW.x)
	c.y = (mh - VIEW.y) / 2.0 if mh <= VIEW.y else clampf(c.y, 0, mh - VIEW.y)
	cam = c.round()

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
	var row: int = kinds_row.get(k, -1)
	if row < 0 or atlas == null:
		draw_rect(Rect2(pos, Vector2(TS, TS)), Color8(20, 16, 28))
		return
	var v = _variant(x, y)
	if k in ["water", "deep", "shallow", "puddle", "wheel", "boat"]:
		v = int(time * 2.0 + (x + y) * 0.0) % 2 if k != "boat" else 0
	draw_texture_rect_region(atlas, Rect2(pos, Vector2(TS, TS)), Rect2(v * TS, row * TS, TS, TS))

func _draw() -> void:
	if map.is_empty():
		return
	var ox = -cam
	var x0 = maxi(0, int(cam.x / TS) - 1)
	var y0 = maxi(0, int(cam.y / TS) - 1)
	var x1 = mini(W - 1, int((cam.x + VIEW.x) / TS) + 1)
	var y1 = mini(H - 1, int((cam.y + VIEW.y) / TS) + 2)
	var bg = Color8(12, 10, 18)
	draw_rect(Rect2(Vector2.ZERO, VIEW), bg)
	var talls = []
	for y in range(y0, y1 + 1):
		for x in range(x0, x1 + 1):
			var k = _tile_kind_draw(x, y)
			var pos = Vector2(x * TS, y * TS) + ox
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
		if e["type"] == "block" and Game.eval_cond(e["cond"]):
			for by in range(e["y1"], e["y2"] + 1):
				for bx in range(e["x1"], e["x2"] + 1):
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
			"obj":
				if objects_tex:
					draw_texture_rect_region(objects_tex, Rect2(t[3], Vector2(16, 16)), Rect2(int(t[2]) * 16, 0, 16, 16))
			"sprite":
				var st = _tex("res://assets/sprites/props/%s.png" % t[2])
				if st:
					draw_texture(st, t[3] + Vector2(8 - st.get_width() / 2.0, 16 - st.get_height()))
			"actor":
				_draw_char(t[2]["sprite"], t[2]["dir"], 1 + int(time * 6) % 4 if t[2]["moving"] else 0, t[3])
			"player":
				var fr = 0
				if p_moving:
					fr = 1 + int(p_anim) % 4
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
	if map.get("dark", false):
		draw_rect(Rect2(Vector2.ZERO, VIEW), Color(0.02, 0.02, 0.08, 0.35))
	if tint.a > 0:
		draw_rect(Rect2(Vector2.ZERO, VIEW), tint)
	if banner_t > 0 and banner_text != "":
		var a = clampf(banner_t, 0.0, 1.0)
		var w = UI.width(banner_text) + 20
		var r = Rect2(Vector2((320 - w) / 2.0, 12), Vector2(w, 16))
		draw_rect(r, Color(0.05, 0.06, 0.12, 0.8 * a))
		UI.text(self, r.position + Vector2(10, 3), banner_text, Color(UI.C_GOLD, a))

func _outdoor() -> bool:
	return not String(map.get("tileset", "")).begins_with("interior")

const DIR_ROW := {"down": 0, "left": 1, "right": 2, "up": 3}

func _draw_char(sprite: String, dir: String, frame: int, pos: Vector2) -> void:
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
	draw_texture_rect_region(t, Rect2(pos + Vector2(-4, -16), Vector2(24, 32)), Rect2(col * 24, row * 32, 24, 32))

func _draw_ship(pos: Vector2) -> void:
	var t = _tex("res://assets/sprites/wayfarer.png")
	if t:
		var bob = round(sin(time * 3.0))
		draw_texture(t, pos + Vector2(8 - t.get_width() / 2.0, 12 - t.get_height() + bob))

func screen_pos_of(tile: Vector2i) -> Vector2:
	return Vector2(tile * TS) - cam
