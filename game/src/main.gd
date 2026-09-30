extends Node
## Root orchestrator: title, field, battle, menus, story director, transitions and overlays.

signal _choice_made(idx: int)
signal _doc_closed
signal _menu_closed

var router: Router
var world: Node2D
var field: Field
var battle: Node = null
var ui: CanvasLayer
var overlay: CanvasLayer
var dialogue: DialogueBox
var director: Director
var fade_rect: ColorRect
var toast_box: Control
var title_screen: Control = null
var mode = "boot"
var toasts: Array = []
var _shake_t = 0.0
var _shake_amp = 0.0
var paused_overlay: Control
var last_battle_result = ""

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	randomize()
	router = Router.new()
	router.name = "Router"
	add_child(router)
	world = Node2D.new()
	world.name = "World"
	world.process_mode = Node.PROCESS_MODE_PAUSABLE
	world.scale = Vector2(UI.U, UI.U)
	add_child(world)
	field = Field.new()
	field.name = "Field"
	field.main = self
	world.add_child(field)
	field.visible = false
	field.request_battle.connect(_on_field_battle)
	field.request_scene.connect(_on_field_scene)
	field.request_menu.connect(_on_field_menu)
	ui = CanvasLayer.new()
	ui.layer = 10
	ui.scale = Vector2(UI.U, UI.U)
	add_child(ui)
	overlay = CanvasLayer.new()
	overlay.layer = 20
	overlay.scale = Vector2(UI.U, UI.U)
	add_child(overlay)
	dialogue = DialogueBox.new()
	ui.add_child(dialogue)
	dialogue.finished.connect(func(): router.pop(dialogue))
	director = Director.new()
	director.main = self
	add_child(director)
	toast_box = Control.new()
	toast_box.size = Vector2(320, 240)
	toast_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toast_box.draw.connect(_draw_toasts)
	ui.add_child(toast_box)
	fade_rect = ColorRect.new()
	fade_rect.color = Color(0, 0, 0, 0)
	fade_rect.size = Vector2(320, 240)
	fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	overlay.add_child(fade_rect)
	paused_overlay = Control.new()
	paused_overlay.size = Vector2(320, 240)
	paused_overlay.visible = false
	paused_overlay.draw.connect(func():
		paused_overlay.draw_rect(Rect2(0, 0, 320, 240), Color(0.02, 0.02, 0.08, 0.6))
		UI.win(paused_overlay, Rect2(116, 106, 88, 28))
		UI.text_center(paused_overlay, 160, 114, "Paused"))
	overlay.add_child(paused_overlay)
	Game.notify.connect(toast)
	get_window().min_size = Vector2i(640, 480)
	if Settings.get_v("fullscreen"):
		get_window().mode = Window.MODE_FULLSCREEN
	await get_tree().process_frame
	to_title()
	if QA.tests:
		QA.run_tests(self)
	elif QA.gallery != "":
		QA.run_gallery(self, QA.gallery)
	elif QA.route != "":
		QA.start(self)

func _process(delta: float) -> void:
	if Input.is_action_just_pressed("g_skip"):
		director.handle_skip()
	if not toasts.is_empty():
		toasts[0]["t"] -= delta
		if toasts[0]["t"] <= 0:
			toasts.pop_front()
		toast_box.queue_redraw()
	if _shake_t > 0:
		_shake_t -= delta
		world.position = Vector2(randi_range(-1, 1), randi_range(-1, 1)) * _shake_amp if _shake_t > 0 else Vector2.ZERO

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and Settings.get_v("pause_on_focus_loss") and mode in ["field", "battle"] and not QA.active:
		get_tree().paused = true
		paused_overlay.visible = true
		paused_overlay.queue_redraw()
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN and paused_overlay.visible:
		get_tree().paused = false
		paused_overlay.visible = false

# ======================================================================
# Title
# ======================================================================
func to_title() -> void:
	mode = "title"
	Game.playing = false
	field.visible = false
	field.active = false
	if battle != null:
		battle.queue_free()
		battle = null
	for ch in ui.get_children():
		if ch is GameMenu:
			ch.queue_free()
	if title_screen != null:
		title_screen.queue_free()
	title_screen = TitleScreen.new()
	title_screen.main = self
	ui.add_child(title_screen)
	router.stack.clear()
	router.push(title_screen)
	fade_rect.color.a = 0.0
	Audio.music("M001")

