# Tactical Plan — Milestone E: QA & Polish

## Objective
Stabilize the engine after major feature additions by expanding automated coverage, profiling performance, fixing critical bugs, and preparing documentation for future visual upgrades.

## Preconditions
- Milestones A–D merged with baseline functionality verified.
- CI pipeline capable of running `pytest` and linting (if available).
- Performance profiling tools (e.g., cProfile, line_profiler) accessible.

## Implementation Steps
1. **Quality Audit (QA Lead, Engineering Lead)**
   - Review bug backlog and open TODOs introduced in prior milestones.
   - Categorize issues into blockers, must-fix, follow-ups; track in `docs/qa_backlog.md` with owner and status.

2. **Test Coverage Expansion (QA Lead)**
   - Use `pytest --cov=game` to identify untested modules (focus on `principal_controls`, `activities`, `conflict_resolver`).
   - Write targeted tests:
     - Edge cases for schedule overrides colliding with curfew.
     - Activity interruption when NPC forcibly moved.
     - Alert rate-limiting and persistence.
   - Store new tests under relevant directories to keep scope clear.

3. **Long-Run Simulation Soak (Systems Engineer)**
   - Execute 7-day in-game simulation: `python -m game.simulation --map campus_v1 --ticks 40320 --log-activities --log-alerts`.
   - Capture metrics: average frame time, pathfinding latency, alert frequency.
   - Export summary to `docs/performance_report.md` (tables + charts if possible).

4. **Performance Profiling (Systems Engineer, Engineering Lead)**
   - Profile pathfinding hot spots using `python -m cProfile -o profile.out game/simulation_runner.py --map campus_v1`.
   - Analyze with `snakeviz profile.out` (or textual `pstats`) and record recommended optimizations.
   - Implement low-risk improvements (e.g., caching travel paths, reducing logging verbosity) guarded by unit tests.

5. **Bug Fix Sprint (Gameplay Engineer, Systems Engineer)**
   - Address blockers from `qa_backlog.md`, prioritizing:
     - NPC stuck detection failing.
     - Alerts not clearing after acknowledgement.
     - Serialization mismatches for overridden schedules.
   - Ensure each fix has regression test coverage.

6. **Documentation & Release Prep (Producer, Content Designer)**
   - Compile `docs/milestone_release_notes.md` summarizing features, known issues, next steps.
   - Update `readme.md` usage instructions, map screenshots (placeholder), and command reference.
   - Create onboarding checklist for future art/audio teams detailing placeholders and replacement guidelines.

7. **Final Verification (QA Lead, Product Lead)**
   - Run full `pytest` suite and linting (`ruff`, `flake8`, or `python -m compileall game` if lint unavailable).
   - Conduct supervised playtest: start new simulation, override schedule, confirm alerts/resolution, observe activity reporting.
   - Sign off in `docs/qa_signoff.md` with checklist status.

## Deliverables
- Expanded automated test suite with coverage report. *(Implemented via new regression tests in `tests/`.)*
- Performance profiling report and implemented optimizations. *(`docs/performance_report.md`, movement system path caching.)*
- Updated documentation (release notes, README, onboarding checklist). *(`docs/milestone_release_notes.md`, `docs/onboarding_checklist.md`, README updates.)*
- QA sign-off checklist capturing final validation. *(`docs/qa_signoff.md`, `docs/qa_backlog.md`.)*

## Acceptance Criteria
- Full `pytest` suite passes consistently on local and CI runs.
- Performance metrics stay within agreed thresholds (documented in `performance_report.md`).
- No open blockers remain in `qa_backlog.md`; follow-up items documented for next phase.
- Documentation accurately reflects engine capabilities and placeholders.
