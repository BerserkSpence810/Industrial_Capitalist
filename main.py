from ui import DrawGrid
from settings import clock, FPS, SCREEN, SCREEN_HEIGHT, SCREEN_WIDTH, BGC, WHITE, TITLE, tile_size

import pygame


run = True
while run:
    clock.tick(FPS)

    #Draw grid
    DrawGrid(tile_size)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()