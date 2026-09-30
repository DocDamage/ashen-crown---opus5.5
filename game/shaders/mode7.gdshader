shader_type canvas_item;
// World map ground plane (FF6 Mode-7 feel): every screen pixel casts a ray from the camera onto the map plane
// and samples the baked ground chunks (a texture array, one layer per chunk). Units are field units (16 per cell);
// z is height above the ground. Mipmapped nearest sampling keeps the near ground crisp and the far ground calm.

uniform sampler2DArray ground : filter_nearest_mipmap, repeat_disable;
uniform vec3 cam_pos;
uniform vec3 fwd;
uniform vec3 right;
uniform vec3 up;
uniform float focal = 240.0;
uniform vec2 center = vec2(160.0, 120.0);
uniform vec2 view = vec2(320.0, 240.0);
uniform vec2 world_units = vec2(2816.0, 2112.0);
uniform float chunk_units = 704.0;
uniform int chunks_x = 4;
uniform int chunks_y = 3;
uniform vec4 outside : source_color = vec4(0.09, 0.17, 0.36, 1.0);
uniform vec4 sky_top : source_color = vec4(0.30, 0.46, 0.72, 1.0);
uniform vec4 sky_low : source_color = vec4(0.74, 0.82, 0.90, 1.0);
uniform vec4 haze : source_color = vec4(0.62, 0.72, 0.84, 1.0);
uniform float haze_near = 900.0;
uniform float haze_far = 2600.0;
uniform float haze_max = 0.75;
uniform vec4 tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);

void fragment() {
	vec2 s = UV * view;
	vec3 ray = fwd * focal + right * (s.x - center.x) - up * (s.y - center.y);
	vec4 col;
	if (ray.z > -0.02 * focal) {
		// sky above the horizon (with a soft band so the horizon never aliases)
		float h = clamp(ray.z / focal * 3.0 + 0.06, 0.0, 1.0);
		col = mix(sky_low, sky_top, sqrt(h));
	} else {
		float t = -cam_pos.z / ray.z;
		vec2 hit = cam_pos.xy + ray.xy * t;
		vec2 g = hit / chunk_units;
		if (hit.x < 0.0 || hit.y < 0.0 || hit.x >= world_units.x || hit.y >= world_units.y) {
			col = outside;
		} else {
			vec2 cc = min(floor(g), vec2(float(chunks_x - 1), float(chunks_y - 1)));
			vec2 local = g - cc;
			float layer = cc.y * float(chunks_x) + cc.x;
			col = textureGrad(ground, vec3(local, layer), dFdx(g), dFdy(g));
		}
		float dist = t * length(ray);
		float f = smoothstep(haze_near, haze_far, dist) * haze_max;
		// the band just under the horizon melts into the sky colour
		f = max(f, smoothstep(-0.10 * focal, -0.02 * focal, ray.z));
		col = mix(col, haze, f);
	}
	COLOR = vec4(col.rgb * tint.rgb, 1.0);
}
