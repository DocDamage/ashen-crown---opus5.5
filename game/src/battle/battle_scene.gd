class_name BattleScene
extends Node2D
## BattlePresenter: reads BattleModel events, animates, and collects player commands.
## Holds no authoritative HP/inventory: everything displayed is read from the model.

signal finished(result: String)

## FF6-style staging: the party stands in a staggered column on the right, facing left; enemies own the left/centre
## of the ground plane. Foot anchors (x zig-zags so neighbouring sprites never overlap).
const PARTY_ANCHORS := [Vector2(240, 88), Vector2(262, 104), Vector2(240, 120), Vector2(262, 136), Vector2(240, 152)]
## Overhaul heroes (HeroArt) stand on these anchors at native size; the old 16x32 battlers keep PARTY_SCALE.
const PARTY_SCALE := 2          # library battlers are ~16x32; drawn 2x (nearest) so the party reads at FF6 weight
const ARENA_H := 168
const ENEMY_BOX := Rect2(4, 6, 208, 160)   # enemies (and their frames) stay inside this box
const FRAMES := {"idle": [0, 4], "attack": [4, 6], "cast": [10, 4], "hurt": [14, 2], "guard": [16, 2], "victory": [18, 4], "ko": [22, 1], "step": [23, 4]}

var main: Node
var model: BattleModel
var form: Dictionary
var bg: Texture2D
var bg_native = false     # 960x720 painted arena (Assets/_processed/battle_backgrounds), drawn full screen
var acc = 0.0
var t = 0.0
var tex = {}
var anim = {}            # battler id -> {name, t}
var offsets = {}         # battler id -> Vector2 (step forward)
var popups: Array = []
var banner = ""
var banner_t = 0.0
var tells = {}           # enemy id -> text
var presenting = false
var done = false
var ui: Control
var cmd_menu: MenuList = null
var sub_menu: MenuList = null
var selecting: BattleModel.Battler = null
var pending_cmd = {}
var target_mode = ""     # "" | enemy_one | enemy_all | ally_one | ally_all | self | ally_ko
var target_idx = 0
var target_list: Array = []
var enemy_pos = {}
var flashes = {}
var vfx: Array = []
var sfx_sprites: Array = []   # sprite effects {name, pos, t, [from, to, travel]}
var summon_fx = {}
var pause_open = false
var hint = ""
var hint_t = 0.0
var _victory_pose = false
var intent_reveal = false
var fast = false
# sys s4: auto-battle ("attack" or "repeat" each hero's last command), toggled with Run during battle
var auto_mode = "off"
var auto_default = "off"
var last_cmd = {}

var stage: BattleStage3D = null     # HD-2D battle stage (render3d/battle_stage3d.gd); null = flat 2D

func _bx(p: Vector2) -> void:
	var m = stage.xf(p) if stage != null else Transform2D.IDENTITY
	UI.base = m
	draw_set_transform_matrix(m)

func _bx_move(p: Vector2) -> void:
	# position only (text and cursors keep their size)
	var m = Transform2D(0.0, (stage.point(p) - p) if stage != null else Vector2.ZERO)
	UI.base = m
	draw_set_transform_matrix(m)

func _bx_reset() -> void:
	UI.base = Transform2D.IDENTITY
	draw_set_transform_matrix(UI.base)

func setup(form_id: String, seed_value: int, opts: Dictionary) -> void:
	form = Content.formation(form_id)
	model = BattleModel.new(Content.data)
	var party = Game.battle_party()
	model.setup(party, form["enemies"], Game.battle_inventory(), seed_value,
		{"mode": Settings.get_v("battle_mode"), "speed": float(Settings.get_v("battle_speed")), "boss": form.get("boss", false),
		 "encounter": form, "difficulty": Game.battle_difficulty(), "no_flee": opts.get("flags", []).has("noflee"),
		 "reserves": Game.battle_reserve_party() if not opts.get("flags", []).has("noreserve") else []})
	bg = _t("res://assets/battle_bg/%s.png" % form.get("bg", "quarry"))
	bg_native = bg != null
	if bg == null:
		bg = _t("res://assets/sprites/bg/%s.png" % form.get("bg", "quarry"))
	for eid in model.enemy_ids:
		Game.bestiary_seen(model.battlers[eid].ref, "seen")
	if Settings.get_v("hd2d") != false:
		stage = BattleStage3D.make(self, str(form.get("bg", "quarry")), bg)
	_layout_enemies()
	ui = Control.new()
	ui.size = Vector2(320, 240)
	ui.draw.connect(_draw_ui)
	var layer = CanvasLayer.new()
	layer.layer = 5
	layer.scale = Vector2(UI.U, UI.U)
	add_child(layer)
	layer.add_child(ui)
	for bid in model.party_ids + model.reserve_ids:
		anim[bid] = {"name": "idle", "t": randf()}
	Audio.music(form.get("music", "M025"), 0.0)
	hint = form.get("hint", "")
	hint_t = 6.0 if hint != "" else 0.0
	intent_reveal = false
	auto_default = str(Settings.get_v("auto_battle")) if Settings.get_v("auto_battle") != null else "off"
	auto_mode = auto_default if not QA.active else "off"
	for bid in model.party_ids:
		if model.battlers[bid].passives.has("reveal_affinity"):
			for eid in model.enemy_ids:
				Game.bestiary_seen(model.battlers[eid].ref, "affinity")
	main.router.push(self)

func _t(path: String) -> Texture2D:
	if tex.has(path):
		return tex[path]
	var r: Texture2D = Content.load_art(path)
	tex[path] = r
	return r

func _layout_enemies() -> void:
	var ids = model.enemy_ids.filter(func(x): return not model.battlers[x].tags.has("part"))
	var parts = model.enemy_ids.filter(func(x): return model.battlers[x].tags.has("part"))
	# foot positions on the ground plane (horizon ~y96): back rank higher/smaller, front rank lower
	var boss = false
	for eid in ids:
		if model.battlers[eid].is_boss():
			boss = true
	if boss:
		var bsz = _enemy_size(ids[0])
		enemy_pos[ids[0]] = Vector2(clampf(20 + bsz.x / 2.0, 0, 110), 162)
		var right = enemy_pos[ids[0]].x + bsz.x / 2.0
		var others = ids.slice(1)
		for i in range(others.size()):
			enemy_pos[others[i]] = Vector2(minf(right + 30, 190), 100 + i * 46)
		for i in range(parts.size()):
			var psz = _enemy_size(parts[i])
			enemy_pos[parts[i]] = Vector2(minf(right + 8 + psz.x / 2.0, 204 - psz.x / 2.0), 130 + i * 34)
	else:
		_layout_rows(ids)
	# keep every sprite inside the enemy area, whatever its size
	for eid in enemy_pos.keys():
		var sz = _enemy_size(eid)
		var p: Vector2 = enemy_pos[eid]
		p.x = clampf(p.x, ENEMY_BOX.position.x + sz.x / 2.0, ENEMY_BOX.end.x - sz.x / 2.0)
		p.y = clampf(p.y, ENEMY_BOX.position.y + sz.y, ENEMY_BOX.end.y)
		enemy_pos[eid] = p

