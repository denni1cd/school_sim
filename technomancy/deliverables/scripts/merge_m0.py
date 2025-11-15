#!/usr/bin/env python
"""
Idempotent merge script for Milestone M0.

Copies staged assets from technomancy/deliverables into the production tree,
cleans legacy root files, and removes staging directories containing shippable
artifacts once the merge is complete.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]
DELIVERABLES = ROOT / "technomancy" / "deliverables"
STAGING_SRC = DELIVERABLES / "src"
STAGING_TESTS = DELIVERABLES / "tests"
PRODUCTION_ROOT = ROOT / "school_sim"


def _copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _copy_tree(src: Path, dest: Path) -> None:
    shutil.copytree(src, dest, dirs_exist_ok=True)


def _remove_paths(paths: Iterable[Path]) -> None:
    for path in paths:
        if not path.exists():
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def main() -> None:
    if not STAGING_SRC.exists():
        raise SystemExit(f"Staging src directory missing: {STAGING_SRC}")

    # 1. Copy updated root files.
    for filename in ("Makefile", "requirements.txt", "readme.md"):
        staged_file = STAGING_SRC / filename
        if not staged_file.exists():
            raise SystemExit(f"Expected staged file missing: {staged_file}")
        _copy_file(staged_file, ROOT / filename)

    # 2. Copy school_sim package into production root.
    staged_package = STAGING_SRC / "school_sim"
    if not staged_package.exists():
        raise SystemExit(f"Staged package missing: {staged_package}")
    _copy_tree(staged_package, PRODUCTION_ROOT)

    # 3. Overlay any staged tests (should already be inside package, but keep hook).
    if STAGING_TESTS.exists():
        for test_file in STAGING_TESTS.rglob("*.py"):
            relative = test_file.relative_to(STAGING_TESTS)
            _copy_file(test_file, PRODUCTION_ROOT / "tests" / relative)

    # 4. Remove legacy root files and directories superseded by the package.
    legacy_dirs = [
        ROOT / "configs",
        ROOT / "events",
        ROOT / "runtime",
        ROOT / "tests",
        ROOT / "src",
        ROOT / "__pycache__",
    ]
    legacy_files = [
        ROOT / "student.py",
        ROOT / "world.py",
        ROOT / "room.py",
        ROOT / "timetable.py",
        ROOT / "game_state.py",
    ]
    _remove_paths(legacy_dirs + legacy_files)

    # 5. Clean pycache artifacts under production tree.
    for cache_dir in PRODUCTION_ROOT.rglob("__pycache__"):
        shutil.rmtree(cache_dir)

    # 6. Remove staging payloads (leave scripts directory intact).
    if STAGING_SRC.exists():
        shutil.rmtree(STAGING_SRC)
    if STAGING_TESTS.exists():
        shutil.rmtree(STAGING_TESTS)

    print("Merge M0 complete.")
    print(f"  - production package => {PRODUCTION_ROOT}")
    print("  - root files refreshed: Makefile, requirements.txt, readme.md")
    print("  - legacy root modules and directories removed")
    print("  - staging directories cleared (src/, tests/)")


if __name__ == "__main__":
    main()
