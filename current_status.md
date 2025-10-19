# Current Status (as of latest milestone)

## Milestones Achieved
- **Milestone 8** complete: interaction text now reflects room/activity context via configurable message templates.
- Milestones 0-7 remain satisfied (movement, scheduling, extensibility, profiles, door metadata, etc.).

## Systems Snapshot
- Config loader merges `config/interactions.yaml` so simulations read room/role/activity message templates.
- Simulation prefers activity-specific phrases, falls back to room or role cues, then default placeholders, primes everyone for their first activity so movement happens in parallel, and adjusts activity countdowns based on actual arrival time.
- Baseline and MakerLab maps restored to the pre-experiment layout (open interior rooms with perimeter walls); hallway/door refactor was rolled back after pathfinding and collision regressions.
- `MapGrid.room_for_position` supports locating NPCs for messaging and future spatial logic.
- Interaction regression tests cover library and MakerLab scenarios; MakerLab profile continues to validate extensibility flow.
- Pygame client automatically displays the richer text when pressing `E` near NPCs—no UI changes required.

## Outstanding Notes / Issues Observed
- Hallway-only room layout broke several assumptions (room walkability, spawn locations, pathfinding tests). A future redesign needs a tighter plan for door tiles, spawn points, and updated tests before swapping the map.
- Messages remain plain text; consider richer formatting/localization plus per-profile overrides so new scenarios can customize tone.
- Room lookup is a full scan; caching or spatial indexing would help once maps grow.

## Next Steps Suggestions
1. Add CLI/docs to highlight available interaction contexts and how to update message templates.
2. Explore lightweight dialogue variables (time of day, player state) to make placeholders livelier.
3. Prototype a hallway-based map in a branch with dedicated tests for walkability, spawn logic, and NPC routing before replacing the baseline layout.
