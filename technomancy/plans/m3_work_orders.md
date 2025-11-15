# Milestone M3 Work Orders

## WO-1 Console & Action Inputs
- Update `principal_console.py` and input handling (renderer/main) to support save/load keys and ensure logging feedback.

## WO-2 Save System Expansion
- Extend `SaveSystem` to include world fields (`budget`, `rating`, policy/curriculum placeholders) per spec; ensure backwards compatibility.

## WO-3 Headless & Main Wiring
- Inject save system into world; enable save/load from headless run/console; ensure world references save system instance.

## WO-4 Tests/Docs
- Add `test_actions.py` and extend `test_save_load.py` to cover new fields; update README if control list changes.

## WO-5 Merge Script & Reporting
- Produce `merge_m3.py`, staging report, final report after verification.
