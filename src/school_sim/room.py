from dataclasses import dataclass
from typing import Dict

ROOM_TYPE_EFFECTS_PER_MINUTE: Dict[str, Dict[str, float]] = {
    "cafeteria": {"hunger": -1.2},
    "dorm": {"energy": 1.6},
    "lounge": {"stress": -1.0},
    "bathroom": {"hygiene": 2.0},
    "classroom": {"stress": 0.6},
}
KNOWLEDGE_GAIN_PER_MINUTE = 0.5


@dataclass
class Room:
    name: str
    room_type: str  # "classroom", "cafeteria", "dorm", "bathroom", "lounge"
    x: int
    y: int
    width: int
    height: int

    def apply_effects(self, student, minutes: float) -> Dict[str, float]:
        """
        Apply the passive effects of being in this room for `minutes` minutes.
        Returns a mapping of need names to the net delta applied after clamping.
        """
        if minutes <= 0:
            return {}

        effects = ROOM_TYPE_EFFECTS_PER_MINUTE.get(self.room_type)
        deltas: Dict[str, float] = {}

        if not effects:
            return deltas

        for need_name, per_minute in effects.items():
            current_value = student.needs.get(need_name, 0.0)
            raw_delta = per_minute * minutes
            new_value = _clamp(current_value + raw_delta)
            student.needs[need_name] = new_value
            deltas[need_name] = new_value - current_value

        if self.room_type == "classroom":
            knowledge_gain = KNOWLEDGE_GAIN_PER_MINUTE * minutes
            student.stats["knowledge"] = student.stats.get("knowledge", 0.0) + knowledge_gain
            deltas["knowledge"] = knowledge_gain

        return deltas


def _clamp(value: float, *, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))
