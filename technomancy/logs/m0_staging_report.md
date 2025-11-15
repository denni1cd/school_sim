# Milestone M0 Staging Report

## Summary
- Ported runtime code, configs, and tests into a production `/school_sim` package with required subdirectories (`configs`, `events`, `runtime`, `tests`).
- Updated Makefile, requirements, and README to reflect the new package-centric layout and documented run/simulate/test commands plus controls.
- Added `test_repo_hygiene.py` to enforce directory hygiene, minimal requirements, and README/Makefile coverage.
- Normalised loaders (`bootstrap`, `headless`, `main`, `save_system`) to resolve paths relative to the package root for portability.

## Tests
- `pytest -q technomancy/deliverables/src/school_sim/tests`
