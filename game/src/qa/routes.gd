extends Node
## Normal-input route bots. They press InputMap actions exactly like a player and read what is visible
## (map geometry, menus, battle panel) to decide what to press. No teleports, no flag/HP edits.

var main: Node
var steps_log = 0
var battles = 0
var choice_plan: Array = []      # queued choice indices for upcoming choice menus
var fail_reason = ""

func run(p_main: Node, route: String) -> void:
	main = p_main
	QA.note("route %s content %s engine %s" % [route, Content.hash, Engine.get_version_info()["string"]])
	var ok = false
	if has_method("r_" + route):
		ok = await call("r_" + route)
	else:
		QA.note("unknown route " + route)
	if not ok and fail_reason != "":
		QA.note("FAIL REASON: " + fail_reason)
	QA.finish(ok, "%s battles=%d steps=%d" % [route, battles, steps_log])

# ---------------------------------------------------------------- primitives
func _act(action: String, pressed: bool) -> void:
	var ev = InputEventAction.new()
	ev.action = "g_" + action
	ev.pressed = pressed
	Input.parse_input_event(ev)

func press(action: String, hold: float = 0.05) -> void:
	_act(action, true)
	await frames(2)
	await get_tree().create_timer(hold, true, false, true).timeout
	_act(action, false)
	await frames(2)

func frames(n: int) -> void:
	for i in range(n):
		await get_tree().process_frame

func wait(s: float) -> void:
	await get_tree().create_timer(s, true, false, true).timeout

func top():
	return main.router.top()

func fail(msg: String) -> bool:
	msg += " | map=%s tile=%s flags=%s" % [main.field.map_id, str(main.field.p_tile), str(Game.S.get("flags", {}).keys())]
	fail_reason = msg
	QA.note("FAIL: " + msg)
	return false

# ---------------------------------------------------------------- dialogue / menus
## Advance any dialogue, choices, docs and toasts until control returns to the field (or a battle starts).
func settle(max_t: float = 60.0) -> void:
	var t = 0.0
	while t < max_t:
		var tp = top()
		if main.battle != null and is_instance_valid(main.battle):
			await fight()
			t = 0.0
			continue
		if tp is DialogueBox:
			await press("confirm")
		elif tp is DocView:
			await press("confirm")
		elif tp is MenuList and tp.get_parent() == main.ui:
			# story choice: take the planned index (default 0)
			var idx: int = choice_plan.pop_front() if not choice_plan.is_empty() else 0
			while tp.index != idx:
				await press("down")
			await press("confirm")
		elif tp is GameMenu or (tp is MenuList and tp.get_parent() is GameMenu):
			if not main.director.running or hold_menus:
				return
			# a scene opened a menu (formation / split / save prompt): accept the defaults and close it
			var gm = _gm()
			if gm != null and gm.page == "split":
				var sm: MenuList = gm.lists[-1]
				await _pick(sm, sm.items.size() - 1)
			elif gm != null and gm.page == "save":
				# a scene asked for a save (the clear save): record it in slot 3
				await _pick(gm.lists[-1], 2)
				await frames(6)
				if is_instance_valid(gm) and gm.lists.size() > 1:
					await _pick(gm.lists[-1], 1)
				QA.note("scene save prompt: wrote slot 3")
			else:
				await press("cancel")
			await frames(4)
		elif tp == main.field and not main.director.running and not main.field.busy and not main._transitioning:
			await frames(3)
			if top() == main.field and not main.director.running and not main.field.busy:
				return
		else:
			await frames(2)
		t += get_process_delta_time()

# ---------------------------------------------------------------- walking
## Tiles a walker must not cross on the way somewhere else: map transitions and live story triggers.
func _avoid_tiles(goal: Vector2i) -> Dictionary:
	var f: Field = main.field
	var out = {}
	for e in f.map["entities"]:
		var t: String = e["type"]
		if t == "location":
			out[Vector2i(e["x"], e["y"])] = true
		elif t in ["exit", "door"] or (t == "trigger" and e.get("touch", true)):
			if t == "trigger":
				if not Game.eval_cond(e["cond"]):
					continue
				var sc = Content.scene(e["scene"])
				if sc.get("once", false) and Game.event_applied(e["scene"]):
					continue
			if goal.x >= e["x1"] and goal.x <= e["x2"] and goal.y >= e["y1"] and goal.y <= e["y2"]:
				continue   # the area we are heading into
			for y in range(e["y1"], e["y2"] + 1):
				for x in range(e["x1"], e["x2"] + 1):
					out[Vector2i(x, y)] = true
	out.erase(goal)
	return out

func _bfs(goal: Vector2i, adjacent: bool) -> Array:
	var f: Field = main.field
	var start: Vector2i = f.p_tile
	var q = [start]
	var prev = {start: start}
	var goals = {}
	if adjacent:
		for d in Field.DV.values():
			goals[goal + d] = true
	else:
		goals[goal] = true
	var found = null
	var avoid = _avoid_tiles(goal)
	while not q.is_empty():
		var c: Vector2i = q.pop_front()
		if goals.has(c):
			found = c
			break
		for d in Field.DV.values():
			var n: Vector2i = c + d
			if prev.has(n) or n.x < 0 or n.y < 0 or n.x >= f.W or n.y >= f.H:
				continue
			if avoid.has(n) and not goals.has(n):
				continue
			if f.solid_at(n.x, n.y) and not (not adjacent and n == goal and not f.solid_set.has(f.kind_at(n.x, n.y))):
				continue
			prev[n] = c
			q.append(n)
	if found == null:
		return []
	var path = []
	var cur: Vector2i = found
	while cur != start:
		path.push_front(cur)
		cur = prev[cur]
	return path

func _gm():
	for c in main.ui.get_children():
		if c is GameMenu and is_instance_valid(c):
			return c
	return null

## Field upkeep through the in-game menu: revive with Phoenix Leaf, heal below 55% with Tonics.
func maintain() -> void:
	for cid in Game.active():
		var m = Game.member(cid)
		var s = Game.stats(cid)
		var iid := ""
		if int(m["hp"]) <= 0 and Game.count("I006") > 0:
			iid = "I006"
		elif int(m["hp"]) > 0 and float(m["hp"]) / s["mhp"] < 0.55 and Game.count("I001") > 0:
			iid = "I001"
		if iid == "":
			continue
		await press("menu")
		await frames(6)
		var gm = _gm()
		if gm == null:
			return
		await menu_pick_text(gm.lists[-1], "Items")
		await frames(4)
		var il: MenuList = gm.lists[-1]
		var k := _menu_index(il, func(it): return it.get("value", "") == iid)
		if k < 0:
			break
		await _pick(il, k)
		await frames(4)
		var ml: MenuList = gm.lists[-1]
		var mi := _menu_index(ml, func(it): return it.get("value", "") == cid)
		if mi >= 0:
			await _pick(ml, mi)
		await frames(4)
		QA.note("maintain: used %s on %s (hp now %d)" % [iid, cid, int(Game.member(cid)["hp"])])
		var guard := 0
		while _gm() != null and guard < 6:
			await press("cancel")
			guard += 1
		await settle()

