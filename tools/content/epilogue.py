"""Post-game epilogue arc (QEPI): encounters for the Belfry Below, the bonus dungeon under drowned Veyr.
Its four floors are hand-made maps in content_src/maps/x_epi.map; scenes in content_src/scenes/x_epi.scn; the boss is
BX27 (tools/content/bosses2.py). Enemies are late-game regulars re-levelled to the post-game band (84-92)."""

FORMS = [
    (["E115", "E115", "E114"], 84), (["E117", "E114"], 85), (["E116"], 87), (["E107", "E107", "E109"], 86),
    (["E108", "E111"], 88), (["E087", "E087", "E088"], 88), (["E120", "E112"], 90), (["E116", "E117"], 92),
]


def apply(FM):
    names = []
    for i, (ids, lv) in enumerate(FORMS):
        fid = "EPI_%d" % (i + 1)
        FM.FORMATIONS[fid] = FM.F([FM.v(e, lv + k % 2) for k, e in enumerate(ids)], "reef" if i < 3 else "crown_core")
        names.append(fid)
    FM.GROUPS["W_EPI"] = names
    apply_guards(FM)


# undersea sealed spots (field systems s3 follow-up): the guardians behind the Tithe's hold and the Oath Gate
GUARDS = {"S3G_TITHE": (["E117", "E117", "E114"], 42, "reef"), "S3G_OATH": (["E120", "E120"], 44, "crown")}


def apply_guards(FM):
    for fid, (ids, lv, bg) in GUARDS.items():
        FM.FORMATIONS[fid] = FM.F([FM.v(e, lv) for e in ids], bg)
