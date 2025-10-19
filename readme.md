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

### Map Selection
- Default sandbox loads `data/campus_map_v1.json`, a full boarding school layout with dorm wings, classrooms, cafeteria, and support spaces.
- Override the map in either headless or interactive modes via `--map`:
  - `python -m game.play --map campus_map_v1`
  - `python -m game.app --ticks 1200 --map data/campus_map_m5.json`

## Milestone 8 snapshot
- `config/interactions.yaml` defines room/role/activity messages; defaults merge via the shared config loader.
- Simulation surfaces context-aware interaction text using room metadata and current activities, seeds the first daily activity for every NPC, and activity timers now account for late arrivals so tasks last their intended duration.
- Pygame client inherits the richer messages automatically; no new controls required.
- `tests/test_interactions.py` validates library and MakerLab dialogues so regressions are caught early.


