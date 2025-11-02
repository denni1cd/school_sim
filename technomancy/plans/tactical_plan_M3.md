# Tactical Plan M3

## Objectives
- Deliver Milestone M3 "Persistence and Verification" by satisfying Deliverables D5, D6, and D7.
- Implement save/load functionality with JSON snapshots stored under `runtime/saves/` and ensure loading via CLI flag and debug key.
- Produce deterministic headless simulation logs for `make simulate` and finalize comprehensive automated test coverage across loaders, persistence, and smoke paths.

## Tasks
- Task ID: T5  
  Description: Specify save/load schema, headless logging strategy, and comprehensive test coverage expectations.  
  Assigned Role: High Technomancer  
  Required File Paths: `technomancy/deliverables/src/m3_persistence_design.md`, `technomancy/deliverables/tests/m3_test_plan.md`  
  Acceptance Checks: D5 Save and Load acceptance criteria; D6 Headless Logs acceptance criteria; D7 Tests acceptance criteria cited.

- Task ID: T6  
  Description: Implement persistence, logging, and full automated test suite ensuring runbook commands succeed.  
  Assigned Role: Technomancer  
  Required File Paths: `technomancy/deliverables/src/m3_save_system.py`, `technomancy/deliverables/src/m3_headless_logging.py`, `technomancy/deliverables/tests/test_m3_save_load.py`, `technomancy/deliverables/tests/test_m3_headless.py`  
  Acceptance Checks: D5 Save and Load acceptance criteria; D6 Headless Logs acceptance criteria; D7 Tests acceptance criteria.

## Risks and Blockers
- Writing JSON saves during gameplay must avoid blocking the main loop; ensure persistence runs asynchronously or fast enough for MVP.
- Loading the latest save via debug key may conflict with running simulations if state is not properly reset; design idempotent load routines.
- Headless logs require deterministic outputs; any randomization in world updates must be controlled or seeded.
- Extensive test suite may need mocking for file I/O and Pygame dependencies; ensure tests isolate filesystem operations using temporary directories.

## Standards
- Follow Python 3.12 coding standards and reuse existing module patterns.
- Ensure all persistence APIs provide docstrings documenting parameters and return values.
- Validate JSON structure before writing and after reading; include defensive error handling.
- Tests must cover success and failure paths, be deterministic, and runnable via `pytest` and `make test`.

## Deliverables
- `technomancy/deliverables/src/m3_persistence_design.md` — Document the persistence architecture, save schema, load workflow, and logging strategy.
- `technomancy/deliverables/tests/m3_test_plan.md` — Enumerate the automated test coverage required for persistence and logging.
- `technomancy/deliverables/src/m3_save_system.py` — Provide reference implementation details for save/load mechanics.
- `technomancy/deliverables/src/m3_headless_logging.py` — Describe the headless logging approach and hooks within simulation.
- `technomancy/deliverables/tests/test_m3_save_load.py` — Mirror the automated tests verifying save/load roundtrip behavior.
- `technomancy/deliverables/tests/test_m3_headless.py` — Mirror the automated tests validating headless logging output and determinism.

```yaml
---
artifact: Tactical-Plan-Deliverables
milestone_id: "M3"
deliverables:
  - path: "technomancy/deliverables/src/m3_persistence_design.md"
    purpose: "Document the persistence architecture, save schema, load workflow, and logging strategy."
    covers_acceptance_criteria:
      - "D5 Save and Load acceptance criteria; D6 Headless Logs acceptance criteria; D7 Tests acceptance criteria cited."
  - path: "technomancy/deliverables/tests/m3_test_plan.md"
    purpose: "Enumerate the automated test coverage required for persistence and logging."
    covers_acceptance_criteria:
      - "D5 Save and Load acceptance criteria; D6 Headless Logs acceptance criteria; D7 Tests acceptance criteria cited."
  - path: "technomancy/deliverables/src/m3_save_system.py"
    purpose: "Provide reference implementation details for save/load mechanics."
    covers_acceptance_criteria:
      - "Define Milestone M3 \"Persistence and Verification\" to deliver D5, D6, and D7, to complete save/load flows, headless deterministic logs, and full automated test coverage, ensuring `make run`, `make simulate`, and `make test` succeed."
  - path: "technomancy/deliverables/src/m3_headless_logging.py"
    purpose: "Describe the headless logging approach and hooks within simulation."
    covers_acceptance_criteria:
      - "Define Milestone M3 \"Persistence and Verification\" to deliver D5, D6, and D7, to complete save/load flows, headless deterministic logs, and full automated test coverage, ensuring `make run`, `make simulate`, and `make test` succeed."
  - path: "technomancy/deliverables/tests/test_m3_save_load.py"
    purpose: "Mirror the automated tests verifying save/load roundtrip behavior."
    covers_acceptance_criteria:
      - "Define Milestone M3 \"Persistence and Verification\" to deliver D5, D6, and D7, to complete save/load flows, headless deterministic logs, and full automated test coverage, ensuring `make run`, `make simulate`, and `make test` succeed."
  - path: "technomancy/deliverables/tests/test_m3_headless.py"
    purpose: "Mirror the automated tests validating headless logging output and determinism."
    covers_acceptance_criteria:
      - "Define Milestone M3 \"Persistence and Verification\" to deliver D5, D6, and D7, to complete save/load flows, headless deterministic logs, and full automated test coverage, ensuring `make run`, `make simulate`, and `make test` succeed."
validation:
  all_acceptance_criteria_covered: true
  uncovered_acceptance_criteria: []
---
```
