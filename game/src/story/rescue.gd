class_name Rescue
extends RefCounted
## CH12 rescue (Shadow-style): five heroes go back for the relay prisoners while the rest hold the lift.
## A hidden timer runs on D09_LIFT. Each hero reaches the cage at a fixed time; hints tell the player to wait.
## Pull the brake early and whoever has not arrived is lost below. They come back changed (undead, rebuilt or
## fragment-bound), and the five become "the Bound": a second, locked party that merges back after a superboss.

const HEROES := ["C02", "C03", "C04", "C05", "C07", "C08", "C09", "C10"]
const FORM := {"C07": "undead", "C03": "undead", "C10": "undead", "C04": "rebuilt", "C08": "rebuilt",
	"C02": "fragment", "C05": "fragment", "C09": "fragment"}
const FORM_NAME := {"undead": "Undead", "rebuilt": "Rebuilt", "fragment": "Fragment-bound"}
const TINT := {"undead": Color(0.72, 0.86, 0.78), "rebuilt": Color(0.86, 0.8, 0.7), "fragment": Color(1.0, 0.78, 0.66)}
const T_END := 100.0
const ARRIVE := [32.0, 50.0, 66.0, 81.0, 96.0]
const HINTS := [15.0, 40.0, 58.0, 74.0, 88.0, 94.0]
const LIFT_MAP := "D09_LIFT"
const CAMP := {"map": "BOUND_CAMP", "spawn": "default", "x": -1, "y": -1, "dir": "down"}

static var snap: Dictionary = {}

static func eligible() -> Array:
	return HEROES.filter(func(c): return Game.is_available(c))

static func state() -> Dictionary:
	return Game.S.get("rescue", {})

static func running() -> bool:
	return str(state().get("state", "")) == "run"

## The picked team leaves the party; the timer starts at zero. The retry point is taken here.
static func begin(team: Array) -> void:
	Game.S["rescue"] = {"team": team.duplicate(), "t": 0.0, "arrived": [], "hint": 0, "state": "run"}
	Game.S["vars"]["rescue_left"] = team.size()
	for c in team:
		Game.set_available(c, false)
	snap = Game.S.duplicate(true)

static func arrival_times(n: int) -> Array:
	# fewer than five heroes: the last arrivals keep the late slots, so waiting still matters
	return ARRIVE.slice(ARRIVE.size() - n)

## Advances the hidden timer. Returns the scene to play now ("" for none).
static func tick(delta: float) -> String:
	if not running():
		return ""
	var r: Dictionary = Game.S["rescue"]
	r["t"] = float(r["t"]) + delta
	var team: Array = r["team"]
	var times = arrival_times(team.size())
	var n: int = r["arrived"].size()
	if n < team.size() and float(r["t"]) >= float(times[n]):
		var cid: String = team[n]
		r["arrived"].append(cid)
		Game.set_available(cid, true)
		Game.S["vars"]["rescue_left"] = team.size() - r["arrived"].size()
		return "CH12_ARRIVE_" + cid
	var h: int = int(r["hint"])
	if h < HINTS.size() and float(r["t"]) >= HINTS[h]:
		r["hint"] = h + 1
		return "CH12_HINT%d" % (h + 1)
	if float(r["t"]) >= T_END:
		r["state"] = "crushed"
		return "CH12_LIFT_CRUSH"
	return ""

static func all_arrived() -> bool:
	var r = state()
	return not r.is_empty() and r["arrived"].size() >= r["team"].size()

## The brake is pulled. Whoever is not on the cage is lost, and comes back changed.
static func finish() -> Array:
	var r: Dictionary = Game.S["rescue"]
	r["state"] = "done"
	var lost = []
	for c in r["team"]:
		if not r["arrived"].has(c):
			lost.append(c)
	if not Game.S.has("changed"):
		Game.S["changed"] = {}
	for c in lost:
		Game.S["changed"][c] = FORM[c]
		Game.set_flag("changed_" + c.to_lower())
		Game.set_available(c, true)
	# soul-bound: every survivor is tied to every hero who died for the prisoners (Bond 3)
	for a in r["arrived"]:
		for c in lost:
			Bonds.gain(a, c, 60)
	Game.set_flag("rescue_done")
	if lost.is_empty():
		Game.set_flag("rescue_all")
	else:
		Game.S["bound"] = {"members": r["team"].duplicate(), "on": false, "merged": false, "loc": CAMP.duplicate(),
			"main_loc": {}, "main_active": [], "main_avail": {}, "met": []}
		Game.set_flag("bound_formed")
	r["lost"] = lost
	return lost

