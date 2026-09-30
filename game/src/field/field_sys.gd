class_name FieldSys
extends RefCounted
## Field and world systems (expansion pass s3), kept out of field.gd so the shared file only carries hooks:
##   time      night / hour conditions, sleeping at inns, the day counter
##   mounts    Brackhorn variants and the terrain each one rides (world maps only)
##   airship   Lanternwake upgrades: Gale Vanes (speed), Grapnel Keel (land anywhere), Diving Hull (undersea),
##             Delver Auger (down the Aurora Pit into the Deep, post-fault)
##   travel    waystones (attune on touch, travel menu by region, surface and Deep apart), the Wayfarer's Sigil,
##             and travel networks (mine-rail, mag-rail, magma skiffs, lake barges) from content "travel"
##   weather   visual weather by region / map (Settings "weather")
## Authoring notes: docs/expansion/FIELD_SYSTEMS_S3.md.

# ======================================================================
# Time
# ======================================================================
const MORNING := 360.0      # 06:00
const EVENING := 1080.0     # 18:00

static func clock() -> float:
	return float(Game.S.get("clock", 480.0)) if not Game.S.is_empty() else 480.0

static func hour() -> float:
	return clock() / 60.0

static func night() -> bool:
	var hr = hour()
	return hr >= 20.0 or hr < 5.0

## "a-b" in hours (floats allowed); wraps past midnight when a > b ("20-5").
static func in_hours(spec: String) -> bool:
	var p = spec.split("-")
	if p.size() != 2:
		return false
	var a = float(p[0])
	var b = float(p[1])
	var hr = hour()
	if a <= b:
		return hr >= a and hr < b
	return hr >= a or hr < b

## Advance the clock to the next morning (06:00) or evening (18:00); counts a day when it passes midnight.
static func sleep_until(which: String) -> void:
	var target = MORNING if which == "morning" else EVENING
	var c = clock()
	if target <= c:
		Game.S["day"] = int(Game.S.get("day", 0)) + 1
	Game.S["clock"] = target

## Called by the field clock: returns true when night began or ended this tick.
static func advance(delta_min: float) -> bool:
	var was = night()
	var c = clock() + delta_min
	if c >= 1440.0:
		Game.S["day"] = int(Game.S.get("day", 0)) + 1
	Game.S["clock"] = fposmod(c, 1440.0)
	return was != night()

## Night formations the active party can face: the strongest enemy at most 3 levels above the party's average.
static func night_forms(post: bool) -> Array:
	var ids: Array = Game.active()
	if ids.is_empty():
		return []
	var tot = 0
	for c in ids:
		tot += int(Game.member(c)["level"])
	var avg = float(tot) / ids.size()
	var out = []
	for fid in Content.group("WP_NIGHT" if post else "W_NIGHT"):
		var top = 0
		for e in Content.formation(fid).get("enemies", []):
			var eid = str(e if typeof(e) == TYPE_STRING else e.get("id", ""))
			top = maxi(top, int(Content.enemy(eid).get("level", 0)))
		if top <= avg + 3.0:
			out.append(fid)
	return out

# ======================================================================
# Mounts: Brackhorn variants
# ======================================================================
const MOUNTS := ["bramble", "ridgehorn", "fenwader", "deepstrider", "gilded"]
const MOUNT_FLAG := {"bramble": "", "ridgehorn": "brackhorn_ridgehorn", "fenwader": "brackhorn_fenwader",
	"deepstrider": "qup1_deepstrider", "gilded": "brackhorn_gilded"}
const MOUNT_NAME := {"bramble": "Bramble", "ridgehorn": "Ridgehorn", "fenwader": "Fenwader", "deepstrider": "Deepstrider",
	"gilded": "Gilded Brackhorn"}
const MOUNT_DESC := {"bramble": "Open roads and fields.", "ridgehorn": "Climbs hills and rocky ground.",
	"fenwader": "Wades marsh, shallows and narrow water.", "deepstrider": "Runs the Deep's floors and lava crust.",
	"gilded": "Fastest of all, over any open ground."}
