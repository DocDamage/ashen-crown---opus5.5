class_name Director
extends Node
## StoryDirector: runs validated scene command lists. State-changing commands always execute; staging
## commands (say/move/wait/fade...) become instant while skipping, so a skipped scene commits exactly
## the same state as a watched one (AC044). Scenes marked `once` record their ID in the applied-event ledger.

signal scene_done(id: String)

var main: Node
var running = false
var skipping = false
var current = ""
var ctx: Dictionary = {}
var abort = false
var depth = 0

func run(scene_id: String, p_ctx: Dictionary = {}) -> String:
	var sc: Dictionary = Content.scene(scene_id)
	if sc.is_empty():
		push_error("Missing scene " + scene_id)
		return "missing"
	if sc.get("once", false) and Game.event_applied(scene_id):
		return "already"
	var outer = running
	running = true
	depth += 1
	current = scene_id
	ctx = p_ctx
	main.field.busy = true
	var cmds: Array = sc["cmds"]
	var labels = {}
	for i in range(cmds.size()):
		if cmds[i]["c"] == "label":
			labels[cmds[i]["a"][0]] = i
	var pc = 0
	var result = "ok"
	while pc < cmds.size():
		if abort:
			result = "aborted"
			break
		var c: Dictionary = cmds[pc]
		pc += 1
		var jump = await _exec(c, labels)
		if typeof(jump) == TYPE_INT and jump >= 0:
			pc = jump
		elif typeof(jump) == TYPE_STRING and jump == "end":
			break
		elif typeof(jump) == TYPE_STRING and jump == "abort":
			result = "aborted"
			abort = true
			break
	if sc.get("once", false) and result == "ok":
		Game.apply_event(scene_id)
	depth -= 1
	if depth == 0:
		running = false
		skipping = false
		abort = false
		main.dialogue.skip_all = false
		if is_instance_valid(main.field):
			main.field.busy = false
			main.field.refresh_npcs()
	emit_signal("scene_done", scene_id)
	return result

