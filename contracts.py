import json
import math
import os
import random

CONTRACTS_FILE = "data/contracts.json"
LOAN_FILE = "data/loans.json"
MARKET_FILE = "data/supply_demand.json"


class LoanManager:
    COMPOUND_INTERVAL = 60.0
    BASE_RATE         = 0.030
    MIN_RATE          = 0.005
    MIN_LOAN          = 100

    def __init__(self):
        self.balance           = 0.0
        self.principal         = 0.0
        self.rate              = self.BASE_RATE
        self.compound_interval = self.COMPOUND_INTERVAL
        self.compound_timer    = self.COMPOUND_INTERVAL
        self.total_borrowed    = 0.0
        self.total_interest    = 0.0
        self.total_repaid      = 0.0
        self.loan_count        = 0
        self.load()

    def load(self):
        if not os.path.exists(LOAN_FILE):
            return
        try:
            with open(LOAN_FILE) as f:
                d = json.load(f)
            for k in ("balance", "principal", "rate", "compound_interval", "compound_timer", "total_borrowed", "total_interest", "total_repaid", "loan_count"):
                if k in d:
                    setattr(self, k, d[k])
        except (json.JSONDecodeError, ValueError, OSError):
            pass

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open(LOAN_FILE, "w") as f:
            json.dump({
                "balance":           self.balance,
                "principal":         self.principal,
                "rate":              self.rate,
                "compound_interval": self.compound_interval,
                "compound_timer":    self.compound_timer,
                "total_borrowed":    self.total_borrowed,
                "total_interest":    self.total_interest,
                "total_repaid":      self.total_repaid,
                "loan_count":        self.loan_count,
            }, f)

    def max_offer(self, money, research_rp):
        base          = 500.0
        from_capital  = max(money, 0) * 5.0
        from_research = max(research_rp, 0) * 50.0
        cap = base + from_capital + from_research
        return max(self.MIN_LOAN, cap - self.balance)

    def rate_for_amount(self, amount):
        decay = math.exp(-amount / 500_000.0)
        return self.MIN_RATE + (self.BASE_RATE - self.MIN_RATE) * decay

    def take_loan(self, amount, money):
        if amount < self.MIN_LOAN:
            return money, False, f"Minimum loan ${self.MIN_LOAN}"
        new_rate = self.rate_for_amount(amount)
        if self.balance > 0:
            self.rate = (self.balance * self.rate + amount * new_rate) / (self.balance + amount)
        else:
            self.rate = new_rate
            self.compound_timer = self.compound_interval
        self.balance       += amount
        self.principal     += amount
        self.total_borrowed += amount
        self.loan_count    += 1
        self.save()
        return money + amount, True, f"+${amount:,.0f} loaned @ {self.rate*100:.2f}%/min"

    def repay(self, amount, money):
        paid = max(0.0, min(float(amount), money, self.balance))
        if paid <= 0:
            return money, 0.0
        self.balance     -= paid
        self.total_repaid += paid
        if self.balance < 0.01:
            self.balance   = 0.0
            self.principal = 0.0
            self.rate      = self.BASE_RATE
            self.compound_timer = self.compound_interval
        self.save()
        return money - paid, paid

    def tick(self, dt):
        if self.balance <= 0:
            return 0.0
        self.compound_timer -= dt
        if self.compound_timer <= 0:
            interest = self.balance * self.rate
            self.balance       += interest
            self.total_interest += interest
            self.compound_timer = self.compound_interval
            self.save()
            return interest
        return 0.0