static func retry() -> void:
	if not snap.is_empty():
		Game.S = snap.duplicate(true)

# ---------------------------------------------------------------- changed heroes
static func form(cid: String) -> String:
	return str(Game.S.get("changed", {}).get(cid, "")) if not Game.S.is_empty() else ""

static func tint(cid: String) -> Color:
	var f = form(cid)
	return TINT.get(f, Color.WHITE)

## Changed heroes: undead hit harder and shrug off poison and doom; rebuilt ones are armoured and cannot be put to
## sleep or stunned; fragment-bound ones cast hotter and resist fire.
static func apply_form(cid: String, st: Dictionary) -> Dictionary:
	var f = form(cid)
	if f == "":
		return st
	var pas: Dictionary = st["passives"].duplicate(true)
	var imm: Array = (pas.get("immune", []) as Array).duplicate()
	match f:
		"undead":
			st["atk"] = int(floor(st["atk"] * 1.15))
			for s in ["poison", "doom", "bleed"]:
				if not imm.has(s):
					imm.append(s)
			var er: Dictionary = pas.get("elem_resist", {}).duplicate() if typeof(pas.get("elem_resist", {})) == TYPE_DICTIONARY else {}
			er["shadow"] = true
			pas["elem_resist"] = er
		"rebuilt":
			st["def"] = int(floor(st["def"] * 1.25))
			st["mhp"] = int(floor(st["mhp"] * 1.1))
			for s in ["sleep", "stun", "slow"]:
				if not imm.has(s):
					imm.append(s)
		"fragment":
			st["matk"] = int(floor(st["matk"] * 1.2))
			st["mmp"] = int(floor(st["mmp"] * 1.15))
			var er2: Dictionary = pas.get("elem_resist", {}).duplicate() if typeof(pas.get("elem_resist", {})) == TYPE_DICTIONARY else {}
			er2["fire"] = true
			pas["elem_resist"] = er2
	pas["immune"] = imm
	pas["changed"] = f
	st["passives"] = pas
	return st

# ---------------------------------------------------------------- the Bound (second, locked party)
static func bound() -> Dictionary:
	return Game.S.get("bound", {}) if not Game.S.is_empty() else {}

static func bound_active() -> bool:
	var b = bound()
	return not b.is_empty() and not bool(b.get("merged", false))

static func bound_on() -> bool:
	return bound_active() and bool(bound().get("on", false))

static func is_bound(cid: String) -> bool:
	return bound_active() and bound()["members"].has(cid)

## A reunion `join` for a bound hero while the Bound still stand apart: the scene plays, the hero stays with them.
static func holds(cid: String) -> bool:
	return is_bound(cid) and not bound_on()

static func note_met(cid: String) -> void:
	var b = bound()
	if not b["met"].has(cid):
		b["met"].append(cid)

## Swaps control between Raven's company and the Bound. `cur` is where the controlled party stands now.
## Returns the location to load.
static func swap(cur: Dictionary) -> Dictionary:
	var b: Dictionary = Game.S["bound"]
	var P: Dictionary = Game.S["party"]
	if not bool(b["on"]):
		b["main_loc"] = cur.duplicate()
		b["main_active"] = P["active"].duplicate()
		b["main_avail"] = P["available"].duplicate()
		for c in P["available"]:
			P["available"][c] = false
		for c in b["members"]:
			P["available"][c] = true
		P["active"] = b["members"].duplicate()
		P["locked"] = true
		b["on"] = true
		return b["loc"]
	b["loc"] = cur.duplicate()
	P["available"] = b["main_avail"].duplicate()
	for c in b["members"]:
		P["available"][c] = false
	P["active"] = (b["main_active"] as Array).filter(func(c): return not b["members"].has(c))
	P["locked"] = false
	b["on"] = false
	return b["main_loc"]

## The Bound rejoin everyone. Whoever is in control stays where they stand.
static func merge() -> bool:
	if not bound_active():
		return false
	var b: Dictionary = Game.S["bound"]
	var P: Dictionary = Game.S["party"]
	if bool(b["on"]):
		for c in b["main_avail"]:
			if bool(b["main_avail"][c]):
				P["available"][c] = true
	for c in b["members"]:
		P["available"][c] = true
	P["locked"] = false
	b["on"] = false
	b["merged"] = true
	Game.set_flag("bound_merged")
	return true
