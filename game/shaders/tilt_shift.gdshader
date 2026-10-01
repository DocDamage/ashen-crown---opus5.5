shader_type canvas_item;
// HD-2D tilt-shift: the band around the player stays sharp; the far top and the near bottom of the view soften,
// with a faint bloom of bright pixels and a vignette. Reads what the field drew beneath it.
uniform sampler2D screen_tex : hint_screen_texture, filter_linear;
uniform float focus_y = 0.55;
uniform float band = 0.22;
uniform float strength = 2.6;
uniform float vignette = 0.28;

void fragment() {
	vec2 uv = SCREEN_UV;
	float d = max(0.0, abs(uv.y - focus_y) - band) / (1.0 - band);
	float r = strength * d * d * 4.0;
	vec2 px = SCREEN_PIXEL_SIZE * r;
	vec3 c = texture(screen_tex, uv).rgb * 0.2;
	c += texture(screen_tex, uv + vec2(px.x, 0.0)).rgb * 0.1;
	c += texture(screen_tex, uv - vec2(px.x, 0.0)).rgb * 0.1;
	c += texture(screen_tex, uv + vec2(0.0, px.y)).rgb * 0.1;
	c += texture(screen_tex, uv - vec2(0.0, px.y)).rgb * 0.1;
	c += texture(screen_tex, uv + px * 0.7).rgb * 0.1;
	c += texture(screen_tex, uv - px * 0.7).rgb * 0.1;
	c += texture(screen_tex, uv + vec2(px.x, -px.y) * 0.7).rgb * 0.1;
	c += texture(screen_tex, uv + vec2(-px.x, px.y) * 0.7).rgb * 0.1;
	vec3 base = texture(screen_tex, uv).rgb;
	vec3 bright = max(base - vec3(0.78), vec3(0.0));
	c += bright * 0.35;
	vec2 q = uv - vec2(0.5, 0.52);
	float v = 1.0 - vignette * smoothstep(0.32, 0.78, length(q * vec2(1.0, 1.25)));
	COLOR = vec4(c * v, 1.0);
}
