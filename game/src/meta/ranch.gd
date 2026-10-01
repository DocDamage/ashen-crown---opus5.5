class_name Ranch
extends RefCounted
## Ranching: a farm in every major kingdom, drawn and played with the owner's "Super Retro Ranch" pack (16 px;
## docs/expansion/RANCH_PACK.md). Data: content "ranch" (tools/content/ranch.py, rules in its doc string); maps
## content_src/maps/ranch.map + Art48 art from tools/maps48/maps/ranch.py; scenes content_src/scenes/ranch.scn.
##
## State Game.S["ranch"][rid] (always read through state(), which migrates the first pass's saves):
##   v 2 | tools (lent) | gate (pen gate open) | u (last processed quarter-day slot)
##   plots {"x,y": {c crop ("" = hoed, empty), g stage index, w watered through slot, fz frost slot, bn scorch slot,
##          nb nibbled slot}}   (a key present = the cell is hoed)
##   animals {kind: {t bought minute, d bought day, aff 0-10, pet last petted day, got last collected day, n doves,
##          seen pig grown up}}
##   eggs [laid day, ...] | hatch day | fox day | mice day | caught day | kart {load {iid: n}, away day, pay}
## Time: slot = day * 4 + clock / 360 (FieldSys.weather_slot); every slot boundary grows the watered crops one
## stage and rolls the hazards; every midnight runs the day (doves lay and hatch, foxes, mice, affection).
## Scene command (director.gd):  ranch menu <RID> | ranch lend <RID> | ranch seeds <RID> | ranch buy <RID> <kind> |
##   ranch plant | ranch kart | ranch animal | ranch nest   (plant / kart / animal / nest read the ranch from the map)
## Conditions (Game.eval_cond):  ranch:<RID>:own:<kind> | :birds:<n> | :gate | :tools | :ready | :any | ranch:at:<RID>
## Field hooks (field.gd): on_enter, interact (plots, gate, animals, nest, doors), draw_ground (hoed beds, animated
## water), collect / draw_tall (crops, campfires, gates, doors, the hands' beds, effects), draw_field (ranch:<key>
## NPC sprites: folk, cows, pigs, doves, coneys, cats, foxes, mice, the kart, the nest), draw_after (fireflies,
## sun rays, wind).

const DAY := 1440.0
const SLOT := 360.0
const ART := "res://assets/ext/ranch/"
const PACK := "res://assets/ext/ranch/pack/"

# ---------------------------------------------------------------- data
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

static func rule(k: String, d: float) -> float:
	return float(data().get("rules", {}).get(k, d))

static func now() -> float:
	if Game.S.is_empty():
		return 0.0
	return float(int(Game.S.get("day", 0))) * DAY + float(Game.S.get("clock", 480.0))

static func slot_now() -> int:
	return int(floor(now() / SLOT))

static func day_now() -> int:
	return int(Game.S.get("day", 0)) if not Game.S.is_empty() else 0

static var _map_rid := {}

static func rid_of(mid: String) -> String:
	if _map_rid.is_empty():
		for rid in order():
			_map_rid[str(info(rid).get("map", ""))] = rid
	return str(_map_rid.get(mid, ""))

# ---------------------------------------------------------------- state
## Read-only view ({} when the ranch was never touched). Never migrates; use state() to change anything.
static func peek(rid: String) -> Dictionary:
	var all = Game.S.get("ranch", {})
	if typeof(all) != TYPE_DICTIONARY:
		return {}
	var r = all.get(rid, {})
	return r if typeof(r) == TYPE_DICTIONARY else {}

static func state(rid: String) -> Dictionary:
	if typeof(Game.S.get("ranch")) != TYPE_DICTIONARY:
		Game.S["ranch"] = {}
	var all: Dictionary = Game.S["ranch"]
	if typeof(all.get(rid)) != TYPE_DICTIONARY:
		all[rid] = {}
	var r: Dictionary = all[rid]
	if int(r.get("v", 1)) < 2:
		_migrate(rid, r)
	for k in ["plots", "animals"]:
		if typeof(r.get(k)) != TYPE_DICTIONARY:
			r[k] = {}
	if typeof(r.get("eggs")) != TYPE_ARRAY:
		r["eggs"] = []
	if typeof(r.get("kart")) != TYPE_DICTIONARY:
		r["kart"] = {}
	var kt: Dictionary = r["kart"]
	if typeof(kt.get("load")) != TYPE_DICTIONARY:
		kt["load"] = {}
	if typeof(r.get("log")) != TYPE_ARRAY:
		r["log"] = []
	if not r.has("u"):
		r["u"] = slot_now()
	return r

## The first ranch pass kept {"animals": {kind: {"t": minute}}, "plots": {"1": {"crop", "t"}}} and a produce crate.
## Livestock carries over (doves become the dove kind "bird"; pigs bought days ago are grown); the numbered plots
## had no cells, so their seed comes back to the bag; the crate's goods are paid out once.
static func _migrate(rid: String, r: Dictionary) -> void:
	var old_an = r.get("animals", {})
	var old_pl = r.get("plots", {})
	var an := {}
	var today = day_now()
	var crate := 0
	if typeof(old_an) == TYPE_DICTIONARY:
		for k in old_an:
			var a = old_an[k]
			var t = float(a.get("t", now())) if typeof(a) == TYPE_DICTIONARY else now()
			var nk = "bird" if str(k) == "dove" else str(k)
			if animal(nk).is_empty():
				continue
			an[nk] = {"t": t, "d": int(t / DAY), "aff": 2, "pet": -1, "got": today - 1, "n": 1}
			crate += 1
	if typeof(old_pl) == TYPE_DICTIONARY:
		for k in old_pl:
			var p = old_pl[k]
			if typeof(p) != TYPE_DICTIONARY:
				continue
			var sd = str(crop(str(p.get("crop", ""))).get("seed", ""))
			if sd != "" and not Game.S.is_empty():
				Game.add_item(sd, 1)
	r.clear()
	r["v"] = 2
	r["animals"] = an
	r["plots"] = {}
	r["tools"] = not an.is_empty()
	r["u"] = slot_now()
	r["log"] = ["The ranch books were redone. Seed from the old plots went back in the bag."] if not old_pl.is_empty() else []
	if crate > 0:
		r["log"].append("The rancher set aside what the beasts gave while you were gone.")

static func _log(st: Dictionary, s: String) -> void:
	var lg: Array = st["log"]
	lg.append(s)
	while lg.size() > 6:
		lg.pop_front()

# ---------------------------------------------------------------- weather (deterministic per region and slot)
## FieldSys.region_weather for any slot (the same rolls), so missed quarter days can be caught up.
static func weather_at_slot(region: String, slot: int) -> String:
	var post: bool = Game.S.get("world_phase", "pre") == "post"
	var tbl: Array = (FieldSys.REGION_WEATHER_POST.get(region, FieldSys.REGION_WEATHER.get(region, [])) if post else FieldSys.REGION_WEATHER.get(region, []))
	for i in range(tbl.size()):
		var h = hash("%s|%d|%d" % [region, slot, i])
		var roll = float(absi(h) % 1000) / 1000.0
		if roll < float(tbl[i][1]):
			return str(tbl[i][0])
	return ""

static func weather_now(rid: String) -> String:
	return weather_at_slot(str(info(rid).get("region", "")), slot_now())

static func _roll(rid: String, slot: int, what: String) -> float:
	return float(absi(hash("%s|%d|%s" % [rid, slot, what])) % 1000) / 1000.0

# ---------------------------------------------------------------- the clock
## Catches the ranch up to now: every quarter-day slot boundary since the last visit (at most 30 days).
static func tick(rid: String) -> void:
	if info(rid).is_empty() or Game.S.is_empty():
		return
	var st = state(rid)
	var sn = slot_now()
	var u = int(st.get("u", sn))
	if u >= sn:
		st["u"] = sn
		return
	for s in range(maxi(u + 1, sn - 120), sn + 1):
		_slot(rid, st, s)
	st["u"] = sn

static func _slot(rid: String, st: Dictionary, s: int) -> void:
	var r = info(rid)
	var w = weather_at_slot(str(r.get("region", "")), s)
	var night = s % 4 == 0
	var hz = str(r.get("hazard", ""))
	for key in st["plots"]:
		var p: Dictionary = st["plots"][key]
		var cid = str(p.get("c", ""))
		if cid == "":
			continue
		if w == "rain":
			p["w"] = maxi(int(p.get("w", -1)), s)
		var last = crop(cid).get("stages", [0]).size() - 1
		var g = int(p.get("g", 0))
		var wet = s <= int(p.get("w", -1))
		if g < last and g >= 1:
			if hz == "frost" and night and w == "snow":
				p["g"] = maxi(1, g - 1)
				p["fz"] = s
				continue
			if hz == "ember" and w == "ash" and not wet and _roll(rid, s, str(key)) < 0.3:
				p["g"] = maxi(1, g - 1)
				p["bn"] = s
				continue
		if wet and g < last:
			p["g"] = g + 1
	if night:
		_day(rid, st, s / 4, s)
	elif s % 4 == 1:
		_dawn(rid, st, s / 4)

