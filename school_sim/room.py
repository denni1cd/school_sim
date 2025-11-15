"""Room definitions and passive effect helpers."""

from dataclasses import dataclass, field
from typing import Dict

ROOM_TYPE_EFFECTS_PER_MINUTE: Dict[str, Dict[str, float]] = {
    "cafeteria": {"hunger": -1.2},
    "dorm": {"energy": 1.6},
    "lounge": {"stress": -1.0},
    "bathroom": {"hygiene": 2.0},
    "classroom": {"stress": 0.6, "knowledge": 0.5},
}


@dataclass
class Room:
    """Spatial room with type, size, and effect definitions."""
    name: str
    room_type: str  # "classroom", "cafeteria", "dorm", "bathroom", "lounge"
    x: int
    y: int
    width: int
    height: int
    effects: Dict[str, float] = field(default_factory=dict)
    knowledge_gain: float = 0.0

    def apply_effects(self, student, minutes: float) -> Dict[str, float]:
        """Apply the room's per-minute modifiers to a student's needs."""
        if minutes <= 0:
            return {}

        effects = self.effects or ROOM_TYPE_EFFECTS_PER_MINUTE.get(self.room_type)
        knowledge_gain = self.knowledge_gain
        if effects and "knowledge" in effects:
            # allow config to define knowledge gain inline
            knowledge_gain = effects.get("knowledge", knowledge_gain)
            effects = {k: v for k, v in effects.items() if k != "knowledge"}

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
            gain = knowledge_gain if knowledge_gain else ROOM_TYPE_EFFECTS_PER_MINUTE["classroom"].get(
                "knowledge", 0.5
            )
            gain_total = gain * minutes
            student.stats["knowledge"] = student.stats.get("knowledge", 0.0) + gain_total
            deltas["knowledge"] = gain_total

        return deltas


def _clamp(value: float, *, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))
