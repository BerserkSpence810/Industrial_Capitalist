# grid maths. no game state in here, everything takes grid/tile as an arg
# rotation is degrees, anticlockwise on screen
import pygame

from settings import (TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, MACHINE_STATS,
                      UP, DOWN, LEFT, RIGHT)


# -- origins & footprints --------

def get_machine_origin(grid, x, y):
    tile = grid[y][x]
    o = tile.get("origin")
    if o is None:
        return (x, y)
    return tuple(o) if isinstance(o, list) else o

def get_any_origin(grid, gx, gy):
    ttype = grid[gy][gx].get("type", 0)
    if MACHINE_STATS.get(ttype, {}).get("size", (1, 1)) != (1, 1):
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


# -- rotation --------

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

def rotate_subtile(sx, sy, tw, th, rotation):
    """Rotate a local subtile coordinate within a twxth footprint.
    Returns (x, y, new_w, new_h) in the rotated footprint."""
    steps = (rotation // 90) % 4
    cx, cy, cw, ch = sx, sy, tw, th
    for _ in range(steps):
        cx, cy = cy, cw - 1 - cx
        cw, ch = ch, cw
    return cx, cy, cw, ch

def rotate_port(ox, oy, sx, sy, tw, th, direction, rotation):
    cx, cy, cw, ch = rotate_subtile(sx, sy, tw, th, rotation)
    rd = rotate_direction(direction, rotation)
    return ox + cx, oy + cy, rd, cw, ch

def unrotate_subtile(wx, wy, push_dx, push_dy, tw, th, rot):
    """Map a world-space footprint offset + push direction back into the
    machine's unrotated local frame.

    (wx, wy) is the offset from the machine origin in the rotated footprint;
    (tw, th) is the UNROTATED machine size. Returns (lx, ly, (lpx, lpy)) so
    receive logic can compare against the port layout as defined in
    MACHINE_DEFS regardless of the placed rotation."""
    steps = (rot // 90) % 4
    inv = (4 - steps) % 4
    # start in the rotated frame's dimensions, undo one 90deg step at a time
    cw, ch = (th, tw) if steps % 2 == 1 else (tw, th)
    cx, cy = wx, wy
    for _ in range(inv):
        cx, cy = cy, cw - 1 - cx
        cw, ch = ch, cw
    lpush = rotate_direction((push_dx, push_dy), (360 - rot) % 360)
    return cx, cy, lpush

def port_pixel(ox, oy, sx, sy, tw, th, rot):
    cx, cy, _, _ = rotate_subtile(sx, sy, tw, th, rot)
    px = (ox + cx) * TILE_SIZE + TILE_SIZE // 2
    py = (oy + cy) * TILE_SIZE + TILE_SIZE // 2
    return px, py


# -- stat-driven IO directions (pipes, drills, simple machines) --------------

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


# -- the one true port list --------

def machine_port_tiles(ttype, rotation, machine_defs, machine_stats):
    """(dx, dy, dir) off the origin, rotated. dir = way the item moves"""
    # the Z overlay and the placement ghost each used to work this out themselves
    # and got different answers, half a tile apart on even width machines.
    # both were wrong anyway - a quarry pushes out all 4 bottom tiles, not 1.
    # everything draws from this now, dont write a second copy
    mdef = machine_defs.get(ttype) or {}
    stats = machine_stats.get(ttype, {})
    tw, th = stats.get("size", (1, 1))
    rw, rh = (th, tw) if (rotation // 90) % 2 else (tw, th)
    inputs, outputs = [], []

    def face(direction, w, h):
        """Every tile along the face `direction` points at."""
        dx, dy = direction
        if dy == 1:
            return [(i, h - 1) for i in range(w)]
        if dy == -1:
            return [(i, 0) for i in range(w)]
        if dx == 1:
            return [(w - 1, i) for i in range(h)]
        if dx == -1:
            return [(0, i) for i in range(h)]
        return [(0, 0)]

    ports = mdef.get("input_ports") or []
    if ports:
        for p in ports:
            sx, sy = p["subtile"]
            fd = tuple(p["from_dir"])
            rx, ry, rfd, _, _ = rotate_port(0, 0, sx, sy, tw, th, fd, rotation)
            if (rx, ry, rfd) not in inputs:
                inputs.append((rx, ry, rfd))
    elif ttype == 12:
        # a Coal Generator accepts coal on any of its tiles, from above
        rd = rotate_direction((0, -1), rotation)
        travel = (-rd[0], -rd[1])
        for tile_xy in face(rd, rw, rh):
            inputs.append((tile_xy[0], tile_xy[1], travel))
    else:
        dirs = stats.get("input_dirs") or (
            [stats["input_dir"]] if stats.get("input_dir") else [])
        for d in dirs:
            rd = rotate_direction(tuple(d), rotation)
            travel = (-rd[0], -rd[1])
            for tile_xy in face(rd, rw, rh):
                if (tile_xy[0], tile_xy[1], travel) not in inputs:
                    inputs.append((tile_xy[0], tile_xy[1], travel))

    out_defs = [mdef[k] for k in ("output_port", "output_port2") if mdef.get(k)]
    if out_defs:
        for op in out_defs:
            sx, sy = op["subtile"]
            pd = tuple(op["push_dir"])
            rx, ry, rpd, _, _ = rotate_port(0, 0, sx, sy, tw, th, pd, rotation)
            if (rx, ry, rpd) not in outputs:
                outputs.append((rx, ry, rpd))
    elif mdef.get("output_subtile") is not None:
        sx, sy = tuple(mdef["output_subtile"])
        pd = tuple(mdef.get("push_dir", (1, 0)))
        rx, ry, rpd, _, _ = rotate_port(0, 0, sx, sy, tw, th, pd, rotation)
        outputs.append((rx, ry, rpd))
    else:
        dirs = stats.get("output_dirs") or (
            [stats["output_dir"]] if stats.get("output_dir") else [])
        for d in dirs:
            rd = rotate_direction(tuple(d), rotation)
            for tile_xy in face(rd, rw, rh):
                if (tile_xy[0], tile_xy[1], rd) not in outputs:
                    outputs.append((tile_xy[0], tile_xy[1], rd))
    return inputs, outputs


# -- connection zones (visual + can_connect overlap tests) -------------------

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


# -- power --------

def power_link_distance(grid, source_cx, source_cy, target_gx, target_gy):
    """Distance in grid tiles from the source's centre tile to the nearest
    tile of the target machine's footprint.

    Uses Chebyshev distance (max of dx/dy) so it matches the square range
    overlay drawn by draw_power_range - anything visually inside the square
    is connectable, including diagonals and the edges of large machines."""
    tile = grid[target_gy][target_gx]
    stats = MACHINE_STATS.get(tile.get("type", 0), {})
    tw, th = stats.get("size", (1, 1))
    raw = tile.get("origin", (target_gx, target_gy))
    ox, oy = tuple(raw) if isinstance(raw, list) else raw
    if grid[oy][ox].get("rotation", 0) % 180 != 0:
        tw, th = th, tw
    nearest_x = min(max(source_cx, ox), ox + tw - 1)
    nearest_y = min(max(source_cy, oy), oy + th - 1)
    return max(abs(nearest_x - source_cx), abs(nearest_y - source_cy))
