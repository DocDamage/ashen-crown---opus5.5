extends Node
## CampaignState + PartyService + InventoryService + SaveService.
## All progression lives in the save-owned dictionary `S`; scenes and UI only read/commit through here.

signal state_changed
signal notify(text: String)

const SCHEMA := 1
const SAVE_DIR := "user://saves"
const SLOTS := 3
const STACK_CAP := 99
const GOLD_CAP := 9999999
const CHAR_IDS := ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08"]

var S: Dictionary = {}
var playing = false
var session_start_ms = 0
var checkpoint: Dictionary = {}
var fixture_label = ""   # non-empty when state was built by a labelled test fixture

func _process(delta: float) -> void:
	if playing and not S.is_empty() and not get_tree().paused:
		S["playtime"] = float(S.get("playtime", 0.0)) + delta

# ======================================================================
# New game
# ======================================================================
func new_game() -> void:
	S = {
		"schema_version": SCHEMA, "content_version": Content.hash, "run_id": "%x" % (Time.get_unix_time_from_system() * 1000),
		"save_id": "", "timestamp": "", "playtime": 0.0, "world_phase": "pre", "chapters": [], "flags": {},
		"vars": {}, "events": [], "quests": {}, "party": {"roster": [], "available": {}, "active": [], "rows": {}, "members": {}, "locked": false},
		"inventory": {"gold": 300, "items": {}, "delivery": []}, "acquired": [], "chests": [], "discovered": [],
		"bestiary": {}, "vehicle": {"mode": "foot", "ship_map": "", "ship_x": 0, "ship_y": 0, "ferry": false, "cable": false, "ship": false},
		"location": {"map": "T01_PLATFORM", "spawn": "start", "x": -1, "y": -1, "dir": "down"},
		"rng": {"combat": 12345, "loot": 777, "enc": 4242}, "play_settings": {"encounters": Settings.get_v("encounters")},
		"journal": {"objective": "", "clue": "", "destination": "", "source": "", "rumors": [], "log": []},
		"links": {}, "salvage": [], "clear": false, "epilogue": {}, "last_town": "L_T01",
	}
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
		"clear": r = bool(S.get("clear", false))
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
	return F.member_stats(member(cid), Content.ch(cid), Content.data["items"])

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
	if S["party"]["active"].size() < 4 and not S["party"]["active"].has(cid):
		S["party"]["active"].append(cid)
	msgs.append("%s joins the party." % Content.ch(cid)["name"])
	emit_signal("state_changed")
	return msgs

func set_available(cid: String, val: bool) -> void:
	S["party"]["available"][cid] = val
	if not val:
		S["party"]["active"].erase(cid)
		# free any vestige link held by an unavailable member (reassign at next safe screen)
	else:
		if S["party"]["active"].size() < 4 and not S["party"]["active"].has(cid):
			S["party"]["active"].append(cid)

func set_active(order: Array) -> void:
	S["party"]["active"] = order.filter(func(c): return is_available(c)).slice(0, 4)

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
	return out

func battle_party() -> Array:
	var out = []
	for cid in active():
		var m = member(cid)
		var s = stats(cid)
		var hp = int(m["hp"]) if int(m["hp"]) >= 0 else int(s["mhp"])
		out.append({"cid": cid, "name": Content.ch(cid)["short"], "stats": s, "hp": mini(hp, s["mhp"]),
			"mp": mini(int(m["mp"]) if int(m["mp"]) >= 0 else int(s["mmp"]), s["mmp"]),
			"row": row(cid), "abilities": learned_abilities(cid), "link": link_of(cid)})
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
## up to x3. Transparent, deterministic, never removes XP; it only shortens the gap for direct-route play.
func catch_up_mult(level: int) -> float:
	var target = var_get("story_floor") + 4
	if var_get("story_floor") <= 0 or level >= target:
		return 1.0
	return minf(3.0, 1.0 + 0.25 * float(target - level))

