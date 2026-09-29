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
	draw_rect(Rect2(0, 0, 320, 240), Color(0, 0, 0, 0.35))
	if page == "main" or page == "pick":
		_draw_party_panel(Rect2(4, 4, 224, 196))
		UI.win(self, Rect2(4, 204, 312, 32))
		UI.text(self, Vector2(10, 208), "%d crowns" % Game.gold(), UI.C_GOLD)
		UI.text(self, Vector2(10, 220), Game.fmt_time(Game.S.get("playtime", 0.0)), UI.C_DIM)
		UI.text_right(self, 310, 208, main.field.map.get("name", ""), UI.C_TEXT)
		UI.text_right(self, 310, 220, Game.current_chapter(), UI.C_DIM)
	if info_draw.is_valid():
		info_draw.call()
	if msg_t > 0 and msg != "":
		var w = UI.width(msg) + 16
		UI.win(self, Rect2((320 - w) / 2.0, 108, w, 18))
		UI.text_center(self, 160, 112, msg, UI.C_HI)

func _draw_party_panel(r: Rect2) -> void:
	UI.win(self, r)
	var y = r.position.y + 5
	var act = Game.active()
	for cid in act:
		_draw_member_line(cid, Vector2(r.position.x + 6, y), true)
		y += 34
	var res = Game.S["party"]["roster"].filter(func(c): return not act.has(c))
	if not res.is_empty():
		UI.text(self, Vector2(r.position.x + 8, y), "Reserve / away", UI.C_DIM)
		y += 11
		var x = r.position.x + 8
		for cid in res:
			var st = "" if Game.is_available(cid) else " (away)"
			UI.text(self, Vector2(x, y), Content.ch(cid)["short"] + st, UI.C_TEXT if Game.is_available(cid) else UI.C_DIM)
			y += 10
			if y > r.end.y - 10:
				x += 100
				y = r.end.y - 30

func _draw_member_line(cid: String, p: Vector2, full: bool) -> void:
	var m = Game.member(cid)
	var s = Game.stats(cid)
	var t: Texture2D = main.field.sprite_tex(cid)
	if t:
		var cw = t.get_width() / 6
		var chh = t.get_height() / 5
		draw_texture_rect_region(t, Rect2(p + Vector2(12 - cw / 2, 30 - chh), Vector2(cw, chh)), Rect2(0, 0, cw, chh))
	var hp = int(m["hp"]) if int(m["hp"]) >= 0 else s["mhp"]
	var mp = int(m["mp"]) if int(m["mp"]) >= 0 else s["mmp"]
	UI.text(self, p + Vector2(28, 0), Content.ch(cid)["name"], UI.C_GOLD)
	UI.text(self, p + Vector2(130, 0), "Lv %d" % m["level"], UI.C_TEXT)
	UI.text(self, p + Vector2(170, 0), "[" + Game.row(cid).substr(0, 1).to_upper() + "]", UI.C_DIM)
	UI.text(self, p + Vector2(28, 11), "HP %d/%d" % [hp, s["mhp"]], UI.C_TEXT if hp > 0 else UI.C_RED)
	UI.text(self, p + Vector2(118, 11), "MP %d/%d" % [mp, s["mmp"]], UI.C_BLUE)
	var need = F.xp_total_for_level(int(m["level"]) + 1) - int(m["xp"])
	UI.text(self, p + Vector2(28, 21), "Next %d" % maxi(0, need), UI.C_DIM)
	var link = Game.link_of(cid)
	if link != "":
		UI.text(self, p + Vector2(118, 21), Content.data["vestiges"][link]["name"], Color8(240, 150, 220))

func _pick_member(cb: Callable, title: String, only_available: bool = true) -> void:
	var items = []
	for cid in Game.S["party"]["roster"]:
		var ok = Game.is_available(cid) or not only_available
		items.append({"text": Content.ch(cid)["name"], "value": cid, "enabled": ok, "reason": "Away from the party"})
	var m = _menu(items, Rect2(232, 150, 84, 56), 4, "")
	m.chosen.connect(func(_i, it): cb.call(it["value"]))