func walk_to(x: int, y: int, adjacent: bool = false, max_t: float = 400.0) -> bool:
	var f: Field = main.field
	var goal = Vector2i(x, y)
	var map0: String = f.map_id
	var t = 0.0
	while t < max_t:
		await settle()
		if main.last_battle_result != "":
			main.last_battle_result = ""
			await maintain()
		if f.map_id != map0:
			return true
		if (not adjacent and f.p_tile == goal) or (adjacent and (f.p_tile - goal).length() == 1.0):
			return true
		var path = _bfs(goal, adjacent)
		if path.is_empty():
			return fail("no path to %s on %s from %s" % [goal, f.map_id, f.p_tile])
		var nxt: Vector2i = path[0]
		var d = ""
		for k in Field.DV:
			if f.p_tile + Field.DV[k] == nxt:
				d = k
		var before: Vector2i = f.p_tile
		if steps_log % 200 == 0:
			QA.note("walk %s -> %s next %s dir %s busy=%s top=%s" % [str(f.p_tile), str(goal), str(nxt), d, str(f.busy), str(top())])
		_act(d, true)
		var tt = 0.0
		# release as soon as the step starts so arrival never chains into an extra step
		while not f.p_moving and f.p_tile == before and tt < 1.2 and f.map_id == map0:
			await frames(1)
			tt += get_process_delta_time()
			if main.director.running or main.battle != null:
				break
		_act(d, false)
		while f.p_moving and tt < 2.0 and f.map_id == map0:
			await frames(1)
			tt += get_process_delta_time()
		if main.director.running or main.battle != null or main._transitioning:
			await settle()
		if f.vehicle != "ship" and (f.p_tile - before).length() > 3.5 and f.map_id == map0 and not _pushed_back(before):
			QA.note("walk: moved by a scene from %s to %s; stopping" % [str(before), str(f.p_tile)])
			return true
		steps_log += 1
		t += tt + 0.02
		await frames(1)
	return fail("walk timeout to %s on %s" % [goal, f.map_id])

func _pushed_back(before: Vector2i) -> bool:
	# hazards push the walker back one step; that is not a scene warp
	return (main.field.p_tile - before).length() <= 1.5 or main.field.p_tile == main.field.p_prev

func face(dir: String) -> void:
	var f: Field = main.field
	if f.p_dir != dir:
		var t = f.p_tile
		await press(dir, 0.02)
		# if the step actually moved us, step back
		if f.p_tile != t:
			await settle()

## Face a walkable target (a floor plaque, a trigger tile) without stepping onto it: arrive at the
## neighbouring tile by moving toward the target, so the last step already faces it.
func _approach_facing(t: Vector2i) -> bool:
	var f: Field = main.field
	for d in Field.DV:
		var a: Vector2i = t - Field.DV[d]
		var back: Vector2i = a - Field.DV[d]
		if f.solid_at(a.x, a.y) or f.solid_at(back.x, back.y) or back == t:
			continue
		if _bfs(back, false).is_empty() and f.p_tile != back:
			continue
		if not await walk_to(back.x, back.y):
			return false
		await settle()
		await press(d, 0.02)
		var g = 0
		while f.p_moving and g < 120:
			await frames(1)
			g += 1
		await settle()
		if f.p_tile == a and f.facing_tile() == t:
			return true
	return false

func talk(x: int, y: int) -> bool:
	var f: Field = main.field
	var tgt = Vector2i(x, y)
	if not f.solid_at(x, y) and not (f.kind_at(x, y) in ["counter", "window", "gate"]):
		for attempt in range(3):
			if not await _approach_facing(tgt):
				break
			var n0: int = f.interactions
			await press("confirm")
			var g3 = 0
			while f.interactions == n0 and g3 < 20:
				await frames(1)
				g3 += 1
			if f.interactions > n0:
				await settle()
				return true
		return fail("could not face walkable target %d,%d on %s" % [x, y, f.map_id])
	for attempt in range(4):
		if not await walk_to(x, y, true):
			return false
		await settle()
		if (f.p_tile - Vector2i(x, y)).length() != 1.0:
			QA.note("talk: not adjacent after walk: at %s target %s moving %s busy %s top %s" % [str(f.p_tile), str(Vector2i(x, y)), str(f.p_moving), str(f.busy), str(top())])
			await wait(0.3)
			continue
		var diff: Vector2i = Vector2i(x, y) - f.p_tile
		var d = ""
		for k in Field.DV:
			if Field.DV[k] == diff:
				d = k
		await face(d)
		var g2 = 0
		while (f.p_moving or f.busy) and g2 < 120:
			await frames(1)
			g2 += 1
		if f.p_tile + Field.DV[d] != Vector2i(x, y):
			QA.note("talk retry: at %s facing %s target %s" % [str(f.p_tile), f.p_dir, str(Vector2i(x, y))])
			continue
		var n0: int = f.interactions
		await press("confirm")
		var g3 = 0
		while f.interactions == n0 and g3 < 20:
			await frames(1)
			g3 += 1
		if f.interactions > n0:
			await settle()
			return true
		QA.note("talk no-interact: at %s dir %s top %s busy %s moving %s" % [str(f.p_tile), f.p_dir, str(top()), str(f.busy), str(f.p_moving)])
	return fail("could not interact with %d,%d on %s" % [x, y, f.map_id])

func npc_pos(id: String) -> Vector2i:
	for n in main.field.npcs:
		if n["id"] == id:
			return n["tile"]
	return Vector2i(-1, -1)

func talk_npc(id: String) -> bool:
	var p = npc_pos(id)
	if p.x < 0:
		return fail("npc %s not present on %s" % [id, main.field.map_id])
	return await talk(p.x, p.y)

func ent_pos(type: String, id: String) -> Vector2i:
	for e in main.field.map["entities"]:
		if e["type"] == type and e.get("id", "") == id:
			return Vector2i(e["x"], e["y"])
	return Vector2i(-1, -1)

func use_ent(type: String, id: String) -> bool:
	var p = ent_pos(type, id)
	if p.x < 0:
		return fail("entity %s %s missing" % [type, id])
	return await talk(p.x, p.y)

func exit_to(dest: String) -> bool:
	var f: Field = main.field
	for e in f.map["entities"]:
		if e["type"] in ["door", "exit"] and e["dest"] == dest and Game.eval_cond(e["cond"]):
			var tx: int = e["x1"]
			var ty: int = e["y1"]
			# prefer a walkable tile of the exit strip (edges can sit on scenery)
			var found_free = false
			for yy in range(e["y1"], e["y2"] + 1):
				for xx in range(e["x1"], e["x2"] + 1):
					if not found_free and not f.solid_set.has(f.kind_at(xx, yy)):
						tx = xx
						ty = yy
						found_free = true
			var map0: String = f.map_id
			if not await walk_to(tx, ty):
				return false
			var t = 0.0
			while f.map_id == map0 and t < 3.0:
				await frames(2)
				t += get_process_delta_time()
			await settle()
			QA.note("entered %s" % f.map_id)
			return f.map_id == dest
	return fail("no open exit to %s from %s" % [dest, f.map_id])

# ---------------------------------------------------------------- battle policy (through the real menus)
func fight() -> void:
	battles += 1
	var bs = main.battle
	QA.note("battle start: %s at %s %s meter=%.1f grace=%d" % [str(bs.form.get("id", "?")), main.field.map_id, str(main.field.p_tile), main.field.enc_meter, main.field.enc_grace])
	var shot_taken = false
	var last_tick := -1
	var stall := 0.0
	while main.battle != null and is_instance_valid(main.battle):
		var tp = top()
		if bs.model.tick == last_tick and not bs.done:
			stall += get_process_delta_time()
			if stall > 15.0:
				QA.note("STALL in battle: top=%s cmd=%s sub=%s target=%s locked=%s events=%d res=%s ready=%s" % [str(tp), str(bs.cmd_menu), str(bs.sub_menu), bs.target_mode, bs.model.locked, bs.model.events.size(), bs.model.result, str(bs.model.ready_order)])
				await QA.shot("stall_battle")
				stall = -1000.0
		else:
			stall = 0.0
			last_tick = bs.model.tick
		if bs.done:
			await frames(2)
			continue
		if not shot_taken and bs.form.get("boss", false):
			# capture the boss telegraph when it first appears
			for eid in bs.tells:
				shot_taken = true
				await QA.shot((seg_name if seg_name != "" else "b1") + "_boss_tell_" + str(bs.form.get("id", "")))
		if bs.cmd_menu != null and tp == bs.cmd_menu:
			await _choose_command(bs)
		elif tp is DialogueBox:
			await press("confirm")
		elif tp is MenuList and tp.get_parent() == main.ui:
			await press("confirm")   # defeat menu -> Retry
		else:
			await frames(2)
	await frames(4)
	var r = await _wait_result()
	QA.note("battle end: " + r)

