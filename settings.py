import pygame

#Grid stuff
TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15
GFILE = "data/world.json"
ROWS = 15
COL = 25

#Basics
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE + 200
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE
TITLE = "Industrial Capitalist"
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption(TITLE)

#Colours
BGC = (50, 50, 50)
WHITE = (255, 255, 255)

#Machine
CEMPTY = BGC
CPIPE = (0, 120, 255)

#Mach Type
MACHINE_TYPES = {
    0: CEMPTY,
    1: CPIPE
}