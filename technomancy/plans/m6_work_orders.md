# Milestone M6 Work Orders

## WO-1 Clubs Module
- Author `technomancy/deliverables/src/school_sim/clubs.py` implementing config parsing, assignment API, meeting effects, and overflow handling with event/log hooks.

## WO-2 World/Student Wiring
- Update `world.py` to load clubs, assign students, call club tick handler, integrate penalties into rating/budget.
- Extend `student.py` to store club membership and movement to club rooms at meeting times.

## WO-3 Persistence & Config
- Ensure `save_system.py` includes club membership round-trip; update `bootstrap.py` if additional defaults required.

## WO-4 UI & Feedback
- Enhance Office reports tab to reflect active clubs/memberships; console log or overlay for overflow penalties.

## WO-5 Tests
- Add `technomancy/deliverables/tests/test_club_assignment_budget.py` and `test_clubs_capacity.py` covering assignment costs and overflow penalty behaviour.
- Adjust existing tests (`test_save_load.py`, `test_office_navigation.py`) if necessary.

## WO-6 Ritual
- Implement merge script `merge_m6.py`, run staged tests, create staging report, perform merge + post-merge verification, draft final report.
