class_name BattleModel
extends RefCounted
## Deterministic fixed-step ATB battle simulation (docs/06_COMBAT_SPECIFICATION.md).
## No scene nodes, no animation timing: the presenter reads `events` and calls ack().

const TICK_HZ := 60
const DT := 1.0 / 60.0
const HARD_CONTROL := ["sleep", "stun"]
const REMOVABLE_NEG := ["poison", "burn", "bleed", "silence", "sleep", "stun", "slow", "mark", "guardbreak", "blind", "doom", "weaken"]
const REMOVABLE_POS := ["haste", "barrier", "regen", "focus"]
const SPELL_KINDS := ["magical", "heal", "revive"]
const LIMIT_MAX := 100.0
const SWAP_ATB := 400.0      # a hero swapped in from the reserve enters with a partly filled gauge

class Battler:
	var id = ""
	var side = 0          # 0 party, 1 enemy
	var ref = ""          # character or enemy content id
	var name = ""
	var level = 1
	var mhp = 1
	var hp = 1
	var mmp = 0
	var mp = 0
	var atk = 1.0
	var matk = 1.0
	var def = 0.0
	var res = 0.0
	var spd = 10
	var acc_bonus = 0
	var row = "front"
	var aff = {}
	var tags = []
	var passives = {}
	var abilities = []
	var atb = 0.0
	var state = "FILLING"
	var ready_tick = 0
	var statuses = {}
	var oath = ""
	var overcast = false
	var heat_uses = 0
	var heat_ready = true
	var infusion = {}
	var mine = {}
	var protect = 0
	var lethal_guard = false
	var feather = false
	var evasion = {}
	var mirror_charge = false
	var status_ward = 0
	var steal = {"common_taken": false, "rare_taken": false, "fails": 0}
	var timer = 0.0
	var pending = {}
	var defending = false
	var defend_concord = false
	var once = {}
	var ai = {"idx": 0, "phase": 0, "last_target": ""}
	var intent = {}
	var resist_mods = {}
	var grounded = 0
	var quick_hands = false
	var witness_charge = false
	var part_of = ""
	var part_hit = false
	var weapon_element = "physical"
	var ranged = false
	var two_handed = false
	var xp = 0
	var gold = 0
	var drops = []
	var steal_table = {}
	var sprite = ""
	var split_done = false
	var copy_element = ""
	var hits_taken = 0
	var mercy_used = false
	var dispel_ward_used = false
	var extra = {}
	# expansion battle systems (limit breaks, blue magic, capture)
	var limit = 0.0
	var limits = []
	var limit_used = []
	var blue = []
	var blue_rule = ""
	var link = ""

	func alive() -> bool:
		return state != "KO"

	func is_boss() -> bool:
		return tags.has("boss")

	func has(s: String) -> bool:
		return statuses.has(s)

	func targetable() -> bool:
		return alive() and state != "AIRBORNE"

# ---- model state ----
var content: Dictionary
var rng: Rng
var loot_rng: Rng
var tick = 0
var battlers = {}
var party_ids = []
var enemy_ids = []
var inventory = {}      # working copy of consumable counts
var reserved_items = {} # action_key -> item id
var concord = 0
var flee_meter = 0
var can_flee = true
var is_boss_battle = false
var party_kos = 0            # sys s4: knockouts suffered by the party this battle (no-KO boss achievements)
var mode = "wait"
var speed = 1.0
var menu_open = false
var paused = false
var locked = false
var queue = []
var events = []
var result = ""
var log = []
var summons_used = {}
var links = {}           # battler id -> vestige id
var decoy = {}
var action_seq = 0
var gold_stolen = 0
var encounter = {}
var phase_queue = []
var seed_used = 0
var ready_order = []    # player battlers waiting for input, ordered
var stats = {"actions": 0}
var stolen_items = []
var reserve_ids = []    # up to 3 reserve heroes (battlers built at setup, outside party_ids until swapped in)
var blue_new = {}       # blue ability id -> cid of the hero who learned it this battle
var captured = []       # enemy content ids captured this battle
var morph_items = []    # rare items from captures
var limit_active = false

func _init(p_content: Dictionary) -> void:
	content = p_content

# ======================================================================
# Setup
# ======================================================================
## party: Array of dicts {cid, name, level, stats (F.member_stats), hp, mp, row, abilities, link}
## enemies: Array of enemy content ids (formation slots) or dicts {id, level}
var opts_diff: Dictionary = {}     # difficulty multipliers for enemies {hp, dmg}

func setup(party: Array, enemies: Array, inv: Dictionary, seed_value: int, opts: Dictionary = {}) -> void:
	seed_used = seed_value
	rng = Rng.new(seed_value)
	loot_rng = Rng.new(seed_value ^ 0x5bd1e995)
	inventory = inv.duplicate(true)
	mode = opts.get("mode", "wait")
	opts_diff = opts.get("difficulty", {})
	speed = float(opts.get("speed", 1.0))
	encounter = opts.get("encounter", {})
	var i = 1
	for p in party:
		var b = _build_hero(p, "A%d" % i, opts)
		i += 1
		battlers[b.id] = b
		party_ids.append(b.id)
	for p in opts.get("reserves", []).slice(0, 3):
		var rb = _build_hero(p, "A%d" % i, opts)
		i += 1
		battlers[rb.id] = rb
		reserve_ids.append(rb.id)
	var e = 1
	for spec in enemies:
		add_enemy(spec, e)
		e += 1
	is_boss_battle = opts.get("boss", false)
	for eid in enemy_ids:
		if battlers[eid].is_boss():
			is_boss_battle = true
	can_flee = not is_boss_battle and not opts.get("no_flee", false)
	# initial readiness spread so identical speeds do not act on the same frame
	for bid in party_ids + enemy_ids:
		var b: Battler = battlers[bid]
		if b.side == 1:
			b.atb = float(rng.randi_range(0, 300))
		else:
			b.atb += float(rng.randi_range(100, 400))

func _build_hero(p: Dictionary, bid: String, opts: Dictionary) -> Battler:
		var b = Battler.new()
		b.id = bid
		b.side = 0
		b.ref = p["cid"]
		b.name = p["name"]
		var st: Dictionary = p["stats"]
		b.level = int(st["level"])
		b.mhp = int(st["mhp"])
		b.hp = clampi(int(p.get("hp", b.mhp)), 0, b.mhp)
		b.mmp = int(st["mmp"])
		b.mp = clampi(int(p.get("mp", b.mmp)), 0, b.mmp)
		b.atk = float(st["atk"])
		b.matk = float(st["matk"])
		b.def = float(st["def"])
		b.res = float(st["res"])
		b.spd = int(st["spd"])
		b.acc_bonus = int(st.get("acc_bonus", 0))
		b.passives = st.get("passives", {})
		b.weapon_element = str(st.get("weapon_element", "physical"))
		b.ranged = bool(st.get("ranged", false))
		b.two_handed = bool(st.get("two_handed", false))
		b.row = p.get("row", "front")
		b.abilities = p.get("abilities", []).duplicate()
		for g in st.get("grants", []):
			if not b.abilities.has(g):
				b.abilities.append(g)
		b.sprite = p["cid"]
		if b.hp <= 0:
			b.state = "KO"
		b.atb = float(opts.get("start_atb", 0)) + (100.0 if b.passives.has("start_atb") and not encounter.get("scripted_start", false) else 0.0)
		if b.passives.has("immune"):
			pass
		if p.get("link", "") != "":
			links[b.id] = p["link"]
		b.link = str(p.get("link", ""))
		b.limit = clampf(float(p.get("limit", 0.0)), 0.0, LIMIT_MAX)
		b.limits = p.get("limits", []).duplicate()
		b.blue = p.get("blue", []).duplicate()
		b.blue_rule = str(p.get("blue_rule", ""))
		return b

func add_enemy(spec, idx: int) -> Battler:
	var eid: String = spec if typeof(spec) == TYPE_STRING else spec["id"]
	var d: Dictionary = content["enemies"][eid]
	var b = Battler.new()
	b.id = "E%d" % idx
	while battlers.has(b.id):
		idx += 1
		b.id = "E%d" % idx
	b.side = 1
	b.ref = eid
	b.name = d["name"]
	b.level = int(d["level"])
	var lvl_override = null if typeof(spec) == TYPE_STRING else spec.get("level", null)
	var scale = 1.0
	if lvl_override != null and int(lvl_override) != b.level:
		scale = float(int(lvl_override)) / float(b.level)
		b.level = int(lvl_override)
	b.mhp = int(round(int(d["hp"]) * (scale * scale if scale != 1.0 else 1.0)))
	if typeof(spec) != TYPE_STRING and spec.has("hp"):
		b.mhp = int(spec["hp"])
	b.mhp = maxi(1, int(round(b.mhp * float(opts_diff.get("hp", 1.0)))))
	b.hp = b.mhp
	b.mmp = 999
	b.mp = 999
	b.atk = float(d["atk"]) * scale * float(opts_diff.get("dmg", 1.0))
	b.matk = float(d["mag"]) * scale * float(opts_diff.get("dmg", 1.0))
	b.def = float(d["def"]) * scale
	b.res = float(d["res"]) * scale
	b.spd = int(d["spd"])
	b.aff = d.get("affinities", {}).duplicate()
	b.tags = d.get("tags", []).duplicate()
	b.xp = int(round(int(d.get("xp", 0)) * scale))
	b.gold = int(round(int(d.get("gold", 0)) * scale))
	b.drops = d.get("drops", [])
	b.steal_table = d.get("steal", {})
	b.sprite = d.get("sprite", eid)
	b.row = "front"
	if typeof(spec) != TYPE_STRING and spec.has("part_of"):
		b.part_of = spec["part_of"]
		b.tags.append("part")
	battlers[b.id] = b
	enemy_ids.append(b.id)
	return b

