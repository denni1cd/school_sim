# Milestone 2: First Playable Simulation Loop

School_Sim Project Plan (for Codex integration)

## Goal of this milestone

By the end of this milestone, you should be able to run `main.py` and watch several students move around a simple school layout (rectangles/placeholders), following schedules, satisfying needs (like hunger/energy), and occasionally skipping class if a need is critical.

No real art. No teachers. No punishment logic, except for tracking "you skipped class."
This gives us our first emergent story engine.

---

## High-level tasks

1. Create/clean core modules:

   * `world.py`
   * `student.py`
   * `room.py`
   * `timetable.py`
   * `main.py`
2. Create config data under `configs/`

   * `configs/rooms.yaml`
   * `configs/students.yaml`
   * `configs/schedule.yaml`
3. Implement the simulation loop:

   * Global clock
   * Need decay
   * Student decision-making (follow class vs fix urgent need)
   * Movement between rooms
   * Room effects on needs
4. Draw a debug view:

   * Render rectangles for rooms and circles for students
   * Text overlay with current goal and needs
5. Log attendance / discipline tally.

Below is the breakdown Codex should follow, file by file.

---

## 1. `room.py`

**Purpose:** Define rooms/locations in the school and what they do for a student.

**Create or update this file so it contains:**

```python
from dataclasses import dataclass

@dataclass
class Room:
    name: str
    room_type: str  # "classroom", "cafeteria", "dorm", "bathroom", "lounge"
    x: int
    y: int
    width: int
    height: int

    def apply_effects(self, student, minutes: float):
        """
        Apply the passive effects of being in this room for `minutes` minutes.
        Example rules for Milestone 2:
        - cafeteria: hunger goes down
        - dorm: energy goes up
        - classroom: stress goes up, knowledge goes up
        - lounge: stress goes down
        - bathroom: hygiene goes up
        """
        if self.room_type == "cafeteria":
            student.needs["hunger"] = max(0, student.needs["hunger"] - 0.8 * minutes)
        elif self.room_type == "dorm":
            student.needs["energy"] = min(100, student.needs["energy"] + 0.6 * minutes)
        elif self.room_type == "classroom":
            student.needs["stress"] = min(100, student.needs["stress"] + 0.4 * minutes)
            student.stats["knowledge"] += 0.5 * minutes
        elif self.room_type == "lounge":
            student.needs["stress"] = max(0, student.needs["stress"] - 0.7 * minutes)
            student.needs["social"] = min(100, student.needs["social"] + 0.4 * minutes)
        elif self.room_type == "bathroom":
            student.needs["hygiene"] = min(100, student.needs["hygiene"] + 1.0 * minutes)
```

**Codex action:**

* If `room.py` already exists, replace its contents with the code above (do a full overwrite instead of partial patch so we stay in sync).

---

## 2. `student.py`

**Purpose:** A student with needs, schedule, and behavior logic.

**Create or update this file so it contains:**

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

CRITICAL_HUNGER = 85
CRITICAL_ENERGY = 20
CRITICAL_HYGIENE = 25
CRITICAL_STRESS = 90

