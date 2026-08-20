"""Regression tests for the bugs found during QA.

These are pure-data / pure-logic tests: they import the game's real modules and
exercise the real functions, but never open a window. Run with:

    python3 -m pytest tests -q          (or: python3 tests/test_regressions.py)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from settings import (MACHINE_STATS, MACHINE_DEFS, BUILD_CATEGORIES,
                      ITEM_VALUES, REFINERY_RECIPES)
from research import TECH_TREE
from geometry import rotate_port


# -- port geometry --------
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
_EDGE = {UP: "top", DOWN: "bottom", LEFT: "left", RIGHT: "right"}


def _required_edge(direction, is_input):
    d = tuple(direction)
    if is_input:                 # an item travelling d enters through face -d
        d = (-d[0], -d[1])
    return _EDGE.get(d)


def _ports(mdef):
    out = []
    for p in (mdef.get("input_ports") or []):
        out.append(("input", p.get("subtile"), p.get("from_dir"), True))
    for key in ("output_port", "output_port2"):
        op = mdef.get(key)
        if op:
            out.append((key, op.get("subtile"), op.get("push_dir"), False))
    if mdef.get("output_subtile") is not None:
        out.append(("fluid_out", mdef["output_subtile"], mdef.get("push_dir"), False))
    return out


def test_every_port_sits_on_the_edge_it_faces():
    """A port whose subtile is not on the matching footprint edge is
    unreachable -- the tile a player wires to belongs to the same machine.
    This is the 'nothing in that tile' class of bug."""
    bad = []
    for mid, mdef in MACHINE_DEFS.items():
        w, h = MACHINE_STATS.get(mid, {}).get("size", (1, 1))
        for kind, sub, d, is_in in _ports(mdef):
            assert sub is not None and d is not None, (mid, kind)
            sx, sy = tuple(sub)
            assert 0 <= sx < w and 0 <= sy < h, (mid, kind, sub, (w, h))
            edge = _required_edge(d, is_in)
            ok = {"top": sy == 0, "bottom": sy == h - 1,
                  "left": sx == 0, "right": sx == w - 1}[edge]
            if not ok:
                bad.append((mid, MACHINE_STATS.get(mid, {}).get("name"), kind, sub, d, (w, h)))
    assert not bad, f"ports not on their own edge: {bad}"


def test_ports_stay_inside_the_footprint_when_rotated():
    """Rotation must map every port to a tile of the rotated footprint and turn
    its direction with it -- checked for all four rotations of every machine."""
    bad = []
    for mid, mdef in MACHINE_DEFS.items():
        tw, th = MACHINE_STATS.get(mid, {}).get("size", (1, 1))
        for rot in (0, 90, 180, 270):
            w, h = (th, tw) if rot % 180 else (tw, th)
            for kind, sub, d, is_in in _ports(mdef):
                sx, sy = tuple(sub)
                rx, ry, rd, _, _ = rotate_port(0, 0, sx, sy, tw, th, tuple(d), rot)
                if not (0 <= rx < w and 0 <= ry < h):
                    bad.append((mid, kind, rot, (rx, ry), (w, h)))
                    continue
                edge = _required_edge(rd, is_in)
                ok = {"top": ry == 0, "bottom": ry == h - 1,
                      "left": rx == 0, "right": rx == w - 1}[edge]
                if not ok:
                    bad.append((mid, MACHINE_STATS.get(mid, {}).get("name"),
                                kind, rot, (rx, ry), rd, (w, h)))
    assert not bad, f"rotated ports off their edge: {bad}"


# -- recipes --------
def test_port_views_have_one_source_of_truth():
    """The Z overlay and the placement preview both read geometry.
    machine_port_tiles. Every tile it reports must lie inside the rotated
    footprint and sit on the face its direction points at -- otherwise one of
    the two views is drawing a marker where nothing can connect."""
    from geometry import machine_port_tiles
    bad = []
    for mid in MACHINE_STATS:
        if mid == 0:
            continue
        tw, th = MACHINE_STATS[mid].get("size", (1, 1))
        for rot in (0, 90, 180, 270):
            w, h = (th, tw) if (rot // 90) % 2 else (tw, th)
            ins, outs = machine_port_tiles(mid, rot, MACHINE_DEFS, MACHINE_STATS)
            for dx, dy, travel in ins:
                if not (0 <= dx < w and 0 <= dy < h):
                    bad.append((mid, "input outside footprint", rot, (dx, dy), (w, h)))
                    continue
                edge = _required_edge(travel, True)
                if not {"top": dy == 0, "bottom": dy == h - 1,
                        "left": dx == 0, "right": dx == w - 1}[edge]:
                    bad.append((mid, f"input not on its {edge} edge", rot, (dx, dy), (w, h)))
            for dx, dy, push in outs:
                if not (0 <= dx < w and 0 <= dy < h):
                    bad.append((mid, "output outside footprint", rot, (dx, dy), (w, h)))
                    continue
                edge = _required_edge(push, False)
                if not {"top": dy == 0, "bottom": dy == h - 1,
                        "left": dx == 0, "right": dx == w - 1}[edge]:
                    bad.append((mid, f"output not on its {edge} edge", rot, (dx, dy), (w, h)))
    assert not bad, f"port views disagree with the footprint: {bad[:6]}"


def test_wide_machines_expose_their_whole_face():
    """A 4x4 Quarry really pushes from all four bottom tiles and a Coal
    Generator really takes coal on either top tile; the views must say so
    rather than drawing a single marker in the middle."""
    from geometry import machine_port_tiles
    _ins, outs = machine_port_tiles(32, 0, MACHINE_DEFS, MACHINE_STATS)
    assert len(outs) == 4, f"Quarry should expose 4 output tiles, got {outs}"
    ins, _outs = machine_port_tiles(12, 0, MACHINE_DEFS, MACHINE_STATS)
    assert len(ins) == 2, f"Coal Generator should expose 2 input tiles, got {ins}"


def test_scrubber_produces_residue_it_can_get_rid_of():
    """Cleaning the air captures waste. The scrubber needs an output port for
    it, and something in the game has to accept it."""
    d = MACHINE_DEFS[21]
    stats = MACHINE_STATS[21]
    assert d.get("scrubber"), "machine 21 should still be the scrubber"
    port = d.get("output_port")
    assert port, "the scrubber has no output port for its residue"
    w, h = stats["size"]
    sx, sy = port["subtile"]
    assert 0 <= sx < w and 0 <= sy < h, (sx, sy, (w, h))
    assert tuple(port["push_dir"]) == (0, 1) and sy == h - 1, \
        "the residue port should sit on the bottom edge and push down"
    assert stats.get("residue_rate", 0) > 0, "no residue rate set"
    assert port.get("cap", 0) > 0, "the residue buffer needs a cap so it can back up"
    takers = [m for m, md in MACHINE_DEFS.items()
              for p in (md.get("input_ports") or [])
              if "residue" in list(p.get("items") or
                                   ([p["item"]] if p.get("item") else []))]
    assert takers, "nothing in the game accepts residue"


def test_exhaust_stack_stays_clean():
    """The stack disperses rather than capturing, so unlike the scrubber it
    should make no waste - that is the trade-off between the two."""
    assert not (MACHINE_DEFS[110].get("output_port")), \
        "the exhaust stack should not produce residue"
    assert MACHINE_STATS[110].get("power_input", 0) == 0


def test_multi_tile_machines_have_sane_footprints():
    """Caught a one-character typo that shrank Research Station 1 from (2,2) to
    (2,1) -- it still placed, still ran, and nothing complained, it just quietly
    lost half itself. Anything with a name like a big machine should be big."""
    for mid, stats in MACHINE_STATS.items():
        if mid == 0:
            continue
        w, h = stats.get("size", (1, 1))
        assert w >= 1 and h >= 1, (mid, (w, h))
        # every tile of the footprint has to be reachable on the grid
        assert w <= 40 and h <= 40, f"{stats.get('name')} is bigger than the map"
    known = {13: (2, 2), 114: (4, 4), 115: (5, 5), 12: (2, 2), 21: (2, 2),
             110: (2, 3), 14: (3, 3), 32: (4, 4), 38: (4, 4)}
    for mid, expect in known.items():
        assert MACHINE_STATS[mid]["size"] == expect, (
            f"{MACHINE_STATS[mid]['name']} should be "
            f"{expect[0]}x{expect[1]}, got {MACHINE_STATS[mid]['size']}")


def test_research_station_footprints_fit_their_ports():
    """RS2 is 4x4 and RS3 is 5x5; every feed port has to land on the top edge
    inside that footprint."""
    assert MACHINE_STATS[114]["size"] == (4, 4), MACHINE_STATS[114]["size"]
    assert MACHINE_STATS[115]["size"] == (5, 5), MACHINE_STATS[115]["size"]
    for mid in (114, 115):
        w, h = MACHINE_STATS[mid]["size"]
        ports = MACHINE_DEFS[mid]["input_ports"]
        assert ports, f"{mid} has no feed port"
        seen = set()
        for p in ports:
            sx, sy = p["subtile"]
            assert 0 <= sx < w and 0 <= sy < h, \
                f"machine {mid} port {(sx, sy)} is outside its {w}x{h} footprint"
            assert sy == 0 and tuple(p["from_dir"]) == (0, 1), \
                f"machine {mid} port {(sx, sy)} should be fed from above"
            assert (sx, sy) not in seen, f"machine {mid} has two ports on {(sx, sy)}"
            seen.add((sx, sy))


def test_mode_recipes_declare_their_inputs():
    """The machine panel builds its 'Needs:' list from recipe['inputs'].
    Every mode recipe must have one, or the panel silently shows nothing."""
    missing = []
    for mid, mdef in MACHINE_DEFS.items():
        for key, rec in ((mdef.get("process") or {}).get("mode_recipes") or {}).items():
            if not rec.get("inputs"):
                missing.append((mid, MACHINE_STATS.get(mid, {}).get("name"), key))
    assert not missing, f"mode recipes with no declared inputs: {missing}"


def test_mode_recipe_inputs_match_the_buffers_they_consume():
    """Regression for the Concrete Plant class of bug: what a recipe says it
    needs must be something its input ports can actually hold."""
    bad = []
    for mid, mdef in MACHINE_DEFS.items():
        holds = {}
        for p in (mdef.get("input_ports") or []):
            items = list(p.get("items") or ([p["item"]] if p.get("item") else []))
            holds.setdefault(p["buf"], []).extend(items)
        for key, rec in ((mdef.get("process") or {}).get("mode_recipes") or {}).items():
            names = {i for i, _q in (rec.get("inputs") or [])}
            for buf in (rec.get("extra_consume") or {}):
                if buf not in holds:
                    bad.append((mid, key, f"consumes {buf} which no port fills"))
                elif holds[buf] and names and not names & set(holds[buf]):
                    bad.append((mid, key, f"consumes {buf} {holds[buf]} but needs {sorted(names)}"))
    assert not bad, bad


def test_every_recipe_output_has_a_sell_value():
    missing = []
    for mid, mdef in MACHINE_DEFS.items():
        proc = mdef.get("process") or {}
        outs = []
        if proc.get("produce"):
            outs.append(proc["produce"])
        for rec in (proc.get("mode_recipes") or {}).values():
            if rec.get("produce"):
                outs.append(rec["produce"])
        for v in (proc.get("recipe_map") or {}).values():
            if isinstance(v, (tuple, list)) and v:
                outs.append(v[0])
        for o in outs:
            if o not in ITEM_VALUES:
                missing.append((mid, o))
    for k, v in REFINERY_RECIPES.items():
        if v.get("produce") not in ITEM_VALUES:
            missing.append((16, v.get("produce")))
    assert not missing, f"outputs with no ITEM_VALUES entry: {missing}"


# -- tech tree --------
def test_tech_tree_is_well_formed():
    ids = [t["id"] for t in TECH_TREE]
    assert len(ids) == len(set(ids)), "duplicate tech ids"
    for t in TECH_TREE:
        for r in t["requires"]:
            assert r in ids, f"{t['id']} requires missing tech {r}"
        assert t["unlocks"], f"{t['id']} unlocks nothing"


def test_no_tech_is_unreachable():
    """Every tech must be researchable by repeatedly taking whatever has all
    its prerequisites met -- i.e. no dependency cycles."""
    done, ids = set(), {t["id"]: t for t in TECH_TREE}
    changed = True
    while changed:
        changed = False
        for tid, t in ids.items():
            if tid not in done and all(r in done for r in t["requires"]):
                done.add(tid)
                changed = True
    assert done == set(ids), f"unreachable techs: {sorted(set(ids) - done)}"


def test_every_machine_is_buildable_and_every_unlock_exists():
    build_ids = {m for _cat, ids in BUILD_CATEGORIES for m in ids}
    stat_ids = set(MACHINE_STATS) - {0}
    assert not (stat_ids - build_ids), f"machines with no build entry: {sorted(stat_ids - build_ids)}"
    assert not (build_ids - stat_ids), f"build entries with no stats: {sorted(build_ids - stat_ids)}"
    for t in TECH_TREE:
        for m in t["unlocks"]:
            assert m in build_ids, f"{t['id']} unlocks {m} which is not in any build category"


def test_research_stations_2_and_3_are_in_the_tree():
    """RS2/RS3 must be present and actually reachable -- the tree is the only
    place a player can find them."""
    unlocked = {m: t for t in TECH_TREE for m in t["unlocks"]}
    for mid in (114, 115):
        assert mid in unlocked, f"Research Station machine {mid} is not unlocked by any tech"
    rs2, rs3 = unlocked[114], unlocked[115]
    assert rs3["cost"] > rs2["cost"], "RS3 should cost more RP than RS2"
    assert rs2["id"] in rs3["requires"] or any(
        rs2["id"] in TECH_TREE[i]["requires"] for i, _ in enumerate(TECH_TREE)), \
        "RS3 should sit downstream of RS2"


def test_no_prerequisite_free_tech_is_a_cost_outlier():
    """Regression for the refining entry point: oil_extraction used to be a
    400 RP tech with no prerequisites, 3.3x the next most expensive one, and
    above the 200 RP soft cap a single Research Station 1 can reach."""
    free = [t for t in TECH_TREE if not t["requires"]]
    costs = sorted(t["cost"] for t in free)
    assert costs[-1] <= 200, (
        f"a prerequisite-free tech costs {costs[-1]} RP, above what one "
        f"Research Station 1 can bank (200): "
        f"{[t['name'] for t in free if t['cost'] > 200]}")


# -- pollution balance --------
def test_powered_scrubber_beats_the_passive_exhaust_stack():
    """The Exhaust Stack used to remove 0.004 %/s for free while the Scrubber
    removed 0.005 %/s for 5 kME/s plus research -- the powered machine has to
    be the stronger one or it has no reason to exist."""
    stack = MACHINE_DEFS[110]["disperse_rate"]
    scrub = MACHINE_STATS[21]["scrub_rate"]
    assert MACHINE_STATS[110].get("power_input", 0) == 0, "the stack is meant to be passive"
    assert MACHINE_STATS[21]["power_input"] > 0, "the scrubber is meant to need power"
    assert scrub > stack * 2, (
        f"scrubber {scrub}/s is not decisively better than the free stack {stack}/s")


def test_research_station_1_is_powerable_alongside_a_starting_income():
    """A fresh save has $1500 and only Solar Panels for power. The tutorial's
    opening build is Coal Drill + Van Depot + Solar for income, and then a
    Research Station 1. All of that has to fit inside the starting capital, or
    the player spends minutes idling before the first research point exists.
    At the original 2100 ME/s draw this needed 8 panels and cost $1685."""
    rs1, solar, drill, depot = (MACHINE_STATS[13], MACHINE_STATS[11],
                                MACHINE_STATS[2], MACHINE_STATS[3])
    panels = -(-rs1["power_input"] // solar["power_output"])
    # one extra panel keeps the drill running next to the station
    total = (drill["cost"] + depot["cost"] + rs1["cost"]
             + (panels + 1) * solar["cost"])
    assert total <= 1500, (
        f"the opening build costs ${total}: Coal Drill + Van Depot + "
        f"Research Station 1 + {panels + 1} Solar Panels "
        f"({rs1['power_input']} ME/s at {solar['power_output']} ME/s each), "
        f"but a new save starts with $1500")


def test_every_depot_can_reach_its_own_selling_point():
    """A depot sells at capacity x sell_threshold, but items land in its input
    port's buffer, which has its own cap. The Huge Truck Depot advertised 350
    capacity behind a 200-cap port, so it filled up and never sold anything."""
    bad = []
    for mid, st in MACHINE_STATS.items():
        if st.get("type") != "depot":
            continue
        cap = st.get("sell_capacity", st.get("capacity", 10))
        sell_at = cap * st.get("sell_threshold", 1.0)
        for p in ((MACHINE_DEFS.get(mid) or {}).get("input_ports") or []):
            if p.get("cap") is not None and sell_at > p["cap"]:
                bad.append(f"{st['name']}: sells at {sell_at:g} but its port holds "
                           f"only {p['cap']:g}")
    assert not bad, bad


def test_recipe_mode_resolver_uses_the_recipe_not_the_mode_name():
    """Regression for the recipe-mode port lock. main.mode_input_items must
    report a mode's real ingredients; the old code filtered ports by the mode
    NAME, which is the product, so machines refused their own inputs."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_ic_main_src", os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "main.py"))
    src = open(spec.origin).read()
    start = src.index("def mode_input_items(")
    end = src.index("def machine_try_receive(")
    ns = {"MACHINE_DEFS": MACHINE_DEFS, "_MODE_INPUT_CACHE": {}}
    exec(compile(src[start:end], "main.py", "exec"), ns)
    mode_input_items = ns["mode_input_items"]

    # a machine with no mode_recipes must return None (Diesel Refinery keeps
    # the old name-based behaviour, where the mode really is the input)
    assert mode_input_items(16, "crude_oil") is None

    checked = 0
    for mid, mdef in MACHINE_DEFS.items():
        for mode, rec in (((mdef.get("process") or {}).get("mode_recipes")) or {}).items():
            allowed = mode_input_items(mid, mode)
            assert allowed is not None, f"{mid}/{mode}"
            for item, _q in (rec.get("inputs") or []):
                checked += 1
                assert item in allowed, (
                    f"{MACHINE_STATS[mid]['name']} mode '{mode}' would refuse "
                    f"its own input '{item}'")
    assert checked > 50, f"only checked {checked} recipe inputs"