const MOUNT_TINT := {"bramble": Color(1, 1, 1), "ridgehorn": Color(0.8, 0.74, 0.68), "fenwader": Color(0.66, 0.9, 0.8),
	"deepstrider": Color(1.0, 0.62, 0.5), "gilded": Color(1.0, 0.88, 0.45)}
const MOUNT_SPEED := {"bramble": 1.35, "ridgehorn": 1.35, "fenwader": 1.35, "deepstrider": 1.4, "gilded": 1.8}
const OPEN_GROUND := ["plains", "grass2", "sand", "salt", "snow", "ash", "olive", "road", "path", "bridge", "ice", "forest"]
const DEEP_FLOOR := ["cave_floor", "crystal_floor", "bone", "ruin_floor", "road", "lava"]
const MOUNT_RIDE := {
	"bramble": OPEN_GROUND,
	"ridgehorn": OPEN_GROUND + ["hills", "rocky"],
	"fenwader": OPEN_GROUND + ["swamp", "shallow", "water"],
	"deepstrider": OPEN_GROUND,
	"gilded": OPEN_GROUND + ["hills", "rocky", "swamp"],
}
## terrain that is solid on foot but a mount crosses (water only within one cell of the shore)
const MOUNT_PASS := {"fenwader": ["water"], "deepstrider": ["lava"]}

static func is_deep_map(mid: String) -> bool:
	return mid.begins_with("DEEP")

static func mount_owned(mk: String) -> bool:
	if Game.S.is_empty() or not bool(Game.S["vehicle"].get("mount", false)):
		return false
	var f: String = MOUNT_FLAG.get(mk, "?")
	return f == "" or Game.flag(f)

static func mounts_owned() -> Array:
	return MOUNTS.filter(func(m): return mount_owned(m))

static func mount_kind() -> String:
	var mk := str(Game.S.get("vehicle", {}).get("mount_kind", "bramble")) if not Game.S.is_empty() else "bramble"
	return mk if mount_owned(mk) else "bramble"

static func set_mount(mk: String) -> bool:
	if not mount_owned(mk):
		return false
	Game.S["vehicle"]["mount_kind"] = mk
	return true

## Next / previous owned variant (dirn +1 / -1); returns the new kind.
static func cycle_mount(dirn: int) -> String:
	var own = mounts_owned()
	if own.is_empty():
		return "bramble"
	var i = own.find(mount_kind())
	var mk: String = own[posmod(i + dirn, own.size())]
	set_mount(mk)
	return mk

## Can mount `mk` be ridden on terrain `kind` on map `mid`? (Off the ridable set the party leads it on foot.)
static func can_ride(kind: String, mid: String, mk: String) -> bool:
	if is_deep_map(mid):
		return mk == "deepstrider" and kind in DEEP_FLOOR
	if mid == "UNDERSEA":
		return false
	return kind in MOUNT_RIDE.get(mk, OPEN_GROUND)

## Solid-on-foot terrain that `mk` still crosses (shore = the water cell touches walkable land).
static func mount_passes(kind: String, mid: String, mk: String, shore: bool) -> bool:
	var ks: Array = MOUNT_PASS.get(mk, [])
	if not ks.has(kind):
		return false
	if kind == "water":
		return shore and not is_deep_map(mid)
	if kind == "lava":
		return is_deep_map(mid)
	return true

# ======================================================================
# Airship upgrades and the sea floor
# ======================================================================
const SEA_MAP := "UNDERSEA"
const SEA_RATIO := 96.0 / 176.0
const SUB_SOLID := ["mountain", "lava", "wall_rock", "void", "reef"]

static func gale() -> bool:
	return Game.flag("gale_vanes")

static func grapnel() -> bool:
	return Game.flag("lanternwake_grapnel")

static func diving() -> bool:
	return Game.flag("lanternwake_diving")

static func auger() -> bool:
	return Game.flag("lanternwake_auger") and Game.S.get("world_phase", "pre") == "post"

static func to_sea(t: Vector2i) -> Vector2i:
	return Vector2i(int(t.x * SEA_RATIO), int(t.y * SEA_RATIO))

static func from_sea(t: Vector2i) -> Vector2i:
	return Vector2i(int((t.x + 0.5) / SEA_RATIO), int((t.y + 0.5) / SEA_RATIO))