# ======================================================================
# Items
# ======================================================================
func _items_menu() -> void:
	page = "items"
	var m = _menu([], Rect2(4, 4, 200, 196), 16, "Items")
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
			items.append({"text": it["name"], "right": str(Game.count(iid)), "value": iid, "enabled": true, "color": UI.C_TEXT if usable or it["kind"] != "consumable" else UI.C_DIM})
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
	UI.win(self, Rect2(208, 4, 108, 196))
	var it = m.current()
	if it.is_empty():
		return
	var d = Content.item(it.get("value", ""))
	var y = 8
	UI.text(self, Vector2(214, y), d.get("kind", "").capitalize(), UI.C_GOLD)
	y += 12
	for ln in UI.wrap(d.get("desc", ""), 96):
		UI.text(self, Vector2(214, y), ln)
		y += 11
	if d.get("kind", "") in ["weapon", "armor"]:
		y += 4
		if d.has("atk"):
			UI.text(self, Vector2(214, y), "ATK %d  MAG %d" % [d["atk"], d["mag"]])
			y += 11
		if d.has("def"):
			UI.text(self, Vector2(214, y), "DEF %d  RES %d" % [d["def"], d["res"]])
			y += 11
	if d.get("kind", "") == "consumable" and not d.get("field", false):
		UI.text(self, Vector2(214, 186), "Battle only", UI.C_DIM)

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
	var m = _menu([], Rect2(4, 4, 150, 95), 7, Content.ch(cid)["name"])
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
			items.append({"text": Content.item_name(iid), "right": str(Game.count(iid)), "value": iid})
	var m = _menu(items, Rect2(4, 92, 150, 108), 8, "")
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
	UI.win(self, Rect2(158, 4, 158, 196))
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
		prev = F.member_stats(mem, Content.ch(cid), Content.data["items"])
	var y = 10
	for k in [["mhp", "Max HP"], ["mmp", "Max MP"], ["atk", "Attack"], ["matk", "Magic"], ["def", "Defense"], ["res", "Resist"], ["spd", "Speed"]]:
		UI.text(self, Vector2(166, y), k[1], UI.C_DIM)
		UI.text_right(self, 262, y, str(cur[k[0]]))
		if has_prev:
			var nv: int = prev[k[0]]
			var col = UI.C_TEXT if nv == cur[k[0]] else (UI.C_GREEN if nv > cur[k[0]] else UI.C_RED)
			UI.text(self, Vector2(266, y), "→", UI.C_DIM)
			UI.text_right(self, 308, y, str(nv), col)
		y += 12
	y += 4
	var grants: Array = prev["grants"] if has_prev else cur["grants"]
	for g in grants:
		UI.text(self, Vector2(166, y), "Grants " + Content.ability(g)["name"], UI.C_GOLD)
		y += 11
	var pas: Dictionary = prev["passives"] if has_prev else cur["passives"]
	for k in pas:
		UI.text(self, Vector2(166, y), _passive_label(k, pas[k]), Color8(210, 190, 250))
		y += 11
		if y > 186:
			break
	if has_prev and preview_item != "":
		var d = Content.item(preview_item)
		var lines = UI.wrap(d.get("desc", ""), 146)
		var yy = 188 - lines.size() * 11
		for ln in lines.slice(0, 3):
			UI.text(self, Vector2(166, yy), ln, UI.C_DIM)
			yy += 11

