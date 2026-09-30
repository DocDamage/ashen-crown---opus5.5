extends Node
## CampaignState + PartyService + InventoryService + SaveService.
## All progression lives in the save-owned dictionary `S`; scenes and UI only read/commit through here.

signal state_changed
signal notify(text: String)

const SCHEMA := 1
const SAVE_DIR := "user://saves"
const SLOTS := 12        # manual slots (sys s4: was 3; slot1..3 files load unchanged)
const STACK_CAP := 99
const GOLD_CAP := 9999999
## Hero ids come from content (C01-C08 originally; the overhaul cast adds C09-C17).
var CHAR_IDS: Array = []
const PARTY_MAX := 5
## Difficulty (per save): enemy HP and damage multipliers.
const DIFFICULTY := {"easy": {"hp": 0.75, "dmg": 0.8}, "normal": {"hp": 1.0, "dmg": 1.0}, "hard": {"hp": 1.35, "dmg": 1.2}}

var S: Dictionary = {}
var playing = false
var session_start_ms = 0
var checkpoint: Dictionary = {}
var fixture_label = ""   # non-empty when state was built by a labelled test fixture

func _ready() -> void:
	var ids: Array = Content.data.get("characters", {}).keys()
	ids.sort()
	CHAR_IDS = ids
	state_changed.connect(func(): _meta_dirty = true)

func _process(delta: float) -> void:
	if playing and not S.is_empty() and not get_tree().paused:
		S["playtime"] = float(S.get("playtime", 0.0)) + delta
	# achievements: the generic evaluator runs at most twice a second after any state change
	_meta_t -= delta
	if _meta_dirty and _meta_t <= 0.0 and playing and not S.is_empty() and not fixture_label.begins_with("unit"):
		_meta_dirty = false
		_meta_t = 0.5
		Achievements.evaluate()

# ======================================================================
# New game
# ======================================================================
func new_game() -> void:
	S = {
		"schema_version": SCHEMA, "content_version": Content.hash, "run_id": "%x" % (Time.get_unix_time_from_system() * 1000),
		"save_id": "", "timestamp": "", "playtime": 0.0, "world_phase": "pre", "chapters": [], "flags": {},
		"vars": {}, "events": [], "quests": {}, "party": {"roster": [], "available": {}, "active": [], "rows": {}, "members": {}, "locked": false},
		"inventory": {"gold": 300, "items": {}, "delivery": []}, "acquired": [], "chests": [], "discovered": [],
		"bestiary": {}, "upgrades": {}, "vehicle": {"mode": "foot", "ship_map": "", "ship_x": 0, "ship_y": 0, "ferry": false, "cable": false, "ship": false, "mount": false},
		"location": {"map": "T01_PLATFORM", "spawn": "start", "x": -1, "y": -1, "dir": "down"},
		"rng": {"combat": 12345, "loot": 777, "enc": 4242}, "play_settings": {"encounters": Settings.get_v("encounters")},
		"journal": {"objective": "", "clue": "", "destination": "", "source": "", "rumors": [], "log": []},
		"links": {}, "salvage": [], "clear": false, "epilogue": {}, "last_town": "L_T01",
		"difficulty": str(Settings.get_v("difficulty_default")), "names": {},
		"blue": [], "captured": {},
		"clock": 480.0, "day": 0, "waystones": [], "arena": {"rank": 0, "solo": [], "gauntlet": false, "bets": 0, "beasts": 0},
		# sys s4: meta progress (counters for achievements, fish log, New Game+ cycle)
		"stats": {}, "fish": {"log": {}, "tourney_best": 0.0}, "achievements": [], "ng": 0,
	}
	S.merge({"glearn": {}, "gknown": {}, "nodes": {}, "steps": 0, "battles": 0, "bestiary_claimed": []})   # systems s2
	S["vehicle"]["mount_kind"] = "bramble"
	for cid in CHAR_IDS:
		S["party"]["members"][cid] = {"level": 1, "xp": 0, "hp": -1, "mp": -1, "equip": {}, "recruited": false, "starter_given": false}
	add_item("I001", 6)
	add_item("I004", 2)
	add_item("I006", 2)
	add_item("I015", 1)
	add_item("I016", 1)
	add_item("I017", 1)
	# Dain is a veteran officer: he starts at level 3 (authored decision, reports/decisions.md)
	S["party"]["members"]["C01"]["level"] = 3
	S["party"]["members"]["C01"]["xp"] = F.xp_total_for_level(3)
	recruit("C01")
	playing = true
	emit_signal("state_changed")

func difficulty() -> String:
	return str(S.get("difficulty", "normal")) if not S.is_empty() else "normal"

func diff_mult(k: String) -> float:
	return float(DIFFICULTY.get(difficulty(), DIFFICULTY["normal"])[k])

## Player-chosen names (renaming when a hero joins, and at the Namer). Empty = the hero's own name.
func char_name(cid: String) -> String:
	var n = str(S.get("names", {}).get(cid, "")) if not S.is_empty() else ""
	return n if n != "" else str(Content.ch(cid).get("name", cid))

func short_name(cid: String) -> String:
	var n = str(S.get("names", {}).get(cid, "")) if not S.is_empty() else ""
	return n if n != "" else str(Content.ch(cid).get("short", cid))

func rename_hero(cid: String, n: String) -> void:
	if not S.has("names"):
		S["names"] = {}
	n = n.strip_edges()
	if n == "" or n == str(Content.ch(cid).get("short", "")):
		S["names"].erase(cid)
	else:
		S["names"][cid] = n
	emit_signal("state_changed")

## Replaces each renamed hero's default short name in a line of script text (whole words only).
func sub_names(text: String) -> String:
	if S.is_empty() or S.get("names", {}).is_empty():
		return text
	for cid in S["names"]:
		var old = str(Content.ch(cid).get("short", ""))
		if old == "":
			continue
		var re = RegEx.new()
		re.compile("\\b" + old + "\\b")
		text = re.sub(text, str(S["names"][cid]), true)
	return text

# ======================================================================
# Flags / conditions
# ======================================================================
func flag(k: String) -> bool:
	return bool(S.get("flags", {}).get(k, false))

func set_flag(k: String, val: bool = true) -> void:
	if val:
		S["flags"][k] = true
	else:
		S["flags"].erase(k)

func var_get(k: String) -> int:
	return int(S["vars"].get(k, 0))

func var_set(k: String, val: int) -> void:
	S["vars"][k] = val

func chapter_done(cid: String) -> bool:
	return S.get("chapters", []).has(cid)

func complete_chapter(cid: String) -> void:
	if not S["chapters"].has(cid):
		S["chapters"].append(cid)

func event_applied(eid: String) -> bool:
	return S.get("events", []).has(eid)

func apply_event(eid: String) -> void:
	if not S["events"].has(eid):
		S["events"].append(eid)

func eval_cond(conds: Array) -> bool:
	for c in conds:
		if not _eval_one(str(c)):
			return false
	return true

func _eval_one(c: String) -> bool:
	var neg = c.begins_with("!")
	if neg:
		c = c.substr(1)
	var r = false
	var p = c.split(":")
	match p[0]:
		"flag": r = flag(p[1])
		"ch": r = chapter_done(p[1])
		"phase": r = S["world_phase"] == p[1]
		"event": r = event_applied(p[1])
		"item": r = count(p[1]) > 0
		"party": r = is_available(p[1])
		"recruited": r = is_recruited(p[1])
		"q":
			var st = quest_state(p[1])
			if p.size() > 2:
				r = st == p[2]
			else:
				r = st == "COMPLETED"
		"qs":
			r = quest_stage(p[1]) == p[2]
		"var":
			var ops = [">=", "<=", "==", ">", "<"]
			var expr: String = p[1]
			for o in ops:
				if expr.find(o) > 0:
					var k = expr.split(o)[0]
					var n = int(expr.split(o)[1])
					var cur = var_get(k)
					match o:
						">=": r = cur >= n
						"<=": r = cur <= n
						"==": r = cur == n
						">": r = cur > n
						"<": r = cur < n
					break
		"vehicle": r = bool(S["vehicle"].get(p[1], false))
		# world clock (field systems s3): night = 20:00-05:00; hour:a-b wraps past midnight (hour:22-4)
		"night": r = FieldSys.night()
		"day": r = not FieldSys.night()
		"hour": r = FieldSys.in_hours(p[1]) if p.size() > 1 else false
		"clear": r = bool(S.get("clear", false))
		# ---- sys s4: mature mode, New Game+, meta counters
		"mature": r = bool(Settings.get_v("mature")) and bool(Settings.get_v("mature_ok"))
		"ng": r = int(S.get("ng", 0)) >= (int(p[1]) if p.size() > 1 else 1)
		"defeated": r = int(S.get("bestiary", {}).get(p[1], {}).get("defeated", 0)) > 0
		"achv": r = has_achievement(p[1])
		"stat", "meta":
			r = Achievements.eval_meta(c)
		_: push_error("Unknown condition " + c)
	return r != neg

