# Milestone M1 Work Orders

## WO-1 Event Visibility + Overlay Contract
- **Stage to:** `technomancy/deliverables/src/school_sim/events/` as needed, tests under `technomancy/deliverables/tests`.  
- **Production targets:** `school_sim/events/scene_overlay.py`, `school_sim/events/event_rules.py`, `school_sim/world.py` (if additional state needed).  
- **Actions:** expose overlay state helpers if required for tests; ensure event firing toggles overlay and clears safely; guarantee 08:02 event triggers via bus during tick.

## WO-2 HUD Enhancements
- **Stage to:** `technomancy/deliverables/src/school_sim/renderer.py`, optionally `school_sim/bootstrap.py`/`world.py`/`configs/game.yaml`.  
- **Actions:** load baseline budget/rating (default or config), update world snapshot, render clock/rating/budget in HUD.

## WO-3 Headless Alignment
- **Stage to:** `technomancy/deliverables/src/school_sim/headless.py` and related modules.  
- **Actions:** capture event firing in headless mode (e.g., log marker or tracking flag) to support deterministic assertions.

## WO-4 Golden Tests + Fixtures
- **Stage to:** `technomancy/deliverables/tests/` with new files `test_events_visible.py`, `test_overlay_contract.py` (and HUD test if required).  
- **Actions:** migrate/retire legacy `test_event_system.py` while preserving coverage; use existing fixtures from `conftest.py`.

## WO-5 Merge Script Refresh + Reporting
- **Stage to:** `technomancy/deliverables/scripts/merge_m1.py`.  
- **Actions:** copy staged files to production, clean staging, update logs (`technomancy/logs/m1_staging_report.md`, later `final_report_m1.md`).