## Ordinary formations: one staggered rank when the sprites fit side by side, otherwise a back rank (higher on the
## ground plane) and a front rank offset by half a slot, so large painted enemies overlap as little as possible.
func _layout_rows(ids: Array) -> void:
	var n = ids.size()
	if n == 0:
		return
	var W = ENEMY_BOX.size.x
	var total = 0.0
	for eid in ids:
		total += _enemy_size(eid).x
	var rows: Array = [ids] if (total + 6 * (n - 1) <= W or n == 1) else [ids.slice(0, (n + 1) / 2), ids.slice((n + 1) / 2)]
	var ys = [158] if rows.size() == 1 else [116, 166]
	for r in range(rows.size()):
		var row: Array = rows[r]
		var sum = 0.0
		for eid in row:
			sum += _enemy_size(eid).x
		var gap = clampf((W - sum) / float(row.size() + 1), -24.0, 40.0)
		var x = ENEMY_BOX.position.x + maxf(gap, 0.0) + (8.0 if r == 1 else 0.0)
		for i in range(row.size()):
			var w = _enemy_size(row[i]).x
			var stagger = (-10.0 if i % 2 == 0 else 2.0) if rows.size() == 1 and row.size() > 1 else 0.0
			enemy_pos[row[i]] = Vector2(x + w / 2.0, ys[r] + stagger)
			x += w + gap

## Frame size of an enemy sheet (4 frames side by side: idle, idle, tell, hurt).
func _enemy_size(eid: String) -> Vector2:
	var b = model.battlers.get(eid)
	if b == null:
		return Vector2(32, 32)
	var art = _enemy_art(b)
	if art:
		var em = _enemy_meta(b)
		if not em.is_empty():
			return Vector2(float(em.get("w", 32)), float(em.get("h", 32))) / float(UI.U)
		return Vector2(art.get_width(), art.get_height()) / float(UI.U)
	var tx = _enemy_tex(b)
	if tx == null:
		return Vector2(32, 32)
	return Vector2(tx.get_width() / 4, tx.get_height())

## Frame strip metadata for enemy art v2 (cell, foot, tags idle/attack/cast/hurt); empty for single images.
var _emeta = {}
func _enemy_meta(b) -> Dictionary:
	var key: String = str(Content.enemy(b.ref).get("sprite", b.ref)).split("@")[0]
	if not _emeta.has(key):
		var jp = "res://assets/ext/enemies/%s.json" % key
		_emeta[key] = JSON.parse_string(FileAccess.get_file_as_string(jp)) if FileAccess.file_exists(jp) else {}
		if _emeta[key] == null:
			_emeta[key] = {}
	return _emeta[key]

## Which frame of the strip to show now.
func _enemy_frame(eid: String, e, m: Dictionary) -> int:
	var tags: Dictionary = m.get("tags", {})
	var a: Dictionary = anim.get(eid, {})
	if not a.is_empty() and float(a["t"]) < 0.55 and tags.has(a["name"]):
		var r: Array = tags[a["name"]]
		var n = int(r[1]) - int(r[0]) + 1
		return int(r[0]) + mini(int(float(a["t"]) / 0.55 * n), n - 1)
	if flashes.get(eid, 0.0) > 0 and tags.has("hurt"):
		return int(tags["hurt"][0])
	if e.state == "CASTING" and tags.has("cast"):
		return int(tags["cast"][0]) + int(t * 4.0) % 2
	var idle: Array = tags.get("idle", [0, 0])
	var seq = [0, 1, 2, 1]
	var k = seq[int(t * 3.0 + float(hash(eid) % 5)) % 4]
	return int(idle[0]) + mini(k, int(idle[1]) - int(idle[0]))

## Native-resolution enemy art (assets/ext/enemies/<sprite>.png, installed by tools/art/install_overhaul.py enemies).
func _enemy_art(b) -> Texture2D:
	var key: String = str(Content.enemy(b.ref).get("sprite", b.ref)).split("@")[0]
	var path = "res://assets/ext/enemies/%s.png" % key
	if not tex.has(path):
		tex[path] = load(path) if ResourceLoader.exists(path) else null
	return tex[path]

func _enemy_tex(b) -> Texture2D:
	return _t("res://assets/sprites/enemies/%s.png" % Content.enemy(b.ref).get("sprite", b.ref).split("@")[0])

func _party_tex(b) -> Texture2D:
	return _t("res://assets/sprites/battle/%s.png" % b.ref)

# ======================================================================
# Loop
# ======================================================================
func _process(delta: float) -> void:
	t += delta
	for k in anim:
		anim[k]["t"] += delta
	for p in popups:
		p["t"] -= delta
	popups = popups.filter(func(p): return p["t"] > 0)
	for v in vfx:
		v["t"] -= delta
	vfx = vfx.filter(func(v): return v["t"] > 0)
	for fx in sfx_sprites:
		fx["t"] += delta
	if not summon_fx.is_empty():
		summon_fx["t"] += delta
	sfx_sprites = sfx_sprites.filter(func(fx): return fx["t"] < fx["len"])
	if banner_t > 0:
		banner_t -= delta
	if hint_t > 0:
		hint_t -= delta
	ui.queue_redraw()
	queue_redraw()
	if done or pause_open:
		return
	model.menu_open = (cmd_menu != null or sub_menu != null or target_mode != "")
	if not presenting:
		if model.locked:
			_present_next()
			return
		acc += delta
		var n = 0
		while acc >= BattleModel.DT and n < 4:
			acc -= BattleModel.DT
			model.step()
			n += 1
			if model.locked:
				break
		if model.result != "" and not model.locked:
			_finish()
			return
		if cmd_menu == null and target_mode == "" and sub_menu == null:
			var w = model.awaiting_input()
			if w != null:
				if auto_mode != "off" and _auto_command(w):
					pass
				else:
					_open_commands(w)

func _finish() -> void:
	if done:
		return
	done = true
	_close_menus()
	main.router.pop(self)
	if model.result == "victory":
		for bid in model.party_ids:
			if model.battlers[bid].alive():
				anim[bid] = {"name": "victory", "t": 0.0}
	emit_signal("finished", model.result)

func show_victory() -> void:
	if Audio.jingle("victory") <= 0.0:
		Audio.music("M029", 0.0)
	banner = T.s("battle.victory")
	banner_t = 1.6
	await get_tree().create_timer(1.4).timeout

# ======================================================================
# Event presentation
# ======================================================================
func _present_next() -> void:
	presenting = true
	var ev: Dictionary = model.events[0]
	var sk = fast or Input.is_action_pressed("g_skip")
	match ev["type"]:
		"action":
			await _present_action(ev, sk)
		"tell":
			var b = model.battlers[ev["actor"]]
			tells[ev["actor"]] = ev["text"]
			var tn = []
			for x in ev.get("targets", []):
				tn.append(model.battlers[x].name)
			banner = "%s: %s" % [b.name, ev["text"]]
			banner_t = 1.6
			Audio.sfx("FX023")
			await _wait(0.5 if not sk else 0.05)
		"skip":
			var b2 = model.battlers[ev["actor"]]
			banner = "%s is %s." % [b2.name, "asleep" if ev["status"] == "sleep" else "stunned"]
			banner_t = 1.0
			await _wait(0.5 if not sk else 0.05)
		"lost_turn":
			pass
		"leap_up":
			anim[ev["actor"]] = {"name": "step", "t": 0.0}
			Audio.sfx("FX017")
			await _wait(0.25 if not sk else 0.02)
		"phase":
			banner = ev.get("text", "")
			banner_t = 2.4
			if not Settings.get_v("reduced_flash"):
				flashes[ev["actor"]] = 0.5
			Audio.sfx("FX021")
			await _wait(1.2 if not sk else 0.1)
			for r in ev.get("results", []):
				if r["kind"] == "spawn":
					_layout_enemies()
	model.ack()
	presenting = false

