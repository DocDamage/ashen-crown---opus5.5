class_name F
extends RefCounted
## Shared arithmetic used by the battle model, menus/previews and tests.
## Constants are initial tuning values from docs/06 and docs/07 (not verified balance).

const ATB_MAX := 1000
const LEVEL_CAP := 50
const REDUCTION_FLOOR := 0.2  # total direct-damage reduction capped at 80%
const ELEMENTS := ["physical", "fire", "ice", "storm", "earth", "water", "light", "shadow", "none"]
const AFF_MULT := {"weak": 1.5, "neutral": 1.0, "resist": 0.5, "immune": 0.0}

static func xp_to_next(level: int) -> int:
	return 30 + 12 * level + 3 * level * level

static func xp_total_for_level(level: int) -> int:
	var t = 0
	for l in range(1, level):
		t += xp_to_next(l)
	return t

static func level_for_xp(xp: int) -> int:
	var l = 1
	while l < LEVEL_CAP and xp >= xp_total_for_level(l + 1):
		l += 1
	return l

## Readiness fill per simulation second.
static func atb_rate(spd: int, speed_factor: float, haste: bool, slow: bool, is_boss: bool) -> float:
	var r = 100.0 + 5.0 * clampi(spd, 1, 99)
	if haste:
		r *= 1.25
	if slow:
		r *= (0.90 if is_boss else 0.75)
	return r * speed_factor

static func physical_raw(atk: float, level: int, power: float) -> float:
	return (2.0 * atk + 3.0 * level) * power / 100.0

static func magical_raw(mag: float, level: int, power: float) -> float:
	return (2.0 * mag + 3.0 * level) * power / 100.0

static func defense_mult(def_value: float) -> float:
	return 100.0 / (100.0 + maxf(0.0, def_value))

static func heal_amount(mag: float, level: int, power: float, target_mhp: int) -> int:
	return maxi(1, int(floor((2.0 * mag + 2.0 * level) * power / 100.0 + 0.06 * target_mhp)))

## Combine reduction multipliers (each <= 1) and clamp to the 80% cap.
static func combine_reductions(mults: Array) -> float:
	var m = 1.0
	for x in mults:
		m *= float(x)
	return maxf(m, REDUCTION_FLOOR)

## Derived stats for a party member. `member` is save-owned state, `cdef` the character
## definition, `items` the content item table.
static func member_stats(member: Dictionary, cdef: Dictionary, items: Dictionary) -> Dictionary:
	var lv: int = int(member.get("level", 1))
	var n = lv - 1
	var b: Dictionary = cdef["base"]
	var g: Dictionary = cdef["growth"]
	var s = {
		"level": lv,
		"mhp": int(b["hp"]) + int(g["hp"]) * n + int(floor(0.65 * n * n)),
		"mmp": int(b["mp"]) + int(g["mp"]) * n,
		"str": int(b["str"]) + int(g["str"]) * n,
		"mag": int(b["mag"]) + int(g["mag"]) * n,
		"def": int(b["def"]) + n,
		"res": int(b["res"]) + n,
		"spd": int(b["spd"]) + int(n / 4),
		"atk": 0, "matk": 0, "acc_bonus": 0, "passives": {}, "grants": [], "ranged": false, "two_handed": false,
		"weapon_element": "physical",
	}
	var eq: Dictionary = member.get("equip", {})
	var passives = {}
	for slot in ["weapon", "offhand", "head", "body", "acc1", "acc2"]:
		var iid = eq.get(slot, "")
		if iid == null or iid == "" or not items.has(iid):
			continue
		var it: Dictionary = items[iid]
		s["def"] += int(it.get("def", 0))
		s["res"] += int(it.get("res", 0))
		if slot == "weapon":
			s["atk"] += int(it.get("atk", 0))
			s["matk"] += int(it.get("mag", 0))
			s["ranged"] = bool(it.get("ranged", false))
			s["two_handed"] = bool(it.get("two_handed", false))
		if it.has("grants"):
			s["grants"].append(it["grants"])
		for k in it.get("passives", {}):
			var v = it["passives"][k]
			# duplicates never stack: strongest wins
			if passives.has(k) and (typeof(v) == TYPE_FLOAT or typeof(v) == TYPE_INT):
				if k.ends_with("_reduce") or k.ends_with("_mult") or k.ends_with("_bonus"):
					passives[k] = maxf(float(passives[k]), float(v))
			elif passives.has(k) and typeof(v) == TYPE_ARRAY:
				var merged: Array = passives[k].duplicate()
				for e in v:
					if not merged.has(e):
						merged.append(e)
				passives[k] = merged
			else:
				passives[k] = v
	s["passives"] = passives
	if passives.has("mhp_mult"):
		s["mhp"] = int(floor(s["mhp"] * float(passives["mhp_mult"])))
	if passives.has("mmp_mult"):
		s["mmp"] = int(floor(s["mmp"] * float(passives["mmp_mult"])))
	s["acc_bonus"] = int(passives.get("acc_bonus", 0))
	s["atk"] += s["str"]
	s["matk"] += s["mag"]
	return s

## Level floor for an initial recruit or a returning character.
static func join_level(stored_level: int, available_levels: Array) -> int:
	if available_levels.is_empty():
		return stored_level
	var arr = available_levels.duplicate()
	arr.sort()
	var med: int
	if arr.size() % 2 == 1:
		med = int(arr[arr.size() / 2])
	else:
		med = int(floor((int(arr[arr.size() / 2 - 1]) + int(arr[arr.size() / 2])) / 2.0))
	return maxi(stored_level, med - 1)

static func inn_price(recruited_count: int) -> int:
	return mini(25 * recruited_count, 150)
