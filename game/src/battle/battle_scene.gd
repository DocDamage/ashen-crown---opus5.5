class_name BattleScene
extends Node2D
## BattlePresenter: reads BattleModel events, animates, and collects player commands.
## Holds no authoritative HP/inventory: everything displayed is read from the model.

signal finished(result: String)

## FF6-style staging: the party stands in a staggered column on the right, facing left; enemies own the left/centre
## of the ground plane. Foot anchors (x zig-zags so neighbouring sprites never overlap).
const PARTY_ANCHORS := [Vector2(206, 96), Vector2(232, 114), Vector2(258, 132), Vector2(284, 150)]
const PARTY_SCALE := 2          # library battlers are ~16x32; drawn 2x (nearest) so the party reads at FF6 weight
const ARENA_H := 168
const ENEMY_BOX := Rect2(4, 6, 208, 160)   # enemies (and their frames) stay inside this box
const FRAMES := {"idle": [0, 4], "attack": [4, 6], "cast": [10, 4], "hurt": [14, 2], "guard": [16, 2], "victory": [18, 4], "ko": [22, 1], "step": [23, 4]}

var main: Node
var model: BattleModel
var form: Dictionary
var bg: Texture2D
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
var summon_fx = {}
var pause_open = false
var hint = ""
var hint_t = 0.0
var _victory_pose = false
var intent_reveal = false
var fast = false

func setup(form_id: String, seed_value: int, opts: Dictionary) -> void:
	form = Content.formation(form_id)
	model = BattleModel.new(Content.data)
	var party = Game.battle_party()
	model.setup(party, form["enemies"], Game.battle_inventory(), seed_value,
		{"mode": Settings.get_v("battle_mode"), "speed": float(Settings.get_v("battle_speed")), "boss": form.get("boss", false),
		 "encounter": form, "no_flee": opts.get("flags", []).has("noflee")})
	bg = _t("res://assets/sprites/bg/%s.png" % form.get("bg", "quarry"))
	for eid in model.enemy_ids:
		Game.bestiary_seen(model.battlers[eid].ref, "seen")
	_layout_enemies()
	ui = Control.new()
	ui.size = Vector2(320, 240)
	ui.draw.connect(_draw_ui)
	var layer = CanvasLayer.new()
	layer.layer = 5
	layer.scale = Vector2(UI.U, UI.U)
	add_child(layer)
	layer.add_child(ui)
	for bid in model.party_ids:
		anim[bid] = {"name": "idle", "t": randf()}
	Audio.music(form.get("music", "M025"), 0.0)
	hint = form.get("hint", "")
	hint_t = 6.0 if hint != "" else 0.0
	intent_reveal = false
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
	var tx = _enemy_tex(b)
	if tx == null:
		return Vector2(32, 32)
	return Vector2(tx.get_width() / 4, tx.get_height())

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
	Audio.music("M029", 0.0)
	banner = "Victory"
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
			"guard": a2 = "guard"
			"shoot": a2 = "attack"
			"leap": a2 = "attack"
			"step": a2 = "step"
		anim[b.id] = {"name": a2, "t": 0.0}
		offsets[b.id] = Vector2(-10, 0)
	else:
		offsets[b.id] = Vector2(8, 0)
		flashes[b.id] = 0.15
	var elem: String = ev.get("element", "physical")
	var sfx = "FX014"
	match an:
		"cast": sfx = {"fire": "FX019", "ice": "FX020", "storm": "FX021", "light": "FX022"}.get(elem, "FX019")
		"shoot": sfx = "FX017" if b.ref == "C05" else "FX018"
		"guard": sfx = "FX016"
		"item": sfx = "FX002"
		"summon": sfx = "FX030"
	Audio.sfx(sfx)
	if ev.has("summon"):
		await _summon_fx(ev["summon"], sk)
	else:
		await _wait(0.22 if not sk else 0.02)
	# effects on targets
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
	offsets.erase(b.id)
	if b.side == 0 and b.alive():
		anim[b.id] = {"name": "idle", "t": 0.0}
	for r in ev["results"]:
		if r["kind"] == "ko":
			Audio.sfx("FX025" if r["id"].begins_with("A") else "FX026")

func _summon_fx(vid: String, sk: bool) -> void:
	var short: bool = Settings.get_v("short_summons") or sk
	summon_fx = {"id": vid, "t": 0.0, "dur": 0.6 if short else 1.6}
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
				anim[id] = {"name": "ko", "t": 0.0}
		"dot":
			txt = str(r["amount"])
			col = Color8(200, 140, 255)
		"selfcost":
			txt = "-" + str(r["amount"])
			col = Color8(255, 150, 120)
		"oath":
			txt = "Oath: " + str(r["status"]).capitalize()
			col = UI.C_GOLD
		"atb", "reveal", "spawn", "decoy", "doom":
			txt = "" if r["kind"] != "doom" else "DOOM"
	if txt != "":
		popups.append({"text": txt, "pos": pos + Vector2(0, -8 * _stack_at(id)), "t": 1.0, "col": col, "id": id})

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
		return PARTY_ANCHORS[i] + Vector2(0, -20 * PARTY_SCALE)
	return enemy_pos.get(id, Vector2(88, 110)) + Vector2(0, -minf(_enemy_size(id).y * 0.55, 48))