func _present_action(ev: Dictionary, sk: bool) -> void:
	var b = model.battlers[ev["actor"]]
	tells.erase(ev["actor"])
	banner = ("%s: %s" % [b.name, ev.get("name", "")]) if ev.get("name", "") != "" else ""
	banner_t = 1.2
	var an: String = ev.get("anim", "attack")
	if b.side == 0:
		var a2 = "attack"
		match an:
			"cast", "summon", "item": a2 = "cast"
			"ult": a2 = "ult"
			"guard": a2 = "guard"
			"shoot": a2 = "attack"
			"leap": a2 = "attack"
			"step": a2 = "step"
		anim[b.id] = {"name": a2, "t": 0.0}
		offsets[b.id] = Vector2(-10, 0) if not HeroArt.has_battle(b.ref) else Vector2(-16, 0)
	else:
		offsets[b.id] = Vector2(8, 0)
		if _enemy_meta(b).is_empty():
			flashes[b.id] = 0.15
		else:
			anim[b.id] = {"name": "cast" if an in ["cast", "summon", "item"] else "attack", "t": 0.0}
	var elem: String = ev.get("element", "physical")
	var sfx = "FX014"
	match an:
		"cast": sfx = {"fire": "FX019", "ice": "FX020", "storm": "FX021", "light": "FX022"}.get(elem, "FX019")
		"shoot": sfx = "FX017" if b.ref == "C05" else "FX018"
		"guard": sfx = "FX016"
		"item": sfx = "FX002"
		"summon": sfx = "FX030"
	Audio.sfx(sfx)
	# HD-2D: the camera pushes in on the exchange (attacker and first target), then settles back
	var cam_on = stage != null and not sk and Settings.get_v("battle_camera") != false and an != "guard"
	if cam_on:
		var tgt0 = ""
		for r in ev.get("results", []):
			if model.battlers.has(str(r.get("id", ""))):
				tgt0 = r["id"]
				break
		stage.act(_battler_pos(b.id), _battler_pos(tgt0) if tgt0 != "" else _battler_pos(b.id))
	var fxspec: Dictionary = _action_fx_cast(ev) if not sk else {}
	if ev.has("summon"):
		await _summon_fx(ev["summon"], sk)
	elif b.side == 0 and HeroArt.has_battle(b.ref):
		# hit lands a little past the middle of the hero's own animation
		await _wait(clampf(HeroArt.anim_length(b.ref, anim[b.id]["name"]) * 0.55, 0.2, 0.9) if not sk else 0.02)
	else:
		await _wait(0.22 if not sk else 0.02)
	# effects on targets
	if fxspec.get("bolt", "") != "":
		var tgt = ""
		for r in ev["results"]:
			if model.battlers.has(str(r.get("id", ""))):
				tgt = r["id"]
				break
		if tgt != "":
			_fx_bolt(fxspec["bolt"], _battler_pos(ev["actor"]), _battler_pos(tgt), 0.25)
			await _wait(0.25)
	_action_fx_hit(ev, fxspec)
	var any_hit = false
	for r in ev["results"]:
		_result_popup(r, elem, ev)
		if r["kind"] == "damage" and int(r.get("amount", 0)) > 0:
			any_hit = true
	if any_hit:
		Audio.sfx("FX015")
	for m in ev.get("msgs", []):
		_popup_msg(m)
	for rv in ev.get("reveal", []):
		Game.bestiary_seen(rv["id"], rv["what"] if rv["what"] != "affinity" else "affinity")
		if rv["what"] == "intent":
			intent_reveal = true
	await _wait(0.45 if not sk else 0.05)
	if cam_on:
		stage.release()
	offsets.erase(b.id)
	if b.side == 0 and b.alive():
		anim[b.id] = {"name": "idle", "t": 0.0}
	for r in ev["results"]:
		if r["kind"] == "ko":
			Audio.sfx("FX025" if r["id"].begins_with("A") else "FX026")

func _fx(name: String, pos: Vector2, delay: float = 0.0) -> void:
	if name == "" or not BattleFX.has(name):
		return
	sfx_sprites.append({"name": name, "pos": pos, "t": -delay, "len": BattleFX.length(name)})

func _fx_bolt(name: String, from: Vector2, to: Vector2, travel: float) -> void:
	if name == "" or not BattleFX.has(name):
		return
	sfx_sprites.append({"name": name, "pos": from, "from": from, "to": to, "travel": travel, "t": 0.0, "len": travel})

## Effects for an action: cast effects at the actor while the animation plays; bolt; hit effects on targets.
func _action_fx_cast(ev: Dictionary) -> Dictionary:
	var spec: Dictionary = BattleFX.for_ability(ev.get("ability", "")) if ev.has("ability") else {}
	if ev.has("summon"):
		spec = BattleFX.for_ability(str(Content.data["vestiges"].get(ev["summon"], {}).get("summon", "")))
	if spec.is_empty() and ev.get("anim", "") in ["attack", "shoot"]:
		var el = str(ev.get("element", "physical"))
		spec = {"cast": [], "bolt": "", "hit": [({"light": "holy"}.get(el, el) + "_impact") if el not in ["physical", "none", ""] else "white_shine"], "mode": "each"}
	for c in spec.get("cast", []):
		_fx(c, _battler_pos(ev["actor"]) + Vector2(0, 6))
	return spec

func _action_fx_hit(ev: Dictionary, spec: Dictionary) -> void:
	if spec.is_empty():
		return
	var ids = []
	for r in ev["results"]:
		var rid = str(r.get("id", ""))
		if rid != "" and rid != "DECOY" and model.battlers.has(rid) and not ids.has(rid) and r["kind"] in ["damage", "heal", "status+", "revive", "miss", "absorb", "mp", "status-"]:
			ids.append(rid)
	if ids.is_empty():
		return
	var hits: Array = spec.get("hit", [])
	if spec.get("mode", "each") == "center":
		var c = Vector2.ZERO
		for i in ids:
			c += _battler_pos(i)
		c /= ids.size()
		for h in hits:
			_fx(h, c)
	else:
		for i in ids:
			for h in hits:
				_fx(h, _battler_pos(i))

func _summon_fx(vid: String, sk: bool) -> void:
	var short: bool = Settings.get_v("short_summons") or sk
	var vm = BattleFX.vestige(vid)
	var full = 1.6
	if not vm.is_empty():
		full = BattleFX.tag_length(vm, "appear") + 1.2 + BattleFX.tag_length(vm, "vanish")
	summon_fx = {"id": vid, "t": 0.0, "dur": 0.6 if short else full}
	var el = str(Content.data["vestiges"].get(vid, {}).get("element", "arcane"))
	_fx({"light": "holy", "none": "arcane"}.get(el, el) + "_rune", Vector2(262, 150))
	await _wait(summon_fx["dur"])
	summon_fx = {}

