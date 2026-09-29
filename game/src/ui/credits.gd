class_name CreditsView
extends Control
## Credits with original-asset provenance and third-party notices.

signal closed
var t = 0.0
var lines = [
	["THE ASHEN CROWN", 1], ["", 0], ["An original pixel-art JRPG", 0], ["", 0],
	["Design package", 1], ["The Ashen Crown handoff v0.1", 0], ["", 0],
	["Implementation, content, art, music", 1], ["Built autonomously by Claude (Anthropic)", 0],
	["from the design package, in Godot 4.7.2", 0], ["", 0],
	["Art", 1], ["Character sprites: Time Fantasy (Elements,", 0], ["Beast Tribes, NPC animations) by finalbossblues", 0],
	["timefantasy.net - see licenses/ART_CREDITS.txt", 0], ["Portraits and other art: project code (tools/art).", 0], ["", 0],
	["Music and sound", 1], ["All cues are synthesized by tools/gen_audio.py.", 0],
	["Development-grade programmatic audio; replaceable", 0], ["cue by cue without code changes.", 0], ["", 0],
	["Font", 1], ["'Ashen8' bitmap font, original to this project.", 0], ["", 0],
	["Engine", 1], ["Godot Engine 4.7.2 (MIT license)", 0], ["Copyright (c) 2014-present Godot Engine contributors.", 0],
	["Copyright (c) 2007-2014 Juan Linietsky, Ariel Manzur.", 0], ["Notices: licenses/GODOT_LICENSE.txt,", 0], ["licenses/GODOT_COPYRIGHT.txt (third-party)", 0], ["", 0],
	["Thank you for playing.", 1],
]

func _ready() -> void:
	size = Vector2(320, 240)
	Audio.music("M030")

var garden_t = -1.0   # post-credits image: an unlit relay repurposed as a public garden
var done = false

func handle(ev: String) -> void:
	if ev in ["confirm", "cancel"]:
		if garden_t >= 1.0:
			_finish()
		elif t > 1.0 and garden_t < 0.0:
			garden_t = 0.0

func _finish() -> void:
	if not done:
		done = true
		emit_signal("closed")

func _process(d: float) -> void:
	if garden_t >= 0.0:
		garden_t += d
		if garden_t > 7.0:
			_finish()
	else:
		t += d * (4.0 if Input.is_action_pressed("g_confirm") else 1.0)
		if 240 - t * 18 + lines.size() * 13 < -20:
			garden_t = 0.0
	queue_redraw()

func _draw_garden() -> void:
	var a = clampf(garden_t / 1.5, 0.0, 1.0)
	# dawn sky and harbour ground
	for i in range(12):
		draw_rect(Rect2(0, i * 12, 320, 12), Color8(40 + i * 12, 60 + i * 10, 110 + i * 6).lerp(Color8(8, 8, 14), 1.0 - a))
	draw_rect(Rect2(0, 144, 320, 96), Color8(58, 74, 52).lerp(Color8(8, 8, 14), 1.0 - a))
	draw_rect(Rect2(0, 144, 320, 3), Color8(90, 110, 70).lerp(Color8(8, 8, 14), 1.0 - a))
	# the relay: a dark, cracked glass housing, no light inside
	var rc = Color8(52, 58, 72).lerp(Color8(8, 8, 14), 1.0 - a)
	draw_rect(Rect2(140, 70, 40, 78), rc)
	draw_rect(Rect2(136, 64, 48, 8), Color8(80, 70, 60).lerp(Color8(8, 8, 14), 1.0 - a))
	draw_rect(Rect2(136, 146, 48, 6), Color8(80, 70, 60).lerp(Color8(8, 8, 14), 1.0 - a))
	draw_line(Vector2(150, 76), Vector2(158, 100), Color8(90, 100, 120, int(255 * a)), 1)
	draw_line(Vector2(158, 100), Vector2(152, 120), Color8(90, 100, 120, int(255 * a)), 1)
	# vines and beds planted around and up the housing
	var g = Color8(70, 150, 70, int(255 * a))
	for k in range(6):
		var x0 = 138 + k * 9
		var h = int(20 + 50 * clampf((garden_t - 1.0 - k * 0.3) / 2.5, 0.0, 1.0))
		for yy in range(0, h, 4):
			draw_rect(Rect2(x0 + (1 if (yy / 4) % 2 == 0 else -1), 146 - yy, 2, 4), g)
	var cols = [Color8(230, 120, 140), Color8(240, 210, 90), Color8(150, 170, 250), Color8(240, 240, 240)]
	for k in range(22):
		var fx = 40 + (k * 53) % 240
		var fy = 156 + (k * 29) % 60
		draw_rect(Rect2(fx, fy, 3, 3), Color(cols[k % 4], a))
		draw_rect(Rect2(fx + 1, fy + 3, 1, 3), g)
	# a bench and a watering can: ordinary use
	draw_rect(Rect2(210, 150, 36, 4), Color8(120, 84, 52, int(255 * a)))
	draw_rect(Rect2(212, 154, 3, 8), Color8(90, 62, 40, int(255 * a)))
	draw_rect(Rect2(241, 154, 3, 8), Color8(90, 62, 40, int(255 * a)))
	draw_rect(Rect2(100, 160, 8, 6), Color8(150, 160, 170, int(255 * a)))
	UI.text_center(self, 160, 222, "The relay garden, Hearthward.", Color(UI.C_DIM, a))

func _draw() -> void:
	if garden_t >= 0.0:
		_draw_garden()
		return
	_draw_credits()

func _draw_credits() -> void:
	draw_rect(Rect2(0, 0, 320, 240), Color8(8, 8, 14))
	var y = 240 - t * 18
	for l in lines:
		if y > -12 and y < 244:
			UI.text_center(self, 160, y, l[0], UI.C_GOLD if l[1] == 1 else UI.C_TEXT)
		y += 13
