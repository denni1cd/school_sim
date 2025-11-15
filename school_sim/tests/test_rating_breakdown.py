import pytest

from school_sim.rating import DEFAULT_WEIGHTS, compute_rating


def test_rating_breakdown_uses_component_weights():
    result = compute_rating(
        previous=75.0,
        critical_students=0,
        total_students=3,
        compliance=0.9,
        compliance_baseline=0.97,
        club_engagement=0.8,
        club_baseline=0.5,
        needs_baseline=0.9,
        attendance_ratio=0.95,
        attendance_baseline=0.95,
        weights=DEFAULT_WEIGHTS,
        flash_threshold=2.0,
        smoothing=0.05,
    )

    assert pytest.approx(result.value, rel=1e-3) == 75.38
    assert result.flash is False
    breakdown = result.breakdown
    assert pytest.approx(breakdown['needs'], rel=1e-3) == 6.0
    assert pytest.approx(breakdown['clubs'], rel=1e-3) == 3.0
    assert pytest.approx(breakdown['compliance'], rel=1e-3) == -1.4
    assert pytest.approx(breakdown['attendance'], rel=1e-3) == 0.0