func _exec(c: Dictionary, labels: Dictionary):
	var a: Array = c.get("a", [])
	match c["c"]:
		"label", "note":
			pass
		"say":
			var spk: String = a[0] if a.size() > 0 else "narr"
			var ex: String = a[1] if a.size() > 1 else "neutral"
			var info: Array = Content.speaker(spk)
			var nm: String = info[0]
			if spk.begins_with("\""):
				nm = spk.strip_edges().replace("\"", "")
			if not Content.data["speakers"].has(spk) and spk != "narr":
				nm = spk.replace("_", " ")
			if info.size() > 1 and Game.CHAR_IDS.has(str(info[1])):
				nm = Game.short_name(str(info[1]))
			main.dialogue.voice_key = str(info[1]) if info.size() > 1 and str(info[1]).begins_with("C") else spk
			await main.say(nm, Game.mature_filter(Game.sub_names(_interp(c["text"])), Game.mature()), info[1] if info.size() > 1 else "", ex)
		"choice":
			var idx: int = await main.choose(c["options"].map(func(o): return Game.mature_filter(Game.sub_names(o["text"]), Game.mature())))
			var tgt: String = c["options"][idx]["goto"]
			if tgt != "" and labels.has(tgt):
				return labels[tgt]
		"goto":
			return labels[a[0]]
		"if":
			# if <cond,...> <label>
			var conds = String(a[0]).split(",")
			if Game.eval_cond(Array(conds)):
				return labels[a[-1]]
		"end":
			return "end"
		"call":
			var r = await run(a[0], ctx)
			if r == "aborted":
				return "abort"
		"set":
			Game.set_flag(a[0], true)
		"unset":
			Game.set_flag(a[0], false)
		"setvar":
			Game.var_set(a[0], int(a[1]))
		"addvar":
			Game.var_set(a[0], Game.var_get(a[0]) + int(a[1]))
		"event":
			Game.apply_event(a[0])
		"give":
			var n = int(a[1]) if a.size() > 1 else 1
			if a.size() > 2:
				if not Game.acquire_unique(a[2], a[0], n):
					return -1
			else:
				Game.add_item(a[0], n)
			Audio.sfx("FX007")
			await main.say("", T.f("sys.received", [Content.item_name(a[0]) + (" x%d" % n if n > 1 else "")]), "")
		"take":
			Game.remove_item(a[0], int(a[1]) if a.size() > 1 else 1)
		"key":
			if Game.count(a[0]) == 0:
				Game.add_item(a[0], 1)
				await main.say("", T.f("sys.obtained", [Content.item_name(a[0])]), "")
		"unkey":
			Game.remove_item(a[0], Game.count(a[0]))
		"gold":
			Game.add_gold(int(a[0]))
			if int(a[0]) > 0:
				await main.say("", T.f("sys.crowns", [int(a[0])]), "")
		"xp":
			var msgs = Game.award_xp(int(a[0]))
			for m in msgs:
				await main.say("", m, "")
		"level_floor":
			# transparent milestone growth when ordinary encounters are off (docs/07)
			var floor_lv = int(a[0])
			Game.S["vars"]["story_floor"] = maxi(Game.var_get("story_floor"), floor_lv)
			if Settings.get_v("encounters") == "off":
				var need = 0
				for cid in Game.available_members():
					need = maxi(need, F.xp_total_for_level(floor_lv) - int(Game.member(cid)["xp"]))
				if need > 0:
					for m in Game.award_xp(need):
						await main.say("", m + " (milestone growth)", "")
		"join":
			var cid: String = a[0]
			if Rescue.holds(cid):
				# a reunion with one of the Bound: the scene plays, but the hero goes back to the other four
				Rescue.note_met(cid)
				if not Content.scene("BOUND_MEET_" + cid).is_empty():
					await run("BOUND_MEET_" + cid, ctx)
				await main.say("", "%s is soul-bound to the others and goes back to them." % Game.char_name(cid), "")
				return -1
			var first = not Game.is_recruited(cid)
			var msgs = Game.recruit(cid)
			if first:
				Audio.jingle("join", true)
			else:
				Audio.sfx("FX028")
			main.field.update_leader()
			for m in msgs:
				await main.say("", m, "")
			if first and not Game.S.get("names_asked", {}).has(cid):
				if not Game.S.has("names_asked"):
					Game.S["names_asked"] = {}
				Game.S["names_asked"][cid] = true
				await main.name_entry(cid)
		"name":
			await main.name_entry(a[0])
		"rename":
			# the Namer: pick a recruited hero, then enter a name
			var ids: Array = Game.S["party"]["roster"].duplicate()
			var opts: Array = ids.map(func(x): return Game.short_name(x))
			opts.append("Never mind")
			var pick: int = await main.choose(opts)
			if pick >= 0 and pick < ids.size():
				await main.name_entry(ids[pick])
		"leave", "avail":
			var val = false if c["c"] == "leave" else (a[1] == "true")
			Game.set_available(a[0], val)
			main.field.update_leader()
		"chapter":
			Game.complete_chapter(a[0])
		"objective":
			Game.set_objective(c["text"], a[0] if a.size() > 0 else "")
			if not skipping:
				main.toast("Objective: " + c["text"])
		"journal":
			Game.S["journal"]["clue"] = c["text"]
		"rumor":
			Game.add_rumor(c["text"])
		"discover":
			Game.discover(a[0])
		"quest":
			Game.quest_set(a[0], a[1], a[2] if a.size() > 2 else "")
		"vestige":
			Game.grant_vestige(a[0])
			Audio.sfx("FX029")
			await main.say("", "The Vestige %s answers. (Link it from the menu.)" % Content.data["vestiges"][a[0]]["name"], "")
		"equip":
			var m = Game.member(a[0])
			m["equip"][a[1]] = a[2]
		"heal":
			Game.heal_all()
		"battle":
			var flags = a.slice(1)
			var res: String = await main.run_battle(a[0], {"scripted": true, "flags": flags})
			if res == "defeat_load" or res == "aborted":
				return "abort"
			if res == "fled":
				return -1
		"warp":
			var spawn: String = a[1] if a.size() > 1 else "default"
			await main.warp(a[0], spawn, a[2] if a.size() > 2 else "")
		"show":
			# show id x y dir sprite
			main.field.show_actor(a[0], int(a[1]), int(a[2]), a[3] if a.size() > 3 else "down", a[4] if a.size() > 4 else a[0])
		"hide":
			main.field.hide_actor(a[0])
		"sprite":
			var ac: Dictionary = main.field.actor(a[0])
			if not ac.is_empty():
				ac["sprite"] = a[1]
		"move":
			# move id dirs...  e.g. move dain up up left
			var path = a.slice(1)
			if skipping:
				_teleport_path(a[0], path)
			else:
				await main.field.move_actor(a[0], path)
		"face":
			main.field.face(a[0], a[1])
		"emote":
			if not skipping:
				main.emote(a[0], a[1] if a.size() > 1 else "!")
				await main.wait(0.5)
		"wait":
			if not skipping:
				await main.wait(float(a[0]))
		"fade":
			await main.fade(a[0] == "out", 0.0 if skipping else (float(a[1]) if a.size() > 1 else 0.4))
		"tint":
			main.field.tint = Color(a[0]) if a[0] != "none" else Color(0, 0, 0, 0)
		"lights":
			pass
		"music":
			Audio.music(a[0], float(a[1]) if a.size() > 1 else 1.2)
		"sfx":
			Audio.sfx(a[0])
		"shake":
			if not skipping:
				main.shake(float(a[0]) if a.size() > 0 else 0.4)
		"flash":
			if not skipping:
				main.flash(Color(a[0]) if a.size() > 0 else Color.WHITE)
		"still":
			# still <id> [seconds]: a full-screen cutscene image; skipped when the art is not installed yet
			if not skipping and StillView.exists(a[0]):
				await main.show_still(a[0], float(a[1]) if a.size() > 1 else 0.0)
		"doc":
			await main.show_doc(a[0].replace("_", " ") if a.size() > 0 else "", c["text"])
		"phase":
			if a[0] == "post":
				Game.catastrophe_transaction()
				Game.autosave_current()
		"backup":
			Game.write_backup(a[0])
		"shop":
			await main.open_shop(a[0])
		"inn":
			await main.open_inn(int(a[0]) if a.size() > 0 else -1)
		"craft":
			await main.open_menu_async("craft", {"id": a[0] if a.size() > 0 else ""})
		"formation":
			await main.open_menu_async("formation")
		"save_prompt":
			await main.open_menu_async("savepoint")
		"vehicle":
			Game.S["vehicle"][a[0]] = a[1] == "true"
		"salvage":
			var got = Game.claim_salvage()
			for iid in got:
				await main.say("", "Salvage: %s recovered." % Content.item_name(iid), "")
		"split_party":
			await main.open_menu_async("split")
		"lock_party":
			Game.S["party"]["locked"] = true
		"unlock_party":
			Game.S["party"]["locked"] = false
		"row":
			Game.S["party"]["rows"][a[0]] = a[1]
		"portrait":
			pass
		"credits":
			await main.roll_credits()
		"clear_save":
			await main.clear_save()
		"epilogue":
			Game.S["epilogue"][a[0]] = true
		"ending":
			await main.ending_menu()
			return "abort"
		"title":
			main.to_title()
			return "abort"
		"ship_travel":
			pass
		"rescue":
			var jr = await _rescue_cmd(a, labels)
			if typeof(jr) == TYPE_INT or (typeof(jr) == TYPE_STRING and jr != ""):
				return jr
		"bound":
			await _bound_cmd(a)
		"team":
			Rescue.merge()
			# final-dungeon teams: "team A" / "team B" lock the formation to that team; "team all" reunites
			if a[0] == "all":
				Game.S["party"]["locked"] = false
				Game.S["vars"]["team_on"] = 0
				var all_ids: Array = Game.S.get("teams", {}).get("A", []) + Game.S.get("teams", {}).get("B", [])
				if not all_ids.is_empty():
					Game.set_active(all_ids)
			else:
				Game.set_active(Game.S.get("teams", {}).get(a[0], Game.active()))
				Game.S["party"]["locked"] = true
				Game.S["vars"]["team_on"] = 1 if a[0] == "A" else 2
			main.field.update_leader()
		"airship":
			var ok = main.field.ship_op(a[0])
			Game.S["vars"]["ship_ok"] = 1 if ok else 0
		"travel":
			await FieldCmds.run(main, a)
		"arena":
			await Arena.run(main, a)
		_:
			push_error("Unhandled scene command " + c["c"])
	return -1

