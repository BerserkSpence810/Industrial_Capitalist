# Industrial Capitalist - QA Report

## ALL QA TESTING SAID HERE IS A GENERATED REPORT FROM CLAUDE CODE NOT ACTUAL TESTERS, TAKE WITH GRAIN OF SALT I ONLY REALLY USED FOR IMAGE STORAGE FOR TUTORIAL

**Method.** The game was played, not read. A harness (`qa/harness.py`) runs the
real `main.py` game loop with pygame's input functions redirected to a scripted
player: every click and keystroke goes through the game's own event handling,
every frame is produced by the game's own render path, and screenshots are taken
off the live display surface. Time is accelerated by removing the frame-rate
sleep - the simulation still advances at its normal 0.05 s tick.

All findings below were reproduced in a running game before being fixed, and
re-verified in a running game afterwards.

---

## Executive summary

The game is in good structural shape. Save/load is exact, the port/connection
geometry is correct for all 57 machines across all four rotations, every recipe's
data is internally consistent, the tech tree has no cycles or dead ends, and
headless performance is 133-150 fps with no degradation as the factory grows.

The defects were concentrated in **feedback rather than mechanics**. Three of the
eight reported bugs turned out to be systems that worked perfectly but reported
nothing, so they were indistinguishable from broken: exhaust stacks, scrubbers,
and the research stations hidden behind an unreadable tree. The genuinely broken
ones were blueprint power capture (real data loss) and the recipe labels (a
formatting bug affecting 33 recipes, of which the reported Concrete Plant case was
one instance).

**All eight reported issues are fixed and retested. Thirteen further bugs were
found, twelve of them fixed, plus blueprint import/export and Scrubber residue
added. 93 regression checks now pass** (26 data/logic, 67 in-game), all green.

A second pass covered the late game (see section 2b), reached by using the game's own
console cheats for money and research at the user's request, then playing
normally from there. That pass found four more defects, three of them severe
enough to kill whole production branches - including one that made six recipes
impossible to run at all.

---

## 1. The eight reported issues

### 1.1 Power connections don't save with blueprints - **FIXED**

| | |
|---|---|
| **Severity** | HIGH - silent data loss |
| **Found / Reproduced** | Yes / Yes |
| **Where** | `main._capture_blueprint`, `main._paste_blueprint`, `blueprints.py` |

**Reproduction.** New save -> place a Solar Panel and a Coal Drill -> `P`, wire
them -> `G`, drag over both -> paste elsewhere.

**Expected.** The pasted pair is wired and the drill runs.
**Actual.** `power_connections == []` on the pasted panel; the pasted drill's
power stayed at `0.0` indefinitely.

**Root cause.** `_capture_blueprint` recorded only `dx, dy, type, rotation,
recipe_mode`. Power wiring was never part of the blueprint format, so it could
not survive a paste - nor a save to the library.

**Fix.** Capture stores each machine's power connections as blueprint-relative
offsets under `power_links`, keeping only links whose target is also inside the
selection. Paste restores them in a second pass, after every machine exists, and
only for links whose target actually got placed (machines can be skipped for cost
or research). `blueprints.py` deep-copies the list so the clipboard and the stored
library entry cannot alias. Blueprints saved before this change load unchanged.

**Verification.** Reproduced end-to-end in the final playthrough:
`pasted solar conns: [(27, 18)]  pasted drill power: 94.0`.

**Regression tests.** `test_blueprint_entries_round_trip_power_links`,
`test_blueprints_without_power_links_still_load`, plus six live-game checks in
`tests/test_integration.py`.

---

### 1.2 Missing entries for better research stations - **FIXED (different root cause)**

| | |
|---|---|
| **Severity** | HIGH - reads as missing content |
| **Found / Reproduced** | Yes / Yes |
| **Where** | `ui.draw_research_panel` |

Research Station 2 and 3 **are** in the tech tree (production branch, tiers 3 and
5, at 400 and 2,500 RP), and both are correctly wired to buildable machines. The
problem was that you cannot read them.

**Root cause.** Hovering any node dims every node outside its ancestor/descendant
set, and the dimmed state rendered only `tech["name"][:4]` in RGB (18, 30, 18) on
an RGB (4, 6, 4) background - effectively invisible. Because the tree is dense,
the cursor is over *some* node almost all the time, so the normal reading
experience is a grid of blank boxes showing "Rese", "Blas", "Pape". A second
defect compounded it: the green **RESEARCH** button was gated on `nw >= 150`, so
zooming out even slightly made it vanish with no explanation while the node still
displayed its cost.

**Fix.** The focus dim is kept, but dimmed nodes now render their full name and RP
cost at reduced contrast, on a legible background. The RESEARCH button threshold
dropped from 150 px to 96 px.

**Verification.** `qa/shots/31_research.png` before and after: the whole tree,
including both research stations, is readable while hovering.

**Regression test.** `test_research_stations_2_and_3_are_in_the_tree` asserts both
machines are unlocked by a tech and correctly ordered.

---

### 1.3 Input/output alignment - "nothing in a tile" - **AUDITED CLEAN; ADJACENT BUGS FIXED**

| | |
|---|---|
| **Severity** | n/a for the port data; MEDIUM for the UI defects found |
| **Found / Reproduced** | Ports: no defect found. Related UI defects: yes |

