class_name Ranch
extends RefCounted
## Ranching: one ranch per major kingdom (content "ranch", compiled by tools/content/ranch.py; maps in
## content_src/maps/ranch.map, scenes in content_src/scenes/ranch.scn).
## State: Game.S["ranch"][rid] = {"animals": {kind: {"t": minute}}, "plots": {"1": {"crop": id, "t": minute}}},
## always read with .get defaults (older saves have no "ranch" key).
## Time is the world clock in minutes: Game.S.day * 1440 + Game.S.clock (FieldSys).
##   livestock  bought once per kind per ranch; makes one good every `period` minutes, at most `cap` waiting;
##              the produce crate hands everything over (collecting at the cap restarts the count from now).
##   plots      plant a seed (one seed item), ripe after `days` days, harvest `yield` crop items.
## Scene command (director.gd):  ranch menu <RID> | ranch crate | ranch plot | ranch animal | ranch seeds <RID> |
##   ranch buy <RID> <kind>.  crate/plot/animal read the ranch from the NPC being talked to (crate_<RID>,
##   plot_<RID>_<n>, own_<RID>_<kind>).
## Conditions (Game.eval_cond):  ranch:<RID>:own:<kind>  ranch:<RID>:ready  ranch:<RID>:any  ranch:at:<RID>
## Field art: NPC sprites "ranch:<key>" are drawn by draw_field (animals from assets/ext/ranch/<key>/field.*,
## crops from assets/ext/ranch/crops.png, the crate from assets/ext/ranch/crate.png; drawn shapes when missing).

const DAY := 1440.0
const ART := "res://assets/ext/ranch/"

# ---------------------------------------------------------------- data and state
static func data() -> Dictionary:
	return Content.data.get("ranch", {})

static func info(rid: String) -> Dictionary:
	return data().get("ranches", {}).get(rid, {})

static func animal(kind: String) -> Dictionary:
	return data().get("animals", {}).get(kind, {})

static func crop(cid: String) -> Dictionary:
	return data().get("crops", {}).get(cid, {})

static func order() -> Array:
	return data().get("order", [])

static func now() -> float:
	if Game.S.is_empty():
		return 0.0
	return float(int(Game.S.get("day", 0))) * DAY + float(Game.S.get("clock", 480.0))

## Read-only view of a ranch's state ({} when nothing was ever bought or planted there).
static func peek(rid: String) -> Dictionary:
	var all = Game.S.get("ranch", {})
	if typeof(all) != TYPE_DICTIONARY:
		return {}
	var r = all.get(rid, {})
	return r if typeof(r) == TYPE_DICTIONARY else {}

static func _st(rid: String) -> Dictionary:
	if typeof(Game.S.get("ranch")) != TYPE_DICTIONARY:
		Game.S["ranch"] = {}
	var all: Dictionary = Game.S["ranch"]
	if typeof(all.get(rid)) != TYPE_DICTIONARY:
		all[rid] = {}
	var r: Dictionary = all[rid]
	for k in ["animals", "plots"]:
		if typeof(r.get(k)) != TYPE_DICTIONARY:
			r[k] = {}
	return r

static func ranch_of_map(mid: String) -> String:
	for rid in order():
		if str(info(rid).get("map", "")) == mid:
			return rid
	return ""

# ---------------------------------------------------------------- livestock
static func owns(rid: String, kind: String) -> bool:
	return peek(rid).get("animals", {}).has(kind)

static func owned(rid: String) -> Array:
	var out = []
	for k in info(rid).get("animals", []):
		if owns(rid, k):
			out.append(k)
	return out

static func price(rid: String, kind: String) -> int:
	return int(animal(kind).get("price", 0)) if info(rid).get("animals", []).has(kind) else 0

## "ok" | "owned" | "unknown" | "gold"
static func can_buy(rid: String, kind: String) -> String:
	if info(rid).is_empty() or not info(rid).get("animals", []).has(kind) or animal(kind).is_empty():
		return "unknown"
	if owns(rid, kind):
		return "owned"
	if Game.gold() < price(rid, kind):
		return "gold"
	return "ok"

