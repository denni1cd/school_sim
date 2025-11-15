import math
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

CRITICAL_HUNGER = 85
CRITICAL_ENERGY = 25
CRITICAL_HYGIENE = 30
CRITICAL_STRESS = 90
DEFAULT_SPEED = 120.0  # pixels per minute


def _minutes_from_timestr(timestr: str) -> int:
    hours, mins = map(int, timestr.split(":"))
    return hours * 60 + mins


def _is_in_window(minute: int, window: tuple[int, int]) -> bool:
    start, end = window
    if start <= end:
        return start <= minute < end
    return minute >= start or minute < end


def _in_windows(minute: int, windows: list[tuple[int, int]]) -> bool:
    return any(_is_in_window(minute, window) for window in windows)


# Recovery hysteresis thresholds
RECOVERY_ENERGY_EXIT = 50.0
RECOVERY_HUNGER_EXIT = 40.0
RECOVERY_HYGIENE_EXIT = 60.0
RECOVERY_STRESS_EXIT = 50.0
PREEMPT_ENERGY = 45.0
PREEMPT_HUNGER = 65.0

MEAL_WINDOWS = [
    (7 * 60, 8 * 60),  # breakfast
    (11 * 60, 12 * 60),  # lunch
    (17 * 60, 18 * 60),  # dinner
]
SLEEP_WINDOWS = [
    (21 * 60, 24 * 60),
    (0, 6 * 60),
]
MIN_HUNGER_FOR_MEAL = 45.0


