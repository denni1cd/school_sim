from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

ROOT = Path(__file__).resolve().parents[1]
_SETTINGS_PATH = ROOT / 'config' / 'settings.yaml'
_PROFILES_DIR = ROOT / 'config' / 'profiles'


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def available_profiles() -> Dict[str, Path]:
    profiles: Dict[str, Path] = {}
    if _PROFILES_DIR.is_dir():
        for path in _PROFILES_DIR.glob('*.yaml'):
            profiles[path.stem] = path
    return profiles


def load_config(*, profile: str | None = None) -> Dict[str, Any]:
    base_cfg = yaml.safe_load(_SETTINGS_PATH.read_text())
    chosen_profile = profile or os.environ.get('SCHOOL_SIM_PROFILE')
    if not chosen_profile:
        return base_cfg

    profiles = available_profiles()
    path = profiles.get(chosen_profile)
    if path is None:
        raise ValueError(f"Unknown profile '{chosen_profile}'. Available: {', '.join(sorted(profiles)) or 'none'}")

    overrides = yaml.safe_load(path.read_text()) or {}
    return _deep_merge(base_cfg, overrides)