**What was tested.** Every machine with declared ports (57 machines, 228
machine/rotation combinations) was placed into a live game world at 0 deg, 90 deg, 180 deg
and 270 deg, and for each declared port the harness checked, using the game's own
functions:

* `machine_try_receive` accepts the port's own item at the computed world tile;
* `can_connect` agrees from the neighbouring tile;
* **no other tile** of the machine accepts input from any direction;
* every output tile lies on the footprint and pushes outwards, not inwards.

**Result: zero mismatches.** A static audit (`qa/audit_ports.py`) independently
confirmed every port subtile sits on the footprint edge its direction faces.

The "nothing in a tile" symptom traced to three real but different defects:

1. **Exhaust Stack and Scrubber genuinely have no ports** - correct by design
   (they are not fed), but nothing in the game said so, so their tiles looked
   broken. Now documented in-game and in the manual (section 1.7, section 1.8).
2. **The machine info panel overflowed its own border.** It was a fixed 360 px
   tall; machines with several recipe modes and buffers painted their text
   straight out over the world, and the status line (`NEEDS CEMENT, AGGREGATE,
   WATER`) was cut off mid-word at the panel edge - so you could not read which
   input a tile was waiting for. **Fixed**: the panel is now sized from the
   machine's actual content, clipped to itself, and long status text wraps.
3. **Buffer labels ran off the panel** when a port accepted many items
   (`Cement / Wet Concrete / Clay: 0.00/6`). **Fixed**: collapsed to
   `Cement +2 more`.

**Regression tests.** `test_every_port_sits_on_the_edge_it_faces` and
`test_ports_stay_inside_the_footprint_when_rotated` (all machines x 4 rotations).

---

### 1.4 Concrete Plant: Clay Bricks -> Clay Bricks - **FIXED**

| | |
|---|---|
| **Severity** | MEDIUM - UI only; recipe logic was correct |
| **Found / Reproduced** | Yes / Yes |
| **Where** | `ui.draw_info_panel`, recipe-mode list |

**Root cause.** The label was built as `f"{mode_key} -> {produce}"`. Mode keys are
named after their *output*, not their input, so every such recipe printed
`X -> X`. The Concrete Plant's `clay_bricks` mode really consumes `clay` and
produces 3 `clay_bricks` - the data was right, only the label was wrong.

**Scope.** This affected **33 recipes across 8 machines**: Concrete Plant, Craft
Assembler, Plastic Refinery, Alloyer, Advanced Assembler, Chemical Plant,
Industrial Firebox. A full audit (`qa/audit_recipes.py`) also confirmed no recipe
consumes a buffer its ports cannot fill, and every recipe output has a sell value.

**Fix.** Each row is now labelled with what it makes (`Clay Bricks x3`), and a
**Needs:** block under the list shows the selected mode's real inputs and
quantities.

**Verification.** `qa/shots/B2_concrete_recipes.png` - a Concrete Plant showing
`Clay Bricks x3 / Wet Concrete / Concrete Block` and
`Needs: Cement x1, Aggregate x1, Water x0.5`.

**Regression tests.** `test_mode_recipes_declare_their_inputs`,
`test_mode_recipe_inputs_match_the_buffers_they_consume`,
`test_every_recipe_output_has_a_sell_value`, plus a live check that clicking a
mode row switches the machine's recipe.

---

### 1.5 Refining tech-tree balance - **REBALANCED**

**Measured problems.**

| Finding | Evidence |
|---|---|
| `oil_extraction` was a **400 RP tech with no prerequisites** | 3.3x the next most expensive prerequisite-free tech (Atmospherics, 120 RP) and 26x the cheapest |
| It was unreachable with one research station | Research Station 1's soft cap is 200.log2(n+1) RP - 400 RP needs **three** stations, and competes head-on with `research_station_2` at the identical 400 RP ceiling |
| The whole branch cost 4.4x production | Refining 26,100 RP total vs production 5,995 RP |
| Tier meant nothing across branches | Refining T2 (500-900 RP) cost more than production T5 (280 RP) |
| `coal_liquefaction`'s description was false | It claimed "Diesel feedstock without an Oil Rig", but the Diesel Refinery accepts only `crude_oil`; light/heavy oil feed the **Chemical Reactor** instead |

**Changes.**

| Tech | Before | After |
|---|---|---|
| Oil Rig (`oil_extraction`) | 400 RP, no prerequisite | **150 RP, requires Coal Furnace** |
| Diesel Refinery | 500 RP | 300 RP |
| Natural Gas | 500 RP | 300 RP |
| Filtration Plant | 500 RP | 300 RP |
| Petrochemistry | 700 RP | 500 RP |
| Gas Refinery | 600 RP | 450 RP |
| Coal Liquefaction | 900 RP, tier 2 | 500 RP, tier 3, **description corrected** |

Refining now enters at a price one research station can reach, behind a cheap
production prerequisite rather than as a free-standing beeline, and its second
rung is priced comparably to production's third. Tiers 5-7 are untouched - the
late branch was always meant to be expensive.

**Regression test.** `test_no_prerequisite_free_tech_is_a_cost_outlier` fails if
any prerequisite-free tech again costs more than a single station can bank.

---

### 1.6 General rebalance / checkover - **PARTIALLY CHANGED, REST REPORTED**

