# Milestone M2 Staging Report

## Summary
- Extended `game.yaml` to include needs override thresholds, room effects, and rating parameters; loaders consume these values.
- Students now honour configurable targeting overrides; rooms apply config-driven effects with knowledge gain; world tracks event history, rating deltas/flash state, and exposes them to renderer/headless logs.
- Rating system penalises critical needs and rewards recovery; HUD shows rating delta and flash state.
- Added golden tests: `test_needs_overrides.py`, `test_room_effects_config.py`, `test_rating_system.py`, plus updated HUD/headless tests.

## Tests
- `pytest -q technomancy/deliverables/tests`
- `pytest -q technomancy/deliverables/src/school_sim/tests`
