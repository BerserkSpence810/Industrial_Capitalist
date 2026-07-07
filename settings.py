import pygame

TILE_SIZE = 32

GRID_WIDTH = 40
GRID_HEIGHT = 40
GFILE = "data/world.json"
MFILE = "data/money.json"
CFILE = "data/contracts.json"
ROWS = 15
COL = 25

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SIDEBAR_WIDTH = 200
TITLE = "Industrial Capitalist"
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption(TITLE)


UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

BGC = (32, 34, 37)
WHITE = (255, 255, 255)

MACHINE_TYPES = {
    0:   BGC,
    1:   (0, 120, 255),    # pipe
    2:   (100, 60, 20),    # coal drill
    3:   (20, 150, 20),    # van depot
    4:   (0, 180, 255),    # L-pipe R
    5:   (0, 200, 255),    # L-pipe L
    6:   (255, 180, 0),    # merger
    7:   (255, 100, 200),  # splitter
    8:   (140, 140, 140),  # iron drill
    9:   (255, 80, 40),    # furnace
    10:  (180, 180, 200),  # ingot molder
    11:  (255, 200, 50),   # solar panel
    12:  (60, 60, 70),     # coal generator
    13:  (80, 40, 160),    # research station
    14:  (72, 48, 28),     # blast furnace
    15:  (28, 32, 38),     # oil rig
    16:  (42, 28, 52),     # diesel refinery
    17:  (72, 62, 18),     # diesel generator
    18:  (130, 95, 55),    # sawmill
    19:  (140, 145, 155),  # press
    20:  (135, 140, 150),  # roller
    21:  (40, 130, 145),   # scrubber
    22:  (135, 105, 60),   # item silo
    23:  (60, 95, 135),    # fluid silo
    24:  (255, 220, 80),   # solar panel 2
    25:  (255, 240, 120),  # solar panel 3
    26:  (200, 220, 230),  # wind turbine 1
    27:  (220, 235, 245),  # wind turbine 2
    28:  (240, 248, 255),  # wind turbine 3
    29:  (180, 60, 30),    # liquid burner
    30:  (195, 105, 55),   # copper drill
    31:  (130, 95, 55),    # soil excavator
    32:  (155, 145, 125),  # quarry
    33:  (75, 80, 90),     # grinder
    34:  (105, 95, 70),    # raw mill
    35:  (180, 90, 45),    # industrial kiln
    36:  (90, 130, 175),   # water pump
    38:  (145, 140, 130),  # concrete plant
    39:  (95, 125, 85),    # craft assembler
    40:  (165, 75, 105),   # steam cracking plant
    41:  (125, 85, 155),   # plastic refinery
    43:  (210, 175, 75),   # plastic production facility
    44:  (175, 125, 95),   # plastic molding machine
    45:  (70, 95, 130),    # natural gas well
    46:  (55, 115, 140),   # condenser
    47:  (90, 110, 150),   # gas refinery
    49:  (180, 100, 40),   # gas burner
    50:  (185, 125, 70),   # kiln
    51:  (65, 90, 120),    # liquid truck depot
    53:  (65, 130, 55),    # tree farm
    55:  (180, 150, 50),   # gold acid refinery
    57:  (165, 80, 40),    # industrial electric furnace
    58:  (155, 130, 180),  # alloyer
    59:  (120, 200, 180),  # lithium ore drill
    60:  (140, 155, 100),  # chemical reactor
    61:  (100, 80, 140),   # advanced assembler
    64:  (80, 130, 155),   # water treatment plant
    65:  (145, 155, 100),  # chemical plant
    68:  (85, 75, 65),     # mineshaft drill
    70:  (100, 165, 130),  # lithium brine extractor
    77:  (125, 130, 140),  # lathe
    78:  (160, 100, 45),   # foundry
    79:  (60, 180, 160),   # logic assembler
    81:  (80, 150, 180),   # electrolysis plant
    82:  (100, 130, 150),  # filtration plant
    83:  (70, 80, 95),     # huge truck depot
    87:  (80, 60, 40),     # coal liquefaction plant
    89:  (175, 85, 50),    # liquid boiler
    90:  (140, 160, 185),  # air separation unit
    91:  (85, 110, 95),    # bottling plant
    92:  (150, 100, 75),   # industrial plastic molder
    93:  (170, 160, 135),  # paper mill
    96:  (180, 30, 30),    # nuclear power plant
    97:  (120, 110, 90),   # LV pole
    98:  (100, 110, 130),  # MV pole
    99:  (140, 50, 50),    # HV pole
    100: (90, 100, 120),   # MV battery
    101: (130, 60, 60),    # HV battery
    102: (110, 90, 70),    # HV transformer
    103: (50, 55, 70),     # NAND gate
    104: (55, 50, 70),     # NOR gate
    105: (60, 55, 65),     # NOT gate
    106: (90, 95, 110),    # steam turbine
    107: (160, 130, 50),   # gasoline generator
    108: (70, 65, 55),     # coal power plant
    109: (200, 120, 60),   # industrial electric furnace MK2
    110: (60, 55, 50),     # exhaust stack
    111: (45, 60, 75),     # AND gate
    112: (50, 65, 70),     # OR gate
    113: (55, 60, 75),     # XOR gate
    114: (100, 50, 180),   # research station 2
    115: (120, 60, 200),   # research station 3
    116: (150, 90, 40),    # industrial kiln 2
    117: (80, 120, 160),   # electrolysis water
    118: (0, 255, 200),    # infinite generator
    119: (235, 195, 60),   # adurite pipe
    120: (245, 205, 80),   # adurite L-pipe R
    121: (255, 215, 100),  # adurite L-pipe L
    122: (220, 175, 40),   # adurite merger
    123: (255, 225, 120),  # adurite splitter
    124: (210, 165, 30),   # adurite intersection
    125: (170, 180, 220),  # iridium pipe
    126: (190, 200, 235),  # iridium L-pipe R
    127: (200, 210, 245),  # iridium L-pipe L
    128: (150, 160, 200),  # iridium merger
    129: (210, 220, 250),  # iridium splitter
    130: (130, 140, 180),  # iridium intersection
    131: (0, 140, 220),    # pipe intersection
}

MACHINE_IMAGES = {}

