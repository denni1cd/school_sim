"""
Milestone M1 implementation reference for room effects.

This module captures the per-minute deltas that must be applied by
``Room.apply_effects`` and mirrors the production logic in ``room.py``.
"""
from __future__ import annotations

from typing import Dict

ROOM_TYPE_EFFECTS_PER_MINUTE: Dict[str, Dict[str, float]] = {
    "cafeteria": {"hunger": -1.2},
    "dorm": {"energy": 1.6},
    "lounge": {"stress": -1.0},
    "bathroom": {"hygiene": 2.0},
    "classroom": {"stress": 0.6},
}
KNOWLEDGE_GAIN_PER_MINUTE = 0.5


def apply_room_effects(student, room_type: str, minutes: float) -> Dict[str, float]:
    """
    Apply configured room effects to ``student`` for a duration of ``minutes``.

    Returns a mapping of need names (and optional ``knowledge`` for classrooms)
    to the deltas actually realized after clamping to [0, 100].
    """
    if minutes <= 0:
        return {}

    effects = ROOM_TYPE_EFFECTS_PER_MINUTE.get(room_type, {})
    deltas: Dict[str, float] = {}

    for need_name, per_minute in effects.items():
        starting_value = student.needs.get(need_name, 0.0)
        delta = per_minute * minutes
        clamped_value = clamp_need(starting_value + delta)
        student.needs[need_name] = clamped_value
        deltas[need_name] = clamped_value - starting_value

    if room_type == "classroom":
        knowledge_gain = KNOWLEDGE_GAIN_PER_MINUTE * minutes
        student.stats["knowledge"] = student.stats.get("knowledge", 0.0) + knowledge_gain
        deltas["knowledge"] = knowledge_gain

    return deltas


def clamp_need(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Clamp a need value to the inclusive range [minimum, maximum]."""
    return max(minimum, min(maximum, value))
