#!/usr/bin/env python3
"""
Remove ephemeral runtime artifacts created for a single Technomancy run.
"""
from pathlib import Path
import shutil

RUNTIME_FILES = [
    "repo_map.md",
    "acceptance_coverage.md",
    "arch_notes.md",
    "high_notes.md",
    "tech_notes.md",
    "context_files.md",
    "run_config.yaml",
    "context_pack.md",
]

def main():
    rt = Path("runtime")
    if not rt.exists():
        print("runtime/ does not exist; nothing to clean")
        return
    for f in RUNTIME_FILES:
        p = rt / f
        if p.exists():
            p.unlink()
            print(f"Removed {p}")
    print("Cleanup complete.")

if __name__ == "__main__":
    main()
