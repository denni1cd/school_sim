"""Core configuration loaders shared across interactive and headless modes."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Dict, List

import yaml

from .room import Room
from .student import Student
from .timetable import Timetable

PACKAGE_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PACKAGE_ROOT / "configs"


def _load_yaml(path: Path | str) -> dict:
    """Read a YAML file and return its contents as a dict (empty if missing)."""
    resolved = Path(path)
    if not resolved.exists():
        return {}
    return yaml.safe_load(resolved.read_text(encoding="utf-8"))


def _merge_with_defaults(defaults: dict, payload: dict | None) -> dict:
    """Deep-merge a payload dictionary over defaults without mutating inputs."""
    result = deepcopy(defaults)
    if not payload:
        return result
    for key, value in payload.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            nested = result.get(key, {}).copy()
            nested.update(value)
            result[key] = nested
        else:
            result[key] = value
    return result


def load_rooms(path: Path | str = CONFIG_DIR / "rooms.yaml") -> Dict[str, Room]:
    """Load room definitions and instantiate Room objects keyed by name."""
    data = _load_yaml(path)
    rooms = data.get("rooms", {})
    return {
        name: Room(
            name=name,
            room_type=info["room_type"],
            x=info["x"],
            y=info["y"],
            width=info["width"],
            height=info["height"],
        )
        for name, info in rooms.items()
    }


def load_students(path: Path | str = CONFIG_DIR / "students.yaml") -> List[Student]:
    """Load the student list from YAML and instantiate Student dataclasses."""
    data = _load_yaml(path)
    students = data.get("students", [])
    return [Student(**entry) for entry in students]


def load_timetable(path: Path | str = CONFIG_DIR / "schedule.yaml") -> Timetable:
    """Load homeroom schedules from the schedule configuration."""
    data = _load_yaml(path)
    schedules = data if isinstance(data, dict) else {}
    return Timetable(homeroom_schedules=schedules)


def load_game_config(path: Path | str = CONFIG_DIR / "game.yaml") -> dict:
    """Load global game configuration and merge with defaults."""
    defaults = {
        "start_budget": 1000,
        "start_rating": 75.0,
        "tick_ms": 100,
        "win_time": "09:00",
    }
    payload = _load_yaml(path) or {}
    return {**defaults, **payload}


def load_policies_config(path: Path | str = CONFIG_DIR / "policies.yaml") -> dict:
    """Load policy configuration, supplying defaults (uniforms, discipline, costs)."""
    defaults = {
        "uniforms": "moderate",
        "discipline": "fair",
        "costs": {"change_policy": 50},
        "baseline_compliance": 0.97,
        "compliance_weight": 1.0,
    }
    payload = _load_yaml(path)
    config = _merge_with_defaults(defaults, payload)
    # ensure valid uniform/discipline values
    config["uniforms"] = str(config.get("uniforms", "moderate")).lower()
    config["discipline"] = str(config.get("discipline", "fair")).lower()
    costs = defaults["costs"].copy()
    costs.update((payload or {}).get("costs", {}) or {})
    config["costs"] = costs
    return config


def load_clubs_config(path: Path | str = CONFIG_DIR / "clubs.yaml") -> dict:
    """Load the clubs configuration and normalise entries with default costs."""
    defaults = {
        "clubs": [],
        "costs": {"create_club": 100, "assign_student": 5},
    }
    payload = _load_yaml(path)
    config = _merge_with_defaults(defaults, payload)
    clubs = config.get("clubs") or []
    normalised = []
    for entry in clubs:
        if not isinstance(entry, dict):
            continue
        normalised.append(
            {
                "id": entry.get("id"),
                "name": entry.get("name"),
                "room": entry.get("room"),
                "meets_at": entry.get("meets_at"),
                "capacity": int(entry.get("capacity", 0)),
                "effects": dict(entry.get("effects", {}) or {}),
            }
        )
    config["clubs"] = normalised
    costs = defaults["costs"].copy()
    costs.update((payload or {}).get("costs", {}) or {})
    config["costs"] = costs
    return config


def load_curriculum_config(path: Path | str = CONFIG_DIR / "curriculum.yaml") -> dict:
    """Load the curriculum configuration and ensure an active track is present."""
    defaults = {"active_track": "General"}
    payload = _load_yaml(path)
    config = _merge_with_defaults(defaults, payload)
    track = config.get("active_track", "General")
    config["active_track"] = str(track)
    return config


def load_staff_config(path: Path | str = CONFIG_DIR / "staff.yaml") -> dict:
    """Load staff entries for use in the Office Staff tab."""
    defaults = {"staff": []}
    payload = _load_yaml(path)
    config = _merge_with_defaults(defaults, payload)
    staff = config.get("staff") or []
    config["staff"] = [dict(entry) for entry in staff if isinstance(entry, dict)]
    return config