CONTRACTS = [
    {
        "id": "t1_01_ignition",
        "name": "System Ignition",
        "description": "Establish basic energy collection. Automate and deliver your first extraction batches of coal.",
        "requirements": {"coal": 30},
        "reward_money": 600, "reward_rp": 15, "tier": 1,
        "hint": "Place a Coal Drill, connect a Basic Pipe, and feed it into a Van Depot.",
    },
    {
        "id": "t1_04_thermal_test",
        "name": "Combustion Analysis",
        "description": "Provide a blended fuel delivery to gauge the operational efficiency of our early burner configurations.",
        "requirements": {"coal": 500, "raw_iron": 100},
        "reward_money": 4500, "reward_rp": 60, "tier": 1,
        "hint": "Run segregated logistics routes to a multi-port drop-off point.",
    },

    {
        "id": "t2_01_first_ingots",
        "name": "The Casting Line",
        "description": "Successfully feed liquid metal into an Ingot Molder to transition from raw material to structural bars.",
        "requirements": {"iron_ingot": 20},
        "reward_money": 5000, "reward_rp": 80, "tier": 2,
        "hint": "Iron Drill → Furnace → Ingot Molder → Van Depot.",
    },
    {
        "id": "t2_02_copper_induction",
        "name": "Conductive Foundations",
        "description": "Smelt raw copper ore into ingots. We need clean conducting pathways for low-voltage power relays.",
        "requirements": {"copper_ingot": 40},
        "reward_money": 6200, "reward_rp": 90, "tier": 2,
        "hint": "Set up a dedicated copper extraction site using Copper Drills.",
    },
    {
        "id": "t2_04_mixed_casting",
        "name": "Alloy Logistics Phase",
        "description": "Deliver a combined cargo of structural ingots to clear out the Tier 2 warehouse backlog.",
        "requirements": {"iron_ingot": 400, "copper_ingot": 250},
        "reward_money": 22000, "reward_rp": 150, "tier": 2,
        "hint": "Use Splitters to efficiently divide your coal fuel lines evenly between your iron and copper furnaces.",
    },

    {
        "id": "t3_01_steel_forge",
        "name": "The Carbon Threshold",
        "description": "Blast raw iron with concentrated carbon additives within the Blast Furnace to produce high-tensile Steel.",
        "requirements": {"steel": 50},
        "reward_money": 35000, "reward_rp": 250, "tier": 3,
        "hint": "Route Iron Ingots and Coke Fuel directly into a Blast Furnace.",
    },
    {
        "id": "t3_02_deforestation",
        "name": "Mill Scaling",
        "description": "Clear out timber preserves to supply organic bracing frames for heavy production lines.",
        "requirements": {"planks": 500},
        "reward_money": 28000, "reward_rp": 200, "tier": 3,
        "hint": "Automate a Tree Farm routing outputs directly into an Industrial Sawmill.",
    },
    {
        "id": "t3_04_logistics_strain",
        "name": "Throughput Threshold",
        "description": "Test the absolute mechanical limits of early basic piping lines with a massive structural delivery.",
        "requirements": {"iron_plate": 600, "steel": 300},
        "reward_money": 75000, "reward_rp": 400, "tier": 3,
        "hint": "Upgrade your core transport avenues to Adurite Pipes to completely eliminate line backing bugs.",
    },

    {
        "id": "t4_01_black_gold",
        "name": "Hydrocarbon Extraction",
        "description": "Tap deep subterranean reservoirs. Extract crude fluid and route it to surface logistics arrays.",
        "requirements": {"crude_oil": 1000},
        "reward_money": 95000, "reward_rp": 600, "tier": 4,
        "hint": "Deploy an Oil Rig over an open oil reservoir, then link it using Fluid Pipes to a Liquid Depot.",
    },
    {
        "id": "t4_03_vulcanization",
        "name": "Elastomer Compounding",
        "description": "Chemically treat heavy oil fractions to produce high-density industrial rubber seals.",
        "requirements": {"rubber": 300},
        "reward_money": 145000, "reward_rp": 900, "tier": 4,
        "hint": "Blend Naphtha and Sulfur within a specialized Chemical Plant line.",
    },
    {
        "id": "t4_04_chemical_saturation",
        "name": "Petrochemical Monopoly",
        "description": "Fulfill an extensive commercial contract requiring every major refined petroleum asset.",
        "requirements": {"plastic_pellets": 800, "rubber": 600, "machine_oil": 400},
        "reward_money": 280000, "reward_rp": 1500, "tier": 4,
        "hint": "Establish a broad multi-tiered petrochemical refinery grid running parallel processing steps.",
    },

    {
        "id": "t5_01_brine_milestone",
        "name": "Lithium Intercalation",
        "description": "Pump deep lithium-dense brine pools and dry the extract to isolate rare-earth minerals.",
        "requirements": {"lithium_carbonate": 200},
        "reward_money": 320000, "reward_rp": 2000, "tier": 5,
        "hint": "Pump Lithium Brine, route to an Evaporation Basin, and finish inside a Chemical Reactor.",
    },
    {
        "id": "t5_03_solid_state_gate",
        "name": "Solid State Micro-Architecture",
        "description": "Etch delicate circuitry pathways onto isolated silicon substrates to mass produce micro-semiconductors.",
        "requirements": {"semiconductor": 300},
        "reward_money": 450000, "reward_rp": 2800, "tier": 5,
        "hint": "Combine Silicon and Copper Wire inside a high-precision Advanced Assembler.",
    },
    {
        "id": "t5_04_sub_micron_supply",
        "name": "Material Sovereignty",
        "description": "Provide a massive shipment of advanced substrates to prepare the logic grid for computational staging.",
        "requirements": {"semiconductor": 600, "lithium_carbonate": 400},
        "reward_money": 750000, "reward_rp": 4000, "tier": 5,
        "hint": "Utilize ultra-capacity Iridium logistics pipes to avoid any physical item backing at processing points.",
    },

    {
        "id": "t6_01_matrix_logic",
        "name": "Computational Genesis",
        "description": "Interlink multi-stage semiconductors onto structural logic plates to create your first Logic Chips.",
        "requirements": {"microchip_2x": 100},
        "reward_money": 1200000, "reward_rp": 6000, "tier": 6,
        "hint": "Route Semiconductors and Logic Plates straight into a specialized Logic Assembler.",
    },
    {
        "id": "t6_03_fission_prep",
        "name": "Actinide Containment",
        "description": "Fabricate heavy shielding assemblies capable of housing volatile, high-output nuclear fuel reactions.",
        "requirements": {"reinforced_concrete": 1000, "steel_plate": 800},
        "reward_money": 2000000, "reward_rp": 8500, "tier": 6,
        "hint": "Scale up large Concrete Plants and run high-efficiency heavy stamping lines.",
    },
    {
        "id": "industrial_titan",
        "name": "Industrial Titan Status",
        "description": "The ultimate corporate milestone. Settle all pending legacy trade balances to cement your industrial legacy.",
        "requirements": {"microchip_2x": 2000, "charged_lithium_battery": 5000},
        "reward_money": 25000000, "reward_rp": 99999, "tier": 6,
        "is_final": True,
        "hint": "This is the final milestone. Maximize factory scale and optimize every pipeline bottleneck to complete the game.",
    },
]

