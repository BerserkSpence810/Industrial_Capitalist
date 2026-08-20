"""Integration regressions -- these boot the REAL game loop headless via the QA
harness and drive it with synthetic input, so they cover behaviour that pure
data tests cannot: blueprint paste, pollution rates, save/load fidelity.

    python3 tests/test_integration.py
"""
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from support.harness import run_scenario                      # noqa: E402
from support.gameplay import (boot_new_game, boot_existing_game, skip_tutorial,      # noqa: E402
                       reset_slot, build_machine, power_link, tile,
                       tile_to_screen, world_summary)
from support.fixtures import place_raw                       # noqa: E402
from pygame.locals import *                               # noqa: E402,F403

SLOT = 3          # a scratch slot; never touches the player's slot 1
RESULTS = []


def check(cond, msg):
    RESULTS.append((bool(cond), msg))


# -- blueprint power connections --------
def _scen_blueprint(bot):
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    yield from build_machine(bot, 11, 14, 15)      # solar
    yield from build_machine(bot, 2, 15, 15)       # coal drill
    yield from power_link(bot, (14, 15), (15, 15))
    check(tile(bot, 14, 15)["power_connections"] == [(15, 15)],
          "power mode wires source -> target")

    yield from bot.key(K_g); yield from bot.idle(3)
    x0, y0 = tile_to_screen(bot, 14, 15)
    x1, y1 = tile_to_screen(bot, 15, 15)
    yield from bot.drag(x0, y0, x1, y1)
    yield from bot.idle(4)
    bp = bot.g("ui").blueprint
    check(bp is not None, "G + drag captures a blueprint")
    links = [m.get("power_links") for m in bp["machines"]]
    check([[1, 0]] in links, f"capture stores power links (got {links})")

    sx, sy = tile_to_screen(bot, 22, 15)
    yield from bot.click(sx, sy)
    yield from bot.idle(6)
    src = tile(bot, 22, 15)
    check(src.get("type") == 11, "blueprint pasted the solar panel")
    check((23, 15) in (src.get("power_connections") or []),
          f"paste restored the power link (got {src.get('power_connections')})")
    yield from bot.idle(120)
    check(tile(bot, 23, 15).get("power", 0) > 0,
          "the pasted drill actually receives power")


# -- exhaust stack + scrubber --------
def _measure(bot, seconds=10, base=100.0):
    bot.ns["pollution"] = base
    yield from bot.idle(4)
    p0 = bot.g("pollution")
    yield from bot.idle(int(seconds / 0.05))
    bot.rate = (bot.g("pollution") - p0) / seconds


def _scen_pollution(bot):
    from settings import MACHINE_STATS, MACHINE_DEFS
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    ns = bot.ns

    yield from _measure(bot)
    check(abs(bot.rate) < 1e-9, f"empty world does not drift ({bot.rate})")

    stack_rate = MACHINE_DEFS[110]["disperse_rate"]
    place_raw(ns, 110, 20, 20, 0)
    yield from _measure(bot)
    check(abs(bot.rate + stack_rate) < 1e-6,
          f"unpowered exhaust stack removes {stack_rate}/s (measured {-bot.rate})")
    check(bot.g("ui").pollution_scrubbed > 0,
          "the stack is reported in the statistics ledger")

    place_raw(ns, 21, 24, 20, 0)                # scrubber, no power yet
    yield from _measure(bot)
    check(abs(bot.rate + stack_rate) < 1e-6,
          f"an unpowered scrubber does nothing (measured {-bot.rate})")
    check(tile(bot, 24, 20).get("scrubbing") == 0.0,
          "an unpowered scrubber reports itself idle")

    place_raw(ns, 118, 27, 22, 0)               # test power rig
    ns["grid"][22][27]["power_connections"] = [(24, 20)]
    yield from bot.idle(60)
    scrub_rate = MACHINE_STATS[21]["scrub_rate"]
    yield from _measure(bot)
    check(abs(bot.rate + stack_rate + scrub_rate) < 1e-6,
          f"powered scrubber removes {scrub_rate}/s on top of the stack "
          f"(measured {-bot.rate})")
    check(tile(bot, 24, 20).get("scrubbing", 0) > 0,
          "a powered scrubber reports itself active")
    ui = bot.g("ui")
    check(abs(ui.pollution_scrubbed - (stack_rate + scrub_rate)) < 1e-6,
          f"statistics ledger totals both ({ui.pollution_scrubbed})")


