# M3 Headless Logging Reference

- `headless.py` exposes `run_headless(ticks=300, log_path=..., load_path=...)` that runs the simulation without Pygame and writes a CSV-like log.
- Logs are stored under `runtime/logs/sim_log.txt` by default; directory is created automatically.
- Each tick advances time by one in-game minute and writes lines ordered by student name to maintain determinism.
- The `make simulate` target can invoke `python headless.py --ticks 300` to produce the log for acceptance testing.
- Optional `--load <path>` argument loads the most recent save before running the headless simulation, enabling replay scenarios.
