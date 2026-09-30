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

const MAIN_ITEMS := ["Items", "Equipment", "Abilities", "Formation", "Vestiges", "Journal", "World Map", "Bestiary", "Settings", "Save", "Quit", "Close"]

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
		var it = {"text": n, "value": n}
		if n == "Save" and not can_save:
			it["enabled"] = false
			it["reason"] = "Save at a lamp, on the world map or aboard ship"
		if n == "Vestiges" and Game.S.get("vestiges", []).is_empty():
			it["enabled"] = false
			it["reason"] = "No Vestiges yet"
		if n == "Formation" and Game.S["party"].get("locked", false):
			it["enabled"] = false
			it["reason"] = "Formation fixed by the current situation"
		items.append(it)
	var m = _menu(items, Rect2(232, 4, 84, 142), 12)
	m.memory_key = "main_menu"
	m.chosen.connect(_on_main_choice)
	m.set_meta("refresh", func(_m): page = "main"; info_draw = Callable())
	info_draw = Callable()

func _on_main_choice(_i: int, it: Dictionary) -> void:
	match it["value"]:
		"Items": _items_menu()
		"Equipment": _pick_member(func(cid): _equip_menu(cid), "Equip whom?")
		"Abilities": _pick_member(func(cid): _abilities_menu(cid), "Whose techniques?")
		"Formation": _formation_menu()
		"Vestiges": _vestige_menu()
		"Journal": _journal()
		"World Map": _worldmap()
		"Bestiary": _bestiary()
		"Settings": _settings_menu()
		"Save": _save_menu(false)
		"Quit": _confirm("Quit to title without saving?", func():
			_close_all()
			main.to_title())
		"Close": _close_all()

func _draw() -> void:
	draw_rect(Rect2(0, 0, 320, 240), Color(0.02, 0.02, 0.08, 0.45))
	if page == "main" or page == "pick":
		_draw_party_panel(Rect2(4, 4, 224, 196))
		# time / money box under the command column
		UI.win(self, Rect2(232, 150, 84, 50))
		UI.label(self, Vector2(239, 154), "Time")
		UI.text_right(self, 309, 164, Game.fmt_time(Game.S.get("playtime", 0.0)))
		UI.label(self, Vector2(239, 176), "Crowns")
		UI.text_right(self, 309, 186, str(Game.gold()))
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
		UI.label(self, Vector2(r.position.x + 9, y), "Reserve / away")
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
	UI.label(self, Vector2(p.x + 134, p.y), "LV")
	UI.text_right(self, p.x + 162, p.y, str(m["level"]))
	UI.text(self, Vector2(p.x + 170, p.y), "[" + Game.row(cid).substr(0, 1).to_upper() + "]", UI.C_DIM)
	var hpc = UI.C_TEXT if hp > s["mhp"] / 4 else (UI.C_HI if hp > 0 else UI.C_RED)
	UI.label(self, Vector2(x, p.y + 11), "HP")
	UI.text_right(self, p.x + 122, p.y + 11, "%d/%d" % [hp, s["mhp"]], hpc)
	UI.label(self, Vector2(x, p.y + 21), "MP")
	UI.text_right(self, p.x + 122, p.y + 21, "%d/%d" % [mp, s["mmp"]])
	var need = F.xp_total_for_level(int(m["level"]) + 1) - int(m["xp"])
	UI.label(self, Vector2(p.x + 134, p.y + 11), "Next")
	UI.text_right(self, p.x + 210, p.y + 11, str(maxi(0, need)))
	var link = Game.link_of(cid)
	if link != "":
		UI.text(self, Vector2(p.x + 134, p.y + 21), Content.data["vestiges"][link]["name"], Color8(240, 170, 230))