# -- recipe labels --------
def _scen_recipe_panel(bot):
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    place_raw(bot.ns, 38, 20, 14, 0)            # Concrete Plant
    bot.ns["grid"][14][20]["recipe_mode"] = "clay_bricks"
    sx, sy = tile_to_screen(bot, 20, 14)
    yield from bot.click(sx, sy)
    yield from bot.idle(4)
    ui = bot.g("ui")
    check(set(ui.recipe_btn_rects) == {"wet_concrete", "concrete_block", "clay_bricks"},
          f"concrete plant offers its three modes ({sorted(ui.recipe_btn_rects)})")
    # clicking a mode row must switch the recipe
    r = ui.recipe_btn_rects["concrete_block"]
    yield from bot.click(r.centerx, r.centery)
    yield from bot.idle(4)
    check(tile(bot, 20, 14).get("recipe_mode") == "concrete_block",
          f"clicking a recipe row switches mode "
          f"(got {tile(bot, 20, 14).get('recipe_mode')})")


# -- power distribution --------
def _scen_power_branch(bot):
    """Regression: a power source used to hand its entire per-tick output to
    the first connection in its list, so branching a line left every branch
    after the first permanently at zero -- reading only "NO POWER"."""
    from support.fixtures import place_raw
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    ns = bot.ns
    # a generator with plenty of headroom, wired to two storage tiles that
    # never fill (so neither can "finish" and let the other through)
    place_raw(ns, 12, 10, 10, 0)                      # Coal Generator
    ns["grid"][10][10]["coal_buffer"] = 9999
    place_raw(ns, 100, 14, 10, 0)                     # MV Battery
    place_raw(ns, 100, 14, 14, 0)                     # MV Battery
    ns["grid"][10][10]["power_connections"] = [(14, 10), (14, 14)]
    for _ in range(20):
        ns["grid"][10][10]["coal_buffer"] = 9999
        yield from bot.idle(60)
    a = tile(bot, 14, 10).get("power", 0)
    b = tile(bot, 14, 14).get("power", 0)
    check(a > 0 and b > 0,
          f"a branching power line feeds every branch (got {a:,.0f} and {b:,.0f})")
    check(min(a, b) / max(a, b, 1) > 0.2,
          f"neither branch is starved (got {a:,.0f} vs {b:,.0f})")

    # and a generator with surplus still fills several machines completely
    for i, gy in enumerate((20, 22, 24)):
        place_raw(ns, 2, 18, gy, 0)
    ns["grid"][10][10]["power_connections"] += [(18, 20), (18, 22), (18, 24)]
    for _ in range(10):
        ns["grid"][10][10]["coal_buffer"] = 9999
        yield from bot.idle(60)
    caps = [tile(bot, 18, gy).get("power", 0) for gy in (20, 22, 24)]
    check(all(c >= 900 for c in caps),
          f"a generator with surplus still tops up every machine (got {caps})")


# -- recipe modes accept their own ingredients --------
def _scen_mode_inputs(bot):
    """Regression for the recipe-mode port lock: selecting a mode used to make
    the machine refuse the very items that mode consumes, whenever the mode's
    name (which is the PRODUCT) also appeared in an input port's item list.
    That silently killed concrete, crankshafts, logic plates, lithium and gold."""
    from settings import MACHINE_STATS, MACHINE_DEFS
    from support.fixtures import place_raw
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    ns = bot.ns
    grid = ns["grid"]
    bad = []
    checked = 0
    for mid, mdef in sorted(MACHINE_DEFS.items()):
        modes = ((mdef.get("process") or {}).get("mode_recipes")) or {}
        w, h = MACHINE_STATS.get(mid, {}).get("size", (1, 1))
        if not modes or max(w, h) > 8:
            continue
        for mode, rec in modes.items():
            for y in range(3, 3 + h + 2):
                for x in range(3, 3 + w + 2):
                    grid[y][x].clear()
                    grid[y][x].update({"type": 0, "stored": None, "amount": 0,
                                       "timer": 0, "rotation": 0, "power": 0,
                                       "max_power": 0, "power_connections": []})
            place_raw(ns, mid, 4, 4, 0)
            grid[4][4]["recipe_mode"] = mode
            yield from bot.idle(1)
            for item, _qty in (rec.get("inputs") or []):
                checked += 1
                took = False
                for p in (mdef.get("input_ports") or []):
                    items = list(p.get("items") or ([p["item"]] if p.get("item") else []))
                    if item not in items:
                        continue
                    sx, sy = p["subtile"]
                    fd = tuple(p["from_dir"])
                    if ns["machine_try_receive"](grid, 4 + sx, 4 + sy, item, fd[0], fd[1], 1):
                        took = True
                        break
                if not took:
                    bad.append(f"{MACHINE_STATS[mid]['name']} mode '{mode}' refuses '{item}'")
    check(not bad, f"every recipe mode accepts its own inputs "
                   f"({checked} checked; failures: {bad[:6]})")