**Changed: Research Station 1 power draw, 2,100 -> 900 ME/s.**
Measured on a fresh save: at 2,100 ME/s the only available generator (Solar Panel,
280 ME/s) meant **eight panels, $960**, on top of the $75 station - and the
tutorial's own opening build (Coal Drill $150 + Van Depot $500) already costs
$650 of the $1,500 start. The result was roughly nine minutes of watching a coal
drill before the first research point existed. At 900 ME/s it is four panels, and
the whole opening fits inside the starting capital.

**Changed: Exhaust Stack vs Scrubber** - see section 1.7/section 1.8.

**Reported, not changed** (these need a design decision, not a QA tweak):

* **The Coal Generator dominates every other early generator.** $160 for
  7,000 ME/s is 43.8 ME/s per dollar against the Solar Panel's 2.3 - 19x better.
  Solar Panel 2 ($700, 528 ME/s) is *worse* per dollar than Solar Panel 1. The
  intended counterweight is pollution, but see below.
* **Pollution is too weak to be a counterweight.** A Coal Generator emits
  10.8 %/h, and 100 % pollution costs only a 0.90x income multiplier - roughly
  ten hours of play for a 10 % revenue cut. The pollution crisis that the game is
  themed around barely bites.
* **The early economy is slow.** One Coal Drill plus a Van Depot returns about
  $2/s for $650 of capital - a five-minute payback with nothing to do in between.
  Feeding several drills into one depot through a merger is the intended answer;
  the tutorial does not mention it. (It now does.)
* **Coal Liquefaction is a near dead end** until the Chemical Reactor four tiers
  later. Making the Diesel Refinery accept `light_oil` would make its description
  true and the chain real; that is a content change, so it is flagged rather than
  made.

---

### 1.7 Exhaust stack statistics / functionality - **FIXED**

| | |
|---|---|
| **Severity** | HIGH - a $2,000 machine that appeared to do nothing |
| **Found / Reproduced** | Yes / Yes |

**Measured behaviour before any change**, with pollution held at 100 % so the
zero-floor could not mask it:

```
empty world                  rate = +0.000000 %/s
1 exhaust stack (unpowered)  rate = -0.004000 %/s
3 exhaust stacks             rate = -0.012000 %/s
stacks removed               rate = +0.000000 %/s
```

**The mechanic was correct all along.** What was missing was every form of
feedback:

* the machine panel showed name, cost, size - and then an empty `STORAGE`
  heading with nothing under it;
* `POLLUTION_PER_MACHINE` has no entry for the stack, so the panel's pollution
  line was skipped entirely;
* **the Statistics panel had no pollution section at all** - only income, power
  and items sold.

**Fix.** `update_world` now tracks gross emissions and gross scrubbing as separate
accumulators (`update_special_generators` returns both) and publishes
`pollution_emitted` / `pollution_scrubbed` / `pollution_net` to the UI each tick.
The machine panel gained an **AIR SCRUBBING** block (`Removing`, `Rated`, and
"Passive - needs no power"), the Statistics panel gained a **POLLUTION** ledger
(level, income multiplier, emitted, scrubbed, net, plus a one-line diagnosis), and
the empty `STORAGE` heading is suppressed on machines with no storage.

**Regression tests.** Live measurement of the stack's exact rate, plus assertions
that it appears in the statistics ledger.

---

### 1.8 Scrubber functionality - **FIXED**

| | |
|---|---|
| **Severity** | HIGH - the game tells you to build these to survive |
| **Found / Reproduced** | Yes / Yes |

Same story, plus a balance inversion. Measured before any change:

```
1 scrubber (no power)        rate = -0.000000 %/s   (correctly inert)
1 scrubber (powered)         rate = -0.005000 %/s
scrubber + stack             rate = -0.009000 %/s   (they stack additively)
```

The mechanic worked. But the game says *"Fix: build Scrubbers to reduce
pollution"* and *"PROTESTERS BLOCKING TRUCKS! Build scrubbers or wait 5 min."* -
while the scrubber gave no indication whatsoever that it was doing anything, and
no indication when it was **unpowered and therefore doing nothing at all**.

**The balance was also inverted**: the Exhaust Stack removed 0.004 %/s for free,
forever, with no research beyond the same unlock - versus the Scrubber's
0.005 %/s for 5,000 ME/s. The powered machine was strictly worse.

**Fix.**

| | Before | After |
|---|---|---|
| Exhaust Stack | $2,000, -14.4 %/h, no power | **$900, -5.4 %/h, no power** |
| Scrubber | $1,500, -18 %/h, 5 kME/s | **$1,500, -28.8 %/h, 5 kME/s** |

The stack is now the cheap always-on baseline; the scrubber is a decisive upgrade
once you have power. Its panel reports **ACTIVE** with a live rate, or
**IDLE - needs full power to scrub**, and an underpowered scrubber shows a
"Removing" figure below its "Rated" figure. The Atmospherics tech description was
corrected to the new numbers.

**Regression tests.** Live rate measurements for unpowered stack, unpowered
scrubber, powered scrubber and both combined; the machine's self-reported
`scrubbing` state; the statistics ledger total; and
`test_powered_scrubber_beats_the_passive_exhaust_stack`.

---

## 2b. Late-game pass - findings