# ======================================================================
# Party
# ======================================================================
func member(cid: String) -> Dictionary:
	return S["party"]["members"][cid]

func is_recruited(cid: String) -> bool:
	return S["party"]["roster"].has(cid)

func is_available(cid: String) -> bool:
	return is_recruited(cid) and bool(S["party"]["available"].get(cid, false))

func available_members() -> Array:
	return S["party"]["roster"].filter(func(c): return is_available(c))

func active() -> Array:
	return S["party"]["active"].filter(func(c): return is_available(c))

func stats(cid: String) -> Dictionary:
	return stats_for(cid, member(cid))

## Derived stats for a member dict (the real one, or a preview copy with other equipment).
func stats_for(cid: String, mem: Dictionary) -> Dictionary:
	var st = F.member_stats(mem, Content.ch(cid), Content.data["items"], S.get("upgrades", {}), float(Content.data.get("gear", {}).get("step", 0.08)))
	st = apply_set_bonus(st, mem)
	var rs = float(st["passives"].get("reserve_scale", 0.0))
	if rs > 0.0:
		# Salvage line: stronger for every recruited, available member waiting in reserve
		var reserve = 0
		for c in S["party"]["roster"]:
			if c != cid and is_available(c) and not S["party"]["active"].has(c):
				reserve += 1
		var k = 1.0 + rs * reserve
		st["atk"] = int(floor(st["atk"] * k))
		st["def"] = int(floor(st["def"] * k))
	return st

## Smith upgrades: level of an item (applies to every copy you own).
func upgrade_level(iid: String) -> int:
	return int(S.get("upgrades", {}).get(iid, 0))

func upgrade_cost(iid: String) -> Dictionary:
	var lv = upgrade_level(iid) + 1
	var g: Dictionary = Content.data.get("gear", {})
	if not g.get("upgrade", {}).has(str(lv)):
		return {}
	var u: Array = g["upgrade"][str(lv)]
	return {"level": lv, "ore": u[0], "n": int(u[1]), "gold": maxi(80, int(round(float(Content.item(iid).get("price", 0)) * float(u[2]) / 10.0)) * 10)}

func upgrade(iid: String) -> Dictionary:
	var c = upgrade_cost(iid)
	if c.is_empty():
		return {"ok": false, "reason": "Fully upgraded"}
	if count(c["ore"]) < c["n"]:
		return {"ok": false, "reason": "Needs %d %s" % [c["n"], Content.item(c["ore"])["name"]]}
	if gold() < c["gold"]:
		return {"ok": false, "reason": "Not enough crowns"}
	spend_gold(c["gold"])
	remove_item(c["ore"], c["n"])
	if not S.has("upgrades"):
		S["upgrades"] = {}
	S["upgrades"][iid] = c["level"]
	return {"ok": true, "level": c["level"]}

func recruit(cid: String) -> Array:
	## Initial recruit or reunion. Returns messages. Idempotent for equipment and growth.
	var msgs = []
	var m = member(cid)
	var levels = []
	for c in available_members():
		if c != cid:
			levels.append(int(member(c)["level"]))
	var new_level = F.join_level(int(m["level"]), levels)
	if new_level > int(m["level"]):
		m["level"] = new_level
		m["xp"] = maxi(int(m["xp"]), F.xp_total_for_level(new_level))
	if not bool(m.get("starter_given", false)):
		m["starter_given"] = true
		var st: Dictionary = Content.ch(cid)["starter"]
		for slot in st:
			m["equip"][slot] = st[slot]
			_record_acq("starter_" + cid + "_" + slot)
	if not S["party"]["roster"].has(cid):
		S["party"]["roster"].append(cid)
		S["party"]["rows"][cid] = "back" if cid in ["C02", "C06", "C05"] else "front"
	S["party"]["available"][cid] = true
	var s = stats(cid)
	m["hp"] = s["mhp"]
	m["mp"] = s["mmp"]
	if S["party"]["active"].size() < PARTY_MAX and not S["party"]["active"].has(cid):
		S["party"]["active"].append(cid)
	msgs.append("%s joins the party." % char_name(cid))
	emit_signal("state_changed")
	return msgs

func set_available(cid: String, val: bool) -> void:
	S["party"]["available"][cid] = val
	if not val:
		S["party"]["active"].erase(cid)
		# free any vestige link held by an unavailable member (reassign at next safe screen)
	else:
		if S["party"]["active"].size() < PARTY_MAX and not S["party"]["active"].has(cid):
			S["party"]["active"].append(cid)

func set_active(order: Array) -> void:
	S["party"]["active"] = order.filter(func(c): return is_available(c)).slice(0, PARTY_MAX)

func row(cid: String) -> String:
	return S["party"]["rows"].get(cid, "front")

func learned_abilities(cid: String) -> Array:
	var out = []
	var m = member(cid)
	for l in Content.ch(cid)["learn"]:
		if int(m["level"]) >= int(l["level"]):
			out.append(l["id"])
	var ult = Content.ch(cid).get("ultimate")
	if ult != null and quest_state(Content.ch(cid)["quest"]) == "COMPLETED":
		out.append(ult)
	for aid in S.get("vknown", {}).get(cid, []):
		if not out.has(aid):
			out.append(aid)
	for aid in S.get("gknown", {}).get(cid, []):
		if not out.has(aid):
			out.append(aid)
	return out

func battle_party() -> Array:
	var out = []
	for cid in active():
		var m = member(cid)
		var s = stats(cid)
		var hp = int(m["hp"]) if int(m["hp"]) >= 0 else int(s["mhp"])
		out.append({"cid": cid, "name": short_name(cid), "stats": s, "hp": mini(hp, s["mhp"]),
			"mp": mini(int(m["mp"]) if int(m["mp"]) >= 0 else int(s["mmp"]), s["mmp"]),
			"row": row(cid), "abilities": learned_abilities(cid), "link": link_of(cid),
			"limits": limit_known(cid), "limit": float(m.get("limit_gauge", 0.0)), "blue": blue_for(cid), "blue_rule": blue_rule(cid)})
	return out

func heal_all(include_ko: bool = true) -> void:
	for cid in S["party"]["roster"]:
		var m = member(cid)
		if int(m["hp"]) <= 0 and not include_ko:
			continue
		var s = stats(cid)
		m["hp"] = s["mhp"]
		m["mp"] = s["mmp"]

## Catch-up growth: members below the story's recommended band (last level floor + 4) earn extra battle XP,
## up to x4. Transparent, deterministic, never removes XP; it only shortens the gap for direct-route play.
func catch_up_mult(level: int) -> float:
	var target = var_get("story_floor") + 4
	if var_get("story_floor") <= 0 or level >= target:
		return 1.0
	return minf(4.0, 1.0 + 0.35 * float(target - level))

func award_xp(amount: int) -> Array:
	## 100% XP to every recruited member, active, reserve or unavailable (docs/07).
	var msgs = []
	for cid in S["party"]["roster"]:
		var m = member(cid)
		var before = int(m["level"])
		var old_learn = learned_abilities(cid)
		m["xp"] = int(m["xp"]) + int(round(amount * catch_up_mult(before)))
		var nl = F.level_for_xp(int(m["xp"]), level_cap())
		if nl > before:
			var s0 = stats(cid)
			var vl = link_of(cid)
			if vl != "" and Content.data["vestiges"].has(vl):
				var vb: Dictionary = m.get("vbonus", {})
				var bon: Dictionary = Content.data["vestiges"][vl].get("bonus", {})
				for k in bon:
					vb[k] = int(vb.get(k, 0)) + int(bon[k]) * (nl - before)
				m["vbonus"] = vb
			m["level"] = nl
			var s1 = stats(cid)
			if int(m["hp"]) > 0:
				m["hp"] = int(m["hp"]) + (s1["mhp"] - s0["mhp"])
			m["mp"] = int(m["mp"]) + (s1["mmp"] - s0["mmp"])
			if is_available(cid):
				msgs.append("%s reached level %d." % [short_name(cid), nl])
				for a in learned_abilities(cid):
					if not old_learn.has(a):
						msgs.append("%s learned %s." % [short_name(cid), Content.ability(a)["name"]])
	return msgs

