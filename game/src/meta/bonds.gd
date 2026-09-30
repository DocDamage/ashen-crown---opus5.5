class_name Bonds
extends RefCounted
## Bonds between heroes (no dual techs): pairs who fight together grow closer. A bond has levels 0-5; each level
## with a partner in the active party gives a small edge in battle, and some pairs have scenes at levels 2 and 4,
## played the next time the party rests at an inn. State: Game.S.bonds = {"C01|C02": points}.

const LEVELS := [10, 30, 60, 100, 160]
const PCT_PER_LEVEL := 0.01
const PCT_CAP := 0.08
const SCENE_LEVELS := [2, 4]

static func key(a: String, b: String) -> String:
	return a + "|" + b if a < b else b + "|" + a

static func _store() -> Dictionary:
	if not Game.S.has("bonds"):
		Game.S["bonds"] = {}
	return Game.S["bonds"]

static func points(a: String, b: String) -> int:
	return int(Game.S.get("bonds", {}).get(key(a, b), 0))

static func level_for(p: int) -> int:
	var lv = 0
	for t in LEVELS:
		if p >= t:
			lv += 1
	return lv

static func level(a: String, b: String) -> int:
	return level_for(points(a, b))

## Adds points to a pair; returns the new level when it rose, else -1.
static func gain(a: String, b: String, n: int) -> int:
	if a == b:
		return -1
	var st = _store()
	var k = key(a, b)
	var before = level_for(int(st.get(k, 0)))
	st[k] = int(st.get(k, 0)) + n
	var after = level_for(int(st[k]))
	return after if after > before else -1

## Every pair in the active party after a won battle. Returns level-up messages.
static func after_battle(party: Array) -> Array:
	var msgs = []
	for i in range(party.size()):
		for j in range(i + 1, party.size()):
			var lv = gain(party[i], party[j], 1)
			if lv > 0:
				msgs.append("%s and %s grow closer. (Bond %d)" % [Game.short_name(party[i]), Game.short_name(party[j]), lv])
	return msgs

## Battle edge for `cid` from bonded partners in the active party.
static func edge(cid: String) -> float:
	if Game.S.is_empty() or not Game.S.get("bonds", {}).size():
		return 0.0
	var act: Array = Game.S["party"]["active"]
	if not act.has(cid):
		return 0.0
	var total = 0
	for c in act:
		if c != cid:
			total += level(cid, c)
	return minf(PCT_CAP, PCT_PER_LEVEL * total)

static func apply(cid: String, st: Dictionary) -> Dictionary:
	var e = edge(cid)
	if e <= 0.0:
		return st
	for k in ["atk", "matk", "def", "res"]:
		st[k] = int(floor(st[k] * (1.0 + e)))
	return st

static func scene_id(a: String, b: String, lv: int) -> String:
	var k = key(a, b).replace("|", "_")
	return "BOND_%s_%d" % [k, lv]

## The first unseen pair scene among the active party whose bond is high enough ("" if none).
static func ready_scene() -> String:
	var act: Array = Game.active()
	for i in range(act.size()):
		for j in range(i + 1, act.size()):
			var lv = level(act[i], act[j])
			for s in SCENE_LEVELS:
				if lv >= s:
					var id = scene_id(act[i], act[j], s)
					if not Content.scene(id).is_empty() and not Game.event_applied(id):
						return id
	return ""

## Pairs with any bond, strongest first: [[a, b, points, level], ...]
static func listing() -> Array:
	var out = []
	for k in Game.S.get("bonds", {}):
		var p = int(Game.S["bonds"][k])
		if p <= 0:
			continue
		var ab = k.split("|")
		out.append([ab[0], ab[1], p, level_for(p)])
	out.sort_custom(func(x, y): return x[2] > y[2])
	return out

static func all_pair_scenes() -> Array:
	var out = []
	for id in Content.data.get("scenes", {}):
		if str(id).begins_with("BOND_"):
			out.append(id)
	return out