func _passive_label(k: String, v) -> String:
	return {"phys_reduce": "Physical damage -10%", "reveal_affinity": "Reveals affinities", "immune": "Immune: " + str(v),
		"acc_bonus": "Accuracy +%s" % str(v), "heal_mult": "Healing x1.15", "mmp_mult": "Max MP +15%", "mhp_mult": "Max HP +15%",
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
		items.append({"text": a["name"] if has else "Lv %d: ???" % l["level"], "right": str(a["mp"]) if has else "", "value": l["id"], "enabled": has and a.get("field", false), "reason": "Battle technique" if has else "Not yet learned", "desc": a["desc"] if has else ""})
	var ult = Content.ch(cid).get("ultimate")
	if ult != null:
		var has2 = learned.has(ult)
		items.append({"text": Content.ability(ult)["name"] if has2 else "Personal story: ???", "value": ult, "enabled": false, "reason": "Battle technique" if has2 else "Resolve their personal story", "desc": Content.ability(ult)["desc"] if has2 else ""})
	for g in st["grants"]:
		items.append({"text": Content.ability(g)["name"] + " (acc.)", "right": str(Content.ability(g)["mp"]), "value": g, "enabled": Content.ability(g).get("field", false), "reason": "Granted while equipped", "desc": Content.ability(g)["desc"]})
	var m = _menu(items, Rect2(4, 4, 200, 150), 12, Content.ch(cid)["name"])
	info_draw = func():
		var it = m.current()
		UI.win(self, Rect2(4, 158, 312, 78))
		var y = 162
		UI.text(self, Vector2(10, y), "MP %d/%d" % [Game.member(cid)["mp"], st["mmp"]], UI.C_BLUE)
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
			items.append({"text": mark + Content.ch(cid)["short"], "right": "%s %s" % [tag, Game.row(cid).substr(0, 1).to_upper()], "value": cid,
				"enabled": Game.is_available(cid), "reason": "Away from the party"})
		mm.items = items
		info_draw = func():
			UI.win(self, Rect2(158, 4, 158, 150))
			var lines = UI.wrap("Confirm a member, then another to swap places. Press Page (Q/E) on a member to switch front/back row. The first four available are active.", 146)
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
			Game.set_active(avail.slice(0, 4))
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
					holder = Content.ch(Game.S["links"][k])["short"]
			items.append({"text": v["name"], "right": holder if holder != "" else "-", "value": vid})
		mm.items = items
		info_draw = func():
			var it = mm.current()
			if it.is_empty():
				return
			UI.win(self, Rect2(4, 128, 312, 60))
			var a = Content.ability(Content.data["vestiges"][it["value"]]["summon"])
			var y = 132
			for ln in UI.wrap(a["desc"] + " Costs 100 Concord; once per battle.", 296):
				UI.text(self, Vector2(10, y), ln)
				y += 11
	refresh.call(m)
	m.set_meta("refresh", refresh)
	m.chosen.connect(func(_i, it):
		var items = [{"text": "(unlink)", "value": ""}]
		for cid in Game.available_members():
			items.append({"text": Content.ch(cid)["name"], "value": cid})
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
	var m = _menu(items, Rect2(4, 4, 120, 200), 17, "Discovered")
	info_draw = func():
		UI.win(self, Rect2(128, 4, 188, 200))
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
			var fw = tx.get_width() / 4
			var h = mini(tx.get_height(), 80)
			draw_texture_rect_region(tx, Rect2(232 - fw / 2.0, y, fw, h), Rect2(0, 0, fw, h))
			y += h + 4
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
	["battle_mode", "Battle mode", ["wait", "active"]],
	["battle_speed", "Battle speed", [0.75, 1.0, 1.25]],
	["text_speed", "Text speed", [0, 1, 2, 3]],
	["run_toggle", "Run", [false, true]],
	["encounters", "Encounters", ["normal", "reduced", "off"]],
	["reduced_flash", "Reduced flashes", [false, true]],
	["shake", "Screen shake", [true, false]],
	["short_summons", "Short summons", [false, true]],
	["vol_master", "Master volume", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]],
	["vol_music", "Music volume", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]],
	["vol_sfx", "Sound volume", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]],
	["pause_on_focus_loss", "Pause on focus loss", [true, false]],
	["fullscreen", "Fullscreen", [false, true]],
]

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
			items.append({"text": d[1], "right": _setting_label(d[0], Settings.get_v(d[0])), "value": d[0]})
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
			var cur = Settings.get_v(k)
			var i = 0
			for j in range(opts.size()):
				if typeof(opts[j]) == typeof(cur) and opts[j] == cur:
					i = j
				elif typeof(cur) == TYPE_FLOAT and typeof(opts[j]) == TYPE_FLOAT and absf(opts[j] - cur) < 0.01:
					i = j
			i = (i + dirn + opts.size()) % opts.size()
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
	var m = _menu([{"text": "No", "value": 0}, {"text": "Yes", "value": 1}], Rect2(110, 170, 100, 36), 2, "")
	info_draw = func():
		UI.win(self, Rect2(60, 150, 200, 18))
		UI.text_center(self, 160, 154, q, UI.C_HI)
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
	if "weapons" in sh["kinds"]:
		for iid in items:
			var it: Dictionary = items[iid]
			if it["kind"] == "weapon" and int(it["tier"]) <= 5:
				var ch: String = rules["weapon_tier_chapter"][str(int(it["tier"]))]
				if (ch == "CH01" or Game.chapter_done(ch)) and Game.is_recruited(it["owner"]):
					out.append(iid)
	if "armor" in sh["kinds"]:
		for iid in items:
			var it: Dictionary = items[iid]
			if it["kind"] == "armor":
				var ch2: String = rules["armor_tier_chapter"][str(int(it["tier"]))]
				if ch2 == "CH01" or Game.chapter_done(ch2):
					out.append(iid)
	if "accessories" in sh["kinds"] or "items" in sh["kinds"]:
		for aid in rules["accessory_chapter"]:
			if Game.chapter_done(rules["accessory_chapter"][aid]):
				out.append(aid)
	return out

func _shop_menu() -> void:
	page = "shop"
	var sid: String = data["id"]
	var sh: Dictionary = Content.data["shops"].get(sid, {"name": "Shop"})
	var m = _menu([{"text": "Buy", "value": "buy"}, {"text": "Sell", "value": "sell"}, {"text": "Leave", "value": "leave"}], Rect2(4, 4, 90, 46), 3, sh["name"])
	info_draw = func(): _shop_info(null)
	m.chosen.connect(func(_i, it):
		if it["value"] == "buy":
			_shop_list(sid, true)
		elif it["value"] == "sell":
			_shop_list(sid, false)
		else:
			_close_all())