## Dawn (06:00): an egg left long enough hatches into another dove; then each dove lays one (the nest holds three).
static func _dawn(rid: String, st: Dictionary, d: int) -> void:
	var an: Dictionary = st["animals"]
	if not an.has("bird"):
		return
	var eggs: Array = st["eggs"]
	var b: Dictionary = an["bird"]
	var n = int(b.get("n", 1))
	if not eggs.is_empty() and d - int(eggs[0]) >= int(rule("egg_hatch_days", 3)) and n < int(rule("max_birds", 3)):
		eggs.pop_front()
		b["n"] = n + 1
		st["hatch"] = d
		_log(st, "An egg left in the nest hatched. Another dove.")
	for i in range(int(b.get("n", 1))):
		if eggs.size() < int(rule("max_eggs", 3)) and int(b.get("d", 0)) < d:
			eggs.append(d)

static func _day(rid: String, st: Dictionary, d: int, s: int) -> void:
	var an: Dictionary = st["animals"]
	for k in an:
		var a: Dictionary = an[k]
		if int(a.get("pet", -1)) < d - 2 and int(a.get("aff", 0)) > 0 and int(a.get("d", d)) < d - 2:
			a["aff"] = int(a["aff"]) - 1
	# the night: a fox at an open pen empties the nest (doves lay again at dawn, see _dawn)
	var eggs: Array = st["eggs"]
	if bool(info(rid).get("foxes", false)) and bool(st.get("gate", false)) and not eggs.is_empty():
		eggs.clear()
		st["fox"] = d
		_log(st, "A fox got into the pen through the open gate. The nest is empty.")
	# mice in the ripe beds (a cat catches them instead)
	var ripe = []
	for key in st["plots"]:
		if is_ripe(st["plots"][key]):
			ripe.append(key)
	if not ripe.is_empty() and _roll(rid, s, "mice") < 0.35:
		if an.has("cat"):
			st["caught"] = d
		else:
			ripe.sort()
			var key2 = ripe[int(_roll(rid, s, "which") * ripe.size()) % ripe.size()]
			var p: Dictionary = st["plots"][key2]
			p["g"] = maxi(0, int(p.get("g", 0)) - 1)
			p["nb"] = s
			st["mice"] = d
			_log(st, "Mice got into the %s in the night. Nothing on the farm keeps them off." % crop(str(p.get("c", ""))).get("name", "beds"))

# ---------------------------------------------------------------- plots
static func key_of(c: Vector2i) -> String:
	return "%d,%d" % [c.x, c.y]

static func is_ripe(p: Dictionary) -> bool:
	var cid = str(p.get("c", ""))
	if cid == "":
		return false
	return int(p.get("g", 0)) >= crop(cid).get("stages", [0]).size() - 1

static func is_wet(rid: String, p: Dictionary) -> bool:
	return slot_now() <= int(p.get("w", -1)) or weather_now(rid) == "rain"

static func plot_cells(mid: String) -> Array:
	var out = []
	var m = Content.map(mid)
	if m.is_empty():
		return out
	for y in range(int(m["h"])):
		var row: String = m["grid"][y]
		for x in range(row.length()):
			if m["legend"].get(row[x], "") == "plot":
				out.append(Vector2i(x, y))
	return out

static func till(rid: String, c: Vector2i) -> bool:
	var st = state(rid)
	if st["plots"].has(key_of(c)):
		return false
	st["plots"][key_of(c)] = {"c": "", "g": 0, "w": -1}
	return true

static func plant(rid: String, c: Vector2i, seed_iid: String) -> bool:
	var cid = str(data().get("seed_crop", {}).get(seed_iid, ""))
	var st = state(rid)
	var p = st["plots"].get(key_of(c), null)
	if cid == "" or p == null or str(p.get("c", "")) != "" or Game.count(seed_iid) <= 0:
		return false
	Game.remove_item(seed_iid, 1)
	st["plots"][key_of(c)] = {"c": cid, "g": 0, "w": slot_now() if weather_now(rid) == "rain" else -1}
	Game.stat_add("ranch_planted")
	Game.emit_signal("state_changed")
	return true

static func water(rid: String, c: Vector2i) -> bool:
	var p = state(rid)["plots"].get(key_of(c), null)
	if p == null or str(p.get("c", "")) == "":
		return false
	p["w"] = slot_now() + 4
	return true

## Takes a ripe crop off its bed: [item, n] ([] when not ripe). The bed stays hoed.
static func harvest(rid: String, c: Vector2i) -> Array:
	var st = state(rid)
	var p = st["plots"].get(key_of(c), null)
	if p == null or not is_ripe(p):
		return []
	var cr = crop(str(p["c"]))
	st["plots"][key_of(c)] = {"c": "", "g": 0, "w": int(p.get("w", -1))}
	var iid = str(cr.get("item", ""))
	var k = int(cr.get("yield", 1))
	Game.add_item(iid, k)
	Game.stat_add("ranch_harvests")
	Game.emit_signal("state_changed")
	return [iid, k]

static func seeds_held() -> Array:
	var out = []
	for sid in data().get("seed_crop", {}):
		if Game.count(sid) > 0:
			out.append(sid)
	out.sort()
	return out

# ---------------------------------------------------------------- animals
static func owns(rid: String, kind: String) -> bool:
	return peek(rid).get("animals", {}).has(kind)

static func owned(rid: String) -> Array:
	var out = []
	for k in data().get("animal_order", []):
		if owns(rid, k):
			out.append(k)
	return out

static func price(kind: String) -> int:
	return int(animal(kind).get("price", 0))

## "ok" | "owned" | "unknown" | "gold"
static func can_buy(rid: String, kind: String) -> String:
	if info(rid).is_empty() or animal(kind).is_empty():
		return "unknown"
	if owns(rid, kind):
		return "owned"
	if Game.gold() < price(kind):
		return "gold"
	return "ok"

static func buy(rid: String, kind: String) -> String:
	var r = can_buy(rid, kind)
	if r != "ok":
		return r
	if not Game.spend_gold(price(kind)):
		return "gold"
	var first = owned(rid).is_empty()
	var d = day_now()
	var a = {"t": now(), "d": d, "aff": 0, "pet": -1, "got": d, "n": 1 if kind != "bird" else 2}
	if kind == "pig":
		a["got"] = d + int(rule("pig_grow_days", 3)) - 2      # the first truffle on the day it is grown
	state(rid)["animals"][kind] = a
	Game.stat_add("ranch_animals")
	if first:
		Game.stat_add("ranch_herds")
	Game.emit_signal("state_changed")
	return "ok"

static func aff(rid: String, kind: String) -> int:
	return int(peek(rid).get("animals", {}).get(kind, {}).get("aff", 0))

static func pig_grown(rid: String) -> bool:
	var a = peek(rid).get("animals", {}).get("pig", {})
	return not a.is_empty() and day_now() - int(a.get("d", 0)) >= int(rule("pig_grow_days", 3))

static func birds(rid: String) -> int:
	var a = peek(rid).get("animals", {}).get("bird", {})
	return 0 if a.is_empty() else int(a.get("n", 1))

static func yield_of(rid: String, kind: String) -> int:
	var f = aff(rid, kind)
	return 1 + (1 if f >= 6 else 0) + (1 if f >= 10 else 0)

## Goods waiting on an animal now (0 or its yield); doves give theirs through the nest.
static func ready_good(rid: String, kind: String) -> int:
	var a = peek(rid).get("animals", {}).get(kind, {})
	if a.is_empty() or kind in ["cat", "bird"]:
		return 0
	if kind == "pig" and not pig_grown(rid):
		return 0
	var every = int(animal(kind).get("every", 1))
	return yield_of(rid, kind) if day_now() - int(a.get("got", day_now())) >= every else 0

static func eggs(rid: String) -> int:
	return peek(rid).get("eggs", []).size()

static func ready_total(rid: String) -> int:
	var n = eggs(rid)
	for k in owned(rid):
		n += ready_good(rid, k)
	return n

