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
    return [[{"type": 0, "stored": None, "amount": 0, "timer": 0} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

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

def update_world(grid, dt, money):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]

            #Coal drill
            if tile["type"] == 2:
                tile["timer"] += dt
                if tile["timer"] >= 2.0:
                    if tile["stored"] is None:
                        tile["stored"] = "coal"
                        tile["amount"] = 1
                    elif tile["stored"] == "coal":
                        tile["amount"] += 1
                    tile["timer"] = 0

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]

            if tile["type"] == 2:
                if 'output_timer' not in tile:
                    tile['output_timer'] = 0
                
                tile['output_timer'] += dt
                
                if tile['output_timer'] >= 0.5 and tile["amount"] > 0:
                    below_y = y + 1
                    if below_y < GRID_HEIGHT:
                        below_tile = grid[below_y][x]
                        
                        #Check
                        if below_tile["type"] == 1:
                            pipe_capacity = MACHINE_STATS[1]["capacity"]
                            space_available = pipe_capacity - below_tile["amount"]
                            
                            if space_available > 0:
                                if below_tile["stored"] is None or below_tile["stored"] == "coal":
                                    below_tile["stored"] = "coal"
                                    below_tile["amount"] += 1
                                    tile["amount"] -= 1
                                    
                                    if tile["amount"] == 0:
                                        tile["stored"] = None
                    
                    tile['output_timer'] = 0

            elif tile["type"] == 1: #Pipe
                tile["timer"] += dt
                if tile["timer"] >= 0.5 and tile["amount"] > 0:
                    below_y = y + 1
                    if below_y < GRID_HEIGHT:
                        below_tile = grid[below_y][x]
                        if below_tile["type"] == 1:
                            pipe_capacity = MACHINE_STATS[1]["capacity"]
                            space_available = pipe_capacity - below_tile["amount"]
                            
                            if space_available > 0 and (below_tile["stored"] is None or below_tile["stored"] == tile["stored"]):
                                below_tile["stored"] = tile["stored"]
                                below_tile["amount"] += 1
                                tile["amount"] -= 1
                                
                                if tile["amount"] == 0:
                                    tile["stored"] = None
                        
                        elif below_tile["type"] == 3: #Depot Van
                            depot_capacity = MACHINE_STATS[3]["capacity"]
                            space_available = depot_capacity - below_tile["amount"]
                            
                            if space_available > 0 and (below_tile["stored"] is None or below_tile["stored"] == tile["stored"]):
                                below_tile["stored"] = tile["stored"]
                                below_tile["amount"] += 1
                                tile["amount"] -= 1
                                
                                if tile["amount"] == 0:
                                    tile["stored"] = None
                    
                    tile["timer"] = 0
    
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

pygame.init()
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
max_zoom = 2.0

#Camera Move
camera_velocity_x = 0
camera_velocity_y = 0
camera_speed = 300  #pps

while run:
    screen.fill(BGC)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_grid()
            save_money(money)
            time.sleep(0.5)
            run = False

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
                            # Shift + click to inspect tile
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                ui.handle_tile_click(grid, gx, gy)
                            else:
                                # Normal click to place tile
                                grid[gy][gx]["type"] = ui.get_active_tool()
                                grid[gy][gx]["stored"] = None
                                grid[gy][gx]["amount"] = 0
                                grid[gy][gx]["timer"] = 0
                                if 'output_timer' in grid[gy][gx]:
                                    del grid[gy][gx]['output_timer']
                                if 'total_sold' in grid[gy][gx]:
                                    del grid[gy][gx]['total_sold']
                                if ui.get_active_tool() == 3:
                                    grid[gy][gx]['total_sold'] = 0
                                if ui.selected_tile and ui.selected_tile[1] == gx and ui.selected_tile[2] == gy:
                                    ui.handle_tile_click(grid, gx, gy)
                else:
                    ui.handle_click((mx, my))
            elif event.button == 3:
                if mx < play_area_width:
                    world_x = (mx - camera_x) / zoom
                    world_y = (my - camera_y) / zoom
                    
                    if 0 <= world_x < grid_pixel_width and 0 <= world_y < grid_pixel_height:
                        gx = int(world_x // TILE_SIZE)
                        gy = int(world_y // TILE_SIZE)
                        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                            ui.handle_tile_click(grid, gx, gy)
            
            elif event.button == 4:
                if mx < play_area_width:
                    old_zoom = zoom
                    zoom = min(zoom + 0.1, max_zoom)
                    zoom_factor = zoom / old_zoom
                    camera_x = mx - (mx - camera_x) * zoom_factor
                    camera_y = my - (my - camera_y) * zoom_factor
            
            elif event.button == 5:
                if mx < play_area_width:
                    old_zoom = zoom
                    zoom = max(zoom - 0.1, min_zoom)
                    zoom_factor = zoom / old_zoom
                    camera_x = mx - (mx - camera_x) * zoom_factor
                    camera_y = my - (my - camera_y) * zoom_factor

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                save_grid()
                save_money(money)

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
    dt = clock.get_time() / 1000
    money = update_world(grid, dt, money)
    play_area_rect = pygame.Rect(0, 0, play_area_width, SCREEN_HEIGHT)
    pygame.draw.rect(screen, (30, 30, 30), play_area_rect)
    world_surface = pygame.Surface((grid_pixel_width, grid_pixel_height))
    world_surface.fill(BGC)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = grid[y][x]
            TILE_VALUE = tile["type"]
            colour = MACHINE_TYPES.get(TILE_VALUE, CEMPTY)
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(world_surface, colour, rect)
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(world_surface, (70, 70, 70), (x * TILE_SIZE, 0), (x * TILE_SIZE, grid_pixel_height), 1)
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(world_surface, (70, 70, 70), (0, y * TILE_SIZE), (grid_pixel_width, y * TILE_SIZE), 1)
    scaled_width = int(scaled_grid_width)
    scaled_height = int(scaled_grid_height)
    scaled_surface = pygame.transform.scale(world_surface, (scaled_width, scaled_height))
    screen.set_clip(play_area_rect)
    screen.blit(scaled_surface, (camera_x, camera_y))
    screen.set_clip(None)
    boundary_rect = pygame.Rect(camera_x, camera_y, scaled_width, scaled_height)
    pygame.draw.rect(screen, (100, 100, 100), boundary_rect, 2)
    ui.draw(screen, money)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()