# -- multi-tile drills --------
def _scen_multitile_drill(bot):
    """Regression: the drill update had no origin guard, so every tile of a
    multi-tile drill mined independently. A 4x4 Quarry ran at 4x its documented
    rate along its bottom edge while twelve inner tiles filled and stalled."""
    from support.fixtures import place_raw
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    ns = bot.ns
    grid = ns["grid"]
    for mid, secs in ((32, 60), (68, 60)):
        for y in range(4, 24):
            for x in range(4, 24):
                grid[y][x].clear()
                grid[y][x].update({"type": 0, "stored": None, "amount": 0, "timer": 0,
                                   "rotation": 0, "power": 0, "max_power": 0,
                                   "power_connections": []})
        w, h = ns["MACHINE_STATS"][mid].get("size", (1, 1))
        place_raw(ns, mid, 6, 6, 0)
        for dx in range(w):
            place_raw(ns, 1, 6 + dx, 6 + h, 0)       # a pipe under each face tile
        place_raw(ns, 118, 2, 2, 0)
        grid[2][2]["power_connections"] = [(6, 6)]
        yield from bot.idle(int(secs / 0.05))
        stuck = sum(grid[6 + dy][6 + dx].get("amount", 0)
                    for dy in range(h) for dx in range(w)
                    if (dx, dy) != (0, 0))
        caught = sum(grid[6 + h][6 + dx].get("amount", 0) for dx in range(w))
        rate = caught / secs * 60.0
        advertised = 60.0 / ns["MACHINE_DEFS"][mid]["mine_time"]
        name = ns["MACHINE_STATS"][mid]["name"]
        check(stuck == 0, f"{name}: no items stranded in non-origin tiles (got {stuck})")
        check(rate <= advertised * 1.35,
              f"{name}: mines at its documented rate "
              f"({rate:.1f}/min vs {advertised:.1f}/min advertised)")