class ContractManager:
    def __init__(self):
        self.active = {}
        self.completed = set()
        self.load()

    @property
    def contract_progress(self):
        return self.active

    def load(self):
        if os.path.exists(CONTRACTS_FILE):
            try:
                with open(CONTRACTS_FILE) as f:
                    data = json.load(f)
                self.active = data.get("active", {})
                self.completed = set(data.get("completed", []))
            except Exception:
                pass

    def save_contracts(self):
        os.makedirs(os.path.dirname(CONTRACTS_FILE), exist_ok=True)
        with open(CONTRACTS_FILE, "w") as f:
            json.dump({"active": self.active, "completed": list(self.completed)}, f)

    def _ensure_active(self, cid):
        if cid in self.active or cid in self.completed:
            return self.active.get(cid)
        contract = next((c for c in CONTRACTS if c["id"] == cid), None)
        if not contract:
            return None
        self.active[cid] = {item: 0 for item in contract["requirements"]}
        return self.active[cid]

    def get_available_contracts(self):
        return []

    def unlocked_tier(self):
        tiers = sorted({c["tier"] for c in CONTRACTS})
        for t in tiers:
            if any(c["id"] not in self.completed for c in CONTRACTS if c["tier"] == t):
                return t
        return tiers[-1]

    def get_locked_contracts(self):
        t = self.unlocked_tier()
        return [c for c in CONTRACTS if c["tier"] > t and c["id"] not in self.completed]

    def get_active_contracts(self):
        t = self.unlocked_tier()
        for c in CONTRACTS:
            if c["id"] not in self.completed and c["tier"] <= t:
                self._ensure_active(c["id"])
        return [c for c in CONTRACTS if c["id"] in self.active and c["tier"] <= t]

    def start_contract(self, cid):
        return self._ensure_active(cid) is not None

    def reset_contract(self, cid):
        if cid not in self.active:
            return False
        del self.active[cid]
        self._ensure_active(cid)
        self.save_contracts()
        return True

    def get_contract_progress(self, cid):
        return self._ensure_active(cid)

    def update_contract_progress(self, cid, item, amount):
        prog = self._ensure_active(cid)
        if prog is None:
            return
        if item in prog:
            contract = next((c for c in CONTRACTS if c["id"] == cid), None)
            if contract:
                prog[item] = min(prog[item] + amount, contract["requirements"][item])

    def check_contract_completion(self, cid):
        if cid not in self.active:
            return False
        contract = next((c for c in CONTRACTS if c["id"] == cid), None)
        if not contract:
            return False
        prog = self.active[cid]
        return all(prog.get(item, 0) >= qty for item, qty in contract["requirements"].items())

    def complete_contract(self, cid):
        contract = next((c for c in CONTRACTS if c["id"] == cid), None)
        if not contract:
            return None
        self.completed.add(cid)
        if cid in self.active:
            del self.active[cid]
        self.save_contracts()
        return {
            "money": contract.get("reward_money", 0),
            "rp":    contract.get("reward_rp", 0),
        }

    def sweep_on_load(self):
        auto_completed = []
        for cid in list(self.active.keys()):
            if self.check_contract_completion(cid):
                auto_completed.append(cid)
        for cid in auto_completed:
            self.complete_contract(cid)
        return auto_completed

    def debug_complete_all_contracts(self):
        total_money = 0
        for contract in CONTRACTS:
            if contract["id"] not in self.completed:
                self.completed.add(contract["id"])
                total_money += contract.get("reward_money", 0)
        self.active.clear()
        self.save_contracts()
        return {"money": total_money}

    def debug_reset_all_contracts(self):
        n = len(self.completed) + len(self.active)
        self.completed.clear()
        self.active.clear()
        self.save_contracts()
        return n

    def track_overflow(self, cid):
        pass

    def track_spending(self, cid, amount):
        if cid not in self.active:
            return
        prog = self.active[cid]
        prog["_spending"] = prog.get("_spending", 0) + amount

    def track_machine_count(self, cid, category, count):
        if cid not in self.active:
            return
        prog = self.active[cid]
        prog[f"_machine_{category}"] = count

    def track_idle_time(self, cid, dt):
        if cid not in self.active:
            return
        prog = self.active[cid]
        prog["_idle_time"] = prog.get("_idle_time", 0) + dt

    def update_contract_time(self, cid, dt):
        if cid not in self.active:
            return
        prog = self.active[cid]
        prog["time_elapsed"] = prog.get("time_elapsed", 0) + dt

    def is_machine_unlocked(self, machine_id, research_manager=None):
        from settings import STARTING_MACHINES
        if machine_id in STARTING_MACHINES:
            return True
        if machine_id in getattr(self, "_cheat_unlocks", set()):
            return True
        if research_manager:
            return machine_id in research_manager.get_all_unlocked_machines()
        return False

    def load_cheats(self):
        from settings import CHEAT_FILE
        self._cheat_unlocks = set()
        if os.path.exists(CHEAT_FILE):
            try:
                with open(CHEAT_FILE) as f:
                    data = json.load(f)
                self._cheat_unlocks = set(int(m) for m in data.get("unlocks", []))
            except (json.JSONDecodeError, ValueError, OSError):
                pass
        return self._cheat_unlocks

    def save_cheats(self):
        from settings import CHEAT_FILE
        os.makedirs(os.path.dirname(CHEAT_FILE), exist_ok=True)
        with open(CHEAT_FILE, "w") as f:
            json.dump({"unlocks": sorted(self._cheat_unlocks)}, f)

    def apply_cheat_code(self, code):
        from settings import CHEAT_CODES
        if not hasattr(self, "_cheat_unlocks"):
            self.load_cheats()
        entry = CHEAT_CODES.get(code.lower())
        if not entry:
            return False, None
        new_machines = [m for m in entry["unlocks"] if m not in self._cheat_unlocks]
        if not new_machines:
            return False, "Already unlocked"
        for m in new_machines:
            self._cheat_unlocks.add(m)
        self.save_cheats()
        return True, entry.get("message", "Unlocked!")


