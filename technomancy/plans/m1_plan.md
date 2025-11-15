# Milestone M1 Plan

## Goal
Deliver the Events + Overlay + HUD milestone: deterministic event firing at 08:02 with on-screen overlay, principal console integration, and HUD showing time/rating/budget values. Introduce the first golden tests (`test_events_visible.py`, `test_overlay_contract.py`) and ensure headless mode reflects the seeded event.

## Current Assessment
- Event bus/rules exist but lack explicit tests covering 08:02 overlay behaviour expected by spec.
- `SceneOverlay` displays captions but renderer HUD only shows time and student needs; no rating/budget indicators.
- Headless runner does not currently surface event firing, making it hard to assert overlay visibility or log evidence.
- Golden test filenames in spec are absent; existing tests (`test_event_system.py`, etc.) should be superseded or migrated to new contracts.

## Work Streams
1. **Event Visibility & Overlay Contract**
   - Ensure `SceneOverlay` binds correctly, exposes active caption, and dismisses on ESC/ENTER.
   - Update event rules/overlay as needed to emit state for tests.
   - Add golden tests verifying 08:02 event and overlay transitions.

2. **HUD Enhancements**
   - Extend renderer to render rating and budget fields in HUD sidebar.
   - Plumb baseline rating/budget values from `World` (load defaults from config or constants).
   - Include values in debug snapshot for headless verification and upcoming systems.

3. **Headless Determinism Alignment**
   - Ensure headless simulation triggers events and optionally records overlay activations in log or emitted data to satisfy tests.
   - Update tests/headless runner to assert event fired at expected tick.

4. **Test Suite Migration**
   - Replace legacy event tests with spec-aligned golden tests.
   - Update fixtures/helpers as needed for new package layout.

## Acceptance Evidence Needed
- `pytest -q school_sim/tests` passes including new golden tests.
- Headless run produces log entries confirming event tick (ensures overlay event fired by 08:02).
- Manual (headless) confirmation that overlay open/dismiss cycle does not crash; graphical verification noted for future milestone if not fully automated.
- `/technomancy/deliverables/**` clear of shippables post-merge; final report summarises HUD additions and event coverage.
