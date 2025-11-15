# Milestone M5 Staging Report

## Summary
- Added policy change journaling so every uniform/discipline swap records timestamped captions, deltas, and balances; the journal is exposed through `World.get_debug_snapshot` and the Office Reports view.
- Office Reports now include the three most recent policy changes alongside rating, budget, attendance, and economy history, giving the Headmistress visibility into recent decisions.
- Introduced `test_policy_history.py` and expanded `test_office_reports.py` to cover the new history tracking while keeping all earlier policy tests intact.

## Tests
- `PYTHONPATH=. conda run -n simulation_test pytest -q school_sim/tests`
- `PYTHONPATH=. conda run -n simulation_test make simulate`
- `SCHOOL_SIM_MAX_LOOPS=12 PYTHONPATH=. conda run -n simulation_test make run`
