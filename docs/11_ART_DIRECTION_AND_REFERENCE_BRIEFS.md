# Art direction and production reference briefs

## Visual contract

The target is dense, carefully composed, low-resolution 2D fantasy—not a modern 3D scene filtered to look pixelated. The world and characters use visible pixel clusters, controlled outlines, a consistent light direction and intentional color ramps. Background detail must not destroy the silhouette of the player or an interactable. Keep the screen readable at its native 320×240 size before judging a large upscale.

Use a 320×240 game viewport with integer upscale and letterboxing. Logical terrain tiles are 16×16. Composite structures may occupy many tiles; there is no requirement that a roof or tree fit in one square. World heroes use a 24×32 transparent canvas with a consistent foot baseline; their visible silhouette may differ. Party battle sprites use 48×64 canvases. Ordinary enemy canvases use 32×32, 48×48 or 64×64 as approved per silhouette. Boss canvases may reach 128×160, but the composition must leave space for every actor, effects and the command panel.

Render nearest-neighbor at integer scale, with integer camera alignment when practical. Do not animate the world through fractional image resampling. The Godot resolution documentation explains viewport and integer-scaling options; test the actual project setting names in the pinned engine. This package’s exact dimensions and layout are original design choices. [S5]

## Battle-screen layout contract

Reserve pixels y=168–239 for the main command/status panel and y=0–167 for the battle arena. Use four readable staggered party slots rather than stacking four 64-pixel canvases vertically: suggested foot anchors are (224, 80), (280, 96), (224, 136), and (280, 152). Review actual visible sprite bounds, not only transparent canvas bounds. Front/back defensive row is shown by a clear status marker and must not be inferred incorrectly from the two-column staging. The boss occupies the left/center with an ordinary safe art envelope of x=16–160 and y=8–160. Move oversized VFX to an overlay without obscuring target focus or required UI. Reduced UI/font modes must reflow these panels rather than clipping them. These are initial layout constraints for visual review, not an already rendered screen.

## Palette system

Maintain a shared neutral ramp, warm skin/stone ramp, crimson/ember ramp, teal/water ramp, green/vegetation ramp, violet/memory ramp and gold/light ramp. Local scenes use a subset and may have a few scene-specific accents. Darkness uses cool colored shadows, not a uniform black overlay. Light effects must retain stepped pixel shapes rather than becoming blurred modern bloom.

Before generating hundreds of assets, define palette swatches and approve one world hero, one NPC, one ordinary enemy, one boss, one room and one battle background together. A reference board communicates intent; it is not an animation sheet and cannot be sliced into usable frames merely because it looks game-like.

## Asset inventory and frame rules

| Asset class | Production requirement | Review gate |
| --- | --- | --- |
| 8 world heroes | Each: 4 directions × (1 idle + 4 walk frames), plus 6 neutral/emotive poses; 26 frames minimum | Foot baseline, direction, silhouette and color identity match across frames. |
| 8 battle heroes | Each: idle 4, attack 6, cast 4, hurt 2, guard 2, victory 4, KO 1, step 4; 27 frames minimum | Weapon hand and body volume stay consistent; role-specific leap/device poses may add frames. |
| 8 portrait sets | Neutral, concern, determined expression per character | Same costume, facial features and species as both sprite forms. |
| Town NPC library | 12 reusable role silhouettes plus distinctive treatment for recurring named NPCs | Recoloring alone must not make every town look identical. |
| 40 normal enemies | Unique silhouette or clearly authored shape identity; idle, attack, hurt and defeat presentation | A color swap is a variant, not a new identity. |
| 16 bosses | Distinct base art; telegraph poses; phase-specific effects | Every tell must remain readable with reduced flashes enabled. |
| Environments | Farm/river, capital, furnace, coast/archive, cliffs, basin/vault, refugee harbor and crown machinery families | Each family supports floor, wall, edge, props, doorway and collision metadata. |
| Two overworld states | Same location identity with changed terrain, collision and landing zones | The player recognizes the transformation. |
| UI | Panels, cursors, gauges, affinity/status icons, equipment icons, map markers | Legible at native scale, no reliance on color alone. |
| Ability effects | Shared effect primitives plus a specific visual identity for every spell family and all 8 summons | Effects do not obscure intent, HP, target or input focus. |

