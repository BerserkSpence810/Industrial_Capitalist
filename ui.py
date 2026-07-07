from settings import *
from settings import MACHINE_DEFS
import pygame
import time as _time_module
import math as _math

MACHINE_THEMES = {
    11: ((55,52,20),(78,72,28),(200,165,40),(255,210,60),(255,220,80)),
    12: ((38,38,50),(55,55,72),(90,90,120),(140,140,180),(180,180,220)),
    13: ((50,38,68),(72,55,98),(110,78,180),(160,115,240),(200,155,255)),
    14: ((55,45,18),(78,64,26),(200,155,40),(255,195,60),(255,210,90)),
    1:  ((22,42,65),(32,60,95),(45,100,170),(70,150,255),(100,180,255)),
    4:  ((22,42,65),(32,60,95),(45,100,170),(70,150,255),(100,180,255)),
    5:  ((22,42,65),(32,60,95),(45,100,170),(70,150,255),(100,180,255)),
    6:  ((55,45,18),(78,64,26),(200,155,40),(255,195,60),(255,210,90)),
    7:  ((55,22,45),(78,32,65),(190,70,160),(240,100,210),(255,130,230)),
    2:  ((48,32,18),(68,46,26),(160,100,45),(210,140,65),(240,170,80)),
    8:  ((38,42,42),(55,60,60),(100,130,130),(145,185,185),(170,215,215)),
    9:  ((55,28,18),(78,40,26),(210,80,45),(255,110,65),(255,140,90)),
    10: ((38,38,50),(55,55,72),(120,120,170),(170,170,220),(200,200,240)),
    3:  ((22,55,28),(32,78,40),(55,170,75),(80,225,105),(110,255,135)),
    15: ((18,22,28),(28,32,42),(42,58,78),(60,88,118),(85,125,165)),
    16: ((28,18,36),(42,28,52),(78,48,105),(118,72,158),(155,95,210)),
    17: ((48,40,12),(68,58,18),(140,115,28),(195,165,38),(245,215,60)),
    18: ((28,22,14),(46,36,22),(110,72,32),(165,108,48),(210,145,70)),
    19: ((28,30,38),(42,46,58),(72,85,112),(108,128,168),(150,175,215)),
    20: ((24,28,32),(38,44,50),(68,80,90),(102,120,135),(145,168,185)),
    21: ((12,38,42),(20,68,72),(40,138,150),(80,200,210),(140,240,245)),
    22: ((40,30,15),(70,52,28),(135,105,60),(190,150,90),(230,195,140)),
    23: ((15,28,42),(28,48,72),(60,95,135),(95,140,190),(140,190,235)),
    24: ((55,52,20),(80,75,30),(220,180,45),(255,225,65),(255,235,90)),
    25: ((60,55,25),(90,82,35),(235,200,55),(255,235,80),(255,245,110)),
    26: ((40,50,55),(70,82,90),(150,170,180),(200,220,230),(235,245,250)),
    27: ((45,55,60),(78,90,98),(170,190,200),(215,230,240),(245,250,255)),
    28: ((50,60,65),(85,98,108),(185,205,215),(225,240,248),(255,255,255)),
    29: ((50,18,10),(78,32,18),(180,60,30),(235,100,50),(255,150,90)),
    30: ((50,22,8),(85,42,18),(195,105,55),(240,155,90),(255,195,140)),
    31: ((40,28,15),(68,48,28),(130,95,55),(175,140,90),(220,190,140)),
    32: ((55,50,42),(95,88,75),(155,145,125),(200,190,170),(235,228,210)),
    33: ((22,24,30),(40,44,52),(75,80,90),(135,142,158),(190,200,215)),
    34: ((35,30,20),(65,58,40),(105,95,70),(160,148,110),(210,195,155)),
    35: ((55,22,10),(95,40,20),(180,90,45),(230,140,75),(255,190,120)),
    36: ((15,28,40),(40,68,95),(90,130,175),(140,185,225),(195,225,250)),
    37: ((10,32,48),(28,82,115),(60,165,210),(120,210,245),(190,235,255)),
    38: ((42,40,36),(82,78,72),(145,140,130),(195,190,180),(230,225,215)),
    39: ((25,35,22),(52,72,45),(95,125,85),(145,175,130),(195,220,180)),
    40: ((40,15,25),(85,32,52),(165,75,105),(210,120,155),(240,175,205)),
    41: ((30,20,40),(60,42,85),(125,85,155),(175,135,210),(220,185,245)),
    42: ((18,35,25),(40,78,58),(85,155,120),(135,200,170),(190,235,215)),
    43: ((50,40,15),(105,85,30),(210,175,75),(240,215,130),(255,240,180)),
    44: ((40,28,20),(85,62,45),(175,125,95),(215,175,140),(245,215,190)),
    45: ((18,25,38),(35,52,75),(70,95,130),(115,148,185),(170,200,230)),
    46: ((12,30,38),(28,62,78),(55,115,140),(105,170,195),(160,210,230)),
    47: ((22,28,42),(48,58,82),(90,110,150),(140,165,200),(190,210,240)),
    48: ((8,22,42),(20,52,88),(40,100,160),(80,150,210),(140,200,245)),
    49: ((48,25,8),(95,52,18),(180,100,40),(225,150,75),(255,200,120)),
    50: ((48,30,15),(95,62,35),(185,125,70),(225,170,110),(255,210,155)),
    51: ((15,22,32),(32,48,68),(65,90,120),(110,140,170),(165,195,225)),
    52: ((55,30,12),(110,65,28),(215,130,65),(245,175,100),(255,215,150)),
    53: ((15,35,12),(32,72,28),(65,130,55),(110,180,95),(165,225,150)),
    54: ((38,32,20),(75,62,42),(140,120,85),(190,168,125),(230,210,170)),
    55: ((50,42,10),(95,78,22),(180,150,50),(225,195,80),(255,235,130)),
    56: ((22,35,48),(48,75,98),(100,140,170),(150,190,215),(200,230,245)),
    57: ((45,20,8),(90,42,18),(165,80,40),(215,125,70),(250,175,110)),
    58: ((38,30,48),(78,62,98),(155,130,180),(200,175,225),(235,215,250)),
    59: ((25,55,48),(55,110,95),(120,200,180),(170,230,215),(210,248,238)),
    60: ((35,40,22),(72,80,48),(140,155,100),(185,200,145),(225,235,190)),
    61: ((25,18,38),(52,40,78),(100,80,140),(150,128,190),(200,180,235)),
    62: ((55,50,12),(110,98,28),(200,180,60),(235,218,100),(255,245,160)),
    63: ((28,22,35),(58,48,72),(110,95,130),(160,145,180),(210,195,230)),
    64: ((18,32,42),(42,72,88),(80,130,155),(130,182,205),(185,222,240)),
    65: ((38,42,22),(78,85,48),(145,155,100),(195,205,150),(232,238,200)),
    66: ((30,25,15),(62,52,32),(100,80,50),(150,125,85),(200,175,130)),
    67: ((32,36,38),(65,72,78),(120,135,140),(175,188,195),(220,230,235)),
    68: ((22,20,16),(48,42,35),(85,75,65),(130,118,105),(180,168,155)),
    69: ((10,12,16),(22,28,38),(40,45,55),(72,80,95),(120,130,148)),
    70: ((25,45,32),(55,95,68),(100,165,130),(150,210,178),(200,240,220)),
    71: ((45,28,10),(92,60,25),(170,115,50),(218,162,80),(248,205,125)),
    72: ((38,40,45),(78,82,90),(140,145,155),(195,200,210),(235,238,245)),
    73: ((35,38,42),(72,76,82),(135,140,150),(190,195,205),(230,234,242)),
    74: ((24,26,30),(50,54,60),(90,95,105),(142,148,162),(198,204,218)),
    75: ((35,25,12),(72,52,28),(130,95,55),(180,142,90),(225,190,140)),
    76: ((28,30,35),(58,62,70),(110,115,128),(165,170,185),(215,220,232)),
    77: ((32,34,38),(68,72,78),(125,130,140),(182,188,198),(228,232,240)),
    78: ((42,25,10),(88,55,22),(160,100,45),(210,148,78),(245,195,125)),
    79: ((12,48,42),(28,98,88),(60,180,160),(110,225,210),(170,248,240)),
    80: ((40,42,48),(82,86,95),(150,160,175),(205,212,228),(238,242,250)),
    81: ((18,38,48),(40,82,100),(80,150,180),(130,200,225),(185,235,248)),
    82: ((25,32,40),(55,72,85),(100,130,150),(155,185,205),(210,228,242)),
    83: ((18,22,28),(40,48,55),(70,80,95),(115,128,145),(168,180,198)),
    84: ((14,20,28),(32,45,58),(55,75,100),(95,118,148),(148,172,205)),
    85: ((24,28,32),(52,58,65),(90,100,115),(140,152,168),(195,205,220)),
    86: ((14,12,18),(30,28,38),(55,50,65),(95,88,115),(145,138,168)),
    87: ((22,16,10),(48,35,22),(80,60,40),(130,105,75),(180,155,120)),
    88: ((25,38,48),(55,80,100),(100,145,175),(150,195,220),(200,232,248)),
    89: ((48,22,12),(95,45,25),(175,85,50),(220,130,85),(250,180,130)),
    90: ((38,42,50),(78,88,102),(140,160,185),(190,208,230),(228,238,250)),
    91: ((22,30,24),(48,62,52),(85,110,95),(135,165,145),(185,212,195)),
    92: ((40,25,18),(82,52,38),(150,100,75),(200,150,115),(238,200,165)),
    93: ((45,42,35),(92,85,72),(170,160,135),(215,205,180),(245,238,218)),
    94: ((28,30,34),(58,62,68),(110,115,125),(162,168,180),(212,218,228)),
    95: ((22,30,36),(48,62,74),(85,115,135),(135,168,190),(188,218,235)),
    96: ((50,8,8),(100,15,15),(180,30,30),(225,60,60),(255,100,100)),
    97: ((32,28,22),(65,58,48),(120,110,90),(172,162,138),(218,210,188)),
    98: ((25,28,35),(52,58,72),(100,110,130),(155,165,185),(205,212,228)),
    99: ((38,12,12),(78,28,28),(140,50,50),(192,82,82),(235,125,125)),
    100: ((22,25,32),(48,52,65),(90,100,120),(140,152,172),(192,202,220)),
    101: ((35,15,15),(72,32,32),(130,60,60),(182,95,95),(228,140,140)),
    102: ((28,22,16),(58,48,38),(110,90,70),(165,140,112),(215,192,162)),
    103: ((12,14,20),(28,32,42),(50,55,70),(85,92,115),(135,142,168)),
    104: ((14,12,20),(32,28,42),(55,50,70),(92,85,115),(142,135,168)),
    105: ((15,14,16),(35,32,38),(60,55,65),(100,95,108),(152,148,162)),
    106: ((22,24,30),(48,52,62),(90,95,110),(142,148,165),(195,200,215)),
    107: ((42,35,10),(88,72,25),(160,130,50),(210,178,82),(245,218,128)),
    108: ((18,16,12),(40,38,32),(70,65,55),(115,108,92),(168,160,142)),
    109: ((45,25,10),(78,45,20),(165,90,40),(215,130,65),(250,175,100)),
    110: ((30,28,25),(55,52,48),(90,85,80),(130,125,118),(175,168,160)),
    111: ((15,25,40),(28,48,72),(55,95,140),(95,148,200),(145,195,240)),
    112: ((25,15,40),(48,28,72),(95,55,140),(148,95,200),(195,145,240)),
    113: ((15,40,25),(28,72,48),(55,140,95),(95,200,148),(145,240,195)),
    114: ((55,35,75),(78,52,105),(125,82,195),(175,120,250),(210,160,255)),
    115: ((65,40,85),(90,60,118),(145,95,215),(195,138,255),(225,175,255)),
    116: ((42,28,8),(68,48,18),(140,100,35),(190,145,60),(235,190,100)),
    117: ((18,32,48),(32,58,88),(55,108,160),(90,158,220),(135,205,255)),
    118: ((0,40,32),(0,80,64),(0,160,120),(0,220,180),(80,255,220)),
    131: ((18,38,60),(28,55,90),(40,90,160),(60,140,230),(100,180,255)),
    119: ((55,42,8),(95,75,18),(200,160,45),(245,210,80),(255,235,130)),
    120: ((58,45,10),(100,78,20),(210,165,48),(250,215,85),(255,238,135)),
    121: ((60,48,12),(105,82,22),(220,170,52),(255,220,90),(255,240,140)),
    122: ((48,38,8),(85,68,16),(180,145,38),(225,195,72),(250,225,118)),
    123: ((62,52,18),(110,90,30),(230,185,60),(255,225,105),(255,245,160)),
    124: ((42,33,5),(78,62,12),(165,130,30),(215,180,62),(245,220,105)),
    125: ((28,30,40),(58,62,82),(120,130,170),(175,185,225),(220,228,250)),
    126: ((30,32,42),(62,66,86),(128,138,178),(182,192,230),(225,232,252)),
    127: ((32,34,44),(66,70,90),(135,145,185),(188,198,235),(230,236,254)),
    128: ((24,26,36),(52,56,76),(108,118,158),(165,175,215),(212,220,245)),
    129: ((34,36,48),(70,74,96),(142,152,192),(195,205,240),(235,240,255)),
    130: ((20,22,32),(46,50,68),(98,108,148),(155,165,205),(205,215,240)),
}
DEFAULT_THEME = ((42,42,46),(60,60,66),(75,75,85),(110,110,125),(200,200,210))

STATS_ITEM_COLORS = {
    "coal":                (90,  65,  45),
    "raw_iron":            (160, 110, 70),
    "liquid_iron":         (255, 130, 20),
    "iron_ingot":          (210, 190, 110),
    "steel":               (155, 165, 185),
    "crude_oil":           (55,  45,  35),
    "poor_quality_diesel": (130, 110, 50),
    "diesel":              (170, 150, 60),
    "refined_diesel":      (210, 190, 70),
    "residue":             (90,  70,  90),
    "iron_plate":          (185, 195, 210),
    "iron_plate2":         (110, 165, 255),
    "iron_coil":           (145, 210, 190),
    "raw_copper":          (195, 105, 55),
    "copper_ingot":        (200, 120, 60),
    "copper_plate":        (210, 140, 75),
    "copper_wire":         (220, 160, 80),
    "oak_log":             (140, 90,  40),
    "planks":              (180, 130, 65),
    "cut_oak_log":         (140, 90,  40),
    "chunk_plank":         (160, 105, 50),
    "plank2":              (175, 120, 60),
    "nails":               (160, 160, 175),
    "chair":               (185, 145, 80),
    "steel_plate":         (145, 155, 175),
    "steel_rod":           (150, 160, 180),
    "gear":                (130, 138, 155),
    "crankshaft":          (135, 145, 165),
    "gearbox":             (125, 135, 155),
    "iron_powder":         (100, 98,  105),
    "copper_powder":       (175, 90,  40),
    "iron_mix":            (70,  68,  80),
    "copper_mix":          (130, 80,  55),
    "steel_coil":          (110, 120, 135),
    "black_dye":           (30,  20,  40),
    "insulated_wire":      (40,  140, 50),
    "sodium_carbonate":    (220, 215, 230),
    "dirty_lithium_sulfate":(50, 110, 60),
    "ferroaluminium_alloy_ingot":(160,155,120),
    "sulfur":              (230, 210, 20),
    "table_salt":          (230, 230, 235),
    "iron_drill_head":     (110, 108, 118),
    "copper_drill_head":   (190, 110, 50),
    "electric_motor":      (70,  70,  100),
    "electromagnet":       (70,  90,  180),
    "tire":                (35,  32,  38),
    "tire_rim":            (130, 135, 150),
    "galvanized_steel":    (150, 165, 175),
    "lead_ingot":          (80,  75,  90),
    "liquid_zinc":         (140, 155, 190),
    "tetraethyllead":      (190, 65,  25),
    "lithium_ore":         (100, 165, 130),
    "lithium_sulfate":     (120, 185, 150),
    "lithium_carbonate":   (140, 200, 165),
    "lithium_ion_battery": (80,  150, 210),
    "charged_lithium_battery":(100,175,230),
    "lithium_battery_pack":(55,  130, 195),
    "rubber":              (40,  110, 55),
    "sand":                (210, 195, 140),
    "silicon":             (90,  95,  120),
    "semiconductor":       (75,  100, 160),
    "logic_plate":         (95,  130, 185),
    "gold_wire":           (210, 175, 50),
    "gold_ingot":          (225, 190, 55),
    "purple_gold_ingot":   (175, 100, 200),
    "cement":              (165, 158, 148),
    "concrete_block":      (150, 145, 138),
    "reinforced_concrete": (130, 128, 138),
    "lng":                 (80,  150, 210),
    "gasoline":            (200, 185, 65),
    "paper":               (225, 215, 185),
    "microchip_2x":        (85,  180, 165),
    "electric_motor":      (70,  70,  100),
}

TOOLBAR_H = 62
LB_W = 42
LB_H = 42

def _fmt_me(v):
    av = abs(v)
    for threshold, prefix in [
        (1e18,"E"),(1e15,"P"),(1e12,"T"),
        (1e9,"G"),(1e6,"M"),(1e3,"k"),
    ]:
        if av >= threshold:
            return f"{v/threshold:.2f} {prefix}ME"
    return f"{v:.1f} ME"


class StatsTracker:
    WINDOW = 60.0

    HIST_INTERVAL = 5.0
    HIST_LEN      = 120

    def __init__(self):
        self._elapsed     = 0.0
        self._sales       = []
        self.total_earned = 0.0
        self.total_items  = {}
        self.income_history = []
        self._hist_timer  = 0.0

    def tick(self, dt):
        self._elapsed += dt
        cutoff = self._elapsed - self.WINDOW
        self._sales = [s for s in self._sales if s[0] > cutoff]
        self._hist_timer += dt
        if self._hist_timer >= self.HIST_INTERVAL:
            self._hist_timer = 0.0
            self.income_history.append(self.money_per_min())
            if len(self.income_history) > self.HIST_LEN:
                del self.income_history[:-self.HIST_LEN]

    def record_sale(self, item, amount, money):
        self._sales.append((self._elapsed, item, amount, money))
        self.total_earned += money
        self.total_items[item] = self.total_items.get(item, 0) + amount

    def money_per_min(self):
        window = min(self._elapsed, self.WINDOW)
        if window < 0.5: return 0.0
        return sum(s[3] for s in self._sales) / window * 60.0

    def items_per_min(self):
        window = min(self._elapsed, self.WINDOW)
        if window < 0.5: return {}
        result = {}
        for _, item, amount, _ in self._sales:
            result[item] = result.get(item, 0) + amount
        return {k: v / window * 60.0 for k, v in result.items()}


_STALL_OK      = (110, 230, 130)
_STALL_WARN    = (245, 205, 90)
_STALL_BAD     = (240, 105, 95)

def machine_stall_reason(tile, ttype):
    mdef  = MACHINE_DEFS.get(ttype, {})
    stats = MACHINE_STATS.get(ttype, {})

    def _powered():
        need = stats.get("power_input", 0)
        return 1.0 if need <= 0 else min(1.0, tile.get("power", 0) / need)

    if mdef.get("drill"):
        p = _powered()
        if p <= 0:  return ("NO POWER", _STALL_BAD)
        if tile.get("amount", 0) >= stats.get("capacity", 10):
            return ("OUTPUT FULL — nothing accepts items below", _STALL_BAD)
        if p < 1.0: return (f"LOW POWER ({p*100:.0f}% speed)", _STALL_WARN)
        return ("RUNNING", _STALL_OK)

    if mdef.get("fluid_producer"):
        p = _powered()
        if p <= 0:  return ("NO POWER", _STALL_BAD)
        if tile.get("fluid_buffer", 0) >= mdef.get("cap", 10) - 1e-6:
            return ("TANK FULL — output blocked", _STALL_BAD)
        return ("RUNNING", _STALL_OK)

    if mdef.get("diesel_gen"):
        if tile.get("fuel_buffer", 0) <= 0: return ("NEEDS DIESEL FUEL", _STALL_BAD)
        return ("RUNNING", _STALL_OK)
    if mdef.get("steam_turbine"):
        if tile.get("input_buffer", 0) <= 0: return ("NEEDS STEAM", _STALL_BAD)
        return ("RUNNING", _STALL_OK)
    if mdef.get("fuel_generator"):
        if tile.get("input_buffer", 0) <= 0:
            return (f"NEEDS {mdef.get('fuel_type','fuel').upper()}", _STALL_BAD)
        return ("RUNNING", _STALL_OK)
    if mdef.get("coal_power_plant"):
        missing = []
        if tile.get("input_buffer", 0) <= 0: missing.append("COAL")
        if tile.get("water_buffer", 0) <= 0: missing.append("WATER")
        if missing: return ("NEEDS " + " + ".join(missing), _STALL_BAD)
        return ("RUNNING", _STALL_OK)
    if ttype == 12:
        if tile.get("coal_buffer", 0) <= 0: return ("NEEDS COAL", _STALL_BAD)
        return ("RUNNING", _STALL_OK)

    proc = mdef.get("process")
    if proc:
        if proc.get("needs_power"):
            p = _powered()
            if p <= 0: return ("NO POWER", _STALL_BAD)
        oport = mdef.get("output_port", {})
        out_buf = oport.get("buf", "output_buffer")
        out_cap = oport.get("cap", 99)
        cur_out = tile.get(out_buf, 0) or 0
        if cur_out >= out_cap - 1e-6:
            return ("OUTPUT FULL — connect/unblock the output", _STALL_BAD)
        check = proc.get("check")
        if check:
            try: ok = bool(check(tile))
            except Exception: ok = True
            if not ok:
                empty = []
                for port in mdef.get("input_ports", []):
                    if (tile.get(port["buf"], 0) or 0) <= 0:
                        label = port.get("item") or (port.get("items") or [port["buf"].replace("_buffer","")])[0]
                        label = label.replace("_", " ")
                        if label not in empty:
                            empty.append(label)
                if empty:
                    return ("NEEDS " + ", ".join(empty[:3]).upper(), _STALL_BAD)
                return ("WAITING — check quantities / recipe mode", _STALL_WARN)
        if proc.get("needs_power"):
            p = _powered()
            if p < 1.0: return (f"LOW POWER ({p*100:.0f}% speed)", _STALL_WARN)
        return ("RUNNING", _STALL_OK)

    if ttype in (3, 83):
        cap = stats.get("capacity", 10)
        sell_at = max(1, int(cap * stats.get("sell_threshold", 1.0)))
        if tile.get("cooldown_timer", 0) > 0: return ("SALE COOLDOWN", _STALL_WARN)
        if tile.get("amount", 0) < sell_at:   return ("FILLING", _STALL_WARN)
        return ("SELLING", _STALL_OK)
    if ttype == 51:
        cap = stats.get("sell_capacity", 400)
        if tile.get("cooldown_timer", 0) > 0: return ("SALE COOLDOWN", _STALL_WARN)
        if (tile.get("input_buffer", 0) or 0) < cap * stats.get("sell_threshold", 1.0):
            return ("FILLING", _STALL_WARN)
        return ("SELLING", _STALL_OK)
    return None


