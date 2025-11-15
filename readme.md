# School Sim

School Sim is a deterministic headless-/GUI-capable school-management prototype where the Headmistress makes strategic choices via an office UI while the world simulation drives student needs, policies, clubs, curriculum, rating, and budget systems. This vertical slice currently implements Milestones M0–M8 from `technomancy/docs/specification.md`, so production code, configs, runtime outputs, and golden tests all live under the authoritative `/school_sim` tree.

## Requirements

- **Python 3.12** (Python 3.12 is required; please use a virtual environment)
- **Dependencies:** `pygame`, `pyyaml`, `pytest` (install with `requirements.txt`)

## Setup

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

- Environment variables such as `SCHOOL_SIM_MAX_LOOPS` bound interactive sessions (e.g., `SCHOOL_SIM_MAX_LOOPS=12 make run`).
- Config-driven values (tick timing, budget, thresholds) live under `school_sim/configs/game.yaml`.

## Running the Application

- `make run` – launches the interactive renderer loop, draws HUD/overlays, and lets you open the Office modal (use `PYTHONPATH=.` on Windows to ensure module resolution).
- `make simulate` – headless loop that writes deterministic logs to `school_sim/runtime/logs/` (log format includes `STATUS`, `RATING`, `EVENT`, and per-student rows).
- `make demo` – drives a short headless snapshot session and auto-stops the interactive loop.
- `make test` – runs `pytest` against `school_sim/tests/`, covering golden tests for HUD, policies, clubs, curriculum, economy, and hygiene.

## Controls & Office Navigation

- **P** – Toggle the Principal Console overlay (displays announcements, saves/loads, and events).
- **T** – Advance time by 15 minutes for rapid progression.
- **E** – Trigger the next scripted event in `school_sim/configs/events.yaml`.
- **B** – Broadcast a log message to the school (log-only behavior).
- **L** – Load the most recent save file from `school_sim/runtime/saves/`.
- **S** – Save a snapshot (JSON) capturing students, policies, curriculum, budget, and rating history.
- **O** – Open the Headmistress Office modal:
  1. **Policies** – switch uniform/disciple levels; each change deducts the configured budget cost and emits overlay captions.
  2. **Clubs** – the latest snapshot displays each club with capacity, live membership count, overflow warnings, roster, and effects.
  3. **Curriculum** – cycle tracks (General/STEM/Arts) and inspect the summarized classroom modifiers before applying.
  4. **Staff** – read-only roster from `configs/staff.yaml`.
  5. **Reports** – current time, rating, budget, rating breakdown (needs/compliance/clubs/attendance), latest event, and economy history entries.
- **Esc/Enter** – close overlays or confirm Office actions; `Enter` applies a tab action while the Office is visible.
- While the Office modal is open, arrow keys or `1–5` switch tabs; the renderer draws the modal with tab labels, helper hints, and wrapped bodies.

## Policies Deep Dive

- Policies are configured in `school_sim/configs/policies.yaml` (default uniforms `moderate`, discipline `fair`, `change_policy` cost).  
- Every tick applies uniform/discipline effects to needs/compliance; uniform adjustments tweak hygiene/stress, discipline edits compliance/kg and stress relief.  
- Policy changes are handled through the Office (Policies tab) by moving the cursor to `Uniforms`/`Discipline` and hitting `Enter`; the change deducts the configured budget cost, emits an overlay via `school_sim/world.py`, and records a history entry surfaced in the Reports tab.  
- The policy history log keeps the last five entries; headless logs include this history if you inspect `school_sim/runtime/logs/sim_log.txt`.  
- Budget deductions and rating shifts following a policy change happen immediately, so you can observe `make run` output or the HUD while toggling policies in a live session.  
- Use `PYTHONPATH=. conda run -n simulation_test pytest -q school_sim/tests` to verify policy golden tests (`test_policies_uniforms.py`, `test_discipline_effects.py`, `test_policy_history.py`) whenever you change policy logic.  

## Clubs Deep Dive

- To add a new club, edit `school_sim/configs/clubs.yaml`: create a dictionary entry with required keys `id`, `name`, `room`, `meets_at`, `capacity`, and `effects` (per-minute deltas for needs/stress/energy). Optionally adjust `costs.assign_student` if clubs should charge more for onboarding.
- After updating the config, re-run `PYTHONPATH=. conda run -n simulation_test pytest -q school_sim/tests` to ensure the golden tests (`test_club_assignment_budget.py`, `test_clubs_capacity.py`, etc.) still pass, and the Office `Clubs` tab will immediately reflect the new entry next time you run `make run`.
- Configure clubs in `school_sim/configs/clubs.yaml`: each entry sets an ID, name, room, `meets_at` time, capacity, and per-tick `effects`. Budget costs for creating or assigning students appear under `costs.create_club` and `costs.assign_student`.
- `ClubsManager` handles assignments, deducting the `assign_student` cost from budget and adding the student to the club roster; over-capacity assignments still succeed but trigger stress penalties and rating warnings.
- Clubs apply their `effects` during meetings (when the world time matches `meets_at`), moving members to the club room, applying need deltas, and recording engagement samples so clubs influence rating.
- Overflow penalties log scene overlay events, add stress, and reduce the engagement ratio fed to the rating system; the office `Clubs` tab highlights capacity status plus roster details to help you rebalance membership.
- Use `PYTHONPATH=. conda run -n simulation_test pytest -q school_sim/tests` to verify the club golden tests (`test_clubs_capacity.py`, `test_club_assignment_budget.py`, `test_office_reports.py`) whenever club behavior changes.

