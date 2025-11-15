"""Curriculum track definitions, captions, and classroom modifiers."""

from __future__ import annotations

from typing import Dict, Optional

TRACK_EFFECTS: Dict[str, Dict[str, float]] = {
    "general": {},
    "stem": {"stress": 0.05, "hygiene": -0.05, "energy": -0.05},
    "arts": {"stress": -0.05, "energy": -0.05},
}

TRACK_CAPTIONS: Dict[str, str] = {
    "general": "Curriculum focus remains General studies.",
    "stem": "Curriculum focus shifted to STEM. Classroom rigor increases stress and hygiene upkeep.",
    "arts": "Curriculum focus shifted to Arts. Creative studies ease stress with modest energy cost.",
}

ACTIVE_TRACK: str = "General"


def current_track(state: Optional[dict] = None) -> str:
    """Return the active curriculum track from state or module default."""
    if state is not None:
        value = state.get("active_track", ACTIVE_TRACK)
        return _canonical(value)
    return _canonical(ACTIVE_TRACK)


def set_track(track_name: str, *, state: Optional[dict] = None) -> str:
    """
    Update the curriculum focus either on the provided state or module-level default.

    Returns a caption describing the outcome for UI overlays.
    """
    target_key = _canonical(track_name)
    if target_key not in TRACK_EFFECTS:
        raise ValueError(f"Unknown curriculum track: {track_name}")

    previous_key = current_track(state)
    if target_key == previous_key:
        return TRACK_CAPTIONS.get(target_key, f"Curriculum remains {target_key.title()}.")

    target_label = _label(target_key)
    if state is not None:
        state["active_track"] = target_label
    else:
        global ACTIVE_TRACK  # noqa: PLW0603 - module-level override used for headless helpers
        ACTIVE_TRACK = target_label
    return TRACK_CAPTIONS.get(target_key, f"Curriculum focus set to {target_label}.")


def apply_classroom_modifiers(
    student,
    *,
    state: Optional[dict] = None,
    track: Optional[str] = None,
    dt_minutes: float = 1.0,
) -> Dict[str, float]:
    """
    Apply curriculum-specific deltas to a student's needs while in a classroom.

    Returns the net change applied to each need so callers can tally effects.
    """
    active_key = (
        _canonical(track)
        if track is not None
        else current_track(state if state is not None else getattr(student, "curriculum_state", None))
    )
    effects = TRACK_EFFECTS.get(active_key, {})
    deltas: Dict[str, float] = {}
    if not effects or dt_minutes <= 0:
        return deltas

    for need, per_minute in effects.items():
        if need not in student.needs:
            continue
        before = student.needs[need]
        after = _clamp(before + per_minute * dt_minutes)
        student.needs[need] = after
        deltas[need] = after - before
    return deltas


def _canonical(name: Optional[str]) -> str:
    if not name:
        return "general"
    return str(name).strip().lower()


def _label(key: str) -> str:
    return {
        "general": "General",
        "stem": "STEM",
        "arts": "Arts",
    }.get(key, key.capitalize() if key else "General")


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))
