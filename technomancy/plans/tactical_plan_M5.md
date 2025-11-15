# Tactical Plan M5

## Objectives
- Capture the last few policy decisions (uniforms & discipline) as structured history so that Office reports/headless logs surface the policy trail in addition to the Rating/Budget data already present.
- Keep acceptance coverage tight: trace the new logging requirement to `test_office_reports.py` and the policy history cap test while maintaining the spec-approved Golden Tests for policies.

## Tasks

- **Task T5.1** – Define policy-history presentation (High Technomancer)
  - Description: Outline what data (time, policy, value, delta, balance, caption) should be stored, capped, and surfaced via snapshots/reports; cite the policy reporting acceptance and ensure this requirement is reflected in the updated `m5_plan.md`.
  - Assigned Role: High Technomancer
  - Required Paths: `/technomancy/plans/m5_plan.md`
  - Acceptance Checks: Plan explicitly references policy history visibility and ties it to the Office Reports acceptance bullet.

- **Task T5.2** – Implement history logging and report output (Technomancer)
  - Description: Append policy history list to `world.get_debug_snapshot`, log per-change entries (capped), and update `office._build_reports_lines` + tests to render them; stage code/tests under `/technomancy/deliverables/**`.
  - Assigned Role: Technomancer
  - Required Paths: `/technomancy/deliverables/src/school_sim/world.py`, `/technomancy/deliverables/src/school_sim/office.py`, `/technomancy/deliverables/tests/test_office_reports.py`, `/technomancy/deliverables/tests/test_policy_history.py`
  - Acceptance Checks: `test_office_reports.py` verifies "Recent policy changes" lines, and `test_policy_history.py` ensures the journal exists and caps at five entries.

## Risks and Blockers
- Policy history must stay deterministic even when budgets block a change (history entries only for successful budget-adjusted changes). Use the existing budget helpers to gate logging.
- Ensure references to `OfficeScreen` internals remain testable without hitting the full renderer loop.

## Standards
- Keep the history entries simple dictionaries (time, policy, value, delta, balance, caption) and add them to `World.get_debug_snapshot` before the snapshot loop populates students/events.
- Tests must run via `conda run -n simulation_test pytest -q school_sim/tests`.

## Deliverables
- `technomancy/deliverables/src/school_sim/world.py`
  - Purpose: Append capped policy history entries, append them to snapshots, and expose them to the renderer.
  - Acceptance Criteria Covered:
    - “Policy history must be visible in Office reports” from this milestone’s acceptance.

- `technomancy/deliverables/src/school_sim/office.py`
  - Purpose: Render the latest policy changes inside the Reports tab.
  - Acceptance Criteria Covered:
    - “Office reports show recent policy changes alongside rating/budget data.”

- `technomancy/deliverables/tests/test_office_reports.py` & `technomancy/deliverables/tests/test_policy_history.py`
  - Purpose: Validate the Office reports text and the policy history cap/logging.
  - Acceptance Criteria Covered:
    - “Golden tests verify policy reporting transparency.”

---
artifact: Tactical-Plan-Deliverables
milestone_id: "M5"
deliverables:
  - path: "technomancy/deliverables/src/school_sim/world.py"
    purpose: "Store the last five policy decisions and include them in snapshots."
    covers_acceptance_criteria:
      - "Policy history must be visible in Office reports."
  - path: "technomancy/deliverables/src/school_sim/office.py"
    purpose: "Render policy history lines under the Reports tab."
    covers_acceptance_criteria:
      - "Office reports show recent policy changes alongside rating/budget data."
  - path: "technomancy/deliverables/tests/test_office_reports.py"
    purpose: "Ensure Reports text updates include the policy history section."
    covers_acceptance_criteria:
      - "Golden tests verify policy reporting transparency."
  - path: "technomancy/deliverables/tests/test_policy_history.py"
    purpose: "Assert policy history entries are recorded, capped, and include context."
    covers_acceptance_criteria:
      - "Golden tests verify policy reporting transparency."
validation:
  all_acceptance_criteria_covered: true
  uncovered_acceptance_criteria: []
