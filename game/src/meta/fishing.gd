class_name FishingGame
extends Control
## Fishing minigame overlay (sys s4). Opened by main when the player uses a fishing spot (`fish x y table=` map entity).
## The field stays visible: the lead hero faces the water, a rod line runs to a bobber from the Mana Seed Fishing Gear
## pack (assets/ext/fishing/, installed by tools/art/fishing_install.py; drawn fallbacks otherwise). A hero-specific
## pose sheet can be dropped in later as assets/ext/heroes/<cid>/fish.png (4 rows: down, left, right, up; square
## frames, height/4 px each, drawn at native resolution); while it exists the field sprite is hidden and the sheet is
## drawn instead.
## Rules: FishCore. Records, rewards and the Saltwhistle Open: record_catch().

signal done

const WATER := ["water", "shallow", "deep", "pool", "reef", "puddle"]
const HAND := {"down": Vector2(12, 9), "up": Vector2(4, 3), "left": Vector2(2, 8), "right": Vector2(14, 8)}

var main: Node
var spot: Dictionary = {}
var core: FishCore
var result_msgs: Array = []
var phase = "play"          # play | result
var menu_idx = 0
var water_tile = Vector2i.ZERO
var dirv = Vector2i(0, 1)
var tt = 0.0
var _reel_on = false
var _prev_hold = false
var pose_tex: Texture2D = null

static var _tex = {}

static func tex(name: String) -> Texture2D:
	if not _tex.has(name):
		var p = "res://assets/ext/fishing/%s.png" % name
		_tex[name] = load(p) if ResourceLoader.exists(p) else null
	return _tex[name]

func setup(p_main: Node, p_spot: Dictionary) -> void:
	main = p_main
	spot = p_spot
	size = Vector2(320, 240)
	var f: Field = main.field
	dirv = Field.DV[f.p_dir]
	water_tile = f.p_tile + dirv
	var cid: String = f.p_sprite
	var pp = "res://assets/ext/heroes/%s/fish.png" % cid
	pose_tex = load(pp) if ResourceLoader.exists(pp) else null
	if pose_tex != null:
		f.hidden_actors["player"] = true
	_new_cast()

func _new_cast() -> void:
	core = FishCore.new()
	var assist = Game.difficulty() == "easy" or bool(Settings.get_v("fish_assist"))
	core.start(str(spot.get("table", "river")), Game.next_seed("loot"), Field.is_night(), assist)
	phase = "play"
	result_msgs = []
	_reel_on = false
	tt = 0.0

func handle(ev: String) -> void:
	if phase == "result":
		match ev:
			"up", "down":
				menu_idx = 1 - menu_idx
				Audio.ui("FX001")
			"confirm":
				Audio.ui("FX002")
				if menu_idx == 0:
					_new_cast()
				else:
					_finish()
			"cancel":
				_finish()
		return
	if ev == "cancel":
		Audio.ui("FX003")
		_finish()

func _finish() -> void:
	if is_instance_valid(main) and main.field.hidden_actors.has("player"):
		main.field.hidden_actors.erase("player")
	emit_signal("done")

func _process(delta: float) -> void:
	tt += delta
	queue_redraw()
	if phase != "play":
		return
	var raw_hold = Input.is_action_pressed("g_confirm")
	var pressed = Input.is_action_just_pressed("g_confirm")
	var hold = raw_hold
	# accessibility: "reel_toggle" turns reeling into press-to-start / press-to-stop
	if core.state == "reel" and Settings.get_v("reel_toggle"):
		if pressed:
			_reel_on = not _reel_on
		hold = _reel_on
		pressed = false
	var before = core.state
	core.step(delta, hold, pressed)
	if before != core.state:
		match core.state:
			"wait":
				Audio.sfx("FX013")
				if Settings.get_v("captions"):
					Audio.emit_signal("caption", T.s("cc.splash"))
			"bite":
				Audio.sfx("FX023")
				if Settings.get_v("captions"):
					Audio.emit_signal("caption", T.s("cc.bite"))
				if Settings.get_v("shake"):
					main.shake(0.15)
			"caught":
				Audio.sfx("FX007")
				result_msgs = record_catch(core.fish, core.size, core.weight, str(main.field.map.get("zone", "")))
				phase = "result"
				menu_idx = 0
			"lost":
				Audio.sfx("FX004")
				result_msgs = [T.s({"too_early": "fish.too_early", "snapped": "fish.snapped", "nothing": "fish.nothing"}.get(core.reason, "fish.escaped"))]
				phase = "result"
				menu_idx = 0
	if core.state == "reel" and hold and int(tt * 8) % 3 == 0 and not _prev_hold:
		Audio.sfx("FX001", "SFX")
	_prev_hold = hold and int(tt * 8) % 3 == 0