static func buy(rid: String, kind: String) -> String:
	var r = can_buy(rid, kind)
	if r != "ok":
		return r
	if not Game.spend_gold(price(rid, kind)):
		return "gold"
	var first = owned(rid).is_empty()
	_st(rid)["animals"][kind] = {"t": now()}
	Game.stat_add("ranch_animals")
	if first:
		Game.stat_add("ranch_herds")
	Game.emit_signal("state_changed")
	return "ok"

## Goods waiting from one owned animal at minute t (default: now).
static func ready_count(rid: String, kind: String, t: float = -1.0) -> int:
	var a = peek(rid).get("animals", {}).get(kind, {})
	if typeof(a) != TYPE_DICTIONARY or a.is_empty():
		return 0
	var at = now() if t < 0.0 else t
	var an = animal(kind)
	var per = maxf(1.0, float(an.get("period", DAY)))
	var n = int(floor(maxf(0.0, at - float(a.get("t", at))) / per))
	return mini(n, int(an.get("cap", 1)))

static func ready_total(rid: String) -> int:
	var n = 0
	for k in owned(rid):
		n += ready_count(rid, k)
	return n

## Empties the produce crate: adds the goods to the inventory, returns [[item, n], ...].
static func collect(rid: String) -> Array:
	var out = []
	var t = now()
	for k in owned(rid):
		var n = ready_count(rid, k, t)
		if n <= 0:
			continue
		var an = animal(k)
		var a: Dictionary = _st(rid)["animals"][k]
		if n >= int(an.get("cap", 1)):
			a["t"] = t
		else:
			a["t"] = float(a.get("t", t)) + n * float(an.get("period", DAY))
		var good = str(an.get("good", ""))
		Game.add_item(good, n)
		Game.stat_add("ranch_goods", n)
		out.append([good, n])
	if not out.is_empty():
		Game.emit_signal("state_changed")
	return out

# ---------------------------------------------------------------- crop plots
static func plot(rid: String, n: int) -> Dictionary:
	var p = peek(rid).get("plots", {}).get(str(n), {})
	return p if typeof(p) == TYPE_DICTIONARY else {}

static func plot_ready(rid: String, n: int, t: float = -1.0) -> bool:
	var p = plot(rid, n)
	if p.is_empty():
		return false
	var at = now() if t < 0.0 else t
	return at - float(p.get("t", at)) >= float(crop(str(p.get("crop", ""))).get("days", 1)) * DAY

## Minutes until the plot is ripe (0 when ripe or empty).
static func plot_left(rid: String, n: int) -> float:
	var p = plot(rid, n)
	if p.is_empty():
		return 0.0
	var need = float(crop(str(p.get("crop", ""))).get("days", 1)) * DAY
	return maxf(0.0, need - maxf(0.0, now() - float(p.get("t", now()))))

static func seed_crop(seed_iid: String) -> String:
	return str(data().get("seed_crop", {}).get(seed_iid, ""))

## Seed items in the inventory (any ranch's seed grows anywhere).
static func seeds_held() -> Array:
	var out = []
	for sid in data().get("seed_crop", {}):
		if Game.count(sid) > 0:
			out.append(sid)
	out.sort()
	return out

static func plant(rid: String, n: int, seed_iid: String) -> bool:
	var cid = seed_crop(seed_iid)
	if cid == "" or info(rid).is_empty() or n < 1 or n > int(info(rid).get("plots", 0)):
		return false
	if not plot(rid, n).is_empty() or Game.count(seed_iid) <= 0:
		return false
	Game.remove_item(seed_iid, 1)
	_st(rid)["plots"][str(n)] = {"crop": cid, "t": now()}
	Game.emit_signal("state_changed")
	return true

## Harvests a ripe plot: [item, n], or [] when it is empty or still growing.
static func harvest(rid: String, n: int) -> Array:
	if not plot_ready(rid, n):
		return []
	var c = crop(str(plot(rid, n)["crop"]))
	_st(rid)["plots"].erase(str(n))
	var iid = str(c.get("item", ""))
	var k = int(c.get("yield", 1))
	Game.add_item(iid, k)
	Game.stat_add("ranch_harvests")
	Game.emit_signal("state_changed")
	return [iid, k]