# ---------------------------------------------------------------- CH12 rescue (story/rescue.gd)
## rescue begin <skip_label>: jumps to the label when the route bot plays or the scene is skipped
## rescue pick: the player sends five of the eight heroes after the prisoners; the timer starts
## rescue finish: the brake is pulled (sets rescue_all or bound_formed)
## rescue crush: the timer ran out - retry from the lift or load a save
func _rescue_cmd(a: Array, labels: Dictionary):
	match a[0]:
		"begin":
			if skipping or QA.active or Rescue.eligible().is_empty():
				return labels.get(a[1], -1) if a.size() > 1 else -1
		"pick":
			var pool: Array = Rescue.eligible()
			var need = mini(5, pool.size())
			var team = []
			while team.size() < need:
				var opts = []
				for c in pool:
					if not team.has(c):
						opts.append(Game.short_name(c))
				var left = need - team.size()
				main.toast("Send who? (%d more)" % left)
				var idx = await main.choose(opts)
				var picked = pool.filter(func(c): return not team.has(c))[idx]
				team.append(picked)
			Game.S["vars"]["rescue_n"] = team.size()
			for i in range(team.size()):
				Game.S["vars"]["rescue_%d" % i] = team[i]
			Rescue.begin(team)
			main.field.update_leader()
		"finish":
			var lost = Rescue.finish()
			Game.S["vars"]["rescue_lost"] = lost.size()
			main.field.update_leader()
		"crush":
			var choice = await main.defeat_menu()
			Rescue.retry()
			if choice == 0:
				await main.warp(Rescue.LIFT_MAP, "start")
				main.field.update_leader()
				return "end"
			await main.open_menu_async("load_after_defeat")
			return "abort"
	return -1

