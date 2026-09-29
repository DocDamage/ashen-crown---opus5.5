extends Node
## ContentRegistry: immutable compiled definitions (res://content/content.json).

var data: Dictionary = {}
var hash = ""

func _ready() -> void:
	load_content()

func load_content(path: String = "res://content/content.json") -> void:
	var f = FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("Content missing: " + path)
		return
	var parsed = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("Content parse failed")
		return
	data = parsed
	hash = data.get("content_hash", "")

## Library art override: res://assets/X resolves to res://assets/ext/X when the owner's licensed library art has
## been installed by `python tools/gen_art.py library` (git-ignored); otherwise the generated original is used.
func art(path: String) -> String:
	if path.begins_with("res://assets/") and not path.begins_with("res://assets/ext/"):
		var e = "res://assets/ext/" + path.substr(13)
		if ResourceLoader.exists(e):
			return e
	return path

func load_art(path: String) -> Texture2D:
	var p = art(path)
	return load(p) if ResourceLoader.exists(p) else null

func ch(id: String) -> Dictionary: return data["characters"].get(id, {})
func item(id: String) -> Dictionary: return data["items"].get(id, {})
func ability(id: String) -> Dictionary: return data["abilities"].get(id, {})
func enemy(id: String) -> Dictionary: return data["enemies"].get(id, {})
func map(id: String) -> Dictionary: return data["maps"].get(id, {})
func scene(id: String) -> Dictionary: return data["scenes"].get(id, {})
func formation(id: String) -> Dictionary: return data["formations"]["formations"].get(id, {})
func group(id: String) -> Array: return data["formations"]["groups"].get(id, [])
func item_name(id: String) -> String:
	var n: String = item(id).get("name", id)
	var up = Game.upgrade_level(id) if Game.S.has("upgrades") else 0
	return n + (" +%d" % up if up > 0 else "")
func speaker(id: String) -> Array: return data["speakers"].get(id, [id.capitalize(), ""])