# ======================================================================
# Equipment
# ======================================================================
func can_equip(cid: String, slot: String, iid: String) -> Dictionary:
	var it = Content.item(iid)
	if it.is_empty():
		return {"ok": false, "reason": "Unknown item"}
	var kind: String = it["kind"]
	var want = slot
	if slot.begins_with("acc"):
		want = "accessory"
	if kind == "weapon" and want != "weapon":
		return {"ok": false, "reason": "Wrong slot"}
	if kind == "armor" and it["slot"] != want:
		return {"ok": false, "reason": "Wrong slot"}
	if kind == "accessory" and want != "accessory":
		return {"ok": false, "reason": "Wrong slot"}
	if not it.get("allowed", []).has(cid):
		return {"ok": false, "reason": "%s cannot use this" % short_name(cid)}
	if want == "offhand":
		var w = member(cid)["equip"].get("weapon", "")
		if w != "" and Content.item(w).get("two_handed", false):
			return {"ok": false, "reason": "Two-handed weapon equipped"}
	return {"ok": true}

## "Optimize": equip the strongest owned weapon/armor per slot (accessories are left to the player).
func optimize_equipment(cid: String) -> int:
	var changed = 0
	for slot in ["weapon", "offhand", "head", "body"]:
		var cur: String = member(cid)["equip"].get(slot, "")
		var best = cur
		var best_score = _gear_score(cur)
		for iid in S["inventory"]["items"]:
			if count(iid) <= 0 or not can_equip(cid, slot, iid)["ok"]:
				continue
			var sc = _gear_score(iid)
			if sc > best_score:
				best_score = sc
				best = iid
		if best != cur and best != "":
			if equip(cid, slot, best)["ok"]:
				changed += 1
	return changed

func _gear_score(iid: String) -> float:
	if iid == "":
		return -1.0
	var it = Content.item(iid)
	return float(it.get("atk", 0)) + float(it.get("mag", 0)) + float(it.get("def", 0)) + float(it.get("res", 0)) + float(it.get("tier", 0)) * 0.1

func equip(cid: String, slot: String, iid: String) -> Dictionary:
	## Moves one item from inventory to the slot; old item returns to inventory. Never duplicates.
	if iid != "":
		var chk = can_equip(cid, slot, iid)
		if not chk["ok"]:
			return chk
		if count(iid) <= 0:
			return {"ok": false, "reason": "Not in inventory"}
	var m = member(cid)
	var hp_pct = 1.0
	var s0 = stats(cid)
	if s0["mhp"] > 0 and int(m["hp"]) >= 0:
		hp_pct = float(m["hp"]) / float(s0["mhp"])
	var old = m["equip"].get(slot, "")
	if iid != "":
		remove_item(iid, 1)
	if old != null and old != "":
		add_item(old, 1, true)
	if iid == "":
		m["equip"].erase(slot)
	else:
		m["equip"][slot] = iid
	# two-handed weapon empties the offhand
	if slot == "weapon" and iid != "" and Content.item(iid).get("two_handed", false):
		var oh = m["equip"].get("offhand", "")
		if oh != "":
			m["equip"].erase("offhand")
			add_item(oh, 1, true)
	var s1 = stats(cid)
	if int(m["hp"]) > 0:
		m["hp"] = clampi(int(round(hp_pct * s1["mhp"])), 1, s1["mhp"])
	m["mp"] = mini(int(m["mp"]), s1["mmp"])
	emit_signal("state_changed")
	return {"ok": true}

func link_of(cid: String) -> String:
	for vid in S["links"]:
		if S["links"][vid] == cid:
			return vid
	return ""

func link_vestige(vid: String, cid: String) -> Dictionary:
	if not has_vestige(vid):
		return {"ok": false, "reason": "Not obtained"}
	if cid != "" and not is_available(cid):
		return {"ok": false, "reason": "Unavailable"}
	# a character holds one vestige; a vestige one character
	for v in S["links"].keys():
		if S["links"][v] == cid:
			S["links"].erase(v)
	if cid == "":
		S["links"].erase(vid)
	else:
		S["links"][vid] = cid
	return {"ok": true}

func has_vestige(vid: String) -> bool:
	return S.get("vestiges", []).has(vid)

func grant_vestige(vid: String) -> void:
	if not S.has("vestiges"):
		S["vestiges"] = []
	if not S["vestiges"].has(vid):
		S["vestiges"].append(vid)

# ======================================================================
# Inventory
# ======================================================================
func count(iid: String) -> int:
	return int(S["inventory"]["items"].get(iid, 0))

func equipped_count(iid: String) -> int:
	var n = 0
	for cid in S["party"]["members"]:
		for slot in member(cid)["equip"]:
			if member(cid)["equip"][slot] == iid:
				n += 1
	return n

func add_item(iid: String, n: int = 1, from_equip: bool = false) -> Dictionary:
	## Returns {added, delivered, converted_gold}
	var it = Content.item(iid)
	var cur = count(iid)
	var room = STACK_CAP - cur
	var added = mini(n, room)
	var over = n - added
	if added > 0:
		S["inventory"]["items"][iid] = cur + added
	var res = {"added": added, "delivered": 0, "converted_gold": 0}
	if over > 0:
		if it.get("kind", "") == "consumable" and not from_equip:
			var g = int(over * int(it.get("price", 0)) / 2)
			add_gold(g)
			res["converted_gold"] = g
			emit_signal("notify", "No room for %d %s; converted to %d crowns." % [over, it.get("name", iid), g])
		else:
			for i in range(over):
				S["inventory"]["delivery"].append(iid)
			res["delivered"] = over
			emit_signal("notify", "%s sent to the delivery chest." % it.get("name", iid))
	return res

func remove_item(iid: String, n: int = 1) -> bool:
	if count(iid) < n:
		return false
	var c = count(iid) - n
	if c <= 0:
		S["inventory"]["items"].erase(iid)
	else:
		S["inventory"]["items"][iid] = c
	return true

func gold() -> int:
	return int(S["inventory"]["gold"])

func add_gold(n: int) -> void:
	S["inventory"]["gold"] = clampi(gold() + n, 0, GOLD_CAP)

func spend_gold(n: int) -> bool:
	if n < 0 or gold() < n:
		return false
	S["inventory"]["gold"] = gold() - n
	return true

func buy(iid: String, qty: int, unit_price: int) -> Dictionary:
	var total = unit_price * qty
	if qty <= 0:
		return {"ok": false, "reason": "Nothing to buy"}
	if count(iid) + qty > STACK_CAP:
		return {"ok": false, "reason": "Not enough room"}
	if gold() < total:
		return {"ok": false, "reason": "Not enough crowns"}
	spend_gold(total)
	add_item(iid, qty)
	return {"ok": true}

func sell(iid: String, qty: int) -> Dictionary:
	var it = Content.item(iid)
	if not it.get("sellable", false) or it.get("kind", "") == "key":
		return {"ok": false, "reason": "Cannot be sold"}
	if count(iid) < qty:
		return {"ok": false, "reason": "Not enough"}
	remove_item(iid, qty)
	add_gold(int(it.get("price", 0)) / 2 * qty)
	return {"ok": true}

func claim_delivery() -> Array:
	var got = []
	var keep = []
	for iid in S["inventory"]["delivery"]:
		if count(iid) < STACK_CAP:
			S["inventory"]["items"][iid] = count(iid) + 1
			got.append(iid)
		else:
			keep.append(iid)
	S["inventory"]["delivery"] = keep
	return got

func _record_acq(acq: String) -> void:
	if not S["acquired"].has(acq):
		S["acquired"].append(acq)

func acquired(acq: String) -> bool:
	return S["acquired"].has(acq)

func acquire_unique(acq: String, iid: String, n: int = 1) -> bool:
	## A unique acquisition transaction: applies exactly once per acquisition ID.
	if acquired(acq):
		return false
	_record_acq(acq)
	add_item(iid, n)
	return true

func open_chest(chest_id: String, iid: String, n: int, gold_amt: int, acq: String) -> Dictionary:
	if S["chests"].has(chest_id):
		return {"ok": false}
	S["chests"].append(chest_id)
	if acq != "":
		_record_acq(acq)
	if gold_amt > 0:
		add_gold(gold_amt)
	if iid != "" and iid != "gold":
		add_item(iid, n)
	return {"ok": true}

# ======================================================================
# Quests & journal
# ======================================================================
func quest_state(qid: String) -> String:
	return S["quests"].get(qid, {}).get("state", "NOT_STARTED")

func quest_stage(qid: String) -> String:
	return S["quests"].get(qid, {}).get("stage", "")

func quest_set(qid: String, state: String, stage: String = "") -> void:
	var q: Dictionary = S["quests"].get(qid, {"state": "NOT_STARTED", "stage": ""})
	var order = ["NOT_STARTED", "ACTIVE", "RESOLUTION_READY", "COMPLETED"]
	if order.find(state) < order.find(q["state"]):
		return   # never regress
	q["state"] = state
	if stage != "":
		q["stage"] = stage
	S["quests"][qid] = q

func set_objective(text: String, source: String = "") -> void:
	S["journal"]["objective"] = text
	if source != "":
		S["journal"]["source"] = source
	S["journal"]["log"].append(text)
	if S["journal"]["log"].size() > 40:
		S["journal"]["log"].pop_front()

