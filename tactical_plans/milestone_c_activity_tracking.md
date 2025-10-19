# Tactical Plan — Milestone C: Activity Tracking & Reporting

## Objective
Connect schedules to a comprehensive activity system that records, reports, and exposes what each NPC is doing in every room, supporting UI and analytics hooks.

## Preconditions
- Milestone B scheduling system functional with travel-time adjustments.
- Interaction text pipeline (`config/interactions.yaml`, `game/interface/interaction_text.py`) operational.
- Logging infrastructure (`game/logging/event_logger.py`) ready to accept new events.

## Implementation Steps
1. **Activity Catalog Design (Content Designer, Product Lead)**
   - Draft canonical activity list: `Sleeping`, `Eating`, `Studying`, `Teaching`, `Recreation`, `Maintenance`, `Medical`, `Discipline`, `Idle`.
   - For each, define:
     - Supported room types.
     - Default duration range.
     - State variables (e.g., `intensity`, `noise_level`).
   - Document in `docs/activity_catalog.md` including placeholder text keys.

2. **Configuration Authoring (Content Designer)**
   - Create `config/activities.yaml` containing entries:
     ```yaml
     Sleeping:
       room_types: [Dormitory, Infirmary]
       default_duration: 08:00
       interaction_key: activity.sleeping
       state:
         posture: lying
         lights: off
     ```
   - Ensure `interaction_key` matches placeholders in `config/interactions.yaml`.

3. **Activity Class Hierarchy (Engineering Lead, Gameplay Engineer)**
   - Add module `game/simulation/activities/base.py` defining `ActivityState` dataclass and `Activity` abstract base with hooks `on_start`, `tick`, `on_complete`.
   - Implement concrete classes in `game/simulation/activities/` (e.g., `sleep.py`, `study.py`, `eat.py`).
   - Provide factory `ActivityFactory.create(activity_name, npc, room, metadata)` returning appropriate activity object.

4. **Schedule Binding (Gameplay Engineer)**
   - Update scheduling pipeline so each `ScheduleBlock` instantiates an `Activity` via factory on block start.
   - Maintain NPC state `npc.current_activity` for UI queries.
   - Handle transitions: call `on_complete` when block ends or NPC leaves room.

5. **Room Occupancy Tracking (Systems Engineer)**
   - Extend `game/world/room_manager.py`:
     - Maintain `room_state[room_id] = {activity_counts, occupants}`.
     - Provide `subscribe(room_id, callback)` for UI/alerts.
   - Trigger updates on occupant arrival/departure and on `Activity.tick` state changes (e.g., intensity).

6. **Interaction & Notification Updates (Gameplay Engineer)**
   - Modify `game/interface/interaction_text.py` to accept `activity_context` and display e.g. "[Student] is Studying in Humanities Classroom".
   - Update placeholder UI overlays to show room activity summary (text list) when player hovers/presses `Tab`.

7. **Event Logging (Systems Engineer)**
   - Enhance `game/logging/event_logger.py` with `log_activity_start`, `log_activity_end`, `log_activity_interrupt`.
   - Ensure logs include timestamps, NPC id, activity name, room id, and optional state metadata.

8. **Testing (QA Lead)**
   - Add `tests/activities/test_activity_factory.py` verifying correct class instantiation and default state.
   - Add `tests/activities/test_room_reporting.py` confirming occupancy and activity summaries update on NPC movement.
   - Expand interaction regression tests to assert new contextual text appears for Sleep/Eat/Study scenarios.

9. **Telemetry Validation (QA Lead)**
   - Run simulation for 48 in-game hours: `python -m game.simulation --map campus_v1 --ticks 5760 --log-activities`.
   - Confirm activity logs align with schedule expectations (no missing start/end events).

## Deliverables
- Activity configuration and class hierarchy with factory.
- Room manager capable of broadcasting activity-aware occupancy.
- Updated UI/interaction placeholders reflecting current activities.
- Tests covering activity instantiation, reporting, and logging.

## Acceptance Criteria
- Every schedule block triggers a corresponding `Activity` instance with start/end events.
- Room summaries report accurate occupant counts and primary activity types.
- Interaction text surfaces activity context without regressions.
- Activity logs provide a complete timeline for audit and analytics use cases.
- Test suite and telemetry validation pass.