func _wait_result() -> String:
	var g := 0
	while main.mode == "battle" and g < 600:
		if top() is DialogueBox:
			await press("confirm")
		await frames(2)
		g += 1
	return main.last_battle_result

func _menu_index(m: MenuList, pred: Callable) -> int:
	for i in range(m.items.size()):
		if pred.call(m.items[i]):
			return i
	return -1

func _pick(m: MenuList, idx: int) -> void:
	var guard = 0
	while m.index != idx and guard < 40:
		await press("down" if m.index < idx else "up")
		guard += 1
	await press("confirm")

func _choose_command(bs) -> void:
	var b = bs.selecting
	var model: BattleModel = bs.model
	var m: MenuList = bs.cmd_menu
	# 1) heal an ally below 40% with a Tonic (or Mend if Oriel)
	var low = null
	for pid in model.party_ids:
		var p = model.battlers[pid]
		if p.alive() and float(p.hp) / p.mhp < 0.4:
			low = p
	var ko_ally = null
	for pid in model.party_ids:
		if not model.battlers[pid].alive():
			ko_ally = model.battlers[pid]
	for aid in ["S044"]:
		if ko_ally != null and b.abilities.has(aid) and b.mp >= int(Content.ability(aid)["mp"]):
			await _use_ability(bs, m, aid, ko_ally.id)
			return
	if low != null:
		var hurt = 0
		for pid in model.party_ids:
			var pp = model.battlers[pid]
			if pp.alive() and float(pp.hp) / pp.mhp < 0.5:
				hurt += 1
		for aid in (["S048", "S043", "S041", "S026"] if hurt >= 2 else ["S041", "S026", "S043"]):
			if b.abilities.has(aid) and b.mp >= int(Content.ability(aid)["mp"]):
				await _use_ability(bs, m, aid, low.id)
				return
	if ko_ally != null and int(model.inventory.get("I006", 0)) > 0:
		await _use_item(bs, m, "I006", ko_ally.id)
		return
	if low != null:
		var deficit = low.mhp - low.hp
		for iid in (["I003", "I002", "I001"] if deficit > 1400 else (["I002", "I001"] if deficit > 600 else ["I001", "I002"])):
			if int(model.inventory.get(iid, 0)) > 0:
				await _use_item(bs, m, iid, low.id)
				return
	# keep the healer casting: Ether when a healer runs dry
	if b.ref in ["C06", "C04"] and b.mp < 16 and b.mmp > 30:
		for iid in ["I004", "I005"]:
			if int(model.inventory.get(iid, 0)) > 0:
				await _use_item(bs, m, iid, b.id)
				return
	# 2) boss tell: Defend if we are the marked target
	for eid in model.enemy_ids:
		var e = model.battlers[eid]
		if e.alive() and e.state == "CASTING" and e.intent.get("targets", []).has(b.id):
			var di = _menu_index(m, func(it): return it.get("value", "") == "defend")
			await _pick(m, di)
			return
	# 3) exploit a weakness with an elemental spell if affordable
	for aid in b.abilities:
		var a = Content.ability(aid)
		if a.get("kind", "") != "magical" or b.mp < int(a["mp"]) or a.get("element", "") == "":
			continue
		for eid in model.enemy_ids:
			var e = model.battlers[eid]
			if e.targetable() and e.aff.get(a["element"], "") == "weak":
				await _use_ability(bs, m, aid, eid)
				return
	# 4) boss with a weakness: throw the matching flask
	var boss = null
	for eid in model.enemy_ids:
		if model.battlers[eid].is_boss() and model.battlers[eid].alive():
			boss = model.battlers[eid]
	if boss != null:
		for pair in [["I017", "storm"], ["I016", "ice"], ["I015", "fire"]]:
			if boss.aff.get(pair[1], "") == "weak" and int(model.inventory.get(pair[0], 0)) > 0:
				await _use_item(bs, m, pair[0], boss.id)
				return
	# 4b) the strongest affordable damage technique while MP lasts (keep a reserve for healers)
	var living = 0
	for eid in model.enemy_ids:
		if model.battlers[eid].targetable():
			living += 1
	var best = ""
	var best_score = 0.0
	for aid in b.abilities:
		var a = Content.ability(aid)
		var k: String = a.get("kind", "")
		if not (k in ["physical", "magical"]) or int(a.get("power", 0)) <= 100:
			continue
		var cost = int(a["mp"])
		if cost > b.mp or b.mp - cost < b.mmp * (0.6 if b.ref in ["C06", "C04"] else 0.35):
			continue
		var score = float(a["power"]) * (living if a.get("target", "") == "enemy_all" else 1)
		if score > best_score:
			best_score = score
			best = aid
	if best != "" and (boss != null or living >= 2 or randi() % 3 == 0):
		var tgt = boss.id if boss != null and boss.targetable() else ""
		await _use_ability(bs, m, best, tgt)
		return
	# 5) attack the first living enemy (lowest id)
	var ai = _menu_index(m, func(it): return it.get("value", "") == "attack")
	await _pick(m, ai)
	await _target(bs, "")

func _target(bs, want: String) -> void:
	var guard = 0
	while bs.target_mode == "" and guard < 20:
		await frames(1)
		guard += 1
	if want != "":
		guard = 0
		while bs.target_list.size() > 0 and bs.target_list[bs.target_idx] != want and guard < 12:
			await press("down")
			guard += 1
	await press("confirm")

func _use_item(bs, m: MenuList, iid: String, target: String) -> void:
	var ii = _menu_index(m, func(it): return it.get("value", "") == "item")
	await _pick(m, ii)
	await frames(2)
	var sm: MenuList = bs.sub_menu
	if sm == null:
		return
	var k = _menu_index(sm, func(it): return it.get("value", "") == iid)
	if k < 0:
		await press("cancel")
		return
	await _pick(sm, k)
	await _target(bs, target)

func _use_ability(bs, m: MenuList, aid: String, target: String) -> void:
	var ri = _menu_index(m, func(it): return it.get("value", "") == "role")
	await _pick(m, ri)
	await frames(2)
	var sm: MenuList = bs.sub_menu
	if sm == null:
		return
	var k = _menu_index(sm, func(it): return it.get("value", "") == aid)
	if k < 0 or not sm.items[k].get("enabled", true):
		await press("cancel")
		var ai = _menu_index(m, func(it): return it.get("value", "") == "attack")
		await _pick(m, ai)
		await _target(bs, "")
		return
	await _pick(sm, k)
	await _target(bs, target)

# ---------------------------------------------------------------- title helpers
func title_pick(label: String) -> bool:
	var ts = main.title_screen
	if ts == null:
		return fail("not on title")
	var idx = _menu_index(ts.menu, func(it): return it["text"] == label)
	if idx < 0 or not ts.menu.items[idx].get("enabled", true):
		return fail("title option unavailable: " + label)
	while ts.menu.index != idx:
		await press("down")
	await press("confirm")
	return true

func menu_pick_text(m: MenuList, text: String) -> bool:
	var idx = _menu_index(m, func(it): return String(it.get("text", "")).begins_with(text))
	if idx < 0:
		return fail("menu option missing: " + text)
	await _pick(m, idx)
	return true

func save_at_lamp(slot: int) -> bool:
	# the player is next to a save lamp: interact, pick slot, confirm overwrite if needed
	await press("confirm")
	await frames(10)
	var gm = null
	for c in main.ui.get_children():
		if c is GameMenu:
			gm = c
	if gm == null:
		return fail("save menu did not open")
	var m: MenuList = gm.lists[-1]
	await _pick(m, slot - 1)
	await frames(6)
	if gm.lists.size() > 1:
		await _pick(gm.lists[-1], 1)   # "Yes" overwrite
	await wait(0.3)
	while is_instance_valid(gm) and not gm.lists.is_empty():
		await press("cancel")
	await settle()
	return true

