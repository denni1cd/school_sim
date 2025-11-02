# M1 Room Effects Design

## Goals
- Implement `Room.apply_effects` so each room type contributes deterministic deltas to student needs every simulation tick.
- Reserve hook points for future room modifiers without breaking the current data contract.
- Maintain separation between configuration parsing and runtime effect application.

## Architectural Directives
- Keep `Room` as a lightweight data class. Derive effects from the room configuration payload and cache them on initialization.
- Accept a `Student` instance and elapsed minutes in `apply_effects`. Never mutate unrelated fields; update only needs defined in the configuration.
- Normalize effect deltas per minute. Multiply per-minute effects by elapsed minutes so headless and interactive loops stay consistent.
- Clamp needs between 0 and 100 after applying effects to prevent runaway values and keep thresholds meaningful.
- Return a structured summary (e.g., dict mapping need name to net delta) so tests and logs can verify changes without re-reading the student object.
- Log no output from `apply_effects`; allow the World or Event system to decide when to broadcast changes.

## Integration Notes
- Call `Room.apply_effects` from the world update loop after students are located in their current rooms.
- When a room configuration omits a need, assume delta 0 for that need.
- Handle optional hygiene entries to support shower rooms without requiring all rooms to define hygiene effects.

## Test Hooks
- Provide a pure function shape so tests can instantiate `Room` with synthetic config and `Student` with controlled needs.
- Expose clamp logic via helper method or inline but ensure tests can observe both clamped and unclamped results by reading returned delta summary.

## Open Questions
- None identified; defaults derived from YAML should be adequate for MVP.
