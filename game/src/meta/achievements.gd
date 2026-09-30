class_name Achievements
extends RefCounted
## In-game achievements (sys s4). Definitions: Content.data.achievements (tools/content/achievements.py).
## Unlocks are kept per player profile (user://profile.json, shared by every save) and mirrored into the save
## (Game.S.achievements) so New Game+ and copied saves carry them. Game.achieve(id) unlocks directly; evaluate()
## is the generic checker run after state changes (Game throttles it to twice a second).

static var path := "user://profile.json"
static var _profile: Dictionary = {}
static var _loaded := false
static var quiet := false          # tests: no toasts

static func defs() -> Dictionary:
	return Content.data.get("achievements", {}).get("list", {})

static func order() -> Array:
	return Content.data.get("achievements", {}).get("order", [])

static func _load() -> void:
	_loaded = true
	_profile = {"achievements": {}}
	if FileAccess.file_exists(path):
		var d = JSON.parse_string(FileAccess.get_file_as_string(path))
		if typeof(d) == TYPE_DICTIONARY:
			_profile = d
	if not _profile.has("achievements"):
		_profile["achievements"] = {}

static func _save() -> void:
	# QA bots and tests never write the player's real profile (sandboxed profiles are written)
	if QA.active and path == "user://profile.json":
		return
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var f = FileAccess.open(path, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(_profile, "\t"))

## Forget the profile (tests) and optionally point it at another file.
static func reset_profile(p: String = "") -> void:
	if p != "":
		path = p
	_loaded = true
	_profile = {"achievements": {}}
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)

static func is_unlocked(id: String) -> bool:
	if not _loaded:
		_load()
	if _profile["achievements"].has(id):
		return true
	return not Game.S.is_empty() and Game.S.get("achievements", []).has(id)

static func unlocked_count() -> int:
	var n = 0
	for id in defs():
		if is_unlocked(id):
			n += 1
	return n

static func unlock(id: String) -> bool:
	if not defs().has(id):
		push_warning("Unknown achievement " + id)
		return false
	if not _loaded:
		_load()
	var fresh = not _profile["achievements"].has(id)
	if fresh:
		_profile["achievements"][id] = Time.get_datetime_string_from_system()
		_save()
	if not Game.S.is_empty():
		if not Game.S.has("achievements"):
			Game.S["achievements"] = []
		if not Game.S["achievements"].has(id):
			Game.S["achievements"].append(id)
			fresh = true
	if fresh and not quiet:
		Game.emit_signal("achieved", id)
	return fresh

## Unlocks every achievement whose conditions now hold. Returns the ids unlocked by this call.
static func evaluate() -> Array:
	var got = []
	if Game.S.is_empty():
		return got
	var d = defs()
	for id in order():
		if is_unlocked(id):
			continue
		var cond: Array = d[id].get("cond", [])
		if cond.is_empty():
			continue
		if Game.eval_cond(cond) and unlock(id):
			got.append(id)
	return got

# ---------------------------------------------------------------- derived values
static func meta_value(key: String) -> float:
	var S = Game.S
	match key:
		"bestiary_pct":
			var total = 0
			var got = 0
			for eid in Content.data["enemies"]:
				var e = Content.data["enemies"][eid]
				if e.has("variant_of") or e.get("tags", []).has("part") or e.get("tags", []).has("superboss"):
					continue
				total += 1
				if int(S.get("bestiary", {}).get(eid, {}).get("defeated", 0)) > 0:
					got += 1
			return 100.0 * got / maxf(1.0, total)
		"fish_species":
			return float(S.get("fish", {}).get("log", {}).size())
		"fish_caught":
			return float(Game.stat("fish_caught"))
		"max_level":
			var mx = 0
			for cid in S["party"]["roster"]:
				mx = maxi(mx, int(S["party"]["members"][cid]["level"]))
			return float(mx)
		"recruited":
			return float(S["party"]["roster"].size())
		"vestiges":
			return float(S.get("vestiges", []).size())
		"chests":
			return float(S.get("chests", []).size())
		"quests":
			var n = 0
			for q in S.get("quests", {}):
				if str(S["quests"][q].get("state", "")) == "COMPLETED":
					n += 1
			return float(n)
		"discovered":
			return float(S.get("discovered", []).size())
		"achv":
			return float(unlocked_count())
		"gold":
			return float(Game.gold())
		"ng":
			return float(S.get("ng", 0))
	return 0.0

static func value_of(expr: String) -> float:
	# "stat:battles" | "meta:bestiary_pct" | "var:arena_rank"
	var p = expr.split(":")
	if p.size() < 2:
		return 0.0
	match p[0]:
		"stat": return float(Game.stat(p[1]))
		"meta": return meta_value(p[1])
		"var": return float(Game.var_get(p[1]))
	return 0.0

## Evaluates "stat:<key><op><n>" / "meta:<key><op><n>".
static func eval_meta(c: String) -> bool:
	var parts = _split(c)
	if parts.is_empty():
		return false
	var cur = value_of(parts[0])
	var n = float(parts[2])
	match parts[1]:
		">=": return cur >= n
		"<=": return cur <= n
		"==": return absf(cur - n) < 0.001
		">": return cur > n
		"<": return cur < n
	return false

static func _split(c: String) -> Array:
	for o in [">=", "<=", "==", ">", "<"]:
		var i = c.find(o)
		if i > 0:
			return [c.substr(0, i), o, c.substr(i + o.length())]
	return []

## Progress for the menu bar: [current, target] or [] when the achievement has no numeric condition.
static func progress(id: String) -> Array:
	var d: Dictionary = defs().get(id, {})
	if d.has("progress"):
		var pr: Array = d["progress"]
		return [minf(value_of(str(pr[0])), float(pr[1])), float(pr[1])]
	var nums = []
	for c in d.get("cond", []):
		var sp = _split(str(c))
		if not sp.is_empty():
			nums.append(sp)
	if nums.size() == 1:
		var target = float(nums[0][2])
		return [minf(value_of(nums[0][0]), target), target]
	var conds: Array = d.get("cond", [])
	if conds.size() > 1:
		var ok = 0
		for c in conds:
			if Game.eval_cond([c]):
				ok += 1
		return [float(ok), float(conds.size())]
	return []