# ---------------------------------------------------------------- routes
func milestone(name: String) -> void:
	var f := FileAccess.open(QA.out_dir + "/ms_%s.json" % name, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify({"S": Game.S, "map": main.field.map_id, "tile": [main.field.p_tile.x, main.field.p_tile.y]}))
	QA.note("milestone " + name)

## Debug-only: resume from a milestone snapshot (labelled fixture; not normal-input evidence).
func resume(name: String) -> bool:
	var f := FileAccess.open(QA.out_dir + "/ms_%s.json" % name, FileAccess.READ)
	if f == null:
		return fail("no milestone " + name)
	var d = JSON.parse_string(f.get_as_text())
	Game.S = Game._sanitize(d["S"])
	Game.playing = true
	Game.fixture_label = "resume:" + name
	if main.title_screen:
		main.router.pop(main.title_screen)
		main.title_screen.queue_free()
		main.title_screen = null
	main.enter_field(d["map"], "", Vector2i(int(d["tile"][0]), int(d["tile"][1])), "down")
	main.fade_rect.color.a = 0.0
	QA.note("RESUMED FIXTURE " + name + " (debug only)")
	await settle()
	return true

func r_smoke() -> bool:
	await wait(1.0)
	await QA.shot("smoke_title")
	return true

func r_look() -> bool:
	await wait(0.5)
	await QA.shot("look_title")
	await title_pick("New Game")
	await wait(2.0)
	await QA.shot("look_opening")
	await settle()
	await QA.shot("look_town")
	return true

func r_b1() -> bool:
	## B1 gate: New Game -> Brackenford -> Crown Quarry -> B01 -> Lift Yard -> save -> reload.
	await wait(0.5)
	await QA.shot("b1_00_title")
	await title_pick("New Game")
	await wait(1.5)
	await settle()
	await QA.shot("b1_01_brackenford")
	if not await talk_npc("worker_list"): return false
	if not await talk_npc("elder"): return false
	if not await exit_to("D01_R01"): return false
	# SC01 fires on the approach to the gate; includes the tutorial battle
	if not await walk_to(19, 9): return false
	await settle()
	if not Game.flag("sc01_done"): return fail("SC01 did not commit")
	await QA.shot("b1_02_gatehouse")
	choice_plan = [0]
	if not await use_ent("switch", "pump0"): return false
	if not await exit_to("D01_R02"): return false
	if not await talk_npc("tessa"): return false
	if not Game.is_recruited("C02"): return fail("Tessa did not join")
	if not await talk(20, 21): return false
	if not await talk_npc("worker1"): return false
	if not await exit_to("D01_R03"): return false
	await QA.shot("b1_03_flooded_spur")
	if not await talk_npc("worker2"): return false
	if not await talk_npc("worker3"): return false
	if not await use_ent("chest", "D01_SECRET_CHEST"): return false
	if not await exit_to("D01_R04"): return false
	choice_plan = [0]
	if not await use_ent("switch", "pump1"): return false
	if not await use_ent("switch", "pump2"): return false
	if not Game.flag("d01_drained"): return fail("pumps did not drain")
	if not await use_ent("switch", "liftlever"): return false
	if not await use_ent("switch", "brake"): return false
	if not await talk_npc("worker4"): return false
	if not await talk_npc("worker5"): return false
	if not await use_ent("chest", "D01_C_R04"): return false
	milestone("before_r05")
	if not await exit_to("D01_R05"): return false
	if not await talk_npc("worker6"): return false
	if not await walk_to(19, 18): return false
	await settle()
	if not Game.flag("b01_done"): return fail("B01 not defeated")
	await QA.shot("b1_05_after_b01")
	if not await exit_to("D01_R06"): return false
	await settle()
	if not await talk_npc("worker7"): return false
	if not await talk_npc("mara_yard"): return false
	await settle()
	if not Game.chapter_done("CH01"): return fail("CH01 did not complete")
	await QA.shot("b1_06_town_after")
	milestone("ch01_done")
	# save at the bunkhouse lamp, slot 1
	if not await exit_to("T01_BUNKHOUSE"): return false
	if not await walk_to(15, 5): return false
	await face("right")
	if not await save_at_lamp(1): return false
	var saved = Game.S.duplicate(true)
	QA.note("saved: gold=%d items=%s chests=%d lv=%d" % [Game.gold(), str(Game.S["inventory"]["items"]), Game.S["chests"].size(), Game.member("C01")["level"]])
	# back to title and Continue
	main.to_title()
	await wait(0.5)
	if not await title_pick("Continue"): return false
	await wait(1.0)
	await settle()
	var same: bool = Game.S["chapters"] == saved["chapters"] and Game.S["inventory"] == saved["inventory"] and Game.S["chests"] == saved["chests"] and Game.S["party"]["roster"] == saved["party"]["roster"] and Game.S["flags"] == saved["flags"]
	await QA.shot("b1_07_reloaded")
	if not same:
		return fail("reloaded state differs")
	QA.note("reload matches: chapters=%s objective=%s" % [str(Game.S["chapters"]), Game.S["journal"]["objective"]])
	return true

# ================================================================ campaign segments (step interpreter)
## Each segment resumes from the end milestone written by the previous normal-input segment (a chained
## save/load handover), then plays on with ordinary inputs. Steps are data so failures report the step.
var seg_name = ""
var hold_menus = false   # let a scene-opened menu (a shop) stay open for the caller

func run_steps(steps: Array) -> bool:
	var i = 0
	for st in steps:
		i += 1
		var op: String = st[0]
		var ok = true
		match op:
			"npc":
				ok = await talk_npc(st[1])
			"use":
				ok = await use_ent(st[1], st[2])
			"tile":
				ok = await talk(st[1], st[2])
			"go":
				ok = await walk_to(st[1], st[2])
			"trig":
				# walk onto the touch trigger that runs this scene on the current map (world ferries, cables)
				var tp = Vector2i(-1, -1)
				for e in main.field.map["entities"]:
					if e["type"] == "trigger" and e.get("scene", "") == st[1]:
						tp = Vector2i(e["x1"], e["y1"])
				ok = tp.x >= 0 and await walk_to(tp.x, tp.y, false, 900.0)
				if tp.x < 0:
					fail("no trigger for %s on %s" % [st[1], main.field.map_id])
			"exit":
				ok = await exit_to(st[1])
			"loc":
				ok = await goto_location(st[1])
			"choice":
				choice_plan = st[1].duplicate()
			"check":
				ok = Game.eval_cond(st[1].split(","))
				if not ok:
					fail("check failed: " + st[1])
			"shot":
				await QA.shot(seg_name + "_" + st[1])
			"ms":
				milestone(st[1])
			"save":
				ok = await save_nearest(st[1])
			"heal":
				ok = await use_heal()
			"settle":
				await settle()
			"wait_map":
				var t = 0.0
				while main.field.map_id != st[1] and t < 30.0:
					await frames(2)
					t += get_process_delta_time()
				ok = main.field.map_id == st[1]
				if not ok:
					fail("expected map %s, on %s" % [st[1], main.field.map_id])
			"grind":
				ok = await grind(st[1])
			"grind_to":
				var guard_g = 0
				while int(Game.member("C01")["level"]) < int(st[1]) and guard_g < int(st[2]) and ok:
					ok = await grind(1)
					guard_g += 1
			"airship":
				ok = await airship_step(st)
			"buy":
				ok = await buy_items(st[1], st[2])
			"optimize":
				ok = await optimize_all()
			"note":
				QA.note(st[1])
			_:
				ok = fail("unknown step " + op)
		if not ok:
			QA.note("segment %s failed at step %d %s" % [seg_name, i, str(st)])
			return false
	return true

func goto_location(lid: String) -> bool:
	var f: Field = main.field
	for e in f.map["entities"]:
		if e["type"] == "location" and e["id"] == lid:
			var map0 = f.map_id
			if not await walk_to(e["x"], e["y"], false, 900.0):
				# the step onto the location tile itself changes map; walk_to reports success on map change
				return false
			var t = 0.0
			while f.map_id == map0 and t < 5.0:
				await frames(2)
				t += get_process_delta_time()
			await settle()
			QA.note("entered %s via %s" % [f.map_id, lid])
			return f.map_id != map0
	return fail("location %s not on %s" % [lid, f.map_id])

