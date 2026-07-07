import json
import os
import math
from settings import RP_VALUES

TECH_TREE = [
    {"id":"smelting","name":"Coal Furnace","description":"Furnace — coal-fired smelter. Turns raw_iron/copper/lead/zinc into liquid metal. First step of every metal chain.","cost":15,"unlocks":[9],"requires":[],"tier":1,"branch":"production"},
    {"id":"iron_extraction","name":"Iron Drill","description":"Iron Drill — mines raw_iron at 0.1/s. Gateway to smelting, steel, and the electric furnace.","cost":40,"unlocks":[8],"requires":[],"tier":1,"branch":"production"},
    {"id":"earthworks","name":"Earthworks","description":"Soil Excavator (2×2) + Quarry (4×4) + Grinder (2×2). Quarry → limestone/clay/sand/earth; Grinder → powders and silicon.","cost":100,"unlocks":[31,32,33],"requires":[],"tier":1,"branch":"production"},
    {"id":"forestry","name":"Forestry","description":"Tree Farm (3×3) — oak_log at 0.125/s. Required by Sawmill and Paper Mill.","cost":100,"unlocks":[53],"requires":[],"tier":1,"branch":"production"},
    {"id":"copper_extraction","name":"Copper Drill","description":"Copper Drill (1×2) — mines raw_copper at 0.15/s. Feeds wire, plate, and electronics.","cost":50,"unlocks":[30],"requires":["iron_extraction"],"tier":2,"branch":"production"},
    {"id":"ingot_casting","name":"Ingot Casting","description":"Ingot Molder — 4 liquid metal → 2 ingots in 4 s. Central node for every metal-forming chain.","cost":60,"unlocks":[10],"requires":["smelting"],"tier":2,"branch":"production"},
    {"id":"electric_furnace_tech","name":"Electric Furnace","description":"Electric Furnace (2×2) — 1 raw → 2 liquid in 5 s, power-only. Unlocks Press, Roller, and Sawmill.","cost":60,"unlocks":[109],"requires":["iron_extraction"],"tier":2,"branch":"production"},
    {"id":"paper_production","name":"Paper Mill","description":"Paper Mill (3×3) — 1 oak_log + 0.5 water → 4 paper in 5 s. Feeds filters and research stations.","cost":200,"unlocks":[93],"requires":["forestry"],"tier":2,"branch":"production"},
    {"id":"brick_production","name":"Kiln & Bricks","description":"Kiln (2×3) — clay_bricks + coal → brick in 5 s. High-value sellable and construction input.","cost":150,"unlocks":[50],"requires":["earthworks"],"tier":2,"branch":"production"},
    {"id":"cement_production","name":"Cement Chain","description":"Raw Mill (3×3) + Industrial Kiln (4×6) — gravel + limestone + clay → rawmix → cement. Foundation of concrete.","cost":200,"unlocks":[34,35],"requires":["earthworks"],"tier":2,"branch":"production"},
    {"id":"blast_furnace_tech","name":"Blast Furnace","description":"Blast Furnace (3×3) — 4 coal + 1 iron_ingot → 2 steel in 5 s. Also smelts alumina and produces coke.","cost":150,"unlocks":[14],"requires":["ingot_casting"],"tier":3,"branch":"production"},
    {"id":"press_roller","name":"Press & Roller","description":"Press (2×2) — ingot/steel → plate/gear/filter. Roller (2×2) — plate → coil/wire; steel → rod; ingot → nails.","cost":120,"unlocks":[19,20],"requires":["electric_furnace_tech"],"tier":3,"branch":"production"},
    {"id":"sawmill_tech","name":"Sawmill","description":"Sawmill (2×3) — oak_log → cut_oak_log → planks; iron_ingot → iron_plate (4 per cycle).","cost":120,"unlocks":[18],"requires":["forestry","electric_furnace_tech"],"tier":3,"branch":"production"},
    {"id":"research_station_2","name":"Research Station 2","description":"Research Station 2 (8×8) — item-fed RP. 10 RP per item on a 2 s cycle. Much faster than RS1 once materials flow.","cost":400,"unlocks":[114],"requires":["electric_furnace_tech","press_roller"],"tier":3,"branch":"production"},
    {"id":"metal_forming","name":"Industrial Firebox","description":"Industrial Firebox (2×3) — oak_log + coal → coke_fuel (×2) or sodium_carbonate in 8 s. Coke is better blast furnace fuel.","cost":220,"unlocks":[116],"requires":["sawmill_tech","ingot_casting"],"tier":4,"branch":"production"},
    {"id":"concrete_production","name":"Concrete Plant","description":"Concrete Plant (4×4) — cement + aggregate + water → concrete_block; also clay → clay_bricks.","cost":280,"unlocks":[38],"requires":["cement_production"],"tier":4,"branch":"production"},
    {"id":"lathe_tech","name":"Lathe","description":"Lathe (2×3) — precision machining: steel → drill_head; aluminium → zirconium_rod; copper → copper_drill_head.","cost":700,"unlocks":[77],"requires":["blast_furnace_tech"],"tier":4,"branch":"production"},
    {"id":"boiling","name":"Liquid Boiler","description":"Liquid Boiler (2×3) — crude_oil → gasoline or water → steam in 4 s. Steam feeds turbines; gasoline feeds generators.","cost":250,"unlocks":[89],"requires":["blast_furnace_tech"],"tier":4,"branch":"production"},
    {"id":"reinforcement","name":"Craft Assembler","description":"Craft Assembler (3×3) — 9 modes: crankshaft, gearbox, semiconductor, galvanized_steel, tire, insulated_wire, reinforced_concrete, and more. 15 s cycle.","cost":280,"unlocks":[39],"requires":["press_roller","concrete_production"],"tier":5,"branch":"production"},
    {"id":"research_station_3","name":"Research Station 3","description":"Research Station 3 (8×8) — dual-item feed, 25 RP per item on a 0.5 s cycle. Top-tier RP generation.","cost":2500,"unlocks":[115],"requires":["research_station_2","reinforcement"],"tier":5,"branch":"production"},

    {"id":"oil_extraction","name":"Oil Rig","description":"Oil Rig (2×1) — pumps crude_oil at 0.12/s. Gateway to diesel, gasoline, plastics, rubber, and all chemistry.","cost":400,"unlocks":[15],"requires":[],"tier":1,"branch":"refining"},
    {"id":"diesel_refining","name":"Diesel Refinery","description":"Diesel Refinery (3×3) — 3-stage chain: crude → poor_quality_diesel → diesel → refined_diesel. Run three in series for full conversion.","cost":500,"unlocks":[16],"requires":["oil_extraction"],"tier":2,"branch":"refining"},
    {"id":"natural_gas","name":"Natural Gas","description":"Natural Gas Well (2×2, 0.15/s) + Condenser (2×3). Well → raw_gas; Condenser → condensed_gas or LNG.","cost":500,"unlocks":[45,46],"requires":["oil_extraction"],"tier":2,"branch":"refining"},
    {"id":"coal_liquefaction","name":"Coal Liquefaction","description":"Coal Liquefaction Plant (4×6) — 2 coal + 1 water → light_oil + heavy_oil in 8 s. Diesel feedstock without an Oil Rig.","cost":900,"unlocks":[87],"requires":["oil_extraction"],"tier":2,"branch":"refining"},
    {"id":"filtration_tech","name":"Filtration Plant","description":"Filtration Plant (2×3) — refined_diesel → machine_oil; contaminated_water → distilled_water; purified_gold → liquid_gold.","cost":500,"unlocks":[82],"requires":["oil_extraction"],"tier":2,"branch":"refining"},
    {"id":"petrochemistry","name":"Petrochemistry","description":"Steam Cracking Plant (4×6) — crude + water → paraxylene + ethylene. Plastic Refinery (3×3) — ethanol, leaded gasoline, and more.","cost":700,"unlocks":[40,41],"requires":["diesel_refining"],"tier":3,"branch":"refining"},
    {"id":"gas_refining","name":"Gas Refinery","description":"Gas Refinery (3×3) — condensed_gas → refined_gas in 6 s; crude_oil → graphite_electrode (×2). Refined gas feeds LNG via Condenser.","cost":600,"unlocks":[47],"requires":["natural_gas"],"tier":3,"branch":"refining"},
    {"id":"plastic_production","name":"Plastic Production","description":"Plastic Production Facility (4×4) — PTA + MEG → 80 plastic_pellets per 7 s. Plastic Molding Machine (3×3) — pellets → plastic_casing.","cost":800,"unlocks":[43,44],"requires":["petrochemistry"],"tier":4,"branch":"refining"},
    {"id":"chemistry","name":"Chemical Reactor","description":"Chemical Reactor (3×3) — 7 recipes: crude → rubber; uranium_ore → yellowcake; heavy_oil → liquid_sulfur; sulfur/lead → acids; and more.","cost":700,"unlocks":[60],"requires":["petrochemistry"],"tier":4,"branch":"refining"},
    {"id":"industrial_molding","name":"Industrial Plastic Molder","description":"Industrial Plastic Molder (3×3) — 10 pellets → 2 plastic_casing per 1.5 s. Four times the output of the standard Molding Machine.","cost":600,"unlocks":[92],"requires":["plastic_production"],"tier":5,"branch":"refining"},
    {"id":"water_treatment","name":"Water Treatment","description":"Water Treatment Plant (3×4) — dirty_lithium_sulfate → lithium_sulfate; water → table_salt. Core of the lithium battery chain.","cost":600,"unlocks":[64],"requires":["chemistry"],"tier":5,"branch":"refining"},
    {"id":"electrolysis_tech","name":"Electrolysis Plant","description":"Electrolysis Plant (3×4) — water → hydrochloric_acid; lithium_ion_battery → charged_lithium_battery. 4 s cycle.","cost":900,"unlocks":[81],"requires":["chemistry"],"tier":5,"branch":"refining"},
    {"id":"advanced_assembly","name":"Advanced Assembler","description":"Advanced Assembler (4×4) — 8 modes: lithium_battery_pack, electric_motor, fuel_rod, control_rod, microchip_8x64x, logic_plate, and more. 10 s cycle.","cost":900,"unlocks":[61],"requires":["petrochemistry","chemistry"],"tier":5,"branch":"refining"},
    {"id":"chemical_plants","name":"Chemical Plant","description":"Chemical Plant (3×3) — 6 modes: lithium battery chain; table_salt → chlorine; earth_fragment → karat_gold; ethanol → acetic_acid; ethylene → MEG.","cost":800,"unlocks":[65],"requires":["water_treatment"],"tier":6,"branch":"refining"},
    {"id":"air_separation","name":"Air Separation Unit","description":"Air Separation Unit (3×3) — produces oxygen at 0.4/s from the atmosphere.","cost":1200,"unlocks":[90],"requires":["electrolysis_tech"],"tier":6,"branch":"refining"},
    {"id":"gold_refining","name":"Gold Acid Refinery","description":"Gold Acid Refinery (3×4) — 1 karat_gold + 0.5 acetic_acid → 1 purified_gold in 10 s. Karat gold comes from Chemical Plant.","cost":1200,"unlocks":[55],"requires":["chemical_plants"],"tier":6,"branch":"refining"},
    {"id":"lithium_extraction","name":"Lithium Ore Drill","description":"Lithium Ore Drill (2×2) — mines lithium_ore at 0.05/s. Feeds the full lithium battery chain.","cost":1200,"unlocks":[59],"requires":["chemical_plants"],"tier":6,"branch":"refining"},
    {"id":"industrial_smelting","name":"Industrial Electric Furnace","description":"Industrial Electric Furnace (3×3) — purified_gold → liquid_gold. 200 kMF/s power draw. Unlocks Alloyer and Foundry.","cost":1500,"unlocks":[57],"requires":["gold_refining"],"tier":7,"branch":"refining"},
    {"id":"deep_mining","name":"Mineshaft Drill","description":"Mineshaft Drill (3×3) — mines deep_earth_fragment, raw_lead, raw_zinc, or uranium_ore at 0.1/s (pick via recipe mode).","cost":2000,"unlocks":[68],"requires":["gold_refining"],"tier":7,"branch":"refining"},
    {"id":"brine_extraction","name":"Lithium Brine Extractor","description":"Lithium Brine Extractor (3×3) — lithium_brine at 0.3/s, 6× throughput vs. Ore Drill.","cost":1500,"unlocks":[70],"requires":["lithium_extraction"],"tier":7,"branch":"refining"},
    {"id":"logic_assembler_tech","name":"Logic Assembler","description":"Logic Assembler (4×4) — 2 logic_plate + 4 semiconductor + 2 gold_wire → 1 microchip_2x in 10 s ($12k each). Foundation of the microchip_8x64x chain.","cost":3500,"unlocks":[79],"requires":["advanced_assembly","gold_refining"],"tier":7,"branch":"refining"},
    {"id":"alloying","name":"Alloyer","description":"Alloyer (3×3) — gold_ingot + aluminium_ingot → molten_purple_gold ($20k per ingot); iron + aluminium → molten_ferroaluminium. 15 s cycle.","cost":1800,"unlocks":[58],"requires":["industrial_smelting"],"tier":7,"branch":"refining"},
    {"id":"foundry_tech","name":"Foundry","description":"Foundry (6×6) — bulk smelting: 4 raw metal + 2 coal → 4 liquid metal in 4 s. Highest liquid-metal throughput (1/s).","cost":2800,"unlocks":[78],"requires":["industrial_smelting"],"tier":7,"branch":"refining"},

    {"id":"water_pumping","name":"Water Pumping","description":"Water Pump — produces 0.5 water/s. Required by concrete, chemistry, paper, and many fluid recipes.","cost":25,"unlocks":[36],"requires":[],"tier":1,"branch":"logistics"},
    {"id":"pipe_intersections","name":"Pipe Crossings","description":"Pipe Intersection — 4-way crossing with two independent lanes. Share tiles without merging flows.","cost":50,"unlocks":[131],"requires":[],"tier":1,"branch":"logistics"},
    {"id":"storage_silos","name":"Storage Silos","description":"Item Silo (2×2, cap 500) + Fluid Silo (2×2, cap 100). Buffer items between production stages.","cost":80,"unlocks":[22,23],"requires":[],"tier":1,"branch":"logistics"},
    {"id":"atmospherics","name":"Atmospherics","description":"Scrubber (2×2) + Exhaust Stack (2×3). Scrubber actively reduces pollution; Stack vents emissions to keep machines running.","cost":120,"unlocks":[21,110],"requires":[],"tier":1,"branch":"logistics"},
    {"id":"waste_handling","name":"Waste Handling","description":"Liquid Burner (2×2) — disposes residue, heavy oil, naphtha, and crude. Essential once refineries are running.","cost":100,"unlocks":[29],"requires":[],"tier":1,"branch":"logistics"},
    {"id":"huge_depot","name":"Huge Truck Depot","description":"Huge Truck Depot (6×6) — 350-capacity bulk depot with 1.25× sell bonus. Best for high-volume end products.","cost":220,"unlocks":[83],"requires":["storage_silos"],"tier":2,"branch":"logistics"},
    {"id":"adurite_pipes","name":"Adurite Pipework","description":"Adurite Pipe/L-Pipe/Merger/Splitter/Intersection — 60 capacity, 40 items/s. Tier-2 logistics.","cost":200,"unlocks":[119,120,121,122,123,124],"requires":["pipe_intersections"],"tier":2,"branch":"logistics"},
    {"id":"fluid_logistics","name":"Liquid Truck Depot","description":"Liquid Truck Depot (4×6) — sells liquid products with 1.05× bonus. Unlocks Bottling Plant.","cost":400,"unlocks":[51],"requires":["storage_silos"],"tier":2,"branch":"logistics"},
    {"id":"gas_burning","name":"Gas Burner","description":"Gas Burner (2×2) — consumes raw_gas, condensed_gas, or refined_gas to relieve pipeline backpressure.","cost":400,"unlocks":[49],"requires":["waste_handling"],"tier":2,"branch":"logistics"},
    {"id":"bottling","name":"Bottling Plant","description":"Bottling Plant (3×3) — packages gasoline, machine_oil, sulfuric_acid, hydrochloric_acid, and water for sale.","cost":500,"unlocks":[91],"requires":["fluid_logistics"],"tier":3,"branch":"logistics"},
    {"id":"iridium_pipes","name":"Iridium Pipework","description":"Iridium Pipe/L-Pipe/Merger/Splitter/Intersection — 200 capacity, 120 items/s. End-game logistics tier.","cost":800,"unlocks":[125,126,127,128,129,130],"requires":["adurite_pipes"],"tier":3,"branch":"logistics"},

    {"id":"lv_poles","name":"LV Poles","description":"LV Power Pole — short-range power relay. Chains generators to distant machines.","cost":10,"unlocks":[97],"requires":[],"tier":1,"branch":"power"},
    {"id":"coal_power","name":"Coal Generator","description":"Coal Generator (2×2) — 7 kMF/s from coal. Dirty but available from the start.","cost":15,"unlocks":[12],"requires":[],"tier":1,"branch":"power"},
    {"id":"wind_energy","name":"Wind Turbine 1","description":"Wind Turbine 1 (2×2) — 1.5 kMF/s clean power. Start of the wind and solar upgrade paths.","cost":30,"unlocks":[26],"requires":[],"tier":1,"branch":"power"},
    {"id":"mv_poles","name":"MV Poles","description":"MV Power Pole — 3-tile range, 24 kMF/s transfer. Unlocks batteries, heater, turbine, logic gates, and generators.","cost":60,"unlocks":[98],"requires":["lv_poles"],"tier":2,"branch":"power"},
    {"id":"solar_tech_2","name":"Solar Panel 2","description":"Solar Panel 2 — 528 MF/s, nearly double Solar 1. Good supplement before diesel and wind are online.","cost":150,"unlocks":[24],"requires":["wind_energy"],"tier":2,"branch":"power"},
    {"id":"energy_storage","name":"MV Battery","description":"MV Battery (2×2) — 10 MMF capacity, 50 kMF/s transfer. Buffers power across demand spikes.","cost":220,"unlocks":[100],"requires":["mv_poles"],"tier":3,"branch":"power"},
    {"id":"electric_water_heater_tech","name":"Electric Water Heater","description":"Electric Water Heater (2×2) — 0.5 water → 1 steam per 2 s using electricity only. Clean steam supply.","cost":300,"unlocks":[117],"requires":["mv_poles"],"tier":3,"branch":"power"},
    {"id":"steam_power","name":"Steam Turbine","description":"Steam Turbine (3×3) — 500 kMF/s from steam. Pair with Electric Water Heater. Required for Coal Power Plant.","cost":350,"unlocks":[106],"requires":["mv_poles"],"tier":3,"branch":"power"},
    {"id":"logic_gates","name":"Logic Gates","description":"NAND, NOR, NOT, AND, OR, XOR gates — read silo fill levels and automate flow control.","cost":300,"unlocks":[103,104,105,111,112,113],"requires":["mv_poles"],"tier":3,"branch":"power"},
    {"id":"diesel_generation","name":"Diesel Generator","description":"Diesel Generator (2×1) — 90 kMF/s on diesel; 78 kMF/s on PQD. Needs diesel fuel from the Refining tree.","cost":500,"unlocks":[17],"requires":["mv_poles"],"tier":3,"branch":"power"},
    {"id":"wind_turbine_2","name":"Wind Turbine 2","description":"Wind Turbine 2 (2×2) — 16 kMF/s, ~10× Wind Turbine 1. Good mid-game clean power.","cost":600,"unlocks":[27],"requires":["wind_energy","mv_poles"],"tier":3,"branch":"power"},
    {"id":"hv_power","name":"HV Power Network","description":"HV Pole (2×2, 10-tile range) + HV Battery (2×2, 100 MMF) + HV Transformer (2×3) — planetary-scale power distribution.","cost":2000,"unlocks":[99,101,102],"requires":["energy_storage"],"tier":4,"branch":"power"},
    {"id":"gasoline_power","name":"Gasoline Generator","description":"Gasoline Generator (2×2) — 120 kMF/s on gasoline. Highest output generator. Needs gasoline from Production or Refining.","cost":600,"unlocks":[107],"requires":["diesel_generation"],"tier":4,"branch":"power"},
    {"id":"solar_tech_3","name":"Solar Panel 3","description":"Solar Panel 3 — 1,056 MF/s, double Solar 2. Caps the photovoltaic path.","cost":2000,"unlocks":[25],"requires":["solar_tech_2"],"tier":4,"branch":"power"},
    {"id":"wind_turbine_3","name":"Wind Turbine 3","description":"Wind Turbine 3 (3×3) — 50 kMF/s clean power. Top of the wind path.","cost":2500,"unlocks":[28],"requires":["wind_turbine_2"],"tier":4,"branch":"power"},
    {"id":"coal_power_plant","name":"Coal Power Plant","description":"Coal Power Plant (12×12) — 500 MMF/s from coal + water. Requires HV grid to distribute. Massive build cost.","cost":2500,"unlocks":[108],"requires":["steam_power","hv_power"],"tier":5,"branch":"power"},
    {"id":"nuclear_power","name":"Nuclear Power Plant","description":"Nuclear Power Plant (16×16) — 1.32 GMF/s from fuel_rod + distilled_water + control_rod. Fuel rods come from the Refining tree.","cost":5000,"unlocks":[96],"requires":["coal_power_plant"],"tier":5,"branch":"power"},
]