func _pick_member(cb: Callable, title: String, only_available: bool = true) -> void:
	var items = []
	for cid in Game.S["party"]["roster"]:
		var ok = Game.is_available(cid) or not only_available
		items.append({"text": Game.char_name(cid), "value": cid, "enabled": ok, "reason": "Away from the party"})
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
			return ["consumable", "weapon", "armor", "accessory", "key"].find(ka) < ["consumable", "weapon", "armor", "accessory", "key"].find(kb))
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
			flash_msg("Claimed %d item(s)." % got.size())
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
		UI.text(self, Vector2(11, 9), "Items sent on by couriers. Confirm to claim.")
		return
	var d = Content.item(it.get("value", ""))
	var dl = UI.wrap(d.get("desc", ""), 296)
	for i in range(mini(2, dl.size())):
		UI.text(self, Vector2(11, 9 + i * 11), dl[i])
	var y = 47
	UI.icon(self, Vector2(284, 46), it.get("value", ""), 24)
	UI.label(self, Vector2(215, y), d.get("kind", "").capitalize())
	y += 12
	UI.label(self, Vector2(215, y), "Owned")
	UI.text_right(self, 308, y, str(Game.count(it.get("value", ""))))
	y += 11
	if d.get("kind", "") in ["weapon", "armor"]:
		y += 4
		if d.has("atk"):
			UI.stat(self, Vector2(215, y), "ATK", str(int(d["atk"])), 250)
			UI.stat(self, Vector2(258, y), "MAG", str(int(d["mag"])), 308)
			y += 11
		if d.has("def"):
			UI.stat(self, Vector2(215, y), "DEF", str(int(d["def"])), 250)
			UI.stat(self, Vector2(258, y), "RES", str(int(d["res"])), 308)
			y += 11
	if dl.size() > 2:
		y += 4
		for ln in UI.wrap(" ".join(dl.slice(2)), 94).slice(0, 6):
			UI.text(self, Vector2(215, y), ln, UI.C_DIM)
			y += 11
	if d.get("kind", "") == "consumable" and not d.get("field", false):
		UI.text(self, Vector2(215, 220), "Battle only", UI.C_DIM)
	elif d.get("kind", "") == "consumable":
		UI.text(self, Vector2(215, 220), "Usable now", UI.C_GREEN)