# ======================================================================
# Queries
# ======================================================================
func get_b(id: String) -> Battler:
	return battlers.get(id)

func living(side: int) -> Array:
	var out = []
	for bid in (party_ids if side == 0 else enemy_ids):
		if battlers[bid].alive():
			out.append(battlers[bid])
	return out

func targetable_list(side: int) -> Array:
	var out = []
	for b in living(side):
		if b.targetable():
			out.append(b)
	return out

func awaiting_input() -> Battler:
	for bid in ready_order:
		var b: Battler = battlers[bid]
		if b.state == "READY" or b.state == "SELECTING":
			return b
	return null

func sim_paused() -> bool:
	if paused or locked or result != "":
		return true
	if mode == "wait" and menu_open:
		return true
	return false

func ability(id: String) -> Dictionary:
	return content["abilities"].get(id, {})

# ======================================================================
# Simulation step
# ======================================================================
func step() -> void:
	if result != "":
		return
	if locked:
		return
	# resolve queued actions first (presentation lock after each)
	if not phase_queue.is_empty():
		_run_phase_transition(phase_queue.pop_front())
		return
	if not queue.is_empty():
		var act = queue.pop_front()
		_resolve(act)
		return
	if sim_paused():
		return
	tick += 1
	var order = party_ids + enemy_ids
	for bid in order:
		var b: Battler = battlers[bid]
		if not b.alive() or b.tags.has("part"):
			continue
		match b.state:
			"FILLING":
				var rate = F.atb_rate(b.spd, speed, b.has("haste"), b.has("slow"), b.is_boss())
				if b.side == 0 and b.passives.has("atb_mult"):
					rate *= float(b.passives["atb_mult"])
				b.atb = minf(F.ATB_MAX, b.atb + rate * DT)
				if b.atb >= F.ATB_MAX:
					_on_ready(b)
			"CASTING", "AIRBORNE":
				b.timer -= DT
				if b.timer <= 0.0:
					b.timer = 0.0
					_enqueue(b.pending)
	_check_end()

func _on_ready(b: Battler) -> void:
	b.atb = F.ATB_MAX
	b.ready_tick = tick
	# hard-control skipping at the action opportunity
	for hc in HARD_CONTROL:
		if b.has(hc):
			_dec_status(b, hc)
			b.atb = 0.0
			_push_event({"type": "skip", "actor": b.id, "status": hc})
			return
	if b.has("doom"):
		pass
	if b.side == 0:
		b.state = "READY"
		ready_order.append(b.id)
		ready_order.sort_custom(func(x, y):
			var bx: Battler = battlers[x]
			var by: Battler = battlers[y]
			if bx.ready_tick == by.ready_tick:
				return x < y
			return bx.ready_tick < by.ready_tick)
		b.defend_concord = false
	else:
		b.state = "READY"
		_enemy_decide(b)

func begin_select(b: Battler) -> void:
	if b.state == "READY":
		b.state = "SELECTING"

func cancel_select(b: Battler) -> void:
	if b.state == "SELECTING":
		b.state = "READY"

# ======================================================================
# Commands (player)
# ======================================================================
## cmd: {type: attack|ability|item|defend|row|escape|summon, id, targets:[ids]}
func validate(b: Battler, cmd: Dictionary) -> Dictionary:
	if not b.alive():
		return {"ok": false, "reason": "Unable to act"}
	var t: String = cmd.get("type", "")
	match t:
		"attack", "defend", "row":
			return {"ok": true}
		"escape":
			if not can_flee:
				return {"ok": false, "reason": "Cannot escape this battle"}
			return {"ok": true}
		"ability":
			var a = ability(cmd.get("id", ""))
			if a.is_empty():
				return {"ok": false, "reason": "Unknown technique"}
			if not (b.abilities.has(a["id"]) or b.limits.has(a["id"]) or b.blue.has(a["id"])):
				return {"ok": false, "reason": "Not learned"}
			if int(a.get("limit_tier", 0)) > 0 and b.limit < LIMIT_MAX:
				return {"ok": false, "reason": "Limit %d%%" % int(b.limit)}
			if b.has("silence") and a.get("family", "skill") in ["spell", "blue"]:
				return {"ok": false, "reason": "Silenced"}
			var cost = mp_cost(b, a)
			if b.mp < cost:
				return {"ok": false, "reason": "Not enough MP"}
			var r = _ability_rule_check(b, a)
			if not r["ok"]:
				return r
			return {"ok": true, "cost": cost}
		"swap":
			var rid: String = str(cmd.get("reserve", ""))
			if reserve_ids.is_empty():
				return {"ok": false, "reason": "No one in reserve"}
			if rid == "":
				for x in reserve_ids:
					if battlers[x].alive():
						return {"ok": true}
				return {"ok": false, "reason": "The reserve cannot fight"}
			if not reserve_ids.has(rid):
				return {"ok": false, "reason": "Not in reserve"}
			if not battlers[rid].alive():
				return {"ok": false, "reason": "Unable to fight"}
			return {"ok": true}
		"summon":
			var vid: String = links.get(b.id, "")
			if vid == "":
				return {"ok": false, "reason": "No Vestige linked"}
			if b.has("silence"):
				return {"ok": false, "reason": "Silenced"}
			if summons_used.has(vid):
				return {"ok": false, "reason": "Already summoned"}
			if concord < 100:
				return {"ok": false, "reason": "Concord %d/100" % concord}
			return {"ok": true}
		"item":
			var iid: String = cmd.get("id", "")
			var it: Dictionary = content["items"].get(iid, {})
			if it.is_empty() or it.get("kind", "") != "consumable":
				return {"ok": false, "reason": "Not usable"}
			if not it.get("battle", true):
				return {"ok": false, "reason": "Not usable in battle"}
			if int(inventory.get(iid, 0)) <= 0:
				return {"ok": false, "reason": "None left"}
			if iid == "I014" and not can_flee:
				return {"ok": false, "reason": "Cannot escape this battle"}
			if iid == "I020" and once_party("seed"):
				return {"ok": false, "reason": "One Seed per battle"}
			return {"ok": true}
	return {"ok": false, "reason": "Unknown command"}

func once_party(key: String) -> bool:
	return summons_used.has("__" + key)

func _ability_rule_check(b: Battler, a: Dictionary) -> Dictionary:
	for op in a.get("ops", []):
		match op["op"]:
			"heat_exchange":
				if b.heat_uses >= 3:
					return {"ok": false, "reason": "Used 3 times"}
				if not b.heat_ready:
					return {"ok": false, "reason": "Cast a damaging spell first"}
			"wingbeat":
				if b.once.has("wingbeat_cycle"):
					return {"ok": false, "reason": "Once per readiness cycle"}
			"once_per_battle":
				if b.once.has(a["id"]):
					return {"ok": false, "reason": "Once per battle"}
			"arm_overcast":
				if b.overcast:
					return {"ok": false, "reason": "Already armed"}
			"decoy":
				if not decoy.is_empty():
					return {"ok": false, "reason": "Decoy already active"}
	return {"ok": true}

func mp_cost(b: Battler, a: Dictionary) -> int:
	var c = int(a.get("mp", 0))
	if b.overcast and a.get("elemental_spell", false):
		c = int(ceil(c * 1.75))
	return c

func commit(b: Battler, cmd: Dictionary) -> Dictionary:
	var v = validate(b, cmd)
	if not v["ok"]:
		return v
	action_seq += 1
	var act = cmd.duplicate(true)
	act["actor"] = b.id
	act["key"] = "act%d" % action_seq
	act["commit_tick"] = tick
	act["ready_tick"] = b.ready_tick
	act["reserved_mp"] = 0
	var cast = 0.0
	match cmd["type"]:
		"ability":
			var a = ability(cmd["id"])
			var cost: int = v["cost"]
			b.mp -= cost
			act["reserved_mp"] = cost
			if int(a.get("limit_tier", 0)) > 0:
				act["reserved_limit"] = b.limit
				b.limit = 0.0
			cast = float(a.get("cast", 0.0))
			for op in a.get("ops", []):
				if op["op"] == "leap":
					act["leap"] = true
					cast = float(op.get("time", 1.2))
		"item":
			var iid: String = cmd["id"]
			inventory[iid] = int(inventory[iid]) - 1
			reserved_items[act["key"]] = iid
			if iid == "I020":
				summons_used["__seed"] = true
				act["seed_reserved"] = true
		"summon":
			act["vestige"] = links[b.id]
			summons_used[links[b.id]] = true
			concord -= 100
			act["reserved_concord"] = 100
	ready_order.erase(b.id)
	b.pending = act
	log.append({"tick": tick, "actor": b.id, "cmd": cmd.duplicate(true)})
	if act.get("leap", false):
		b.state = "AIRBORNE"
		b.timer = cast
		_push_event({"type": "leap_up", "actor": b.id})
	elif cast > 0.0:
		b.state = "CASTING"
		b.timer = cast
	else:
		b.state = "COMMITTED"
		_enqueue(act)
	return {"ok": true}

