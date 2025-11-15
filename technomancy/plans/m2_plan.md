# Milestone M2 Plan

## Goal
Implement spec Milestone M2: configurable needs overrides (per-room/per-target thresholds), room effects, and rating tick/flash updates. Introduce golden tests `test_needs_overrides.py` and rating coverage; ensure headless and HUD reflect new behaviour.

## Current Assessment
- Student targeting already handles some crisis/preemptive logic but lacks config-driven overrides from `game.yaml`.
- Room effects currently hard-coded per room types; needs to move to configurable data and expose deltas for testing.
- Rating value is static; no tick logic or flash feedback tied to needs thresholds.
- HUD renders rating but does not flash or indicate delta.
- No rating/needs override tests yet.

## Work Streams
1. **Config Extensions & Loaders**
   - Expand `game.yaml` (or new config files) with needs thresholds, override multipliers, and rating parameters.
   - Update loaders (`bootstrap`, `world`, `student`, maybe `room`) to ingest new config.

2. **Needs Override Mechanics**
   - Implement configuration-driven overrides determining targeting decisions, including priority queue per spec (stress/hunger thresholds, etc.).
   - Add deterministic tests verifying behaviour.

3. **Room Effects**
   - Define per-room effect values in config; apply each tick with tests for positive/negative deltas.

4. **Rating System**
   - Add rating module or logic inside world to adjust rating per tick based on number of students in critical needs; implement flash indicator accessible via renderer snapshot.
   - Ensure budget unaffected this milestone but ready for future integration.

5. **HUD Feedback**
   - Provide rating delta info to renderer for flashing (maybe store `rating_flash_timer`).

6. **Testing & Regression**
   - Add golden tests per spec while keeping existing event overlay tests passing.

## Acceptance Evidence Needed
- `pytest -q school_sim/tests` passes including new needs & rating tests.
- Headless log indicates rating adjustments or demonstrates deterministic event/needs behaviours.
- `make simulate` and `make run` succeed without regressions; rating overlay highlight may remain manual but document expectation.
- Final report summarises rating changes and log evidence.
