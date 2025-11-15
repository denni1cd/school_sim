# Technomancy Ephemeral Helpers — Integration Guide

These helpers keep Technomancy **green-field and repo-scoped** while improving clarity and coverage. Nothing persists between runs.

## Files & Scripts

- `tools/generate_repo_map.py` → emits `runtime/repo_map.md`
- `tools/generate_acceptance_coverage.py --spec <spec.md>` → emits `runtime/acceptance_coverage.md`
- `tools/start_scratchpads.py` → emits `runtime/arch_notes.md`, `runtime/high_notes.md`, `runtime/tech_notes.md`
- `tools/context_budgeter.py --task "<task>"` → emits `runtime/context_files.md`
- `tools/mempack.py` → concatenates all runtime files into `runtime/context_pack.md`
- `tools/cleanup_runtime.py` → removes runtime artifacts after the run
- `prompts/determinism_preamble.md` → add to your system prompt

## Typical Flow

1. Generate ephemeral context for the **current task**:
   ```bash
   python tools/generate_repo_map.py --root . --out runtime/repo_map.md
   python tools/generate_acceptance_coverage.py --spec docs/spec.md --out runtime/acceptance_coverage.md
   python tools/start_scratchpads.py
   python tools/context_budgeter.py --root . --task "TASK TITLE & SUMMARY" --limit 25 --out runtime/context_files.md
   python tools/mempack.py
   ```

2. Ensure your **system prompt** tells Codex/agents to read:
   - `prompts/determinism_preamble.md`
   - `runtime/context_pack.md`

3. After the run, clean up:
   ```bash
   python tools/cleanup_runtime.py
   ```

## System Prompt Patch

Add this block near the top of `technomancy_system_prompt.md`:

```
Before you begin:
- Read and follow `prompts/determinism_preamble.md`.
- Read `runtime/context_pack.md` for situational context (repo map, acceptance coverage, persona scratchpads, context files).
- Treat all `runtime/*.md` as ephemeral and authoritative for this run.
- Cite Acceptance IDs (AC-xxx) and file paths in your plan and commits.
```

## Notes
- No external indexes, no persistent memory. Everything derives from the **current** repo + spec.
- If your spec stores acceptance criteria elsewhere, point `--spec` accordingly.
- You can wire these into a Makefile or a simple shell script for convenience.