func add_rumor(text: String) -> void:
	if not S["journal"]["rumors"].has(text):
		S["journal"]["rumors"].append(text)

func discover(loc: String) -> void:
	if not S["discovered"].has(loc):
		S["discovered"].append(loc)

func bestiary_seen(eid: String, what: String = "seen") -> void:
	var base: String = Content.enemy(eid).get("variant_of", eid)
	var b: Dictionary = S["bestiary"].get(base, {"seen": false, "defeated": 0, "affinity": false, "drops": false, "weak": []})
	match what:
		"seen": b["seen"] = true
		"defeated": b["defeated"] = int(b["defeated"]) + 1
		"affinity": b["affinity"] = true
		"drops": b["drops"] = true
		"scan":
			b["affinity"] = true
			b["drops"] = true
			b["scanned"] = true
		_:
			if what.begins_with("weak:"):
				var e = what.substr(5)
				if not b["weak"].has(e):
					b["weak"].append(e)
	S["bestiary"][base] = b

# ======================================================================
# Battle transaction
# ======================================================================
func make_checkpoint(label: String) -> void:
	checkpoint = {"label": label, "S": S.duplicate(true)}

func restore_checkpoint() -> void:
	if not checkpoint.is_empty():
		S = checkpoint["S"].duplicate(true)
		emit_signal("state_changed")

func apply_battle_victory(model: BattleModel) -> Array:
	## One transaction: XP, gold, drops, steals, consumed items, end HP/MP.
	var msgs = []
	var r = model.rewards()
	# consumed items: working copy becomes authoritative
	for iid in model.inventory:
		var n = int(model.inventory[iid])
		if Content.item(iid).get("kind", "") == "consumable":
			if n <= 0:
				S["inventory"]["items"].erase(iid)
			else:
				S["inventory"]["items"][iid] = n
	for ps in model.party_end_state():
		var m = member(ps["cid"])
		m["hp"] = ps["hp"]
		m["mp"] = ps["mp"]
		S["party"]["rows"][ps["cid"]] = ps["row"]
	for eid in model.enemy_ids:
		var e = model.battlers[eid]
		if not e.tags.has("part"):
			bestiary_seen(e.ref, "defeated")
	_battle_stats(model)
	add_gold(int(r["gold"]))
	msgs.append("Gained %d XP and %d crowns." % [r["xp"], r["gold"]])
	for d in r["drops"]:
		add_item(d, 1)
		msgs.append("Found %s." % Content.item_name(d))
	for st in model.stolen_items:
		add_item(st, 1)
		msgs.append("Kept stolen %s." % Content.item_name(st))
	msgs.append_array(expansion_victory(model))
	msgs.append_array(award_xp(int(r["xp"])))
	msgs.append_array(limit_learning())
	msgs.append_array(vestige_learning(3 if model.is_boss_battle else 1))
	msgs.append_array(gear_learning(3 if model.is_boss_battle else 1))
	S["battles"] = int(S.get("battles", 0)) + 1
	emit_signal("state_changed")
	return msgs

## FF6-style Esper learning: every active, conscious hero with a linked Vestige gains progress (rate x AP) on
## each spell it teaches; at 100 the spell is learned for good.
func vestige_learning(ap: int) -> Array:
	var msgs = []
	if not S.has("vlearn"):
		S["vlearn"] = {}
	if not S.has("vknown"):
		S["vknown"] = {}
	for cid in active():
		var vid = link_of(cid)
		if vid == "" or not Content.data["vestiges"].has(vid):
			continue
		if int(member(cid)["hp"]) == 0:
			continue
		var prog: Dictionary = S["vlearn"].get(cid, {})
		var known: Array = S["vknown"].get(cid, [])
		for t in Content.data["vestiges"][vid].get("teach", []):
			var aid: String = t[0]
			if known.has(aid) or learned_abilities(cid).has(aid):
				continue
			var p = int(prog.get(aid, 0)) + int(t[1]) * ap
			if p >= 100:
				known.append(aid)
				prog.erase(aid)
				msgs.append("%s learned %s." % [short_name(cid), Content.ability(aid)["name"]])
			else:
				prog[aid] = p
		S["vlearn"][cid] = prog
		S["vknown"][cid] = known
	return msgs

## Learning progress (0-100, or 100 when known) of spell `aid` for hero `cid`.
func vestige_progress(cid: String, aid: String) -> int:
	if S.get("vknown", {}).get(cid, []).has(aid) or learned_abilities(cid).has(aid):
		return 100
	return int(S.get("vlearn", {}).get(cid, {}).get(aid, 0))

func apply_battle_flee(model: BattleModel) -> void:
	expansion_flee(model)
	for st in model.stolen_items:
		add_item(st, 1)
	for iid in model.inventory:
		var n = int(model.inventory[iid])
		if Content.item(iid).get("kind", "") == "consumable":
			if n <= 0:
				S["inventory"]["items"].erase(iid)
			else:
				S["inventory"]["items"][iid] = n
	for ps in model.party_end_state():
		var m = member(ps["cid"])
		m["hp"] = ps["hp"]
		m["mp"] = ps["mp"]

func battle_inventory() -> Dictionary:
	var inv = {}
	for iid in S["inventory"]["items"]:
		if Content.item(iid).get("kind", "") == "consumable":
			inv[iid] = S["inventory"]["items"][iid]
	return inv

func next_seed(stream: String) -> int:
	var r = Rng.new(int(S["rng"].get(stream, 1)))
	var v = r.next_u32()
	S["rng"][stream] = v
	return v

# ======================================================================
# World phase: catastrophe transaction (docs/04)
# ======================================================================
func catastrophe_transaction() -> void:
	if S["world_phase"] == "post":
		return
	write_backup("pre_catastrophe")
	var n = S.duplicate(true)
	n["world_phase"] = "post"
	if not n["chapters"].has("CH12"):
		n["chapters"].append("CH12")
	n["location"] = {"map": "T07_HEARTH", "spawn": "wake", "x": -1, "y": -1, "dir": "down"}
	for cid in n["party"]["roster"]:
		n["party"]["available"][cid] = cid in ["C01", "C06"]
	n["party"]["active"] = ["C01", "C06"]
	n["vehicle"]["mode"] = "foot"
	n["vehicle"]["ferry"] = false
	n["vehicle"]["cable"] = false
	# the pre-fault Wayfarer is lost with the Crown Dais; the Lanternwake is a new ship (CH16)
	n["vehicle"]["ship"] = false
	n["vehicle"]["ship_map"] = ""
	if not n["events"].has("EV_CATASTROPHE"):
		n["events"].append("EV_CATASTROPHE")
	# salvage: unique pre-state rewards the player never collected
	n["salvage"] = compute_salvage(n)
	S = n
	emit_signal("state_changed")

const SEALED_UNIQUES := [
	["D01_SECRET", "A001"], ["D02_SECRET", "A002"], ["D03_SECRET", "A003"], ["D04_SECRET", "A004"],
	["D05_SECRET", "A005"], ["D06_SECRET", "A006"], ["D07_SECRET", "A007"], ["D08_SECRET", "A008"], ["D09_SECRET", "A009"],
]

func compute_salvage(state: Dictionary) -> Array:
	var out = []
	for pair in SEALED_UNIQUES:
		if not state["acquired"].has(pair[0]):
			out.append(pair)
	return out

func claim_salvage() -> Array:
	var got = []
	for pair in S.get("salvage", []):
		if acquire_unique(pair[0], pair[1]):
			got.append(pair[1])
	S["salvage"] = []
	return got

# ======================================================================
# Save service: versioned payload, checksum, atomic replace, backups
# ======================================================================
## sys s4: the save folder can be redirected (tests, the dev gallery) so they never touch the player's saves.
var save_root := SAVE_DIR

func slot_path(slot: int) -> String:
	return "%s/slot%d.json" % [save_root, slot]

func _ensure_dir() -> void:
	DirAccess.make_dir_recursive_absolute(save_root)

func _payload() -> Dictionary:
	S["timestamp"] = Time.get_datetime_string_from_system()
	S["content_version"] = Content.hash
	var body = JSON.stringify(S, "", true)
	return {"schema_version": SCHEMA, "checksum": body.sha256_text(), "body": body}

