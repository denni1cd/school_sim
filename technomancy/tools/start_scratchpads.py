#!/usr/bin/env python3
"""
Create ephemeral scratchpads for personas for THIS RUN only.
Outputs:
  runtime/arch_notes.md
  runtime/high_notes.md
  runtime/tech_notes.md
"""
from pathlib import Path
from datetime import datetime

TEMPLATE = """# {role} Scratchpad (Ephemeral)
_Run ID: {run_id} • Created: {ts}_

## Intent for this run
-

## Key assumptions (verify or remove)
-

## Risks / Unknowns
-

## Decisions (cite acceptance IDs if relevant)
-

## Next actions
-
"""

def main():
    runtime = Path("runtime")
    runtime.mkdir(parents=True, exist_ok=True)
    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    ts = run_id
    for role, fname in [("Arch Technomancer","arch_notes.md"),
                        ("High Technomancer","high_notes.md"),
                        ("Technomancer","tech_notes.md")]:
        Path(runtime / fname).write_text(TEMPLATE.format(role=role, run_id=run_id, ts=ts), encoding="utf-8")
        print(f"Wrote runtime/{fname}")

if __name__ == "__main__":
    main()