These are requirements for the future game, not assets supplied in this package. Each generated/source asset must have a manifest entry with relative path, dimensions, frame layout, palette, animation timings, author/source, license status and approval status. A contact sheet is useful for reviewing a sheet; a contact sheet is not proof that the engine’s slicing, pivots and animation work.

## Programmatic art policy

An agent may generate deterministic simple sprites, tiles, icons and effects in code. Store its seed, palette and generator version. Do not declare final quality merely because every required PNG exists. Inspect contact sheets for inconsistent limbs, weapons switching hands, jitter, duplicate frames and flat silhouettes. Inspect assets inside the running game against the intended composition.

Do not secretly replace the game with colored rectangles to satisfy a screenshot-count test. Development placeholders must be labelled in the asset ledger and removed or explicitly retained as an outstanding limitation. Reusing shapes and palettes is encouraged; copying copyrighted sprite sheets, maps, portraits or title treatments is not part of this brief.

## Revision 2026-09-29 — FF6-inspired direction (owner request)

This section supersedes the size numbers above where they differ.

Target: the look and feel of a mid-90s Square SNES RPG (Final Fantasy VI as the reference), with **original** or
properly-licensed art. No FF6 assets, characters, logos or UI graphics are copied — only the conventions below.

### Screen and grid
- Internal viewport stays 320x240 (FF6 is 256x224); 16x16 tiles; integer scaling, nearest filtering.
- Field camera 3/4 top-down, light from the upper left.

### Colour
- Every material uses a 3–5 step ramp. Shadows shift cool (violet/blue), highlights shift warm (cream/yellow).
- No pure black except character outlines and void. Mid-saturation, earthy base, with a few saturated accents
  (red cloth, gold trim, magic light). Night/interior scenes lean blue-violet.
- Texture is made from 2–4 px clusters, never single-pixel noise. Dithering only in skies and large gradients.

### Terrain (field)
- Transitions are autotiled: grass overhangs dirt with a tufted fringe and a dark under-lip; water has a light
  foam line and a darker depth band at shorelines; paths have soft ragged edges.
- Cliffs: bright top lip, vertical striated face in 3 tones, dark contact shadow at the base.
- Buildings and tall props cast a soft dark shadow onto the ground to the right/below.
- Towns: timber/stone/brick walls with visible courses, steep roofs with shingle rows and ridge caps, lit windows.

### Characters
- Field sprites use the Time Fantasy frame (26x36 canvas, ~16x28 visible, big head, dark outline) when library
  art is installed; the generated fallback is 16x24 in the same proportions.
- Walk cycle: stand / step / stand / step. Idle breathing optional.
- Battle: party in side view on the right facing left; ready, attack, cast, hurt, KO, victory poses.

### Enemies and battle
- Enemies are large and painterly compared to the party (48–96 px; bosses up to 160 px), rich ramps, no hard
  outline (dark selective edge only), lit from the upper left.
- Backdrops: painted panorama — sky/ceiling band, silhouette layers, a detailed midground, and a textured ground
  plane with perspective. 16–32 colours each.

### UI
- Windows: vertical blue gradient fill (light royal blue at top to deep navy at bottom), rounded 2 px bevelled
  silver/white border. White text with a dark drop shadow; grey for disabled; pale blue labels (HP/MP/LV).
- Pointing-hand cursor. Battle HUD: bottom window split into enemy names (left) and party name/HP/ATB (right).
- Dialogue box full-width at top or bottom with portrait at left.

### Asset sources
- Base look: the owner's licensed Time Fantasy (finalbossblues) packs — steampunk, sewers, ruins, ashlands,
  winter, fairy forest, jungle, beach, cloud, Future Fantasy, dark dimension, final tower, monsters.
- Those packs forbid redistributing raw files, so they are never committed. `python tools/gen_art.py library`
  copies/assembles them from the owner's library (`ASHEN_LIB`) into `game/assets/ext/` (git-ignored); the
  runtime prefers `ext/` and falls back to the programmatic art in `tools/art/`, so the public repo still runs.
- Every imported asset is recorded in `reports/asset_ledger.json` with source pack and licence. Packs licensed
  only for RPG Maker, or based on third-party IP (Batman, Spider-Man, X-Men, Street Fighter, Fantastic Four),
  are not used. Credits for used packs go in `game/licenses/`.

## Six visual reference prompts

