# Milestone M2 Work Orders

## WO-1 Config Foundations
- Stage under `technomancy/deliverables/src/school_sim/configs/` new files `game.yaml` extensions (targets, thresholds), `needs_overrides.yaml` if needed.
- Adjust loaders (`bootstrap.py`) and world/student modules to use config values.

## WO-2 Needs Override Implementation
- Update `student.py` and related logic to respect targeting overrides from config (per need thresholds, room priorities).
- Add/adjust tests under `technomancy/deliverables/tests` (`test_needs_overrides.py`).

## WO-3 Room Effects from Config
- Move `ROOM_TYPE_EFFECTS_PER_MINUTE` into config; allow delta definitions and ensure application via loader.
- Add tests verifying effects.

## WO-4 Rating System
- Introduce rating update logic (new module or within `world.py`) with flash/ delta tracking; renderer uses flag for HUD flash.
- Provide golden test `test_rating_system.py`.

## WO-5 Regression + Merge Script
- Ensure prior tests pass; extend merge script (`merge_m2.py`) to handle config/test additions.
- Stage report + final report updates.
