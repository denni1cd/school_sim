# Milestone M8 Staging Report

## Summary
- Added the “Budget & Reports Deep Dive” section to `README.md`, covering the economy module, rating breakdowns, headless status logs, and tests to rerun after touching the budget/reporting stack.
- Staged the updated README under `technomancy/deliverables/docs/readme.md` so the merge script can refresh the project root documentation while keeping the staging tree clean.

## Tests
- `PYTHONPATH=. conda run -n simulation_test pytest -q school_sim/tests`
- `PYTHONPATH=. conda run -n simulation_test make simulate`
- `SCHOOL_SIM_MAX_LOOPS=12 PYTHONPATH=. conda run -n simulation_test make run`
