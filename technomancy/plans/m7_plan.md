# Milestone M7 Plan

## Objective
Introduce curriculum tracks that influence classroom needs, expose controls through the Office, and surface state through saves and logs per Spec 2.6C and 6.3.

## Scope & Decisions
1. Implement dedicated `curriculum.py` module with validated track set/apply helpers; integrate with world tick for classroom modifiers.
2. Extend `World` to accept curriculum config, expose `change_curriculum_track`, emit overlay + event, and include track in debug snapshots/logs.
3. Update Office curriculum tab to cycle/select tracks and trigger world changes with messaging.
4. Align persistence, headless logging, and tests with curriculum state (ensure save/load keeps track, logs show track once per minute).

## Acceptance Evidence
- New golden test `test_curriculum_modifiers.py` validating STEM vs General classroom stress deltas.
- Office curriculum interaction test verifying track switching + overlay/event linking.
- Updated headless/log tests asserting curriculum data presence.
- Full `pytest -q` plus `make simulate` (conda env `simulation test`).
