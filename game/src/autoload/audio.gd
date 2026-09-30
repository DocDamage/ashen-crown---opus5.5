extends Node
## AudioService: semantic cue IDs -> streams, crossfades, buses (docs/12).

var _music_a: AudioStreamPlayer
var _music_b: AudioStreamPlayer
var _cur: AudioStreamPlayer
var current_cue = ""
var _sfx_pool: Array = []
var _cache = {}
var _last_sfx_ms = {}

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_music_a = AudioStreamPlayer.new()
	_music_b = AudioStreamPlayer.new()
	for p in [_music_a, _music_b]:
		p.bus = "Music"
		add_child(p)
	_cur = _music_a
	for i in range(8):
		var s = AudioStreamPlayer.new()
		s.bus = "SFX"
		add_child(s)
		_sfx_pool.append(s)

func _stream(path: String) -> AudioStream:
	if _cache.has(path):
		return _cache[path]
	var st: AudioStream = null
	if ResourceLoader.exists(path):
		st = load(path)
	_cache[path] = st
	return st

func music(cue: String, fade: float = 1.2) -> void:
	if cue == current_cue:
		return
	current_cue = cue
	var nxt = _music_b if _cur == _music_a else _music_a
	var old = _cur
	if cue == "" or cue == "silence":
		_fade_out(old, fade)
		return
	var st = _cue_stream("music", cue)
	if st == null:
		_fade_out(old, fade)
		return
	if st is AudioStreamOggVorbis or st is AudioStreamMP3:
		st.loop = true
	nxt.stream = st
	nxt.volume_db = -40.0 if fade > 0.0 else 0.0
	nxt.play()
	_cur = nxt
	if fade > 0.0:
		var tw = create_tween()
		tw.tween_property(nxt, "volume_db", 0.0, fade)
	_fade_out(old, fade)

## Library audio (the owner's soundtrack, fanfares and sound packs, installed by tools/art/install_overhaul.py
## into assets/ext/audio) wins over the generated originals in assets/audio.
func _cue_stream(kind: String, cue: String) -> AudioStream:
	for ext in ["ogg", "mp3", "wav"]:
		var p = "res://assets/ext/audio/%s/%s.%s" % [kind, cue, ext]
		if ResourceLoader.exists(p):
			return _stream(p)
	for ext in ["ogg", "wav"]:
		var p2 = "res://assets/audio/%s/%s.%s" % [kind, cue, ext]
		if ResourceLoader.exists(p2):
			return _stream(p2)
	return null

var _jingle: AudioStreamPlayer = null
var _resume_cue = ""

## Short fanfare (victory, level_up, item, inn, save, join, quest, game_over, rare). Silences the music; the next
## music() call (map entry, battle end) brings music back. Returns the jingle length in seconds (0 if none).
func jingle(name: String, resume: bool = false) -> float:
	var st = _cue_stream("jingle", name)
	if st == null:
		return 0.0
	if _jingle == null:
		_jingle = AudioStreamPlayer.new()
		_jingle.bus = "Music"
		add_child(_jingle)
		_jingle.finished.connect(func():
			if _resume_cue != "" and current_cue == "":
				music(_resume_cue, 0.6)
			_resume_cue = "")
	_resume_cue = current_cue if resume else ""
	stop_music(0.2)
	if st is AudioStreamOggVorbis:
		st.loop = false
	_jingle.stream = st
	_jingle.play()
	return st.get_length()

func _fade_out(p: AudioStreamPlayer, fade: float) -> void:
	if not p.playing:
		return
	if fade <= 0.0:
		p.stop()
		return
	var tw = create_tween()
	tw.tween_property(p, "volume_db", -40.0, fade)
	tw.tween_callback(p.stop)

func stop_music(fade: float = 0.0) -> void:
	current_cue = ""
	_fade_out(_music_a, fade)
	_fade_out(_music_b, fade)

func sfx(id: String, bus: String = "SFX") -> void:
	if id == "":
		return
	if bus != "UI" and Settings.get_v("captions") and T.has("cc." + id):
		emit_signal("caption", T.s("cc." + id))
	var now = Time.get_ticks_msec()
	if _last_sfx_ms.get(id, 0) + 40 > now:
		return
	_last_sfx_ms[id] = now
	var st = _cue_stream("sfx", id)
	if st == null:
		return
	for p in _sfx_pool:
		if not p.playing:
			p.stream = st
			p.bus = bus
			p.volume_db = randf_range(-1.5, 0.0)
			p.play()
			return

func ui(id: String) -> void:
	sfx(id, "UI")

# ======================================================================
# sys s4: dialogue voice blips and sound captions
# ======================================================================
signal caption(text: String)
var _blip_player: AudioStreamPlayer = null
var _voices = null
var _last_blip_ms = 0

func _voice_table() -> Dictionary:
	if _voices == null:
		var p = "res://assets/audio/blips/voices.json"
		_voices = JSON.parse_string(FileAccess.get_file_as_string(p)) if FileAccess.file_exists(p) else {}
		if typeof(_voices) != TYPE_DICTIONARY:
			_voices = {}
	return _voices

## [voice, pitch] for a speaker key: heroes (C01..), then named speakers through their portrait/type key, then a
## stable hash so every unnamed voice still sounds the same each time.
func voice_for(key: String) -> Array:
	var vt = _voice_table()
	var m: Dictionary = vt.get("map", {})
	var ty: Dictionary = vt.get("types", {})
	if m.has(key):
		return m[key]
	if ty.has(key):
		return ty[key]
	var info: Array = Content.speaker(key) if Content.data.has("speakers") else []
	var h = absi(hash(key))
	if info.size() > 1:
		var t = str(info[1])
		if m.has(t):
			return m[t]
		if ty.has(t):
			var v: Array = ty[t]
			return [v[0], float(v[1]) * (0.92 + 0.16 * float(h % 100) / 100.0)]
	var names: Array = vt.get("voices", ["pulse"])
	if names.is_empty():
		return ["pulse", 1.0]
	return [names[h % names.size()], 0.8 + 0.6 * float((h / 7) % 100) / 100.0]

func blip(key: String) -> void:
	var now = Time.get_ticks_msec()
	if now - _last_blip_ms < 45:
		return
	_last_blip_ms = now
	var v = voice_for(key)
	var st = _cue_stream("blips", str(v[0]))
	if st == null:
		return
	if _blip_player == null:
		_blip_player = AudioStreamPlayer.new()
		_blip_player.bus = "Voice" if AudioServer.get_bus_index("Voice") >= 0 else "SFX"
		add_child(_blip_player)
	_blip_player.stream = st
	_blip_player.pitch_scale = clampf(float(v[1]) * randf_range(0.97, 1.03), 0.3, 3.0)
	_blip_player.play()
