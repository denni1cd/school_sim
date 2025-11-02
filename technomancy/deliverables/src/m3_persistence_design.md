# M3 Persistence Design

## Save System Overview
- Serialize world state to `runtime/saves/save_YYYYMMDD_HHMM.json` containing:
  - `time_minutes`: current simulation time.
  - `students`: list of objects with `name`, `room`, `target`, and `needs`.
- Use `pathlib` and `json` for deterministic ordering and UTF-8 encoding.
- Provide `save_game(world)` that assembles the snapshot and writes to disk.
- Provide `load_game(path, world)` that reads JSON, validates schema, and mutates world state accordingly.

## Trigger Mechanics
- Expose CLI flag `--load path` to load a specified file at startup.
- Bind debug key `L` to load the most recent save. Use `glob` to find latest timestamped file.
- Save key `S` or auto-save every simulated hour (optional extension) while keeping MVP requirement focused on manual save.

## Data Integrity
- Validate JSON schema: ensure all student entries map to known room names; fallback to homeroom if missing.
- Clamp needs between 0 and 100 after loading to prevent corruption.
- Handle missing files gracefully by logging warnings and skipping load.

## Headless Logging
- Implement headless runner that executes 300 ticks, writes log lines into `runtime/logs/sim_log.txt`.
- Each line: `timestamp,name,room,target,hunger,energy,stress,hygiene`.
- Ensure deterministic order by sorting students by name before logging.

## Integration Points
- `main.py` accepts arguments to choose headless or interactive mode and load saves.
- `world.World` exposes `export_state()` and `apply_state(snapshot)` helpers.
- `make simulate` runs the headless script, ensuring log file creation.

## Testing Targets
- Save/load roundtrip equality for time and a subset of students.
- Loading invalid JSON raises `ValueError`.
- Headless log contains expected number of lines and deterministic content given seeded world.