func _result_popup(r: Dictionary, elem: String, ev: Dictionary) -> void:
	var id: String = r["id"]
	if id == "DECOY":
		return
	var pos = _battler_pos(id) + Vector2(0, -30)
	var txt = ""
	var col = UI.C_TEXT
	match r["kind"]:
		"damage":
			txt = str(r["amount"])
			if r.get("crit", false):
				txt += "!"
			col = Color8(255, 255, 255) if not r.get("weak", false) else Color8(255, 200, 80)
			if r.get("resisted", false):
				txt += " RESIST"
			if r.get("weak", false):
				txt += " WEAK"
			if id.begins_with("A"):
				anim[id] = {"name": "hurt", "t": 0.0}
			flashes[id] = 0.2
			vfx.append({"pos": _battler_pos(id) + Vector2(0, -16), "elem": elem, "t": 0.35, "dur": 0.35})
		"heal":
			txt = "+" + str(r["amount"])
			col = UI.C_GREEN
		"mp":
			txt = ("+" if int(r["amount"]) >= 0 else "") + str(r["amount"]) + " MP"
			col = UI.C_BLUE
		"miss":
			txt = "MISS"
			col = UI.C_DIM
		"immune":
			txt = "IMMUNE" if not r.has("status") else "IMMUNE " + r["status"].capitalize()
			col = UI.C_DIM
		"resist":
			txt = "RESIST" + (" " + r["status"].capitalize() if r.has("status") else "")
			col = UI.C_DIM
		"absorb":
			txt = "ABSORB +" + str(r["amount"])
			col = UI.C_GREEN
		"status+":
			txt = r["status"].capitalize()
			_fx(BattleFX.for_status(str(r["status"])), _battler_pos(id))
			col = Color8(220, 170, 255)
			Audio.sfx("FX023")
		"status-":
			txt = "Cured"
			col = UI.C_GREEN
			Audio.sfx("FX024")
		"revive":
			txt = "Revived"
			col = UI.C_GREEN
			anim[id] = {"name": "idle", "t": 0.0}
		"ko":
			txt = ""
			if id.begins_with("A"):
				anim[id] = {"name": "death", "t": 0.0}
		"dot":
			txt = str(r["amount"])
			col = Color8(200, 140, 255)
		"selfcost":
			txt = "-" + str(r["amount"])
			col = Color8(255, 150, 120)
		"oath":
			txt = "Oath: " + str(r["status"]).capitalize()
			col = UI.C_GOLD
		"capture":
			txt = "CAPTURED"
			col = UI.C_GOLD
		"swap_in":
			txt = "IN"
			col = UI.C_HI
			anim[id] = {"name": "idle", "t": 0.0}
		"atb", "reveal", "spawn", "decoy", "doom":
			txt = "" if r["kind"] != "doom" else "DOOM"
	if txt != "":
		popups.append({"text": txt, "pos": pos + Vector2(0, -8 * _stack_at(id)), "t": 1.0, "col": col, "id": id,
			"elem": elem if r["kind"] == "damage" and elem not in ["", "none", "physical"] else ""})

func _stack_at(id: String) -> int:
	var n = 0
	for p in popups:
		if p["id"] == id:
			n += 1
	return n

func _popup_msg(m: String) -> void:
	banner = m
	banner_t = 1.4

func _wait(s: float) -> void:
	await get_tree().create_timer(s).timeout

func _battler_pos(id: String) -> Vector2:
	var b = model.battlers.get(id)
	if b == null:
		return Vector2(160, 80)
	if b.side == 0:
		var i = model.party_ids.find(id)
		return PARTY_ANCHORS[i] + (Vector2(0, -12) if HeroArt.has_battle(b.ref) else Vector2(0, -20 * PARTY_SCALE))
	return enemy_pos.get(id, Vector2(88, 110)) + Vector2(0, -minf(_enemy_size(id).y * 0.55, 48))

# ======================================================================
# Commands
# ======================================================================
func _open_commands(b) -> void:
	selecting = b
	model.begin_select(b)
	var cdef = Content.ch(b.ref)
	var items = [
		{"text": T.s("battle.attack"), "value": "attack"},
		{"text": cdef["role_command"], "value": "role", "enabled": _role_list(b).size() > 0, "reason": T.s("battle.no_techniques")},
	]
	if model.limit_ready(b):
		items.push_front({"text": "Limit", "value": "limit", "color": UI.C_GOLD, "desc": "The limit gauge is full."})
	if not _magic_list(b).is_empty():
		items.append({"text": T.s("battle.magic"), "value": "magic"})
	if b.blue_rule != "":
		items.append({"text": "Lore", "value": "lore", "enabled": not b.blue.is_empty(), "reason": "No enemy lore learned yet"})
	var cap_id = str(Content.data.get("capture", {}).get("id", ""))
	if cap_id != "" and b.abilities.has(cap_id):
		items.append({"text": "Capture", "value": "capture", "desc": Content.ability(cap_id).get("desc", "")})
	items += [
		{"text": T.s("battle.item"), "value": "item"},
		{"text": T.s("battle.defend"), "value": "defend"},
	]
	var vid: String = model.links.get(b.id, "")
	if vid != "":
		var v = model.validate(b, {"type": "summon"})
		items.append({"text": T.s("battle.summon"), "value": "summon", "enabled": v["ok"], "reason": v.get("reason", "")})
	if not model.reserve_ids.is_empty():
		var vs = model.validate(b, {"type": "swap"})
		items.append({"text": "Swap", "value": "swap", "enabled": vs["ok"], "reason": vs.get("reason", "")})
	items.append({"text": T.s("battle.row"), "value": "row"})
	var ve = model.validate(b, {"type": "escape"})
	items.append({"text": T.s("battle.escape"), "value": "escape", "enabled": ve["ok"], "reason": ve.get("reason", "")})
	cmd_menu = MenuList.new()
	cmd_menu.position = Vector2(4, 170)
	cmd_menu.size = Vector2(88, 68)
	cmd_menu.memory_key = "cmd_" + b.ref
	cmd_menu.allow_cancel = true
	cmd_menu.setup(items, 5)
	ui.add_child(cmd_menu)
	main.router.push(cmd_menu)
	cmd_menu.chosen.connect(_on_cmd)
	cmd_menu.cancelled.connect(func(): _cycle_ready())
	Audio.ui("FX001")

func _cycle_ready() -> void:
	# pass the turn to the next ready character (the current one stays ready)
	if model.ready_order.size() > 1 and selecting != null:
		model.cancel_select(selecting)
		model.ready_order.erase(selecting.id)
		model.ready_order.append(selecting.id)
		_close_menus()

func _role_list(b) -> Array:
	var out = []
	for aid in b.abilities:
		var a = Content.ability(aid)
		if a.is_empty() or a.get("kind", "") == "summon" or str(a.get("owner", "")) != b.ref or a.has("command"):
			continue
		out.append(aid)
	return out

## Spells a Vestige taught (and accessory spells): anything the hero knows that is not their own technique.
func _magic_list(b) -> Array:
	var out = []
	for aid in b.abilities:
		var a = Content.ability(aid)
		if a.is_empty() or a.get("kind", "") == "summon" or str(a.get("owner", "")) == b.ref:
			continue
		out.append(aid)
	return out