static func sub_solid(kind: String) -> bool:
	return kind in SUB_SOLID

## Nearest cell (spiral) on map `mid` that satisfies ok(kind) — for dive / surface placement.
static func nearest_cell(mid: String, c: Vector2i, ok: Callable, rmax: int = 12) -> Vector2i:
	var m: Dictionary = Content.map(mid)
	if m.is_empty():
		return Vector2i(-1, -1)
	var w = int(m["w"])
	var h = int(m["h"])
	for r in range(0, rmax + 1):
		for dy in range(-r, r + 1):
			for dx in range(-r, r + 1):
				if maxi(absi(dx), absi(dy)) != r:
					continue
				var p = c + Vector2i(dx, dy)
				if p.x < 0 or p.y < 0 or p.x >= w or p.y >= h:
					continue
				var k: String = m["legend"].get(String(m["grid"][p.y][p.x]), "void")
				if ok.call(k):
					return p
	return Vector2i(-1, -1)

# ======================================================================
# Waystones
# ======================================================================
const BEACON := "WS_P09"
const WARP_ITEM := "ZW01"
const REGION_NAMES := {"R01": "Crown March", "R02": "Cinder Reach", "R03": "Glass Coast", "R04": "Skyspine", "R05": "Pale Basin",
	"R06": "Ember Sea", "R07": "Vermilion Reach", "R08": "Mirewold", "R09": "Hoarfrost March", "SKY": "Shattered Choir",
	"U1": "Emberdeep", "U2": "The Lattice", "U3": "The Hollow Throne", "SEA": "The Sea Floor"}
const REGION_ORDER := ["R01", "R02", "R08", "R03", "R06", "R04", "R05", "R07", "R09", "SKY", "U1", "U2", "U3"]

static func attuned() -> Array:
	return Game.S.get("waystones", []) if not Game.S.is_empty() else []

static func is_attuned(wid: String) -> bool:
	return attuned().has(wid)

## Attune a waystone; returns true the first time.
static func attune(wid: String) -> bool:
	if not Game.S.has("waystones"):
		Game.S["waystones"] = []
	if Game.S["waystones"].has(wid):
		return false
	Game.S["waystones"].append(wid)
	return true

## After the fault the stones are dark until the Last Beacon's stone is lit again.
static func network_live() -> bool:
	if Game.S.get("world_phase", "pre") != "post":
		return true
	return is_attuned(BEACON)

## Every waystone of the current phase: [{id, name, region, layer, map, spawn}] (map = the phase's world map).
static func waystones() -> Array:
	var out = []
	for base in ["WORLD", "DEEP"]:
		var mid: String = Game.world_for_phase(base)
		for e in Content.map(mid).get("entities", []):
			if e["type"] != "waystone" or not Game.eval_cond(e["cond"]):
				continue
			out.append({"id": e["id"], "name": e.get("name", e["id"]), "region": e.get("region", ""), "layer": e.get("layer", "surface"),
				"map": mid, "spawn": str(e["id"]).to_lower(), "x": int(e["x"]), "y": int(e["y"])})
	return out

## Menu rows for one layer ("surface" | "deep"): region headers (disabled) + attuned stones; `here` is marked.
static func waystone_rows(layer: String, here: String = "") -> Array:
	var by = {}
	for w in waystones():
		if w["layer"] != layer or not is_attuned(w["id"]):
			continue
		if not by.has(w["region"]):
			by[w["region"]] = []
		by[w["region"]].append(w)
	var rows = []
	var regs: Array = by.keys()
	regs.sort_custom(func(a, b): return REGION_ORDER.find(a) < REGION_ORDER.find(b))
	for r in regs:
		rows.append({"text": REGION_NAMES.get(r, r), "enabled": false, "reason": "", "color": UI.C_LABEL, "header": true})
		for w in by[r]:
			var here_w: bool = w["id"] == here
			rows.append({"text": "  " + str(w["name"]), "value": w, "enabled": not here_w, "reason": "You are here.",
				"right": "here" if here_w else ""})
	return rows

