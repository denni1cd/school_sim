# Milestone M4 Plan

## Goal
Deliver Milestone M4 (Office Shell): introduce an office modal with tab navigation and read-only summaries sourced from new configuration files while keeping existing gameplay stable.

## Current Assessment
- Renderer lacks any binding for the `O` key or modal overlay beyond the event scene.
- No `office.py` module; no structures to represent tabs, tab content, or keyboard navigation.
- Config files for policies/clubs/curriculum/staff do not exist; bootstrap loaders have no awareness of them.
- Tests do not exercise office navigation or the presence of new config assets.

## Work Streams
1. **Office Module Foundation**
   - Create `office.py` owning modal state, tab registry, text summaries, and clubs tab output that shows live membership counts/overflow warnings drawn from world snapshots.
2. **Config Scaffolding & Loading**
   - Add YAML scaffolds for policies/clubs/curriculum/staff; extend bootstrap utilities to load them with defaults.
3. **Renderer Integration**
   - Wire Office into renderer/main loop: toggle visibility with `O`, close via `ESC`/`ENTER`, draw modal overlay without disturbing existing HUD/overlay.
4. **Testing & Hygiene**
   - New `test_office_shell.py` for navigation + summaries; update `test_repo_hygiene.py` for required config assets; ensure regressions avoided.
5. **Merge & Reporting**
   - Follow technomancy workflow: stage changes, generate merge script, run verification, publish reports.

- `pytest -q school_sim/tests` including new office tests passes, with the Clubs tab test covering membership counts and overflow warnings.
- `make run` demonstrates toggling office modal and tab cycling w/o crashes.
- `make simulate` still writes logs without office interference.
- Staging + final reports captured under `technomancy/logs`.