@dataclass
class Student:
    name: str
    homeroom: str  # e.g. "homeroom_A" - used to look up schedule
    current_room: str  # name of the room they're currently in
    target_room: Optional[str] = None  # where they're walking to
    attendance_record: Dict[str, bool] = field(default_factory=dict)
    stats: Dict[str, float] = field(default_factory=lambda: {
        "knowledge": 0.0,
        "discipline_risk": 0.0,
    })
    needs: Dict[str, float] = field(default_factory=lambda: {
        "hunger": 30.0,   # 0 = full, 100 = starving
        "energy": 80.0,   # 0 = exhausted, 100 = fully rested
        "hygiene": 60.0,  # 0 = filthy, 100 = clean
        "stress": 20.0,   # 0 = calm, 100 = meltdown
        "social": 50.0,   # 0 = lonely, 100 = very fulfilled
    })

    def decay_needs(self, minutes: float):
        """Needs naturally drift over time."""
        self.needs["hunger"] = min(100, self.needs["hunger"] + 0.5 * minutes)
        self.needs["energy"] = max(0,   self.needs["energy"] - 0.4 * minutes)
        self.needs["hygiene"] = max(0,  self.needs["hygiene"] - 0.2 * minutes)
        self.needs["stress"] = min(100, self.needs["stress"] + 0.2 * minutes)
        self.needs["social"] = max(0,   self.needs["social"] - 0.1 * minutes)

    def choose_target(self, world_time_str: str, schedule: Dict[str, str], rooms: Dict[str, Any]):
        """
        Decide where to go next.
        1. Check for crisis needs (cafeteria, dorm, bathroom, lounge).
        2. Otherwise follow schedule for this time slot.
        """
        # Crisis overrides schedule
        if self.needs["hunger"] >= CRITICAL_HUNGER:
            self.target_room = self.find_room_by_type("cafeteria", rooms)
            return
        if self.needs["energy"] <= CRITICAL_ENERGY:
            self.target_room = self.find_room_by_type("dorm", rooms)
            return
        if self.needs["hygiene"] <= CRITICAL_HYGIENE:
            self.target_room = self.find_room_by_type("bathroom", rooms)
            return
        if self.needs["stress"] >= CRITICAL_STRESS:
            self.target_room = self.find_room_by_type("lounge", rooms)
            return

        # Otherwise follow assigned schedule
        if world_time_str in schedule:
            self.target_room = schedule[world_time_str]
        else:
            # unscheduled time -> socialize
            self.target_room = self.find_room_by_type("lounge", rooms)

    def find_room_by_type(self, room_type: str, rooms: Dict[str, Any]) -> Optional[str]:
        for room_name, room in rooms.items():
            if room.room_type == room_type:
                return room_name
        return None

    def move_towards_target(self):
        """
        Milestone 2 behavior: snap instantly to target.
        (Pathfinding / gradual walking comes in Milestone 3.)
        """
        if self.target_room is not None:
            self.current_room = self.target_room

    def record_attendance(self, world_time_str: str, expected_room: Optional[str]):
        """
        Track if she's skipping what she 'should' be doing.
        This is the seed for discipline/enforcement systems.
        """
        in_class_when_she_should_be = (
            expected_room is not None
            and expected_room == self.current_room
        )
        self.attendance_record[world_time_str] = in_class_when_she_should_be
        if not in_class_when_she_should_be and expected_room is not None:
            # She's skipping. Nudge discipline risk up.
            self.stats["discipline_risk"] += 1.0
```

**Codex action:**

* Overwrite `student.py` with that full content.

---

## 3. `timetable.py`

**Purpose:** Timekeeping + looking up “what class should you be in now.”

**Create or update this file so it contains:**

```python
from typing import Dict, Optional, Tuple

def minutes_to_timestr(total_minutes: int) -> str:
    """480 -> '08:00'."""
    hours = total_minutes // 60
    mins = total_minutes % 60
    return f"{hours:02d}:{mins:02d}"

class Timetable:
    """
    Holds:
    - per-homeroom schedules (like homeroom_A)
    - global school periods, etc.
    """

    def __init__(self, homeroom_schedules: Dict[str, Dict[str, str]]):
        # homeroom_schedules["homeroom_A"]["08:00"] = "MathClassA"
        self.homeroom_schedules = homeroom_schedules

    def expected_room_for(self, homeroom: str, timestr: str) -> Optional[str]:
        schedule = self.homeroom_schedules.get(homeroom, {})
        return schedule.get(timestr)
```

**Codex action:**

* Add this file if missing.
* If file exists, overwrite.

Note: For now we assume classes are hour-aligned, like `"08:00"`, `"09:00"`. Minute-by-minute granularity comes later.

---

## 4. `world.py`

**Purpose:** Owns students, rooms, and global time. Runs one simulation "tick."

**Create or update this file so it contains:**

```python
from typing import Dict, List
from room import Room
from student import Student
from timetable import Timetable, minutes_to_timestr

