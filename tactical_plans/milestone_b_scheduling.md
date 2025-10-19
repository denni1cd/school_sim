# Tactical Plan — Milestone B: Comprehensive Scheduling

## Objective
Build a configurable scheduling system that assigns each student a full day-night routine with travel-time awareness, conflict resolution, and persistence hooks.

## Preconditions
- Milestone A campus map (`campus_v1`) and room metadata committed.
- Existing scheduling modules (`game/simulation/schedule_generator.py`, `config/schedules/*.yaml`) load without errors.
- Regression tests from prior milestones pass.

## Implementation Steps
1. **Archetype Definition (Content Designer, Product Lead)**
   - Draft personas: `boarding_student`, `day_student`, `athlete`, `prefect`.
   - For each, list mandatory activities per block (wake, breakfast, morning classes, lunch, afternoon classes, clubs/sports, dinner, study hall, lights-out).
   - Record variations (e.g., athletes have practice Mon/Wed/Fri equivalent) in `docs/schedule_archetypes.md`.

2. **Template Configuration (Content Designer)**
   - Create `config/schedules/student_templates.yaml` with structures:
     ```yaml
     boarding_student:
       weekday:
         - {slot: wake_up, start: 06:30, duration: 00:30, activity: WakeUp, room: dorm_north_a}
         - {slot: breakfast, start: 07:00, duration: 00:30, activity: Eating, room: cafeteria_main}
       weekend:
         - {slot: wake_up, start: 08:00, duration: 00:30, activity: WakeUp, room: dorm_north_a}
     ```
   - Use ISO 8601 durations to simplify parsing; include `travel_buffer` optional field for long distances.

3. **Schedule Engine Refactor (Engineering Lead, Gameplay Engineer)**
   - Introduce classes in `game/simulation/schedule_generator.py`:
     - `DailySchedule` dataclass capturing `start_tick`, `end_tick`, `activity_id`, `room_id`, `notes`.
     - `ScheduleTemplate` to encapsulate template data and instantiate `DailySchedule` blocks.
     - `ScheduleAssignment` to bind templates to NPC profiles.
     - `TravelEstimator` utility to compute path length between rooms using `MapGraph`.
   - Add `DailySchedule.from_config(slot_cfg: dict, *, timezone: str) -> "DailySchedule"` helper that uses `time_utils.hours_to_ticks` for conversions and injects default travel buffers when unspecified.
   - Ensure generator respects object-oriented principles by delegating block creation to dedicated methods instead of procedural loops.
   - Document new class responsibilities and helper API in `docs/scheduling_schema.md` with before/after YAML samples.

4. **Conflict Detection & Resolution (Gameplay Engineer)**
   - Implement `game/simulation/conflict_resolver.py`:
     - `detect_room_capacity_conflicts(schedule: Sequence[DailySchedule], room_metadata)` returning overbooked intervals.
     - `resolve_with_staggering(conflicts, increment=timedelta(minutes=5))` shifting start times and recalculating travel, returning both the adjusted `DailySchedule` list and structured `ConflictRecord`s for reporting.
   - Emit events through `game/logging/events.py` with payloads `{ "event": "schedule_conflict_resolved", "actor": actor_id, ... }` for analytics.
   - Integrate resolver into schedule generation pipeline with logging for adjustments.

5. **Travel-Time Awareness (Systems Engineer)**
   - Augment `ScheduleBlock` with `expected_travel` and `travel_path` attributes.
   - Before finalizing schedule, calculate A* route between previous block room and next block room; if travel exceeds buffer, extend previous block’s end or start earlier as per resolver policy.
   - Persist chosen path to `npc_state.travel_plan` for debugging.

6. **Persistence Hooks (Engineering Lead)**
   - Add serialization in `game/state/save_game.py` to persist `ScheduleAssignment` objects.
   - Implement `load_schedule_assignment` to reconstruct templates on load.

7. **Configuration Validation (QA Lead)**
   - Write `tests/scheduling/test_template_parsing.py` verifying YAML parsing handles required/optional fields and raises descriptive errors on missing data.
   - Add `tests/scheduling/test_conflict_resolution.py` with scenarios for capacity conflict and travel overrun adjustments.

8. **Simulation Verification (QA Lead)**
   - Run `python -m game.simulation --map campus_v1 --ticks 2880 --schedule-profile boarding_student` ensuring 24-hour loop completes without idle gaps.
   - Enable CSV export via `--dump-daily-plan reports/daily_schedule.csv` (add CLI flag if missing) and confirm columns for `actor_id`, `slot`, `start_time`, `end_time`, `room`, `activity`.
   - Use logging to confirm conflict resolver adjustments appear when cafeteria overloaded and append anomalies to `reports/scheduling_anomalies.md` with cross-referenced CSV rows.

## Deliverables
- Rich schedule template configuration covering all personas.
- Refactored scheduling engine classes with conflict resolution utilities.
- Persistence hooks for saving/loading schedules.
- Automated tests validating templates, conflicts, and travel-time handling.

## Acceptance Criteria
- Every NPC archetype receives a schedule covering 24 hours with no unscheduled gaps.
- Conflict resolver automatically staggers schedules to keep room usage within capacity limits.
- Travel buffers adjust automatically when rooms are far apart.
- Serialization/deserialization retains full schedule fidelity across save/load.
- All new tests and simulation verification succeed.