static func ripe_plots(rid: String) -> int:
	var n = 0
	for i in range(1, int(info(rid).get("plots", 0)) + 1):
		if plot_ready(rid, i):
			n += 1
	return n

# ---------------------------------------------------------------- conditions
## parts = the condition split on ":" without the leading "ranch".
static func cond(parts: Array) -> bool:
	if parts.size() < 2:
		return false
	if parts[0] == "at":
		return Game.S.get("location", {}).get("map", "") == str(info(str(parts[1])).get("map", "?"))
	var rid = str(parts[0])
	match str(parts[1]):
		"own":
			return parts.size() > 2 and owns(rid, str(parts[2]))
		"ready":
			return ready_total(rid) > 0
		"any":
			return not owned(rid).is_empty()
	return false

# ---------------------------------------------------------------- scene command
static func _npc_ctx(main: Node) -> Array:
	## "crate_R01" -> ["crate", "R01"], "plot_R01_2" -> ["plot", "R01", "2"], "own_R01_cow" -> ["own", "R01", "cow"]
	var id = str(main.director.ctx.get("npc", ""))
	return id.split("_")

static func _fmt_time(mins: float) -> String:
	if mins >= DAY:
		var d = int(ceil(mins / DAY))
		return "%d day%s" % [d, "" if d == 1 else "s"]
	var h = maxi(1, int(ceil(mins / 60.0)))
	return "%d hour%s" % [h, "" if h == 1 else "s"]

static func run(main: Node, a: Array) -> void:
	var op: String = a[0] if a.size() > 0 else ""
	var interactive = not main.director.skipping and QA.route == ""
	match op:
		"menu":
			if interactive:
				await _menu(main, a[1])
		"seeds":
			if interactive:
				await main.open_shop(str(info(a[1]).get("shop", "")))
		"buy":
			buy(a[1], a[2] if a.size() > 2 else "")
		"crate":
			var c = _npc_ctx(main)
			if c.size() >= 2:
				await _crate(main, c[1])
		"plot":
			var p = _npc_ctx(main)
			if p.size() >= 3:
				await _plot(main, p[1], int(p[2]), interactive)
		"animal":
			var o = _npc_ctx(main)
			if o.size() >= 3:
				await _animal(main, o[1], o[2])
		_:
			push_error("ranch: unknown op " + op)
	if is_instance_valid(main.field):
		main.field.refresh_npcs()

static func _menu(main: Node, rid: String) -> void:
	var r = info(rid)
	if r.is_empty():
		return
	while true:
		var pick = await main.choose(["Buy livestock", "Seed box", "How does it work?", "Leave"], 0)
		match pick:
			0:
				await _buy_menu(main, rid)
			1:
				await main.open_shop(str(r.get("shop", "")))
			2:
				await main.say("", "Livestock bought here stays here. Each beast fills the produce crate as the days pass, and the crate holds only so much.")
				await main.say("", "Plots take one seed from the seed box. The crop is ready after a day or more; come back and pull it.")
				await main.say("", "Goods eat, sell and cook. Crafters turn milk, eggs and crops into stews, tarts and cordials.")
			_:
				return

static func _buy_menu(main: Node, rid: String) -> void:
	var kinds: Array = info(rid).get("animals", [])
	var opts = []
	for k in kinds:
		var an = animal(k)
		opts.append("%s  %s" % [an.get("name", k), "(yours)" if owns(rid, k) else "%d cr" % price(rid, k)])
	opts.append("Never mind")
	var pick = await main.choose(opts, 0)
	if pick < 0 or pick >= kinds.size():
		return
	var kind: String = kinds[pick]
	var an = animal(kind)
	match can_buy(rid, kind):
		"owned":
			await main.say("", "That one's already yours. One of each to a ranch; the fields won't carry more.")
			return
		"gold":
			await main.say("", "%s costs %d crowns. You have %d." % [an.get("name", kind), price(rid, kind), Game.gold()])
			return
	await main.say("", str(an.get("note", "")))
	var yes = await main.choose(["Buy for %d crowns" % price(rid, kind), "Not now"], 1)
	if yes != 0:
		return
	if buy(rid, kind) == "ok":
		Audio.sfx("FX007")
		await main.say("", "The %s is yours. It stays at %s; its %s goes in the produce crate." % [an.get("name", kind), info(rid).get("name", ""), Content.item_name(str(an.get("good", "")))])