func save_nearest(slot: int) -> bool:
	var f: Field = main.field
	var best = Vector2i(-1, -1)
	for e in f.map["entities"]:
		if e["type"] == "save" and Game.eval_cond(e["cond"]):
			var p = Vector2i(e["x"], e["y"])
			if best.x < 0 or (p - f.p_tile).length() < (best - f.p_tile).length():
				best = p
	if best.x < 0:
		return fail("no save lamp on " + f.map_id)
	if not await walk_to(best.x, best.y, true):
		return false
	await settle()
	var diff: Vector2i = best - f.p_tile
	for k in Field.DV:
		if Field.DV[k] == diff:
			await face(k)
	return await save_at_lamp(slot)

func use_heal() -> bool:
	for e in main.field.map["entities"]:
		if e["type"] == "heal":
			return await talk(e["x"], e["y"])
	return true

## Walk back and forth in the current room until n more battles have been fought (levels by play, not edits).
func grind(n: int) -> bool:
	var f: Field = main.field
	var target = battles + n
	var a = f.p_tile
	var guard = 0
	while battles < target and guard < 400:
		guard += 1
		var moved = false
		for d in (["left", "right"] if guard % 2 == 0 else ["up", "down"]):
			var nt = f.p_tile + Field.DV[d]
			if not f.solid_at(nt.x, nt.y):
				await walk_to(nt.x, nt.y)
				await walk_to(a.x, a.y)
				moved = true
				break
		if not moved:
			return fail("grind: boxed in at %s" % str(f.p_tile))
		await settle()
	QA.note("grind: %d battles, Dain Lv %d" % [n, int(Game.member("C01")["level"])])
	return true

## Shop through the real shop menu: approach the counter, Buy, confirm each unit.
func buy_items(shop_id: String, wants: Array) -> bool:
	var f: Field = main.field
	hold_menus = true
	var ok = false
	if shop_id.begins_with("npc:"):
		ok = await talk_npc(shop_id.substr(4))
	else:
		var p = ent_pos("shop", shop_id)
		if p.x < 0:
			hold_menus = false
			return fail("no shop %s on %s" % [shop_id, f.map_id])
		ok = await talk(p.x, p.y)
	if not ok:
		hold_menus = false
		return false
	await frames(6)
	var gm = _gm()
	var g0 = 0
	while gm == null and g0 < 120:
		await press("confirm")    # finish the shopkeeper's greeting
		await frames(4)
		gm = _gm()
		g0 += 1
	if gm == null:
		hold_menus = false
		return fail("shop menu did not open")
	await _pick(gm.lists[-1], 0)   # Buy
	await frames(4)
	var lst: MenuList = gm.lists[-1]
	QA.note("shop open: page=%s lists=%d items=%d top=%s" % [gm.page, gm.lists.size(), lst.items.size(), str(top())])
	for w in wants:
		var k = _menu_index(lst, func(it): return it.get("value", "") == w[0])
		if k < 0:
			QA.note("shop %s does not stock %s" % [shop_id, w[0]])
			continue
		while lst.index != k:
			await press("down" if lst.index < k else "up")
		for i in range(int(w[1])):
			if Game.gold() < int(Content.item(w[0])["price"]):
				break
			await press("confirm")
			await frames(2)
	QA.note("bought; gold now %d, items %s" % [Game.gold(), str(Game.S["inventory"]["items"])])
	var guard = 0
	while _gm() != null and guard < 8:
		await press("cancel")
		guard += 1
	hold_menus = false
	await settle()
	return true

## Menu > Equipment > member > Optimize, for every available member.
func optimize_all() -> bool:
	for idx in range(Game.S["party"]["roster"].size()):
		var cid: String = Game.S["party"]["roster"][idx]
		if not Game.is_available(cid):
			continue
		await press("menu")
		await frames(6)
		var gm = _gm()
		if gm == null:
			return fail("menu did not open")
		await menu_pick_text(gm.lists[-1], "Equipment")
		await frames(4)
		await _pick(gm.lists[-1], idx)
		await frames(4)
		var el: MenuList = gm.lists[-1]
		var k = _menu_index(el, func(it): return it.get("value", "") == "optimize")
		if k >= 0:
			await _pick(el, k)
		await frames(4)
		var guard = 0
		while _gm() != null and guard < 8:
			await press("cancel")
			guard += 1
		await settle()
	QA.note("optimized equipment for available members")
	return true

func airship_step(st: Array) -> bool:
	var f: Field = main.field
	match st[1]:
		"board":
			if f.ship_pos.x < 0:
				return fail("no parked ship on " + f.map_id)
			choice_plan = [0]
			if not await talk(f.ship_pos.x, f.ship_pos.y):
				return false
			return f.vehicle == "ship" or fail("did not board")
		"fly":
			return await walk_to(st[2], st[3], false, 900.0)
		"fly_to":
			# the named landing field of the current world map
			for e in f.map["entities"]:
				if e["type"] == "landing" and e.get("name", "") == st[2]:
					return await walk_to(int(e["x1"]) + 1, int(e["y1"]), false, 1500.0)
			return fail("no landing %s on %s" % [st[2], f.map_id])
		"land":
			choice_plan = [0]
			await press("confirm")
			await settle()
			return f.vehicle == "foot" or fail("landing refused at %s" % str(f.p_tile))
	return fail("bad airship step")

func seg_resume(from_ms: String, name: String) -> bool:
	seg_name = name
	await wait(0.5)
	if not await resume(from_ms):
		return false
	QA.note("CHAIN: segment %s starts from milestone %s (written by the previous normal-input segment)" % [name, from_ms])
	return true

# ---------------------------------------------------------------- pre-state: CH02-CH04
func r_seg2() -> bool:
	if not await seg_resume("ch01_done", "seg2"): return false
	return await run_steps(SEG2)

func r_seg2b() -> bool:
	## continue CH04 from the ch03_done milestone written by seg2
	if not await seg_resume("ch03_done", "seg2b"): return false
	return await run_steps(SEG2.slice(SEG2.find(["ms", "ch03_done"]) + 1))

var SEG2 = [
		["exit", "WORLD"], ["loc", "L_T02"], ["shot", "veyr"], ["exit", "T02_SQUARE"], ["go", 19, 12],
		["wait_map", "D02_R01"], ["npc", "oriel_cell"], ["check", "recruited:C06"], ["exit", "D02_R02"], ["go", 15, 13],
		["exit", "D02_R03"], ["use", "switch", "bell"], ["exit", "D02_R05"], ["go", 19, 20], ["check", "flag:b02_done"],
		["exit", "D02_R06"], ["go", 14, 11], ["wait_map", "WORLD"], ["check", "ch:CH02"], ["ms", "ch02_done"],
		["loc", "L_D03"], ["npc", "nera_camp"], ["exit", "D03_R02"], ["exit", "D03_R03"],
		["use", "switch", "valve_c"], ["use", "switch", "valve_a"], ["use", "switch", "valve_b"], ["check", "flag:d03_sluices"],
		["exit", "D03_R04"], ["exit", "D03_R05"], ["go", 19, 12], ["check", "flag:b03_done"], ["shot", "after_b03"],
		["exit", "D03_R06"], ["go", 15, 5], ["check", "ch:CH03"], ["exit", "WORLD"], ["ms", "ch03_done"],
		["loc", "L_T03"], ["exit", "T03_SHOP"], ["npc", "ivo_shop"], ["exit", "T03_TOWN"], ["exit", "D04_R01"],
		["go", 6, 13], ["check", "recruited:C04"], ["exit", "D04_R02"], ["exit", "D04_R03"], ["choice", [1]],
		["use", "switch", "valve"], ["check", "flag:d04_red"], ["exit", "D04_R02"], ["exit", "D04_R04"], ["choice", [0]],
		["use", "switch", "valve"], ["check", "flag:d04_blue"], ["save", 2], ["exit", "D04_R05"], ["go", 19, 14],
		["check", "flag:b04_done"], ["exit", "D04_R06"], ["go", 4, 11], ["wait_map", "T03_TOWN"], ["check", "ch:CH04"],
		["shot", "cinderwake_after"], ["ms", "ch04_done"],
	]


