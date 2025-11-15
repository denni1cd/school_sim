# Project Plan

## Traceability
- **FR1 – Core Simulation Loop & Needs:** deliver deterministic time progression, room effects, and need drift under Milestones M0–M2 so later tabs have valid input data.
- **FR2 – Events & Overlay:** tie scene overlay behavior and event instrumentation to Milestone M1 so overlays can later report policy or club triggers.
- **FR3 – Needs Overrides & Rating:** align Milestone M2 with per-room/target overrides, room effects, and rating flash logic to keep HUD meaningfully responsive.
- **FR4 – Console Actions & Persistence:** reserve Milestone M3 for console toggles, manual actions (`P/T/E/B/L`), and JSON save/load compliance to lock down reproducibility.
- **FR5 – Office Shell:** assign Milestone M4 to the office modal plus tab navigation, configuration summaries, and the club membership visibility enhancement described in the current work scope.
- **FR6 – Policies:** let Milestone M5 implement uniform and discipline policies, compliance tracking, and budget hooks.
- **FR7 – Clubs:** dedicate Milestone M6 to club configuration, assignment, meetings, overflow penalties, and membership reporting via the office.
- **FR8 – Curriculum:** target Milestone M7 with track selection and classroom modifiers while plumbing canvas updates and reports.
- **FR9 – Budget & Reports:** finish in Milestone M8 by wiring the economy module, rating breakdowns, headless HUD, logs, and tests.
- **NFR1 – Python 3.12 Stack:** enforce the interpreter and dependency constraints across every milestone.
- **NFR2 – Config-Driven Content:** keep YAML configs authoritative for rooms, policies, clubs, curriculum, and events starting in M1.
- **NFR3 – Deterministic Runbook:** require `make run`, `make simulate`, and `pytest` to succeed in every milestone per the spec’s verification gates.

## Architecture
- **Entry point (`main.py`/`headless.py`):** parse CLI args, instantiate configs, set up `World`, bind the `EventBus`, `SceneOverlay`, `PrincipalConsole`, `OfficeScreen`, and `SaveSystem`, then drive the renderer loop.
- **World & Students (`world.py`, `student.py`):** orchestrate per-minute ticks, needs drift, policy effects, club meetings, rating computation (`rating.py`), attendance tracking, and economy history. `World` exposes snapshots, registers events, and workflows with `SaveSystem`.
- **Renderer/Office/Console (`renderer.py`, `office.py`, `principal_console.py`):** translate world snapshots to HUD frames, overlay states, and input actions (`O` toggles the office, arrow keys cycle tabs, `ENTER/ESC` confirm or dismiss). The office leverages configuration metadata and live snapshots (including club membership counts) to render summaries.
- **Policies/Clubs/Curriculum Modules (`policies.py`, `clubs.py`, `curriculum.py`):** provide deterministic modifiers, compliance adjustments, club scheduling effects, and curriculum track modifiers that the `World` orchestrates via dependency injection.
- **Economy & Rating (`economy.py`, `rating.py`):** centralize budget mutations, record high-level transactions, and expose the weighted rating breakdown (needs, compliance, clubs, attendance) to stats consumers (HUD, reports).
- **Events (`events/` package):** define models, loaders, buses, rules, and overlays so policy, club, and curriculum actions can emit deterministic narratives.
- **Tests (`tests/`):** drive golden acceptance coverage per milestone, especially: `test_office_shell.py`, `test_policies_uniforms.py`, `test_clubs_capacity.py`, `test_curriculum_modifiers.py`, `test_economy_budget.py`, `test_rating_breakdown.py`, etc.
- **Configs & Runtime:** store YAML under `/school_sim/configs/` and runtime artifacts/logs under `/school_sim/runtime/` per the hygiene rules.

## Milestone Summary
- **M0 – Tree Hygiene & Bootstrapping:** ensure `/school_sim/**`, `/technomancy/**` structure, Makefile targets, and initial smoke tests succeed.
- **M1 – Events + HUD:** add event bus, overlay, HUD instrumentation, and the principal console; verify golden tests (`test_events_visible.py`, `test_overlay_contract.py`).
- **M2 – Needs & Rating:** wire per-room overrides, dynamic rating with flash threshold, and deterministic headless logging; confirm `test_needs_overrides.py`, `test_rating_system.py`.
- **M3 – Actions & Persistence:** expand console controls, implement save/load, ensure `make run`, `make simulate`, and `pytest` remain green.
- **M4 – Office Shell & Club Visibility:** add the office modal with tabs, config summaries, and snapshot-driven club membership badges/overflow warnings; acceptance includes `test_office_shell.py` and new coverage showing membership data and navigation shortcuts.
- **M5 – Policies & Compliance:** implement uniforms/discipline choices, overlay triggers, and budget costs; acceptance includes `test_policies_uniforms.py`, `test_discipline_effects.py`, and log verification.
- **M6 – Clubs Management:** implement config-driven clubs, meeting application, overflow penalties, and deterministic scheduler tests; acceptance includes `test_clubs_capacity.py`, `test_club_assignment_budget.py`, and `test_office_reports.py`.
- **M7 – Curriculum Tracks:** expose STEM/Arts/General tracks with classroom modifiers, headless reporting, and persistent configs; acceptance includes `test_curriculum_modifiers.py` and `test_office_curriculum.py`.
- **M8 – Budget & Reports:** route all transactions through `economy.py`, compute rating breakdowns, surfaced in HUD/office, and verify with `test_economy_budget.py`, `test_rating_breakdown.py`, plus `make simulate`/`make run` runs.

## Rationale
- Sequence each milestone so dependencies resolve: the office requires a deterministic world and HUD (M1, M2), policies depend on the office UI (M4), clubs build on policy state and office reporting (M5, M6), curriculum chooses tracks before budget/reporting (M7), and the economy is last to present a polished vertical slice (M8).
- Centralize snapshots and economy changes so deterministic acceptance tests can assert the same data (club memberships, rating breakdowns, transactions) across interactive and headless runs, reducing flakiness.
- Keep configs and runtime outputs rooted at `/school_sim` with staged artifacts under `/technomancy` to align with the spec’s hygiene rules and to maintain separation between production and staging work.