class World:
    def __init__(self, rooms: Dict[str, Room], students: List[Student], timetable: Timetable):
        self.rooms = rooms
        self.students = students
        self.timetable = timetable
        self.time_minutes = 8 * 60  # start at 08:00

    def tick(self, dt_minutes: int = 1):
        """Advance world by dt_minutes."""
        self.time_minutes += dt_minutes
        timestr = minutes_to_timestr(self.time_minutes)

        for s in self.students:
            # 1. Passive need decay
            s.decay_needs(dt_minutes)

            # 2. Decide where to go
            homeroom_schedule = self.timetable.homeroom_schedules.get(s.homeroom, {})
            s.choose_target(timestr, homeroom_schedule, self.rooms)

            # 3. Move to the target (instant in Milestone 2)
            s.move_towards_target()

            # 4. Apply room effects
            current_room_obj = self.rooms.get(s.current_room)
            if current_room_obj:
                current_room_obj.apply_effects(s, dt_minutes)

            # 5. Record attendance / discipline tracking
            expected = self.timetable.expected_room_for(s.homeroom, timestr)
            s.record_attendance(timestr, expected)

    def get_debug_snapshot(self):
        """Return lightweight info for rendering / console log."""
        timestr = minutes_to_timestr(self.time_minutes)
        data = {
            "time": timestr,
            "students": []
        }
        for s in self.students:
            data["students"].append({
                "name": s.name,
                "room": s.current_room,
                "target": s.target_room,
                "needs": s.needs.copy(),
                "discipline_risk": s.stats["discipline_risk"],
            })
        return data
```

**Codex action:**

* Overwrite `world.py`.

---

## 5. `configs/` data files

Create a new folder called `configs` if it does not exist.

### `configs/rooms.yaml`

This defines the spaces in the school and also their 2D placeholder layout for rendering.

```yaml
rooms:
  ClassroomA:
    room_type: "classroom"
    x: 50
    y: 50
    width: 200
    height: 120

  Cafeteria:
    room_type: "cafeteria"
    x: 300
    y: 50
    width: 200
    height: 120

  DormA:
    room_type: "dorm"
    x: 50
    y: 200
    width: 200
    height: 120

  Lounge:
    room_type: "lounge"
    x: 300
    y: 200
    width: 200
    height: 120

  BathroomA:
    room_type: "bathroom"
    x: 550
    y: 50
    width: 100
    height: 80
```

### `configs/schedule.yaml`

Homeroom schedules (hour-aligned). Keys must match the student's `homeroom`.

```yaml
homeroom_A:
  "08:00": "ClassroomA"
  "09:00": "ClassroomA"
  "10:00": "ClassroomA"
  "11:00": "Cafeteria"

homeroom_B:
  "08:00": "ClassroomA"
  "09:00": "ClassroomA"
  "10:00": "Lounge"
  "11:00": "Cafeteria"
```

### `configs/students.yaml`

Initial student roster.

```yaml
students:
  - name: "Alice"
    homeroom: "homeroom_A"
    current_room: "DormA"

  - name: "Becca"
    homeroom: "homeroom_A"
    current_room: "DormA"

  - name: "Chloe"
    homeroom: "homeroom_B"
    current_room: "DormA"
```

**Codex action:**

* Create directory `configs/`.
* Add the 3 YAML files above.

---

## 6. `main.py`

**Purpose:** Glue everything together. This file:

1. Loads configs.
2. Builds Room, Student, Timetable, World.
3. Runs a loop (text or pygame).
4. Renders debug view.

For Milestone 2 we accept either:

* pure console print every tick, OR
* pygame rectangles + text.

If you already have pygame set up in this repo, keep it and update to match below.
If you do NOT have pygame yet, do console mode for now (Codex: pick one and commit to it — do not try to do both).

### Version A: console main loop (fallback / guaranteed to run)

```python
import time
import yaml
from room import Room
from student import Student
from timetable import Timetable
from world import World

