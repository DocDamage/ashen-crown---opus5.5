class_name FishCore
extends RefCounted
## Fishing minigame rules (sys s4), deterministic and presentation-free so tests can drive it.
## States: cast (hold to wind up, release to cast) -> wait (bobber; striking early spooks the fish) -> bite (strike
## inside the window) -> reel (hold to reel in; tension rises, faster while the fish runs; release to let it ease;
## tension 1.0 snaps the line, a long slack lets the fish throw the hook) -> caught | lost.
## Content: Content.data.fishing (tools/content/fishing.py).

var state = "cast"
var rng: Rng
var table = "river"
var night = false
var assist = false          # easy difficulty / assist: wider bite window, slower tension
var fish: Dictionary = {}
var size = 0.0
var weight = 0.0
var power = 0.0
var t = 0.0
var wait_t = 0.0
var nibbles: Array = []     # times during the wait when the bobber twitches (not a bite)
var window = 0.8
var line = 1.0              # remaining distance (0 = landed)
var tension = 0.0           # 0..1 (1 = snap)
var running = false         # the fish is making a run
var run_t = 0.0
var slack_t = 0.0
var reason = ""             # lost: too_early | escaped | snapped | nothing
var _held = false
var elapsed = 0.0

const WATER := ["water", "shallow", "deep", "pool", "reef", "puddle"]

static func data() -> Dictionary:
	return Content.data.get("fishing", {})

static func fish_def(fid: String) -> Dictionary:
	var d = data()
	if d.get("fish", {}).has(fid):
		return d["fish"][fid]
	return d.get("junk", {}).get(fid, {})

## Candidates for a table at this hour (night-only fish only at night).
static func candidates(p_table: String, p_night: bool) -> Array:
	var out = []
	var fs: Dictionary = data().get("fish", {})
	var ids: Array = fs.keys()
	ids.sort()
	for fid in ids:
		var f: Dictionary = fs[fid]
		if not f["tables"].has(p_table):
			continue
		if f["night"] and not p_night:
			continue
		out.append(f)
	return out

## Weighted pick: rarity weights, far casts favour rarer fish, a small junk chance.
static func pick_fish(p_table: String, r: Rng, p_night: bool, p_power: float) -> Dictionary:
	var cands = candidates(p_table, p_night)
	if cands.is_empty():
		return {}
	if r.chance(4.0):
		var junk: Dictionary = data().get("junk", {})
		var jk: Array = junk.keys()
		jk.sort()
		if not jk.is_empty():
			return junk[jk[r.next_u32() % jk.size()]]
	var rw: Dictionary = data().get("rarity_weight", {"1": 60, "2": 26, "3": 10, "4": 3})
	var total = 0.0
	var ws = []
	for f in cands:
		var w = float(rw.get(str(int(f["rarity"])), 10))
		if int(f["rarity"]) >= 3:
			w *= 1.0 + p_power * 0.8
		ws.append(w)
		total += w
	var x = r.randf() * total
	for i in range(cands.size()):
		x -= ws[i]
		if x < 0.0:
			return cands[i]
	return cands[-1]

static func roll_size(f: Dictionary, r: Rng, p_power: float) -> float:
	if not f.has("size"):
		return 0.0
	var lo = float(f["size"][0])
	var hi = float(f["size"][1])
	# two draws averaged (sizes cluster in the middle), a far cast nudges them up
	var u = (r.randf() + r.randf()) / 2.0
	u = clampf(u + (p_power - 0.5) * 0.12, 0.0, 1.0)
	return snappedf(lo + (hi - lo) * u, 0.1)

static func weight_of(f: Dictionary, size_cm: float) -> float:
	if not f.has("k"):
		return 0.0
	return snappedf(float(f["k"]) * pow(size_cm / 10.0, 3.0), 0.01)

## Saltwhistle Open placing for one catch: 1 gold, 2 silver, 3 bronze, 0 none.
static func tourney_rank(kg: float) -> int:
	var tt: Dictionary = data().get("tourney", {"gold": 18.0, "silver": 8.0, "bronze": 3.0})
	if kg >= float(tt["gold"]):
		return 1
	if kg >= float(tt["silver"]):
		return 2
	if kg >= float(tt["bronze"]):
		return 3
	return 0