## Logs a catch: fish log (count, best size and weight), counters, reward item and crowns, and the Saltwhistle Open
## placing (sets fishing_entered and fishing_rank1/2/3 for a new best placing while the tournament is open at N14).
## Returns the result lines.
static func record_catch(f: Dictionary, size_cm: float, kg: float, zone: String) -> Array:
	var msgs = []
	if f.is_empty():
		return msgs
	if not Game.S.has("fish") or typeof(Game.S["fish"]) != TYPE_DICTIONARY:
		Game.S["fish"] = {}
	var fl: Dictionary = Game.S["fish"]
	if not fl.has("log"):
		fl["log"] = {}
	var fid: String = f["id"]
	var is_fish = fid.begins_with("F")
	var line = "%s" % f["name"]
	if is_fish:
		line += "  %.1f cm, %.2f kg" % [size_cm, kg]
	msgs.append(line)
	if is_fish:
		var e: Dictionary = fl["log"].get(fid, {"n": 0, "best": 0.0, "kg": 0.0})
		var first = int(e["n"]) == 0
		e["n"] = int(e["n"]) + 1
		if size_cm > float(e["best"]):
			if not first:
				msgs.append(T.s("fish.record"))
			e["best"] = size_cm
			e["kg"] = kg
		fl["log"][fid] = e
		if first:
			msgs.append(T.s("fish.new"))
		Game.stat_add("fish_caught")
		if int(f.get("rarity", 1)) >= 3:
			Game.stat_add("fish_rare")
		if bool(f.get("night", false)):
			Game.stat_add("fish_night")
	var rw: String = str(f.get("reward", ""))
	var val = int(f.get("value", 0))
	var nrw = 2 if int(f.get("rarity", 1)) >= 4 else 1
	if rw != "":
		Game.add_item(rw, nrw)
	if val > 0:
		Game.add_gold(val)
	if rw != "":
		msgs.append(T.f("fish.reward", [Content.item_name(rw) + (" x%d" % nrw if nrw > 1 else ""), val]))
	if is_fish and Game.flag("fishing_tournament_open") and zone == str(FishCore.data().get("tourney", {}).get("map_zone", "N14")):
		Game.set_flag("fishing_entered")
		Game.stat_add("tourney_entries")
		fl["tourney_best"] = maxf(float(fl.get("tourney_best", 0.0)), kg)
		var rank = FishCore.tourney_rank(kg)
		var best = int(fl.get("tourney_rank", 0))
		if rank > 0 and (best == 0 or rank < best):
			fl["tourney_rank"] = rank
			Game.set_flag("fishing_rank%d" % rank)
			msgs.append(T.f("fish.tourney", ["%.2f kg" % kg, T.s("fish.place.%d" % rank)]))
		else:
			msgs.append(T.s("fish.tourney_rank.%d" % rank))
	Game.emit_signal("state_changed")
	return msgs

# ---------------------------------------------------------------- drawing
## Field marker for a fishing spot: the pack's school-of-fish ripples on the water cell (drawn ripples otherwise).
static func draw_spot(ci: CanvasItem, pos: Vector2, time: float) -> void:
	var t = tex("school_summer")
	if t != null:
		var fr = int(time * 5.0) % 4
		ci.draw_texture_rect_region(t, Rect2(pos + Vector2(-8, -8), Vector2(32, 32)), Rect2(fr * 32, 0, 32, 32), Color(1, 1, 1, 0.85))
		return
	var r = 3.0 + fmod(time * 4.0, 5.0)
	ci.draw_arc(pos + Vector2(8, 9), r, 0, TAU, 16, Color(1, 1, 1, 0.5 - r / 20.0), 1.0)
	ci.draw_rect(Rect2(pos + Vector2(6, 8), Vector2(4, 1)), Color(0.1, 0.1, 0.2, 0.6))

