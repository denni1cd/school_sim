# School Simulation Engine (Placeholder-First)

**Python:** 3.12  
**Goal:** Engine-first simulation (PC movement + NPC schedules/activities) with clearly labeled **placeholders** for all visuals.

## Quickstart
```bash
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
make run      # launch interactive placeholder map
make simulate # run headless scheduling loop
make test
```

### Principal Controls (Milestone D)
- Press `P` in the pygame client to open the principal console overlay. While it is open you can acknowledge alerts with the number keys or issue a placeholder campus broadcast with `Shift+B`.
- Feed scripted commands to the headless simulator via `--commands`:
  ```bash
  python -m game.simulation --ticks 600 --commands scripts/principal_demo.txt
  ```
  The command dispatcher understands schedule overrides, summons, alert acknowledgements, and broadcasts. See `docs/principal_controls.md` for the full syntax.

### Map Selection
- Default sandbox loads `data/campus_map_v1.json`, a full boarding school layout with dorm wings, classrooms, cafeteria, and support spaces.
- Override the map in either headless or interactive modes via `--map`:
  - `python -m game.play --map campus_map_v1`
  - `python -m game.app --ticks 1200 --map data/campus_map_m5.json`

## Milestone 8 snapshot
- `config/interactions.yaml` still supplies role and room templates, now enriched with activity keys emitted by the factory.
- Activity catalog (`config/activities.yaml`) drives a hierarchy of activity classes with room-aware defaults, interaction keys, and placeholder metadata exposed through the factory.
- Simulation now records structured activity start/end/interrupt events, updates room occupancy summaries via `RoomManager`, and exposes the stream through `simulation.event_logger` or `python -m game.simulation --log-activities -`.
- Interaction text can incorporate activity labels and metadata, while the Pygame client displays a Tab-activated overlay summarizing the current room's occupants and tasks.
- Principal management hooks provide CLI and overlay tooling for schedule overrides, summons, alerts, and broadcasts; alerts are published for over-capacity rooms, missed classes, and curfew violations.
- `tests/activities/` verifies factory wiring and room reporting; scheduling, simulation, and interaction suites exercise the integrated flow end-to-end.