func _enqueue(act: Dictionary) -> void:
	var b: Battler = battlers[act["actor"]]
	if b.state != "AIRBORNE":
		b.state = "COMMITTED"
	queue.append(act)
	queue.sort_custom(func(x, y):
		if x["ready_tick"] == y["ready_tick"]:
			return x["actor"] < y["actor"]
		return x["ready_tick"] < y["ready_tick"])

# ======================================================================
# Enemy AI
# ======================================================================
func _enemy_def(b: Battler) -> Dictionary:
	return content["enemies"][b.ref]

func _current_cycle(b: Battler) -> Array:
	var d = _enemy_def(b)
	if d.has("phases"):
		return d["phases"][b.ai["phase"]]["cycle"]
	return d.get("cycle", ["attack"])

func next_scheduled_move(b: Battler) -> String:
	var cyc = _current_cycle(b)
	if cyc.is_empty():
		return "attack"
	return cyc[b.ai["idx"] % cyc.size()]

func _enemy_decide(b: Battler) -> void:
	var d = _enemy_def(b)
	var mid = next_scheduled_move(b)
	b.ai["idx"] += 1
	var mv: Dictionary = d.get("moves", {}).get(mid, {})
	if mv.is_empty():
		mv = {"name": "Attack", "ops": [{"op": "damage", "power": 100, "type": "physical"}], "target": "random"}
	var targets = _enemy_targets(b, mv)
	action_seq += 1
	var act = {"type": "enemy", "actor": b.id, "move": mid, "targets": targets, "key": "act%d" % action_seq,
		"commit_tick": tick, "ready_tick": b.ready_tick}
	b.pending = act
	b.intent = {"move": mid, "name": mv.get("name", mid), "targets": targets, "tell": mv.get("tell", "")}
	var charge = float(mv.get("charge", 0.0))
	if charge > 0.0:
		b.state = "CASTING"
		b.timer = charge
		b.part_hit = false
		_push_event({"type": "tell", "actor": b.id, "text": mv.get("tell", mv.get("name", "")), "targets": targets})
	else:
		_enqueue(act)

func _enemy_targets(b: Battler, mv: Dictionary) -> Array:
	var rule: String = mv.get("target", "random")
	var foes = targetable_list(0)
	var allies = living(1)
	if foes.is_empty():
		return []
	# decoy draws eligible single-target attacks
	match rule:
		"all":
			return foes.map(func(x): return x.id)
		"self":
			return [b.id]
		"ally_lowest":
			var best: Battler = null
			for a in allies:
				if best == null or float(a.hp) / a.mhp < float(best.hp) / best.mhp:
					best = a
			return [best.id]
		"ally_random":
			return [rng.pick(allies).id]
		"row_front", "row_back":
			var want = "front" if rule == "row_front" else "back"
			var rowed = foes.filter(func(x): return x.row == want)
			if rowed.is_empty():
				rowed = foes
			return rowed.map(func(x): return x.id)
		"front_lowest":
			var fr = foes.filter(func(x): return x.row == "front")
			if fr.is_empty():
				fr = foes
			var lo: Battler = fr[0]
			for x in fr:
				if x.hp < lo.hp or (x.hp == lo.hp and x.id < lo.id):
					lo = x
			return [lo.id]
		"highest_mp":
			var hi: Battler = foes[0]
			for x in foes:
				if x.mp > hi.mp:
					hi = x
			return [hi.id]
		"marked":
			if b.ai.get("last_target", "") != "" and battlers.has(b.ai["last_target"]) and battlers[b.ai["last_target"]].targetable():
				return [b.ai["last_target"]]
			return [rng.pick(foes).id]
		"lowest_hp":
			var l2: Battler = foes[0]
			for x in foes:
				if float(x.hp) / x.mhp < float(l2.hp) / l2.mhp:
					l2 = x
			return [l2.id]
		"protector":
			# Voss points at a protector: prefer a defending/oath ally, else front
			for x in foes:
				if x.oath != "" or x.defending:
					return [x.id]
			return [rng.pick(foes).id]
		_:
			# random weighted toward front row (2:1)
			var pool = []
			for x in foes:
				pool.append(x)
				if x.row == "front":
					pool.append(x)
			return [rng.pick(pool).id]

# ======================================================================
# Resolution
# ======================================================================
func _refund(act: Dictionary) -> void:
	var b: Battler = battlers[act["actor"]]
	b.mp = mini(b.mmp, b.mp + int(act.get("reserved_mp", 0)))
	if reserved_items.has(act["key"]):
		var iid: String = reserved_items[act["key"]]
		inventory[iid] = int(inventory.get(iid, 0)) + 1
		reserved_items.erase(act["key"])
		if act.get("seed_reserved", false):
			summons_used.erase("__seed")
	if act.has("reserved_concord"):
		concord += int(act["reserved_concord"])
		summons_used.erase(act.get("vestige", ""))
	if act.has("reserved_limit"):
		b.limit = maxf(b.limit, float(act["reserved_limit"]))

func _resolve(act: Dictionary) -> void:
	var b: Battler = battlers[act["actor"]]
	stats["actions"] += 1
	if not b.alive():
		_refund(act)
		_push_event({"type": "lost_turn", "actor": b.id})
		return
	var ev = {"type": "action", "actor": b.id, "key": act["key"], "results": [], "msgs": []}
	var ctx = {"act": act, "ev": ev, "depth": 0, "damaging_spell": false, "reactions": {}}
	b.defending = false
	b.extra.erase("shell")
	b.intent = {}
	match act["type"]:
		"attack":
			ev["name"] = "Attack"
			ev["anim"] = "shoot" if b.ranged else "attack"
			var tgt = _retarget_offense(b, act.get("targets", []), 1)
			var power = 100.0
			var op = {"op": "damage", "power": power, "type": "physical", "element": b.weapon_element}
			if not b.infusion.is_empty():
				op["element"] = b.infusion["elem"]
				op["infused"] = true
			if b.witness_charge:
				op["power"] = power * 1.2
				b.witness_charge = false
			for t in tgt:
				_apply_op(b, t, op, ctx)
			if not b.infusion.is_empty():
				_infusion_attack_rider(b, tgt, ctx)
			_gain_concord(b, 6)
		"defend":
			ev["name"] = "Defend"
			ev["anim"] = "guard"
			b.defending = true
			if not b.defend_concord:
				b.defend_concord = true
				_gain_concord(b, 3)
		"row":
			b.row = "back" if b.row == "front" else "front"
			ev["name"] = "Row: " + b.row
			ev["anim"] = "step"
		"swap":
			_do_swap(b, act, ev)
		"escape":
			ev["name"] = "Escape"
			ev["anim"] = "step"
			flee_meter += 250
			if flee_meter >= 1000:
				result = "fled"
			ev["msgs"].append("Escape %d%%" % mini(100, flee_meter / 10))
		"ability":
			var a = ability(act["id"])
			ev["name"] = a["name"]
			ev["anim"] = a.get("anim", "cast")
			ev["element"] = a.get("element", "none")
			ev["ability"] = a["id"]
			if int(a.get("limit_tier", 0)) > 0:
				ev["limit"] = true
				b.limit_used.append(a["id"])
				limit_active = true
			_run_ability(b, a, act, ctx)
			limit_active = false
		"summon":
			var vid: String = act["vestige"]
			var sid: String = content["vestiges"][vid]["summon"]
			var a2 = ability(sid)
			ev["name"] = a2["name"]
			ev["anim"] = "summon"
			ev["summon"] = vid
			ev["element"] = a2.get("element", "none")
			var tg = []
			for x in (targetable_list(1) if a2.get("target", "") == "enemy_all" else living(0)):
				tg.append(x)
			for op in a2["ops"]:
				var t_list = tg
				if op.get("to", "") == "allies":
					t_list = living(0)
				elif op.get("to", "") == "enemies":
					t_list = targetable_list(1)
				for t in t_list:
					_apply_op(b, t, op, ctx)
		"item":
			var iid: String = act["id"]
			var it: Dictionary = content["items"][iid]
			ev["name"] = it["name"]
			ev["anim"] = "item"
			reserved_items.erase(act["key"])
			_run_item(b, it, act, ctx)
			if iid == "I020":
				concord = mini(100, concord + 30)
			if b.quick_hands:
				b.quick_hands = false
				ctx["atb_refund"] = 500
		"enemy":
			_resolve_enemy(b, act, ctx)
	_after_action(b, act, ctx)
	_push_event(ev)