MACHINE_STATS = {
    0:  {"name": "Empty", "type": "empty", "cost": 0},
    1:  {"name": "Pipe",         "rate": 6.0, "capacity": 12, "type": "pipe",    "category": "pipe",  "cost": 10,  "output_dir": DOWN,  "input_dir": UP,
         "transfer_interval": 0.5, "push_per_tick": 3},
    4:  {"name": "L-Pipe R",     "rate": 6.0, "capacity": 12, "type": "pipe",    "category": "pipe",  "cost": 2,   "output_dir": RIGHT, "input_dir": UP,
         "transfer_interval": 0.5, "push_per_tick": 3},
    5:  {"name": "L-Pipe L",     "rate": 6.0, "capacity": 12, "type": "pipe",    "category": "pipe",  "cost": 2,   "output_dir": LEFT,  "input_dir": UP,
         "transfer_interval": 0.5, "push_per_tick": 3},
    6:  {"name": "Merger",       "rate": 6.0, "capacity": 18, "type": "merger",  "category": "pipe",  "cost": 10,  "output_dir": DOWN,  "input_dirs": [UP,LEFT,RIGHT],
         "transfer_interval": 0.5, "push_per_tick": 9},
    7:  {"name": "Splitter",     "rate": 6.0, "capacity": 18, "type": "splitter","category": "pipe",  "cost": 10,  "output_dirs": [LEFT,RIGHT,DOWN], "input_dir": UP,
         "transfer_interval": 0.5, "push_per_tick": 9},
    131: {"name": "Pipe Intersection", "rate": 6.0, "capacity": 12, "type": "pipe", "category": "pipe", "cost": 15,
          "output_dirs": [UP, DOWN, LEFT, RIGHT], "input_dirs": [UP, DOWN, LEFT, RIGHT],
          "transfer_interval": 0.5, "push_per_tick": 3},
    119: {"name": "Adurite Pipe",       "rate": 40.0, "capacity": 60, "type": "pipe",    "category": "pipe", "cost": 150,
          "output_dir": DOWN, "input_dir": UP,
          "transfer_interval": 0.5, "push_per_tick": 20},
    120: {"name": "Adurite L-Pipe R",   "rate": 40.0, "capacity": 60, "type": "pipe",    "category": "pipe", "cost": 50,
          "output_dir": RIGHT, "input_dir": UP,
          "transfer_interval": 0.5, "push_per_tick": 20},
    121: {"name": "Adurite L-Pipe L",   "rate": 40.0, "capacity": 60, "type": "pipe",    "category": "pipe", "cost": 50,
          "output_dir": LEFT, "input_dir": UP,
          "transfer_interval": 0.5, "push_per_tick": 20},
    122: {"name": "Adurite Merger",      "rate": 40.0, "capacity": 60, "type": "merger",  "category": "pipe", "cost": 120,
          "output_dir": DOWN, "input_dirs": [UP, LEFT, RIGHT],
          "transfer_interval": 0.5, "push_per_tick": 20},
    123: {"name": "Adurite Splitter",    "rate": 40.0, "capacity": 60, "type": "splitter","category": "pipe", "cost": 120,
          "output_dirs": [LEFT, RIGHT, DOWN], "input_dir": UP,
          "transfer_interval": 0.5, "push_per_tick": 20},
    124: {"name": "Adurite Intersection","rate": 40.0,"capacity": 60, "type": "pipe",    "category": "pipe", "cost": 180,
          "output_dirs": [UP, DOWN, LEFT, RIGHT], "input_dirs": [UP, DOWN, LEFT, RIGHT],
          "transfer_interval": 0.5, "push_per_tick": 20},
    125: {"name": "Iridium Pipe",        "rate": 120.0, "capacity": 200, "type": "pipe",    "category": "pipe", "cost": 1200,
          "output_dir": DOWN, "input_dir": UP,
          "transfer_interval": 0.5, "push_per_tick": 60},
    126: {"name": "Iridium L-Pipe R",    "rate": 120.0, "capacity": 200, "type": "pipe",    "category": "pipe", "cost": 200,
          "output_dir": RIGHT, "input_dir": UP,
          "transfer_interval": 0.5, "push_per_tick": 60},
    127: {"name": "Iridium L-Pipe L",    "rate": 120.0, "capacity": 200, "type": "pipe",    "category": "pipe", "cost": 200,
          "output_dir": LEFT, "input_dir": UP,
          "transfer_interval": 0.5, "push_per_tick": 60},
    128: {"name": "Iridium Merger",      "rate": 120.0, "capacity": 200, "type": "merger",  "category": "pipe", "cost": 500,
          "output_dir": DOWN, "input_dirs": [UP, LEFT, RIGHT],
          "transfer_interval": 0.5, "push_per_tick": 60},
    129: {"name": "Iridium Splitter",    "rate": 120.0, "capacity": 200, "type": "splitter","category": "pipe", "cost": 500,
          "output_dirs": [LEFT, RIGHT, DOWN], "input_dir": UP,
          "transfer_interval": 0.5, "push_per_tick": 60},
    130: {"name": "Iridium Intersection","rate": 120.0, "capacity": 200, "type": "pipe",    "category": "pipe", "cost": 750,
          "output_dirs": [UP, DOWN, LEFT, RIGHT], "input_dirs": [UP, DOWN, LEFT, RIGHT],
          "transfer_interval": 0.5, "push_per_tick": 60},
    3:  {"name": "Van Depot",                  "type": "depot", "category": "logistics", "cost": 500,
         "input_dir": UP, "capacity": 12,
         "cooldown_time": 8.0,  "sell_bonus": 0.90, "sell_threshold": 0.50},
    83: {"name": "Huge Truck Depot",           "type": "depot", "category": "logistics", "cost": 8500,
         "size": (6,6), "capacity": 350,
         "cooldown_time": 16.0, "sell_bonus": 1.25, "sell_threshold": 1.00},
    51: {"name": "Liquid Truck Depot",         "type": "depot", "category": "logistics", "cost": 12000,
         "size": (4,6), "sell_capacity": 500,
         "cooldown_time": 14.0, "sell_bonus": 1.05, "sell_threshold": 0.75},
    2:  {"name": "Coal Drill",        "rate": 0.5,   "capacity": 10, "type": "drill", "category": "drill", "cost": 150,   "output_dir": DOWN, "power_input": 120,   "power_transfer": 1200,  "power_capacity": 900},
    8:  {"name": "Iron Drill",        "rate": 0.1,   "capacity": 10, "type": "drill", "category": "drill", "cost": 1200,  "output_dir": DOWN, "power_input": 1200,  "power_transfer": 9000,  "power_capacity": 50000},
    30: {"name": "Copper Drill",      "rate": 0.15,  "capacity": 20, "type": "drill", "category": "drill", "cost": 1100,  "output_dir": DOWN, "size": (1,2), "power_input": 1000, "power_transfer": 3000,  "power_capacity": 20000},
    31: {"name": "Soil Excavator",    "rate": 0.25,  "capacity": 20, "type": "drill", "category": "drill", "cost": 400,   "output_dir": DOWN, "size": (2,2), "power_input": 200,  "power_transfer": 2000,  "power_capacity": 5000},
    32: {"name": "Quarry",            "rate": 1/6,   "capacity": 30, "type": "drill", "category": "drill", "cost": 1500,  "output_dir": DOWN, "size": (4,4), "power_input": 800,  "power_transfer": 3000,  "power_capacity": 10000},
    53: {"name": "Tree Farm",         "rate": 1/8,   "capacity": 20, "type": "drill", "category": "drill", "cost": 1500,  "output_dir": DOWN, "size": (3,3), "power_input": 500,  "power_transfer": 3000,  "power_capacity": 8000},
    59: {"name": "Lithium Ore Drill", "rate": 0.05,  "capacity": 20, "type": "drill", "category": "drill", "cost": 95000, "output_dir": DOWN, "size": (2,2), "power_input": 45000,"power_transfer": 60000, "power_capacity": 150000},
    68: {"name": "Mineshaft Drill",   "rate": 1/10,  "capacity": 20, "type": "drill", "category": "drill", "cost": 180000, "output_dir": DOWN, "size": (3,3), "power_input": 8000, "power_transfer": 15000, "power_capacity": 80000},
    15: {"name": "Oil Rig",              "type": "fluid_producer", "cost": 22000,  "size": (2,1), "power_input": 15000,"power_transfer": 30000, "power_capacity": 50000},
    36: {"name": "Water Pump",           "type": "fluid_producer", "category": "drill", "cost": 500,   "size": (2,2), "power_input": 600,  "power_transfer": 3000,  "power_capacity": 5000},
    45: {"name": "Natural Gas Well",     "type": "fluid_producer", "category": "drill", "cost": 18000,  "size": (2,2), "power_input": 800,  "power_transfer": 3000,  "power_capacity": 8000},
    70: {"name": "Lithium Brine Extractor","type": "fluid_producer","category": "drill","cost": 150000, "size": (3,3), "power_input": 3000, "power_transfer": 6000,  "power_capacity": 20000},
    90: {"name": "Air Separation Unit",  "type": "fluid_producer", "category": "drill", "cost": 110000, "size": (3,3), "power_input": 4000, "power_transfer": 8000,  "power_capacity": 30000},
    11:  {"name": "Solar Panel",    "type": "power_source", "cost": 120,     "power_output": 280,       "power_transfer": 600,      "power_capacity": 1000,     "power_range": 3},
    24:  {"name": "Solar Panel 2",  "type": "power_source", "cost": 700,     "power_output": 528,       "power_transfer": 1200,     "power_capacity": 2000,     "power_range": 5},
    25:  {"name": "Solar Panel 3",  "type": "power_source", "cost": 80000,    "power_output": 1056,      "power_transfer": 2400,     "power_capacity": 4000,     "power_range": 5},
    26:  {"name": "Wind Turbine 1", "type": "power_source", "cost": 400,     "size": (2,2), "power_output": 1500,    "power_transfer": 3000,   "power_capacity": 5000,     "power_range": 6},
    27:  {"name": "Wind Turbine 2", "type": "power_source", "cost": 20000,    "size": (2,2), "power_output": 16000,   "power_transfer": 30000,  "power_capacity": 50000,    "power_range": 7},
    28:  {"name": "Wind Turbine 3", "type": "power_source", "cost": 150000,  "size": (3,3), "power_output": 50000,   "power_transfer": 100000, "power_capacity": 1000000,  "power_range": 10},
    12:  {"name": "Coal Generator", "type": "power_source", "cost": 160,     "size": (2,2), "power_output": 7000,    "power_transfer": 9000,   "power_capacity": 7000,     "coal_consumption": 0.25, "input_dir": UP, "power_range": 4},
    17:  {"name": "Diesel Generator","type": "power_source","cost": 30000,    "size": (2,1), "power_output": 90000,   "power_transfer": 150000, "power_capacity": 250000,   "power_range": 10, "fuel_capacity": 10.0},
    106: {"name": "Steam Turbine",  "type": "power_source", "category": "power", "cost": 18000,   "size": (3,3), "power_output": 500000,  "power_transfer": 1000000,"power_capacity": 5000000,  "power_range": 8,  "power_input": 2000},
    107: {"name": "Gasoline Generator","type": "power_source","category": "power","cost": 35000,   "size": (2,2), "power_output": 120000,  "power_transfer": 500000, "power_capacity": 2000000,  "power_range": 6},
    108: {"name": "Coal Power Plant","type": "power_source", "category": "power", "cost": 2500000,"size": (12,12),"power_output": 500000000,"power_transfer": 1000000000,"power_capacity": 2000000000,"power_range": 25},
    96:  {"name": "Nuclear Power Plant","type": "power_source","category": "power","cost": 1200000,"size": (16,16),"power_output": 1320000000,"power_transfer": 2000000000,"power_capacity": 5000000000,"power_range": 20},
    97:  {"name": "LV Pole",    "type": "power_pole","category": "power","cost": 5,      "power_transfer": 2400,     "power_capacity": 2400,     "power_range": 2},
    98:  {"name": "MV Pole",    "type": "power_pole","category": "power","cost": 500,    "power_transfer": 24000,    "power_capacity": 50000,    "power_range": 3},
    99:  {"name": "HV Pole",    "type": "power_pole","category": "power","cost": 300000,"size": (2,2),"power_transfer": 120000000,"power_capacity": 50000000,"power_range": 10},
    118: {"name": "Infinite Generator", "type": "power_source", "category": "power", "cost": 0, "size": (1, 1), "power_output":   1.0e18, "power_transfer": 1.0e18, "power_capacity": 1.0e18, "power_range":    9999, "infinite": True},
    100: {"name": "MV Battery", "type": "power_storage","category": "power","cost": 5000,  "size": (2,2),"power_transfer": 50000,   "power_capacity": 10000000},
    101: {"name": "HV Battery", "type": "power_storage","category": "power","cost": 250000, "size": (2,2),"power_transfer": 500000,  "power_capacity": 100000000},
    102: {"name": "HV Transformer","type": "processor","category": "power","cost": 200000,"size": (2,3),"power_input": 10000,"power_transfer": 120000000,"power_capacity": 50000000},
    117: {"name": "Electric Water Heater","type": "processor","category": "power","cost": 5000,"size": (2,2),"power_input": 50000,"power_transfer": 100000,"power_capacity": 500000},
    103: {"name": "NAND Gate","type": "logic","category": "logic","cost": 800},
    104: {"name": "NOR Gate", "type": "logic","category": "logic","cost": 800},
    105: {"name": "NOT Gate", "type": "logic","category": "logic","cost": 700},
    111: {"name": "AND Gate", "type": "logic","category": "logic","cost": 800},
    112: {"name": "OR Gate",  "type": "logic","category": "logic","cost": 800},
    113: {"name": "XOR Gate", "type": "logic","category": "logic","cost": 850},
    22:  {"name": "Item Silo",               "type": "storage","category": "storage","cost": 800,  "size": (2,2),"capacity": 500,  "input_dir": UP,"output_dir": DOWN},
    23:  {"name": "Fluid Silo",              "type": "storage","category": "storage","cost": 1000, "size": (2,2),"capacity": 100,  "input_dir": UP,"output_dir": DOWN},
    13:  {"name": "Research Station 1","type": "research","cost": 75,   "size": (2,2), "power_input": 2100,  "power_transfer": 3000,  "power_capacity": 3000,   "power_range": 6, "rp_formula": "sqrt_n"},
    114: {"name": "Research Station 2","type": "research","cost": 7500, "size": (8,8), "power_input": 8000,  "power_transfer": 15000, "power_capacity": 20000,  "power_range": 6, "rp_formula": "rs2_item","item_cycle_time": 2.0, "rp_per_item": 10.0},
    115: {"name": "Research Station 3","type": "research","cost": 250000,"size": (8,8), "power_input": 20000, "power_transfer": 40000, "power_capacity": 80000,  "power_range": 8, "rp_formula": "rs3_dual","item_cycle_time": 0.5, "rp_per_item": 25.0},
    21:  {"name": "Scrubber",     "type": "scrubber","category": "scrubber","cost": 1500,"size": (2,2),"power_input": 5000,"power_transfer": 10000,"power_capacity": 50000,"scrub_rate": 0.005},
    110: {"name": "Exhaust Stack","type": "utility","category": "utility","cost": 2000,"size": (2,3),"power_input": 0,"power_capacity": 0,"base_pollution_rate": 0.001},
    109: {"name": "Electric Furnace","type": "processor","category": "furnace","cost": 1200,  "size": (2,2),"power_input": 24000,"power_transfer": 40000,"power_capacity": 150000},
    9:   {"name": "Furnace",         "type": "processor","category": "furnace","cost": 400,  "size": (1,1),"input_dirs": [UP, LEFT],"output_dir": DOWN,"capacity": 8,"coal_capacity": 10,"power_input": 500,"power_transfer": 1500,"power_capacity": 5000},
    10:  {"name": "Ingot Molder",    "type": "processor",                      "cost": 1500, "size": (1,1),"input_dir": UP,"output_dir": DOWN,"power_input": 1500,"power_transfer": 4000,"power_capacity": 15000},
    14:  {"name": "Blast Furnace",   "type": "processor",                      "cost": 6500, "size": (3,3),"power_input": 8000,"power_transfer": 25000,"power_capacity": 200000,"coal_capacity": 16,"ingot_capacity": 4,"output_capacity": 8,"processing_time": 5.0},
    57:  {"name": "Industrial Electric Furnace","type": "processor","category": "processor","cost": 120000,"size": (3,3),"power_input": 200000,"power_transfer": 400000,"power_capacity": 1000000},
    78:  {"name": "Foundry",         "type": "processor","category": "processor","cost": 500000,"size": (6,6),"power_input": 50000,"power_transfer": 100000,"power_capacity": 500000},
    116: {"name": "Industrial Firebox","type": "processor","category": "processor","cost": 3500,"size": (2,3),"power_input": 0,"power_transfer": 5000,"power_capacity": 10000},
    18:  {"name": "Sawmill",         "type": "processor",                      "cost": 3000,  "size": (2,3),"power_input": 3000,"power_transfer": 10000,"power_capacity": 30000},
    19:  {"name": "Press",           "type": "processor",                      "cost": 2500,  "size": (2,2),"power_input": 6250,"power_transfer": 15000,"power_capacity": 250000},
    20:  {"name": "Roller",          "type": "processor",                      "cost": 2500,  "size": (2,2),"power_input": 1125,"power_transfer": 3000,"power_capacity": 250000},
    33:  {"name": "Grinder",         "type": "processor","category": "processor","cost": 800,  "size": (2,2),"power_input": 4000, "power_transfer": 10000,"power_capacity": 30000},
    34:  {"name": "Raw Mill",        "type": "processor","category": "processor","cost": 3500,"size": (3,3),"power_input": 1200,"power_transfer": 3000,"power_capacity": 8000},
    35:  {"name": "Industrial Kiln", "type": "processor","category": "processor","cost": 5500,"size": (4,6),"power_input": 2500,"power_transfer": 4000,"power_capacity": 15000},
    77:  {"name": "Lathe",           "type": "processor","category": "processor","cost": 25000,"size": (2,3),"power_input": 3000,"power_transfer": 6000,"power_capacity": 25000},
    39:  {"name": "Craft Assembler", "type": "processor","category": "processor","cost": 4500,"size": (3,3),"power_input": 4000,"power_transfer": 8000,"power_capacity": 10000},
    61:  {"name": "Advanced Assembler","type": "processor","category": "processor","cost": 45000,"size": (4,4),"power_input": 4000,"power_transfer": 8000,"power_capacity": 20000},
    79:  {"name": "Logic Assembler", "type": "processor","category": "processor","cost": 350000,"size": (4,4),"power_input": 120000,"power_transfer": 250000,"power_capacity": 1000000},
    38:  {"name": "Concrete Plant",  "type": "processor","category": "processor","cost": 5000,"size": (4,4),"power_input": 1800,"power_transfer": 4000,"power_capacity": 12000},
    50:  {"name": "Kiln",           "type": "processor","category": "processor","cost": 2000, "size": (2,3),"power_input": 400,"power_transfer": 2000,"power_capacity": 6000},
    40:  {"name": "Steam Cracking Plant","type": "processor","category": "processor","cost": 30000,"size": (4,6),"power_input": 3500,"power_transfer": 6000,"power_capacity": 20000},
    41:  {"name": "Plastic Refinery","type": "processor","category": "processor","cost": 28000,"size": (3,3),"power_input": 18000,"power_transfer": 30000,"power_capacity": 100000},
    43:  {"name": "Plastic Production Facility","type": "processor","category": "processor","cost": 35000,"size": (4,4),"power_input": 4000,"power_transfer": 7000,"power_capacity": 25000},
    44:  {"name": "Plastic Molding Machine","type": "processor","category": "processor","cost": 20000,"size": (3,3),"power_input": 1400,"power_transfer": 3000,"power_capacity": 10000},
    92:  {"name": "Industrial Plastic Molder","type": "processor","category": "processor","cost": 30000,"size": (3,3),"power_input": 2500,"power_transfer": 5000,"power_capacity": 15000},
    16:  {"name": "Diesel Refinery", "type": "processor",                      "cost": 25000,"size": (3,3),"power_input": 1000,"power_transfer": 20000,"power_capacity": 50000},
    46:  {"name": "Condenser",       "type": "processor","category": "processor","cost": 14000,"size": (2,3),"power_input": 1200,"power_transfer": 4000,"power_capacity": 10000},
    47:  {"name": "Gas Refinery",    "type": "processor","category": "processor","cost": 22000,"size": (3,3),"power_input": 2000,"power_transfer": 5000,"power_capacity": 15000},
    49:  {"name": "Gas Burner",      "type": "processor","category": "processor","cost": 5000, "size": (2,2),"power_input": 100,"power_transfer": 1000,"power_capacity": 3000},
    87:  {"name": "Coal Liquefaction Plant","type": "processor","category": "processor","cost": 45000,"size": (4,6),"power_input": 6000,"power_transfer": 12000,"power_capacity": 40000},
    89:  {"name": "Liquid Boiler",   "type": "processor","category": "processor","cost": 4000,"size": (2,3),"power_input": 1000,"power_transfer": 3000,"power_capacity": 8000},
    55:  {"name": "Gold Acid Refinery","type": "processor","category": "processor","cost": 100000,"size": (3,4),"power_input": 2500,"power_transfer": 6000,"power_capacity": 18000},
    58:  {"name": "Alloyer",         "type": "processor","category": "processor","cost": 140000,"size": (3,3),"power_input": 3000,"power_transfer": 6000,"power_capacity": 20000},
    60:  {"name": "Chemical Reactor","type": "processor","category": "processor","cost": 32000,"size": (3,3),"power_input": 2000,"power_transfer": 5000,"power_capacity": 15000},
    64:  {"name": "Water Treatment Plant","type": "processor","category": "processor","cost": 30000,"size": (3,4),"power_input": 2000,"power_transfer": 5000,"power_capacity": 15000},
    65:  {"name": "Chemical Plant",  "type": "processor","category": "processor","cost": 32000,"size": (3,3),"power_input": 22000,"power_transfer": 40000,"power_capacity": 120000},
    29:  {"name": "Liquid Burner",   "type": "processor",                      "cost": 600, "size": (2,2),"power_input": 200,"power_transfer": 1200,"power_capacity": 5000,"input_dir": UP},
    81:  {"name": "Electrolysis Plant","type": "processor","category": "processor","cost": 35000,"size": (3,4),"power_input": 5000,"power_transfer": 10000,"power_capacity": 40000},
    82:  {"name": "Filtration Plant","type": "processor","category": "processor","cost": 25000,"size": (2,3),"power_input": 1500,"power_transfer": 4000,"power_capacity": 12000},
    91:  {"name": "Bottling Plant",  "type": "processor","category": "processor","cost": 8000,"size": (3,3),"power_input": 800,"power_transfer": 3000,"power_capacity": 8000},
    93:  {"name": "Paper Mill",      "type": "processor","category": "processor","cost": 5500,"size": (3,3),"power_input": 1500,"power_transfer": 4000,"power_capacity": 12000},
}

