# Tactical Plan M2

## Objectives
- Deliver Milestone M2 "Event Interaction Framework" by implementing Deliverables D3 and D4 as defined in the project plan.
- Establish a robust events pipeline including data models, loader, bus, rule evaluation, and scene overlay rendering that aligns with the existing architecture.
- Extend the Principal Console to meet interactive debugging requirements with key bindings `P`, `T`, `E`, and `B` while preserving stability of the simulation loop.

## Tasks
- Task ID: T3  
  Description: Design event bus contracts, scene overlay integration, and Principal Console control flow in tactical plan.  
  Assigned Role: High Technomancer  
  Required File Paths: `technomancy/deliverables/src/m2_event_system_design.md`, `technomancy/deliverables/tests/m2_events_test_matrix.md`  
  Acceptance Checks: D3 Event System acceptance criteria; D4 Principal Console acceptance criteria documented.

- Task ID: T4  
  Description: Build events package, scene overlay, console interactions, and associated automated tests.  
  Assigned Role: Technomancer  
  Required File Paths: `technomancy/deliverables/src/m2_event_system.py`, `technomancy/deliverables/src/m2_scene_overlay.py`, `technomancy/deliverables/src/m2_principal_console.py`, `technomancy/deliverables/tests/test_m2_events.py`, `technomancy/deliverables/tests/test_m2_console.py`  
  Acceptance Checks: D3 Event System acceptance criteria; D4 Principal Console acceptance criteria.

## Risks and Blockers
- Pygame overlay rendering changes risk regressions in existing renderer layout; plan incremental integration to avoid disrupting base UI.
- Event rule engine must parse the mini-language without external dependencies; unclear expressions could require manual parser implementation.
- Asset loading for scenes depends on filesystem availability; ensure graceful failure when images are missing while still meeting acceptance criteria.

## Standards
- Maintain separation of concerns: keep loader, bus, rules, and overlay modules independent with clear contracts defined in docstrings.
- Require docstrings for all public classes and functions in new modules, emphasizing parameter types and return values.
- Enforce automated tests for loaders, rules evaluation, event dispatch, and console triggers with deterministic assertions.
- Follow existing code style and ensure dependency-free YAML parsing via `yaml.safe_load`.

## Deliverables
- `technomancy/deliverables/src/m2_event_system_design.md` — Document the architecture for event models, bus orchestration, rule evaluation, and renderer integration.
- `technomancy/deliverables/tests/m2_events_test_matrix.md` — Outline automated test coverage for event loading, rule evaluation, and dispatch flows.
- `technomancy/deliverables/src/m2_event_system.py` — Provide the consolidated reference implementation for event models, loader, bus, and rules logic.
- `technomancy/deliverables/src/m2_scene_overlay.py` — Capture the reference implementation details for the scene overlay component.
- `technomancy/deliverables/src/m2_principal_console.py` — Describe the Principal Console interaction patterns and debug action handling.
- `technomancy/deliverables/tests/test_m2_events.py` — Mirror the automated tests validating event system behavior.
- `technomancy/deliverables/tests/test_m2_console.py` — Mirror the automated tests validating Principal Console interactions and shortcuts.

```yaml
---
artifact: Tactical-Plan-Deliverables
milestone_id: "M2"
deliverables:
  - path: "technomancy/deliverables/src/m2_event_system_design.md"
    purpose: "Document the architecture for event models, bus orchestration, rule evaluation, and renderer integration."
    covers_acceptance_criteria:
      - "D3 Event System acceptance criteria; D4 Principal Console acceptance criteria documented."
  - path: "technomancy/deliverables/tests/m2_events_test_matrix.md"
    purpose: "Outline automated test coverage for event loading, rule evaluation, and dispatch flows."
    covers_acceptance_criteria:
      - "D3 Event System acceptance criteria; D4 Principal Console acceptance criteria documented."
  - path: "technomancy/deliverables/src/m2_event_system.py"
    purpose: "Provide the consolidated reference implementation for event models, loader, bus, and rules logic."
    covers_acceptance_criteria:
      - "Define Milestone M2 \"Event Interaction Framework\" to deliver D3 and D4, to implement the event system, scene overlay, Principal Console toggles, and interactive debug actions with acceptance checks satisfied."
  - path: "technomancy/deliverables/src/m2_scene_overlay.py"
    purpose: "Capture the reference implementation details for the scene overlay component."
    covers_acceptance_criteria:
      - "Define Milestone M2 \"Event Interaction Framework\" to deliver D3 and D4, to implement the event system, scene overlay, Principal Console toggles, and interactive debug actions with acceptance checks satisfied."
  - path: "technomancy/deliverables/src/m2_principal_console.py"
    purpose: "Describe the Principal Console interaction patterns and debug action handling."
    covers_acceptance_criteria:
      - "Define Milestone M2 \"Event Interaction Framework\" to deliver D3 and D4, to implement the event system, scene overlay, Principal Console toggles, and interactive debug actions with acceptance checks satisfied."
  - path: "technomancy/deliverables/tests/test_m2_events.py"
    purpose: "Mirror the automated tests validating event system behavior."
    covers_acceptance_criteria:
      - "Define Milestone M2 \"Event Interaction Framework\" to deliver D3 and D4, to implement the event system, scene overlay, Principal Console toggles, and interactive debug actions with acceptance checks satisfied."
  - path: "technomancy/deliverables/tests/test_m2_console.py"
    purpose: "Mirror the automated tests validating Principal Console interactions and shortcuts."
    covers_acceptance_criteria:
      - "Define Milestone M2 \"Event Interaction Framework\" to deliver D3 and D4, to implement the event system, scene overlay, Principal Console toggles, and interactive debug actions with acceptance checks satisfied."
validation:
  all_acceptance_criteria_covered: true
  uncovered_acceptance_criteria: []
---
```
