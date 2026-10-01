class_name GameMenu
extends Control
## In-game menus. Every change goes through Game services; this node owns no progression state.

signal closed

var main: Node
var kind = "main"
var data = {}
var lists: Array = []       # stack of MenuList
var page = ""
var info_draw: Callable = Callable()
var sel_member = ""
var sel_slot = ""
var preview_item = ""
var msg = ""
var msg_t = 0.0
var swap_from = -1
var shop_mode = "buy"
var rebinding = ""
var confirm_cb: Callable = Callable()
var split_teams = {"A": [], "B": []}

const MAIN_ITEMS := ["Items", "Equipment", "Abilities", "Formation", "Vestiges", "Journal", "World Map", "Bestiary", "Records", "Settings", "Save", "Quit", "Close"]

func _ready() -> void:
	size = Vector2(320, 240)

func open(p_kind: String, p_data: Dictionary = {}) -> void:
	kind = p_kind
	data = p_data
	main.router.push(self)
	match kind:
		"main": _main_menu()
		"savepoint": _save_menu(true)
		"load", "load_after_defeat": _load_menu()
		"settings": _settings_menu()
		"shop": _shop_menu()
		"inn": _inn_menu()
		"craft": _craft_menu(str(data.get("id", "")))
		"formation": _formation_menu()
		"split": _split_menu()
		"clear_save": _clear_save_menu()
		_: _main_menu()

func _close_all() -> void:
	for l in lists:
		main.router.pop(l)
		l.queue_free()
	lists.clear()
	main.router.pop(self)
	emit_signal("closed")

func handle(ev: String) -> void:
	if rebinding != "":
		return
	if not lists.is_empty():
		lists[-1].handle(ev)

func _push(m: MenuList) -> MenuList:
	add_child(m)
	lists.append(m)
	main.router.push(m)
	m.cancelled.connect(_pop_list)
	return m

func _pop_list() -> void:
	if lists.is_empty():
		return
	var m: MenuList = lists.pop_back()
	main.router.pop(m)
	m.queue_free()
	if lists.is_empty():
		_close_all()
	else:
		lists[-1].active = true
		_refresh_top()

func _refresh_top() -> void:
	if lists.is_empty():
		return
	var top: MenuList = lists[-1]
	if top.has_meta("refresh"):
		var cb: Callable = top.get_meta("refresh")
		cb.call(top)

func _menu(items: Array, rect: Rect2, rows: int, title: String = "") -> MenuList:
	var m = MenuList.new()
	m.position = rect.position
	m.size = rect.size
	m.setup(items, rows, title)
	if not lists.is_empty():
		lists[-1].active = false
	return _push(m)

func flash_msg(t: String) -> void:
	msg = t
	msg_t = 2.0

func _process(d: float) -> void:
	if msg_t > 0:
		msg_t -= d
	# the command column belongs to the main screen; sub-screens take the whole view
	for l in lists:
		if l.memory_key == "main_menu":
			l.visible = page == "main" or page == "pick"
	queue_redraw()

# ======================================================================
# Main
# ======================================================================
func _main_menu() -> void:
	page = "main"
	var items = []
	var can_save: bool = main.field.map.get("save_ok", false) or main.field.vehicle == "ship"
	for n in MAIN_ITEMS:
		var it = {"text": T.s("menu." + n, n), "value": n}
		if n == "Save" and not can_save:
			it["enabled"] = false
			it["reason"] = T.s("menu.save_where")
		if n == "Vestiges" and Game.S.get("vestiges", []).is_empty():
			it["enabled"] = false
			it["reason"] = T.s("menu.no_vestiges")
		if n == "Formation" and Game.S["party"].get("locked", false):
			it["enabled"] = false
			it["reason"] = T.s("menu.formation_locked")
		items.append(it)
		if n == "Formation" and Rescue.bound_active():
			var sw = {"text": T.s("menu.Switch", "Switch"), "value": "Switch"}
			var ok_here = (main.field.map.get("save_ok", false) or main.field.map.get("kind", "") == "world") and main.field.vehicle in ["", "foot"]
			if not ok_here:
				sw["enabled"] = false
				sw["reason"] = T.s("menu.switch_where", "Switch parties at a save point or on foot on the world map.")
			items.append(sw)
	var m = _menu(items, Rect2(232, 4, 84, 153), 13)
	m.memory_key = "main_menu"
	m.chosen.connect(_on_main_choice)
	m.set_meta("refresh", func(_m): page = "main"; info_draw = Callable())
	info_draw = Callable()

func _on_main_choice(_i: int, it: Dictionary) -> void:
	match it["value"]:
		"Items": _items_menu()
		"Equipment": _pick_member(func(cid): _equip_menu(cid), T.s("gm.equip_whom", "Equip whom?"))
		"Abilities": _pick_member(func(cid): _abilities_menu(cid), T.s("gm.whose_techniques", "Whose techniques?"))
		"Formation": _formation_menu()
		"Switch":
			_close_all()
			main.call_deferred("run_bound_swap")
		"Vestiges": _vestige_menu()
		"Journal": _journal()
		"World Map": _worldmap()
		"Bestiary": _bestiary()
		"Records": _records_menu()
		"Settings": _settings_menu()
		"Save": _save_menu(false)
		"Quit": _confirm(T.s("menu.quit_confirm"), func():
			_close_all()
			main.to_title())
		"Close": _close_all()

func _draw() -> void:
	draw_rect(Rect2(0, 0, 320, 240), Color(0.02, 0.02, 0.08, 0.45))
	if page == "main" or page == "pick":
		_draw_party_panel(Rect2(4, 4, 224, 196))
		# time / money box under the command column
		UI.win(self, Rect2(232, 160, 84, 40))
		UI.label(self, Vector2(239, 164), T.s("menu.time"))
		UI.text_right(self, 309, 173, Game.fmt_time(Game.S.get("playtime", 0.0)))
		UI.label(self, Vector2(239, 182), T.s("menu.crowns"))
		UI.text_right(self, 309, 188, str(Game.gold()))
		# location strip
		UI.win(self, Rect2(4, 204, 312, 32))
		UI.text(self, Vector2(11, 208), main.field.map.get("name", ""))
		UI.text(self, Vector2(11, 220), Game.current_chapter(), UI.C_LABEL)
	if info_draw.is_valid():
		info_draw.call()
	if msg_t > 0 and msg != "":
		var w = UI.width(msg) + 20
		UI.win(self, Rect2(round((320 - w) / 2.0), 106, w, 22))
		UI.text_center(self, 160, 111, msg, UI.C_TEXT)

func _draw_party_panel(r: Rect2) -> void:
	UI.win(self, r)
	var y = r.position.y + 6
	var act = Game.active()
	for cid in act:
		_draw_member_line(cid, Vector2(r.position.x + 6, y), true)
		y += 34
	var res = Game.S["party"]["roster"].filter(func(c): return not act.has(c))
	if not res.is_empty():
		UI.label(self, Vector2(r.position.x + 9, y), T.s("gm.reserve_away", "Reserve / away"))
		y += 11
		var x = r.position.x + 13
		for cid in res:
			var st = "" if Game.is_available(cid) else " (away)"
			UI.text(self, Vector2(x, y), Game.short_name(cid) + st, UI.C_TEXT if Game.is_available(cid) else UI.C_DIM)
			y += 10
			if y > r.end.y - 12:
				x += 100
				y = r.end.y - 32

func _draw_member_line(cid: String, p: Vector2, full: bool) -> void:
	var m = Game.member(cid)
	var s = Game.stats(cid)
	var back = Game.row(cid) == "back"
	var t: Texture2D = null if HeroArt.has_field(cid) else main.field.sprite_tex(cid)
	if HeroArt.has_field(cid):
		HeroArt.draw_field(self, cid, "down", false, p + Vector2(13 + (4 if back else 0), 31))
	if t:
		var cw = t.get_width() / 6
		var chh = t.get_height() / 5
		# back-row members stand a little to the right, as in the classic party screen
		draw_texture_rect_region(t, Rect2(p + Vector2(12 - cw / 2 + (4 if back else 0), 30 - chh), Vector2(cw, chh)), Rect2(0, 0, cw, chh))
	var hp = int(m["hp"]) if int(m["hp"]) >= 0 else s["mhp"]
	var mp = int(m["mp"]) if int(m["mp"]) >= 0 else s["mmp"]
	var x = p.x + 32
	UI.text(self, Vector2(x, p.y), Game.char_name(cid))
	UI.label(self, Vector2(p.x + 134, p.y), T.s("gm.lv", "LV"))
	UI.text_right(self, p.x + 162, p.y, str(m["level"]))
	UI.text(self, Vector2(p.x + 170, p.y), "[" + Game.row(cid).substr(0, 1).to_upper() + "]", UI.C_DIM)
	var hpc = UI.C_TEXT if hp > s["mhp"] / 4 else (UI.C_HI if hp > 0 else UI.C_RED)
	UI.label(self, Vector2(x, p.y + 11), T.s("gm.hp", "HP"))
	UI.text_right(self, p.x + 122, p.y + 11, "%d/%d" % [hp, s["mhp"]], hpc)
	UI.label(self, Vector2(x, p.y + 21), T.s("gm.mp", "MP"))
	UI.text_right(self, p.x + 122, p.y + 21, "%d/%d" % [mp, s["mmp"]])
	var need = F.xp_total_for_level(int(m["level"]) + 1) - int(m["xp"])
	UI.label(self, Vector2(p.x + 134, p.y + 11), T.s("gm.next", "Next"))
	UI.text_right(self, p.x + 210, p.y + 11, str(maxi(0, need)))
	var link = Game.link_of(cid)
	if link != "":
		UI.text(self, Vector2(p.x + 134, p.y + 21), Content.data["vestiges"][link]["name"], Color8(240, 170, 230))

func _pick_member(cb: Callable, title: String, only_available: bool = true) -> void:
	var items = []
	for cid in Game.S["party"]["roster"]:
		var ok = Game.is_available(cid) or not only_available
		items.append({"text": Game.char_name(cid), "value": cid, "enabled": ok, "reason": T.s("gm.away_from_the_party", "Away from the party")})
	var m = _menu(items, Rect2(232, 150, 84, 56), 4, "")
	m.chosen.connect(func(_i, it): cb.call(it["value"]))

# ======================================================================
# Items
# ======================================================================
func _items_menu() -> void:
	page = "items"
	var m = _menu([], Rect2(4, 42, 200, 194), 15, "Items")
	var refresh = func(mm: MenuList):
		var items = []
		var ids: Array = Game.S["inventory"]["items"].keys()
		ids.sort_custom(func(a, b):
			var ka: String = Content.item(a).get("kind", "")
			var kb: String = Content.item(b).get("kind", "")
			if ka == kb:
				return a < b
			return ["consumable", "weapon", "armor", "accessory", "material", "key"].find(ka) < ["consumable", "weapon", "armor", "accessory", "material", "key"].find(kb))
		for iid in ids:
			var it = Content.item(iid)
			var usable: bool = it.get("kind", "") == "consumable" and it.get("field", false)
			items.append({"icon": iid, "text": Content.item_name(iid), "right": str(Game.count(iid)), "value": iid, "enabled": true, "color": UI.C_TEXT if usable or it["kind"] != "consumable" else UI.C_DIM})
		var dl: Array = Game.S["inventory"]["delivery"]
		if not dl.is_empty():
			items.append({"text": "Delivery chest (%d)" % dl.size(), "value": "__delivery"})
		mm.items = items
		mm.index = clampi(mm.index, 0, maxi(0, items.size() - 1))
		page = "items"
		info_draw = func(): _item_info(mm)
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		if it["value"] == "__delivery":
			var got = Game.claim_delivery()
			flash_msg(T.s("gm.claimed_d_item_s", "Claimed %d item(s).") % got.size())
			refresh.call(m)
			return
		var itd = Content.item(it["value"])
		if itd.get("kind", "") == "consumable" and itd.get("field", false):
			_use_item_field(it["value"], func(): refresh.call(m))
		else:
			Audio.ui("FX004"))