func _use_item_field(iid: String, done: Callable) -> void:
	var d = Content.item(iid)
	if d.get("special", "") == "tent":
		if not (main.field.map.get("save_ok", false) or main.field.map.get("kind", "") == "world"):
			flash_msg("Use a Travel Tent at a lamp or on the world map.")
			return
		Game.remove_item(iid)
		Game.heal_all()
		Audio.sfx("FX022")
		flash_msg("The party rests.")
		done.call()
		return
	if d.get("special", "") == "waystone":
		var dg: String = String(main.field.map_id).substr(0, 3)
		if not Content.data["dungeons"].has(dg) or main.director.running:
			flash_msg("Waystones work only inside a dungeon.")
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
			flash_msg("It would have no effect."), "Use on whom?")

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
				reason = "Two-handed weapon"
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
			flash_msg("Equipped %d stronger item%s." % [n, "" if n == 1 else "s"] if n > 0 else "Already the strongest owned gear.")
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
		UI.text(self, Vector2(183, y), "Grants " + Content.ability(g)["name"], UI.C_GOLD)
		y += 11
	var pas: Dictionary = prev["passives"] if has_prev else cur["passives"]
	for k in pas:
		UI.text(self, Vector2(183, y), _passive_label(k, pas[k]), Color8(210, 190, 250))
		y += 11
		if y > 170:
			break
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
			return "Faster readiness"
		"mag_bonus":
			return "Magic up"
		"reserve_scale":
			return "Stronger with reserves"
		"auto_revive":
			return "Survives one fatal blow"
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
		items.append({"spell": l["id"] if has else "", "text": a["name"] if has else "Lv %d: ???" % l["level"], "right": str(int(a["mp"])) if has else "", "value": l["id"], "enabled": has and a.get("field", false), "reason": "Battle technique" if has else "Not yet learned", "desc": a["desc"] if has else ""})
	var ult = Content.ch(cid).get("ultimate")
	if ult != null:
		var has2 = learned.has(ult)
		items.append({"text": Content.ability(ult)["name"] if has2 else "Personal story: ???", "value": ult, "enabled": false, "reason": "Battle technique" if has2 else "Resolve their personal story", "desc": Content.ability(ult)["desc"] if has2 else ""})
	for vk in Game.S.get("vknown", {}).get(cid, []):
		var va = Content.ability(vk)
		items.append({"spell": vk, "text": va["name"], "right": str(int(va["mp"])), "value": vk, "enabled": va.get("field", false), "reason": "Battle magic", "desc": va["desc"] + " (Vestige magic)"})
	for g in st["grants"]:
		items.append({"spell": g, "text": Content.ability(g)["name"] + " (acc.)", "right": str(int(Content.ability(g)["mp"])), "value": g, "enabled": Content.ability(g).get("field", false), "reason": "Granted while equipped", "desc": Content.ability(g)["desc"]})
	var m = _menu(items, Rect2(4, 4, 200, 150), 12, Game.char_name(cid))
	info_draw = func():
		var it = m.current()
		UI.win(self, Rect2(4, 158, 312, 78))
		var y = 162
		UI.stat(self, Vector2(11, y), "MP", "%d/%d" % [Game.member(cid)["mp"], st["mmp"]], 80)
		y += 12
		for ln in UI.wrap(it.get("desc", it.get("reason", "")), 296).slice(0, 5):
			UI.text(self, Vector2(10, y), ln)
			y += 11
	m.chosen.connect(func(_i, it):
		var a = Content.ability(it["value"])
		var mem = Game.member(cid)
		if int(mem["mp"]) < int(a["mp"]):
			flash_msg("Not enough MP.")
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
				flash_msg("It would have no effect."), "Cast on whom?"))

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
		for i in range(order.size()):
			var cid: String = order[i]
			var tag = "Active" if i < act.size() else ("Reserve" if Game.is_available(cid) else "Away")
			var mark = "* " if i == swap_from else ""
			items.append({"text": mark + Game.short_name(cid), "right": "%s %s" % [tag, Game.row(cid).substr(0, 1).to_upper()], "value": cid,
				"enabled": Game.is_available(cid), "reason": "Away from the party"})
		mm.items = items
		info_draw = func():
			UI.win(self, Rect2(158, 4, 158, 150))
			var lines = UI.wrap("Confirm a member, then another to swap places. Press Page (Q/E) on a member to switch front/back row. The first five available are active.", 146)
			var y = 10
			for ln in lines:
				UI.text(self, Vector2(164, y), ln, UI.C_DIM)
				y += 11
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
			var a = Content.ability(vd["summon"])
			var y = 132
			for ln in UI.wrap(a["desc"] + " Costs 100 Concord; once per battle.", 296):
				UI.text(self, Vector2(10, y), ln)
				y += 11
			UI.text(self, Vector2(10, y), "Level-up bonus: " + str(vd.get("bonus_text", "-")), UI.C_GOLD)
			y += 12
			var holder_id = ""
			for k in Game.S["links"]:
				if k == it["value"]:
					holder_id = Game.S["links"][k]
			UI.label(self, Vector2(10, y), "Teaches" + (" (" + Game.short_name(holder_id) + ")" if holder_id != "" else ""))
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

