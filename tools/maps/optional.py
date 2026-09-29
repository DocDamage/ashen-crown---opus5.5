"""Optional post-state content: quest rooms (D04P, D05P, D08P, D07P_R03, D02P_SEALS) and the optional airship
dungeons D11 Cradle of Winter (Q09, B13) and D12 Starless Reef (Q10, B14)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------- quest rooms at existing dungeon locations
def d04p():
    g = Grid(40, 26, "#")
    g.rect(2, 3, 37, 22, ".")
    g.rect(17, 22, 22, 25, ":")
    g.text(15, 6, "mmmmmmmmmm")          # the new engine (waterwheel-driven, no heartglass)
    g.text(18, 5, "<<<<")
    g.put(20, 10, "t")                    # manual lectern
    g.e("spawn world 19 24 up")
    g.e("spawn default 19 24 up")
    g.e("exit 17..22 25 WORLD_POST l_d04")
    g.e("read 20 10 \"The engine manual.\" scene=Q04_MANUAL")
    g.e("npc q4w1 8 12 right sprite=worker talk=Q04_WORKER1")
    g.e("npc q4w2 31 12 left sprite=worker talk=Q04_WORKER2")
    g.e("npc q4w3 20 17 up sprite=apprentice talk=Q04_WORKER3")
    g.e("switch restart 24 9 scene=Q04_RESTART if=qs:Q04:revised")
    g.e("npc crew_d4 5 20 right sprite=worker talk=D04P_CREW")
    g.e("save 34 20")
    g.decorate("cr>5", 12, 126, ".")
    return g.emit("D04P_R01", name="Furnace Spine - Waterwheel Engine House", tileset="furnace", music="M022", zone="D04P",
                  region="R02", location="L_D04", encounters="none", save="true", phase="post")


def d05p():
    g = Grid(40, 28, "w")
    g.rect(3, 3, 36, 8, ".")
    g.rect(3, 19, 36, 24, ".")
    g.rect(17, 24, 22, 27, ".")
    g.rect(19, 8, 20, 19, "=")
    for i, (x, y) in enumerate(((6, 4), (33, 4), (6, 22))):
        g.put(x, y, "l")
        g.e(f"npc station{i+1} {x+1} {y} down sprite={('keeper','monk','worker')[i]} talk=Q02_STATION{i+1}")
    g.put(30, 21, "m")
    g.e("switch circuit 30 20 scene=Q02_CIRCUIT if=qs:Q02:observed")
    g.e("npc apprentice_q2 28 21 left sprite=apprentice talk=Q02_APPRENTICE if=q:Q02:ACTIVE")
    g.e("chest D05P_C1 35 23 I005 2")
    g.e("spawn world 19 26 up")
    g.e("spawn default 19 26 up")
    g.e("exit 17..22 27 WORLD_POST l_d05")
    g.e("read 20 20 \"A notice: 'Lantern stations are staffed. Knock, don't shout.'\"")
    g.decorate("k?", 10, 127, ".")
    return g.emit("D05P_R01", name="Drowned Archive - Lantern Stations", tileset="archive", music="M023", zone="D05P",
                  region="R03", location="L_D05", encounters="D05P", rate="0.5", phase="post")


def d08p():
    g = Grid(32, 24)
    g.rect(3, 3, 28, 20, ".")
    g.rect(14, 20, 17, 23, ".")
    g.put(15, 5, "@")                    # the automatic prognostic seal
    g.text(5, 5, "kkk")
    g.e("read 6 6 \"The original authorization.\" scene=Q06_AUTH")
    g.e("switch seal 15 6 scene=Q06_SEAL if=q:Q06:ACTIVE")
    g.e("npc q6_patient 22 10 left sprite=patient talk=Q06_PATIENT if=q:Q06:ACTIVE")
    g.e("spawn world 15 22 up")
    g.e("spawn default 15 22 up")
    g.e("exit 14..17 23 WORLD_POST l_d08")
    g.e("save 26 18")
    g.decorate("k?*", 8, 128, ".")
    return g.emit("D08P_R01", name="Memory Vault - Prognosis Room", tileset="vault", music="M024", zone="D08P", region="R05",
                  location="L_D08", encounters="none", save="true", phase="post")


def d07p_r03():
    g = Grid(32, 22)
    g.rect(3, 3, 28, 18, ".")
    g.rect(14, 18, 17, 21, ".")
    for i, x in enumerate((7, 15, 23)):
        g.put(x, 6, "@")
        g.e(f"read {x} 7 \"A binding seal.\" scene=Q07_SEAL{i+1}")
        g.e(f"npc q7occ{i+1} {x} 9 up sprite={('survivor','elder','patient')[i]} talk=Q07_OCC{i+1}")
    g.put(15, 14, "m")
    g.e("switch repeater 15 13 scene=Q07_REPEATER if=qs:Q07:recorded")
    g.e("spawn from_r02 15 20 up")
    g.e("spawn default 15 20 up")
    g.e("exit 14..17 21 D07P_R02 from_r03")
    return g.emit("D07P_R03", name="Whitebone Sanctuary - Deep Seals", tileset="whitebone", music="M008", zone="D07P", region="R05",
                  location="L_D07", encounters="none", phase="post")


def d02p_seals():
    g = Grid(28, 20)
    g.rect(3, 3, 24, 16, ".")
    g.rect(24, 8, 27, 11, ".")
    # safe puzzle chamber: three dials, clue on the wall; wrong settings just reset
    for i, x in enumerate((8, 13, 18)):
        g.put(x, 5, ">")
        g.e(f"switch dial{i+1} {x} 6 scene=Q08_DIAL{i+1}")
    g.put(13, 12, "$")
    g.e("read 13 11 \"The seal safe.\" scene=Q08_SAFE")
    g.e("read 5 4 \"Scratched by a clerk: 'River, Crown, Ledger. The order the city was built in.'\"")
    g.e("spawn from_canals 26 9 left")
    g.e("spawn default 26 9 left")
    g.e("exit 27 8..11 T02_CANALS from_seals")
    return g.emit("D02P_SEALS", name="Veyr Underways - Seal Chamber", tileset="underways", music="M011", zone="D02P", region="R01",
                  location="L_T02", encounters="none", phase="post")


# ---------------------------------------------------------------- D11 Cradle of Winter (Q09, B13, V07)
WIN = dict(tileset="winter", music="M017", zone="D11", region="R05", location="L_D11", phase="post")


def d11():
    out = []
    g = Grid(40, 28, "q")
    g.rect(16, 3, 23, 25, "i")
    g.rect(16, 25, 23, 27, ".")
    g.rect(16, 0, 23, 3, ".")
    g.put(12, 10, "!")
    g.e("spawn world 19 26 up"); g.e("spawn from_r02 19 1 down"); g.e("spawn default 19 26 up")
    g.e("exit 16..23 27 WORLD_POST l_d11")
    g.e("exit 16..23 0 D11_R02 from_r01")
    g.e("trigger 16..23 20..21 scene=Q09_CAUSEWAY if=!event:Q09_CAUSEWAY")
    g.e("save 13 12"); g.e("heal 11 12")
    g.decorate("o*", 14, 112, "q")
    out.append(g.emit("D11_R01", name="Cradle of Winter - White Causeway", encounters="D11", rate="0.5", save="true", **WIN))

    g = Grid(32, 32, "#")
    g.rect(3, 3, 28, 28, ".")
    g.rect(14, 28, 17, 31, "."); g.rect(28, 14, 31, 17, "."); g.rect(14, 0, 17, 3, ".")
    g.text(5, 6, "BB  BB  BB  BB")
    for i, x in enumerate((6, 14, 22)):
        g.e(f"npc sleeper{i+1} {x} 8 down sprite={('elder','survivor','child')[i]} talk=Q09_SLEEPER{i+1}")
    g.put(26, 20, "y")
    g.e("read 26 21 \"A figure under a blanket, perfectly still. Frost on its eyelashes. It is a carved statue - someone's memorial, not a sleeper.\"")
    g.e("spawn from_r01 15 30 up"); g.e("spawn from_r03 30 15 left"); g.e("spawn from_r04 15 1 down")
    g.e("exit 14..17 31 D11_R01 from_r02")
    g.e("exit 31 14..17 D11_R03 from_r02")
    g.e("exit 14..17 0 D11_R04 from_r02 if=flag:d11_thaw locked=\"Ice seals the north door. The warmth channels (east) could thaw it.\"")
    g.decorate("tkc", 10, 113, ".")
    out.append(g.emit("D11_R02", name="Cradle of Winter - Sleeping House", encounters="none", **WIN))

    g = Grid(40, 24, "q")
    g.rect(2, 4, 37, 19, ".")
    g.rect(0, 10, 2, 13, ".")
    g.rect(18, 0, 21, 4, ".")
    for i, x in enumerate((9, 19, 29)):
        g.put(x, 8, "!")
        g.e(f"switch heat{i+1} {x} 9 flag=d11_heat{i+1} scene=Q09_HEAT{i+1}")
    g.e("block 18..21 3..4 tile=ice if=!flag:d11_thaw msg=\"Solid ice. The three heat braziers could melt it together.\"")
    g.e("spawn from_r02 1 11 right"); g.e("spawn from_r04 19 1 down")
    g.e("exit 0 10..13 D11_R02 from_r03")
    g.e("exit 18..21 0 D11_R04 from_r03 if=flag:d11_thaw")
    g.rect(4, 12, 35, 13, "i")
    g.decorate("o*q", 16, 111, ".")
    out.append(g.emit("D11_R03", name="Cradle of Winter - Warmth Channels", encounters="D11", rate="0.6", **WIN))

    g = Grid(32, 28, "#")
    g.rect(3, 3, 28, 24, "i")
    g.rect(14, 24, 17, 27, "."); g.rect(14, 0, 17, 3, "."); g.rect(28, 20, 31, 23, ".")
    g.text(6, 6, "** **")
    g.e("chest D11_CACHE 5 22 W035 1")
    g.e("chest D11_CACHE2 26 5 G024 1")
    g.rect(22, 12, 27, 16, "#"); g.rect(23, 13, 26, 15, "."); g.put(22, 14, ".")
    g.e("chest D11_SECRET_CHEST 25 14 A011 1 acq=D11_SECRET")
    g.e("read 10 20 \"A child's scratch on the ice: 'the warm hiding place is where the light bends east.'\"")
    g.e("spawn from_r02 15 26 up"); g.e("spawn from_r03 30 21 left"); g.e("spawn from_r05 15 1 down")
    g.e("exit 14..17 27 D11_R02 from_r04")
    g.e("exit 31 20..23 D11_R03 from_r04")
    g.e("exit 14..17 0 D11_R05 from_r04")
    g.e("save 6 18")
    g.decorate("*o", 12, 114, "i")
    out.append(g.emit("D11_R04", name="Cradle of Winter - Rime Gallery", encounters="D11", rate="0.5", save="true", **WIN))

    g = Grid(40, 32, "q")
    g.blob(20, 16, 16, 12, ".")
    g.rect(18, 26, 21, 31, "."); g.rect(18, 0, 21, 5, ".")
    g.put(20, 8, "!")
    g.e("trigger 14..25 16..17 scene=Q09_B13 if=!flag:b13_done")
    g.e("spawn from_r04 19 29 up"); g.e("spawn from_r06 19 2 down")
    g.e("exit 18..21 31 D11_R04 from_r05")
    g.e("exit 18..21 0 D11_R06 from_r05 if=flag:b13_done")
    g.decorate("*o", 10, 115, "q")
    out.append(g.emit("D11_R05", name="Cradle of Winter - Lantern Cradle", encounters="none", **WIN))

    g = Grid(32, 24, "q")
    g.blob(16, 12, 12, 8, ".")
    g.rect(14, 19, 17, 23, ".")
    g.text(12, 4, "QQQQQQ")
    g.e("trigger 10..21 9..11 scene=Q09_HIND if=!flag:v07_given")
    g.e("spawn from_r05 15 21 up"); g.e("spawn default 15 21 up")
    g.e("exit 14..17 23 D11_R05 from_r06")
    out.append(g.emit("D11_R06", name="Cradle of Winter - Dawn Window", encounters="none", **WIN))
    return out


# ---------------------------------------------------------------- D12 Starless Reef (Q10, B14, V08)
REEF = dict(tileset="reef", music="M023", zone="D12", region="R06", location="L_D12", phase="post", dark="true")


def d12():
    out = []
    g = Grid(40, 28, "~")
    g.rect(10, 16, 29, 25, "d")
    g.rect(17, 25, 22, 27, "d")
    g.rect(18, 0, 21, 16, "Z")
    g.rect(19, 0, 20, 16, ",")
    g.put(14, 18, "l")
    g.e("spawn world 19 26 up"); g.e("spawn from_r02 19 1 down"); g.e("spawn default 19 26 up")
    g.e("exit 17..22 27 WORLD_POST l_d12")
    g.e("exit 18..21 0 D12_R02 from_r01")
    g.e("trigger 12..27 20..21 scene=Q10_MOORING if=!event:Q10_MOORING")
    g.e("save 25 22"); g.e("heal 23 22")
    out.append(g.emit("D12_R01", name="Starless Reef - Blackwater Mooring", encounters="none", save="true", **REEF))

    # the first beacon teaches the rhythm: a visible lamp pulses with the sound; tide hazard follows it
    g = Grid(32, 32, "~")
    g.rect(3, 3, 28, 28, ",")
    g.rect(14, 28, 17, 31, ","); g.rect(14, 0, 17, 3, ","); g.rect(28, 14, 31, 17, ",")
    g.put(15, 14, "l")
    g.e("hazard 4..27 18..21 period=4 on=1.4 phase=0")
    g.e("sign 13 26 \"The beacon lamp brightens and the bell sounds together. Then the tide surges across the reef. Cross while the lamp is dark.\"")
    g.e("spawn from_r01 15 30 up"); g.e("spawn from_r03 15 1 down"); g.e("spawn from_r04 30 15 left")
    g.e("exit 14..17 31 D12_R01 from_r02")
    g.e("exit 14..17 0 D12_R03 from_r02")
    g.e("exit 31 14..17 D12_R04 from_r02")
    g.decorate("Zo", 18, 121, ",", area=(4, 4, 27, 16))
    g.decorate("Zo6", 10, 122, ",", area=(4, 22, 27, 27))
    out.append(g.emit("D12_R02", name="Starless Reef - First Beacon", encounters="D12", rate="0.6", **REEF))

    g = Grid(40, 24, "~")
    g.rect(2, 3, 37, 20, ",")
    g.rect(18, 20, 21, 23, ","); g.rect(37, 10, 39, 13, ",")
    g.put(8, 6, "l"); g.put(31, 6, "l")
    g.e("switch reflector 20 10 scene=Q10_REFLECTOR")
    g.e("read 8 7 \"The return beacon. Keep it lit, or nobody finds the way back.\"")
    g.e("spawn from_r02 19 21 up"); g.e("spawn from_r04 38 11 left")
    g.e("exit 18..21 23 D12_R02 from_r03")
    g.e("exit 39 10..13 D12_R04 from_r03 if=flag:d12_reflector locked=\"The channel east is black. The second beacon's light doesn't reach it yet.\"")
    g.decorate("Zo6", 22, 123, ",")
    out.append(g.emit("D12_R03", name="Starless Reef - Second Beacon", encounters="D12", rate="0.6", **REEF))

    g = Grid(32, 28, "~")
    g.rect(3, 3, 28, 24, ",")
    g.rect(0, 12, 3, 15, ","); g.rect(14, 24, 17, 27, ","); g.rect(14, 0, 17, 3, ",")
    g.text(6, 5, "6666")
    g.text(8, 12, "kk.kk.kk")
    g.e("read 11 12 \"The wreck library.\" scene=Q10_REGISTER")
    g.rect(22, 18, 27, 22, "#"); g.rect(23, 19, 26, 21, ","); g.put(22, 20, ",")
    g.e("chest D12_SECRET_CHEST 25 20 A012 1 acq=D12_SECRET")
    g.e("read 6 20 \"A purser's note: 'Valuables in the aft locker, starboard. Past the bent rib.'\"")
    g.e("spawn from_r03 1 13 right"); g.e("spawn from_r02 15 26 up"); g.e("spawn from_r05 15 1 down")
    g.e("exit 0 12..15 D12_R03 from_r04")
    g.e("exit 14..17 27 D12_R02 from_r04")
    g.e("exit 14..17 0 D12_R05 from_r04 if=item:K_PASSENGER_REGISTER locked=\"The trench bell won't answer without the passenger register.\"")
    g.e("save 26 5")
    g.decorate("xc6", 12, 124, ",")
    out.append(g.emit("D12_R04", name="Starless Reef - Wreck Library", encounters="none", save="true", **REEF))

    g = Grid(40, 32, "K")
    g.blob(20, 16, 15, 11, ",")
    g.rect(18, 26, 21, 31, ","); g.rect(18, 0, 21, 5, ",")
    for (x, y) in ((8, 10), (32, 10), (8, 22), (32, 22)):
        g.put(x, y, "l")
    g.e("trigger 14..25 16..17 scene=Q10_B14 if=!flag:b14_done")
    g.e("spawn from_r04 19 29 up"); g.e("spawn from_r06 19 2 down")
    g.e("exit 18..21 31 D12_R04 from_r05")
    g.e("exit 18..21 0 D12_R06 from_r05 if=flag:b14_done")
    g.decorate("Zo", 14, 125, ",")
    out.append(g.emit("D12_R05", name="Starless Reef - Night Trench", encounters="none", **REEF))

    g = Grid(32, 24, "~")
    g.blob(16, 13, 11, 7, ",")
    g.rect(14, 19, 17, 23, ",")
    g.e("trigger 10..21 9..12 scene=Q10_LEVIATHAN if=!flag:v08_given")
    g.e("spawn from_r05 15 21 up"); g.e("spawn default 15 21 up")
    g.e("exit 14..17 23 D12_R05 from_r06")
    out.append(g.emit("D12_R06", name="Starless Reef - Open Current", encounters="none", **{**REEF, "dark": "false"}))
    return out


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "optional.map"),
          [d04p(), d05p(), d08p(), d07p_r03(), d02p_seals()] + d11() + d12(), "Optional post-state content")
    print("optional written")
