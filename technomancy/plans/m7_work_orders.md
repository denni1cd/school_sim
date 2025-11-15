# Milestone M7 Work Orders

1. Curriculum engine module
   - Production target: `school_sim/curriculum.py`
   - Staging path: `technomancy/deliverables/src/school_sim/curriculum.py`
   - Actions: Implement track constants, `set_track`, `apply_classroom_modifiers`, helpers for captions/deltas.
   - Tests: `technomancy/deliverables/tests/test_curriculum_modifiers.py`

2. World integration & persistence
   - Production target: `school_sim/world.py`, `school_sim/bootstrap.py`, `school_sim/headless.py`
   - Staging paths: `technomancy/deliverables/src/school_sim/{world.py,bootstrap.py,headless.py}`
   - Actions: Accept curriculum config, apply modifiers during classroom ticks, expose `change_curriculum_track`, log snapshots & headless output with curriculum info.
   - Tests: `school_sim/tests/test_headless.py`, `school_sim/tests/test_save_load.py`

3. Office interaction & overlays
   - Production target: `school_sim/office.py`, `school_sim/events/scene_overlay.py`
   - Staging paths: `technomancy/deliverables/src/school_sim/{office.py,events/scene_overlay.py}`
   - Actions: Add curriculum cursor/activation, display next track, emit overlay via world event bus.
   - Tests: `technomancy/deliverables/tests/test_office_curriculum.py`, update `school_sim/tests/test_office_navigation.py` if needed.

4. Merge, scripts, and reports
   - Production target: `technomancy/deliverables/scripts/merge_m7.py`, `technomancy/logs/m7_staging_report.md`, `technomancy/logs/final_report_m7.md`.
   - Actions: Generate merge script, run conda-based pytest/make simulate/make run, document outcomes, ensure staging cleared post-merge.
