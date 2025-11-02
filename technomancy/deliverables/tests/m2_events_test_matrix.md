# M2 Events Test Matrix

## Event Loader Tests
- Load valid `configs/events.yaml` with multiple events; assert dataclass attributes.
- Reject missing required keys (`id`, `scene.image` when `scene` present).
- Validate time format parsing (`HH:MM`) and provide descriptive errors for misformatted strings.

## Event Rules Tests
- Time-triggered event fires exactly at scheduled tick and respects `once: true`.
- Condition expression `needs.hunger >= 85 and student in homeroom_A` evaluates correctly.
- Room-specific events only trigger when the student is present in the target room.
- Ensure events do not fire twice when `once` is `true` even if conditions persist.

## Event Bus Tests
- Subscription and synchronous callback execution for each topic.
- Emitting `event_fired` passes the expected payload to subscribers (scene data, event id).

## Scene Overlay Tests
- `show()` stores paths and marks overlay active.
- `hide()` resets state and clears caption.
- Simulated ESC/ENTER input hides active overlay without affecting base renderer.

## Principal Console Tests
- Key `P` toggles visibility.
- Key `T` advances time by 15 minutes and logs the action.
- Key `E` triggers the first event through the event bus.
- Key `B` writes a placeholder broadcast entry.

## Integration Smoke
- Compose loader, bus, rules, and overlay; feed synthetic world ticks to assert combined flow results in overlay activation.