# ---------------------------------------------------------------- pre-state: CH05-CH07
func r_seg3() -> bool:
	if not await seg_resume("ch04_done", "seg3"): return false
	var steps = [
		["exit", "WORLD"], ["loc", "L_T04"], ["shot", "bellharbor"], ["npc", "pip_quay"], ["npc", "pot_child"],
		["check", "flag:t04_distracted"], ["exit", "T04_CUSTOMS"], ["tile", 3, 3], ["wait_map", "T04_CHASE"],
		["go", 15, 14], ["go", 15, 11], ["go", 15, 5], ["go", 26, 2], ["exit", "T04_QUAY"], ["exit", "T04_LANE"],
		["go", 16, 7], ["check", "ch:CH05"], ["check", "recruited:C08"], ["ms", "ch05_done"],
		["exit", "T04_QUAY"], ["exit", "WORLD"], ["loc", "L_D05"], ["go", 19, 20], ["exit", "D05_R02"],
		["use", "switch", "bell_low"], ["go", 3, 9], ["check", "flag:d05_dry"], ["use", "switch", "bell_high"],
		["exit", "D05_R03"], ["go", 1, 19], ["check", "flag:d05_vault"], ["exit", "D05_R05"], ["go", 19, 14],
		["check", "flag:b05_done"], ["exit", "D05_R06"], ["go", 15, 8], ["wait_map", "WORLD"], ["check", "ch:CH06"],
		["ms", "ch06_done"], ["choice", [0]], ["trig", "FERRY_BELLHARBOR"], ["settle"], ["loc", "L_D06"], ["npc", "corren_foot"],
		["check", "recruited:C03"], ["exit", "D06_R02"], ["use", "switch", "ballast1"], ["use", "switch", "ballast2"],
		["exit", "D06_R03"], ["exit", "D06_R04"], ["save", 2], ["exit", "D06_R05"], ["go", 19, 18], ["check", "flag:b06_done"],
		["exit", "D06_R06"], ["go", 4, 11], ["check", "ch:CH07"], ["shot", "high_landing"], ["exit", "WORLD"], ["ms", "ch07_done"],
	]
	return await run_steps(steps)

# ---------------------------------------------------------------- pre-state: CH08-CH10
func r_seg4() -> bool:
	if not await seg_resume("ch07_done", "seg4"): return false
	return await run_steps(SEG4)

func r_seg4b() -> bool:
	if not await seg_resume("ch08_done", "seg4b"): return false
	return await run_steps(SEG4.slice(SEG4.find(["ms", "ch08_done"]) + 1))

var SEG4 = [
		["choice", [0]], ["trig", "CABLE_AERIE"], ["settle"], ["loc", "L_D07"], ["go", 19, 15], ["check", "event:D07_SABLE_GATE"],
		["exit", "D07_R02"], ["exit", "D07_R03"], ["tile", 8, 5], ["tile", 19, 5], ["tile", 30, 5],
		["check", "flag:d07_name1,flag:d07_name2,flag:d07_name3"], ["exit", "D07_R04"], ["npc", "prisoner1"], ["use", "switch", "lock1"], ["npc", "prisoner2"],
		["use", "switch", "lock2"], ["npc", "prisoner3"], ["use", "switch", "lock3"], ["check", "flag:d07_open1,flag:d07_open2,flag:d07_open3"],
		["save", 2], ["exit", "D07_R05"], ["go", 19, 10], ["check", "flag:b07_done"], ["exit", "D07_R06"], ["go", 4, 11],
		["check", "ch:CH08"], ["check", "recruited:C07"], ["exit", "WORLD"], ["ms", "ch08_done"],
		["loc", "L_D08"], ["choice", [0]], ["go", 19, 14], ["exit", "D08_R02"], ["tile", 8, 6], ["exit", "D08_R03"],
		["tile", 12, 15], ["tile", 26, 15], ["exit", "D08_R02"], ["exit", "D08_R04"], ["tile", 22, 19], ["exit", "D08_R02"],
		["choice", [1, 1, 0]], ["tile", 15, 14], ["check", "flag:d08_chrono"], ["exit", "D08_R04"], ["exit", "D08_R05"],
		["go", 19, 14], ["check", "flag:b08_done"], ["exit", "D08_R06"], ["go", 15, 16], ["check", "ch:CH09"], ["shot", "still_pool"],
		["ms", "ch09_done"],
		["exit", "D08_R05"], ["exit", "D08_R04"], ["exit", "D08_R02"], ["exit", "D08_R01"], ["exit", "WORLD"],
		["loc", "L_T06"], ["npc", "sen"], ["check", "flag:accord_nacre"], ["exit", "WORLD"],
		["loc", "L_T03"], ["exit", "T03_GARDEN"], ["use", "switch", "bypass"], ["check", "flag:accord_cinder"],
		["exit", "T03_TOWN"], ["exit", "WORLD"], ["choice", [0]], ["trig", "CABLE_NACRE"], ["settle"], ["loc", "L_T05"],
		["use", "switch", "cable_brake"], ["check", "flag:accord_aerie"], ["exit", "WORLD"], ["choice", [0]], ["trig", "CABLE_AERIE"],
		["settle"], ["loc", "L_T06"], ["exit", "T06_POOL"], ["go", 24, 16], ["check", "ch:CH10"], ["shot", "smaller_accord"],
		["exit", "T06_MARKET"], ["exit", "WORLD"], ["ms", "ch10_done"],
	]


# ---------------------------------------------------------------- CH11-CH12 (the Conduit and the catastrophe)
func r_seg5() -> bool:
	if not await seg_resume("ch10_done", "seg5"): return false
	var steps = [
		["loc", "L_D09"], ["go", 19, 20], ["check", "event:D09_ENTER"], ["exit", "D09_R02"], ["choice", [0]],
		["use", "switch", "relay_s"], ["check", "flag:d09_relay_s"], ["exit", "D09_R04"], ["exit", "D09_R03"], ["choice", [0]],
		["use", "switch", "lift_route"], ["check", "flag:d09_relay_n"], ["exit", "D09_R04"], ["go", 15, 5],
		["check", "event:D09_WARNING"], ["save", 3], ["heal"], ["exit", "D09_R05"], ["go", 19, 20], ["check", "flag:b09_done,ch:CH11"],
		["ms", "ch11_done"], ["use", "switch", "relay_bridge"], ["exit", "D09_R06"], ["go", 15, 13], ["wait_map", "D09_ESC"],
		["shot", "escape"], ["go", 40, 9], ["wait_map", "T07_HEARTH"], ["settle"], ["check", "ch:CH12"], ["shot", "hearthward_wake"],
		["ms", "ch12_done"],
	]
	return await run_steps(steps)

