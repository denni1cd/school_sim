#!/usr/bin/env python3
"""
Assemble a single context pack that Codex/agents can read before execution.
This stays ephemeral and uses ONLY repo-local data created this run.
It simply concatenates the runtime artifacts into runtime/context_pack.md.

Usage (typical order):
  python tools/generate_repo_map.py --root . --out runtime/repo_map.md
  python tools/generate_acceptance_coverage.py --spec docs/spec.md --out runtime/acceptance_coverage.md
  python tools/start_scratchpads.py
  python tools/context_budgeter.py --root . --task "TASK" --limit 25 --out runtime/context_files.md
  python tools/mempack.py
"""
from pathlib import Path
from datetime import datetime

PARTS = [
    ("Repository Map", "runtime/repo_map.md"),
    ("Acceptance Coverage Matrix", "runtime/acceptance_coverage.md"),
    ("Persona Scratchpads", "runtime/arch_notes.md"),
    ("Persona Scratchpads", "runtime/high_notes.md"),
    ("Persona Scratchpads", "runtime/tech_notes.md"),
    ("Context Files", "runtime/context_files.md"),
]

def read_if(path: Path):
    return path.read_text(encoding="utf-8") if path.exists() else f"_missing: {path}_"

def main():
    out = Path("runtime/context_pack.md")
    lines = ["# Technomancy Context Pack (Ephemeral)",
             "",
             f"_Generated: {datetime.utcnow().isoformat()}Z_",
             ""]
    for title, rel in PARTS:
        lines += [f"\n---\n\n# {title}\n", read_if(Path(rel))]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
