# Milestone M1 Staging Report

## Summary
- Introduced `game.yaml` and path-resilient loaders so budget/rating defaults feed the world and HUD (`bootstrap.py`, `world.py`, `main.py`, `headless.py`).
- Extended renderer HUD to display clock, rating, and budget each frame with test-visible metrics hook.
- Added event history tracking in `World`, headless event logging, and overlay trimming/property helpers for golden tests.
- Authored golden tests `test_events_visible.py`, `test_overlay_contract.py`, and `test_hud_display.py` covering 08:02 event, overlay dismissal, and HUD metrics.

## Tests
- `pytest -q technomancy/deliverables/tests`
