#!/usr/bin/env python
"""Merge script for Milestone M2."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DELIVERABLES = ROOT / "technomancy" / "deliverables"
STAGING_SRC = DELIVERABLES / "src"
STAGING_TESTS = DELIVERABLES / "tests"
PRODUCTION_ROOT = ROOT / "school_sim"
PRODUCTION_TESTS = PRODUCTION_ROOT / "tests"


def _copytree(src: Path, dest: Path) -> None:
    shutil.copytree(src, dest, dirs_exist_ok=True)


def _copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _clear_pycache(root: Path) -> None:
    for path in root.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)


def main() -> None:
    package_src = STAGING_SRC / "school_sim"
    if not package_src.exists():
        raise SystemExit(f"Missing staged package: {package_src}")

    _copytree(package_src, PRODUCTION_ROOT)

    if STAGING_TESTS.exists():
        for test_file in STAGING_TESTS.glob("*.py"):
            _copy_file(test_file, PRODUCTION_TESTS / test_file.name)

    for runtime_dir in (
        PRODUCTION_ROOT / "runtime" / "logs",
        PRODUCTION_ROOT / "runtime" / "saves",
        PRODUCTION_ROOT / "runtime" / "scenes",
    ):
        runtime_dir.mkdir(parents=True, exist_ok=True)

    _clear_pycache(PRODUCTION_ROOT)

    if package_src.exists():
        shutil.rmtree(package_src)
    if STAGING_TESTS.exists():
        shutil.rmtree(STAGING_TESTS)

    print("Merge M2 complete.")
    print(f"  - Updated school_sim package at {PRODUCTION_ROOT}")
    print("  - Copied golden/spec tests into school_sim/tests")
    print("  - Cleared staging directories")


if __name__ == "__main__":
    main()
