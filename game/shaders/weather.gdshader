// Ashen Crown weather overlay (rain / snow). Put on a ColorRect that covers the 960x720 view,
// with the ColorRect's own colour fully transparent.
// Based on "Rain and Snow shader" by Brian Smith (steampunkdemon.itch.io), MIT licence.
// Changes: rain/snow is a uniform instead of commented code, drops snap to a pixel grid so they
// match the pixel art, and time can be driven from script so weather pauses with the game.
shader_type canvas_item;

uniform int mode : hint_range(0, 1) = 0;               // 0 = rain (streaks), 1 = snow (flakes)
uniform float amount = 200.0;                          // columns of drops across the screen
uniform float near_length : hint_range(0.01, 1.0) = 0.2;
uniform float far_length : hint_range(0.01, 1.0) = 0.1;
uniform float near_width : hint_range(0.1, 1.0) = 1.0;
uniform float far_width : hint_range(0.1, 1.0) = 0.5;
uniform float near_alpha : hint_range(0.0, 1.0) = 0.8;
uniform float far_alpha : hint_range(0.0, 1.0) = 0.4;
uniform vec4 drop_color : source_color = vec4(0.8, 0.85, 0.95, 1.0);
uniform float base_speed : hint_range(0.0, 2.0) = 0.5;
uniform float extra_speed : hint_range(0.0, 2.0) = 0.5;
uniform float slant : hint_range(-1.0, 1.0) = 0.2;
uniform vec2 screen_size = vec2(960.0, 720.0);
uniform float pixel_size = 2.0;                        // 1 = native pixels, 2 = match the 2x backdrops
uniform bool use_script_time = false;                  // set true and drive script_time to pause weather
uniform float script_time = 0.0;

void fragment() {
	float t = 10000.0 + (use_script_time ? script_time : TIME);
	vec2 grid = screen_size / pixel_size;
	vec2 p = (floor(UV * grid) + 0.5) / grid;          // snap to the pixel grid

	float x = p.x - p.y * slant;
	float remainder = mod(x, 1.0 / amount);
	float col = x - remainder;
	float rn = fract(sin(col * amount) * 43758.5453);
	float y = fract(p.y + rn);
	float len = far_length + (near_length - far_length) * rn;
	float phase = fract(y - t * (base_speed + extra_speed * rn));
	float width_mask = step(remainder * amount, far_width + (near_width - far_width) * rn);
	float alpha = far_alpha + (near_alpha - far_alpha) * rn;

	float drop;
	if (mode == 0) {
		drop = smoothstep(1.0 - len, 1.0, phase);      // streak with a trail
	} else {
		drop = step(1.0 - len * 0.02, phase);          // short flake (a pixel or two), no trail
	}
	COLOR = vec4(drop_color.rgb, drop * width_mask * alpha * drop_color.a);
}
