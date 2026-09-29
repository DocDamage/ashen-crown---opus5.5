"""D05 Drowned Archive. Mechanic: match three bell tones to archive shelves; clues stay visible and replayable.
Tone glyphs are written in text as well as sound (audio is never the only channel)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMMON = dict(tileset="archive", music="M023", zone="D05", region="R03", location="L_D05")


def r01():
    g = Grid(40, 28, "~")
    g.rect(2, 4, 37, 23, ",")
    g.blob(20, 14, 12, 7, ".")
    g.rect(18, 24, 21, 27, "d")
    g.rect(18, 0, 21, 4, ".")
    g.rect(15, 1, 24, 3, "#")
    g.rect(18, 1, 21, 3, "+")
    g.scatter("'", 0.15, ",", 5)
    g.e("spawn world 19 26 up")
    g.e("spawn from_r02 19 2 down")
    g.e("spawn default 19 26 up")
    g.e("exit 18..21 27 WORLD l_d05")
    g.e("exit 18..21 0 D05_R02 from_r01")
    g.e("trigger 17..22 20..21 scene=D05_ENTER if=!event:D05_ENTER")
    g.e("save 26 18")
    return g.emit("D05_R01", name="Drowned Archive - Tide Door", encounters="none", save="true", **COMMON)


def r02():
    g = Grid(32, 32)
    g.rect(2, 2, 29, 29, ".")
    g.rect(14, 29, 17, 31, ".")
    g.rect(0, 8, 2, 11, ".")      # west: dry gallery
    g.rect(29, 8, 31, 11, ".")    # east: wet gallery
    for (x, y) in ((8, 6), (16, 5), (24, 6)):
        g.put(x, y, "j")
    g.rect(12, 14, 19, 18, "9")
    for (x, y) in ((4, 26), (27, 26), (4, 4), (27, 4)):
        g.put(x, y, "u")
    g.e("switch bell_low 8 7 scene=D05_BELL_LOW")
    g.e("switch bell_mid 16 6 scene=D05_BELL_MID")
    g.e("switch bell_high 24 7 scene=D05_BELL_HIGH")
    g.e("sign 3 9 \"Dry Gallery door: an ANCHOR glyph. 'Opens to the low tone.'\"")
    g.e("sign 28 9 \"Wet Gallery door: a WAVE glyph. 'Opens to the middle tone.'\"")
    g.e("read 15 20 \"The nave floor is inlaid: ANCHOR = low bell (west), WAVE = middle bell (north), LANTERN = high bell (east). Ring, then walk to the matching door.\"")
    g.e("spawn from_r01 15 29 up")
    g.e("spawn from_r03 1 9 right")
    g.e("spawn from_r04 30 9 left")
    g.e("exit 14..17 31 D05_R01 from_r02")
    g.e("exit 0 8..11 D05_R03 from_r02 if=flag:d05_dry locked=\"The anchor door is sealed. It answers to a bell.\"")
    g.e("exit 31 8..11 D05_R04 from_r02 if=flag:d05_wet locked=\"The wave door is sealed. It answers to a bell.\"")
    g.e("trigger 3 8..11 scene=D05_DOOR_DRY if=!flag:d05_dry")
    g.e("trigger 28 8..11 scene=D05_DOOR_WET if=!flag:d05_wet")
    return g.emit("D05_R02", name="Drowned Archive - Bell Nave", encounters="D05", rate="0.5", **COMMON)


def r03():
    g = Grid(40, 24)
    g.rect(1, 2, 38, 21, ".")
    for x in range(4, 36, 5):
        g.rect(x, 4, x + 2, 16, "k")
    g.rect(38, 8, 39, 11, ".")
    g.rect(1, 20, 38, 21, ",")
    g.rect(0, 18, 1, 21, ".")
    g.e("read 22 18 \"Contract, pre-kingdom: 'Shared-body accords by consent, with a separation rite available to either party.'\"")
    g.e("read 9 18 \"A relay diagram. Six relays marked; a seventh line runs off the page toward 'Crown Dais - secondary'. Someone has pasted over it.\"")
    g.e("read 30 18 \"Ministry standardisation order, stamped: 'Separation rite: discontinued. Hosts: infrastructure.'\"")
    g.e("chest D05_C_R03 36 3 I005 1")
    g.e("spawn from_r02 38 9 left")
    g.e("spawn from_r05 1 19 right")
    g.e("exit 39 8..11 D05_R02 from_r03")
    g.e("exit 0 18..21 D05_R05 from_r03 if=flag:d05_vault locked=\"A lantern-glyph door. It answers to the high tone.\"")
    g.e("trigger 1 18..21 scene=D05_DOOR_VAULT if=!flag:d05_vault")
    g.e("key_note 0 0")
    return g.emit("D05_R03", name="Drowned Archive - Dry Gallery", encounters="D05", rate="0.8", **COMMON)


def r04():
    g = Grid(32, 28, "~")
    g.rect(1, 2, 30, 4, ".")
    g.rect(0, 2, 1, 5, ".")
    g.rect(28, 20, 30, 26, ".")
    # submerged route above safe stepping blocks
    g.path([(4, 5), (4, 10), (8, 10), (8, 14), (14, 14), (14, 18), (20, 18), (20, 22), (28, 22), (28, 26)], "w", 2)
    g.e("chest D05_C_R04 20 3 I017 2")
    # clue-led secret on a side island
    g.rect(24, 8, 28, 11, ",")
    g.rect(21, 10, 23, 10, "w")
    g.path([(14, 14), (14, 10), (24, 10)], "w")
    g.e("chest D05_SECRET_CHEST 27 9 A005 1 acq=D05_SECRET")
    g.e("read 2 3 \"A diver's slate: 'Hearth token left on the east shelf-island. Mind the old steps.'\"")
    g.e("spawn from_r02 1 3 right")
    g.e("spawn from_r05 29 25 up")
    g.e("exit 0 2..5 D05_R02 from_r04")
    g.e("exit 28..30 27 D05_R05 from_r04")
    g.rect(28, 27, 30, 27, ".")
    return g.emit("D05_R04", name="Drowned Archive - Wet Gallery", encounters="D05", rate="0.9", **COMMON)


def r05():
    g = Grid(40, 32)
    g.blob(20, 16, 16, 12, ".")
    g.rect(36, 16, 39, 19, ".")
    g.rect(18, 0, 21, 4, ".")
    g.rect(17, 26, 22, 31, ".")
    g.rect(13, 4, 16, 7, "k")
    g.rect(23, 4, 26, 7, "k")          # shelves flank the stair to the roof
    g.e("trigger 14..25 14 scene=D05_CUSTODIAN if=!flag:b05_done")
    g.e("trigger 14..25 20 scene=D05_CUSTODIAN if=!flag:b05_done")
    g.e("npc rook_vault 26 10 left sprite=rook talk=D05_ROOK_TALK if=flag:b05_done,!ch:CH06")
    g.e("spawn from_r03 38 17 left")
    g.e("spawn from_r04 19 29 up")
    g.e("spawn from_r06 19 2 down")
    g.e("exit 39 16..19 D05_R03 from_r05")
    g.e("exit 17..22 31 D05_R04 from_r05")
    g.e("exit 18..21 0 D05_R06 from_r05 if=flag:b05_done")
    g.e("save 30 22")
    g.e("heal 32 22")
    return g.emit("D05_R05", name="Drowned Archive - Witness Vault", encounters="none", save="true", **COMMON)


def r06():
    g = Grid(32, 24, "~")
    g.rect(4, 6, 27, 16, ".")
    g.rect(14, 16, 17, 23, ".")
    g.rect(12, 2, 19, 6, "d")
    g.put(16, 1, "6")
    g.put(10, 8, "j")
    g.e("trigger 12..19 8..9 scene=CH06_ROOF if=!ch:CH06")
    g.e("spawn from_r05 15 22 up")
    g.e("exit 14..17 23 D05_R05 from_r06")
    return g.emit("D05_R06", name="Drowned Archive - Roof Pier", encounters="none", **COMMON)


if __name__ == "__main__":
    blocks = [r01(), r02(), r03(), r04(), r05(), r06()]
    blocks = [b.replace("key_note 0 0\n", "") for b in blocks]
    write(os.path.join(ROOT, "content_src", "maps", "d05_archive.map"), blocks, "D05 Drowned Archive")
    print("d05 written")