func _item_info(m: MenuList) -> void:
	# description strip on top, details on the right (classic item screen)
	UI.win(self, Rect2(4, 4, 312, 34))
	UI.win(self, Rect2(208, 42, 108, 194))
	var it = m.current()
	if it.is_empty():
		return
	if it.get("value", "") == "__delivery":
		UI.text(self, Vector2(11, 9), T.s("gm.items_sent_on_by_couriers", "Items sent on by couriers. Confirm to claim."))
		return
	var d = Content.item(it.get("value", ""))
	var dl = UI.wrap(d.get("desc", ""), 296)
	for i in range(mini(2, dl.size())):
		UI.text(self, Vector2(11, 9 + i * 11), dl[i])
	var y = 47
	UI.icon(self, Vector2(284, 46), it.get("value", ""), 24)
	UI.label(self, Vector2(215, y), d.get("kind", "").capitalize())
	y += 12
	UI.label(self, Vector2(215, y), T.s("gm.owned", "Owned"))
	UI.text_right(self, 308, y, str(Game.count(it.get("value", ""))))
	y += 11
	if d.get("kind", "") in ["weapon", "armor"]:
		y += 4
		if d.has("atk"):
			UI.stat(self, Vector2(215, y), T.s("gm.atk", "ATK"), str(int(d["atk"])), 250)
			UI.stat(self, Vector2(258, y), T.s("gm.mag", "MAG"), str(int(d["mag"])), 308)
			y += 11
		if d.has("def"):
			UI.stat(self, Vector2(215, y), T.s("gm.def", "DEF"), str(int(d["def"])), 250)
			UI.stat(self, Vector2(258, y), T.s("gm.res", "RES"), str(int(d["res"])), 308)
			y += 11
	if dl.size() > 2:
		y += 4
		for ln in UI.wrap(" ".join(dl.slice(2)), 94).slice(0, 6):
			UI.text(self, Vector2(215, y), ln, UI.C_DIM)
			y += 11
	if d.get("kind", "") == "consumable" and not d.get("field", false):
		UI.text(self, Vector2(215, 220), T.s("gm.battle_only", "Battle only"), UI.C_DIM)
	elif d.get("kind", "") == "consumable":
		UI.text(self, Vector2(215, 220), T.s("gm.usable_now", "Usable now"), UI.C_GREEN)

func _use_item_field(iid: String, done: Callable) -> void:
	var d = Content.item(iid)
	if d.get("special", "") == "tent":
		if not (main.field.map.get("save_ok", false) or main.field.map.get("kind", "") == "world"):
			flash_msg(T.s("gm.use_a_travel_tent_at", "Use a Travel Tent at a lamp or on the world map."))
			return
		Game.remove_item(iid)
		Game.heal_all()
		Audio.sfx("FX022")
		flash_msg(T.s("gm.the_party_rests", "The party rests."))
		done.call()
		return
	if d.get("special", "") == "warp":
		# Wayfarer's Sigil (field systems s3): the waystone roads from anywhere outside battle and dungeons
		if main.director.running or not FieldSys.warp_allowed(main.field, true):
			flash_msg("The sigil stays dark here. Use it in the open or in a town.")
			return
		_close_all()
		main.director.run("WAYSTONE_SIGIL")
	if d.get("special", "") == "save_lantern":
		# Waylamp (sys s4): the save ledger anywhere outside battle, scenes and boss rooms; consumed on use
		if not main.can_use_save_lantern():
			flash_msg(T.s("save.lantern_no"))
			return
		_save_menu(false, iid)
		return
	if d.get("special", "") == "waystone":
		var dg: String = String(main.field.map_id).substr(0, 3)
		if not Content.data["dungeons"].has(dg) or main.director.running:
			flash_msg(T.s("gm.waystones_work_only_inside_a", "Waystones work only inside a dungeon."))
			return
		Game.remove_item(iid)
		_close_all()
		main.transition_to(Content.data["dungeons"][dg]["rooms"][0], "default")
		return
	var targets_all: bool = d.get("target", "") == "ally_all"
	_pick_member(func(cid):
		if Game.count(iid) <= 0:
			return
		var r = _apply_field_ops(d.get("ops", []), targets_all, cid, 0, 0)
		if r:
			Game.remove_item(iid)
			Audio.sfx("FX022")
			done.call()
			_pop_list()
		else:
			flash_msg(T.s("gm.it_would_have_no_effect", "It would have no effect.")), T.s("gm.use_on_whom", "Use on whom?"))

func _apply_field_ops(ops: Array, all: bool, cid: String, mag: int, level: int) -> bool:
	var targets = Game.available_members() if all else [cid]
	var any = false
	for c in targets:
		var m = Game.member(c)
		var s = Game.stats(c)
		for op in ops:
			match op["op"]:
				"heal":
					if int(m["hp"]) <= 0:
						continue
					var amt = int(op["flat"]) if op.has("flat") else F.heal_amount(mag, level, float(op.get("power", 100)), s["mhp"])
					if int(m["hp"]) < s["mhp"]:
						m["hp"] = mini(s["mhp"], int(m["hp"]) + amt)
						any = true
				"mp":
					if int(m["mp"]) < s["mmp"]:
						m["mp"] = mini(s["mmp"], int(m["mp"]) + int(op["amount"]))
						any = true
				"revive":
					if int(m["hp"]) <= 0:
						m["hp"] = maxi(1, int(s["mhp"] * float(op.get("pct", 0.25))))
						any = true
				"full_restore":
					if int(m["hp"]) > 0:
						m["hp"] = s["mhp"]
						m["mp"] = s["mmp"]
						any = true
	return any

# ======================================================================
# Equipment (preview all derived stats before confirming)
# ======================================================================
const SLOTS := ["weapon", "offhand", "head", "body", "acc1", "acc2"]

func _equip_menu(cid: String) -> void:
	sel_member = cid
	page = "equip"
	var m = _menu([], Rect2(4, 4, 168, 98), 7, Game.char_name(cid))
	var refresh = func(mm: MenuList):
		var items = []
		var eq: Dictionary = Game.member(cid)["equip"]
		for s in SLOTS:
			var iid = eq.get(s, "")
			var nm: String = Content.item_name(iid) if iid != "" else "-"
			var en = true
			var reason = ""
			if s == "offhand" and eq.get("weapon", "") != "" and Content.item(eq["weapon"]).get("two_handed", false):
				en = false
				reason = T.s("gm.two_handed_weapon", "Two-handed weapon")
			items.append({"text": "%s: %s" % [s.capitalize().replace("Acc", "Acc "), nm], "value": s, "enabled": en, "reason": reason})
		items.append({"text": "Optimize", "value": "optimize"})
		mm.items = items
		page = "equip"
		preview_item = ""
		info_draw = func(): _equip_info(cid, mm)
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		if it["value"] == "optimize":
			var n = Game.optimize_equipment(cid)
			Audio.sfx("FX006" if n > 0 else "FX004")
			flash_msg(T.s("gm.equipped_d_stronger_item_s", "Equipped %d stronger item%s.") % [n, "" if n == 1 else "s"] if n > 0 else "Already the strongest owned gear.")
			refresh.call(m)
			return
		_equip_pick(cid, it["value"], func(): refresh.call(m)))

func _equip_pick(cid: String, slot: String, done: Callable) -> void:
	var items = [{"text": "(remove)", "value": ""}]
	for iid in Game.S["inventory"]["items"]:
		if Game.can_equip(cid, slot, iid)["ok"]:
			items.append({"icon": iid, "text": Content.item_name(iid), "right": str(Game.count(iid)), "value": iid})
	var m = _menu(items, Rect2(4, 104, 168, 132), 11, "")
	sel_slot = slot
	m.moved.connect(func(_i): preview_item = m.current().get("value", ""))
	preview_item = m.current().get("value", "")
	m.chosen.connect(func(_i, it):
		var r = Game.equip(cid, slot, it["value"])
		if r["ok"]:
			Audio.ui("FX002")
			_pop_list()
			done.call()
		else:
			flash_msg(r["reason"]))

func _equip_info(cid: String, m: MenuList) -> void:
	UI.win(self, Rect2(176, 4, 140, 232))
	var cur = Game.stats(cid)
	var prev = cur
	var has_prev = lists.size() > 0 and lists[-1] != m and preview_item != null
	if has_prev:
		var mem = Game.member(cid).duplicate(true)
		if preview_item == "":
			mem["equip"].erase(sel_slot)
		else:
			mem["equip"][sel_slot] = preview_item
			if sel_slot == "weapon" and Content.item(preview_item).get("two_handed", false):
				mem["equip"].erase("offhand")
		prev = Game.stats_for(cid, mem)
	var y = 10
	for k in [["mhp", "Max HP"], ["mmp", "Max MP"], ["atk", "Attack"], ["matk", "Magic"], ["def", "Defense"], ["res", "Resist"], ["spd", "Speed"]]:
		UI.label(self, Vector2(183, y), k[1])
		UI.text_right(self, 262, y, str(cur[k[0]]))
		if has_prev:
			var nv: int = prev[k[0]]
			var col = UI.C_TEXT if nv == cur[k[0]] else (UI.C_GREEN if nv > cur[k[0]] else UI.C_RED)
			UI.text(self, Vector2(266, y), "→", UI.C_LABEL)
			UI.text_right(self, 308, y, str(nv), col)
		y += 12
	y += 4
	var grants: Array = prev["grants"] if has_prev else cur["grants"]
	for g in grants:
		UI.text(self, Vector2(183, y), T.s("gm.grants", "Grants ") + Content.ability(g)["name"], UI.C_GOLD)
		y += 11
	# item sets and teaching gear (systems s2)
	var sets_now: Dictionary = Content.data.get("gear2", {}).get("sets", {})
	for sa in (prev if has_prev else cur).get("sets", []):
		UI.text(self, Vector2(183, y), "%s %d/%d" % [sets_now.get(sa[0], {}).get("name", sa[0]), sa[1], sa[2]], UI.C_GOLD)
		y += 11
	for sl in Game.member(cid)["equip"]:
		var tid = Game.member(cid)["equip"][sl]
		if tid == null or tid == "":
			continue
		for tt in Content.item(tid).get("teach", []):
			if y > 158:
				break
			var pg = Game.gear_progress(cid, tt[0])
			UI.text(self, Vector2(183, y), "%s %s" % [Content.ability(tt[0]).get("name", tt[0]), "learned" if pg >= 100 else "%d%%" % pg], UI.C_GREEN if pg >= 100 else UI.C_LABEL)
			y += 11
	var pas: Dictionary = prev["passives"] if has_prev else cur["passives"]
	for k in pas:
		if y > 170:
			break
		UI.text(self, Vector2(183, y), _passive_label(k, pas[k]), Color8(210, 190, 250))
		y += 11
	if has_prev and preview_item != "":
		var d = Content.item(preview_item)
		var lines = UI.wrap(d.get("desc", ""), 124).slice(0, 4)
		var yy = 226 - lines.size() * 11
		for ln in lines:
			UI.text(self, Vector2(183, yy), ln, UI.C_DIM)
			yy += 11

func _passive_label(k: String, v) -> String:
	match k:
		"lowhp_guard":
			return "Guard below 40% HP"
		"mp_regen":
			return "MP +%s per action" % str(v)
		"atb_mult":
			return T.s("gm.faster_readiness", "Faster readiness")
		"mag_bonus":
			return T.s("gm.magic_up", "Magic up")
		"reserve_scale":
			return T.s("gm.stronger_with_reserves", "Stronger with reserves")
		"auto_revive":
			return T.s("gm.survives_one_fatal_blow", "Survives one fatal blow")
		"elem_resist":
			var names = []
			if typeof(v) == TYPE_DICTIONARY:
				for e in v:
					names.append(str(e))
			return "Resists " + ", ".join(PackedStringArray(names))
		"weapon_element":
			return "Weapon: " + str(v)
	return {"phys_reduce": "Physical damage -10%", "reveal_affinity": "Reveals affinities", "immune": "Immune: " + str(v),
		"acc_bonus": "Accuracy +%s" % str(v), "heal_mult": "Healing up", "mmp_mult": "Max MP up", "mhp_mult": "Max HP up",
		"counter": "Counterattack", "twohand_mult": "Two-handed x1.15", "mercy_barrier": "Barrier below 30% HP", "start_atb": "Quick start",
		"encounter_mult": "Fewer encounters", "dispel_ward": "Wards first dispel", "concord_bonus": "Concord +2"}.get(k, k.capitalize().replace("_", " "))

