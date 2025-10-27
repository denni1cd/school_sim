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