func _bobber_pos() -> Vector2:
	var f: Field = main.field
	var far = 1 + int(round(core.power * 2.0))
	var tile = water_tile
	for i in range(far):
		var nt = f.p_tile + dirv * (i + 1)
		if WATER.has(f.kind_at(nt.x, nt.y)):
			tile = nt
	var p = f.screen_pos_of(tile) + Vector2(8, 9)
	if core.state == "reel":
		# the bobber comes in with the line
		var hand = f.screen_pos_of(f.p_tile) + HAND.get(f.p_dir, Vector2(8, 8))
		p = hand.lerp(p, clampf(core.line / maxf(0.3, 0.35 + core.power * 0.55), 0.0, 1.0))
		p += Vector2(sin(tt * 18.0), cos(tt * 15.0)) * (1.5 if core.running else 0.4)
	return p

func _draw() -> void:
	var f: Field = main.field
	var me = f.screen_pos_of(f.p_tile)
	if pose_tex != null:
		var fh = pose_tex.get_height() / 4
		var nfr = maxi(1, pose_tex.get_width() / maxi(1, fh))
		var row = {"down": 0, "left": 1, "right": 2, "up": 3}.get(f.p_dir, 0)
		var fr = int(tt * 6.0) % nfr
		UI.native_begin(self, me + Vector2(8, 16) - Vector2(fh, fh) / (2.0 * UI.U) - Vector2(0, fh / (2.0 * UI.U)))
		draw_texture_rect_region(pose_tex, Rect2(0, 0, fh, fh), Rect2(fr * fh, row * fh, fh, fh))
		UI.native_end(self)
	var hand = me + HAND.get(f.p_dir, Vector2(8, 8))
	var s = core.state
	var cast_out = s in ["wait", "bite", "reel"] or (phase == "result" and core.state == "caught")
	# rod: a short stave from the hand, bending with tension
	var rod_dir = Vector2(dirv) * 0.8 + Vector2(0, -0.6)
	if s == "cast":
		rod_dir = Vector2(dirv) * (0.2 + core.power * 0.4) + Vector2(0, -1.0)
	var bend = core.tension * 3.0 if s == "reel" else 0.0
	var tip = hand + rod_dir.normalized() * 11.0 + Vector2(dirv) * bend * 0.5 + Vector2(0, bend)
	draw_line(hand, tip, Color8(92, 58, 30), 1.4)
	draw_line(hand, hand + (tip - hand) * 0.35, Color8(40, 28, 20), 1.8)
	if cast_out and phase == "play":
		var bp = _bobber_pos()
		var sag = (1.0 - core.tension) * 6.0 if s == "reel" else 7.0
		var mid = (tip + bp) / 2.0 + Vector2(0, sag)
		var pts = PackedVector2Array()
		for i in range(9):
			var u = i / 8.0
			pts.append(tip.lerp(mid, u).lerp(mid.lerp(bp, u), u))
		var lc = Color8(230, 230, 240, 200) if core.tension < 0.75 or s != "reel" else Color8(255, 150, 120, 230)
		draw_polyline(pts, lc, 0.6)
		var bt = tex("bobber")
		var dip = 2.0 if s == "bite" else (1.0 if core.nibbling() else 0.0)
		if bt != null:
			var fr = int(tt * 6.0) % 4
			draw_texture_rect_region(bt, Rect2(bp + Vector2(-16, -18 + dip), Vector2(32, 32)), Rect2(fr * 32, 0, 32, 32))
		else:
			draw_circle(bp + Vector2(0, dip), 2.5, Color8(220, 50, 40))
			draw_rect(Rect2(bp + Vector2(-2.5, dip), Vector2(5, 1.5)), Color8(250, 250, 250))
			draw_arc(bp + Vector2(0, 2), 4.0 + fmod(tt * 3.0, 3.0), 0, TAU, 14, Color(1, 1, 1, 0.4), 1.0)
		if s == "bite":
			UI.text(self, bp + Vector2(-2, -22), "!", UI.C_RED)
	_draw_hud()

