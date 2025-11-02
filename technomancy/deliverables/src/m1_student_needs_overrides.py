"""
Milestone M1 reference implementation for need decay and crisis overrides.

The helpers in this module reflect the specification-aligned logic adopted
inside ``student.py`` for milestone M1.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

CRITICAL_THRESHOLDS = {
    "hunger": 85.0,
    "energy": 25.0,
    "hygiene": 30.0,
    "stress": 90.0,
}

RECOVERY_THRESHOLDS = {
    "hunger": 40.0,
    "energy": 50.0,
    "hygiene": 60.0,
    "stress": 50.0,
}

BASE_DECAY_PER_MINUTE = {
    "hunger": +0.5,
    "stress": +0.2,
    "energy": -0.4,
    "hygiene": -0.2,
}


def apply_base_decay(needs: Dict[str, float], minutes: float) -> Dict[str, float]:
    """Return the new needs dictionary after applying baseline decay."""
    if minutes <= 0:
        return needs

    updated = needs.copy()
    for need, rate in BASE_DECAY_PER_MINUTE.items():
        value = updated.get(need, 0.0) + rate * minutes
        updated[need] = clamp_need(value)
    return updated


def determine_override_target(
    needs: Dict[str, float],
    rooms: Dict[str, Any],
) -> Optional[str]:
    """
    Determine if a crisis override should occur and return the room name.
    Overrides respect the ordering defined in the specification:
    hunger -> energy -> hygiene -> stress.
    """
    if needs.get("hunger", 0.0) >= CRITICAL_THRESHOLDS["hunger"]:
        return _find_room(rooms, "cafeteria")
    if needs.get("energy", 100.0) <= CRITICAL_THRESHOLDS["energy"]:
        return _find_room(rooms, "dorm")
    if needs.get("hygiene", 100.0) <= CRITICAL_THRESHOLDS["hygiene"]:
        return _find_room(rooms, "bathroom")
    if needs.get("stress", 0.0) >= CRITICAL_THRESHOLDS["stress"]:
        return _find_room(rooms, "lounge")
    return None


def should_hold_position(room_type: Optional[str], needs: Dict[str, float]) -> bool:
    """
    Decide whether the student should remain in the current room until the
    recovery thresholds are satisfied.
    """
    if room_type is None:
        return False

    if room_type == "cafeteria":
        return needs.get("hunger", 0.0) > RECOVERY_THRESHOLDS["hunger"]
    if room_type == "dorm":
        return needs.get("energy", 100.0) < RECOVERY_THRESHOLDS["energy"]
    if room_type == "bathroom":
        return needs.get("hygiene", 0.0) < RECOVERY_THRESHOLDS["hygiene"]
    if room_type == "lounge":
        return needs.get("stress", 0.0) > RECOVERY_THRESHOLDS["stress"]
    return False


def clamp_need(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Clamp a need value to the inclusive range [minimum, maximum]."""
    return max(minimum, min(maximum, value))


def _find_room(rooms: Dict[str, Any], room_type: str) -> Optional[str]:
    for room_name, room in rooms.items():
        if getattr(room, "room_type", None) == room_type:
            return room_name
    return None