class ResearchManager:
    def __init__(self):
        self.rp = 0.0
        self.researched = set()
        self.load()

    def load(self):
        if os.path.exists("data/research.json"):
            try:
                with open("data/research.json", "r") as f:
                    data = json.load(f)
                    self.rp = data.get("rp", 0.0)
                    self.researched = set(data.get("researched", []))
            except (json.JSONDecodeError, ValueError):
                print("research.json corrupted. Starting fresh.")

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open("data/research.json", "w") as f:
            json.dump({"rp": self.rp, "researched": list(self.researched)}, f)

    def add_rp(self, amount):
        self.rp += amount

    def has_effect(self, effect_name):
        for tech in TECH_TREE:
            if tech["id"] in self.researched and tech.get("effect") == effect_name:
                return True
        return False

    def get_available_techs(self):
        return [t for t in TECH_TREE
                if t["id"] not in self.researched
                and all(r in self.researched for r in t.get("requires", []))]

    def get_researched_techs(self):
        return [t for t in TECH_TREE if t["id"] in self.researched]

    def can_research(self, tech_id):
        tech = self._get_tech(tech_id)
        if not tech or tech["id"] in self.researched:
            return False
        if not all(r in self.researched for r in tech.get("requires", [])):
            return False
        return self.rp >= tech["cost"]

    def research(self, tech_id):
        tech = self._get_tech(tech_id)
        if not tech or not self.can_research(tech_id):
            return None
        self.rp -= tech["cost"]
        self.researched.add(tech_id)
        self.save()
        return tech.get("unlocks", [])

    def get_all_unlocked_machines(self):
        unlocked = set()
        for tech in TECH_TREE:
            if tech["id"] in self.researched:
                for m in tech.get("unlocks", []):
                    unlocked.add(m)
        return unlocked

    def debug_unlock_all(self):
        all_unlocked = []
        for tech in TECH_TREE:
            if tech["id"] not in self.researched:
                self.researched.add(tech["id"])
                all_unlocked.extend(tech.get("unlocks", []))
        self.save()
        return all_unlocked

    def _get_tech(self, tech_id):
        for tech in TECH_TREE:
            if tech["id"] == tech_id:
                return tech
        return None

    def compute_rs1_rp_per_second(self, n_active):
        return 0.5 * float(max(0, n_active))

    def compute_rs1_cap(self, n_active):
        if n_active <= 0:
            return 0.0
        return 120.0 * math.log2(n_active + 1)

    def rs1_can_generate(self, n_active):
        if n_active <= 0:
            return False
        return self.rp < self.compute_rs1_cap(n_active)

    def compute_rs2_rp_per_second(self, total_rpx):
        if total_rpx <= 0:
            return 0.0
        return 2.0 * (total_rpx ** 0.6)

    def compute_rs2_cap(self, n_active):
        if n_active <= 0:
            return 0.0
        return 2000.0 * math.log2(n_active + 1)