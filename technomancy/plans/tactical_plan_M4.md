# Tactical Plan M4

## Objectives
- Deliver the Office Shell modal from Milestone M4 plus a config-driven Clubs tab that surfaces live membership counts and over-capacity warnings so the Headmistress can act with awareness.
- Confirm new traces appear in tests (`test_office_shell.py`) and match the club visibility acceptance noted in the project plan.

## Tasks

- **Task T4.1** – Office architecture review and data requirements (High Technomancer)
  - Description: Document which snapshots the office will rely on (club membership, events, economy history), ensure `OfficeScreen` tab navigation handles keyboard shortcuts, and confirm the club configuration YAML provides necessary metadata.
  - Assigned Role: High Technomancer
  - Required Paths: `/technomancy/plans/tactical_plan_M4.md`, `/technomancy/matrix/delegation_matrix.md`
  - Acceptance Checks: The office tab plan explicitly calls out membership counts/overflow lines and cites the spec’s Clubs section plus the project plan traceability entry for M4.

- **Task T4.2** – Implement Office tab membership visibility (Technomancer)
  - Description: Update `OfficeScreen._build_clubs_lines` to read `snapshot["clubs"]`, show member counts vs. capacity, flag overflow, respect keyboard navigation instructions, and expand `test_office_shell.py` to cover the new text.
  - Assigned Role: Technomancer
  - Required Paths: `technomancy/deliverables/src/office.py`, `technomancy/deliverables/tests/test_office_shell.py`
  - Acceptance Checks: `test_office_shell.py` asserts the club tab includes membership lines and overflow messaging when provided snapshot data; navigation and tab switching remain covered.

## Risks and Blockers
- Snapshot data must include club membership lists (World already records them). If snapshots are empty, the UI must still render a sensible fallback (zero members) without crashing.
- Adding overflow text *must* avoid encumbering wrapping logic in the renderer; confirm the HUD handles new strings gracefully.

## Standards
- Use object-oriented patterns already present in `OfficeScreen`; keep `OfficeTab` builders simple and side-effect free.
- Public helper methods need concise docstrings describing inputs/outputs.
- Tests must cover new behavior (membership counts and overflow warnings) deterministically without requiring live `World` runs.

## Deliverables
- `technomancy/deliverables/src/office.py`
  - Purpose: Read live club membership data from `World` snapshots, format lines so members/capacity appear together, and flag over-capacity warnings.
  - Acceptance Criteria Covered:
    - “Office modal plus tab navigation and club summaries” (from project plan M4 summary).
    - “Club membership visibility and overflow warnings” (traceability entry in the project plan).

- `technomancy/deliverables/tests/test_office_shell.py`
  - Purpose: Validate club tab output for default configs and snapshot-driven membership data, including overflow messaging.
  - Acceptance Criteria Covered:
    - “test_office_shell.py ensures navigation and config reflection.”
    - “Club tab membership display acceptance from the project plan.”

---
artifact: Tactical-Plan-Deliverables
milestone_id: "M4"
deliverables:
  - path: "technomancy/deliverables/src/office.py"
    purpose: "Surface live club membership data and overflow warnings in the Office Clubs tab."
    covers_acceptance_criteria:
      - "Office modal plus tab navigation and club summaries (M4 acceptance)."
      - "Club membership visibility and overflow warnings (project plan traceability)."
  - path: "technomancy/deliverables/tests/test_office_shell.py"
    purpose: "Regression tests for club membership lines and overflow messaging triggered by snapshots."
    covers_acceptance_criteria:
      - "test_office_shell.py ensures navigation/config reflection."
      - "Club tab membership display acceptance from the project plan."
validation:
  all_acceptance_criteria_covered: true
  uncovered_acceptance_criteria: []
