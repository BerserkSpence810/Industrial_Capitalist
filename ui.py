from settings import clock, FPS, SCREEN, SCREEN_HEIGHT, SCREEN_WIDTH, BGC, WHITE, TITLE

import pygame

def DrawGrid(tile_size):
    SCREEN.fill(BGC)

    #Grid vert lines
    for x in range(tile_size, SCREEN_WIDTH, tile_size):
        pygame.draw.line(SCREEN, WHITE, (x, 0), (x, SCREEN_HEIGHT))

    #Grid hori lines
    for y in range(tile_size,SCREEN_HEIGHT, tile_size):
        pygame.draw.line(SCREEN, WHITE, (0, y), (SCREEN_WIDTH, y))