## The panel sits at the bottom, or at the top when the angler stands in the lower part of the view.
func _hud_y() -> float:
	var f: Field = main.field
	return 4.0 if f.screen_pos_of(f.p_tile).y > 130.0 else 180.0

func _draw_hud() -> void:
	var y0 = _hud_y()
	var r = Rect2(4, y0, 312, 56)
	UI.win(self, r)
	var s = core.state
	if phase == "result":
		_draw_result(y0)
		return
	var prompt = {"cast": "fish.prompt_cast", "wait": "fish.prompt_wait", "bite": "fish.prompt_bite", "reel": "fish.prompt_reel"}.get(s, "")
	var gx = 11.0
	gx += Glyphs.draw(self, Vector2(gx, y0 + 5), "confirm") + 2
	UI.text(self, Vector2(gx, y0 + 5), T.s(prompt), UI.C_HI if s == "bite" else UI.C_TEXT)
	match s:
		"cast":
			UI.label(self, Vector2(11, y0 + 19), T.s("fish.line"))
			UI.gauge(self, Rect2(70, y0 + 21, 170, 7), core.power, UI.C_GOLD)
		"wait", "bite":
			UI.text(self, Vector2(11, y0 + 19), _where(), UI.C_DIM)
		"reel":
			UI.label(self, Vector2(11, y0 + 17), T.s("fish.tension"))
			var tr = Rect2(70, y0 + 19, 170, 7)
			UI.gauge(self, tr, core.tension, UI.C_GREEN if core.tension < 0.6 else (UI.C_HI if core.tension < 0.85 else UI.C_RED))
			# danger zone mark (a notch, not colour alone)
			draw_rect(Rect2(tr.position.x + tr.size.x * 0.85, tr.position.y - 2, 1, tr.size.y + 4), UI.C_TEXT)
			UI.text(self, Vector2(246, y0 + 17), "!!" if core.tension >= 0.85 else ("!" if core.running else ""), UI.C_RED)
			UI.label(self, Vector2(11, y0 + 29), T.s("fish.line"))
			UI.gauge(self, Rect2(70, y0 + 31, 170, 7), 1.0 - clampf(core.line / 1.25, 0.0, 1.0), UI.C_BLUE)
	Glyphs.hints(self, Vector2(11, y0 + 42), [["cancel", T.s("fish.quit")]])

func _where() -> String:
	var n = str(main.field.map.get("name", ""))
	return n + ("  -  " + T.s("fish.night") if Field.is_night() else "")

func _draw_result(y0: float) -> void:
	var f: Dictionary = core.fish if core.state == "caught" else {}
	var x = 11.0
	if not f.is_empty():
		draw_icon(self, Vector2(10, y0 + 8), int(f.get("icon", 0)), 2.0)
		x = 48.0
	var y = y0 + 5
	var lines = []
	if not result_msgs.is_empty():
		lines.append([result_msgs[0], UI.C_GOLD if not f.is_empty() else UI.C_TEXT])
		for ln in UI.wrap(" ".join(result_msgs.slice(1)), 236 - x):
			lines.append([ln, UI.C_TEXT])
	for i in range(mini(4, lines.size())):
		UI.text(self, Vector2(x, y), lines[i][0], lines[i][1])
		y += 11
	var ox = 250.0
	for i in range(2):
		var lab = T.s("fish.again") if i == 0 else T.s("fish.stop")
		if i == menu_idx:
			UI.cursor(self, Vector2(ox - 8, y0 + 16 + i * 11))
		UI.text(self, Vector2(ox, y0 + 16 + i * 11), lab)

## Pack icon cell n (16x16 cells, 8 per row) at `scale` units per pixel; a lettered tile when the pack is missing.
static func draw_icon(ci: CanvasItem, pos: Vector2, n: int, scale: float = 1.0) -> void:
	var t = tex("icons")
	if t != null:
		ci.draw_texture_rect_region(t, Rect2(pos, Vector2(16, 16) * scale), Rect2((n % 8) * 16, (n / 8) * 16, 16, 16))
	else:
		ci.draw_rect(Rect2(pos, Vector2(16, 16) * scale), Color8(40, 70, 110))
		UI.text(ci, pos + Vector2(4, 3) * scale, "F", UI.C_TEXT)