ITEM_VALUES = {
    "coal": 5.20, "raw_iron": 5.80, "raw_copper": 5.51, "oak_log": 5.80,
    "soil": 0.30, "clay": 0.80, "limestone": 1.20, "gravel": 1.50, "sand": 0.50,
    "lithium_ore": 8.00, "deep_earth_fragment": 5.00, "earth_fragment": 2.00,
    "crude_oil": 11.60, "raw_gas": 2.00, "raw_lead": 4.00, "raw_zinc": 4.00, "water": 0.10,
    "liquid_iron": 23.20, "iron_ingot": 65.54, "iron_powder": 3.00, "iron_mix": 8.00,
    "iron_plate": 80.0, "iron_plate2": 340.0, "iron_coil": 55.0,
    "cut_oak_log": 3.50, "chunk_plank": 4.50, "planks": 8.00, "plank2": 18.00,
    "nails": 5.00, "chair": 1029.50,
    "steel": 48.72, "steel_plate": 65.0, "steel_rod": 72.0, "gear": 85.0,
    "steel_coil": 130.0, "crankshaft": 758.00, "gearbox": 2552.00, "galvanized_steel": 240.0,
    "liquid_copper": 7.54, "copper_ingot": 16.00, "copper_powder": 3.50,
    "copper_mix": 10.00, "copper_plate": 38.0, "copper_wire": 9.0, "insulated_wire": 32.0,
    "karat_gold": 40.00, "bauxite_residue": -0.5, "purified_gold": 200.00,
    "liquid_gold": 350.00, "gold_ingot": 500.00, "gold_wire": 25.00, "purple_gold_ingot": 20000.00,
    "crushed_bauxite": 3.00, "alumina": 10.00, "alumina_dust": 8.00,
    "liquid_aluminium": 30.00, "aluminium_ingot": 50.00,
    "ferroaluminium_magnet": 200.00, "ferroaluminium_alloy_ingot": 150.00,
    "lithium_sulfate": 25.00, "dirty_lithium_sulfate": 8.00,
    "lithium_carbonate": 80.0, "lithium_ion_battery": 120.0,
    "charged_lithium_battery": 300.0, "rubber": 18.0, "graphite_electrode": 15.00,
    "lithium_battery_pack": 2200.0, "lithium_brine": 12.00, "sodium_carbonate": 30.00,
    "rawmix": 6.00, "aggregate": 2.50, "cement": 28.00, "wet_concrete": 8.00,
    "concrete_block": 150.00, "reinforced_concrete": 420.0,
    "clay_bricks": 8.00, "brick": 50.00,
    "paraxylene": 12.00, "ethylene": 8.00, "ethanol": 6.00, "acetic_acid": 10.00,
    "pta": 18.00, "meg": 14.00, "plastic_pellets": 25.0, "plastic_casing": 42.0,
    "condensed_gas": 8.00, "refined_gas": 25.00, "lng": 160.00,
    "poor_quality_diesel": 21.80, "diesel": 30.50, "refined_diesel": 40.60, "residue": -8.0,
    "naphtha": 8.00, "heavy_oil": 6.00, "light_oil": 7.00, "gasoline": 35.00,
    "leaded_gasoline": 45.00, "coke_fuel": 8.00, "machine_oil": 30.00,
    "sulfuric_acid": 15.00, "hydrochloric_acid": 12.00, "boric_acid": 20.00,
    "chlorine": 5.00, "liquid_sulfur": 10.00, "sulfur": 8.00, "table_salt": 3.00,
    "hydrogen": 2.00, "oxygen": 1.00, "steam": 1.50, "filter": 20.00,
    "silicon": 12.00, "semiconductor": 100.0, "logic_plate": 180.0,
    "glass": 8.00, "liquid_glass": 5.00, "paper": 5.00,
    "microchip_2x": 12000.0, "microchip_8x64x": 200000.0,
    "drill_head": 40.00, "steel_drill_head": 120.00, "iron_drill_head": 25.00,
    "copper_drill_head": 60.00, "electric_motor": 500.00, "electromagnet": 180.00,
    "black_dye": 6.00, "liquid_lead": 18.00, "lead_ingot": 25.00, "liquid_zinc": 12.00,
    "uranium_ore": 15.00, "yellowcake": 100.00, "zirconium_rod": 40.00,
    "fuel_rod": 500.00, "control_rod": 200.00, "spent_fuel": -80.0,
    "contaminated_water": -1.5, "distilled_water": 2.00,
    "molten_purple_gold": 800.00, "molten_ferroaluminium": 150.00, "tetraethyllead": 80.00,
    "tire": 300.00, "tire_rim": 120.00,
}

