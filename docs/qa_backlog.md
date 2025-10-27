# QA Backlog — Milestone E

| ID     | Description                                                    | Severity | Owner             | Status     | Notes |
|--------|----------------------------------------------------------------|----------|-------------------|------------|-------|
| QA-001 | NPCs occasionally remain flagged inside rooms after overrides. | High     | Systems Engineer  | Resolved   | Added interrupt coverage in `tests/activities/test_activity_interrupts.py` to confirm room state cleanup. |
| QA-002 | Curfew alerts fail to trigger for late-night schedule changes. | High     | Gameplay Engineer | Resolved   | Regression test `test_override_during_curfew_triggers_alert` ensures overrides respect curfew alerts. |
| QA-003 | Alerts repeat too quickly after acknowledgement.               | Medium   | QA Lead           | Resolved   | Added cooldown persistence test to guard against duplicate alert spam. |
| QA-004 | Replanning paths every tick causes frame spikes.               | Medium   | Systems Engineer  | Resolved   | Introduced cached path reuse in `MovementSystem` with targeted unit coverage. |

All blocker-level items have been resolved for this milestone. Non-blocking enhancements have been logged for the next iteration in `suggestions.md`.