class DrawGrid:
    def __init__(self, contracts, research=None):
        self.contracts = contracts
        self.research = research
        self.buttons          = []
        self.active_tool      = -1

        fo = ["Segoe UI","SF Pro Display","Helvetica Neue","Helvetica","Arial"]
        self.font       = pygame.font.SysFont(fo, 17, bold=False)
        self.small_font = pygame.font.SysFont(fo, 14, bold=False)
        self.tiny_font  = pygame.font.SysFont(fo, 12, bold=False)
        self.money_font = pygame.font.SysFont(fo, 22, bold=True)
        self.title_font = pygame.font.SysFont(fo, 15, bold=True)
        self.icon_font  = pygame.font.SysFont(fo, 18, bold=True)

        self.refresh_buttons()
        self.selected_tile        = None
        self.info_panel_rect      = None
        self.floaters             = []
        self.show_contracts_panel = False
        self.contract_scroll_offset = 0
        self.contract_max_scroll  = 0
        self.selected_contract_id = None
        self.show_research_panel  = False
        self.research_tree_scroll = 0
        self.research_tree_hscroll = 0
        self.research_zoom        = 1.0
        self.research_zoom_btns   = {}
        self.research_cam_x   = 0.0
        self.research_cam_y   = 0.0
        self.research_cam_zoom = 0.55
        self.research_tab     = "production"
        self.research_panning = False
        self._research_pan_mouse = None
        self._research_pan_cam   = None
        self._research_vp_center = (640, 360)
        self._research_canvas_rect = None
        self._research_tabs   = {}
        self._research_needs_center = True
        self.show_build_panel     = False
        self.build_panel_selected = None
        self.build_search         = ""
        self.build_searching      = False
        self.build_panel_scroll   = 0
        self.build_panel_max_scroll = 0
        self.build_machine_buttons  = {}
        self.build_panel_rect     = None
        self.build_panel_close_rect = None
        self.build_place_btn_rect = None
        self.build_search_rect    = None
        self.show_code_console    = False
        self.console_input        = ""
        self.show_loans_panel     = False
        self.loans_panel_rect     = None
        self.loan_take_buttons    = {}
        self.loan_repay_buttons   = {}
        self.bank         = None
        self.console_message      = ""
        self.console_message_color= (200,200,200)
        self.console_message_timer= 0
        self.show_settings_panel  = False
        self._settings_console_btn = None
        self.show_stats_panel     = False
        self.show_keybind_overlay = False
        self.show_recipe_book     = False
        self.show_market_panel    = False
        self.market_scroll        = 0
        self.market_max_scroll    = 0
        self.market_search        = ""
        self.market_searching     = False
        self.market_search_rect   = None
        self.market_panel_rect    = None
        self.market_close_rect    = None
        self.market_selected_item = None
        self.market_item_rects    = {}
        self.protesters      = None
        self.market               = None
        self.rb_selected_item     = None
        self.rb_tile_rects        = {}
        self.rb_hover_t           = {}
        self.rb_recipe_index      = None
        self.rb_search_text       = ""
        self.rb_search_focused    = False
        self.rb_search_rect       = None
        self.rb_grid_scroll       = 0

        try:
            import os
            _here = os.path.dirname(os.path.abspath(__file__))
            self.material_sheet = None
            self.material_cell  = 32
            for _p in ("materials_32.png", os.path.join(_here, "materials_32.png")):
                if os.path.exists(_p):
                    self.material_sheet = pygame.image.load(_p).convert_alpha()
                    self.material_cell  = 32
                    break
            if self.material_sheet is None:
                for _p in ("materials_64.png", os.path.join(_here, "materials_64.png")):
                    if os.path.exists(_p):
                        self.material_sheet = pygame.image.load(_p).convert_alpha()
                        self.material_cell  = 64
                        break
            if self.material_sheet is None:
                for _p in ("materials.png", os.path.join(_here, "materials.png")):
                    if os.path.exists(_p):
                        self.material_sheet = pygame.image.load(_p).convert_alpha()
                        self.material_cell  = 16
                        break
        except Exception:
            self.material_sheet = None
            self.material_cell  = 32

        self.material_order = [
            "coal","raw_iron","liquid_iron","iron_ingot","steel",
            "crude_oil","poor_quality_diesel","diesel","refined_diesel",
            "residue","iron_plate","iron_plate2","iron_coil",
            "raw_copper","liquid_copper","copper_ingot","copper_plate","copper_wire",
            "soil","clay","limestone","gravel",
            "rawmix","aggregate","cement","water",
            "wet_concrete","concrete_block","reinforced_concrete",
            "steel_plate","steel_rod","gear","crankshaft",
            "paraxylene","ethylene","ethanol","acetic_acid",
            "pta","meg","plastic_pellets","plastic_casing","gearbox",
            "raw_gas","condensed_gas","refined_gas","lng",
            "clay_bricks","brick","oak_log","planks","nails","chair",
            "earth_fragment","karat_gold","bauxite_residue",
            "purified_gold","liquid_gold","gold_ingot",
            "crushed_bauxite","alumina","alumina_dust",
            "liquid_aluminium","aluminium_ingot","purple_gold_ingot",
            "lithium_ore","lithium_sulfate","lithium_carbonate",
            "lithium_ion_battery","charged_lithium_battery",
            "rubber","graphite_electrode","lithium_battery_pack",
            "sand","liquid_glass","glass","silicon",
            "semiconductor","logic_plate","gold_wire",
            "machine_oil","coke_fuel","sulfuric_acid",
            "hydrochloric_acid","filter","deep_earth_fragment",
            "microchip_2x","microchip_8x64x",
            "drill_head","ferroaluminium_magnet","steel_drill_head",
            "hydrogen","oxygen",
            "steam","naphtha","heavy_oil","light_oil",
            "gasoline","leaded_gasoline","paper",
            "raw_lead","raw_zinc","liquid_sulfur","liquid_lead",
            "boric_acid","lithium_brine",
            "molten_purple_gold","molten_ferroaluminium","chlorine",
            "uranium_ore","yellowcake","zirconium_rod",
            "fuel_rod","control_rod","spent_fuel",
            "contaminated_water","distilled_water",
            "cut_oak_log","chunk_plank","plank2",
            "iron_powder","copper_powder","iron_mix","copper_mix",
            "steel_coil","black_dye","insulated_wire",
            "sodium_carbonate","dirty_lithium_sulfate","ferroaluminium_alloy_ingot",
            "sulfur","table_salt",
            "iron_drill_head","copper_drill_head",
            "electric_motor","electromagnet",
            "tire","tire_rim","galvanized_steel",
            "lead_ingot","liquid_zinc","tetraethyllead",
        ]

        self.clipboard_settings   = None
        self.stats_tracker        = StatsTracker()
        self.stats_close_rect     = None
        self.stats_scroll         = 0
        self.debug_mode           = False
        self.power_anim_time      = 0.0
        self.autosave_flash_timer = 0.0
        self.autosave_flash_duration = 2.0
        self.net_worth_cache      = 0.0
        self.pollution_cache      = 0.0
        self.wind_speed_cache     = 0.5
        self.md_drag_start        = None
        self.md_drag_end          = None
        self.md_pending           = None
        self.bp_select_mode       = False
        self.bp_drag_start        = None
        self.bp_drag_end          = None
        self.blueprint            = None
        self.bp_paste_mode        = False
        self.show_bottleneck_overlay = False
        self.shown_milestones     = self._load_milestones()
        self.milestone_message    = None
        self.milestone_timer      = 0.0
        self.milestone_duration   = 5.0
        self._toolbar_rects       = {}
        self._left_btn_rects      = {}
        self._grid_ref            = None
        self._power_toggle_requested  = False
        self.recipe_btn_rects     = {}
        self.tile_ctrl_btn_rects  = {}

    def refresh_buttons(self):
        self.buttons = []

    def show_transaction_message(self, msg, color):
        self.floaters.append({"msg": msg, "color": color,
                               "x": 110, "y": 72,
                               "timer": 1.8, "max_timer": 1.8})

    def trigger_autosave_flash(self):
        self.autosave_flash_timer = self.autosave_flash_duration

    def compute_net_worth(self, grid, money):
        mv = 0.0
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                t = tile.get("type", 0)
                if t == 0: continue
                mstats = MACHINE_STATS.get(t, {})
                size = mstats.get("size", (1, 1))
                if size != (1, 1):
                    origin = tile.get("origin", (x, y))
                    if isinstance(origin, list): origin = tuple(origin)
                    if origin != (x, y): continue
                mv += mstats.get("cost", 0) * 0.8
                stored = tile.get("stored") or tile.get("input_item") or tile.get("output_item")
                amt = tile.get("amount", 0) + tile.get("input_buffer", 0) + tile.get("output_buffer", 0)
                if stored and amt:
                    mv += ITEM_VALUES.get(stored, 0) * amt
        return money + mv

    def compute_power_stats(self, grid):
        generated = 0.0; consumed = 0.0; seen = set()
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                t = tile.get("type", 0)
                if t == 0: continue
                ms = MACHINE_STATS.get(t, {})
                sz = ms.get("size", (1, 1))
                if sz != (1, 1):
                    orig = tile.get("origin", (x, y))
                    if isinstance(orig, list): orig = tuple(orig)
                    if orig in seen: continue
                    seen.add(orig)
                generated += ms.get("power_output", 0)
                consumed  += ms.get("power_input",  0)
        return generated, consumed


    def draw(self, screen, money, contracts, building_rotation=0,
             show_zones=False, power_mode=False, debug_mode=False,
             research=None, grid=None, pollution=0.0, wind_speed=0.5):

        self.contracts = contracts
        if research: self.research = research
        self.pollution_cache  = pollution
        self.wind_speed_cache = wind_speed
        if grid is not None:
            self._grid_ref       = grid
            self.net_worth_cache = self.compute_net_worth(grid, money)

        self.power_anim_time += clock.get_time() / 1000.0
        dt = clock.get_time() / 1000.0

        self._draw_money_hud(screen, money)
        self._draw_loan_hud(screen)
        self._draw_floaters(screen, dt)
        self._draw_toolbar(screen, power_mode, debug_mode)
        self._draw_left_buttons(screen)
        self._draw_autosave(screen)

        if self.milestone_timer > 0:
            self._draw_milestone(screen, dt)
        if self.show_build_panel:
            self._draw_build_panel(screen, money)
        if self.show_code_console:
            self._draw_code_console(screen)
        if self.show_contracts_panel:
            self.draw_contracts_overlay(screen, money)
        if self.show_research_panel:
            self.draw_research_panel(screen)
        if self.show_settings_panel:
            self._draw_settings_panel(screen)
        if self.show_stats_panel:
            self._draw_stats_panel(screen, money)
        if self.show_loans_panel:
            self._draw_loans_panel(screen, money)
        if self.show_market_panel:
            self._draw_market_panel(screen)
        if self.selected_tile:
            self.draw_info_panel(screen)
        if self.show_keybind_overlay:
            self._draw_keybind_overlay(screen)
        if self.show_recipe_book:
            self._draw_recipe_book(screen)
        if self.protesters and self.protesters.is_blocking():
            self._draw_protest_overlay(screen)

    def _draw_money_hud(self, screen, money):
        rp = self.research.rp if self.research else 0.0
        hx, hy, hw, hh = 8, 8, 205, 54
        s = pygame.Surface((hw, hh), pygame.SRCALPHA)
        pygame.draw.rect(s, (14,16,22,215), (0,0,hw,hh), border_radius=10)
        pygame.draw.rect(s, (52,58,74,255), (0,0,hw,hh), 1, border_radius=10)
        screen.blit(s, (hx, hy))

        screen.blit(self.tiny_font.render("CAPITAL", True, (85,92,112)), (hx+10, hy+7))
        screen.blit(self.money_font.render(f"${money:,.2f}", True, (88,228,108)), (hx+10, hy+20))

        rp_s = self.tiny_font.render(f"{rp:.0f} RP", True, (178,128,252))
        rw = rp_s.get_width()+10
        pygame.draw.rect(screen, (28,20,44), (hx+hw-rw-6, hy+6, rw, 16), border_radius=4)
        pygame.draw.rect(screen, (70,46,115), (hx+hw-rw-6, hy+6, rw, 16), 1, border_radius=4)
        screen.blit(rp_s, (hx+hw-rw-1, hy+8))

        poll = self.pollution_cache
        if poll > 0.01:
            intensity = min(1.0, poll / 40.0)
            badge_bg  = (40+int(20*intensity),18,18,220)
            badge_brd = (180+int(60*intensity),70,45)
            text_col  = (245,150,110) if poll < 20 else (255,95,70)
            label, value_str = "POLLUTION", f"+{poll:.2f}%"
        elif poll < -0.01:
            intensity = min(1.0, -poll / 20.0)
            badge_bg  = (14,32+int(18*intensity),18,220)
            badge_brd = (55,170+int(50*intensity),75)
            text_col  = (120,240,140)
            label, value_str = "CLEAN AIR", f"{poll:.2f}%"
        else:
            badge_bg  = (18,22,28,220)
            badge_brd = (60,68,84)
            text_col  = (150,160,180)
            label, value_str = "POLLUTION", "0.00%"

        bw_, bh_ = 110, 54; bx_ = hx+hw+8; by_ = hy
        pb = pygame.Surface((bw_,bh_), pygame.SRCALPHA)
        pygame.draw.rect(pb, badge_bg, (0,0,bw_,bh_), border_radius=10)
        pygame.draw.rect(pb, badge_brd, (0,0,bw_,bh_), 1, border_radius=10)
        screen.blit(pb, (bx_, by_))
        screen.blit(self.tiny_font.render(label, True, (85,92,112)), (bx_+10, by_+7))
        screen.blit(self.font.render(value_str, True, text_col), (bx_+10, by_+23))

        from settings import get_pollution_income_multiplier
        mult = get_pollution_income_multiplier(poll)
        mult_col = (215,140,90) if poll>0 and mult>=0.7 else (235,80,60) if poll>0 else (120,230,140) if poll<0 else (100,108,130)
        screen.blit(self.tiny_font.render(f"{mult:.2f}x income", True, mult_col), (bx_+10, by_+41))

        ws = self.wind_speed_cache; wind_pct = int(ws*100); wind_bx = bx_+bw_+8
        if ws > 0.7:   w_bg,w_brd,w_text = (18,32,44,220),(95,165,215),(175,225,255); w_lc=(130,195,245)
        elif ws > 0.4: w_bg,w_brd,w_text = (22,28,36,220),(75,115,165),(165,195,235); w_lc=(115,155,200)
        else:          w_bg,w_brd,w_text = (24,26,32,220),(58,72,92),(145,160,190);   w_lc=(95,115,145)
        wpb = pygame.Surface((bw_,bh_), pygame.SRCALPHA)
        pygame.draw.rect(wpb, w_bg, (0,0,bw_,bh_), border_radius=10)
        pygame.draw.rect(wpb, w_brd, (0,0,bw_,bh_), 1, border_radius=10)
        screen.blit(wpb, (wind_bx, by_))
        screen.blit(self.tiny_font.render("WIND", True, w_lc), (wind_bx+10, by_+7))
        screen.blit(self.font.render(f"{wind_pct}%", True, w_text), (wind_bx+10, by_+23))
        bar_x = wind_bx+10; bar_y = by_+46; bar_w = bw_-20
        pygame.draw.rect(screen, (30,36,48), (bar_x, bar_y, bar_w, 3))
        pygame.draw.rect(screen, w_brd, (bar_x, bar_y, int(bar_w*ws), 3))

        if self.active_tool > 0:
            mname = MACHINE_STATS.get(self.active_tool,{}).get("name","")
            mcost = MACHINE_STATS.get(self.active_tool,{}).get("cost",0)
            theme = MACHINE_THEMES.get(self.active_tool, DEFAULT_THEME)
            ls = self.tiny_font.render(f"PLACING  {mname}  |  ${mcost}", True, theme[4])
            lw = ls.get_width()+18
            ps = pygame.Surface((lw,20), pygame.SRCALPHA)
            pygame.draw.rect(ps, (12,14,20,210), (0,0,lw,20), border_radius=6)
            pygame.draw.rect(ps, theme[3], (0,0,lw,20), 1, border_radius=6)
            screen.blit(ps, (hx, hy+hh+4)); screen.blit(ls, (hx+9, hy+hh+6))
        elif self.active_tool == 0:
            ds = self.tiny_font.render("DELETE MODE  [ESC cancel]", True, (235,95,95))
            dw = ds.get_width()+18
            ps = pygame.Surface((dw,20), pygame.SRCALPHA)
            pygame.draw.rect(ps, (28,10,10,210), (0,0,dw,20), border_radius=6)
            pygame.draw.rect(ps, (195,65,65), (0,0,dw,20), 1, border_radius=6)
            screen.blit(ps, (hx, hy+hh+4)); screen.blit(ds, (hx+9, hy+hh+6))

    def _draw_loan_hud(self, screen):
        lm = self.bank
        if lm is None or lm.balance <= 0:
            self._loan_hud_rect = None
            return
        hx, hy, hw, hh = 8, 68, 205, 54
        s = pygame.Surface((hw, hh), pygame.SRCALPHA)
        pygame.draw.rect(s, (38, 16, 14, 215), (0, 0, hw, hh), border_radius=10)
        pygame.draw.rect(s, (170, 80, 60, 255), (0, 0, hw, hh), 1, border_radius=10)
        screen.blit(s, (hx, hy))
        screen.blit(self.tiny_font.render("DEBT", True, (220, 130, 110)), (hx + 10, hy + 6))
        screen.blit(self.money_font.render(f"-${lm.balance:,.0f}", True, (255, 140, 120)),
                    (hx + 10, hy + 18))
        rate_s = self.tiny_font.render(f"{lm.rate*100:.2f}%/min", True, (255, 180, 140))
        rw = rate_s.get_width() + 10
        pygame.draw.rect(screen, (50, 22, 16), (hx + hw - rw - 6, hy + 6, rw, 14), border_radius=3)
        pygame.draw.rect(screen, (140, 70, 50), (hx + hw - rw - 6, hy + 6, rw, 14), 1, border_radius=3)
        screen.blit(rate_s, (hx + hw - rw - 1, hy + 7))
        progress = 1.0 - (lm.compound_timer / max(lm.compound_interval, 0.001))
        bw, bh = hw - 20, 5
        bar_x, bar_y = hx + 10, hy + hh - 9
        pygame.draw.rect(screen, (24, 12, 10), (bar_x, bar_y, bw, bh), border_radius=2)
        fw = int(bw * progress)
        if fw > 0:
            if progress > 0.85:   col = (255,  90,  80)
            elif progress > 0.6:  col = (240, 160,  90)
            else:                 col = (200, 200, 100)
            pygame.draw.rect(screen, col, (bar_x, bar_y, fw, bh), border_radius=2)
        cd_text = self.tiny_font.render(f"{lm.compound_timer:.0f}s to compound",
                                         True, (210, 180, 150))
        screen.blit(cd_text, (hx + 10, bar_y - 12))
        self._loan_hud_rect = pygame.Rect(hx, hy, hw, hh)

    def _draw_loans_panel(self, screen, money):
        lm = self.bank
        if lm is None:
            return
        pw, ph = 560, 490
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        self.loans_panel_rect = pygame.Rect(px, py, pw, ph)
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 175))
        screen.blit(dim, (0, 0))
        pygame.draw.rect(screen, (24, 18, 14), (px, py, pw, ph), border_radius=12)
        pygame.draw.rect(screen, (200, 145, 80), (px, py, pw, ph), 2, border_radius=12)
        screen.blit(self.title_font.render("BANK · LOANS", True, (255, 200, 100)),
                    (px + 18, py + 13))
        screen.blit(self.tiny_font.render("[L] / [ESC] Close", True,
                    (130, 110, 90)), (px + pw - 130, py + 15))

        y = py + 50
        if lm.balance > 0:
            screen.blit(self.title_font.render("OUTSTANDING DEBT", True, (255, 140, 100)),
                        (px + 20, y))
            y += 22
            screen.blit(self.font.render(f"${lm.balance:,.2f}", True, (255, 150, 130)),
                        (px + 30, y))
            y += 26
            progress = 1.0 - (lm.compound_timer / max(lm.compound_interval, 0.001))
            bw, bh = pw - 60, 14
            pygame.draw.rect(screen, (28, 18, 12), (px + 30, y, bw, bh), border_radius=4)
            fw = int(bw * progress)
            if fw > 0:
                if progress > 0.85:   col = (255,  90,  80)
                elif progress > 0.6:  col = (240, 160,  90)
                else:                 col = (200, 200, 100)
                pygame.draw.rect(screen, col, (px + 30, y, fw, bh), border_radius=4)
            for q in (0.25, 0.5, 0.75):
                tx = px + 30 + int(bw * q)
                pygame.draw.line(screen, (80, 60, 50), (tx, y), (tx, y + bh), 1)
            y += bh + 4
            next_interest = lm.balance * lm.rate
            screen.blit(self.tiny_font.render(
                f"Next compound: +${next_interest:,.2f} in {lm.compound_timer:.1f}s    "
                f"Rate: {lm.rate*100:.2f}% per {lm.compound_interval:.0f}s",
                True, (210, 180, 150)), (px + 30, y))
            y += 22
        else:
            screen.blit(self.font.render("No outstanding debt.", True, (140, 220, 150)),
                        (px + 30, y))
            y += 30

        rp = self.research.rp if self.research else 0
        offered = int(lm.max_offer(money, rp))
        y += 10
        screen.blit(self.title_font.render("LOAN OFFER", True, (180, 200, 255)),
                    (px + 20, y))
        y += 22
        screen.blit(self.font.render(f"Available: ${offered:,}", True, (180, 200, 255)),
                    (px + 30, y))
        if offered >= lm.MIN_LOAN:
            prev_rate = lm.rate_for_amount(offered)
            screen.blit(self.tiny_font.render(
                f"(Rate if borrowed in full: {prev_rate*100:.2f}%/min)",
                True, (130, 150, 200)), (px + 30, y + 22))
            y += 18
        y += 26

        self.loan_take_buttons = {}
        take_amounts = sorted({
            a for a in (500, 5000, 50000, 500000, offered)
            if lm.MIN_LOAN <= a <= offered
        })
        if take_amounts:
            screen.blit(self.tiny_font.render("BORROW", True, (160, 180, 230)),
                        (px + 30, y))
            y += 14
            btn_w = (pw - 60 - (len(take_amounts) - 1) * 8) // len(take_amounts)
            bx = px + 30
            for amt in take_amounts:
                btn = pygame.Rect(bx, y, btn_w, 30)
                pygame.draw.rect(screen, (45, 70, 130), btn, border_radius=5)
                pygame.draw.rect(screen, (120, 160, 220), btn, 1, border_radius=5)
                label = f"+${amt:,}"
                txt = self.small_font.render(label, True, (210, 225, 255))
                screen.blit(txt, txt.get_rect(center=btn.center))
                self.loan_take_buttons[amt] = btn
                bx += btn_w + 8
            y += 38

        self.loan_repay_buttons = {}
        if lm.balance > 0:
            full_amt = max(1, int(lm.balance + 0.5))
            repay_amounts = sorted({
                a for a in (100, 1000, 10000, 100000, full_amt)
                if 0 < a <= money and a <= full_amt
            })
            if repay_amounts:
                screen.blit(self.tiny_font.render("REPAY", True, (220, 170, 130)),
                            (px + 30, y))
                y += 14
                btn_w = (pw - 60 - (len(repay_amounts) - 1) * 8) // len(repay_amounts)
                bx = px + 30
                for amt in repay_amounts:
                    btn = pygame.Rect(bx, y, btn_w, 30)
                    pygame.draw.rect(screen, (110, 60, 40), btn, border_radius=5)
                    pygame.draw.rect(screen, (220, 150, 95), btn, 1, border_radius=5)
                    label = f"-${amt:,}" if amt < full_amt else "PAY OFF"
                    txt = self.small_font.render(label, True, (255, 220, 190))
                    screen.blit(txt, txt.get_rect(center=btn.center))
                    self.loan_repay_buttons[amt] = btn
                    bx += btn_w + 8
                y += 38
            elif money < lm.MIN_LOAN:
                screen.blit(self.tiny_font.render("Not enough cash to make a payment.",
                            True, (200, 120, 100)), (px + 30, y))
                y += 18

        y += 6
        screen.blit(self.tiny_font.render("─── LIFETIME ───", True, (110, 110, 130)),
                    (px + 30, y))
        y += 16
        screen.blit(self.tiny_font.render(
            f"Loans taken: {lm.loan_count}", True, (150, 170, 200)), (px + 30, y))
        y += 14
        screen.blit(self.tiny_font.render(
            f"Total borrowed:    ${lm.total_borrowed:,.0f}", True, (160, 180, 200)),
            (px + 30, y))
        y += 14
        screen.blit(self.tiny_font.render(
            f"Total interest:    ${lm.total_interest:,.0f}", True, (220, 140, 120)),
            (px + 30, y))
        y += 14
        screen.blit(self.tiny_font.render(
            f"Total repaid:      ${lm.total_repaid:,.0f}", True, (140, 220, 150)),
            (px + 30, y))

    def _draw_floaters(self, screen, dt):
        done = []
        for f in self.floaters:
            f["timer"] -= dt
            if f["timer"] <= 0: done.append(f); continue
            ratio = f["timer"] / f["max_timer"]
            alpha = int(255 * min(1.0, ratio * 3.0))
            rise  = int((1.0 - ratio) * 44)
            txt = self.small_font.render(f["msg"], True, f["color"])
            surf = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
            surf.blit(txt, (0,0)); surf.set_alpha(alpha)
            screen.blit(surf, (f["x"] - surf.get_width()//2, f["y"] - rise))
        for f in done: self.floaters.remove(f)

    def _draw_toolbar(self, screen, power_mode, debug_mode):
        protest_active = bool(self.protesters and self.protesters.is_blocking())
        entries = [
            ("B","Build",     self.show_build_panel,              (55,145,240)),
            ("C","Contracts", self.show_contracts_panel,          (60,150,220)),
            ("T","Research",  self.show_research_panel,           (140,75,245)),
            ("N","Stats",     self.show_stats_panel,              (75,185,215)),
            ("M","Market",    getattr(self,"show_market_panel",False), (255,200,80)),
            ("K","Recipes",   self.show_recipe_book,              (255,180,80)),
            ("L","Loans",     self.show_loans_panel,              (255,140,90)),
            ("P","Power",     power_mode,                         (235,205,50)),
            ("X","Delete",    self.active_tool == 0,              (235,75,75)),
            ("Z","Debug",     debug_mode,                         (55,215,80)),
        ]
        BW,BH,GAP = 80,48,8
        total  = len(entries)*(BW+GAP)-GAP
        bar_w  = total+24; bar_h = BH+14
        bar_x  = (SCREEN_WIDTH-bar_w)//2; bar_y = SCREEN_HEIGHT-bar_h-10
        bg = pygame.Surface((bar_w,bar_h), pygame.SRCALPHA)
        pygame.draw.rect(bg, (11,13,19,225), (0,0,bar_w,bar_h), border_radius=14)
        pygame.draw.rect(bg, (44,48,62,255), (0,0,bar_w,bar_h), 1, border_radius=14)
        screen.blit(bg, (bar_x, bar_y))
        mx,my = pygame.mouse.get_pos(); self._toolbar_rects = {}; sx = bar_x+12
        for i,(key,lbl,active,accent) in enumerate(entries):
            bx = sx+i*(BW+GAP); by = bar_y+7; r = pygame.Rect(bx,by,BW,BH)
            self._toolbar_rects[key] = r; hov = r.collidepoint(mx,my)
            if active:
                bg2 = (max(0,int(accent[0]*0.20)),max(0,int(accent[1]*0.20)),max(0,int(accent[2]*0.20)))
                brd = accent; bw2 = 2
            elif hov: bg2=(26,30,40); brd=(76,82,100); bw2=1
            else:     bg2=(18,21,28); brd=(40,44,56);  bw2=1
            pygame.draw.rect(screen, bg2, r, border_radius=9)
            pygame.draw.rect(screen, brd, r, bw2, border_radius=9)
            if active: pygame.draw.circle(screen, accent, (bx+BW-8, by+8), 3)
            kc = accent if (active or hov) else (135,142,162)
            ks = self.icon_font.render(key, True, kc)
            screen.blit(ks, (bx+BW//2-ks.get_width()//2, by+5))
            lc = (218,226,248) if active else (90,96,116)
            ls = self.tiny_font.render(lbl, True, lc)
            screen.blit(ls, (bx+BW//2-ls.get_width()//2, by+30))

    def _draw_left_buttons(self, screen):
        entries = [("Fn","SET",self.show_settings_panel,(75,105,165))]
        mx,my = pygame.mouse.get_pos(); self._left_btn_rects = {}
        bx = 10; total_h = len(entries)*(LB_H+6)-6; start_y = (SCREEN_HEIGHT-total_h)//2
        for i,(key,lbl,active,accent) in enumerate(entries):
            by = start_y+i*(LB_H+6); r = pygame.Rect(bx,by,LB_W,LB_H)
            self._left_btn_rects[key] = r; hov = r.collidepoint(mx,my)
            if active:   bg2=(max(0,int(accent[0]*0.28)),max(0,int(accent[1]*0.28)),max(0,int(accent[2]*0.28))); brd=accent; bw2=2
            elif hov:    bg2=(26,30,40); brd=(76,82,100); bw2=1
            else:        bg2=(14,16,22); brd=(40,44,56);  bw2=1
            s2 = pygame.Surface((LB_W,LB_H), pygame.SRCALPHA)
            pygame.draw.rect(s2, bg2+(220,), (0,0,LB_W,LB_H), border_radius=9)
            pygame.draw.rect(s2, brd, (0,0,LB_W,LB_H), bw2, border_radius=9)
            screen.blit(s2, (bx,by))
            tc = accent if (active or hov) else (105,112,135)
            ts = self.tiny_font.render(lbl, True, tc)
            screen.blit(ts, (bx+LB_W//2-ts.get_width()//2, by+LB_H//2-ts.get_height()//2))

    def _draw_autosave(self, screen):
        if self.autosave_flash_timer <= 0: return
        t = self.autosave_flash_timer/self.autosave_flash_duration
        alpha = max(0, min(255, int(255*min(1.0,t*4)*min(1.0,(1.0-t)*3+0.15))))
        pulse = 0.7+0.3*_math.sin(self.autosave_flash_timer*_math.pi*6)
        g = int(200*pulse)
        s = pygame.Surface((76,18), pygame.SRCALPHA)
        s.fill((10,10,14,min(200,alpha)))
        pygame.draw.rect(s, (38,g,55,alpha), (0,0,76,18), 1, border_radius=4)
        txt = self.tiny_font.render("SAVED", True, (75,g+40,95))
        s.blit(txt, (6,2)); screen.blit(s, (222,12))
        self.autosave_flash_timer -= clock.get_time()/1000

    def _draw_milestone(self, screen, dt):
        af = self.milestone_timer/self.milestone_duration
        pw,ph = 480,68; px=(SCREEN_WIDTH-pw)//2; py=60
        o = pygame.Surface((pw,ph), pygame.SRCALPHA)
        pygame.draw.rect(o, (16,18,28,int(225*af)), (0,0,pw,ph), border_radius=10)
        pygame.draw.rect(o, (95,145,250,int(255*af)), (0,0,pw,ph), 2, border_radius=10)
        ts = self.title_font.render("MILESTONE", True, (255,198,95)); o.blit(ts, ts.get_rect(center=(pw//2,16)))
        ms = self.small_font.render(self.milestone_message or "", True, (195,205,228)); o.blit(ms, ms.get_rect(center=(pw//2,44)))
        screen.blit(o, (px,py)); self.milestone_timer -= dt


    def _draw_stats_panel(self, screen, money):
        pw,ph = 600,560; px=(SCREEN_WIDTH-pw)//2; py=(SCREEN_HEIGHT-ph)//2
        self._stats_panel_rect = pygame.Rect(px,py,pw,ph)
        dim = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); dim.fill((0,0,0,150)); screen.blit(dim,(0,0))
        pygame.draw.rect(screen,(15,17,23),(px,py,pw,ph),border_radius=12)
        pygame.draw.rect(screen,(55,62,82),(px,py,pw,ph),1,border_radius=12)
        pygame.draw.rect(screen,(19,22,30),(px,py,pw,44),border_radius=12)
        pygame.draw.rect(screen,(40,45,60),(px,py+44,pw,1))
        ts = self.title_font.render("STATISTICS",True,(185,196,228)); screen.blit(ts,ts.get_rect(center=(px+pw//2,py+22)))
        mx,my = pygame.mouse.get_pos()
        cr = pygame.Rect(px+pw-36,py+10,26,24); ch = cr.collidepoint(mx,my)
        pygame.draw.rect(screen,(62,22,22) if ch else (38,16,16),cr,border_radius=6)
        pygame.draw.rect(screen,(215,65,65) if ch else (115,45,45),cr,1,border_radius=6)
        xs = self.small_font.render("X",True,(238,95,95)); screen.blit(xs,xs.get_rect(center=cr.center))
        self.stats_close_rect = cr
        col_mid = px+pw//2; sec_y = py+54
        screen.blit(self.title_font.render("INCOME",True,(88,228,108)),(px+16,sec_y)); y1=sec_y+22
        mpm = self.stats_tracker.money_per_min()
        screen.blit(self.small_font.render("$/min:",True,(115,125,150)),(px+16,y1))
        screen.blit(self.font.render(f"${mpm:,.2f}",True,(88,228,108) if mpm>0 else (80,90,110)),(px+72,y1)); y1+=22
        screen.blit(self.small_font.render("Total earned:",True,(115,125,150)),(px+16,y1))
        screen.blit(self.font.render(f"${self.stats_tracker.total_earned:,.2f}",True,(165,175,200)),(px+110,y1)); y1+=22
        screen.blit(self.small_font.render("Net worth:",True,(115,125,150)),(px+16,y1))
        screen.blit(self.font.render(f"${self.net_worth_cache:,.2f}",True,(255,215,80)),(px+88,y1))
        screen.blit(self.title_font.render("POWER  (installed)",True,(250,195,45)),(col_mid+16,sec_y)); y2=sec_y+22
        gen,con = (0.0,0.0)
        if self._grid_ref: gen,con = self.compute_power_stats(self._grid_ref)
        net_p = gen-con
        screen.blit(self.small_font.render("Generation:",True,(115,125,150)),(col_mid+16,y2))
        screen.blit(self.font.render(f"{_fmt_me(gen)}/s",True,(88,228,108)),(col_mid+102,y2)); y2+=22
        screen.blit(self.small_font.render("Consumption:",True,(115,125,150)),(col_mid+16,y2))
        screen.blit(self.font.render(f"{_fmt_me(con)}/s",True,(235,95,95)),(col_mid+102,y2)); y2+=22
        nc = (88,228,108) if net_p>=0 else (235,95,95); pref="+" if net_p>=0 else ""
        screen.blit(self.small_font.render("Net:",True,(115,125,150)),(col_mid+16,y2))
        screen.blit(self.font.render(f"{pref}{_fmt_me(net_p)}/s",True,nc),(col_mid+50,y2))
        div_y = sec_y+92
        pygame.draw.line(screen,(36,40,54),(px+10,div_y),(px+pw-10,div_y),1)
        pygame.draw.line(screen,(36,40,54),(col_mid,sec_y+2),(col_mid,div_y-2),1)
        gy = div_y+10
        screen.blit(self.title_font.render("INCOME  $/MIN  (last 10 min)",True,(185,192,212)),(px+16,gy)); gy+=20
        g_rect = pygame.Rect(px+16, gy, pw-32, 72)
        pygame.draw.rect(screen,(11,13,18),g_rect,border_radius=4)
        pygame.draw.rect(screen,(38,42,56),g_rect,1,border_radius=4)
        hist = self.stats_tracker.income_history
        if len(hist) >= 2:
            peak = max(max(hist), 1e-9)
            n = len(hist)
            pts = []
            for i, v in enumerate(hist):
                gx_ = g_rect.x + 2 + (g_rect.w - 4) * i / max(1, self.stats_tracker.HIST_LEN - 1)
                gy_ = g_rect.bottom - 2 - (g_rect.h - 4) * min(v / peak, 1.0)
                pts.append((gx_, gy_))
            if len(pts) >= 2:
                pygame.draw.lines(screen,(88,228,108),False,pts,2)
            peak_s=self.tiny_font.render(f"peak ${peak:,.0f}/min",True,(80,120,90))
            screen.blit(peak_s,(g_rect.right-peak_s.get_width()-6,g_rect.y+4))
        else:
            hint=self.tiny_font.render("collecting samples...",True,(55,62,80))
            screen.blit(hint,hint.get_rect(center=g_rect.center))
        div2_y = g_rect.bottom+10
        pygame.draw.line(screen,(36,40,54),(px+10,div2_y),(px+pw-10,div2_y),1)
        iy = div2_y+12
        screen.blit(self.title_font.render("ITEMS SOLD / MIN  (60 s rolling avg)",True,(185,192,212)),(px+16,iy)); iy+=22
        ipm = self.stats_tracker.items_per_min()
        if not ipm:
            screen.blit(self.small_font.render("No sales recorded yet — sell some items at a depot.",True,(60,68,86)),(px+16,iy))
        else:
            max_rate = max(ipm.values()) if ipm else 1.0
            bar_area = pw-230
            clip_rect = pygame.Rect(px+8, iy-2, pw-16, ph-(iy-py)-28)
            screen.set_clip(clip_rect)
            scroll_y = iy-self.stats_scroll
            for item, rate in sorted(ipm.items(), key=lambda kv: -kv[1]):
                if scroll_y > py+ph-30: break
                if scroll_y+18 < iy: scroll_y+=20; continue
                col = STATS_ITEM_COLORS.get(item,(130,130,150))
                pygame.draw.circle(screen,col,(px+22,scroll_y+8),5)
                label = item.replace("_"," ").title()
                screen.blit(self.small_font.render(label,True,(155,162,188)),(px+32,scroll_y))
                bx=px+178; bh=10; by_=scroll_y+3
                fill=int(bar_area*min(rate/max_rate,1.0))
                pygame.draw.rect(screen,(22,24,32),(bx,by_,bar_area,bh),border_radius=3)
                if fill>0: pygame.draw.rect(screen,col,(bx,by_,fill,bh),border_radius=3)
                rs=self.small_font.render(f"{rate:.1f}/min",True,(165,175,200))
                screen.blit(rs,(bx+bar_area+6,scroll_y)); scroll_y+=20
            screen.set_clip(None)
        screen.blit(self.tiny_font.render("[N] toggle  |  60 s rolling window  |  power = installed capacity",True,(48,54,70)),(px+16,py+ph-16))

    def _draw_build_panel(self, screen, money):
        pw=min(940,SCREEN_WIDTH-40); ph=500
        px=(SCREEN_WIDTH-pw)//2; py=(SCREEN_HEIGHT-TOOLBAR_H-20-ph)//2
        self.build_panel_rect = pygame.Rect(px,py,pw,ph)
        dim=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); dim.fill((0,0,0,150)); screen.blit(dim,(0,0))
        pygame.draw.rect(screen,(15,17,23),(px,py,pw,ph),border_radius=12)
        pygame.draw.rect(screen,(48,52,68),(px,py,pw,ph),1,border_radius=12)
        pygame.draw.rect(screen,(19,22,30),(px,py,pw,44),border_radius=12)
        pygame.draw.rect(screen,(44,48,62),(px,py+44,pw,1))
        ts=self.title_font.render("BUILD",True,(185,196,228)); screen.blit(ts,ts.get_rect(center=(px+pw//2,py+22)))
        cr=pygame.Rect(px+pw-36,py+10,26,24); mx,my=pygame.mouse.get_pos(); ch_=cr.collidepoint(mx,my)
        pygame.draw.rect(screen,(62,22,22) if ch_ else (38,16,16),cr,border_radius=6)
        pygame.draw.rect(screen,(215,65,65) if ch_ else (115,45,45),cr,1,border_radius=6)
        xs=self.small_font.render("X",True,(238,95,95)); screen.blit(xs,xs.get_rect(center=cr.center))
        self.build_panel_close_rect=cr
        sx_=px+264; sr_=pygame.Rect(sx_,py+52,340,24)
        sb_=(62,110,190) if self.build_searching else (42,46,60)
        pygame.draw.rect(screen,(20,22,30),sr_,border_radius=5)
        pygame.draw.rect(screen,sb_,sr_,1,border_radius=5)
        screen.blit(self.tiny_font.render("/",True,(85,92,112)),(sr_.x+5,sr_.y+5))
        st_=self.build_search if self.build_search else "Search..."
        sc_=(196,206,248) if self.build_search else (58,64,82)
        screen.blit(self.small_font.render(st_,True,sc_),(sr_.x+17,sr_.y+5))
        self.build_search_rect=sr_
        lw=252; lx=px+8; ly=py+48; lh=ph-56
        ls=pygame.Surface((lw,lh),pygame.SRCALPHA)
        pygame.draw.rect(ls,(11,13,19,205),(0,0,lw,lh),border_radius=8)
        pygame.draw.rect(ls,(36,40,54,255),(0,0,lw,lh),1,border_radius=8)
        screen.blit(ls,(lx,ly))
        if self.build_panel_selected is not None:
            mid=self.build_panel_selected; mstats=MACHINE_STATS.get(mid,{})
            mname=mstats.get("name","Unknown"); mcost=mstats.get("cost",0)
            theme=MACHINE_THEMES.get(mid,DEFAULT_THEME)
            pr=pygame.Rect(lx+12,ly+12,lw-24,118)
            colour=MACHINE_TYPES.get(mid,(48,52,64))
            pygame.draw.rect(screen,colour,pr,border_radius=8)
            pygame.draw.rect(screen,theme[3],pr,2,border_radius=8)
            if mid in MACHINE_IMAGES:
                try:
                    img=MACHINE_IMAGES[mid]; iw,ih=img.get_size()
                    scale=min(pr.width/iw,pr.height/ih); sw,sh=int(iw*scale),int(ih*scale)
                    im=pygame.transform.scale(img,(sw,sh))
                    screen.blit(im,(pr.x+(pr.width-sw)//2,pr.y+(pr.height-sh)//2))
                except Exception: pass
            screen.blit(self.title_font.render(mname,True,(232,240,255)),(lx+12,ly+138))
            tmap={"drill":"EXTRACTOR","pipe":"LOGISTICS","merger":"LOGISTICS","splitter":"LOGISTICS",
                  "depot":"STORAGE","processor":"PROCESSING","power_source":"POWER","research":"RESEARCH",
                  "scrubber":"UTILITY","logic":"LOGIC","utility":"UTILITY"}
            badge=tmap.get(mstats.get("type",""),mstats.get("type","").upper())
            bs_=self.tiny_font.render(badge,True,theme[4]); bw_=bs_.get_width()+10
            pygame.draw.rect(screen,theme[0],(lx+12,ly+156,bw_,15),border_radius=3)
            pygame.draw.rect(screen,theme[2],(lx+12,ly+156,bw_,15),1,border_radius=3)
            screen.blit(bs_,(lx+17,ly+157))
            sy_=ly+178; can_afford=mcost<=money
            cc_=(72,215,90) if can_afford else (215,70,70)
            screen.blit(self.money_font.render(f"${mcost}",True,cc_),(lx+12,sy_)); sy_+=28
            for lbl_,val_ in self._stat_lines(mid,mstats):
                screen.blit(self.tiny_font.render(lbl_,True,(84,90,110)),(lx+12,sy_))
                vs_=self.tiny_font.render(val_,True,(165,174,202))
                screen.blit(vs_,(lx+lw-vs_.get_width()-14,sy_)); sy_+=16
            mdef_b = MACHINE_DEFS.get(mid, {})
            def _pretty(name): return name.replace("_", " ").title() if name else ""
            def _join(items, max_n=4):
                items = list(items)
                if len(items) <= max_n:
                    return ", ".join(_pretty(i) for i in items)
                return ", ".join(_pretty(i) for i in items[:max_n]) + f"  (+{len(items)-max_n})"

            in_items = []
            for port in mdef_b.get("input_ports", []) or []:
                if port.get("item") and port["item"] not in in_items:
                    in_items.append(port["item"])
                for it in port.get("items", []) or []:
                    if it not in in_items: in_items.append(it)
            out_items = []
            proc_b = mdef_b.get("process", {}) or {}
            if proc_b.get("produce"):
                out_items.append(proc_b["produce"])
            for v in (proc_b.get("recipe_map") or {}).values():
                if isinstance(v, tuple) and v and v[0] not in out_items:
                    out_items.append(v[0])
            for m in (proc_b.get("mode_recipes") or {}).values():
                if m.get("produce") and m["produce"] not in out_items:
                    out_items.append(m["produce"])
            if mdef_b.get("drill"):
                if mdef_b.get("resource") and mdef_b["resource"] not in out_items:
                    out_items.append(mdef_b["resource"])
                for r in mdef_b.get("resources", []) or []:
                    if r not in out_items: out_items.append(r)
            if mdef_b.get("fluid_producer") and mdef_b.get("resource"):
                if mdef_b["resource"] not in out_items:
                    out_items.append(mdef_b["resource"])
            from settings import REFINERY_RECIPES as _RR
            if mid == 16:
                in_items = [k for k in _RR.keys() if k not in in_items] + in_items
                for v in _RR.values():
                    if v.get("produce") and v["produce"] not in out_items:
                        out_items.append(v["produce"])
                if "residue" not in out_items: out_items.append("residue")

            DESC = {
                "drill":        "Mines raw material from the ground below.",
                "fluid_producer":"Pumps fluid from underground reserves.",
                "pipe":         "Routes items between machines.",
                "merger":       "Combines three input lanes into one.",
                "splitter":     "Splits one input across three outputs.",
                "depot":        "Sells stored items at the listed cooldown.",
                "processor":    "Consumes inputs and produces refined items.",
                "power_source": "Generates power for connected machines.",
                "power_pole":   "Relays power across the grid.",
                "power_storage":"Buffers power for off-peak draw.",
                "research":     "Generates Research Points (RP) for the tech tree.",
                "scrubber":     "Removes pollution from the atmosphere.",
                "logic":        "Logic gate. Reserved for advanced wiring.",
                "utility":      "Specialised infrastructure.",
                "storage":      "High-capacity item / fluid buffer.",
            }
            desc_text = DESC.get(mstats.get("type"), "")

            blk_y = sy_ + 4
            if desc_text:
                words = desc_text.split()
                line = ""
                max_w = lw - 24
                for w in words:
                    test = (line + " " + w).strip()
                    if self.tiny_font.size(test)[0] > max_w:
                        screen.blit(self.tiny_font.render(line, True, (140,148,170)),
                                    (lx+12, blk_y))
                        blk_y += 12
                        line = w
                    else:
                        line = test
                if line:
                    screen.blit(self.tiny_font.render(line, True, (140,148,170)),
                                (lx+12, blk_y))
                    blk_y += 14
            if in_items:
                screen.blit(self.tiny_font.render("Resources:", True, (130,180,250)),
                            (lx+12, blk_y))
                screen.blit(self.tiny_font.render(_join(in_items, 3), True, (180,210,240)),
                            (lx+12, blk_y+12))
                blk_y += 26
            if out_items:
                screen.blit(self.tiny_font.render("Outputs:", True, (140,230,150)),
                            (lx+12, blk_y))
                screen.blit(self.tiny_font.render(_join(out_items, 3), True, (180,240,190)),
                            (lx+12, blk_y+12))
                blk_y += 26

            screen.blit(self.tiny_font.render(f"Sell: ${mcost*0.8:.0f}",True,(75,82,102)),(lx+12,ly+lh-64))
            pb_=pygame.Rect(lx+10,ly+lh-46,lw-20,36); ph_=pb_.collidepoint(mx,my)
            if can_afford: pg_=(30,90,46) if not ph_ else (40,115,60); pc_=(58,205,80); ptc_=(165,252,178)
            else:          pg_=(52,26,26); pc_=(125,55,55); ptc_=(165,116,116)
            pygame.draw.rect(screen,pg_,pb_,border_radius=8)
            pygame.draw.rect(screen,pc_,pb_,2,border_radius=8)
            pt_=self.font.render("Start Placing [T]",True,ptc_)
            screen.blit(pt_,pt_.get_rect(center=pb_.center))
            self.build_place_btn_rect=pb_
        else:
            hint=self.small_font.render("Select a machine",True,(56,62,78))
            screen.blit(hint,hint.get_rect(center=(lx+lw//2,ly+lh//2)))
            self.build_place_btn_rect=None
        div_x=px+lw+12; pygame.draw.line(screen,(36,40,54),(div_x,py+48),(div_x,py+ph-8))
        rx=div_x+8; rw=pw-lw-28; ry=py+84; rh=ph-92
        clip=pygame.Rect(rx,ry,rw,rh); screen.set_clip(clip)
        BTN=90; GAP2=6; per_row=max(1,(rw-12)//(BTN+GAP2))
        cy_=ry-self.build_panel_scroll; sl_=self.build_search.lower()
        self.build_machine_buttons={}
        for cat,ids in BUILD_CATEGORIES:
            unlocked=[m for m in ids if self.contracts.is_machine_unlocked(m,self.research)]
            if sl_: unlocked=[m for m in unlocked if sl_ in MACHINE_STATS.get(m,{}).get("name","").lower()]
            if not unlocked: continue
            pygame.draw.line(screen,(32,36,48),(rx+4,cy_+10),(rx+rw-8,cy_+10),1)
            screen.blit(self.title_font.render(cat.upper(),True,(112,120,148)),(rx+6,cy_-1)); cy_+=22; rs_=cy_
            for i,mid in enumerate(unlocked):
                col_=i%per_row; row_=i//per_row
                bx_=rx+8+col_*(BTN+GAP2); by_=rs_+row_*(BTN+GAP2)
                br_=pygame.Rect(bx_,by_,BTN,BTN); self.build_machine_buttons[mid]=br_
                is_sel=mid==self.build_panel_selected; is_act=mid==self.active_tool
                hov_=br_.collidepoint(mx,my) and clip.collidepoint(mx,my)
                th_=MACHINE_THEMES.get(mid,DEFAULT_THEME)
                if is_sel or is_act:   bg3=th_[1]; brd3=th_[3]; bw3=2
                elif hov_:             bg3=tuple(min(255,c+14) for c in th_[0]); brd3=th_[2]; bw3=1
                else:                  bg3=th_[0]; brd3=(34,38,50); bw3=1
                pygame.draw.rect(screen,bg3,br_,border_radius=8)
                pygame.draw.rect(screen,brd3,br_,bw3,border_radius=8)
                if is_act: pygame.draw.circle(screen,th_[4],(bx_+BTN-7,by_+7),3)
                ir_=pygame.Rect(bx_+7,by_+5,BTN-14,BTN-26)
                c3_=MACHINE_TYPES.get(mid,(48,52,64)); pygame.draw.rect(screen,c3_,ir_,border_radius=5)
                if mid in MACHINE_IMAGES:
                    try:
                        img=MACHINE_IMAGES[mid]; iw,ih=img.get_size()
                        scale=min(ir_.width/iw,ir_.height/ih); sw,sh=int(iw*scale),int(ih*scale)
                        im=pygame.transform.scale(img,(sw,sh))
                        screen.blit(im,(ir_.x+(ir_.width-sw)//2,ir_.y+(ir_.height-sh)//2))
                    except Exception: pass
                nm_=MACHINE_STATS.get(mid,{}).get("name","?")
                if len(nm_)>11: nm_=nm_[:10]+"."
                nc_=(205,216,245) if (is_sel or is_act or hov_) else (122,130,155)
                ns_=self.tiny_font.render(nm_,True,nc_)
                screen.blit(ns_,(bx_+BTN//2-ns_.get_width()//2,by_+BTN-18))
            rows_=(len(unlocked)+per_row-1)//per_row; cy_=rs_+rows_*(BTN+GAP2)+10
        content_h_=cy_-ry+self.build_panel_scroll
        self.build_panel_max_scroll=max(0,content_h_-rh); screen.set_clip(None)
        if self.build_panel_max_scroll>0:
            sbx_=px+pw-10; sbh_=rh
            pygame.draw.rect(screen,(18,20,28),(sbx_,ry,7,sbh_),border_radius=3)
            hh2_=max(22,int(sbh_*rh/(rh+self.build_panel_max_scroll)))
            rat_=self.build_panel_scroll/self.build_panel_max_scroll if self.build_panel_max_scroll else 0
            hy2_=ry+int(rat_*(sbh_-hh2_))
            pygame.draw.rect(screen,(62,72,98),(sbx_,hy2_,7,hh2_),border_radius=3)
        hovered_mid=None
        for mid,br in self.build_machine_buttons.items():
            if br.collidepoint(mx,my) and clip.collidepoint(mx,my): hovered_mid=mid; break
        if hovered_mid is not None and hovered_mid!=self.build_panel_selected:
            hstats=MACHINE_STATS.get(hovered_mid,{}); hname=hstats.get("name","?"); hcost=hstats.get("cost",0)
            htheme=MACHINE_THEMES.get(hovered_mid,DEFAULT_THEME)
            lines=[(hname,htheme[4],self.title_font)]
            lines.append((f"${hcost}",(88,228,108) if hcost<=money else (235,95,95),self.font))
            for lbl_,val_ in self._stat_lines(hovered_mid,hstats):
                lines.append((f"{lbl_}: {val_}",(165,174,202),self.tiny_font))
            sz=hstats.get("size",(1,1))
            if sz!=(1,1): lines.append((f"Size: {sz[0]}x{sz[1]}",(135,148,175),self.tiny_font))
            from settings import POLLUTION_PER_MACHINE
            pol_rate=POLLUTION_PER_MACHINE.get(hovered_mid,0)
            if pol_rate>0: lines.append((f"Pollution: +{pol_rate*3600:.3f}%/h",(235,140,90),self.tiny_font))
            elif hovered_mid==11: lines.append(("Pollution: 0 (clean)",(120,230,140),self.tiny_font))
            tt_w=0; tt_h=0; rendered=[]
            for text,col,fnt in lines:
                surf=fnt.render(text,True,col); rendered.append(surf)
                tt_w=max(tt_w,surf.get_width()); tt_h+=surf.get_height()+2
            tt_w+=16; tt_h+=10
            tx_=mx+14; ty_=my+10
            if tx_+tt_w>SCREEN_WIDTH-4: tx_=mx-tt_w-10
            if ty_+tt_h>SCREEN_HEIGHT-4: ty_=SCREEN_HEIGHT-tt_h-4
            tts=pygame.Surface((tt_w,tt_h),pygame.SRCALPHA)
            pygame.draw.rect(tts,(10,12,18,235),(0,0,tt_w,tt_h),border_radius=7)
            pygame.draw.rect(tts,htheme[3]+(255,),(0,0,tt_w,tt_h),1,border_radius=7)
            screen.blit(tts,(tx_,ty_)); cy_tt=ty_+6
            for surf in rendered: screen.blit(surf,(tx_+8,cy_tt)); cy_tt+=surf.get_height()+2

    def _stat_lines(self,mid,ms_):
        out=[]
        if ms_.get("power_output",0)>0:
            out.append(("Output",f"{_fmt_me(ms_['power_output'])}/s"))
            out.append(("Range",f"{ms_.get('power_range',0)} tiles"))
        if ms_.get("power_input",0)>0: out.append(("Needs",f"{_fmt_me(ms_['power_input'])}/s"))
        if ms_.get("capacity",0)>0: out.append(("Capacity",str(ms_["capacity"])))
        if ms_.get("rate",0)>0: out.append(("Rate",f"{ms_['rate']}/s"))
        return out


    def _draw_code_console(self,screen):
        pw,ph=420,175; px=(SCREEN_WIDTH-pw)//2; py=(SCREEN_HEIGHT-ph)//2
        o=pygame.Surface((pw,ph),pygame.SRCALPHA)
        pygame.draw.rect(o,(13,9,22,240),(0,0,pw,ph),border_radius=10)
        pygame.draw.rect(o,(135,85,252,255),(0,0,pw,ph),2,border_radius=10)
        screen.blit(o,(px,py))
        ts=self.title_font.render("CODE CONSOLE",True,(170,115,252))
        screen.blit(ts,ts.get_rect(center=(px+pw//2,py+20)))
        hs=self.tiny_font.render("Type a code, ENTER to submit  |  ESC closes",True,(90,72,128))
        screen.blit(hs,hs.get_rect(center=(px+pw//2,py+38)))
        pygame.draw.line(screen,(70,45,110),(px+14,py+52),(px+pw-14,py+52),1)
        ib=pygame.Rect(px+18,py+62,pw-36,34)
        pygame.draw.rect(screen,(20,12,36),ib,border_radius=5)
        pygame.draw.rect(screen,(138,90,252),ib,2,border_radius=5)
        screen.blit(self.small_font.render(">",True,(135,90,252)),(ib.x+7,ib.y+9))
        dt_="*"*len(self.console_input)
        screen.blit(self.font.render(dt_,True,(205,185,252)),(ib.x+22,ib.y+8))
        cx_=ib.x+22+self.font.size(dt_)[0]
        if int(_time_module.time()*2)%2==0: pygame.draw.rect(screen,(170,130,252),(cx_+1,ib.y+7,2,20))
        if self.console_message and self.console_message_timer>0:
            ms_=self.small_font.render(self.console_message,True,self.console_message_color)
            screen.blit(ms_,ms_.get_rect(center=(px+pw//2,py+125)))
            self.console_message_timer-=clock.get_time()/1000
        screen.blit(self.tiny_font.render("Tip: codes are secret -- ask around!",True,(62,48,88)),
            self.tiny_font.render("Tip: codes are secret -- ask around!",True,(62,48,88)).get_rect(center=(px+pw//2,py+155)))

    def _draw_settings_panel(self,screen):
        pw,ph=400,440; px=(SCREEN_WIDTH-pw)//2; py=(SCREEN_HEIGHT-ph)//2
        self._settings_panel_rect=pygame.Rect(px,py,pw,ph)
        dim=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); dim.fill((0,0,0,135)); screen.blit(dim,(0,0))
        o=pygame.Surface((pw,ph),pygame.SRCALPHA)
        pygame.draw.rect(o,(15,17,25,240),(0,0,pw,ph),border_radius=12)
        pygame.draw.rect(o,(52,58,76,255),(0,0,pw,ph),1,border_radius=12)
        screen.blit(o,(px,py))
        ts=self.title_font.render("SETTINGS / KEY BINDINGS",True,(185,194,222))
        screen.blit(ts,ts.get_rect(center=(px+pw//2,py+21)))
        pygame.draw.line(screen,(42,46,62),(px+16,py+40),(px+pw-16,py+40),1)
        bindings=[("B","Build panel"),("C","Contracts"),("T","Research / Confirm place"),
                  ("N","Statistics panel"),("K","Recipe Book"),
                  ("P","Toggle Power mode"),("X","Toggle Delete mode"),("Z","Debug view"),
                  ("R","Rotate building"),("ESC","Close panel / cancel tool"),
                  ("Ctrl+S","Manual save"),("WASD","Pan camera"),("Scroll","Zoom")]
        y_=py+52
        for k,d in bindings:
            ks=self.tiny_font.render(k,True,(95,168,252)); ds=self.tiny_font.render(d,True,(145,152,175))
            screen.blit(ks,(px+18,y_)); screen.blit(ds,(px+95,y_)); y_+=18
        pygame.draw.line(screen,(42,46,62),(px+16,y_+6),(px+pw-16,y_+6),1)
        btn_w,btn_h=220,30; btn_x=px+(pw-btn_w)//2; btn_y=y_+16
        self._settings_console_btn=pygame.Rect(btn_x,btn_y,btn_w,btn_h)
        mx_p,my_p=pygame.mouse.get_pos(); hov=self._settings_console_btn.collidepoint(mx_p,my_p)
        pygame.draw.rect(screen,(58,38,92) if hov else (38,28,64),self._settings_console_btn,border_radius=6)
        pygame.draw.rect(screen,(165,105,240) if hov else (125,75,200),self._settings_console_btn,1,border_radius=6)
        bs=self.small_font.render("Open Code Console",True,(215,195,255))
        screen.blit(bs,bs.get_rect(center=self._settings_console_btn.center))
        vol_y=btn_y+45
        pygame.draw.line(screen,(42,46,62),(px+16,vol_y-6),(px+pw-16,vol_y-6),1)
        screen.blit(self.small_font.render("Volume",True,(185,194,222)),(px+18,vol_y)); vol_y+=22
        if not hasattr(self,'_music_vol'): self._music_vol=0.5; self._sfx_vol=0.7
        for label,attr in [("Music","_music_vol"),("SFX","_sfx_vol")]:
            val=getattr(self,attr)
            screen.blit(self.tiny_font.render(label,True,(145,152,175)),(px+18,vol_y+2))
            sl_x=px+80; sl_w=pw-120; sl_y=vol_y+6
            pygame.draw.rect(screen,(30,34,48),(sl_x,sl_y,sl_w,6),border_radius=3)
            pygame.draw.rect(screen,(80,130,200),(sl_x,sl_y,int(sl_w*val),6),border_radius=3)
            thumb_x=sl_x+int(sl_w*val)
            pygame.draw.circle(screen,(120,170,240),(thumb_x,sl_y+3),7)
            pygame.draw.circle(screen,(180,210,255),(thumb_x,sl_y+3),4)
            pct=self.tiny_font.render(f"{int(val*100)}%",True,(100,110,135))
            screen.blit(pct,(px+pw-38,vol_y+2))
            setattr(self,f'{attr}_slider',pygame.Rect(sl_x,sl_y-4,sl_w,14)); vol_y+=24
        cs=self.tiny_font.render("[ESC] Close",True,(68,74,94))
        screen.blit(cs,cs.get_rect(center=(px+pw//2,py+ph-14)))

    def _build_recipe_index(self):
        from settings import MACHINE_DEFS,MACHINE_STATS
        idx={}
        def add(item,rec): idx.setdefault(item,[]).append(rec)
        for mid,mdef in MACHINE_DEFS.items():
            stats=MACHINE_STATS.get(mid,{}); mname=stats.get("name",f"Machine {mid}"); power=stats.get("power_input",0)
            if mdef.get("drill"):
                resource=mdef.get("resource"); mine_time=mdef.get("mine_time",1.0)
                if resource: add(resource,{"machine_type":mid,"machine_name":mname,"inputs":[],"output_qty":1,"time":mine_time,"power":power,"fuel":None})
                if "resources" in mdef:
                    for res in mdef["resources"]:
                        add(res,{"machine_type":mid,"machine_name":mname,"inputs":[],"output_qty":1,"time":mine_time,"power":power,"fuel":None})
                continue
            if mdef.get("fluid_producer"):
                prod=mdef.get("resource"); rate=mdef.get("rate",0.12)
                if prod: add(prod,{"machine_type":mid,"machine_name":mname,"inputs":[],"output_qty":rate,"time":1.0,"power":power,"fuel":None})
                continue
            proc=mdef.get("process")
            if not proc: continue
            input_items=[]
            for port in mdef.get("input_ports",[]):
                if "items" in port: input_items.extend(port["items"])
                elif "item" in port: input_items.append(port["item"])
            time_=proc.get("time",1.0); consume=proc.get("consume",{})
            pfn=proc.get("produce_fn")
            if pfn=="recipe_map":
                rmap=proc.get("recipe_map",{})
                for inp,(out,amt) in rmap.items():
                    qty=consume.get("input_buffer",1)
                    add(out,{"machine_type":mid,"machine_name":mname,"inputs":[(inp,qty)],"output_qty":amt,"time":time_,"power":power,"fuel":None})
            elif pfn=="furnace":
                coal_qty=consume.get("coal_buffer",1); ore_qty=consume.get("input_buffer",1)
                furnace_map={"raw_iron":"liquid_iron","raw_copper":"liquid_copper","sand":"liquid_glass"}
                for inp in input_items:
                    out=furnace_map.get(inp,inp.replace("raw_","liquid_"))
                    if out!=inp:
                        add(out,{"machine_type":mid,"machine_name":mname,"inputs":[(inp,ore_qty)],"output_qty":1,"time":time_,"power":power,"fuel":("coal",coal_qty)})
            elif pfn=="refinery":
                from settings import REFINERY_RECIPES
                for inp,rec in REFINERY_RECIPES.items():
                    out=rec.get("produce")
                    if out: add(out,{"machine_type":mid,"machine_name":mname,"inputs":[(inp,rec.get("consume",1))],"output_qty":rec.get("output",1),"time":time_,"power":power,"fuel":None})
                    if rec.get("residue",0)>0:
                        add("residue",{"machine_type":mid,"machine_name":f"{mname} (byproduct)","inputs":[(inp,rec.get("consume",1))],"output_qty":rec.get("residue",0),"time":time_,"power":power,"fuel":None})
            elif pfn=="multi_output":
                rec_inputs=[]
                for port in mdef.get("input_ports",[]):
                    if "items" in port: item=port["items"][0]
                    elif "item" in port: item=port["item"]
                    else: continue
                    buf=port.get("buf","input_buffer"); qty=consume.get(buf,1)
                    rec_inputs.append((item,qty))
                for _,_,out_item,out_amt in proc.get("outputs",[]):
                    add(out_item,{"machine_type":mid,"machine_name":mname,"inputs":rec_inputs,"output_qty":out_amt,"time":time_,"power":power,"fuel":None})
            elif pfn=="mode_recipes":
                modes=proc.get("mode_recipes",{})
                for mode,mrec in modes.items():
                    out_item=mrec.get("produce")
                    if not out_item: continue
                    out_amt=mrec.get("amount",1)
                    if "inputs" in mrec: rec_inputs=list(mrec["inputs"])
                    else:
                        rec_inputs=[]; extra=mrec.get("extra_consume",{})
                        for port in mdef.get("input_ports",[]):
                            if "items" in port: item=port["items"][0]
                            elif "item" in port: item=port["item"]
                            else: continue
                            buf=port.get("buf","input_buffer"); qty=consume.get(buf,0)
                            if buf in extra: qty+=extra[buf]
                            if qty>0: rec_inputs.append((item,qty))
                    add(out_item,{"machine_type":mid,"machine_name":f"{mname} [{mode}]","inputs":rec_inputs,"output_qty":out_amt,"time":time_,"power":power,"fuel":None})
            else:
                out=proc.get("produce")
                if out:
                    qty_in=consume.get("input_buffer",1); rec_inputs=[]; fuel=None
                    for port in mdef.get("input_ports",[]):
                        buf=port.get("buf","input_buffer")
                        if buf=="coal_buffer": fuel=("coal",consume.get("coal_buffer",1)); continue
                        if "items" in port: item=port["items"][0]
                        elif "item" in port: item=port["item"]
                        else: continue
                        qty=consume.get(buf,1)
                        if qty>0: rec_inputs.append((item,qty))
                    add(out,{"machine_type":mid,"machine_name":mname,"inputs":rec_inputs,"output_qty":proc.get("amount",1),"time":time_,"power":power,"fuel":fuel})
        self.rb_recipe_index=idx

    def _draw_recipe_book(self,screen):
        from settings import ITEM_VALUES
        try: from settings import RP_VALUES
        except ImportError: RP_VALUES={}
        if self.rb_recipe_index is None: self._build_recipe_index()
        pw,ph=1100,640; px=(SCREEN_WIDTH-pw)//2; py=(SCREEN_HEIGHT-ph)//2
        dim=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); dim.fill((0,0,0,190)); screen.blit(dim,(0,0))
        panel=pygame.Surface((pw,ph),pygame.SRCALPHA)
        pygame.draw.rect(panel,(14,18,28,248),(0,0,pw,ph),border_radius=16)
        pygame.draw.rect(panel,(95,145,250,255),(0,0,pw,ph),2,border_radius=16)
        screen.blit(panel,(px,py))
        title=self.title_font.render("RECIPE BOOK",True,(155,205,255)); screen.blit(title,title.get_rect(center=(px+pw//2,py+22)))
        sub=self.tiny_font.render("Click a material to view recipes  ·  K or ESC to close",True,(85,108,150)); screen.blit(sub,sub.get_rect(center=(px+pw//2,py+44)))
        pygame.draw.line(screen,(42,58,92),(px+20,py+62),(px+pw-20,py+62),1)
        sb_w,sb_h=260,24; sb_x=px+24; sb_y=py+74
        self.rb_search_rect=pygame.Rect(sb_x,sb_y,sb_w,sb_h)
        mx_p,my_p=pygame.mouse.get_pos(); sb_hov=self.rb_search_rect.collidepoint(mx_p,my_p)
        if self.rb_search_focused: sb_bg,sb_brd=(18,26,44),(120,180,255)
        elif sb_hov: sb_bg,sb_brd=(14,20,32),(80,120,180)
        else: sb_bg,sb_brd=(10,14,22),(45,60,90)
        pygame.draw.rect(screen,sb_bg,self.rb_search_rect,border_radius=6)
        pygame.draw.rect(screen,sb_brd,self.rb_search_rect,1,border_radius=6)
        pygame.draw.circle(screen,(120,160,220),(sb_x+11,sb_y+12),4,1)
        pygame.draw.line(screen,(120,160,220),(sb_x+14,sb_y+15),(sb_x+17,sb_y+18),1)
        placeholder="Search materials..." if not self.rb_search_focused else "Type to filter..."
        shown=self.rb_search_text if self.rb_search_text else placeholder
        text_color=(225,235,250) if self.rb_search_text else (85,100,130)
        screen.blit(self.small_font.render(shown,True,text_color),(sb_x+24,sb_y+4))
        if self.rb_search_focused and (pygame.time.get_ticks()//500)%2==0:
            cursor_x=sb_x+24+self.small_font.size(self.rb_search_text)[0]+1
            pygame.draw.line(screen,(200,220,250),(cursor_x,sb_y+5),(cursor_x,sb_y+sb_h-5),1)
        q=self.rb_search_text.lower().strip()
        filtered=[m for m in self.material_order if q in m.lower().replace("_"," ")] if q else list(self.material_order)
        grid_x=px+24; grid_y=py+110; tile_size=52; tile_gap=8; cols=7
        self.rb_tile_rects={}
        total_rows=(len(filtered)+cols-1)//cols; row_h=tile_size+tile_gap
        total_grid_h=total_rows*row_h; visible_h=py+ph-grid_y-12
        max_scroll=max(0,total_grid_h-visible_h)
        self.rb_grid_scroll=max(0,min(self.rb_grid_scroll,max_scroll)); scroll_off=self.rb_grid_scroll
        grid_clip=pygame.Rect(grid_x-2,grid_y-2,cols*(tile_size+tile_gap)+4,visible_h+4)
        for i,mat in enumerate(filtered):
            col=i%cols; row=i//cols
            tx=grid_x+col*(tile_size+tile_gap); ty=grid_y+row*row_h-scroll_off
            trect=pygame.Rect(tx,ty,tile_size,tile_size); self.rb_tile_rects[mat]=trect
            if ty+tile_size<grid_y-2 or ty>grid_y+visible_h+2: continue
            target=1.0 if trect.collidepoint(mx_p,my_p) and grid_clip.collidepoint(mx_p,my_p) else 0.0
            cur=self.rb_hover_t.get(mat,0.0); self.rb_hover_t[mat]=cur+(target-cur)*0.2
            selected=(self.rb_selected_item==mat)
            if selected: bg_c=(45,85,150,255); brd_c=(120,180,255,255); brd_w=2
            else:
                base=22+int(self.rb_hover_t[mat]*18)
                bg_c=(base,base+4,base+14,255)
                brd_c=(55+int(self.rb_hover_t[mat]*60),70+int(self.rb_hover_t[mat]*80),110+int(self.rb_hover_t[mat]*90),255)
                brd_w=1
            ts=pygame.Surface((tile_size,tile_size),pygame.SRCALPHA)
            pygame.draw.rect(ts,bg_c,(0,0,tile_size,tile_size),border_radius=8)
            pygame.draw.rect(ts,brd_c,(0,0,tile_size,tile_size),brd_w,border_radius=8)
            screen.blit(ts,(tx,ty))
            if self.material_sheet:
                try:
                    orig_idx=self.material_order.index(mat); cs=self.material_cell
                    sprite_rect=pygame.Rect(orig_idx*cs,0,cs,cs)
                    if sprite_rect.right<=self.material_sheet.get_width():
                        scaled=pygame.transform.scale(self.material_sheet.subsurface(sprite_rect),(tile_size-16,tile_size-16))
                        screen.blit(scaled,(tx+8,ty+8))
                except Exception: pass
        if max_scroll>0:
            sb_x2=grid_x+cols*(tile_size+tile_gap)-6; sb_y2=grid_y; sb_h2=visible_h
            thumb_h=max(20,int(sb_h2*visible_h/total_grid_h))
            thumb_y=sb_y2+int((sb_h2-thumb_h)*scroll_off/max_scroll) if max_scroll>0 else sb_y2
            pygame.draw.rect(screen,(30,35,48),(sb_x2,sb_y2,5,sb_h2),border_radius=2)
            pygame.draw.rect(screen,(80,95,130),(sb_x2,thumb_y,5,thumb_h),border_radius=2)
        if q and not filtered:
            nores=self.small_font.render(f"No materials matching '{q}'",True,(120,140,180)); screen.blit(nores,(grid_x,grid_y+20))
        detail_x=grid_x+cols*(tile_size+tile_gap)+12; detail_y=py+110
        detail_w=px+pw-detail_x-24; detail_h=ph-134
        ds=pygame.Surface((detail_w,detail_h),pygame.SRCALPHA)
        pygame.draw.rect(ds,(9,12,20,240),(0,0,detail_w,detail_h),border_radius=10)
        pygame.draw.rect(ds,(40,55,85,255),(0,0,detail_w,detail_h),1,border_radius=10)
        screen.blit(ds,(detail_x,detail_y))
        if self.rb_selected_item is None:
            hint=self.small_font.render("Select a material to view details",True,(95,110,140))
            screen.blit(hint,hint.get_rect(center=(detail_x+detail_w//2,detail_y+detail_h//2))); return
        mat=self.rb_selected_item; dx_=detail_x+12; dy_=detail_y+12
        rb_hover_sprites = []
        def _get_sprite(item_name,size=28):
            if not self.material_sheet or item_name not in self.material_order:
                s=pygame.Surface((size,size),pygame.SRCALPHA); pygame.draw.rect(s,(80,90,110),(0,0,size,size),border_radius=3); return s
            idx=self.material_order.index(item_name); cs=self.material_cell
            if (idx+1)*cs>self.material_sheet.get_width():
                s=pygame.Surface((size,size),pygame.SRCALPHA); pygame.draw.rect(s,(80,90,110),(0,0,size,size),border_radius=3); pygame.draw.rect(s,(140,150,170),(0,0,size,size),1,border_radius=3); return s
            sr=pygame.Rect(idx*cs,0,cs,cs); return pygame.transform.scale(self.material_sheet.subsurface(sr),(size,size))
        hdr_w=detail_w-24; hdr_h=60
        hdr_surf=pygame.Surface((hdr_w,hdr_h),pygame.SRCALPHA)
        pygame.draw.rect(hdr_surf,(18,22,32,250),(0,0,hdr_w,hdr_h),border_radius=8)
        pygame.draw.rect(hdr_surf,(55,68,95),(0,0,hdr_w,hdr_h),1,border_radius=8)
        screen.blit(hdr_surf,(dx_,dy_))
        sprite_big=_get_sprite(mat,44); screen.blit(sprite_big,(dx_+8,dy_+8))
        name_txt=mat.replace("_"," ").title(); screen.blit(self.title_font.render(name_txt,True,(240,245,255)),(dx_+60,dy_+6))
        sell=ITEM_VALUES.get(mat,0); rp=RP_VALUES.get(mat,0)
        sc=(80,235,120) if sell>=0 else (255,110,110)
        sell_str=f"${sell:,.2f}" if abs(sell)<10000 else f"${sell:,.0f}"
        screen.blit(self.small_font.render(sell_str,True,sc),(dx_+60,dy_+28))
        rp_color=(200,180,100) if rp>=10 else (160,180,230)
        screen.blit(self.small_font.render(f"{rp}x RP",True,rp_color),(dx_+160,dy_+28))
        screen.blit(self.tiny_font.render("No description.",True,(80,92,120)),(dx_+60,dy_+44))
        sy=dy_+hdr_h+14; screen.blit(self.small_font.render("Sources",True,(180,200,235)),(dx_,sy)); sy+=20
        recipes=self.rb_recipe_index.get(mat,[])
        if not recipes:
            screen.blit(self.tiny_font.render("No known recipe — extract or purchase.",True,(100,115,145)),(dx_,sy)); return
        row_right_limit=dx_+hdr_w-4
        for rec in recipes:
            row_h2=48; row_w=hdr_w
            row_surf=pygame.Surface((row_w,row_h2),pygame.SRCALPHA)
            pygame.draw.rect(row_surf,(22,26,36,250),(0,0,row_w,row_h2),border_radius=6)
            pygame.draw.rect(row_surf,(50,58,78),(0,0,row_w,row_h2),1,border_radius=6)
            screen.blit(row_surf,(dx_,sy)); rx=dx_+6; ry_center=sy+row_h2//2
            inputs_all=list(rec["inputs"])
            if rec.get("fuel"): inputs_all.append(rec["fuel"])
            max_inputs_section=row_right_limit-rx-180; input_slot_w=36
            max_inputs=max(1,min(len(inputs_all),max_inputs_section//(input_slot_w+10)))
            shown_inputs=inputs_all[:max_inputs]; overflow=len(inputs_all)>max_inputs
            for j,(inp,qty) in enumerate(shown_inputs):
                if j>0:
                    plus=self.tiny_font.render("+",True,(140,150,175)); screen.blit(plus,(rx,ry_center-6)); rx+=10
                qty_str=f"{qty}x" if qty==int(qty) else f"{qty:.1f}x"
                ql=self.tiny_font.render(qty_str,True,(180,190,210)); screen.blit(ql,(rx,sy+2))
                isp=_get_sprite(inp,24); screen.blit(isp,(rx,sy+14))
                rb_hover_sprites.append((pygame.Rect(rx, sy+14, 24, 24), inp))
                rx+=26
            if overflow:
                ov_s=self.tiny_font.render(f"+{len(inputs_all)-max_inputs}",True,(150,160,185)); screen.blit(ov_s,(rx+2,ry_center-5)); rx+=18
            rx+=2; time_s=rec["time"]; power_w=rec["power"]
            pstr=f"{power_w/1000:.0f}kME" if power_w>=1000 else f"{power_w}ME"
            time_txt=self.tiny_font.render(f"{time_s:.0f}s",True,(220,230,250))
            pow_txt=self.tiny_font.render(pstr,True,(140,155,185))
            tw=max(time_txt.get_width(),pow_txt.get_width()); arr_x_start=rx; arr_x_end=rx+tw+10
            if arr_x_end>row_right_limit-60: arr_x_end=row_right_limit-60
            arr_y=ry_center
            if arr_x_end>arr_x_start+8:
                pygame.draw.line(screen,(120,140,180),(arr_x_start,arr_y),(arr_x_end,arr_y),2)
                pygame.draw.polygon(screen,(120,140,180),[(arr_x_end,arr_y),(arr_x_end-5,arr_y-4),(arr_x_end-5,arr_y+4)])
                screen.blit(time_txt,(rx+2,sy+4)); screen.blit(pow_txt,(rx+2,sy+28))
            rx=arr_x_end+4
            oqty=rec["output_qty"]; oq_str=f"{oqty}x" if oqty==int(oqty) else f"{oqty:.1f}x"
            oql=self.tiny_font.render(oq_str,True,(180,220,180))
            if rx+28<=row_right_limit:
                screen.blit(oql,(rx,sy+2)); osp=_get_sprite(mat,24); screen.blit(osp,(rx,sy+14))
                rb_hover_sprites.append((pygame.Rect(rx, sy+14, 24, 24), mat))
                rx+=28
            mname=f"({rec['machine_name']})"; mn_surf=self.tiny_font.render(mname,True,(145,160,195))
            avail=row_right_limit-rx-2
            if avail>12: screen.blit(mn_surf,(rx+2,ry_center-6),pygame.Rect(0,0,min(mn_surf.get_width(),avail),mn_surf.get_height()))
            sy+=row_h2+4
            if sy>detail_y+detail_h-100: break
        sy+=10
        if sy<detail_y+detail_h-60:
            used_in=[]
            for out_item,recs in self.rb_recipe_index.items():
                for rec in recs:
                    for inp in rec.get("inputs",[]):
                        inp_name=inp[0] if isinstance(inp,(list,tuple)) else inp
                        if inp_name==mat: used_in.append((out_item,rec["machine_name"])); break
            if used_in:
                screen.blit(self.small_font.render("Used In",True,(200,180,140)),(dx_,sy)); sy+=20
                for out_item,mname in used_in:
                    if sy>detail_y+detail_h-30:
                        more=self.tiny_font.render(f"  +{len(used_in)-used_in.index((out_item,mname))} more...",True,(90,100,120)); screen.blit(more,(dx_,sy)); break
                    out_name=out_item.replace("_"," ").title()
                    osp=_get_sprite(out_item,18); screen.blit(osp,(dx_+4,sy))
                    rb_hover_sprites.append((pygame.Rect(dx_+4, sy, 18, 18), out_item))
                    txt=self.tiny_font.render(f"{out_name}  ({mname})",True,(150,165,195))
                    avail_w=hdr_w-30; clip=pygame.Rect(0,0,min(txt.get_width(),avail_w),txt.get_height())
                    screen.blit(txt,(dx_+26,sy+2),clip); sy+=22

        mx_, my_ = pygame.mouse.get_pos()
        hovered_item = None
        for rect, item_name in self.rb_tile_rects.items():
            pass
        for item_name, rect in self.rb_tile_rects.items():
            if rect.collidepoint(mx_, my_):
                hovered_item = item_name; break
        if hovered_item is None:
            for rect, item_name in rb_hover_sprites:
                if rect.collidepoint(mx_, my_):
                    hovered_item = item_name; break
        if hovered_item is not None:
            pretty = hovered_item.replace("_", " ").title()
            sell = ITEM_VALUES.get(hovered_item, 0)
            rp_v = RP_VALUES.get(hovered_item, 0)
            line1 = self.small_font.render(pretty, True, (245, 245, 255))
            sell_color = (110, 240, 130) if sell >= 0 else (255, 100, 100)
            sell_text = f"${sell:,.2f}" if abs(sell) < 10000 else f"${sell:,.0f}"
            line2 = self.tiny_font.render(f"Sells {sell_text}   {rp_v}× RP",
                                          True, sell_color)
            tw = max(line1.get_width(), line2.get_width()) + 16
            th = line1.get_height() + line2.get_height() + 12
            tx = mx_ + 14
            ty = my_ + 12
            if tx + tw > SCREEN_WIDTH - 4: tx = mx_ - tw - 10
            if ty + th > SCREEN_HEIGHT - 4: ty = mx_ - th - 4
            bg = pygame.Surface((tw, th), pygame.SRCALPHA)
            pygame.draw.rect(bg, (12, 14, 22, 235), (0, 0, tw, th), border_radius=6)
            pygame.draw.rect(bg, (90, 110, 150, 255), (0, 0, tw, th), 1, border_radius=6)
            screen.blit(bg, (tx, ty))
            screen.blit(line1, (tx + 8, ty + 6))
            screen.blit(line2, (tx + 8, ty + 6 + line1.get_height() + 2))


    def _draw_keybind_overlay(self,screen):
        bindings=[("B","Build panel"),("C","Contracts"),("T","Research / Confirm place"),
                  ("N","Statistics panel"),("M","Market prices (S&D)"),("P","Power mode"),
                  ("X","Delete mode"),("Z","Debug view"),
                  ("O","Bottleneck overlay"),("G","Blueprint copy/paste"),
                  ("R","Rotate building"),("`","Code console"),("Fn","Settings"),("?","This cheatsheet (hold)"),
                  ("",""),("Ctrl+S","Manual save"),("Ctrl+C","Copy machine settings"),
                  ("Ctrl+V","Paste machine settings"),("ESC","Close panel / cancel"),
                  ("WASD","Pan camera"),("Scroll","Zoom"),("L-click","Place / select"),
                  ("R-click","Select (no place)"),("Shift","Place multiple"),
                  ("Drag","Lay pipes along path (pipe tool)")]
        col_count=2; rows_per_col=(len(bindings)+col_count-1)//col_count; row_h=20; col_w=260
        pw=col_w*col_count+40; ph=rows_per_col*row_h+70
        px=(SCREEN_WIDTH-pw)//2; py=(SCREEN_HEIGHT-ph)//2
        dim=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); dim.fill((0,0,0,160)); screen.blit(dim,(0,0))
        o=pygame.Surface((pw,ph),pygame.SRCALPHA)
        pygame.draw.rect(o,(12,14,22,240),(0,0,pw,ph),border_radius=14)
        pygame.draw.rect(o,(95,145,250,255),(0,0,pw,ph),2,border_radius=14)
        screen.blit(o,(px,py))
        title=self.title_font.render("KEYBIND REFERENCE",True,(135,195,255)); screen.blit(title,title.get_rect(center=(px+pw//2,py+20)))
        sub=self.tiny_font.render("Release ? to dismiss",True,(68,92,130)); screen.blit(sub,sub.get_rect(center=(px+pw//2,py+38)))
        pygame.draw.line(screen,(42,58,92),(px+20,py+50),(px+pw-20,py+50),1)
        for i,(key,desc) in enumerate(bindings):
            col=i//rows_per_col; row=i%rows_per_col
            bx=px+20+col*col_w; by=py+60+row*row_h
            if not key: continue
            ks=self.tiny_font.render(key,True,(180,210,255)); kw=max(ks.get_width()+10,44)
            pygame.draw.rect(screen,(22,32,54),(bx,by,kw,16),border_radius=4)
            pygame.draw.rect(screen,(60,100,170),(bx,by,kw,16),1,border_radius=4)
            screen.blit(ks,(bx+(kw-ks.get_width())//2,by+2))
            ds=self.small_font.render(desc,True,(170,182,210)); screen.blit(ds,(bx+kw+10,by+1))

    def draw_info_panel(self,screen):
        if not self.selected_tile: return
        tile_data,gx,gy=self.selected_tile; tile_type=tile_data["type"]
        if tile_type==0: return
        pw=240; ph=min(360,SCREEN_HEIGHT-20); panel_x=SCREEN_WIDTH-pw-10; panel_y=10
        self.info_panel_rect=pygame.Rect(panel_x,panel_y,pw,ph)
        s=pygame.Surface((pw,ph),pygame.SRCALPHA)
        pygame.draw.rect(s,(13,15,21,220),(0,0,pw,ph),border_radius=8)
        pygame.draw.rect(s,(48,52,68,255),(0,0,pw,ph),1,border_radius=8)
        screen.blit(s,(panel_x,panel_y))
        mi=MACHINE_STATS.get(tile_type,{}); mn=mi.get("name","Unknown"); mc=mi.get("cost",0)
        y=panel_y+10
        if tile_type!=16: self.recipe_btn_rects={}
        if tile_type not in (131, 124, 130):
            self.tile_ctrl_btn_rects = {}
        screen.blit(self.title_font.render(mn,True,(252,212,85)),(panel_x+10,y)); y+=22
        pygame.draw.line(screen,(52,56,72),(panel_x+10,y),(panel_x+pw-10,y),1); y+=8
        screen.blit(self.tiny_font.render(f"({gx},{gy})  rot:{tile_data.get('rotation',0)}",True,(115,122,145)),(panel_x+10,y)); y+=16
        screen.blit(self.tiny_font.render(f"Cost ${mc}  |  Sell ${mc*0.8:.0f}",True,(148,155,178)),(panel_x+10,y)); y+=16
        _sz = mi.get("size",(1,1))
        if _sz != (1,1):
            screen.blit(self.tiny_font.render(f"Size: {_sz[0]}x{_sz[1]}",True,(135,148,175)),(panel_x+10,y)); y+=14
        from settings import POLLUTION_PER_MACHINE as _PPM
        _pol = _PPM.get(tile_type, 0)
        if _pol > 0:
            screen.blit(self.tiny_font.render(f"Pollution: +{_pol*3600:.3f}%/h",True,(235,140,90)),(panel_x+10,y)); y+=14
        elif tile_type in (11, 24, 25, 26, 27, 28):
            screen.blit(self.tiny_font.render("Pollution: 0 (clean)",True,(120,230,140)),(panel_x+10,y)); y+=14
        _stall = machine_stall_reason(tile_data, tile_type)
        if _stall:
            _stxt, _scol = _stall
            pygame.draw.circle(screen, _scol, (panel_x+16, y+8), 4)
            screen.blit(self.small_font.render(_stxt, True, _scol), (panel_x+26, y)); y += 18
        y += 4
        if mi.get("power_output",0)>0 or mi.get("power_input",0)>0 or mi.get("power_capacity",0)>0:
            screen.blit(self.title_font.render("POWER",True,(250,194,45)),(panel_x+10,y)); y+=18
            pw_=tile_data.get("power",0); mp_=tile_data.get("max_power",0)
            screen.blit(self.tiny_font.render(f"{_fmt_me(pw_)} / {_fmt_me(mp_)}",True,(150,158,192)),(panel_x+10,y)); y+=14
            bw_=pw-20; bh_=10
            pygame.draw.rect(screen,(16,16,20),(panel_x+10,y,bw_,bh_),border_radius=3)
            pygame.draw.rect(screen,(42,46,56),(panel_x+10,y,bw_,bh_),1,border_radius=3)
            if mp_>0:
                r_=pw_/mp_; fw_=int(bw_*r_)
                if fw_>0:
                    t__=self.power_anim_time
                    if r_>0.6: bc__,br__=(55,185,65),(110,255,120)
                    elif r_>0.3: bc__,br__=(195,145,20),(255,210,60)
                    else: bc__,br__=(185,55,55),(255,100,100)
                    p__=0.5+0.5*_math.sin(t__*_math.pi*3)
                    bc2=(int(bc__[0]+(br__[0]-bc__[0])*p__),int(bc__[1]+(br__[1]-bc__[1])*p__),int(bc__[2]+(br__[2]-bc__[2])*p__))
                    pygame.draw.rect(screen,bc2,(panel_x+10,y,fw_,bh_),border_radius=3)
            y+=15
            if mi.get("power_output",0)>0: screen.blit(self.tiny_font.render(f"Out: {_fmt_me(mi['power_output'])}/s",True,(135,235,135)),(panel_x+10,y)); y+=14
            if mi.get("power_input",0)>0: screen.blit(self.tiny_font.render(f"Needs: {_fmt_me(mi['power_input'])}/s",True,(252,172,70)),(panel_x+10,y)); y+=14
            if tile_data.get("power_connections"): screen.blit(self.tiny_font.render(f"Connections: {len(tile_data['power_connections'])}",True,(135,190,252)),(panel_x+10,y)); y+=14
            y+=4
        if tile_type in (3, 83, 85, 51, 84):
            hdr = self.title_font.render("DEPOT", True, (130, 220, 140))
            screen.blit(hdr, (panel_x + 10, y)); y += 18
            is_fluid = tile_type in (51, 84)
            cap = mi.get("sell_capacity", mi.get("capacity", 10))
            cd_max = mi.get("cooldown_time", 15.0)
            bonus = mi.get("sell_bonus", 1.0)
            thresh = mi.get("sell_threshold", 1.0)
            sell_at = max(1, cap * thresh)

            if is_fluid:
                amt = tile_data.get("input_buffer", 0)
                stored = tile_data.get("input_item")
            else:
                amt = tile_data.get("amount", 0)
                stored = tile_data.get("stored")
            label = stored.replace("_", " ").title() if stored else "empty"
            screen.blit(self.tiny_font.render(
                f"{label}: {amt:.0f}/{cap:.0f}  (sells at {sell_at:.0f})",
                True, (165, 230, 175)), (panel_x + 10, y))
            y += 14
            bw = pw - 20; bh = 8
            pygame.draw.rect(screen, (16, 22, 18), (panel_x + 10, y, bw, bh), border_radius=3)
            if cap > 0:
                fill = int(bw * min(amt / cap, 1.0))
                if fill > 0:
                    fill_col = (90, 220, 110) if amt >= sell_at else (200, 180, 70)
                    pygame.draw.rect(screen, fill_col, (panel_x + 10, y, fill, bh), border_radius=3)
                tx = panel_x + 10 + int(bw * thresh)
                pygame.draw.line(screen, (255, 255, 255), (tx, y - 1), (tx, y + bh + 1), 1)
            y += bh + 6

            cd = tile_data.get("cooldown_timer", 0.0)
            cd_label = f"Cooldown: {cd:.1f}s / {cd_max:.0f}s" if cd > 0 else f"Ready (cooldown {cd_max:.0f}s)"
            cd_col = (255, 170, 90) if cd > 0 else (130, 220, 140)
            screen.blit(self.tiny_font.render(cd_label, True, cd_col), (panel_x + 10, y))
            y += 14
            pygame.draw.rect(screen, (24, 18, 14), (panel_x + 10, y, bw, bh), border_radius=3)
            if cd_max > 0 and cd > 0:
                cd_fill = int(bw * (cd / cd_max))
                pygame.draw.rect(screen, (220, 150, 70), (panel_x + 10, y, cd_fill, bh), border_radius=3)
            y += bh + 4

            if bonus != 1.0:
                pct = int((bonus - 1.0) * 100)
                screen.blit(self.tiny_font.render(
                    f"Sale bonus: +{pct}%", True, (255, 215, 90)),
                    (panel_x + 10, y))
                y += 14
            total_sold = tile_data.get("total_sold", 0)
            if total_sold:
                screen.blit(self.tiny_font.render(
                    f"Lifetime sold: {total_sold}", True, (170, 180, 200)),
                    (panel_x + 10, y))
                y += 14
            fr = pygame.Rect(panel_x + 10, y, pw - 20, 20)
            self.tile_ctrl_btn_rects["flush_depot"] = fr
            pygame.draw.rect(screen, (52, 30, 22), fr, border_radius=4)
            pygame.draw.rect(screen, (220, 140, 80), fr, 1, border_radius=4)
            ft = self.tiny_font.render("FLUSH CARGO (void contents)", True, (240, 175, 110))
            screen.blit(ft, ft.get_rect(center=fr.center))
            y += 24
            y += 6

        if tile_type in (131, 124, 130):
            self.tile_ctrl_btn_rects = {}
            cap = mi.get("capacity", 6)
            hdr = self.title_font.render("LANES", True, (140, 200, 255))
            screen.blit(hdr, (panel_x + 10, y)); y += 18
            btn_w, btn_h = pw - 20, 22
            for lane_key, lane_label in (("lane_v", "Vertical  (↑↓)"),
                                          ("lane_h", "Horizontal (←→)")):
                enabled = tile_data.get(f"{lane_key}_enabled", True)
                amt     = tile_data.get(f"{lane_key}_amount", 0)
                stored  = tile_data.get(f"{lane_key}_stored")
                r = pygame.Rect(panel_x + 10, y, btn_w, btn_h)
                self.tile_ctrl_btn_rects[f"{lane_key}_toggle"] = r
                bg  = (28, 52, 32) if enabled else (52, 28, 28)
                brd = (110, 220, 140) if enabled else (220, 110, 110)
                pygame.draw.rect(screen, bg, r, border_radius=4)
                pygame.draw.rect(screen, brd, r, 1, border_radius=4)
                tc = (190, 240, 200) if enabled else (240, 190, 190)
                label = f"{lane_label}  [{'ON' if enabled else 'OFF'}]"
                screen.blit(self.small_font.render(label, True, tc), (r.x + 8, r.y + 4))
                y += btn_h + 2
                if stored and amt > 0:
                    txt = f"{stored.replace('_',' ').title()}: {amt}/{cap}"
                else:
                    txt = f"empty   0/{cap}"
                screen.blit(self.tiny_font.render(txt, True, (150, 165, 200)),
                            (panel_x + 18, y))
                y += 14
            y += 6

        if tile_type==13:
            from research import RP_VALUES
            screen.blit(self.title_font.render("RESEARCH FEED",True,(178,128,252)),(panel_x+10,y)); y+=18
            in_buf=tile_data.get("input_buffer",0); in_item=tile_data.get("input_item")
            stats13=MACHINE_STATS.get(13,{}); cap13=10.0
            for port in MACHINE_DEFS.get(13,{}).get("input_ports",[]):
                cap13=port.get("cap",10.0); break
            if in_item and in_buf>0:
                rpx=RP_VALUES.get(in_item,1.0); per_i=stats13.get("rp_per_item",5.0)*rpx; cyc=stats13.get("item_cycle_time",2.0); rate=per_i/cyc
                screen.blit(self.small_font.render(f"{in_item.replace('_',' ').title()}: {in_buf:.1f}/{cap13:.0f}",True,(200,160,255)),(panel_x+10,y)); y+=14
                screen.blit(self.tiny_font.render(f"RPx: {rpx:.1f}  |  {per_i:.1f} RP/item  |  {rate:.1f} RP/s",True,(150,115,200)),(panel_x+10,y)); y+=14
                bw_=pw-20; bh_=8
                pygame.draw.rect(screen,(20,18,30),(panel_x+10,y,bw_,bh_),border_radius=2)
                fw_=int(bw_*min(in_buf/cap13,1.0))
                if fw_>0: pygame.draw.rect(screen,(140,90,220),(panel_x+10,y,fw_,bh_),border_radius=2)
                y+=12
            else:
                screen.blit(self.small_font.render("No item feed",True,(90,80,120)),(panel_x+10,y)); y+=14
                screen.blit(self.tiny_font.render("Pipe in items for bonus RP. Higher RPx = more RP.",True,(70,60,95)),(panel_x+10,y)); y+=14
            y+=6
        if tile_type not in [11,12,13]:
            th_=MACHINE_THEMES.get(tile_type,DEFAULT_THEME); mdef=MACHINE_DEFS.get(tile_type)
            if mdef and mdef.get("drill") and "resources" in mdef:
                screen.blit(self.title_font.render("RESOURCE",True,(185,192,212)),(panel_x+10,y)); y+=16
                cur_mode=tile_data.get("recipe_mode"); self.recipe_btn_rects={}
                btn_w=pw-20; btn_h=20
                for rkey in mdef["resources"]:
                    r=pygame.Rect(panel_x+10,y,btn_w,btn_h); self.recipe_btn_rects[rkey]=r
                    active=(cur_mode==rkey) or (cur_mode is None and rkey==mdef["resources"][0])
                    pygame.draw.rect(screen,(32,52,32) if active else (22,22,28),r,border_radius=4)
                    pygame.draw.rect(screen,(120,220,120) if active else (55,60,72),r,1,border_radius=4)
                    tc=(180,240,180) if active else (110,115,130)
                    ts=self.small_font.render(rkey.replace("_"," ").title(),True,tc); screen.blit(ts,(panel_x+20,y+3)); y+=btn_h+3
                y+=6
            if mdef and not mdef.get("drill"):
                proc=mdef.get("process",{}); mr=proc.get("mode_recipes")
                if mr:
                    screen.blit(self.title_font.render("RECIPE MODE",True,(185,192,212)),(panel_x+10,y)); y+=16
                    cur_mode=tile_data.get("recipe_mode",proc.get("default_mode","")); self.recipe_btn_rects={}
                    btn_w=pw-20; btn_h=20
                    for rkey in mr.keys():
                        r=pygame.Rect(panel_x+10,y,btn_w,btn_h); self.recipe_btn_rects[rkey]=r
                        active=(cur_mode==rkey)
                        pygame.draw.rect(screen,(32,42,52) if active else (22,22,28),r,border_radius=4)
                        pygame.draw.rect(screen,(100,160,230) if active else (55,60,72),r,1,border_radius=4)
                        tc=(160,210,255) if active else (110,115,130)
                        out_item=mr[rkey].get("produce",rkey)
                        label=f"{rkey.replace('_',' ').title()} → {out_item.replace('_',' ').title()}"
                        ts=self.small_font.render(label,True,tc); screen.blit(ts,(panel_x+20,y+3)); y+=btn_h+3
                    y+=6
            if mdef and ("input_ports" in mdef or "output_port" in mdef) and not mdef.get("fluid_producer") and not mdef.get("diesel_gen"):
                if tile_type==16:
                    from settings import REFINERY_RECIPES
                    screen.blit(self.title_font.render("RECIPE",True,(185,192,212)),(panel_x+10,y)); y+=16
                    cur_mode=tile_data.get("recipe_mode"); self.recipe_btn_rects={}
                    recipes=[("crude_oil","Crude → PQD"),("poor_quality_diesel","PQD → Diesel"),("diesel","Diesel → Rfnd")]
                    btn_w=pw-20; btn_h=20
                    for rkey,rlabel in recipes:
                        r=pygame.Rect(panel_x+10,y,btn_w,btn_h); self.recipe_btn_rects[rkey]=r
                        active=(cur_mode==rkey) or (cur_mode is None and rkey=="crude_oil")
                        pygame.draw.rect(screen,(52,28,80) if active else (22,20,32),r,border_radius=4)
                        pygame.draw.rect(screen,(160,90,240) if active else (55,50,72),r,1,border_radius=4)
                        tc=(200,160,255) if active else (100,95,125)
                        ls=self.tiny_font.render(rlabel,True,tc); screen.blit(ls,(r.x+r.w//2-ls.get_width()//2,r.y+3)); y+=btn_h+3
                    y+=4
                screen.blit(self.title_font.render("BUFFERS",True,(185,192,212)),(panel_x+10,y)); y+=18

                def _pretty(name):
                    return name.replace("_", " ").title() if name else ""
                def _port_label(port, current_item):
                    if current_item:
                        return _pretty(current_item)
                    if port.get("item"):
                        return _pretty(port["item"])
                    items = port.get("items") or []
                    if items:
                        return " / ".join(_pretty(i) for i in items)
                    buf_name = port.get("buf", "")
                    if buf_name.endswith("_buffer"):
                        return _pretty(buf_name[:-7])
                    return _pretty(buf_name) or "Input"

                _seen_bufs = set()
                for port in mdef.get("input_ports",[]):
                    buf_key = port["buf"]
                    if buf_key in _seen_bufs:
                        continue
                    _seen_bufs.add(buf_key)
                    buf_val=tile_data.get(buf_key,0); buf_cap=port["cap"]
                    col=th_[4] if buf_val>0 else (90,95,115)
                    in_item=tile_data.get(port.get("item_buf","input_item"))
                    disp_label = _port_label(port, in_item) + ": "
                    screen.blit(self.small_font.render(f"{disp_label}{buf_val:.2f}/{buf_cap}",True,col),(panel_x+10,y)); y+=15
                    bw_=pw-20; bh_=6
                    pygame.draw.rect(screen,(20,20,26),(panel_x+10,y,bw_,bh_),border_radius=2)
                    if buf_cap>0 and buf_val>0:
                        fw_=int(bw_*min(buf_val/buf_cap,1.0)); pygame.draw.rect(screen,th_[3],(panel_x+10,y,fw_,bh_),border_radius=2)
                    y+=9
                oport=mdef.get("output_port")
                if oport:
                    buf_val=tile_data.get(oport["buf"],0); buf_cap=oport["cap"]
                    item=tile_data.get(oport.get("item_buf","output_item"))
                    if item:
                        label2 = _pretty(item)
                    else:
                        proc = mdef.get("process", {}) or {}
                        if proc.get("produce"):
                            label2 = _pretty(proc["produce"])
                        elif proc.get("recipe_map"):
                            outs = sorted({v[0] for v in proc["recipe_map"].values() if isinstance(v, tuple) and v})
                            label2 = " / ".join(_pretty(o) for o in outs) if outs else "—"
                        elif proc.get("mode_recipes"):
                            outs = sorted({m.get("produce", "") for m in proc["mode_recipes"].values() if m.get("produce")})
                            label2 = " / ".join(_pretty(o) for o in outs) if outs else "—"
                        else:
                            label2 = "—"
                    col=(100,235,110) if buf_val>0 else (90,95,115)
                    screen.blit(self.small_font.render(f"Out ({label2}): {buf_val:.2f}/{buf_cap}",True,col),(panel_x+10,y)); y+=15
                    bw_=pw-20; bh_=6
                    pygame.draw.rect(screen,(20,20,26),(panel_x+10,y,bw_,bh_),border_radius=2)
                    if buf_cap>0 and buf_val>0:
                        fw_=int(bw_*min(buf_val/buf_cap,1.0)); pygame.draw.rect(screen,(80,220,90),(panel_x+10,y,fw_,bh_),border_radius=2)
                    y+=11
                oport2=mdef.get("output_port2")
                if oport2:
                    res_val=tile_data.get(oport2["buf"],0); res_cap=oport2["cap"]
                    col=(220,80,80) if res_val>0 else (90,95,115)
                    screen.blit(self.small_font.render(f"Residue: {res_val:.3f}/{res_cap}",True,col),(panel_x+10,y)); y+=15
                    bw_=pw-20; bh_=6
                    pygame.draw.rect(screen,(20,20,26),(panel_x+10,y,bw_,bh_),border_radius=2)
                    if res_cap>0 and res_val>0:
                        fw_=int(bw_*min(res_val/res_cap,1.0)); pygame.draw.rect(screen,(200,70,70),(panel_x+10,y,fw_,bh_),border_radius=2)
                    y+=11
                cbr = pygame.Rect(panel_x+10, y, pw-20, 18)
                self.tile_ctrl_btn_rects["clear_buffers"] = cbr
                pygame.draw.rect(screen, (46, 28, 24), cbr, border_radius=4)
                pygame.draw.rect(screen, (200, 130, 90), cbr, 1, border_radius=4)
                cbt = self.tiny_font.render("CLEAR BUFFERS (void contents)", True, (235, 170, 115))
                screen.blit(cbt, cbt.get_rect(center=cbr.center))
                y += 22
                proc=mdef.get("process",{})
                if proc:
                    in_item=tile_data.get("input_item","")
                    if in_item and tile_type==16:
                        from settings import REFINERY_RECIPES
                        recipe=REFINERY_RECIPES.get(in_item)
                        if recipe:
                            screen.blit(self.tiny_font.render(f"{in_item.replace('_',' ').title()} → {recipe['produce'].replace('_',' ').title()}",True,th_[4]),(panel_x+10,y)); y+=13
                    screen.blit(self.title_font.render("PROCESSING",True,(185,192,212)),(panel_x+10,y)); y+=14
                    bw_=pw-20; bh_=10
                    pygame.draw.rect(screen,(20,20,24),(panel_x+10,y,bw_,bh_),border_radius=3)
                    pygame.draw.rect(screen,(52,56,68),(panel_x+10,y,bw_,bh_),1,border_radius=3)
                    pt_=proc.get("time",5.0); prog_=min(tile_data.get("timer",0)/pt_,1.0) if pt_>0 else 0
                    fw_=int(bw_*prog_)
                    if fw_>0: pygame.draw.rect(screen,th_[3],(panel_x+10,y,fw_,bh_),border_radius=3)
                    screen.blit(self.tiny_font.render(f"{int(prog_*100)}%",True,(195,202,222)),(panel_x+10+bw_//2-12,y+1)); y+=14
            elif mdef and mdef.get("fluid_producer"):
                screen.blit(self.title_font.render("PRODUCTION",True,th_[4]),(panel_x+10,y)); y+=18
                fluid=tile_data.get("fluid_buffer",0.0); cap=mdef.get("cap",10.0); rate=mdef.get("rate",0.12)
                col=(80,150,220) if fluid>0 else (90,95,115)
                screen.blit(self.small_font.render(f"{mdef.get('resource','Fluid')}: {fluid:.2f}/{cap:.0f}",True,col),(panel_x+10,y)); y+=15
                bw_=pw-20; bh_=10
                pygame.draw.rect(screen,(20,20,26),(panel_x+10,y,bw_,bh_),border_radius=3)
                if fluid>0:
                    fw_=int(bw_*min(fluid/cap,1.0)); pygame.draw.rect(screen,th_[3],(panel_x+10,y,fw_,bh_),border_radius=3)
                y+=14
                screen.blit(self.tiny_font.render(f"Rate: {rate} units/s",True,(135,148,175)),(panel_x+10,y)); y+=13
            elif mdef and mdef.get("diesel_gen"):
                from settings import DIESEL_GEN_OUTPUT
                screen.blit(self.title_font.render("FUEL",True,th_[4]),(panel_x+10,y)); y+=18
                fuel=tile_data.get("fuel_buffer",0.0); fitem=tile_data.get("fuel_item")
                fuel_cap=MACHINE_STATS.get(17,{}).get("fuel_capacity",10.0)
                col=th_[4] if fuel>0 else (90,95,115); fname=fitem.replace("_"," ").title() if fitem else "Empty"
                screen.blit(self.small_font.render(f"{fname}: {fuel:.2f}/{fuel_cap:.0f}",True,col),(panel_x+10,y)); y+=15
                bw_=pw-20; bh_=10
                pygame.draw.rect(screen,(20,20,26),(panel_x+10,y,bw_,bh_),border_radius=3)
                if fuel>0:
                    fw_=int(bw_*min(fuel/fuel_cap,1.0)); pygame.draw.rect(screen,th_[3],(panel_x+10,y,fw_,bh_),border_radius=3)
                y+=14
                if fitem:
                    out_me=DIESEL_GEN_OUTPUT.get(fitem,0)
                    screen.blit(self.tiny_font.render(f"Output: {_fmt_me(out_me)}/s  |  Burn: 0.1/s",True,(165,175,200)),(panel_x+10,y)); y+=13
            else:
                screen.blit(self.title_font.render("STORAGE",True,(185,192,212)),(panel_x+10,y)); y+=18
                stored=tile_data.get("stored",None); amount=tile_data.get("amount",0); cap=mi.get("capacity",0)
                if cap:
                    screen.blit(self.small_font.render(f"{stored or 'Empty'}: {amount}/{cap}",True,th_[4]),(panel_x+10,y)); y+=16
                if stored and amount>0:
                    worth=amount*ITEM_VALUES.get(stored,0)
                    screen.blit(self.tiny_font.render(f"Worth: ${worth:,.2f}",True,(95,210,105)),(panel_x+10,y)); y+=14
                if tile_type in [2,8]:
                    screen.blit(self.title_font.render("PRODUCTION",True,(185,192,212)),(panel_x+10,y)); y+=16
                    bw_=pw-20; bh_=10
                    pygame.draw.rect(screen,(20,20,24),(panel_x+10,y,bw_,bh_),border_radius=3)
                    pygame.draw.rect(screen,(52,56,68),(panel_x+10,y,bw_,bh_),1,border_radius=3)
                    pt_={2:2.0,8:15.0}.get(tile_type,2.0); prog_=min(tile_data.get("timer",0)/pt_,1.0)
                    fw_=int(bw_*prog_)
                    if fw_>0: pygame.draw.rect(screen,th_[3],(panel_x+10,y,fw_,bh_),border_radius=3)
                    screen.blit(self.tiny_font.render(f"{int(prog_*100)}%",True,(195,202,222)),(panel_x+10+bw_//2-12,y+1)); y+=14
                if tile_type==3:
                    y+=4
                    screen.blit(self.tiny_font.render(f"Total sold: {tile_data.get('total_sold',0)}",True,(135,145,168)),(panel_x+10,y)); y+=14
                    cd=tile_data.get("cooldown_timer",0.0)
                    if cd>0: screen.blit(self.tiny_font.render(f"Cooldown: {cd:.1f}s",True,(252,140,70)),(panel_x+10,y))

        from settings import MACHINE_DEFS as _MDEFS2
        _mdef_g = _MDEFS2.get(tile_type, {})
        if _mdef_g.get("logic_gate"):
            y += 6
            screen.blit(self.title_font.render("SIGNAL GATE", True, (80, 255, 200)), (panel_x+10, y)); y += 18
            gtype_s = _mdef_g.get("gate_type", "?")
            gout = tile_data.get("gate_output", "—")
            ginputs = tile_data.get("signal_inputs", [])
            goutputs = tile_data.get("signal_outputs", [])
            out_col = (80, 255, 150) if gout == 1 else (235, 80, 60) if gout == 0 else (150, 150, 150)
            screen.blit(self.small_font.render(f"Type: {gtype_s}", True, (200, 210, 230)), (panel_x+10, y)); y += 15
            screen.blit(self.small_font.render(f"Output: {gout}", True, out_col), (panel_x+10, y)); y += 15
            screen.blit(self.tiny_font.render(f"Inputs:  {len(ginputs)} wired", True, (130, 200, 170)), (panel_x+10, y)); y += 13
            screen.blit(self.tiny_font.render(f"Outputs: {len(goutputs)} wired", True, (130, 200, 170)), (panel_x+10, y)); y += 13
            screen.blit(self.tiny_font.render("[G] to enter signal wire mode", True, (80, 140, 120)), (panel_x+10, y))

        if tile_type in (22, 23, 94, 95):
            sv = tile_data.get("signal_value")
            if sv is not None:
                y += 6
                sv_col = (80, 255, 150) if sv == 1 else (180, 180, 180)
                screen.blit(self.tiny_font.render(
                    f"Signal: {'FULL (1)' if sv==1 else 'NOT FULL (0)'}",
                    True, sv_col), (panel_x+10, y))

    def draw_contracts_overlay(self,screen,money):
        pw=620; ph=500; px=(SCREEN_WIDTH-pw)//2; py=(SCREEN_HEIGHT-ph)//2
        self.contracts_panel_rect=pygame.Rect(px,py,pw,ph)
        dim=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); dim.fill((0,0,0,165)); screen.blit(dim,(0,0))
        pygame.draw.rect(screen,(20,24,34),(px,py,pw,ph),border_radius=12)
        pygame.draw.rect(screen,(82,125,180),(px,py,pw,ph),2,border_radius=12)
        screen.blit(self.title_font.render("CONTRACTS",True,(135,192,252)),(px+18,py+13))
        screen.blit(self.tiny_font.render("[C] / [ESC] Close",True,(96,104,126)),(px+pw-125,py+15))
        acs = self.contracts.get_active_contracts()
        screen.blit(self.small_font.render(
            f"{len(acs)} active  |  {len(self.contracts.completed)} completed",
            True, (155,164,188)), (px+18, py+33))
        cy_s=py+54; ch_=ph-62
        clip_=pygame.Rect(px,cy_s,pw,ch_); screen.set_clip(clip_)
        y_=cy_s-self.contract_scroll_offset
        if not acs:
            screen.blit(self.small_font.render("No contracts available yet.",True,(115,122,145)),(px+30,y_+30))
        else:
            self.contract_start_buttons={}; self.contract_reset_buttons={}; total_=0
            for contract in acs:
                cid=contract["id"]; is_s=cid in self.contracts.active
                h_=100
                csts=[k for k in ["time_limit","max_spending","max_drills","max_pipes","no_overflow","min_furnaces","max_idle_time"] if contract.get(k)]
                if csts: h_+=15
                if is_s:
                    prog_=self.contracts.get_contract_progress(cid)
                    h_+=len(contract["requirements"])*12+sum(1 for k in csts if contract.get(k))*12
                cr_=pygame.Rect(px+12,y_,pw-24,h_)
                pygame.draw.rect(screen,(28,33,46),cr_,border_radius=7)
                pygame.draw.rect(screen,(66,105,150),cr_,1,border_radius=7)
                screen.blit(self.font.render(contract["name"],True,(192,210,252)),(cr_.x+10,cr_.y+8))
                t_s=self.tiny_font.render(f"T{contract.get('tier',1)}",True,(252,195,75))
                t_r=pygame.Rect(cr_.right-40,cr_.y+10,30,15)
                pygame.draw.rect(screen,(68,48,20),t_r,border_radius=3); screen.blit(t_s,(t_r.x+4,t_r.y+2))
                screen.blit(self.small_font.render(contract["description"],True,(155,162,190)),(cr_.x+10,cr_.y+28))
                cy2_=cr_.y+46
                if csts:
                    parts_=[]
                    if contract.get("time_limit"): parts_.append(f"{contract['time_limit']}s")
                    if contract.get("max_spending"): parts_.append(f"${contract['max_spending']}")
                    if contract.get("max_drills"): parts_.append(f"max {contract['max_drills']} drills")
                    if contract.get("max_pipes"): parts_.append(f"max {contract['max_pipes']} pipes")
                    if contract.get("no_overflow"): parts_.append("no overflow")
                    if contract.get("min_furnaces"): parts_.append(f"{contract['min_furnaces']}+ furnaces")
                    screen.blit(self.tiny_font.render("  ".join(parts_),True,(242,172,85)),(cr_.x+10,cy2_))
                    ry_=cr_.y+62
                else:
                    ry_=cr_.y+46
                req_str="Deliver: "+", ".join(f"{v} {k}" for k,v in contract["requirements"].items())
                screen.blit(self.small_font.render(req_str,True,(125,190,130)),(cr_.x+10,ry_))
                if is_s:
                    prog2_=self.contracts.get_contract_progress(cid); py2_=ry_+16
                    for item,req in contract["requirements"].items():
                        dlv=prog2_["delivered"].get(item,0) if isinstance(prog2_,dict) and "delivered" in prog2_ else prog2_.get(item,0) if prog2_ else 0
                        col_=(95,225,100) if dlv>=req else (205,205,85)
                        screen.blit(self.tiny_font.render(f"  {item}: {dlv}/{req}",True,col_),(cr_.x+10,py2_)); py2_+=12
                    if contract.get("time_limit"):
                        el=prog2_.get("time_elapsed",0) if prog2_ else 0; lm=contract["time_limit"]
                        col_=(252,85,85) if el>lm*0.8 else (198,198,85)
                        screen.blit(self.tiny_font.render(f"  {int(el)}s/{lm}s",True,col_),(cr_.x+10,py2_)); py2_+=12
                rb_=pygame.Rect(cr_.right-94,cr_.bottom-26,82,20)
                pygame.draw.rect(screen,(56,36,16),rb_,border_radius=4)
                pygame.draw.rect(screen,(185,130,50),rb_,1,border_radius=4)
                rt_=self.tiny_font.render("RESET",True,(225,168,70))
                screen.blit(rt_,rt_.get_rect(center=rb_.center))
                self.contract_reset_buttons[cid]=rb_
                y_+=h_+8
                total_=y_-(cy_s-self.contract_scroll_offset)
            locked=self.contracts.get_locked_contracts() if hasattr(self.contracts,"get_locked_contracts") else []
            if locked:
                gate=self.contracts.unlocked_tier()
                hdr=self.small_font.render(f"LOCKED — complete Tier {gate} to unlock:",True,(150,120,70))
                screen.blit(hdr,(px+18,y_+4)); y_+=26
                for contract in locked:
                    cr_=pygame.Rect(px+12,y_,pw-24,44)
                    pygame.draw.rect(screen,(22,24,30),cr_,border_radius=7)
                    pygame.draw.rect(screen,(52,54,64),cr_,1,border_radius=7)
                    screen.blit(self.font.render(contract["name"],True,(105,110,128)),(cr_.x+10,cr_.y+6))
                    t_s=self.tiny_font.render(f"T{contract.get('tier',1)}",True,(150,120,60))
                    t_r=pygame.Rect(cr_.right-40,cr_.y+8,30,15)
                    pygame.draw.rect(screen,(42,34,18),t_r,border_radius=3); screen.blit(t_s,(t_r.x+4,t_r.y+2))
                    screen.blit(self.tiny_font.render(contract["description"][:86],True,(85,90,105)),(cr_.x+10,cr_.y+26))
                    y_+=44+6
                total_=y_-(cy_s-self.contract_scroll_offset)
            self.contract_max_scroll=max(0,total_-ch_)
            self.contract_scroll_offset=max(0,min(self.contract_scroll_offset,self.contract_max_scroll))
        screen.set_clip(None)

    def draw_research_panel(self, screen):
        if not self.show_research_panel or not self.research: return
        from research import TECH_TREE
        from collections import defaultdict
        pw, ph = SCREEN_WIDTH-40, SCREEN_HEIGHT-80
        px, py = 20, 40
        self.research_panel_rect = pygame.Rect(px, py, pw, ph)
        HEADER = 52; TABS_H = 30
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 200))
        screen.blit(dim, (0, 0))
        pygame.draw.rect(screen, (6, 6, 12), (px, py, pw, ph), border_radius=10)
        pygame.draw.rect(screen, (45, 25, 90), (px, py, pw, ph), 1, border_radius=10)
        ts = self.title_font.render("RESEARCH TREE", True, (55, 200, 55))
        screen.blit(ts, (px+16, py+10))
        rp_s = self.small_font.render(f"{self.research.rp:.0f} RP", True, (100, 220, 100))
        screen.blit(rp_s, (px+16, py+28))
        hint_s = self.tiny_font.render(
            f"scroll wheel = zoom  |  drag = pan  |  {int(self.research_cam_zoom*100)}%",
            True, (30, 68, 30))
        screen.blit(hint_s, (px+pw-hint_s.get_width()-70, py+28))
        close_s = self.tiny_font.render("[T]/[ESC]", True, (50, 80, 50))
        screen.blit(close_s, (px+pw-close_s.get_width()-8, py+14))
        pygame.draw.line(screen, (20, 55, 20), (px+8, py+48), (px+pw-8, py+48), 1)

        BCOLS = {"production":(50,200,70),"logistics":(70,160,220),"refining":(220,130,50),"power":(220,90,60)}
        TABS  = [("production","PROD",(50,200,70)),
                 ("logistics","LOGI",(70,160,220)),
                 ("refining","RFNG",(220,130,50)),
                 ("power","POWR",(220,90,60))]
        self._research_tabs = {}
        tbx = px+16; tby = py+HEADER+4
        for tab_id, tab_lbl, tab_col in TABS:
            tw_ = self.tiny_font.size(tab_lbl)[0]+18
            tr_ = pygame.Rect(tbx, tby, tw_, 22)
            act_ = (self.research_tab == tab_id)
            bg_ = tuple(c//4+4 for c in tab_col)
            brd_ = tab_col if act_ else tuple(c//2 for c in tab_col)
            pygame.draw.rect(screen, bg_, tr_, border_radius=4)
            pygame.draw.rect(screen, brd_, tr_, 1 if not act_ else 2, border_radius=4)
            if tab_id != "all":
                pygame.draw.circle(screen, tab_col if act_ else tuple(c//2 for c in tab_col),
                                   (tbx+7, tby+11), 3)
            lc_ = (210,245,210) if act_ else (60,100,60)
            ls_ = self.tiny_font.render(tab_lbl, True, lc_)
            screen.blit(ls_, ls_.get_rect(centery=tr_.centery, left=tbx+(13 if tab_id!="all" else 6)))
            self._research_tabs[tab_id] = tr_
            tbx += tw_+4

        WNW, WNH = 200, 88
        WHS      = 300
        WVS      = 18
        WBS      = 44

        if self.research_tab == "all":
            visible_techs = TECH_TREE
        else:
            visible_techs = [t for t in TECH_TREE if t.get("branch","production")==self.research_tab]
        visible_ids = {t["id"] for t in visible_techs}

        tm_ = defaultdict(list)
        for tech in visible_techs:
            tm_[tech["tier"]].append(tech)
        tiers_ = sorted(tm_.keys())

        world_pos = {}
        for col, tier in enumerate(tiers_):
            wx_ = col * WHS
            wy_ = 0; cur_b_ = None
            for tech in tm_[tier]:
                b_ = tech.get("branch","production")
                if self.research_tab == "all" and cur_b_ is not None and b_ != cur_b_:
                    wy_ += WBS
                world_pos[tech["id"]] = (wx_, wy_)
                wy_ += WNH + WVS
                cur_b_ = b_

        canvas_top = py + HEADER + TABS_H + 4
        canvas_h_  = ph - HEADER - TABS_H - 14
        canvas_rect = pygame.Rect(px+4, canvas_top, pw-8, canvas_h_)
        self._research_canvas_rect = canvas_rect
        vcx = px + 4 + (pw-8)//2
        vcy = canvas_top + canvas_h_//2
        self._research_vp_center = (vcx, vcy)

        if self._research_needs_center and world_pos:
            xs = [wx for wx, wy in world_pos.values()]
            ys = [wy for wx, wy in world_pos.values()]
            bx0, bx1 = min(xs), max(xs) + WNW
            by0, by1 = min(ys), max(ys) + WNH
            pad = 40
            fit_zoom = min((pw-8) / (bx1-bx0+pad*2), canvas_h_ / (by1-by0+pad*2), 1.0)
            self.research_cam_zoom = fit_zoom
            self.research_cam_x = (bx0 + bx1) / 2
            self.research_cam_y = (by0 + by1) / 2
            self._research_needs_center = False

        zoom  = self.research_cam_zoom
        cam_x = self.research_cam_x
        cam_y = self.research_cam_y

        def w2s(wx, wy):
            return (int((wx-cam_x)*zoom+vcx), int((wy-cam_y)*zoom+vcy))

        nw = int(WNW*zoom); nh = int(WNH*zoom)

        mx_, my_ = pygame.mouse.get_pos()
        hov_tid  = None
        if canvas_rect.collidepoint(mx_, my_):
            for tech in visible_techs:
                wp_ = world_pos.get(tech["id"])
                if wp_ is None: continue
                sx_, sy_ = w2s(wp_[0], wp_[1])
                if sx_ <= mx_ <= sx_+nw and sy_ <= my_ <= sy_+nh:
                    hov_tid = tech["id"]; break

        highlight_set = set()
        if hov_tid:
            def _anc(tid, seen=None):
                if seen is None: seen = set()
                if tid in seen: return seen
                seen.add(tid)
                t2 = next((x for x in TECH_TREE if x["id"]==tid), None)
                if t2:
                    for r2 in t2.get("requires",[]):
                        _anc(r2, seen)
                return seen
            def _desc(tid):
                res = set()
                for t2 in TECH_TREE:
                    if tid in t2.get("requires",[]):
                        res.add(t2["id"]); res.update(_desc(t2["id"]))
                return res
            highlight_set = _anc(hov_tid) | _desc(hov_tid)

        id_branch = {t["id"]:t.get("branch","production") for t in TECH_TREE}
        id_tier_  = {t["id"]:t["tier"] for t in TECH_TREE}

        screen.set_clip(canvas_rect)

        pygame.draw.rect(screen, (3, 6, 3), canvas_rect)
        if zoom > 0.35:
            step_ = 100
            gx0_ = int((canvas_rect.left-vcx)/zoom+cam_x)//step_*step_
            gy0_ = int((canvas_rect.top -vcy)/zoom+cam_y)//step_*step_
            gxN_ = int((canvas_rect.right -vcx)/zoom+cam_x)+step_
            gyN_ = int((canvas_rect.bottom-vcy)/zoom+cam_y)+step_
            for gwx in range(gx0_, gxN_, step_):
                for gwy in range(gy0_, gyN_, step_):
                    gsx, gsy = w2s(gwx, gwy)
                    if canvas_rect.collidepoint(gsx, gsy):
                        pygame.draw.circle(screen, (9,15,9), (gsx, gsy), 1)

        if zoom > 0.28:
            lf_ = pygame.font.SysFont(["Segoe UI","Arial"], 10)
            for col, tier in enumerate(tiers_):
                lsx, lsy = w2s(col*WHS + WNW//2, -30)
                if canvas_rect.left < lsx < canvas_rect.right:
                    lt_ = lf_.render(f"TIER {tier}", True, (22,52,22))
                    screen.blit(lt_, lt_.get_rect(centerx=lsx, centery=lsy))

        def _bezier(p0, p3, steps=16):
            ctrl = abs(p3[0]-p0[0])*0.44
            p1=(p0[0]+ctrl,p0[1]); p2=(p3[0]-ctrl,p3[1])
            pts=[]
            for i in range(steps+1):
                t=i/steps
                x=(1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t**2*p2[0]+t**3*p3[0]
                y=(1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t**2*p2[1]+t**3*p3[1]
                pts.append((int(x),int(y)))
            return pts

        for tech in TECH_TREE:
            tid = tech["id"]
            wp_t = world_pos.get(tid)
            if wp_t is None: continue
            for req in tech.get("requires",[]):
                wp_r = world_pos.get(req)
                if wp_r is None: continue
                req_done  = req in self.research.researched
                this_done = tid in self.research.researched
                in_hl  = hov_tid and req in highlight_set and tid in highlight_set
                hov_d_ = hov_tid and not in_hl
                if hov_d_:
                    lc_=(9,17,9); lw_=1
                elif this_done and req_done:
                    bc_=BCOLS.get(id_branch.get(req,"production"),(40,200,40))
                    lc_=tuple(min(255,int(c*0.9)) for c in bc_); lw_=2
                elif req_done:
                    bc_=BCOLS.get(id_branch.get(req,"production"),(30,130,30))
                    lc_=tuple(int(c*0.5) for c in bc_); lw_=2
                else:
                    lc_=(20,42,20); lw_=1
                rsx,rsy = w2s(wp_r[0]+WNW, wp_r[1]+WNH//2)
                tsx,tsy = w2s(wp_t[0],     wp_t[1]+WNH//2)
                if id_tier_.get(req,-1)==tech["tier"]:
                    rsx2,rsy2=w2s(wp_r[0]+WNW//2, wp_r[1]+WNH)
                    tsx2,tsy2=w2s(wp_t[0]+WNW//2, wp_t[1])
                    if abs(tsy2-rsy2)>2:
                        pygame.draw.line(screen,lc_,(rsx2,rsy2),(tsx2,tsy2),lw_)
                        midp=((rsx2+tsx2)//2,(rsy2+tsy2)//2)
                        ah_=max(3,int(5*zoom))
                        pygame.draw.polygon(screen,lc_,[(midp[0],midp[1]+ah_),(midp[0]-3,midp[1]-ah_),(midp[0]+3,midp[1]-ah_)])
                else:
                    pts_=_bezier((rsx,rsy),(tsx,tsy))
                    if len(pts_)>=2:
                        pygame.draw.lines(screen,lc_,False,pts_,lw_)
                        last_=pts_[-1]; prev_=pts_[-3] if len(pts_)>=3 else pts_[-2]
                        ddx=last_[0]-prev_[0]; ddy=last_[1]-prev_[1]
                        mag_=max(1.0,(ddx**2+ddy**2)**0.5); ddx/=mag_; ddy/=mag_
                        ah_=max(4,int(6*zoom)); aw_=max(2,int(3*zoom))
                        base_=(last_[0]-int(ddx*ah_),last_[1]-int(ddy*ah_))
                        perp_=(-ddy,ddx)
                        q1=(base_[0]+int(perp_[0]*aw_),base_[1]+int(perp_[1]*aw_))
                        q2=(base_[0]-int(perp_[0]*aw_),base_[1]-int(perp_[1]*aw_))
                        pygame.draw.polygon(screen,lc_,[last_,q1,q2])

        self.research_buttons = {}
        fn_name  = pygame.font.SysFont(["Segoe UI","Arial"], 13)
        fn_small = pygame.font.SysFont(["Segoe UI","Arial"], 11)
        fn_tiny  = pygame.font.SysFont(["Segoe UI","Arial"],  9)
        tooltip_data = None

        for tech in visible_techs:
            tid = tech["id"]
            wp_ = world_pos.get(tid)
            if wp_ is None: continue
            sx_, sy_ = w2s(wp_[0], wp_[1])
            if sx_+nw < canvas_rect.left-10 or sx_ > canvas_rect.right+10: continue
            if sy_+nh < canvas_rect.top-10  or sy_ > canvas_rect.bottom+10: continue
            r = pygame.Rect(sx_, sy_, nw, nh)

            done_  = tid in self.research.researched
            rmets_ = all(req in self.research.researched for req in tech.get("requires",[]))
            afford_= self.research.rp >= tech["cost"]
            hov_   = (tid == hov_tid)
            hov_d_ = hov_tid and not hov_ and tid not in highlight_set
            dimmed = hov_d_
            bc_    = BCOLS.get(tech.get("branch","production"), (50,200,70))

            if dimmed:
                bg4=(4,6,4); brd4=(9,14,9)
            elif done_:
                bg4=(8,20,8); brd4=tuple(min(255,c//3+16) for c in bc_)
            elif rmets_ and afford_:
                p4_=int(80+60*_math.sin(self.power_anim_time*_math.pi*2))
                bg4=(8,16,6); brd4=(28,p4_,28)
            elif rmets_:
                bg4=(8,13,8); brd4=(20,78,20)
            else:
                bg4=(7,10,7); brd4=(14,26,14)
            if hov_:
                bg4=tuple(min(255,c+22) for c in bg4)
                brd4=tuple(min(255,c+58) for c in brd4)

            rad_ = max(2, int(4*zoom))
            pygame.draw.rect(screen, bg4, r, border_radius=rad_)
            pygame.draw.rect(screen, brd4, r, 1 if not done_ else 2, border_radius=rad_)

            if not dimmed and nw > 12:
                sw_=max(3,int(4*zoom)); sa_=210 if done_ else (160 if rmets_ else 80)
                ssurf=pygame.Surface((sw_,nh-4),pygame.SRCALPHA)
                ssurf.fill(bc_[:3]+(sa_,)); screen.blit(ssurf,(r.x+2,r.y+2))

            if nw < 34: continue

            if dimmed:
                if nw >= 52:
                    ab_=fn_tiny.render(tech["name"][:4],True,(18,30,18))
                    screen.blit(ab_,ab_.get_rect(center=r.center))
                continue

            if done_:            nc_=(60,220,70)
            elif rmets_ and afford_: nc_=(88,228,88)
            elif rmets_:         nc_=(42,135,42)
            else:                nc_=(26,58,26)
            if hov_: nc_=tuple(min(255,c+26) for c in nc_)

            txp = r.x+max(7,int(7*zoom))

            tc_=tuple(max(18,c//2+12) for c in bc_)
            if done_: tc_=tuple(min(255,c+42) for c in tc_)
            ts2=fn_tiny.render(f"T{tech['tier']}",True,tc_)
            screen.blit(ts2,(r.right-ts2.get_width()-3, r.y+3))

            if nw >= 65:
                ns_=tech["name"]
                maxcw=max(6,(nw-txp+r.x-ts2.get_width()-8)//7)
                if len(ns_)>maxcw: ns_=ns_[:maxcw-1]+"…"
                screen.blit(fn_name.render(ns_,True,nc_),(txp, r.y+3))

            if nw < 108: continue

            ul_=", ".join(MACHINE_STATS.get(m,{}).get("name","?") for m in tech.get("unlocks",[]))
            if ul_:
                muc=max(8,(nw-txp+r.x-4)//6)
                if len(ul_)>muc: ul_=ul_[:muc-1]+"…"
                screen.blit(fn_small.render(ul_,True,(22,105,58)),(txp, r.y+18))

            if self.research_tab != "all":
                BLAB={"production":"PROD","logistics":"LOGI","energy":"ENER","power":"POWR"}
                cross_=[(next((tt2["name"] for tt2 in TECH_TREE if tt2["id"]==rq),rq),
                         tt2["branch"] if (tt2:=next((tt3 for tt3 in TECH_TREE if tt3["id"]==rq),None)) else "production")
                        for rq in tech.get("requires",[]) if rq not in visible_ids]
                if cross_ and nw >= 100:
                    cb_x=txp; cb_y=r.bottom-12
                    for cname,cbranch in cross_[:2]:
                        cbc_=BCOLS.get(cbranch,(80,80,80))
                        clbl=f"{BLAB.get(cbranch,'?')} ← {cname[:10]}"
                        cs_=fn_tiny.render(clbl,True,tuple(max(30,c//2+30) for c in cbc_))
                        screen.blit(cs_,(cb_x,cb_y)); cb_y-=10

            if nw < 128: continue

            sy3=r.y+35
            if done_:
                screen.blit(fn_small.render("✓ DONE",True,(33,160,40)),(txp,sy3))
            elif rmets_:
                rp_c=(50,202,50) if afford_ else (25,85,25)
                screen.blit(fn_small.render(f"{tech['cost']} RP",True,rp_c),(txp,sy3))
                if afford_ and nw >= 150:
                    bh_=max(14,int(16*zoom))
                    btn=pygame.Rect(r.x+3,r.bottom-bh_-2,r.w-6,bh_)
                    pygame.draw.rect(screen,(12,50,12) if not hov_ else (20,70,20),btn,border_radius=3)
                    pygame.draw.rect(screen,(30,168,30),btn,1,border_radius=3)
                    bt=fn_small.render("RESEARCH",True,(50,208,50))
                    screen.blit(bt,bt.get_rect(center=btn.center))
                    self.research_buttons[tid]=btn
                elif not afford_:
                    ns2=fn_tiny.render(f"Need {tech['cost']-self.research.rp:.0f} more",True,(15,52,15))
                    screen.blit(ns2,(txp,r.bottom-12))
            else:
                missing=[next((tt2["name"] for tt2 in TECH_TREE if tt2["id"]==rq2),rq2)
                         for rq2 in tech.get("requires",[]) if rq2 not in self.research.researched]
                if missing:
                    ms_="← "+", ".join(missing[:2])
                    if len(ms_)>22: ms_=ms_[:21]+"…"
                    screen.blit(fn_tiny.render(ms_,True,(17,38,17)),(txp,sy3))
                else:
                    screen.blit(fn_small.render("LOCKED",True,(17,38,17)),(txp,sy3))

            if hov_: tooltip_data=(tech,r)

        screen.set_clip(None)
        pygame.draw.rect(screen,(16,32,16),canvas_rect,1)

        if tooltip_data:
            t_tech,t_node=tooltip_data
            TW=278; t_lines=[]
            desc=t_tech.get("description","")
            words=desc.split(); cur_ln=""
            for w in words:
                test=(cur_ln+" "+w).strip()
                if len(test)<=38: cur_ln=test
                else:
                    if cur_ln: t_lines.append(("d",cur_ln))
                    cur_ln=w
            if cur_ln: t_lines.append(("d",cur_ln))
            ul2=", ".join(MACHINE_STATS.get(m,{}).get("name","?") for m in t_tech.get("unlocks",[]))
            if ul2: t_lines.append(("u","Unlocks: "+ul2))
            rn2=[next((tt3["name"] for tt3 in TECH_TREE if tt3["id"]==r3),r3) for r3 in t_tech.get("requires",[])]
            if rn2: t_lines.append(("r","Requires: "+", ".join(rn2)))
            TH=30+len(t_lines)*13
            tx2=t_node.right+10; ty2=t_node.y
            if tx2+TW>px+pw-4: tx2=t_node.left-TW-10
            tx2=max(px+4,min(tx2,px+pw-TW-4))
            ty2=max(py+54,min(ty2,py+ph-TH-6))
            tsurf=pygame.Surface((TW,TH),pygame.SRCALPHA)
            tsurf.fill((4,8,4,240))
            pygame.draw.rect(tsurf,(36,152,36),(0,0,TW,TH),1,border_radius=5)
            tf_n=pygame.font.SysFont(["Segoe UI","Arial"],12)
            tf_s=pygame.font.SysFont(["Segoe UI","Arial"],10)
            tsurf.blit(tf_n.render(t_tech["name"],True,(76,230,86)),(7,6))
            ty_off=20
            for kind2,txt2 in t_lines:
                c2=(66,190,90) if kind2=="d" else ((50,148,205) if kind2=="u" else (175,170,55))
                tsurf.blit(tf_s.render(txt2,True,c2),(7,ty_off)); ty_off+=13
            screen.blit(tsurf,(tx2,ty2))

    def _load_milestones(self):
        import json as _json, os as _os
        try:
            if _os.path.exists("data/milestones.json"):
                with open("data/milestones.json") as f:
                    return set(_json.load(f).get("shown", []))
        except (_json.JSONDecodeError, ValueError, OSError):
            pass
        return set()

    def _save_milestones(self):
        import json as _json, os as _os
        try:
            _os.makedirs("data", exist_ok=True)
            with open("data/milestones.json", "w") as f:
                _json.dump({"shown": sorted(self.shown_milestones)}, f)
        except OSError:
            pass

    def check_story_milestones(self,money):
        for ms in STORY_MILESTONES:
            cap=ms["capital"]
            if money>=cap and cap not in self.shown_milestones:
                self.milestone_message=ms["message"]; self.milestone_timer=self.milestone_duration; self.shown_milestones.add(cap)
                self._save_milestones()

    def submit_console_code(self,contracts):
        code=self.console_input.strip().lower(); self.console_input=""; result={}
        if code=="mick":
            rewards=contracts.debug_complete_all_contracts()
            result["money"]=rewards.get("money",0)
            self.console_message=f"Unlocked! +${result['money']}"; self.console_message_color=(80,255,80)
            self.console_message_timer=3.0; self.show_transaction_message("Cheat accepted!",(80,255,80))
        elif code=="mick2":
            if self.research:
                self.research.debug_unlock_all()
                self.console_message="All research unlocked!"; self.console_message_color=(180,120,255)
                self.console_message_timer=3.0; self.show_transaction_message("Full tech tree unlocked!",(180,120,255))
        elif code=="mick3":
            result["money"]=100_000_000
            self.console_message="$100,000,000 added!"; self.console_message_color=(255,215,0)
            self.console_message_timer=3.0; self.show_transaction_message("+$100,000,000",(255,215,0))
        elif code in ("reset", "rstc"):
            n = contracts.debug_reset_all_contracts()
            self.console_message = f"Contracts reset ({n} cleared)."
            self.console_message_color = (120, 220, 255); self.console_message_timer = 3.0
            self.show_transaction_message("Contracts reset!", (120, 220, 255))
        else:
            try:
                from settings import CHEAT_CODES as _CHEATS
            except Exception:
                _CHEATS = {}
            if code in _CHEATS:
                ok, msg = contracts.apply_cheat_code(code)
                if msg is None:
                    msg = "Unlocked!" if ok else "Already unlocked"
                col = (80, 255, 200) if ok else (200, 200, 80)
                self.console_message = msg
                self.console_message_color = col
                self.console_message_timer = 3.0
                self.show_transaction_message(msg, col)
            else:
                self.console_message=f"Unknown: '{code}'"; self.console_message_color=(255,100,100); self.console_message_timer=2.0
        return result

    def handle_click(self,pos):
        if self.show_recipe_book:
            if self.rb_search_rect and self.rb_search_rect.collidepoint(pos): self.rb_search_focused=True; return True
            for mat,rect in self.rb_tile_rects.items():
                if rect.collidepoint(pos): self.rb_selected_item=mat; self.rb_search_focused=False; return True
            pw,ph=1100,640; px=(SCREEN_WIDTH-pw)//2; py=(SCREEN_HEIGHT-ph)//2
            if not pygame.Rect(px,py,pw,ph).collidepoint(pos): self.show_recipe_book=False
            else: self.rb_search_focused=False
            return True
        if self.show_stats_panel:
            if self.stats_close_rect and self.stats_close_rect.collidepoint(pos): self.show_stats_panel=False; return True
            if hasattr(self,'_stats_panel_rect') and self._stats_panel_rect and self._stats_panel_rect.collidepoint(pos): return True
            self.show_stats_panel=False; return True
        if self.show_research_panel:
            if not (hasattr(self,"research_panel_rect") and self.research_panel_rect.collidepoint(pos)):
                self.show_research_panel=False; return True
            for tab_id,tab_rect in getattr(self,"_research_tabs",{}).items():
                if tab_rect.collidepoint(pos):
                    if self.research_tab != tab_id:
                        self.research_tab=tab_id
                        self._research_needs_center = True
                    return True
            if hasattr(self,"research_buttons") and self.research:
                for tid,btn in self.research_buttons.items():
                    if btn.collidepoint(pos):
                        unlocked=self.research.research(tid)
                        if unlocked is not None:
                            from research import TECH_TREE
                            tech=next((t for t in TECH_TREE if t["id"]==tid),None)
                            self.show_transaction_message(f"Researched: {tech['name'] if tech else tid}!",(180,120,255))
                            try:
                                from menu import play_research_sfx; play_research_sfx()
                            except Exception: pass
                        return True
            if hasattr(self,"_research_canvas_rect") and self._research_canvas_rect and self._research_canvas_rect.collidepoint(pos):
                self.research_panning=True
                self._research_pan_mouse=pos
                self._research_pan_cam=(self.research_cam_x, self.research_cam_y)
            return True
        if self.show_contracts_panel:
            if hasattr(self,"contracts_panel_rect") and self.contracts_panel_rect.collidepoint(pos):
                for cid,btn in getattr(self,"contract_start_buttons",{}).items():
                    if btn.collidepoint(pos):
                        if self.contracts.start_contract(cid): self.show_transaction_message("Contract started!",(100,255,100))
                        return True
                for cid,btn in getattr(self,"contract_reset_buttons",{}).items():
                    if btn.collidepoint(pos):
                        if self.contracts.reset_contract(cid): self.show_transaction_message("Contract reset!",(255,180,80))
                        return True
                return True
            self.show_contracts_panel=False; return True
        if self.show_settings_panel:
            if hasattr(self,"_settings_console_btn") and self._settings_console_btn and self._settings_console_btn.collidepoint(pos):
                self.show_code_console=True; self.console_input=""; self.show_settings_panel=False; return True
            if hasattr(self,"_settings_panel_rect") and self._settings_panel_rect and self._settings_panel_rect.collidepoint(pos):
                for attr in ['_music_vol','_sfx_vol']:
                    slider=getattr(self,f'{attr}_slider',None)
                    if slider and slider.collidepoint(pos):
                        val=max(0.0,min(1.0,(pos[0]-slider.x)/slider.width)); setattr(self,attr,val)
                        try:
                            from menu import set_volumes; set_volumes(self._music_vol,self._sfx_vol)
                        except Exception: pass
                        return True
                return True
            self.show_settings_panel=False; return True
        if self.show_market_panel:
            if self.market_close_rect and self.market_close_rect.collidepoint(pos):
                self.show_market_panel=False; self.market_searching=False; return True
            if self.market_panel_rect and self.market_panel_rect.collidepoint(pos):
                if self.market_search_rect and self.market_search_rect.collidepoint(pos):
                    self.market_searching=True
                else:
                    self.market_searching=False
                    for item_key, r in self.market_item_rects.items():
                        if r.collidepoint(pos):
                            self.market_selected_item = (
                                None if self.market_selected_item == item_key else item_key
                            )
                            break
                return True
            self.market_searching=False
        if self.show_build_panel:
            if self.build_panel_rect and self.build_panel_rect.collidepoint(pos):
                if self.build_panel_close_rect and self.build_panel_close_rect.collidepoint(pos): self.show_build_panel=False; return True
                if self.build_search_rect and self.build_search_rect.collidepoint(pos): self.build_searching=True; return True
                else: self.build_searching=False
                if self.build_place_btn_rect and self.build_place_btn_rect.collidepoint(pos):
                    if self.build_panel_selected is not None:
                        self.active_tool=self.build_panel_selected; self.show_build_panel=False
                        self.md_drag_start=None; self.md_drag_end=None; self.md_pending=None
                        self.show_transaction_message(f"Placing: {MACHINE_STATS.get(self.active_tool,{}).get('name','')} [ESC cancel]",(100,200,255))
                    return True
                for mid,br in self.build_machine_buttons.items():
                    if br.collidepoint(pos): self.build_panel_selected=mid; return True
                return True
            self.show_build_panel=False; self.build_searching=False; return True
        for key,rect in self._toolbar_rects.items():
            if rect.collidepoint(pos):
                if key=="B":
                    self.show_build_panel=not self.show_build_panel; self.show_contracts_panel=self.show_research_panel=self.show_stats_panel=False
                    if self.show_build_panel and self.active_tool==0: self.active_tool=-1; self.md_drag_start=None; self.md_drag_end=None; self.md_pending=None
                elif key=="C": self.show_contracts_panel=not self.show_contracts_panel; self.show_build_panel=self.show_research_panel=self.show_stats_panel=False
                elif key=="T":
                    was=self.show_research_panel
                    self.show_research_panel=not was; self.show_build_panel=self.show_contracts_panel=self.show_stats_panel=False
                    if not was: self._research_needs_center=True
                elif key=="N": self.show_stats_panel=not self.show_stats_panel; self.show_build_panel=self.show_contracts_panel=self.show_research_panel=False
                elif key=="K": self.show_recipe_book=not self.show_recipe_book; self.show_build_panel=self.show_contracts_panel=self.show_research_panel=self.show_stats_panel=False
                elif key=="L": self.show_loans_panel=not self.show_loans_panel; self.show_build_panel=self.show_contracts_panel=self.show_research_panel=self.show_stats_panel=self.show_recipe_book=False
                elif key=="M":
                    self.show_market_panel=not self.show_market_panel
                    if not self.show_market_panel:
                        self.market_searching=False; self.market_search=""; self.market_scroll=0
                    self.show_build_panel=self.show_contracts_panel=self.show_research_panel=self.show_stats_panel=False
                elif key=="P": self._power_toggle_requested=True
                elif key=="X": self.active_tool=-1 if self.active_tool==0 else 0
                elif key=="Z": self.debug_mode=not self.debug_mode
                return True
        for key,rect in self._left_btn_rects.items():
            if rect.collidepoint(pos):
                if key=="Fn": self.show_settings_panel=not self.show_settings_panel; self.show_code_console=False; self.console_input=""
                return True
        return False

    def handle_scroll(self,direction,mouse_pos=None):
        amt=30
        if self.show_market_panel:
            self.market_scroll=max(0,min(self.market_scroll-direction*amt,self.market_max_scroll)); return
        if self.show_recipe_book:
            self.rb_grid_scroll=max(0,self.rb_grid_scroll-direction*amt); return
        if self.show_stats_panel:
            self.stats_scroll=max(0,self.stats_scroll-direction*amt); return
        if self.show_contracts_panel and mouse_pos and hasattr(self,"contracts_panel_rect"):
            if self.contracts_panel_rect.collidepoint(mouse_pos):
                self.contract_scroll_offset=max(0,min(self.contract_scroll_offset-direction*amt,self.contract_max_scroll)); return
        if self.show_research_panel:
            vcx_,vcy_=self._research_vp_center if hasattr(self,"_research_vp_center") else (640,360)
            mx2,my2=mouse_pos if mouse_pos else (vcx_,vcy_)
            wx0=(mx2-vcx_)/self.research_cam_zoom+self.research_cam_x
            wy0=(my2-vcy_)/self.research_cam_zoom+self.research_cam_y
            factor=1.15 if direction>0 else (1/1.15)
            self.research_cam_zoom=max(0.18,min(3.5,self.research_cam_zoom*factor))
            self.research_cam_x=wx0-(mx2-vcx_)/self.research_cam_zoom
            self.research_cam_y=wy0-(my2-vcy_)/self.research_cam_zoom
            return
        if self.show_build_panel:
            self.build_panel_scroll=max(0,min(self.build_panel_scroll-direction*amt,self.build_panel_max_scroll)); return

    def handle_mouse_motion(self, pos):
        if self.research_panning and self._research_pan_mouse and self._research_pan_cam:
            if not pygame.mouse.get_pressed()[0]:
                self.research_panning=False
            else:
                dx=pos[0]-self._research_pan_mouse[0]
                dy=pos[1]-self._research_pan_mouse[1]
                self.research_cam_x=self._research_pan_cam[0]-dx/self.research_cam_zoom
                self.research_cam_y=self._research_pan_cam[1]-dy/self.research_cam_zoom

    def handle_tile_click(self,grid,gx,gy):
        if 0<=gx<GRID_WIDTH and 0<=gy<GRID_HEIGHT:
            self.selected_tile=(grid[gy][gx],gx,gy)

    def get_active_tool(self):
        return self.active_tool

    def _draw_protest_overlay(self, screen):
        pm = self.protesters
        if not pm or not pm.is_blocking():
            return

        from settings import SCREEN_WIDTH
        import math as _m, time as _t
        pulse = 0.65 + 0.35 * _m.sin(_t.time() * 3.5)

        bw, bh = 680, 82
        bx = (SCREEN_WIDTH - bw) // 2
        by = 8

        panel = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(panel, (22, 8, 8, int(235 * pulse)), (0, 0, bw, bh),
                         border_radius=10)
        pygame.draw.rect(panel, (220, 45, 35, int(200 * pulse)), (0, 0, bw, bh),
                         2, border_radius=10)
        screen.blit(panel, (bx, by))

        icon_s = pygame.Surface((36, bh), pygame.SRCALPHA)
        icon_s.fill((180, 30, 25, int(120 * pulse)))
        screen.blit(icon_s, (bx, by))

        fo = ["Segoe UI", "Helvetica Neue", "Arial"]
        big   = pygame.font.SysFont(fo, 18, bold=True)
        small = pygame.font.SysFont(fo, 13, bold=False)

        title = big.render("  PROTESTERS BLOCKING TRUCKS", True,
                           (255, int(100 * pulse), int(80 * pulse)))
        screen.blit(title, (bx + 44, by + 10))

        rem = pm.get_remaining_str()
        msg1 = small.render(
            f"Trucks cannot sell until protesters disperse  —  auto-dispersal in {rem}",
            True, (245, 160, 140))
        msg2 = small.render(
            "Fix: build Scrubbers to reduce pollution below 200, or take a Loan [L] to buy them.",
            True, (220, 130, 110))
        screen.blit(msg1, (bx + 44, by + 35))
        screen.blit(msg2, (bx + 44, by + 55))

    def _draw_market_panel(self, screen):
        sd = self.market
        if sd is None:
            return

        from settings import SCREEN_WIDTH, SCREEN_HEIGHT, ITEM_VALUES

        DETAIL_H = 110 if self.market_selected_item else 0
        PW, PH = 660, 500 + DETAIL_H
        px = (SCREEN_WIDTH - PW) // 2
        py = max(10, (SCREEN_HEIGHT - PH) // 2)

        AMBER     = (255, 176, 60)
        AMBER_DIM = (140, 95, 28)
        AMBER_HOT = (255, 215, 130)
        GREEN_UP  = (80, 220, 120)
        RED_DOWN  = (220, 80, 70)
        NEUTRAL   = (160, 165, 170)

        fo = ["Consolas", "Courier New", "Courier", "monospace"]
        title_f = pygame.font.SysFont(fo, 15, bold=True)
        head_f  = pygame.font.SysFont(fo, 12, bold=True)
        row_f   = pygame.font.SysFont(fo, 12)
        tiny_f  = pygame.font.SysFont(fo, 11)

        self.market_panel_rect = pygame.Rect(px, py, PW, PH)

        panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
        pygame.draw.rect(panel, (8, 10, 14, 252), (0, 0, PW, PH), border_radius=10)
        pygame.draw.rect(panel, (50, 70, 55, 255), (0, 0, PW, PH), 1, border_radius=10)
        screen.blit(panel, (px, py))

        title_surf = pygame.Surface((PW, 34), pygame.SRCALPHA)
        title_surf.fill((14, 22, 12, 220))
        screen.blit(title_surf, (px, py))
        pygame.draw.line(screen, (50, 70, 55), (px, py + 34), (px + PW, py + 34), 1)

        title_s = title_f.render("ANTHRACITE MARKET FEED", True, AMBER_HOT)
        screen.blit(title_s, (px + 14, py + 10))

        refresh_s = tiny_f.render(f"refresh in {sd.time_until_refresh_str()}", True, AMBER_DIM)
        screen.blit(refresh_s, (px + PW - refresh_s.get_width() - 44, py + 12))

        cx, cy = px + PW - 28, py + 8
        self.market_close_rect = pygame.Rect(cx, cy, 20, 18)
        pygame.draw.rect(screen, (55, 18, 18), self.market_close_rect, border_radius=3)
        pygame.draw.rect(screen, (130, 40, 40), self.market_close_rect, 1, border_radius=3)
        xs = tiny_f.render("✕", True, (200, 70, 70))
        screen.blit(xs, (cx + 5, cy + 3))

        SB_Y = py + 40
        SB_H = 22
        search_rect = pygame.Rect(px + 10, SB_Y, PW - 20, SB_H)
        self.market_search_rect = search_rect
        sb_bg  = (18, 28, 16) if self.market_searching else (12, 16, 12)
        sb_bdr = AMBER if self.market_searching else (55, 72, 55)
        pygame.draw.rect(screen, sb_bg, search_rect, border_radius=4)
        pygame.draw.rect(screen, sb_bdr, search_rect, 1, border_radius=4)
        slash_s = tiny_f.render("/", True, AMBER_DIM)
        screen.blit(slash_s, (px + 16, SB_Y + 5))
        if self.market_search:
            st_col = AMBER_HOT
            st_txt = self.market_search
        else:
            st_col = (70, 85, 68)
            st_txt = "search items..."
        screen.blit(row_f.render(st_txt, True, st_col), (px + 28, SB_Y + 4))
        if self.market_searching and (pygame.time.get_ticks() // 530) % 2 == 0:
            cursor_x = px + 28 + row_f.size(self.market_search)[0]
            pygame.draw.line(screen, AMBER, (cursor_x, SB_Y + 3), (cursor_x, SB_Y + SB_H - 3), 1)

        COL_ITEM   = px + 12
        COL_BASE   = px + 330
        COL_LIVE   = px + 430
        COL_CHG    = px + 530
        HDR_Y = py + 68
        pygame.draw.line(screen, (40, 55, 42), (px + 8, HDR_Y - 2), (px + PW - 8, HDR_Y - 2), 1)
        screen.blit(head_f.render("ITEM",   True, AMBER), (COL_ITEM, HDR_Y))
        screen.blit(head_f.render("BASE $", True, AMBER), (COL_BASE, HDR_Y))
        screen.blit(head_f.render("LIVE $", True, AMBER), (COL_LIVE, HDR_Y))
        screen.blit(head_f.render("CHANGE", True, AMBER), (COL_CHG,  HDR_Y))
        pygame.draw.line(screen, (40, 55, 42), (px + 8, HDR_Y + 16), (px + PW - 8, HDR_Y + 16), 1)

        LIST_TOP = HDR_Y + 20
        LIST_BOT = py + PH - 32 - DETAIL_H
        LIST_H   = LIST_BOT - LIST_TOP
        ROW_H    = 20
        SB_W     = 8

        query = self.market_search.lower().strip()
        all_items = sd.get_movers(9999)
        if query:
            all_items = [(k, v) for k, v in all_items
                         if query in k.replace("_", " ").lower()]

        total_h = len(all_items) * ROW_H
        self.market_max_scroll = max(0, total_h - LIST_H)
        self.market_scroll = max(0, min(self.market_scroll, self.market_max_scroll))

        clip_w = PW - 16 - SB_W - 4
        screen.set_clip(pygame.Rect(px + 8, LIST_TOP, clip_w, LIST_H))

        self.market_item_rects = {}
        for i, (item, mult) in enumerate(all_items):
            ry = LIST_TOP + i * ROW_H - self.market_scroll
            if ry + ROW_H < LIST_TOP:
                continue
            if ry >= LIST_BOT:
                break

            base = ITEM_VALUES.get(item, 0)
            live = base * mult
            pct  = (mult - 1.0) * 100.0
            col  = GREEN_UP if pct > 0.05 else (RED_DOWN if pct < -0.05 else NEUTRAL)
            selected = (item == self.market_selected_item)

            row_bg = (30, 44, 30, 120) if selected else ((18, 26, 16, 55) if i % 2 == 0 else (0, 0, 0, 0))
            alt = pygame.Surface((clip_w, ROW_H), pygame.SRCALPHA)
            alt.fill(row_bg)
            screen.blit(alt, (px + 8, ry))
            if selected:
                pygame.draw.rect(screen, AMBER, (px + 8, ry, clip_w, ROW_H), 1)

            self.market_item_rects[item] = pygame.Rect(px + 8, ry, clip_w, ROW_H)

            name = item.replace("_", " ").title()
            name_col = AMBER_HOT if selected else (200, 205, 195)
            screen.blit(row_f.render(name[:30],          True, name_col), (COL_ITEM, ry + 3))
            screen.blit(row_f.render(f"${base:,.2f}",    True, AMBER_DIM),       (COL_BASE, ry + 3))
            screen.blit(row_f.render(f"${live:,.2f}",    True, col),             (COL_LIVE, ry + 3))
            arrow = "▲" if pct > 0.05 else ("▼" if pct < -0.05 else "—")
            screen.blit(row_f.render(f"{arrow} {abs(pct):.1f}%", True, col),     (COL_CHG,  ry + 3))

        screen.set_clip(None)

        sb_x = px + PW - 14
        pygame.draw.rect(screen, (22, 32, 22), (sb_x, LIST_TOP, SB_W, LIST_H), border_radius=4)
        if self.market_max_scroll > 0:
            vis_ratio   = LIST_H / max(total_h, 1)
            thumb_h     = max(18, int(LIST_H * vis_ratio))
            scroll_frac = self.market_scroll / self.market_max_scroll
            thumb_y     = LIST_TOP + int((LIST_H - thumb_h) * scroll_frac)
            pygame.draw.rect(screen, AMBER_DIM, (sb_x, thumb_y, SB_W, thumb_h), border_radius=4)

        if self.market_selected_item and DETAIL_H > 0:
            item  = self.market_selected_item
            mult  = sd.get_multiplier(item)
            base  = ITEM_VALUES.get(item, 0)
            live  = base * mult
            pct   = (mult - 1.0) * 100.0
            col   = GREEN_UP if pct > 0.05 else (RED_DOWN if pct < -0.05 else NEUTRAL)
            hist  = sd.price_history.get(item, [])
            sold  = getattr(self, "stats_tracker", None)
            sold_count = sold.total_items.get(item, 0) if sold else 0

            dy = LIST_BOT + 4
            pygame.draw.line(screen, (50, 80, 55), (px + 8, dy), (px + PW - 8, dy), 1)
            dy += 4

            name_disp = item.replace("_", " ").title()
            screen.blit(head_f.render(name_disp, True, AMBER_HOT), (px + 12, dy))
            dy += 16
            screen.blit(tiny_f.render(f"Base: ${base:,.2f}   Live: ${live:,.2f}   Change: {pct:+.1f}%", True, col), (px + 12, dy))
            dy += 14
            screen.blit(tiny_f.render(f"You have sold: {sold_count:,} units", True, (140, 160, 140)), (px + 12, dy))
            dy += 14
            screen.blit(tiny_f.render(f"Multiplier: {mult:.4f}   History samples: {len(hist)}", True, AMBER_DIM), (px + 12, dy))

            GX = px + 320
            GY = LIST_BOT + 8
            GW, GH = PW - 340, DETAIL_H - 16
            pygame.draw.rect(screen, (12, 18, 12), (GX, GY, GW, GH))
            pygame.draw.rect(screen, (35, 55, 35), (GX, GY, GW, GH), 1)

            lo_b = 0.92
            hi_b = 1.08
            mid_y = GY + GH // 2
            pygame.draw.line(screen, (30, 50, 30), (GX, mid_y), (GX + GW, mid_y), 1)

            if len(hist) >= 2:
                pts = []
                for i2, v in enumerate(hist):
                    fx = GX + int(i2 / (len(hist) - 1) * (GW - 2)) + 1
                    norm = (v - lo_b) / (hi_b - lo_b)
                    fy = GY + GH - 2 - int(norm * (GH - 4))
                    pts.append((fx, fy))
                line_col = GREEN_UP if hist[-1] >= hist[-2] else RED_DOWN
                pygame.draw.lines(screen, line_col, False, pts, 2)
                pygame.draw.circle(screen, AMBER_HOT, pts[-1], 3)
            elif len(hist) == 1:
                fx = GX + GW // 2
                norm = (hist[0] - lo_b) / (hi_b - lo_b)
                fy = GY + GH - 2 - int(norm * (GH - 4))
                pygame.draw.circle(screen, AMBER_HOT, (fx, fy), 3)

            screen.blit(tiny_f.render("24h price history", True, AMBER_DIM), (GX + 2, GY + 2))

        pygame.draw.line(screen, (40, 55, 42), (px + 8, LIST_BOT + 2), (px + PW - 8, LIST_BOT + 2), 1)
        n = len(all_items)
        suffix = f"  —  {n} matching '{query}'" if query else f"  —  {n} items"
        hint = "click row for detail" if not self.market_selected_item else "click row again to deselect"
        foot_s = tiny_f.render(f"±8%/hr{suffix}  |  {hint}  |  [M] close", True, AMBER_DIM)
        screen.blit(foot_s, (px + PW // 2 - foot_s.get_width() // 2, LIST_BOT + 9))