func _on_cmd(_i: int, it: Dictionary) -> void:
	var b = selecting
	match it["value"]:
		"attack":
			pending_cmd = {"type": "attack"}
			_begin_target("enemy_one")
		"defend":
			_commit({"type": "defend"})
		"row":
			_commit({"type": "row"})
		"escape":
			_commit({"type": "escape"})
		"summon":
			var vid: String = model.links[b.id]
			var a = Content.ability(Content.data["vestiges"][vid]["summon"])
			pending_cmd = {"type": "summon"}
			_confirm_summon(a)
		"role":
			_open_sub_abilities(b)
		"magic":
			_open_sub_abilities(b, true)
		"item":
			_open_sub_items(b)
		"limit":
			_open_sub_abilities(b, false, b.limits)
		"lore":
			_open_sub_abilities(b, false, b.blue)
		"capture":
			pending_cmd = {"type": "ability", "id": str(Content.data["capture"]["id"])}
			_begin_target("enemy_one")
		"swap":
			_open_sub_swap(b)

func _confirm_summon(a: Dictionary) -> void:
	_commit({"type": "summon"})

func _open_sub_abilities(b, magic: bool = false, only: Array = []) -> void:
	var items = []
	for aid in (only if not only.is_empty() else (_magic_list(b) if magic else _role_list(b))):
		var a = Content.ability(aid)
		var v = model.validate(b, {"type": "ability", "id": aid})
		var cost = model.mp_cost(b, a)
		items.append({"spell": aid, "text": a["name"], "right": str(cost) if cost > 0 else "", "value": aid, "enabled": v["ok"], "reason": v.get("reason", ""), "desc": a.get("desc", "")})
	_open_sub(items, "role")

## Swap: pick a reserve hero to take the acting hero's place.
func _open_sub_swap(b) -> void:
	var items = []
	for rid in model.reserve_ids:
		var r = model.battlers[rid]
		var v = model.validate(b, {"type": "swap", "reserve": rid})
		items.append({"text": r.name, "right": "%d/%d" % [r.hp, r.mhp], "value": rid, "enabled": v["ok"], "reason": v.get("reason", ""),
			"desc": "%s steps back; %s enters with readiness partly filled." % [b.name, r.name]})
	_open_sub(items, "swap")

func _open_sub_items(b) -> void:
	var items = []
	var ids: Array = model.inventory.keys()
	ids.sort()
	for iid in ids:
		if int(model.inventory[iid]) <= 0:
			continue
		var it = Content.item(iid)
		var v = model.validate(b, {"type": "item", "id": iid})
		items.append({"icon": iid, "text": it["name"], "right": str(model.inventory[iid]), "value": iid, "enabled": v["ok"], "reason": v.get("reason", ""), "desc": it.get("desc", "")})
	if items.is_empty():
		items.append({"text": "(no items)", "enabled": false, "reason": "Inventory empty", "value": ""})
	_open_sub(items, "item")

func _open_sub(items: Array, kind: String) -> void:
	sub_menu = MenuList.new()
	sub_menu.position = Vector2(4, 104)
	sub_menu.size = Vector2(170, 134)
	sub_menu.memory_key = "sub_%s_%s" % [kind, selecting.ref]
	sub_menu.setup(items, 10)
	ui.add_child(sub_menu)
	main.router.push(sub_menu)
	sub_menu.set_meta("kind", kind)
	sub_menu.chosen.connect(func(_i, it):
		if kind == "swap":
			_commit({"type": "swap", "reserve": it["value"]})
			return
		if kind == "role":
			var a = Content.ability(it["value"])
			pending_cmd = {"type": "ability", "id": it["value"]}
			var tm: String = a.get("target", "enemy_one")
			if a.get("revive", false) and tm == "ally_one":
				tm = "ally_ko"
			_begin_target(tm)
		else:
			var itd = Content.item(it["value"])
			pending_cmd = {"type": "item", "id": it["value"]}
			var tm2: String = itd.get("target", "ally_one")
			if itd.get("revive", false):
				tm2 = "ally_ko"
			if tm2 == "party":
				tm2 = "ally_all"
			_begin_target(tm2))
	sub_menu.cancelled.connect(func():
		main.router.pop(sub_menu)
		sub_menu.queue_free()
		sub_menu = null)

func _begin_target(mode: String) -> void:
	target_mode = mode
	target_list = []
	match mode:
		"enemy_one", "enemy_all":
			for eid in model.enemy_ids:
				if model.battlers[eid].targetable():
					target_list.append(eid)
		"ally_one", "ally_all":
			for pid in model.party_ids:
				if model.battlers[pid].alive():
					target_list.append(pid)
		"ally_ko":
			for pid in model.party_ids:
				if not model.battlers[pid].alive():
					target_list.append(pid)
			if target_list.is_empty():
				for pid in model.party_ids:
					target_list.append(pid)
		"self":
			target_list = [selecting.id]
	if target_list.is_empty():
		target_mode = ""
		Audio.ui("FX004")
		return
	target_idx = 0
	if mode in ["ally_one"]:
		# default to the lowest HP ally
		var lo = 0
		for i in range(target_list.size()):
			var tb = model.battlers[target_list[i]]
			var lb = model.battlers[target_list[lo]]
			if float(tb.hp) / tb.mhp < float(lb.hp) / lb.mhp:
				lo = i
		target_idx = lo
	main.router.push(self)

func handle(ev: String) -> void:
	if ev == "menu" and target_mode == "" and not done:
		pause_open = not pause_open
		model.paused = pause_open
		Audio.ui("FX002")
		return
	if pause_open:
		if ev in ["cancel", "confirm"]:
			pause_open = false
			model.paused = false
		return
	if target_mode == "":
		return
	match ev:
		"up", "left":
			target_idx = (target_idx - 1 + target_list.size()) % target_list.size()
			Audio.ui("FX001")
		"down", "right":
			target_idx = (target_idx + 1) % target_list.size()
			Audio.ui("FX001")
		"cancel":
			target_mode = ""
			_restore_focus()
			Audio.ui("FX003")
		"confirm":
			var tg: Array
			if target_mode in ["enemy_all", "ally_all"]:
				tg = target_list.duplicate()
			else:
				tg = [target_list[target_idx]]
			var c = pending_cmd.duplicate()
			c["targets"] = tg
			if c["type"] == "ability" and model.battlers[tg[0]].side == 1 and Content.ability(c["id"]).get("kind", "") == "heal":
				c["hostile_heal"] = true
			target_mode = ""
			_restore_focus()
			_commit(c)

func _restore_focus() -> void:
	if sub_menu != null:
		main.router.push(sub_menu)
	elif cmd_menu != null:
		main.router.push(cmd_menu)

func _commit(c: Dictionary) -> void:
	var r = model.commit(selecting, c)
	if not r["ok"]:
		Audio.ui("FX004")
		banner = r["reason"]
		banner_t = 1.2
		return
	if selecting != null:
		last_cmd[selecting.ref] = c.duplicate(true)
	_close_menus()

func _close_menus() -> void:
	for m in [sub_menu, cmd_menu]:
		if m != null:
			main.router.pop(m)
			m.queue_free()
	sub_menu = null
	cmd_menu = null
	target_mode = ""
	selecting = null

