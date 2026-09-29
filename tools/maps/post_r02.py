"""Post-state Cinder Reach: T03_POST (uneven power, waterwheels, heat rotation) and T03_YARD (the old assembly
yard where Wayfarer waits; CH16: cooling channels, assembly space, Iron Tortoise, the manual, the launch)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import Grid, write

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOWN = dict(tileset="town_r02", music="M012", zone="T03", region="R02", location="L_T03", phase="post")
LEG = {"P": "pipe_tall"}


def town_post():
    g = Grid(44, 32, "#")
    g.rect(2, 22, 41, 29, ":")
    g.rect(2, 13, 41, 19, ":")
    g.rect(2, 4, 41, 10, ":")
    for (x, y) in ((10, 20), (30, 20), (20, 11)):
        g.rect(x, y, x + 2, y + 1, "s")
    g.rect(19, 30, 24, 31, ":")
    g.house(4, 23, 8, 3, chimney=6)       # canteen (heat rotated by shift)
    g.house(32, 23, 8, 4)
    g.house(4, 14, 9, 4)
    g.house(30, 14, 9, 5, chimney=3)      # clinic
    g.house(14, 4, 7, 3)
    g.text(20, 26, "<<<")                  # waterwheels at every terrace
    g.text(22, 16, "<<")
    g.text(26, 7, "<<")
    g.text(34, 8, "xx")
    g.rect(41, 5, 43, 7, ":")              # east: the assembly yard (was the Spine gate)
    for (x, y) in ((14, 26), (28, 26), (16, 17), (26, 17)):
        g.put(x, y, "l")
    g.e("spawn world 21 29 up")
    g.e("spawn from_yard 40 6 left")
    g.e("spawn default 21 29 up")
    g.e("exit 19..24 31 WORLD_POST l_t03")
    g.e("exit 43 5..7 T03_YARD from_town if=ch:CH15 locked=\"A crew chief: 'Yard's Quill's business. And Quill says he's waiting for someone who can light a lamp without burning down the street.'\"")
    g.e("npc pell_p 18 24 up sprite=pell talk=T03P_PELL")
    g.e("npc rota 12 27 up sprite=worker talk=T03P_ROTA")
    g.e("npc clinic_n 34 20 up sprite=monk talk=T03P_CLINIC")
    g.e("npc tally 6 21 right sprite=worker talk=T03P_TALLY")
    g.e("npc child_p 27 17 left sprite=child talk=T03P_CHILD wander=1")
    g.e("npc wheelwright 24 8 down sprite=worker talk=T03P_WHEEL")
    g.e("npc cook_p 9 27 up sprite=baker talk=T03P_CANTEEN")
    g.e("shop 8 28 SHOP_T03")
    g.e("inn 36 27 scene=T03P_INN")
    g.e("npc inn_p 37 27 left sprite=keeper talk=T03P_INN")
    g.e("save 16 28")
    g.decorate("cr5>l", 18, 86, ":")
    return g.emit("T03_POST", name="Cinderwake - Shared Heat", legend=LEG, save="true", **TOWN)


def yard():
    g = Grid(44, 30, "#")
    g.rect(2, 3, 41, 26, ".")
    g.rect(0, 12, 2, 15, ":")              # west: town
    g.rect(14, 8, 34, 18, ",")             # slipway
    g.rect(16, 10, 32, 16, "=")            # Wayfarer's hull on the slipway
    g.e("tileset_over 16..32 10..16 floor2 if=ch:CH16")
    # cooling channels (three), each powered by a valve on the north wall
    for i, x in enumerate((8, 22, 36)):
        g.rect(x, 4, x, 7, "p")
        g.e(f"switch channel{i+1} {x} 3 flag=t03y_ch{i+1} scene=CH16_CHANNEL{i+1}")
    # assembly space clutter (cleared by crews once channels are powered)
    g.text(6, 20, "xxcc")
    g.text(36, 20, "ccxx")
    g.e("tileset_over 6..9 20 floor if=flag:t03y_clear")
    g.e("tileset_over 36..39 20 floor if=flag:t03y_clear")
    g.put(24, 22, "t")                     # the workshop bench (the manual lies here)
    g.e("trigger 3..5 12..15 scene=CH16_YARD if=ch:CH15,!event:CH16_YARD")
    g.e("npc ivo_y 24 20 up sprite=C04 talk=CH16_IVO if=!ch:CH16")
    g.e("npc crew_y1 10 22 up sprite=worker talk=CH16_CREW if=flag:t03y_ch1,flag:t03y_ch2,flag:t03y_ch3,!flag:t03y_clear")
    g.e("npc tortoise 38 13 left sprite=tortoise talk=CH16_TORTOISE if=flag:t03y_clear,!flag:v06_given")
    g.e("npc pell_y 26 22 up sprite=pell talk=CH16_PELL if=flag:v06_given,!ch:CH16")
    g.e("read 24 23 \"The workshop bench.\" scene=CH16_BENCH")
    g.e("chest T03Y_C1 40 24 W022 1")
    g.e("save 4 24")
    g.e("spawn from_town 1 13 right")
    g.e("spawn default 1 13 right")
    g.e("exit 0 12..15 T03_POST from_yard")
    g.decorate("cr>5", 10, 87, ".")
    return g.emit("T03_YARD", name="Cinderwake - Old Assembly Yard", tileset="furnace", music="M012", zone="T03", region="R02",
                  location="L_T03", encounters="none", save="true", phase="post", legend=LEG)


if __name__ == "__main__":
    write(os.path.join(ROOT, "content_src", "maps", "post_r02.map"), [town_post(), yard()], "Post-state Cinder Reach")
    print("post_r02 written")