func _bestiary() -> void:
	page = "best"
	var items = []
	for eid in Content.data["enemies"]:
		var e = Content.enemy(eid)
		if e.has("variant_of") or e["tags"].has("part"):
			continue
		var b: Dictionary = Game.S["bestiary"].get(eid, {})
		if b.get("seen", false):
			items.append({"text": e["name"], "value": eid, "right": str(b.get("defeated", 0))})
	if items.is_empty():
		items.append({"text": "(no entries)", "enabled": false})
	var m = _menu(items, Rect2(4, 4, 140, 232), 20, "Bestiary")
	info_draw = func():
		var it = m.current()
		UI.win(self, Rect2(148, 4, 168, 232))
		if not it.has("value"):
			return
		var e = Content.enemy(it["value"])
		var b: Dictionary = Game.S["bestiary"].get(it["value"], {})
		var tx: Texture2D = Content.load_art("res://assets/sprites/enemies/%s.png" % it["value"])
		var y = 8
		if tx:
			# frame 0 of the 4-frame sheet; large battlers (up to 160 px) are shown at 1/2 so the panel keeps its text
			var fw = tx.get_width() / 4
			var fh = tx.get_height()
			var k = 1.0 if (fw <= 156 and fh <= 80) else 0.5
			var dw = fw * k
			var dh = mini(int(fh * k), 80)
			draw_texture_rect_region(tx, Rect2(232 - dw / 2.0, y, dw, dh), Rect2(0, 0, fw, dh / k))
			y += dh + 4
		UI.text(self, Vector2(154, y), "Lv %d  HP %d" % [e["level"], e["hp"]])
		y += 12
		var wk = []
		for el in e["affinities"]:
			if b.get("affinity", false) or b.get("weak", []).has(el):
				wk.append("%s %s" % [UI.elem_label(el), e["affinities"][el]])
		UI.text(self, Vector2(154, y), ("Affinity: " + ", ".join(wk)) if not wk.is_empty() else "Affinity: unknown", UI.C_GOLD)
		y += 12
		if b.get("drops", false):
			UI.text(self, Vector2(154, y), "Steal: " + Content.item_name(e.get("steal", {}).get("common", "")), UI.C_DIM)
			y += 12
		for ln in UI.wrap(e.get("behavior", e.get("tell", "")), 156):
			UI.text(self, Vector2(154, y), ln)
			y += 11

# ======================================================================
# Settings (persist separately from saves) and key remapping
# ======================================================================
const SETTING_DEFS := [
	["difficulty", "Difficulty", ["easy", "normal", "hard"]],
	["battle_mode", "Battle mode", ["wait", "active"]],
	["battle_speed", "Battle speed", [0.75, 1.0, 1.25]],
	["text_speed", "Text speed", [0, 1, 2, 3]],
	["run_toggle", "Run", [false, true]],
	["encounters", "Encounters", ["normal", "reduced", "off"]],
	["ride_mount", "Ride Brackhorn", [true, false]],
	["reduced_flash", "Reduced flashes", [false, true]],
	["shake", "Screen shake", [true, false]],
	["short_summons", "Short summons", [false, true]],
	["vol_master", "Master volume", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]],
	["vol_music", "Music volume", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]],
	["vol_sfx", "Sound volume", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]],
	["pause_on_focus_loss", "Pause on focus loss", [true, false]],
	["fullscreen", "Fullscreen", [false, true]],
	["window_color", "Window colour", ["blue", "ash", "crimson", "verdant", "violet"]],
	["mature", "Mature content", [false, true]],
]

func _setting_value(k: String):
	if k == "difficulty":
		return Game.difficulty() if Game.playing else Settings.get_v("difficulty_default")
	return Settings.get_v(k)

func _setting_label(k: String, v) -> String:
	match k:
		"text_speed": return ["Slow", "Normal", "Fast", "Instant"][int(v)]
		"run_toggle": return "Toggle" if v else "Hold"
		"battle_speed": return "x%.2f" % float(v)
	if typeof(v) == TYPE_BOOL:
		return "On" if v else "Off"
	if typeof(v) == TYPE_FLOAT and k.begins_with("vol"):
		return "%d%%" % int(round(v * 100))
	return str(v).capitalize()