RP_VALUES = {
    "coal":                  1.0,
    "raw_iron":              1.5,
    "liquid_iron":           2.5,
    "iron_ingot":            3.0,
    "iron_powder":           1.0,
    "iron_mix":              2.0,
    "steel":                 5.0,
    "iron_plate":            5,
    "iron_plate2":           8.0,
    "iron_coil":             4.0,
    "cut_oak_log":           1.0,
    "chunk_plank":           1.0,
    "planks":                2.0,
    "plank2":                3.0,
    "nails":                 2.0,
    "chair":                20.0,
    "crude_oil":             2.0,
    "poor_quality_diesel":   3.0,
    "diesel":                4.5,
    "refined_diesel":        6.0,
    "raw_copper":            1.0,
    "liquid_copper":         0.0,
    "copper_ingot":          3.0,
    "copper_powder":         1.0,
    "copper_mix":            2.0,
    "copper_plate":          6.0,
    "copper_wire":           3.0,
    "insulated_wire":        8.0,
    "steel_plate":           8,
    "steel_rod":             6.0,
    "gear":                  5.0,
    "steel_coil":            6.0,
    "crankshaft":           30.0,
    "gearbox":              50.0,
    "galvanized_steel":     10.0,
    "soil":                  0.0,
    "clay":                  1.0,
    "limestone":             1.0,
    "gravel":                1.0,
    "rawmix":                2.0,
    "aggregate":             1.0,
    "cement":                6.0,
    "water":                 0.0,
    "wet_concrete":          3.0,
    "concrete_block":        8.0,
    "reinforced_concrete":  12.0,
    "clay_bricks":           1.0,
    "brick":                 2.0,
    "oak_log":               1.0,
    "lithium_ore":           2.0,
    "lithium_brine":         3.0,
    "dirty_lithium_sulfate": 3.0,
    "lithium_sulfate":       5.0,
    "lithium_carbonate":     10,
    "lithium_ion_battery":  10.0,
    "charged_lithium_battery": 15.0,
    "rubber":                6,
    "graphite_electrode":    4.0,
    "lithium_battery_pack": 70,
    "sodium_carbonate":      8.0,
    "sand":                  0.0,
    "liquid_glass":          1.0,
    "glass":                 2.0,
    "silicon":               5,
    "semiconductor":        18,
    "logic_plate":          24,
    "gold_wire":             8.0,
    "machine_oil":           6,
    "coke_fuel":             2.0,
    "sulfuric_acid":         5.0,
    "hydrochloric_acid":     5.0,
    "filter":                4.0,
    "deep_earth_fragment":   2.0,
    "earth_fragment":        1.0,
    "microchip_2x":          5,
    "microchip_8x64x":     300.0,
    "drill_head":            6.0,
    "iron_drill_head":       4.0,
    "copper_drill_head":     6.0,
    "steel_drill_head":      8.0,
    "ferroaluminium_magnet":12.0,
    "ferroaluminium_alloy_ingot": 8.0,
    "electric_motor":       20.0,
    "electromagnet":         8.0,
    "black_dye":             2.0,
    "hydrogen":              1.0,
    "oxygen":                0.0,
    "steam":                 0.0,
    "naphtha":               2.0,
    "heavy_oil":             1.0,
    "light_oil":             1.0,
    "gasoline":              5.0,
    "leaded_gasoline":       6.0,
    "paper":                 2.0,
    "raw_lead":              1.0,
    "raw_zinc":              1.0,
    "lead_ingot":            3.0,
    "liquid_lead":           3.0,
    "boric_acid":            5.0,
    "molten_purple_gold":   60.0,
    "molten_ferroaluminium":10.0,
    "chlorine":              2.0,
    "sulfur":                3.0,
    "table_salt":            1.0,
    "tetraethyllead":        6.0,
    "karat_gold":            5.0,
    "bauxite_residue":       0.0,
    "purified_gold":        15.0,
    "liquid_gold":          20.0,
    "gold_ingot":           25.0,
    "purple_gold_ingot":    80.0,
    "crushed_bauxite":       1.0,
    "alumina":               3.0,
    "alumina_dust":          2.0,
    "liquid_aluminium":      5.0,
    "aluminium_ingot":       8.0,
    "uranium_ore":           5.0,
    "yellowcake":           15.0,
    "zirconium_rod":         8.0,
    "fuel_rod":             40.0,
    "control_rod":          10.0,
    "spent_fuel":            0.0,
    "contaminated_water":    0.0,
    "distilled_water":       1.0,
    "paraxylene":            4.0,
    "ethylene":              3.0,
    "ethanol":               3.0,
    "acetic_acid":           4.0,
    "pta":                   5.0,
    "meg":                   5.0,
    "plastic_pellets":      12,
    "plastic_casing":       10.0,
    "raw_gas":               1.0,
    "condensed_gas":         2.0,
    "refined_gas":           4.0,
    "lng":                   8.0,
    "tire":                 12.0,
    "tire_rim":              6.0,
}

POLLUTION_PER_MACHINE = {
    2: 0.00072, 8: 0.00105, 15: 0.00240,
    9: 0.00135, 10: 0.00036, 14: 0.00600,
    16: 0.00450, 18: 0.00060, 19: 0.00030, 20: 0.00036,
    11: 0.0, 24: 0.0, 25: 0.0, 26: 0.0, 27: 0.0, 28: 0.0,
    12: 0.00300, 17: 0.00390, 107: 0.00360,
    45: 0.00120, 49: 0.00600, 50: 0.00180,
    87: 0.00240, 96: 0.01500, 108: 0.00900, 116: 0.00180,
}

POLLUTION_INCOME_MAX_BONUS = 1.0
POLLUTION_INCOME_MIN_PENALTY = 0.1
POLLUTION_BONUS_DIVISOR = 20.0
POLLUTION_PENALTY_DIVISOR = 1000.0
POLLUTION_TINT_MAX_ALPHA = 45
POLLUTION_TINT_REFERENCE = 40.0

def get_pollution_income_multiplier(pollution):
    if pollution <= 0:
        return min(POLLUTION_INCOME_MAX_BONUS, 1.0 + (-pollution / POLLUTION_BONUS_DIVISOR))
    return max(POLLUTION_INCOME_MIN_PENALTY, 1.0 - (pollution / POLLUTION_PENALTY_DIVISOR))

REFINERY_RECIPES = {
    "crude_oil":           {"consume": 0.45, "produce": "poor_quality_diesel", "output": 0.41, "residue": 0.04},
    "poor_quality_diesel": {"consume": 0.41, "produce": "diesel", "output": 0.37, "residue": 0.04},
    "diesel":              {"consume": 0.37, "produce": "refined_diesel", "output": 0.34, "residue": 0.03},
}

DIESEL_GEN_OUTPUT = {
    "poor_quality_diesel": 55200,
    "diesel": 78000,
    "refined_diesel": 90000,
}

# ── CHECK FUNCTIONS ────────────────────────────────────────────────────────────
def _furnace_check(t):
    return (t.get("coal_buffer", 0) > 0 and t.get("input_buffer", 0) > 0 and (t.get("input_item") or "").startswith("raw_"))

def _molder_check(t):
    return (t.get("input_buffer", 0) >= 4 and t.get("input_item") in ("liquid_iron","liquid_copper","liquid_gold","liquid_aluminium", "liquid_glass","liquid_sulfur","liquid_lead","molten_ferroaluminium","molten_purple_gold"))

def _blast_check(t):
    return t.get("coal_buffer", 0) >= 4 and t.get("ingot_buffer", 0) >= 1

def _sawmill_check(t): return t.get("input_buffer", 0) >= 1
def _press_check(t): return t.get("input_buffer", 0) >= 1
def _roller_check(t): return t.get("input_buffer", 0) >= 2
def _grinder_check(t): return t.get("input_buffer", 0) >= 4

def _rawmill_check(t):
    return (t.get("gravel_buffer", 0) >= 1 and t.get("limestone_buffer", 0) >= 1 and t.get("clay_buffer", 0) >= 1)

def _indkiln_check(t):
    return (t.get("input_buffer", 0) >= 1 and t.get("coal_buffer", 0) >= 1 and (t.get("input_item") or "") == "rawmix")

def _concplant_check(t):
    mode = t.get("recipe_mode", "wet_concrete")
    if mode == "clay_bricks":
        return t.get("input_buffer", 0) >= 1 and (t.get("input_item") or "") == "clay"
    if mode == "concrete_block":
        return (t.get("input_buffer", 0) >= 1 and t.get("water_buffer", 0) >= 0.5 and (t.get("input_item") or "") == "wet_concrete")
    return (t.get("input_buffer", 0) >= 1 and t.get("aggregate_buffer", 0) >= 1 and t.get("water_buffer", 0) >= 0.5)

def _craftasm_check(t):
    mode = t.get("recipe_mode", "crankshaft")
    _CA_MODES = {
        "reinforced_concrete": [("concrete_block", 1), ("steel_rod", 1)],
        "crankshaft":    [("steel_rod", 2),       ("gear", 4)],
        "gearbox":       [("crankshaft", 1),       ("plastic_casing", 2)],
        "chair":         [("planks", 12),          ("nails", 20)],
        "semiconductor": [("silicon", 1),          ("copper_plate", 1)],
        "galvanized_steel": [("steel_plate", 2),   ("liquid_zinc", 1)],
        "tire":          [("tire_rim", 1),         ("rubber", 4)],
        "tire_rim":      [("aluminium_ingot", 2),  ("steel", 4)],
        "insulated_wire":[("rubber", 20),          ("copper_wire", 40)],
    }
    reqs = _CA_MODES.get(mode)
    if not reqs: return False
    (a_item, a_qty), (b_item, b_qty) = reqs
    return (t.get("input_buffer", 0) >= a_qty and (t.get("input_item") or "") == a_item
            and t.get("input2_buffer", 0) >= b_qty and (t.get("input2_item") or "") == b_item)

def _steamcrack_check(t):
    return (t.get("input_buffer", 0) >= 1 and t.get("water_buffer", 0) >= 0.5
            and (t.get("input_item") or "") == "crude_oil")

def _plasticref_check(t):
    mode = t.get("recipe_mode", "ethanol")
    if mode == "pta":
        return (t.get("input_buffer", 0) >= 1 and (t.get("input_item") or "") == "paraxylene"
                and t.get("input2_buffer", 0) >= 1)
    if mode == "leaded_gasoline":
        return (t.get("input_buffer", 0) >= 1 and (t.get("input_item") or "") == "gasoline"
                and t.get("input2_buffer", 0) >= 1 and (t.get("input2_item") or "") == "tetraethyllead")
    return (t.get("input_buffer", 0) >= 1 and (t.get("input_item") or "") == "crude_oil"
            and t.get("water_buffer", 0) >= 0.5)

def _oxidation_check(t):   return t.get("input_buffer", 0) >= 1
def _plasticfac_check(t):  return t.get("input_buffer", 0) >= 1 and t.get("input2_buffer", 0) >= 1
def _plasticmold_check(t): return t.get("input_buffer", 0) >= 10 and (t.get("input_item") or "") == "plastic_pellets"
def _gasburner_check(t):   return t.get("input_buffer", 0) >= 0.5
def _kiln_check(t):        return (t.get("input_buffer", 0) >= 1 and t.get("coal_buffer", 0) >= 1 and (t.get("input_item") or "") == "clay_bricks")
def _goldref_check(t):     return t.get("input_buffer", 0) >= 1 and t.get("input2_buffer", 0) >= 0.5
def _indfurnace_check(t):  return t.get("input_buffer", 0) >= 1
def _alloyer_check(t):
    mode = t.get("recipe_mode", "molten_purple_gold")
    if mode == "molten_ferroaluminium":
        return (t.get("input_buffer", 0) >= 2 and (t.get("input_item") or "") == "iron_ingot"
                and t.get("input2_buffer", 0) >= 2)
    return (t.get("input_buffer", 0) >= 1 and (t.get("input_item") or "") == "gold_ingot"
            and t.get("input2_buffer", 0) >= 2)
def _watertreat_check(t):  return t.get("input_buffer", 0) >= 1 and t.get("water_buffer", 0) >= 0.5
def _chemplant_check(t):
    mode = t.get("recipe_mode", "lithium_carbonate")
    if mode == "karat_gold":
        return t.get("input_buffer", 0) >= 1 and t.get("input2_buffer", 0) >= 0.5
    if mode in ("acetic_acid", "meg"):
        return t.get("input_buffer", 0) >= 1
    return t.get("input_buffer", 0) >= 1