## bound swap: switch control between Raven's company and the Bound (at the cursor's safe spot)
## bound merge: the Bound rejoin everyone
func _bound_cmd(a: Array) -> void:
	match a[0]:
		"swap":
			if not Rescue.bound_active():
				return
			var f = main.field
			var cur = {"map": f.map_id, "spawn": "default", "x": f.p_tile.x, "y": f.p_tile.y, "dir": f.p_dir}
			var dest: Dictionary = Rescue.swap(cur)
			await main.fade(true, 0.0 if skipping else 0.35)
			var pos = Vector2i(int(dest.get("x", -1)), int(dest.get("y", -1)))
			f.load_map(str(dest["map"]), str(dest.get("spawn", "default")), pos, str(dest.get("dir", "down")))
			f.update_leader()
			await main.fade(false, 0.0 if skipping else 0.35)
		"merge":
			Rescue.merge()
			main.field.update_leader()

func _interp(t: String) -> String:
	var i = t.find("{v:")
	while i >= 0:
		var j = t.find("}", i)
		var k = t.substr(i + 3, j - i - 3)
		t = t.substr(0, i) + str(Game.var_get(k)) + t.substr(j + 1)
		i = t.find("{v:")
	return t

func _teleport_path(id: String, path: Array) -> void:
	var f: Field = main.field
	var dv = Field.DV
	if id in ["player", "leader"]:
		var t = f.p_tile
		for d in path:
			t += dv[d]
			f.p_dir = d
		f.place_player(t.x, t.y, f.p_dir)
	else:
		var ac = f.actor(id)
		if ac.is_empty():
			return
		for d in path:
			ac["tile"] += dv[d]
			ac["dir"] = d
		ac["pos"] = Vector2(ac["tile"] * Field.TS)
		ac["target"] = ac["tile"]
		ac["moving"] = false

func handle_skip() -> void:
	if running:
		skipping = true
		main.dialogue.skip_all = true