# ---------------------------------------------------------------- post-state: CH13-CH16
func r_seg6() -> bool:
	if not await seg_resume("ch12_done", "seg6"): return false
	var steps = [
		["check", "event:CH13_WAKE"], ["npc", "plank_pile"], ["npc", "lamp_keeper"], ["tile", 30, 12], ["check", "flag:t07_fuel,flag:t07_path"],
		["npc", "oriel_h"], ["check", "ch:CH13"], ["use", "chest", "T07_SUPPLIES"], ["use", "chest", "T07_SUPPLIES2"],
		["use", "switch", "salvage_chest"], ["shot", "hearth"], ["exit", "T07_MARKET"], ["shot", "market"], ["exit", "WORLD_POST"],
		["ms", "ch13_done"], ["loc", "L_D03"], ["go", 18, 17], ["check", "event:CH14_CAMP"], ["exit", "D03P_R02"],
		["use", "switch", "route1"], ["use", "switch", "route2"], ["use", "switch", "route3"], ["exit", "D03P_R03"],
		["go", 17, 12], ["check", "flag:b11_done"], ["go", 17, 18], ["check", "ch:CH14"], ["check", "party:C05"],
		["exit", "D03P_R02"], ["exit", "D03P_R01"], ["exit", "WORLD_POST"], ["ms", "ch14_done"],
		["loc", "L_T07"], ["choice", [0]], ["npc", "ferryman"], ["wait_map", "WORLD_POST"], ["loc", "L_T04"],
		["exit", "T04_GALLERY"], ["go", 19, 23], ["check", "event:CH15_ARRIVE"], ["use", "switch", "winch1"],
		["use", "switch", "winch2"], ["npc", "res1"], ["npc", "res2"], ["npc", "res3"], ["go", 19, 12], ["check", "ch:CH15"],
		["check", "party:C02"], ["shot", "lanterns"], ["exit", "T04_UPPER"], ["exit", "WORLD_POST"], ["ms", "ch15_done"],
		["choice", [0]], ["trig", "FERRY_HEARTHWARD"], ["wait_map", "T07_MARKET"], ["exit", "WORLD_POST"], ["loc", "L_T03"],
		["exit", "T03_YARD"], ["go", 4, 13], ["check", "event:CH16_YARD"], ["use", "switch", "channel1"],
		["use", "switch", "channel2"], ["use", "switch", "channel3"], ["npc", "crew_y1"], ["check", "flag:t03y_clear"],
		["npc", "tortoise"], ["check", "flag:v06_given"], ["npc", "pell_y"], ["check", "ch:CH16"], ["check", "party:C04"],
		["shot", "launch"], ["exit", "T03_POST"], ["exit", "WORLD_POST"], ["ms", "ch16_done"],
	]
	return await run_steps(steps)

# ---------------------------------------------------------------- post-state: CH17-CH20 (reunions in any order; this run: Corren, Pip, Sable)
func r_seg7() -> bool:
	if not await seg_resume("ch16_done", "seg7"): return false
	var steps = [
		["airship", "board"], ["shot", "helm"], ["airship", "fly_to", "Skychain"], ["airship", "land"],
		["loc", "L_D06"], ["go", 10, 24], ["check", "event:CH17_ARRIVE"], ["use", "switch", "anchor1"],
		["use", "switch", "anchor2"], ["use", "switch", "anchor3"], ["npc", "corren_m"], ["check", "ch:CH17,party:C03"],
		["exit", "WORLD_POST"], ["ms", "ch17_done"],
		["airship", "board"], ["airship", "fly_to", "Veyr"], ["airship", "land"], ["loc", "L_T02"], ["npc", "jori_v"],
		["exit", "T02_CANALS"], ["use", "switch", "gate1"], ["use", "switch", "gate2"], ["use", "switch", "gate3"],
		["exit", "T02_REGISTRY_POST"], ["go", 15, 18], ["check", "flag:t02r_clear"], ["npc", "pip_r"], ["tile", 11, 14],
		["check", "ch:CH18,party:C08"], ["exit", "T02_CANALS"], ["exit", "T02_SQUARE_POST"], ["exit", "WORLD_POST"], ["ms", "ch18_done"],
		["airship", "board"], ["airship", "fly_to", "Whitebone"], ["airship", "land"], ["loc", "L_D07"], ["go", 19, 19],
		["check", "event:CH19_ARRIVE"], ["exit", "D07P_R02"], ["tile", 9, 9], ["use", "switch", "lock1"], ["tile", 19, 9],
		["use", "switch", "lock2"], ["tile", 29, 9], ["use", "switch", "lock3"], ["go", 19, 22], ["check", "ch:CH19,party:C07"],
		["exit", "D07P_R01"], ["exit", "WORLD_POST"], ["ms", "ch19_done"],
		["loc", "L_T06"], ["go", 20, 23], ["check", "ch:CH20"], ["shot", "ash_accord"], ["exit", "WORLD_POST"], ["ms", "ch20_done"],
	]
	return await run_steps(steps)

# ---------------------------------------------------------------- CH22-CH24 (Crown Heart, ending, post-clear)
func r_seg8() -> bool:
	if not await seg_resume("ch20_done", "seg8"): return false
	var steps = [
		["airship", "board"], ["airship", "fly_to", "Hearthward"], ["airship", "land"], ["loc", "L_T07"],
		["buy", "npc:stall", [["I002", 8], ["I004", 8], ["I006", 4], ["W004", 1], ["W010", 1], ["W034", 1], ["W028", 1]]],
		["optimize"], ["exit", "WORLD_POST"], ["grind_to", 31, 45],
		["loc", "L_T02"], ["buy", "npc:market_v", [["G016", 1], ["G004", 1], ["G008", 1], ["G023", 2]]], ["optimize"],
		["exit", "WORLD_POST"], ["airship", "board"], ["airship", "fly_to", "Crown Heart"], ["airship", "land"], ["loc", "L_D10"],
		["go", 19, 18], ["check", "event:D10_DOCK"], ["use", "switch", "split"], ["wait_map", "D10_R02"],
		["check", "flag:d10_split"], ["grind_to", 33, 30], ["use", "switch", "lockA"], ["choice", [0]], ["use", "switch", "swapbell"],
		["wait_map", "D10_R03"], ["use", "switch", "lockA"], ["choice", [0]], ["use", "switch", "swapbell"], ["wait_map", "D10_R02"],
		["use", "switch", "lockB"], ["choice", [0]], ["use", "switch", "swapbell"], ["wait_map", "D10_R03"], ["use", "switch", "lockB"],
		["wait_map", "D10_R04"], ["check", "flag:d10_done_lungs"], ["go", 15, 18], ["save", 2], ["heal"], ["ms", "ch22_before_vessel"],
		["exit", "D10_R05"], ["go", 19, 16], ["check", "flag:b12_done"], ["exit", "D10_R06"], ["go", 15, 11],
		["wait_map", "T07_MARKET"], ["check", "ch:CH22,ch:CH23"], ["shot", "after"], ["exit", "T07_HEARTH"], ["go", 17, 14],
		["check", "flag:dawn"], ["exit", "T07_MARKET"], ["exit", "T07_BERTH"], ["go", 17, 12], ["shot", "lamp_three"],
		["choice", [0]], ["go", 35, 12], ["wait_map", "D10_R01"], ["check", "flag:post_clear"], ["shot", "post_clear"],
		["ms", "post_clear"],
	]
	return await run_steps(steps)

# ---------------------------------------------------------------- CH21 window: the twelve optional quests
func r_segq() -> bool:
	if not await seg_resume("ch20_done", "segq"): return false
	return await run_steps(SEGQ)

func r_segq2() -> bool:
	if not await seg_resume("q_winter", "segq2"): return false
	return await run_steps(SEGQ.slice(SEGQ.find(["ms", "q_winter"]) + 1))

func r_segq3() -> bool:
	if not await seg_resume("q_reef", "segq3"): return false
	return await run_steps(SEGQ.slice(SEGQ.find(["ms", "q_reef"]) + 1))