func _after_action(b: Battler, act: Dictionary, ctx: Dictionary) -> void:
	if not b.alive():
		_finish_actor(b, ctx)
		_check_end()
		return
	# damage/heal over time after an actual resolved action
	var tick_ops = []
	if b.has("poison"):
		tick_ops.append(["poison", mini(F.DAMAGE_CAP, int(ceil(b.mhp * 0.04))), true])
	if b.has("burn"):
		tick_ops.append(["burn", mini(F.DAMAGE_CAP, int(ceil(b.mhp * 0.03))), true])
	if b.has("bleed") and ctx.get("physical_action", false):
		tick_ops.append(["bleed", mini(F.DAMAGE_CAP, int(ceil(b.mhp * 0.05))), true])
	if b.has("regen"):
		tick_ops.append(["regen", int(floor(b.mhp * 0.05)), false])
	if b.side == 0 and b.passives.has("mp_regen") and b.mp < b.mmp:
		var mr = mini(int(b.passives["mp_regen"]), b.mmp - b.mp)
		b.mp += mr
		ctx["ev"]["results"].append({"id": b.id, "kind": "mp", "amount": mr, "status": "mp_regen"})
	for t in tick_ops:
		if not b.alive():
			break
		if t[2]:
			b.hp = maxi(0, b.hp - t[1])
			ctx["ev"]["results"].append({"id": b.id, "kind": "dot", "amount": t[1], "status": t[0]})
			if b.hp == 0:
				_ko(b, ctx)
		else:
			var h = mini(t[1], b.mhp - b.hp)
			b.hp += h
			ctx["ev"]["results"].append({"id": b.id, "kind": "heal", "amount": h, "status": t[0]})
	# decrement action-based durations (one per resolved action)
	for s in b.statuses.keys().duplicate():
		if s in HARD_CONTROL:
			continue
		if s == "doom":
			continue
		_dec_status(b, s)
	if b.has("doom"):
		_dec_status(b, "doom")
		if not b.has("doom") and b.alive():
			b.hp = 0
			ctx["ev"]["results"].append({"id": b.id, "kind": "doom"})
			_ko(b, ctx)
	for k in b.resist_mods.keys().duplicate():
		b.resist_mods[k]["dur"] -= 1
		if b.resist_mods[k]["dur"] <= 0:
			b.resist_mods.erase(k)
	if b.grounded > 0:
		b.grounded -= 1
	if b.protect > 0:
		b.extra["protect_dur"] = int(b.extra.get("protect_dur", 3)) - 1
		if b.extra["protect_dur"] <= 0:
			b.protect = 0
	if b.has("barrier") == false:
		b.extra.erase("bramble")
	if not b.infusion.is_empty() and act["type"] != "ability":
		b.infusion["dur"] -= 1
		if b.infusion["dur"] <= 0:
			b.infusion = {}
	# Clock Mine detonates after that enemy's next resolved action
	if not b.mine.is_empty() and b.alive() and act["type"] == "enemy":
		var m = b.mine
		b.mine = {}
		var owner: Battler = battlers.get(m["owner"])
		if owner != null:
			var op = {"op": "damage", "power": m["power"], "type": "magical", "element": "fire", "reaction": true}
			_apply_op(owner, b, op, ctx)
			ctx["ev"]["msgs"].append("Clock Mine detonates!")
	_finish_actor(b, ctx)
	_check_phase_and_split(ctx)
	_check_end()

func _finish_actor(b: Battler, ctx: Dictionary) -> void:
	if b.alive():
		b.atb = minf(500.0, float(ctx.get("atb_refund", 0)))
		b.state = "FILLING"
		b.timer = 0.0
		b.once.erase("wingbeat_cycle")
		b.once.erase("pilfer_cycle")
		b.extra["delay_since_action"] = 0.0
		b.extra["omen_cycle"] = false
	b.pending = {}

func _dec_status(b: Battler, s: String) -> void:
	if not b.statuses.has(s):
		return
	b.statuses[s]["dur"] -= 1
	if b.statuses[s]["dur"] <= 0:
		b.statuses.erase(s)

func _retarget_offense(b: Battler, targets: Array, side_if_missing: int) -> Array:
	var out = []
	var foe_side = 1 if b.side == 0 else 0
	for tid in targets:
		var t: Battler = battlers.get(tid)
		if t != null and t.targetable() and t.side == foe_side:
			out.append(t)
	if out.is_empty():
		var cands = targetable_list(foe_side)
		if not cands.is_empty():
			cands.sort_custom(func(x, y): return x.id < y.id)
			out.append(cands[0])
			log.append({"tick": tick, "actor": b.id, "retarget": cands[0].id})
	return out

func _retarget_heal(b: Battler, targets: Array) -> Array:
	var out = []
	for tid in targets:
		var t: Battler = battlers.get(tid)
		if t != null and t.alive():
			out.append(t)
	if out.is_empty():
		var cands = living(b.side)
		if not cands.is_empty():
			cands.sort_custom(func(x, y): return float(x.hp) / x.mhp < float(y.hp) / y.mhp)
			out.append(cands[0])
			log.append({"tick": tick, "actor": b.id, "retarget": cands[0].id})
	return out

func _resolve_targets(b: Battler, a: Dictionary, act: Dictionary) -> Array:
	var mode_t: String = a.get("target", "enemy_one")
	var foe = 1 if b.side == 0 else 0
	match mode_t:
		"enemy_one":
			if act.get("hostile_heal", false):
				return _retarget_offense(b, act.get("targets", []), foe)
			return _retarget_offense(b, act.get("targets", []), foe)
		"enemy_all":
			return targetable_list(foe)
		"ally_one":
			if a.get("revive", false):
				var out = []
				for tid in act.get("targets", []):
					var t: Battler = battlers.get(tid)
					if t != null and not t.alive():
						out.append(t)
				return out
			return _retarget_heal(b, act.get("targets", []))
		"ally_all":
			if a.get("revive", false):
				return (party_ids if b.side == 0 else enemy_ids).map(func(x): return battlers[x])
			return living(b.side)
		"self":
			return [b]
	return []

func _run_ability(b: Battler, a: Dictionary, act: Dictionary, ctx: Dictionary) -> void:
	var targets = _resolve_targets(b, a, act)
	var kind: String = a.get("kind", "utility")
	ctx["physical_action"] = kind == "physical"
	if a.get("revive", false) and targets.is_empty():
		_refund(act)
		ctx["ev"]["msgs"].append("No one to revive.")
		return
	# Overcast applies to elemental spells
	var oc = b.overcast and a.get("elemental_spell", false)
	if oc:
		ctx["overcast"] = true
		b.overcast = false
	if a.get("hostile_heal", false) or (act.get("hostile_heal", false)):
		pass
	for op in a.get("ops", []):
		var o: Dictionary = op
		if oc and o["op"] == "damage":
			o = o.duplicate()
			o["power"] = float(o["power"]) * 1.4
		var tl = targets
		if o.get("to", "") == "self":
			tl = [b]
		elif o.get("to", "") == "allies":
			tl = living(b.side)
		elif o.get("to", "") == "allies_except_self":
			tl = living(b.side).filter(func(x): return x != b)
		elif o.get("to", "") == "enemies":
			tl = targetable_list(1 if b.side == 0 else 0)
		elif o.get("to", "") == "lowest_ally":
			var lst = living(b.side).filter(func(x): return x != b)
			lst.sort_custom(func(x, y): return float(x.hp) / x.mhp < float(y.hp) / y.mhp)
			tl = [b] + (lst.slice(0, 1) if not lst.is_empty() else [])
		if o.get("per_battle", false):
			pass
		if o["op"] in ["once_per_battle"]:
			b.once[a["id"]] = true
			continue
		for t in tl:
			_apply_op(b, t, o, ctx)
	if ctx.get("set_open_hand", false):
		b.once["open_hand_guard"] = true
	if oc:
		var cost = int(floor(b.mhp * (0.05 if b.passives.has("overcast_5") else 0.08)))
		b.hp = maxi(1, b.hp - cost)
		ctx["ev"]["results"].append({"id": b.id, "kind": "selfcost", "amount": cost})
	if kind in ["magical"] and a.get("elemental_spell", false):
		b.heat_ready = true
	if a.get("concord", true):
		_gain_concord(b, 6)

func _gain_concord(b: Battler, amount: int) -> void:
	if b.side != 0:
		return
	var bonus = int(b.passives.get("concord_bonus", 0))
	concord = mini(100, concord + mini(10, amount + bonus))

func _run_item(b: Battler, it: Dictionary, act: Dictionary, ctx: Dictionary) -> void:
	var tmode: String = it.get("target", "ally_one")
	var targets = []
	var fake = {"target": tmode, "revive": it.get("revive", false)}
	targets = _resolve_targets(b, fake, act)
	if it.get("revive", false) and targets.is_empty():
		_refund_item(act, it)
		ctx["ev"]["msgs"].append("No one to revive.")
		return
	for op in it.get("ops", []):
		for t in targets:
			var o: Dictionary = op.duplicate()
			o["item"] = true
			_apply_op(b, t, o, ctx)

func _refund_item(act: Dictionary, it: Dictionary) -> void:
	inventory[it["id"]] = int(inventory.get(it["id"], 0)) + 1

func _infusion_attack_rider(b: Battler, tgts: Array, ctx: Dictionary) -> void:
	var e: String = b.infusion["elem"]
	for t in tgts:
		if not t.alive():
			continue
		if e == "fire":
			_apply_op(b, t, {"op": "status", "id": "burn", "chance": 25}, ctx)
		elif e == "ice":
			_apply_op(b, t, {"op": "status", "id": "slow", "chance": 25}, ctx)