@dataclass
class Student:
    name: str
    homeroom: str  # e.g. "homeroom_A" - used to look up schedule
    current_room: str  # name of the room they're currently in
    target_room: Optional[str] = None  # where they're walking to
    club_id: Optional[str] = None
    attendance_record: Dict[str, bool] = field(default_factory=dict)
    stats: Dict[str, float] = field(
        default_factory=lambda: {
            "knowledge": 0.0,
            "discipline_risk": 0.0,
        }
    )
    needs: Dict[str, float] = field(
        default_factory=lambda: {
            "hunger": 25.0,  # 0 = full, 100 = starving
            "energy": 85.0,  # 0 = exhausted, 100 = fully rested
            "hygiene": 70.0,  # 0 = filthy, 100 = clean
            "stress": 15.0,  # 0 = calm, 100 = meltdown
            "social": 55.0,  # 0 = lonely, 100 = very fulfilled
        }
    )
    x: float = 0.0
    y: float = 0.0
    speed: float = DEFAULT_SPEED

    def decay_needs(self, minutes: float):
        """Needs naturally drift over time according to specification deltas."""
        if minutes <= 0:
            return

        self.needs["hunger"] = min(100.0, self.needs["hunger"] + 0.5 * minutes)
        self.needs["stress"] = min(100.0, self.needs["stress"] + 0.2 * minutes)
        self.needs["energy"] = max(0.0, self.needs["energy"] - 0.4 * minutes)
        self.needs["hygiene"] = max(0.0, self.needs["hygiene"] - 0.2 * minutes)
        # Social remains an auxiliary stat that decays slowly.
        self.needs["social"] = max(0.0, self.needs["social"] - 0.03 * minutes)

    def choose_target(
        self,
        world_time_str: str,
        schedule: Dict[str, str],
        rooms: Dict[str, Any],
        overrides: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Decide where to go next.
        1. Check for crisis needs (cafeteria, dorm, bathroom, lounge).
        2. Otherwise follow schedule for this time slot.
        """
        total_minutes = _minutes_from_timestr(world_time_str)
        minute_of_day = total_minutes % (24 * 60)
        in_sleep_window = _in_windows(minute_of_day, SLEEP_WINDOWS)
        in_meal_window = _in_windows(minute_of_day, MEAL_WINDOWS)

        overrides = overrides or {}

        def override_value(need: str, key: str, fallback: float | str) -> float | str:
            return overrides.get(need, {}).get(key, fallback)

        hunger_target = override_value("hunger", "room", "cafeteria")
        hunger_critical = float(override_value("hunger", "critical", CRITICAL_HUNGER))
        hunger_preempt = float(override_value("hunger", "preempt", PREEMPT_HUNGER))

        energy_target = override_value("energy", "room", "dorm")
        energy_critical = float(override_value("energy", "critical", CRITICAL_ENERGY))
        energy_preempt = float(override_value("energy", "preempt", PREEMPT_ENERGY))

        hygiene_target = override_value("hygiene", "room", "bathroom")
        hygiene_critical = float(override_value("hygiene", "critical", CRITICAL_HYGIENE))
        hygiene_preempt = float(override_value("hygiene", "preempt", RECOVERY_HYGIENE_EXIT))

        stress_target = override_value("stress", "room", "lounge")
        stress_critical = float(override_value("stress", "critical", CRITICAL_STRESS))
        stress_preempt = float(override_value("stress", "preempt", RECOVERY_STRESS_EXIT))

        if not self.is_traveling():
            current_room_obj = rooms.get(self.current_room)
            if current_room_obj:
                if (
                    current_room_obj.room_type == hunger_target
                    and (in_meal_window or self.needs["hunger"] > RECOVERY_HUNGER_EXIT)
                ):
                    self.target_room = self.current_room
                    return
                if (
                    current_room_obj.room_type == energy_target
                    and (
                        self.needs["energy"] < RECOVERY_ENERGY_EXIT
                        or (in_sleep_window and self.needs["hunger"] < hunger_critical)
                    )
                ):
                    self.target_room = self.current_room
                    return
                if current_room_obj.room_type == stress_target and self.needs["stress"] > RECOVERY_STRESS_EXIT:
                    self.target_room = self.current_room
                    return
                if current_room_obj.room_type == hygiene_target and self.needs["hygiene"] < RECOVERY_HYGIENE_EXIT:
                    self.target_room = self.current_room
                    return

        # Crisis overrides schedule
        if self.needs["hunger"] >= hunger_critical:
            self.target_room = self.find_room_by_type(hunger_target, rooms)
            return
        if self.needs["energy"] <= energy_critical:
            self.target_room = self.find_room_by_type(energy_target, rooms)
            return
        if self.needs["hygiene"] <= hygiene_critical:
            self.target_room = self.find_room_by_type(hygiene_target, rooms)
            return
        if self.needs["stress"] >= stress_critical:
            self.target_room = self.find_room_by_type(stress_target, rooms)
            return

        # Pre-emptive need handling so students recover before true crisis
        if self.needs["hunger"] >= hunger_preempt and in_meal_window:
            cafeteria = self.find_room_by_type(hunger_target, rooms)
            if cafeteria is not None:
                self.target_room = cafeteria
                return
        if self.needs["energy"] <= energy_preempt:
            dorm = self.find_room_by_type(energy_target, rooms)
            if dorm is not None:
                self.target_room = dorm
                return

        # Otherwise follow assigned schedule
        if world_time_str in schedule:
            self.target_room = schedule[world_time_str]
            return

        # Unscheduled time policies to maintain daily rhythm
        if in_sleep_window:
            dorm = self.find_room_by_type(energy_target, rooms)
            if dorm is not None:
                self.target_room = dorm
                return

        if in_meal_window and self.needs["hunger"] >= MIN_HUNGER_FOR_MEAL:
            cafeteria = self.find_room_by_type(hunger_target, rooms)
            if cafeteria is not None:
                self.target_room = cafeteria
                return

        if self.needs["energy"] <= RECOVERY_ENERGY_EXIT:
            dorm = self.find_room_by_type(energy_target, rooms)
            if dorm is not None:
                self.target_room = dorm
                return

        if self.needs["stress"] >= stress_preempt:
            lounge = self.find_room_by_type(stress_target, rooms)
            if lounge is not None:
                self.target_room = lounge
                return

        # default unscheduled choice
        self.target_room = self.find_room_by_type(stress_target, rooms)

    def find_room_by_type(self, room_type: str, rooms: Dict[str, Any]) -> Optional[str]:
        for room_name, room in rooms.items():
            if room.room_type == room_type:
                return room_name
        return None

    def is_traveling(self) -> bool:
        return self.target_room is not None and self.current_room != self.target_room

    def _room_center(self, room: Any) -> tuple[float, float]:
        return room.x + room.width / 2.0, room.y + room.height / 2.0

    def move_towards_target(self, rooms: Dict[str, Any], minutes: float):
        if not self.target_room:
            room = rooms.get(self.current_room)
            if room:
                self.x, self.y = self._room_center(room)
            return

        destination = rooms.get(self.target_room)
        if destination is None:
            return

        target_x, target_y = self._room_center(destination)

        if self.current_room == self.target_room:
            self.x, self.y = target_x, target_y
            return

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            self.current_room = self.target_room
            self.x, self.y = target_x, target_y
            return

        max_distance = self.speed * minutes
        if max_distance >= distance:
            self.x, self.y = target_x, target_y
            self.current_room = self.target_room
        else:
            ratio = max_distance / distance
            self.x += dx * ratio
            self.y += dy * ratio

    def record_attendance(self, world_time_str: str, expected_room: Optional[str], *, traveling: bool = False):
        """
        Track if she's skipping what she 'should' be doing.
        This is the seed for discipline/enforcement systems.
        """
        in_class_when_she_should_be = expected_room is not None and expected_room == self.current_room
        if expected_room is not None and traveling and self.target_room == expected_room:
            in_class_when_she_should_be = True

        self.attendance_record[world_time_str] = in_class_when_she_should_be
        if not in_class_when_she_should_be and expected_room is not None:
            # She's skipping. Nudge discipline risk up.
            self.stats["discipline_risk"] += 1.0
