#!/usr/bin/env python
"""
Merge script for Milestone M1.

Copies staged sources/tests into the production tree, removes temporary staging
folders, and performs light hygiene (clearing __pycache__ entries).
"""
from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DELIVERABLES = ROOT / "technomancy" / "deliverables"
STAGING_SRC = DELIVERABLES / "src"
STAGING_TESTS = DELIVERABLES / "tests"
PRODUCTION_ROOT = ROOT / "school_sim"
TEST_ROOT = PRODUCTION_ROOT / "tests"


def _copytree(src: Path, dest: Path) -> None:
    shutil.copytree(src, dest, dirs_exist_ok=True)


def _copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _clear_pycache(root: Path) -> None:
    for path in root.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)


def main() -> None:
    if not STAGING_SRC.exists():
        raise SystemExit(f"Staging sources missing: {STAGING_SRC}")

    staged_package = STAGING_SRC / "school_sim"
    if not staged_package.exists():
        raise SystemExit("Expected staged school_sim package not found.")

    # Copy staged package into production.
    _copytree(staged_package, PRODUCTION_ROOT)

    # Copy staged tests into the production tests directory.
    if STAGING_TESTS.exists():
        for test_file in STAGING_TESTS.glob("*.py"):
            _copy_file(test_file, TEST_ROOT / test_file.name)

    # Hygiene: ensure runtime directories exist and clear pycache.
    for runtime_dir in (PRODUCTION_ROOT / "runtime" / "logs", PRODUCTION_ROOT / "runtime" / "saves", PRODUCTION_ROOT / "runtime" / "scenes"):
        runtime_dir.mkdir(parents=True, exist_ok=True)
    _clear_pycache(PRODUCTION_ROOT)

    # Remove staging payloads after successful copy (but keep scripts directory).
    if STAGING_SRC.exists():
        shutil.rmtree(STAGING_SRC)
    if STAGING_TESTS.exists():
        shutil.rmtree(STAGING_TESTS)

    print("Merge M1 complete.")
    print(f"  - school_sim package updated at {PRODUCTION_ROOT}")
    print("  - golden tests copied to school_sim/tests")
    print("  - staging directories cleared")


if __name__ == "__main__":
    main()