## Pets an animal (once a day) and takes what it has. Returns the toast text.
static func tend(rid: String, kind: String) -> String:
	tick(rid)
	var st = state(rid)
	var a: Dictionary = st["animals"].get(kind, {})
	if a.is_empty():
		return ""
	var an = animal(kind)
	var today = day_now()
	var petted = false
	if int(a.get("pet", -1)) < today:
		a["pet"] = today
		a["aff"] = mini(10, int(a.get("aff", 0)) + 1)
		petted = true
		if int(a["aff"]) == 10:
			Game.stat_add("ranch_hearts")
	var n = ready_good(rid, kind)
	var parts = []
	if n > 0:
		a["got"] = today
		Game.add_item(str(an["good"]), n)
		Game.stat_add("ranch_goods", n)
		parts.append("%s x%d." % [Content.item_name(str(an["good"])), n])
	var line = ""
	match kind:
		"cow":
			line = "She leans into your hand." if petted else "She has had her scratch today."
		"pig":
			line = ("It roots at your boots, pleased with itself." if pig_grown(rid) else "The piglet squeals and follows your heel.") if petted else "It grunts. Once a day is enough, apparently."
		"bunny":
			line = "It allows the comb. Barely." if petted else "It has been combed today and holds the grudge."
		"cat":
			line = "The cat permits it, once, and goes back to watching the beds." if petted else "The cat has had enough of you for today."
		"bird":
			line = "The doves coo and settle." if petted else "The doves have had your attention today."
	parts.append(line)
	Game.emit_signal("state_changed")
	return " ".join(parts)

static func nest_take(rid: String) -> String:
	tick(rid)
	var st = state(rid)
	var e: Array = st["eggs"]
	if not owns(rid, "bird"):
		return "An empty nest in the straw. The rancher sells doves."
	if e.is_empty():
		var why = " A fox was here in the night." if int(st.get("fox", -99)) == day_now() else ""
		return "No eggs today." + why
	var n = e.size() + (1 if aff(rid, "bird") >= 6 else 0) + (1 if aff(rid, "bird") >= 10 else 0)
	e.clear()
	Game.add_item("RK02", n)
	Game.stat_add("ranch_goods", n)
	Game.emit_signal("state_changed")
	return "Dove Egg x%d, still warm." % n

# ---------------------------------------------------------------- the kart
static func kart(rid: String) -> Dictionary:
	return state(rid)["kart"]

static func kart_away(rid: String) -> bool:
	return int(peek(rid).get("kart", {}).get("away", -1)) >= 0 and not kart_back(rid)

## Back from the line: the morning (06:00) after it was sent.
static func kart_back(rid: String) -> bool:
	var away = int(peek(rid).get("kart", {}).get("away", -1))
	return away >= 0 and slot_now() >= (away + 1) * 4 + 1

static func kart_value(rid: String) -> int:
	var v = 0
	var ld: Dictionary = kart(rid)["load"]
	for iid in ld:
		v += int(Content.item(iid).get("price", 0)) / 2 * int(ld[iid])
	return int(round(v * (1.0 + rule("kart_bonus", 0.1))))

static func shippable() -> Array:
	var out = []
	for iid in Game.S.get("inventory", {}).get("items", {}):
		var it = Content.item(str(iid))
		if it.get("src", "") == "ranch" and it.get("ranch", "") in ["good", "crop", "cooked"] and Game.count(str(iid)) > 0:
			out.append(str(iid))
	out.sort()
	return out

static func kart_load(rid: String, iid: String, n: int) -> bool:
	if n <= 0 or Game.count(iid) < n or kart_away(rid):
		return false
	Game.remove_item(iid, n)
	var ld: Dictionary = kart(rid)["load"]
	ld[iid] = int(ld.get(iid, 0)) + n
	return true

static func kart_send(rid: String) -> bool:
	var k = kart(rid)
	if k["load"].is_empty() or kart_away(rid):
		return false
	k["pay"] = kart_value(rid)
	k["load"] = {}
	k["away"] = day_now()
	Game.stat_add("ranch_kart")
	return true

## Coins from a returned kart (0 when nothing is due).
static func kart_collect(rid: String) -> int:
	if not kart_back(rid):
		return 0
	var k = kart(rid)
	var pay = int(k.get("pay", 0))
	k["away"] = -1
	k["pay"] = 0
	Game.add_gold(pay)
	return pay

# ---------------------------------------------------------------- conditions
static func cond(parts: Array) -> bool:
	if parts.size() < 2:
		return false
	if parts[0] == "at":
		return Game.S.get("location", {}).get("map", "") == str(info(str(parts[1])).get("map", "?"))
	var rid = str(parts[0])
	match str(parts[1]):
		"own":
			return parts.size() > 2 and owns(rid, str(parts[2]))
		"birds":
			return parts.size() > 2 and birds(rid) >= int(parts[2])
		"gate":
			return bool(peek(rid).get("gate", false))
		"tools":
			return bool(peek(rid).get("tools", false))
		"ready":
			return ready_total(rid) > 0
		"any":
			return not owned(rid).is_empty()
	return false

# ---------------------------------------------------------------- scene command
static func _here(main: Node) -> String:
	return rid_of(str(Game.S.get("location", {}).get("map", "")))

static func run(main: Node, a: Array) -> void:
	var op: String = a[0] if a.size() > 0 else ""
	var interactive = not main.director.skipping and QA.route == ""
	var rid = str(a[1]) if a.size() > 1 and op in ["menu", "lend", "seeds", "buy"] else _here(main)
	match op:
		"menu":
			if interactive:
				await _menu(main, rid)
		"lend":
			await _lend(main, rid)
		"seeds":
			if interactive:
				await main.open_shop(str(info(rid).get("shop", "")))
		"buy":
			buy(rid, a[2] if a.size() > 2 else "")
		"plant":
			if interactive:
				await _plant(main, rid)
		"kart":
			if interactive:
				await _kart(main, rid)
		"animal":
			var id = str(main.director.ctx.get("npc", ""))
			var p = id.split("_")
			if p.size() >= 3:
				await main.say("", tend(rid, p[2].rstrip("0123456789")))
		"nest":
			await main.say("", nest_take(rid))
		_:
			push_error("ranch: unknown op " + op)
	if is_instance_valid(main.field):
		main.field.refresh_npcs()

static func _lend(main: Node, rid: String) -> void:
	var st = state(rid)
	var missing = []
	for t in data().get("tools", []):
		if Game.count(str(t)) <= 0:
			missing.append(str(t))
	st["tools"] = true
	if missing.is_empty():
		return
	for t in missing:
		Game.add_item(t, 1)
	Audio.sfx("FX007")
	await main.say("", "Received: " + ", ".join(missing.map(func(t): return Content.item_name(t))) + ".")

static func _menu(main: Node, rid: String) -> void:
	var r = info(rid)
	if r.is_empty():
		return
	tick(rid)
	while true:
		var pick = await main.choose(["Buy livestock", "Seed box", "How does it work?", "Leave"], 0)
		match pick:
			0:
				await _buy_menu(main, rid)
			1:
				await main.open_shop(str(r.get("shop", "")))
			2:
				await main.say("", "Face a dirt bed and press on: hoe it, plant a seed, water it. Water carries a crop four quarter days; rain does the watering for you.")
				await main.say("", "When it's ripe, the sickle takes it. Beasts give once a day if you come and see them, and more if they like you.")
				await main.say("", "Doves lay in the nest; leave an egg three days and it hatches. Goods ride the kart down the line and come back as coin in the morning.")
				match str(r.get("hazard", "")):
					"frost":
						await main.say("", "Snowy nights take a stage off anything growing. Pull what's ripe before dark.")
					"ember":
						await main.say("", "Ash storms scorch a dry bed. Keep them watered and the cinders roll off.")
					"wind":
						await main.say("", "The wind shakes everything up here. It does no harm. It just never stops.")
				if bool(r.get("foxes", false)):
					await main.say("", "Shut the pen gate at night. The foxes count eggs better than I do.")
			_:
				return

static func _buy_menu(main: Node, rid: String) -> void:
	var kinds: Array = info(rid).get("animals", [])
	var opts = []
	for k in kinds:
		opts.append("%s  %s" % [animal(k).get("name", k), "(yours)" if owns(rid, k) else "%d cr" % price(k)])
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
			await main.say("", "%s costs %d crowns. You have %d." % [an.get("name", kind), price(kind), Game.gold()])
			return
	await main.say("", str(an.get("note", "")))
	var yes = await main.choose(["Buy for %d crowns" % price(kind), "Not now"], 1)
	if yes != 0:
		return
	if buy(rid, kind) == "ok":
		Audio.sfx("FX007")
		await main.say("", "The %s is yours. It stays at %s; come and see it." % [an.get("name", kind), info(rid).get("name", "")])

static func _plant(main: Node, rid: String) -> void:
	var cell = main.director.ctx.get("cell", Vector2i(-1, -1))
	var held = seeds_held()
	if held.is_empty():
		await main.say("", "A hoed bed, empty. The rancher's seed box sells seed.")
		return
	var opts = []
	for s in held:
		opts.append("%s  x%d" % [Content.item_name(s), Game.count(s)])
	opts.append("Leave it")
	var pick = await main.choose(opts, 0)
	if pick < 0 or pick >= held.size():
		return
	if plant(rid, cell, held[pick]):
		Audio.sfx("FX010")
		fx("seed", cell)