# ======================================================================
# Abilities
# ======================================================================
func _abilities_menu(cid: String) -> void:
	page = "abil"
	var items = []
	var learned = Game.learned_abilities(cid)
	var st = Game.stats(cid)
	for g in st["grants"]:
		if not learned.has(g):
			learned.append(g)
	for l in Content.ch(cid)["learn"]:
		var a = Content.ability(l["id"])
		var has = learned.has(l["id"])
		items.append({"spell": l["id"] if has else "", "text": a["name"] if has else "Lv %d: ???" % l["level"], "right": str(int(a["mp"])) if has else "", "value": l["id"], "enabled": has and a.get("field", false), "reason": T.s("gm.battle_technique", "Battle technique") if has else "Not yet learned", "desc": a["desc"] if has else ""})
	var ult = Content.ch(cid).get("ultimate")
	if ult != null:
		var has2 = learned.has(ult)
		items.append({"text": Content.ability(ult)["name"] if has2 else "Personal story: ???", "value": ult, "enabled": false, "reason": T.s("gm.battle_technique", "Battle technique") if has2 else "Resolve their personal story", "desc": Content.ability(ult)["desc"] if has2 else ""})
	for vk in Game.S.get("vknown", {}).get(cid, []):
		var va = Content.ability(vk)
		items.append({"spell": vk, "text": va["name"], "right": str(int(va["mp"])), "value": vk, "enabled": va.get("field", false), "reason": T.s("gm.battle_magic", "Battle magic"), "desc": va["desc"] + " (Vestige magic)"})
	for g in st["grants"]:
		items.append({"spell": g, "text": Content.ability(g)["name"] + " (acc.)", "right": str(int(Content.ability(g)["mp"])), "value": g, "enabled": Content.ability(g).get("field", false), "reason": T.s("gm.granted_while_equipped", "Granted while equipped"), "desc": Content.ability(g)["desc"]})
	_limit_and_lore_items(cid, items)
	var m = _menu(items, Rect2(4, 4, 200, 150), 12, Game.char_name(cid))
	info_draw = func():
		var it = m.current()
		UI.win(self, Rect2(4, 158, 312, 78))
		var y = 162
		UI.stat(self, Vector2(11, y), T.s("gm.mp", "MP"), "%d/%d" % [Game.member(cid)["mp"], st["mmp"]], 80)
		y += 12
		for ln in UI.wrap(it.get("desc", it.get("reason", "")), 296).slice(0, 5):
			UI.text(self, Vector2(10, y), ln)
			y += 11
	m.chosen.connect(func(_i, it):
		var a = Content.ability(it["value"])
		var mem = Game.member(cid)
		if int(mem["mp"]) < int(a["mp"]):
			flash_msg(T.s("gm.not_enough_mp", "Not enough MP."))
			return
		var all: bool = a.get("target", "") == "ally_all"
		_pick_member(func(tc):
			var ok = _apply_field_ops(a["ops"], all, tc, st["matk"], st["level"])
			if a["id"] == "S042" or a["id"] == "S044":
				ok = _apply_field_ops([{"op": "revive", "pct": 0.25}] if a["id"] == "S044" else [], all, tc, 0, 0) or ok
			if ok:
				mem["mp"] = int(mem["mp"]) - int(a["mp"])
				Audio.sfx("FX022")
				_pop_list()
			else:
				flash_msg(T.s("gm.it_would_have_no_effect", "It would have no effect.")), T.s("gm.cast_on_whom", "Cast on whom?")))

## Limit breaks (known ones, then what the next needs) and, for the blue mages, the learned Lore.
func _limit_and_lore_items(cid: String, items: Array) -> void:
	var known = Game.limit_known(cid)
	var ids: Array = Content.data.get("limits", {}).get("heroes", {}).get(cid, [])
	var nxt = Game.limit_next(cid)
	for aid in ids:
		var a = Content.ability(aid)
		if known.has(aid):
			items.append({"text": "Limit: " + a["name"], "value": aid, "enabled": false, "reason": "Limit break", "color": UI.C_GOLD,
				"desc": a["desc"] + " (Limit: when the gauge is full.)"})
		elif not nxt.is_empty() and nxt["id"] == aid:
			items.append({"text": "Limit: ???", "value": aid, "enabled": false, "reason": "Use the last limit %d/%d times; level %d." % [mini(nxt["uses"], nxt["need"]), nxt["need"], nxt["level"]]})
	for bid in Game.blue_for(cid):
		var ba = Content.ability(bid)
		items.append({"spell": bid, "text": "Lore: " + ba["name"], "right": str(int(ba["mp"])), "value": bid, "enabled": false, "reason": "Enemy lore", "desc": ba["desc"]})

# ======================================================================
# Formation: active four, reserve, rows (free at safe screens)
# ======================================================================
func _formation_menu() -> void:
	page = "formation"
	swap_from = -1
	var m = _menu([], Rect2(4, 4, 150, 150), 12, "Formation")
	var refresh = func(mm: MenuList):
		var items = []
		var act = Game.active()
		var order = act.duplicate()
		for cid in Game.S["party"]["roster"]:
			if not order.has(cid):
				order.append(cid)
		var bench = Game.battle_reserves()
		for i in range(order.size()):
			var cid: String = order[i]
			var tag = "Active" if i < act.size() else ("Bench" if bench.has(cid) else ("Reserve" if Game.is_available(cid) else "Away"))
			var mark = "* " if i == swap_from else ""
			items.append({"text": mark + Game.short_name(cid), "right": "%s %s" % [tag, Game.row(cid).substr(0, 1).to_upper()], "value": cid,
				"enabled": Game.is_available(cid), "reason": T.s("gm.away_from_the_party", "Away from the party")})
		mm.items = items
		info_draw = func():
			UI.win(self, Rect2(158, 4, 158, 150))
			var lines = UI.wrap("Confirm a member, then another to swap places. Press Page (Q/E) on a member to switch front/back row. The first five available are active; the next three wait on the bench and can Swap in during battle.", 146)
			var y = 10
			for ln in lines:
				UI.text(self, Vector2(164, y), ln, UI.C_DIM)
				y += 11
			_draw_row_depth(Rect2(158, 158, 158, 78), str(mm.current().get("value", "")))
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(i, it):
		if swap_from < 0:
			swap_from = i
		else:
			var order: Array = m.items.map(func(x): return x["value"])
			var a = order[swap_from]
			order[swap_from] = order[i]
			order[i] = a
			var avail = order.filter(func(c): return Game.is_available(c))
			Game.set_active(avail.slice(0, Game.PARTY_MAX))
			var ros: Array = Game.S["party"]["roster"]
			ros.sort_custom(func(x, y): return order.find(x) < order.find(y))
			swap_from = -1
		refresh.call(m))
	m.gui_input.connect(func(_e): pass)
	# row toggle via page keys
	var orig_handle = m
	m.set_meta("row_toggle", true)

## Row depth panel (Formation): what the highlighted hero's row does in battle.
func _draw_row_depth(r: Rect2, cid: String) -> void:
	if cid == "" or not Game.S["party"]["members"].has(cid):
		return
	UI.win(self, r)
	var rw = Game.row(cid)
	UI.text(self, r.position + Vector2(6, 4), "%s: %s row" % [Game.short_name(cid), rw.capitalize()], UI.C_GOLD)
	var txt = "Full melee damage dealt and taken. Targeted twice as often." if rw == "front" else "Melee damage dealt and taken halved; bows and magic unaffected. Some attacks strike a whole row."
	var y = r.position.y + 16
	for ln in UI.wrap(txt, r.size.x - 12):
		UI.text(self, Vector2(r.position.x + 6, y), ln, UI.C_TEXT)
		y += 11

func _row_toggle_current() -> void:
	if lists.is_empty():
		return
	var m: MenuList = lists[-1]
	if not m.has_meta("row_toggle"):
		return
	var cid: String = m.current().get("value", "")
	if cid == "":
		return
	Game.S["party"]["rows"][cid] = "back" if Game.row(cid) == "front" else "front"
	_refresh_top()

# ======================================================================
# Vestiges
# ======================================================================
func _vestige_menu() -> void:
	page = "vest"
	var m = _menu([], Rect2(4, 4, 200, 120), 8, "Vestiges")
	var refresh = func(mm: MenuList):
		var items = []
		for vid in Game.S.get("vestiges", []):
			var v: Dictionary = Content.data["vestiges"][vid]
			var holder = ""
			for k in Game.S["links"]:
				if k == vid:
					holder = Game.short_name(Game.S["links"][k])
			items.append({"text": v["name"], "right": holder if holder != "" else "-", "value": vid})
		mm.items = items
		info_draw = func():
			var it = mm.current()
			if it.is_empty():
				return
			var vd: Dictionary = Content.data["vestiges"][it["value"]]
			UI.win(self, Rect2(4, 128, 312, 108))
			UI.inset(self, Rect2(268, 186, 44, 44))
			Portraits.draw(self, {"V01": "moth", "V02": "stag", "V03": "whale", "V04": "manta", "V05": "fox", "V06": "tortoise", "V07": "hind", "V08": "leviathan", "V09": "colossus", "V10": "thorn", "V11": "wyrm", "V12": "wraith"}.get(it["value"], ""), Rect2(270, 188, 40, 40))
			if int(str(it["value"]).substr(1)) >= 13 and not BattleFX.draw_vestige_idle(self, it["value"], 0.0, Vector2(290, 228), 0.3):
				var el = str(vd.get("element", "none"))
				UI.text_center(self, 290, 196, str(it["value"]), UI.C_DIM)
				if UI.elem_label(el) != "-":
					UI.text_center(self, 290, 208, UI.elem_label(el), UI.elem_color(el))
			var a = Content.ability(vd["summon"])
			var y = 132
			for ln in UI.wrap(a["desc"] + " Costs 100 Concord; once per battle.", 296):
				UI.text(self, Vector2(10, y), ln)
				y += 11
			UI.text(self, Vector2(10, y), T.s("gm.level_up_bonus", "Level-up bonus: ") + str(vd.get("bonus_text", "-")), UI.C_GOLD)
			y += 12
			var holder_id = ""
			for k in Game.S["links"]:
				if k == it["value"]:
					holder_id = Game.S["links"][k]
			UI.label(self, Vector2(10, y), T.s("gm.teaches", "Teaches") + (" (" + Game.short_name(holder_id) + ")" if holder_id != "" else ""))
			y += 11
			for t in vd.get("teach", []):
				var an = Content.ability(t[0]).get("name", t[0])
				var pr = Game.vestige_progress(holder_id, t[0]) if holder_id != "" else 0
				UI.text(self, Vector2(16, y), an, UI.C_TEXT)
				UI.text_right(self, 200, y, "x%d" % int(t[1]), UI.C_DIM)
				UI.text_right(self, 250, y, ("%d%%" % pr) if holder_id != "" else "-", UI.C_HI if pr >= 100 else UI.C_TEXT)
				y += 11
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		var items = [{"text": "(unlink)", "value": ""}]
		for cid in Game.available_members():
			items.append({"text": Game.char_name(cid), "value": cid})
		var m2 = _menu(items, Rect2(208, 4, 108, 110), 9)
		m2.chosen.connect(func(_j, it2):
			var r = Game.link_vestige(it["value"], it2["value"])
			if not r["ok"]:
				flash_msg(r["reason"])
			_pop_list()))

# ======================================================================
# Journal / World map / Bestiary
# ======================================================================
func _journal() -> void:
	page = "journal"
	var j: Dictionary = Game.S["journal"]
	var items = [{"text": "Current objective", "value": "obj"}, {"text": "Rumors (%d)" % j["rumors"].size(), "value": "rum"}, {"text": "Quests", "value": "q"}, {"text": "Chapters", "value": "ch"}]
	var m = _menu(items, Rect2(4, 4, 110, 60), 4, "Journal")
	var view = ["obj"]
	info_draw = func():
		UI.win(self, Rect2(118, 4, 198, 232))
		var lines = []
		match m.current().get("value", "obj"):
			"obj":
				lines.append(["Objective", UI.C_GOLD])
				for ln in UI.wrap(j.get("objective", "") if j.get("objective", "") != "" else "-", 184):
					lines.append([ln, UI.C_TEXT])
				if j.get("clue", "") != "":
					lines.append(["", UI.C_TEXT])
					lines.append(["Last clue", UI.C_GOLD])
					for ln in UI.wrap(j["clue"], 184):
						lines.append([ln, UI.C_TEXT])
				if j.get("source", "") != "":
					lines.append(["", UI.C_TEXT])
					lines.append(["Source: " + j["source"], UI.C_DIM])
			"rum":
				for r in j["rumors"]:
					for ln in UI.wrap("- " + r, 184):
						lines.append([ln, UI.C_TEXT])
				if j["rumors"].is_empty():
					lines.append(["No rumors heard yet.", UI.C_DIM])
			"q":
				for qid in Content.data["quests"]:
					var st = Game.quest_state(qid)
					if st == "NOT_STARTED":
						continue
					lines.append([Content.data["quests"][qid]["name"], UI.C_GOLD if st == "COMPLETED" else UI.C_TEXT])
					lines.append(["  " + st.replace("_", " ").capitalize(), UI.C_DIM])
				if lines.is_empty():
					lines.append(["No optional stories begun.", UI.C_DIM])
			"ch":
				for cid in Game.S["chapters"]:
					lines.append([cid + " " + Content.data["chapters"][cid]["name"], UI.C_TEXT])
		var y = 8
		for l in lines.slice(0, 20):
			UI.text(self, Vector2(124, y), l[0], l[1])
			y += 11
	m.chosen.connect(func(_i, _it): pass)

