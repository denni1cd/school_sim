# Milestone M7 Staging Report

## Summary
- Added `school_sim/curriculum.py` with track validation/apply helpers and wired classroom modifiers through `World.tick`.
- Extended Office curriculum tab for track selection, emitting overlays via the event bus with updated scene overlay handling.
- Updated headless runner/status logging, save-system curriculum restores, and new curriculum/headless golden tests.

## Tests
- `$env:PYTHONPATH='src;..\..'; conda run -n simulation_test pytest -q tests`