# -- blueprints --------
def test_blueprint_entries_round_trip_power_links():
    """Power wiring is part of a layout; the library must persist it and must
    not share the list between the clipboard and the stored copy."""
    from blueprints import BlueprintLibrary
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        lib = BlueprintLibrary(os.path.join(d, "bp.json"))
        clip = {"w": 2, "h": 1, "machines": [
            {"dx": 0, "dy": 0, "type": 11, "rotation": 0,
             "recipe_mode": None, "power_links": [[1, 0]]},
            {"dx": 1, "dy": 0, "type": 2, "rotation": 0,
             "recipe_mode": None, "power_links": []}]}
        lib.add("cell", clip)
        clip["machines"][0]["power_links"].append([9, 9])   # must not leak in
        lib2 = BlueprintLibrary(os.path.join(d, "bp.json"))
        stored = lib2.blueprints[0]["machines"][0]
        assert stored["power_links"] == [[1, 0]], stored["power_links"]


def test_blueprint_strings_round_trip():
    """Export -> string -> import must preserve position, type, rotation,
    recipe mode and power wiring exactly."""
    from blueprints import BlueprintLibrary as BL
    bp = {"name": "Iron Cell", "w": 6, "h": 4, "machines": [
        {"dx": 0, "dy": 0, "type": 11, "rotation": 0,
         "recipe_mode": None, "power_links": [[1, 0], [3, 2]]},
        {"dx": 1, "dy": 0, "type": 8, "rotation": 90,
         "recipe_mode": None, "power_links": []},
        {"dx": 3, "dy": 2, "type": 38, "rotation": 270,
         "recipe_mode": "clay_bricks", "power_links": []},
    ]}
    text = BL.encode(bp)
    assert text.startswith("IC1:"), text
    assert " " not in text and "\n" not in text
    back = BL.decode(text)
    assert back["w"] == bp["w"] and back["h"] == bp["h"]
    assert back["name"] == "Iron Cell"
    assert back["machines"] == bp["machines"], back["machines"]