static func _kart(main: Node, rid: String) -> void:
	tick(rid)
	if kart_back(rid):
		var pay = kart_collect(rid)
		Audio.sfx("FX007")
		fx("coin", Vector2i(-1, -1))
		await main.say("", "The kart came back up the line in the night. %d crowns in the chest, and a buyer's chit." % pay)
		return
	if kart_away(rid):
		await main.say("", "The kart is somewhere down the line. It comes back in the morning.")
		return
	while true:
		var goods = shippable()
		var ld: Dictionary = kart(rid)["load"]
		var opts = []
		var acts = []
		if not goods.is_empty():
			opts.append("Load every ranch good")
			acts.append("all")
		for iid in goods.slice(0, 6):
			opts.append("Load %s x%d" % [Content.item_name(iid), Game.count(iid)])
			acts.append(iid)
		if not ld.is_empty():
			opts.append("Send it off  (%d cr)" % kart_value(rid))
			acts.append("send")
			opts.append("Take it all back")
			acts.append("back")
		opts.append("Leave")
		acts.append("leave")
		if goods.is_empty() and ld.is_empty():
			await main.say("", "The kart's chest stands open. Ranch goods only: milk, eggs, wool, truffles, crops, dishes.")
			return
		var pick = await main.choose(opts, 0)
		var act = acts[pick] if pick >= 0 and pick < acts.size() else "leave"
		match act:
			"all":
				for iid in goods:
					kart_load(rid, iid, Game.count(iid))
				Audio.sfx("FX010")
			"send":
				if kart_send(rid):
					Audio.sfx("FX031")
					fx("depart", Vector2i(-1, -1))
					await main.say("", "The kart rolls off down the line with the goods. The buyers pay in the morning.")
				return
			"back":
				for iid in ld.keys():
					Game.add_item(iid, int(ld[iid]))
				ld.clear()
			"leave":
				return
			_:
				kart_load(rid, act, Game.count(act))
				Audio.sfx("FX010")

# ---------------------------------------------------------------- field: interaction
static var _fx: Array = []          # [{k kind, c cell, t0 field time, map}]
static var _field: Node = null

static func fx(kind: String, cell: Vector2i) -> void:
	if _field == null or not is_instance_valid(_field):
		return
	_fx.append({"k": kind, "c": cell, "t0": float(_field.time), "map": str(_field.map_id)})

static func on_enter(field: Node) -> void:
	_field = field
	_fx = []
	_ground_tex = {}
	var rid = rid_of(str(field.map_id))
	if rid == "":
		return
	tick(rid)
	_music(field, rid, true)

## Confirm on a cell of a ranch map. True when the ranch handled it (the field does nothing else).
static func interact(field: Node, ft: Vector2i) -> bool:
	var rid = rid_of(str(field.map_id))
	if rid == "":
		return false
	_field = field
	tick(rid)
	var st = state(rid)
	# animals the player owns, and the nest: tended on the spot (no dialogue)
	for n in field.npcs:
		if n["tile"] != ft:
			continue
		var id = str(n["id"])
		if id.begins_with("own_%s_" % rid):
			var kind = id.substr(5 + rid.length()).rstrip("0123456789")
			n["dir"] = {"up": "down", "down": "up", "left": "right", "right": "left"}[field.p_dir]
			var msg = tend(rid, kind)
			Audio.sfx("FX010")
			fx("hearts:%d" % aff(rid, kind), ft)
			field.main.toast(msg)
			return true
		if id == "nest_" + rid:
			field.main.toast(nest_take(rid))
			Audio.sfx("FX010")
			return true
		return false
	# the pen gate
	for e in field.map["entities"]:
		if e["type"] == "block" and e.get("tile", "") == "gate" and e["x1"] == ft.x and e["y1"] == ft.y:
			if field.p_tile == ft:
				return false
			st["gate"] = not bool(st.get("gate", false))
			Audio.sfx("FX008")
			field.main.toast("The gate is open. Shut it before night." if st["gate"] else "The gate is shut.")
			return true
	# farmhouse doors: the door swings open while its text shows
	var art = _art(field)
	for d in art.get("doors", []):
		if Vector2i(int(d[0]), int(d[1])) == ft:
			fx("door", ft)
			return false
	# the beds
	if field.kind_at(ft.x, ft.y) != "plot":
		return false
	var key = key_of(ft)
	if not bool(st.get("tools", false)) and Game.count("RT01") <= 0:
		field.main.toast("Hard dirt. The rancher lends tools to anyone who asks.")
		return true
	if not st["plots"].has(key):
		till(rid, ft)
		Audio.sfx("FX019")
		fx("dust", ft)
		return true
	var p: Dictionary = st["plots"][key]
	if str(p.get("c", "")) == "":
		if seeds_held().is_empty():
			field.main.toast("A hoed bed. The rancher's seed box sells seed.")
		else:
			field.emit_signal("request_scene", "RANCH_PLANT", {"cell": ft})
		return true
	var cr = crop(str(p["c"]))
	if is_ripe(p):
		var h = harvest(rid, ft)
		Audio.sfx("FX007")
		fx("sickle", ft)
		field.main.toast("%s x%d." % [Content.item_name(h[0]), int(h[1])])
		return true
	var last = cr.get("stages", [0]).size() - 1
	if is_wet(rid, p):
		field.main.toast("%s, stage %d of %d. Damp enough for now." % [cr.get("name", ""), int(p.get("g", 0)), last])
		return true
	water(rid, ft)
	Audio.sfx("FX013")
	fx("water", ft)
	return true

# ---------------------------------------------------------------- field: drawing helpers
static var _tex := {}
static var _ground_tex := {}
static var _art_cache := {}
static var _blob := {}

static func _t(path: String) -> Texture2D:
	if not _tex.has(path):
		var p = PACK + path if not path.begins_with("res://") else path
		_tex[path] = load(p) if ResourceLoader.exists(p) else null
	return _tex[path]

static func _art(field: Node) -> Dictionary:
	var mid = str(field.map_id)
	if not _art_cache.has(mid):
		var a = field.art
		_art_cache[mid] = a.data.get("ranch", {}) if a != null else {}
	return _art_cache[mid]

## Godot 3x3 minimal mask -> tile, decoded from the pack's template (red = the terrain's bits).
static func _blob_cell(mask: int) -> Vector2i:
	if _blob.is_empty():
		var t = _t("res://assets/ext/ranch/autotiles/template_godot_3x3.png")
		if t == null:
			return Vector2i(0, 3)
		var im = t.get_image()
		if im.is_compressed():
			im.decompress()
		var pts = [[1, 8, 3], [2, 13, 3], [4, 13, 8], [8, 13, 13], [16, 8, 13], [32, 3, 13], [64, 3, 8], [128, 3, 3]]
		for r in range(4):
			for c in range(12):
				var cc = im.get_pixel(c * 16 + 8, r * 16 + 8)
				if not (cc.r > 0.78 and cc.g < 0.6):
					continue
				var m = 0
				for p in pts:
					var px = im.get_pixel(c * 16 + int(p[1]), r * 16 + int(p[2]))
					if px.r > 0.78 and px.g < 0.6:
						m |= int(p[0])
				m = _norm(m)
				if not _blob.has(m):
					_blob[m] = Vector2i(c, r)
	if _blob.has(mask):
		return _blob[mask]
	return _blob.get(_norm(mask & 85), _blob.get(0, Vector2i(0, 3)))

static func _norm(m: int) -> int:
	if not (m & 1 and m & 4):
		m &= ~2
	if not (m & 16 and m & 4):
		m &= ~8
	if not (m & 16 and m & 64):
		m &= ~32
	if not (m & 1 and m & 64):
		m &= ~128
	return m

static func _mask(cells: Dictionary, c: Vector2i) -> int:
	var m = 0
	var bits = [[1, 0, -1], [2, 1, -1], [4, 1, 0], [8, 1, 1], [16, 0, 1], [32, -1, 1], [64, -1, 0], [128, -1, -1]]
	for b in bits:
		if cells.has(c + Vector2i(int(b[1]), int(b[2]))):
			m |= int(b[0])
	return _norm(m)

## Screen position (units) of a ground point (units): through the HD-2D camera, or the flat 2D camera.
static func _gp(field: Node, p: Vector2) -> Vector2:
	if field.hd_on:
		return field.hd.project(p)[0]
	return p - field.cam

