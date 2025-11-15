# Milestone M5 Work Orders

## WO-1 Policy Module
- Add `technomancy/deliverables/src/school_sim/policies.py` implementing `apply_policy_effects`, `change_uniform`, `change_discipline`, compliance helpers.

## WO-2 World & Rating Wiring
- Update `technomancy/deliverables/src/school_sim/world.py` to call policy effects, maintain compliance stats, integrate into rating delta.
- Introduce `technomancy/deliverables/src/school_sim/rating.py` if needed to compute blended rating components.

## WO-3 Office Interaction & Renderer
- Extend `technomancy/deliverables/src/school_sim/office.py` to support selection/action states for policies tab.
- Ensure renderer/office link updates overlay/event bus (maybe via world + renderer) and console logging.

## WO-4 Persistence & Config
- Ensure policy state saves/loads (update `save_system.py` if necessary) and configs expose costs.

## WO-5 Tests
- New tests under `technomancy/deliverables/tests/` for uniforms, discipline, office navigation.
- Update existing fixtures/utilities if required.

## WO-6 Rituals
- Run staged tests, produce staging report, merge script `merge_m5.py`, final verification/report.
