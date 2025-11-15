# Milestone M8 Work Orders

1. Economy module & world integration
   - Production targets: `school_sim/economy.py`, `school_sim/world.py`, `school_sim/save_system.py`, `school_sim/headless.py`
   - Staging paths: `technomancy/deliverables/src/school_sim/{economy.py,world.py,save_system.py,headless.py}`
   - Actions: Implement transaction-aware budget helper, refactor world budget calls, persist/load transaction history, include history in headless status.
   - Tests: `technomancy/deliverables/tests/test_economy_budget.py`

2. Rating breakdown helper
   - Production targets: `school_sim/rating.py`, `school_sim/world.py`
   - Staging paths: `technomancy/deliverables/src/school_sim/{rating.py,world.py}`
   - Actions: Provide weighted rating calculator with breakdown dict; world should consume helper and expose summary.
   - Tests: `technomancy/deliverables/tests/test_rating_breakdown.py`

3. Office reports & renderer polish
   - Production targets: `school_sim/office.py`, `school_sim/renderer.py`
   - Staging paths: `technomancy/deliverables/src/school_sim/{office.py,renderer.py}`
   - Actions: Display rating components, budget history, and track toggles; update HUD/report rendering.
   - Tests: `technomancy/deliverables/tests/test_office_reports.py`, update `school_sim/tests/test_office_navigation.py`

4. End-to-end persistence & logging
   - Production targets: `school_sim/tests/test_headless.py`, `school_sim/tests/test_office_navigation.py`, configs if needed, merge script `merge_m8.py`, reports.
   - Staging paths: corresponding under `technomancy/deliverables/tests/` and `technomancy/deliverables/src/`.
   - Actions: Adjust tests for new status fields, ensure configs include budget parameters, update merge script and final report artifacts.

5. Verification & cleanup
   - Commands: `conda run -n simulation_test pytest -q`, `make simulate`, `make run` (bounded), confirm staging cleared and runtime cleaned.
   - Outputs: `technomancy/deliverables/scripts/merge_m8.py`, `technomancy/logs/m8_staging_report.md`, `technomancy/logs/final_report_m8.md`.