func save_to(path: String, fault_stage: String = "") -> Dictionary:
	## Write temp -> verify -> keep last-known-good backup -> atomic rename.
	_ensure_dir()
	var p = _payload()
	var text = JSON.stringify(p)
	var tmp = path + ".tmp"
	var f = FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		return {"ok": false, "reason": "Cannot write save"}
	if fault_stage == "partial_tmp":
		f.store_string(text.substr(0, text.length() / 2))
		f.close()
		return {"ok": false, "reason": "Injected interruption"}
	f.store_string(text)
	f.flush()
	f.close()
	var verify = _read_payload(tmp)
	if not verify["ok"]:
		return {"ok": false, "reason": "Verification failed"}
	if fault_stage == "before_rename":
		return {"ok": false, "reason": "Injected interruption"}
	if FileAccess.file_exists(path):
		var bak = path + ".bak"
		if FileAccess.file_exists(bak):
			DirAccess.remove_absolute(bak)
		DirAccess.rename_absolute(path, bak)
	var err = DirAccess.rename_absolute(tmp, path)
	if err != OK:
		return {"ok": false, "reason": "Rename failed %d" % err}
	return {"ok": true}

func save_slot(slot: int) -> Dictionary:
	S["save_id"] = "slot%d" % slot
	if fixture_label == "":
		stat_add("saves")
	return save_to(slot_path(slot))

func write_backup(tag: String) -> Dictionary:
	return save_to(backup_path(tag))

func backup_path(tag: String) -> String:
	return "%s/backup_%s.json" % [save_root, tag]

## Protected backups: written by the story at fixed points, never by the slot menu. Load-only.
const PROTECTED := [["pre_dais", "Protected: Before the Crown Dais"], ["pre_finale", "Protected: Before the Final Descent"]]

func info_of(path: String) -> Dictionary:
	return path_info(path)

func world_for_phase(map_id: String) -> String:
	## Pre-state dungeons revisited after the catastrophe exit to the altered overworld (shared location IDs).
	if S.get("world_phase", "pre") == "post" and (map_id == "WORLD" or map_id == "DEEP"):
		return map_id + "_POST"
	return map_id

func autosave_current() -> Dictionary:
	## Commit the in-memory state to the slot this run was last saved to/loaded from (if any).
	var sid: String = str(S.get("save_id", ""))
	if sid.begins_with("slot"):
		return save_slot(int(sid.substr(4)))
	return {"ok": false, "reason": "no slot"}

