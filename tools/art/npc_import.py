"""Townsfolk importer: Assets/_processed/townsfolk sheets (5 cols stand + 4 walk; rows south, west, east, north; 129px
cells; adults ~62px) -> game/assets/ext/npcs/<stem>/field.png + field.json (same layout as heroes: rows down, left,
right, up; column 0 standing), cropped to a common cell with the feet aligned; plus npcs/npc_map.json mapping the game's
NPC sprite keys to candidate townsfolk (the game picks one per NPC id for variety)."""
import os, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.environ.get("ASHEN_ASSETS", os.path.join(os.path.dirname(REPO), "Assets"))
SRC = os.path.join(ASSETS, "_processed", "townsfolk")
OUT = os.path.join(REPO, "game", "assets", "ext", "npcs")

MAP = {
    "worker": ["cozy_village/village_blacksmith", "kingdom_citizens/village_blacksmith", "steampunk/clockwork_engineer_male",
               "steampunk/young_apprentice_engineer_free_character", "cozy_village/fisherman"],
    "elder": ["cozy_village/village_elder", "kingdom_citizens/elder_scholar"],
    "survivor": ["cozy_village/fisherman", "cozy_village/flower_gardener", "cozy_village/shepherd_girl",
                 "cozy_village/village_farmer", "kingdom_citizens/herbalist", "kingdom_citizens/tavern_waitress"],
    "guard": ["kingdom_citizens/royal_guard"],
    "soldier": ["kingdom_citizens/royal_guard", "dark_gothic/dark_fantasy_gothic_knight_pixel"],
    "child": ["cozy_village/village_kid_free"],
    "keeper": ["kingdom_citizens/tavern_keeper", "cozy_village/traveling_merchant", "kingdom_citizens/traveling_merchant", "cozy_village/caf_owner"],
    "monk": ["cozy_village/librarian", "kingdom_citizens/elder_scholar", "psych_horror/the_weeping_nun_female"],
    "pilot": ["steampunk/airship_captain_male", "steampunk/sky_navigator"],
    "farmer": ["cozy_village/village_farmer"],
    "baker": ["cozy_village/village_baker", "kingdom_citizens/village_baker"],
    "sailor": ["cozy_village/fisherman", "atlantis/sea_dragon_hunter"],
    "scholar": ["kingdom_citizens/elder_scholar", "cozy_village/librarian"],
    "patient": ["cozy_village/shepherd_girl", "cozy_village/flower_gardener"],
    "mara": ["steampunk/clockwork_huntress_female"],
    "inspector": ["steampunk/iron_baron_male"],
    "noble": ["kingdom_citizens/noble_lady"],
    "clerk": ["kingdom_citizens/guild_receptionist"],
    "apprentice": ["steampunk/young_apprentice_engineer_free_character"],
    "volunteer": ["cozy_village/shepherd_girl"],
    "pell": ["kingdom_citizens/traveling_merchant"],
    "jori": ["steampunk/sky_navigator"],
    "edda": ["kingdom_citizens/herbalist"],
    "ansel": ["cozy_village/librarian"],
    "sen": ["samurai_yokai/shrine_maiden_warrior_female"],
    "rook": ["dark_dungeon/shadow_dungeon_assassin_male"],
}
ROWS = [("down", 0), ("left", 1), ("right", 2), ("up", 3)]
CELL = 129


def bbox(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else None


def build(stem):
    im = Image.open(os.path.join(SRC, stem + ".png")).convert("RGBA")
    cols = im.width // CELL
    frames = {}
    for d, r in ROWS:
        frames[d] = [np.array(im.crop((c * CELL, r * CELL, (c + 1) * CELL, (r + 1) * CELL))) for c in range(cols)]
    boxes = [bbox(f) for fs in frames.values() for f in fs if bbox(f)]
    x0 = min(b[0] for b in boxes) - 1
    x1 = max(b[2] for b in boxes) + 1
    y0 = min(b[1] for b in boxes) - 1
    feet = max(b[3] for b in boxes)
    x0, x1, y0, feet = int(x0), int(x1), int(y0), int(feet)
    cw, ch = x1 - x0, feet - y0 + 1
    sheet = Image.new("RGBA", (cw * cols, ch * 4), (0, 0, 0, 0))
    for d, r in ROWS:
        for c, f in enumerate(frames[d]):
            sheet.paste(Image.fromarray(f).crop((x0, y0, x1, feet + 1)), (c * cw, r * ch))
    dst = os.path.join(OUT, stem.replace("/", "__"))
    os.makedirs(dst, exist_ok=True)
    sheet.save(os.path.join(dst, "field.png"))
    json.dump({"cell": [cw, ch], "foot": [int(CELL / 2 - x0), ch - 1], "fps": 7,
               "rows": {d: {"row": r, "n": cols - 1} for d, r in ROWS}}, open(os.path.join(dst, "field.json"), "w"))


def main():
    os.makedirs(OUT, exist_ok=True)
    stems = sorted({s for v in MAP.values() for s in v})
    for s in stems:
        build(s)
    json.dump({k: [s.replace("/", "__") for s in v] for k, v in MAP.items()}, open(os.path.join(OUT, "npc_map.json"), "w"), indent=1)
    print("npcs:", len(stems), "sheets,", len(MAP), "sprite keys")


if __name__ == "__main__":
    main()
