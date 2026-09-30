// Ashen Crown weather haze (fog banks, sandstorm dust, ash pall): drifting value-noise layers on a ColorRect
// covering the view. Visual only; driven by src/field/weather_fx.gd. Pixel-snapped to match the art.
shader_type canvas_item;

uniform vec4 haze_color : source_color = vec4(0.8, 0.82, 0.86, 1.0);
uniform float density : hint_range(0.0, 1.0) = 0.4;
uniform vec2 drift = vec2(0.02, 0.0);
uniform float scale = 3.0;
uniform vec2 screen_size = vec2(960.0, 720.0);
uniform float pixel_size = 3.0;
uniform float script_time = 0.0;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	float a = hash(i);
	float b = hash(i + vec2(1.0, 0.0));
	float c = hash(i + vec2(0.0, 1.0));
	float d = hash(i + vec2(1.0, 1.0));
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

void fragment() {
	vec2 grid = screen_size / pixel_size;
	vec2 p = (floor(UV * grid) + 0.5) / grid;
	vec2 q = p * vec2(scale * 1.33, scale) + drift * script_time;
	float n = noise(q) * 0.55 + noise(q * 2.1 + vec2(3.7, 1.3) - drift * script_time * 0.6) * 0.3 + noise(q * 4.3) * 0.15;
	float a = smoothstep(0.25, 0.85, n) * density;
	// a little more at the top of the view (farther away on the tilted world)
	a *= mix(1.15, 0.8, p.y);
	COLOR = vec4(haze_color.rgb, clamp(a, 0.0, 1.0) * haze_color.a);
}