func award_xp(amount: int) -> Array:
	## 100% XP to every recruited member, active, reserve or unavailable (docs/07).
	var msgs = []
	for cid in S["party"]["roster"]:
		var m = member(cid)
		var before = int(m["level"])
		var old_learn = learned_abilities(cid)
		m["xp"] = int(m["xp"]) + int(round(amount * catch_up_mult(before)))
		var nl = F.level_for_xp(int(m["xp"]))
		if nl > before:
			var s0 = stats(cid)
			m["level"] = nl
			var s1 = stats(cid)
			if int(m["hp"]) > 0:
				m["hp"] = int(m["hp"]) + (s1["mhp"] - s0["mhp"])
			m["mp"] = int(m["mp"]) + (s1["mmp"] - s0["mmp"])
			if is_available(cid):
				msgs.append("%s reached level %d." % [Content.ch(cid)["short"], nl])
				for a in learned_abilities(cid):
					if not old_learn.has(a):
						msgs.append("%s learned %s." % [Content.ch(cid)["short"], Content.ability(a)["name"]])
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
		return {"ok": false, "reason": "%s cannot use this" % Content.ch(cid)["short"]}
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
	add_gold(int(r["gold"]))
	msgs.append("Gained %d XP and %d crowns." % [r["xp"], r["gold"]])
	for d in r["drops"]:
		add_item(d, 1)
		msgs.append("Found %s." % Content.item_name(d))
	for st in model.stolen_items:
		add_item(st, 1)
		msgs.append("Kept stolen %s." % Content.item_name(st))
	msgs.append_array(award_xp(int(r["xp"])))
	emit_signal("state_changed")
	return msgs

func apply_battle_flee(model: BattleModel) -> void:
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
func slot_path(slot: int) -> String:
	return "%s/slot%d.json" % [SAVE_DIR, slot]

func _ensure_dir() -> void:
	DirAccess.make_dir_recursive_absolute(SAVE_DIR)

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
	return save_to(slot_path(slot))

func write_backup(tag: String) -> Dictionary:
	return save_to(backup_path(tag))

func backup_path(tag: String) -> String:
	return "%s/backup_%s.json" % [SAVE_DIR, tag]

## Protected backups: written by the story at fixed points, never by the slot menu. Load-only.
const PROTECTED := [["pre_dais", "Protected: Before the Crown Dais"], ["pre_finale", "Protected: Before the Final Descent"]]

func info_of(path: String) -> Dictionary:
	var r = _read_payload(path)
	if not r["ok"]:
		return r
	var s: Dictionary = r["state"]
	var mp = Content.map(s["location"]["map"])
	return {"ok": true, "chapter": _current_chapter_name(s), "location": mp.get("name", s["location"]["map"]),
		"playtime": float(s["playtime"]), "date": s.get("timestamp", ""), "level": int(s["party"]["members"]["C01"]["level"])}

func world_for_phase(map_id: String) -> String:
	## Pre-state dungeons revisited after the catastrophe exit to the altered overworld (shared location IDs).
	if map_id == "WORLD" and S.get("world_phase", "pre") == "post":
		return "WORLD_POST"
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
	for k in st["rng"]:
		st["rng"][k] = int(st["rng"][k])
	return st

func slot_info(slot: int) -> Dictionary:
	var r = _read_payload(slot_path(slot))
	if not r["ok"]:
		return r
	var s: Dictionary = r["state"]
	var ch_name = "Prologue"
	var last = ""
	for c in s["chapters"]:
		last = c
	var cur_ch = _current_chapter_name(s)
	var mp = Content.map(s["location"]["map"])
	return {"ok": true, "chapter": cur_ch, "location": mp.get("name", s["location"]["map"]),
		"playtime": float(s["playtime"]), "date": s.get("timestamp", ""), "level": int(s["party"]["members"]["C01"]["level"])}

func _current_chapter_name(s: Dictionary) -> String:
	var ids: Array = Content.data["chapters"].keys()
	ids.sort()
	for cid in ids:
		if not s["chapters"].has(cid) and Content.data["chapters"][cid]["status"] == "required":
			return "%s %s" % [cid.replace("CH", "Ch."), Content.data["chapters"][cid]["name"]]
	return "Complete"

func current_chapter() -> String:
	return _current_chapter_name(S)

static func fmt_time(sec: float) -> String:
	var s = int(sec)
	return "%d:%02d:%02d" % [s / 3600, (s / 60) % 60, s % 60]
