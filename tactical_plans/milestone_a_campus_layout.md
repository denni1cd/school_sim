# Tactical Plan — Milestone A: Campus Layout & Navigation

## Objective
Deliver a realistic boarding school map with complete navigation metadata so students and staff can traverse all required rooms without collisions while preserving placeholder art hooks.

## Preconditions
- Existing MakerLab/baseline maps and `MapGrid` loading pipeline compile and pass tests.
- Tile editing tool (Tiled 1.10+) available with repo's tileset placeholders (`data/tilesets/placeholder.tsx`).
- Current collision masks and spawn configuration understood (`data/maps/*.tmx`, `config/rooms/*.yaml`).

## Implementation Steps
1. **Room & Traffic Blueprint (Product Lead, Content Designer)**
   - List mandatory rooms with capacities: dormitories (north/south wings), classrooms (STEM, humanities, arts), cafeteria, kitchen, library, gym, infirmary, offices, courtyard.
   - Document main traffic flows (e.g., dorm → cafeteria at breakfast) and note potential choke points.
   - Capture blueprint in `docs/campus_layout_notes.md` for future art reference.

2. **Tile Map Construction (Content Designer)**
   - Duplicate `data/maps/baseline.tmx` → `data/maps/campus_v1.tmx`.
   - In Tiled, create layers:
     - `Ground`, `Decor`, `Collision`, `RoomBounds`, `SpawnPoints`, `Waypoints` (for guiding pathfinding).
     - Use placeholder tiles but label each room with text objects on `RoomLabels` layer for clarity.
   - Lay out corridors at least 3 tiles wide to reduce congestion; ensure stairs/elevators (if any) represented via `Waypoints` objects linking floors.
   - Export map and verify no missing tileset references (should point to `data/tilesets/placeholder.tsx`).

3. **Room Metadata Definition (Content Designer, Gameplay Engineer)**
   - Create `config/rooms/campus_v1.yaml` with entries per room, e.g.:
     ```yaml
     dorm_north_a:
       display_name: "North Dorm A"
       room_type: Dormitory
       floor: 1
       capacity: 12
       default_activity: Sleeping
       spawn_points:
         - {x: 5, y: 12}
         - {x: 6, y: 12}
     ```
   - Include metadata for transitions (stairs/elevators) using `links` arrays referencing other rooms for cross-floor navigation.
   - Ensure naming scheme matches `RoomBounds` object names in TMX file.

4. **Navigation Graph Extension (Gameplay Engineer)**
   - Update `game/navigation/map_graph.py`:
     - Load `Waypoints` objects and convert to graph nodes.
     - Extend `MapGraph.build_from_tmx` to interpret `links` from YAML as bidirectional edges.
     - Cache pathfinding grids per floor to avoid recomputation; reuse `MapGrid.room_for_position` for node classification.
   - Add docstring describing new waypoint semantics.

5. **Spawn & Entrance Hooks (Gameplay Engineer)**
   - Update `game/world/spawn_manager.py` to read spawn points from `config/rooms/campus_v1.yaml` by role (`Student`, `Staff`).
   - Ensure fallback spawn exists (`admin_office_entry`) and add assertion if config missing.

6. **Placeholder Asset Audit (Content Designer)**
   - Confirm each new room has placeholder sprites/labels referenced in `data/placeholders/README.md`.
   - Add TODO markers for future art replacements without blocking build.

7. **Integration Wiring (Engineering Lead)**
   - Modify map selection in `game/bootstrap.py` to load `campus_v1` when milestone flag `--map campus_v1` provided.
   - Update CLI docs in `readme.md` to mention new map option.

8. **Automated Tests (QA Lead)**
   - Add `tests/maps/test_campus_v1.py` covering:
     - All rooms resolve from `MapGrid.room_for_position`.
     - Paths exist between core routes (dorm → cafeteria, cafeteria → classrooms, classrooms → library, dorm → infirmary).
   - Run `pytest tests/maps/test_campus_v1.py` and ensure green.

9. **Simulation Smoke Validation (QA Lead)**
   - Execute `python -m game.simulation --map campus_v1 --ticks 2400` and confirm NPCs reach classrooms and cafeteria without being stuck.
   - Capture screenshots/logs for documentation.

## Deliverables
- `data/maps/campus_v1.tmx` with documented layers and labels.
- `config/rooms/campus_v1.yaml` capturing capacities, default activities, and transitions.
- Navigation/spawn manager updates enabling traversal across the new layout.
- Test suite additions ensuring map integrity.

## Acceptance Criteria
- Simulation loads `campus_v1` without runtime errors.
- Every required room is reachable from every dormitory via pathfinding.
- Spawn points are role-aware and place NPCs inside valid room bounds.
- Tests and smoke simulation complete successfully.