static func _crate(main: Node, rid: String) -> void:
	if owned(rid).is_empty():
		await main.say("", "The produce crate. Nothing in it is yours. The rancher sells livestock.")
		return
	var got = collect(rid)
	if got.is_empty():
		var soon = DAY * 9
		for k in owned(rid):
			var a = peek(rid)["animals"][k]
			var per = float(animal(k).get("period", DAY))
			soon = minf(soon, per - fmod(maxf(0.0, now() - float(a.get("t", now()))), per))
		await main.say("", "The crate is empty. More in about %s." % _fmt_time(soon))
		return
	Audio.sfx("FX007")
	var parts = []
	for g in got:
		parts.append("%s x%d" % [Content.item_name(g[0]), int(g[1])])
	await main.say("", "From the crate: " + ", ".join(parts) + ".")

static func _plot(main: Node, rid: String, n: int, interactive: bool) -> void:
	var p = plot(rid, n)
	if not p.is_empty():
		var c = crop(str(p.get("crop", "")))
		if plot_ready(rid, n):
			var h = harvest(rid, n)
			Audio.sfx("FX007")
			await main.say("", "Harvested: %s x%d." % [Content.item_name(h[0]), int(h[1])])
		else:
			await main.say("", "%s, still growing. Ready in about %s." % [c.get("name", "A crop"), _fmt_time(plot_left(rid, n))])
		return
	var held = seeds_held()
	if held.is_empty():
		await main.say("", "A tilled plot, empty. The rancher's seed box sells seed.")
		return
	if not interactive:
		return
	var opts = []
	for s in held:
		opts.append("%s  x%d" % [Content.item_name(s), Game.count(s)])
	opts.append("Leave it")
	var pick = await main.choose(opts, 0)
	if pick < 0 or pick >= held.size():
		return
	if plant(rid, n, held[pick]):
		Audio.sfx("FX010")
		var c2 = crop(seed_crop(held[pick]))
		await main.say("", "Planted %s. Ready in %s." % [c2.get("name", ""), _fmt_time(float(c2.get("days", 1)) * DAY)])

static func _animal(main: Node, rid: String, kind: String) -> void:
	var an = animal(kind)
	var n = ready_count(rid, kind)
	await main.say("", "Your %s. %s waiting in the crate: %d of %d." % [an.get("name", kind), Content.item_name(str(an.get("good", ""))), n, int(an.get("cap", 1))])

# ---------------------------------------------------------------- field drawing
static var _tex = {}
static var _crop_meta = null

static func _t(name: String) -> Texture2D:
	if not _tex.has(name):
		var p = ART + name
		_tex[name] = load(p) if ResourceLoader.exists(p) else null
	return _tex[name]

const FALLBACK := {"cow": Color8(150, 96, 60), "cow_black": Color8(50, 46, 52), "pig": Color8(236, 150, 160),
	"pig_black": Color8(80, 74, 80), "dove": Color8(240, 240, 248), "bunny": Color8(236, 236, 230),
	"cat": Color8(180, 110, 60), "fox": Color8(232, 120, 40), "mouse": Color8(150, 140, 170)}