## Budget & Reports Deep Dive

- The `economy.py` module centralizes budget adjustments; every policy or club action passes through `World._adjust_budget`, which records a timestamped transaction in `economy_history`. Transactions now appear in `Office Reports`, headless logs, and saves (visible under `school_sim/runtime/logs/` and `school_sim/runtime/saves/`).
- `rating.py` exposes a breakdown of the weighted components (needs, compliance, clubs, attendance). The HUD and headless `STATUS` lines surface this breakdown each tick, so you can tell how each pillar contributes to the total rating.
- The Offices reports section now shows budget, rating delta, attendance ratio, rating breakdown, outward events, recent transactions, and policy/history entries, so verifying finances and KPIs is just a glance away.
- To extend the budget/rating system, update `economy.py`, `rating.py`, and the `World` snapshot logic, then rerun `PYTHONPATH=. conda run -n simulation_test pytest -q school_sim/tests` along with `make simulate` and `make run`. Pay special attention to `test_economy_budget.py`, `test_rating_breakdown.py`, and `test_office_reports.py` when adjusting economy or reporting behavior.

## Project Layout

- `/school_sim/` – production code modules, configs, runtime artifacts, and tests.
- `/school_sim/configs/` – YAML definitions for events, room metadata, schedules, students, policies, clubs, curriculum, staff, and game constants.
- `/school_sim/runtime/` – deterministic outputs (logs, saves, scenes) used for verification; cleaned as part of each milestone’s standing order.
- `/school_sim/tests/` – golden acceptance tests referenced in the spec (office, policies, clubs, curriculum, economy, HUD, hygiene).
- `/technomancy/` – staging (deliverables, scripts), plans, logs, and tooling; contains only artifacts, merge scripts, and workflow documents.

## Configuration Highlights

- **Policies (`configs/policies.yaml`)** – control default uniforms (`strict`, `moderate`, `relaxed`), discipline (`tough`, `fair`, `lenient`), and change costs.
- **Clubs (`configs/clubs.yaml`)** – describe club schedules, rooms, capacities, effects, and economics (`create_club`, `assign_student` costs). Office and headless snapshots expose live roster data plus overflow penalties.
- **Curriculum (`configs/curriculum.yaml`)** – selects the active track; classroom modifiers apply every tick to student needs in the `Classroom`.
- **Game (`configs/game.yaml`)** – tick duration, win time, starting budget, rating penalties, and critical thresholds for hunger/energy/hygiene/stress.
- **Events (`configs/events.yaml`)** – feeds overlays and headless logs; events fire via the event bus and record captioned scene data under `school_sim/events`.

## Development & Verification Workflow

- Follow `technomancy/prompts/technomancy_system_prompt.md` during milestone work: plan (ARCH), generate tactical plans (HIGH), stage deliverables, write merge scripts, verify headless and interactive runs, and publish `technomancy/logs/final_report_m<id>.md`.
- Keep production code under `/school_sim` while staging happens beneath `/technomancy/deliverables/{src,tests}`; after each milestone, run the generated merge script and ensure `/technomancy/deliverables/` holds only scripts (no shippables).
- Apply `PYTHONPATH=.` when invoking any Python-based command from the repo root to guarantee local packages supersede global installs.
- Use `technomancy/tools/generate_acceptance_coverage.py` to keep tasks aligned with spec Acceptance IDs; cite `AC-xxx` references in plans and reports.

Refer to `technomancy/docs/specification.md` (v1.4) for milestone acceptance criteria, config schemas, and the overall modernization roadmap.

## Implementation Review (Pending Structures)

1. **Policy flow and automation (`school_sim/policies.py`, `school_sim/world.py`, `school_sim/office.py`)** – Uniforms and discipline toggles are wired through the office UI, budget adjustments, and rating hooks, yet there is no scheduled automation, policy cooldown handling, or teacher-targeted interventions. Future work could layer in policy milestones, tiered costs, and more granular compliance tracking per homeroom beyond the current uniform/discipline pair.

2. **Clubs system (`school_sim/clubs.py`, `school_sim/configs/clubs.yaml`)** – Club meetings, assignments, and overflow penalties exist, but club creation/assignment still requires direct YAML edits; there is no runtime editor, limiting operations to config tweaks or tests. Planned enhancements include a club builder UI, dynamic costs per student, and richer effect profiles per need (currently static modifiers).

3. **Curriculum tracks and classroom impacts (`school_sim/curriculum.py`)** – The three hardcoded tracks only adjust need deltas for stress/energy/hygiene; there are no elective scheduling, teacher availability, or progress rewards yet. Expanding this structure will involve tracking classroom assignments, unlocking track-specific modules, and tying curriculum changes into policy/event budgets.

4. **Staff management (`school_sim/office.py`, `school_sim/configs/staff.yaml`)** – Staff entries render in the Office but remain read-only data. The console lacks hiring/firing, shift scheduling, or staff-driven effects on student needs or compliance. Consider adding staff actions, budget impacts, or integration with events/ratings before claiming the staff subsystem is implemented.

5. **Event-driven overlays (`school_sim/events/*`)** – Scene payloads, bus wiring, and rules fire overlays, yet metadata beyond image/caption is minimal, and there is no visual editor or event authoring GUI. Expanding this structure, including event tagging, conditional payload variations, or richer metadata, would make the feature set complete.