func start_new_game() -> void:
	await fade(true, 0.6)
	if title_screen:
		router.pop(title_screen)
		title_screen.queue_free()
		title_screen = null
	Game.new_game()
	enter_field(Game.S["location"]["map"], Game.S["location"]["spawn"])
	await fade(false, 0.6)
	if Content.data["scenes"].has("OPENING"):
		await director.run("OPENING")

func continue_from_state() -> void:
	if title_screen:
		router.pop(title_screen)
		title_screen.queue_free()
		title_screen = null
	var loc: Dictionary = Game.S["location"]
	enter_field(loc["map"], loc.get("spawn", "default"), Vector2i(int(loc.get("x", -1)), int(loc.get("y", -1))), loc.get("dir", "down"))
	await fade(false, 0.4)

func enter_field(map_id: String, spawn: String, pos: Vector2i = Vector2i(-1, -1), dir: String = "") -> void:
	mode = "field"
	field.visible = true
	field.active = true
	field.vehicle = "foot"
	field.load_map(map_id, spawn, pos, dir)
	router.stack.erase(field)
	router.stack.insert(0, field)
	var nm: String = field.map.get("name", "")
	if nm != "":
		field.show_banner(nm)

# ======================================================================
# Transitions
# ======================================================================
var _transitioning = false

func transition_to(dest: String, spawn: String, sfx: String = "") -> void:
	if _transitioning:
		return
	_transitioning = true
	field.busy = true
	if sfx != "":
		Audio.sfx(sfx)
	var prev_zone: String = field.map.get("zone", "")
	await fade(true, 0.18)
	field.load_map(Game.world_for_phase(dest), spawn)
	if field.map.get("zone", "") != prev_zone and field.map.get("name", "") != "":
		field.show_banner(field.map["name"])
	await fade(false, 0.18)
	field.busy = false
	_transitioning = false
	_check_auto_scenes()

func warp(map_id: String, spawn: String, dir: String = "") -> void:
	await fade(true, 0.0 if director.skipping else 0.25)
	field.load_map(map_id, spawn, Vector2i(-1, -1), dir)
	await fade(false, 0.0 if director.skipping else 0.25)

func _check_auto_scenes() -> void:
	# trigger entities with touch at spawn position (arrival scenes)
	for e in field.map["entities"]:
		if e["type"] == "trigger" and e.get("touch", true) and e["x1"] <= field.p_tile.x and field.p_tile.x <= e["x2"] and e["y1"] <= field.p_tile.y and field.p_tile.y <= e["y2"] and Game.eval_cond(e["cond"]):
			var sc = Content.scene(e["scene"])
			if sc.get("once", false) and Game.event_applied(e["scene"]):
				continue
			await director.run(e["scene"], {"trigger": true})
			return

# ======================================================================
# Overlays: dialogue, choices, docs, toasts, fades
# ======================================================================
func say(speaker: String, text: String, portrait: String = "", expr: String = "neutral") -> void:
	if director.skipping:
		return
	dialogue.say(speaker, text, portrait, expr)
	router.push(dialogue)
	await dialogue.finished

func show_text(speaker: String, text: String) -> void:
	field.busy = true
	await say(speaker, text)
	field.busy = false

func choose(options: Array) -> int:
	var m = MenuList.new()
	var items = []
	for o in options:
		items.append({"text": o})
	var w = 40
	for o in options:
		w = maxi(w, int(UI.width(o)) + 30)
	m.size = Vector2(mini(w, 300), 10 + options.size() * UI.LINE_H)
	m.position = Vector2(316 - m.size.x, 166 - m.size.y)
	m.allow_cancel = false
	m.setup(items, options.size())
	ui.add_child(m)
	router.push(m)
	var res = [-1]
	m.chosen.connect(func(i, _it): res[0] = i; emit_signal("_choice_made", i))
	await _choice_made
	router.pop(m)
	m.queue_free()
	return res[0]