PRICE_REFRESH_INTERVAL = 3600.0
MAX_PRICE_SWING        = 0.08
PRICE_DRIFT_RATE       = 0.25
PRICE_HISTORY_SIZE     = 24


class MarketManager:
    def __init__(self):
        from settings import ITEM_VALUES
        self._tradeable    = {k for k, v in ITEM_VALUES.items() if v > 0.5}
        self.prices        = {k: 1.0 for k in self._tradeable}
        self.refresh_timer = 0.0
        self.price_history = {k: [] for k in self._tradeable}
        self._load()
        if all(abs(v - 1.0) < 1e-6 for v in self.prices.values()):
            self._shuffle()

    def _load(self):
        try:
            if os.path.exists(MARKET_FILE):
                with open(MARKET_FILE) as f:
                    d = json.load(f)
                for k, v in d.get("multipliers", {}).items():
                    if k in self.prices:
                        self.prices[k] = max(1 - MAX_PRICE_SWING, min(1 + MAX_PRICE_SWING, float(v)))
                self.refresh_timer = float(d.get("timer", 0.0))
                for k, hist in d.get("history", {}).items():
                    if k in self.price_history:
                        self.price_history[k] = [float(v) for v in hist[-PRICE_HISTORY_SIZE:]]
        except (json.JSONDecodeError, ValueError, OSError):
            pass

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open(MARKET_FILE, "w") as f:
            json.dump({
                "multipliers": self.prices,
                "timer":       self.refresh_timer,
                "history":     self.price_history,
            }, f)

    def tick(self, dt):
        self.refresh_timer += dt
        if self.refresh_timer >= PRICE_REFRESH_INTERVAL:
            self.refresh_timer = 0.0
            self._shuffle()
            return True
        return False

    def _shuffle(self):
        lo, hi = 1.0 - MAX_PRICE_SWING, 1.0 + MAX_PRICE_SWING
        for k in self.prices:
            cur   = self.prices[k]
            hist = self.price_history.setdefault(k, [])
            hist.append(round(cur, 5))
            if len(hist) > PRICE_HISTORY_SIZE:
                del hist[:-PRICE_HISTORY_SIZE]
            drift = (1.0 - cur) * PRICE_DRIFT_RATE
            room  = min(cur - lo, hi - cur)
            noise = random.gauss(0.0, MAX_PRICE_SWING * 0.4)
            noise = max(-room, min(room, noise))
            self.prices[k] = max(lo, min(hi, cur + drift + noise))

    def get_price(self, item):
        from settings import ITEM_VALUES
        return ITEM_VALUES.get(item, 0) * self.prices.get(item, 1.0)

    def get_multiplier(self, item):
        return self.prices.get(item, 1.0)

    def time_until_refresh_str(self):
        rem = max(0.0, PRICE_REFRESH_INTERVAL - self.refresh_timer)
        return f"{int(rem) // 60}:{int(rem) % 60:02d}"

    def get_movers(self, n=12):
        from settings import ITEM_VALUES
        pairs = [(k, v) for k, v in self.prices.items() if ITEM_VALUES.get(k, 0) > 0]
        pairs.sort(key=lambda x: abs(x[1] - 1.0), reverse=True)
        return pairs[:n]