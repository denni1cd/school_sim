# M2 Event System Design

## Overview
Implement the event framework mandated by the specification, ensuring time, room, and conditional triggers generate scenes and console actions without blocking the simulation loop.

## Components
- `events/event_models.py`: dataclasses for `Event` with validation helpers converting YAML payloads into strongly typed instances.
- `events/event_loader.py`: loader that reads `configs/events.yaml`, validates schema, and returns lists of events keyed by identifiers.
- `events/event_bus.py`: lightweight publish/subscribe system with topic strings (`time_tick`, `room_enter`, `room_exit`, `needs_update`, `event_fired`) and synchronous callback invocation.
- `events/event_rules.py`: evaluator that inspects world snapshots, checks time windows, room matches, and parsed condition expressions using a simple boolean AST.
- `events/scene_overlay.py`: overlay manager owning Pygame surfaces for image display, caption text rendering, and keyboard dismissal.

## Data Flow
1. `main.py` loads events via the loader and registers rule evaluators with `World`.
2. `World` emits `time_tick` and room transitions through `EventBus`.
3. `event_rules` listens to relevant topics, evaluates conditions, and emits `event_fired` when criteria succeed.
4. `scene_overlay` subscribes to `event_fired`, loads the referenced image from `runtime/scenes/`, and toggles display state until ESC or ENTER is pressed.
5. `renderer` integrates overlay draw calls after base map rendering and updates the Principal Console when toggled.

## Principal Console Integration
- Add console state to `renderer` with toggle key `P`.
- Handle `T`, `E`, and `B` keys when console is active: advance time by publishing debug events, manually emit the first configured event, and log broadcast messages respectively.
- Present console data (current time, student summary) in a distinct panel region.

## Error Handling
- Gracefully handle missing event images by logging warnings and skipping overlay display while still marking events as fired.
- Provide guardrails for malformed conditions by raising explicit exceptions during loader validation.

## Testing Strategy
- Unit tests for loader (valid and invalid YAML).
- Rule evaluation tests verifying time-based and conditional triggers, including `once: true` semantics.
- Scene overlay tests using Pygame surface stubs to confirm show/hide behavior responds to `event_fired` and keyboard input.
- Principal Console tests simulating key events to ensure toggles and debug actions work.
