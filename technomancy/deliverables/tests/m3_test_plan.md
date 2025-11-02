# M3 Test Plan

## Save/Load Tests
- `test_m3_save_roundtrip` — Save world state to a temporary directory and reload into a new world; verify time and student needs match within tolerance.
- `test_m3_load_missing_file` — Attempt to load nonexistent path; expect graceful `FileNotFoundError` handling and no state change.
- `test_m3_load_invalid_schema` — Provide malformed JSON; loader should raise `ValueError`.

## Headless Logging Tests
- `test_m3_headless_log_length` — Run headless simulation for 300 ticks using deterministic seed; assert log file contains expected line count.
- `test_m3_headless_log_content` — Verify first and last lines include timestamps and student data.

## Command-Line Tests
- `test_m3_cli_load_flag` — Simulate `--load` argument to ensure game boots with specified save.
- `test_m3_cli_headless` — Ensure headless mode exit code zero and log created.

## Regression Tests
- Ensure existing M1/M2 suites still pass after persistence hooks added.
- Add coverage for edge cases (empty student list, multiple saves).
