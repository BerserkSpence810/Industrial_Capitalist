from ui import *
from settings import *
from settings import MACHINE_DEFS
from settings import REFINERY_RECIPES, DIESEL_GEN_OUTPUT
from settings import (POLLUTION_PER_MACHINE, get_pollution_income_multiplier, POLLUTION_TINT_MAX_ALPHA, POLLUTION_TINT_REFERENCE)
from contracts import ContractManager, LoanManager, MarketManager
from research import ResearchManager, RP_VALUES
from protest import ProtestManager

from menu import run_menu, TutorialOverlay, _activate_slot, _save_active_to_slot

import random
import pygame
import json
import time
import os
import math

_crt_overlay = None
_crt_overlay_size = None

def get_crt_overlay(w, h):
    global _crt_overlay, _crt_overlay_size
    if _crt_overlay is None or _crt_overlay_size != (w, h):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 3):
            pygame.draw.line(surf, (0, 0, 0, 18), (0, y), (w, y), 1)
        _crt_overlay      = surf
        _crt_overlay_size = (w, h)
    return _crt_overlay

_SILO_TYPES = frozenset({22, 23})
_GATE_TYPES = frozenset({103, 104, 105, 111, 112, 113})

def get_machine_origin(grid, x, y):
    tile = grid[y][x]
    o = tile.get("origin")
    if o is None:
        return (x, y)
    return tuple(o) if isinstance(o, list) else o

PIPE_TYPES = (1, 4, 5, 6, 7, 131, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130)
INTERSECTION_TYPES = (131, 124, 130)

_MULTI_TILE_TYPES = frozenset(
    t for t, ms in MACHINE_STATS.items()
    if ms.get("size", (1, 1)) != (1, 1)
)

_current_grid = None

def get_coal_generator_origin(grid, x, y):
    if grid[y][x]["type"] != 12: return None
    return get_machine_origin(grid, x, y)

def get_research_station_origin(grid, x, y):
    if grid[y][x]["type"] != 13: return None
    return get_machine_origin(grid, x, y)

def get_blast_furnace_origin(grid, x, y):
    if grid[y][x]["type"] != 14: return None
    return get_machine_origin(grid, x, y)

def get_any_origin(grid, gx, gy):
    ttype = grid[gy][gx].get("type", 0)
    if MACHINE_STATS.get(ttype, {}).get("size", (1,1)) != (1,1):
        return get_machine_origin(grid, gx, gy)
    return (gx, gy)