var SEGQ = [
		# Nacre leads (Q06, Q07, Q09, Q12)
		["loc", "L_T06"], ["npc", "patient_p"], ["npc", "survivor_n"], ["npc", "winter_pilgrim"], ["npc", "pool_voice"],
		["check", "q:Q06:ACTIVE,q:Q07:ACTIVE,q:Q09:ACTIVE,q:Q12:ACTIVE"], ["exit", "WORLD_POST"],
		["loc", "L_D08"], ["tile", 6, 6], ["npc", "q6_patient"], ["use", "switch", "seal"], ["check", "q:Q06"], ["exit", "WORLD_POST"],
		["loc", "L_D07"], ["exit", "D07P_R02"], ["exit", "D07P_R03"], ["npc", "q7occ1"], ["tile", 7, 7], ["npc", "q7occ2"],
		["tile", 15, 7], ["npc", "q7occ3"], ["tile", 23, 7], ["use", "switch", "repeater"], ["check", "q:Q07"],
		["exit", "D07P_R02"], ["exit", "D07P_R01"], ["exit", "WORLD_POST"], ["ms", "q_nacre"],
		# supplies at Hearthward
		["airship", "board"], ["airship", "fly_to", "Hearthward"], ["airship", "land"], ["loc", "L_T07"],
		["buy", "npc:stall", [["I002", 10], ["I004", 10], ["I006", 5], ["I003", 2], ["W004", 1], ["W010", 1], ["W028", 1]]],
		["optimize"], ["exit", "WORLD_POST"],
		# Brackenford (Q01, Q05)
		["airship", "board"], ["airship", "fly_to", "Brackenford"], ["airship", "land"], ["loc", "L_T01"], ["npc", "forewoman"],
		["npc", "camp_west"], ["check", "q:Q01:ACTIVE,q:Q05:ACTIVE"], ["exit", "WORLD_POST"], ["loc", "L_D01"],
		["use", "switch", "record1"], ["use", "switch", "record2"], ["use", "switch", "record3"], ["npc", "family1"],
		["check", "q:Q01:RESOLUTION_READY"], ["exit", "WORLD_POST"], ["loc", "L_T01"], ["npc", "forewoman"], ["check", "q:Q01"],
		["exit", "WORLD_POST"], ["loc", "L_D03"], ["exit", "D03P_R02"], ["tile", 12, 25], ["check", "qs:Q05:surveyed"],
		["exit", "D03P_R01"], ["exit", "WORLD_POST"], ["loc", "L_T01"], ["npc", "camp_west"], ["check", "q:Q05"],
		["exit", "WORLD_POST"], ["ms", "q_brackenford"],
		# Glass Coast (Q02)
		["airship", "board"], ["airship", "fly_to", "Bellharbor"], ["airship", "land"], ["loc", "L_T04"], ["npc", "apprentice_u"],
		["exit", "WORLD_POST"], ["airship", "board"], ["airship", "fly_to", "Archive Point"], ["airship", "land"], ["loc", "L_D05"],
		["npc", "station1"], ["npc", "station2"], ["npc", "station3"], ["npc", "apprentice_q2"], ["use", "switch", "circuit"],
		["check", "q:Q02"], ["exit", "WORLD_POST"],
		# Skyspine (Q03)
		["airship", "board"], ["airship", "fly_to", "High Aerie"], ["airship", "land"], ["loc", "L_T05"], ["npc", "edda_p"],
		["exit", "WORLD_POST"], ["airship", "board"], ["airship", "fly_to", "Skychain"], ["airship", "land"], ["loc", "L_D06"],
		["tile", 5, 24], ["npc", "q3_survivor"], ["use", "switch", "marker"], ["check", "q:Q03:RESOLUTION_READY"],
		["exit", "WORLD_POST"], ["airship", "board"], ["airship", "fly_to", "High Aerie"], ["airship", "land"], ["loc", "L_T05"],
		["npc", "edda_p"], ["check", "q:Q03"], ["exit", "WORLD_POST"],
		# Cinder Reach (Q04)
		["airship", "board"], ["airship", "fly_to", "Cinderwake"], ["airship", "land"], ["loc", "L_T03"], ["npc", "pell_p"],
		["exit", "WORLD_POST"], ["loc", "L_D04"], ["npc", "q4w1"], ["npc", "q4w2"], ["npc", "q4w3"], ["use", "switch", "restart"],
		["check", "q:Q04"], ["exit", "WORLD_POST"], ["ms", "q_personal_7"],
		# Winter island (Q09)
		["airship", "board"], ["airship", "fly_to", "Winter Island"], ["airship", "land"], ["loc", "L_D11"], ["go", 19, 20],
		["exit", "D11_R02"], ["npc", "sleeper1"], ["npc", "sleeper2"], ["npc", "sleeper3"], ["exit", "D11_R03"],
		["use", "switch", "heat1"], ["use", "switch", "heat2"], ["use", "switch", "heat3"], ["check", "flag:d11_thaw"],
		["exit", "D11_R04"], ["grind_to", 35, 40], ["save", 3], ["heal"], ["exit", "D11_R05"], ["choice", [0]], ["go", 19, 16],
		["check", "flag:b13_done"], ["exit", "D11_R06"], ["go", 15, 10], ["check", "q:Q09"], ["exit", "D11_R05"], ["exit", "D11_R04"],
		["exit", "D11_R02"], ["exit", "D11_R01"], ["exit", "WORLD_POST"], ["ms", "q_winter"],
		# Starless Reef (Q10)
		["airship", "board"], ["airship", "fly_to", "Hearthward"], ["airship", "land"], ["loc", "L_T07"], ["npc", "bell_child"],
		["check", "q:Q10:ACTIVE"], ["exit", "WORLD_POST"], ["airship", "board"], ["airship", "fly_to", "Reef Shoal"], ["airship", "land"],
		["loc", "L_D12"], ["go", 19, 20], ["exit", "D12_R02"], ["exit", "D12_R03"], ["use", "switch", "reflector"],
		["grind_to", 37, 40], ["exit", "D12_R04"], ["tile", 11, 12], ["save", 3], ["exit", "D12_R05"], ["choice", [0]], ["go", 19, 16],
		["check", "flag:b14_done"], ["exit", "D12_R06"], ["go", 15, 10], ["check", "q:Q10"], ["exit", "D12_R05"], ["exit", "D12_R04"],
		["exit", "D12_R02"], ["exit", "D12_R01"], ["exit", "WORLD_POST"], ["ms", "q_reef"],
		# Veyr (Q08, Q11)
		["airship", "board"], ["airship", "fly_to", "Veyr"], ["airship", "land"], ["loc", "L_T02"], ["npc", "ansel_p"],
		["exit", "T02_CANALS"], ["exit", "T02_REGISTRY_POST"], ["npc", "registrar"], ["exit", "T02_CANALS"], ["exit", "D02P_SEALS"],
		["choice", [0]], ["use", "switch", "dial1"], ["choice", [1]], ["use", "switch", "dial2"], ["choice", [2]], ["use", "switch", "dial3"],
		["tile", 13, 11], ["check", "qs:Q08:sealed"], ["exit", "T02_CANALS"], ["exit", "T02_REGISTRY_POST"], ["npc", "registrar"],
		["check", "q:Q08"], ["exit", "T02_CANALS"], ["exit", "D02P_ECHO"], ["tile", 9, 4], ["save", 3], ["go", 13, 8],
		["check", "q:Q11"], ["exit", "T02_CANALS"], ["exit", "T02_SQUARE_POST"], ["exit", "WORLD_POST"], ["ms", "q_veyr"],
		# Q12: the silent alcove, before the final commitment
		["airship", "board"], ["airship", "fly_to", "Crown Heart"], ["airship", "land"], ["loc", "L_D10"], ["go", 19, 18],
		["use", "switch", "split"], ["wait_map", "D10_R02"], ["use", "switch", "lockA"], ["choice", [0]], ["use", "switch", "swapbell"],
		["wait_map", "D10_R03"], ["use", "switch", "lockA"], ["choice", [0]], ["use", "switch", "swapbell"], ["wait_map", "D10_R02"],
		["use", "switch", "lockB"], ["choice", [0]], ["use", "switch", "swapbell"], ["wait_map", "D10_R03"], ["grind_to", 38, 40],
		["use", "switch", "lockB"], ["wait_map", "D10_R04"], ["go", 15, 18], ["save", 3], ["heal"], ["exit", "D10_ALCOVE"], ["choice", [0]],
		["go", 10, 8], ["check", "q:Q12"], ["ms", "q_all"],
	]


func r_shoptest() -> bool:
	if not await seg_resume("ch12_done", "shoptest"): return false
	return await run_steps([["exit", "T07_MARKET"], ["buy", "npc:stall", [["I001", 2], ["I004", 1]]], ["check", "flag:t07_path"]])