func _worldmap() -> void:
	page = "wmap"
	var items = []
	for lid in Content.data["locations"]:
		if Game.S["discovered"].has(lid):
			items.append({"text": Content.data["locations"][lid]["name"], "value": lid, "enabled": true})
	if items.is_empty():
		items.append({"text": "(nothing charted)", "enabled": false})
	var m = _menu(items, Rect2(4, 4, 120, 200), 16, "Discovered")
	info_draw = func():
		UI.win(self, Rect2(128, 4, 188, 200))
		UI.inset(self, Rect2(130, 7, 184, 194))
		var wm = Content.map("WORLD_POST" if Game.S["world_phase"] == "post" else "WORLD")
		if wm.is_empty():
			return
		var sc = minf(180.0 / wm["w"], 190.0 / wm["h"])
		var ox = 132.0
		var oy = 9.0
		for y in range(0, wm["h"], 2):
			var row: String = wm["grid"][y]
			for x in range(0, wm["w"], 2):
				var k: String = wm["legend"].get(row[x], "void")
				var col = Color8(40, 80, 150)
				match k:
					"plains", "grass", "path": col = Color8(90, 150, 70)
					"forest": col = Color8(40, 100, 40)
					"hills": col = Color8(110, 140, 70)
					"mountain": col = Color8(130, 120, 110)
					"sand", "salt": col = Color8(210, 200, 170)
					"snow": col = Color8(230, 236, 244)
					"deep": col = Color8(30, 50, 110)
					"ash": col = Color8(80, 70, 76)
					"reef": col = Color8(70, 50, 70)
				draw_rect(Rect2(ox + x * sc, oy + y * sc, ceil(sc * 2), ceil(sc * 2)), col)
		for e in wm["entities"]:
			if e["type"] == "location" and Game.S["discovered"].has(e["id"]):
				var sel: bool = m.current().get("value", "") == e["id"]
				draw_rect(Rect2(ox + e["x"] * sc - 1, oy + e["y"] * sc - 1, 3, 3), UI.C_HI if sel else UI.C_RED)
		var pl: Vector2i = main.field.p_tile if main.field.map_id.begins_with("WORLD") else Vector2i(-1, -1)
		if pl.x >= 0 and int(Time.get_ticks_msec() / 300) % 2 == 0:
			draw_rect(Rect2(ox + pl.x * sc - 1, oy + pl.y * sc - 1, 3, 3), Color.WHITE)

var best_tab = 0

## Bestiary (systems s2): every entry (unseen ones as ???), completion and its rewards, stats once defeated or
## scanned, affinities, loot, lore and where the creature lives. Confirm switches Data / Lore; the first line claims
## completion rewards.
func _bestiary() -> void:
	page = "best"
	best_tab = 0
	var m = _menu([], Rect2(4, 4, 140, 232), 20, "Bestiary")
	var refresh = func(mm: MenuList):
		var items = []
		var pend = Game.bestiary_rewards_pending()
		items.append({"text": "Rewards", "value": "__rewards", "right": "!" if not pend.is_empty() else "", "color": UI.C_GOLD})
		for eid in Game.bestiary_entries():
			var e = Content.enemy(eid)
			var b: Dictionary = Game.S["bestiary"].get(eid, {})
			if b.get("seen", false):
				var nm: String = e["name"].split(",")[0]
				while nm.length() > 4 and UI.width(nm) > 92:
					nm = nm.substr(0, nm.length() - 1)
				items.append({"text": nm, "value": eid, "right": str(b.get("defeated", 0))})
			else:
				items.append({"text": "??????", "value": eid, "enabled": false, "reason": "Not yet met"})
		mm.items = items
		mm.index = clampi(mm.index, 0, maxi(0, items.size() - 1))
		info_draw = func(): _bestiary_info(mm)
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.moved.connect(func(_i): best_tab = 0)
	m.chosen.connect(func(_i, it):
		if it["value"] == "__rewards":
			var got = Game.claim_bestiary_rewards()
			if got.is_empty():
				flash_msg("No new rewards.")
			else:
				Audio.sfx("FX007")
				flash_msg(got[0] + ("" if got.size() == 1 else " (+%d more)" % (got.size() - 1)))
			refresh.call(m)
			return
		best_tab = 1 - best_tab
		Audio.ui("FX001"))

func _bestiary_info(m: MenuList) -> void:
	var it = m.current()
	UI.win(self, Rect2(148, 4, 168, 232))
	var pg = Game.bestiary_progress()
	UI.label(self, Vector2(154, 8), "Seen")
	UI.text_right(self, 226, 8, "%d/%d" % [pg["seen"], pg["total"]])
	UI.label(self, Vector2(236, 8), "Won")
	UI.text_right(self, 310, 8, "%d/%d" % [pg["defeated"], pg["total"]])
	if it.is_empty() or not it.has("value"):
		return
	var y = 22
	if it["value"] == "__rewards":
		var rw: Dictionary = Content.data.get("gear2", {}).get("bestiary_rewards", {})
		var claimed: Array = Game.S.get("bestiary_claimed", [])
		var pend = Game.bestiary_rewards_pending()
		for track in ["seen", "defeated"]:
			UI.text(self, Vector2(154, y), "Creatures seen" if track == "seen" else "Creatures defeated", UI.C_GOLD)
			y += 12
			for pct in [25, 50, 75, 100]:
				var lst: Array = rw.get(track, {}).get(str(pct), [])
				var names = []
				for r in lst:
					names.append("%s x%d" % [Content.item_name(r[0]), int(r[1])] if int(r[1]) > 1 else Content.item_name(r[0]))
				var key = "%s:%d" % [track, pct]
				var ready = false
				for p in pend:
					if p[0] == track and p[1] == pct:
						ready = true
				var col = UI.C_DIM if claimed.has(key) else (UI.C_GREEN if ready else UI.C_TEXT)
				UI.text(self, Vector2(154, y), "%d%%" % pct, UI.C_LABEL)
				var ln = UI.wrap(", ".join(names), 124)
				for i in range(mini(2, ln.size())):
					UI.text(self, Vector2(182, y), ln[i], col)
					y += 10
				y += 2
			y += 4
		UI.text(self, Vector2(154, 222), "Confirm: claim", UI.C_DIM)
		return
	var eid: String = it["value"]
	var e = Content.enemy(eid)
	var b: Dictionary = Game.S["bestiary"].get(eid, {})
	var known = int(b.get("defeated", 0)) > 0 or b.get("scanned", false)
	var tx: Texture2D = Content.load_art("res://assets/sprites/enemies/%s.png" % eid)
	if tx:
		var fw = tx.get_width() / 4
		var fh = tx.get_height()
		var k = 1.0 if (fw <= 156 and fh <= 64) else minf(0.5, 64.0 / fh)
		var dw = fw * k
		var dh = mini(int(fh * k), 64)
		draw_texture_rect_region(tx, Rect2(232 - dw / 2.0, y, dw, dh), Rect2(0, 0, fw, dh / k))
		y += dh + 3
	var nm = UI.wrap(e["name"], 156)
	for ln in nm.slice(0, 2):
		UI.text(self, Vector2(154, y), ln, UI.C_HI)
		y += 11
	if best_tab == 0:
		UI.text(self, Vector2(154, y), "Lv %d  HP %s" % [int(e["level"]), str(int(e["hp"])) if known else "?"])
		y += 11
		if known:
			UI.stat(self, Vector2(154, y), "ATK", str(int(e.get("atk", 0))), 196)
			UI.stat(self, Vector2(204, y), "MAG", str(int(e.get("mag", 0))), 246)
			UI.stat(self, Vector2(254, y), "SPD", str(int(e.get("spd", 0))), 308)
			y += 11
			UI.stat(self, Vector2(154, y), "DEF", str(int(e.get("def", 0))), 196)
			UI.stat(self, Vector2(204, y), "RES", str(int(e.get("res", 0))), 246)
			UI.stat(self, Vector2(254, y), "Won", str(b.get("defeated", 0)), 308)
			y += 12
		var wk = []
		for el in e["affinities"]:
			if b.get("affinity", false) or b.get("weak", []).has(el):
				wk.append("%s %s" % [UI.elem_label(el), e["affinities"][el]])
		for ln in UI.wrap(("Affinity: " + ", ".join(wk)) if not wk.is_empty() else "Affinity: unknown", 156).slice(0, 2):
			UI.text(self, Vector2(154, y), ln, UI.C_GOLD)
			y += 11
		if b.get("drops", false):
			var dn = []
			for d in e.get("drops", []):
				var n = Content.item_name(d["item"])
				if not dn.has(n):
					dn.append(n)
			for ln in UI.wrap("Drops: " + (", ".join(dn.slice(0, 4)) if not dn.is_empty() else "none"), 156).slice(0, 3):
				UI.text(self, Vector2(154, y), ln, UI.C_TEXT)
				y += 11
			if e.get("steal", {}).get("common", "") != "":
				UI.text(self, Vector2(154, y), "Steal: " + Content.item_name(e["steal"]["common"]), UI.C_DIM)
				y += 11
		else:
			UI.text(self, Vector2(154, y), "Drops: ?  (defeat or scan)", UI.C_DIM)
			y += 11
		for ln in UI.wrap(e.get("behavior", e.get("tell", "")), 156):
			if y > 210:
				break
			UI.text(self, Vector2(154, y), ln, UI.C_DIM)
			y += 11
		UI.text(self, Vector2(154, 222), "Confirm: lore", UI.C_DIM)
	else:
		for ln in UI.wrap(e.get("lore", "") if e.get("lore", "") != "" else "No one has written this one down.", 156):
			if y > 170:
				break
			UI.text(self, Vector2(154, y), ln)
			y += 11
		y += 4
		UI.text(self, Vector2(154, y), "Found in", UI.C_LABEL)
		y += 11
		var wh: Array = e.get("where", [])
		if wh.is_empty():
			UI.text(self, Vector2(160, y), "Unknown", UI.C_DIM)
		for w in wh:
			if y > 210:
				break
			UI.text(self, Vector2(160, y), w)
			y += 10
		UI.text(self, Vector2(154, 222), "Confirm: data", UI.C_DIM)

# ======================================================================
# Crafting (systems s2): opened by talking to a crafter_ NPC (field.gd) or the scene command `craft <id>`
# ======================================================================
var craft_id = ""
const CRAFT_CATS := [["Weapons", "weapon"], ["Armour", "armor"], ["Accessories", "accessory"], ["Items", "consumable"], ["Reforge", "reforge"]]

func _craft_menu(crafter_id: String) -> void:
	page = "craft"
	craft_id = crafter_id
	var opts = []
	var have = Game.craft_recipes(crafter_id)
	for c in CRAFT_CATS:
		var n = 0
		for rid in have:
			if _craft_cat(rid) == c[1]:
				n += 1
		opts.append({"text": c[0], "value": c[1], "right": str(n), "enabled": n > 0, "reason": "Nothing to make"})
	opts.append({"text": "Leave", "value": "leave"})
	var m = _menu(opts, Rect2(4, 42, 104, 22 + 11 * opts.size()), opts.size(), "Bench")
	info_draw = func(): _craft_head()
	m.set_meta("refresh", func(_m): page = "craft"; info_draw = func(): _craft_head())
	m.chosen.connect(func(_i, it):
		if it["value"] == "leave":
			_close_all()
		else:
			_craft_list(it["value"]))

func _craft_cat(rid: String) -> String:
	var r: Dictionary = Content.data["gear2"]["recipes"][rid]
	if r["kind"] == "reforge":
		return "reforge"
	return str(Content.item(r["result"]).get("kind", "consumable"))

func _crafter_name() -> String:
	if main != null and main.field != null:
		for e in main.field.map.get("entities", []):
			if e["type"] == "npc" and e.get("id", "") == craft_id and e.get("name", "") != "":
				return e["name"]
	return "Crafter"

func _craft_head() -> void:
	UI.win(self, Rect2(4, 4, 312, 34))
	var tier: String = Game.crafter_tier(craft_id)
	UI.text(self, Vector2(11, 9), _crafter_name(), UI.C_HI)
	UI.text(self, Vector2(11, 20), "%s bench" % Content.data["gear2"]["tiers"].get(tier, {}).get("name", ""), UI.C_LABEL)
	UI.label(self, Vector2(236, 9), "Crowns")
	UI.text_right(self, 309, 20, str(Game.gold()))