# ======================================================================
# Drawing
# ======================================================================
func _draw() -> void:
	if stage != null:
		draw_texture_rect(stage.texture(), Rect2(Vector2.ZERO, BattleStage3D.AREA), false)
	elif bg and bg_native:
		UI.native_begin(self, Vector2.ZERO)
		draw_texture(bg, Vector2.ZERO)
		UI.native_end(self)
	elif bg:
		draw_texture(bg, Vector2.ZERO)
	else:
		draw_rect(Rect2(0, 0, 320, 168), Color8(40, 34, 46))
	# enemies
	var ids: Array = model.enemy_ids.duplicate()
	ids.sort_custom(func(a, b): return enemy_pos.get(a, Vector2.ZERO).y < enemy_pos.get(b, Vector2.ZERO).y)
	for eid in ids:
		var e = model.battlers[eid]
		if not e.alive():
			continue
		var tx = _enemy_tex(e)
		var p: Vector2 = enemy_pos.get(eid, Vector2(88, 110)) + offsets.get(eid, Vector2.ZERO)
		_bx(p)
		var art = _enemy_art(e)
		var em: Dictionary = _enemy_meta(e) if art else {}
		if art and not em.is_empty():
			# frame strip: idle breathing, attack/cast/hurt frames (tools/aseprite/enemy_v2.lua)
			var cw = int(em["cell"][0])
			var chh = int(em["cell"][1])
			var fx = int(em["foot"][0])
			var fy = int(em["foot"][1])
			var fi = _enemy_frame(eid, e, em)
			_draw_shadow(p, float(em.get("w", cw)) / float(UI.U))
			var mod2 = Color.WHITE
			if e.state == "CASTING":
				var k2 = 0.5 + 0.5 * sin(t * 10.0)
				mod2 = Color(1.0, 1.0 - 0.35 * k2, 1.0 - 0.35 * k2)
			UI.native_begin(self, (p * UI.U).round() / UI.U)
			var dst2 = Rect2(Vector2(-fx, -fy), Vector2(cw, chh))
			var srcr = Rect2(fi * cw, 0, cw, chh)
			draw_texture_rect_region(art, dst2, srcr, mod2)
			if flashes.get(eid, 0.0) > 0 and not Settings.get_v("reduced_flash"):
				draw_texture_rect_region(art, dst2, srcr, Color(3, 3, 3, 0.4))
			UI.native_end(self)
			if e.state == "CASTING":
				UI.text(self, p + Vector2(-4, -float(em.get("h", chh)) / float(UI.U) - 12), "!", UI.C_RED if int(t * 4) % 2 == 0 else UI.C_HI)
			continue
		if art:
			# painted/pixel art at native resolution: gentle breathing bob, red pulse while casting, white flash on hurt
			var aw = art.get_width()
			var ah = art.get_height()
			_draw_shadow(p, aw / float(UI.U))
			var bob = round(sin(t * 2.2 + float(hash(eid) % 7)) * 1.5)
			var mod = Color.WHITE
			if e.state == "CASTING":
				var k = 0.5 + 0.5 * sin(t * 10.0)
				mod = Color(1.0, 1.0 - 0.45 * k, 1.0 - 0.45 * k)
			var hurt = flashes.get(eid, 0.0) > 0
			var shake = Vector2(round(sin(t * 60.0) * 2.0), 0) if hurt else Vector2.ZERO
			UI.native_begin(self, (p * UI.U).round() / UI.U)
			var r = Rect2(Vector2(-aw / 2, -ah + bob) + shake, Vector2(aw, ah))
			draw_texture_rect(art, r, false, mod)
			if hurt and not Settings.get_v("reduced_flash"):
				draw_texture_rect(art, r, false, Color(1, 1, 1, 0.55))
				draw_texture_rect(art, r, false, Color(3, 3, 3, 0.35))
			UI.native_end(self)
			if e.state == "CASTING":
				UI.text(self, p + Vector2(-4, -ah / float(UI.U) - 12), "!", UI.C_RED if int(t * 4) % 2 == 0 else UI.C_HI)
			continue
		if tx:
			var fw = tx.get_width() / 4
			var fh = tx.get_height()
			var fr = int(t * 2.0) % 2
			if e.state == "CASTING":
				fr = 2
			if flashes.get(eid, 0.0) > 0:
				fr = 3
			_draw_shadow(p, fw)
			var dst = Rect2(p - Vector2(fw / 2.0, fh), Vector2(fw, fh)).abs()
			dst.position = dst.position.round()
			draw_texture_rect_region(tx, dst, Rect2(fr * fw, 0, fw, fh))
			if flashes.get(eid, 0.0) > 0 and not Settings.get_v("reduced_flash"):
				draw_texture_rect_region(tx, dst, Rect2(fr * fw, 0, fw, fh), Color(1, 1, 1, 0.5))
		else:
			draw_rect(Rect2(p - Vector2(16, 32), Vector2(32, 32)), Color8(120, 60, 60))
		if e.state == "CASTING":
			var mk = p + Vector2(-4, -((tx.get_height() if tx else 32)) - 12)
			UI.text(self, mk, "!", UI.C_RED if int(t * 4) % 2 == 0 else UI.C_HI)
	_bx_reset()
	for k in flashes.keys():
		flashes[k] -= get_process_delta_time()
		if flashes[k] <= 0:
			flashes.erase(k)
	# party
	for i in range(model.party_ids.size()):
		var bid: String = model.party_ids[i]
		var b = model.battlers[bid]
		var base: Vector2 = PARTY_ANCHORS[i] + offsets.get(bid, Vector2.ZERO)
		if b.row == "back":
			base.x += 12
		_bx(base)
		var tx = _party_tex(b)
		var a: Dictionary = anim.get(bid, {"name": "idle", "t": 0.0})
		var nm: String = a["name"]
		if not b.alive():
			nm = "ko"
		elif b.defending and nm == "idle":
			nm = "guard"
		elif nm == "idle" and float(b.hp) / b.mhp < 0.25:
			nm = "hurt"
		if b.state == "AIRBORNE":
			continue
		if HeroArt.has_battle(b.ref):
			var hn: String = a["name"]
			var ht: float = a["t"]
			if not b.alive():
				hn = "death" if hn == "death" and ht < HeroArt.anim_length(b.ref, "death") else "ko"
			elif b.defending and hn == "idle":
				hn = "guard"
			elif hn == "idle" and float(b.hp) / b.mhp < 0.25:
				hn = "hurt"
				ht = 99.0
			var mod = Color.WHITE
			if flashes.get(bid, 0.0) > 0 and not Settings.get_v("reduced_flash"):
				mod = Color(1.6, 1.6, 1.6)
			draw_rect(Rect2(base + Vector2(-9, -1.5), Vector2(18, 3)), Color(0.05, 0.03, 0.1, 0.3))
			HeroArt.draw_battle(self, b.ref, hn, ht, base, mod)
			if selecting == b:
				UI.text(self, base + Vector2(-3, -HeroArt.field_height(b.ref) - 12), "▼", UI.C_HI)
			continue
		var spec: Array = FRAMES[nm if FRAMES.has(nm) else "idle"]
		var fr: int = spec[0] + (int(a["t"] * 8) % spec[1] if nm not in ["attack", "cast", "victory"] else mini(int(a["t"] * 12), spec[1] - 1))
		if tx:
			draw_texture_rect_region(tx, Rect2(base - Vector2(24, 62) * PARTY_SCALE, Vector2(48, 64) * PARTY_SCALE), Rect2(fr * 48, 0, 48, 64))
		if selecting == b:
			UI.text(self, base + Vector2(-3, -76), "▼", UI.C_HI)
	_bx_reset()
	# target cursor
	if target_mode != "" and not target_list.is_empty():
		var sel: Array = target_list if target_mode in ["enemy_all", "ally_all"] else [target_list[target_idx]]
		for tid in sel:
			var tp = _battler_pos(tid)
			_bx_move(tp)
			if model.battlers[tid].side == 1:
				UI.cursor(self, tp + Vector2(-_enemy_size(tid).x / 2.0 - 10, -4))
			else:
				UI.cursor(self, tp + Vector2(-36, 4))
	_bx_reset()
	# sprite effects (library packs)
	for fx in sfx_sprites:
		if fx["t"] < 0:
			continue
		var fp: Vector2 = fx["pos"]
		if fx.has("to"):
			fp = (fx["from"] as Vector2).lerp(fx["to"], clampf(fx["t"] / fx["travel"], 0, 1))
		_bx(fp)
		BattleFX.draw(self, fx["name"], fmod(fx["t"], maxf(0.01, BattleFX.length(fx["name"]))) if fx.has("to") else fx["t"], fp)
	_bx_reset()
	# vfx (fallback particles when the effect packs are not installed)
	for v in vfx:
		if BattleFX.ok():
			break
		var k: float = 1.0 - v["t"] / v["dur"]
		var col = UI.elem_color(v["elem"])
		var rad = 4.0 + k * 10.0
		for j in range(8):
			var ang = j * PI / 4.0 + k
			var pp: Vector2 = v["pos"] + Vector2(cos(ang), sin(ang)) * rad
			draw_rect(Rect2(pp.round(), Vector2(2, 2)), col)
	if not summon_fx.is_empty():
		var k2 = clampf((t * 1.0), 0, 1)
		draw_rect(Rect2(0, 0, 320, 168), Color(0, 0, 0, 0.45))
		if not BattleFX.draw_vestige(self, summon_fx["id"], summon_fx["t"], summon_fx["dur"], Vector2(110, 162)):
			var st = _t("res://assets/sprites/vestiges/%s.png" % summon_fx["id"])
			if st:
				draw_texture(st, Vector2(96 - st.get_width() / 2.0, 150 - st.get_height()))
	# popups
	for p in popups:
		_bx_move(p["pos"])
		var yoff: float = (1.0 - p["t"]) * 10.0
		UI.text_center(self, p["pos"].x, p["pos"].y - yoff, p["text"], p["col"])
		if str(p.get("elem", "")) != "" and UI.cues_on():
			UI.elem_badge(self, Vector2(p["pos"].x - UI.width(p["text"]) / 2.0 - 18, p["pos"].y - yoff), p["elem"])
	_bx_reset()