These are **reference-image prompts**, not generated images or runtime assets. Their role is to establish composition and art direction. Their labels are for the asset workflow and should not be drawn as visible annotations unless requested.

### REF01 — Brackenford playable exploration

Create an original 4:3 pixel-art gameplay reference at a logical 320×240 composition: a compact riverside quarry-workers’ town, viewed from classic top-down three-quarter perspective. Show low timber-and-stone houses, a shared bakery with warm windows, laundry crossing a narrow street, vegetable boxes beside an industrial rail line, lunch carts, water and a visible route toward a quarry gate. Place a small crimson-scaled knight in charcoal armor at the foot of the central path, with a cobalt-coated young mage a few paces behind. Keep consistent 16-pixel terrain logic and 24×32 character proportions. Prioritize readable walking space, layered roofs and purposeful props. No 3D rendering, depth-of-field blur, modern bloom, copied game characters, giant quest arrows or photorealistic texture.

### REF02 — Battle against the Extractor Warden

Create an original low-resolution 4:3 JRPG battle-screen reference. A huge brass-and-black digging machine occupies the left half of a quarry chamber; its raised clamp and glowing pressure gauge telegraph a forthcoming strike. Dain, a crimson-scaled armored knight, and Tessa, a cobalt-coated mage with amber spectacles, stand on the right at consistent ground baselines. Use detailed but readable pixel clusters and a lower command/status panel with space for names, HP/MP and readiness gauges. Show one focused fire effect, not a screen-filling bloom. Preserve clear separation among enemy silhouette, targets and UI. Do not reproduce a known game’s exact window borders or font.

### REF03 — Eight-character identity board

Create an original pixel-character direction board with eight separated characters on a plain dark-neutral background. Show Dain’s crimson scales and charcoal armor; Tessa’s cobalt coat and amber spectacles; Corren’s ochre scarf and flight harness; Ivo’s gray curls and copper tool rig; Nera’s moss cape and map tube; Oriel’s ivory stole and plum dress; Sable’s black-violet coat and scarred forearm; Pip’s rust waistcoat and green sash. Use one consistent world-sprite scale and a larger matching portrait above each. Distinguish silhouettes, ages, body shapes and posture. This is a reference board, not a claimed production spritesheet; do not imply an exact frame grid.

### REF04 — One world, two states

Create a side-by-side original pixel-art world-map reference with two equally sized 4:3 maps. Left: a river capital, farm belt, copper industrial ridge, eastern port, northeastern cliffs and a pale northern basin. Right: the same recognizably aligned geography after a relay catastrophe, with fractured coasts, new islands, flooded lower port streets, exposed dark machinery and a small refugee harbor in the new central sea. Preserve landmark identity. Use symbolic tile-scale mountains, forests and towns rather than a painted satellite map. Include a small original repair-built airship silhouette, not a famous vehicle replica. No UI labels are required.

### REF05 — Memory Vault room and staging

Create an original 4:3 gameplay reference of a salt-and-mineral memory sanctuary in strict low-resolution pixel art. Concentric rooms use lilac mineral walls, dark plum shadows, low water channels and warm amber record lamps. Three visibly different testimony installations surround a quiet central pool. Show space for a party to walk around them and a readable doorway at the bottom. Dain and Oriel face a small fox-shaped light, with no spectacle overpowering the conversation. Architecture should communicate listening and preservation, not a generic crystal dungeon. No anti-aliased painted gradients or HD-2D lighting.

### REF06 — Menu and equipment screen

Create an original 4:3 low-resolution RPG equipment-menu reference with deliberate pixel typography and clean dark-blue/charcoal panels accented in muted gold. Show a party column, a matching character portrait, weapon/offhand/head/body/two-accessory slots, and a before/after stat comparison. Include room for readable command descriptions. The active focus must be unmistakable without depending only on color. Keep ornament restrained and information hierarchy strong. Do not copy a specific commercial RPG’s borders, exact icons or logo. Text can be a visual placeholder in this reference; runtime text must later be rendered by the engine, not baked into the image.

## Required runtime screenshots

Capture the title, Brackenford, one interior, a normal battle, B01’s tell, equipment screen, world map before, world map after, Hearthward, a reunion scene, airship landing, two-party formation, final boss and ending. Record source commit/content hash, engine version, window/internal resolution, save/route fixture and the exact capture method. Do not substitute generated concept images for game screenshots.
