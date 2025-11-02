# M3 Save System Reference

- `save_system.SaveSystem` encapsulates snapshotting, saving, loading, and applying JSON state to the active `World`.
- Snapshots include `time_minutes` and a `students` array with `name`, `room`, `target`, and `needs` values clamped to `[0, 100]`.
- Save files are timestamped (`save_YYYYMMDD_HHMMSS.json`) and written to `runtime/saves/`; directories are created on demand.
- `SaveSystem.load_latest(world)` locates the newest save and mutates the world in-place, repositioning students to room centers.
- Integration points: key `S` saves the game, key `L` loads latest save, and CLI flag `--load` triggers load on startup.