## Limit gauge: a slim bar under the readiness gauge; pulses red/gold when full.
func _draw_limit_gauge(c: CanvasItem, r: Rect2, b) -> void:
	var k = clampf(b.limit / BattleModel.LIMIT_MAX, 0.0, 1.0)
	c.draw_rect(r, Color8(30, 18, 30))
	var col = Color8(220, 90, 150)
	if k >= 1.0:
		col = UI.C_GOLD if int(t * 6.0) % 2 == 0 else Color8(255, 90, 70)
	if k > 0.0:
		c.draw_rect(Rect2(r.position, Vector2(r.size.x * k, r.size.y)), col)

## Soft stepped contact shadow under a battler (keeps pale enemies grounded on bright floors).
func _draw_shadow(p: Vector2, w: float) -> void:
	var rx = clampf(w * 0.36, 8.0, 56.0)
	for k in range(3):
		var f = 1.0 - k * 0.28
		var r = Rect2(p.x - rx * f, p.y - 3 + k, rx * 2 * f, 5 - k * 2)
		draw_rect(r.abs(), Color(0.05, 0.03, 0.1, 0.16 + k * 0.08))

func _draw_ui() -> void:
	var c = ui
	# top banner (action names / tells)
	if banner_t > 0 and banner != "":
		var w = minf(312.0, UI.width(banner) + 16)
		UI.win(c, Rect2((320 - w) / 2.0, 2, w, 15))
		UI.text_center(c, 160, 5, banner)
	elif hint_t > 0 and hint != "":
		var lines = UI.wrap(hint, 296)
		UI.win(c, Rect2(8, 2, 304, 6 + lines.size() * 11), Color(0.07, 0.08, 0.16, 0.85))
		for i in range(lines.size()):
			UI.text(c, Vector2(14, 5 + i * 11), lines[i], UI.C_HI)
	# tells over enemies
	for eid in tells:
		var e = model.battlers.get(eid)
		if e == null or e.state != "CASTING":
			continue
		var p: Vector2 = enemy_pos.get(eid, Vector2(88, 110))
		var tt: String = tells[eid]
		var tn = []
		for x in e.intent.get("targets", []):
			tn.append(model.battlers[x].name)
		var s: String = tt + ("  → " + ", ".join(tn) if tn.size() == 1 else ("  → all" if tn.size() > 1 else ""))
		var lines = UI.wrap(s, 150)
		var w = 0.0
		for l in lines:
			w = maxf(w, UI.width(l))
		var r = Rect2(clampf(p.x - w / 2 - 4, 2, 318 - w - 8), 20, w + 8, 4 + lines.size() * 11)
		UI.win(c, r, Color8(60, 16, 20, 230))
		for i in range(lines.size()):
			UI.text(c, r.position + Vector2(4, 2 + i * 11), lines[i], UI.C_HI)
		for x in e.intent.get("targets", []):
			var tb = model.battlers[x]
			if tb.side == 0:
				var pp = _battler_pos(x) + Vector2(10, -44)
				UI.text(c, pp, "!", UI.C_RED)
	# bottom panel, FF6-style: enemy names (left window) | party name, HP, MP, readiness (right window)
	UI.win(c, Rect2(0, 168, 108, 72))
	UI.win(c, Rect2(108, 168, 212, 72))
	if cmd_menu == null:
		var y = 173
		for eid in model.enemy_ids:
			var e = model.battlers[eid]
			if not e.alive() or e.tags.has("part"):
				continue
			var nm: String = e.name.split(",")[0]
			while nm.length() > 4 and UI.width(nm) > 96:
				nm = nm.substr(0, nm.length() - 1)
			UI.text(c, Vector2(8, y), nm, UI.C_TEXT)
			var bi: Dictionary = Game.S["bestiary"].get(Content.enemy(e.ref).get("variant_of", e.ref), {})
			if bi.get("affinity", false) or bi.get("weak", []).size() > 0:
				var wk = []
				for el in e.aff:
					if e.aff[el] == "weak":
						wk.append(UI.elem_label(el))
				if bi.get("affinity", false) and not wk.is_empty():
					UI.text(c, Vector2(12, y + 9), "Weak: " + ",".join(wk), UI.C_GOLD)
					y += 9
			y += 11
			if y > 226:
				break
	var px = 114
	var py = 171
	var pitch = 16 if model.party_ids.size() <= 4 else 13
	for i in range(model.party_ids.size()):
		var b = model.battlers[model.party_ids[i]]
		var yy = py + i * pitch
		var ready = b.state in ["READY", "SELECTING"]
		var ncol = UI.C_HI if selecting == b else (UI.C_TEXT if b.alive() else UI.C_RED)
		UI.text(c, Vector2(px, yy), b.name, ncol)
		var sl = ""
		for st in b.statuses:
			sl += st.substr(0, 2).capitalize()
		if b.oath != "":
			sl = "[" + b.oath.substr(0, 3).capitalize() + "]" + sl
		if sl != "" and UI.width(b.name) < 60:
			UI.text(c, Vector2(px + 64, yy), sl.substr(0, 5), Color8(210, 170, 250))
		var hpc = UI.C_TEXT if float(b.hp) / b.mhp > 0.25 else UI.C_RED
		UI.text_right(c, px + 140, yy, "%d/%d" % [b.hp, b.mhp], hpc)
		UI.text_right(c, px + 160, yy, str(b.mp), UI.C_BLUE)
		UI.gauge(c, Rect2(px + 164, yy + 2, 36, 6), b.atb / 1000.0, UI.C_GOLD if ready else Color8(90, 150, 220))
		if not b.limits.is_empty():
			_draw_limit_gauge(c, Rect2(px + 164, yy + 9, 36, 2), b)
		UI.gauge(c, Rect2(px, yy + 10.67, 160, 1.34 if pitch < 16 else 2), float(b.hp) / b.mhp, UI.C_GREEN if float(b.hp) / b.mhp > 0.25 else UI.C_RED)
	# Concord (and the shared escape meter) sit in slim tabs on the arena's bottom edge
	UI.win(c, Rect2(232, 154, 88, 14))
	UI.text(c, Vector2(236, 155), "Concord", UI.C_DIM)
	UI.gauge(c, Rect2(282, 158, 34, 6), model.concord / 100.0, Color8(240, 150, 220))
	if model.flee_meter > 0:
		UI.win(c, Rect2(0, 154, 84, 14))
		UI.text(c, Vector2(4, 155), "Escape %d%%" % mini(100, model.flee_meter / 10), UI.C_HI)
	# sub-menu description / disabled reasons
	var m: MenuList = sub_menu if sub_menu != null else cmd_menu
	if m != null and target_mode == "":
		var it = m.current()
		var tip = ""
		if not it.get("enabled", true):
			tip = it.get("reason", "")
		elif it.has("desc"):
			tip = it["desc"]
		if tip != "":
			var lines = UI.wrap(tip, 300)
			var h = 4 + mini(lines.size(), 3) * 11
			UI.win(c, Rect2(4, 102 - h if sub_menu != null else 152 - h, 312, h), Color8(14, 18, 34, 235))
			for i in range(mini(lines.size(), 3)):
				UI.text(c, Vector2(10, (102 - h if sub_menu != null else 152 - h) + 2 + i * 11), lines[i], UI.C_TEXT)
	if target_mode != "" and not target_list.is_empty():
		var tb = model.battlers[target_list[target_idx]]
		var label: String = "All" if target_mode in ["enemy_all", "ally_all"] else tb.name
		if tb.side == 1 and target_mode == "enemy_one":
			label += "  HP %d%%" % int(100.0 * tb.hp / tb.mhp)
		UI.win(c, Rect2(88, 152, 140, 16))
		UI.text(c, Vector2(94, 155), "Target: " + label, UI.C_HI)
	if pause_open:
		c.draw_rect(Rect2(0, 0, 320, 240), Color(0, 0, 0, 0.5))
		UI.win(c, Rect2(96, 90, 128, 44))
		UI.text_center(c, 160, 96, T.s("battle.paused"), UI.C_GOLD)
		UI.text_center(c, 160, 110, T.f("battle.mode", [T.s("val." + str(Settings.get_v("battle_mode")))]), UI.C_TEXT)
	if Settings.get_v("battle_mode") == "active" and cmd_menu != null:
		UI.text(c, Vector2(282, 140), "ACTIVE", UI.C_RED)
	# auto-battle tab (sys s4): Run toggles it for this battle
	if auto_mode != "off" or auto_default != "off":
		var lab = T.s("battle.auto") if auto_mode != "off" else T.s("common.off")
		var w2 = UI.width(lab) + Glyphs.width("run") + 10
		UI.win(c, Rect2(230 - w2, 154, w2, 14), Color8(20, 24, 50, 220))
		var gx = 234 - w2
		gx += Glyphs.draw(c, Vector2(gx, 156), "run")
		UI.text(c, Vector2(gx + 1, 155), lab, UI.C_HI if auto_mode != "off" else UI.C_DIM)

