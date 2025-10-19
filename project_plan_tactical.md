# Project Plan — Tactical (Per Milestone)

## Phase 1 — Placeholder Map & PC Movement (Headless)
- Validate config, map load, clock, PC bounds/collisions.

## Phase 2 — NPC Scheduling
- Load activities & schedules; trigger at times; start with teleport then walking.

## Phase 3 — Autonomous Movement
- A* paths; step movement; arrival -> perform task; variability.

## Phase 4 — Integration & Extensibility
- Add room+NPC with no refactor; stub interact; docs updated.

|5|Data Swap Stress Test|config,data|test_extensibility_data|MakerLab loads via config|
|6|Room Metadata & Doors|data,map,render|test_map,test_simulation|Door metadata drives targets|
|7|Config Profiles|config,cli|test_config_profiles|Profiles selectable via flags|
|8|Contextual Interactions|simulation,config|test_interactions|Room/activity aware messages|

