# Industrial Capitalist

My Software Engineering major project "Industrial Capitalist" is a comprehensive factory automation game built in Python using the Pygame Community Edition library. Players build and expand industrial production chains, starting from basic resource extraction like coal mining and advance to complex manufacturing operations while managing an evergrowing pollution crisis to become the ultimate Capitalist.

## Running

```bash
pip install -r requirements.txt
python3 main.py
```

## Documentation

| Document | What it covers |
| --- | --- |
| [`docs/MANUAL.md`](docs/MANUAL.md) | Full user manual - installation, controls, production, power, research, blueprints, pollution, troubleshooting, and a reference table for every machine |
| [`tutorial/README.md`](tutorial/README.md) | Ratio-perfect reference layouts with screenshots and ready-to-paste blueprint strings |
| [`docs/QA_REPORT.md`](docs/QA_REPORT.md) | Was done by claude code take lighlty but is a rough QA report from the end-to-end play-test pass: bugs found, root causes, fixes and balance changes |


## Blueprint strings

Blueprints can be exported to and imported from a single shareable string
(`IC1:...`). Open the library with **V**, then **EXPORT STRING** or
**IMPORT STRING**. Exported strings are copied to the clipboard and written to
`data/blueprint_strings/`. Ready-made layouts live in
[`tutorial/`](tutorial/README.md).

## Project layout

| File / folder | What lives there |
| --- | --- |
| `main.py` | Game loop: world simulation (items, power, pollution), event handling, world rendering |
| `settings.py` | All game data: machine stats, ports & recipes (`MACHINE_DEFS`), item values, contracts, build menu |
| `geometry.py` | Pure grid math: machine origins/footprints, port rotation, connection zones, power range |
| `ui.py` | HUD, toolbar and every panel (build, research tree, stats, market, blueprint library, ...) |
| `research.py` | Tech tree data + `ResearchManager` (RP, unlocks) |
| `contracts.py` | Contracts, loans and the supply/demand market |
| `blueprints.py` | Named blueprint library persisted to `data/blueprints.json` (shared across save slots) |
| `menu.py` | Main menu, save slots, audio |
| `protest.py` | Pollution protest events |
| `assets/` | Pixel art sprites (34 logical px per grid tile) |
| `data/` | Save data - created at runtime, not committed |

### Conventions worth knowing

- Machine **stats** (cost, size, power) live in `MACHINE_STATS`; machine **behaviour** (ports, recipes, flags) lives in `MACHINE_DEFS`. Both are keyed by the machine's integer id.
- Port positions are defined **unrotated** in `MACHINE_DEFS`; everything (placement preview, zone overlay, `can_connect`, item receive/push) rotates them through the shared helpers in `geometry.py`. If you add a machine with ports, define them once there and every system stays in sync.
- Sprites: input ports are marked with a green socket pixel, outputs with red, in the style of the pipe ends.

## Version History
### https://docs.google.com/document/d/1X5EWgT_7keE_5xkd5lLNm4uTNcSLNbVbVOj-zSHYnIY/edit?usp=sharing