func _craft_list(cat: String) -> void:
	var m = _menu([], Rect2(4, 42, 196, 194), 16, "")
	var refresh = func(mm: MenuList):
		var items = []
		for rid in Game.craft_recipes(craft_id):
			if _craft_cat(rid) != cat:
				continue
			var r: Dictionary = Content.data["gear2"]["recipes"][rid]
			var c = Game.can_craft(rid)
			var nm: String = Content.item_name(r["result"]) + (" x%d" % int(r["count"]) if int(r["count"]) > 1 else "")
			items.append({"icon": r["result"], "text": nm, "right": str(int(r.get("gold", 0))) if int(r.get("gold", 0)) > 0 else "",
				"value": rid, "enabled": true, "color": UI.C_TEXT if c["ok"] else UI.C_DIM})
		mm.items = items
		mm.index = clampi(mm.index, 0, maxi(0, items.size() - 1))
		page = "craft"
		info_draw = func(): _craft_info(mm)
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		var r = Game.craft(it["value"])
		if r["ok"]:
			Audio.sfx("FX006")
			flash_msg("Made %s%s." % [Content.item_name(r["item"]), " x%d" % r["count"] if r["count"] > 1 else ""])
		else:
			Audio.ui("FX004")
			flash_msg(r["reason"])
		refresh.call(m))

func _craft_info(m: MenuList) -> void:
	_craft_head()
	UI.win(self, Rect2(204, 42, 112, 194))
	var it: Dictionary = m.current()
	if it.is_empty():
		UI.text(self, Vector2(211, 48), "Nothing to make.", UI.C_DIM)
		return
	var r: Dictionary = Content.data["gear2"]["recipes"][it["value"]]
	var d = Content.item(r["result"])
	var y = 48
	var ix = 211
	if UI.icon(self, Vector2(211, 47), r["result"], 24):
		ix = 239
	UI.stat(self, Vector2(ix, y), "Owned", str(Game.count(r["result"])), 308)
	y += 11
	if d.has("atk"):
		UI.stat(self, Vector2(ix, y), "ATK", str(int(d["atk"])), 308)
		y += 11
		UI.stat(self, Vector2(ix, y), "MAG", str(int(d["mag"])), 308)
		y += 11
	elif d.has("def"):
		UI.stat(self, Vector2(ix, y), "DEF", str(int(d["def"])), 308)
		y += 11
		UI.stat(self, Vector2(ix, y), "RES", str(int(d["res"])), 308)
		y += 11
	y = maxi(y, 78) + 2
	for ln in UI.wrap(d.get("desc", ""), 98).slice(0, 4):
		UI.text(self, Vector2(211, y), ln, UI.C_DIM)
		y += 10
	y += 4
	UI.label(self, Vector2(211, y), "Needs")
	y += 11
	var need = r["mats"].duplicate()
	if r["kind"] == "reforge":
		need.push_front([r["input"], 1])
	for mt in need:
		var have = Game.count(mt[0])
		var ok = have >= int(mt[1])
		UI.icon(self, Vector2(211, y), mt[0], 11)
		var nm: String = Content.item(mt[0]).get("name", mt[0])
		while nm.length() > 4 and UI.width(nm) > 62:
			nm = nm.substr(0, nm.length() - 1)
		UI.text(self, Vector2(224, y), nm, UI.C_TEXT if ok else UI.C_RED)
		UI.text_right(self, 308, y, "%d/%d" % [have, int(mt[1])], UI.C_TEXT if ok else UI.C_RED)
		y += 11
	if int(r.get("gold", 0)) > 0:
		UI.text(self, Vector2(224, y), "Crowns", UI.C_TEXT if Game.gold() >= int(r["gold"]) else UI.C_RED)
		UI.text_right(self, 308, y, str(int(r["gold"])), UI.C_TEXT if Game.gold() >= int(r["gold"]) else UI.C_RED)

# ======================================================================
# Settings (persist separately from saves) and key remapping
# ======================================================================
## sys s4: settings grouped into pages (Game, Battle, Text and Display, Accessibility, Audio, Keyboard, Controller).
## Each entry: [key, options]; the label is T.s("set.<key>"). Left/Right (or Confirm) cycles the value.
const SETTING_PAGES := {
	"game": [["difficulty", ["easy", "normal", "hard"]], ["autosave", [true, false]], ["run_toggle", [false, true]],
		["ride_mount", [true, false]], ["encounters", ["normal", "reduced", "off"]], ["encounter_rate", [0.5, 0.75, 1.0, 1.25, 1.5]],
		["pause_on_focus_loss", [true, false]], ["mature", [false, true]]],
	"battle": [["battle_mode", ["wait", "active"]], ["battle_speed", [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]],
		["auto_battle", ["off", "attack", "repeat"]], ["short_summons", [false, true]]],
	"text": [["text_speed", [0, 1, 2, 3]], ["auto_text", [0, 1, 2, 3]], ["text_size", [0, 1, 2]],
		["dialogue_opacity", [0.4, 0.55, 0.7, 0.85, 1.0]], ["window_color", ["dark", "blue", "ash", "crimson", "verdant", "violet", "contrast"]],
		["glyphs", ["auto", "keyboard", "xbox", "playstation", "deck"]], ["minimap", [true, false]],
		["window_size", ["960x720", "1280x800", "1280x720", "1440x1080", "1920x1080"]], ["fullscreen", [false, true]]],
	"access": [["colorblind", ["off", "deuteranopia", "protanopia", "tritanopia"]], ["shape_cues", [true, false]],
		["high_contrast", [false, true]], ["reduced_flash", [false, true]], ["shake", [true, false]],
		["world_view", ["mode7", "flat"]], ["hd2d", [true, false]], ["hd2d_dof", [true, false]], ["battle_camera", [true, false]], ["weather", [true, false]], ["hold_confirm", [false, true]], ["reel_toggle", [false, true]],
		["fish_assist", [false, true]], ["captions", [false, true]], ["mono", [false, true]]],
	"audio": [["vol_master", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]], ["vol_music", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]],
		["vol_sfx", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]], ["vol_ambience", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]],
		["vol_ui", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]], ["blips", [true, false]], ["vol_voice", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]]],
}
const SETTING_PAGE_ORDER := ["game", "battle", "text", "access", "audio", "keys", "pad"]
var rebinding_pad = ""

func _setting_opts(k: String) -> Array:
	for pg in SETTING_PAGES:
		for d in SETTING_PAGES[pg]:
			if d[0] == k:
				return d[1]
	return []

func _setting_value(k: String):
	if k == "difficulty":
		return Game.difficulty() if Game.playing else Settings.get_v("difficulty_default")
	return Settings.get_v(k)

func _setting_label(k: String, v) -> String:
	match k:
		"text_speed", "auto_text", "text_size":
			return T.s("val.%s.%d" % [k, int(v)])
		"run_toggle": return T.s("val.toggle") if v else T.s("val.hold")
		"battle_speed": return "x%.2f" % float(v)
		"encounter_rate": return "%d%%" % int(round(float(v) * 100))
		"dialogue_opacity": return "%d%%" % int(round(float(v) * 100))
		"window_size": return str(v)
	if typeof(v) == TYPE_BOOL:
		return T.s("common.on") if v else T.s("common.off")
	if typeof(v) == TYPE_FLOAT and k.begins_with("vol"):
		return "%d%%" % int(round(v * 100))
	return T.s("val." + str(v), str(v).capitalize())

func _settings_menu() -> void:
	page = "settings"
	var items = []
	for pg in SETTING_PAGE_ORDER:
		items.append({"text": T.s("settings.page." + pg), "value": pg})
	var m = _menu(items, Rect2(4, 4, 104, 22 + 11 * items.size()), items.size(), T.s("settings.title"))
	m.memory_key = "settings_pages"
	m.setup(items, items.size(), T.s("settings.title"))
	var preview = func(): _settings_page_preview(m.current().get("value", "game"))
	info_draw = preview
	m.set_meta("refresh", func(_mm): page = "settings"; info_draw = preview)
	m.chosen.connect(func(_i, it): _settings_page(it["value"]))

func _settings_page_preview(pg: String) -> void:
	UI.win(self, Rect2(112, 4, 204, 232))
	var y = 10
	UI.label(self, Vector2(119, y), T.s("settings.page." + pg))
	y += 13
	for it in _settings_page_items(pg).slice(0, 17):
		UI.text(self, Vector2(124, y), it["text"], UI.C_DIM)
		if it.has("right"):
			UI.text_right(self, 310, y, str(it["right"]), UI.C_DIM)
		y += 11
	_settings_footer()

func _settings_footer() -> void:
	Glyphs.hints(self, Vector2(8, 226), [["confirm", T.s("common.select")], ["cancel", T.s("common.back")]])

func _settings_page_items(pg: String) -> Array:
	var items = []
	match pg:
		"keys":
			for a in Settings.ACTIONS:
				var ks = []
				for k in Settings.keys_for(a):
					ks.append(OS.get_keycode_string(int(k)))
				items.append({"text": T.s("act." + a), "right": ", ".join(ks).substr(0, 18), "value": "key:" + a})
			items.append({"text": T.s("settings.reset_keys"), "value": "reset_keys"})
		"pad":
			var st = Glyphs.style()
			if st == "keyboard":
				st = "xbox"
			for a in Settings.ACTIONS:
				items.append({"text": T.s("act." + a), "right": Glyphs.label(a, st), "value": "pad:" + a})
			items.append({"text": T.s("settings.reset_pad"), "value": "reset_keys"})
		_:
			for d in SETTING_PAGES.get(pg, []):
				items.append({"text": T.s("set." + d[0]), "right": _setting_label(d[0], _setting_value(d[0])), "value": d[0]})
	return items

func _settings_page(pg: String) -> void:
	page = "settings"
	var m = _menu([], Rect2(112, 4, 204, 232), 18, T.s("settings.page." + pg) + "   " + T.s("settings.hint"))
	var refresh = func(mm: MenuList):
		mm.items = _settings_page_items(pg)
		mm.index = clampi(mm.index, 0, maxi(0, mm.items.size() - 1))
		page = "settings"
		info_draw = func(): _settings_footer()
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		var v: String = it["value"]
		if v == "reset_keys":
			Settings.reset_bindings()
			refresh.call(m)
		elif v.begins_with("key:"):
			rebinding = v.substr(4)
			flash_msg(T.f("settings.press_key", [T.s("act." + rebinding)]))
		elif v.begins_with("pad:"):
			rebinding_pad = v.substr(4)
			flash_msg(T.f("settings.press_pad", [T.s("act." + rebinding_pad)]))
		else:
			_cycle_setting(v, 1)
			refresh.call(m))
	m.set_meta("lr", func(dirn: int):
		var v: String = m.current().get("value", "")
		if not v.contains(":") and v != "reset_keys":
			_cycle_setting(v, dirn)
			refresh.call(m))

func _cycle_setting(k: String, dirn: int) -> void:
	var opts: Array = _setting_opts(k)
	if opts.is_empty():
		return
	var cur = _setting_value(k)
	var i = 0
	for j in range(opts.size()):
		if typeof(opts[j]) == typeof(cur) and opts[j] == cur:
			i = j
		elif (typeof(cur) == TYPE_FLOAT or typeof(cur) == TYPE_INT) and (typeof(opts[j]) == TYPE_FLOAT or typeof(opts[j]) == TYPE_INT) and absf(float(opts[j]) - float(cur)) < 0.01:
			i = j
	i = (i + dirn + opts.size()) % opts.size()
	if k == "difficulty":
		if Game.playing:
			Game.S["difficulty"] = opts[i]
		Settings.set_v("difficulty_default", opts[i])
		Audio.ui("FX001")
		return
	if k == "mature" and opts[i] and not Settings.get_v("mature_ok"):
		_confirm(T.s("settings.mature_confirm"), func():
			Settings.set_v("mature_ok", true)
			Settings.set_v("mature", true)
			_art_reload()
			_refresh_top())
		return
	Settings.set_v(k, opts[i])
	match k:
		"fullscreen":
			get_window().mode = Window.MODE_FULLSCREEN if opts[i] else Window.MODE_WINDOWED
			if not opts[i]:
				Settings.apply_window()
		"window_size":
			Settings.apply_window()
		"encounters":
			if Game.playing:
				Game.S["play_settings"]["encounters"] = opts[i]
		"mature":
			_art_reload()
	Audio.ui("FX001")

## Mature mode switches art variants (<name>_m.png): drop cached textures so the next draw picks the right one.
func _art_reload() -> void:
	Portraits._cache = {}
	HeroArt._meta = {}
	HeroArt._tex = {}
	if main != null and main.field != null:
		main.field.tex_cache = {}

