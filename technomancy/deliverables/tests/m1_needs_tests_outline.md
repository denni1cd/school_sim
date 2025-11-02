# M1 Needs Test Outline

## Purpose
Document the automated tests that validate room effects and student override logic before implementation.

## Planned Test Modules
- `tests/test_m1_room_effects.py`
  - Validate that positive and negative deltas accumulate over multiple minutes.
  - Ensure needs clamp between 0 and 100.
  - Confirm missing keys default to zero delta.
- `tests/test_m1_student_needs.py`
  - Verify hunger, energy, stress, and hygiene overrides trigger when thresholds are crossed.
  - Ensure schedule adherence resumes when needs return below thresholds.
  - Check that hygiene paths consider available rooms defined in YAML.

## Fixtures
- Create synthetic `Room` objects with controlled effects per need.
- Create `Student` instances with base needs and stub timetable entries.
- Mock or isolate world time progression to avoid dependence on the main loop.

## Edge Cases
- Apply effects that would push needs below 0 or above 100.
- Students already in their target room should not re-route unnecessarily.
- Simultaneous high stress and hunger must prefer the more severe deficit per specification thresholds.
