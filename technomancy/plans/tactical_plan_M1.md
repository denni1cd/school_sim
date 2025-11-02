# Tactical Plan M1

## Objectives
- Complete Milestone M1 "Core Simulation Stability" by delivering D1 Room Effects and D2 Needs Overrides with automated tests that prove needs thresholds.
- Stabilize the core simulation loop so subsequent milestones can rely on deterministic needs updates and student decision overrides.
- Ensure all work adheres to Python 3.12, YAML-driven configuration, and existing module boundaries defined in the project plan.

## Tasks
- Task ID: T1  
  Description: Direct architecture for Room effects and needs escalation thresholds and stub required tests.  
  Assigned Role: High Technomancer  
  Required File Paths: `technomancy/deliverables/src/m1_room_effects_design.md`, `technomancy/deliverables/tests/m1_needs_tests_outline.md`  
  Acceptance Checks: Deliverables D1 and D2 acceptance criteria defined and referenced in tactical plan.

- Task ID: T2  
  Description: Implement Room.apply_effects, finalize student decision overrides, and ship automated tests proving thresholds.  
  Assigned Role: Technomancer  
  Required File Paths: `technomancy/deliverables/src/m1_room_effects.py`, `technomancy/deliverables/src/m1_student_needs_overrides.py`, `technomancy/deliverables/tests/test_m1_room_effects.py`, `technomancy/deliverables/tests/test_m1_student_needs.py`  
  Acceptance Checks: D1 Room Effects acceptance criteria; D2 Needs Overrides acceptance criteria.

## Risks and Blockers
- Existing repository artifacts may conflict with new implementations; ensure only authoritative modules defined in the specification are touched.
- Needs thresholds could lack historical coverage, increasing test design complexity; capture edge cases before implementation begins.
- Read-only or restricted runtime assets could impede automated test execution; validate environment permissions before development.

## Standards
- Enforce single-responsibility principles within updated modules (`room.py`, `student.py`) to keep logic composable and testable.
- Require docstrings or inline documentation only where non-obvious algorithms arise; keep explanations concise.
- Maintain automated unit tests with deterministic assertions; ensure coverage includes both normal and edge-case schedules.
- Align code style with existing Python conventions in the repository and utilize dependency contracts defined in the specification.

## Deliverables
- `technomancy/deliverables/src/m1_room_effects_design.md` — Capture architectural directives for Room effects and critical threshold handling.
- `technomancy/deliverables/tests/m1_needs_tests_outline.md` — Document planned automated test scenarios for needs adjustments.
- `technomancy/deliverables/src/m1_room_effects.py` — Provide the finalized Room.apply_effects implementation according to specification A5.
- `technomancy/deliverables/src/m1_student_needs_overrides.py` — Supply the complete student decision override logic for critical needs.
- `technomancy/deliverables/tests/test_m1_room_effects.py` — Implement automated tests validating room effect deltas against specification thresholds.
- `technomancy/deliverables/tests/test_m1_student_needs.py` — Implement automated tests validating decision logic for hunger, energy, stress, and hygiene overrides.

```yaml
---
artifact: Tactical-Plan-Deliverables
milestone_id: "M1"
deliverables:
  - path: "technomancy/deliverables/src/m1_room_effects_design.md"
    purpose: "Capture architectural directives for Room effects and critical threshold handling."
    covers_acceptance_criteria:
      - "Deliverables D1 and D2 acceptance criteria defined and referenced in tactical plan."
  - path: "technomancy/deliverables/tests/m1_needs_tests_outline.md"
    purpose: "Document planned automated test scenarios for needs adjustments."
    covers_acceptance_criteria:
      - "Deliverables D1 and D2 acceptance criteria defined and referenced in tactical plan."
  - path: "technomancy/deliverables/src/m1_room_effects.py"
    purpose: "Provide the finalized Room.apply_effects implementation according to specification A5."
    covers_acceptance_criteria:
      - "Define Milestone M1 \"Core Simulation Stability\" to deliver D1 and D2, to complete Room.apply_effects, finalize student decision logic, and prove needs thresholds via automated tests."
  - path: "technomancy/deliverables/src/m1_student_needs_overrides.py"
    purpose: "Supply the complete student decision override logic for critical needs."
    covers_acceptance_criteria:
      - "Define Milestone M1 \"Core Simulation Stability\" to deliver D1 and D2, to complete Room.apply_effects, finalize student decision logic, and prove needs thresholds via automated tests."
  - path: "technomancy/deliverables/tests/test_m1_room_effects.py"
    purpose: "Implement automated tests validating room effect deltas against specification thresholds."
    covers_acceptance_criteria:
      - "Define Milestone M1 \"Core Simulation Stability\" to deliver D1 and D2, to complete Room.apply_effects, finalize student decision logic, and prove needs thresholds via automated tests."
  - path: "technomancy/deliverables/tests/test_m1_student_needs.py"
    purpose: "Implement automated tests validating decision logic for hunger, energy, stress, and hygiene overrides."
    covers_acceptance_criteria:
      - "Define Milestone M1 \"Core Simulation Stability\" to deliver D1 and D2, to complete Room.apply_effects, finalize student decision logic, and prove needs thresholds via automated tests."
validation:
  all_acceptance_criteria_covered: true
  uncovered_acceptance_criteria: []
---
```
