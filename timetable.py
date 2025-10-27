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