def get_machine_center(grid, gx, gy):
    tile = grid[gy][gx]
    ttype = tile.get("type", 0)
    mstats = MACHINE_STATS.get(ttype, {})
    size = mstats.get("size", (1, 1))
    if size == (1, 1):
        return (gx, gy)
    ox, oy = get_machine_origin(grid, gx, gy)
    rot = grid[oy][ox].get("rotation", 0)
    w, h = size
    if (rot // 90) % 2 == 1:
        w, h = h, w
    return (ox + w // 2, oy + h // 2)

def machine_try_receive(grid, nx, ny, item, push_dx, push_dy, push_amount=1):
    ntype = grid[ny][nx].get("type", 0)
    mdef = MACHINE_DEFS.get(ntype)
    if not mdef or "input_ports" not in mdef:
        return False
    ox, oy = get_machine_origin(grid, nx, ny)
    origin_tile = grid[oy][ox]
    rot = origin_tile.get("rotation", 0)
    mstats = MACHINE_STATS.get(ntype, {})
    tw, th = mstats.get("size", (1, 1))
    for port in mdef["input_ports"]:
        sx, sy = port["subtile"]
        fd = tuple(port["from_dir"])
        if rot != 0:
            rx, ry, rfd, _, _ = rotate_port(ox, oy, sx, sy, tw, th, fd, rot)
            if nx != rx or ny != ry:
                continue
            if (push_dx, push_dy) != rfd:
                continue
        else:
            if nx != ox + sx or ny != oy + sy:
                continue
            if (push_dx, push_dy) != fd:
                continue
        accepted = port.get("items")
        if accepted is not None and len(accepted) == 0:
            pass
        elif accepted:
            if item not in accepted:
                continue
            recipe_mode = origin_tile.get("recipe_mode")
            if recipe_mode and recipe_mode in accepted and item != recipe_mode:
                continue
        else:
            if item != port.get("item"):
                continue
        cur = origin_tile.get(port["buf"], 0)
        if cur + push_amount > port["cap"]:
            continue
        if "item_buf" in port:
            existing = origin_tile.get(port["item_buf"])
            if existing not in (None, item):
                continue
        origin_tile[port["buf"]] = cur + push_amount
        if "item_buf" in port:
            origin_tile[port["item_buf"]] = item
        return True
    return False

def push_item_to_neighbor(grid, item, nx, ny, push_dx, push_dy, amount=1):
    if not (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT):
        return False
    nb = grid[ny][nx]
    ntype = nb.get("type", 0)
    if ntype in INTERSECTION_TYPES:
        mstats = MACHINE_STATS.get(ntype, {})
        cap_per_lane = mstats.get("capacity", 6)
        if push_dy != 0 and push_dx == 0:
            lane = "lane_v"
            exit_dir = (0, push_dy)
        elif push_dx != 0 and push_dy == 0:
            lane = "lane_h"
            exit_dir = (push_dx, 0)
        else:
            return False
        if not nb.get(f"{lane}_enabled", True):
            return False
        cur_stored = nb.get(f"{lane}_stored")
        cur_amount = nb.get(f"{lane}_amount", 0)
        if cur_stored not in (None, item):
            return False
        if cur_amount + amount > cap_per_lane:
            return False
        nb[f"{lane}_stored"] = item
        nb[f"{lane}_amount"] = cur_amount + amount
        nb[f"{lane}_exit"]   = exit_dir
        nb["stored"] = nb.get(f"{lane}_stored") or item
        nb["amount"] = nb.get("lane_v_amount", 0) + nb.get("lane_h_amount", 0)
        return True
    if ntype in PIPE_TYPES:
        cap = MACHINE_STATS[ntype]["capacity"]
        if nb["amount"] + amount <= cap and (nb["stored"] is None or nb["stored"] == item):
            nb["stored"] = item
            nb["amount"] += amount
            return True
    elif ntype == 3:
        cap = MACHINE_STATS[3]["capacity"]
        if nb["amount"] + amount <= cap and (nb["stored"] is None or nb["stored"] == item):
            nb["stored"] = item
            nb["amount"] += amount
            return True
    elif ntype == 83:
        ox, oy = get_machine_origin(grid, nx, ny)
        ot = grid[oy][ox]
        if ny != oy:
            return False
        if push_dx != 0 or push_dy != 1:
            return False
        cap = MACHINE_STATS[ntype].get("capacity", 100)
        ot.setdefault("stored", None)
        ot.setdefault("amount", 0)
        if ot["amount"] + amount <= cap and (ot["stored"] is None or ot["stored"] == item):
            ot["stored"] = item
            ot["amount"] += amount
            return True
        return False
    elif ntype in (22, 23):
        ox, oy = get_machine_origin(grid, nx, ny)
        ot = grid[oy][ox]
        if (nx, ny) != (ox, oy):
            return False
        if push_dx != 0 or push_dy != 1:
            return False
        cap = MACHINE_STATS[ntype]["capacity"]
        ot.setdefault("stored", None)
        ot.setdefault("amount", 0)
        if ot["amount"] + amount <= cap and (ot["stored"] is None or ot["stored"] == item):
            ot["stored"] = item
            ot["amount"] += amount
            return True
        return False
    elif ntype == 12 and item == "coal":
        ox, oy = get_machine_origin(grid, nx, ny)
        ot = grid[oy][ox]
        ot.setdefault("coal_buffer", 0.0)
        if ot["coal_buffer"] < 10.0:
            ot["coal_buffer"] += amount
            for dy_ in range(2):
                for dx_ in range(2):
                    cx, cy = ox + dx_, oy + dy_
                    if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT and grid[cy][cx]["type"] == 12:
                        grid[cy][cx]["coal_buffer"] = ot["coal_buffer"]
            return True
    elif ntype == 17 and item in ("poor_quality_diesel", "diesel", "refined_diesel"):
        ox, oy = get_machine_origin(grid, nx, ny)
        ot = grid[oy][ox]
        if nx != ox or ny != oy:
            return False
        if push_dx != 0 or push_dy != 1:
            return False
        ot.setdefault("fuel_buffer", 0.0)
        ot.setdefault("fuel_item", None)
        fuel_cap = MACHINE_STATS[17].get("fuel_capacity", 10.0)
        if ot.get("fuel_item") in (None, item) and ot["fuel_buffer"] + amount <= fuel_cap:
            ot["fuel_buffer"] = ot["fuel_buffer"] + amount
            ot["fuel_item"] = item
            rx, ry = ox + 1, oy
            if 0 <= rx < GRID_WIDTH and grid[ry][rx].get("type") == 17:
                grid[ry][rx]["fuel_buffer"] = ot["fuel_buffer"]
                grid[ry][rx]["fuel_item"] = item
            return True
    elif ntype in MACHINE_DEFS:
        return machine_try_receive(grid, nx, ny, item, push_dx, push_dy, amount)
    return False

def _sanitize_tile_items(tile):
    _PAIRS = [("stored", "amount"),
              ("lane_v_stored", "lane_v_amount"), ("lane_h_stored", "lane_h_amount"),
              ("fuel_item", "fuel_buffer"), ("control_item", "control_buffer")]
    for k in list(tile.keys()):
        if k.endswith("_item"):
            _PAIRS.append((k, k[:-5] + "_buffer"))
    for item_key, amt_key in _PAIRS:
        val = tile.get(item_key)
        if val is not None and val not in ITEM_VALUES:
            tile[item_key] = None
            if amt_key in tile:
                tile[amt_key] = 0
    mdef = MACHINE_DEFS.get(tile.get("type", 0))
    if mdef:
        ports = list(mdef.get("input_ports", []))
        for op in (mdef.get("output_port"), mdef.get("output_port2")):
            if op:
                ports.append(op)
        for port in ports:
            ibk = port.get("item_buf")
            if ibk and tile.get(port["buf"], 0) > 0 and tile.get(ibk) is None:
                tile[port["buf"]] = 0
    return tile

def _find_origin(grid, x, y, ttype):
    ox, oy = x, y
    while ox > 0 and grid[oy][ox - 1].get("type") == ttype:
        ox -= 1
    while oy > 0 and grid[oy - 1][ox].get("type") == ttype:
        oy -= 1
    return (ox, oy)

def load_grid():
    if os.path.exists(GFILE):
        try:
            with open(GFILE, "r") as f:
                content = f.read()
                if content.strip():
                    loaded_grid = json.loads(content)

                    for y in range(len(loaded_grid)):
                        for x in range(len(loaded_grid[0])):
                            tile = loaded_grid[y][x]
                            ttype = tile["type"]
                            _sanitize_tile_items(tile)

                            if ttype in _MULTI_TILE_TYPES:
                                if "origin" not in tile:
                                    tile["origin"] = _find_origin(loaded_grid, x, y, ttype)
                                elif isinstance(tile["origin"], list):
                                    tile["origin"] = tuple(tile["origin"])

                            if "power_connections" in tile:
                                tile["power_connections"] = [
                                    tuple(c) if isinstance(c, list) else c
                                    for c in tile["power_connections"]
                                ]
                            for _sig_key in ("signal_inputs", "signal_outputs"):
                                if _sig_key in tile:
                                    tile[_sig_key] = [
                                        tuple(c) if isinstance(c, list) else c
                                        for c in tile[_sig_key]
                                    ]

                    old_h = len(loaded_grid)
                    old_w = len(loaded_grid[0]) if old_h else 0
                    if old_w < GRID_WIDTH or old_h < GRID_HEIGHT:
                        def _empty():
                            return {"type": 0, "stored": None, "amount": 0,
                                    "timer": 0, "rotation": 0, "power": 0,
                                    "max_power": 0, "power_connections": []}
                        for row in loaded_grid:
                            while len(row) < GRID_WIDTH:
                                row.append(_empty())
                        while len(loaded_grid) < GRID_HEIGHT:
                            loaded_grid.append([_empty() for _ in range(GRID_WIDTH)])
                        print(f"Migrated save from {old_w}x{old_h} to {GRID_WIDTH}x{GRID_HEIGHT}")

                    return loaded_grid
        except (json.JSONDecodeError, ValueError):
            print("Warning: world.json is corrupted. Creating new grid.")
    return [
        [
            {
                "type": 0,
                "stored": None,
                "amount": 0,
                "timer": 0,
                "rotation": 0,
                "power": 0,
                "max_power": 0,
                "power_connections": [],
            }
            for _ in range(GRID_WIDTH)
        ]
        for _ in range(GRID_HEIGHT)
    ]

def save_grid():
    os.makedirs("data", exist_ok=True)

    grid_copy = []
    for row in grid:
        row_copy = []
        for tile in row:
            tile_copy = tile.copy()
            if "power_connections" in tile_copy and isinstance(
                tile_copy["power_connections"], list
            ):
                tile_copy["power_connections"] = [
                    list(conn) if isinstance(conn, tuple) else conn
                    for conn in tile_copy["power_connections"]
                ]
            for _sk in ("signal_inputs", "signal_outputs"):
                if _sk in tile_copy and isinstance(tile_copy[_sk], list):
                    tile_copy[_sk] = [
                        list(c) if isinstance(c, tuple) else c
                        for c in tile_copy[_sk]
                    ]
            row_copy.append(tile_copy)
        grid_copy.append(row_copy)

    with open(GFILE, "w") as f:
        json.dump(grid_copy, f)

STARTING_CAPITAL = 1500.0

def load_money():
    if os.path.exists(MFILE):
        try:
            with open(MFILE, "r") as f:
                data = json.load(f)
                return data.get("money", STARTING_CAPITAL)
        except (json.JSONDecodeError, ValueError):
            print("Money.json corrupted. Starting with default capital.")
    return STARTING_CAPITAL

def save_money(money):
    os.makedirs("data", exist_ok=True)
    with open("data/money.json", "w") as f:
        json.dump({"money": money}, f)

POLLUTION_FILE = "data/pollution.json"

def load_pollution():
    if os.path.exists(POLLUTION_FILE):
        try:
            with open(POLLUTION_FILE, "r") as f:
                val = float(json.load(f).get("pollution", 0.0))
                if val < 0 or val > 2000:
                    print(f"pollution.json value {val} outside 0-2000 range — resetting to 0")
                    return 0.0
                return val
        except (json.JSONDecodeError, ValueError):
            print("pollution.json corrupted. Starting at 0.")
    return 0.0

def save_pollution(value):
    os.makedirs("data", exist_ok=True)
    with open(POLLUTION_FILE, "w") as f:
        json.dump({"pollution": value}, f)

def rotate_direction(direction, rotation):
    if direction is None:
        return None

    dirs = [UP, RIGHT, DOWN, LEFT]
    if direction not in dirs:
        return direction

    idx = dirs.index(direction)
    steps = (rotation // 90) % 4
    new_idx = (idx - steps) % 4
    return dirs[new_idx]

def rotate_port(ox, oy, sx, sy, tw, th, direction, rotation):
    steps = (rotation // 90) % 4
    cx, cy, cw, ch = sx, sy, tw, th
    for _ in range(steps):
        cx, cy = cy, cw - 1 - cx
        cw, ch = ch, cw
    rd = rotate_direction(direction, rotation)
    return ox + cx, oy + cy, rd, cw, ch

def port_pixel(ox, oy, sx, sy, tw, th, rot):
    steps = (rot // 90) % 4
    cx, cy, cw, ch = sx, sy, tw, th
    for _ in range(steps):
        cx, cy = cy, cw - 1 - cx
        cw, ch = ch, cw
    px = (ox + cx) * TILE_SIZE + TILE_SIZE // 2
    py = (oy + cy) * TILE_SIZE + TILE_SIZE // 2
    return px, py

def get_output_direction(tile):
    machine_stats = MACHINE_STATS.get(tile["type"], {})

    if "output_dirs" in machine_stats:
        base_dirs = machine_stats["output_dirs"]
        rotation = tile.get("rotation", 0)
        return [rotate_direction(d, rotation) for d in base_dirs]

    base_dir = machine_stats.get("output_dir", None)
    if base_dir is None:
        return None
    rotation = tile.get("rotation", 0) 
    return rotate_direction(base_dir, rotation)

def get_input_direction(tile):
    machine_stats = MACHINE_STATS.get(tile["type"], {})

    if "input_dirs" in machine_stats:
        base_dirs = machine_stats["input_dirs"]
        rotation = tile.get("rotation", 0)
        return [rotate_direction(d, rotation) for d in base_dirs]

    base_dir = machine_stats.get("input_dir", None)
    if base_dir is None:
        return None
    rotation = tile.get("rotation", 0)
    return rotate_direction(base_dir, rotation)

def get_neighbor_in_direction(x, y, direction):
    dx, dy = direction
    nx, ny = x + dx, y + dy
    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
        return nx, ny
    return None

def get_zone_rect(x, y, direction, is_input=False):
    ZONE_WIDTH = 12
    ZONE_EXTEND = 4
    base_x = x * TILE_SIZE
    base_y = y * TILE_SIZE
    center_x = base_x + TILE_SIZE // 2
    center_y = base_y + TILE_SIZE // 2
    dx, dy = direction

    if dx == 0 and dy == -1:
        return pygame.Rect(
            center_x - ZONE_WIDTH // 2,
            base_y - ZONE_EXTEND,
            ZONE_WIDTH,
            ZONE_EXTEND + 3,
        )
    elif dx == 0 and dy == 1:
        return pygame.Rect(
            center_x - ZONE_WIDTH // 2,
            base_y + TILE_SIZE - 3,
            ZONE_WIDTH,
            ZONE_EXTEND + 3,
        )
    elif dx == -1 and dy == 0:
        return pygame.Rect(
            base_x - ZONE_EXTEND,
            center_y - ZONE_WIDTH // 2,
            ZONE_EXTEND + 3,
            ZONE_WIDTH,
        )
    elif dx == 1 and dy == 0:
        return pygame.Rect(
            base_x + TILE_SIZE - 3,
            center_y - ZONE_WIDTH // 2,
            ZONE_EXTEND + 3,
            ZONE_WIDTH,
        )

    return None

def get_zone_rect_for_multitile(x, y, direction, width, height, is_input=False):
    ZONE_WIDTH = 12
    ZONE_EXTEND = 4
    base_x = x * TILE_SIZE
    base_y = y * TILE_SIZE
    dx, dy = direction

    if dx == 0 and dy == -1:
        center_x = base_x + (TILE_SIZE * width) // 2
        return pygame.Rect(center_x - ZONE_WIDTH // 2,
                           base_y - ZONE_EXTEND,
                           ZONE_WIDTH, ZONE_EXTEND + 3)

    elif dx == 0 and dy == 1:
        center_x = base_x + (TILE_SIZE * width) // 2
        bottom_y  = base_y + TILE_SIZE * height
        return pygame.Rect(center_x - ZONE_WIDTH // 2,
                           bottom_y - 3,
                           ZONE_WIDTH, ZONE_EXTEND + 3)

    elif dx == -1 and dy == 0:
        center_y = base_y + (TILE_SIZE * height) // 2
        return pygame.Rect(base_x - ZONE_EXTEND,
                           center_y - ZONE_WIDTH // 2,
                           ZONE_EXTEND + 3, ZONE_WIDTH)

    elif dx == 1 and dy == 0:
        center_y = base_y + (TILE_SIZE * height) // 2
        right_x   = base_x + TILE_SIZE * width
        return pygame.Rect(right_x - 3,
                           center_y - ZONE_WIDTH // 2,
                           ZONE_EXTEND + 3, ZONE_WIDTH)

    return None

def _port_accepts_from(grid, tx, ty, push_dx, push_dy):
    ttype = grid[ty][tx].get("type", 0)
    mdef = MACHINE_DEFS.get(ttype)
    if not mdef or "input_ports" not in mdef:
        return False
    ox, oy = get_machine_origin(grid, tx, ty)
    rot = grid[oy][ox].get("rotation", 0)
    tw, th = MACHINE_STATS.get(ttype, {}).get("size", (1, 1))
    for port in mdef["input_ports"]:
        sx, sy = port["subtile"]
        fd = tuple(port["from_dir"])
        if rot != 0:
            rx, ry, rfd, _, _ = rotate_port(ox, oy, sx, sy, tw, th, fd, rot)
        else:
            rx, ry, rfd = ox + sx, oy + sy, fd
        if (tx, ty) == (rx, ry) and (push_dx, push_dy) == rfd:
            return True
    return False

def can_connect(source_x, source_y, source_tile, target_x, target_y, target_tile):
    ttype_t = target_tile.get("type", 0)
    ddx, ddy = target_x - source_x, target_y - source_y
    if abs(ddx) + abs(ddy) == 1:
        tdef = MACHINE_DEFS.get(ttype_t)
        if tdef and "input_ports" in tdef:
            if _port_accepts_from(grid, target_x, target_y, ddx, ddy):
                return True
            if ttype_t == 83:
                ox83, oy83 = get_machine_origin(grid, target_x, target_y)
                if target_y == oy83 and (ddx, ddy) == (0, 1):
                    return True

    if source_tile.get("type") == 15:
        raw = source_tile.get("origin", (source_x, source_y))
        ox, oy = (tuple(raw) if isinstance(raw, list) else raw)
        rot = grid[oy][ox].get("rotation", 0)
        tx, ty, rd, _, _ = rotate_port(ox, oy, 1, 0, 2, 1, RIGHT, rot)
        rdx, rdy = rd
        if source_x == tx and source_y == ty and target_x == tx + rdx and target_y == ty + rdy:
            return True
        return False
    if target_tile.get("type") == 15:
        return False

    if target_tile.get("type") == 16:
        raw = target_tile.get("origin", (target_x, target_y))
        ox, oy = (tuple(raw) if isinstance(raw, list) else raw)
        rot = grid[oy][ox].get("rotation", 0)
        tx, ty, rd, _, _ = rotate_port(ox, oy, 0, 0, 3, 3, UP, rot)
        rdx, rdy = rd
        if source_x == tx + rdx and source_y == ty + rdy and target_x == tx and target_y == ty:
            return True
        return False
    if source_tile.get("type") == 16:
        raw = source_tile.get("origin", (source_x, source_y))
        ox, oy = (tuple(raw) if isinstance(raw, list) else raw)
        rot = grid[oy][ox].get("rotation", 0)
        tx, ty, rd, _, _ = rotate_port(ox, oy, 0, 2, 3, 3, DOWN, rot)
        rdx, rdy = rd
        if source_x == tx and source_y == ty and target_x == tx + rdx and target_y == ty + rdy:
            return True
        tx2, ty2, rd2, _, _ = rotate_port(ox, oy, 0, 2, 3, 3, LEFT, rot)
        rdx2, rdy2 = rd2
        if source_x == tx2 and source_y == ty2 and target_x == tx2 + rdx2 and target_y == ty2 + rdy2:
            return True
        return False

    if target_tile.get("type") == 17:
        raw = target_tile.get("origin", (target_x, target_y))
        ox, oy = (tuple(raw) if isinstance(raw, list) else raw)
        rot = grid[oy][ox].get("rotation", 0)
        tx, ty, rd, _, _ = rotate_port(ox, oy, 0, 0, 2, 1, UP, rot)
        rdx, rdy = rd
        if source_x == tx + rdx and source_y == ty + rdy and target_x == tx and target_y == ty:
            return True
        return False
    if source_tile.get("type") == 17:
        return False

    if target_tile.get("type") == 12:
        origin = target_tile.get("origin", (target_x, target_y))
        if isinstance(origin, list): origin = tuple(origin)
        ox, oy = origin
        if source_x == ox and source_y == oy - 1 and target_x == ox and target_y == oy:
            return True
        return False

    if target_tile.get("type") in (22, 23):
        raw = target_tile.get("origin", (target_x, target_y))
        ox, oy = (tuple(raw) if isinstance(raw, list) else raw)
        if source_x == ox and source_y == oy - 1 and target_x == ox and target_y == oy:
            return True
        return False
    if source_tile.get("type") in (22, 23):
        raw = source_tile.get("origin", (source_x, source_y))
        ox, oy = (tuple(raw) if isinstance(raw, list) else raw)
        if source_x == ox and source_y == oy + 1 and target_x == ox and target_y == oy + 2:
            return True
        return False

    if target_tile.get("type") == 18:
        raw = target_tile.get("origin", (target_x, target_y))
        ox, oy = (tuple(raw) if isinstance(raw, list) else raw)
        rot = grid[oy][ox].get("rotation", 0)
        tx, ty, rd, _, _ = rotate_port(ox, oy, 0, 0, 3, 1, DOWN, rot)
        rdx, rdy = rd
        if source_x == tx + rdx and source_y == ty + rdy and target_x == tx and target_y == ty:
            return True
        return False
    if source_tile.get("type") == 18:
        return False

    if target_tile.get("type") == 19:
        raw = target_tile.get("origin", (target_x, target_y))
        ox, oy = (tuple(raw) if isinstance(raw, list) else raw)
        rot = grid[oy][ox].get("rotation", 0)
        tx, ty, rd, _, _ = rotate_port(ox, oy, 0, 0, 2, 1, UP, rot)
        rdx, rdy = rd
        if source_x == tx + rdx and source_y == ty + rdy and target_x == tx and target_y == ty:
            return True
        return False
    if source_tile.get("type") == 19:
        return False

    if target_tile.get("type") == 20:
        raw = target_tile.get("origin", (target_x, target_y))
        ox, oy = (tuple(raw) if isinstance(raw, list) else raw)
        rot = grid[oy][ox].get("rotation", 0)
        tx, ty, rd, _, _ = rotate_port(ox, oy, 0, 0, 2, 1, UP, rot)
        rdx, rdy = rd
        if source_x == tx + rdx and source_y == ty + rdy and target_x == tx and target_y == ty:
            return True
        return False
    if source_tile.get("type") == 20:
        return False

    if target_tile.get("type") == 14:
        origin = target_tile.get("origin", (target_x, target_y))
        if isinstance(origin, list): origin = tuple(origin)
        ox, oy = origin
        if source_x == ox and source_y == oy-1 and target_x == ox and target_y == oy:
            return True
        if source_x == ox+2 and source_y == oy-1 and target_x == ox+2 and target_y == oy:
            return True
        return False
    if source_tile.get("type") == 14:
        origin = source_tile.get("origin", (source_x, source_y))
        if isinstance(origin, list): origin = tuple(origin)
        ox, oy = origin
        if source_x == ox+2 and source_y == oy+2 and target_x == ox+2 and target_y == oy+3:
            return True
        return False

    source_output_dir = get_output_direction(source_tile)
    if source_output_dir is None:
        return False

    target_input_dir = get_input_direction(target_tile)
    if target_input_dir is None:
        return False

    source_stats = MACHINE_STATS.get(source_tile["type"], {})
    source_size = source_stats.get("size", (1, 1))
    target_stats = MACHINE_STATS.get(target_tile["type"], {})
    target_size = target_stats.get("size", (1, 1))

    if source_tile["type"] == 12:
        source_origin = source_tile.get("origin", (source_x, source_y))
        source_x, source_y = source_origin

    if isinstance(source_output_dir, list):
        for output_dir in source_output_dir:
            if source_size != (1, 1):
                source_output_rect = get_zone_rect_for_multitile(
                    source_x, source_y, output_dir,
                    source_size[0], source_size[1], is_input=False,
                )
            else:
                source_output_rect = get_zone_rect(source_x, source_y, output_dir, is_input=False)

            if not source_output_rect:
                continue

            if isinstance(target_input_dir, list):
                for input_dir in target_input_dir:
                    if target_size != (1, 1):
                        target_input_rect = get_zone_rect_for_multitile(
                            target_x, target_y, input_dir,
                            target_size[0], target_size[1], is_input=True,
                        )
                    else:
                        target_input_rect = get_zone_rect(target_x, target_y, input_dir, is_input=True)
                    if target_input_rect and source_output_rect.colliderect(target_input_rect):
                        return True
            else:
                if target_size != (1, 1):
                    target_input_rect = get_zone_rect_for_multitile(
                        target_x, target_y, target_input_dir,
                        target_size[0], target_size[1], is_input=True,
                    )
                else:
                    target_input_rect = get_zone_rect(target_x, target_y, target_input_dir, is_input=True)
                if target_input_rect and source_output_rect.colliderect(target_input_rect):
                    return True
        return False

    if source_size != (1, 1):
        source_output_rect = get_zone_rect_for_multitile(source_x, source_y, source_output_dir, source_size[0], source_size[1], is_input=False,
        )
    else:
        source_output_rect = get_zone_rect(source_x, source_y, source_output_dir, is_input=False)

    if source_output_rect is None:
        return False

    if isinstance(target_input_dir, list):
        for input_dir in target_input_dir:
            if target_size != (1, 1):
                target_input_rect = get_zone_rect_for_multitile(target_x, target_y, input_dir, target_size[0], target_size[1], is_input=True,
                )
            else:
                target_input_rect = get_zone_rect(target_x, target_y, input_dir, is_input=True)
            if target_input_rect and source_output_rect.colliderect(target_input_rect):
                return True
        return False

    if target_size != (1, 1):
        target_input_rect = get_zone_rect_for_multitile(
            target_x, target_y, target_input_dir,
            target_size[0], target_size[1], is_input=True,
        )
    else:
        target_input_rect = get_zone_rect(target_x, target_y, target_input_dir, is_input=True)

    if target_input_rect is None:
        return False

    return source_output_rect.colliderect(target_input_rect)

def is_part_of_coal_generator(grid, x, y):
    return grid[y][x]["type"] == 12

def can_coal_generator_receive_input(grid, target_x, target_y):
    origin = get_coal_generator_origin(grid, target_x, target_y)
    if not origin:
        return False
    origin_x, origin_y = origin
    return target_x == origin_x and target_y == origin_y

def is_powered(tile):
    machine_stats = MACHINE_STATS.get(tile["type"], {})
    power_input = machine_stats.get("power_input", 0)
    if power_input == 0:
        return True
    return tile.get("power", 0) >= power_input

def get_power_efficiency(tile):
    machine_stats = MACHINE_STATS.get(tile["type"], {})
    power_input = machine_stats.get("power_input", 0)
    if power_input == 0:
        return 1.0
    current_power = tile.get("power", 0)
    return min(1.0, current_power / power_input)

def update_power_system(grid, dt):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            ttype = tile["type"]
            if ttype == 0:
                continue
            machine_stats = MACHINE_STATS.get(ttype, {})
            tile.setdefault("power", 0)
            tile.setdefault("max_power", machine_stats.get("power_capacity", 0))
            tile.setdefault("power_connections", [])

            if ttype == 11:
                power_output = machine_stats.get("power_output", 0)
                tile["power"] = min(tile["power"] + power_output * dt, tile["max_power"])

            elif ttype in (24, 25):
                power_output = machine_stats.get("power_output", 0)
                tile["power"] = min(tile["power"] + power_output * dt, tile["max_power"])

            elif ttype == 118 or machine_stats.get("infinite"):
                tile["max_power"] = machine_stats.get("power_capacity", 1.0e18)
                tile["power"]     = tile["max_power"]

            elif ttype in (26, 27, 28):
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                base_output = machine_stats.get("power_output", 0)
                effective = base_output * globals().get("wind_speed", 0.5)
                tile["power"] = min(tile["power"] + effective * dt, tile["max_power"])
                tw, th = machine_stats.get("size", (2, 2))
                for dy in range(th):
                    for dx in range(tw):
                        cx, cy = ox + dx, oy + dy
                        if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT and grid[cy][cx]["type"] == ttype:
                            grid[cy][cx]["power"] = tile["power"]
                            grid[cy][cx]["max_power"] = tile["max_power"]

            elif ttype == 12:
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                tile.setdefault("coal_buffer", 0.0)
                if tile["coal_buffer"] > 0:
                    coal_consumption = machine_stats.get("coal_consumption", 0.25)
                    tile["coal_buffer"] = max(0, tile["coal_buffer"] - coal_consumption * dt)
                    power_output = machine_stats.get("power_output", 0)
                    tile["power"] = min(tile["power"] + power_output * dt, tile["max_power"])
                    for dy in range(2):
                        for dx in range(2):
                            cx, cy = ox + dx, oy + dy
                            if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT and grid[cy][cx]["type"] == 12:
                                grid[cy][cx]["power"]       = tile["power"]
                                grid[cy][cx]["max_power"]   = tile["max_power"]
                                grid[cy][cx]["coal_buffer"] = tile["coal_buffer"]

            elif machine_stats.get("power_input", 0) > 0 and ttype != 106:
                tw, th = machine_stats.get("size", (1, 1))
                draw = machine_stats["power_input"] * dt
                if tw > 1 or th > 1:
                    ox, oy = get_machine_origin(grid, x, y)
                    if (x, y) != (ox, oy):
                        continue
                    tile["power"] = max(0.0, tile["power"] - draw)
                    for dy in range(th):
                        for dx in range(tw):
                            cx, cy = ox + dx, oy + dy
                            if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT and grid[cy][cx]["type"] == ttype:
                                grid[cy][cx]["power"]     = tile["power"]
                                grid[cy][cx]["max_power"] = tile["max_power"]
                else:
                    tile["power"] = max(0.0, tile["power"] - draw)

def transfer_power_between_tiles(
    source_x, source_y, source_tile, target_x, target_y, target_tile, dt
):
    raw_origin = source_tile.get("origin")
    if raw_origin is not None:
        ox, oy = tuple(raw_origin) if isinstance(raw_origin, list) else raw_origin
        source_tile = _current_grid[oy][ox]

    source_stats = MACHINE_STATS.get(source_tile["type"], {})
    src_type = source_stats.get("type")
    can_relay = (
        source_stats.get("power_output", 0) > 0
        or src_type in ("power_pole", "power_storage")
        or source_stats.get("power_transfer", 0) > 0
    )
    if not can_relay:
        return

    source_transfer_rate = source_stats.get("power_transfer", 0)
    if source_transfer_rate == 0:
        return

    raw_origin = target_tile.get("origin")
    if raw_origin is not None:
        ox, oy = tuple(raw_origin) if isinstance(raw_origin, list) else raw_origin
        target_tile = _current_grid[oy][ox]

    target_stats         = MACHINE_STATS.get(target_tile.get("type", 0), {})
    target_transfer_rate = target_stats.get("power_transfer", 0)
    transfer_rate = (
        min(source_transfer_rate, target_transfer_rate)
        if target_transfer_rate > 0
        else source_transfer_rate
    )

    source_power = source_tile.get("power", 0)
    target_power = target_tile.get("power", 0)
    target_max   = target_tile.get("max_power", 0)

    if source_power > 0 and target_power < target_max:
        amount = min(transfer_rate * dt, source_power, target_max - target_power)
        if amount > 0:
            source_tile["power"] -= amount
            target_tile["power"] += amount

def update_diesel_generators(grid, dt):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            if tile.get("type") != 17:
                continue
            ox, oy = get_machine_origin(grid, x, y)
            if (x, y) != (ox, oy):
                continue

            tile.setdefault("fuel_buffer", 0.0)
            tile.setdefault("fuel_item",   None)
            tile.setdefault("power",       0.0)
            tile.setdefault("max_power",   MACHINE_STATS[17].get("power_capacity", 250000))

            fuel_type = tile.get("fuel_item")
            fuel_amt  = tile.get("fuel_buffer", 0.0)

            if fuel_type and fuel_amt > 0:
                consume = min(0.1 * dt, fuel_amt)
                tile["fuel_buffer"] -= consume
                if tile["fuel_buffer"] <= 1e-6:
                    tile["fuel_buffer"] = 0.0
                    tile["fuel_item"]   = None

                power_rate = DIESEL_GEN_OUTPUT.get(fuel_type, 0)
                tile["power"] = min(tile["power"] + power_rate * dt, tile["max_power"])

            rx, ry = ox + 1, oy
            if 0 <= rx < GRID_WIDTH and grid[ry][rx].get("type") == 17:
                grid[ry][rx]["fuel_buffer"] = tile["fuel_buffer"]
                grid[ry][rx]["fuel_item"]   = tile.get("fuel_item")
                grid[ry][rx]["power"]       = tile["power"]
                grid[ry][rx]["max_power"]   = tile["max_power"]

def _mirror_power(grid, ox, oy, ttype, tile):
    tw, th = MACHINE_STATS.get(ttype, {}).get("size", (1, 1))
    if grid[oy][ox].get("rotation", 0) % 180 != 0:
        tw, th = th, tw
    for dy in range(th):
        for dx in range(tw):
            cx, cy = ox + dx, oy + dy
            if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT and grid[cy][cx]["type"] == ttype:
                grid[cy][cx]["power"] = tile["power"]
                grid[cy][cx]["max_power"] = tile["max_power"]

def update_special_generators(grid, dt):
    pollution_rate = 0.0
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            ttype = tile.get("type", 0)
            if ttype not in (106, 107, 108, 96, 110):
                continue
            ox, oy = get_machine_origin(grid, x, y)
            if (x, y) != (ox, oy):
                continue
            mdef = MACHINE_DEFS.get(ttype, {})
            stats = MACHINE_STATS.get(ttype, {})
            tile.setdefault("power", 0.0)
            tile.setdefault("max_power", stats.get("power_capacity", 0))

            if ttype == 110:
                pollution_rate -= mdef.get("disperse_rate", 0.001)
                continue

            out_rate = stats.get("power_output", 0)
            frac = 0.0
            if ttype == 106:
                burn = mdef.get("steam_rate", 0.5) * dt
                have = tile.get("input_buffer", 0)
                used = min(burn, have)
                if used > 0:
                    tile["input_buffer"] = have - used
                    frac = used / burn if burn > 0 else 0.0
            elif ttype == 107:
                burn = mdef.get("fuel_rate", 0.1) * dt
                have = tile.get("input_buffer", 0)
                if tile.get("input_item") == mdef.get("fuel_type", "gasoline") and have > 0:
                    used = min(burn, have)
                    tile["input_buffer"] = have - used
                    if tile["input_buffer"] <= 1e-6:
                        tile["input_buffer"] = 0.0
                        tile["input_item"] = None
                    frac = used / burn if burn > 0 else 0.0
            elif ttype == 108:
                cb = mdef.get("coal_rate", 0.5) * dt
                wb = mdef.get("water_rate", 1.0) * dt
                have_c = tile.get("input_buffer", 0)
                have_w = tile.get("water_buffer", 0)
                frac = min(1.0, (have_c / cb) if cb > 0 else 0.0,
                           (have_w / wb) if wb > 0 else 0.0)
                if frac > 0:
                    tile["input_buffer"] = max(0.0, have_c - cb * frac)
                    tile["water_buffer"] = max(0.0, have_w - wb * frac)
                    if tile["input_buffer"] <= 1e-6:
                        tile["input_buffer"] = 0.0
                        tile["input_item"] = None
            elif ttype == 96:
                if mdef.get("power_while_processing") and tile.get("timer", 0) > 0:
                    frac = 1.0

            if frac > 0:
                tile["power"] = min(tile["power"] + out_rate * frac * dt, tile["max_power"])
                if ttype != 96:
                    pollution_rate += POLLUTION_PER_MACHINE.get(ttype, 0) * frac
            _mirror_power(grid, ox, oy, ttype, tile)
    return pollution_rate

def update_world(grid, dt, money, pollution, contracts, ui=None,
                 research=None, protesters=None, market=None):
    global _current_grid
    _current_grid = grid
    update_power_system(grid, dt)
    update_diesel_generators(grid, dt)
    _special_pollution = update_special_generators(grid, dt)
    for _sy in range(GRID_HEIGHT):
        for _sx in range(GRID_WIDTH):
            _st = grid[_sy][_sx]
            if _st.get("type", 0) not in _SILO_TYPES:
                continue
            _ox2, _oy2 = get_machine_origin(grid, _sx, _sy)
            if (_sx, _sy) != (_ox2, _oy2):
                continue
            _ms2 = MACHINE_STATS.get(_st["type"], {})
            _cap = _ms2.get("capacity", 100)
            _amt = _st.get("amount", 0) or _st.get("input_buffer", 0) or 0
            _thr = _st.get("signal_threshold", 0.9)
            _st["signal_value"] = 1 if (_cap > 0 and _amt / _cap >= _thr) else 0

    rs1_active = 0
    for _ry in range(GRID_HEIGHT):
        for _rx in range(GRID_WIDTH):
            _rt = grid[_ry][_rx]
            if _rt.get("type") != 13:
                continue
            _ox, _oy = get_machine_origin(grid, _rx, _ry)
            if (_rx, _ry) != (_ox, _oy):
                continue
            if _rt.get("power", 0.0) > 1e-3:
                rs1_active += 1

    tick_pollution_rate = _special_pollution

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            if "power_connections" in tile:
                for conn_x, conn_y in tile["power_connections"]:
                    if 0 <= conn_x < GRID_WIDTH and 0 <= conn_y < GRID_HEIGHT:
                        transfer_power_between_tiles(
                            x, y, tile, conn_x, conn_y, grid[conn_y][conn_x], dt
                        )

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            ttype = tile["type"]
            if ttype == 0:
                continue

            mdef = MACHINE_DEFS.get(ttype, {})
            if mdef.get("drill"):
                drill_cap  = MACHINE_STATS[ttype]["capacity"]
                mine_time  = mdef["mine_time"]
                if "resources" in mdef:
                    mode = tile.get("recipe_mode")
                    resource = mode if mode in mdef["resources"] else mdef["resources"][0]
                else:
                    resource = mdef["resource"]
                if is_powered(tile) and tile["amount"] < drill_cap:
                    efficiency = get_power_efficiency(tile)
                    tile["timer"] += dt * efficiency
                    tick_pollution_rate += POLLUTION_PER_MACHINE.get(ttype, 0) * efficiency
                    if tile["timer"] >= mine_time:
                        tile["stored"] = resource
                        tile["amount"] = tile.get("amount", 0) + 1
                        tile["timer"] = 0
                elif tile["amount"] >= drill_cap:
                    for contract in contracts.get_active_contracts():
                        cid = contract["id"]
                        if contracts.get_contract_progress(cid):
                            contracts.track_idle_time(cid, dt)

                tile.setdefault("output_timer", 0)
                tile["output_timer"] += dt
                if tile["output_timer"] >= 0.5 and tile["amount"] > 0:
                    odir = get_output_direction(tile)
                    if odir is not None and not isinstance(odir, list):
                        nx, ny = x + odir[0], y + odir[1]
                        if push_item_to_neighbor(grid, tile["stored"], nx, ny, odir[0], odir[1]):
                            tile["amount"] -= 1
                            if tile["amount"] == 0:
                                tile["stored"] = None
                    tile["output_timer"] = 0

            elif mdef.get("fluid_producer"):
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                tile.setdefault("fluid_buffer", 0.0)
                tile.setdefault("output_timer", 0.0)
                rate = mdef["rate"]
                cap  = mdef["cap"]
                if is_powered(tile) and tile["fluid_buffer"] < cap:
                    tile["fluid_buffer"] = min(tile["fluid_buffer"] + rate * dt, cap)
                    tick_pollution_rate += POLLUTION_PER_MACHINE.get(ttype, 0)
                tile["output_timer"] += dt
                push_amt = mdef.get("push_amount", 0.45)
                if tile["output_timer"] >= 0.5 and tile["fluid_buffer"] >= push_amt:
                    sx_, sy_ = mdef["output_subtile"]
                    dx_, dy_ = mdef["push_dir"]
                    out_x = ox + sx_ + dx_
                    out_y = oy + sy_ + dy_
                    if push_item_to_neighbor(grid, mdef["resource"], out_x, out_y, dx_, dy_, push_amt):
                        tile["fluid_buffer"] -= push_amt
                    tile["output_timer"] = 0.0

            elif mdef.get("research_station") and mdef.get("rs_tier", 1) > 1:
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                tile.setdefault("input_buffer", 0.0)
                tile.setdefault("input_item", None)
                tile.setdefault("item_timer", 0.0)
                stats_rs = MACHINE_STATS.get(ttype, {})
                item_cycle = stats_rs.get("item_cycle_time", 2.0)
                rp_per_item = stats_rs.get("rp_per_item", 5.0)
                if tile.get("input_buffer", 0) >= 1 and is_powered(tile) and research is not None:
                    tile["item_timer"] += dt * get_power_efficiency(tile)
                    if tile["item_timer"] >= item_cycle:
                        tile["item_timer"] = 0.0
                        consumed = tile["input_item"]
                        tile["input_buffer"] -= 1
                        if tile["input_buffer"] <= 1e-6:
                            tile["input_buffer"] = 0.0
                            tile["input_item"] = None
                        rpx = RP_VALUES.get(consumed, 1.0)
                        research.add_rp(rp_per_item * rpx)
                else:
                    tile["item_timer"] = 0.0

            elif "process" in mdef:
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                proc = mdef["process"]

                oport  = mdef.get("output_port", {})
                oport2 = mdef.get("output_port2", {})
                for port in mdef.get("input_ports", []):
                    tile.setdefault(port["buf"], 0)
                    if "item_buf" in port:
                        tile.setdefault(port["item_buf"], None)
                tile.setdefault(oport.get("buf", "output_buffer"), 0)
                tile.setdefault(oport.get("item_buf", "output_item"), None)
                if oport2:
                    tile.setdefault(oport2.get("buf", "residue_buffer"), 0.0)
                    tile.setdefault(oport2.get("item_buf", "residue_item"), None)
                tile.setdefault("timer", 0)

                if proc.get("needs_power") and not is_powered(tile):
                    tile["timer"] = 0
                    continue

                if proc.get("produce_fn") == "refinery":
                    in_item = tile.get("input_item")
                    recipe  = REFINERY_RECIPES.get(in_item)
                    res_cap = oport2.get("cap", 2.0)
                    residue_full = tile.get(oport2.get("buf","residue_buffer"), 0) >= res_cap
                    if not recipe or residue_full or tile.get("input_buffer", 0) < recipe["consume"]:
                        tile["timer"] = 0
                        continue
                    out_cap = oport.get("cap", 2.0)
                    if tile.get(oport.get("buf","output_buffer"), 0) + recipe["output"] > out_cap:
                        tile["timer"] = 0
                        continue
                    eff = get_power_efficiency(tile)
                    tile["timer"] += dt * eff
                    tick_pollution_rate += POLLUTION_PER_MACHINE.get(ttype, 0) * eff
                    if tile["timer"] >= proc["time"]:
                        tile["timer"] = 0
                        tile["input_buffer"] = tile.get("input_buffer", 0) - recipe["consume"]
                        if tile["input_buffer"] <= 1e-6:
                            tile["input_buffer"] = 0.0
                            tile["input_item"]   = None
                        out_buf = oport.get("buf", "output_buffer")
                        out_ibk = oport.get("item_buf", "output_item")
                        tile[out_buf]  = tile.get(out_buf, 0)  + recipe["output"]
                        tile[out_ibk]  = recipe["produce"]
                        res_buf = oport2.get("buf", "residue_buffer")
                        res_ibk = oport2.get("item_buf", "residue_item")
                        tile[res_buf]  = tile.get(res_buf, 0) + recipe["residue"]
                        tile[res_ibk]  = "residue"
                    continue

                check_fn = proc.get("check")
                if check_fn and not check_fn(tile):
                    tile["timer"] = 0
                    continue

                out_buf = oport.get("buf", "output_buffer")
                out_cap = oport.get("cap", 99)
                amount  = proc.get("amount", 1)
                if tile.get(out_buf, 0) + amount > out_cap:
                    tile["timer"] = 0
                    continue

                eff = get_power_efficiency(tile) if proc.get("needs_power") else 1.0
                tile["timer"] += dt * eff
                tick_pollution_rate += POLLUTION_PER_MACHINE.get(ttype, 0) * eff

                if tile["timer"] >= proc["time"]:
                    tile["timer"] = 0
                    item_buf_key = oport.get("item_buf", "output_item")

                    pf = proc.get("produce_fn")
                    to_consume = dict(proc.get("consume", {}))
                    secondary_outs = []
                    if pf == "furnace":
                        inp = tile.get("input_item")
                        if not inp or not inp.startswith("raw_"):
                            continue
                        out_item = inp.replace("raw_", "liquid_")
                    elif pf == "recipe_map":
                        mapping = proc.get("recipe_map", {}).get(tile.get("input_item"))
                        if mapping is None:
                            continue
                        out_item, amount = mapping
                    elif pf == "multi_output":
                        outs = proc.get("outputs", [])
                        if not outs:
                            continue
                        _, _, out_item, amount = outs[0]
                        secondary_outs = outs[1:]
                    elif pf == "mode_recipes":
                        mode = tile.get("recipe_mode", proc.get("default_mode", ""))
                        mrec = proc.get("mode_recipes", {}).get(mode)
                        if not mrec:
                            continue
                        out_item = mrec.get("produce")
                        amount = mrec.get("amount", proc.get("amount", 1))
                        for ek, eq in mrec.get("extra_consume", {}).items():
                            to_consume[ek] = to_consume.get(ek, 0) + eq
                    else:
                        out_item = proc.get("produce")
                        if out_item is None:
                            continue

                    cur_out = tile.get(out_buf, 0)
                    if cur_out > 1e-6 and tile.get(item_buf_key) not in (None, out_item):
                        continue
                    if cur_out + amount > out_cap and cur_out > 1e-6:
                        continue
                    blocked = False
                    for bk, ibk, item, amt in secondary_outs:
                        cur2 = tile.get(bk, 0)
                        cap2 = (oport2.get("cap", 99) if oport2 and oport2.get("buf") == bk else 99)
                        if cur2 > 1e-6 and tile.get(ibk) not in (None, item):
                            blocked = True; break
                        if cur2 + amt > cap2 and cur2 > 1e-6:
                            blocked = True; break
                    if blocked:
                        continue

                    for buf_key, qty in to_consume.items():
                        tile[buf_key] = max(0.0, tile.get(buf_key, 0) - qty)
                    for bk, ibk, item, amt in secondary_outs:
                        tile[bk] = tile.get(bk, 0) + amt
                        tile[ibk] = item
                    tile[out_buf] = tile.get(out_buf, 0) + amount
                    tile[item_buf_key] = out_item
                    for port in mdef.get("input_ports", []):
                        ibk2 = port.get("item_buf")
                        if ibk2 and tile.get(port["buf"], 0) <= 1e-6:
                            tile[ibk2] = None

            elif ttype == 13:
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue

                cur_power = tile.get("power", 0.0)
                max_power = tile.get("max_power",
                                     MACHINE_STATS.get(13, {}).get("power_capacity", 3000))
                for dy in range(2):
                    for dx in range(2):
                        cx, cy = ox + dx, oy + dy
                        if 0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT and grid[cy][cx]["type"] == 13:
                            grid[cy][cx]["power"]     = cur_power
                            grid[cy][cx]["max_power"] = max_power

                if research is not None and is_powered(tile):
                    if research.rs1_can_generate(rs1_active):
                        eff = get_power_efficiency(tile)
                        gained = 0.5 * eff * dt
                        cap = research.compute_rs1_cap(rs1_active)
                        headroom = cap - research.rp
                        if headroom > 0:
                            research.add_rp(min(gained, headroom))

            elif ttype == 12:
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                if tile.get("coal_buffer", 0) > 0:
                    tick_pollution_rate += POLLUTION_PER_MACHINE.get(12, 0)

            elif ttype == 17:
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                if tile.get("fuel_buffer", 0) > 0 and tile.get("fuel_item"):
                    tick_pollution_rate += POLLUTION_PER_MACHINE.get(17, 0)

            elif ttype == 21:
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                if is_powered(tile):
                    eff = get_power_efficiency(tile)
                    scrub_rate = MACHINE_STATS.get(21, {}).get("scrub_rate", 0)
                    tick_pollution_rate -= scrub_rate * eff

            elif ttype == 29:
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                if is_powered(tile) and tile.get("input_buffer", 0) > 0:
                    burn = min(0.5 * dt, tile.get("input_buffer", 0))
                    tile["input_buffer"] -= burn
                    if tile["input_buffer"] <= 1e-6:
                        tile["input_buffer"] = 0
                        tile["input_item"] = None
                    tick_pollution_rate += 0.003

            elif ttype == 49:
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                if tile.get("input_buffer", 0) > 0:
                    burn = min(0.5 * dt, tile.get("input_buffer", 0))
                    tile["input_buffer"] -= burn
                    if tile["input_buffer"] <= 1e-6:
                        tile["input_buffer"] = 0
                        tile["input_item"] = None
                    tick_pollution_rate += POLLUTION_PER_MACHINE.get(49, 0.002)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            ttype = tile["type"]
            if ttype == 0:
                continue

            mdef = MACHINE_DEFS.get(ttype, {})
            if "output_port" in mdef and not mdef.get("drill") and not mdef.get("fluid_producer") and not mdef.get("diesel_gen"):
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                oport   = mdef["output_port"]
                buf_key = oport["buf"]
                ibk     = oport.get("item_buf", "output_item")
                rot     = grid[oy][ox].get("rotation", 0)
                mstats2 = MACHINE_STATS.get(ttype, {})
                tw2, th2 = mstats2.get("size", (1, 1))

                tile.setdefault("output_timer", 0)
                tile["output_timer"] += dt

                if tile["output_timer"] >= 0.5 and tile.get(buf_key, 0) > 0:
                    item = tile.get(ibk)
                    if item:
                        sx, sy  = oport["subtile"]
                        pd      = tuple(oport["push_dir"])
                        if rot != 0:
                            ax, ay, rd, _, _ = rotate_port(ox, oy, sx, sy, tw2, th2, pd, rot)
                            out_x, out_y = ax + rd[0], ay + rd[1]
                            dx, dy = rd
                        else:
                            out_x = ox + sx + pd[0]
                            out_y = oy + sy + pd[1]
                            dx, dy = pd
                        push_amt = tile[buf_key]
                        if push_item_to_neighbor(grid, item, out_x, out_y, dx, dy, push_amt):
                            tile[buf_key] = 0
                            tile[ibk] = None
                        elif push_amt > 1.0:
                            while tile.get(buf_key, 0) > 1e-6:
                                unit = min(1.0, tile[buf_key])
                                if push_item_to_neighbor(grid, item, out_x, out_y, dx, dy, unit):
                                    tile[buf_key] = max(0.0, tile[buf_key] - unit)
                                else:
                                    break
                            if tile.get(buf_key, 0) <= 1e-6:
                                tile[buf_key] = 0
                                tile[ibk] = None
                    tile["output_timer"] = 0

                oport2 = mdef.get("output_port2")
                if oport2:
                    res_buf = oport2["buf"]
                    res_ibk = oport2.get("item_buf", "residue_item")
                    tile.setdefault("residue_output_timer", 0)
                    tile["residue_output_timer"] += dt
                    if tile["residue_output_timer"] >= 0.5 and tile.get(res_buf, 0) > 0:
                        res_item = tile.get(res_ibk)
                        if res_item:
                            sx2, sy2 = oport2["subtile"]
                            pd2      = tuple(oport2["push_dir"])
                            if rot != 0:
                                ax2, ay2, rd2, _, _ = rotate_port(ox, oy, sx2, sy2, tw2, th2, pd2, rot)
                                out_x2, out_y2 = ax2 + rd2[0], ay2 + rd2[1]
                                dx2, dy2 = rd2
                            else:
                                out_x2 = ox + sx2 + pd2[0]
                                out_y2 = oy + sy2 + pd2[1]
                                dx2, dy2 = pd2
                            res_amt = tile[res_buf]
                            if push_item_to_neighbor(grid, res_item, out_x2, out_y2, dx2, dy2, res_amt):
                                tile[res_buf] = 0
                                tile[res_ibk] = None
                            elif res_amt > 1.0:
                                while tile.get(res_buf, 0) > 1e-6:
                                    unit2 = min(1.0, tile[res_buf])
                                    if push_item_to_neighbor(grid, res_item, out_x2, out_y2, dx2, dy2, unit2):
                                        tile[res_buf] = max(0.0, tile[res_buf] - unit2)
                                    else:
                                        break
                                if tile.get(res_buf, 0) <= 1e-6:
                                    tile[res_buf] = 0
                                    tile[res_ibk] = None
                        tile["residue_output_timer"] = 0

            elif ttype in (22, 23):
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
                tile.setdefault("output_timer", 0.0)
                tile["output_timer"] += dt
                if tile["output_timer"] >= 0.5 and tile.get("amount", 0) > 0 and tile.get("stored"):
                    out_x, out_y = ox, oy + 2
                    push_amt = 1 if ttype == 22 else 0.5
                    if tile["amount"] >= push_amt and push_item_to_neighbor(
                            grid, tile["stored"], out_x, out_y, 0, 1, push_amt):
                        tile["amount"] -= push_amt
                        if tile["amount"] <= 1e-6:
                            tile["amount"] = 0
                            tile["stored"] = None
                    tile["output_timer"] = 0.0

            elif ttype in INTERSECTION_TYPES:
                mstats = MACHINE_STATS.get(ttype, {})
                transfer_interval = mstats.get("transfer_interval", 0.5)
                push_per_tick     = mstats.get("push_per_tick", 1)
                tile["timer"] = tile.get("timer", 0) + dt
                if tile["timer"] >= transfer_interval:
                    for lane in ("lane_v", "lane_h"):
                        if not tile.get(f"{lane}_enabled", True):
                            continue
                        amt  = tile.get(f"{lane}_amount", 0)
                        item = tile.get(f"{lane}_stored")
                        exit_dir = tile.get(f"{lane}_exit")
                        if amt <= 0 or item is None or exit_dir is None:
                            continue
                        edx, edy = exit_dir
                        nx, ny = x + edx, y + edy
                        pushes_left = push_per_tick
                        while pushes_left > 0 and tile.get(f"{lane}_amount", 0) > 0:
                            if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT
                                    and can_connect(x, y, tile, nx, ny, grid[ny][nx])
                                    and push_item_to_neighbor(grid, item, nx, ny, edx, edy)):
                                tile[f"{lane}_amount"] -= 1
                                if tile[f"{lane}_amount"] == 0:
                                    tile[f"{lane}_stored"] = None
                                    tile[f"{lane}_exit"]   = None
                                pushes_left -= 1
                            else:
                                break
                    total = tile.get("lane_v_amount", 0) + tile.get("lane_h_amount", 0)
                    tile["amount"] = total
                    if total == 0:
                        tile["stored"] = None
                    else:
                        tile["stored"] = tile.get("lane_v_stored") or tile.get("lane_h_stored")
                    tile["timer"] = 0

            elif ttype in PIPE_TYPES:
                if tile.get("signal_blocked", False):
                    continue
                mstats = MACHINE_STATS.get(ttype, {})
                transfer_interval = mstats.get("transfer_interval", 0.5)
                push_per_tick     = mstats.get("push_per_tick", 1)
                tile["timer"] = tile.get("timer", 0) + dt
                if tile["timer"] >= transfer_interval and tile["amount"] > 0:
                    output_dirs = get_output_direction(tile)
                    if output_dirs:
                        if isinstance(output_dirs, list):
                            tile.setdefault("output_index", 0)
                            pushes_left = push_per_tick
                            stalled_dirs = 0
                            while pushes_left > 0 and tile["amount"] > 0 and stalled_dirs < len(output_dirs):
                                odir = output_dirs[tile["output_index"]]
                                nx, ny = x + odir[0], y + odir[1]
                                if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT
                                        and can_connect(x, y, tile, nx, ny, grid[ny][nx])
                                        and push_item_to_neighbor(grid, tile["stored"], nx, ny, odir[0], odir[1])):
                                    tile["amount"] -= 1
                                    if tile["amount"] == 0:
                                        tile["stored"] = None
                                    tile["output_index"] = (tile["output_index"] + 1) % len(output_dirs)
                                    pushes_left -= 1
                                    stalled_dirs = 0
                                else:
                                    tile["output_index"] = (tile["output_index"] + 1) % len(output_dirs)
                                    stalled_dirs += 1
                        else:
                            nx, ny = x + output_dirs[0], y + output_dirs[1]
                            pushes_left = push_per_tick
                            while pushes_left > 0 and tile["amount"] > 0:
                                if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT
                                        and can_connect(x, y, tile, nx, ny, grid[ny][nx])
                                        and push_item_to_neighbor(grid, tile["stored"], nx, ny, output_dirs[0], output_dirs[1])):
                                    tile["amount"] -= 1
                                    if tile["amount"] == 0:
                                        tile["stored"] = None
                                    pushes_left -= 1
                                else:
                                    break
                    tile["timer"] = 0

    for _gy2 in range(GRID_HEIGHT):
        for _gx2 in range(GRID_WIDTH):
            _gt = grid[_gy2][_gx2]
            if _gt.get("type", 0) not in _GATE_TYPES:
                continue
            _inputs = []
            for _ix, _iy in _gt.get("signal_inputs", []):
                if 0 <= _ix < GRID_WIDTH and 0 <= _iy < GRID_HEIGHT:
                    _src = grid[_iy][_ix]
                    if _src.get("type", 0) in _GATE_TYPES:
                        _inputs.append(_src.get("gate_output", 0))
                    else:
                        _inputs.append(_src.get("signal_value", 0))
            gtype = MACHINE_DEFS.get(_gt["type"], {}).get("gate_type", "AND")
            if not _inputs:
                _out = 0
            elif gtype == "NOT":
                _out = 0 if _inputs[0] else 1
            elif gtype == "AND":
                _out = 1 if all(_inputs) else 0
            elif gtype == "OR":
                _out = 1 if any(_inputs) else 0
            elif gtype == "XOR":
                _out = 1 if (sum(_inputs) % 2 == 1) else 0
            elif gtype == "NAND":
                _out = 0 if all(_inputs) else 1
            elif gtype == "NOR":
                _out = 0 if any(_inputs) else 1
            else:
                _out = 0
            _gt["gate_output"] = _out
    for _gy3 in range(GRID_HEIGHT):
        for _gx3 in range(GRID_WIDTH):
            _gt2 = grid[_gy3][_gx3]
            if _gt2.get("type", 0) not in _GATE_TYPES:
                continue
            _gout = _gt2.get("gate_output", 0)
            for _ox3, _oy3 in _gt2.get("signal_outputs", []):
                if 0 <= _ox3 < GRID_WIDTH and 0 <= _oy3 < GRID_HEIGHT:
                    grid[_oy3][_ox3]["signal_blocked"] = (_gout == 0)

    income_multiplier = get_pollution_income_multiplier(pollution)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            if tile["type"] not in (3, 83):
                continue
            if tile["type"] in (83,):
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue
            tile.setdefault("total_sold", 0)
            tile.setdefault("cooldown_timer", 0.0)
            if tile["cooldown_timer"] > 0:
                tile["cooldown_timer"] = max(0.0, tile["cooldown_timer"] - dt)

            dstats = MACHINE_STATS.get(tile["type"], {})
            depot_capacity  = dstats.get("capacity", 10)
            cooldown_time   = dstats.get("cooldown_time", 15.0)
            sell_bonus      = dstats.get("sell_bonus", 1.0)
            sell_threshold  = dstats.get("sell_threshold", 1.0)
            sell_at = max(1, int(depot_capacity * sell_threshold))

            if tile["amount"] >= sell_at and tile["stored"] is not None and tile["cooldown_timer"] <= 0:
                if protesters and protesters.is_blocking():
                    continue
                item_type   = tile["stored"]
                item_value  = (market.get_price(item_type) if market
                               else ITEM_VALUES.get(item_type, 0))
                sale_amount = tile["amount"] * item_value * income_multiplier * sell_bonus
                money      += sale_amount
                play_sell_sfx()
                sold_amount = tile["amount"]
                tile["total_sold"]    += sold_amount
                tile["cooldown_timer"] = cooldown_time

                if ui:
                    ui.stats_tracker.record_sale(item_type, sold_amount, sale_amount)

                for contract in contracts.get_active_contracts():
                    cid = contract["id"]
                    if contracts.get_contract_progress(cid):
                        contracts.update_contract_progress(cid, item_type, sold_amount)
                        if contracts.check_contract_completion(cid):
                            rewards = contracts.complete_contract(cid)
                            if rewards:
                                money += rewards.get("money", 0)
                                play_sell_sfx()
                                rp_earned = rewards.get("rp", 0)
                                if rp_earned and research:
                                    research.add_rp(rp_earned)
                                if ui:
                                    ui.refresh_buttons()
                                    ui.show_transaction_message("CONTRACT COMPLETE!", (255, 215, 0))

                tile["stored"] = None
                tile["amount"] = 0
            elif tile["amount"] >= depot_capacity:
                for contract in contracts.get_active_contracts():
                    cid = contract["id"]
                    if contracts.get_contract_progress(cid):
                        contracts.track_overflow(cid)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            if tile["type"] not in (51,):
                continue
            ox, oy = get_machine_origin(grid, x, y)
            if (x, y) != (ox, oy):
                continue
            tile.setdefault("cooldown_timer", 0.0)
            if tile["cooldown_timer"] > 0:
                tile["cooldown_timer"] = max(0.0, tile["cooldown_timer"] - dt)
            buf = tile.get("input_buffer", 0)
            item = tile.get("input_item")
            dstats = MACHINE_STATS.get(tile["type"], {})
            sell_cap       = dstats.get("sell_capacity", 400)
            cooldown_time  = dstats.get("cooldown_time", 80.0)
            sell_bonus     = dstats.get("sell_bonus", 1.0)
            sell_threshold = dstats.get("sell_threshold", 1.0)
            sell_at = sell_cap * sell_threshold

            for contract in contracts.get_active_contracts():
                cid = contract["id"]
                if buf >= sell_cap and contracts.get_contract_progress(cid):
                    contracts.track_overflow(cid)

            if buf >= sell_at and item is not None and tile["cooldown_timer"] <= 0:
                if protesters and protesters.is_blocking():
                    continue
                item_value = (market.get_price(item) if market
                              else ITEM_VALUES.get(item, 0))
                sale_amount = buf * item_value * income_multiplier * sell_bonus
                money += sale_amount
                play_sell_sfx()
                if ui:
                    ui.stats_tracker.record_sale(item, int(buf), sale_amount)
                for contract in contracts.get_active_contracts():
                    cid = contract["id"]
                    if contracts.get_contract_progress(cid):
                        contracts.update_contract_progress(cid, item, int(buf))
                        if contracts.check_contract_completion(cid):
                            rewards = contracts.complete_contract(cid)
                            if rewards:
                                money += rewards.get("money", 0)
                                play_sell_sfx()
                                rp_earned = rewards.get("rp", 0)
                                if rp_earned and research:
                                    research.add_rp(rp_earned)
                                if ui:
                                    ui.refresh_buttons()
                                    ui.show_transaction_message("CONTRACT COMPLETE!", (255, 215, 0))
                tile["input_buffer"] = 0
                tile["input_item"] = None
                tile["cooldown_timer"] = cooldown_time

    delta = tick_pollution_rate * dt
    if pollution + delta < 0 and pollution >= 0:
        pollution = 0.0
    else:
        pollution += delta
    pollution = max(0.0, min(2000.0, pollution))

    return money, pollution

def draw_connection_zones(world_surface, grid):
    GREEN      = (80, 255, 80)
    GREEN_EDGE = (150, 255, 150)
    RED        = (255, 80, 80)
    RED_EDGE   = (255, 150, 150)
    ORANGE     = (255, 160, 40)
    ORG_EDGE   = (255, 200, 100)

    drawn_origins = set()

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            ttype = tile["type"]
            if ttype == 0:
                continue

            mstats = MACHINE_STATS.get(ttype, {})
            tw, th = mstats.get("size", (1, 1))
            is_multi = tw > 1 or th > 1

            if is_multi:
                raw_origin = tile.get("origin", (x, y))
                origin = tuple(raw_origin) if isinstance(raw_origin, list) else raw_origin
                if origin in drawn_origins:
                    continue
                drawn_origins.add(origin)
                ox, oy = origin

                mdef = MACHINE_DEFS.get(ttype)

                if ttype == 12:
                    rot = grid[oy][ox].get("rotation", 0)
                    tx, ty, rd, _, _ = rotate_port(ox, oy, 0, 0, 2, 2, UP, rot)
                    rect = get_zone_rect(tx, ty, rd, is_input=True)
                    if rect:
                        pygame.draw.rect(world_surface, GREEN, rect)
                        pygame.draw.rect(world_surface, GREEN_EDGE, rect, 1)
                    continue

                if mdef and mdef.get("fluid_producer"):
                    rot = grid[oy][ox].get("rotation", 0)
                    sx_, sy_ = mdef.get("output_subtile", (1, 0))
                    dx_, dy_ = mdef.get("push_dir", (1, 0))
                    tw_, th_ = mstats.get("size", (1, 1))
                    tx, ty, rd, _, _ = rotate_port(ox, oy, sx_, sy_, tw_, th_, (dx_, dy_), rot)
                    rect = get_zone_rect(tx, ty, rd, is_input=False)
                    if rect:
                        pygame.draw.rect(world_surface, RED, rect)
                        pygame.draw.rect(world_surface, RED_EDGE, rect, 1)
                    continue

                if ttype == 17:
                    rot = grid[oy][ox].get("rotation", 0)
                    tw_, th_ = mstats.get("size", (1, 1))
                    tx, ty, rd, _, _ = rotate_port(ox, oy, 0, 0, tw_, th_, UP, rot)
                    rect = get_zone_rect(tx, ty, rd, is_input=True)
                    if rect:
                        pygame.draw.rect(world_surface, GREEN, rect)
                        pygame.draw.rect(world_surface, GREEN_EDGE, rect, 1)
                    continue

                if mdef and ("input_ports" in mdef or "output_port" in mdef):
                    rot = grid[oy][ox].get("rotation", 0)
                    tw_, th_ = mstats.get("size", (1, 1))
                    for port in mdef.get("input_ports", []):
                        sx, sy = port["subtile"]
                        fdx, fdy = port["from_dir"]
                        base_edge = (-fdx, -fdy)
                        tx, ty, rd, _, _ = rotate_port(ox, oy, sx, sy, tw_, th_, base_edge, rot)
                        rect = get_zone_rect(tx, ty, rd, is_input=True)
                        if rect:
                            pygame.draw.rect(world_surface, GREEN, rect)
                            pygame.draw.rect(world_surface, GREEN_EDGE, rect, 1)
                    oport = mdef.get("output_port")
                    if oport:
                        sx, sy = oport["subtile"]
                        pdx, pdy = oport["push_dir"]
                        tx, ty, rd, _, _ = rotate_port(ox, oy, sx, sy, tw_, th_, (pdx, pdy), rot)
                        rect = get_zone_rect(tx, ty, rd, is_input=False)
                        if rect:
                            pygame.draw.rect(world_surface, RED, rect)
                            pygame.draw.rect(world_surface, RED_EDGE, rect, 1)
                    oport2 = mdef.get("output_port2")
                    if oport2:
                        sx2, sy2 = oport2["subtile"]
                        pdx2, pdy2 = oport2["push_dir"]
                        tx2, ty2, rd2, _, _ = rotate_port(ox, oy, sx2, sy2, tw_, th_, (pdx2, pdy2), rot)
                        rect2 = get_zone_rect(tx2, ty2, rd2, is_input=False)
                        if rect2:
                            pygame.draw.rect(world_surface, ORANGE, rect2)
                            pygame.draw.rect(world_surface, ORG_EDGE, rect2, 1)
                elif ttype in (22, 23):
                    in_rect = get_zone_rect(ox, oy, UP, is_input=True)
                    if in_rect:
                        pygame.draw.rect(world_surface, GREEN, in_rect)
                        pygame.draw.rect(world_surface, GREEN_EDGE, in_rect, 1)
                    out_rect = get_zone_rect(ox, oy + 1, DOWN, is_input=False)
                    if out_rect:
                        pygame.draw.rect(world_surface, RED, out_rect)
                        pygame.draw.rect(world_surface, RED_EDGE, out_rect, 1)
                else:
                    origin_tile = grid[oy][ox]
                    output_dir = get_output_direction(origin_tile)
                    if output_dir:
                        dirs = output_dir if isinstance(output_dir, list) else [output_dir]
                        for d in dirs:
                            rect = get_zone_rect_for_multitile(ox, oy, d, tw, th, is_input=False)
                            if rect:
                                pygame.draw.rect(world_surface, RED, rect)
                                pygame.draw.rect(world_surface, RED_EDGE, rect, 1)
                    input_dir = get_input_direction(origin_tile)
                    if input_dir:
                        dirs = input_dir if isinstance(input_dir, list) else [input_dir]
                        for d in dirs:
                            rect = get_zone_rect_for_multitile(ox, oy, d, tw, th, is_input=True)
                            if rect:
                                pygame.draw.rect(world_surface, GREEN, rect)
                                pygame.draw.rect(world_surface, GREEN_EDGE, rect, 1)
                continue

            output_dir = get_output_direction(tile)
            if output_dir:
                dirs = output_dir if isinstance(output_dir, list) else [output_dir]
                for d in dirs:
                    rect = get_zone_rect(x, y, d, is_input=False)
                    if rect:
                        pygame.draw.rect(world_surface, RED, rect)
                        pygame.draw.rect(world_surface, RED_EDGE, rect, 1)

            input_dir = get_input_direction(tile)
            if input_dir:
                dirs = input_dir if isinstance(input_dir, list) else [input_dir]
                for d in dirs:
                    rect = get_zone_rect(x, y, d, is_input=True)
                    if rect:
                        pygame.draw.rect(world_surface, GREEN, rect)
                        pygame.draw.rect(world_surface, GREEN_EDGE, rect, 1)

def _draw_signal_wires(world_surface, grid):
    WIRE_COL  = (80, 255, 200)
    WIRE_DIM  = (40, 140, 110)
    seen = set()
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            ttype = tile.get("type", 0)
            if ttype in _GATE_TYPES:
                for ix, iy in tile.get("signal_inputs", []):
                    key = (min(x, ix), min(y, iy), max(x, ix), max(y, iy), "in")
                    if key in seen: continue
                    seen.add(key)
                    x1 = ix * TILE_SIZE + TILE_SIZE // 2
                    y1 = iy * TILE_SIZE + TILE_SIZE // 2
                    x2 = x  * TILE_SIZE + TILE_SIZE // 2
                    y2 = y  * TILE_SIZE + TILE_SIZE // 2
                    pygame.draw.line(world_surface, WIRE_COL, (x1, y1), (x2, y2), 2)
                    pygame.draw.circle(world_surface, WIRE_COL, (x1, y1), 3)
                    pygame.draw.circle(world_surface, WIRE_COL, (x2, y2), 3)
            if ttype in _GATE_TYPES:
                gout = tile.get("gate_output", 0)
                col  = WIRE_COL if gout == 1 else WIRE_DIM
                for ox2, oy2 in tile.get("signal_outputs", []):
                    key = (x, y, ox2, oy2, "out")
                    if key in seen: continue
                    seen.add(key)
                    x1 = x   * TILE_SIZE + TILE_SIZE // 2
                    y1 = y   * TILE_SIZE + TILE_SIZE // 2
                    x2 = ox2 * TILE_SIZE + TILE_SIZE // 2
                    y2 = oy2 * TILE_SIZE + TILE_SIZE // 2
                    pygame.draw.line(world_surface, col, (x1, y1), (x2, y2), 2)
                    pygame.draw.circle(world_surface, col, (x2, y2), 3)


def _machine_pixel_center(grid, tx, ty):
    ox, oy = get_any_origin(grid, tx, ty)
    ttype = grid[oy][ox].get("type", 0)
    mstats = MACHINE_STATS.get(ttype, {})
    size = mstats.get("size", (1, 1))
    rot = grid[oy][ox].get("rotation", 0)
    w, h = size
    if (rot // 90) % 2 == 1:
        w, h = h, w
    return ox * TILE_SIZE + w * TILE_SIZE // 2, oy * TILE_SIZE + h * TILE_SIZE // 2


def draw_power_connections(world_surface, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            if "power_connections" not in tile:
                continue
            stale = []
            for conn in tile["power_connections"]:
                cx, cy = conn
                if not (0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT):
                    stale.append(conn); continue
                if grid[cy][cx].get("type", 0) == 0:
                    stale.append(conn); continue
            for conn in stale:
                tile["power_connections"].remove(conn)

            for conn_x, conn_y in tile["power_connections"]:
                start_x, start_y = _machine_pixel_center(grid, x, y)
                end_x,   end_y   = _machine_pixel_center(grid, conn_x, conn_y)
                pygame.draw.line(world_surface, (255, 200, 50),
                                 (start_x, start_y), (end_x, end_y), 2)
                pygame.draw.circle(world_surface, (255, 220, 100), (start_x, start_y), 3)
                pygame.draw.circle(world_surface, (255, 220, 100), (end_x, end_y), 3)
                dx_l = end_x - start_x
                dy_l = end_y - start_y
                length = math.hypot(dx_l, dy_l)
                if length > 8:
                    ux, uy = dx_l / length, dy_l / length
                    perp_x, perp_y = -uy, ux
                    mx_, my_ = (start_x + end_x) / 2, (start_y + end_y) / 2
                    head_len = 9
                    head_wid = 6
                    tip = (mx_ + ux * head_len, my_ + uy * head_len)
                    p1  = (mx_ - ux * head_len * 0.4 + perp_x * head_wid,
                           my_ - uy * head_len * 0.4 + perp_y * head_wid)
                    p2  = (mx_ - ux * head_len * 0.4 - perp_x * head_wid,
                           my_ - uy * head_len * 0.4 - perp_y * head_wid)
                    pygame.draw.polygon(world_surface, (255, 235, 130), [tip, p1, p2])
                    pygame.draw.polygon(world_surface, (110, 70, 20), [tip, p1, p2], 1)

def draw_power_range(world_surface, grid, selected_tile_pos, research=None):
    if not selected_tile_pos:
        return

    gx, gy = selected_tile_pos
    tile = grid[gy][gx]
    machine_stats = MACHINE_STATS.get(tile["type"], {})

    if "power_range" not in machine_stats:
        return

    power_range = machine_stats["power_range"]

    display_range = min(power_range, max(GRID_WIDTH, GRID_HEIGHT) + 1)

    gx, gy = get_any_origin(grid, gx, gy)
    size = machine_stats.get("size", (1, 1))
    rot  = grid[gy][gx].get("rotation", 0)
    w, h = size
    if (rot // 90) % 2 == 1:
        w, h = h, w
    cx = gx + w // 2
    cy = gy + h // 2

    left   = max(0,           cx - display_range)     * TILE_SIZE
    top    = max(0,           cy - display_range)     * TILE_SIZE
    right  = min(GRID_WIDTH,  cx + 1 + display_range) * TILE_SIZE
    bottom = min(GRID_HEIGHT, cy + 1 + display_range) * TILE_SIZE
    rect_w = right - left
    rect_h = bottom - top

    if rect_w <= 0 or rect_h <= 0:
        return

    fs = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
    fs.fill((255, 200, 50, 22))
    pygame.draw.rect(fs, (255, 200, 50, 130), (0, 0, rect_w, rect_h), 2)
    world_surface.blit(fs, (left, top))

pygame.init()

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_image_defs = [
    (2,  "assets/Drills/Coal-Drill.png",          (TILE_SIZE, TILE_SIZE)),
    (1,  "assets/Pipes/Pipe.png",                  (TILE_SIZE, TILE_SIZE)),
    (3,  "assets/Depot/Van-Depot.png",             (TILE_SIZE, TILE_SIZE)),
    (4,  "assets/Pipes/L-Pipe-R.png",              (TILE_SIZE, TILE_SIZE)),
    (5,  "assets/Pipes/L-Pipe-L.png",              (TILE_SIZE, TILE_SIZE)),
    (6,  "assets/Pipes/Merger.png",                (TILE_SIZE, TILE_SIZE)),
    (7,  "assets/Pipes/Splitter.png",              (TILE_SIZE, TILE_SIZE)),
    (8,  "assets/Drills/Iron-Drill.png",           (TILE_SIZE, TILE_SIZE)),
    (9,  "assets/Processors/Furnace.png",          (TILE_SIZE, TILE_SIZE)),
    (10, "assets/Processors/Ingot-Molder.png",     (TILE_SIZE, TILE_SIZE)),
    (11, "assets/Generators/Solar-Panel.png",      (TILE_SIZE, TILE_SIZE)),
    (12, "assets/Generators/Coal-Generator.png",   None),
    (13, "assets/Stations/Research-station.png",   None),
    (14, "assets/Processors/Blast-Furnace.png",    None),
    (15, "assets/Drills/Oil-Rig.png",              None),
    (16, "assets/Processors/Diesel-Refinery.png",  None),
    (17, "assets/Generators/Diesel-Generator.png", None),
    (18, "assets/Processors/Sawmill.png",          None),
    (19, "assets/Processors/Press.png",            None),
    (20, "assets/Processors/Roller.png",           None),
    (22, "assets/Storage/Item-Silo.png",               None),
    (23, "assets/Storage/Fluid-Silo.png",              None),
    (21, "assets/Stations/Scrubber.png",            None),
    (24, "assets/Generators/Solar-Panel-2.png",     (TILE_SIZE, TILE_SIZE)),
    (25, "assets/Generators/Solar-Panel-3.png",     (TILE_SIZE, TILE_SIZE)),
    (26, "assets/Generators/Wind-Turbine-1.png",    None),
    (27, "assets/Generators/Wind-Turbine-2.png",    None),
    (28, "assets/Generators/Wind-Turbine-3.png",    None),
    (29, "assets/Processors/Liquid-Burner.png",     None),
    (30, "assets/Drills/Copper-Drill.png",           None),
    (31, "assets/Drills/Soil-Excavator.png",         None),
    (32, "assets/Drills/Quarry.png",                 None),
    (33, "assets/Processors/Grinder.png",            None),
    (34, "assets/Processors/Raw-Mill.png",           None),
    (35, "assets/Processors/Industrial-Kiln.png",    None),
    (36, "assets/Drills/Water-Pump.png",             None),
    (38, "assets/Processors/Concrete-Plant.png",     None),
    (39, "assets/Processors/Craft-Assembler.png",    None),
    (40, "assets/Processors/Steam-Cracking-Plant.png", None),
    (41, "assets/Processors/Plastic-Refinery.png",   None),
    (43, "assets/Processors/Plastic-Production-Facility.png", None),
    (44, "assets/Processors/Plastic-Molding-Machine.png", None),
    (45, "assets/Drills/Natural-Gas-Well.png",           None),
    (46, "assets/Processors/Condenser.png",              None),
    (47, "assets/Processors/Gas-Refinery.png",           None),
    (49, "assets/Processors/Gas-Burner.png",             None),
    (50, "assets/Processors/Kiln.png",                   None),
    (51, "assets/Logistics/Liquid-Truck-Depot.png",      None),
    (53, "assets/Drills/Tree-Farm.png",                  None),
    (55, "assets/Processors/Gold-Acid-Refinery.png",     None),
    (57, "assets/Processors/Industrial-Electric-Furnace.png", None),
    (58, "assets/Processors/Alloyer.png",                None),
    (59, "assets/Drills/Lithium-Ore-Drill.png",          None),
    (60, "assets/Processors/Chemical-Reactor.png",       None),
    (61, "assets/Processors/Advanced-Assembler.png",     None),
    (64, "assets/Processors/Water-Treatment-Plant.png",  None),
    (65, "assets/Processors/Chemical-Plant.png",         None),
    (68, "assets/Drills/Mineshaft-Drill.png",            None),
    (70, "assets/Drills/Lithium-Brine-Extractor.png",    None),
    (77, "assets/Processors/Lathe.png",                  None),
    (78, "assets/Processors/Foundry.png",                None),
    (79, "assets/Processors/Logic-Assembler.png",        None),
    (81, "assets/Processors/Electrolysis-Plant.png",     None),
    (82, "assets/Processors/Filtration-Plant.png",       None),
    (83, "assets/Logistics/Huge-Truck-Depot.png",        None),
    (87, "assets/Processors/Coal-Liquefaction-Plant.png",None),
    (89, "assets/Processors/Liquid-Boiler.png",          None),
    (90, "assets/Drills/Air-Separation-Unit.png",        None),
    (91, "assets/Processors/Bottling-Plant.png",         None),
    (92, "assets/Processors/Industrial-Plastic-Molder.png", None),
    (93, "assets/Processors/Paper-Mill.png",             None),
    (96, "assets/Power/Nuclear-Power-Plant.png",         None),
    (97, "assets/Power/LV-Pole.png",                     None),
    (98, "assets/Power/MV-Pole.png",                     None),
    (99, "assets/Power/HV-Pole.png",                     None),
    (100, "assets/Power/MV-Battery.png",                 None),
    (101, "assets/Power/HV-Battery.png",                 None),
    (102, "assets/Power/HV-Transformer.png",             None),
    (103, "assets/Logic/NAND-Gate.png",                  None),
    (104, "assets/Logic/NOR-Gate.png",                   None),
    (105, "assets/Logic/NOT-Gate.png",                   None),
    (106, "assets/Power/Steam-Turbine.png",              None),
    (107, "assets/Power/Gasoline-Generator.png",         None),
    (108, "assets/Power/Coal-Power-Plant.png",           None),
]

for _mid, _rel_path, _size in _image_defs:
    _tried_paths = []
    _img = None
    for _base in ("", _SCRIPT_DIR):
        _full_path = os.path.join(_base, _rel_path) if _base else _rel_path
        _tried_paths.append(_full_path)
        if os.path.exists(_full_path):
            try:
                _img = pygame.image.load(_full_path).convert_alpha()
                if _size:
                    _img = pygame.transform.scale(_img, _size)
                MACHINE_IMAGES[_mid] = _img
                print(f"Loaded image {_mid}: {_full_path} -> {_img.get_size()}")
                break
            except Exception as _e:
                print(f"Warning: Error loading {_full_path} for machine {_mid}: {_e}")
    if _img is None:
        print(f"Warning: Could not find image for machine {_mid}. Tried: {_tried_paths}")

_img_render_cache: dict = {}

def _get_render_img(tile_value, pw, ph, rotation):
    key = (tile_value, pw, ph, rotation)
    if key in _img_render_cache:
        return _img_render_cache[key]

    img = MACHINE_IMAGES[tile_value]
    if rotation != 0:
        img = pygame.transform.rotate(img, rotation)
    if img.get_size() != (pw, ph):
        img = pygame.transform.scale(img, (pw, ph))

    if img.get_colorkey() is None:
        w2, h2 = img.get_size()
        step   = max(1, min(w2, h2) // 8)
        opaque = all(img.get_at((x, y))[3] >= 128
                     for y in range(0, h2, step)
                     for x in range(0, w2, step))
        if opaque:
            r, g, b = img.get_at((0, 0))[:3]
            if max(r, g, b) <= 30:
                img = img.copy()
                img.set_colorkey((r, g, b))

    _img_render_cache[key] = img
    return img

_sheet_path = None
for _base in ("", _SCRIPT_DIR):
    _sp = os.path.join(_base, "machines_sheet.png") if _base else "machines_sheet.png"
    if os.path.exists(_sp):
        _sheet_path = _sp
        break
if _sheet_path:
    try:
        _msheet = pygame.image.load(_sheet_path).convert_alpha()
        _mcell = 64
        _max_idx = _msheet.get_width() // _mcell
        for _mid in range(_max_idx):
            if _mid not in MACHINE_IMAGES and _mid > 0:
                _sr = pygame.Rect(_mid * _mcell, 0, _mcell, _mcell)
                if _sr.right <= _msheet.get_width():
                    MACHINE_IMAGES[_mid] = _msheet.subsurface(_sr).copy()
        print(f"Loaded machine sheet: {_sheet_path} ({_max_idx} cells)")
    except Exception as _e:
        print(f"Warning: Could not load machines_sheet.png: {_e}")

_menu_clock = pygame.time.Clock()
_menu_result = run_menu(screen, _menu_clock)
if _menu_result is None:
    pygame.quit()
    import sys; sys.exit()

_active_slot, _is_new_save = _menu_result
_activate_slot(_active_slot)
from menu import stop_music, play_music, play_click_sfx, play_sell_sfx, play_button_sfx, play_power_connect_sfx, play_power_fail_sfx, play_research_sfx, play_quit_sfx
stop_music()
play_music("SFX/Game/game1.wav")
_tutorial = TutorialOverlay()
if _is_new_save:
    _tutorial.start()

grid = load_grid()
money = load_money()
pollution = load_pollution()
contracts = ContractManager()
contracts.load_cheats()
contracts.sweep_on_load()
research = ResearchManager()
bank = LoanManager()
protesters = ProtestManager()
market = MarketManager()
run = True
ui = DrawGrid(contracts, research)
ui.bank = bank
ui.protesters = protesters
ui.market = market

play_area_width = SCREEN_WIDTH
grid_pixel_width = GRID_WIDTH * TILE_SIZE
grid_pixel_height = GRID_HEIGHT * TILE_SIZE
camera_x = (play_area_width - grid_pixel_width) / 2
camera_y = (SCREEN_HEIGHT - grid_pixel_height) / 2
zoom = 1.0
min_zoom = 0.5
max_zoom = 4.0

camera_velocity_x = 0
camera_velocity_y = 0
camera_speed = 300

building_rotation = 0

show_zones = False
power_mode = False
power_source = None
smoke_particles = []
pipe_dots = []
warning_flash_time = 0
wind_speed = 0.65
autosave_timer = 0.0
AUTOSAVE_INTERVAL = 30.0

machine_count_timer = 0.0
MACHINE_COUNT_INTERVAL = 1.0

PIPE_DRAG_TIERS = {1: (1, 4, 5), 119: (119, 120, 121), 125: (125, 126, 127)}
_FLOW_TO_ROT = {DOWN: 0, RIGHT: 90, UP: 180, LEFT: 270}
pipe_drag_active = False
pipe_drag_last = None
pipe_drag_dir = None
pipe_drag_tiles = set()

def _pipe_variant_for_turn(tier, d_in, d_out):
    straight, l_r, l_l = PIPE_DRAG_TIERS[tier]
    rot = _FLOW_TO_ROT[d_in]
    if d_in == d_out:
        return straight, rot
    for lt in (l_r, l_l):
        if rotate_direction(MACHINE_STATS[lt]["output_dir"], rot) == d_out:
            return lt, rot
    return straight, rot

def _drag_place_pipe(gx, gy, ttype, rotation):
    global money
    if not (0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT):
        return False
    if grid[gy][gx]["type"] != 0:
        return False
    if not contracts.is_machine_unlocked(ttype, research):
        return False
    cost = MACHINE_STATS.get(ttype, {}).get("cost", 0)
    if money < cost:
        return False
    money -= cost
    for _c in contracts.get_active_contracts():
        if contracts.get_contract_progress(_c["id"]):
            contracts.track_spending(_c["id"], cost)
    grid[gy][gx].update({"type": ttype, "stored": None, "amount": 0, "timer": 0,
                         "rotation": rotation, "power": 0, "max_power": 0,
                         "power_connections": [], "origin": (gx, gy)})
    return True

def _drag_convert_pipe(gx, gy, tier, new_type, rotation):
    global money
    t = grid[gy][gx]
    if t["type"] not in PIPE_DRAG_TIERS[tier]:
        return
    diff = MACHINE_STATS.get(new_type, {}).get("cost", 0) - MACHINE_STATS.get(t["type"], {}).get("cost", 0)
    if diff > money:
        return
    money -= diff
    t["type"] = new_type
    t["rotation"] = rotation

def _step_toward(a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return None
    if abs(dx) >= abs(dy) and dx != 0:
        return (1 if dx > 0 else -1, 0)
    return (0, 1 if dy > 0 else -1)

def _capture_blueprint(x_lo, y_lo, x_hi, y_hi):
    machines = []
    seen = set()
    for yy in range(y_lo, y_hi + 1):
        for xx in range(x_lo, x_hi + 1):
            t = grid[yy][xx]
            if t["type"] == 0:
                continue
            raw = t.get("origin", (xx, yy))
            o = tuple(raw) if isinstance(raw, list) else raw
            if o in seen:
                continue
            seen.add(o)
            ox_b, oy_b = o
            if not (x_lo <= ox_b <= x_hi and y_lo <= oy_b <= y_hi):
                continue
            ot = grid[oy_b][ox_b]
            machines.append({"dx": ox_b - x_lo, "dy": oy_b - y_lo,
                             "type": ot["type"], "rotation": ot.get("rotation", 0),
                             "recipe_mode": ot.get("recipe_mode")})
    if not machines:
        return None
    return {"w": x_hi - x_lo + 1, "h": y_hi - y_lo + 1, "machines": machines}

def _blueprint_cost(bp):
    return sum(MACHINE_STATS.get(m["type"], {}).get("cost", 0) for m in bp["machines"])

def _paste_blueprint(bp, gx, gy):
    global money
    placed = skipped = 0
    spent = 0.0
    for m in bp["machines"]:
        ttype = m["type"]
        stats = MACHINE_STATS.get(ttype, {})
        if not contracts.is_machine_unlocked(ttype, research):
            skipped += 1; continue
        w, h = stats.get("size", (1, 1))
        if m["rotation"] % 180 != 0:
            w, h = h, w
        px_, py_ = gx + m["dx"], gy + m["dy"]
        ok = True
        for dy_ in range(h):
            for dx_ in range(w):
                cx, cy = px_ + dx_, py_ + dy_
                if not (0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT) or grid[cy][cx]["type"] != 0:
                    ok = False; break
            if not ok: break
        cost = stats.get("cost", 0)
        if not ok or money < cost:
            skipped += 1; continue
        money -= cost
        spent += cost
        for _c in contracts.get_active_contracts():
            if contracts.get_contract_progress(_c["id"]):
                contracts.track_spending(_c["id"], cost)
        for dy_ in range(h):
            for dx_ in range(w):
                grid[py_ + dy_][px_ + dx_].update({
                    "type": ttype, "stored": None, "amount": 0, "timer": 0,
                    "rotation": m["rotation"], "power": 0,
                    "max_power": stats.get("power_capacity", 0),
                    "power_connections": [], "origin": (px_, py_)})
        if m.get("recipe_mode"):
            grid[py_][px_]["recipe_mode"] = m["recipe_mode"]
        placed += 1
    return placed, skipped, spent

while run:
    screen.fill(BGC)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_grid()
            save_money(money)
            save_pollution(pollution)
            contracts.save_contracts()
            research.save()
            bank.save()
            protesters.save()
            market.save()
            _save_active_to_slot(_active_slot)
            time.sleep(0.5)
            run = False

        elif event.type == pygame.KEYDOWN:
            if ui.md_pending is not None:
                if event.key == pygame.K_y:
                    x_lo, y_lo, x_hi, y_hi, cnt, origins = ui.md_pending
                    wiped = 0
                    total_refund = 0.0
                    for (ox_r, oy_r) in origins:
                        if 0 <= ox_r < GRID_WIDTH and 0 <= oy_r < GRID_HEIGHT:
                            otype = grid[oy_r][ox_r].get("type", 0)
                            if otype != 0:
                                total_refund += MACHINE_STATS.get(otype, {}).get("cost", 0) * 0.8
                    for yy in range(GRID_HEIGHT):
                        for xx in range(GRID_WIDTH):
                            t = grid[yy][xx]
                            if t["type"] == 0:
                                continue
                            raw = t.get("origin", (xx, yy))
                            origin = tuple(raw) if isinstance(raw, list) else raw
                            if origin in origins:
                                grid[yy][xx] = {"type": 0, "stored": None, "amount": 0,
                                                 "timer": 0, "rotation": 0, "power": 0,
                                                 "max_power": 0, "power_connections": []}
                                wiped += 1
                    money += total_refund
                    play_sell_sfx()
                    ui.show_transaction_message(
                        f"Deleted {cnt} machines  +${total_refund:.2f}",
                        (120, 255, 140))
                    ui.md_pending = None
                    continue
                elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                    ui.md_pending = None
                    ui.show_transaction_message("Mass delete cancelled", (200, 200, 200))
                    continue
            if event.key == pygame.K_ESCAPE and ui.md_drag_start is not None:
                ui.md_drag_start = None
                ui.md_drag_end = None
                continue
            if ui.show_code_console:
                if event.key == pygame.K_ESCAPE:
                    ui.show_code_console = False
                    ui.console_input = ""
                elif event.key == pygame.K_RETURN:
                    result = ui.submit_console_code(contracts)
                    if result and result.get("money"):
                        money += result["money"]
                        save_money(money)
                        ui.refresh_buttons()
                elif event.key == pygame.K_BACKSPACE:
                    ui.console_input = ui.console_input[:-1]
                else:
                    if event.unicode and len(ui.console_input) < 32:
                        ui.console_input += event.unicode
            elif ui.build_searching:
                if event.key == pygame.K_ESCAPE:
                    ui.build_searching = False
                    ui.build_search = ""
                elif event.key == pygame.K_RETURN:
                    ui.build_searching = False
                elif event.key == pygame.K_BACKSPACE:
                    ui.build_search = ui.build_search[:-1]
                else:
                    if event.unicode and len(ui.build_search) < 24:
                        ui.build_search += event.unicode
            elif ui.market_searching:
                if event.key == pygame.K_ESCAPE:
                    if ui.market_search:
                        ui.market_search = ""
                    else:
                        ui.market_searching = False
                elif event.key == pygame.K_RETURN:
                    ui.market_searching = False
                elif event.key == pygame.K_BACKSPACE:
                    ui.market_search = ui.market_search[:-1]
                else:
                    if event.unicode and event.unicode.isprintable() and len(ui.market_search) < 30:
                        ui.market_search += event.unicode
            elif ui.show_recipe_book and ui.rb_search_focused:
                if event.key == pygame.K_ESCAPE:
                    if ui.rb_search_text:
                        ui.rb_search_text = ""
                    else:
                        ui.rb_search_focused = False
                elif event.key == pygame.K_RETURN:
                    ui.rb_search_focused = False
                elif event.key == pygame.K_BACKSPACE:
                    ui.rb_search_text = ui.rb_search_text[:-1]
                else:
                    if event.unicode and event.unicode.isprintable() and len(ui.rb_search_text) < 24:
                        ui.rb_search_text += event.unicode
            else:
                if event.key == pygame.K_ESCAPE:
                    if ui.bp_select_mode or ui.bp_paste_mode:
                        ui.bp_select_mode = False
                        ui.bp_paste_mode = False
                        ui.bp_drag_start = None
                        ui.bp_drag_end = None
                        ui.show_transaction_message("Blueprint cancelled", (200, 200, 200))
                    elif ui.show_settings_panel:
                        ui.show_settings_panel = False
                    elif ui.show_code_console:
                        ui.show_code_console = False
                        ui.console_input = ""
                    elif ui.show_recipe_book:
                        ui.show_recipe_book = False
                    elif ui.show_loans_panel:
                        ui.show_loans_panel = False
                    elif ui.show_stats_panel:
                        ui.show_stats_panel = False
                    elif ui.show_build_panel:
                        ui.show_build_panel = False
                    elif ui.show_contracts_panel:
                        ui.show_contracts_panel = False
                    elif ui.show_research_panel:
                        ui.show_research_panel = False
                    elif ui.active_tool >= 0:
                        ui.active_tool = -1
                elif event.key == pygame.K_c and not (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    ui.show_contracts_panel = not ui.show_contracts_panel
                    ui.show_research_panel = False
                    ui.show_build_panel = False
                    ui.show_stats_panel = False
                    ui.refresh_buttons()
                elif event.key == pygame.K_b:
                    ui.show_build_panel = not ui.show_build_panel
                    ui.show_contracts_panel = False
                    ui.show_research_panel = False
                    ui.show_stats_panel = False
                    if ui.show_build_panel and ui.active_tool == 0:
                        ui.active_tool = -1
                        ui.md_drag_start = None
                        ui.md_drag_end = None
                        ui.md_pending = None
                elif event.key == pygame.K_t:
                    if ui.show_build_panel and ui.build_panel_selected is not None:
                        ui.active_tool = ui.build_panel_selected
                        ui.show_build_panel = False
                        ui.md_drag_start = None
                        ui.md_drag_end = None
                        ui.md_pending = None
                        tool_name = MACHINE_STATS.get(ui.active_tool, {}).get("name", "")
                        ui.show_transaction_message(f"Placing: {tool_name}", (100, 200, 255))
                    else:
                        ui.show_research_panel = not ui.show_research_panel
                        ui.show_contracts_panel = False
                        ui.show_stats_panel = False
                elif event.key == pygame.K_x:
                    if ui.active_tool == 0:
                        ui.active_tool = -1
                    else:
                        ui.active_tool = 0
                        if power_mode:
                            power_mode = False
                            power_source = None
                elif event.key == pygame.K_r:
                    building_rotation = (building_rotation + 90) % 360
                elif event.key == pygame.K_z:
                    ui.debug_mode = not ui.debug_mode
                    ui.show_transaction_message(
                        f"Debug View: {'ON' if ui.debug_mode else 'OFF'}",
                        (80, 255, 80) if ui.debug_mode else (150, 150, 150),
                    )
                elif event.key == pygame.K_o:
                    ui.show_bottleneck_overlay = not ui.show_bottleneck_overlay
                    ui.show_transaction_message(
                        f"Bottleneck Overlay: {'ON' if ui.show_bottleneck_overlay else 'OFF'}",
                        (240, 105, 95) if ui.show_bottleneck_overlay else (150, 150, 150),
                    )
                elif event.key == pygame.K_g:
                    if ui.bp_select_mode or ui.bp_paste_mode:
                        ui.bp_select_mode = False
                        ui.bp_paste_mode = False
                        ui.bp_drag_start = None
                        ui.bp_drag_end = None
                        ui.show_transaction_message("Blueprint cancelled", (200, 200, 200))
                    else:
                        ui.bp_select_mode = True
                        ui.active_tool = -1
                        power_mode = False
                        power_source = None
                        ui.md_drag_start = None
                        ui.md_drag_end = None
                        ui.md_pending = None
                        ui.show_transaction_message(
                            "Blueprint: drag to select machines", (120, 200, 255))
                elif event.key == pygame.K_p:
                    power_mode = not power_mode
                    power_source = None
                    if power_mode:
                        if ui.active_tool == 0:
                            ui.active_tool = -1
                        elif ui.active_tool > 0:
                            ui.active_tool = -1
                        ui.md_drag_start = None
                        ui.md_drag_end = None
                        ui.md_pending = None
                    ui.show_transaction_message(
                        f"Power Mode: {'ON' if power_mode else 'OFF'}",
                        (255, 200, 50) if power_mode else (150, 150, 150),
                    )
                elif event.key == pygame.K_m:
                    ui.show_market_panel = not ui.show_market_panel
                    if not ui.show_market_panel:
                        ui.market_searching = False
                        ui.market_search    = ""
                        ui.market_scroll    = 0
                    ui.show_build_panel       = False
                    ui.show_contracts_panel   = False
                    ui.show_research_panel    = False
                    ui.show_stats_panel       = False
                elif event.key == pygame.K_n:
                    ui.show_stats_panel = not ui.show_stats_panel
                    ui.show_build_panel = False
                    ui.show_contracts_panel = False
                    ui.show_research_panel = False
                elif event.key == pygame.K_l:
                    ui.show_loans_panel = not ui.show_loans_panel
                    ui.show_build_panel = False
                    ui.show_contracts_panel = False
                    ui.show_research_panel = False
                    ui.show_stats_panel = False
                elif event.key == pygame.K_ESCAPE and ui.show_loans_panel:
                    ui.show_loans_panel = False
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    save_grid()
                    save_money(money)
                    save_pollution(pollution)
                    contracts.save_contracts()
                    research.save()
                    bank.save()
                    protesters.save()
                    market.save()
                    _save_active_to_slot(_active_slot)
                    ui.show_transaction_message("Game Saved", (100, 255, 100))
                elif event.key == pygame.K_k:
                    ui.show_recipe_book = not ui.show_recipe_book
                elif event.key == pygame.K_ESCAPE and ui.show_recipe_book:
                    ui.show_recipe_book = False
                elif event.key in (pygame.K_QUESTION, pygame.K_SLASH):
                    if event.key == pygame.K_SLASH and not (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                        pass
                    else:
                        ui.show_keybind_overlay = True
                elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if ui.selected_tile:
                        td, _, _ = ui.selected_tile
                        src_type = td.get("type", 0)
                        if src_type != 0:
                            clip = {"type": src_type}
                            for key in ("recipe_mode", "rotation"):
                                if key in td:
                                    clip[key] = td[key]
                            ui.clipboard_settings = clip
                            mname = MACHINE_STATS.get(src_type, {}).get("name", "?")
                            ui.show_transaction_message(
                                f"Copied: {mname}", (120, 200, 255))
                        else:
                            ui.show_transaction_message("Nothing to copy", (200, 150, 100))
                    else:
                        ui.show_transaction_message("Select a machine first", (200, 150, 100))
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    clip = ui.clipboard_settings
                    if not clip:
                        ui.show_transaction_message("Clipboard empty", (200, 150, 100))
                    elif not ui.selected_tile:
                        ui.show_transaction_message("Select a target machine", (200, 150, 100))
                    else:
                        td, tgx, tgy = ui.selected_tile
                        tgt_type = td.get("type", 0)
                        if tgt_type != clip["type"]:
                            ui.show_transaction_message(
                                "Type mismatch — can't paste", (235, 95, 95))
                        else:
                            raw_o = td.get("origin", (tgx, tgy))
                            ox_p, oy_p = tuple(raw_o) if isinstance(raw_o, list) else raw_o
                            origin_tile = grid[oy_p][ox_p]
                            applied = []
                            if "recipe_mode" in clip:
                                old = origin_tile.get("recipe_mode")
                                if old != clip["recipe_mode"]:
                                    origin_tile["input_buffer"] = 0
                                    origin_tile["input_item"] = None
                                origin_tile["recipe_mode"] = clip["recipe_mode"]
                                applied.append("recipe")
                            if applied:
                                ui.show_transaction_message(
                                    f"Pasted: {', '.join(applied)}", (120, 255, 160))
                            else:
                                ui.show_transaction_message(
                                    "Nothing to paste for this type", (200, 150, 100))

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_QUESTION, pygame.K_SLASH):
                ui.show_keybind_overlay = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if (event.button == 1 and ui.active_tool == 0 and ui.md_pending is None
                    and mx < play_area_width and ui.md_drag_start is None):
                world_x = (mx - camera_x) / zoom
                world_y = (my - camera_y) / zoom
                if 0 <= world_x < grid_pixel_width and 0 <= world_y < grid_pixel_height:
                    gx = int(world_x // TILE_SIZE)
                    gy = int(world_y // TILE_SIZE)
                    if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                        if grid[gy][gx]["type"] == 0:
                            ui.md_drag_start = (gx, gy)
                            ui.md_drag_end = (gx, gy)
                            continue

            if event.button == 1 and (ui.bp_select_mode or ui.bp_paste_mode) and mx < play_area_width:
                world_x = (mx - camera_x) / zoom
                world_y = (my - camera_y) / zoom
                if 0 <= world_x < grid_pixel_width and 0 <= world_y < grid_pixel_height:
                    gx = int(world_x // TILE_SIZE)
                    gy = int(world_y // TILE_SIZE)
                    if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                        if ui.bp_select_mode:
                            ui.bp_drag_start = (gx, gy)
                            ui.bp_drag_end = (gx, gy)
                        elif ui.blueprint:
                            placed, skipped, spent = _paste_blueprint(ui.blueprint, gx, gy)
                            if placed:
                                play_click_sfx()
                                msg = f"Pasted {placed} machines  -${spent:,.0f}"
                                if skipped:
                                    msg += f"  ({skipped} skipped)"
                                ui.show_transaction_message(msg, (120, 255, 160))
                            else:
                                ui.show_transaction_message(
                                    "Nothing pasted — blocked, locked, or too expensive",
                                    (235, 95, 95))
                        continue

            if event.button == 1:
                play_click_sfx()
                if _tutorial.active and _tutorial.handle_click((mx, my)):
                    continue
                if ui.handle_click((mx, my)):
                    if ui._power_toggle_requested:
                        ui._power_toggle_requested = False
                        power_mode = not power_mode
                        power_source = None
                        if power_mode:
                            if ui.active_tool >= 0:
                                ui.active_tool = -1
                            ui.md_drag_start = None
                            ui.md_drag_end = None
                            ui.md_pending = None
                        ui.show_transaction_message(
                            f"Power Mode: {'ON' if power_mode else 'OFF'}",
                            (255, 200, 50) if power_mode else (150, 150, 150),
                        )

                elif ui.show_loans_panel and ui.loans_panel_rect and ui.loans_panel_rect.collidepoint(mx, my):
                    consumed = False
                    for amt, btn in list(ui.loan_take_buttons.items()):
                        if btn.collidepoint(mx, my):
                            money, ok, msg = bank.take_loan(amt, money)
                            ui.show_transaction_message(msg, (180, 200, 255) if ok else (220, 150, 100))
                            save_money(money)
                            consumed = True
                            break
                    if not consumed:
                        for amt, btn in list(ui.loan_repay_buttons.items()):
                            if btn.collidepoint(mx, my):
                                money, paid = bank.repay(amt, money)
                                if paid > 0:
                                    ui.show_transaction_message(
                                        f"Repaid ${paid:,.0f}", (140, 220, 150))
                                    save_money(money)
                                else:
                                    ui.show_transaction_message(
                                        "Not enough cash to repay.", (220, 150, 100))
                                consumed = True
                                break
                elif (getattr(ui, "_loan_hud_rect", None)
                      and ui._loan_hud_rect.collidepoint(mx, my)):
                    ui.show_loans_panel = True
                elif ui.info_panel_rect and ui.info_panel_rect.collidepoint(mx, my):
                    handled_ctrl = False
                    for ctrl_key, btn_rect in ui.tile_ctrl_btn_rects.items():
                        if btn_rect.collidepoint(mx, my) and ui.selected_tile:
                            td, sgx, sgy = ui.selected_tile
                            ot = grid[sgy][sgx]
                            if ctrl_key == "lane_v_toggle":
                                ot["lane_v_enabled"] = not ot.get("lane_v_enabled", True)
                                ui.show_transaction_message(
                                    f"Vertical lane: {'ON' if ot['lane_v_enabled'] else 'OFF'}",
                                    (140, 220, 160) if ot["lane_v_enabled"] else (220, 140, 140))
                            elif ctrl_key == "lane_h_toggle":
                                ot["lane_h_enabled"] = not ot.get("lane_h_enabled", True)
                                ui.show_transaction_message(
                                    f"Horizontal lane: {'ON' if ot['lane_h_enabled'] else 'OFF'}",
                                    (140, 220, 160) if ot["lane_h_enabled"] else (220, 140, 140))
                            elif ctrl_key == "flush_depot":
                                ot["stored"] = None
                                ot["amount"] = 0
                                ot["input_buffer"] = 0
                                ot["input_item"] = None
                                ui.show_transaction_message("Depot cargo flushed", (240, 175, 110))
                            elif ctrl_key == "clear_buffers":
                                _cb_def = MACHINE_DEFS.get(ot.get("type", 0), {})
                                for _cb_port in _cb_def.get("input_ports", []):
                                    ot[_cb_port["buf"]] = 0
                                    if "item_buf" in _cb_port:
                                        ot[_cb_port["item_buf"]] = None
                                for _cb_op in (_cb_def.get("output_port"), _cb_def.get("output_port2")):
                                    if _cb_op:
                                        ot[_cb_op["buf"]] = 0
                                        ot[_cb_op.get("item_buf", "output_item")] = None
                                ot["timer"] = 0
                                ui.show_transaction_message("Buffers cleared", (235, 170, 115))
                            handled_ctrl = True
                            break
                    if handled_ctrl:
                        pass
                    else:
                        for recipe_key, btn_rect in ui.recipe_btn_rects.items():
                            if btn_rect.collidepoint(mx, my):
                                if ui.selected_tile:
                                    td, sgx, sgy = ui.selected_tile
                                    ot = grid[sgy][sgx]
                                    if ot.get("recipe_mode") != recipe_key:
                                        ot["input_buffer"] = 0
                                        ot["input_item"]   = None
                                        if ot.get("stored") and ot["stored"] != recipe_key:
                                            ot["stored"] = None
                                            ot["amount"] = 0
                                            ot["timer"] = 0
                                    ot["recipe_mode"] = recipe_key
                                    ui.show_transaction_message(
                                        f"Recipe: {recipe_key.replace('_',' ').title()}",
                                        (180, 120, 255))
                                break
                elif mx < play_area_width:
                    world_x = (mx - camera_x) / zoom
                    world_y = (my - camera_y) / zoom

                    if (0 <= world_x < grid_pixel_width and 0 <= world_y < grid_pixel_height):
                        gx = int(world_x // TILE_SIZE)
                        gy = int(world_y // TILE_SIZE)

                        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                            if power_mode:
                                tile = grid[gy][gx]
                                if tile["type"] == 0:
                                    ui.show_transaction_message("Empty tile!", (255, 100, 100))
                                    play_power_fail_sfx()
                                elif power_source is None:
                                    src_stats = MACHINE_STATS.get(tile["type"], {})
                                    is_src = (
                                        src_stats.get("type") in ("power_source", "power_pole", "power_storage")
                                        or src_stats.get("power_output", 0) > 0
                                        or "power_range" in src_stats
                                    )
                                    if is_src:
                                        if src_stats.get("size", (1, 1)) != (1, 1):
                                            gx, gy = get_machine_center(grid, gx, gy)

                                        power_source = (gx, gy)
                                        source_name = MACHINE_STATS.get(grid[gy][gx]["type"], {}).get("name", "Power Source")
                                        ui.show_transaction_message(f"{source_name} selected", (255, 200, 50))
                                    else:
                                        ui.show_transaction_message("Select power source first!", (255, 100, 100))
                                        play_power_fail_sfx()
                                else:
                                    source_tile = grid[power_source[1]][power_source[0]]
                                    machine_stats = MACHINE_STATS.get(tile["type"], {})
                                    source_stats = MACHINE_STATS.get(source_tile["type"], {})

                                    if machine_stats.get("size", (1, 1)) != (1, 1):
                                        target_gx, target_gy = get_machine_center(grid, gx, gy)
                                    else:
                                        target_gx, target_gy = gx, gy

                                    if (target_gx, target_gy) == (power_source[0], power_source[1]):
                                        ui.show_transaction_message("Can't connect to itself!", (255, 100, 100))
                                        play_power_fail_sfx()
                                        power_source = None
                                        continue

                                    power_range = source_stats.get("power_range", 999)
                                    distance = abs(target_gx - power_source[0]) + abs(target_gy - power_source[1])

                                    target_is_pure_source = (
                                        machine_stats.get("type") == "power_source"
                                        and machine_stats.get("power_output", 0) > 0
                                    )
                                    target_relay_ok = (
                                        machine_stats.get("type") in ("power_pole", "power_storage")
                                        or machine_stats.get("power_input", 0) > 0
                                    )

                                    if distance > power_range:
                                        ui.show_transaction_message(f"Out of range! (Max: {power_range})", (255, 100, 100))
                                        play_power_fail_sfx()
                                    elif target_is_pure_source and not target_relay_ok:
                                        ui.show_transaction_message(
                                            "Can't wire a generator to another generator.",
                                            (255, 130, 80))
                                        play_power_fail_sfx()
                                    elif ("power_input" in machine_stats or "power_capacity" in machine_stats):
                                        if (target_gx, target_gy) not in source_tile["power_connections"]:
                                            source_tile["power_connections"].append((target_gx, target_gy))
                                            ui.show_transaction_message("Power connected!", (100, 255, 100))
                                            play_power_connect_sfx()
                                        else:
                                            source_tile["power_connections"].remove((target_gx, target_gy))
                                            ui.show_transaction_message("Power disconnected!", (255, 150, 50))
                                            play_power_connect_sfx()
                                        power_source = None
                                    else:
                                        ui.show_transaction_message("Machine doesn't use power!", (255, 100, 100))
                                        play_power_fail_sfx()
                            else:
                                shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT
                                tool_to_place = ui.get_active_tool()
                                current_tile_type = grid[gy][gx]["type"]

                                if tool_to_place in PIPE_DRAG_TIERS and current_tile_type == 0:
                                    if not contracts.is_machine_unlocked(tool_to_place, research):
                                        ui.show_transaction_message("Complete contracts to unlock!", (255, 180, 50))
                                    elif _drag_place_pipe(gx, gy, tool_to_place, building_rotation):
                                        pipe_drag_active = True
                                        pipe_drag_last = (gx, gy)
                                        pipe_drag_dir = None
                                        pipe_drag_tiles = {(gx, gy)}
                                    else:
                                        ui.show_transaction_message("Not enough money!", (255, 50, 50))
                                    continue

                                if tool_to_place == -1:
                                    gx, gy = get_any_origin(grid, gx, gy)
                                    ui.handle_tile_click(grid, gx, gy)

                                elif tool_to_place == 0:
                                    if current_tile_type != 0:
                                        mstats_del = MACHINE_STATS.get(current_tile_type, {})
                                        base_size  = mstats_del.get("size", (1, 1))
                                        ox_del, oy_del = get_machine_origin(grid, gx, gy)
                                        rot_del = grid[oy_del][ox_del].get("rotation", 0)
                                        if rot_del % 180 != 0:
                                            msize_del = (base_size[1], base_size[0])
                                        else:
                                            msize_del = base_size
                                        sell_val = mstats_del.get("cost", 0) * 0.8
                                        money += sell_val
                                        if sell_val:
                                            play_sell_sfx()
                                            ui.show_transaction_message(f"+${sell_val:.2f} (Sold)", (100, 255, 100))

                                        empty_tile = lambda: {"type":0,"stored":None,"amount":0,"timer":0,"rotation":0,"power":0,"max_power":0,"power_connections":[]}

                                        for dy_d in range(msize_del[1]):
                                            for dx_d in range(msize_del[0]):
                                                tx_d = ox_del + dx_d
                                                ty_d = oy_del + dy_d
                                                if not (0 <= tx_d < GRID_WIDTH and 0 <= ty_d < GRID_HEIGHT):
                                                    continue
                                                for py_d in range(GRID_HEIGHT):
                                                    for px_d in range(GRID_WIDTH):
                                                        pc = grid[py_d][px_d].get("power_connections")
                                                        if pc and (tx_d, ty_d) in pc:
                                                            pc.remove((tx_d, ty_d))
                                                grid[ty_d][tx_d] = empty_tile()

                                        if ui.selected_tile:
                                            _, sel_x, sel_y = ui.selected_tile
                                            if (ox_del <= sel_x < ox_del + msize_del[0] and
                                                    oy_del <= sel_y < oy_del + msize_del[1]):
                                                ui.selected_tile = None

                                        if not shift_held:
                                            ui.active_tool = -1

                                else:
                                    if not contracts.is_machine_unlocked(tool_to_place, research):
                                        ui.show_transaction_message("Complete contracts to unlock!", (255, 180, 50))
                                    else:
                                        machine_stats = MACHINE_STATS.get(tool_to_place, {})
                                        building_size = machine_stats.get("size", (1, 1))
                                        if building_rotation % 180 != 0:
                                            building_size = (building_size[1], building_size[0])

                                        can_place = True
                                        for dy in range(building_size[1]):
                                            for dx in range(building_size[0]):
                                                check_x = gx + dx
                                                check_y = gy + dy
                                                if (check_x >= GRID_WIDTH or check_y >= GRID_HEIGHT
                                                        or grid[check_y][check_x]["type"] != 0):
                                                    can_place = False
                                                    break
                                            if not can_place:
                                                break

                                        if can_place:
                                            machine_cost = machine_stats.get("cost", 0)

                                            if money >= machine_cost:
                                                money -= machine_cost
                                                ui.show_transaction_message(f"-${machine_cost:.2f}", (255, 100, 100))

                                                for contract in contracts.get_active_contracts():
                                                    contract_id = contract["id"]
                                                    if contracts.get_contract_progress(contract_id):
                                                        contracts.track_spending(contract_id, machine_cost)

                                                for dy in range(building_size[1]):
                                                    for dx in range(building_size[0]):
                                                        place_x = gx + dx
                                                        place_y = gy + dy
                                                        grid[place_y][place_x]["type"]             = tool_to_place
                                                        grid[place_y][place_x]["stored"]           = None
                                                        grid[place_y][place_x]["amount"]           = 0
                                                        grid[place_y][place_x]["timer"]            = 0
                                                        grid[place_y][place_x]["rotation"]         = building_rotation
                                                        grid[place_y][place_x]["power"]            = 0
                                                        grid[place_y][place_x]["max_power"]        = machine_stats.get("power_capacity", 0)
                                                        grid[place_y][place_x]["power_connections"] = []
                                                        grid[place_y][place_x]["origin"]           = (gx, gy)

                                                        if tool_to_place == 3:
                                                            grid[place_y][place_x]["total_sold"] = 0

                                                if (ui.selected_tile
                                                        and ui.selected_tile[1] == gx
                                                        and ui.selected_tile[2] == gy):
                                                    ui.handle_tile_click(grid, gx, gy)

                                                if not shift_held:
                                                    ui.active_tool = -1
                                            else:
                                                ui.show_transaction_message("Not enough money!", (255, 50, 50))
                                        else:
                                            ui.show_transaction_message("Remove existing building first!", (255, 150, 50))

            elif event.button == 3:
                if ui.bp_select_mode or ui.bp_paste_mode:
                    ui.bp_select_mode = False
                    ui.bp_paste_mode = False
                    ui.bp_drag_start = None
                    ui.bp_drag_end = None
                    ui.show_transaction_message("Blueprint cancelled", (200, 200, 200))
                elif mx < play_area_width:
                    world_x = (mx - camera_x) / zoom
                    world_y = (my - camera_y) / zoom

                    if (0 <= world_x < grid_pixel_width and 0 <= world_y < grid_pixel_height):
                        gx = int(world_x // TILE_SIZE)
                        gy = int(world_y // TILE_SIZE)
                        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                            if power_mode:
                                power_source = None
                                ui.show_transaction_message("Selection cancelled", (200, 200, 200))
                            else:
                                gx, gy = get_any_origin(grid, gx, gy)
                                ui.handle_tile_click(grid, gx, gy)

            elif event.button == 4:
                if ui.show_build_panel or ui.show_contracts_panel or ui.show_research_panel or ui.show_stats_panel or ui.show_recipe_book or ui.show_market_panel:
                    ui.handle_scroll(1, (mx, my))
                else:
                    old_zoom = zoom
                    zoom = min(zoom + 0.1, max_zoom)
                    zoom_factor = zoom / old_zoom
                    camera_x = mx - (mx - camera_x) * zoom_factor
                    camera_y = my - (my - camera_y) * zoom_factor

            elif event.button == 5:
                if ui.show_build_panel or ui.show_contracts_panel or ui.show_research_panel or ui.show_stats_panel or ui.show_recipe_book or ui.show_market_panel:
                    ui.handle_scroll(-1, (mx, my))
                else:
                    old_zoom = zoom
                    zoom = max(zoom - 0.1, min_zoom)
                    zoom_factor = zoom / old_zoom
                    camera_x = mx - (mx - camera_x) * zoom_factor
                    camera_y = my - (my - camera_y) * zoom_factor

        elif event.type == pygame.MOUSEMOTION and (ui.md_drag_start is not None or ui.research_panning
                                                   or pipe_drag_active
                                                   or (ui.bp_select_mode and ui.bp_drag_start is not None)):
            ui.handle_mouse_motion(event.pos)
            if ui.md_drag_start is not None:
                mx, my = event.pos
                world_x = (mx - camera_x) / zoom
                world_y = (my - camera_y) / zoom
                gx = max(0, min(GRID_WIDTH - 1,  int(world_x // TILE_SIZE)))
                gy = max(0, min(GRID_HEIGHT - 1, int(world_y // TILE_SIZE)))
                ui.md_drag_end = (gx, gy)
            if ui.bp_select_mode and ui.bp_drag_start is not None:
                mx, my = event.pos
                world_x = (mx - camera_x) / zoom
                world_y = (my - camera_y) / zoom
                gx = max(0, min(GRID_WIDTH - 1,  int(world_x // TILE_SIZE)))
                gy = max(0, min(GRID_HEIGHT - 1, int(world_y // TILE_SIZE)))
                ui.bp_drag_end = (gx, gy)
            if pipe_drag_active:
                if ui.active_tool not in PIPE_DRAG_TIERS:
                    pipe_drag_active = False
                else:
                    tier = ui.active_tool
                    mx, my = event.pos
                    world_x = (mx - camera_x) / zoom
                    world_y = (my - camera_y) / zoom
                    tx = max(0, min(GRID_WIDTH - 1,  int(world_x // TILE_SIZE)))
                    ty = max(0, min(GRID_HEIGHT - 1, int(world_y // TILE_SIZE)))
                    while pipe_drag_last != (tx, ty):
                        d = _step_toward(pipe_drag_last, (tx, ty))
                        if d is None:
                            break
                        nx = pipe_drag_last[0] + d[0]
                        ny = pipe_drag_last[1] + d[1]
                        if not (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT):
                            break
                        if grid[ny][nx]["type"] != 0:
                            break
                        lx, ly = pipe_drag_last
                        if (lx, ly) in pipe_drag_tiles:
                            if pipe_drag_dir is None:
                                _drag_convert_pipe(lx, ly, tier, PIPE_DRAG_TIERS[tier][0], _FLOW_TO_ROT[d])
                            elif d != pipe_drag_dir:
                                turn_t, turn_rot = _pipe_variant_for_turn(tier, pipe_drag_dir, d)
                                _drag_convert_pipe(lx, ly, tier, turn_t, turn_rot)
                        if not _drag_place_pipe(nx, ny, PIPE_DRAG_TIERS[tier][0], _FLOW_TO_ROT[d]):
                            break
                        pipe_drag_tiles.add((nx, ny))
                        pipe_drag_dir = d
                        pipe_drag_last = (nx, ny)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and pipe_drag_active:
            pipe_drag_active = False
            pipe_drag_dir = None
            pipe_drag_tiles = set()
            if not (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                ui.active_tool = -1

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and ui.bp_select_mode and ui.bp_drag_start is not None:
            gx0, gy0 = ui.bp_drag_start
            gx1, gy1 = ui.bp_drag_end or ui.bp_drag_start
            x_lo, x_hi = min(gx0, gx1), max(gx0, gx1)
            y_lo, y_hi = min(gy0, gy1), max(gy0, gy1)
            ui.bp_drag_start = None
            ui.bp_drag_end = None
            bp = _capture_blueprint(x_lo, y_lo, x_hi, y_hi)
            if bp:
                ui.blueprint = bp
                ui.bp_select_mode = False
                ui.bp_paste_mode = True
                ui.show_transaction_message(
                    f"Blueprint: {len(bp['machines'])} machines "
                    f"(${_blueprint_cost(bp):,.0f}) — click to paste",
                    (120, 200, 255))
            else:
                ui.show_transaction_message("No machines in selection", (200, 150, 100))

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and ui.md_drag_start is not None:
            gx0, gy0 = ui.md_drag_start
            gx1, gy1 = ui.md_drag_end or ui.md_drag_start
            x_lo, x_hi = min(gx0, gx1), max(gx0, gx1)
            y_lo, y_hi = min(gy0, gy1), max(gy0, gy1)
            affected_origins = set()
            for yy in range(y_lo, y_hi + 1):
                for xx in range(x_lo, x_hi + 1):
                    t = grid[yy][xx]
                    if t["type"] != 0:
                        raw = t.get("origin", (xx, yy))
                        origin = tuple(raw) if isinstance(raw, list) else raw
                        affected_origins.add(origin)
            if affected_origins:
                ui.md_pending = (x_lo, y_lo, x_hi, y_hi, len(affected_origins), affected_origins)
            ui.md_drag_start = None
            ui.md_drag_end = None

    keys = pygame.key.get_pressed()
    if ui.active_tool == 0 and power_mode:
        power_mode = False
        power_source = None
    if ui.active_tool > 0 and power_mode:
        power_mode = False
        power_source = None
    camera_velocity_x = 0
    camera_velocity_y = 0

    if keys[pygame.K_w]:
        camera_velocity_y = camera_speed
    if keys[pygame.K_s]:
        camera_velocity_y = -camera_speed
    if keys[pygame.K_a]:
        camera_velocity_x = camera_speed
    if keys[pygame.K_d]:
        camera_velocity_x = -camera_speed

    dt = clock.get_time() / 1000
    dt = min(dt, 0.05)

    camera_x += camera_velocity_x * dt
    camera_y += camera_velocity_y * dt

    warning_flash_time += dt

    ui.stats_tracker.tick(dt)

    autosave_timer += dt
    if autosave_timer >= AUTOSAVE_INTERVAL:
        autosave_timer = 0.0
        save_grid()
        save_money(money)
        save_pollution(pollution)
        contracts.save_contracts()
        research.save()
        bank.save()
        protesters.save()
        market.save()
        _save_active_to_slot(_active_slot)
        ui.trigger_autosave_flash()

    for contract in contracts.get_active_contracts():
        contract_id = contract["id"]
        if contracts.get_contract_progress(contract_id):
            contracts.update_contract_time(contract_id, dt)

    for particle in smoke_particles[:]:
        particle["life"]  -= dt
        particle["x"]     += particle.get("vx", 0) * dt
        particle["y"]     -= particle["speed"] * dt
        particle["y"]     += particle.get("vy", 0) * dt
        particle["vy"]    = particle.get("vy", 0) + particle.get("gravity", 0) * dt
        particle["alpha"] -= particle.get("fade", 15) * dt
        if particle["life"] <= 0 or particle["alpha"] <= 0:
            smoke_particles.remove(particle)

    for dot in pipe_dots[:]:
        dot["life"]  -= dt
        dot["x"]     += dot["vx"] * dt
        dot["y"]     += dot["vy"] * dt
        dot["alpha"] -= 80 * dt
        if dot["life"] <= 0 or dot["alpha"] <= 0:
            pipe_dots.remove(dot)

    scaled_grid_width = grid_pixel_width * zoom
    scaled_grid_height = grid_pixel_height * zoom
    max_offset_x = grid_pixel_width * zoom * 0.5
    max_offset_y = grid_pixel_height * zoom * 0.5
    min_camera_x = play_area_width - scaled_grid_width - max_offset_x
    max_camera_x = max_offset_x
    min_camera_y = SCREEN_HEIGHT - scaled_grid_height - max_offset_y
    max_camera_y = max_offset_y
    camera_x = max(min(camera_x, max_camera_x), min_camera_x)
    camera_y = max(min(camera_y, max_camera_y), min_camera_y)

    money, pollution = update_world(grid, dt, money, pollution, contracts, ui,
                                     research, protesters, market)
    _protest_event = protesters.tick(dt, pollution)
    if _protest_event == "started":
        ui.show_transaction_message(
            "PROTESTERS BLOCKING TRUCKS!  Build scrubbers or wait 5 min.",
            (255, 80, 60))
    elif _protest_event == "dispersed":
        ui.show_transaction_message(
            "Protesters have dispersed.  Trucks running again.",
            (100, 255, 140))
    if market.tick(dt):
        ui.show_transaction_message("Market prices updated!", (255, 210, 80))
    _interest = bank.tick(dt)
    if _interest > 0:
        ui.show_transaction_message(
            f"Interest +${_interest:,.2f}  ({bank.rate*100:.2f}%/min)",
            (255, 150, 100))
    wind_speed += random.uniform(-0.3, 0.3) * dt
    wind_speed = max(0.1, min(1.0, wind_speed))

    machine_count_timer += dt
    if machine_count_timer >= MACHINE_COUNT_INTERVAL:
        machine_count_timer = 0.0
        active_progress_cids = [c["id"] for c in contracts.get_active_contracts()
                                if contracts.get_contract_progress(c["id"])]
        if active_progress_cids:
            drill_count = 0
            pipe_count = 0
            furnace_count = 0
            seen_origins = set()
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    t = grid[y][x].get("type", 0)
                    if t == 0:
                        continue
                    stats = MACHINE_STATS.get(t, {})
                    cat = stats.get("category")
                    if not cat:
                        continue
                    size = stats.get("size", (1, 1))
                    if size != (1, 1):
                        raw_o = grid[y][x].get("origin", (x, y))
                        o = tuple(raw_o) if isinstance(raw_o, list) else raw_o
                        if o in seen_origins:
                            continue
                        seen_origins.add(o)
                    if cat == "drill":
                        drill_count += 1
                    elif cat == "pipe":
                        pipe_count += 1
                    elif cat == "furnace":
                        furnace_count += 1
            for cid in active_progress_cids:
                contracts.track_machine_count(cid, "drill", drill_count)
                contracts.track_machine_count(cid, "pipe", pipe_count)
                contracts.track_machine_count(cid, "furnace", furnace_count)

    ui.check_story_milestones(money)
    play_area_rect = pygame.Rect(0, 0, play_area_width, SCREEN_HEIGHT)
    pygame.draw.rect(screen, (30, 30, 30), play_area_rect)

    world_surface = pygame.Surface((grid_pixel_width, grid_pixel_height), pygame.SRCALPHA)
    _gt = min(1.0, pollution / 500.0)
    _grass_color = (
        int(34 * (1 - _gt) + 120 * _gt),
        int(139 * (1 - _gt) + 110 * _gt),
        int(34 * (1 - _gt) + 50 * _gt),
    )
    world_surface.fill((*_grass_color, 255))

    for _gxi in range(GRID_WIDTH + 1):
        pygame.draw.line(world_surface, (55, 58, 55),
                         (_gxi * TILE_SIZE, 0), (_gxi * TILE_SIZE, grid_pixel_height), 1)
    for _gyi in range(GRID_HEIGHT + 1):
        pygame.draw.line(world_surface, (55, 58, 55),
                         (0, _gyi * TILE_SIZE), (grid_pixel_width, _gyi * TILE_SIZE), 1)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            TILE_VALUE = tile["type"]
            if TILE_VALUE == 0:
                continue

            mstats = MACHINE_STATS.get(TILE_VALUE, {})
            tile_w, tile_h = mstats.get("size", (1, 1))
            is_multi = tile_w > 1 or tile_h > 1

            if is_multi:
                ox, oy = get_machine_origin(grid, x, y)
                if (x, y) != (ox, oy):
                    continue

            px = x * TILE_SIZE
            py = y * TILE_SIZE
            rot_tile = tile.get("rotation", 0)
            if is_multi and rot_tile % 180 != 0:
                pw = TILE_SIZE * tile_h
                ph = TILE_SIZE * tile_w
            else:
                pw = TILE_SIZE * tile_w
                ph = TILE_SIZE * tile_h
            draw_rect = pygame.Rect(px, py, pw, ph)

            if TILE_VALUE in MACHINE_IMAGES:
                img = _get_render_img(TILE_VALUE, pw, ph, tile.get("rotation", 0))
                world_surface.blit(img, (px, py))
            else:
                colour = MACHINE_TYPES.get(TILE_VALUE, BGC)
                pygame.draw.rect(world_surface, colour, draw_rect)
                border_col = tuple(min(255, c + 60) for c in colour)
                pygame.draw.rect(world_surface, border_col, draw_rect, 2)
                if is_multi:
                    try:
                        lbl = mstats.get("name", f"T{TILE_VALUE}")
                        _lf = pygame.font.SysFont("Arial", 11, bold=True)
                        _ls = _lf.render(lbl, True, (240, 240, 200))
                        world_surface.blit(_ls, (px + pw // 2 - _ls.get_width() // 2,
                                                  py + ph // 2 - _ls.get_height() // 2))
                    except Exception:
                        pass

            cx_  = px + pw // 2
            cy_  = py + ph // 2
            rot_ = tile.get("rotation", 0)
            fx_ox = ox if is_multi else x
            fx_oy = oy if is_multi else y

            def _processing(t, ttype):
                mdef_ = MACHINE_DEFS.get(ttype, {})
                if mdef_.get("drill"):
                    return is_powered(t)
                if mdef_.get("fluid_producer"):
                    return is_powered(t) and t.get("fluid_buffer", 0) > 0
                if mdef_.get("diesel_gen"):
                    return t.get("fuel_buffer", 0) > 0
                if ttype == 12:
                    return t.get("coal_buffer", 0) > 0
                if "process" in mdef_:
                    return (is_powered(t) and t.get("input_buffer", 0) > 0 and t.get("timer", 0) > 0)
                if ttype == 11:
                    return True
                if ttype == 13:
                    return is_powered(t)
                return is_powered(t)

            proc = _processing(tile, TILE_VALUE)

            if TILE_VALUE in (2, 8) and proc and random.random() > 0.88:
                od = get_output_direction(tile)
                if od is None: od = DOWN
                odx, ody = od
                spx = cx_ + odx * (TILE_SIZE // 3)
                spy = cy_ + ody * (TILE_SIZE // 3)
                for _ in range(random.randint(1, 2)):
                    col = (90,60,30) if TILE_VALUE == 2 else (100,90,80)
                    smoke_particles.append({
                        "x": spx + random.randint(-4, 4), "y": spy + random.randint(-4, 4),
                        "vx": random.uniform(-12, 12), "vy": random.uniform(-6, 2),
                        "gravity": 28, "speed": random.uniform(4, 10),
                        "life": random.uniform(0.4, 0.9), "alpha": random.randint(140, 200),
                        "fade": 80, "size": random.randint(1, 2), "color": col, "shape": "rect",
                    })

            elif TILE_VALUE == 12 and proc and random.random() > 0.88:
                sx12, sy12 = port_pixel(fx_ox, fx_oy, 1, 0, 2, 2, rot_)
                smoke_particles.append({
                    "x": sx12 + random.randint(-3, 3), "y": sy12 + random.randint(-3, 3),
                    "vx": random.uniform(-2, 2), "vy": 0, "gravity": 0,
                    "speed": random.uniform(8, 15), "life": random.uniform(2.0, 3.5),
                    "alpha": random.randint(60, 100), "fade": 15,
                    "size": random.randint(2, 4), "color": (80, 80, 80), "shape": "circle",
                })

            elif TILE_VALUE == 15 and proc and random.random() > 0.97:
                smoke_particles.append({
                    "x": float(cx_), "y": float(cy_),
                    "vx": 0, "vy": 0, "gravity": 0, "speed": 0,
                    "life": 0.7, "alpha": 90, "fade": 110,
                    "size": 2, "color": (160, 120, 60), "shape": "ripple", "max_r": pw * 0.7,
                })

            elif TILE_VALUE == 9 and proc and random.random() > 0.82:
                col = random.choice([(255,200,40),(255,140,30),(255,80,20)])
                smoke_particles.append({
                    "x": cx_ + random.uniform(-6, 6), "y": cy_ + random.uniform(-2, 4),
                    "vx": random.uniform(-8, 8), "vy": 0, "gravity": -2,
                    "speed": random.uniform(10, 22), "life": random.uniform(0.5, 1.2),
                    "alpha": random.randint(180, 255), "fade": 90,
                    "size": 1, "color": col, "shape": "rect",
                })

            elif TILE_VALUE == 14 and proc:
                if random.random() > 0.75:
                    col = random.choice([(255,200,40),(255,150,30),(255,90,20),(255,60,10)])
                    smoke_particles.append({
                        "x": cx_ + random.uniform(-pw*0.3, pw*0.3),
                        "y": cy_ + random.uniform(-ph*0.2, ph*0.2),
                        "vx": random.uniform(-14, 14), "vy": 0, "gravity": -3,
                        "speed": random.uniform(14, 30), "life": random.uniform(0.4, 1.0),
                        "alpha": random.randint(160, 240), "fade": 100,
                        "size": random.randint(1, 2), "color": col, "shape": "rect",
                    })
                if random.random() > 0.96:
                    smoke_particles.append({
                        "x": float(cx_), "y": float(cy_),
                        "vx": 0, "vy": 0, "gravity": 0, "speed": 0,
                        "life": 0.5, "alpha": 35, "fade": 50,
                        "size": pw // 3, "color": (220, 60, 10), "shape": "glow",
                    })

            elif TILE_VALUE == 10 and tile.get("output_buffer", 0) > 0 and random.random() > 0.90:
                for _ in range(random.randint(2, 4)):
                    smoke_particles.append({
                        "x": cx_ + random.uniform(-4, 4), "y": cy_,
                        "vx": random.uniform(-18, 18), "vy": 0, "gravity": 0,
                        "speed": random.uniform(4, 8), "life": random.uniform(0.25, 0.55),
                        "alpha": random.randint(80, 160), "fade": 140,
                        "size": random.randint(2, 4), "color": (210, 230, 255), "shape": "circle",
                    })

            elif TILE_VALUE == 16 and proc and random.random() > 0.88:
                bx16, by16 = port_pixel(fx_ox, fx_oy, 2, 0, 3, 3, rot_)
                col = random.choice([(180,140,220),(140,200,140),(160,130,210)])
                smoke_particles.append({
                    "x": bx16 + random.uniform(-TILE_SIZE*0.4, TILE_SIZE*0.4),
                    "y": by16 + random.uniform(-TILE_SIZE*0.4, TILE_SIZE*0.4),
                    "vx": random.uniform(-3, 3), "vy": 0, "gravity": 0,
                    "speed": random.uniform(3, 7), "life": random.uniform(1.2, 2.5),
                    "alpha": random.randint(40, 80), "fade": 25,
                    "size": random.randint(2, 5), "color": col, "shape": "circle",
                })

            elif TILE_VALUE == 17 and proc and random.random() > 0.80:
                ex17, ey17 = port_pixel(fx_ox, fx_oy, 0, 0, 2, 1, rot_)
                _, _, exdir, _, _ = rotate_port(fx_ox, fx_oy, 0, 0, 2, 1, LEFT, rot_)
                col = random.choice([(80,120,255),(60,100,240),(255,140,30),(255,100,20)])
                smoke_particles.append({
                    "x": ex17 + random.uniform(-3, 3), "y": ey17 + random.uniform(-4, 4),
                    "vx": exdir[0] * random.uniform(8, 18), "vy": exdir[1] * random.uniform(8, 18),
                    "gravity": 0, "speed": 0, "life": random.uniform(0.2, 0.5),
                    "alpha": random.randint(120, 200), "fade": 150,
                    "size": random.randint(2, 4), "color": col, "shape": "circle",
                })

            elif TILE_VALUE == 13 and proc and random.random() > 0.92:
                col = random.choice([(80,200,255),(180,80,255),(60,240,200)])
                smoke_particles.append({
                    "x": cx_ + random.uniform(-pw*0.35, pw*0.35),
                    "y": cy_ + random.uniform(-ph*0.2, ph*0.2),
                    "vx": random.uniform(-3, 3), "vy": 0, "gravity": 0,
                    "speed": random.uniform(6, 14), "life": random.uniform(0.8, 1.8),
                    "alpha": random.randint(150, 220), "fade": 60,
                    "size": 1, "color": col, "shape": "rect",
                })

            elif TILE_VALUE == 11 and random.random() > 0.997:
                smoke_particles.append({
                    "x": float(px), "y": float(py),
                    "vx": 0, "vy": 0, "gravity": 0, "speed": 0,
                    "life": 0.22, "alpha": 180, "fade": 500, "size": pw,
                    "color": (255, 255, 255), "shape": "glint",
                    "px": float(px), "py": float(py), "pw": float(pw), "ph": float(ph),
                })

            elif TILE_VALUE == 18 and proc and random.random() > 0.85:
                sx18, sy18 = port_pixel(fx_ox, fx_oy, 2, 0, 3, 1, rot_)
                col = random.choice([(200,160,80),(180,140,60),(220,180,100)])
                smoke_particles.append({
                    "x": sx18 + random.uniform(-6, 6), "y": sy18 + random.uniform(-6, 6),
                    "vx": random.uniform(-20, 20), "vy": random.uniform(-12, 0),
                    "gravity": 20, "speed": random.uniform(2, 6),
                    "life": random.uniform(0.3, 0.8), "alpha": random.randint(120, 200),
                    "fade": 90, "size": 1, "color": col, "shape": "rect",
                })

            elif TILE_VALUE == 19 and proc and random.random() > 0.92:
                sx19, sy19 = port_pixel(fx_ox, fx_oy, 1, 0, 2, 1, rot_)
                _, _, spdir, _, _ = rotate_port(fx_ox, fx_oy, 1, 0, 2, 1, UP, rot_)
                col = random.choice([(255,240,100),(255,200,50),(220,220,255)])
                smoke_particles.append({
                    "x": sx19 + random.uniform(-3, 3), "y": sy19 + random.uniform(-3, 3),
                    "vx": spdir[0]*random.uniform(4,15) + random.uniform(-6,6),
                    "vy": spdir[1]*random.uniform(4,15) + random.uniform(-6,6),
                    "gravity": 30, "speed": 0,
                    "life": random.uniform(0.15, 0.4), "alpha": random.randint(180, 255),
                    "fade": 200, "size": 1, "color": col, "shape": "rect",
                })

            elif TILE_VALUE == 20 and proc and random.random() > 0.88:
                sx20, sy20 = port_pixel(fx_ox, fx_oy, 1, 0, 2, 1, rot_)
                col = random.choice([(255,220,80),(255,180,40),(200,200,255)])
                smoke_particles.append({
                    "x": sx20 + random.uniform(-TILE_SIZE*0.4, TILE_SIZE*0.4),
                    "y": sy20 + random.uniform(-4, 4),
                    "vx": random.uniform(-8, 8), "vy": random.uniform(-12, -4),
                    "gravity": 25, "speed": 0,
                    "life": random.uniform(0.2, 0.5), "alpha": random.randint(160, 240),
                    "fade": 160, "size": 1, "color": col, "shape": "rect",
                })

            if TILE_VALUE in PIPE_TYPES:
                pipe_has_item = tile.get("stored") and tile.get("amount", 0) > 0
                pipe_just_moved = tile.get("timer", 0) < 0.12
                if pipe_has_item and pipe_just_moved and random.random() > 0.5:
                    item = tile["stored"]
                    FLOW_COLORS = {
                        "coal": (60,50,40), "raw_iron": (160,100,60),
                        "liquid_iron": (255,120,0), "iron_ingot": (200,180,100),
                        "steel": (150,160,180), "crude_oil": (50,40,30),
                        "poor_quality_diesel": (120,100,40), "diesel": (160,140,50),
                        "refined_diesel": (200,180,60), "residue": (80,60,80),
                        "iron_plate": (180,190,200), "iron_plate2": (100,160,255),
                        "iron_coil": (140,200,180),
                    }
                    col = FLOW_COLORS.get(item, (180,180,180))
                    od = get_output_direction(tile)
                    if od:
                        if isinstance(od, list):
                            idx = tile.get("output_index", 0) % len(od)
                            od = od[idx]

            if not is_multi or (x, y) == (ox, oy):
                if TILE_VALUE not in (13,):
                    power_input = mstats.get("power_input", 0)
                    if power_input > 0:
                        current_power = tile.get("power", 0)
                        if 0 < current_power < power_input:
                            flash_intensity = (math.sin(warning_flash_time * 2) + 1) / 2
                            alpha = int(30 + flash_intensity * 40)
                            cx = px + pw // 2
                            cy = py + ph // 2
                            ts = max(6, pw // 6)
                            tri_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
                            pts = [(cx - px, cy - ts - py),
                                   (cx - ts - px, cy + ts - py),
                                   (cx + ts - px, cy + ts - py)]
                            pygame.draw.polygon(tri_surf, (255, 50, 50, alpha), pts)
                            pygame.draw.polygon(tri_surf, (200, 0, 0, min(255, alpha+40)), pts, 1)
                            world_surface.blit(tri_surf, (px, py))

    for particle in smoke_particles:
        col  = particle.get("color", (80, 80, 80))
        alph = max(0, min(255, int(particle["alpha"])))
        sx_  = int(particle["x"])
        sy_  = int(particle["y"])
        sz_  = max(1, particle["size"])
        shp  = particle.get("shape", "circle")

        if shp == "rect":
            s = pygame.Surface((sz_, sz_), pygame.SRCALPHA)
            s.fill((*col, alph))
            world_surface.blit(s, (sx_, sy_))

        elif shp == "circle":
            s = pygame.Surface((sz_*2+1, sz_*2+1), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, alph), (sz_, sz_), sz_)
            world_surface.blit(s, (sx_ - sz_, sy_ - sz_))

        elif shp == "ripple":
            max_r = particle.get("max_r", 20)
            age   = 1.0 - max(0, particle["life"] / 0.7)
            r     = int(age * max_r)
            if r > 0:
                s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*col, alph), (r+1, r+1), r, 1)
                world_surface.blit(s, (sx_ - r - 1, sy_ - r - 1))

        elif shp == "glow":
            for gi in range(3):
                gr = sz_ - gi * sz_//3
                if gr <= 0: break
                ga = alph // (gi+1)
                s  = pygame.Surface((gr*2+1, gr*2+1), pygame.SRCALPHA)
                pygame.draw.circle(s, (*col, ga), (gr, gr), gr)
                world_surface.blit(s, (sx_ - gr, sy_ - gr))

        elif shp == "glint":
            pw_ = int(particle.get("pw", sz_))
            ph_ = int(particle.get("ph", sz_))
            bpx = int(particle.get("px", sx_))
            bpy = int(particle.get("py", sy_))
            age  = 1.0 - max(0, particle["life"] / 0.22)
            x0 = bpx + int(age * pw_)
            s  = pygame.Surface((4, ph_), pygame.SRCALPHA)
            s.fill((*col, alph))
            world_surface.blit(s, (x0, bpy))

    for dot in pipe_dots:
        alph = max(0, min(255, int(dot["alpha"])))
        col  = dot["color"]
        s    = pygame.Surface((3, 3), pygame.SRCALPHA)
        s.fill((*col, alph))
        world_surface.blit(s, (int(dot["x"]) - 1, int(dot["y"]) - 1))

    if ui.debug_mode:
        draw_connection_zones(world_surface, grid)

    if ui.show_bottleneck_overlay:
        _bn_seen = set()
        for _bny in range(GRID_HEIGHT):
            for _bnx in range(GRID_WIDTH):
                _bnt = grid[_bny][_bnx]
                _bntt = _bnt["type"]
                if _bntt == 0:
                    continue
                _bno = get_any_origin(grid, _bnx, _bny)
                if _bno in _bn_seen:
                    continue
                _bn_seen.add(_bno)
                _bnox, _bnoy = _bno
                _bnres = machine_stall_reason(grid[_bnoy][_bnox], _bntt)
                if not _bnres or _bnres[0] in ("RUNNING", "SELLING"):
                    continue
                _bncol = _bnres[1]
                _bnw, _bnh = MACHINE_STATS.get(_bntt, {}).get("size", (1, 1))
                if grid[_bnoy][_bnox].get("rotation", 0) % 180 != 0:
                    _bnw, _bnh = _bnh, _bnw
                _bns = pygame.Surface((_bnw * TILE_SIZE, _bnh * TILE_SIZE), pygame.SRCALPHA)
                _bns.fill((*_bncol, 60))
                pygame.draw.rect(_bns, (*_bncol, 220), (0, 0, _bnw * TILE_SIZE, _bnh * TILE_SIZE), 2)
                world_surface.blit(_bns, (_bnox * TILE_SIZE, _bnoy * TILE_SIZE))

    if power_mode or power_source is not None:
        draw_power_connections(world_surface, grid)

    _draw_signal_wires(world_surface, grid)

    if power_mode and power_source:
        draw_power_range(world_surface, grid, power_source, research)

    if ui.selected_tile:
        tile_data, sel_gx, sel_gy = ui.selected_tile
        if "power_range" in MACHINE_STATS.get(tile_data["type"], {}):
            draw_power_range(world_surface, grid, (sel_gx, sel_gy), research)

    _vis_x = max(0, int(-camera_x / zoom))
    _vis_y = max(0, int(-camera_y / zoom))
    _vis_w = max(1, min(grid_pixel_width  - _vis_x,
                        int(math.ceil(SCREEN_WIDTH  / zoom)) + 2))
    _vis_h = max(1, min(grid_pixel_height - _vis_y,
                        int(math.ceil(SCREEN_HEIGHT / zoom)) + 2))
    _crop        = world_surface.subsurface((_vis_x, _vis_y, _vis_w, _vis_h))
    _tgt_w       = min(int(_vis_w * zoom), SCREEN_WIDTH  + 2)
    _tgt_h       = min(int(_vis_h * zoom), SCREEN_HEIGHT + 2)
    scaled_surface = pygame.transform.scale(_crop, (_tgt_w, _tgt_h))
    _dest_x      = max(0, int(camera_x + _vis_x * zoom))
    _dest_y      = max(0, int(camera_y + _vis_y * zoom))

    screen.set_clip(play_area_rect)
    screen.blit(scaled_surface, (_dest_x, _dest_y))

    if zoom < 1.0:
        _gcol = (55, 58, 55)
        _cell = TILE_SIZE * zoom
        for _gx in range(GRID_WIDTH + 1):
            _sx = int(camera_x + _gx * _cell)
            if 0 <= _sx <= play_area_width:
                pygame.draw.line(screen, _gcol,
                                 (_sx, max(0, int(camera_y))),
                                 (_sx, min(SCREEN_HEIGHT, int(camera_y + scaled_grid_height))), 1)
        for _gy in range(GRID_HEIGHT + 1):
            _sy = int(camera_y + _gy * _cell)
            if 0 <= _sy <= SCREEN_HEIGHT:
                pygame.draw.line(screen, _gcol, (max(0, int(camera_x)), _sy), (min(play_area_width, int(camera_x + scaled_grid_width)), _sy), 1)

    mx, my = pygame.mouse.get_pos()
    if mx < play_area_width and ui.get_active_tool() > 0 and not power_mode:
        world_x = (mx - camera_x) / zoom
        world_y = (my - camera_y) / zoom

        if 0 <= world_x < grid_pixel_width and 0 <= world_y < grid_pixel_height:
            gx = int(world_x // TILE_SIZE)
            gy = int(world_y // TILE_SIZE)

            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                tool_to_place = ui.get_active_tool()
                machine_stats = MACHINE_STATS.get(tool_to_place, {})
                building_size = machine_stats.get("size", (1, 1))
                if building_rotation % 180 != 0:
                    building_size = (building_size[1], building_size[0])
                current_tile_occupied = False
                for dy in range(building_size[1]):
                    for dx in range(building_size[0]):
                        check_x = gx + dx
                        check_y = gy + dy
                        if (check_x >= GRID_WIDTH or check_y >= GRID_HEIGHT
                                or grid[check_y][check_x]["type"] != 0):
                            current_tile_occupied = True
                            break

                hologram_color = (255, 80, 80, 140) if current_tile_occupied else (160, 210, 255, 60)

                screen_x = camera_x + (gx * TILE_SIZE * zoom)
                screen_y = camera_y + (gy * TILE_SIZE * zoom)
                hologram_width = int(TILE_SIZE * building_size[0] * zoom)
                hologram_height = int(TILE_SIZE * building_size[1] * zoom)

                hologram_rect    = pygame.Rect(screen_x, screen_y, hologram_width, hologram_height)
                hologram_surface = pygame.Surface((hologram_width, hologram_height), pygame.SRCALPHA)

                if tool_to_place in MACHINE_IMAGES:
                    img_scaled = _get_render_img(tool_to_place, hologram_width, hologram_height, building_rotation)
                    img_scaled = img_scaled.copy()
                    img_scaled.fill(hologram_color[:3] + (0,), special_flags=pygame.BLEND_RGBA_ADD)
                    img_scaled.set_alpha(hologram_color[3])
                    hologram_surface.blit(img_scaled, (0, 0))
                else:
                    pygame.draw.rect(hologram_surface, hologram_color, (0, 0, hologram_width, hologram_height))

                screen.blit(hologram_surface, (screen_x, screen_y))
                border_color = (255, 50, 50) if current_tile_occupied else (50, 255, 50)
                pygame.draw.rect(screen, border_color, hologram_rect, 2)

                from settings import MACHINE_DEFS as _MDEFS
                mdef_h = _MDEFS.get(tool_to_place, {})

                def _rot_dir(d, rot):
                    base = [UP, RIGHT, DOWN, LEFT]
                    if d not in base: return d
                    return base[(base.index(d) - (rot // 90)) % 4]

                def _rot_subtile(sx, sy, rot, w, h):
                    steps = (rot // 90) % 4
                    cx, cy, cw, ch = sx, sy, w, h
                    for _ in range(steps):
                        cx, cy = cy, cw - 1 - cx
                        cw, ch = ch, cw
                    return cx, cy

                orig_mw, orig_mh = machine_stats.get("size", (1, 1))
                mw_, mh_ = building_size
                input_ports_draw  = []
                output_ports_draw = []

                defs_in = mdef_h.get("input_ports") or []
                if defs_in:
                    seen_in = set()
                    for port in defs_in:
                        sx_, sy_ = port.get("subtile", (0, 0))
                        fd_ = tuple(port.get("from_dir", (0, 1)))
                        rsx, rsy = _rot_subtile(sx_, sy_, building_rotation, orig_mw, orig_mh)
                        rfd = _rot_dir(fd_, building_rotation)
                        k_ = (rsx, rsy, rfd)
                        if k_ not in seen_in:
                            seen_in.add(k_)
                            input_ports_draw.append((rsx, rsy, rfd))
                else:
                    stat_in = machine_stats.get("input_dirs") or (
                        [machine_stats["input_dir"]] if machine_stats.get("input_dir") else []
                    )
                    for d in stat_in:
                        rd_ = _rot_dir(tuple(d), building_rotation)
                        fd_ = (-rd_[0], -rd_[1])
                        if fd_ not in [x[2] for x in input_ports_draw]:
                            if rd_ == UP:     csx, csy = mw_ // 2, 0
                            elif rd_ == DOWN: csx, csy = mw_ // 2, mh_ - 1
                            elif rd_ == LEFT: csx, csy = 0, mh_ // 2
                            else:             csx, csy = mw_ - 1, mh_ // 2
                            input_ports_draw.append((csx, csy, fd_))

                defs_out = []
                if mdef_h.get("output_port"):  defs_out.append(mdef_h["output_port"])
                if mdef_h.get("output_port2"): defs_out.append(mdef_h["output_port2"])
                if defs_out:
                    seen_out = set()
                    for op_ in defs_out:
                        sx_, sy_ = op_.get("subtile", (0, 0))
                        pd_ = tuple(op_.get("push_dir", (0, 1)))
                        rsx, rsy = _rot_subtile(sx_, sy_, building_rotation, orig_mw, orig_mh)
                        rpd = _rot_dir(pd_, building_rotation)
                        k_ = (rsx, rsy, rpd)
                        if k_ not in seen_out:
                            seen_out.add(k_)
                            output_ports_draw.append((rsx, rsy, rpd))
                else:
                    if mdef_h.get("fluid_producer"):
                        sx_, sy_ = mdef_h.get("output_subtile", (0, 0))
                        pd_ = tuple(mdef_h.get("push_dir", (0, 1)))
                        rsx, rsy = _rot_subtile(sx_, sy_, building_rotation, orig_mw, orig_mh)
                        output_ports_draw.append((rsx, rsy, _rot_dir(pd_, building_rotation)))
                    else:
                        stat_out = machine_stats.get("output_dirs") or (
                            [machine_stats["output_dir"]] if machine_stats.get("output_dir") else []
                        )
                        for d in stat_out:
                            rd_ = _rot_dir(tuple(d), building_rotation)
                            if rd_ not in [x[2] for x in output_ports_draw]:
                                if rd_ == UP:     csx, csy = mw_ // 2, 0
                                elif rd_ == DOWN: csx, csy = mw_ // 2, mh_ - 1
                                elif rd_ == LEFT: csx, csy = 0, mh_ // 2
                                else:             csx, csy = mw_ - 1, mh_ // 2
                                output_ports_draw.append((csx, csy, rd_))

                hx, hy, hw, hh = hologram_rect
                tw_px = hw / max(1, mw_)
                th_px = hh / max(1, mh_)
                arrow_len = max(8, int(min(tw_px, th_px) * 0.45))

                def _draw_port_arrow(sx, sy, direction, color, kind):
                    dx_, dy_ = direction
                    tcx = hx + sx * tw_px + tw_px / 2
                    tcy = hy + sy * th_px + th_px / 2
                    if kind == "in":
                        ax_ = tcx - dx_ * (tw_px / 2)
                        ay_ = tcy - dy_ * (th_px / 2)
                    else:
                        ax_ = tcx + dx_ * (tw_px / 2)
                        ay_ = tcy + dy_ * (th_px / 2)
                    flow = (dx_, dy_)
                    tip_ = (ax_ + flow[0] * arrow_len, ay_ + flow[1] * arrow_len)
                    perp_ = (-flow[1], flow[0])
                    half_ = max(5, arrow_len // 2)
                    p1_ = (ax_ + perp_[0] * half_, ay_ + perp_[1] * half_)
                    p2_ = (ax_ - perp_[0] * half_, ay_ - perp_[1] * half_)
                    pygame.draw.polygon(screen, color, [tip_, p1_, p2_])
                    pygame.draw.polygon(screen, (0, 0, 0), [tip_, p1_, p2_], 2)

                for sx_, sy_, fd_ in input_ports_draw:
                    _draw_port_arrow(sx_, sy_, fd_, (90, 255, 110), "in")
                for sx_, sy_, pd_ in output_ports_draw:
                    _draw_port_arrow(sx_, sy_, pd_, (255, 110, 90), "out")

    if power_mode and power_source:
        mx, my = pygame.mouse.get_pos()
        if mx < play_area_width:
            _src_px, _src_py = _machine_pixel_center(grid, power_source[0], power_source[1])
            source_screen_x = camera_x + _src_px * zoom
            source_screen_y = camera_y + _src_py * zoom
            pygame.draw.line(screen, (255, 200, 50), (source_screen_x, source_screen_y), (mx, my), 3)
            sq = 10
            pygame.draw.rect(screen, (255, 220, 100), (int(source_screen_x) - sq // 2, int(source_screen_y) - sq // 2, sq, sq))
            pygame.draw.rect(screen, (255, 255, 180), (int(source_screen_x) - sq // 2, int(source_screen_y) - sq // 2, sq, sq), 1)


    screen.set_clip(None)

    boundary_rect = pygame.Rect(camera_x, camera_y, int(scaled_grid_width), int(scaled_grid_height))
    pygame.draw.rect(screen, (100, 100, 100), boundary_rect, 2)

    ui.draw(screen, money, contracts,
            building_rotation=building_rotation,
            show_zones=ui.debug_mode,
            power_mode=power_mode,
            debug_mode=ui.debug_mode,
            research=research,
            grid=grid,
            pollution=pollution,
            wind_speed=wind_speed)

    if ui.md_drag_start is not None and ui.md_drag_end is not None:
        gx0, gy0 = ui.md_drag_start
        gx1, gy1 = ui.md_drag_end
        x_lo, x_hi = min(gx0, gx1), max(gx0, gx1)
        y_lo, y_hi = min(gy0, gy1), max(gy0, gy1)
        sx = camera_x + x_lo * TILE_SIZE * zoom
        sy = camera_y + y_lo * TILE_SIZE * zoom
        sw = (x_hi - x_lo + 1) * TILE_SIZE * zoom
        sh = (y_hi - y_lo + 1) * TILE_SIZE * zoom
        rect_surf = pygame.Surface((int(sw), int(sh)), pygame.SRCALPHA)
        rect_surf.fill((235, 70, 70, 80))
        screen.blit(rect_surf, (int(sx), int(sy)))
        pygame.draw.rect(screen, (255, 100, 100), (int(sx), int(sy), int(sw), int(sh)), 2)
        count = 0
        origins_seen = set()
        for yy in range(y_lo, y_hi + 1):
            for xx in range(x_lo, x_hi + 1):
                t = grid[yy][xx]
                if t["type"] != 0:
                    raw = t.get("origin", (xx, yy))
                    o = tuple(raw) if isinstance(raw, list) else raw
                    if o not in origins_seen:
                        origins_seen.add(o)
                        count += 1
        mx, my = pygame.mouse.get_pos()
        txt = ui.font.render(f"{count} machines in selection", True, (255, 200, 200))
        tbg = pygame.Surface((txt.get_width() + 12, txt.get_height() + 6), pygame.SRCALPHA)
        tbg.fill((20, 10, 10, 210))
        screen.blit(tbg, (mx + 14, my + 14))
        screen.blit(txt, (mx + 20, my + 17))

    if ui.bp_select_mode and ui.bp_drag_start is not None and ui.bp_drag_end is not None:
        gx0, gy0 = ui.bp_drag_start
        gx1, gy1 = ui.bp_drag_end
        x_lo, x_hi = min(gx0, gx1), max(gx0, gx1)
        y_lo, y_hi = min(gy0, gy1), max(gy0, gy1)
        sx = camera_x + x_lo * TILE_SIZE * zoom
        sy = camera_y + y_lo * TILE_SIZE * zoom
        sw = (x_hi - x_lo + 1) * TILE_SIZE * zoom
        sh = (y_hi - y_lo + 1) * TILE_SIZE * zoom
        bp_surf = pygame.Surface((int(sw), int(sh)), pygame.SRCALPHA)
        bp_surf.fill((90, 170, 255, 70))
        screen.blit(bp_surf, (int(sx), int(sy)))
        pygame.draw.rect(screen, (120, 200, 255), (int(sx), int(sy), int(sw), int(sh)), 2)
    elif ui.bp_select_mode:
        mx_b, my_b = pygame.mouse.get_pos()
        bp_hint = ui.font.render("BLUEPRINT: drag to select  [ESC/G cancel]", True, (150, 210, 255))
        screen.blit(bp_hint, (mx_b + 14, my_b + 14))

    if ui.bp_paste_mode and ui.blueprint:
        mx_b, my_b = pygame.mouse.get_pos()
        if mx_b < play_area_width:
            world_x = (mx_b - camera_x) / zoom
            world_y = (my_b - camera_y) / zoom
            if 0 <= world_x < grid_pixel_width and 0 <= world_y < grid_pixel_height:
                agx = int(world_x // TILE_SIZE)
                agy = int(world_y // TILE_SIZE)
                for m in ui.blueprint["machines"]:
                    stats_b = MACHINE_STATS.get(m["type"], {})
                    w_b, h_b = stats_b.get("size", (1, 1))
                    if m["rotation"] % 180 != 0:
                        w_b, h_b = h_b, w_b
                    bx = agx + m["dx"]
                    by = agy + m["dy"]
                    fits = all(0 <= bx + dx_ < GRID_WIDTH and 0 <= by + dy_ < GRID_HEIGHT
                               and grid[by + dy_][bx + dx_]["type"] == 0
                               for dy_ in range(h_b) for dx_ in range(w_b))
                    col_b = (120, 200, 255) if fits else (255, 90, 90)
                    sxp = int(camera_x + bx * TILE_SIZE * zoom)
                    syp = int(camera_y + by * TILE_SIZE * zoom)
                    swp = max(1, int(w_b * TILE_SIZE * zoom))
                    shp = max(1, int(h_b * TILE_SIZE * zoom))
                    bs = pygame.Surface((swp, shp), pygame.SRCALPHA)
                    bs.fill((*col_b, 80))
                    screen.blit(bs, (sxp, syp))
                    pygame.draw.rect(screen, col_b, (sxp, syp, swp, shp), 1)
                cost_txt = ui.font.render(
                    f"Paste {len(ui.blueprint['machines'])} machines: "
                    f"${_blueprint_cost(ui.blueprint):,.0f}   [ESC/G/R-click cancel]",
                    True, (150, 210, 255))
                screen.blit(cost_txt, (mx_b + 14, my_b + 14))

    if ui.md_pending is not None:
        _, _, _, _, cnt, _ = ui.md_pending
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 170))
        screen.blit(dim, (0, 0))
        pw, ph = 380, 160
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (22, 14, 18, 245), (0, 0, pw, ph), border_radius=14)
        pygame.draw.rect(panel, (235, 95, 95, 255), (0, 0, pw, ph), 2, border_radius=14)
        screen.blit(panel, (px, py))
        title = ui.title_font.render("DELETE CONFIRM", True, (255, 180, 180))
        screen.blit(title, title.get_rect(center=(px + pw // 2, py + 28)))
        body = ui.font.render(f"Delete {cnt} machine{'s' if cnt != 1 else ''}?", True, (240, 230, 230))
        screen.blit(body, body.get_rect(center=(px + pw // 2, py + 70)))
        hint = ui.tiny_font.render("[Y] Confirm       [N] or [ESC] Cancel", True, (200, 150, 150))
        screen.blit(hint, hint.get_rect(center=(px + pw // 2, py + ph - 28)))

    _tutorial.draw(screen)


    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()