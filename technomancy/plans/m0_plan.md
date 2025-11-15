# Milestone M0 Plan 

## Goal
Align repository grounding artifacts (tree layout, Makefile, requirements, README) with spec v1.4 and add a hygiene test to enforce structure before gameplay milestones.

## Current Assessment
- Code lives under `src/school_sim/` instead of `/school_sim`; tests under `/tests` rather than `/school_sim/tests`.
- `Makefile`, `requirements.txt`, and `readme.md` exist but need validation against spec (naming, commands, docs).
- No Technomancy staging directories populated; no hygiene test ensuring layout.

## Work Streams
1. **Production Layout Migration**
   - Stage scripts to create `/school_sim` production tree with required subdirs (`configs`, `runtime`, `tests`, etc.).
   - Plan migration of existing modules from `src/school_sim` into production tree while keeping spec placeholders for future modules.
2. **Tooling & Docs Hygiene**
   - Verify/adjust `Makefile` commands (`run`, `simulate`, `test`) to operate against production tree.
   - Trim `requirements.txt` to spec allowed packages.
   - Update root `README.md` with run/test/simulate instructions and controls reference per spec.
3. **Hygiene Testing**
   - Add `tests/test_repo_hygiene.py` covering directory layout, README sections, Makefile presence, requirements minimality.

## Acceptance Evidence Needed
- `pytest -q` passes including new hygiene test (staged).
- Manual verification of README content and requirements list.
- `make run`, `make simulate`, `make test` execute without missing targets (post-merge verification step for HIGH persona).
- No production artifacts left in `/technomancy/deliverables/**` after merge.