func _shop_list(sid: String, buying: bool) -> void:
	var m = _menu([], Rect2(4, 54, 190, 150), 12, "")
	var refresh = func(mm: MenuList):
		var items = []
		if buying:
			for iid in shop_stock(sid):
				var it = Content.item(iid)
				var price = int(it["price"])
				var ok = Game.gold() >= price and Game.count(iid) < Game.STACK_CAP
				items.append({"text": it["name"], "right": str(price), "value": iid, "enabled": ok, "reason": "Not enough crowns" if Game.gold() < price else "Stack full"})
		else:
			for iid in Game.S["inventory"]["items"]:
				var it2 = Content.item(iid)
				var ok2: bool = it2.get("sellable", false)
				items.append({"text": it2["name"], "right": str(int(it2.get("price", 0)) / 2), "value": iid, "enabled": ok2, "reason": "Cannot be sold"})
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
	UI.win(self, Rect2(198, 4, 118, 200))
	UI.text(self, Vector2(204, 8), "%d crowns" % Game.gold(), UI.C_GOLD)
	if m == null:
		return
	var it: Dictionary = m.current()
	if it.is_empty():
		return
	var d = Content.item(it["value"])
	var y = 22
	UI.text(self, Vector2(204, y), "Owned %d  Eq %d" % [Game.count(it["value"]), Game.equipped_count(it["value"])], UI.C_DIM)
	y += 12
	if d.get("kind", "") in ["weapon", "armor", "accessory"]:
		var who = []
		for cid in d.get("allowed", []):
			if Game.is_recruited(cid):
				who.append(Content.ch(cid)["short"])
		for ln in UI.wrap("Can equip: " + ", ".join(who), 106):
			UI.text(self, Vector2(204, y), ln, UI.C_TEXT)
			y += 11
		if d.has("atk"):
			UI.text(self, Vector2(204, y), "ATK %d MAG %d" % [d["atk"], d["mag"]])
			y += 11
		if d.has("def"):
			UI.text(self, Vector2(204, y), "DEF %d RES %d" % [d["def"], d["res"]])
			y += 11
	for ln in UI.wrap(d.get("desc", ""), 106):
		UI.text(self, Vector2(204, y), ln, UI.C_DIM)
		y += 11
		if y > 196:
			break

func _inn_menu() -> void:
	page = "inn"
	var price: int = int(data.get("price", -1))
	if price < 0:
		price = F.inn_price(Game.S["party"]["roster"].size())
	var m = _menu([{"text": "Rest (%d crowns)" % price if price > 0 else "Rest (free)", "value": 1, "enabled": Game.gold() >= price, "reason": "Not enough crowns"}, {"text": "Leave", "value": 0}], Rect2(110, 90, 120, 40), 2, "")
	m.chosen.connect(func(_i, it):
		if it["value"] == 1 and Game.spend_gold(price):
			Game.heal_all()
			Audio.music("M029", 0.0)
			flash_msg("The party rests.")
			await get_tree().create_timer(1.2).timeout
			Audio.music(main.field.map.get("music", ""), 0.5)
		_close_all())

# ======================================================================
# Two-party split for the final dungeon
# ======================================================================
func _split_menu() -> void:
	page = "split"
	split_teams = {"A": [], "B": []}
	var avail = Game.available_members()
	for i in range(avail.size()):
		split_teams["A" if i < 4 else "B"].append(avail[i])
	var m = _menu([], Rect2(4, 4, 150, 150), 11, "West (A) / East (B)")
	var refresh = func(mm: MenuList):
		var items = []
		for cid in avail:
			var team = "A" if split_teams["A"].has(cid) else "B"
			items.append({"text": Content.ch(cid)["short"], "right": team, "value": cid})
		var ok: bool = split_teams["A"].size() == 4 and split_teams["B"].size() == 4
		items.append({"text": "Confirm teams", "value": "__ok", "enabled": ok, "reason": "Each team needs four"})
		mm.items = items
		info_draw = func():
			UI.win(self, Rect2(158, 4, 158, 150))
			var y = 8
			for tm in ["A", "B"]:
				UI.text(self, Vector2(164, y), "Team " + tm + (" (west)" if tm == "A" else " (east)"), UI.C_GOLD)
				y += 11
				var heal = false
				for cid in split_teams[tm]:
					UI.text(self, Vector2(170, y), Content.ch(cid)["short"])
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
		if split_teams["A"].has(cid):
			split_teams["A"].erase(cid)
			split_teams["B"].append(cid)
		else:
			split_teams["B"].erase(cid)
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
