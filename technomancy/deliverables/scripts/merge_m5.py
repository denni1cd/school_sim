#!/usr/bin/env python
"""Merge script for Milestone M5."""
from __future__ import annotations

import shutil
import sys
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


def _ensure(path: Path, description: str) -> None:
    if not path.exists():
        sys.exit(f"Missing {description}: {path}")


def main() -> None:
    package_src = STAGING_SRC / "school_sim"
    _ensure(package_src, "staged package directory")

    _copytree(package_src, PRODUCTION_ROOT)

    if STAGING_TESTS.exists():
        for test_file in STAGING_TESTS.rglob("*.py"):
            destination = PRODUCTION_TESTS / test_file.relative_to(STAGING_TESTS)
            _copy_file(test_file, destination)

    _clear_pycache(PRODUCTION_ROOT)

    if package_src.exists():
        shutil.rmtree(package_src)
    if STAGING_TESTS.exists():
        shutil.rmtree(STAGING_TESTS)

    print("Merge M5 complete.")
    print(f"  - Updated {PRODUCTION_ROOT}")
    print("  - Copied staged tests into school_sim/tests")
    print("  - Cleared technomancy/deliverables/src and tests")


if __name__ == "__main__":
    main()