func _settings_menu() -> void:
	page = "settings"
	var m = _menu([], Rect2(4, 4, 312, 232), 18, "Settings  (Left/Right to change)")
	var refresh = func(mm: MenuList):
		var items = []
		for d in SETTING_DEFS:
			items.append({"text": d[1], "right": _setting_label(d[0], _setting_value(d[0])), "value": d[0]})
		for a in ["up", "down", "left", "right", "confirm", "cancel", "menu", "run"]:
			var ks = []
			for k in Settings.keys_for(a):
				ks.append(OS.get_keycode_string(int(k)))
			items.append({"text": "Key: " + a.capitalize(), "right": ", ".join(ks), "value": "key:" + a})
		items.append({"text": "Reset keys to default", "value": "reset_keys"})
		mm.items = items
		page = "settings"
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		var v: String = it["value"]
		if v == "reset_keys":
			Settings.reset_bindings()
			refresh.call(m)
		elif v.begins_with("key:"):
			rebinding = v.substr(4)
			flash_msg("Press a key for %s" % rebinding.capitalize())
		else:
			_cycle_setting(v, 1)
			refresh.call(m))
	m.set_meta("lr", func(dirn: int):
		var v: String = m.current().get("value", "")
		if not v.begins_with("key") and v != "reset_keys":
			_cycle_setting(v, dirn)
			refresh.call(m))

func _cycle_setting(k: String, dirn: int) -> void:
	for d in SETTING_DEFS:
		if d[0] == k:
			var opts: Array = d[2]
			var cur = _setting_value(k)
			var i = 0
			for j in range(opts.size()):
				if typeof(opts[j]) == typeof(cur) and opts[j] == cur:
					i = j
				elif typeof(cur) == TYPE_FLOAT and typeof(opts[j]) == TYPE_FLOAT and absf(opts[j] - cur) < 0.01:
					i = j
			i = (i + dirn + opts.size()) % opts.size()
			if k == "difficulty":
				if Game.playing:
					Game.S["difficulty"] = opts[i]
				Settings.set_v("difficulty_default", opts[i])
				Audio.ui("FX001")
				return
			if k == "mature" and opts[i] and not Settings.get_v("mature_ok"):
				_confirm("Mature content shows uncovered adult figures. It is meant for players aged 18 or older. Are you 18 or older?", func():
					Settings.set_v("mature_ok", true)
					Settings.set_v("mature", true)
					_refresh_top())
				return
			Settings.set_v(k, opts[i])
			if k == "fullscreen":
				get_window().mode = Window.MODE_FULLSCREEN if opts[i] else Window.MODE_WINDOWED
			if k == "encounters" and Game.playing:
				Game.S["play_settings"]["encounters"] = opts[i]
			Audio.ui("FX001")

func _input(event: InputEvent) -> void:
	if rebinding != "" and event is InputEventKey and event.pressed and not event.echo:
		Settings.rebind(rebinding, event.physical_keycode)
		rebinding = ""
		msg_t = 0
		_refresh_top()
		get_viewport().set_input_as_handled()
		return
	if lists.is_empty() or rebinding != "":
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
# Save / load
# ======================================================================
func _slot_items() -> Array:
	var items = []
	for s in range(1, Game.SLOTS + 1):
		var info = Game.slot_info(s)
		if info.get("ok", false):
			items.append({"text": "Slot %d  %s" % [s, info["chapter"]], "right": Game.fmt_time(info["playtime"]), "value": s, "info": info})
		elif info.get("reason", "") == "missing":
			items.append({"text": "Slot %d  (empty)" % s, "value": s, "empty": true})
		else:
			items.append({"text": "Slot %d  (%s)" % [s, info.get("reason", "?")], "value": s, "bad": info.get("reason", "")})
	return items

func _load_items() -> Array:
	var items = _slot_items()
	for pr in Game.PROTECTED:
		var path = Game.backup_path(pr[0])
		var info = Game.info_of(path)
		if info.get("ok", false):
			items.append({"text": pr[1], "right": Game.fmt_time(info["playtime"]), "value": -1, "path": path, "info": info})
	return items