The first pass stopped at the iron chain. With money and research granted through
the in-game console (`mick3`, `mick2`), the rest of the game was reachable. Every
processing machine was then exercised in a live world: **135 recipes across 40
machines**, each one fed its declared inputs through the real port logic and run
until it produced. Before the fixes below, **116 of 135 produced output; after
them, 135 of 135**.

### L1 - Selecting a recipe mode made machines refuse their own ingredients - **CRITICAL, FIXED**

| | |
|---|---|
| **Severity** | CRITICAL - six recipes could never be run, killing four branches |
| **Where** | `main.machine_try_receive` |

**Reproduction.** Place a Concrete Plant, set it to **Wet Concrete**, try to feed
it cement. The port refuses. Same for Craft Assembler -> Crankshaft, Advanced
Assembler -> Logic Plate, Chemical Plant -> Lithium Carbonate, Chemical Plant ->
Acetic Acid, Industrial Firebox -> Coke Fuel.

**Root cause.** The port filter read:

```python
if recipe_mode and recipe_mode in accepted and item != recipe_mode:
    continue
```

That is correct for the Diesel Refinery, whose modes really are named after their
*input* (`crude_oil` -> `poor_quality_diesel` -> `diesel`). Every other
mode-recipe machine names its modes after the **product**. Whenever that product
was also an accepted input - because the machine consumes it in some other mode -
selecting the mode locked the port to the very item the recipe was supposed to
*produce*, so the machine could never be fed.

**Impact.** This is the functional twin of the reported Concrete Plant display
bug. It silently severed:

* **concrete** - no wet concrete, so no concrete blocks, so no reinforced concrete;
* **gold** - no acetic acid, so no karat gold, so no purified gold, liquid gold or purple gold;
* **lithium** - no lithium carbonate, so no lithium-ion battery, charged battery or battery pack;
* **microchips** - no logic plates, so no `microchip_8x64x`;
* crankshafts, tyre rims and coke fuel.

**Fix.** A new `main.mode_input_items()` resolves the allowed items from the
selected mode's own `inputs` list. Machines with no `mode_recipes` (the Diesel
Refinery) keep the old name-based behaviour, which is right for them.

**Verification.** All eight reproduction cases now accept their inputs; the live
recipe sweep went from 116/135 to 135/135.

**Regression tests.** `test_recipe_mode_resolver_uses_the_recipe_not_the_mode_name`
plus a live check across **all 63 recipe-mode inputs in the game**.

### L2 - The Huge Truck Depot never sold anything - **CRITICAL, FIXED**

| | |
|---|---|
| **Severity** | CRITICAL - an $8,500 machine behind a 220 RP tech that cannot pay out |
| **Where** | `main.update_world` depot block, `settings.MACHINE_DEFS[83]` |

**Measured before the fix:**

```
Van Depot          pushed=12   total_sold=12   money +$717.38
Huge Truck Depot   pushed=200  total_sold=0    money +$0.00
```

**Root cause.** Two faults stacked. The depot declares `input_ports`, so items
land in `input_buffer` / `input_item` - but the sell path reads the legacy
`stored` / `amount` pair, which stayed at zero forever. And its port `cap` was
200 while its advertised capacity is 350 with a 1.0 sell threshold, so even a
working sell path could never reach its own selling point.

**Fix.** The depot block now mirrors a declared port's buffer into
`stored`/`amount` (and clears it on sale), so one sell path serves both kinds of
depot. The port cap was raised 200 -> 350 to match the advertised capacity.

**Verification.** 350 items in, 350 sold, **+$28,573.92**.

**Regression tests.** `test_every_depot_can_reach_its_own_selling_point` plus a
live sell check.

### L3 - A power line could not branch - **HIGH, FIXED**

| | |
|---|---|
| **Severity** | HIGH - silently kills every branch after the first |
| **Where** | `main.transfer_power_between_tiles` and its call site |

**Measured before the fix**, one HV Pole wired to two downstream poles:

```
after 200 ticks:  hub=0   branch1=1,269,859   branch2=0
after 800 ticks:  hub=0   branch1=2,714,594   branch2=0
```

**Root cause.** Each connection was served in list order and took
`min(rate x dt, source_power, headroom)`. With HV transfer rates the first
connection drained the source every tick. A machine target eventually fills and
lets the next through, but a **pole** never fills - so a trunk-and-branch layout,
the natural way to power a large factory, left every branch after the first
permanently dead, showing only "NO POWER".

**Fix.** Each connection now gets an equal claim on what the source holds that
tick (`max_fraction = 1 / len(connections)`).

**Verification.** Both branches now charge (280k and 140k), and a generator with
surplus still tops up all of its machines to full.

**Regression tests.** Live checks for both the branching case and the
no-regression surplus case.

### L4 - Every tile of a multi-tile drill mined independently - **HIGH, FIXED**

| | |
|---|---|
| **Severity** | HIGH - wrong throughput, and most of the machine silently stalled |
| **Where** | `main.update_world` drill block |

**Measured before the fix**, 60 seconds each with a pipe under every face tile:

| Drill | Documented | Items stranded inside |
|---|---|---|
| Soil Excavator 2x2 | 15/min | 32 |
| Quarry 4x4 | 10/min | **108** |
| Mineshaft Drill 3x3 | 6/min | 30 |

