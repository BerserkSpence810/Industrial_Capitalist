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
SIDEBAR_WIDTH = 200  # Back to original size
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
CLPIPE_R = (0, 180, 255)  # Lighter blue for L-pipe right
CLPIPE_L = (0, 200, 255)  # Even lighter blue for L-pipe left
CMERGER = (255, 180, 0)   # Orange for merger
CSPLITTER = (255, 100, 200)  # Pink for splitter

MACHINE_TYPES = {
    0: CEMPTY,
    1: CPIPE,
    2: CCDRILL,
    3: CDEPOT,
    4: CLPIPE_R,
    5: CLPIPE_L,
    6: CMERGER,
    7: CSPLITTER
}

MACHINE_IMAGES = {}

MACHINE_STATS = {
    0: {"name": "Empty", "type": "empty", "cost": 0},
    1: {"name": "Pipe", "capacity": 10, "type": "pipe", "cost": 10, "output_dir": DOWN, "input_dir": UP},
    2: {"name": "Coal Drill", "rate": 1.0, "type": "drill", "output_dir": DOWN, "cost": 50},
    3: {"name": "Van Depot", "capacity": 20, "type": "depot", "input_dir": UP, "cost": 100},
    4: {"name": "L-Pipe R", "capacity": 10, "type": "pipe", "cost": 15, "output_dir": RIGHT, "input_dir": UP},
    5: {"name": "L-Pipe L", "capacity": 10, "type": "pipe", "cost": 15, "output_dir": LEFT, "input_dir": UP},
    6: {"name": "Merger", "capacity": 15, "type": "merger", "cost": 25, "output_dir": DOWN, "input_dirs": [UP, LEFT, RIGHT]},
    7: {"name": "Splitter", "capacity": 15, "type": "splitter", "cost": 25, "output_dirs": [LEFT, RIGHT, DOWN], "input_dir": UP}
}

ITEM_VALUES = {
    "coal": 5.22
}