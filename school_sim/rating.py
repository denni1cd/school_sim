"""Rating computation helpers and breakdown structure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

DEFAULT_WEIGHTS = {
    "needs": 0.6,
    "compliance": 0.2,
    "clubs": 0.1,
    "attendance": 0.1,
}

DEFAULT_BASELINES = {
    "needs": 0.9,
    "clubs": 0.5,
    "attendance": 0.95,
}


@dataclass(frozen=True)
class RatingResult:
    """Container for computed rating value, delta, flash, and breakdown."""
    value: float
    delta: float
    flash: bool
    breakdown: Dict[str, float]


def compute_rating(
    *,
    previous: float,
    critical_students: int,
    total_students: int,
    compliance: float,
    compliance_baseline: float,
    club_engagement: float,
    club_baseline: float,
    needs_baseline: float,
    attendance_ratio: float,
    attendance_baseline: float,
    weights: Dict[str, float],
    flash_threshold: float,
    smoothing: float,
    ) -> RatingResult:
    """Compute the weighted rating based on needs, compliance, clubs, and attendance."""
    weights = _normalise_weights(weights or DEFAULT_WEIGHTS)
    needs_health = 1.0
    if total_students > 0:
        needs_health = max(0.0, 1.0 - (critical_students / total_students))

    needs_delta = needs_health - needs_baseline
    compliance_delta = compliance - compliance_baseline
    clubs_delta = club_engagement - club_baseline
    attendance_delta = attendance_ratio - attendance_baseline

    weighted_needs = needs_delta * weights["needs"]
    weighted_compliance = compliance_delta * weights["compliance"]
    weighted_clubs = clubs_delta * weights["clubs"]
    weighted_attendance = attendance_delta * weights["attendance"]

    total_weight = max(sum(weights.values()), 1e-6)
    target_delta = (weighted_needs + weighted_compliance + weighted_clubs + weighted_attendance) / total_weight * 100.0

    smoothing = _clamp(smoothing, 0.0, 1.0)
    new_value = _clamp(previous + target_delta * smoothing, 0.0, 100.0)
    rating_delta = new_value - previous
    flash = abs(rating_delta) >= flash_threshold if rating_delta else False

    breakdown = {
        "needs": weighted_needs / total_weight * 100.0,
        "compliance": weighted_compliance / total_weight * 100.0,
        "clubs": weighted_clubs / total_weight * 100.0,
        "attendance": weighted_attendance / total_weight * 100.0,
    }

    return RatingResult(
        value=new_value,
        delta=rating_delta,
        flash=flash,
        breakdown=breakdown,
    )


def _normalise_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """Return weights with defaults applied, ensuring the sum is positive."""
    merged = DEFAULT_WEIGHTS.copy()
    for key, value in weights.items():
        if key in merged:
            merged[key] = float(value)
    total = sum(merged.values())
    if total <= 0:
        return DEFAULT_WEIGHTS.copy()
    return merged


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp the input between the provided bounds."""
    return max(minimum, min(maximum, value))