**Root cause.** The drill branch had no origin guard - every other multi-tile
machine block has one. So all 16 tiles of a Quarry ran their own mining timer
into their own buffer. The four tiles on the output face could push out (giving
roughly 4x the documented rate); the twelve inner tiles filled to capacity and
stalled forever, holding items that could never leave, and each one also fed
`track_idle_time` into contract scoring.

**Fix.** The drill mines once per machine from its origin tile. A wide drill can
still feed any lane along the face it points at, but from a single shared buffer,
so the affordance survives without multiplying production. Contents are mirrored
across the footprint so clicking any tile shows what the machine holds.

**Verification.** Stranded items: 0 for every drill. Measured rates now match the
documented ones (Quarry 9.0/min vs 10 advertised, Mineshaft 5.0 vs 6).

**Regression tests.** Live checks on the Quarry and Mineshaft Drill for both
stranding and rate.

### Verified working in the late game

* **Every recipe** - 135/135 produce their declared output in a live world.
* **Oil branch** - Oil Rig -> three Diesel Refineries in series -> Liquid Truck
  Depot, played end to end: crude -> poor quality diesel -> diesel -> refined
  diesel, with residue drawn off the side port and burned in a Liquid Burner.
  Residue backpressure correctly stalls a refinery whose by-product has nowhere
  to go.
* **End-game power** - Water Pump -> Electric Water Heater -> Steam Turbine; the
  turbine banked 595-740 kME. Wind Turbine 3 and Solar Panel 3 both generate
  correctly; HV Poles relay across the map (they pass power through rather than
  store it, so an intermediate pole correctly reads ~0); HV Batteries charge.
* **Lithium branch** - Lithium Ore Drill -> Chemical Reactor -> Water Treatment ->
  Chemical Plant built, powered and flowing.
* **Construction branch** - Quarry -> Raw Mill -> Industrial Kiln -> Concrete Plant
  built, powered and flowing.
* **Console** - `mick3` / `mick2` / the settings panel's code console all work.
* Deep chains correctly stall when only one of their two or three ingredient
  lines is connected, and the machine panel names the missing input.

### Late-game observations (not bugs)

* **Machines late in the tree need two or three separate input lines.** A Raw
  Mill wants gravel, limestone *and* clay in three different ports; a Water
  Treatment Plant making table salt needs water in **both** of its ports. The
  panel's status line names what is missing, but the "Needs:" ingredient list is
  only drawn for mode-recipe machines - `recipe_map` machines (Chemical Reactor,
  Roller, Press, Grinder, Filtration, Sawmill, Lathe) do not get one. Worth
  extending.
* **A battery wired to the same generator as a pole never charges**, because the
  pole's transfer rate is far higher and it drains the source first. Now that
  branching shares fairly this is much less severe, but batteries still fill
  slowly when they share a source with a relay.
* **An Electric Water Heater draws 50 kME/s**, more than one Wind Turbine 3
  averages, so the intended pattern is to feed the heater from the Steam Turbine
  it powers once the loop is lit.

---

## 2c. Third pass - blueprint strings, remaining fixes, power hardening

### Shipped: blueprint import/export strings

Blueprints can now be exchanged as a single line of text. `blueprints.py` gained
`encode` / `decode` (zlib + urlsafe base64 behind an `IC1:` version prefix) and
the library panel gained **EXPORT STRING** and **IMPORT STRING**. Exports go to
the system clipboard *and* to `data/blueprint_strings/<name>.txt`, so a missing
clipboard is not a dead end. Imports accept a pasted string with any whitespace
in it and reject junk with a readable message rather than placing something
wrong.

A typical cell is around 120-160 characters. Position, rotation, recipe mode and
power wiring all survive the round trip - verified by exporting a powered cell,
clearing the library, importing the string back and placing it: the pasted drill
came up at full power.

### Fixed: four issues carried over from the previous report

| Issue | Fix |
|---|---|
| `recipe_map` machines showed no ingredient list, which is exactly where players stall - a Raw Mill wants three separate input lines and said so nowhere | The machine panel now prints a **NEEDS** block for them: `Gravel x1 / Limestone x1 / Clay x1`, and for keyed machines the resulting output too |
| The build panel's search filter persisted between openings, so unlocked machines looked missing | Cleared whenever the panel closes |
| Research Station 1's soft cap was invisible - RP simply stopped rising while the station read `RUNNING` | Its panel now shows stations running, RP/s, and `RP cap: 199 / 200`, with an explanation once the cap is hit |
| A failed power link left the source selected, so the next click wired A->B instead of picking B | The selection is dropped, and the message now names the actual distance |

### Fixed: power distribution was still biased

The previous pass stopped branches starving, but each connection took its share
of what was *left* rather than of the original pot, so a four-way split decayed
1 : 0.75 : 0.56 : 0.42. The source is now snapshotted before any connection is
served and each gets an equal slice. Measured across four batteries on one
generator: **78,750 each, exactly**.

### Power hardening

A dedicated pass over the whole power layer, now part of the test suite:

* every generator produces - Solar 1/2/3, Wind Turbine 1/2/3, Coal Generator,
  Diesel Generator, Steam Turbine, Gasoline Generator;