func show_doc(title: String, text: String) -> void:
	if director.skipping:
		return
	var d = DocView.new()
	d.setup(title, text)
	ui.add_child(d)
	router.push(d)
	await d.closed
	router.pop(d)
	d.queue_free()

func toast(text: String) -> void:
	if text == "":
		return
	toasts.append({"text": text, "t": 2.4 + text.length() / 45.0})
	toast_box.queue_redraw()

func _draw_toasts() -> void:
	if toasts.is_empty():
		return
	var t: Dictionary = toasts[0]
	var lines: Array = UI.wrap(t["text"], 284.0)
	var w = 24.0
	for l in lines:
		w = maxf(w, UI.width(l) + 22)
	w = minf(312.0, w)
	var r = Rect2(Vector2(round((320 - w) / 2.0), 34), Vector2(w, 12 + 11 * lines.size()))
	UI.win(toast_box, r)
	for i in range(lines.size()):
		UI.text_center(toast_box, 160, r.position.y + 5 + 11 * i, lines[i])

func fade(out: bool, dur: float) -> void:
	var target = 1.0 if out else 0.0
	if dur <= 0.0:
		fade_rect.color.a = target
		return
	var tw = create_tween()
	tw.tween_property(fade_rect, "color:a", target, dur)
	await tw.finished

func wait(sec: float) -> void:
	await get_tree().create_timer(sec).timeout

func shake(sec: float) -> void:
	if not Settings.get_v("shake"):
		return
	_shake_t = sec
	_shake_amp = 2.0

func flash(col: Color) -> void:
	if Settings.get_v("reduced_flash"):
		col.a = 0.25
	fade_rect.color = Color(col.r, col.g, col.b, 0.8 if not Settings.get_v("reduced_flash") else 0.25)
	var tw = create_tween()
	tw.tween_property(fade_rect, "color:a", 0.0, 0.35)
	await tw.finished
	fade_rect.color = Color(0, 0, 0, 0)

func emote(actor_id: String, sym: String) -> void:
	var tile: Vector2i
	if actor_id in ["player", "leader"]:
		tile = field.p_tile
	else:
		var a = field.actor(actor_id)
		if a.is_empty():
			return
		tile = a["tile"]
	var pos = field.screen_pos_of(tile) + Vector2(6, -26)
	var lbl = Control.new()
	lbl.position = pos
	lbl.draw.connect(func():
		lbl.draw_rect(Rect2(-2, -1, 10, 11), Color8(250, 246, 230))
		lbl.draw_rect(Rect2(-2, -1, 10, 11), Color8(40, 30, 40), false)
		UI.text(lbl, Vector2(0, 0), sym, Color8(200, 40, 40), false))
	ui.add_child(lbl)
	get_tree().create_timer(0.8).timeout.connect(lbl.queue_free)

# ======================================================================
# Field events
# ======================================================================
func _on_field_scene(scene_id: String, ctx: Dictionary) -> void:
	await director.run(scene_id, ctx)

func _on_field_battle(form: String, opts: Dictionary) -> void:
	await run_battle(form, opts)

func _on_field_menu(kind: String, data: Dictionary) -> void:
	match kind:
		"main":
			await open_menu_async("main")
		"savepoint":
			Game.heal_all()
			Audio.sfx("FX022")
			await open_menu_async("savepoint")
		"shop":
			await open_shop(data["id"])
		"inn":
			if data.get("scene", "") != "":
				await director.run(data["scene"])
			else:
				await open_inn(-1)

func open_menu_async(kind: String, data: Dictionary = {}) -> void:
	field.busy = true
	var m = GameMenu.new()
	m.main = self
	ui.add_child(m)
	m.open(kind, data)
	await m.closed
	m.queue_free()
	field.busy = false
	field.update_leader()
	field.refresh_npcs()

func open_shop(id: String) -> void:
	await open_menu_async("shop", {"id": id})

func open_inn(price: int) -> void:
	await open_menu_async("inn", {"price": price})