func _resolve_enemy(b: Battler, act: Dictionary, ctx: Dictionary) -> void:
	var d = _enemy_def(b)
	var mv: Dictionary = d.get("moves", {}).get(act["move"], {"name": "Attack", "ops": [{"op": "damage", "power": 100, "type": "physical"}]})
	ctx["ev"]["name"] = mv.get("name", "Attack")
	ctx["ev"]["anim"] = mv.get("anim", "attack")
	ctx["ev"]["element"] = mv.get("element", "physical")
	ctx["enemy_action"] = true
	ctx["physical_action"] = true
	var targets = []
	var rule: String = mv.get("target", "random")
	if rule == "all":
		targets = targetable_list(0)
	elif rule in ["self"]:
		targets = [b]
	elif rule in ["ally_lowest", "ally_random", "allies"]:
		if rule == "allies":
			targets = living(1)
		else:
			for tid in act["targets"]:
				if battlers[tid].alive():
					targets.append(battlers[tid])
			if targets.is_empty():
				targets = [b]
	elif rule in ["row_front", "row_back"]:
		for tid in act["targets"]:
			if battlers[tid].targetable():
				targets.append(battlers[tid])
		if targets.is_empty():
			targets = targetable_list(0)
	else:
		targets = _retarget_offense(b, act["targets"], 0)
		# decoy draws single-target attacks
		if not decoy.is_empty() and targets.size() == 1 and mv.get("single", true):
			decoy["draws"] -= 1
			decoy["hp"] -= 1
			ctx["ev"]["results"].append({"id": "DECOY", "kind": "decoy"})
			ctx["ev"]["msgs"].append("The decoy frame takes the hit.")
			if decoy["draws"] <= 0:
				decoy = {}
			return
	if not targets.is_empty():
		b.ai["last_target"] = targets[0].id
	var power_mult = 1.0
	if mv.get("weakened_by_part", "") != "" and b.part_hit:
		power_mult = 0.5
		ctx["ev"]["msgs"].append("The strike is weakened!")
	if mv.get("weaker_if_hit", false) and b.hits_taken > 0:
		power_mult = 0.5
	for op in mv.get("ops", []):
		var o: Dictionary = op.duplicate()
		if o["op"] == "damage":
			o["power"] = float(o["power"]) * power_mult
			if b.copy_element != "" and o.get("copy", false):
				o["element"] = b.copy_element
		var tl = targets
		if o.get("to", "") == "self":
			tl = [b]
		elif o.get("to", "") == "allies":
			tl = living(1)
		for t in tl:
			_apply_op(b, t, o, ctx)
	b.hits_taken = 0
	_blue_observe(b, act["move"], targets)

# ======================================================================
# Operation handlers
# ======================================================================
func _aff_category(t: Battler, elem: String) -> String:
	var cat: String = t.aff.get(elem, "neutral")
	if t.resist_mods.has(elem):
		var m: float = t.resist_mods[elem]["mult"]
		if cat == "neutral" or cat == "weak":
			cat = "resist" if m <= 0.5 else "resist75"
	if t.side == 0:
		var imm = t.passives.get("elem_resist", {})
		if typeof(imm) == TYPE_DICTIONARY and imm.has(elem):
			cat = "resist"
	return cat

func _apply_op(src: Battler, t: Battler, op: Dictionary, ctx: Dictionary) -> void:
	var ev: Dictionary = ctx["ev"]
	match op["op"]:
		"damage":
			if not t.alive():
				return
			if src.side == 0 and t.side == 1 and t.state == "CASTING":
				t.part_hit = true
			if not t.part_of.is_empty() and t.side == 1:
				var parent: Battler = battlers.get(t.part_of)
				if parent != null:
					parent.part_hit = true
			_do_damage(src, t, op, ctx)
		"heal":
			if not t.alive():
				return
			if t.tags.has("undead") and t.side != src.side:
				var o2 = op.duplicate()
				o2["type"] = "magical"
				o2["element"] = "light"
				_do_damage(src, t, o2, ctx)
				return
			var amt = 0
			if op.has("flat"):
				amt = int(op["flat"])
			elif op.has("pct"):
				amt = int(floor(t.mhp * float(op["pct"])))
			else:
				amt = F.heal_amount(src.matk, src.level, float(op.get("power", 100)), t.mhp)
				if src.passives.has("heal_mult"):
					amt = int(floor(amt * float(src.passives["heal_mult"])))
			amt = mini(amt, t.mhp - t.hp)
			t.hp += amt
			ev["results"].append({"id": t.id, "kind": "heal", "amount": amt})
		"mp":
			if not t.alive():
				return
			var m = mini(int(op["amount"]), t.mmp - t.mp)
			t.mp += m
			ev["results"].append({"id": t.id, "kind": "mp", "amount": m})
		"full_restore":
			if not t.alive():
				return
			var hh = t.mhp - t.hp
			t.hp = t.mhp
			t.mp = t.mmp
			ev["results"].append({"id": t.id, "kind": "heal", "amount": hh})
		"revive":
			if t.alive():
				return
			t.state = "FILLING"
			t.atb = 0.0
			t.statuses = {}
			t.hp = maxi(1, int(floor(t.mhp * float(op.get("pct", 0.25)))))
			ev["results"].append({"id": t.id, "kind": "revive", "amount": t.hp})
		"status":
			if not t.alive():
				return
			_try_status(src, t, op, ctx)
		"cleanse":
			var removed = []
			for s in op.get("ids", []):
				if t.statuses.has(s):
					t.statuses.erase(s)
					removed.append(s)
			if not removed.is_empty():
				ev["results"].append({"id": t.id, "kind": "status-", "status": ",".join(removed)})
		"dispel_positive":
			var n = int(op.get("count", 99))
			var removed2 = []
			for s in REMOVABLE_POS:
				if n <= 0:
					break
				if t.statuses.has(s):
					if t.side == 0 and t.passives.has("dispel_ward") and not t.dispel_ward_used:
						t.dispel_ward_used = true
						ev["msgs"].append("Broken Diadem wards off the dispel.")
						break
					t.statuses.erase(s)
					removed2.append(s)
					n -= 1
			if not removed2.is_empty():
				ev["results"].append({"id": t.id, "kind": "status-", "status": ",".join(removed2)})
			elif op.get("else_damage", 0) > 0:
				var el: String = src.infusion.get("elem", "light") if not src.infusion.is_empty() else "light"
				_do_damage(src, t, {"op": "damage", "power": op["else_damage"], "type": "magical", "element": el}, ctx)
		"atb":
			if not t.alive():
				return
			var amt2 = float(op["amount"])
			if t.is_boss() and amt2 < 0:
				var used: float = t.extra.get("delay_since_action", 0.0)
				var allowed = maxf(0.0, 200.0 - used)
				amt2 = -minf(-amt2, allowed)
				t.extra["delay_since_action"] = used - amt2
			if t.state == "FILLING":
				t.atb = clampf(t.atb + amt2, 0.0, F.ATB_MAX - 1.0)
			ev["results"].append({"id": t.id, "kind": "atb", "amount": amt2})
		"oath":
			t.oath = op["oath"]
			ev["results"].append({"id": t.id, "kind": "oath", "status": op["oath"]})
		"arm_overcast":
			t.overcast = true
			ev["results"].append({"id": t.id, "kind": "status+", "status": "overcast"})
		"heat_exchange":
			var cost = maxi(1, int(floor(t.hp * 0.15)))
			cost = mini(cost, t.hp - 1)
			t.hp -= cost
			t.mp = mini(t.mmp, t.mp + 20)
			t.heat_uses += 1
			t.heat_ready = false
			ev["results"].append({"id": t.id, "kind": "selfcost", "amount": cost})
			ev["results"].append({"id": t.id, "kind": "mp", "amount": 20})
		"leap":
			pass
		"ground":
			if t.tags.has("flying"):
				if t.is_boss():
					ev["msgs"].append("%s resists grounding." % t.name)
				else:
					t.grounded = int(op.get("dur", 2))
					ev["results"].append({"id": t.id, "kind": "status+", "status": "grounded"})
		"mine":
			t.mine = {"power": float(op.get("power", 170)), "owner": src.id}
			ev["results"].append({"id": t.id, "kind": "status+", "status": "mine"})
		"decoy":
			decoy = {"hp": int(src.mhp * 0.25), "draws": 2, "owner": src.id}
			ev["results"].append({"id": src.id, "kind": "status+", "status": "decoy"})
		"steal":
			_do_steal(src, t, ctx)
		"protect":
			t.protect = 1
			t.extra["protect_dur"] = 3
			ev["results"].append({"id": t.id, "kind": "status+", "status": "protected"})
		"lethal_guard":
			if not src.once.has("open_hand_guard"):
				t.lethal_guard = true
				ctx["set_open_hand"] = true
		"bramble":
			t.extra["bramble"] = true
		"flee":
			if can_flee:
				flee_meter += int(op["amount"])
				ev["msgs"].append("Escape %d%%" % mini(100, flee_meter / 10))
				if flee_meter >= 1000:
					result = "fled"
			elif op.has("else_evasion"):
				t.evasion = {"pct": float(op["else_evasion"]), "count": 1}
		"evasion":
			t.evasion = {"pct": float(op["pct"]), "count": int(op.get("count", 1))}
		"infuse":
			var dur = int(op.get("dur", 4)) + (2 if t.passives.has("infusion_plus2") else 0)
			t.infusion = {"elem": op["elem"], "dur": dur}
			ev["results"].append({"id": t.id, "kind": "status+", "status": "infuse_" + op["elem"]})
		"resist":
			var cur = t.resist_mods.get(op["elem"], {"mult": 1.0})
			if float(op["mult"]) <= float(cur["mult"]):
				t.resist_mods[op["elem"]] = {"mult": float(op["mult"]), "dur": int(op.get("dur", 3))}
			ev["results"].append({"id": t.id, "kind": "status+", "status": op["elem"] + " ward"})
		"reveal":
			ev["results"].append({"id": t.id, "kind": "reveal", "what": op.get("what", "affinity")})
			_push_to(ev, "reveal", {"id": t.ref, "what": op.get("what", "affinity")})
			if op.get("what", "") == "scan":
				# Libra (systems s2): read the target aloud; the bestiary entry fills in battle_scene
				var wk = []
				for el in t.aff:
					if t.aff[el] == "weak":
						wk.append(str(el).capitalize())
				ev["msgs"].append("%s  Lv %d  HP %d/%d" % [t.name, t.level, t.hp, t.mhp])
				ev["msgs"].append("Weak: %s" % (", ".join(wk) if not wk.is_empty() else "nothing"))
		"scan_foe":
			# an enemy that reads the party (systems s2): a message, no effect
			ev["msgs"].append("%s scans %s: HP %d/%d." % [src.name, t.name, t.hp, t.mhp])
		"omen":
			var nm = next_scheduled_move(t)
			var mv: Dictionary = _enemy_def(t).get("moves", {}).get(nm, {})
			var txt: String = mv.get("name", nm)
			if not t.intent.is_empty():
				var tn = []
				for x in t.intent["targets"]:
					tn.append(battlers[x].name)
				txt = "%s → %s" % [t.intent["name"], ", ".join(tn)]
			ev["msgs"].append("%s: %s" % [t.name, txt])
			if not t.extra.get("omen_cycle", false):
				t.extra["omen_cycle"] = true
				_apply_op(src, t, {"op": "atb", "amount": -100}, ctx)
		"mirror":
			t.mirror_charge = true
		"feather":
			t.feather = true
			ev["results"].append({"id": t.id, "kind": "status+", "status": "feather"})
		"quick_hands":
			t.quick_hands = true
		"witness":
			t.oath = "witness"
			ev["results"].append({"id": t.id, "kind": "oath", "status": "witness"})
		"status_ward":
			t.status_ward = 1
		"row_back":
			t.row = "back"
		"remove_hard":
			for s in ["sleep", "stun"]:
				if t.statuses.has(s):
					t.statuses.erase(s)
					break
		"cancel_charge":
			if t.state == "CASTING" and not t.is_boss():
				t.state = "FILLING"
				t.atb = 0.0
				t.intent = {}
				t.pending = {}
				ev["msgs"].append("%s's charge is cancelled." % t.name)
		"concord":
			concord = mini(100, concord + int(op["amount"]))
		"steal_gold":
			var g = mini(10, 10)
			gold_stolen += g
			ev["msgs"].append("%s pockets %d crowns (returned on victory)." % [src.name, g])
		"drain":
			pass
		"split":
			pass
		"copy_element":
			pass
		"buff_ally":
			if not t.extra.get("empowered", false):
				t.extra["empowered"] = true
				ev["results"].append({"id": t.id, "kind": "status+", "status": "empowered"})
		"self_hp":
			# Inferna: pay a share of max HP (never lethal)
			var cost = mini(int(src.mhp * float(op.get("pct", 0.1))), src.hp - 1)
			if cost > 0:
				src.hp -= cost
				ev["results"].append({"id": src.id, "kind": "damage", "amount": cost})
		"guard_self":
			t.defending = true
			t.extra["shell"] = float(op.get("mult", 0.5))
			ev["results"].append({"id": t.id, "kind": "status+", "status": op.get("label", "guard")})
		"mp_drain":
			var md = mini(int(op.get("amount", 15)), t.mp)
			t.mp -= md
			ev["results"].append({"id": t.id, "kind": "mp", "amount": -md})
		"summon_part":
			pass
		"once_per_battle":
			pass
		"wingbeat":
			src.once["wingbeat_cycle"] = true
		"capture":
			_do_capture(src, t, ctx)
		"msg":
			ev["msgs"].append(op["text"])
		_:
			push_error("Unknown op " + str(op["op"]))

