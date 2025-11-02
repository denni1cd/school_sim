# Project Plan

## Traceability
- Catalog Functional Requirement FR1 (Room Effects) to Milestone M1 and enforce Deliverable D1 acceptance criteria.
- Catalog Functional Requirement FR2 (Needs Overrides) to Milestone M1 and enforce Deliverable D2 acceptance criteria.
- Catalog Functional Requirement FR3 (Event System) to Milestone M2 and enforce Deliverable D3 acceptance criteria.
- Catalog Functional Requirement FR4 (Scene Overlay) to Milestone M2 and enforce Scene Overlay acceptance criteria inside Deliverable D3.
- Catalog Functional Requirement FR5 (Principal Console) to Milestone M2 and enforce Deliverable D4 acceptance criteria.
- Catalog Functional Requirement FR6 (Save and Load) to Milestone M3 and enforce Deliverable D5 acceptance criteria.
- Catalog Functional Requirement FR7 (Headless Logs) to Milestone M3 and enforce Deliverable D6 acceptance criteria.
- Catalog Functional Requirement FR8 (Automated Tests) to Milestone M3 and enforce Deliverable D7 acceptance criteria.
- Catalog Non-Functional Requirement NFR1 (Python 3.12 stack) to all milestones and enforce interpreter and dependency constraints.
- Catalog Non-Functional Requirement NFR2 (Config-driven content in YAML) to Milestones M1 and M2 and enforce loader coverage.
- Catalog Non-Functional Requirement NFR3 (Pygame placeholder visuals) to Milestones M1 and M2 and enforce renderer contract.
- Catalog Non-Functional Requirement NFR4 (Deterministic simulation loop with make run, make simulate, make test targets) to Milestone M3 and enforce runbook compliance.

## Architecture
- Retain module boundaries defined in `/docs/specification.md` and instruct all roles to respect existing files (`main.py`, `renderer.py`, `student.py`, `world.py`, `room.py`, `timetable.py`).
- Establish the `events` package with submodules `event_models.py`, `event_loader.py`, `event_bus.py`, `event_rules.py`, and `scene_overlay.py` to manage event data, dispatch, rules evaluation, and rendering overlays.
- Store configuration YAML files under `configs/` and enforce the new `configs/events.yaml` schema for sceneable events referencing assets under `runtime/scenes/`.
- Persist simulation state under `runtime/saves/` using JSON save files shaped exactly as defined in the specification and load them through CLI flag `--load` or debug key `L`.
- Maintain runtime logs and optional headless outputs within `runtime/logs/` produced by `make simulate` for 300 ticks with snapshots that include time and student states.
- Orchestrate data flow so that `main.py` loads configs, constructs `World`, registers event subscriptions, enters the game loop, and lets `renderer.py` draw rooms, students, overlays, and the Principal Console.
- Command `World` to publish bus events (`time_tick`, `room_enter`, `room_exit`, `needs_update`, `event_fired`) that in turn drive rule evaluation and overlay updates per the event system contract.
- Direct tests under `tests/` to exercise needs math, schedule targeting, event rules, save-load, and loader correctness to guarantee coverage across milestones.

## Milestone Summary
- Define Milestone M1 "Core Simulation Stability" to deliver D1 and D2, to complete `Room.apply_effects`, finalize student decision logic, and prove needs thresholds via automated tests.
- Define Milestone M2 "Event Interaction Framework" to deliver D3 and D4, to implement the event system, scene overlay, Principal Console toggles, and interactive debug actions with acceptance checks satisfied.
- Define Milestone M3 "Persistence and Verification" to deliver D5, D6, and D7, to complete save/load flows, headless deterministic logs, and full automated test coverage, ensuring `make run`, `make simulate`, and `make test` succeed.

## Rationale
- Prioritize Milestone M1 to stabilize core mechanics required by Deliverables D1 and D2, because subsequent features depend on accurate needs updates and decision logic.
- Sequence the event system and console work in Milestone M2 to align with Deliverable D3 and D4 requirements and to exploit stabilized simulation data from M1.
- Reserve persistence, logging, and test hardening for Milestone M3 to leverage earlier functionality, fulfill Deliverables D5 through D7, and certify the runbook obligations.
- Centralize event assets and saves under `runtime/` to satisfy the specification's directory constraints and to avoid contaminating existing project structure.