func _input(event: InputEvent) -> void:
	if rebinding != "" and event is InputEventKey and event.pressed and not event.echo:
		Settings.rebind(rebinding, event.physical_keycode)
		rebinding = ""
		msg_t = 0
		_refresh_top()
		get_viewport().set_input_as_handled()
		return
	if rebinding_pad != "" and event is InputEventJoypadButton and event.pressed:
		Settings.rebind_pad(rebinding_pad, event.button_index)
		rebinding_pad = ""
		msg_t = 0
		_refresh_top()
		get_viewport().set_input_as_handled()
		return
	if lists.is_empty() or rebinding != "" or rebinding_pad != "":
		return
	var top: MenuList = lists[-1]
	if top.has_meta("lr"):
		if event.is_action_pressed("g_left"):
			top.get_meta("lr").call(-1)
		elif event.is_action_pressed("g_right"):
			top.get_meta("lr").call(1)
	if top.has_meta("row_toggle") and (event.is_action_pressed("g_page_l") or event.is_action_pressed("g_page_r")):
		_row_toggle_current()

# ======================================================================
# Save / load (sys s4: 12 manual slots in a scrolling list, autosave, world-map quicksave, detail panel)
# ======================================================================
func _slot_items() -> Array:
	var items = []
	for s in range(1, Game.SLOTS + 1):
		var info = Game.slot_info(s)
		var nm = T.f("save.slot", [s])
		if info.get("ok", false):
			items.append({"text": nm, "right": Game.fmt_time(info["playtime"]), "value": s, "info": info})
		elif info.get("reason", "") == "missing":
			items.append({"text": nm + "  " + T.s("save.empty"), "value": s, "empty": true, "color": UI.C_DIM})
		else:
			items.append({"text": nm + "  (%s)" % info.get("reason", "?"), "value": s, "bad": info.get("reason", "")})
	return items

func _load_items() -> Array:
	var items = _slot_items()
	for pr in [[Game.auto_path(), T.s("save.auto")], [Game.quick_path(), T.s("save.quick")]]:
		var info = Game.path_info(pr[0])
		if info.get("ok", false):
			items.append({"text": pr[1], "right": Game.fmt_time(info["playtime"]), "value": -1, "path": pr[0], "info": info})
	for pr in Game.PROTECTED:
		var path = Game.backup_path(pr[0])
		var info = Game.info_of(path)
		if info.get("ok", false):
			items.append({"text": pr[1], "right": Game.fmt_time(info["playtime"]), "value": -1, "path": path, "info": info})
	return items

func _slot_info_draw(m: MenuList) -> void:
	var it = m.current()
	var r = Rect2(158, 4, 158, 232)
	UI.win(self, r)
	var x = r.position.x + 7
	var y = r.position.y + 5
	UI.text(self, Vector2(x, y), str(it.get("text", "")).split("  ")[0], UI.C_GOLD)
	y += 14
	if it.has("info"):
		var i: Dictionary = it["info"]
		for ln in UI.wrap(str(i["chapter"]), 144).slice(0, 2):
			UI.text(self, Vector2(x, y), ln)
			y += 11
		for ln in UI.wrap(str(i["location"]), 144).slice(0, 2):
			UI.text(self, Vector2(x, y), ln, UI.C_LABEL)
			y += 11
		y += 3
		UI.stat(self, Vector2(x, y), T.s("save.playtime"), Game.fmt_time(i["playtime"]), r.end.x - 7)
		y += 11
		UI.stat(self, Vector2(x, y), T.s("save.crowns"), str(i.get("gold", 0)), r.end.x - 7)
		y += 11
		var tags = [T.s("val." + str(i.get("difficulty", "normal")))]
		if int(i.get("ng", 0)) > 0:
			tags.append(T.f("save.ng", [int(i["ng"])]))
		if i.get("clear", false):
			tags.append(T.s("save.cleared"))
		if str(i.get("reason", "")) != "":
			tags.append(T.s("save.reason." + str(i["reason"])))
		UI.text(self, Vector2(x, y), ", ".join(tags), UI.C_DIM)
		y += 11
		UI.text(self, Vector2(x, y), T.f("save.saved_at", [str(i["date"]).replace("T", " ").substr(0, 16)]), UI.C_DIM)
		y += 15
		UI.label(self, Vector2(x, y), T.s("save.party"))
		y += 12
		var party: Array = i.get("party", [])
		for k in range(mini(party.size(), 5)):
			var pm: Dictionary = party[k]
			var py = y + k * 20
			if HeroArt.has_field(str(pm["cid"])):
				HeroArt.draw_field(self, str(pm["cid"]), "down", false, Vector2(x + 8, py + 18))
			UI.text(self, Vector2(x + 20, py + 4), str(pm["name"]))
			UI.stat(self, Vector2(x + 96, py + 4), T.s("gm.lv", "LV"), str(pm["level"]), r.end.x - 7)
	elif it.has("bad"):
		for ln in UI.wrap(T.f("save.damaged", [it["bad"]]), 144):
			UI.text(self, Vector2(x, y), ln, UI.C_RED)
			y += 11
		for ln in UI.wrap(T.s("save.backup_hint"), 144):
			UI.text(self, Vector2(x, y), ln, UI.C_DIM)
			y += 11
	elif str(it.get("value", "")) == "quick":
		for ln in UI.wrap(T.s("save.quick_only_world") + ".", 144):
			UI.text(self, Vector2(x, y), ln, UI.C_DIM)
			y += 11
	else:
		UI.text(self, Vector2(x, y), T.s("save.empty"), UI.C_DIM)

## `lantern`: the Waylamp item id when the ledger was opened by it (consumed on the first successful save).
func _save_menu(at_point: bool, lantern: String = "") -> void:
	page = "save"
	var items = _slot_items()
	var on_world: bool = main.field.map.get("kind", "") == "world"
	if not at_point and lantern == "":
		items.append({"text": T.s("save.quick_do"), "value": "quick", "enabled": on_world, "reason": T.s("save.quick_only_world")})
	var m = _menu(items, Rect2(4, 4, 150, 232), 19, T.s("save.title"))
	info_draw = func(): _slot_info_draw(m)
	var used = [false]
	m.chosen.connect(func(_i, it):
		if str(it["value"]) == "quick":
			var do_q = func():
				var rq = Game.save_quick()
				if rq["ok"]:
					Audio.sfx("FX006")
					flash_msg(T.s("save.quick_saved"))
				else:
					flash_msg(T.f("save.failed", [rq["reason"]]))
			if FileAccess.file_exists(Game.quick_path()):
				_confirm(T.s("save.overwrite_quick"), do_q)
			else:
				do_q.call()
			return
		var do_save = func():
			var r = Game.save_slot(it["value"])
			if r["ok"]:
				Audio.sfx("FX006")
				flash_msg(T.s("save.saved"))
				if lantern != "" and not used[0]:
					used[0] = true
					Game.remove_item(lantern)
				var ni = _slot_items()
				if not at_point and lantern == "":
					ni.append(m.items[-1])
				m.items = ni
			else:
				flash_msg(T.f("save.failed", [r["reason"]]))
		if it.get("empty", false):
			do_save.call()
		else:
			_confirm(T.f("save.overwrite", [it["value"]]), do_save))

func _confirm(q: String, yes: Callable) -> void:
	var m = _menu([{"text": "No", "value": 0}, {"text": "Yes", "value": 1}], Rect2(120, 170, 80, 36), 2, "")
	info_draw = func():
		var lines = UI.wrap(q, 280)
		var qw = 120.0
		for ln in lines:
			qw = maxf(qw, UI.width(ln) + 28)
		var qh = 11 * lines.size() + 11
		UI.win(self, Rect2(round(160 - qw / 2), 166 - qh, qw, qh))
		for li in range(lines.size()):
			UI.text_center(self, 160, 171 - qh + li * 11, lines[li])
	m.chosen.connect(func(_i, it):
		_pop_list()
		if it["value"] == 1:
			yes.call())

func _load_menu() -> void:
	page = "load"
	var m = _menu(_load_items(), Rect2(4, 4, 150, 232), 19, T.s("save.load_title"))
	info_draw = func(): _slot_info_draw(m)
	m.chosen.connect(func(_i, it):
		if it.get("empty", false):
			Audio.ui("FX004")
			return
		var path = it["path"] if it.has("path") else Game.slot_path(it["value"])
		var r = Game.load_from(path)
		if r["ok"]:
			_close_all()
			if main.title_screen != null or kind == "load_after_defeat" or kind == "load":
				main.continue_from_state()
			return
		if r["reason"] == "future":
			flash_msg(T.f("save.future", [str(r.get("version", ""))]))
		elif r.get("backup_ok", false):
			_confirm(T.s("save.damaged_backup"), func():
				var rb = Game.load_backup_of(path)
				if rb["ok"]:
					_close_all()
					main.continue_from_state())
		else:
			flash_msg(T.s("save.damaged_none")))

# ======================================================================
# Shops & inns
# ======================================================================
func shop_stock(shop_id: String) -> Array:
	var sh: Dictionary = Content.data["shops"][shop_id]
	var rules: Dictionary = Content.data["shop_rules"]
	var out = []
	if "items" in sh["kinds"]:
		out.append_array(rules["basic"])
		if Game.chapter_done("CH08") or Game.chapter_done("CH07"):
			out.append_array(rules["expanded"])
		if Game.chapter_done("CH16"):
			out.append_array(rules["late"])
	var items: Dictionary = Content.data["items"]
	var ids: Array = items.keys()
	ids.sort()
	if "weapons" in sh["kinds"]:
		for iid in ids:
			var it: Dictionary = items[iid]
			if it["kind"] == "weapon" and int(it["tier"]) <= 5 and not it.has("line") and not it.has("src"):
				var ch: String = rules["weapon_tier_chapter"][str(int(it["tier"]))]
				if (ch == "CH01" or Game.chapter_done(ch)) and Game.is_recruited(it["owner"]):
					out.append(iid)
	if "armor" in sh["kinds"]:
		for iid in ids:
			var it: Dictionary = items[iid]
			if it["kind"] == "armor" and not it.has("line") and not it.has("src"):
				var ch2: String = rules["armor_tier_chapter"][str(int(it["tier"]))]
				if ch2 == "CH01" or Game.chapter_done(ch2):
					out.append(iid)
	if "accessories" in sh["kinds"] or "items" in sh["kinds"]:
		for aid in rules["accessory_chapter"]:
			if Game.chapter_done(rules["accessory_chapter"][aid]):
				out.append(aid)
	# regional line: this town's specialist stock (docs expansion design, Phase 2)
	for iid in ids:
		var it3: Dictionary = items[iid]
		if it3.get("shop_town", "") == sh.get("town", "") and Game.chapter_done(it3["chapter"]):
			if it3["kind"] != "weapon" or Game.is_recruited(it3["owner"]):
				out.append(iid)
	# expansion region tiers (systems s2): the region's shops stock its tier once it is reachable
	for iid in Game.tier_stock(shop_id):
		if not out.has(iid):
			out.append(iid)
	# extra stock (sys s4: the Waylamp in three shops)
	for xid in sh.get("extra", []):
		if not out.has(xid):
			out.append(xid)
	# ore at the smiths
	var g: Dictionary = Content.data.get("gear", {})
	if g.get("smith_shops", []).has(shop_id):
		for oid in g.get("ore_stock", {}):
			var ch3: String = g["ore_stock"][oid]
			if ch3 == "CH01" or Game.chapter_done(ch3):
				out.append(oid)
	return out

func is_smith(shop_id: String) -> bool:
	return Content.data.get("gear", {}).get("smith_shops", []).has(shop_id)

func _shop_menu() -> void:
	page = "shop"
	var sid: String = data["id"]
	var sh: Dictionary = Content.data["shops"].get(sid, {"name": "Shop"})
	var opts = [{"text": "Buy", "value": "buy"}, {"text": "Sell", "value": "sell"}]
	if is_smith(sid):
		opts.append({"text": "Upgrade", "value": "smith"})
	opts.append({"text": "Leave", "value": "leave"})
	var m = _menu(opts, Rect2(4, 4, 96, 22 + 11 * opts.size()), opts.size(), sh["name"])
	info_draw = func(): _shop_info(null)
	m.chosen.connect(func(_i, it):
		if it["value"] == "buy":
			_shop_list(sid, true)
		elif it["value"] == "sell":
			_shop_list(sid, false)
		elif it["value"] == "smith":
			_smith_list()
		else:
			_close_all())

