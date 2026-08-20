"""Test fixtures: put machines into the world directly.

Used only to reach states that would otherwise take hours of play. Placement
writes exactly the fields the game's own placement code writes.
"""


def place_raw(ns, mid, gx, gy, rot=0):
    grid = ns["grid"]
    stats = ns["MACHINE_STATS"].get(mid, {})
    w, h = stats.get("size", (1, 1))
    if rot % 180 != 0:
        w, h = h, w
    for dy in range(h):
        for dx in range(w):
            grid[gy + dy][gx + dx].update({
                "type": mid, "stored": None, "amount": 0, "timer": 0,
                "rotation": rot, "power": 0,
                "max_power": stats.get("power_capacity", 0),
                "power_connections": [], "origin": (gx, gy)})
    return w, h


def clear_area(ns, x0, y0, x1, y1):
    """Fully reset tiles -- dict.update() alone leaves stale buffers behind."""
    grid = ns["grid"]
    for y in range(max(0, y0), min(len(grid), y1)):
        for x in range(max(0, x0), min(len(grid[0]), x1)):
            grid[y][x].clear()
            grid[y][x].update({"type": 0, "stored": None, "amount": 0, "timer": 0,
                               "rotation": 0, "power": 0, "max_power": 0,
                               "power_connections": []})
