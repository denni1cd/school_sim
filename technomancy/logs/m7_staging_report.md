# Milestone M7 Staging Report

## Summary
- Added the “Curriculum Deep Dive” instructions to `README.md`, covering config keys, track effects, and golden tests to rerun (`test_curriculum_modifiers.py`, `test_office_curriculum.py`).
- Staged the updated README under `technomancy/deliverables/docs/readme.md` so the merge script delivers the documentation while keeping the staged tree clean.

## Tests
- `PYTHONPATH=. conda run -n simulation_test pytest -q school_sim/tests`
- `PYTHONPATH=. conda run -n simulation_test make simulate`
- `SCHOOL_SIM_MAX_LOOPS=12 PYTHONPATH=. conda run -n simulation_test make run`