## Blacksmith: raise a weapon or body armour +1..+3 (ore + crowns). Upgrades apply to every copy of that item.
func _smith_list() -> void:
	var m = _menu([], Rect2(4, 60, 196, 176), 15, "")
	var refresh = func(mm: MenuList):
		var items = []
		var seen = {}
		var ids: Array = Game.S["inventory"]["items"].keys()
		for cid in Game.S["party"]["roster"]:
			for sl in Game.member(cid)["equip"]:
				ids.append(Game.member(cid)["equip"][sl])
		ids.sort()
		for iid in ids:
			if iid == "" or seen.has(iid):
				continue
			seen[iid] = true
			var it = Content.item(iid)
			if not (it.get("kind", "") == "weapon" or (it.get("kind", "") == "armor" and it.get("slot", "") == "body")):
				continue
			var c = Game.upgrade_cost(iid)
			items.append({"icon": iid, "text": Content.item_name(iid), "right": str(c["gold"]) if not c.is_empty() else "MAX", "value": iid,
				"enabled": not c.is_empty(), "reason": T.s("gm.fully_upgraded", "Fully upgraded")})
		mm.items = items
		mm.index = clampi(mm.index, 0, maxi(0, items.size() - 1))
		info_draw = func(): _smith_info(mm)
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		var r = Game.upgrade(it["value"])
		if r["ok"]:
			Audio.sfx("FX006")
			flash_msg(T.s("gm.s_is_now_d", "%s is now +%d.") % [Content.item(it["value"])["name"], r["level"]])
		else:
			flash_msg(r["reason"])
		refresh.call(m))

func _smith_info(m) -> void:
	UI.win(self, Rect2(104, 4, 212, 52))
	UI.label(self, Vector2(111, 8), T.s("gm.crowns", "Crowns"))
	UI.text_right(self, 308, 8, str(Game.gold()), UI.C_TEXT)
	UI.text(self, Vector2(111, 22), T.s("gm.each_upgrade_adds_8_to", "Each upgrade adds 8% to its stats."), UI.C_TEXT)
	UI.win(self, Rect2(204, 60, 112, 176))
	var it: Dictionary = m.current()
	if it.is_empty():
		UI.text(self, Vector2(211, 66), T.s("gm.nothing_to_upgrade", "Nothing to upgrade."), UI.C_DIM)
		return
	var iid: String = it["value"]
	UI.icon(self, Vector2(211, 66), iid, 24)
	var d = Content.item(iid)
	var y = 94
	var c = Game.upgrade_cost(iid)
	var lv = Game.upgrade_level(iid)
	UI.stat(self, Vector2(211, y), T.s("gm.level", "Level"), "+%d" % lv, 308)
	y += 13
	var step = float(Content.data["gear"]["step"])
	for k in [["atk", "ATK"], ["mag", "MAG"], ["def", "DEF"], ["res", "RES"]]:
		if d.has(k[0]):
			var now = int(round(float(d[k[0]]) * (1.0 + step * lv)))
			var nxt = int(round(float(d[k[0]]) * (1.0 + step * (lv + 1))))
			UI.label(self, Vector2(211, y), k[1])
			UI.text_right(self, 262, y, str(now))
			if not c.is_empty():
				UI.text(self, Vector2(266, y), "→", UI.C_LABEL)
				UI.text_right(self, 308, y, str(nxt), UI.C_GREEN if nxt > now else UI.C_TEXT)
			y += 11
	if not c.is_empty():
		y += 6
		UI.label(self, Vector2(211, y), T.s("gm.needs", "Needs"))
		y += 12
		var have = Game.count(c["ore"])
		UI.icon(self, Vector2(211, y), c["ore"], 11)
		UI.text(self, Vector2(225, y), T.s("gm.s_x_d", "%s x%d") % [Content.item(c["ore"])["name"], c["n"]], UI.C_TEXT if have >= c["n"] else UI.C_RED)
		y += 11
		UI.text(self, Vector2(225, y), T.s("gm.have_d", "(have %d)") % have, UI.C_DIM)
		y += 11
		UI.text(self, Vector2(225, y), T.s("gm.d_crowns", "%d crowns") % c["gold"], UI.C_TEXT if Game.gold() >= c["gold"] else UI.C_RED)

func _shop_list(sid: String, buying: bool) -> void:
	var m = _menu([], Rect2(4, 60, 196, 176), 15, "")
	var refresh = func(mm: MenuList):
		var items = []
		if buying:
			for iid in shop_stock(sid):
				var it = Content.item(iid)
				var price = int(it["price"])
				var ok = Game.gold() >= price and Game.count(iid) < Game.STACK_CAP
				items.append({"icon": iid, "text": it["name"], "right": str(price), "value": iid, "enabled": ok, "reason": T.s("gm.not_enough_crowns", "Not enough crowns") if Game.gold() < price else "Stack full"})
		else:
			for iid in Game.S["inventory"]["items"]:
				var it2 = Content.item(iid)
				var ok2: bool = it2.get("sellable", false)
				items.append({"icon": iid, "text": Content.item_name(iid), "right": str(int(it2.get("price", 0)) / 2), "value": iid, "enabled": ok2, "reason": T.s("gm.cannot_be_sold", "Cannot be sold")})
		mm.items = items
		mm.index = clampi(mm.index, 0, maxi(0, items.size() - 1))
		info_draw = func(): _shop_info(mm)
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		var iid: String = it["value"]
		if buying:
			var r = Game.buy(iid, 1, int(Content.item(iid)["price"]))
			if r["ok"]:
				Audio.sfx("FX006")
			else:
				flash_msg(r["reason"])
		else:
			var r2 = Game.sell(iid, 1)
			if r2["ok"]:
				Audio.sfx("FX006")
			else:
				flash_msg(r2["reason"])
		refresh.call(m))

func _shop_info(m) -> void:
	UI.win(self, Rect2(104, 4, 212, 52))
	UI.label(self, Vector2(111, 8), T.s("gm.crowns", "Crowns"))
	UI.text_right(self, 308, 8, str(Game.gold()), UI.C_TEXT)
	UI.win(self, Rect2(204, 60, 112, 176))
	if m == null:
		UI.text(self, Vector2(111, 22), T.s("gm.welcome_take_a_look", "Welcome. Take a look."), UI.C_TEXT)
		return
	var it: Dictionary = m.current()
	if it.is_empty():
		return
	var iid: String = it["value"]
	var d = Content.item(iid)
	var dl = UI.wrap(d.get("desc", ""), 196)
	for i in range(mini(2, dl.size())):
		UI.text(self, Vector2(111, 20 + i * 11), dl[i])
	var y = 65
	var ix = 211
	if UI.icon(self, Vector2(211, 65), iid, 24):
		ix = 239
	UI.stat(self, Vector2(ix, y), T.s("gm.owned", "Owned"), str(Game.count(iid)), 308)
	y += 11
	UI.stat(self, Vector2(ix, y), T.s("gm.worn", "Worn"), str(Game.equipped_count(iid)), 308)
	y = 94
	if d.has("atk"):
		UI.stat(self, Vector2(211, y), T.s("gm.atk", "ATK"), str(int(d["atk"])), 250)
		UI.stat(self, Vector2(258, y), T.s("gm.mag", "MAG"), str(int(d["mag"])), 308)
		y += 11
	if d.has("def"):
		UI.stat(self, Vector2(211, y), T.s("gm.def", "DEF"), str(int(d["def"])), 250)
		UI.stat(self, Vector2(258, y), T.s("gm.res", "RES"), str(int(d["res"])), 308)
		y += 11
	if d.get("kind", "") in ["weapon", "armor", "accessory"]:
		# per-member comparison against what each one wears now (FF-style arrows)
		y += 3
		UI.label(self, Vector2(211, y), T.s("gm.party", "Party"))
		y += 12
		var slot: String = "weapon" if d["kind"] == "weapon" else ("acc1" if d["kind"] == "accessory" else str(d.get("slot", "body")))
		for cid in Game.S["party"]["roster"]:
			if y > 222:
				break
			var nm: String = Game.char_name(cid).split(" ")[0]
			var can: bool = d.get("allowed", []).has(cid) and (d["kind"] != "weapon" or d.get("owner", cid) == cid)
			UI.text(self, Vector2(211, y), nm, UI.C_TEXT if can else UI.C_DIM)
			if not can:
				UI.text_right(self, 308, y, "-", UI.C_DIM)
			else:
				var mem = Game.member(cid).duplicate(true)
				var worn: String = mem["equip"].get(slot, "")
				if worn == iid:
					UI.text_right(self, 308, y, "worn", UI.C_LABEL)
				else:
					var cur = Game.stats(cid)
					mem["equip"][slot] = iid
					if slot == "weapon" and d.get("two_handed", false):
						mem["equip"].erase("offhand")
					var nw = Game.stats_for(cid, mem)
					var keys = [["atk", "ATK"], ["matk", "MAG"]] if d["kind"] == "weapon" else [["def", "DEF"], ["res", "RES"]]
					var best = keys[0]
					if abs(int(nw[keys[1][0]]) - int(cur[keys[1][0]])) > abs(int(nw[keys[0][0]]) - int(cur[keys[0][0]])):
						best = keys[1]
					var dv: int = int(nw[best[0]]) - int(cur[best[0]])
					if d["kind"] == "accessory":
						UI.text_right(self, 308, y, "can wear", UI.C_TEXT)
					elif dv == 0:
						UI.text_right(self, 308, y, "%s =" % best[1], UI.C_TEXT)
					else:
						UI.text_right(self, 308, y, "%s %s%d" % [best[1], "+" if dv > 0 else "", dv], UI.C_GREEN if dv > 0 else UI.C_RED)
			y += 11
	elif dl.size() > 2:
		for ln in UI.wrap(" ".join(dl.slice(2)), 98).slice(0, 8):
			UI.text(self, Vector2(211, y), ln, UI.C_DIM)
			y += 11

func _inn_menu() -> void:
	page = "inn"
	var price: int = int(data.get("price", -1))
	if price < 0:
		price = F.inn_price(Game.S["party"]["roster"].size())
		price = Game.inn_price_for(str(main.field.map.get("region", "")) if main != null and main.field != null else "", price)
	# sleeping moves the world clock (field systems s3): Rest keeps the hour, the two sleeps wake at 06:00 / 18:00
	var m = _menu([{"text": "Rest (%d crowns)" % price if price > 0 else "Rest (free)", "value": 1, "enabled": Game.gold() >= price, "reason": "Not enough crowns"},
		{"text": "Sleep until morning", "value": 2, "enabled": Game.gold() >= price, "reason": "Not enough crowns"},
		{"text": "Sleep until evening", "value": 3, "enabled": Game.gold() >= price, "reason": "Not enough crowns"},
		{"text": "Leave", "value": 0}], Rect2(100, 80, 140, 62), 4, "")
	m.chosen.connect(func(_i, it):
		if it["value"] >= 1 and Game.spend_gold(price):
			Game.heal_all()
			Game.S["vars"]["inn_rests"] = int(Game.S["vars"].get("inn_rests", 0)) + 1
			if it["value"] >= 2:
				FieldSys.sleep_until("morning" if it["value"] == 2 else "evening")
			var jl = Audio.jingle("inn")
			if jl <= 0.0:
				Audio.music("M029", 0.0)
			flash_msg(T.s("gm.the_party_rests", "The party rests."))
			await get_tree().create_timer(maxf(1.2, jl)).timeout
			Audio.current_cue = ""
			Audio.music(main.field.map.get("music", ""), 0.5)
		_close_all())

# ======================================================================
# Two-party split for the final dungeon
# ======================================================================
func _split_menu() -> void:
	page = "split"
	split_teams = {"A": [], "B": []}
	var avail = Game.available_members()
	# teams of five (fewer if the roster is small); anyone else waits in reserve at the recovery point
	var need: int = mini(Game.PARTY_MAX, avail.size() / 2)
	for i in range(avail.size()):
		if i < need:
			split_teams["A"].append(avail[i])
		elif i < need * 2:
			split_teams["B"].append(avail[i])
	var m = _menu([], Rect2(4, 4, 150, 150), 11, "West (A) / East (B)")
	var refresh = func(mm: MenuList):
		var items = []
		for cid in avail:
			var team = "A" if split_teams["A"].has(cid) else ("B" if split_teams["B"].has(cid) else "-")
			items.append({"text": Game.short_name(cid), "right": team, "value": cid})
		var ok: bool = split_teams["A"].size() == need and split_teams["B"].size() == need
		items.append({"text": "Confirm teams", "value": "__ok", "enabled": ok, "reason": T.s("gm.each_team_needs_d", "Each team needs %d") % need})
		mm.items = items
		info_draw = func():
			UI.win(self, Rect2(158, 4, 158, 150))
			var y = 8
			for tm in ["A", "B"]:
				UI.text(self, Vector2(164, y), T.s("gm.team", "Team ") + tm + (" (west)" if tm == "A" else " (east)"), UI.C_GOLD)
				y += 11
				var heal = false
				for cid in split_teams[tm]:
					UI.text(self, Vector2(170, y), Game.short_name(cid))
					y += 10
					for a in Game.learned_abilities(cid):
						if Content.ability(a).get("kind", "") == "heal":
							heal = true
				if not heal and not split_teams[tm].is_empty():
					UI.text(self, Vector2(164, y), T.s("gm.no_healer_bring_tonics", "No healer: bring Tonics."), UI.C_HI)
					y += 11
				y += 4
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		if it["value"] == "__ok":
			Game.S["vars"]["team_a"] = 0
			Game.S["teams"] = split_teams.duplicate(true)
			_close_all()
			return
		var cid: String = it["value"]
		# cycle A -> B -> reserve -> A
		if split_teams["A"].has(cid):
			split_teams["A"].erase(cid)
			split_teams["B"].append(cid)
		elif split_teams["B"].has(cid):
			split_teams["B"].erase(cid)
		else:
			split_teams["A"].append(cid)
		refresh.call(m))
	m.allow_cancel = false

