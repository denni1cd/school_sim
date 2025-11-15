# Milestone M4 Work Orders

## WO-1 Config Foundations
- Create new YAML scaffolds under `technomancy/deliverables/docs/configs` destined for `school_sim/configs/{policies.yaml,clubs.yaml,curriculum.yaml,staff.yaml}`.
- Update `bootstrap.py` staging copy (`technomancy/deliverables/src/bootstrap.py`) to expose loaders for the new configs.

## WO-2 Office Module
- Implement `technomancy/deliverables/src/office.py` providing modal state, tab definitions, summary generation hooks, keyboard navigation helpers, and `Clubs` tab lines that reflect live membership counts and highlight overflow per snapshot data.

## WO-3 Renderer/Main Wiring
- Modify renderer (`technomancy/deliverables/src/renderer.py`) and entry (`technomancy/deliverables/src/main.py`) to instantiate the office module, route keyboard events (`O`, arrow keys, digits, `ESC`/`ENTER`), and draw the modal shell.

- Add `technomancy/deliverables/tests/test_office_shell.py` covering toggle, tab navigation, config summary pulls, and the new club membership/overflow output.
- Extend `technomancy/deliverables/tests/test_repo_hygiene.py` (or patch existing) asserting presence of new config files; ensure fixtures updated as needed.

## WO-5 Technomancy Rituals
- Generate `technomancy/deliverables/scripts/merge_m4.py` to move staged assets into production tree.
- Produce staging report (`technomancy/logs/m4_staging_report.md`) and final report once verification completes.
