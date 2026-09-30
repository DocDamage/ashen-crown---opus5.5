# Cutscene stills and title art: image brief for the owner

The game shows a full-screen still at 14 moments. Each one is already wired in: if the image is missing, the scene
simply plays without it.

## How to hand them over

- **Format:** any size in 4:3 or wider, PNG or JPG. Painted or AI images are fine. The job centre-crops to 4:3.
- **File names:** name each file by its id below (for example `ST06_dais.png`) and put it in
  `F:\Ashen Crown\The Ashen Crown\Assets\Stills\`.
- **Processing:** the job crops, resizes to 320x240, and reduces each image to 48 colours with no dithering in Aseprite, so
  every still matches the game's pixel look. With the Aseprite Job Runner open, run `python tools/art/stills_job.py`.
- **Composition:** keep the subject in the middle two thirds. The bottom quarter can be dark or plain, because
  dialogue boxes sometimes follow straight after.
- **Mature mode:** these moments are harsh but not graphic. No mature variants are needed.

## Cast references

- **Raven:** the Executioner, dark plate, a heavy blade, hood down.
- **Morwen:** the eclipse witch, a lamp and dark robes.
- **Vespera:** the moonhare warrior, rabbit ears, pink and white.
- **Golem:** a big rune-lit construct.
- **Elowen:** the moonlit grove guardian.
- **Aurex:** dragonblood, red and gold, horns.
- **Oni:** crimson armour and a mask.
- **Sak:** the cat-kingdom guardian.
- **Kitsune:** the crimson fox empress, nine tails.
- **Archangel:** a white-winged commander.

Use the hero sheets in `Assets\heroes` for likeness.

## The images

| Id | Where it plays | What it shows |
|---|---|---|
| `title` | Title screen, behind the logo | A ruined crown-shaped keep on a ridge at night, silhouetted against an ember-red horizon, with ash drifting upward. Stars in the top third, and **keep the top 40% empty for the logo**. No characters, or only a small lone figure (Raven) on the road below. Mood: grim, quiet, beautiful. |
| `ST00_opening` | The opening narration | Heartglass relay towers across a dark valley at dusk, each one pulsing pale blue. Tiny lamplit mining towns sit at their feet. Seen from high up, like a map come to life. |
| `ST01_quarry` | Crown Quarry, the first shift scene (CH01) | The quarry face: terraced grey stone and wooden lifts. Workers with lamps are lined up. A ministry inspector in a clean coat stands on a platform. Raven, in Crown plate, sits at the edge of the frame, turned away from the inspector. |
| `ST04_collapse` | CH07b, the Heartglass Face collapses | The quarry face cracking open from inside. Blue heartglass bleeds light through the fractures, workers run, and a dust cloud rolls toward the viewer. |
| `ST05_deep_glow` | CH07b, the shaft into the Deep | Looking straight down a vast shaft into warm dark. Far below, a forge-orange glow outlines the shape of something enormous: a sleeping dragon's spine of rock. |
| `ST06_dais` | CH12, the Crown Dais before Rook | A round stone dais high above the Conduit. Three relay pylons light around it and cast long shadows. Rook kneels at the centre in a tattered cloak. The party stands at the edge in silhouette, with Raven in front. |
| `ST07_lift` | CH12, the rescuers go back | The lift cage hangs on a fraying cable over a collapsing aqueduct. Five figures drop over the rail into the dust below (small, backlit). The ones who stay grip the bars. |
| `ST08_fault` | CH12, the catastrophe | Wide and apocalyptic. The coastline splits along glowing fault lines, and dragon-shaped rock formations rise out of plains and sea. The Crown's bell tower rings, with a visible shockwave. The sky is split between night and fire. |
| `ST09_rootwell` | After CH12, the Bound in the Rootwell (only if heroes were lost) | A cave of giant roots under the drowned Conduit. A green, smokeless fire in the middle. Five silhouettes sit around it; one or two are subtly wrong (bone-pale, brass-jointed, or glowing with an ember inside). Keep them silhouettes, because the party varies. |
| `ST10_hearthward` | CH13, Raven wakes | A floating refugee harbour made of cargo pontoons lashed together on a dark sea. Iron-drum fires and lanterns on ropes. Raven lies on a cot in the foreground, with Aurex beside him. |
| `ST11_launch` | CH16, the Lanternwake takes off | An unfinished rescue airship lifts off a flooded shipyard at dawn. Crews cheer on the scaffolds, water pours off the hull, and the lanterns along the gunwale are lit. |
| `ST12_crown_heart` | CH22, arrival at Crown Heart | The airship docking at a colossal crown-shaped relay citadel over the Ember Sea. Arcs of blue energy run between its spires. The party is tiny on the deck. |
| `ST13_dawn` | CH24, the last morning | The rebuilt Hearthward harbour at sunrise. Two ordinary workers replace a lamp part on a post while the party watches from a distance. Warm, quiet and hopeful. The only bright still in the set. |

## Optional extras (not wired yet; say if you want them)

- a still for each ancient dragon's first appearance (the four wyrms);
- a still for the Unmade Crown;
- a credits backdrop.
