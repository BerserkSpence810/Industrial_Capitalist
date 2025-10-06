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
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def save_grid():
    os.makedirs("data", exist_ok=True)
    with open(GFILE, "w") as f:
        json.dump(grid, f)

pygame.init()
grid = load_grid()
run = True
ui = DrawGrid()

while run:
    screen.fill(BGC)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_grid()
            time.sleep(0.5)
            run = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()

            if mx < GRID_WIDTH * TILE_SIZE:
                gx = mx // TILE_SIZE
                gy = my // TILE_SIZE
                grid[gy][gx] = ui.get_active_tool()
            else:
                ui.handle_click((mx, my))
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_grid()
                print("Grid saved!")

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            TILE_VALUE = grid[y][x]
            colour = MACHINE_TYPES.get(TILE_VALUE, CEMPTY)
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, colour, rect)
    
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, (70, 70, 70), (x * TILE_SIZE, 0), (x * TILE_SIZE, SCREEN_HEIGHT), 1)
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, (70, 70, 70), (0, y * TILE_SIZE), (GRID_WIDTH * TILE_SIZE, y * TILE_SIZE), 1)

    ui.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
            
pygame.quit()