# ======================================================================
# Battle
# ======================================================================
func run_battle(form_id: String, opts: Dictionary = {}) -> String:
	var fdef = Content.formation(form_id)
	if fdef.is_empty():
		push_error("Unknown formation " + form_id)
		return "victory"
	mode = "battle"
	field.busy = true
	field.active = false
	Game.make_checkpoint(form_id)
	var seed_value = Game.next_seed("combat")
	var prev_music = Audio.current_cue
	var result = ""
	while true:
		Audio.sfx("FX015")
		await flash(Color(1, 1, 1))
		await fade(true, 0.15)
		field.visible = false
		battle = BattleScene.new()
		battle.main = self
		world.add_child(battle)
		battle.setup(form_id, seed_value, opts)
		await fade(false, 0.2)
		result = await battle.finished
		if result == "victory":
			await battle.show_victory()
		await fade(true, 0.25)
		var model: BattleModel = battle.model
		battle.queue_free()
		battle = null
		if result == "victory":
			var msgs = Game.apply_battle_victory(model)
			field.visible = true
			await fade(false, 0.25)
			for m in msgs.slice(1):
				await say("", m)
			break
		elif result == "fled":
			Game.apply_battle_flee(model)
			field.visible = true
			await fade(false, 0.25)
			break
		else:
			# defeat: Retry from Checkpoint / Load Save
			var choice = await defeat_menu()
			if choice == 0:
				Game.restore_checkpoint()
				continue
			else:
				result = "defeat_load"
				Game.restore_checkpoint()
				field.visible = true
				await open_menu_async("load_after_defeat")
				await fade(false, 0.25)
				break
	if prev_music != "" and Audio.current_cue != prev_music and result != "defeat_load":
		Audio.music(prev_music)
	mode = "field"
	field.active = true
	field.busy = director.running
	field.enc_grace = 8
	last_battle_result = result
	return result

func defeat_menu() -> int:
	fade_rect.color.a = 0.0
	var bg = Control.new()
	bg.size = Vector2(320, 240)
	bg.draw.connect(func():
		bg.draw_rect(Rect2(0, 0, 320, 240), Color8(4, 2, 8))
		for i in range(10):
			bg.draw_rect(Rect2(0, 150 + i * 9, 320, 9), Color8(20 + i * 3, 4 + i, 10 + i, 255))
		UI.text_center(bg, 160, 70, "The party has fallen.", UI.C_RED)
		UI.win(bg, Rect2(24, 88, 272, 22))
		UI.text_center(bg, 160, 94, "Retry restores the checkpoint and its supplies.", UI.C_TEXT))
	ui.add_child(bg)
	Audio.music("silence")
	var idx = await choose(["Retry from Checkpoint", "Load Save"])
	bg.queue_free()
	return idx

func roll_credits() -> void:
	var c = CreditsView.new()
	ui.add_child(c)
	router.push(c)
	await c.closed
	router.pop(c)
	c.queue_free()

func clear_save() -> void:
	Game.S["clear"] = true
	await open_menu_async("clear_save")

func ending_menu() -> void:
	var idx = await choose(["Continue from Before the Final Descent", "Return to Title"])
	if idx == 0:
		# post-clear: the pre-finale snapshot plus clear and personal-quest flags (not a simulated post-ending world)
		var carry = {"quests": {}, "flags": {}, "epilogue": Game.S.get("epilogue", {}).duplicate(true)}
		for q in Game.S["quests"]:
			if Game.S["quests"][q].get("state", "") == "COMPLETED":
				carry["quests"][q] = Game.S["quests"][q].duplicate(true)
		for k in Game.S["flags"]:
			if k.begins_with("q") and k.ends_with("_done"):
				carry["flags"][k] = true
		var r = Game.load_from(Game.backup_path("pre_finale"))
		if r.get("ok", false):
			Game.S["clear"] = true
			Game.S["flags"]["post_clear"] = true
			for q in carry["quests"]:
				Game.S["quests"][q] = carry["quests"][q]
			for k in carry["flags"]:
				Game.S["flags"][k] = true
			Game.S["epilogue"] = carry["epilogue"]
			continue_from_state()
			return
		await say("", "The pre-finale backup could not be read. Returning to the title.", "")
	to_title()
