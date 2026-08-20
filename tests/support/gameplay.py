"""Shared bot routines: booting into a game, reading world state, building."""
import os
import json
import pygame
from pygame.locals import *  # noqa: F403,F401

SCREEN_W, SCREEN_H = 1280, 720


def boot_new_game(bot, slot=2, company="QA TESTCO"):
    """Splash -> main menu -> loading -> save select (new slot) -> name -> intro."""
    yield from bot.idle(20)
    yield from bot.key(K_SPACE)          # skip boot splash
    yield from bot.idle(15)
    yield from bot.type_text("play")     # terminal main menu
    yield from bot.key(K_RETURN)
    yield from bot.idle(400)             # play-loading terminal
    # save select: selected starts at 0 (slot 1); move down to target slot
    for _ in range(slot - 1):
        yield from bot.key(K_DOWN)
        yield from bot.idle(2)
    yield from bot.key(K_RETURN)
    yield from bot.idle(10)
    yield from bot.type_text(company)
    yield from bot.key(K_RETURN)
    yield from bot.idle(10)
    # story intro: several pages, ESC skips the whole thing
    yield from bot.key(K_ESCAPE)
    yield from bot.idle(30)


def boot_existing_game(bot, slot=2):
    yield from bot.idle(20)
    yield from bot.key(K_SPACE)
    yield from bot.idle(15)
    yield from bot.type_text("play")
    yield from bot.key(K_RETURN)
    yield from bot.idle(400)
    for _ in range(slot - 1):
        yield from bot.key(K_DOWN)
        yield from bot.idle(2)
    yield from bot.key(K_RETURN)
    yield from bot.idle(30)


def skip_tutorial(bot):
    """Click the tutorial SKIP button (top-right panel)."""
    tut = bot.g("_tutorial")
    if tut is None or not getattr(tut, "active", False):
        return
    W, H, pw, ph, px, py = tut._geom()
    yield from bot.click(px + 12 + 28, py + ph - 32 + 11)
    yield from bot.idle(5)


def reset_slot(slot):
    """Wipe a save slot so the next boot is genuinely fresh."""
    import shutil
    d = os.path.join("data", f"slot_{slot}")
    if os.path.exists(d):
        shutil.rmtree(d)


# ----- inspection
def world_summary(bot):
    grid = bot.g("grid")
    if grid is None:
        return {"error": "no grid yet"}
    counts = {}
    machines = []
    seen = set()
    for y, row in enumerate(grid):
        for x, t in enumerate(row):
            tt = t.get("type", 0)
            if tt == 0:
                continue
            counts[tt] = counts.get(tt, 0) + 1
            o = t.get("origin", (x, y))
            o = tuple(o) if isinstance(o, list) else o
            if o not in seen:
                seen.add(o)
                machines.append((tt, o))
    return {
        "money": bot.g("money"),
        "pollution": bot.g("pollution"),
        "tile_counts": counts,
        "machine_origins": sorted(machines, key=lambda m: (m[0], m[1])),
    }


def dump(bot, label, path="qa/out"):
    os.makedirs(path, exist_ok=True)
    data = world_summary(bot)
    with open(os.path.join(path, f"{label}.json"), "w") as f:
        json.dump(data, f, indent=1, default=str)
    return data


# ----- coordinates
TILE = 32


def tile_to_screen(bot, gx, gy):
    cam_x = bot.g("camera_x", 0.0)
    cam_y = bot.g("camera_y", 0.0)
    zoom = bot.g("zoom", 1.0)
    return (cam_x + (gx + 0.5) * TILE * zoom,
            cam_y + (gy + 0.5) * TILE * zoom)


def tile(bot, gx, gy):
    return bot.g("grid")[gy][gx]


def origin_tile(bot, gx, gy):
    t = tile(bot, gx, gy)
    o = t.get("origin", (gx, gy))
    o = tuple(o) if isinstance(o, list) else o
    return bot.g("grid")[o[1]][o[0]], o


# ----- player acts
def close_panels(bot):
    ui = bot.g("ui")
    for attr in ("show_build_panel", "show_research_panel", "show_stats_panel",
                 "show_contracts_panel", "show_market_panel", "show_recipe_book",
                 "show_blueprint_panel", "show_loans_panel"):
        if getattr(ui, attr, False):
            yield from bot.key(K_ESCAPE)
            yield from bot.idle(2)
    yield from bot.idle(1)


def open_build(bot):
    ui = bot.g("ui")
    if not ui.show_build_panel:
        yield from bot.key(K_b)
        yield from bot.idle(3)


def build_search(bot, text):
    """Click the build panel search box and type a query, like a player would."""
    ui = bot.g("ui")
    r = ui.build_search_rect
    yield from bot.click(r.centerx, r.centery)
    yield from bot.idle(2)
    for _ in range(24):
        yield from bot.key(K_BACKSPACE)
    yield from bot.type_text(text)
    yield from bot.idle(3)


def pick_machine(bot, mid):
    """Select a machine tile in the build panel by clicking its button."""
    ui = bot.g("ui")
    btn = ui.build_machine_buttons.get(mid)
    if btn is None:
        raise AssertionError(f"machine {mid} has no build button (locked or filtered)")
    yield from bot.click(btn.centerx, btn.centery)
    yield from bot.idle(3)


def place_at(bot, gx, gy, rotation=0):
    """With a tool active, rotate then click a world tile."""
    cur = bot.g("building_rotation", 0)
    turns = ((rotation - cur) % 360) // 90
    for _ in range(turns):
        yield from bot.key(K_r)
        yield from bot.idle(1)
    sx, sy = tile_to_screen(bot, gx, gy)
    yield from bot.click(sx, sy)
    yield from bot.idle(3)


def build_machine(bot, mid, gx, gy, rotation=0, name_hint=None):
    """Full player flow: open build -> search -> select -> place -> close."""
    from settings import MACHINE_STATS
    name = name_hint or MACHINE_STATS.get(mid, {}).get("name", "")
    yield from open_build(bot)
    yield from build_search(bot, name)
    ui = bot.g("ui")
    if mid not in ui.build_machine_buttons:
        yield from build_search(bot, "")
    yield from pick_machine(bot, mid)
    yield from bot.key(K_t)               # Start Placing
    yield from bot.idle(2)
    yield from place_at(bot, gx, gy, rotation)
    yield from bot.key(K_ESCAPE)
    yield from bot.idle(2)
    placed = tile(bot, gx, gy).get("type", 0)
    return placed


def power_link(bot, a, b):
    """P -> click source -> click target -> P."""
    yield from bot.key(K_p)
    yield from bot.idle(2)
    sx, sy = tile_to_screen(bot, *a)
    yield from bot.click(sx, sy)
    yield from bot.idle(2)
    tx, ty = tile_to_screen(bot, *b)
    yield from bot.click(tx, ty)
    yield from bot.idle(2)
    yield from bot.key(K_p)
    yield from bot.idle(2)


def select_tile(bot, gx, gy):
    sx, sy = tile_to_screen(bot, gx, gy)
    yield from bot.click(sx, sy)
    yield from bot.idle(3)