def load_rooms(path="configs/rooms.yaml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    rooms = {}
    for name, info in data["rooms"].items():
        rooms[name] = Room(
            name=name,
            room_type=info["room_type"],
            x=info["x"],
            y=info["y"],
            width=info["width"],
            height=info["height"],
        )
    return rooms

def load_students(path="configs/students.yaml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    students = []
    for s in data["students"]:
        students.append(
            Student(
                name=s["name"],
                homeroom=s["homeroom"],
                current_room=s["current_room"],
            )
        )
    return students

def load_timetable(path="configs/schedule.yaml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return Timetable(homeroom_schedules=data)

def main():
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    world = World(rooms, students, timetable)

    # Simple loop: 20 ticks = 20 minutes
    for _ in range(20):
        world.tick(dt_minutes=1)
        snapshot = world.get_debug_snapshot()

        # clear screen-ish
        print("\n" + "=" * 60)
        print(f"Time: {snapshot['time']}")
        for s in snapshot["students"]:
            print(
                f"{s['name']:6} | room={s['room']:10} -> target={s['target']:10} "
                f"| hunger={s['needs']['hunger']:.1f} "
                f"energy={s['needs']['energy']:.1f} "
                f"stress={s['needs']['stress']:.1f} "
                f"| discipline_risk={s['discipline_risk']:.1f}"
            )

        time.sleep(0.25)

if __name__ == "__main__":
    main()
```

**Codex action:**

* Create/overwrite `main.py` with that.
* Make sure `pyyaml` is in requirements if you are tracking dependencies.

---

## 7. `requirements.txt`

Add (or update) a `requirements.txt` at project root so the env is reproducible:

```text
pyyaml
```

If you're already using pygame in the repo and planning to render visually this milestone, then also include:

```text
pygame
```

Codex should not remove anything else you already had in `requirements.txt`. Just ensure these are present.

---

## 8. Smoke test stub (`tests/test_smoke.py`)

We said we want pytest in this project.

Create `tests/test_smoke.py`:

```python
from room import Room
from student import Student
from timetable import Timetable
from world import World

def test_world_ticks_without_crashing():
    rooms = {
        "ClassroomA": Room("ClassroomA", "classroom", 0,0,10,10),
        "Cafeteria": Room("Cafeteria", "cafeteria", 0,0,10,10),
        "DormA": Room("DormA", "dorm", 0,0,10,10),
        "Lounge": Room("Lounge", "lounge", 0,0,10,10),
        "BathroomA": Room("BathroomA", "bathroom", 0,0,10,10),
    }

    students = [
        Student(name="TestGirl", homeroom="homeroom_A", current_room="DormA")
    ]

    timetable = Timetable(
        homeroom_schedules={
            "homeroom_A": {
                "08:00": "ClassroomA",
                "09:00": "ClassroomA",
            }
        }
    )

    w = World(rooms, students, timetable)

    # run 5 ticks to ensure no obvious exceptions
    for _ in range(5):
        w.tick(dt_minutes=1)

    snap = w.get_debug_snapshot()
    assert "students" in snap
    assert len(snap["students"]) == 1
```

Codex action:

* Create `tests/` if it doesn't exist.
* Add the file above.

---

## 9. Definition of done for Milestone 2

Milestone 2 is COMPLETE when ALL of these are true:

* `main.py` runs with no manual editing.
* The loop advances time and prints out each girl's:

  * current room
  * target room
  * hunger / energy / stress
  * discipline_risk
* Needs actually change over time.
* Students sometimes break schedule for survival needs (ex: going to Cafeteria instead of Class).
* Attendance is logged and discipline_risk goes up when they skip.
* `pytest -q` passes `test_world_ticks_without_crashing`.

At that point we officially have:

* a working "living school" core,
* trackable disobedience,
* data-driven students / rooms / schedules,
* and a foundation we can scale.

---

## 10. Milestone 3 preview (what comes after this)

Not for Codex yet, but just so we're aligned on direction:

* Add gradual movement and render positions in pygame instead of teleport.
* Add basic staff / enforcement:

  * Hall monitor / prefect / teacher who patrols halls and catches students skipping.
* Add stress → meltdown behavior and consequences.
* Night cycle (curfew, lights-out).

That’s when this stops being a sandbox and starts feeling like an actual boarding school sim.

---

## TL;DR for Codex

1. Overwrite/create: `room.py`, `student.py`, `timetable.py`, `world.py`, `main.py`.
2. Create `configs/rooms.yaml`, `configs/schedule.yaml`, `configs/students.yaml`.
3. Add/update `requirements.txt` to include `pyyaml` (and `pygame` if using it).
4. Add `tests/test_smoke.py`.
5. Ensure `main.py` runs and `pytest -q` passes.

Do not optimize. Do not refactor beyond what’s written here. The goal is to get a working baseline first.
