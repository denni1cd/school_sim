# Milestone M3 Plan

## Goal
Deliver Milestone M3 (Actions + Save/Load). Expand player actions (P/T/E/B/L plus save/load triggers), ensure JSON save format matches spec, and solidify console/headless interactions.

## Current Assessment
- Console handles P/T/E/B subset; lacks direct Save (`S`) and Load (`L`) triggers and budget/rating logging.
- Save system snapshot excludes policy/curriculum/budget/rating fields required by spec v1.4.
- Tests cover earlier milestones but no dedicated action/save-load contract tests.
- Headless runner can load but snapshot lacks new fields.

## Work Streams
1. **Action Handling**
   - Extend `PrincipalConsole` and main loop to support P/T/E/B/L plus new action keys (save/load via console and keyboard overlay).

2. **Save/Load Format**
   - Update `SaveSystem` snapshot/apply to capture `budget`, `rating`, policies/curriculum placeholders per spec.
   - Ensure load handles missing fields gracefully (backward compatibility).

3. **Headless + CLI**
   - Add CLI arguments or simulation commands for save/load during headless runs.

4. **Testing**
   - Add `test_actions.py` verifying console/world side-effects.
   - Extend `test_save_load.py` for new fields & compatibility.

5. **Docs/Config**
   - Update README/Makefile docs if action usage changes.

## Acceptance Evidence
- `pytest -q school_sim/tests` passes with new action & save/load coverage.
- Headless run with save/load executes without errors.
- Final report captures new snapshot fields.
