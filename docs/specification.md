# Technomancy Spec — School Simulation MVP (Engine-First, Placeholder Visuals)

**Repo root**: `school_sim/`  
**Python**: 3.12  
**Run targets**: `make run`, `make simulate`, `make test`  
**This spec is executable-as-instruction** for the Technomancy agent suite. It defines **deliverables**, **acceptance criteria**, **test obligations**, and the **exact file-level outputs** required to finish an MVP that integrates the existing code and adds event scenes with swappable images.

---

## 0) Roles (Technomancy)
- **Arch-Technomancer (Architect)** — Owns system boundaries, modules, and contracts. Produces/maintains this spec and enforces acceptance criteria.
- **High-Technomancer (Tech Lead)** — Plans tasks, creates interfaces, writes reference implementations, stubs tests. Ensures CI green.
- **Technomancers (Implementers)** — Build features to spec, keep code modular, write/extend **automated tests** for everything produced.

**All technomancers must ship automated tests for all created code.** No deliverable is complete without passing tests.

---

## 1) Project Scope (MVP you must finish)
1. **Engine-first school sim** with placeholder rectangles for rooms and circle markers for students.
2. **Student needs + schedule loop** (hunger, energy, stress, hygiene) with room-based effects.
3. **Timetable-driven movement**: homerooms map to room-by-time schedules.
4. **Event Scenes framework**: show **custom static images** (user-supplied) when an event triggers (e.g., “Fire Drill 10:30”, “Assembly 09:15”). Scenes are modal overlays; escape/enter closes.
5. **Config-driven content** in YAML for rooms, students, schedules, **and events**.
6. **Headless mode** for sim logging + **interactive mode** for visual debug.
7. **Principal Console (minimal)**: toggle overlay (`P`) to view time, student list, and trigger test events (placeholder).
8. **Save/Load (lightweight)**: dump/load sim state to `runtime/saves/` in JSON.
9. **Tests**: unit + smoke tests for loader, needs math, movement, and event dispatch.

**Out of scope (MVP)**: pathfinding between arbitrary waypoints, combat, inventory, story scripting, animation beyond basic movement, audio.

---

## 2) Current Code & Gaps to Close

### Present in repo
- `main.py` — Boots config -> world -> renderer; drives main loop.
- `renderer.py` — Pygame rectangles for rooms, circles for students, right-side debug panel.
- `student.py` — Needs model + decision loop scaffold.
- `world.py` — Time, updates, snapshot for UI.
- `room.py` — Room dataclass; **apply_effects** not implemented.
- `timetable.py` — Homeroom schedule mapping + time utilities.
- `configs/rooms.yaml`, `configs/students.yaml`, `configs/schedule.yaml` — Core content.
- Makefile + requirements + docs.

### Confirmed missing/incomplete (must implement)
- `Room.apply_effects(...)` — apply room-type deltas to needs.
- Student decision loop edge-cases (stay/leave logic) and hygiene path.
- **Event system** (config, dispatch, and scene overlay).
- **Principal console** minimal overlay & test-event trigger.
- **Save/Load** (JSON) and corresponding tests.
- Tests for all new modules; smoke test for headless loop.

---

## 3) Target Architecture (modules & contracts)

```
school_sim/
  events/
    __init__.py
    event_models.py         # dataclasses + validation
    event_loader.py         # read configs/events.yaml -> List[Event]
    event_bus.py            # subscribe/emit; World publishes, Scenes/UI consume
    event_rules.py          # time/room/need-based triggers
    scene_overlay.py        # pygame overlay that renders an image & caption
  runtime/
    saves/                  # JSON save files
    scenes/                 # user images (png/jpg); file names referenced by events.yaml
    logs/                   # simulation logs (optional, text)
  configs/
    rooms.yaml
    students.yaml
    schedule.yaml
    events.yaml             # NEW: sceneable events (see format below)
```

### 3.1 Events data model
- **Event**: `{ id: str, when: "HH:MM" | null, room: str | null, condition: str | null, scene: { image: str, caption: str } | null, once: bool }`
- **Condition mini-language** (simple): supports `needs.<name> [><= >= ==] <number>` and `student in <homeroom>`; boolean `and/or` only.
- **Examples** in `configs/events.yaml`:
```yaml
- id: "assembly_0900"
  when: "09:00"
  room: "ClassroomA"
  scene:
    image: "assembly.png"
    caption: "Morning assembly in the gym."
  once: true

- id: "fire_drill"
  when: "10:30"
  scene:
    image: "fire_drill.jpg"
    caption: "Fire drill! All students exit."
  once: true
```

### 3.2 Event Bus contract
- `EventBus.subscribe(topic: str, callback: Callable)`
- `EventBus.emit(topic: str, payload: dict)`
- Topics: `"time_tick"`, `"room_enter"`, `"room_exit"`, `"needs_update"`, `"event_fired"`

### 3.3 Scene overlay contract
- `SceneOverlay.show(image_path: str, caption: str) -> None`
- `SceneOverlay.hide() -> None`
- Non-blocking; overlay draws each frame if active. ESC/ENTER hides.

---

## 4) Game Loop Contract

**Tick** = 30 in-game seconds (configurable).  
Per tick, in order:
1. Read input (pygame) and console toggles.
2. Advance **World.time_minutes**.
3. For each student:
   - Determine **target room** (schedule vs. immediate need recovery).
   - Move toward target (speed px/min).
   - Apply **Room.apply_effects** for time spent in current room.
   - Publish `"needs_update"`, `"room_enter/exit"` as needed.
4. Event rules evaluate (time-based & condition-based). Fire scenes via `EventBus`.
5. Renderer draws rooms, students, panel, then scene overlay if active.
6. If headless: write snapshot logs to `runtime/logs/`.