* every relay carries - LV, MV and HV Poles, each at its own range;
* MV and HV Batteries both charge and discharge into a machine;
* a four-way branch splits evenly, while a generator with surplus still fills
  every machine to capacity;
* an underpowered machine runs slower rather than stopping;
* a rotated generator still powers its target, and deleting one tears down its
  links.

**52 in-game checks and 20 data checks now pass** (up from 34 and 16).

### Verified: reference layouts

Five ratio-perfect layouts were built through the build panel in a live game,
left running, and confirmed before their strings were exported:

| Design | Ratio | Verified |
|---|---|---|
| Coal Outpost | 3 Coal Drills : 1 Van Depot | 198 coal sold |
| Research Cluster | 4 Solar Panels : 1 Research Station 1 | station held at 3,000 ME |
| Coal Power Block | 1 Coal Drill : 2 Coal Generators | both generators at 7,000 ME |
| Iron Smelter Cell | 5 Iron Drills : 1 Coal Drill : 1 Furnace | furnace saturated, producing liquid iron |
| Ingot Line | 2 Furnaces : 1 Ingot Molder : 1 Van Depot | 66 iron ingots sold |

They live in `tutorial/` with screenshots, port diagrams and their strings.

### Repo cleanup

* **Dead code removed** after checking every reference across all modules:
  `get_crt_overlay`, `get_coal_generator_origin`,
  `get_research_station_origin`, `get_blast_furnace_origin`,
  `is_part_of_coal_generator`, `can_coal_generator_receive_input` (main.py),
  `_apply_crt` (menu.py), `_oxidation_check` (settings.py), plus the unused
  `_crt_overlay` globals and the `AMBER_FAINT` / `RED_ERR` constants. The game
  boots and the full suite passes afterwards.
* **Build intermediates deleted**: `build/` (58 MB), all `__pycache__`, and every
  `.DS_Store`. `dist/` (94 MB, the built app) was **left alone** - it is the
  shipped artefact and is already gitignored; delete it yourself if you want the
  space back, it rebuilds from `IndustrialCapitalist.spec`.
* **`pixl/` was kept**: those `.pixil` files are the editable sources for the
  sprites, so they are not dead weight.
* **`.gitignore` now covers the assistant tooling**: `graphify-out/`,
  `.claude/`, `CLAUDE.md` and `qa/`, alongside the existing build and save-data
  entries.
* Because `qa/` is now ignored, the harness the integration tests depend on
  moved to **`tests/support/`**, so `tests/` runs from a clean checkout. `qa/`
  keeps only the exploratory scenarios and screenshots.

---

## 2d. Fourth pass - scrubber residue, port views, station footprints

### Shipped: the Scrubber now produces residue

Cleaning the air used to be free once powered. It now captures what it removes:
the Scrubber gained an output port on its bottom-left tile pushing down, fills
with **residue at 7.5/min**, and **stops scrubbing when that buffer (cap 8)
backs up**. Residue already existed in the game as a waste item worth -$8 and is
already accepted by the Liquid Burner and the Liquid Truck Depot, so it slots
into the existing disposal chain rather than inventing one.

This also gives the two air-cleaning machines genuinely different characters:
the Exhaust Stack *disperses* (no waste, no plumbing, never clogs) while the
Scrubber *captures* (five times stronger, but needs power and a pipe out).

The panel reports it - `Makes 7.5 residue/min`, and a `RESIDUE FULL - pipe it to
a Liquid Burner` status once blocked. Verified end to end: a blocked scrubber
stops and pollution stops falling; connect a Liquid Burner under it and both
resume.

### Fixed: the debug overlay and the placement preview disagreed

**Root cause.** The two views worked port positions out independently. For any
machine falling back to `MACHINE_STATS` directions (no `input_ports` in
`MACHINE_DEFS`), the preview drew one arrow at subtile `w // 2` while the
overlay centred one bar on the whole edge - **half a tile apart on every
even-sized machine**: Coal Generator, Copper Drill, Soil Excavator, Quarry,
Lithium Ore Drill.

Worse, *both* were wrong about the truth. A wide drill pushes from **every tile
along the face it points at** (`_drill_output_tiles`), and a Coal Generator
accepts coal on **any** of its tiles - while the views each drew a single
marker.

**Fix.** One new function, `geometry.machine_port_tiles(ttype, rotation, ...)`,
returns the complete, truthful set of port tiles in the rotated frame, covering
the defs-based ports, the Coal Generator special case, and the stat-based
fallback. `draw_connection_zones` and the placement preview were both rewritten
to call it, so they cannot drift apart again.

Visible result: a Quarry now shows **four** red output markers along its bottom
edge and a Coal Generator **two** green input markers along its top - matching
what the simulation really does, in both views.

### Fixed: Research Station 3's second feed port was off its own footprint

Resizing RS2 to **4 x 4** and RS3 to **5 x 5** surfaced a latent bug: RS3's
second input port sat at subtile **(5, 0)**, which is outside a 5-wide
footprint - it would have been unreachable. Both feeds moved to (1, 0) and
(3, 0). A regression test now asserts every research-station port lies inside
its footprint, sits on the top edge, and does not collide with another port.

### Also fixed

Floating status messages were anchored at y=72, colliding with the
`PLACING <machine> | $cost` banner under the HUD cards; moved clear.

### Self-inflicted: a footprint typo, caught and fixed

