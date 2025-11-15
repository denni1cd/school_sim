#!/usr/bin/env python
"""Merge script for Milestone M3."""
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

    for root_file in ("Makefile", "requirements.txt", "readme.md"):
        staged = STAGING_SRC / root_file
        if staged.exists():
            _copy_file(staged, ROOT / root_file)

    if STAGING_TESTS.exists():
        for test_file in STAGING_TESTS.glob("*.py"):
            _copy_file(test_file, PRODUCTION_TESTS / test_file.name)

    _clear_pycache(PRODUCTION_ROOT)

    if (STAGING_SRC / "school_sim").exists():
        shutil.rmtree(STAGING_SRC / "school_sim")
    if (STAGING_SRC / "Makefile").exists():
        (STAGING_SRC / "Makefile").unlink()
    if (STAGING_SRC / "requirements.txt").exists():
        (STAGING_SRC / "requirements.txt").unlink()
    if (STAGING_SRC / "readme.md").exists():
        (STAGING_SRC / "readme.md").unlink()
    if STAGING_TESTS.exists():
        shutil.rmtree(STAGING_TESTS)

    print("Merge M3 complete.")
    print(f"  - Updated {PRODUCTION_ROOT}")
    print("  - Root docs (Makefile/requirements/readme) refreshed")
    print("  - Tests copied to school_sim/tests")
    print("  - Staging directories cleared")


if __name__ == "__main__":
    main()