func _clear_save_menu() -> void:
	page = "save"
	var m = _menu(_slot_items(), Rect2(4, 4, 150, 232), 19, T.s("save.clear_title"))
	info_draw = func(): _slot_info_draw(m)
	m.chosen.connect(func(_i, it):
		var do_save = func():
			Game.save_slot(it["value"])
			Audio.sfx("FX006")
			_close_all()
		if it.get("empty", false):
			do_save.call()
		else:
			_confirm("Overwrite slot %d?" % it["value"], do_save))

# ======================================================================
# Records (sys s4): achievements, fish log, statistics
# ======================================================================
func _records_menu() -> void:
	page = "records"
	var items = [{"text": T.s("records.achievements"), "value": "achv"}, {"text": T.s("records.fish"), "value": "fish"},
		{"text": T.s("records.stats"), "value": "stats"}, {"text": T.s("records.bonds", "Bonds"), "value": "bonds"},
		{"text": T.s("records.ranches", "Ranches"), "value": "ranch"}]
	var m = _menu(items, Rect2(4, 4, 110, 22 + 11 * items.size()), items.size(), T.s("records.title"))
	var prev = func():
		UI.win(self, Rect2(118, 4, 198, 60))
		UI.text(self, Vector2(125, 9), T.f("achv.title", [Achievements.unlocked_count(), Achievements.defs().size()]))
		UI.text(self, Vector2(125, 21), T.f("fish.log_title", [Game.S.get("fish", {}).get("log", {}).size(), FishCore.data().get("fish", {}).size()]))
		UI.gauge(self, Rect2(125, 36, 184, 6), float(Achievements.unlocked_count()) / maxf(1.0, Achievements.defs().size()), UI.C_GOLD)
		UI.gauge(self, Rect2(125, 46, 184, 6), float(Game.S.get("fish", {}).get("log", {}).size()) / maxf(1.0, FishCore.data().get("fish", {}).size()), UI.C_BLUE)
	info_draw = prev
	m.set_meta("refresh", func(_mm): page = "records"; info_draw = prev)
	m.chosen.connect(func(_i, it): _records_open(str(it["value"])))

func _records_open(v: String) -> void:
	match v:
		"achv": _achievements_page()
		"fish": _fish_log_page()
		"stats": _stats_page()
		"bonds": _bonds_page()
		"ranch": _ranch_page()

## Records > Ranches (meta/ranch.gd): each ranch's beds, beasts (affection hearts), nest and rail kart.
func _ranch_page() -> void:
	page = "records"
	var items = Ranch.record_rows()
	var m = _menu(items, Rect2(4, 4, 150, mini(232, 22 + 11 * maxi(1, items.size()))), maxi(1, items.size()), T.s("records.ranches", "Ranches"))
	var draw_it = func():
		UI.win(self, Rect2(158, 4, 158, 232))
		var rid: String = str(m.current().get("value", ""))
		if rid == "":
			return
		Ranch.draw_record(self, rid, Rect2(158, 4, 158, 232))   # beds, beasts and hearts, nest, kart
	info_draw = draw_it
	m.set_meta("refresh", func(_mm): page = "records"; info_draw = draw_it)

func _bonds_page() -> void:
	page = "records"
	var items = []
	for row in Bonds.listing():
		items.append({"text": "%s & %s" % [Game.short_name(row[0]), Game.short_name(row[1])], "value": row})
	if items.is_empty():
		items.append({"text": T.s("bonds.none", "No bonds yet."), "value": [], "enabled": false})
	var m = _menu(items, Rect2(4, 4, 176, 232), 19, T.s("records.bonds", "Bonds"))
	var draw_it = func():
		UI.win(self, Rect2(184, 4, 132, 92))
		var cur: Dictionary = m.current() if m.has_method("current") else {}
		var row = cur.get("value", [])
		if typeof(row) != TYPE_ARRAY or row.size() < 4:
			UI.text(self, Vector2(191, 9), T.s("bonds.hint", "Fight side by side."), UI.C_DIM)
			return
		UI.text(self, Vector2(191, 9), "Bond %d / 5" % int(row[3]))
		var lo = 0 if int(row[3]) == 0 else Bonds.LEVELS[int(row[3]) - 1]
		var hi = Bonds.LEVELS[mini(int(row[3]), 4)]
		UI.gauge(self, Rect2(191, 24, 118, 6), 1.0 if int(row[3]) >= 5 else float(int(row[2]) - lo) / maxf(1.0, hi - lo), UI.C_GOLD)
		UI.text(self, Vector2(191, 36), "+%d%% together" % int(round(100.0 * minf(Bonds.PCT_CAP, Bonds.PCT_PER_LEVEL * int(row[3])))), UI.C_LABEL)
		var seen = 0
		for s in Bonds.SCENE_LEVELS:
			if Game.event_applied(Bonds.scene_id(row[0], row[1], s)):
				seen += 1
		UI.text(self, Vector2(191, 50), "Talks heard: %d" % seen, UI.C_TEXT)
	info_draw = draw_it
	m.set_meta("refresh", func(_mm): page = "records"; info_draw = draw_it)

func _achievements_page() -> void:
	page = "records"
	var items = []
	var defs = Achievements.defs()
	for id in Achievements.order():
		var d: Dictionary = defs[id]
		var got = Achievements.is_unlocked(id)
		var hide = d.get("hidden", false) and not got
		var pr = Achievements.progress(id)
		var right = "OK" if got else ("%d/%d" % [int(pr[0]), int(pr[1])] if not pr.is_empty() and not hide else "")
		items.append({"text": T.s("common.unknown") if hide else str(d["name"]), "right": right, "value": id,
			"color": UI.C_GOLD if got else UI.C_TEXT})
	var m = _menu(items, Rect2(4, 4, 176, 232), 19, T.f("achv.title", [Achievements.unlocked_count(), defs.size()]))
	info_draw = func():
		var r = Rect2(184, 4, 132, 232)
		UI.win(self, r)
		var id: String = m.current().get("value", "")
		if id == "":
			return
		var d: Dictionary = defs[id]
		var got = Achievements.is_unlocked(id)
		var hide = d.get("hidden", false) and not got
		var y = 9
		UI.label(self, Vector2(191, y), str(d.get("group", "")))
		y += 12
		for ln in UI.wrap(T.s("achv.hidden") if hide else str(d["name"]), 118):
			UI.text(self, Vector2(191, y), ln, UI.C_GOLD if got else UI.C_TEXT)
			y += 11
		y += 4
		for ln in UI.wrap(T.s("achv.hidden_desc") if hide else str(d.get("desc", "")), 118):
			UI.text(self, Vector2(191, y), ln)
			y += 11
		y += 6
		var pr = Achievements.progress(id)
		if not pr.is_empty() and not hide:
			UI.label(self, Vector2(191, y), T.s("achv.progress"))
			UI.text_right(self, 309, y, "%d / %d" % [int(pr[0]), int(pr[1])])
			y += 12
			UI.gauge(self, Rect2(191, y, 118, 6), 1.0 if got else pr[0] / maxf(1.0, pr[1]), UI.C_GOLD if got else UI.C_BLUE)
			y += 12
		if got:
			var when = str(Achievements._profile.get("achievements", {}).get(id, ""))
			UI.text(self, Vector2(191, y), T.f("achv.unlocked", [when.replace("T", " ").substr(0, 10)]) if when != "" else "OK", UI.C_GREEN)

func _fish_log_page() -> void:
	page = "records"
	var fd: Dictionary = FishCore.data().get("fish", {})
	var ids: Array = fd.keys()
	ids.sort()
	var log: Dictionary = Game.S.get("fish", {}).get("log", {})
	var items = []
	for fid in ids:
		var e: Dictionary = log.get(fid, {})
		var known = int(e.get("n", 0)) > 0
		items.append({"text": str(fd[fid]["name"]) if known else T.s("common.unknown"), "right": str(e.get("n", "")) if known else "", "value": fid,
			"color": UI.C_TEXT if known else UI.C_DIM})
	var m = _menu(items, Rect2(4, 4, 150, 232), 19, T.f("fish.log_title", [log.size(), fd.size()]))
	info_draw = func():
		var r = Rect2(158, 4, 158, 232)
		UI.win(self, r)
		var fid: String = m.current().get("value", "")
		if fid == "":
			return
		var f: Dictionary = fd[fid]
		var e: Dictionary = log.get(fid, {})
		var known = int(e.get("n", 0)) > 0
		UI.inset(self, Rect2(164, 10, 36, 36))
		if known:
			FishingGame.draw_icon(self, Vector2(166, 12), int(f["icon"]), 2.0)
		else:
			UI.text(self, Vector2(178, 22), "?", UI.C_DIM)
		UI.text(self, Vector2(206, 10), str(f["name"]) if known else T.s("fish.unknown"), UI.C_GOLD if known else UI.C_DIM)
		UI.text(self, Vector2(206, 22), T.s("fish.rare.%d" % int(f["rarity"])), UI.C_HI if int(f["rarity"]) >= 3 else UI.C_TEXT)
		if UI.cues_on():
			UI.text(self, Vector2(206, 33), "*".repeat(int(f["rarity"])), UI.C_HI)
		var y = 52
		UI.label(self, Vector2(165, y), T.s("fish.where"))
		y += 11
		var names = []
		for tb in f["tables"]:
			names.append(T.s("fish.table." + str(tb), str(tb).capitalize()))
		for ln in UI.wrap(", ".join(names), 144):
			UI.text(self, Vector2(170, y), ln)
			y += 11
		if f.get("night", false):
			UI.text(self, Vector2(165, y), T.s("fish.night"), UI.C_BLUE)
			y += 11
		y += 4
		if known:
			UI.stat(self, Vector2(165, y), T.s("fish.caught"), str(e["n"]), 309)
			y += 11
			UI.stat(self, Vector2(165, y), T.s("fish.best"), "%.1f cm" % float(e.get("best", 0.0)), 309)
			y += 11
			UI.text_right(self, 309, y, "%.2f kg" % float(e.get("kg", 0.0)), UI.C_DIM)
			y += 15
			for ln in UI.wrap(str(f.get("note", "")), 144).slice(0, 6):
				UI.text(self, Vector2(165, y), ln, UI.C_DIM)
				y += 11

func _stats_page() -> void:
	page = "records"
	var rows = [["records.stat.playtime", Game.fmt_time(Game.S.get("playtime", 0.0))], ["records.stat.battles", str(Game.stat("battles"))],
		["records.stat.bosses", str(Game.stat("boss_wins"))], ["records.stat.nokos", str(Game.stat("boss_nokos"))],
		["records.stat.superbosses", str(Game.stat("superbosses"))], ["records.stat.bestiary", "%d%%" % int(Achievements.meta_value("bestiary_pct"))],
		["records.stat.chests", str(Game.S.get("chests", []).size())], ["records.stat.fish", str(Game.stat("fish_caught"))],
		["records.stat.crafted", str(Game.stat("crafted"))], ["records.stat.saves", str(Game.stat("saves"))],
		["records.stat.ng", str(int(Game.S.get("ng", 0)))]]
	rows.push_front(["records.stat.completion", "%d%%" % Completion.percent()])
	for cp in Completion.parts():
		if cp[0] != "Bestiary":
			rows.append([str(cp[0]), "%d / %d" % [cp[1], cp[2]]])
	var items = []
	for r in rows:
		items.append({"text": T.s(r[0], r[0]) if r[0] != "records.stat.completion" else T.s(r[0], "Completion"), "right": r[1], "value": r[0]})
	var m = _menu(items, Rect2(4, 4, 200, mini(232, 22 + 11 * items.size())), mini(items.size(), 19), T.s("records.stats"))
	info_draw = func(): pass
