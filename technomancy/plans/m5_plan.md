# Milestone M5 Plan

## Goal
Implement functional policies system: uniforms and discipline effects influence student needs and compliance, policy changes deduct budget and trigger overlays, and office interactions persist changes.

## Current Assessment
- Policy configs load but world ignores them beyond initial state.
- No `policies.py` module or per-tick effect hook.
- Office screen `activate` is a stub; cannot change policies or budget.
- Rating logic lacks compliance component.
- No automated tests for policy mechanics or office-driven policy changes.

## Work Streams
1. **Policy Engine**
   - Build `policies.py` providing effect helpers and change operations (budget cost + overlay caption).
2. **World Integration**
   - Apply policy effects each tick; track compliance metrics affecting rating; expose hooks for discipline events.
3. **Office Interaction**
   - Enable tab selection + ENTER to modify uniforms/discipline, call policy engine, deduct budget, log + overlay.
4. **Testing**
   - Golden tests for uniforms, discipline, and office navigation; extend fixtures as needed.
5. **Technomancy Rituals**
   - Stage via deliverables, run tests headlessly, produce merge script/report, verify post-merge.

## Acceptance Evidence
- New golden tests pass under `pytest -q school_sim/tests`.
- `make simulate` and `make run` succeed with visible policy changes and overlay.
- Budget reflects policy adjustments; compliance affects rating trend in tests.
