// Ashen Crown starfield (night skies, the void, airship at night). Put on a ColorRect.
// Based on "Starfield shader v5" by Brian Smith (steampunkdemon.itch.io), MIT licence.
// Changes: defaults sized for the 960x720 view, hard-edged pixel stars by default,
// scroll direction and script-driven time as uniforms.
shader_type canvas_item;

uniform vec2 dimensions = vec2(960.0, 720.0);
uniform float small_stars = 50.0;
uniform float small_stars_far_size : hint_range(0.1, 1.0, 0.1) = 0.5;
uniform float small_stars_near_size : hint_range(0.1, 1.0, 0.1) = 1.0;
uniform float large_stars = 8.0;
uniform float large_stars_far_size : hint_range(0.1, 1.0, 0.1) = 0.3;
uniform float large_stars_near_size : hint_range(0.1, 1.0, 0.1) = 0.6;
uniform vec4 far_stars_color : source_color = vec4(0.55, 0.45, 1.0, 1.0);
uniform vec4 near_stars_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float base_scroll_speed : hint_range(0.0, 1.0, 0.001) = 0.01;
uniform float additional_scroll_speed : hint_range(0.0, 1.0, 0.001) = 0.01;
uniform bool vertical = false;                         // false = scroll right-to-left, true = bottom-to-top
uniform bool hard_edges = true;                        // true suits the pixel art
uniform float pixel_size = 2.0;
uniform bool use_script_time = false;
uniform float script_time = 0.0;

float greater_than(float x, float y) { return max(sign(x - y), 0.0); }

vec2 star_uv(vec2 uv, float count, float rn, float t) {
	if (vertical) {
		return vec2(fract(uv.x * count), fract(uv.y + (base_scroll_speed + rn * additional_scroll_speed) * t) * count * dimensions.y / dimensions.x) * 2.0 - 1.0;
	}
	return vec2(fract(uv.x + (base_scroll_speed + rn * additional_scroll_speed) * t) * count * dimensions.x / dimensions.y, fract(uv.y * count)) * 2.0 - 1.0;
}

float star_rn(vec2 uv, float count) {
	return vertical ? fract(sin(floor(uv.x * count)) * dimensions.x) : fract(sin(floor(uv.y * count)) * dimensions.y);
}

void fragment() {
	float t = 10000.0 + (use_script_time ? script_time : TIME);
	vec2 grid = dimensions / pixel_size;
	vec2 uv = (floor(UV * grid) + 0.5) / grid;

	float srn = star_rn(uv, small_stars);
	vec2 suv = star_uv(uv, small_stars, srn, t);
	vec4 sc = mix(far_stars_color, near_stars_color, srn);
	float ss = small_stars_far_size + (small_stars_near_size - small_stars_far_size) * srn;
	float small_mask = hard_edges ? greater_than(ss, length(suv)) : max((ss - length(suv)) / ss, 0.0);
	COLOR.rgb = mix(COLOR.rgb, sc.rgb, small_mask * sc.a);

	float lrn = star_rn(uv, large_stars);
	vec2 luv = star_uv(uv, large_stars, lrn, t);
	vec4 lc = mix(far_stars_color, near_stars_color, lrn);
	float ls = large_stars_far_size + (large_stars_near_size - large_stars_far_size) * lrn;
	float cross = max(greater_than(ls / 10.0, abs(luv.x)), greater_than(ls / 10.0, abs(luv.y)));
	float large_mask = hard_edges
		? max(greater_than(ls / 1.7, length(luv)), greater_than(ls, length(luv)) * cross)
		: max((ls / 1.7 - length(luv)) / ls, 0.0) + max((ls - length(luv)) / ls / 2.0, 0.0) * cross;
	COLOR.rgb = mix(COLOR.rgb, lc.rgb, large_mask * lc.a);
}