## Where the Wayfarer's Sigil works: outside battle, scenes and dungeons (world maps, towns, isles).
static func warp_allowed(field: Field, ignore_busy: bool = false) -> bool:
	if field == null or field.map.is_empty() or (field.busy and not ignore_busy):
		return false
	if field.vehicle != "foot":
		return false
	if field.map.get("kind", "") == "world":
		return field.map_id != SEA_MAP
	if str(field.map.get("encounters", "")) not in ["", "none"]:
		return false
	for e in field.map.get("entities", []):
		if e["type"] == "zone":
			return false
	var dg: String = String(field.map_id).substr(0, 3)
	return not Content.data.get("dungeons", {}).has(dg)

# ======================================================================
# Travel networks (content "travel")
# ======================================================================
static func network(net: String) -> Dictionary:
	return Content.data.get("travel", {}).get(net, {})

static func network_rows(net: String, here_map: String) -> Array:
	var rows = []
	for st in network(net).get("stops", []):
		if not Game.eval_cond(st.get("if", [])):
			continue
		var here_s: bool = st["map"] == here_map
		rows.append({"text": st["name"], "value": st, "enabled": not here_s, "reason": "You are here.", "right": "here" if here_s else ""})
	return rows

# ======================================================================
# Weather (visual only)
# ======================================================================
## region -> [[kind, chance], ...] for each six-hour slot; the first kind that rolls wins.
const REGION_WEATHER := {
	"R01": [["rain", 0.25]], "R02": [["ash", 0.75]], "R03": [["rain", 0.35], ["fog", 0.2]],
	"R04": [["snow", 0.3], ["fog", 0.25]], "R05": [["sandstorm", 0.3]], "R06": [["rain", 0.2]],
	"R07": [["rain", 0.25], ["fog", 0.2]], "R08": [["fog", 0.55], ["rain", 0.3]], "R09": [["snow", 0.85]],
	"SKY": [["fog", 0.3]],
}
const REGION_WEATHER_POST := {"R01": [["ash", 0.3], ["rain", 0.25]], "R02": [["ash", 1.0]], "R03": [["rain", 0.45], ["fog", 0.2]],
	"R08": [["fog", 0.6], ["ash", 0.2]]}
const OUTDOOR_TILESETS := ["town_r01", "town_r02", "town_r03", "town_r04", "town_r05", "vermilion", "fen", "harbor", "capital", "sky"]
const KINDS := ["rain", "snow", "ash", "fog", "sandstorm"]

static func weather_slot() -> int:
	return int(Game.S.get("day", 0)) * 4 + int(clock() / 360.0)

## Weather for a region now ("" when clear); deterministic per region and six-hour slot.
static func region_weather(region: String, post: bool = false) -> String:
	var tbl: Array = (REGION_WEATHER_POST.get(region, REGION_WEATHER.get(region, [])) if post else REGION_WEATHER.get(region, []))
	var slot = weather_slot()
	for i in range(tbl.size()):
		var h = hash("%s|%d|%d" % [region, slot, i])
		var roll = float(absi(h) % 1000) / 1000.0
		if roll < float(tbl[i][1]):
			return str(tbl[i][0])
	return ""

## Weather for a map at a cell: `weather:` header wins (a kind, "none", or "region"); world maps use the zone's
## region (from its encounter group W_Rxx / WP_Rxx); outdoor town tilesets use the map's region.
static func weather_at(m: Dictionary, mid: String, cell: Vector2i) -> String:
	if m.is_empty() or Settings.get_v("weather") == false:
		return ""
	var hdr := str(m.get("weather", ""))
	if hdr == "none":
		return ""
	if hdr in KINDS:
		return hdr
	var post: bool = Game.S.get("world_phase", "pre") == "post"
	if m.get("kind", "") == "world":
		if is_deep_map(mid) or mid == SEA_MAP:
			return ""
		for e in m.get("entities", []):
			if e["type"] == "zone" and cell.x >= e["x1"] and cell.x <= e["x2"] and cell.y >= e["y1"] and cell.y <= e["y2"]:
				var g := str(e.get("encounters", ""))
				var r = g.substr(g.find("_") + 1) if g.find("_") >= 0 else ""
				return region_weather(r, post)
		return ""
	if hdr == "region" or str(m.get("tileset", "")) in OUTDOOR_TILESETS:
		return region_weather(str(m.get("region", "")), post)
	return ""