## Light on flat overlays so they sit in the lit HD-2D ground: the stage's ambient (its sun is a faint extra that
## the ground in the gallery shots does not show, so it is left out).
static func _ground_light(field: Node) -> Color:
	if not field.hd_on:
		return Color.WHITE
	var env: Environment = field.hd.env
	var a = env.ambient_light_color * env.ambient_light_energy
	return Color(minf(1.0, a.r), minf(1.0, a.g), minf(1.0, a.b), 1.0)

static func _quad(ci: CanvasItem, field: Node, tex: Texture2D, cell: Vector2i, src: Rect2, col: Color) -> void:
	var p0 = Vector2(cell * 16)
	var pts = PackedVector2Array([_gp(field, p0), _gp(field, p0 + Vector2(16, 0)), _gp(field, p0 + Vector2(16, 16)), _gp(field, p0 + Vector2(0, 16))])
	var ts = tex.get_size()
	var e = 0.02
	var uv = PackedVector2Array([Vector2(src.position.x + e, src.position.y + e) / ts, Vector2(src.end.x - e, src.position.y + e) / ts,
		Vector2(src.end.x - e, src.end.y - e) / ts, Vector2(src.position.x + e, src.end.y - e) / ts])
	ci.draw_polygon(pts, PackedColorArray([col, col, col, col]), uv, tex)

static func _in_view(field: Node, c: Vector2i) -> bool:
	var cx = field.cam.x / 16.0
	var cy = field.cam.y / 16.0
	var m = 10.0 if field.hd_on else 1.0
	return c.x >= cx - m and c.x <= cx + 21 + m and c.y >= cy - m - 4 and c.y <= cy + 16 + m

# ---------------------------------------------------------------- field: ground overlays (under every upright)
static func draw_ground(field: Node) -> void:
	var rid = rid_of(str(field.map_id))
	if rid == "":
		return
	var ci: CanvasItem = field
	var col = _ground_light(field)
	var art = _art(field)
	# animated water (the baked ground holds frame 0)
	var ws = _t("res://assets/ext/" + str(art.get("water_sheet", ""))) if art.has("water_sheet") else null
	if ws != null:
		var f = int(field.time * 3.0) % 4
		for w in art.get("water", []):
			var c = Vector2i(int(w[0]), int(w[1]))
			if _in_view(field, c):
				_quad(ci, field, ws, c, Rect2(f * 192 + int(w[2]) * 16, int(w[3]) * 16, 16, 16), col)
	if field.art == null:
		# no pack map art installed: the tileset has no dirt-bed kind, so the beds are drawn as plain dirt
		for c0 in plot_cells(str(field.map_id)):
			if _in_view(field, c0):
				ci.draw_rect(Rect2(_gp(field, Vector2(c0 * 16)), Vector2(16, 16)), Color8(150, 100, 64))
	# the player's hoed beds: the field autotile over the hoed cells, darker where watered
	var st = peek(rid)
	var plots: Dictionary = st.get("plots", {})
	if plots.is_empty():
		return
	var tl: Array = art.get("tilled", ["ranch/autotiles/field_02.png", "ranch/autotiles/field_wet.png"])
	var dry = _t("res://assets/ext/" + str(tl[0]))
	var wet = _t("res://assets/ext/" + str(tl[1]))
	var cells := {}
	for key in plots:
		var p = str(key).split(",")
		cells[Vector2i(int(p[0]), int(p[1]))] = true
	for c in cells:
		if not _in_view(field, c):
			continue
		var pl: Dictionary = plots[key_of(c)]
		var t = wet if (str(pl.get("c", "")) != "" and is_wet(rid, pl)) else dry
		if t == null:
			var r = Rect2(_gp(field, Vector2(c * 16) + Vector2(2, 2)), Vector2(12, 12))
			ci.draw_rect(r, Color8(110, 70, 50) if t == dry else Color8(80, 46, 44))
			continue
		var bc = _blob_cell(_mask(cells, c))
		_quad(ci, field, t, c, Rect2(bc.x * 16, bc.y * 16, 16, 16), col)

# ---------------------------------------------------------------- field: uprights (y-sorted with actors)
## Adds the ranch's upright things to the field's draw list: [sort_y, "ranch", payload, screen pos of the cell].
static func collect(field: Node, talls: Array) -> void:
	var rid = rid_of(str(field.map_id))
	if rid == "":
		return
	var ox = -field.cam
	var st = peek(rid)
	var plots: Dictionary = st.get("plots", {})
	for key in plots:
		var pl: Dictionary = plots[key]
		if str(pl.get("c", "")) == "":
			continue
		var p = str(key).split(",")
		var c = Vector2i(int(p[0]), int(p[1]))
		if _in_view(field, c):
			talls.append([c.y * 16 + 14, "ranch", {"k": "crop", "p": pl, "c": c, "rid": rid}, Vector2(c * 16) + ox])
	var art = _art(field)
	for b in art.get("beds", []):
		var c2 = Vector2i(int(b[0]), int(b[1]))
		if _in_view(field, c2):
			talls.append([c2.y * 16 + 14, "ranch", {"k": "bed", "crop": str(b[2]), "f": int(b[3]), "c": c2}, Vector2(c2 * 16) + ox])
	for fpos in art.get("fires", []):
		var c3 = Vector2i(int(fpos[0]) / 16, int(fpos[1]) / 16 + 1)
		if _in_view(field, c3):
			talls.append([c3.y * 16 + 15, "ranch", {"k": "fire", "c": c3}, Vector2(c3 * 16) + ox])
	for g in art.get("gates", []):
		var c4 = Vector2i(int(g[0]), int(g[1]))
		if not bool(st.get("gate", false)):
			talls.append([c4.y * 16 + 15, "ranch", {"k": "gate", "g": g, "c": c4}, Vector2(c4 * 16) + ox])
	for d in art.get("doors", []):
		var c5 = Vector2i(int(d[0]), int(d[1]))
		var f = _door_frame(field, c5)
		if f >= 0:
			talls.append([c5.y * 16 + 16.2, "ranch", {"k": "door", "f": f, "c": c5}, Vector2(c5 * 16) + ox])
	# night visitors: a fox at an open pen, a mouse at a ripe bed, the cat's catch on the step by day
	var night = Field.is_night()
	var nest = _npc_home(field, "nest_" + rid)
	if night and bool(info(rid).get("foxes", false)) and bool(st.get("gate", false)) and nest.x >= 0:
		var fp = Vector2(nest * 16) + Vector2(-24 + 16 * sin(field.time * 0.8), 18)
		talls.append([fp.y + 15, "ranch", {"k": "fox", "dx": cos(field.time * 0.8)}, fp + ox])
	if night and not owns(rid, "cat"):
		for key in plots:
			if is_ripe(plots[key]):
				var p2 = str(key).split(",")
				var mp = Vector2(int(p2[0]) * 16 + 10 + 6 * sin(field.time * 1.7), int(p2[1]) * 16 + 4)
				talls.append([mp.y + 15, "ranch", {"k": "mouse", "dx": cos(field.time * 1.7)}, mp + ox])
				break
	if not night and int(st.get("caught", -99)) == day_now() and not art.get("doors", []).is_empty():
		var dc = Vector2i(int(art["doors"][0][0]) + 1, int(art["doors"][0][1]) + 1)
		talls.append([dc.y * 16 + 10, "ranch", {"k": "deadmouse"}, Vector2(dc * 16) + ox])
	# tool effects
	var keep = []
	for e in _fx:
		if e["map"] != str(field.map_id):
			continue
		var age = float(field.time) - float(e["t0"])
		if age > 2.6:
			continue
		keep.append(e)
		var c6: Vector2i = e["c"]
		if c6.x < 0:
			var kc = _npc_home(field, "kart_" + rid)
			c6 = kc
		talls.append([c6.y * 16 + 15.5, "ranch", {"k": "fx", "e": e, "age": age}, Vector2(c6 * 16) + ox])
	_fx = keep

static func _npc_home(field: Node, id: String) -> Vector2i:
	for n in field.npcs:
		if str(n["id"]) == id:
			return n["tile"]
	return Vector2i(-1, -1)

static func _door_frame(field: Node, c: Vector2i) -> int:
	for e in _fx:
		if e["k"] == "door" and e["c"] == c and e["map"] == str(field.map_id):
			var age = float(field.time) - float(e["t0"])
			if age < 0.4:
				return int(age / 0.1)
			if age < 2.0:
				return 3
			if age < 2.4:
				return 3 - int((age - 2.0) / 0.1)
	return -1

static func _strip(ci: CanvasItem, tex: Texture2D, fw: int, fh: int, f: int, at: Vector2, flip: bool = false, mod: Color = Color.WHITE) -> void:
	if tex == null:
		return
	var cols = maxi(1, int(tex.get_width()) / fw)
	var src = Rect2((f % cols) * fw, (f / cols) * fh, fw, fh)
	var dst = Rect2(at, Vector2(fw, fh))
	if flip:
		dst = Rect2(at + Vector2(fw, 0), Vector2(-fw, fh))
	ci.draw_texture_rect_region(tex, dst, src, mod)

