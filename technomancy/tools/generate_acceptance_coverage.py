#!/usr/bin/env python3
"""
Parse a spec markdown and emit an Acceptance Coverage Matrix as runtime/acceptance_coverage.md.

The script looks for a header containing "Acceptance Criteria" (case-insensitive)
and then collects bullet items until the next header. If no such section is found,
it will scan for any lines that look like checklist/bullets and warn.

Usage:
  python tools/generate_acceptance_coverage.py --spec docs/spec.md --out runtime/acceptance_coverage.md
"""
import re, argparse
from pathlib import Path
from datetime import datetime

HEADER_RE = re.compile(r'^\s{0,3}#{1,6}\s+.*$', re.I)
ACCEPT_HEADER_RE = re.compile(r'^\s{0,3}#{1,6}\s+.*acceptance.*criteria.*$', re.I)
BULLET_RE = re.compile(r'^\s*[-*+]\s+(.*\S)\s*$')
CHECK_RE = re.compile(r'^\s*[-*+]\s+\[(?: |x|X)\]\s+(.*\S)\s*$')

def extract_acceptance(spec_text: str):
    lines = spec_text.splitlines()
    in_accept = False
    items = []
    for i, line in enumerate(lines):
        if ACCEPT_HEADER_RE.match(line):
            in_accept = True
            continue
        if in_accept and HEADER_RE.match(line):
            break
        if in_accept:
            m = CHECK_RE.match(line) or BULLET_RE.match(line)
            if m:
                items.append(m.group(1).strip())
    # fallback: collect any bullets if none found
    if not items:
        for line in lines:
            m = CHECK_RE.match(line) or BULLET_RE.match(line)
            if m:
                items.append(m.group(1).strip())
    return items

def render_matrix(items, spec_path: Path):
    ts = datetime.utcnow().isoformat()+"Z"
    rows = []
    for idx, text in enumerate(items, 1):
        ac_id = f"AC-{idx:03d}"
        # Planned columns left for personas to fill during the run
        rows.append(f"| {ac_id} | {text} | _TBD_ | _TBD_ | Not Started |")
    table = "\n".join([
        "# Acceptance Coverage Matrix",
        "",
        f"_Spec: {spec_path} • Generated: {ts}_",
        "",
        "| ID | Criterion | Planned Deliverables | Planned Tests | Status |",
        "|---:|---|---|---|---|",
        *rows,
        "",
        "> Personas: Before coding, fill 'Planned Deliverables' & 'Planned Tests'. Update Status as you proceed."
    ])
    return table

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="Path to spec markdown file")
    ap.add_argument("--out", default="runtime/acceptance_coverage.md")
    args = ap.parse_args()

    spec_path = Path(args.spec)
    text = spec_path.read_text(encoding="utf-8", errors="ignore")
    items = extract_acceptance(text)
    if not items:
        items = ["<No acceptance criteria found in spec>"]
    out_text = render_matrix(items, spec_path)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_text, encoding="utf-8")
    print(f"Wrote {out_path} ({len(items)} criteria)")

if __name__ == "__main__":
    main()
