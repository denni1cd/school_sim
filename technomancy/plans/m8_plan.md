# Milestone M8 Plan

## Objective
Implement the budget/economy systems and reporting polish so the Office Reports tab surfaces actionable KPIs, budget adjustments follow a unified economy module, and rating breakdown adheres to spec weights.

## Scope & Decisions
1. Author `economy.py` and adjust world budget mutations to go through it; capture transaction history for reports/logging.
2. Refactor rating computation into dedicated helper exposing per-component contributions (needs, compliance, clubs, attendance) with spec weights.
3. Expand Office Reports/renderer to display budget balance, recent transactions, and rating breakdown; include in headless status and saves.
4. Ensure headless log, save/load, and tests reflect new data; add targeted golden tests.

## Acceptance Evidence
- Economy unit test verifying budget deductions, insufficient funds rejection, and transaction recording.
- Rating breakdown test validating weighted result matches component sums.
- Office reports test confirming KPIs/transactions render with snapshot data.
- Full pytest + simulate + bounded run via `simulation_test` env after merge.