def test_blueprint_strings_survive_whitespace_and_wrapping():
    """Players paste these out of chat and text files."""
    from blueprints import BlueprintLibrary as BL
    bp = {"name": "x", "w": 1, "h": 1, "machines": [
        {"dx": 0, "dy": 0, "type": 2, "rotation": 0,
         "recipe_mode": None, "power_links": []}]}
    text = BL.encode(bp)
    mangled = text[:20] + "\n  " + text[20:40] + " \t" + text[40:]
    assert BL.decode(mangled)["machines"] == bp["machines"]


def test_blueprint_strings_reject_junk_with_a_readable_message():
    from blueprints import BlueprintLibrary as BL
    for bad, expect in [("", "Nothing to import"),
                        ("hello", "Not a blueprint string"),
                        ("IC9:abc", "Unsupported blueprint version"),
                        ("IC1:!!!!", "corrupt")]:
        try:
            BL.decode(bad)
            raise AssertionError(f"accepted junk: {bad!r}")
        except ValueError as e:
            assert expect.lower() in str(e).lower(), (bad, str(e))


def test_blueprint_strings_reject_unknown_machine_ids():
    """A string from a newer build must fail loudly, not place nothing."""
    from blueprints import BlueprintLibrary as BL
    bp = {"name": "future", "w": 1, "h": 1, "machines": [
        {"dx": 0, "dy": 0, "type": 9999, "rotation": 0,
         "recipe_mode": None, "power_links": []}]}
    text = BL.encode(bp)
    try:
        BL.decode(text)
        raise AssertionError("accepted an unknown machine id")
    except ValueError as e:
        assert "unknown machine" in str(e).lower(), str(e)


def test_blueprints_without_power_links_still_load():
    """Blueprints saved before power capture existed must keep working."""
    from blueprints import BlueprintLibrary
    import json, tempfile
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "bp.json")
        with open(path, "w") as f:
            json.dump({"blueprints": [{"name": "old", "w": 1, "h": 1, "machines": [
                {"dx": 0, "dy": 0, "type": 2, "rotation": 0, "recipe_mode": None}]}]}, f)
        lib = BlueprintLibrary(path)
        assert len(lib.blueprints) == 1
        assert "power_links" not in lib.blueprints[0]["machines"][0]


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL  {name}\n      {e}")
    print(f"\n{fails} failure(s)")
    sys.exit(1 if fails else 0)