## Draws a "ranch:<key>" NPC sprite with its tile's top-left at `pos` (units).
static func draw_field(ci: CanvasItem, key: String, dir: String, frame: int, pos: Vector2) -> void:
	var p = key.split(":")
	if p[0] == "plot" and p.size() >= 3:
		_draw_plot(ci, p[1], int(p[2]), pos)
		return
	if p[0] == "crate" and p.size() >= 2:
		_draw_crate(ci, p[1], pos)
		return
	var art = "ext/ranch/" + key
	if HeroArt.has_field(art):
		ci.draw_rect(Rect2(pos + Vector2(3, 14), Vector2(10, 2)), Color(0, 0, 0, 0.25))
		HeroArt.draw_field(ci, art, dir if not dir.begins_with("pose") else "down", frame > 0, pos + Vector2(8, 15.67))
		return
	# drawn fallback: a body, a head, legs
	var col: Color = FALLBACK.get(key, Color8(160, 140, 120))
	var big = key.begins_with("cow")
	var small = key in ["dove", "mouse"]
	var w = 14.0 if big else (6.0 if small else 10.0)
	var h = 8.0 if big else (4.0 if small else 6.0)
	var bob = 1.0 if frame % 2 == 1 else 0.0
	var base = pos + Vector2(8, 15)
	ci.draw_rect(Rect2(base + Vector2(-w / 2.0 + 1, -1), Vector2(w - 2, 2)), Color(0, 0, 0, 0.25))
	ci.draw_rect(Rect2(base + Vector2(-w / 2.0, -h - 2 - bob), Vector2(w, h)), col)
	var hx = (w / 2.0 - 1) if dir == "right" else (-w / 2.0 - 2 if dir == "left" else -1.5)
	ci.draw_rect(Rect2(base + Vector2(hx, -h - 4 - bob), Vector2(3.5, 3.5)), col.lightened(0.15))
	if not small:
		ci.draw_rect(Rect2(base + Vector2(-w / 2.0 + 1, -2), Vector2(1.5, 2)), col.darkened(0.4))
		ci.draw_rect(Rect2(base + Vector2(w / 2.0 - 2.5, -2), Vector2(1.5, 2)), col.darkened(0.4))

static func _crops() -> Dictionary:
	if _crop_meta == null:
		var jp = ART + "crops.json"
		_crop_meta = JSON.parse_string(FileAccess.get_file_as_string(jp)) if FileAccess.file_exists(jp) else {}
		if typeof(_crop_meta) != TYPE_DICTIONARY:
			_crop_meta = {}
	return _crop_meta

static func _draw_plot(ci: CanvasItem, rid: String, n: int, pos: Vector2) -> void:
	var pl = plot(rid, n)
	if pl.is_empty():
		return
	var cid = str(pl.get("crop", ""))
	var ripe = plot_ready(rid, n)
	var t = _t("crops.png")
	var m = _crops()
	var idx = (m.get("order", []) as Array).find(cid)
	if t != null and idx >= 0:
		var cw = int(m["cell"][0])
		var chh = int(m["cell"][1])
		UI.native_begin(ci, ((pos + Vector2(8, 16)) * UI.U).round() / UI.U)
		ci.draw_texture_rect_region(t, Rect2(-cw / 2.0, -chh, cw, chh), Rect2((1 if ripe else 0) * cw, idx * chh, cw, chh))
		UI.native_end(ci)
		return
	var col = Color8(90, 170, 70)
	var cc = crop(cid).get("color", [])
	if ripe and cc.size() == 3:
		col = Color8(int(cc[0]), int(cc[1]), int(cc[2]))
	for i in range(3):
		var x = pos.x + 3 + i * 4
		if ripe:
			ci.draw_rect(Rect2(Vector2(x, pos.y + 6), Vector2(1, 4)), Color8(70, 140, 60))
			ci.draw_rect(Rect2(Vector2(x - 1, pos.y + 9), Vector2(3, 3)), col)
		else:
			ci.draw_rect(Rect2(Vector2(x, pos.y + 9), Vector2(1, 3)), col)