# -- generators, relays and storage --------
def _scen_power_hardware(bot):
    """Every generator produces, every pole relays, every battery charges and
    discharges. Guards the whole power layer, not just the branching fix."""
    from support.fixtures import place_raw, clear_area
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    ns = bot.ns
    MS = ns["MACHINE_STATS"]
    fuels = {12: ("coal_buffer", 999), 17: ("fuel_buffer", 99),
             106: ("input_buffer", 999), 107: ("input_buffer", 99)}
    for mid in (11, 24, 25, 26, 27, 28, 12, 17, 106, 107):
        clear_area(ns, 0, 0, 30, 30)
        place_raw(ns, mid, 4, 4, 0)
        t = ns["grid"][4][4]
        if mid in fuels:
            t[fuels[mid][0]] = fuels[mid][1]
            if mid in (17, 107):
                t["fuel_item"] = "diesel" if mid == 17 else "gasoline"
                t["input_item"] = "gasoline"
        for _ in range(8):
            if mid in fuels:
                ns["grid"][4][4][fuels[mid][0]] = fuels[mid][1]
            yield from bot.idle(50)
        check(ns["grid"][4][4].get("power", 0) > 0,
              f"{MS[mid]['name']} generates power")
    for pole, rng in ((97, 2), (98, 3), (99, 10)):
        clear_area(ns, 0, 0, 30, 30)
        place_raw(ns, 12, 2, 2, 0)
        ns["grid"][2][2]["coal_buffer"] = 999
        place_raw(ns, pole, 2 + rng + 1, 2, 0)
        place_raw(ns, 2, 2 + rng + 1, 6, 0)
        ns["grid"][2][2]["power_connections"] = [(2 + rng + 1, 2)]
        ns["grid"][2][2 + rng + 1]["power_connections"] = [(2 + rng + 1, 6)]
        for _ in range(8):
            ns["grid"][2][2]["coal_buffer"] = 999
            yield from bot.idle(60)
        check(ns["grid"][6][2 + rng + 1].get("power", 0) > 0,
              f"{MS[pole]['name']} relays power to a machine")
    for batt in (100, 101):
        clear_area(ns, 0, 0, 30, 30)
        place_raw(ns, 12, 2, 2, 0)
        ns["grid"][2][2]["coal_buffer"] = 999
        place_raw(ns, batt, 6, 2, 0)
        ns["grid"][2][2]["power_connections"] = [(6, 2)]
        for _ in range(8):
            ns["grid"][2][2]["coal_buffer"] = 999
            yield from bot.idle(60)
        check(ns["grid"][2][6].get("power", 0) > 0, f"{MS[batt]['name']} charges")
        place_raw(ns, 2, 10, 2, 0)
        ns["grid"][2][6]["power_connections"] = [(10, 2)]
        ns["grid"][2][2]["power_connections"] = []
        yield from bot.idle(200)
        check(ns["grid"][2][10].get("power", 0) > 0,
              f"{MS[batt]['name']} discharges into a machine")
    # a machine given less than it draws runs slower, it does not stop
    clear_area(ns, 0, 0, 30, 30)
    place_raw(ns, 11, 2, 2, 0)
    place_raw(ns, 8, 6, 2, 0)
    ns["grid"][2][2]["power_connections"] = [(6, 2)]
    yield from bot.idle(600)
    d = ns["grid"][2][6]
    check(0 < d.get("power", 0) < MS[8]["power_input"],
          "an underpowered machine runs at partial speed rather than stopping")


# -- scrubber residue --------
def _scen_scrubber_residue(bot):
    """Cleaning the air produces residue; when it backs up the scrubber stops,
    and it restarts once the residue has somewhere to go."""
    from support.fixtures import place_raw, clear_area
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    ns = bot.ns
    MS = ns["MACHINE_STATS"]
    clear_area(ns, 0, 0, 40, 40)
    ns["pollution"] = 100.0
    place_raw(ns, 21, 10, 10, 0)
    place_raw(ns, 118, 16, 16, 0)
    ns["grid"][16][16]["power_connections"] = [(10, 10)]
    yield from bot.idle(120)
    t = tile(bot, 10, 10)
    check(t.get("scrubbing", 0) > 0, "a powered scrubber scrubs")
    check(t.get("output_item") == "residue" and t.get("output_buffer", 0) > 0,
          f"it fills with residue ({t.get('output_buffer', 0):.2f})")

    cap = ns["MACHINE_DEFS"][21]["output_port"]["cap"]
    ns["grid"][10][10]["output_buffer"] = float(cap)
    yield from bot.idle(40)
    check(tile(bot, 10, 10).get("scrubbing", 0) == 0,
          "a scrubber full of residue stops scrubbing")
    p0 = bot.g("pollution")
    yield from bot.idle(60)
    check(abs(bot.g("pollution") - p0) < 1e-6,
          "and pollution stops falling while it is blocked")

    place_raw(ns, 29, 10, 12, 0)          # Liquid Burner under the output port
    ns["grid"][16][16]["power_connections"] = [(10, 10), (10, 12)]
    yield from bot.idle(400)
    check(tile(bot, 10, 10).get("output_buffer", 0) < cap,
          "residue drains into the Liquid Burner")
    check(tile(bot, 10, 10).get("scrubbing", 0) > 0,
          "and the scrubber resumes")
    p0 = bot.g("pollution")
    yield from bot.idle(200)
    check(bot.g("pollution") < p0, "pollution falls again")