static func draw_tall(field: Node, pl: Dictionary, pos: Vector2) -> void:
	var ci: CanvasItem = field
	var t = float(field.time)
	match str(pl.get("k", "")):
		"crop":
			_draw_crop(field, pl, pos)
		"bed":
			var cr = crop(str(pl["crop"]))
			var tex = _t(str(cr.get("strip", "")))
			var fw = int(cr.get("fw", 16))
			var fh = int(cr.get("fh", 16))
			var sway = round(sin(t * 1.3 + pos.x * 0.07) * 0.6 * 3.0) / 3.0
			_strip(ci, tex, fw, fh, int(pl["f"]), pos + Vector2(8 - fw / 2.0 + sway, 15 - fh))
		"fire":
			var tex2 = _t("objects/campfires/campfire_05_16x32_3frames.png")
			_strip(ci, tex2, 16, 32, int(t * 8.0) % 3, pos + Vector2(0, -16))
		"gate":
			var g: Array = pl["g"]
			var sh = _t("res://assets/ext/" + str(_art(field).get("fence_sheet", "")))
			if sh != null:
				ci.draw_texture_rect_region(sh, Rect2(pos, Vector2(16, 16)), Rect2(int(g[2]) * 16, int(g[3]) * 16, 16, 16))
		"door":
			var f = int(pl["f"])
			var tex3 = _t("buildings/doors/door_01/opening/door_01_opening_16x16_4frames.png")
			_strip(ci, tex3, 16, 16, clampi(f, 0, 3), pos)
		"fox":
			var tex4 = _t("animals/foxes/fox_01/move/fox_01_move_%s_16x20_4frames.png" % ("right" if float(pl["dx"]) > 0 else "left"))
			_strip(ci, tex4, 16, 20, int(t * 6) % 4, pos + Vector2(0, -4))
		"mouse":
			var tex5 = _t("animals/mouses/mouse_01/move/mouse_01_move_%s_16x20_4frames.png" % ("right" if float(pl["dx"]) > 0 else "left"))
			_strip(ci, tex5, 16, 20, int(t * 8) % 4, pos + Vector2(0, -4))
		"deadmouse":
			_strip(ci, _t("animals/mouses/mouse_01/dead/mouse_01_dead_16x20.png"), 16, 20, 0, pos + Vector2(0, -4))
		"fx":
			_draw_fx(field, pl["e"], float(pl["age"]), pos)

static func _draw_crop(field: Node, pl: Dictionary, pos: Vector2) -> void:
	var ci: CanvasItem = field
	var p: Dictionary = pl["p"]
	var rid = str(pl["rid"])
	var cid = str(p.get("c", ""))
	var cr = crop(cid)
	var stages: Array = cr.get("stages", [0])
	var g = clampi(int(p.get("g", 0)), 0, stages.size() - 1)
	var f = int(stages[g])
	var fw = int(cr.get("fw", 16))
	var fh = int(cr.get("fh", 16))
	var tex = _t(str(cr.get("strip", "")))
	var t = float(field.time)
	var sn = slot_now()
	var frozen = int(p.get("fz", -99)) >= sn - 1
	var burnt = int(p.get("bn", -99)) >= sn - 1
	var hz = str(info(rid).get("hazard", ""))
	var at = pos + Vector2(8 - fw / 2.0, 15 - fh)
	var mod = Color.WHITE
	if cid == "corn":
		# corn's own strips: frozen / on fire / shaking in the wind (8 frames each, the growth_basic stages)
		var cs: Dictionary = data().get("corn_strips", {})
		var bf = clampi(int(round(float(g) / maxf(1.0, stages.size() - 1) * 5.0)), 0, 7)
		if frozen and cs.has("frozen"):
			_strip(ci, _t(str(cs["frozen"])), 16, 32, bf, at)
			return
		if burnt and cs.has("fire"):
			_strip(ci, _t(str(cs["fire"])), 16, 32, bf, at)
			return
		if hz == "wind" and g >= stages.size() - 1 and cs.has("tempest") and weather_now(rid) != "":
			_strip(ci, _t(str(cs["tempest"])), 16, 32, int(t * 10) % 12, at)
			return
		if hz == "wind" and g >= stages.size() - 1 and cs.has("shake"):
			_strip(ci, _t(str(cs["shake"])), 16, 32, int(t * 8) % 8, at)
			return
	var sway = 0.0
	if hz == "wind":
		sway = round(sin(t * 4.0 + pos.x * 0.3) * 1.0 * 3.0) / 3.0
	if frozen:
		mod = Color(0.72, 0.88, 1.15)
	elif burnt:
		mod = Color(0.75, 0.55, 0.45)
	_strip(ci, tex, fw, fh, f, at + Vector2(sway, 0), false, mod)
	if burnt:
		var ft = _t("visual_effects/fires/fire_01_16x16_3frames.png")
		_strip(ci, ft, 16, 26, int(t * 8) % 3, pos + Vector2(0, -12), false, Color(1, 1, 1, 0.85))

static func _draw_fx(field: Node, e: Dictionary, age: float, pos: Vector2) -> void:
	var ci: CanvasItem = field
	var k = str(e["k"])
	if k == "dust" and age < 0.6:
		for i in range(6):
			var a = i * 1.05 + 0.3
			var r = 3.0 + age * 14.0
			var p = pos + Vector2(8, 12) + Vector2(cos(a) * r, sin(a) * r * 0.5 - age * 8.0)
			ci.draw_rect(Rect2(p, Vector2(2, 2)), Color(0.55, 0.36, 0.24, 1.0 - age / 0.6))
	elif k == "water" and age < 0.9:
		var tex = _t("visual_effects/droplets/droplet_01_16x16_5frames.png")
		var f = int(age / 0.18)
		for o in [Vector2(-4, 2), Vector2(4, -1), Vector2(0, 4)]:
			_strip(ci, tex, 16, 16, clampi(f, 0, 4), pos + o)
	elif k == "sickle" and age < 0.8:
		var tex2 = _t("objects/sickle/sickle_slicing/sickle_slicing_48x48_8frames.png")
		_strip(ci, tex2, 48, 48, clampi(int(age / 0.1), 0, 7), pos + Vector2(-16, -24))
	elif k == "seed" and age < 0.5:
		for i in range(4):
			ci.draw_rect(Rect2(pos + Vector2(4 + i * 3, 9 + (i % 2) * 2 - age * 6.0), Vector2(1, 1)), Color(0.95, 0.78, 0.4, 1.0 - age / 0.5))
	elif k.begins_with("hearts:") and age < 1.4:
		var n = int(k.substr(7))
		var y = -12.0 - minf(age, 0.4) * 10.0
		var x0 = 8.0 - 5 * 4.0
		for i in range(5):
			var full = n >= (i + 1) * 2
			var half = not full and n >= i * 2 + 1
			var tex3 = _t("icons/heart_0%d_16x16.png" % (1 if full else (2 if half else 3)))
			if tex3 != null:
				ci.draw_texture_rect(tex3, Rect2(pos + Vector2(x0 + i * 8, y), Vector2(8, 8)), false, Color(1, 1, 1, 1.0 - maxf(0.0, age - 1.0) / 0.4))
	elif k == "coin" and age < 1.6:
		var tex4 = _t("objects/coins/coin_01/coin_01_16x16_8frames.png")
		for i in range(3):
			_strip(ci, tex4, 16, 16, int(age * 12 + i * 3) % 8, pos + Vector2(-8 + i * 8, -18 - age * 10 - i * 3))

# ---------------------------------------------------------------- field: NPC sprites "ranch:<key>"
const FOLK_ROW := {"down": 0, "left": 1, "right": 2, "up": 3}
const DIRS := ["down", "left", "right", "up"]

static func _cow_colour(rid: String) -> String:
	return str(info(rid).get("cow", "brown"))

static var _grow := {}

