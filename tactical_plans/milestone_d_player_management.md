# Tactical Plan — Milestone D: Player Management Hooks

## Objective
Provide the principal persona with tools to monitor, adjust, and intervene in school operations through engine APIs, notifications, and placeholder UI interactions.

## Preconditions
- Activity reporting from Milestone C delivers real-time room and NPC activity data.
- Command dispatch infrastructure (`game/interface/commands.py`) exists for console inputs.
- Logging/event system can emit notifications to interested listeners.

## Implementation Steps
1. **Use Case Prioritization (Product Lead, Producer)**
   - Finalize principal interventions: schedule override, call student to office, issue dorm inspection, acknowledge alerts.
   - Document scenarios and success criteria in `docs/principal_use_cases.md`.

2. **Command Interface Design (Engineering Lead)**
   - Draft API surface in `game/interface/principal_controls.py`:
     - `override_schedule(npc_id, new_blocks)`
     - `summon_student(npc_id, target_room_id)`
     - `mark_alert_resolved(alert_id)`
     - `broadcast_message(message, audience_filter)`
   - Define validation rules (e.g., cannot summon if student already moving to target, only override future blocks).

3. **Command Dispatcher Implementation (Gameplay Engineer)**
   - Hook CLI: extend `game/interface/commands.py` to parse `schedule override`, `summon`, `alerts resolve`, `broadcast` commands.
   - Add Pygame placeholder overlay buttons invoking same APIs (text-based UI, e.g., `ui/principal_overlay.py`).
   - Ensure dispatcher sends structured payloads to `principal_controls` methods and handles success/error responses.

4. **Alert System Build-Out (Systems Engineer)**
   - Introduce `game/notifications/alerts.py` with:
     - `Alert` dataclass (id, category, severity, message, room_id, npc_ids, created_at, acknowledged_at).
     - `AlertBus` class supporting `publish`, `subscribe`, `acknowledge`.
   - Wire activity system to publish alerts (e.g., `MissedClass`, `Overcapacity`, `CurfewViolation`).
   - Provide rate-limiting to avoid spam (e.g., cooldown per alert type per room).

5. **Schedule Override Mechanics (Gameplay Engineer)**
   - Implement ability to insert ad-hoc `ScheduleBlock`s when override invoked.
   - Persist overrides via Milestone B serialization hooks; mark blocks with `source=override`.
   - Ensure conflict resolver reruns for impacted NPC to prevent collisions.

6. **Summon & Escort Logic (Gameplay Engineer)**
   - Add function `npc_movement.route_override(target_room_id)` forcing immediate travel after current block ends; support optional escort by staff NPCs (future extension placeholder).
   - Update path planner to respect `priority_route` flag so summoned students ignore low-priority activities until arrival logged.

7. **UI & Feedback (Content Designer, Gameplay Engineer)**
   - Extend CLI output: display active alerts, upcoming overrides, and command confirmations.
   - Pygame placeholder overlay should highlight rooms with alerts (flashing border) and list actionable items.

8. **Documentation & Tutorials (Producer)**
   - Create `docs/principal_controls.md` with command syntax, examples, and troubleshooting tips.
   - Record scripted simulation log demonstrating overriding a schedule and resolving alerts.

9. **Testing (QA Lead)**
   - Unit tests:
     - `tests/commands/test_principal_controls.py` verifying validation and state changes.
     - `tests/notifications/test_alert_bus.py` ensuring publish/acknowledge flow.
   - Integration script `tests/integration/test_principal_flow.py` exercising override → summon → resolve sequence across simulated day.
   - Run `pytest tests/commands/test_principal_controls.py tests/notifications/test_alert_bus.py tests/integration/test_principal_flow.py` and confirm success.

## Deliverables
- Principal control API with command-line and placeholder UI entry points.
- Alert system integrated with activity reporting and scheduling overrides.
- Documentation and demo logs for principal workflows.
- Automated tests verifying command handling and alert lifecycle.

## Acceptance Criteria
- Principal can override schedules, summon students, and resolve alerts via CLI or placeholder UI.
- Alerts are generated for key incidents with severity and context, and can be acknowledged.
- Overrides persist across save/load and do not break travel/pathfinding.
- All new unit and integration tests pass.