func _try_status(src: Battler, t: Battler, op: Dictionary, ctx: Dictionary) -> void:
	var sid: String = op["id"]
	var ev: Dictionary = ctx["ev"]
	var chance = float(op.get("chance", 100))
	var negative: bool = content["statuses"][sid]["type"] == "negative"
	if negative and t.side == 0:
		var imm = t.passives.get("immune", [])
		if imm.has(sid) or (t.oath == "witness" and sid in ["silence", "blind"]):
			ev["results"].append({"id": t.id, "kind": "immune", "status": sid})
			return
		if t.status_ward > 0:
			t.status_ward = 0
			ev["results"].append({"id": t.id, "kind": "immune", "status": sid})
			return
	if t.is_boss() and sid in ["sleep", "stun", "doom"]:
		ev["results"].append({"id": t.id, "kind": "immune", "status": sid})
		return
	if t.side == 1 and content["enemies"][t.ref].get("status_immune", []).has(sid):
		ev["results"].append({"id": t.id, "kind": "immune", "status": sid})
		return
	if negative and not rng.chance(chance):
		ev["results"].append({"id": t.id, "kind": "resist", "status": sid})
		return
	# reapplication cannot extend stun until target acted
	if sid == "stun" and t.statuses.has("stun"):
		return
	if sid == "sleep" and t.statuses.has("sleep"):
		return
	var dur = int(op.get("dur", content["statuses"][sid]["duration"]))
	if sid == "mark" and src.passives.has("mark_plus1"):
		dur += 1
	if sid == "haste":
		t.statuses.erase("slow")
	if sid == "slow":
		t.statuses.erase("haste")
	var cur = t.statuses.get(sid, {"dur": 0})
	t.statuses[sid] = {"dur": maxi(int(cur["dur"]), dur)}
	ev["results"].append({"id": t.id, "kind": "status+", "status": sid})

