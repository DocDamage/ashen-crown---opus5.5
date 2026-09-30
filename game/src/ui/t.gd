class_name T
extends RefCounted
## Localization-ready UI strings (sys s4). Every menu, settings, battle-command and system-message string lives in
## res://content/strings/<lang>.json as "key": "text". Call T.s("menu.items") (Object.tr is a native method and cannot
## be shadowed by a static function, so the helper is T.s; T.f formats with % args).
## Story dialogue stays in the scene files; tools/l10n/extract.py dumps it to a CSV template with stable keys.
## Missing keys return the fallback (or the key itself) and are listed by T.missing for the string audit.

static var lang := "en"
static var _table: Dictionary = {}
static var _loaded := false
static var missing: Dictionary = {}

static func _load() -> void:
	_loaded = true
	_table = {}
	for l in ["en", lang]:
		var p = "res://content/strings/%s.json" % l
		if FileAccess.file_exists(p):
			var d = JSON.parse_string(FileAccess.get_file_as_string(p))
			if typeof(d) == TYPE_DICTIONARY:
				for k in d:
					if not str(k).begins_with("_"):
						_table[k] = str(d[k])

static func set_lang(l: String) -> void:
	lang = l
	_loaded = false

static func has(key: String) -> bool:
	if not _loaded:
		_load()
	return _table.has(key)

## Looks a string up by key. `fallback` is returned (and the key recorded as missing) when the table lacks it.
static func s(key: String, fallback: String = "") -> String:
	if not _loaded:
		_load()
	if _table.has(key):
		return _table[key]
	missing[key] = true
	return fallback if fallback != "" else key

## Formatted lookup: T.f("save.overwrite", [3]) with "Overwrite slot %d?" in the table.
static func f(key: String, args: Array, fallback: String = "") -> String:
	var t = s(key, fallback)
	return t % args if not args.is_empty() else t
