# School Simulation Engine — Next-Level Project Plan

## Vision
Create a realistic boarding school simulation where students follow daily routines across a believable campus map while the player, acting as the principal, manages operations. Placeholder assets will continue to stand in for eventual art and audio so engine development remains fast and testable.

## Objectives for This Level
1. **Campus Realism:** Design a single, fully traversable boarding school map that includes core facilities (dormitories, classrooms, cafeteria, courtyard, offices) with placeholder tiles and clear labels for later asset swaps.
2. **Daily Scheduling System:** Expand the scheduling engine so each student (NPC) follows a complete day/night cycle with classes, meals, study hall, recreation, and sleep.
3. **Activity Awareness:** Ensure the engine can describe and track what every NPC is doing in each room, exposing this context to UI and tooling hooks.
4. **Player Interaction Hooks:** Keep the principal’s management viewpoint in mind by exposing schedule overrides, attendance monitoring, and alerts through engine APIs (UI stubs only).
5. **Extensibility:** Maintain object-oriented design principles so new roles, rooms, and activity types can be added with minimal code changes.

## Scope
- **In Scope:**
  - Tile map design, navigation graph updates, and room metadata for the new campus layout.
  - NPC schedule generation, including configurable templates and per-student variation.
  - Activity definitions with durations, prerequisites, and room affinity rules.
  - Placeholder sprites/tiles and interaction text updates to cover new rooms and activities.
  - Engine-level player tools (APIs/events) to manage schedules and respond to issues.
  - Automated tests covering pathfinding, scheduling, and activity reporting.
- **Out of Scope (for this level):**
  - Final art/audio assets.
  - Complex AI decision-making beyond deterministic schedules plus simple contingencies.
  - Multiplayer or network features.
  - Economic/financial simulation systems.

## Assumptions
- The existing codebase (Milestone 8) is stable and continues to provide baseline movement, interaction text, and schedule seeding.
- Placeholder art remains sufficient for all new map locations.
- All work will target Python 3.12 and existing tooling (pytest, Pygame client, CLI simulation).

## High-Level Approach
1. **Map Upgrade:**
   - Gather requirements for rooms and traffic patterns.
   - Prototype layout in Tiled (or equivalent) with placeholder tiles.
   - Update map loader, collision layers, and room metadata.
2. **Schedule Framework:**
   - Define daily templates for student archetypes (e.g., freshman, senior, athlete).
   - Implement schedule generation that respects class assignments, meal slots, and curfew.
   - Integrate with existing movement/pathfinding to ensure punctual arrivals.
3. **Activity System Enhancements:**
   - Expand activity definitions to include state metadata (e.g., "Sleeping", "Eating").
   - Connect room occupancy to activity reporting for UI/analytics.
   - Support event hooks when activities start/end or fail (e.g., late arrival).
4. **Player Management Hooks:**
   - Provide API endpoints or commands to adjust schedules, trigger inspections, or respond to incidents.
   - Add logging/notifications for key events (missed classes, overcrowded rooms).
5. **Testing & QA:**
   - Extend regression tests to cover new schedules, pathfinding edges, and activity reporting.
   - Use simulations to validate day/night cycles and ensure no deadlocks or overlaps.

## Milestones Overview
1. **Milestone A — Campus Layout & Navigation:** Deliver the new map, navigation data, and room metadata.
2. **Milestone B — Comprehensive Scheduling:** Implement daily schedules with variation, conflict resolution, and testing.
3. **Milestone C — Activity Tracking & Reporting:** Tie schedules to activity states, expose reporting hooks, and update placeholders.
4. **Milestone D — Player Management Hooks:** Provide tools for the principal to monitor and intervene, backed by automated alerts.
5. **Milestone E — QA & Polish:** Stabilize, document, and prepare for future graphics integration.

## Success Criteria
- All students follow believable daily routines across the campus without collisions or schedule deadlocks.
- Each room reports the current activity context, accessible through engine APIs and placeholder UI.
- Player management hooks allow manual schedule adjustments and provide visibility into student behavior.
- Automated test suite covers the new systems and runs cleanly.

## Risks & Mitigations
- **Pathfinding Complexity:** Larger maps can increase pathfinding load. *Mitigation:* Profile routes, cache navigation meshes, and introduce hallway waypoints.
- **Schedule Conflicts:** Overlapping room usage may cause overcrowding. *Mitigation:* Implement capacity checks and staggered schedules.
- **State Explosion:** Activity metadata may become unwieldy. *Mitigation:* Keep activity classes modular with clear inheritance and configuration-driven behavior.
- **Player Overload:** Too many alerts could overwhelm the principal role. *Mitigation:* Prioritize notifications and allow filtering.

## Dependencies
- Existing map loading and schedule engine components.
- Placeholder art pipeline.
- YAML/JSON configuration loaders for schedules and interactions.

## Deliverables
- Updated campus map assets and metadata files.
- Code modules handling schedule generation and activity tracking.
- Documentation outlining new APIs and configuration formats.
- Expanded automated test coverage.
- Per-milestone tactical plans capturing step-by-step execution details (`tactical_plans/`).

## Milestone Progression
- **Milestone A — Campus Layout & Navigation:** Establish the foundational map and navigation data before layering on systemic changes.
- **Milestone B — Comprehensive Scheduling:** Build on the new map with robust day/night schedules that drive believable behavior.
- **Milestone C — Activity Tracking & Reporting:** Connect schedules to activity state, giving clear visibility into what happens in each room.
- **Milestone D — Player Management Hooks:** Add principal-facing controls and feedback loops on top of the activity system.
- **Milestone E — QA & Polish:** Harden, document, and prepare the engine for future visual upgrades once the core systems prove stable.

## Measurement & Metrics
- Simulation runs without blocking errors for at least three consecutive in-game days.
- Average pathfinding resolution under target threshold (<50 ms per decision).
- Automated tests pass with >90% coverage on new scheduling/activity modules.
- Player hook interactions (e.g., schedule override) succeed in >95% test cases.

