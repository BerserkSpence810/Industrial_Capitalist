from ui import *
from settings import *

import pygame
import json
import time
import os

def load_grid():
    if os.path.exists(GFILE):
        try:
            with open(GFILE, "r") as f:
                content = f.read()
                if content.strip():
                    return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            print("Warning: world.json is corrupted. Creating new grid.")
    return [[{"type": 0, "stored": None, "amount": 0, "timer": 0, "rotation": 0} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def save_grid():
    os.makedirs("data", exist_ok=True)
    with open(GFILE, "w") as f:
        json.dump(grid, f)

def load_money():
    if os.path.exists(MFILE):
        try:
            with open(MFILE, "r") as f:
                data = json.load(f)
                return data.get("money", 0)
        except (json.JSONDecodeError, ValueError):
            print("Money.json is corrupted. Starting with $0.")
    return 0

def save_money(money):
    os.makedirs("data", exist_ok=True)
    with open("data/money.json", "w") as f:
        json.dump({"money": money}, f)

def rotate_direction(direction, rotation):
    """Rotate a direction counter-clockwise by rotation degrees"""
    if direction is None:
        return None
    
    dirs = [UP, RIGHT, DOWN, LEFT]
    if direction not in dirs:
        return direction
    
    idx = dirs.index(direction)
    steps = (rotation // 90) % 4
    new_idx = (idx - steps) % 4
    return dirs[new_idx]

def get_output_direction(tile):
    """Get the actual output direction based on rotation"""
    machine_stats = MACHINE_STATS.get(tile["type"], {})
    
    # Check for multiple output directions (splitter)
    if "output_dirs" in machine_stats:
        base_dirs = machine_stats["output_dirs"]
        rotation = tile.get("rotation", 0)
        return [rotate_direction(d, rotation) for d in base_dirs]
    
    # Single output direction
    base_dir = machine_stats.get("output_dir", None)
    if base_dir is None:
        return None
    rotation = tile.get("rotation", 0)
    return rotate_direction(base_dir, rotation)

def get_input_direction(tile):
    """Get the actual input direction based on rotation"""
    machine_stats = MACHINE_STATS.get(tile["type"], {})
    
    # Check for multiple input directions (merger)
    if "input_dirs" in machine_stats:
        base_dirs = machine_stats["input_dirs"]
        rotation = tile.get("rotation", 0)
        return [rotate_direction(d, rotation) for d in base_dirs]
    
    # Single input direction
    base_dir = machine_stats.get("input_dir", None)
    if base_dir is None:
        return None
    rotation = tile.get("rotation", 0)
    return rotate_direction(base_dir, rotation)

def get_neighbor_in_direction(x, y, direction):
    """Get neighbor position in a direction"""
    dx, dy = direction
    nx, ny = x + dx, y + dy
    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
        return nx, ny
    return None

def get_zone_rect(x, y, direction, is_input=False):
    """Get the rectangle for an input or output zone"""
    ZONE_WIDTH = 12
    ZONE_EXTEND = 4
    
    base_x = x * TILE_SIZE
    base_y = y * TILE_SIZE
    center_x = base_x + TILE_SIZE // 2
    center_y = base_y + TILE_SIZE // 2
    
    dx, dy = direction
    
    if dx == 0 and dy == -1:  # UP
        return pygame.Rect(center_x - ZONE_WIDTH//2, base_y - ZONE_EXTEND, ZONE_WIDTH, ZONE_EXTEND + 3)
    elif dx == 0 and dy == 1:  # DOWN
        return pygame.Rect(center_x - ZONE_WIDTH//2, base_y + TILE_SIZE - 3, ZONE_WIDTH, ZONE_EXTEND + 3)
    elif dx == -1 and dy == 0:  # LEFT
        return pygame.Rect(base_x - ZONE_EXTEND, center_y - ZONE_WIDTH//2, ZONE_EXTEND + 3, ZONE_WIDTH)
    elif dx == 1 and dy == 0:  # RIGHT
        return pygame.Rect(base_x + TILE_SIZE - 3, center_y - ZONE_WIDTH//2, ZONE_EXTEND + 3, ZONE_WIDTH)
    
    return None

def can_connect(source_x, source_y, source_tile, target_x, target_y, target_tile):
    """Check if source output zone overlaps with target input zone - ACTUAL COLLISION CHECK"""
    # Get output direction(s) from source
    source_output_dir = get_output_direction(source_tile)
    if source_output_dir is None:
        print(f"  ✗ Source ({source_x},{source_y}) has no output direction")
        return False
    
    # Get input direction(s) from target
    target_input_dir = get_input_direction(target_tile)
    
    # Target MUST have an input direction
    if target_input_dir is None:
        print(f"  ✗ Target ({target_x},{target_y}) type={target_tile['type']} has no input direction")
        return False
    
    # Handle multiple output directions (splitter)
    if isinstance(source_output_dir, list):
        # Check each output direction
        for output_dir in source_output_dir:
            source_output_rect = get_zone_rect(source_x, source_y, output_dir, is_input=False)
            if not source_output_rect:
                continue
            
            # Check against target's input(s)
            if isinstance(target_input_dir, list):
                for input_dir in target_input_dir:
                    target_input_rect = get_zone_rect(target_x, target_y, input_dir, is_input=True)
                    if target_input_rect and source_output_rect.colliderect(target_input_rect):
                        print(f"  ✓ Source ({source_x},{source_y}) out={output_dir} -> Target ({target_x},{target_y}) in={input_dir} | OVERLAP=True")
                        return True
            else:
                target_input_rect = get_zone_rect(target_x, target_y, target_input_dir, is_input=True)
                if target_input_rect and source_output_rect.colliderect(target_input_rect):
                    print(f"  ✓ Source ({source_x},{source_y}) out={output_dir} -> Target ({target_x},{target_y}) in={target_input_dir} | OVERLAP=True")
                    return True
        print(f"  ✗ Source outputs don't match target inputs")
        return False
    
    # Single output direction
    source_output_rect = get_zone_rect(source_x, source_y, source_output_dir, is_input=False)
    if source_output_rect is None:
        print(f"  ✗ Could not create output zone rect")
        return False
    
    # Handle multiple input directions (merger)
    if isinstance(target_input_dir, list):
        for input_dir in target_input_dir:
            target_input_rect = get_zone_rect(target_x, target_y, input_dir, is_input=True)
            if target_input_rect and source_output_rect.colliderect(target_input_rect):
                print(f"  ✓ Source ({source_x},{source_y}) out={source_output_dir} -> Target ({target_x},{target_y}) in={input_dir} | OVERLAP=True")
                return True
        print(f"  ✗ Source output doesn't match any of target's inputs")
        return False
    
    # Single input direction
    target_input_rect = get_zone_rect(target_x, target_y, target_input_dir, is_input=True)
    if target_input_rect is None:
        print(f"  ✗ Could not create input zone rect")
        return False
    
    # THE ACTUAL COLLISION CHECK
    zones_overlap = source_output_rect.colliderect(target_input_rect)
    
    print(f"  {'✓' if zones_overlap else '✗'} Source ({source_x},{source_y}) out={source_output_dir} -> Target ({target_x},{target_y}) in={target_input_dir} | OVERLAP={zones_overlap}")
    
    return zones_overlap

def update_world(grid, dt, money):
    # Production phase - drills create resources
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]

            if tile["type"] == 2:  # Coal drill
                tile["timer"] += dt
                if tile["timer"] >= 2.0:
                    if tile["stored"] is None:
                        tile["stored"] = "coal"
                        tile["amount"] = 1
                    elif tile["stored"] == "coal":
                        tile["amount"] += 1
                    tile["timer"] = 0

    # Transfer phase - NEW LOGIC USING ZONE OVERLAP
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]

            # Coal drill transfers - CHECK ALL 4 NEIGHBORS
            if tile["type"] == 2:
                if 'output_timer' not in tile:
                    tile['output_timer'] = 0
                
                tile['output_timer'] += dt
                
                if tile['output_timer'] >= 0.5 and tile["amount"] > 0:
                    # Get the drill's output direction
                    output_dir = get_output_direction(tile)
                    if output_dir:
                        # Check the neighbor in that direction
                        nx = x + output_dir[0]
                        ny = y + output_dir[1]
                        
                        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                            neighbor = grid[ny][nx]
                            
                            # ONLY TRANSFER IF ZONES ACTUALLY OVERLAP
                            if can_connect(x, y, tile, nx, ny, neighbor):
                                if neighbor["type"] in [1, 4, 5, 6, 7]:  # Any pipe type
                                    pipe_capacity = MACHINE_STATS[neighbor["type"]]["capacity"]
                                    space_available = pipe_capacity - neighbor["amount"]
                                    
                                    if space_available > 0:
                                        # Check if neighbor can accept this resource type
                                        if neighbor["stored"] is None or neighbor["stored"] == tile["stored"]:
                                            neighbor["stored"] = tile["stored"]
                                            neighbor["amount"] += 1
                                            tile["amount"] -= 1
                                            
                                            if tile["amount"] == 0:
                                                tile["stored"] = None
                                            
                                            print(f"✓ Coal drill ({x},{y}) -> Pipe ({nx},{ny})")
                                elif neighbor["type"] == 3:  # Van depot
                                    depot_capacity = MACHINE_STATS[3]["capacity"]
                                    space_available = depot_capacity - neighbor["amount"]
                                    
                                    if space_available > 0:
                                        if neighbor["stored"] is None or neighbor["stored"] == tile["stored"]:
                                            neighbor["stored"] = tile["stored"]
                                            neighbor["amount"] += 1
                                            tile["amount"] -= 1
                                            
                                            if tile["amount"] == 0:
                                                tile["stored"] = None
                                            
                                            print(f"✓ Coal drill ({x},{y}) -> Depot ({nx},{ny})")
                    
                    tile['output_timer'] = 0

            # Pipe/Merger/Splitter transfers
            elif tile["type"] in [1, 4, 5, 6, 7]:  # Regular pipe, L-pipes, merger, or splitter
                tile["timer"] += dt
                if tile["timer"] >= 0.5 and tile["amount"] > 0:
                    # Get the output direction(s)
                    output_dirs = get_output_direction(tile)
                    if output_dirs:
                        # Handle multiple outputs (splitter) - round-robin distribution
                        if isinstance(output_dirs, list):
                            if 'output_index' not in tile:
                                tile['output_index'] = 0
                            
                            # Try each output starting from the last used one
                            attempts = 0
                            while attempts < len(output_dirs):
                                output_dir = output_dirs[tile['output_index']]
                                nx = x + output_dir[0]
                                ny = y + output_dir[1]
                                
                                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                                    neighbor = grid[ny][nx]
                                    
                                    if can_connect(x, y, tile, nx, ny, neighbor):
                                        if neighbor["type"] in [1, 4, 5, 6, 7]:  # Another pipe/merger/splitter
                                            pipe_capacity = MACHINE_STATS[neighbor["type"]]["capacity"]
                                            space_available = pipe_capacity - neighbor["amount"]
                                            
                                            if space_available > 0 and (neighbor["stored"] is None or neighbor["stored"] == tile["stored"]):
                                                neighbor["stored"] = tile["stored"]
                                                neighbor["amount"] += 1
                                                tile["amount"] -= 1
                                                
                                                if tile["amount"] == 0:
                                                    tile["stored"] = None
                                                
                                                # Move to next output for next item
                                                tile['output_index'] = (tile['output_index'] + 1) % len(output_dirs)
                                                print(f"✓ Splitter ({x},{y}) -> Pipe ({nx},{ny}) [output {tile['output_index']}]")
                                                break
                                        
                                        elif neighbor["type"] == 3:  # Van Depot
                                            depot_capacity = MACHINE_STATS[3]["capacity"]
                                            space_available = depot_capacity - neighbor["amount"]
                                            
                                            if space_available > 0 and (neighbor["stored"] is None or neighbor["stored"] == tile["stored"]):
                                                neighbor["stored"] = tile["stored"]
                                                neighbor["amount"] += 1
                                                tile["amount"] -= 1
                                                
                                                if tile["amount"] == 0:
                                                    tile["stored"] = None
                                                
                                                tile['output_index'] = (tile['output_index'] + 1) % len(output_dirs)
                                                print(f"✓ Splitter ({x},{y}) -> Depot ({nx},{ny})")
                                                break
                                
                                # Try next output
                                tile['output_index'] = (tile['output_index'] + 1) % len(output_dirs)
                                attempts += 1
                        
                        else:
                            # Single output direction (normal pipes)
                            nx = x + output_dirs[0]
                            ny = y + output_dirs[1]
                            
                            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                                neighbor = grid[ny][nx]
                                
                                if can_connect(x, y, tile, nx, ny, neighbor):
                                    if neighbor["type"] in [1, 4, 5, 6, 7]:  # Another pipe/merger/splitter
                                        pipe_capacity = MACHINE_STATS[neighbor["type"]]["capacity"]
                                        space_available = pipe_capacity - neighbor["amount"]
                                        
                                        if space_available > 0 and (neighbor["stored"] is None or neighbor["stored"] == tile["stored"]):
                                            neighbor["stored"] = tile["stored"]
                                            neighbor["amount"] += 1
                                            tile["amount"] -= 1
                                            
                                            if tile["amount"] == 0:
                                                tile["stored"] = None
                                            
                                            print(f"✓ Pipe ({x},{y}) -> Pipe ({nx},{ny})")
                                    
                                    elif neighbor["type"] == 3:  # Van Depot
                                        depot_capacity = MACHINE_STATS[3]["capacity"]
                                        space_available = depot_capacity - neighbor["amount"]
                                        
                                        if space_available > 0 and (neighbor["stored"] is None or neighbor["stored"] == tile["stored"]):
                                            neighbor["stored"] = tile["stored"]
                                            neighbor["amount"] += 1
                                            tile["amount"] -= 1
                                            
                                            if tile["amount"] == 0:
                                                tile["stored"] = None
                                            
                                            print(f"✓ Pipe ({x},{y}) -> Depot ({nx},{ny})")
                    
                    tile["timer"] = 0
    
    # Selling phase
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            
            if tile["type"] == 3:
                if 'total_sold' not in tile:
                    tile['total_sold'] = 0
                depot_capacity = MACHINE_STATS[3]["capacity"]
                if tile["amount"] >= depot_capacity and tile["stored"] is not None:
                    item_type = tile["stored"]
                    item_value = ITEM_VALUES.get(item_type, 0)
                    sale_amount = tile["amount"] * item_value
                    money += sale_amount
                    sold_amount = tile["amount"]
                    tile['total_sold'] += sold_amount
                    tile["stored"] = None
                    tile["amount"] = 0
                    print(f"Van Depot at ({x}, {y}) shipped {sold_amount} {item_type}! Earned ${sale_amount}. Total sold: {tile['total_sold']}")
    return money

def draw_connection_zones(world_surface, grid):
    """Draw input/output zones for debugging"""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            if tile["type"] == 0:
                continue
            
            # Draw output zone(s) (red)
            output_dir = get_output_direction(tile)
            if output_dir:
                # Handle multiple output directions (splitter)
                if isinstance(output_dir, list):
                    for out_dir in output_dir:
                        rect = get_zone_rect(x, y, out_dir, is_input=False)
                        if rect:
                            pygame.draw.rect(world_surface, (255, 80, 80), rect)
                            pygame.draw.rect(world_surface, (255, 150, 150), rect, 1)
                else:
                    rect = get_zone_rect(x, y, output_dir, is_input=False)
                    if rect:
                        pygame.draw.rect(world_surface, (255, 80, 80), rect)
                        pygame.draw.rect(world_surface, (255, 150, 150), rect, 1)
            
            # Draw input zone(s) (green)
            input_dir = get_input_direction(tile)
            if input_dir:
                # Handle multiple input directions (merger)
                if isinstance(input_dir, list):
                    for in_dir in input_dir:
                        rect = get_zone_rect(x, y, in_dir, is_input=True)
                        if rect:
                            pygame.draw.rect(world_surface, (80, 255, 80), rect)
                            pygame.draw.rect(world_surface, (150, 255, 150), rect, 1)
                else:
                    rect = get_zone_rect(x, y, input_dir, is_input=True)
                    if rect:
                        pygame.draw.rect(world_surface, (80, 255, 80), rect)
                        pygame.draw.rect(world_surface, (150, 255, 150), rect, 1)

pygame.init()

#Image loading
try:
    MACHINE_IMAGES[2] = pygame.transform.scale(
        pygame.image.load("assets/Drills/Coal-Drill.png").convert_alpha(), 
        (TILE_SIZE, TILE_SIZE)
    )
    MACHINE_IMAGES[1] = pygame.transform.scale(
        pygame.image.load("assets/Pipes/Pipe.png").convert_alpha(), 
        (TILE_SIZE, TILE_SIZE)
    )
    MACHINE_IMAGES[3] = pygame.transform.scale(
        pygame.image.load("assets/Depot/Van-Depot.png").convert_alpha(), 
        (TILE_SIZE, TILE_SIZE)
    )
    MACHINE_IMAGES[4] = pygame.transform.scale(
        pygame.image.load("assets/Pipes/L-Pipe-R.png").convert_alpha(), 
        (TILE_SIZE, TILE_SIZE)
    )
    MACHINE_IMAGES[5] = pygame.transform.scale(
        pygame.image.load("assets/Pipes/L-Pipe-L.png").convert_alpha(), 
        (TILE_SIZE, TILE_SIZE)
    )
    MACHINE_IMAGES[6] = pygame.transform.scale(
        pygame.image.load("assets/Pipes/Merger.png").convert_alpha(), 
        (TILE_SIZE, TILE_SIZE)
    )
    MACHINE_IMAGES[7] = pygame.transform.scale(
        pygame.image.load("assets/Pipes/Splitter.png").convert_alpha(), 
        (TILE_SIZE, TILE_SIZE)
    )
except pygame.error as e:
    print(f"Warning: Could not load images: {e}")
    print("Using colored rectangles instead.")

grid = load_grid()
money = load_money()
run = True
ui = DrawGrid()

#Camera
play_area_width = SCREEN_WIDTH - SIDEBAR_WIDTH
grid_pixel_width = GRID_WIDTH * TILE_SIZE
grid_pixel_height = GRID_HEIGHT * TILE_SIZE
camera_x = (play_area_width - grid_pixel_width) / 2
camera_y = (SCREEN_HEIGHT - grid_pixel_height) / 2
zoom = 1.0
min_zoom = 0.5
max_zoom = 4.0

#Camera Move
camera_velocity_x = 0
camera_velocity_y = 0
camera_speed = 300  #pps

# Rotation for building
building_rotation = 0

# Debug mode for showing connection zones
show_zones = False

while run:
    screen.fill(BGC)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_grid()
            save_money(money)
            time.sleep(0.5)
            run = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                building_rotation = (building_rotation + 90) % 360
            elif event.key == pygame.K_z:
                show_zones = not show_zones
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                save_grid()
                save_money(money)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            if event.button == 1:
                if mx < play_area_width:
                    world_x = (mx - camera_x) / zoom
                    world_y = (my - camera_y) / zoom
                    
                    if 0 <= world_x < grid_pixel_width and 0 <= world_y < grid_pixel_height:
                        gx = int(world_x // TILE_SIZE)
                        gy = int(world_y // TILE_SIZE)
                        
                        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                            shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT
                            
                            tool_to_place = ui.get_active_tool()
                            current_tile_type = grid[gy][gx]["type"]
                            
                            # Inspect mode (no tool selected)
                            if tool_to_place == -1:
                                ui.handle_tile_click(grid, gx, gy)
                            
                            # Delete tool
                            elif tool_to_place == 0:
                                if current_tile_type != 0:
                                    machine_cost = MACHINE_STATS.get(current_tile_type, {}).get("cost", 0)
                                    sell_value = machine_cost * 0.8
                                    money += sell_value
                                    ui.show_transaction_message(f"+${sell_value:.2f} (Sold)", (100, 255, 100))
                                    
                                    grid[gy][gx]["type"] = 0
                                    grid[gy][gx]["stored"] = None
                                    grid[gy][gx]["amount"] = 0
                                    grid[gy][gx]["timer"] = 0
                                    grid[gy][gx]["rotation"] = 0
                                    if 'output_timer' in grid[gy][gx]:
                                        del grid[gy][gx]['output_timer']
                                    if 'total_sold' in grid[gy][gx]:
                                        del grid[gy][gx]['total_sold']
                                    
                                    if ui.selected_tile and ui.selected_tile[1] == gx and ui.selected_tile[2] == gy:
                                        ui.selected_tile = None
                                    
                                    if not shift_held:
                                        ui.active_tool = -1
                            
                            # Place building
                            else:
                                # Can only place on empty tiles
                                if current_tile_type == 0:
                                    machine_cost = MACHINE_STATS.get(tool_to_place, {}).get("cost", 0)
                                    
                                    if money >= machine_cost:
                                        money -= machine_cost
                                        ui.show_transaction_message(f"-${machine_cost:.2f}", (255, 100, 100))
                                        
                                        grid[gy][gx]["type"] = tool_to_place
                                        grid[gy][gx]["stored"] = None
                                        grid[gy][gx]["amount"] = 0
                                        grid[gy][gx]["timer"] = 0
                                        grid[gy][gx]["rotation"] = building_rotation
                                        if 'output_timer' in grid[gy][gx]:
                                            del grid[gy][gx]['output_timer']
                                        if 'total_sold' in grid[gy][gx]:
                                            del grid[gy][gx]['total_sold']
                                        if tool_to_place == 3:
                                            grid[gy][gx]['total_sold'] = 0
                                        
                                        if ui.selected_tile and ui.selected_tile[1] == gx and ui.selected_tile[2] == gy:
                                            ui.handle_tile_click(grid, gx, gy)
                                        
                                        if not shift_held:
                                            ui.active_tool = -1
                                    else:
                                        ui.show_transaction_message("Not enough money!", (255, 50, 50))
                                else:
                                    # Can't place on occupied tile
                                    ui.show_transaction_message("Remove existing building first!", (255, 150, 50))
                else:
                    ui.handle_click((mx, my))
            
            elif event.button == 3: #Inspect
                if mx < play_area_width:
                    world_x = (mx - camera_x) / zoom
                    world_y = (my - camera_y) / zoom
                    
                    if 0 <= world_x < grid_pixel_width and 0 <= world_y < grid_pixel_height:
                        gx = int(world_x // TILE_SIZE)
                        gy = int(world_y // TILE_SIZE)
                        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                            ui.handle_tile_click(grid, gx, gy)
            
            elif event.button == 4: #Scroll up
                if mx >= SCREEN_WIDTH - SIDEBAR_WIDTH:
                    # Scroll in sidebar
                    ui.handle_scroll(1)
                elif mx < play_area_width:
                    # Zoom in
                    old_zoom = zoom
                    zoom = min(zoom + 0.1, max_zoom)
                    zoom_factor = zoom / old_zoom
                    camera_x = mx - (mx - camera_x) * zoom_factor
                    camera_y = my - (my - camera_y) * zoom_factor
            
            elif event.button == 5:  #Scroll down
                if mx >= SCREEN_WIDTH - SIDEBAR_WIDTH:
                    # Scroll in sidebar
                    ui.handle_scroll(-1)
                elif mx < play_area_width:
                    # Zoom out
                    old_zoom = zoom
                    zoom = max(zoom - 0.1, min_zoom)
                    zoom_factor = zoom / old_zoom
                    camera_x = mx - (mx - camera_x) * zoom_factor
                    camera_y = my - (my - camera_y) * zoom_factor

    #Movement
    keys = pygame.key.get_pressed()
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
    camera_x += camera_velocity_x * dt
    camera_y += camera_velocity_y * dt
    
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
    
    money = update_world(grid, dt, money)
    
    play_area_rect = pygame.Rect(0, 0, play_area_width, SCREEN_HEIGHT)
    pygame.draw.rect(screen, (30, 30, 30), play_area_rect)
    
    world_surface = pygame.Surface((grid_pixel_width, grid_pixel_height))
    world_surface.fill((34, 139, 34))  #Background
    
    # Draw grid tiles
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            TILE_VALUE = tile["type"]
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if TILE_VALUE != 0:
                if TILE_VALUE in MACHINE_IMAGES:
                    img = MACHINE_IMAGES[TILE_VALUE]
                    rotation = tile.get("rotation", 0)
                    if rotation != 0:
                        # Rotate counter-clockwise (positive rotation)
                        img = pygame.transform.rotate(img, rotation)
                    world_surface.blit(img, (x * TILE_SIZE, y * TILE_SIZE))
                else:
                    colour = MACHINE_TYPES.get(TILE_VALUE, CEMPTY)
                    pygame.draw.rect(world_surface, colour, rect)
    
    # Draw connection zones if debug mode is on
    if show_zones:
        draw_connection_zones(world_surface, grid)
    
    # Draw grid lines
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(world_surface, (70, 70, 70), (x * TILE_SIZE, 0), (x * TILE_SIZE, grid_pixel_height), 1)
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(world_surface, (70, 70, 70), (0, y * TILE_SIZE), (grid_pixel_width, y * TILE_SIZE), 1)
    
    scaled_width = int(scaled_grid_width)
    scaled_height = int(scaled_grid_height)
    scaled_surface = pygame.transform.scale(world_surface, (scaled_width, scaled_height))
    
    screen.set_clip(play_area_rect)
    screen.blit(scaled_surface, (camera_x, camera_y))
    
    # Draw hologram preview
    mx, my = pygame.mouse.get_pos()
    if mx < play_area_width and ui.get_active_tool() > 0:  # Only show hologram for placement tools (not inspect or delete)
        world_x = (mx - camera_x) / zoom
        world_y = (my - camera_y) / zoom
        
        if 0 <= world_x < grid_pixel_width and 0 <= world_y < grid_pixel_height:
            gx = int(world_x // TILE_SIZE)
            gy = int(world_y // TILE_SIZE)
            
            if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                tool_to_place = ui.get_active_tool()
                current_tile_occupied = grid[gy][gx]["type"] != 0
                
                # Determine hologram color (green if can place, red if can't)
                if current_tile_occupied:
                    hologram_color = (255, 50, 50, 120)  # Red
                else:
                    hologram_color = (50, 255, 50, 120)  # Green
                
                # Draw hologram
                screen_x = camera_x + (gx * TILE_SIZE * zoom)
                screen_y = camera_y + (gy * TILE_SIZE * zoom)
                hologram_size = int(TILE_SIZE * zoom)
                
                hologram_rect = pygame.Rect(screen_x, screen_y, hologram_size, hologram_size)
                
                # Create semi-transparent surface for hologram
                hologram_surface = pygame.Surface((hologram_size, hologram_size), pygame.SRCALPHA)
                
                if tool_to_place in MACHINE_IMAGES:
                    # Draw rotated hologram image
                    img = MACHINE_IMAGES[tool_to_place]
                    # Rotate counter-clockwise
                    img_rotated = pygame.transform.rotate(img, building_rotation)
                    img_scaled = pygame.transform.scale(img_rotated, (hologram_size, hologram_size))
                    
                    # Apply color tint
                    img_scaled.fill(hologram_color[:3] + (0,), special_flags=pygame.BLEND_RGBA_ADD)
                    img_scaled.set_alpha(hologram_color[3])
                    hologram_surface.blit(img_scaled, (0, 0))
                else:
                    # Draw colored rectangle hologram
                    pygame.draw.rect(hologram_surface, hologram_color, (0, 0, hologram_size, hologram_size))
                
                screen.blit(hologram_surface, (screen_x, screen_y))
                
                # Draw border around hologram
                border_color = (255, 50, 50) if current_tile_occupied else (50, 255, 50)
                pygame.draw.rect(screen, border_color, hologram_rect, 2)
    
    screen.set_clip(None)
    
    boundary_rect = pygame.Rect(camera_x, camera_y, scaled_width, scaled_height)
    pygame.draw.rect(screen, (100, 100, 100), boundary_rect, 2)
    
    ui.draw(screen, money, building_rotation, show_zones)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()