static func draw_field(ci: CanvasItem, key: String, dir: String, frame: int, pos: Vector2) -> void:
	var p = key.split(":")
	var kind = p[0]
	var moving = frame > 0
	var d = dir if dir in DIRS else "down"
	var t = Time.get_ticks_msec() / 1000.0
	if _field != null and is_instance_valid(_field):
		t = float(_field.time)
	var shadow = func(w: float):
		ci.draw_rect(Rect2(pos + Vector2(8 - w / 2.0, 13.5), Vector2(w, 2.5)), Color(0, 0, 0, 0.22))
	match kind:
		"folk":
			var look = p[1] if p.size() > 1 else "m"
			var task = p[2] if p.size() > 2 else "idle"
			if moving:
				task = "walk"
			var fmt: String = str(data().get("folk", {}).get(look, "characters/males/male_01/%s/male_01_%s"))
			var base = fmt % [task, task]
			var tex = _t(base + ("_32x32.png" if task == "idle" else "_32x32_3frames.png"))
			if tex == null:
				_fallback(ci, pos, Color8(150, 110, 80), 8, 14)
				return
			shadow.call(10.0)
			var n = 1 if task == "idle" else 3
			var f = 0
			if task == "walk":
				f = [0, 1, 2, 1][int(t * 7) % 4] if moving else 1
			elif n == 3:
				f = int(t * 4.0) % 3
			ci.draw_texture_rect_region(tex, Rect2(pos + Vector2(-8, -9), Vector2(32, 32)), Rect2(f * 32, int(FOLK_ROW[d]) * 32, 32, 32))
		"cow":
			var col = _cow_colour(p[1] if p.size() > 1 else "R01")
			var b = "animals/cows/cow_01/%s/" % col
			shadow.call(18.0 if d in ["left", "right"] else 12.0)
			if moving:
				_strip(ci, _t(b + "move/cow_01_%s_move_%s_32x32_4frames.png" % [col, d]), 32, 32, int(t * 6) % 4, pos + Vector2(-8, -11))
			else:
				_strip(ci, _t(b + "idle/cow_01_%s_idle_%s_32x32.png" % [col, d]), 32, 32, 0, pos + Vector2(-8, -11))
		"pig":
			var rid = p[1] if p.size() > 1 else "R01"
			var colr = str(info(rid).get("pig", "pink"))
			var adult = p.size() > 2 and p[2] == "adult"
			if not adult:
				adult = pig_grown(rid)
				var a = peek(rid).get("animals", {}).get("pig", {})
				if adult and not bool(a.get("seen", false)) and not a.is_empty():
					# the first sight of the grown pig: the pack's grow strip, then the adult
					if not _grow.has(rid):
						_grow[rid] = t
					var age = t - float(_grow[rid])
					if age < 1.5:
						shadow.call(12.0)
						_strip(ci, _t("animals/pigs/pig_01/%s/baby/grow/pig_01_%s_baby_grow_32x32_6frames.png" % [colr, colr]), 32, 32, clampi(int(age / 0.25), 0, 5), pos + Vector2(-8, -11))
						return
					state(rid)["animals"]["pig"]["seen"] = true
			var b2 = "animals/pigs/pig_01/%s/%s" % [colr, "" if adult else "baby/"]
			var nm = "pig_01_%s_%s" % [colr, "" if adult else "baby_"]
			shadow.call(14.0 if adult else 9.0)
			var oy = -11 if adult else -8
			if moving:
				_strip(ci, _t(b2 + "move/" + nm + "move_%s_32x32_4frames.png" % d), 32, 32, int(t * 6) % 4, pos + Vector2(-8, oy))
			else:
				_strip(ci, _t(b2 + "idle/" + nm + "idle_%s_32x32.png" % d), 32, 32, 0, pos + Vector2(-8, oy))
		"bird":
			shadow.call(6.0)
			if moving:
				_strip(ci, _t("animals/birds/bird_01/fly/bird_01_fly_%s_16x20_4frames.png" % d), 16, 20, int(t * 10) % 4, pos + Vector2(0, -8))
			else:
				var side = "left" if d in ["left", "up"] else "right"
				var bob = -1 if int(t * 2.0 + pos.x) % 5 == 0 else 0
				_strip(ci, _t("animals/birds/bird_01/idle/bird_01_idle_%s_16x20.png" % side), 16, 20, 0, pos + Vector2(0, -1 + bob))
		"bunny", "fox", "mouse":
			var nm2 = {"bunny": "bunnies/bunny_01/%s/bunny_01_%s", "fox": "foxes/fox_01/%s/fox_01_%s", "mouse": "mouses/mouse_01/%s/mouse_01_%s"}[kind]
			shadow.call(8.0)
			if moving:
				_strip(ci, _t("animals/" + (nm2 % ["move", "move"]) + "_%s_16x20_4frames.png" % d), 16, 20, int(t * 8) % 4, pos + Vector2(0, -4))
			else:
				_strip(ci, _t("animals/" + (nm2 % ["idle", "idle"]) + "_%s_16x20.png" % d), 16, 20, 0, pos + Vector2(0, -4))
		"cat":
			shadow.call(8.0)
			if moving:
				_strip(ci, _t("animals/cats/cat_01/move/cat_01_move_%s_16x20_4frames.png" % d), 16, 20, int(t * 8) % 4, pos + Vector2(0, -4))
			elif not Field.is_night() and Field.hour() >= 9.0 and Field.hour() < 18.0:
				_strip(ci, _t("animals/cats/cat_01/sleep/cat_01_sleep_16x20_2frames.png"), 16, 20, int(t * 1.2) % 2, pos + Vector2(0, -4))
			else:
				_strip(ci, _t("animals/cats/cat_01/idle/cat_01_idle_%s_16x20.png" % d), 16, 20, 0, pos + Vector2(0, -4))
		"nest":
			_draw_nest(ci, p[1] if p.size() > 1 else "", pos, t)
		"kart":
			_draw_kart(ci, p[1] if p.size() > 1 else "", pos, t)
		_:
			_fallback(ci, pos, Color8(160, 140, 120), 10, 6)

static func _fallback(ci: CanvasItem, pos: Vector2, col: Color, w: float, h: float) -> void:
	var base = pos + Vector2(8, 15)
	ci.draw_rect(Rect2(base + Vector2(-w / 2.0, -h), Vector2(w, h)), col)

static func _draw_nest(ci: CanvasItem, rid: String, pos: Vector2, t: float) -> void:
	_strip(ci, _t("animals/birds/nest_16x20.png"), 16, 20, 0, pos + Vector2(0, -4))
	var st = peek(rid)
	var e: Array = st.get("eggs", [])
	var offs = [Vector2(-3, -6), Vector2(3, -7), Vector2(0, -4)]
	for i in range(mini(3, e.size())):
		var age = day_now() - int(e[i])
		var at = pos + offs[i]
		if age >= int(rule("egg_hatch_days", 3)) - 1:
			_strip(ci, _t("animals/egg/move/egg_move_16x20_4frames.png"), 16, 20, int(t * 6 + i) % 4, at)   # about to hatch
		else:
			_strip(ci, _t("animals/egg/idle/egg_idle_16x20.png"), 16, 20, 0, at)
	if int(st.get("hatch", -99)) == day_now():
		_strip(ci, _t("animals/egg/opened/egg_opened_16x20.png"), 16, 20, 0, pos + Vector2(10, -2))

static func _draw_kart(ci: CanvasItem, rid: String, pos: Vector2, t: float) -> void:
	var st = peek(rid)
	var k: Dictionary = st.get("kart", {})
	var art = _art(_field) if _field != null and is_instance_valid(_field) else {}
	var rails: Array = art.get("rails", [0, 0, 0, 1])
	var east = int(rails[3]) > 0 if rails.size() > 3 else true
	var side = "right" if east else "left"
	# rolling off: the chest kart runs down the rails to the map edge, then it is away
	for e in _fx:
		if e["k"] == "depart":
			var age = float(_field.time) - float(e["t0"])
			if age < 3.0:
				var dx = (1.0 if east else -1.0) * age * age * 30.0
				_strip(ci, _t("objects/kart/move/chest_move_%s_22x25_3frames.png" % side), 22, 25, int(age * 10) % 3, pos + Vector2(-3 + dx, -10))
				return
	if kart_away(rid):
		return
	var name = "idle_%s_22x25.png" % side
	if not k.get("load", {}).is_empty() or kart_back(rid):
		name = "chest_closed_idle_%s_22x25.png" % side
	elif true:
		name = "chest_opened_idle_%s_22x25.png" % side
	ci.draw_rect(Rect2(pos + Vector2(-1, 12), Vector2(18, 3)), Color(0, 0, 0, 0.22))
	_strip(ci, _t("objects/kart/idle/" + name), 22, 25, 0, pos + Vector2(-3, -10))
	if kart_back(rid):
		_strip(ci, _t("objects/coins/coin_01/coin_01_16x16_8frames.png"), 16, 16, int(t * 10) % 8, pos + Vector2(0, -22 + sin(t * 3.0)))