func start(p_table: String, seed_value: int, p_night: bool, p_assist: bool = false) -> void:
	table = p_table
	rng = Rng.new(seed_value)
	night = p_night
	assist = p_assist
	state = "cast"
	t = 0.0
	power = 0.0
	_held = false
	elapsed = 0.0
	reason = ""

func strength() -> float:
	return float(fish.get("strength", 1))

## One tick. `hold`: Confirm is down; `pressed`: Confirm went down this tick.
func step(dt: float, hold: bool, pressed: bool) -> void:
	elapsed += dt
	match state:
		"cast":
			if hold:
				_held = true
				t += dt
				power = 1.0 - absf(fmod(t * 1.25, 2.0) - 1.0)   # ping-pong 0..1
			elif _held:
				_cast()
		"wait":
			t += dt
			if pressed:
				_lose("too_early")
			elif t >= wait_t:
				state = "bite"
				t = 0.0
		"bite":
			t += dt
			if pressed:
				state = "reel"
				t = 0.0
				line = 0.35 + power * 0.55
				tension = 0.25
				running = false
				run_t = 0.6 + rng.randf() * 0.8
			elif t > window:
				_lose("escaped")
		"reel":
			_reel(dt, hold)

func _cast() -> void:
	fish = pick_fish(table, rng, night, power)
	if fish.is_empty():
		_lose("nothing")
		return
	size = roll_size(fish, rng, power)
	weight = weight_of(fish, size)
	state = "wait"
	t = 0.0
	wait_t = 1.2 + rng.randf() * 3.2
	nibbles = []
	var nn = rng.randi_range(0, 2)
	for i in range(nn):
		nibbles.append(0.4 + rng.randf() * maxf(0.2, wait_t - 0.9))
	window = 0.85 * (1.35 if assist else 1.0) * (0.8 if int(fish.get("rarity", 1)) >= 4 else 1.0)

func pull() -> float:
	return (0.3 + strength() * 0.07) if running else 0.1

func _reel(dt: float, hold: bool) -> void:
	run_t -= dt
	if run_t <= 0.0:
		running = not running
		if running:
			run_t = (0.4 + rng.randf() * 0.9) * (0.7 + strength() * 0.06)
		else:
			run_t = 0.7 + rng.randf() * 1.4
	var p = pull()
	var k = 0.72 if assist else 1.0
	if hold:
		line -= dt * (0.3 - p * 0.16)
		tension += dt * (0.22 + p * 0.95) * k
	else:
		line += dt * p * 0.1
		# a running fish keeps the line taut even with the reel still
		tension -= dt * (0.75 - (p * 0.55 if running else 0.0)) * (1.0 if not assist else 1.15)
	tension = clampf(tension, 0.0, 1.0)
	if tension < 0.04:
		slack_t += dt
	else:
		slack_t = 0.0
	if tension >= 1.0:
		_lose("snapped")
	elif slack_t > 2.6:
		_lose("escaped")
	elif line >= 1.25:
		_lose("escaped")
	elif line <= 0.0:
		line = 0.0
		state = "caught"

func _lose(why: String) -> void:
	state = "lost"
	reason = why

## Nibble twitch at time t during the wait (cosmetic).
func nibbling() -> bool:
	if state != "wait":
		return false
	for n in nibbles:
		if t >= n and t < n + 0.25:
			return true
	return false

## Headless helper for tests: plays a whole cast with a simple policy ("good": reel while the fish is calm and
## tension is safe; "greedy": hold the whole time; "early": strike before the bite). Returns the end state.
func autoplay(policy: String, cast_hold: float = 0.6, dt: float = 1.0 / 60.0) -> String:
	var n = 0
	while state == "cast" and n < 10000:
		step(dt, t < cast_hold, n == 0)
		n += 1
	var pressed_once = false
	while state in ["wait", "bite", "reel"] and n < 200000:
		var hold = false
		var press = false
		match state:
			"wait":
				press = policy == "early" and t > 0.3 and not pressed_once
				pressed_once = pressed_once or press
			"bite":
				press = t > 0.2
			"reel":
				hold = policy == "greedy" or (tension < (0.55 if running else 0.8) and not (running and tension > 0.35))
		step(dt, hold, press)
		n += 1
	return state