---

## 5) Needs & Effects (MVP numbers)

All rates are **per minute**; implement with clamped 0–100.

- **Base decay** (everywhere):
  - hunger `+0.5`
  - stress `+0.2`
  - energy `-0.4`
  - hygiene `-0.2`

- **Room effects** (additive deltas applied in `Room.apply_effects`):
  - cafeteria: hunger `-1.2` (min 0)
  - dorm: energy `+1.6`
  - lounge: stress `-1.0`
  - bathroom: hygiene `+2.0`
  - classroom: stress `+0.6`; (optional future: knowledge `+0.5`)

- **Critical thresholds & behaviors**:
  - If **hunger ≥ 85** → override target to cafeteria until `hunger ≤ 40`.
  - If **energy ≤ 25** → override to dorm until `energy ≥ 50`.
  - If **hygiene ≤ 30** → override to bathroom until `hygiene ≥ 60`.
  - If **stress ≥ 90** → override to lounge until `stress ≤ 50`.
  - Overrides beat timetable until cleared.

---

## 6) YAML Config Formats

### 6.1 `configs/rooms.yaml`
Already present. No changes required for MVP.

### 6.2 `configs/students.yaml`
Add defaults for speed (px/min) and initial needs (optional), e.g.:
```yaml
students:
  - name: "Alice"
    homeroom: "homeroom_A"
    current_room: "DormA"
    speed: 120
    needs:
      hunger: 30
      energy: 80
      stress: 20
      hygiene: 80
```

### 6.3 `configs/schedule.yaml`
Already present. Timetable keys `"HH:MM"` → room name.

### 6.4 `configs/events.yaml` (NEW)
See §3.1 example. Scenes refer to files in `runtime/scenes/`.

---

## 7) Principal Console (MVP)
- Key `P`: toggle right-panel overlay section “Console”.
- Console actions:
  - `T`: advance 15 minutes (debug).
  - `E`: trigger first event in `events.yaml` (debug).
  - `B`: placeholder “campus broadcast” (no effect, log only).

---

## 8) Save/Load

- **Save**: `runtime/saves/save_YYYYMMDD_HHMM.json` with:
  ```json
  {
    "time_minutes": int,
    "students": [{"name": str, "room": str, "needs": {"hunger":0,"energy":0,"stress":0,"hygiene":0}, "target": str}]
  }
  ```
- **Load**: optional CLI `--load path` or key `L` in debug to load most recent.

---

## 9) Tests (required to ship)

1. `tests/test_needs_math.py` — base decay + room effects produce expected values after N minutes.
2. `tests/test_schedule_targeting.py` — timetable vs. overrides precedence.
3. `tests/test_event_rules.py` — time-based & condition triggers; `once: true` respected.
4. `tests/test_save_load.py` — round-trip equality for time + students (subset).
5. `tests/test_loader.py` — rooms/students/schedule/events YAML parse.

`make test` must pass.

---

## 10) Deliverables → Acceptance Criteria (1:1 mapping)

| Deliverable | Files / Modules | Acceptance Criteria |
|---|---|---|
| D1. Room Effects | `room.py` | `Room.apply_effects` implements §5 exactly; unit tests green. |
| D2. Needs Overrides | `student.py` | Students override timetable when critical; tests prove thresholds. |
| D3. Event System | `events/*`, `configs/events.yaml` | Time + condition triggers; emits `event_fired`; scene overlay displays supplied image/caption; ESC/ENTER hides. |
| D4. Principal Console | `renderer.py` additions | `P` toggles console; `T/E/B` keys behave as defined; visible overlay text. |
| D5. Save/Load | `runtime/saves/*`, loader funcs | Save & load work; test verifies round-trip subset equivalence. |
| D6. Headless Logs | `make simulate` path | 300 ticks produce a text log with snapshots including time + student states. |
| D7. Tests | `tests/*` | All tests pass in CI; coverage includes new modules. |

**Definition of Done**: All D1–D7 acceptance criteria satisfied, `make run` and `make simulate` both work without errors for 10 minutes of real time, and no failing tests.

---

## 11) Work Plan (Sequenced)

1. **D1 Room Effects** → implement + tests.
2. **D2 Needs Overrides** → finalize student decision logic + tests.
3. **D3 Event System** → add `events/` modules, loader, bus, rules; write tests.
4. **D3 Scene Overlay** → image rendering; connect to bus.
5. **D4 Principal Console** → small overlay with debug actions.
6. **D5 Save/Load** → JSON round-trip + tests.
7. **D6 Headless Logs** → deterministic log structure.
8. **D7 Test hardening** → finalize unit/smoke tests.

---

## 12) Runbook

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Interactive
make run

# Headless
make simulate

# Tests
make test
```

---

## 13) Risks & Honest Assessment

- **Feasible for an MVP** in a focused push using the above plan. The current codebase is close: rendering, world loop, config loading, and timetable exist.
- The **new Event/Scene** system, **save/load**, and **test suite** are fresh work but straight-forward given Pygame + YAML.
- “Finish it all in one go” is realistic **for MVP D1–D7**; anything beyond (pathfinding, complex AI, animations, content authoring tools) would exceed a single burst.
- Graphics remain placeholder by design; swapping to real assets later is low-risk due to the overlay and rectangle-first approach.

---

## 14) Appendix — Example `configs/events.yaml`

```yaml
- id: "welcome_assembly"
  when: "08:15"
  scene:
    image: "welcome.png"
    caption: "Welcome assembly in the gym."
  once: true

- id: "alice_too_hungry"
  condition: "student in homeroom_A and needs.hunger >= 85"
  scene:
    image: "snack_break.jpg"
    caption: "Alice needs a snack break."
  once: false
```