static func _draw_crate(ci: CanvasItem, rid: String, pos: Vector2) -> void:
	var t = _t("crate.png")
	var full = ready_total(rid) > 0
	if t != null:
		UI.native_begin(ci, ((pos + Vector2(8, 16)) * UI.U).round() / UI.U)
		ci.draw_texture(t, Vector2(-t.get_width() / 2.0, -t.get_height()))
		UI.native_end(ci)
	else:
		ci.draw_rect(Rect2(pos + Vector2(1, 4), Vector2(14, 11)), Color8(120, 78, 44))
		ci.draw_rect(Rect2(pos + Vector2(1, 4), Vector2(14, 2)), Color8(160, 110, 64))
		ci.draw_rect(Rect2(pos + Vector2(1, 9), Vector2(14, 1)), Color8(80, 50, 30))
	if full:
		# goods heaped on top: the first owned animal's good icon, or white eggs
		var goods = []
		for k in owned(rid):
			if ready_count(rid, k) > 0:
				goods.append(str(animal(k).get("good", "")))
		var drawn = false
		for i in range(mini(2, goods.size())):
			if draw_icon(ci, pos + Vector2(1 + i * 7, -2), goods[i], 0.6):
				drawn = true
		if not drawn:
			ci.draw_rect(Rect2(pos + Vector2(4, 2), Vector2(3, 3)), Color8(244, 240, 228))
			ci.draw_rect(Rect2(pos + Vector2(8, 1), Vector2(3, 3)), Color8(244, 240, 228))

## Ranch item icon (assets/ext/ranch/icons.png, 16x16 cells, 8 per row) at `scale` units per pixel. False if missing.
static func draw_icon(ci: CanvasItem, pos: Vector2, iid: String, scale: float = 1.0) -> bool:
	var it: Dictionary = Content.item(iid)
	var t = _t("icons.png")
	if t == null or not it.has("icon_ranch"):
		return false
	var n = int(it["icon_ranch"])
	if (n / 8 + 1) * 16 > t.get_height():
		return false
	ci.draw_texture_rect_region(t, Rect2(pos, Vector2(16, 16) * scale), Rect2((n % 8) * 16, (n / 8) * 16, 16, 16))
	return true

# ---------------------------------------------------------------- Records > Ranches
static func record_rows() -> Array:
	var out = []
	for rid in order():
		var r = info(rid)
		var right = ""
		var o = owned(rid).size()
		if o > 0 or not peek(rid).get("plots", {}).is_empty():
			right = "%d/%d" % [o, r.get("animals", []).size()]
			if ready_total(rid) > 0 or ripe_plots(rid) > 0:
				right += " !"
		out.append({"text": str(r.get("name", rid)), "right": right, "value": rid,
			"color": UI.C_TEXT if right != "" else UI.C_DIM})
	return out

static func record_lines(rid: String) -> Array:
	## -> [[text, color], ...] for the info panel
	var r = info(rid)
	var out = [[str(r.get("name", rid)), UI.C_GOLD], ["%s  -  %s" % [r.get("town", ""), r.get("rancher", "")], UI.C_DIM], ["", UI.C_TEXT]]
	out.append(["Livestock", UI.C_LABEL])
	for k in r.get("animals", []):
		var an = animal(k)
		if owns(rid, k):
			out.append(["  %s  %d/%d" % [an.get("name", k), ready_count(rid, k), int(an.get("cap", 1))], UI.C_TEXT])
		else:
			out.append(["  %s  -  %d cr" % [an.get("name", k), price(rid, k)], UI.C_DIM])
	out.append(["Plots", UI.C_LABEL])
	for i in range(1, int(r.get("plots", 0)) + 1):
		var p = plot(rid, i)
		if p.is_empty():
			out.append(["  %d  empty" % i, UI.C_DIM])
		elif plot_ready(rid, i):
			out.append(["  %d  %s - ready" % [i, crop(str(p["crop"])).get("name", "")], UI.C_GREEN])
		else:
			out.append(["  %d  %s - %s" % [i, crop(str(p["crop"])).get("name", ""), _fmt_time(plot_left(rid, i))], UI.C_TEXT])
	out.append(["Seed box", UI.C_LABEL])
	for c in r.get("seeds", []):
		out.append(["  %s  %d day%s" % [crop(c).get("name", c), int(crop(c).get("days", 1)), "" if int(crop(c).get("days", 1)) == 1 else "s"], UI.C_DIM])
	var rt = ready_total(rid)
	if rt > 0:
		out.append(["Crate: %d waiting" % rt, UI.C_HI])
	return out