func _slot_info_draw(m: MenuList) -> void:
	var it = m.current()
	UI.win(self, Rect2(4, 110, 312, 50))
	if it.has("info"):
		var i: Dictionary = it["info"]
		UI.text(self, Vector2(10, 114), "%s - Lv %d" % [i["location"], i["level"]])
		UI.text(self, Vector2(10, 126), "Saved %s" % str(i["date"]).replace("T", " "), UI.C_DIM)
		UI.text(self, Vector2(10, 138), "Playtime %s" % Game.fmt_time(i["playtime"]), UI.C_DIM)
	elif it.has("bad"):
		UI.text(self, Vector2(10, 114), "This save cannot be read (%s)." % it["bad"], UI.C_RED)
		UI.text(self, Vector2(10, 126), "A backup may be offered when you load it.", UI.C_DIM)

func _save_menu(at_point: bool) -> void:
	page = "save"
	var m = _menu(_slot_items(), Rect2(4, 4, 312, 100), 4, "Save to which slot?")
	info_draw = func(): _slot_info_draw(m)
	m.chosen.connect(func(_i, it):
		var do_save = func():
			var r = Game.save_slot(it["value"])
			if r["ok"]:
				Audio.sfx("FX006")
				flash_msg("Saved.")
				m.items = _slot_items()
			else:
				flash_msg("Save failed: " + r["reason"])
		if it.get("empty", false):
			do_save.call()
		else:
			_confirm("Overwrite slot %d?" % it["value"], do_save))

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
	var m = _menu(_load_items(), Rect2(4, 4, 312, 100), 4, "Load which slot?")
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
			flash_msg("This save is from a newer version (%s)." % str(r.get("version", "")))
		elif r.get("backup_ok", false):
			_confirm("Save damaged. Load its backup?", func():
				var rb = Game.load_backup_of(path)
				if rb["ok"]:
					_close_all()
					main.continue_from_state())
		else:
			flash_msg("Save damaged; no usable backup."))

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
			if it["kind"] == "weapon" and int(it["tier"]) <= 5 and not it.has("line"):
				var ch: String = rules["weapon_tier_chapter"][str(int(it["tier"]))]
				if (ch == "CH01" or Game.chapter_done(ch)) and Game.is_recruited(it["owner"]):
					out.append(iid)
	if "armor" in sh["kinds"]:
		for iid in ids:
			var it: Dictionary = items[iid]
			if it["kind"] == "armor" and not it.has("line"):
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
				"enabled": not c.is_empty(), "reason": "Fully upgraded"})
		mm.items = items
		mm.index = clampi(mm.index, 0, maxi(0, items.size() - 1))
		info_draw = func(): _smith_info(mm)
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		var r = Game.upgrade(it["value"])
		if r["ok"]:
			Audio.sfx("FX006")
			flash_msg("%s is now +%d." % [Content.item(it["value"])["name"], r["level"]])
		else:
			flash_msg(r["reason"])
		refresh.call(m))

func _smith_info(m) -> void:
	UI.win(self, Rect2(104, 4, 212, 52))
	UI.label(self, Vector2(111, 8), "Crowns")
	UI.text_right(self, 308, 8, str(Game.gold()), UI.C_TEXT)
	UI.text(self, Vector2(111, 22), "Each upgrade adds 8% to its stats.", UI.C_TEXT)
	UI.win(self, Rect2(204, 60, 112, 176))
	var it: Dictionary = m.current()
	if it.is_empty():
		UI.text(self, Vector2(211, 66), "Nothing to upgrade.", UI.C_DIM)
		return
	var iid: String = it["value"]
	UI.icon(self, Vector2(211, 66), iid, 24)
	var d = Content.item(iid)
	var y = 94
	var c = Game.upgrade_cost(iid)
	var lv = Game.upgrade_level(iid)
	UI.stat(self, Vector2(211, y), "Level", "+%d" % lv, 308)
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
		UI.label(self, Vector2(211, y), "Needs")
		y += 12
		var have = Game.count(c["ore"])
		UI.icon(self, Vector2(211, y), c["ore"], 11)
		UI.text(self, Vector2(225, y), "%s x%d" % [Content.item(c["ore"])["name"], c["n"]], UI.C_TEXT if have >= c["n"] else UI.C_RED)
		y += 11
		UI.text(self, Vector2(225, y), "(have %d)" % have, UI.C_DIM)
		y += 11
		UI.text(self, Vector2(225, y), "%d crowns" % c["gold"], UI.C_TEXT if Game.gold() >= c["gold"] else UI.C_RED)

