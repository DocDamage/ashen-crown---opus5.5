"""Mature mode markup check (sys s4). Scene lines may carry `{m:strong|mild}`: the strong wording shows with Mature
on, the mild one otherwise (either may be empty). Game.mature_filter() applies it at runtime; `if mature <label>` /
`if !mature <label>` branch whole passages; art variants are `<name>_m.png` files beside the art.
This check makes sure every marker is closed, has one `|`, and never nests."""
import re

MARK = re.compile(r"\{m:([^{}]*)\}")


def check(scenes, err):
    n = 0
    for sid, sc in scenes.items():
        for c in sc["cmds"]:
            texts = [c.get("text", "")] + [o["text"] for o in c.get("options", [])]
            for t in texts:
                if "{m:" not in t:
                    continue
                rest = MARK.sub("", t)
                if "{m:" in rest:
                    err(f"{sid}: malformed mature markup: {t[:60]}")
                for body in MARK.findall(t):
                    if body.count("|") != 1:
                        err(f"{sid}: mature markup needs one '|': {body}")
                    n += 1
    return n