# ======================================================================
# sys s4: auto-battle
# ======================================================================
func _unhandled_input(event: InputEvent) -> void:
	if done or model == null or QA.active:
		return
	if event.is_action_pressed("g_run") and not event.is_echo():
		auto_mode = ("attack" if auto_default == "off" else auto_default) if auto_mode == "off" else "off"
		banner = T.s("battle.auto_on") if auto_mode != "off" else T.s("battle.auto_off")
		banner_t = 1.0
		Audio.ui("FX002")

## Picks and commits a command for a ready hero without opening the menu. Returns false to fall back to the menu.
func _auto_command(b) -> bool:
	model.begin_select(b)
	selecting = b
	var c: Dictionary = {}
	if auto_mode == "repeat" and last_cmd.has(b.ref):
		c = _retarget(last_cmd[b.ref])
	if c.is_empty() or not model.validate(b, c).get("ok", false):
		c = _retarget({"type": "attack", "targets": []})
	if c.is_empty():
		model.cancel_select(b)
		selecting = null
		return false
	var r = model.commit(b, c)
	if not r.get("ok", false):
		model.cancel_select(b)
		selecting = null
		auto_mode = "off"
		return false
	last_cmd[b.ref] = c.duplicate(true)
	selecting = null
	return true

## Re-aims a remembered command at living targets (same side as before; lowest-HP ally, first enemy).
func _retarget(c: Dictionary) -> Dictionary:
	var out = c.duplicate(true)
	var old: Array = out.get("targets", [])
	var enemy_side = true
	if not old.is_empty() and model.battlers.has(old[0]):
		enemy_side = model.battlers[old[0]].side == 1
	var alive = []
	for bid in (model.enemy_ids if enemy_side else model.party_ids):
		var tb = model.battlers[bid]
		if (tb.targetable() if enemy_side else tb.alive()):
			alive.append(bid)
	if alive.is_empty():
		return {}
	if old.size() > 1:
		out["targets"] = alive
		return out
	if not old.is_empty() and alive.has(old[0]):
		return out
	if enemy_side:
		out["targets"] = [alive[0]]
	else:
		var lo = alive[0]
		for bid in alive:
			if float(model.battlers[bid].hp) / model.battlers[bid].mhp < float(model.battlers[lo].hp) / model.battlers[lo].mhp:
				lo = bid
		out["targets"] = [lo]
	return out