# -- resized research stations --------
def _scen_research_station_sizes(bot):
    """RS2 at 4x4 and RS3 at 5x5 still place cleanly and still make RP."""
    from support.fixtures import place_raw, clear_area
    from geometry import machine_port_tiles
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    ns = bot.ns
    MS, MD = ns["MACHINE_STATS"], ns["MACHINE_DEFS"]
    check(MS[114]["size"] == (4, 4), f"RS2 is 4x4 ({MS[114]['size']})")
    check(MS[115]["size"] == (5, 5), f"RS3 is 5x5 ({MS[115]['size']})")
    clear_area(ns, 0, 0, 40, 40)
    rp0 = ns["research"].rp
    for mid, gx in ((114, 4), (115, 14)):
        w, h = MS[mid]["size"]
        place_raw(ns, mid, gx, 6, 0)
        place_raw(ns, 118, gx, 20, 0)
        ns["grid"][20][gx]["power_connections"] = [(gx, 6)]
        filled = sum(1 for yy in range(6, 6 + h) for xx in range(gx, gx + w)
                     if tile(bot, xx, yy).get("type") == mid)
        check(filled == w * h, f"{MS[mid]['name']} fills all {w*h} of its tiles")
    yield from bot.idle(120)
    for mid, gx in ((114, 4), (115, 14)):
        for dx, dy, travel in machine_port_tiles(mid, 0, MD, MS)[0]:
            fed = 0
            for _ in range(4):
                if ns["machine_try_receive"](ns["grid"], gx + dx, 6 + dy,
                                             "iron_ingot", travel[0], travel[1], 1):
                    fed += 1
            check(fed > 0, f"{MS[mid]['name']} accepts items at its feed port {(dx, dy)}")
    yield from bot.idle(400)
    check(ns["research"].rp > rp0,
          f"both stations generate RP ({rp0:.1f} -> {ns['research'].rp:.1f})")


# -- depots pay out --------
def _scen_depot(bot):
    """Regression: the Huge Truck Depot received into its port buffer while the
    sell path read the legacy stored/amount pair, so it filled to its cap and
    never sold anything at all."""
    from support.fixtures import place_raw
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    ns = bot.ns
    place_raw(ns, 83, 12, 6, 0)
    d = ns["MACHINE_DEFS"][83]["input_ports"][0]
    sx, sy = d["subtile"]
    fd = tuple(d["from_dir"])
    m0 = bot.g("money")
    pushed = 0
    for _ in range(600):
        if ns["machine_try_receive"](ns["grid"], 12 + sx, 6 + sy, "iron_ingot",
                                     fd[0], fd[1], 1):
            pushed += 1
    yield from bot.idle(600)
    t = tile(bot, 12, 6)
    check(pushed >= 350, f"the depot accepts its advertised capacity (took {pushed})")
    check(t.get("total_sold", 0) > 0,
          f"the Huge Truck Depot actually sells (total_sold={t.get('total_sold', 0)})")
    check(bot.g("money") > m0,
          f"selling pays out (money {m0:,.0f} -> {bot.g('money'):,.0f})")


# -- save / load --------
SNAP = os.path.join(ROOT, "qa", "out", "integration_snapshot.json")
# Structure must come back byte-identical. Buffers are still being filled by a
# running factory in the frames between saving and finishing the reload, so
# those are compared with a small tolerance instead.
EXACT_KEYS = ["type", "rotation", "power_connections", "recipe_mode",
              "input_item", "stored"]
NUMERIC_KEYS = ["power", "amount", "input_buffer", "coal_buffer"]


def _snapshot(bot):
    grid = bot.g("grid")
    out = {}
    for y, row in enumerate(grid):
        for x, t in enumerate(row):
            if not t.get("type", 0):
                continue
            rec = {k: str(t.get(k)) for k in EXACT_KEYS if k in t}
            for k in NUMERIC_KEYS:
                if k in t:
                    try:
                        rec["#" + k] = float(t[k])
                    except (TypeError, ValueError):
                        pass
            out[f"{x},{y}"] = rec
    return {"tiles": out, "money": round(bot.g("money"), 4),
            "rp": bot.g("research").rp,
            "researched": sorted(bot.g("research").researched)}


def _scen_save(bot):
    yield from boot_new_game(bot, slot=SLOT)
    yield from skip_tutorial(bot)
    ns = bot.ns
    yield from build_machine(bot, 11, 14, 15)
    yield from build_machine(bot, 2, 15, 15)
    yield from build_machine(bot, 3, 15, 16)
    yield from power_link(bot, (14, 15), (15, 15))
    place_raw(ns, 9, 20, 15, 90)
    ns["grid"][15][20]["coal_buffer"] = 4
    ns["grid"][15][20]["input_buffer"] = 2
    ns["grid"][15][20]["input_item"] = "raw_iron"
    place_raw(ns, 38, 24, 14, 270)
    ns["grid"][14][24]["recipe_mode"] = "clay_bricks"
    ns["research"].rp = 137.5
    ns["research"].researched.add("coal_power")
    yield from bot.idle(150)
    os.makedirs(os.path.dirname(SNAP), exist_ok=True)
    with open(SNAP, "w") as f:
        json.dump(_snapshot(bot), f)
    yield from bot.key(K_s, mod=KMOD_CTRL)
    yield from bot.idle(10)
    slot_world = os.path.join(ROOT, "data", f"slot_{SLOT}", "world.json")
    check(os.path.exists(slot_world), "Ctrl+S writes the save slot")