func _do_damage(src: Battler, t: Battler, op: Dictionary, ctx: Dictionary) -> void:
	var ev: Dictionary = ctx["ev"]
	var typ: String = op.get("type", "physical")
	var elem: String = op.get("element", "physical" if typ == "physical" else "none")
	var physical = typ == "physical"
	var ranged = bool(op.get("ranged", false)) or (physical and src.ranged and not op.get("melee", false) and op.get("weapon_ranged", true))
	# accuracy
	if physical and not op.get("item", false):
		var acc = 95.0 + src.acc_bonus + (10.0 if src.has("focus") else 0.0)
		if src.has("blind"):
			acc = maxf(50.0, acc - 25.0)
		acc = minf(acc, 100.0)
		if t.side == 1 and content["enemies"][t.ref].get("melee_dodge", 0) > 0 and not ranged:
			acc -= float(content["enemies"][t.ref]["melee_dodge"])
		if src.side == 1:
			acc -= float(content["enemies"][src.ref].get("acc_penalty", 0))
		if not t.evasion.is_empty():
			acc -= float(t.evasion["pct"])
			t.evasion["count"] -= 1
			if t.evasion["count"] <= 0:
				t.evasion = {}
		if not rng.chance(acc):
			ev["results"].append({"id": t.id, "kind": "miss"})
			return
	var level = src.level
	var stat = src.atk if physical else src.matk
	if op.has("fixed_mag"):
		stat = float(op["fixed_mag"])
		level = 1 if op.get("item", false) else src.level
	if src.has("weaken"):
		stat *= 0.85
	if src.extra.get("empowered", false):
		stat *= 1.10
	var raw = F.physical_raw(stat, level, float(op["power"])) if physical else F.magical_raw(stat, level, float(op["power"]))
	# defense
	var dv = t.def if physical else t.res
	if t.has("guardbreak") and physical:
		dv *= 0.8
	if op.has("ignore_def"):
		dv *= (1.0 - float(op["ignore_def"]))
	if src.infusion.get("elem", "") == "storm" and op.get("infused", false):
		dv *= 0.85
	var dmg = raw * F.defense_mult(dv)
	# affinity
	var cat = _aff_category(t, elem)
	if elem == "earth" and t.tags.has("flying") and t.grounded <= 0 and cat == "neutral":
		cat = "resist"
	if cat == "immune":
		ev["results"].append({"id": t.id, "kind": "immune"})
		return
	if cat == "absorb":
		var h = mini(int(floor(dmg)), t.mhp - t.hp)
		t.hp += h
		ev["results"].append({"id": t.id, "kind": "absorb", "amount": h})
		return
	if cat == "resist75":
		dmg *= 0.75
	else:
		dmg *= F.AFF_MULT.get(cat, 1.0)
	# rows (melee physical only)
	if physical and not ranged:
		if src.row == "back":
			dmg *= 0.5
		if t.row == "back":
			dmg *= 0.5
	# dealt modifiers
	if physical and src.oath == "shelter":
		dmg *= 0.9
	if physical and src.oath == "wrath":
		dmg *= 1.2
	if physical and src.has("burn"):
		dmg *= 0.9
	if physical and src.two_handed and src.passives.has("twohand_mult"):
		dmg *= float(src.passives["twohand_mult"])
	for k in op.get("bonus_vs", {}):
		if t.has(k):
			dmg *= float(op["bonus_vs"][k])
			if op.get("bonus_once", true):
				break
	# received modifiers
	var red = []
	if t.defending:
		red.append(float(t.extra.get("shell", 0.5)))
	if t.has("barrier"):
		red.append(0.75)
	if t.feather:
		red.append(0.4)
		t.feather = false
	if physical and t.passives.has("phys_reduce"):
		red.append(1.0 - float(t.passives["phys_reduce"]))
	if t.side == 0 and t.passives.has("lowhp_guard") and t.mhp > 0 and float(t.hp) / t.mhp < 0.4:
		red.append(1.0 - float(t.passives["lowhp_guard"]))
	if not physical and t.mirror_charge:
		red.append(0.7)
		t.mirror_charge = false
	if t.extra.get("oath_protect_bonus", false) and t.oath != "":
		pass
	dmg *= F.combine_reductions(red)
	if physical and t.has("mark"):
		dmg *= 1.10
	if physical and t.oath == "wrath":
		dmg *= 1.15
	# variance and crit
	dmg *= 0.95 + rng.randf() * 0.10
	var crit = false
	if physical and not op.get("no_crit", false) and not op.get("item", false):
		var cc = 5.0 + (5.0 if src.has("focus") else 0.0)
		cc = minf(cc, 35.0)
		if rng.chance(cc):
			crit = true
			dmg *= 1.5
	var amount = maxi(1, int(floor(dmg)))
	amount = mini(amount, damage_cap(src, op))
	if t.tags.has("part"):
		amount = mini(amount, t.hp - 1)
		if amount <= 0:
			ev["results"].append({"id": t.id, "kind": "damage", "amount": 0, "part": true})
			return
	# Dain: Shelter interception / Sacrifice transfer (party only)
	if t.side == 0 and src.side == 1 and not op.get("reaction", false):
		amount = _dain_reactions(t, amount, ctx, op)
	# lethal protection
	if t.side == 0 and amount >= t.hp:
		if t.protect > 0:
			t.protect = 0
			amount = t.hp - 1
			ev["msgs"].append("%s is protected." % t.name)
		elif t.lethal_guard:
			t.lethal_guard = false
			amount = t.hp - 1
			ev["msgs"].append("Open Hand holds %s up." % t.name)
	if amount <= 0:
		ev["results"].append({"id": t.id, "kind": "damage", "amount": 0})
		return
	t.hp = maxi(0, t.hp - amount)
	t.hits_taken += 1
	_limit_fill(src, t, amount)
	if op.get("drain", false) and src.alive():
		var dfrac = float(op["drain"]) if typeof(op["drain"]) in [TYPE_FLOAT, TYPE_INT] and float(op["drain"]) < 1.0 else 1.0
		var dr = mini(int(amount * dfrac), src.mhp - src.hp)
		src.hp += dr
		ev["results"].append({"id": src.id, "kind": "heal", "amount": dr})
	if t.side == 1 and not physical and content["enemies"][t.ref].get("copy_element", false) and elem != "none":
		t.copy_element = elem
	var r = {"id": t.id, "kind": "damage", "amount": amount, "crit": crit, "element": elem}
	if cat == "weak":
		r["weak"] = true
	if cat == "resist":
		r["resisted"] = true
	ev["results"].append(r)
	if t.has("sleep"):
		t.statuses.erase("sleep")
	if t.side == 1 and cat == "weak":
		_push_to(ev, "reveal", {"id": t.ref, "what": "weak:" + elem})
	# interrupt interruptible charges
	if t.side == 1 and t.state == "CASTING" and not t.pending.is_empty():
		var mv: Dictionary = _enemy_def(t).get("moves", {}).get(t.pending.get("move", ""), {})
		if mv.get("interruptible", false):
			t.state = "FILLING"
			t.atb = 0.0
			t.pending = {}
			t.intent = {}
			ev["msgs"].append("%s's charge is interrupted!" % t.name)
	if t.side == 0 and t.hp > 0 and t.passives.has("mercy_barrier") and not t.mercy_used and float(t.hp) / t.mhp < 0.3:
		t.mercy_used = true
		t.statuses["barrier"] = {"dur": 3}
		ev["results"].append({"id": t.id, "kind": "status+", "status": "barrier"})
	if t.hp == 0 and t.side == 0 and t.passives.has("auto_revive") and not t.once.has("auto_revive"):
		# Returner's Cord: once per battle a fatal blow leaves 1 HP
		t.once["auto_revive"] = true
		t.hp = 1
		ev["msgs"].append("%s holds on!" % t.name)
	if t.hp == 0:
		_ko(t, ctx)
	else:
		# reactions: counters and reflection (never recursive)
		if not op.get("reaction", false) and ctx["depth"] == 0:
			if t.side == 0 and physical and src.side == 1 and t.passives.has("counter"):
				var rk: String = "counter_" + t.id
				if not ctx["reactions"].has(rk):
					ctx["reactions"][rk] = true
					ctx["depth"] = 1
					_do_damage(t, src, {"op": "damage", "power": 50, "type": "physical", "reaction": true}, ctx)
					ctx["depth"] = 0
					ev["msgs"].append("%s counters!" % t.name)
			if t.side == 0 and physical and src.side == 1 and t.extra.get("bramble", false) and t.has("barrier"):
				var rk2: String = "reflect_" + t.id
				if not ctx["reactions"].has(rk2):
					ctx["reactions"][rk2] = true
					var refl = maxi(1, int(floor(amount * 0.15)))
					src.hp = maxi(0, src.hp - refl)
					ev["results"].append({"id": src.id, "kind": "damage", "amount": refl, "reflect": true})
					if src.hp == 0:
						_ko(src, ctx)
		if t.side == 0 and src.side == 1:
			for pid in party_ids:
				var p: Battler = battlers[pid]
				if p.alive() and p.oath == "witness" and p != t:
					p.witness_charge = true
		# enemy split below 50%
		if t.side == 1 and content["enemies"][t.ref].get("split", false) and not t.split_done and t.hp * 2 < t.mhp:
			t.split_done = true
			_push_to(ctx, "splits", t.id)

func _dain_reactions(t: Battler, amount: int, ctx: Dictionary, op: Dictionary) -> int:
	var single = ctx["act"].get("targets", []).size() <= 1 and op.get("aoe", false) == false
	for pid in party_ids:
		var d: Battler = battlers[pid]
		if d == t or not d.alive():
			continue
		if d.oath == "shelter" and single and not ctx["reactions"].has("shelter") and float(t.hp) / t.mhp < 0.35:
			ctx["reactions"]["shelter"] = true
			var take = int(floor(amount * 0.5))
			var red = 0.5
			if d.passives.has("oath_guard_10"):
				red = 0.4
			var taken = int(floor(take * (red / 0.5)))
			d.hp = maxi(0, d.hp - taken)
			ctx["ev"]["results"].append({"id": d.id, "kind": "damage", "amount": taken, "intercept": true})
			ctx["ev"]["msgs"].append("%s intercepts!" % d.name)
			if d.hp == 0:
				_ko(d, ctx)
			return 0
		if d.oath == "sacrifice" and not ctx["reactions"].has("sacrifice_" + t.id):
			ctx["reactions"]["sacrifice_" + t.id] = true
			var tr = int(floor(amount * 0.25))
			tr = mini(tr, int(floor(d.mhp * 0.10)))
			tr = mini(tr, d.hp - 1)
			if tr > 0:
				d.hp -= tr
				ctx["ev"]["results"].append({"id": d.id, "kind": "damage", "amount": tr, "transfer": true})
				return amount - tr
	return amount

func _ko(t: Battler, ctx: Dictionary) -> void:
	if t.state == "KO":
		return
	if t.side == 0:
		party_kos += 1
	t.hp = 0
	t.state = "KO"
	t.statuses = {}
	t.atb = 0.0
	t.oath = ""
	t.overcast = false
	t.infusion = {}
	t.intent = {}
	ready_order.erase(t.id)
	if not t.pending.is_empty():
		var act = t.pending
		t.pending = {}
		if queue.has(act):
			queue.erase(act)
		_refund(act)
	ctx["ev"]["results"].append({"id": t.id, "kind": "ko"})
	if t.side == 1 and decoy.get("owner", "") == "":
		pass

func _do_steal(src: Battler, t: Battler, ctx: Dictionary) -> void:
	var ev: Dictionary = ctx["ev"]
	var st: Dictionary = t.steal_table
	if st.is_empty():
		ev["msgs"].append("Nothing to steal.")
		return
	if not t.steal["common_taken"]:
		var ok = rng.chance(70) or t.steal["fails"] >= 3
		if ok and st.has("common"):
			t.steal["common_taken"] = true
			stolen_items.append(st["common"])
			_push_to(ev, "steals", st["common"])
			ev["msgs"].append("Stole %s!" % content["items"][st["common"]]["name"])
			if src.passives.has("pilfer_refund") and not src.once.has("pilfer_cycle"):
				src.once["pilfer_cycle"] = true
				ctx["atb_refund"] = 150
		else:
			t.steal["fails"] += 1
			ev["msgs"].append("Missed the steal.")
	elif not t.steal["rare_taken"] and st.has("rare"):
		if rng.chance(10):
			t.steal["rare_taken"] = true
			stolen_items.append(st["rare"])
			_push_to(ev, "steals", st["rare"])
			ev["msgs"].append("Stole %s!" % content["items"][st["rare"]]["name"])
		else:
			ev["msgs"].append("Missed the steal.")
	else:
		ev["msgs"].append("Nothing left to steal.")