While changing Research Station 1's power draw in an earlier pass I also
fat-fingered its size from `(2,2)` to `(2,1)`. It kept placing, kept running and
kept generating RP - it had simply lost half of itself, and nothing in the suite
noticed because every test asked about ports and power, never about footprints.

Caught by eye afterwards (`tile_counts` showed `13: 2` where an earlier run had
`13: 4`), restored to `(2,2)`, and `test_multi_tile_machines_have_sane_footprints`
now pins the known sizes so a silent one-character change cannot slip through
again.

A full data diff against `HEAD` confirmed nothing else in `settings.py` drifted:
the only other difference, `steel` at 50.0 rather than 48.72, was already in the
working tree before this work started.

**93 regression checks now pass** (26 data/logic, 67 in-game).

---

## 3. New bugs found (first pass)

| ID | Severity | Bug | Status |
|---|---|---|---|
| N1 | MEDIUM | **WASD pans the camera while you type.** The pan reads `pygame.key.get_pressed()` unconditionally, so typing `sand`, `water` or `steel` into the build/market/recipe search, or naming a blueprint, drags the view across the map. | Fixed - pan is gated on a new `ui.text_input_active()` covering all five text fields |
| N2 | MEDIUM | **Machine info panel overflowed its border**, painting text over the world, and clipped long status lines mid-word. | Fixed - content-sized panel, clipped, with wrapped status text |
| N3 | MEDIUM | **The tutorial states wrong facts.** Coal Drill "$50" (really $150), Van Depot "$100" (really $500), "You start with a Research Station 1" (you start with nothing), coal "$5.22" (really $5.20), solar range "~5 tiles" (really 3). | Fixed - the tutorial now derives every figure from `MACHINE_STATS`/`ITEM_VALUES`, so it cannot drift again |
| N4 | MEDIUM | **Stalled machines are undiscoverable.** The `[O]` overlay and the per-machine stall diagnostics are genuinely good, but `[O]` is not on the toolbar, not in the tutorial and not in the keybind list - a mis-wired factory just sits there silently. | Fixed - HUD banner `[!] N machines idle - press [O] to see why`, and `O`/`V`/`G`/`M`/`L` added to the in-game keybind list |
| N5 | LOW | **Empty `STORAGE` heading** drawn on machines with no item storage. | Fixed |
| N6 | LOW | **A failed power link leaves the source selected.** After "Out of range!", clicking a second generator tries to wire A->B instead of selecting B. | Reported - behaviour is arguably intentional (retry), left alone |
| N7 | LOW | **Esc does not close the Market panel.** Every other panel is listed in the central Esc dispatcher; the market was simply omitted, so it could only be closed with `M` or its X button. | Fixed - added to the same dispatcher. Verified by opening and Esc-closing all eight panels in a live game |
| N8 | LOW | **Status messages draw on top of each other.** Every floating message was anchored at the same pixel, so two arriving together were illegible (observed as "Bottleneck Overlay: ON", "OFF" and "Game Saved" superimposed). | Fixed - messages stack downwards from the anchor, clear of the HUD |
| N9 | COSMETIC | **Items-sold rates clipped** in the Statistics panel (`90.0/n`, `6.0/mi`) - the bar was 38 px too wide for its label. | Fixed |

### Design traps (not bugs, worth knowing)

* **Coal Generator bootstrap deadlock.** Wiring the coal drill that feeds a Coal
  Generator *to that same generator* means neither ever starts. Hit during play;
  now called out in the manual with a worked example.
* **Delete mode is one-shot.** `X` then a click deletes one machine and exits;
  Shift keeps it active. Undocumented before - now in the tutorial and manual.
* **Blueprint paste mode stays armed** after pasting, so a stray click stamps
  (and charges for) another copy. Intentional for repeat-stamping and the on-screen
  hint says so.

---

## 4. Balance issues (separate from bugs)

| # | Issue | Evidence | Action |
|---|---|---|---|
| B1 | Research Station 1 unaffordable to power on a fresh save | 8 solar panels / $960 needed against $1,500 starting capital with a $650 income build | **Changed**: 2,100 -> 900 ME/s |
| B2 | Exhaust Stack strictly dominated the Scrubber | 0.004 %/s free vs 0.005 %/s for 5 kME/s | **Changed** (section 1.8) |
| B3 | Refining entry priced above what one research station can bank | 400 RP vs a 200 RP soft cap | **Changed** (section 1.5) |
| B4 | Coal Generator dominates all early power | 43.8 ME/s per $ vs solar's 2.3 | Reported |
| B5 | Solar Panel 2 is worse value than Solar Panel 1 | 0.75 ME/s per $ vs 2.3 | Reported |
| B6 | Pollution's income penalty is too weak to matter | 100 % pollution ~ 10 h of play for a 10 % revenue cut | Reported |
| B7 | Early economy is slow relative to costs | ~$2/s from a $650 build | Reported; mitigated by teaching the merger pattern |
| B8 | Coal Liquefaction is a near dead end | outputs only usable by the Chemical Reactor, four tiers away and behind the Oil Rig it claims to replace | Reported; description corrected |

---

## 5. UX issues

1. **Nothing is powered until it is wired.** Proximity is not enough, and the
   only feedback is a transient toast. Addressed by the idle-machine HUD banner
   and by an explicit tutorial step.