def _scen_load(bot):
    yield from boot_existing_game(bot, slot=SLOT)
    yield from bot.idle(15)
    with open(SNAP) as f:
        before = json.load(f)
    after = _snapshot(bot)
    diffs, drift = [], []
    for k in set(before["tiles"]) | set(after["tiles"]):
        b, a = before["tiles"].get(k), after["tiles"].get(k)
        if b is None or a is None:
            diffs.append(f"{k}: {'gained' if b is None else 'LOST'}")
            continue
        for f_ in set(b) | set(a):
            bv, av = b.get(f_), a.get(f_)
            if f_.startswith("#"):
                if abs(float(bv or 0) - float(av or 0)) > max(3.0, abs(float(bv or 0)) * 0.05):
                    drift.append(f"{k}.{f_}: {bv} -> {av}")
                continue
            # json turns tuples into lists on the way through the save file
            if bv != av and str(bv).replace("[", "(").replace("]", ")") != av:
                diffs.append(f"{k}.{f_}: {bv} -> {av}")
    check(not diffs, f"machine layout, rotations, wiring and recipe modes "
                     f"survive save/load exactly ({diffs[:6]})")
    check(not drift, f"machine buffers survive save/load ({drift[:6]})")
    for f_ in ("money", "rp", "researched"):
        check(str(before[f_]) == str(after[f_]),
              f"{f_} survives save/load ({before[f_]} -> {after[f_]})")
    yield from bot.idle(100)
    check(world_summary(bot)["tile_counts"], "the world still simulates after loading")


SCENARIOS = {
    "blueprint": (_scen_blueprint, True),
    "modes": (_scen_mode_inputs, True),
    "power": (_scen_power_branch, True),
    "power_hw": (_scen_power_hardware, True),
    "residue": (_scen_scrubber_residue, True),
    "rs_sizes": (_scen_research_station_sizes, True),
    "depot": (_scen_depot, True),
    "drills": (_scen_multitile_drill, True),
    "pollution": (_scen_pollution, True),
    "recipe": (_scen_recipe_panel, True),
    "save": (_scen_save, True),
    "load": (_scen_load, False),
}
ORDER = ["blueprint", "pollution", "recipe", "modes", "power", "power_hw",
         "residue", "rs_sizes", "depot", "drills", "save", "load"]


def _run_one(name):
    """main.py calls pygame.quit() when its loop ends, so each scenario needs a
    fresh process."""
    scen, fresh = SCENARIOS[name]
    if fresh:
        reset_slot(SLOT)
    d = run_scenario(scen, max_frames=8000)
    if d.error:
        check(False, f"[{name}] scenario crashed: {d.error.strip().splitlines()[-1]}")
    for ok, msg in RESULTS:
        print(("PASS\t" if ok else "FAIL\t") + msg)
    return 1 if any(not ok for ok, _ in RESULTS) else 0


def main():
    import subprocess
    fails = 0
    total = 0
    for name in ORDER:
        r = subprocess.run([sys.executable, __file__, name],
                           capture_output=True, text=True, cwd=ROOT)
        lines = [l for l in r.stdout.splitlines() if l.startswith(("PASS\t", "FAIL\t"))]
        if not lines:
            print(f"FAIL  [{name}] produced no checks")
            print("      " + (r.stderr.strip().splitlines() or ["?"])[-1])
            fails += 1
            continue
        for l in lines:
            kind, msg = l.split("\t", 1)
            print(f"{kind}  {msg}")
            total += 1
            fails += kind == "FAIL"
    print(f"\n{fails} failure(s) of {total}")
    return 1 if fails else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in SCENARIOS:
        sys.exit(_run_one(sys.argv[1]))
    sys.exit(main())