func _check_phase_and_split(ctx: Dictionary) -> void:
	for sid in ctx.get("splits", []):
		var t: Battler = battlers[sid]
		var child = add_enemy(t.ref, enemy_ids.size() + 1)
		child.split_done = true
		child.mhp = maxi(1, int(t.mhp / 2))
		child.hp = child.mhp
		child.drops = []
		child.steal_table = {}
		child.xp = int(t.xp / 2)
		_push_to(ctx["ev"], "spawns", child.id)
		ctx["ev"]["msgs"].append("%s splits!" % t.name)
	for eid in enemy_ids:
		var e: Battler = battlers[eid]
		if not e.alive() or not e.is_boss():
			continue
		var d = _enemy_def(e)
		if not d.has("phases"):
			continue
		var ph: Array = d["phases"]
		var pct = 100.0 * e.hp / e.mhp
		var target_phase: int = e.ai["phase"]
		for i in range(ph.size()):
			if pct <= float(ph[i]["at"]) and i > target_phase:
				target_phase = i
		if target_phase > e.ai["phase"] and not phase_queue.has([e.id, target_phase]):
			phase_queue.append([e.id, target_phase])

func _run_phase_transition(item: Array) -> void:
	var e: Battler = battlers[item[0]]
	var ph: int = item[1]
	if ph <= e.ai["phase"] or not e.alive():
		return
	e.ai["phase"] = ph
	e.ai["idx"] = 0
	var d = _enemy_def(e)
	var pdef: Dictionary = d["phases"][ph]
	var ev = {"type": "phase", "actor": e.id, "phase": ph, "text": pdef.get("enter", ""), "results": [], "msgs": []}
	for aff_k in pdef.get("affinities", {}):
		e.aff[aff_k] = pdef["affinities"][aff_k]
	for sp in pdef.get("spawn", []):
		var nb = add_enemy(sp, enemy_ids.size() + 1)
		ev["results"].append({"id": nb.id, "kind": "spawn"})
	_push_event(ev)

func _check_end() -> void:
	if result != "":
		return
	var party_up = false
	for pid in party_ids:
		var p: Battler = battlers[pid]
		if p.alive():
			party_up = true
	var foes_up = false
	for eid in enemy_ids:
		var e: Battler = battlers[eid]
		if e.alive() and not e.tags.has("part"):
			foes_up = true
	if not party_up:
		result = "defeat"   # defeat takes precedence over simultaneous enemy wipe
	elif not foes_up:
		result = "victory"

func _push_event(ev: Dictionary) -> void:
	events.append(ev)
	locked = true

## Presenter acknowledges the oldest event (or tests call it immediately).
func ack() -> void:
	if not events.is_empty():
		events.pop_front()
	locked = not events.is_empty()

# ======================================================================
# Rewards (computed once; applied by the campaign transaction)
# ======================================================================
func rewards() -> Dictionary:
	var xp = 0
	var gold = gold_stolen
	var drops = []
	for eid in enemy_ids:
		var e: Battler = battlers[eid]
		if e.tags.has("part"):
			continue
		xp += e.xp
		gold += e.gold
		for dr in e.drops:
			if loot_rng.chance(float(dr.get("chance", 0))):
				drops.append(dr["item"])
	return {"xp": xp, "gold": gold, "drops": drops}

## Party end-state for writing back to the campaign.
func party_end_state() -> Array:
	var out = []
	for pid in party_ids + reserve_ids:
		var b: Battler = battlers[pid]
		out.append({"cid": b.ref, "hp": b.hp, "mp": b.mp, "row": b.row, "limit": b.limit, "limit_used": b.limit_used.duplicate(),
			"active": party_ids.has(pid)})
	return out

## Hash of the authoritative state (for determinism tests).
func state_hash() -> String:
	var parts = [tick, concord, flee_meter, result]
	for bid in party_ids + enemy_ids:
		var b: Battler = battlers[bid]
		parts.append([b.id, b.hp, b.mp, int(b.atb), b.state, b.statuses.keys()])
	return str(parts).md5_text()

## Run until the next point needing input or the end (headless helper).
func run_until_input(max_ticks: int = 100000) -> Battler:
	var n = 0
	while n < max_ticks:
		while locked:
			ack()
		if result != "":
			return null
		var w = awaiting_input()
		if w != null:
			return w
		step()
		n += 1
	return null

# ======================================================================
# Expansion battle systems (branch s1): damage cap, limit gauge, party swap, blue magic, capture
# ======================================================================
## 9,999 per hit; `uncapped` ops and heroes with the break_damage passive go to 99,999.
func damage_cap(src: Battler, op: Dictionary) -> int:
	if op.get("uncapped", false) or (src != null and src.side == 0 and src.passives.has("break_damage")):
		return F.DAMAGE_BREAK_CAP
	return F.DAMAGE_CAP

## Gauge fills from damage taken (share of max HP) and dealt (per hit); only heroes with limits have a gauge.
func _limit_fill(src: Battler, t: Battler, amount: int) -> void:
	var cfg: Dictionary = content.get("limits", {})
	if t.side == 0 and not t.limits.is_empty() and t.mhp > 0 and t.alive():
		t.limit = minf(LIMIT_MAX, t.limit + float(cfg.get("fill_taken", 75.0)) * float(amount) / float(t.mhp))
	if src != null and src.side == 0 and t.side == 1 and not src.limits.is_empty() and not limit_active:
		src.limit = minf(LIMIT_MAX, src.limit + float(cfg.get("fill_dealt", 2.5)))

func limit_ready(b: Battler) -> bool:
	return b.side == 0 and not b.limits.is_empty() and b.limit >= LIMIT_MAX

func reserves_alive() -> Array:
	return reserve_ids.filter(func(x): return battlers[x].alive())

## The acting hero steps back into the reserve; the chosen reserve takes the same slot with a partly filled gauge.
func _do_swap(b: Battler, act: Dictionary, ev: Dictionary) -> void:
	var rid: String = str(act.get("reserve", ""))
	if rid == "" or not reserve_ids.has(rid) or not battlers[rid].alive():
		rid = ""
		for x in reserve_ids:
			if battlers[x].alive():
				rid = x
				break
	ev["anim"] = "step"
	if rid == "":
		ev["name"] = "Swap"
		ev["msgs"].append("No one can take the place.")
		return
	var nb: Battler = battlers[rid]
	var idx = party_ids.find(b.id)
	party_ids[idx] = rid
	reserve_ids[reserve_ids.find(rid)] = b.id
	nb.state = "FILLING"
	nb.atb = SWAP_ATB
	nb.timer = 0.0
	nb.pending = {}
	nb.defending = false
	b.defending = false
	b.oath = ""
	ev["name"] = "%s steps in" % nb.name
	ev["swap"] = {"out": b.id, "in": rid}
	ev["results"].append({"id": rid, "kind": "swap_in"})

## Blue magic: a learnable enemy move resolving near a blue mage ("see": any use; "hit": the mage was a target).
func _blue_observe(e: Battler, move: String, targets: Array) -> void:
	var src: Dictionary = content.get("blue", {}).get("src", {})
	if src.is_empty() or e.side != 1:
		return
	var bid: String = str(src.get(e.ref + ":" + move, ""))
	if bid == "":
		var base = str(_enemy_def(e).get("variant_of", ""))
		if base != "":
			bid = str(src.get(base + ":" + move, ""))
	if bid == "" or blue_new.has(bid):
		return
	for pid in party_ids:
		var p: Battler = battlers[pid]
		if p.blue_rule == "" or not p.alive() or p.blue.has(bid):
			continue
		if p.blue_rule == "see" or (p.blue_rule == "hit" and targets.has(p)):
			blue_new[bid] = p.ref
			return

## Capture (Sak): a weakened non-boss enemy leaves the battle and joins Game.S.captured; sometimes it morphs.
func _do_capture(src: Battler, t: Battler, ctx: Dictionary) -> void:
	var ev: Dictionary = ctx["ev"]
	var cfg: Dictionary = content.get("capture", {})
	if t.side != 1 or not t.alive():
		return
	if t.is_boss() or t.tags.has("part") or t.tags.has("superboss") or _enemy_def(t).get("no_capture", false):
		ev["results"].append({"id": t.id, "kind": "immune"})
		ev["msgs"].append("%s cannot be captured." % t.name)
		return
	var hf = float(cfg.get("hp_frac", 0.5))
	var frac = float(t.hp) / float(maxi(1, t.mhp))
	if frac > hf:
		ev["results"].append({"id": t.id, "kind": "resist"})
		ev["msgs"].append("%s is too strong to capture." % t.name)
		return
	var chance = minf(float(cfg.get("max", 95)), float(cfg.get("base", 35)) + (hf - frac) * float(cfg.get("slope", 120)))
	if not rng.chance(chance):
		ev["results"].append({"id": t.id, "kind": "miss"})
		ev["msgs"].append("%s slips the net." % t.name)
		return
	captured.append(t.ref)
	t.extra["captured"] = true
	var msg = "Captured %s!" % t.name
	if rng.chance(float(cfg.get("morph_chance", 25))):
		var item = ""
		for row in cfg.get("morph", []):
			if t.level >= int(row[0]):
				item = str(row[1])
		if item != "" and content["items"].has(item):
			morph_items.append(item)
			msg = "Captured %s. It morphs into %s!" % [t.name, content["items"][item]["name"]]
	ev["results"].append({"id": t.id, "kind": "capture"})
	ev["msgs"].append(msg)
	_ko(t, ctx)

static func _push_to(d: Dictionary, key: String, v) -> void:
	if not d.has(key):
		d[key] = []
	d[key].append(v)
