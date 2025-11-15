"""Timetable helper storing homeroom schedules and expectations."""

from typing import Dict, Optional


def minutes_to_timestr(total_minutes: int) -> str:
    """480 -> '08:00'."""
    hours = total_minutes // 60
    mins = total_minutes % 60
    return f"{hours:02d}:{mins:02d}"


class Timetable:
    """Store homeroom schedules and provide expected rooms."""
    """
    Holds:
    - per-homeroom schedules (like homeroom_A)
    - global school periods, etc.
    """

    def __init__(self, homeroom_schedules: Dict[str, Dict[str, str]]):
        """Create a timetable with the provided homeroom schedules."""
        # homeroom_schedules["homeroom_A"]["08:00"] = "MathClassA"
        self.homeroom_schedules = homeroom_schedules

    def expected_room_for(self, homeroom: str, timestr: str) -> Optional[str]:
        """Return the expected room for the homeroom at the given time slot."""
        schedule = self.homeroom_schedules.get(homeroom, {})
        return schedule.get(timestr)