# ======================================================================
# Commands
# ======================================================================
func _open_commands(b) -> void:
	selecting = b
	model.begin_select(b)
	var cdef = Content.ch(b.ref)
	var items = [
		{"text": "Attack", "value": "attack"},
		{"text": cdef["role_command"], "value": "role", "enabled": _role_list(b).size() > 0, "reason": "No techniques"},
		{"text": "Item", "value": "item"},
		{"text": "Defend", "value": "defend"},
	]
	var vid: String = model.links.get(b.id, "")
	if vid != "":
		var v = model.validate(b, {"type": "summon"})
		items.append({"text": "Summon", "value": "summon", "enabled": v["ok"], "reason": v.get("reason", "")})
	items.append({"text": "Row", "value": "row"})
	var ve = model.validate(b, {"type": "escape"})
	items.append({"text": "Escape", "value": "escape", "enabled": ve["ok"], "reason": ve.get("reason", "")})
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
		if a.is_empty() or a.get("kind", "") == "summon":
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
		"item":
			_open_sub_items(b)

func _confirm_summon(a: Dictionary) -> void:
	_commit({"type": "summon"})

func _open_sub_abilities(b) -> void:
	var items = []
	for aid in _role_list(b):
		var a = Content.ability(aid)
		var v = model.validate(b, {"type": "ability", "id": aid})
		var cost = model.mp_cost(b, a)
		items.append({"text": a["name"], "right": str(cost) if cost > 0 else "", "value": aid, "enabled": v["ok"], "reason": v.get("reason", ""), "desc": a.get("desc", "")})
	_open_sub(items, "role")

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
	if bg:
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
		var tx = _party_tex(b)
		var a: Dictionary = anim.get(bid, {"name": "idle", "t": 0.0})
		var nm: String = a["name"]
		if not b.alive():
			nm = "ko"
		elif b.defending and nm == "idle":
			nm = "guard"
		elif nm == "idle" and float(b.hp) / b.mhp < 0.25:
			nm = "hurt"
		var spec: Array = FRAMES[nm]
		var fr: int = spec[0] + (int(a["t"] * 8) % spec[1] if nm not in ["attack", "cast", "victory"] else mini(int(a["t"] * 12), spec[1] - 1))
		if b.state == "AIRBORNE":
			continue
		if tx:
			draw_texture_rect_region(tx, Rect2(base - Vector2(24, 62) * PARTY_SCALE, Vector2(48, 64) * PARTY_SCALE), Rect2(fr * 48, 0, 48, 64))
		if selecting == b:
			UI.text(self, base + Vector2(-3, -76), "▼", UI.C_HI)
	# target cursor
	if target_mode != "" and not target_list.is_empty():
		var sel: Array = target_list if target_mode in ["enemy_all", "ally_all"] else [target_list[target_idx]]
		for tid in sel:
			var tp = _battler_pos(tid)
			if model.battlers[tid].side == 1:
				UI.cursor(self, tp + Vector2(-_enemy_size(tid).x / 2.0 - 10, -4))
			else:
				UI.cursor(self, tp + Vector2(-36, 4))
	# vfx
	for v in vfx:
		var k: float = 1.0 - v["t"] / v["dur"]
		var col = UI.elem_color(v["elem"])
		var rad = 4.0 + k * 10.0
		for j in range(8):
			var ang = j * PI / 4.0 + k
			var pp: Vector2 = v["pos"] + Vector2(cos(ang), sin(ang)) * rad
			draw_rect(Rect2(pp.round(), Vector2(2, 2)), col)
	if not summon_fx.is_empty():
		var k2 = clampf((t * 1.0), 0, 1)
		var st = _t("res://assets/sprites/vestiges/%s.png" % summon_fx["id"])
		draw_rect(Rect2(0, 0, 320, 168), Color(0, 0, 0, 0.45))
		if st:
			draw_texture(st, Vector2(96 - st.get_width() / 2.0, 150 - st.get_height()))
	# popups
	for p in popups:
		var yoff: float = (1.0 - p["t"]) * 10.0
		UI.text_center(self, p["pos"].x, p["pos"].y - yoff, p["text"], p["col"])

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
	var py = 172
	for i in range(model.party_ids.size()):
		var b = model.battlers[model.party_ids[i]]
		var yy = py + i * 16
		var ready = b.state in ["READY", "SELECTING"]
		var ncol = UI.C_HI if selecting == b else (UI.C_TEXT if b.alive() else UI.C_RED)
		UI.text(c, Vector2(px, yy), b.name, ncol)
		var sl = ""
		for st in b.statuses:
			sl += st.substr(0, 2).capitalize()
		if b.oath != "":
			sl = "[" + b.oath.substr(0, 3).capitalize() + "]" + sl
		if b.row == "back":
			UI.text(c, Vector2(px + 38, yy), "B", UI.C_DIM)
		UI.text(c, Vector2(px + 46, yy), sl.substr(0, 7), Color8(210, 170, 250))
		var hpc = UI.C_TEXT if float(b.hp) / b.mhp > 0.25 else UI.C_RED
		UI.text_right(c, px + 138, yy, "%d/%d" % [b.hp, b.mhp], hpc)
		UI.text_right(c, px + 160, yy, str(b.mp), UI.C_BLUE)
		UI.gauge(c, Rect2(px + 164, yy + 2, 36, 6), b.atb / 1000.0, UI.C_GOLD if ready else Color8(90, 150, 220))
		UI.gauge(c, Rect2(px, yy + 11, 160, 2), float(b.hp) / b.mhp, UI.C_GREEN if float(b.hp) / b.mhp > 0.25 else UI.C_RED)
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
		UI.text_center(c, 160, 96, "Paused", UI.C_GOLD)
		UI.text_center(c, 160, 110, "Mode: " + Settings.get_v("battle_mode").capitalize(), UI.C_TEXT)
	if Settings.get_v("battle_mode") == "active" and cmd_menu != null:
		UI.text(c, Vector2(282, 140), "ACTIVE", UI.C_RED)
