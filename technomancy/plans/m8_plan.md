# Milestone M8 Plan

## Objective
Ensure the budget/economy reporting documentation, headless logs, and README references are crystal clear so new contributors understand how the economy module, rating breakdown, and reward/spend flows work after the previous code implementation.

## Scope & Decisions
1. Expand the “Budget & Reports Deep Dive” section in `README.md` explaining the existing `economy.py`, transaction history, `rating_breakdown`, and headless log output, plus the golden tests that already cover these components.
2. Stage the README update via `technomancy/deliverables/docs/readme.md` so the merge script mirrors our doc changes while keeping the staging tree hygienic.
3. Confirm the documentation references the tests (`test_economy_budget.py`, `test_rating_breakdown.py`, `test_office_reports.py`) and headless logs (`school_sim/runtime/logs/sim_log.txt`) that demonstrate compliance.

## Acceptance Evidence
- Fresh README section elaborates budget module, rating breakdown, headless logs, and test commands (per M8 acceptance).
- The golden tests `test_economy_budget.py`, `test_rating_breakdown.py`, and `test_office_reports.py` remain passing after documentation updates.
- Verification suite (`pytest`, `make simulate`, `make run` with `simulation_test`) covers the end-to-end runbook with the documented metrics.
