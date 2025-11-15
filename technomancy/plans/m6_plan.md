# Milestone M6 Plan

## Goal
Deliver the clubs system: configuration-driven club definitions, student assignment with capacity checks, meeting-time effects, and integration with budget/rating per spec v1.4.

## Current Assessment
- No `clubs.py` module; clubs configuration is unused beyond scaffolding.
- World tick has no awareness of clubs or meeting schedules.
- Students lack club assignment fields; save/load already reserves a `club` slot but world doesn?t populate it.
- Office UI reports tab lists static info only.
- No tests covering clubs, capacity penalties, or assignment costs.

## Work Streams
1. **Club Engine**
   - Implement module to load definitions, assign students, enforce capacity, and compute meeting effects.
2. **World Integration**
   - Store club registry on world, manage assignments, hook into tick loop to trigger meetings and apply effects.
3. **Student Persistence & Data**
   - Ensure students track `club_id`; update save/load and snapshots accordingly.
4. **Office & Console Surface**
   - Update reports tab to show active memberships and capacity; optionally console logging for overflow penalties.
5. **Testing & Hygiene**
   - Add golden tests for budget deduction and capacity penalty; update save/load regression tests.
6. **Technomancy Rituals**
   - Stage in deliverables, run tests, produce merge script/report, verify post-merge.

## Acceptance Evidence
- New club golden tests pass under `pytest -q school_sim/tests`.
- `make simulate` & bounded `make run` demonstrate club assignments without crashes.
- Headless log shows stress adjustments/penalties when overflow occurs (per spec), and budget reflects assignments.