func _read_payload(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {"ok": false, "reason": "missing"}
	var f = FileAccess.open(path, FileAccess.READ)
	var d = JSON.parse_string(f.get_as_text())
	if typeof(d) != TYPE_DICTIONARY or not d.has("body"):
		return {"ok": false, "reason": "corrupt"}
	if int(d.get("schema_version", 0)) > SCHEMA:
		return {"ok": false, "reason": "future", "version": d.get("schema_version")}
	if str(d["body"]).sha256_text() != d.get("checksum", ""):
		return {"ok": false, "reason": "corrupt"}
	var body = JSON.parse_string(d["body"])
	if typeof(body) != TYPE_DICTIONARY:
		return {"ok": false, "reason": "corrupt"}
	return {"ok": true, "state": body}

func load_from(path: String) -> Dictionary:
	var r = _read_payload(path)
	if not r["ok"]:
		if r["reason"] == "corrupt":
			# preserve corrupt file for diagnosis; offer backup
			var keep = path + ".corrupt"
			if FileAccess.file_exists(path):
				DirAccess.copy_absolute(path, keep)
			var bak = _read_payload(path + ".bak")
			r["backup_ok"] = bak["ok"]
		return r
	S = _sanitize(r["state"])
	playing = true
	emit_signal("state_changed")
	return {"ok": true}

func load_backup_of(path: String) -> Dictionary:
	return load_from(path + ".bak")

func _sanitize(st: Dictionary) -> Dictionary:
	# JSON turns ints into floats; normalise the few places that matter
	for cid in st["party"]["members"]:
		var m: Dictionary = st["party"]["members"][cid]
		for k in ["level", "xp", "hp", "mp"]:
			m[k] = int(m[k])
	for k in st["inventory"]["items"].keys():
		st["inventory"]["items"][k] = int(st["inventory"]["items"][k])
	st["inventory"]["gold"] = int(st["inventory"]["gold"])
	if not st.has("upgrades"):
		st["upgrades"] = {}
	# overhaul fields (older saves): difficulty, names, members for the heroes added in the overhaul
	if not st.has("difficulty"):
		st["difficulty"] = "normal"
	if not st.has("names"):
		st["names"] = {}
	# sys s4 fields (older saves): meta counters, fish log, achievements mirror, New Game+ cycle
	for k in ["stats", "fish"]:
		if typeof(st.get(k)) != TYPE_DICTIONARY:
			st[k] = {}
	if not st["fish"].has("log"):
		st["fish"]["log"] = {}
	if typeof(st.get("achievements")) != TYPE_ARRAY:
		st["achievements"] = []
	st["ng"] = int(st.get("ng", 0))
	for cid in CHAR_IDS:
		if not st["party"]["members"].has(cid):
			st["party"]["members"][cid] = {"level": 1, "xp": 0, "hp": -1, "mp": -1, "equip": {}, "recruited": false, "starter_given": false}
	for k in st["upgrades"].keys():
		st["upgrades"][k] = int(st["upgrades"][k])
	for k in st["rng"]:
		st["rng"][k] = int(st["rng"][k])
	return st

func slot_info(slot: int) -> Dictionary:
	return path_info(slot_path(slot))

func _current_chapter_name(s: Dictionary) -> String:
	var ids: Array = Content.data["chapters"].keys()
	ids.sort()
	for cid in ids:
		if not s["chapters"].has(cid) and Content.data["chapters"][cid]["status"] == "required":
			return "%s %s" % [cid.replace("CH", "Ch."), Content.data["chapters"][cid]["name"]]
	return "Complete"

func current_chapter() -> String:
	return _current_chapter_name(S)

# ======================================================================
# Expansion battle systems (branch s1): level breaks, limit breaks, reserves, blue magic, capture, superbosses
# ======================================================================
## Current level cap: 99, raised by the level-break flags (set by superboss victories).
func level_cap() -> int:
	var caps: Dictionary = Content.data.get("level_breaks", {}).get("caps", {})
	for k in ["levelbreak_3", "levelbreak_2", "levelbreak_1"]:
		if flag(k):
			return int(caps.get(k, F.LEVEL_CAP))
	return int(caps.get("default", F.LEVEL_CAP))

## Flag set when superboss `id` (SB01..SB12) falls.
func sb_flag(id: String) -> String:
	return "sb_%s_down" % id.to_lower()

func superboss_down(id: String) -> bool:
	return flag(sb_flag(id))

## Re-derives the level-break flags from the superboss flags (first wyrm: 120, all four: 150, the Unmade Crown: 200).
func update_level_breaks() -> Array:
	var msgs = []
	var lb: Dictionary = Content.data.get("level_breaks", {})
	var n = 0
	for w in lb.get("wyrms", []):
		if superboss_down(w):
			n += 1
	var want = []
	if n >= 1:
		want.append("levelbreak_1")
	if n >= 4 and lb.get("wyrms", []).size() > 0:
		want.append("levelbreak_2")
	if superboss_down(str(lb.get("finale", "SB12"))):
		want.append("levelbreak_3")
	for k in want:
		if not flag(k):
			var before = level_cap()
			set_flag(k)
			if level_cap() > before:
				msgs.append("The level limit rises to %d." % level_cap())
	return msgs

## Superboss rewards: flag, Vestige (VESTIGE_OF), level breaks. Called from the victory transaction.
func superboss_victory(bid: String) -> Array:
	var msgs = []
	if not bid.begins_with("SB") or not Content.enemy(bid).get("tags", []).has("superboss"):
		return msgs
	set_flag(sb_flag(bid))
	for vid in Content.data["vestiges"]:
		if str(Content.data["vestiges"][vid].get("source", "")) == bid and not has_vestige(vid):
			grant_vestige(vid)
			msgs.append("The Vestige %s answers. (Link it from the menu.)" % Content.data["vestiges"][vid]["name"])
	msgs.append_array(update_level_breaks())
	return msgs

func expansion_victory(model: BattleModel) -> Array:
	var msgs = []
	_expansion_end_state(model)
	for cid in model.captured:
		msgs.append("%s is kept for the Arena." % Content.enemy(cid).get("name", cid))
	for iid in model.morph_items:
		add_item(iid, 1)
		msgs.append("Morphed: %s." % Content.item_name(iid))
	var ends = {}
	for ps in model.party_end_state():
		ends[ps["cid"]] = ps
	for bid in model.blue_new:
		var who: String = model.blue_new[bid]
		if int(ends.get(who, {}).get("hp", 0)) <= 0 or S.get("blue", []).has(bid):
			continue
		if not S.has("blue"):
			S["blue"] = []
		S["blue"].append(bid)
		msgs.append("%s learned the lore %s." % [short_name(who), Content.ability(bid).get("name", bid)])
	var seen = {}
	for eid in model.enemy_ids:
		var ref: String = model.battlers[eid].ref
		if not seen.has(ref):
			seen[ref] = true
			msgs.append_array(superboss_victory(ref))
	return msgs

func expansion_flee(model: BattleModel) -> void:
	_expansion_end_state(model)
	for iid in model.morph_items:
		add_item(iid, 1)

## Limit gauges and limit uses back to the save; captured enemies into S.captured.
func _expansion_end_state(model: BattleModel) -> void:
	for ps in model.party_end_state():
		var m = member(ps["cid"])
		m["limit_gauge"] = float(ps.get("limit", 0.0))
		var uses: Dictionary = m.get("limit_uses", {})
		for aid in ps.get("limit_used", []):
			uses[aid] = int(uses.get(aid, 0)) + 1
		m["limit_uses"] = uses
	if not S.has("captured"):
		S["captured"] = {}
	for cid in model.captured:
		S["captured"][cid] = int(S["captured"].get(cid, 0)) + 1

## Limits a hero knows: tier 1 always; tier k+1 after `uses[k]` uses of tier k and level `levels[k]`.
func limit_known(cid: String) -> Array:
	var L: Dictionary = Content.data.get("limits", {})
	var ids: Array = L.get("heroes", {}).get(cid, [])
	if ids.is_empty():
		return []
	var m = member(cid)
	var uses: Dictionary = m.get("limit_uses", {})
	var levels: Array = L.get("levels", [1, 15, 30, 50])
	var need: Array = L.get("uses", [0, 3, 5, 8])
	var out = [ids[0]]
	for k in range(1, ids.size()):
		if int(m["level"]) >= int(levels[k]) and int(uses.get(ids[k - 1], 0)) >= int(need[k]):
			out.append(ids[k])
		else:
			break
	return out

## What the next limit needs, for menus: {id, uses, need, level} or {} when all are known.
func limit_next(cid: String) -> Dictionary:
	var L: Dictionary = Content.data.get("limits", {})
	var ids: Array = L.get("heroes", {}).get(cid, [])
	var known = limit_known(cid)
	if known.size() >= ids.size():
		return {}
	var k = known.size()
	return {"id": ids[k], "uses": int(member(cid).get("limit_uses", {}).get(ids[k - 1], 0)), "need": int(L["uses"][k]), "level": int(L["levels"][k])}

## Reports newly learned limits once (tracked in member.limits_seen).
func limit_learning() -> Array:
	var msgs = []
	for cid in S["party"]["roster"]:
		var m = member(cid)
		var seen: Array = m.get("limits_seen", [])
		for aid in limit_known(cid):
			if not seen.has(aid):
				seen.append(aid)
				if seen.size() > 1:
					msgs.append("%s can now use the limit %s." % [short_name(cid), Content.ability(aid).get("name", aid)])
		m["limits_seen"] = seen
	return msgs

func blue_rule(cid: String) -> String:
	return str(Content.data.get("blue", {}).get("mages", {}).get(cid, ""))

## Learned blue magic (a shared pool) for a blue mage, in catalogue order.
func blue_for(cid: String) -> Array:
	if blue_rule(cid) == "":
		return []
	var known: Array = S.get("blue", [])
	return Content.data.get("blue", {}).get("order", []).filter(func(x): return known.has(x))

## Battle reserves: the next three available heroes after the active five (order set in the Formation menu).
func battle_reserves() -> Array:
	if S["party"].get("locked", false):
		return []
	var act = active()
	var out = []
	for cid in S["party"]["roster"]:
		if out.size() >= 3:
			break
		if is_available(cid) and not act.has(cid):
			out.append(cid)
	return out

func battle_reserve_party() -> Array:
	var out = []
	for cid in battle_reserves():
		var m = member(cid)
		var s = stats(cid)
		var hp = int(m["hp"]) if int(m["hp"]) >= 0 else int(s["mhp"])
		out.append({"cid": cid, "name": short_name(cid), "stats": s, "hp": mini(hp, s["mhp"]),
			"mp": mini(int(m["mp"]) if int(m["mp"]) >= 0 else int(s["mmp"]), s["mmp"]),
			"row": row(cid), "abilities": learned_abilities(cid), "link": link_of(cid),
			"limits": limit_known(cid), "limit": float(m.get("limit_gauge", 0.0)), "blue": blue_for(cid), "blue_rule": blue_rule(cid)})
	return out

static func fmt_time(sec: float) -> String:
	var s = int(sec)
	return "%d:%02d:%02d" % [s / 3600, (s / 60) % 60, s % 60]

# ======================================================================
# Expansion systems s2 (tools/content/gear2.py, crafting.py): item sets, teaching gear, crafting, gathering,
# bestiary completion, tier shop stock, regional inn prices.
# ======================================================================
func _g2() -> Dictionary:
	return Content.data.get("gear2", {})

## Set pieces worn by a member dict: {set id: pieces}. A piece counts once even if worn twice.
func set_counts(mem: Dictionary) -> Dictionary:
	var n = {}
	var seen = {}
	var eq: Dictionary = mem.get("equip", {})
	for slot in eq:
		var iid = eq[slot]
		if iid == null or iid == "" or seen.has(iid):
			continue
		seen[iid] = true
		var sid: String = str(Content.item(iid).get("set", ""))
		if sid != "":
			n[sid] = int(n.get(sid, 0)) + 1
	return n

static func _merge_passive(p: Dictionary, k: String, v) -> void:
	if not p.has(k):
		p[k] = v.duplicate(true) if (typeof(v) == TYPE_DICTIONARY or typeof(v) == TYPE_ARRAY) else v
	elif typeof(v) == TYPE_DICTIONARY and typeof(p[k]) == TYPE_DICTIONARY:
		p[k] = p[k].duplicate(true)   # never write into an item's own passive dict
		for e in v:
			p[k][e] = v[e]
	elif typeof(v) == TYPE_ARRAY and typeof(p[k]) == TYPE_ARRAY:
		p[k] = p[k].duplicate(true)
		for e in v:
			if not p[k].has(e):
				p[k].append(e)
	elif typeof(v) == TYPE_FLOAT or typeof(v) == TYPE_INT:
		p[k] = maxf(float(p[k]), float(v))

## Set bonuses: every threshold reached (2, 3, 4 pieces) adds its stats, passives and granted ability.
func apply_set_bonus(st: Dictionary, mem: Dictionary) -> Dictionary:
	var sets: Dictionary = _g2().get("sets", {})
	var cnt = set_counts(mem)
	var act = []
	var pas: Dictionary = st["passives"]
	var m0 = {"mhp_mult": float(pas.get("mhp_mult", 1.0)), "mmp_mult": float(pas.get("mmp_mult", 1.0)), "mag_bonus": float(pas.get("mag_bonus", 0.0))}
	for sid in cnt:
		if not sets.has(sid) or int(cnt[sid]) < 2:
			continue
		act.append([sid, int(cnt[sid]), sets[sid]["pieces"].size()])
		for th in sets[sid]["bonus"]:
			if int(cnt[sid]) < int(th):
				continue
			var b: Dictionary = sets[sid]["bonus"][th]
			for k in ["atk", "matk", "def", "res", "spd", "mhp", "mmp"]:
				if b.has(k):
					st[k] = int(st[k]) + int(b[k])
			for pk in b.get("passives", {}):
				_merge_passive(pas, pk, b["passives"][pk])
			if b.has("grants") and not st["grants"].has(b["grants"]):
				st["grants"].append(b["grants"])
	if not act.is_empty():
		if float(pas.get("mhp_mult", 1.0)) > m0["mhp_mult"]:
			st["mhp"] = int(floor(st["mhp"] * float(pas["mhp_mult"]) / m0["mhp_mult"]))
		if float(pas.get("mmp_mult", 1.0)) > m0["mmp_mult"]:
			st["mmp"] = int(floor(st["mmp"] * float(pas["mmp_mult"]) / m0["mmp_mult"]))
		if float(pas.get("mag_bonus", 0.0)) > m0["mag_bonus"]:
			st["matk"] = int(floor(st["matk"] * (1.0 + float(pas["mag_bonus"])) / (1.0 + m0["mag_bonus"])))
		st["acc_bonus"] = int(pas.get("acc_bonus", st.get("acc_bonus", 0)))
		if pas.has("weapon_element"):
			st["weapon_element"] = str(pas["weapon_element"])
	st["passives"] = pas
	st["sets"] = act
	return st

## Teaching gear (FF6 relic style): each active, conscious hero gains rate x AP on every ability taught by what they
## wear; at 100 it is known for good (kept in S.gknown, also when the item comes off).
func gear_learning(ap: int) -> Array:
	var msgs = []
	if not S.has("glearn"):
		S["glearn"] = {}
	if not S.has("gknown"):
		S["gknown"] = {}
	for cid in active():
		if int(member(cid)["hp"]) == 0:
			continue
		var prog: Dictionary = S["glearn"].get(cid, {})
		var known: Array = S["gknown"].get(cid, [])
		var eq: Dictionary = member(cid)["equip"]
		for slot in eq:
			var iid = eq[slot]
			if iid == null or iid == "":
				continue
			for t in Content.item(iid).get("teach", []):
				var aid: String = t[0]
				if known.has(aid) or learned_abilities(cid).has(aid) or Content.ability(aid).is_empty():
					continue
				var p = int(prog.get(aid, 0)) + int(t[1]) * ap
				if p >= 100:
					known.append(aid)
					prog.erase(aid)
					msgs.append("%s learned %s." % [short_name(cid), Content.ability(aid)["name"]])
				else:
					prog[aid] = p
		S["glearn"][cid] = prog
		S["gknown"][cid] = known
	return msgs

func gear_progress(cid: String, aid: String) -> int:
	if S.get("gknown", {}).get(cid, []).has(aid) or learned_abilities(cid).has(aid):
		return 100
	return int(S.get("glearn", {}).get(cid, {}).get(aid, 0))

# ---------------------------------------------------------------- crafting
func crafter_tier(crafter_id: String) -> String:
	return str(_g2().get("crafters", {}).get(crafter_id, "R01"))

## Recipe ids a crafter offers: every recipe of its tier or an earlier one (gear2 TIER_ORDER).
func craft_recipes(crafter_id: String) -> Array:
	var order: Array = _g2().get("tier_order", [])
	var lim = order.find(crafter_tier(crafter_id))
	var out = []
	var rs: Dictionary = _g2().get("recipes", {})
	var ids = rs.keys()
	ids.sort()
	for rid in ids:
		if order.find(rs[rid]["tier"]) <= lim:
			out.append(rid)
	return out

func can_craft(rid: String) -> Dictionary:
	var r: Dictionary = _g2().get("recipes", {}).get(rid, {})
	if r.is_empty():
		return {"ok": false, "reason": "Unknown recipe"}
	if r["kind"] == "reforge" and count(r["input"]) < 1:
		return {"ok": false, "reason": "Needs %s (unequipped)" % Content.item_name(r["input"])}
	for m in r["mats"]:
		if count(m[0]) < int(m[1]):
			return {"ok": false, "reason": "Needs %d %s" % [int(m[1]), Content.item(m[0]).get("name", m[0])]}
	if gold() < int(r.get("gold", 0)):
		return {"ok": false, "reason": "Not enough crowns"}
	if count(r["result"]) + int(r["count"]) > STACK_CAP:
		return {"ok": false, "reason": "No room"}
	return {"ok": true}

func craft(rid: String) -> Dictionary:
	var c = can_craft(rid)
	if not c["ok"]:
		return c
	var r: Dictionary = _g2()["recipes"][rid]
	for m in r["mats"]:
		remove_item(m[0], int(m[1]))
	if r["kind"] == "reforge":
		remove_item(r["input"], 1)
	spend_gold(int(r.get("gold", 0)))
	add_item(r["result"], int(r["count"]))
	emit_signal("state_changed")
	return {"ok": true, "item": r["result"], "count": int(r["count"])}

# ---------------------------------------------------------------- gathering
func node_ready(node_id: String, table: String) -> bool:
	var st: Dictionary = S.get("nodes", {}).get(node_id, {})
	if st.is_empty():
		return true
	var g: Dictionary = _g2().get("gather", {}).get(table, {})
	return int(S.get("steps", 0)) - int(st.get("steps", 0)) >= int(g.get("steps", 100)) \
		or int(S.get("battles", 0)) - int(st.get("battles", 0)) >= int(g.get("battles", 3))

func _party_passive(k: String) -> int:
	var best = 0
	for cid in active():
		best = maxi(best, int(stats(cid)["passives"].get(k, 0)))
	return best

## Harvest a node: `rolls` weighted draws from its table (loot stream), +1 per draw with a Gatherer's Satchel.
func gather(node_id: String, table: String) -> Dictionary:
	var g: Dictionary = _g2().get("gather", {}).get(table, {})
	if g.is_empty():
		return {"ok": false, "text": "Nothing here."}
	var verb: String = _g2().get("gather_verb", {}).get(g["kind"], "Found")
	if not node_ready(node_id, table):
		var spent = {"mine": "The seam is worked out for now.", "herb": "Nothing left to pick. It will grow back.", "salvage": "Picked clean. The tide will bring more."}
		return {"ok": false, "text": spent.get(g["kind"], "Nothing left for now.")}
	var r = Rng.new(next_seed("loot"))
	var total = 0
	for d in g["drops"]:
		total += int(d[1])
	var got = {}
	var bonus = _party_passive("gather_bonus")
	for i in range(int(g.get("rolls", 1))):
		var roll = r.randi_range(0, total - 1)
		for d in g["drops"]:
			roll -= int(d[1])
			if roll < 0:
				got[d[0]] = int(got.get(d[0], 0)) + r.randi_range(int(d[2]), int(d[3])) + bonus
				break
	var parts = []
	for iid in got:
		add_item(iid, got[iid])
		parts.append("%s x%d" % [Content.item_name(iid), got[iid]])
	if not S.has("nodes"):
		S["nodes"] = {}
	S["nodes"][node_id] = {"steps": int(S.get("steps", 0)), "battles": int(S.get("battles", 0))}
	emit_signal("state_changed")
	return {"ok": true, "got": got, "text": "%s %s." % [verb, ", ".join(parts)]}

# ---------------------------------------------------------------- bestiary completion
## Base entries: regular enemies, bosses and superbosses (no level variants, no boss parts).
func bestiary_entries() -> Array:
	var out = []
	for eid in Content.data["enemies"]:
		var e: Dictionary = Content.data["enemies"][eid]
		if e.has("variant_of") or e.get("tags", []).has("part") or "@" in eid:
			continue
		out.append(eid)
	out.sort_custom(func(a, b):
		var ka = 0 if a.begins_with("E") else (1 if a.begins_with("B") and not a.begins_with("BX") else (2 if a.begins_with("BX") else 3))
		var kb = 0 if b.begins_with("E") else (1 if b.begins_with("B") and not b.begins_with("BX") else (2 if b.begins_with("BX") else 3))
		if ka == kb:
			return a < b
		return ka < kb)
	return out

func bestiary_progress() -> Dictionary:
	var ids = bestiary_entries()
	var seen = 0
	var won = 0
	for eid in ids:
		var b: Dictionary = S["bestiary"].get(eid, {})
		if b.get("seen", false):
			seen += 1
		if int(b.get("defeated", 0)) > 0:
			won += 1
	return {"total": ids.size(), "seen": seen, "defeated": won}

## Milestones reached but not yet claimed: [[track, pct], ...] (track "seen" or "defeated").
func bestiary_rewards_pending() -> Array:
	var p = bestiary_progress()
	var out = []
	var claimed: Array = S.get("bestiary_claimed", [])
	var rw: Dictionary = _g2().get("bestiary_rewards", {})
	for track in ["seen", "defeated"]:
		for pct in [25, 50, 75, 100]:
			var key = "%s:%d" % [track, pct]
			if claimed.has(key) or not rw.get(track, {}).has(str(pct)):
				continue
			if int(p[track]) * 100 >= pct * int(p["total"]):
				out.append([track, pct])
	return out

func claim_bestiary_rewards() -> Array:
	var msgs = []
	if not S.has("bestiary_claimed"):
		S["bestiary_claimed"] = []
	for pr in bestiary_rewards_pending():
		S["bestiary_claimed"].append("%s:%d" % [pr[0], pr[1]])
		for rw in _g2()["bestiary_rewards"][pr[0]][str(pr[1])]:
			add_item(rw[0], int(rw[1]))
			msgs.append("%d%% %s: %s x%d." % [pr[1], pr[0], Content.item_name(rw[0]), int(rw[1])])
	return msgs

# ---------------------------------------------------------------- tier shop stock and inns
## Region-tier gear a shop stocks now: the shop's tiers, once their gate chapter is done; weapons only for a
## recruited hero who can use them; only the kinds the shop sells (plus gear2 shop_extra_kinds).
func tier_stock(shop_id: String) -> Array:
	var out = []
	var g2 = _g2()
	var sh: Dictionary = Content.data["shops"].get(shop_id, {})
	var kinds: Array = sh.get("kinds", []).duplicate()
	kinds.append_array(g2.get("shop_extra_kinds", {}).get(shop_id, []))
	for tid in g2.get("shop_tiers", {}).get(shop_id, []):
		var t: Dictionary = g2["tiers"][tid]
		if t["gate"] != "" and not chapter_done(t["gate"]):
			continue
		for iid in t["items"]:
			var it = Content.item(iid)
			var k = {"weapon": "weapons", "armor": "armor", "accessory": "accessories"}.get(it.get("kind", ""), "")
			if not kinds.has(k):
				continue
			if k == "weapons":
				var any = false
				for c in it.get("allowed", []):
					if is_recruited(c):
						any = true
						break
				if not any:
					continue
			if not out.has(iid):
				out.append(iid)
	return out

## Inn price in a region (docs/expansion/ECONOMY.md): the canon price, raised to the region's rate.
func inn_price_for(region: String, base: int) -> int:
	var g2 = _g2()
	var p = int(g2.get("inn", {}).get(region, 0))
	if S.get("world_phase", "pre") == "post" and region.begins_with("R"):
		p = maxi(p, int(g2.get("inn_post", 0)))
	return maxi(base, p)
# sys s4: meta counters, achievements, autosave / quicksave, New Game+
# ======================================================================
var _meta_dirty = false
var _meta_t = 0.0
signal achieved(id: String)

## Counters for achievements and records (battles, boss wins without a KO, fish caught, crafted ...). Other systems
## call Game.stat_add("crafted") etc.; the achievement evaluator reads them with "stat:<key>>=N".
func stat(k: String) -> int:
	return int(S.get("stats", {}).get(k, 0)) if not S.is_empty() else 0

func stat_add(k: String, n: int = 1) -> void:
	if S.is_empty():
		return
	if not S.has("stats"):
		S["stats"] = {}
	S["stats"][k] = stat(k) + n
	_meta_dirty = true

func stat_max(k: String, n: int) -> void:
	if n > stat(k):
		if not S.has("stats"):
			S["stats"] = {}
		S["stats"][k] = n
		_meta_dirty = true

func _battle_stats(model: BattleModel) -> void:
	stat_add("battles")
	if model.is_boss_battle:
		stat_add("boss_wins")
		if int(model.party_kos) == 0:
			stat_add("boss_nokos")
		for eid in model.enemy_ids:
			var e = model.battlers[eid]
			if e.tags.has("superboss"):
				stat_add("superbosses")
		request_autosave("boss")

## Unlocks an achievement (idempotent). Other systems may call it directly for event-style achievements.
func achieve(id: String) -> bool:
	return Achievements.unlock(id)

func has_achievement(id: String) -> bool:
	return Achievements.is_unlocked(id)

## Enemy scaling for battle: difficulty times the New Game+ cycle (+25% HP, +12% damage per cycle, up to NG+5).
func battle_difficulty() -> Dictionary:
	var d: Dictionary = DIFFICULTY.get(difficulty(), DIFFICULTY["normal"]).duplicate()
	var ng = clampi(int(S.get("ng", 0)) if not S.is_empty() else 0, 0, 5)
	if ng > 0:
		d["hp"] = float(d["hp"]) * (1.0 + 0.25 * ng)
		d["dmg"] = float(d["dmg"]) * (1.0 + 0.12 * ng)
	return d

# ---------------------------------------------------------------- autosave / quicksave
func auto_path() -> String:
	return save_root + "/auto.json"

func quick_path() -> String:
	return save_root + "/quick.json"
var _autosave_reason = ""
var last_autosave_ms = -100000

func save_auto(reason: String = "") -> Dictionary:
	if S.is_empty() or not playing:
		return {"ok": false, "reason": "no game"}
	var keep = S.get("save_id", "")
	S["save_id"] = "auto"
	S["autosave_reason"] = reason
	var r = save_to(auto_path())
	S["save_id"] = keep
	S.erase("autosave_reason")
	if r.get("ok", false):
		last_autosave_ms = Time.get_ticks_msec()
	return r

func save_quick() -> Dictionary:
	if S.is_empty():
		return {"ok": false, "reason": "no game"}
	var keep = S.get("save_id", "")
	S["save_id"] = "quick"
	var r = save_to(quick_path())
	S["save_id"] = keep
	return r

## Marks an autosave as due; main flushes it when no scene is running (never mid-scene, so a boss scene cannot be
## re-triggered by loading an autosave taken between its battle and its end).
func request_autosave(reason: String) -> void:
	if not Settings.get_v("autosave") or fixture_label.begins_with("unit") or S.is_empty():
		return
	_autosave_reason = reason

func autosave_pending() -> bool:
	return _autosave_reason != ""

func flush_autosave() -> Dictionary:
	if _autosave_reason == "" or fixture_label.begins_with("unit"):
		_autosave_reason = ""
		return {"ok": false, "reason": "none"}
	var why = _autosave_reason
	_autosave_reason = ""
	return save_auto(why)

## Everything the save list shows for one file: chapter, location, playtime, party (id + level), NG cycle, clear.
func info_from_state(s: Dictionary) -> Dictionary:
	var mp = Content.map(s["location"]["map"])
	var party = []
	for cid in s.get("party", {}).get("active", []):
		var m = s["party"]["members"].get(cid, {})
		party.append({"cid": cid, "level": int(m.get("level", 1)), "name": str(s.get("names", {}).get(cid, Content.ch(cid).get("short", cid)))})
	return {"ok": true, "chapter": _current_chapter_name(s), "location": mp.get("name", s["location"]["map"]),
		"playtime": float(s["playtime"]), "date": s.get("timestamp", ""), "level": int(s["party"]["members"]["C01"]["level"]),
		"party": party, "ng": int(s.get("ng", 0)), "clear": bool(s.get("clear", false)), "gold": int(s.get("inventory", {}).get("gold", 0)),
		"difficulty": str(s.get("difficulty", "normal")), "reason": str(s.get("autosave_reason", ""))}

func path_info(path: String) -> Dictionary:
	var r = _read_payload(path)
	if not r["ok"]:
		return r
	return info_from_state(r["state"])

## The newest readable save of all (manual slots, autosave, quicksave): {path, info} or {}.
func latest_save() -> Dictionary:
	var best = {}
	var paths = [auto_path(), quick_path()]
	for sl in range(1, SLOTS + 1):
		paths.append(slot_path(sl))
	for p in paths:
		var info = path_info(p)
		if info.get("ok", false) and (best.is_empty() or str(info["date"]) > str(best["info"]["date"])):
			best = {"path": p, "info": info}
	return best

# ---------------------------------------------------------------- New Game+
## Starts a new cycle from a cleared state: levels, XP, equipment, inventory (not key items), crowns, Vestiges,
## learned Vestige magic, smith upgrades, bestiary, fish log, counters, names and achievements carry; the story,
## quests, chests, flags and world state reset. Difficulty carries; Mature is a player setting and stays as set.
func new_game_plus(from: Dictionary) -> void:
	var carry = from.duplicate(true)
	new_game()
	S["ng"] = int(carry.get("ng", 0)) + 1
	S["difficulty"] = str(carry.get("difficulty", S["difficulty"]))
	for cid in carry["party"]["members"]:
		if not S["party"]["members"].has(cid):
			continue
		var om: Dictionary = carry["party"]["members"][cid]
		var nm: Dictionary = S["party"]["members"][cid]
		for k in ["level", "xp", "equip", "vbonus", "starter_given"]:
			if om.has(k):
				nm[k] = om[k]
		nm["hp"] = -1
		nm["mp"] = -1
	var items: Dictionary = {}
	for iid in carry["inventory"]["items"]:
		if Content.item(iid).get("kind", "") != "key":
			items[iid] = int(carry["inventory"]["items"][iid])
	S["inventory"]["items"] = items
	S["inventory"]["gold"] = int(carry["inventory"]["gold"])
	for k in ["vestiges", "vknown", "vlearn", "upgrades", "bestiary", "fish", "stats", "names", "achievements", "names_asked"]:
		if carry.has(k):
			S[k] = carry[k]
	S["links"] = {}
	S["stats"]["ng_started"] = int(S["stats"].get("ng_started", 0)) + 1
	# C01 re-joins with the carried level and gear
	var m = S["party"]["members"]["C01"]
	var st = stats("C01")
	m["hp"] = st["mhp"]
	m["mp"] = st["mmp"]
	_meta_dirty = true
	emit_signal("state_changed")

# ---------------------------------------------------------------- Mature mode
## Mature mode is on only with both the setting and the one-time 18+ confirmation.
func mature() -> bool:
	return bool(Settings.get_v("mature")) and bool(Settings.get_v("mature_ok"))

## Dialogue filter for the `{m:strong|mild}` markup in scene lines: the strong wording with Mature on, else the mild
## one (either side may be empty). Lines without markup pass through unchanged.
static func mature_filter(text: String, on: bool = false) -> String:
	var i = text.find("{m:")
	while i >= 0:
		var j = text.find("}", i)
		if j < 0:
			break
		var body = text.substr(i + 3, j - i - 3)
		var bar = body.find("|")
		var strong = body.substr(0, bar) if bar >= 0 else body
		var mild = body.substr(bar + 1) if bar >= 0 else ""
		text = text.substr(0, i) + (strong if on else mild) + text.substr(j + 1)
		i = text.find("{m:", i)
	return text.replace("  ", " ").strip_edges() if text.find("  ") >= 0 else text
