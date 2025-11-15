# Milestone M0 Work Orders

## WO-1 Production Layout Bootstrap
- **Production target:** `/school_sim/`
- **Stage files to:** `technomancy/deliverables/src/school_sim/`
- **Actions:**
  1. Mirror required directory skeleton (`configs`, `runtime/{logs,saves,scenes}`, `tests`, `events`) in staging.
  2. Move existing modules from `src/school_sim/` into staging tree (preserve package imports) and prepare merge to production root.
  3. Ensure `__init__.py` present where needed.
- **Tests:** rely on repo hygiene test once added.

## WO-2 Tooling Hygiene
- **Production targets:** `Makefile`, `requirements.txt`, `README.md`
- **Stage files to:** `technomancy/deliverables/src/`
- **Actions:**
  1. Align Makefile commands to operate on `/school_sim` layout.
  2. Trim `requirements.txt` to `[pygame, pyyaml, pytest]` + actually used packages.
  3. Update README with Run/Test/Simulate instructions and controls list (at minimum: `run`, `simulate`, `test`, basic keybindings `P,T,E,B,L,O,ESC/ENTER`).
- **Tests:** repo hygiene test to assert sections and minimal requirements.

## WO-3 Repo Hygiene Test
- **Production target:** `/school_sim/tests/test_repo_hygiene.py`
- **Stage file to:** `technomancy/deliverables/tests/test_repo_hygiene.py`
- **Actions:**
  1. Implement test verifying: production tree exists with required dirs, `Makefile` has `run/simulate/test` targets, `requirements.txt` only contains allowed packages, README includes sections for running/testing/simulating and controls.
  2. Update `pytest` configuration if needed to discover tests under new tree.
- **Tests:** run `pytest -q` against staging (TECH to execute).

## WO-4 Merge Script + Reports
- **Production target:** n/a (script only)
- **Stage to:** `technomancy/deliverables/scripts/merge_m0.py`
- **Actions:**
  1. Author merge script copying staged files into production tree (`/school_sim`, root files) and removing staging deliverables after merge per hygiene.
  2. Document staging changes in `technomancy/logs/m0_staging_report.md`.
- **Tests:** High persona to run script and verify post-merge commands.