# ---------------------------------------------------------------- field: over everything (fireflies, sun rays, wind)
static func draw_after(field: Node) -> void:
	var rid = rid_of(str(field.map_id))
	if rid == "":
		return
	var ci: CanvasItem = field
	var t = float(field.time)
	var art = _art(field)
	var w = weather_now(rid)
	if Field.is_night():
		var tex = _t("animals/fireflies/firefly_01/idle/firefly_01_idle_16x16_4frames.png")
		var i = 0
		for f in art.get("fireflies", []):
			for j in range(2):
				var k = i * 2 + j
				var p = Vector2(float(f[0]) * 16 + 8, float(f[1]) * 16 + 8) + Vector2(sin(t * 0.6 + k * 2.1) * 20, cos(t * 0.45 + k * 1.3) * 12)
				var sp = _gp(field, p) - Vector2(0, 10 + 3 * sin(t * 1.7 + k))
				if tex != null:
					# a glow: brighter than the night tint on the field, so it reads as light
					_strip(ci, tex, 16, 16, int(t * 6 + k) % 4, sp - Vector2(8, 8), false, Color(2.4, 2.1, 1.3, 0.95))
			i += 1
	elif w == "" and Field.hour() >= 7.0 and Field.hour() < 17.5:
		var ray = _t("weathers/rays/ray_01/ray_01_white_320x240.png")
		if ray != null:
			ci.draw_texture_rect(ray, Rect2(Vector2.ZERO, Vector2(320, 240)), false, Color(1, 1, 1, 0.22 + 0.06 * sin(t * 0.5)))
	if str(info(rid).get("hazard", "")) == "wind":
		var wt = _t("weathers/winds/wind_01/wind_01_272x160.png")
		if wt != null:
			var ox = fmod(t * 90.0, 272.0)
			for xx in range(-1, 2):
				for yy in range(0, 2):
					ci.draw_texture_rect(wt, Rect2(Vector2(xx * 272 + ox, yy * 160 - 20), Vector2(272, 160)), false, Color(1, 1, 1, 0.45))
	_music(field, rid, false)

static var _cue := ""

## The pack's own music on the ranch maps when it is installed: the field theme by day, the night ambient after
## dark, the rain ambient in rain (WAV, looped here). Otherwise the map's music stays.
static func _music(field: Node, rid: String, force: bool) -> void:
	var want = "field"
	if str(info(rid).get("region", "")) in ["R02", "R08"]:
		want = "village"
	if Field.is_night():
		want = "night"
	elif weather_now(rid) == "rain":
		want = "rain"
	if want == _cue and not force:
		return
	var path = ART + "music/%s.wav" % want
	if not ResourceLoader.exists(path):
		return
	_cue = want
	var st = load(path)
	if st is AudioStreamWAV:
		st.loop_mode = AudioStreamWAV.LOOP_FORWARD
		st.loop_begin = 0
		st.loop_end = int(st.get_length() * st.mix_rate)
	var pl: AudioStreamPlayer = Audio._music_b if Audio._cur == Audio._music_a else Audio._music_a
	var old: AudioStreamPlayer = Audio._cur
	Audio.current_cue = "ranch_" + want
	pl.stream = st
	pl.volume_db = -40.0
	pl.play()
	Audio._cur = pl
	var tw = Audio.create_tween()
	tw.tween_property(pl, "volume_db", -4.0, 1.2)
	Audio._fade_out(old, 1.2)

# ---------------------------------------------------------------- item icons (assets/ext/ranch/icons.png)
static func draw_icon(ci: CanvasItem, pos: Vector2, iid: String, scale: float = 1.0) -> bool:
	var it: Dictionary = Content.item(iid)
	var t = _t("res://assets/ext/ranch/icons.png")
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
		var st = peek(rid)
		var right = ""
		if not st.is_empty() and (not st.get("animals", {}).is_empty() or not st.get("plots", {}).is_empty()):
			tick(rid)
			var ripe = 0
			for k in state(rid)["plots"]:
				if is_ripe(state(rid)["plots"][k]):
					ripe += 1
			right = "%d/%d" % [owned(rid).size(), r.get("animals", []).size()]
			if ready_total(rid) > 0 or ripe > 0 or kart_back(rid):
				right += " !"
		out.append({"text": str(r.get("name", rid)), "right": right, "value": rid,
			"color": UI.C_TEXT if right != "" else UI.C_DIM})
	return out

## Draws a ranch's page in the Records panel at rect r (beds, beasts with their hearts, nest, kart, news).
static func draw_record(ci: CanvasItem, rid: String, r: Rect2) -> void:
	var inf = info(rid)
	if inf.is_empty():
		return
	var x = r.position.x + 7
	var y = r.position.y + 5
	UI.text(ci, Vector2(x, y), str(inf.get("name", rid)), UI.C_GOLD)
	y += 11
	UI.text(ci, Vector2(x, y), "%s  -  %s" % [inf.get("town", ""), inf.get("rancher", "")], UI.C_DIM)
	y += 13
	var st = peek(rid)
	if st.is_empty() or int(st.get("v", 1)) < 2:
		UI.text(ci, Vector2(x, y), "Not farmed yet.", UI.C_DIM)
		y += 11
		for c in inf.get("seeds", []):
			UI.text(ci, Vector2(x + 4, y), "Seed: " + str(crop(c).get("name", c)), UI.C_DIM)
			y += 11
		return
	tick(rid)
	st = state(rid)
	# beds
	var plots: Dictionary = st["plots"]
	var n_hoed = plots.size()
	var planted = []
	for k in plots:
		if str(plots[k].get("c", "")) != "":
			planted.append(k)
	planted.sort()
	UI.text(ci, Vector2(x, y), "Beds  %d hoed, %d planted" % [n_hoed, planted.size()], UI.C_LABEL)
	y += 11
	var shown = 0
	for k in planted:
		if shown >= 5:
			UI.text(ci, Vector2(x + 4, y), "...and %d more" % (planted.size() - shown), UI.C_DIM)
			y += 11
			break
		var p: Dictionary = plots[k]
		var cr = crop(str(p["c"]))
		var last = cr.get("stages", [0]).size() - 1
		var txt = "%s  %d/%d" % [cr.get("name", ""), int(p.get("g", 0)), last]
		var col = UI.C_TEXT
		if is_ripe(p):
			txt += "  ripe"
			col = UI.C_GREEN
		elif is_wet(rid, p):
			txt += "  watered"
			col = UI.C_BLUE
		else:
			txt += "  dry"
		draw_icon(ci, Vector2(x + 2, y - 1), str(cr.get("item", "")), 10.0 / 16.0)
		UI.text(ci, Vector2(x + 15, y), txt, col)
		y += 11
		shown += 1
	y += 2
	# beasts
	UI.text(ci, Vector2(x, y), "Beasts", UI.C_LABEL)
	y += 11
	for kind in inf.get("animals", []):
		var an = animal(kind)
		if not owns(rid, kind):
			UI.text(ci, Vector2(x + 4, y), "%s  -  %d cr" % [an.get("name", kind), price(kind)], UI.C_DIM)
			y += 11
			continue
		var label = {"cow": "Cow", "bunny": "Coney", "cat": "Cat"}.get(kind, str(an.get("name", kind)))
		if kind == "bird":
			label = "Doves x%d" % birds(rid)
		elif kind == "pig" and not pig_grown(rid):
			label = "Piglet"
		elif kind == "pig":
			label = "Pig"
		var ready = ready_good(rid, kind)
		UI.text(ci, Vector2(x + 4, y), label, UI.C_GREEN if ready > 0 else UI.C_TEXT)
		var f = aff(rid, kind)
		for i in range(5):
			var tex = _t("icons/heart_0%d_16x16.png" % (1 if f >= (i + 1) * 2 else (2 if f >= i * 2 + 1 else 3)))
			if tex != null:
				ci.draw_texture_rect(tex, Rect2(Vector2(r.end.x - 50 + i * 9, y + 1), Vector2(8, 8)), false)
		y += 11
	var ne = eggs(rid)
	if owns(rid, "bird"):
		UI.text(ci, Vector2(x + 4, y), "Nest: %d egg%s" % [ne, "" if ne == 1 else "s"], UI.C_GREEN if ne > 0 else UI.C_DIM)
		y += 11
	if bool(st.get("gate", false)):
		UI.text(ci, Vector2(x + 4, y), "The pen gate is open.", UI.C_RED if bool(inf.get("foxes", false)) else UI.C_DIM)
		y += 11
	y += 2
	var ks = "Kart: waiting"
	var kc = UI.C_DIM
	if kart_back(rid):
		ks = "Kart back: %d cr" % int(st["kart"].get("pay", 0))
		kc = UI.C_HI
	elif kart_away(rid):
		ks = "Kart: away till morning"
	elif not st["kart"]["load"].is_empty():
		ks = "Kart: loaded (%d cr)" % kart_value(rid)
		kc = UI.C_TEXT
	UI.text(ci, Vector2(x, y), ks, kc)
	y += 13
	var lg: Array = st.get("log", [])
	if not lg.is_empty() and y < r.end.y - 22:
		for ln in UI.wrap(str(lg[-1]), r.size.x - 14):
			if y > r.end.y - 11:
				break
			UI.text(ci, Vector2(x, y), ln, UI.C_DIM)
			y += 11