2. **The research tree's focus dim destroyed readability** (section 1.2).
3. **The build panel's search filter persists** between openings, so a machine can
   appear "locked" when it is merely filtered out. Worth an auto-clear on close.
4. **Multi-tile machines accept input on one specific tile**, which is only
   discoverable via `Z`. The manual now leads its troubleshooting with `Z`.
5. **Depot direction is not obvious.** A Van Depot accepts only from the north,
   so it must sit *below* a Coal Drill. Now stated explicitly in the tutorial.
6. **No in-game explanation of the Research Station 1 soft cap.** RP simply stops
   rising while the station still reads `RUNNING`. Documented in the manual;
   an in-panel note would be better.

---

## 6. Performance and stability

Measured headless with the frame limiter removed:

| World | Frame rate |
|---|---|
| Empty | 133 fps |
| 3 machines | 146 fps |
| 200 pipes + machines | 150 fps |

No degradation with factory size, no memory growth, no error spam, no freezes.
`update_world` costs ~3 ms per tick. **No performance problems found.** Panels
that rebuild full-screen alpha surfaces every frame (research tree, build panel)
are the heaviest draws but stay comfortably above 60 fps.

No crashes occurred in any scenario. The two harness aborts during testing were
both faults in my own test scripts (a scenario left blueprint paste mode armed;
`pygame.key.get_mods` was not stubbed), not game defects - the second of those
did reveal that the harness had never been exercising `Ctrl+S`, which is now
covered.

---

## 7. Test coverage - what was actually tested

**Played end to end, in a running game:**

* Boot sequence, terminal main menu, save-slot select, company registration,
  story intro, tutorial overlay.
* Placing, rotating and deleting machines through the build panel; the search box;
  Shift-repeat placement; box delete with Y/N confirmation.
* Coal Drill -> Van Depot income; three drills -> pipes -> merger -> one depot.
* Power mode: wiring, range limits, out-of-range rejection, link removal.
* Research Station 1 power-up, RP accrual, the soft cap, a second station.
* Researching `coal_power`, `smelting`, `iron_extraction`, `ingot_casting`,
  `atmospherics` by clicking the tree; all four branch tabs.
* Coal Generator fuelling and bootstrap; the full iron chain
  (Iron Drill -> Furnace -> Ingot Molder -> Van Depot) producing and selling ingots.
* Blueprint capture by drag, save to library with a name, delete originals, paste
  from the library, verify wiring and power.
* Exhaust Stack and Scrubber pollution rates, powered and unpowered, individually
  and combined, measured against the simulation.
* Ctrl+S save, slot reload, and continued play after loading.
* Every panel opened and screenshotted: build, research (x4 tabs), contracts,
  statistics, market, recipe book, loans, blueprints, settings, machine info,
  debug port view, bottleneck overlay.

**Audited exhaustively (data + live game):**

* 57 machines x 4 rotations = 228 port configurations.
* All 107 buildable machines against the build categories and tech unlocks.
* All mode recipes, recipe maps and refinery recipes for input/output/value
  consistency.
* The whole tech tree for cycles, dangling prerequisites, dead unlocks and cost
  outliers.

**Late-game pass (money and research granted via the in-game console at the
user's request, then played normally):**

* Every processing machine and every recipe mode exercised in a live world -
  135 recipes across 40 machines, fed through the real port logic.
* Oil branch played end to end, including by-product disposal and backpressure.
* Steam power chain (Water Pump -> Electric Water Heater -> Steam Turbine).
* Wind Turbine 3, Solar Panel 3, HV Poles, HV Batteries, and power branching.
* Lithium and construction chains built, powered and flowing.
* Huge Truck Depot and Liquid Truck Depot selling behaviour.
* Multi-tile drill throughput (Quarry, Mineshaft Drill, Soil Excavator).
* The in-game code console.

**Still not tested** (stated plainly rather than claimed):

* The Nuclear Power Plant (16x16, 300 s cycle) and the Coal Power Plant (12x12)
  were never run - their recipes were verified in the sweep, but neither was
  built and fuelled in a live factory.
* The full microchip chain end to end (Logic Assembler -> Advanced Assembler),
  and the gold chain past the Chemical Plant. Their individual recipes pass the
  sweep, but the chains were not assembled.
* Logic gates and signal wiring beyond placement.
* Contracts beyond the first, loans, and market price dynamics over time.
* Audio.
* Windows and Linux (tested on macOS only).
* Multi-hour sessions for long-run memory behaviour.

---

## 8. Files added

| Path | Purpose |
|---|---|
| `qa/harness.py` | Drives the real game loop with scripted input; captures screenshots |
| `qa/common.py` | Player actions: boot, build, wire power, place blueprints, inspect |
| `qa/scen_*.py` | The play scenarios used above |
| `qa/audit_ports.py`, `qa/audit_recipes.py` | Standalone data audits |
| `tests/test_regressions.py` | 14 data/logic regression tests |
| `tests/test_integration.py` | 23 in-game regression checks |
| `docs/MANUAL.md` | The user manual |
| `docs/QA_REPORT.md` | This report |

Run the tests with:

```bash
python3 tests/test_regressions.py     # fast, no display needed
python3 tests/test_integration.py     # boots the game headless, ~2 minutes
```