func _shop_list(sid: String, buying: bool) -> void:
	var m = _menu([], Rect2(4, 60, 196, 176), 15, "")
	var refresh = func(mm: MenuList):
		var items = []
		if buying:
			for iid in shop_stock(sid):
				var it = Content.item(iid)
				var price = int(it["price"])
				var ok = Game.gold() >= price and Game.count(iid) < Game.STACK_CAP
				items.append({"icon": iid, "text": it["name"], "right": str(price), "value": iid, "enabled": ok, "reason": "Not enough crowns" if Game.gold() < price else "Stack full"})
		else:
			for iid in Game.S["inventory"]["items"]:
				var it2 = Content.item(iid)
				var ok2: bool = it2.get("sellable", false)
				items.append({"icon": iid, "text": Content.item_name(iid), "right": str(int(it2.get("price", 0)) / 2), "value": iid, "enabled": ok2, "reason": "Cannot be sold"})
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
	UI.label(self, Vector2(111, 8), "Crowns")
	UI.text_right(self, 308, 8, str(Game.gold()), UI.C_TEXT)
	UI.win(self, Rect2(204, 60, 112, 176))
	if m == null:
		UI.text(self, Vector2(111, 22), "Welcome. Take a look.", UI.C_TEXT)
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
	UI.stat(self, Vector2(ix, y), "Owned", str(Game.count(iid)), 308)
	y += 11
	UI.stat(self, Vector2(ix, y), "Worn", str(Game.equipped_count(iid)), 308)
	y = 94
	if d.has("atk"):
		UI.stat(self, Vector2(211, y), "ATK", str(int(d["atk"])), 250)
		UI.stat(self, Vector2(258, y), "MAG", str(int(d["mag"])), 308)
		y += 11
	if d.has("def"):
		UI.stat(self, Vector2(211, y), "DEF", str(int(d["def"])), 250)
		UI.stat(self, Vector2(258, y), "RES", str(int(d["res"])), 308)
		y += 11
	if d.get("kind", "") in ["weapon", "armor", "accessory"]:
		# per-member comparison against what each one wears now (FF-style arrows)
		y += 3
		UI.label(self, Vector2(211, y), "Party")
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
	var m = _menu([{"text": "Rest (%d crowns)" % price if price > 0 else "Rest (free)", "value": 1, "enabled": Game.gold() >= price, "reason": "Not enough crowns"}, {"text": "Leave", "value": 0}], Rect2(110, 90, 120, 40), 2, "")
	m.chosen.connect(func(_i, it):
		if it["value"] == 1 and Game.spend_gold(price):
			Game.heal_all()
			var jl = Audio.jingle("inn")
			if jl <= 0.0:
				Audio.music("M029", 0.0)
			flash_msg("The party rests.")
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
		items.append({"text": "Confirm teams", "value": "__ok", "enabled": ok, "reason": "Each team needs %d" % need})
		mm.items = items
		info_draw = func():
			UI.win(self, Rect2(158, 4, 158, 150))
			var y = 8
			for tm in ["A", "B"]:
				UI.text(self, Vector2(164, y), "Team " + tm + (" (west)" if tm == "A" else " (east)"), UI.C_GOLD)
				y += 11
				var heal = false
				for cid in split_teams[tm]:
					UI.text(self, Vector2(170, y), Game.short_name(cid))
					y += 10
					for a in Game.learned_abilities(cid):
						if Content.ability(a).get("kind", "") == "heal":
							heal = true
				if not heal and not split_teams[tm].is_empty():
					UI.text(self, Vector2(164, y), "No healer: bring Tonics.", UI.C_HI)
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
	var m = _menu(_slot_items(), Rect2(4, 4, 312, 100), 4, "Record a clear save?")
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
