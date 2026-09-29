extends SceneTree
## Loads every script to surface parse errors (autoload identifiers may be reported as missing here).
func _init():
	var files = []
	_walk("res://src", files)
	for p in files:
		load(p)
	print("parse_check loaded ", files.size(), " scripts")
	quit()
func _walk(d, out):
	var da = DirAccess.open(d)
	for f in da.get_files():
		if f.ends_with(".gd"): out.append(d + "/" + f)
	for sd in da.get_directories():
		_walk(d + "/" + sd, out)