def _chemreactor_check(t): return t.get("input_buffer", 0) >= 1 and t.get("input2_buffer", 0) >= 0.5
def _advassembler_check(t):
    mode = t.get("recipe_mode", "lithium_battery_pack")
    if mode == "lithium_battery_pack":
        return (t.get("input_buffer", 0) >= 8 and t.get("input2_buffer", 0) >= 8
                and t.get("input3_buffer", 0) >= 12)
    if mode == "gearbox":
        return t.get("input_buffer", 0) >= 1 and t.get("input2_buffer", 0) >= 2
    if mode == "crankshaft":
        return t.get("input_buffer", 0) >= 2 and t.get("input2_buffer", 0) >= 4
    if mode == "electric_motor":
        return (t.get("input_buffer", 0) >= 2 and t.get("input2_buffer", 0) >= 8
                and t.get("input3_buffer", 0) >= 4)
    if mode == "fuel_rod":
        return t.get("input_buffer", 0) >= 2 and t.get("input2_buffer", 0) >= 4
    if mode == "control_rod":
        return t.get("input_buffer", 0) >= 2 and t.get("input2_buffer", 0) >= 2
    if mode == "microchip_8x64x":
        return t.get("input_buffer", 0) >= 8 and t.get("input2_buffer", 0) >= 4
    if mode == "logic_plate":
        return t.get("input_buffer", 0) >= 1 and t.get("input2_buffer", 0) >= 1
    return False
def _elecfurnace_check(t): return t.get("input_buffer", 0) >= 1
def _indfirebox_check(t):  return t.get("input_buffer", 0) >= 1 and t.get("coal_buffer", 0) >= 1
def _foundry_check(t):
    return (t.get("coal_buffer", 0) >= 2 and t.get("input_buffer", 0) >= 4
            and (t.get("input_item") or "").startswith("raw_"))

