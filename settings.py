import pygame

#Grid stuff
TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15
GFILE = "data/world.json"
MFILE = "data/money.json"
ROWS = 15
COL = 25

#Basics
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SIDEBAR_WIDTH = 200
TITLE = "Industrial Capitalist"
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption(TITLE)

#Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

#Colours
BGC = (50, 50, 50)
WHITE = (255, 255, 255)

#Machine stuff
CEMPTY = BGC
CPIPE = (0, 120, 255)
CCDRILL = (100, 60, 20)
CDEPOT = (20, 150, 20)
CDELETE = CEMPTY

coal_drill = pygame.image.load("assets/CoalDrill.png").convert_alpha()

MACHINE_TYPES = {
    0: CEMPTY,
    1: CPIPE,
    2: CCDRILL,
    3: CDEPOT,
    4: CDELETE
}

MACHINE_STATS = {
    1: {"name": "Pipe", "capacity": 10, "type": "pipe"},
    2: {"name": "Coal Drill", "rate": 1.0, "type": "drill", "output_dir": DOWN},
    3: {"name": "Van Depot", "capacity": 20, "type": "depot", "input_dir": UP}
}

ITEM_VALUES = {
    "coal": 5.22
}