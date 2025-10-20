from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping, Optional, Type

import yaml

from .base import Activity
from .discipline import DisciplineActivity
from .eat import EatActivity
from .idle import IdleActivity
from .maintenance import MaintenanceActivity
from .medical import MedicalActivity
from .recreation import RecreationActivity
from .sleep import SleepActivity
from .study import StudyActivity
from .teach import TeachActivity


@dataclass
class ActivityProfile:
    activity_id: str
    canonical: str
    label: str
    interaction_key: str
    state: Dict[str, Any]
    default_duration: int


class ActivityCatalog:
    """Utility that loads canonical activities and aliases."""

    def __init__(self, profiles: Mapping[str, ActivityProfile], canonical_defaults: Mapping[str, ActivityProfile]):
        self._profiles = dict(profiles)
        self._canonical = dict(canonical_defaults)

    def resolve(self, activity_id: str) -> ActivityProfile | None:
        profile = self._profiles.get(activity_id)
        if profile:
            return profile
        if activity_id in self._canonical:
            return self._canonical[activity_id]
        return None

    @classmethod
    def load(cls, path: str | Path) -> "ActivityCatalog":
        payload = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        catalog_section: Mapping[str, Mapping[str, Any]] = payload.get("catalog", {}) or {}
        alias_section: Mapping[str, Mapping[str, Any]] = payload.get("aliases", {}) or {}

        canonical: Dict[str, ActivityProfile] = {}
        for canonical_name, info in catalog_section.items():
            label = str(info.get("display_name", canonical_name))
            interaction_key = str(info.get("interaction_key", canonical_name))
            state = dict(info.get("state", {}) or {})
            default_duration = _parse_duration(info.get("default_duration", "00:00"))
            canonical[canonical_name] = ActivityProfile(
                activity_id=canonical_name,
                canonical=canonical_name,
                label=label,
                interaction_key=interaction_key,
                state=state,
                default_duration=default_duration,
            )

        profiles: Dict[str, ActivityProfile] = dict(canonical)
        for alias_name, info in alias_section.items():
            ref = str(info.get("activity", ""))
            base = canonical.get(ref)
            if not base:
                continue
            label = str(info.get("display_name", alias_name.replace("_", " ").title()))
            interaction_key = str(info.get("interaction_key", base.interaction_key))
            state = dict(base.state)
            state.update(info.get("state", {}) or {})
            duration = _parse_duration(info.get("default_duration", base.default_duration))
            profiles[alias_name] = ActivityProfile(
                activity_id=alias_name,
                canonical=base.canonical,
                label=label,
                interaction_key=interaction_key,
                state=state,
                default_duration=duration,
            )

        return cls(profiles, canonical)


def _parse_duration(value: str | int) -> int:
    if isinstance(value, int):
        return value
    if not value:
        return 0
    hours, minutes = map(int, str(value).split(":"))
    return hours * 60 + minutes


class ActivityFactory:
    """Factory for creating activity instances."""

    _registry: MutableMapping[str, Type[Activity]] = {
        "Sleeping": SleepActivity,
        "Eating": EatActivity,
        "Studying": StudyActivity,
        "Teaching": TeachActivity,
        "Recreation": RecreationActivity,
        "Maintenance": MaintenanceActivity,
        "Medical": MedicalActivity,
        "Discipline": DisciplineActivity,
        "Idle": IdleActivity,
    }

    @classmethod
    def create(
        cls,
        activity_profile: ActivityProfile,
        *,
        room_id: str,
        duration: int,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Activity:
        activity_cls = cls._registry.get(activity_profile.canonical, IdleActivity)
        return activity_cls(
            name=activity_profile.activity_id,
            label=activity_profile.label,
            interaction_key=activity_profile.interaction_key,
            room_id=room_id,
            duration=duration,
            state_defaults=activity_profile.state,
            overrides=overrides,
        )

    @classmethod
    def register(cls, canonical: str, activity_cls: Type[Activity]) -> None:
        cls._registry[canonical] = activity_cls