MACHINE_DEFS = {
    # Drills
    2:  {"drill": True, "resource": "coal",              "mine_time": 2.0},   # 0.5/s
    8:  {"drill": True, "resource": "raw_iron",           "mine_time": 10.0},  # 0.1/s
    30: {"drill": True, "resource": "raw_copper",         "mine_time": 6.67},  # 0.15/s
    31: {"drill": True, "resources": ["soil","clay"],     "mine_time": 4.0},
    32: {"drill": True, "resources": ["limestone","clay","earth_fragment","sand"], "mine_time": 6.0},
    53: {"drill": True, "resource": "oak_log",            "mine_time": 8.0},
    59: {"drill": True, "resource": "lithium_ore",        "mine_time": 20.0},  # 0.05/s
    68: {"drill": True, "resources": ["deep_earth_fragment","raw_lead","raw_zinc","uranium_ore"],"mine_time": 10.0},
    # Fluid producers
    15: {"fluid_producer": True, "resource": "crude_oil",   "rate": 0.12, "push_amount": 0.45, "cap": 10.0,  "output_subtile": (1,0), "push_dir": (1,0)},
    36: {"fluid_producer": True, "resource": "water",       "rate": 0.5,  "push_amount": 0.45, "cap": 8.0,   "output_subtile": (1,1), "push_dir": (0,1)},
    45: {"fluid_producer": True, "resource": "raw_gas",     "rate": 0.15, "push_amount": 0.45, "cap": 10.0,  "output_subtile": (1,1), "push_dir": (0,1)},
    70: {"fluid_producer": True, "resource": "lithium_brine","rate": 0.3, "push_amount": 0.45, "cap": 12.0,  "output_subtile": (1,2), "push_dir": (0,1)},
    90: {"fluid_producer": True, "resource": "oxygen",      "rate": 0.4,  "push_amount": 0.45, "cap": 15.0,  "output_subtile": (1,2), "push_dir": (0,1)},
    # Special / non-process machines
    17: {"diesel_gen": True},
    21: {"scrubber": True},
    22: {"silo": True, "fluid": False},
    23: {"silo": True, "fluid": True},
    # depots
    83: {"depot": True, "input_ports": [{"items": [], "buf": "input_buffer","item_buf": "input_item", "subtile": (3, 0),"from_dir": (0, 1),"cap": 200}]},
    51: {"depot": True, "fluid_depot": True, "input_ports": [{"items": ["lng","diesel","refined_diesel","poor_quality_diesel","crude_oil","water", "liquid_iron","liquid_copper","liquid_gold","machine_oil","residue", "light_oil","heavy_oil","naphtha","gasoline","ethanol"], "buf": "input_buffer","item_buf": "input_item","subtile": (1,0),"from_dir": (0,1),"cap": 400.0}]},
    29: {"liquid_burner": True, "input_ports": [{"items": ["residue","poor_quality_diesel","diesel","refined_diesel","crude_oil", "light_oil","heavy_oil","naphtha"], "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 5.0}]},
    97: {"power_pole": True, "pole_range": 10, "pole_tier": "LV"},
    98: {"power_pole": True, "pole_range": 15, "pole_tier": "MV"},
    99: {"power_pole": True, "pole_range": 70, "pole_tier": "HV"},
    100: {"battery": True, "battery_tier": "MV"},
    101: {"battery": True, "battery_tier": "HV"},
    103: {"logic_gate": True, "gate_type": "NAND"},
    104: {"logic_gate": True, "gate_type": "NOR"},
    105: {"logic_gate": True, "gate_type": "NOT"},
    111: {"logic_gate": True, "gate_type": "AND"},
    112: {"logic_gate": True, "gate_type": "OR"},
    113: {"logic_gate": True, "gate_type": "XOR"},
    13:  {"research_station": True, "rs_tier": 1},
    114: {"research_station": True, "rs_tier": 2, "input_ports": [{"items": [], "buf": "input_buffer","item_buf": "input_item","subtile": (3,0),"from_dir": (0,1),"cap": 10.0}]},
    115: {"research_station": True, "rs_tier": 3, "input_ports": [ {"items": [], "buf": "input_buffer",  "item_buf": "input_item",  "subtile": (2,0),"from_dir": (0,1),"cap": 5.0}, {"items": [], "buf": "input2_buffer", "item_buf": "input2_item", "subtile": (5,0),"from_dir": (0,1),"cap": 5.0},]},
    110: {"exhaust_stack": True, "disperse_rate": 0.001},
    106: {"input_ports": [{"item": "steam","buf": "input_buffer","subtile": (1,0),"from_dir": (0,1),"cap": 10.0}], "steam_turbine": True, "steam_rate": 0.5},        # steam/s at full output
    107: {"input_ports": [{"item": "gasoline","buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 5.0}], "fuel_generator": True, "fuel_type": "gasoline", "fuel_rate": 0.1},
    102: {"input_ports": [{"items": ["water","machine_oil"],"buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 4.0}], "transformer": True},
    108: {"input_ports": [{"item": "coal",  "buf": "input_buffer","item_buf": "input_item","subtile": (3,0),"from_dir": (0,1),"cap": 40}, {"item": "water", "buf": "water_buffer", "subtile": (8,0),"from_dir": (0,1),"cap": 50.0}],
          "coal_power_plant": True, "coal_rate": 0.5, "water_rate": 1.0},
    96: {"input_ports": [
             {"item": "fuel_rod",        "buf": "input_buffer",   "item_buf": "input_item",  "subtile": (7,0),"from_dir": (0,1),"cap": 20},
             {"item": "distilled_water", "buf": "water_buffer",   "subtile": (0,0),"from_dir": (0,1),"cap": 100.0},
             {"item": "control_rod",     "buf": "control_buffer", "item_buf": "control_item","subtile": (15,0),"from_dir": (0,1),"cap": 20}],
         "output_port": {"subtile": (7,15),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 50},
         "process": {"time": 300.0,"needs_power": False,
                     "check": lambda t: (t.get("input_buffer",0)>=1 and t.get("water_buffer",0)>=10 and t.get("control_buffer",0)>=1),
                     "consume": {"input_buffer":1,"water_buffer":10,"control_buffer":1},
                     "produce": "spent_fuel","amount": 1},
         "nuclear": True, "power_while_processing": True},
    49: {"input_ports": [{"items": ["raw_gas","condensed_gas","refined_gas"],
                          "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 4.0}],
         "process": {"time": 2.0,"needs_power": False,"check": _gasburner_check,
                     "consume": {"input_buffer": 0.5}},
         "gas_burner": True},

    109: {
        "input_ports": [{"items": ["raw_iron","raw_copper","sand"],
                         "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 8}],
        "output_port":  {"subtile": (1,1),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 8},
        "process": {"time": 5.0,"needs_power": True,"check": _elecfurnace_check,
                    "consume": {"input_buffer": 1},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "raw_iron":   ("liquid_iron",   2),
                        "raw_copper": ("liquid_copper", 2),
                        "sand":       ("liquid_glass",  2),
                    }, "amount": 2},
    },

    9: {
        "input_ports": [
            {"items": ["raw_iron","raw_copper","raw_lead","raw_zinc"],
             "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 8},
            {"item": "coal","buf": "coal_buffer","subtile": (0,0),"from_dir": (0,1),"cap": 10},
            {"item": "coal","buf": "coal_buffer","subtile": (0,0),"from_dir": (1,0),"cap": 10},
        ],
        "output_port": {"subtile": (0,0),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 8},
        "process": {"time": 2.0,"needs_power": True,"check": _furnace_check,
                    "consume": {"input_buffer":1,"coal_buffer":1},"produce_fn": "furnace"},
    },

    10: {
        "input_ports": [{"items": ["liquid_iron","liquid_copper","liquid_gold","liquid_aluminium",
                                   "liquid_glass","liquid_sulfur","liquid_lead","molten_ferroaluminium","molten_purple_gold"],
                         "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 8}],
        "output_port": {"subtile": (0,0),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 8},
        "process": {"time": 4.0,"needs_power": True,"check": _molder_check,
                    "consume": {"input_buffer": 4},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "liquid_iron":          ("iron_ingot",             2),
                        "liquid_copper":        ("copper_ingot",           2),
                        "liquid_gold":          ("gold_ingot",             2),
                        "liquid_aluminium":     ("aluminium_ingot",        2),
                        "liquid_glass":         ("glass",                  2),
                        "liquid_sulfur":        ("sulfur",                 2),
                        "liquid_lead":          ("lead_ingot",             2),
                        "molten_ferroaluminium":("ferroaluminium_alloy_ingot",2),
                        "molten_purple_gold":   ("purple_gold_ingot",      1),
                    }, "amount": 2},
    },

    14: {
        "input_ports": [
            {"items": ["coal","coke_fuel"],"buf": "coal_buffer","subtile": (0,0),"from_dir": (0,1),"cap": 16},
            {"items": ["iron_ingot","iron_mix","crushed_bauxite","alumina_dust","oak_log"],
             "buf": "ingot_buffer","item_buf": "input_item","subtile": (2,0),"from_dir": (0,1),"cap": 4},
        ],
        "output_port": {"subtile": (2,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 8},
        "process": {"time": 5.0,"needs_power": True,"check": _blast_check,
                    "consume": {"coal_buffer":4,"ingot_buffer":1},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "iron_ingot":      ("steel",            2),
                        "iron_mix":        ("steel",            6),
                        "crushed_bauxite": ("alumina",          1),
                        "alumina_dust":    ("liquid_aluminium", 1),
                        "oak_log":         ("coke_fuel",        2),
                    }, "amount": 2},
    },


    116: {
        "input_ports": [
            {"items": ["oak_log","coal"],"buf": "input_buffer","item_buf": "input_item",
             "subtile": (0,0),"from_dir": (0,1),"cap": 8},
            {"items": ["coal","coke_fuel"],"buf": "coal_buffer",
             "subtile": (1,0),"from_dir": (0,1),"cap": 10},
        ],
        "output_port": {"subtile": (0,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 8.0,"needs_power": False,"check": _indfirebox_check,
                    "consume": {"input_buffer":1,"coal_buffer":1},
                    "produce_fn": "mode_recipes","default_mode": "coke_fuel",
                    "mode_recipes": {
                        "coke_fuel":        {"produce":"coke_fuel",       "amount":2,"extra_consume":{},"inputs":[("oak_log",1),("coal",1)]},
                        "sodium_carbonate": {"produce":"sodium_carbonate","amount":1,"extra_consume":{},"inputs":[("oak_log",1),("coal",1)]},
                    }},
    },

    117: {
        "input_ports": [{"item": "water","buf": "input_buffer","subtile": (0,0),"from_dir": (0,1),"cap": 10.0}],
        "output_port": {"subtile": (1,1),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 10.0},
        "process": {"time": 2.0,"needs_power": True,
                    "check": lambda t: t.get("input_buffer",0)>=0.5,
                    "consume": {"input_buffer":0.5},"produce": "steam","amount": 1},
    },

    18: {
        "input_ports": [{"items": ["iron_ingot","oak_log","cut_oak_log","chunk_plank"],
                         "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6.0}],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 12.0},
        "process": {"time": 20.0,"needs_power": True,"check": _sawmill_check,
                    "consume": {"input_buffer":1},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "iron_ingot":  ("iron_plate",  4),
                        "oak_log":     ("cut_oak_log", 2),
                        "cut_oak_log": ("chunk_plank", 1),
                        "chunk_plank": ("planks",      3),
                    }, "amount": 4},
    },


    19: {
        "input_ports": [{"items": ["copper_ingot","iron_ingot","steel","iron_plate","planks","steel_plate","paper"],
                         "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6.0}],
        "output_port": {"subtile": (1,1),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6.0},
        "process": {"time": 4.0,"needs_power": True,"check": _press_check,
                    "consume": {"input_buffer":1},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "copper_ingot": ("copper_plate", 1),
                        "iron_ingot":   ("iron_plate",   1),
                        "steel":        ("steel_plate",  1),
                        "iron_plate":   ("iron_plate2",  0.25),
                        "planks":       ("plank2",       0.25),
                        "paper":        ("filter",       1),
                        "steel_plate":  ("gear",         1),
                    }, "amount": 1},
    },

    20: {
        "input_ports": [{"items": ["iron_plate","copper_plate","steel","steel_plate","iron_ingot","gold_ingot",
                                   "aluminium_ingot","ferroaluminium_alloy_ingot","insulated_wire"],
                         "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 8.0}],
        "output_port": {"subtile": (1,1),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 12.0},
        "process": {"time": 8.0,"needs_power": True,"check": _roller_check,
                    "consume": {"input_buffer":2},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "iron_plate":                ("iron_coil",             4),
                        "copper_plate":              ("copper_wire",           12),
                        "steel":                     ("steel_rod",             2),
                        "steel_plate":               ("steel_coil",            4),
                        "iron_ingot":                ("nails",                 4),
                        "gold_ingot":                ("gold_wire",             2),
                        "aluminium_ingot":           ("ferroaluminium_magnet", 1),
                        "ferroaluminium_alloy_ingot":("ferroaluminium_magnet", 2),
                        "insulated_wire":            ("electromagnet",         1),
                    }, "amount": 4},
    },

    33: {
        "input_ports": [
            {"items": ["coal","raw_iron","raw_copper","soil","bauxite_residue","alumina","sand","oak_log","iron_ingot","copper_ingot"],
             "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6},
        ],
        "output_port": {"subtile": (1,1),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 8},
        "process": {"time": 12.0,"needs_power": True,"check": _grinder_check,
                    "consume": {"input_buffer":4},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "coal":            ("black_dye",      3),
                        "raw_iron":        ("iron_powder",    2),
                        "raw_copper":      ("copper_powder",  2),
                        "soil":            ("gravel",         1),
                        "bauxite_residue": ("crushed_bauxite",1),
                        "alumina":         ("alumina_dust",   1),
                        "sand":            ("silicon",        1),
                        "oak_log":         ("paper",          3),
                        "iron_ingot":      ("iron_mix",       1),
                        "copper_ingot":    ("copper_mix",     1),
                    }, "amount": 3},
    },


    34: {
        "input_ports": [
            {"item": "gravel",    "buf": "gravel_buffer",    "item_buf": "gravel_item",    "subtile": (0,0),"from_dir": (0,1),"cap": 6},
            {"item": "limestone", "buf": "limestone_buffer", "item_buf": "limestone_item", "subtile": (1,0),"from_dir": (0,1),"cap": 6},
            {"item": "clay",      "buf": "clay_buffer",      "item_buf": "clay_item",      "subtile": (2,0),"from_dir": (0,1),"cap": 6},
        ],
        "output_port":  {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer",    "item_buf": "output_item",    "cap": 6},
        "output_port2": {"subtile": (2,2),"push_dir": (0,1),"buf": "aggregate_buffer", "item_buf": "aggregate_item", "cap": 6},
        "process": {"time": 6.0,"needs_power": True,"check": _rawmill_check,
                    "consume": {"gravel_buffer":1,"limestone_buffer":1,"clay_buffer":1},
                    "produce_fn": "multi_output",
                    "outputs": [("output_buffer","output_item","rawmix",2),
                                ("aggregate_buffer","aggregate_item","aggregate",1)], "amount": 2},
    },

    35: {
        "input_ports": [
            {"items": ["rawmix"],"buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 8},
            {"items": ["coal","coke_fuel"],"buf": "coal_buffer","subtile": (3,0),"from_dir": (0,1),"cap": 10},
        ],
        "output_port": {"subtile": (2,5),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 8},
        "process": {"time": 10.0,"needs_power": True,"check": _indkiln_check,
                    "consume": {"input_buffer":1,"coal_buffer":1},"produce": "cement","amount": 1},
    },

    38: {
        "input_ports": [
            {"items": ["cement","wet_concrete","clay"],"buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6},
            {"item": "aggregate","buf": "aggregate_buffer","item_buf": "aggregate_item","subtile": (1,0),"from_dir": (0,1),"cap": 6},
            {"item": "water","buf": "water_buffer","subtile": (2,0),"from_dir": (0,1),"cap": 4.0},
        ],
        "output_port": {"subtile": (2,3),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 8.0,"needs_power": True,"check": _concplant_check,
                    "consume": {},
                    "produce_fn": "mode_recipes","default_mode": "wet_concrete",
                    "mode_recipes": {
                        "clay_bricks":   {"produce":"clay_bricks",   "amount":3,"extra_consume":{"input_buffer":1},                                          "inputs":[("clay",1)]},
                        "wet_concrete":  {"produce":"wet_concrete",  "amount":1,"extra_consume":{"input_buffer":1,"water_buffer":0.5,"aggregate_buffer":1},  "inputs":[("cement",1),("aggregate",1),("water",0.5)]},
                        "concrete_block":{"produce":"concrete_block","amount":1,"extra_consume":{"input_buffer":1,"water_buffer":0.5},                       "inputs":[("wet_concrete",1),("water",0.5)]},
                    }},
    },

    39: {
        "input_ports": [
            {"items": ["concrete_block","steel_rod","gear","crankshaft","plastic_casing","planks",
                       "silicon","tire_rim","rubber","aluminium_ingot","copper_wire","steel","steel_plate"],
             "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 40},
            {"items": ["steel_rod","gear","concrete_block","plastic_casing","crankshaft","nails",
                       "copper_plate","rubber","copper_wire","steel","liquid_zinc"],
             "buf": "input2_buffer","item_buf": "input2_item","subtile": (2,0),"from_dir": (0,1),"cap": 40},
        ],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 4},
        "process": {"time": 15.0,"needs_power": True,"check": _craftasm_check,
                    "consume": {},
                    "produce_fn": "mode_recipes","default_mode": "crankshaft",
                    "mode_recipes": {
                        "reinforced_concrete": {"produce":"reinforced_concrete","amount":1,"extra_consume":{"input_buffer":1,"input2_buffer":1},"inputs":[("concrete_block",1),("steel_rod",1)]},
                        "crankshaft":    {"produce":"crankshaft",   "amount":1,"extra_consume":{"input_buffer":2,"input2_buffer":4},"inputs":[("steel_rod",2),("gear",4)]},
                        "gearbox":       {"produce":"gearbox",      "amount":1,"extra_consume":{"input_buffer":1,"input2_buffer":2},"inputs":[("crankshaft",1),("plastic_casing",2)]},
                        "chair":         {"produce":"chair",        "amount":1,"extra_consume":{"input_buffer":12,"input2_buffer":20},"inputs":[("planks",12),("nails",20)]},
                        "semiconductor": {"produce":"semiconductor","amount":1,"extra_consume":{"input_buffer":1,"input2_buffer":1},"inputs":[("silicon",1),("copper_plate",1)]},
                        "galvanized_steel": {"produce":"galvanized_steel","amount":1,"extra_consume":{"input_buffer":2,"input2_buffer":1},"inputs":[("steel_plate",2),("liquid_zinc",1)]},
                        "tire":          {"produce":"tire",         "amount":1,"extra_consume":{"input_buffer":1,"input2_buffer":4},"inputs":[("tire_rim",1),("rubber",4)]},
                        "tire_rim":      {"produce":"tire_rim",     "amount":1,"extra_consume":{"input_buffer":2,"input2_buffer":4},"inputs":[("aluminium_ingot",2),("steel",4)]},
                        "insulated_wire":{"produce":"insulated_wire","amount":40,"extra_consume":{"input_buffer":20,"input2_buffer":40},"inputs":[("rubber",20),("copper_wire",40)]},
                    }},
    },

    61: {
        "input_ports": [
            {"items": ["charged_lithium_battery","steel_rod","gear","crankshaft","plastic_casing",
                       "silicon","copper_plate","rubber","ferroaluminium_magnet","yellowcake","boric_acid","microchip_2x","semiconductor"],
             "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 20},
            {"items": ["rubber","gear","plastic_casing","crankshaft","copper_wire","copper_plate","ferroaluminium_magnet","zirconium_rod","logic_plate"],
             "buf": "input2_buffer","item_buf": "input2_item","subtile": (1,0),"from_dir": (0,1),"cap": 20},
            {"items": ["copper_plate","graphite_electrode","nails","steel_rod","rubber"],
             "buf": "input3_buffer","item_buf": "input3_item","subtile": (3,0),"from_dir": (0,1),"cap": 20},
        ],
        "output_port": {"subtile": (2,3),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 4},
        "process": {"time": 10.0,"needs_power": True,"check": _advassembler_check,
                    "consume": {},
                    "produce_fn": "mode_recipes","default_mode": "lithium_battery_pack",
                    "mode_recipes": {
                        "lithium_battery_pack":{"produce":"lithium_battery_pack","amount":1,
                            "extra_consume":{"input_buffer":8,"input2_buffer":8,"input3_buffer":12},
                            "inputs":[("charged_lithium_battery",8),("rubber",8),("copper_plate",12)]},
                        "gearbox":             {"produce":"gearbox",             "amount":1,
                            "extra_consume":{"input_buffer":1,"input2_buffer":2},
                            "inputs":[("crankshaft",1),("plastic_casing",2)]},
                        "crankshaft":          {"produce":"crankshaft",          "amount":1,
                            "extra_consume":{"input_buffer":2,"input2_buffer":4},
                            "inputs":[("steel_rod",2),("gear",4)]},
                        "electric_motor":      {"produce":"electric_motor",      "amount":1,
                            "extra_consume":{"input_buffer":2,"input2_buffer":8,"input3_buffer":4},
                            "inputs":[("ferroaluminium_magnet",2),("copper_wire",8),("steel_rod",4)]},
                        "fuel_rod":            {"produce":"fuel_rod",            "amount":1,
                            "extra_consume":{"input_buffer":2,"input2_buffer":4},
                            "inputs":[("yellowcake",2),("zirconium_rod",4)]},
                        "control_rod":         {"produce":"control_rod",         "amount":1,
                            "extra_consume":{"input_buffer":2,"input2_buffer":2},
                            "inputs":[("boric_acid",2),("zirconium_rod",2)]},
                        "microchip_8x64x":     {"produce":"microchip_8x64x",     "amount":1,
                            "extra_consume":{"input_buffer":8,"input2_buffer":4},
                            "inputs":[("microchip_2x",8),("logic_plate",4)]},
                        "logic_plate":         {"produce":"logic_plate",         "amount":1,
                            "extra_consume":{"input_buffer":1,"input2_buffer":1},
                            "inputs":[("semiconductor",1),("copper_plate",1)]},
                    }},
    },

    79: {
        "input_ports": [
            {"item": "logic_plate",   "buf": "input_buffer",  "item_buf": "input_item",  "subtile": (0,0),"from_dir": (0,1),"cap": 6},
            {"item": "semiconductor", "buf": "input3_buffer", "item_buf": "input3_item", "subtile": (1,0),"from_dir": (0,1),"cap": 8},
            {"item": "gold_wire",     "buf": "input4_buffer", "item_buf": "input4_item", "subtile": (2,0),"from_dir": (0,1),"cap": 6},
        ],
        "output_port": {"subtile": (1,3),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 4},
        "process": {"time": 10.0,"needs_power": True,
                    "check": lambda t: (t.get("input_buffer",0)>=2 and t.get("input3_buffer",0)>=4
                                        and t.get("input4_buffer",0)>=2),
                    "consume": {"input_buffer":2,"input3_buffer":4,"input4_buffer":2},
                    "produce": "microchip_2x","amount": 1},
    },


    50: {
        "input_ports": [
            {"item": "clay_bricks","buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 8},
            {"items": ["coal","coke_fuel"],"buf": "coal_buffer","subtile": (1,0),"from_dir": (0,1),"cap": 10},
        ],
        "output_port": {"subtile": (0,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 8},
        "process": {"time": 5.0,"needs_power": True,"check": _kiln_check,
                    "consume": {"input_buffer":1,"coal_buffer":1},"produce": "brick","amount": 1},
    },


    55: {
        "input_ports": [
            {"item": "karat_gold","buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6},
            {"item": "acetic_acid","buf": "input2_buffer","item_buf": "input2_item","subtile": (2,0),"from_dir": (0,1),"cap": 4.0},
        ],
        "output_port":  {"subtile": (1,3),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "output_port2": {"subtile": (2,3),"push_dir": (0,1),"buf": "residue_buffer","item_buf": "residue_item","cap": 6},
        "process": {"time": 10.0,"needs_power": True,"check": _goldref_check,
                    "consume": {"input_buffer":1,"input2_buffer":0.5},
                    "produce_fn": "multi_output",
                    "outputs": [("output_buffer","output_item","purified_gold",1),
                                ("residue_buffer","residue_item","bauxite_residue",1)], "amount": 1},
    },


    57: {
        "input_ports": [{"items": ["purified_gold","karat_gold"],
                         "buf": "input_buffer","item_buf": "input_item","subtile": (1,0),"from_dir": (0,1),"cap": 4}],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 4},
        "process": {"time": 5.0,"needs_power": True,"check": _indfurnace_check,
                    "consume": {"input_buffer":1},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "purified_gold": ("liquid_gold", 1),
                        "karat_gold":    ("liquid_gold", 0.4),
                    }, "amount": 1},
    },

    58: {
        "input_ports": [
            {"items": ["gold_ingot","iron_ingot"], "buf": "input_buffer", "item_buf": "input_item", "subtile": (0,0),"from_dir": (0,1),"cap": 8},
            {"item": "aluminium_ingot", "buf": "input2_buffer","item_buf": "input2_item","subtile": (2,0),"from_dir": (0,1),"cap": 8},
        ],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 4},
        "process": {"time": 15.0,"needs_power": True,"check": _alloyer_check,
                    "consume": {"input2_buffer":2},
                    "produce_fn": "mode_recipes","default_mode": "molten_purple_gold",
                    "mode_recipes": {
                        "molten_purple_gold":   {"produce":"molten_purple_gold",  "amount":1,"extra_consume":{"input_buffer":1},"inputs":[("gold_ingot",1),("aluminium_ingot",2)]},
                        "molten_ferroaluminium":{"produce":"molten_ferroaluminium","amount":1,"extra_consume":{"input_buffer":2},"inputs":[("iron_ingot",2),("aluminium_ingot",2)]},
                    }},
    },

    60: {
        "input_ports": [
            {"items": ["crude_oil","lithium_ore","uranium_ore","heavy_oil","light_oil","sulfur","lead_ingot","liquid_sulfur"],"buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6},
            {"item": "water","buf": "input2_buffer","item_buf": "input2_item","subtile": (2,0),"from_dir": (0,1),"cap": 4.0},
        ],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 6.0,"needs_power": True,"check": _chemreactor_check,
                    "consume": {"input_buffer":1,"input2_buffer":0.5},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "crude_oil":   ("rubber",                 2),
                        "lithium_ore": ("dirty_lithium_sulfate",  1),
                        "uranium_ore": ("yellowcake",             1),
                        "heavy_oil":   ("liquid_sulfur",          1),
                        "light_oil":   ("naphtha",                2),
                        "sulfur":      ("boric_acid",             1),
                        "lead_ingot":  ("tetraethyllead",         1),
                        "liquid_sulfur":("sulfuric_acid",         1),
                    }, "amount": 2},
    },



    64: {
        "input_ports": [
            {"items": ["lithium_ore","dirty_lithium_sulfate","water"],"buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6},
            {"item": "water","buf": "water_buffer","subtile": (2,0),"from_dir": (0,1),"cap": 4.0},
        ],
        "output_port": {"subtile": (1,3),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 6.0,"needs_power": True,"check": _watertreat_check,
                    "consume": {"input_buffer":1,"water_buffer":0.5},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "lithium_ore":           ("lithium_sulfate", 1),
                        "dirty_lithium_sulfate": ("lithium_sulfate", 1),
                        "water":                 ("table_salt",      1),
                    }, "amount": 1},
    },

    65: {
        "input_ports": [
            {"items": ["lithium_sulfate","lithium_carbonate","table_salt","earth_fragment","ethanol","ethylene"],
             "buf": "input_buffer","item_buf": "input_item","subtile": (1,0),"from_dir": (0,1),"cap": 6},
            {"items": ["acetic_acid"],
             "buf": "input2_buffer","item_buf": "input2_item","subtile": (2,0),"from_dir": (0,1),"cap": 4.0},
        ],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 5.0,"needs_power": True,"check": _chemplant_check,
                    "consume": {"input_buffer":1},
                    "produce_fn": "mode_recipes","default_mode": "lithium_carbonate",
                    "mode_recipes": {
                        "lithium_carbonate": {"produce":"lithium_carbonate",   "amount":1,"extra_consume":{},"inputs":[("lithium_sulfate",1)]},
                        "lithium_ion_battery":{"produce":"lithium_ion_battery","amount":1,"extra_consume":{},"inputs":[("lithium_carbonate",1)]},
                        "chlorine":          {"produce":"chlorine",            "amount":2,"extra_consume":{},"inputs":[("table_salt",1)]},
                        "karat_gold":        {"produce":"karat_gold",          "amount":1,"extra_consume":{"input2_buffer":0.5},"inputs":[("earth_fragment",1),("acetic_acid",0.5)]},
                        "acetic_acid":       {"produce":"acetic_acid",         "amount":1,"extra_consume":{},"inputs":[("ethanol",1)]},
                        "meg":               {"produce":"meg",                 "amount":1,"extra_consume":{},"inputs":[("ethylene",1)]},
                    }},
    },

    16: {
        "input_ports": [{"items": ["crude_oil","poor_quality_diesel","diesel"],
                         "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 5.0}],
        "output_port":  {"subtile": (0,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 2.0},
        "output_port2": {"subtile": (0,2),"push_dir": (-1,0),"buf": "residue_buffer","item_buf": "residue_item","cap": 2.0},
        "process": {"time": 1.0,"needs_power": True,"produce_fn": "refinery"},
    },

    46: {
        "input_ports": [{"items": ["raw_gas","refined_gas"],"buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6}],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 4.0,"needs_power": True,
                    "check": lambda t: t.get("input_buffer",0)>=1 and (t.get("input_item") or "") in ("raw_gas","refined_gas"),
                    "consume": {"input_buffer":1},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "raw_gas":    ("condensed_gas", 1),
                        "refined_gas":("lng",           1),
                    }, "amount": 1},
    },
    47: {
        "input_ports": [{"items": ["condensed_gas","crude_oil"],"buf": "input_buffer","item_buf": "input_item","subtile": (1,0),"from_dir": (0,1),"cap": 6}],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 6.0,"needs_power": True,
                    "check": lambda t: t.get("input_buffer",0)>=1 and (t.get("input_item") or "") in ("condensed_gas","crude_oil"),
                    "consume": {"input_buffer":1},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "condensed_gas":   ("refined_gas",       1),
                        "crude_oil":       ("graphite_electrode",2),
                    }, "amount": 1},
    },

    40: {
        "input_ports": [
            {"item": "crude_oil","buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6},
            {"item": "water","buf": "water_buffer","subtile": (3,0),"from_dir": (0,1),"cap": 4.0},
        ],
        "output_port":  {"subtile": (1,5),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "output_port2": {"subtile": (2,5),"push_dir": (0,1),"buf": "ethylene_buffer","item_buf": "ethylene_item","cap": 6},
        "process": {"time": 10.0,"needs_power": True,"check": _steamcrack_check,
                    "consume": {"input_buffer":1,"water_buffer":0.5},
                    "produce_fn": "multi_output",
                    "outputs": [("output_buffer","output_item","paraxylene",1),
                                ("ethylene_buffer","ethylene_item","ethylene",1)], "amount": 1},
    },

    41: {
        "input_ports": [
            {"items": ["crude_oil","paraxylene","gasoline"],"buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6},
            {"items": ["acetic_acid","tetraethyllead"],"buf": "input2_buffer","item_buf": "input2_item","subtile": (2,0),"from_dir": (0,1),"cap": 6},
            {"item": "water","buf": "water_buffer","subtile": (1,0),"from_dir": (0,1),"cap": 4.0},
        ],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 5.0,"needs_power": True,"check": _plasticref_check,
                    "consume": {"input_buffer":1},
                    "produce_fn": "mode_recipes","default_mode": "ethanol",
                    "mode_recipes": {
                        "ethanol": {"produce":"ethanol","amount":1,"extra_consume":{"water_buffer":0.5},"inputs":[("crude_oil",1),("water",0.5)]},
                        "pta":     {"produce":"pta",    "amount":1,"extra_consume":{"input2_buffer":1},"inputs":[("paraxylene",1),("acetic_acid",1)]},
                        "leaded_gasoline": {"produce":"leaded_gasoline","amount":1,"extra_consume":{"input2_buffer":1},"inputs":[("gasoline",1),("tetraethyllead",1)]},
                    }},
    },


    43: {
        "input_ports": [
            {"item": "pta","buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6},
            {"item": "meg","buf": "input2_buffer","item_buf": "input2_item","subtile": (3,0),"from_dir": (0,1),"cap": 6},
        ],
        "output_port": {"subtile": (1,3),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 100},
        "process": {"time": 7.0,"needs_power": True,"check": _plasticfac_check,
                    "consume": {"input_buffer":1,"input2_buffer":1},"produce": "plastic_pellets","amount": 80},
    },

    44: {
        "input_ports": [{"item": "plastic_pellets","buf": "input_buffer","item_buf": "input_item","subtile": (1,0),"from_dir": (0,1),"cap": 40}],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 3.0,"needs_power": True,"check": _plasticmold_check,
                    "consume": {"input_buffer":10},"produce": "plastic_casing","amount": 1},
    },

    92: {
        "input_ports": [{"item": "plastic_pellets","buf": "input_buffer","item_buf": "input_item","subtile": (1,0),"from_dir": (0,1),"cap": 100}],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 20},
        "process": {"time": 1.5,"needs_power": True,
                    "check": lambda t: t.get("input_buffer",0)>=10 and (t.get("input_item") or "")=="plastic_pellets",
                    "consume": {"input_buffer":10},"produce": "plastic_casing","amount": 2},
    },


    89: {
        "input_ports": [{"items": ["crude_oil","water"],"buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6}],
        "output_port":  {"subtile": (0,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 4.0,"needs_power": True,
                    "check": lambda t: t.get("input_buffer",0)>=1,
                    "consume": {"input_buffer":1},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "crude_oil": ("gasoline", 1),
                        "water":     ("steam",    1),
                    }, "amount": 1},
    },

    87: {
        "input_ports": [
            {"item": "coal","buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 10},
            {"item": "water","buf": "water_buffer","subtile": (3,0),"from_dir": (0,1),"cap": 8.0},
        ],
        "output_port":  {"subtile": (1,5),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 8},
        "output_port2": {"subtile": (2,5),"push_dir": (0,1),"buf": "heavy_buffer","item_buf": "heavy_item","cap": 8},
        "process": {"time": 8.0,"needs_power": True,
                    "check": lambda t: t.get("input_buffer",0)>=2 and t.get("water_buffer",0)>=1,
                    "consume": {"input_buffer":2,"water_buffer":1.0},
                    "produce_fn": "multi_output",
                    "outputs": [("output_buffer","output_item","light_oil",1),
                                ("heavy_buffer","heavy_item","heavy_oil",1)], "amount": 1},
    },


    81: {
        "input_ports": [{"items": ["water","distilled_water","lithium_ion_battery"],"buf": "input_buffer","item_buf": "input_item","subtile": (1,0),"from_dir": (0,1),"cap": 8.0}],
        "output_port":  {"subtile": (0,3),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 6},
        "process": {"time": 4.0,"needs_power": True,
                    "check": lambda t: t.get("input_buffer",0)>=1,
                    "consume": {"input_buffer":1},
                    "produce_fn": "recipe_map",
                    "recipe_map": {
                        "water":               ("hydrochloric_acid",      1),
                        "distilled_water":     ("hydrogen",               2),
                        "lithium_ion_battery": ("charged_lithium_battery",1),
                    }, "amount": 1},
    },

    82: {
        "input_ports": [
            {"items": ["refined_diesel","contaminated_water","water","spent_fuel","purified_gold"],
             "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 4.0},
            {"items": ["water"],
             "buf": "water_buffer","subtile": (1,0),"from_dir": (0,1),"cap": 4.0},
        ],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 4.0},
        "process": {"time": 3.0,"needs_power": True,
                    "check": lambda t: t.get("input_buffer",0)>=1,
                    "consume": {"input_buffer":1},"produce_fn": "recipe_map",
                    "recipe_map": {
                        "refined_diesel":     ("machine_oil",       0.6),
                        "contaminated_water": ("distilled_water",   1.0),
                        "water":              ("distilled_water",   1.0),
                        "spent_fuel":         ("contaminated_water",1.0),
                        "purified_gold":      ("liquid_gold",       1.0),
                    }, "amount": 1},
    },

    91: {
        "input_ports": [{"items": ["gasoline","machine_oil","sulfuric_acid","hydrochloric_acid","water"],
                         "buf": "input_buffer","item_buf": "input_item","subtile": (1,0),"from_dir": (0,1),"cap": 10.0}],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 10},
        "process": {"time": 3.0,"needs_power": True,
                    "check": lambda t: t.get("input_buffer",0)>=1,
                    "consume": {"input_buffer":1},"produce_fn": "recipe_map",
                    "recipe_map": {
                        "gasoline":         ("gasoline",         1),
                        "machine_oil":      ("machine_oil",      1),
                        "sulfuric_acid":    ("sulfuric_acid",    1),
                        "hydrochloric_acid":("hydrochloric_acid",1),
                        "water":            ("water",            1),
                    }, "amount": 1},
    },

    93: {
        "input_ports": [
            {"item": "oak_log","buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 6},
            {"item": "water","buf": "water_buffer","subtile": (2,0),"from_dir": (0,1),"cap": 4.0},
        ],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 8},
        "process": {"time": 5.0,"needs_power": True,
                    "check": lambda t: t.get("input_buffer",0)>=1 and t.get("water_buffer",0)>=0.5,
                    "consume": {"input_buffer":1,"water_buffer":0.5},"produce": "paper","amount": 4},
    },

    77: {
        "input_ports": [{"items": ["steel","steel_rod","iron_ingot","copper_ingot","aluminium_ingot"],
                         "buf": "input_buffer","item_buf": "input_item","subtile": (0,0),"from_dir": (0,1),"cap": 4}],
        "output_port": {"subtile": (1,2),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 4},
        "process": {"time": 8.0,"needs_power": True,"check": _press_check,
                    "consume": {"input_buffer":1},"produce_fn": "recipe_map",
                    "recipe_map": {
                        "steel":           ("steel_drill_head",  1),
                        "steel_rod":       ("drill_head",        1),
                        "iron_ingot":      ("iron_drill_head",   1),
                        "copper_ingot":    ("copper_drill_head", 1),
                        "aluminium_ingot": ("zirconium_rod",     1),
                    }, "amount": 1},
    },

    78: {
        "input_ports": [
            {"items": ["raw_iron","raw_copper","raw_lead","raw_zinc"],"buf": "input_buffer","item_buf": "input_item","subtile": (1,0),"from_dir": (0,1),"cap": 20},
            {"items": ["coal","coke_fuel"],"buf": "coal_buffer","subtile": (4,0),"from_dir": (0,1),"cap": 20},
        ],
        "output_port": {"subtile": (2,5),"push_dir": (0,1),"buf": "output_buffer","item_buf": "output_item","cap": 20},
        "process": {"time": 4.0,"needs_power": True,"check": _foundry_check,
                    "consume": {"input_buffer":4,"coal_buffer":2},
                    "produce_fn": "furnace","amount": 4},
    },
}

BUILD_CATEGORIES = [
    ("Power",      [11, 24, 25, 26, 27, 28, 12, 17, 106, 107, 108, 96, 97, 98, 99, 100, 101, 102, 117, 118]),
    ("Logistics",  [1, 4, 5, 6, 7, 131,
                    119, 120, 121, 122, 123, 124,
                    125, 126, 127, 128, 129, 130]),
    ("Extractors", [2, 8, 30, 31, 32, 36, 45, 53, 59, 68, 70, 90, 15]),
    ("Processing", [109, 9, 10, 14, 78, 116, # smelters / furnaces
                    18, 19, 20, # forming
                    33, 34, 35, 38, 50, # grind/mill/kiln/concrete
                    39, 61, 79, # assembly
                    16, 29, 40, 41, 43, 44, 92, # plastics/refinery
                    46, 47, 49, 87, 89, # gas/oil
                    55, 57, 58, 60, 64, 65, # gold/lithium/chem
                    77, 81, 82, 91, 93]), # misc processors
    ("Storage",    [3, 83, 51, 22, 23]),
    ("Utility",    [13, 114, 115, 21, 110]),
    ("Logic",      [103, 104, 105, 111, 112, 113]),
]

TOOLBAR_H = 62
LB_W = 42
LB_H = 42

CONTRACTS_BUTTON_Y = 75
CONTRACTS_BUTTON_HEIGHT = 40

STARTING_MACHINES = [0, 1, 2, 3, 11, 13, 4, 5, 6, 7]

CHEAT_CODES = {
    "ryan": {"unlocks": [118], "message": "Dev power unlocked: Infinite Generator"},
}
CHEAT_FILE = "data/cheats.json"

CONTRACTS = [
    {"id": "efficiency_test","name": "The Efficiency Test","description": "Deliver 30 coal",
     "requirements": {"coal": 30},"rewards": {"money": 500,"rp": 5},"tier": 1},
    {"id": "rush_order","name": "Rush Order","description": "Deliver 500 coal within 5 minutes",
     "requirements": {"coal": 500},"rewards": {"money": 300,"rp": 8},"tier": 1,"time_limit": 300},
    {"id": "quality_over_quantity","name": "Quality Over Quantity","description": "Deliver 15 coal without depot overflow",
     "requirements": {"coal": 15},"no_overflow": True,"rewards": {"money": 400,"rp": 6},"tier": 1},
    {"id": "bootstrap_bargain","name": "Bootstrap Bargain","description": "Deliver 40 coal in 2 minutes, spend max $300",
     "requirements": {"coal": 40},"max_spending": 300,"rewards": {"money": 200,"rp": 4},"tier": 1,"time_limit": 120},
    {"id": "dual_supply","name": "Dual Supply Chain","description": "Deliver 20 coal and 20 iron ore",
     "requirements": {"coal": 20,"raw_iron": 20},"rewards": {"money": 800,"rp": 15},"tier": 2},
    {"id": "bottleneck_challenge","name": "The Bottleneck Challenge","description": "Deliver 100 iron ore using only 3 pipes total",
     "requirements": {"raw_iron": 100},"max_pipes": 3,"rewards": {"money": 600,"rp": 12},"tier": 2},
    {"id": "liquid_assets","name": "Liquid Assets","description": "Deliver 25 liquid iron while maintaining 3+ furnaces",
     "requirements": {"liquid_iron": 25},"min_furnaces": 3,"rewards": {"money": 1200,"rp": 25},"tier": 3},
    {"id": "the_perfectionist","name": "The Perfectionist","description": "Deliver 20 iron ingots with 100% uptime",
     "requirements": {"iron_ingot": 20},"max_idle_time": 10,"rewards": {"money": 2000,"rp": 40},"tier": 4},
    {"id": "industrial_titan","name": "Industrial Titan","description": "Deliver 1,000 iron ingots total",
     "requirements": {"iron_ingot": 1000},"rewards": {"money": 50000,"rp": 200},"tier": 6,"is_final": True},
]

STORY_MILESTONES = [
    {
        "capital": 10000,
        "message": (
            "[SYSTEM LOG: CORE_BOOT]\n"
            "Local grids are online. The automated coal loops are humming steadily.\n"
            "Small trade groups have noticed your minor output footprint. Keep drilling."
        ),
    },
    {
        "capital": 75000,
        "message": (
            "[FINANCIAL WIRE: MARKET_ALERT]\n"
            "Your metallurgical casting arrays have successfully bypassed local suppliers.\n"
            "Heavy fabrication industries are listing your firm as a primary provider of cast ingots."
        ),
    },
    {
        "capital": 350000,
        "message": (
            "[CORPORATE DOSSIER: COMPETITIVE_INTELLIGENCE]\n"
            "Regional legacy operators are acknowledging your structural steel output.\n"
            "Automated processing pipelines have eliminated overhead by 41%. Investors are buying in."
        ),
    },
    {
        "capital": 1500000,
        "message": (
            "[REGULATORY NOTICE: RESOURCE_HEGEMONY]\n"
            "The Department of Energy has classified your petrochemical drilling complexes as critical assets.\n"
            "You are setting the baseline pricing for polymers across the continental market."
        ),
    },
    {
        "capital": 8000000,
        "message": (
            "[BOARD DIRECTIVE: ORBITAL_PROJECTION]\n"
            "Your solid-state semiconductor and lithium-ion battery integration networks are operational.\n"
            "You have achieved total supply chain dominance. Legacy competitors are filing for liquidation."
        ),
    },
    {
        "capital": 50000000,
        "message": (
            "[SINGULARITY PROTOCOL: TITAN_ASCENSION]\n"
            "The cybernetic automation expansion is absolute. Human staff are obsolete.\n"
            "The factory has evolved from a commercial enterprise into a unified self-sustaining planetary entity."
        ),
        "is_victory": True,
    },
]