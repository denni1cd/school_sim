from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


UNIFORM_EFFECTS: Dict[str, Dict[str, float]] = {
    "strict": {"hygiene": 0.1, "stress": 0.15},
    "moderate": {"hygiene": 0.0, "stress": 0.0},
    "relaxed": {"hygiene": -0.1, "stress": -0.05},
}

UNIFORM_COMPLIANCE: Dict[str, float] = {
    "strict": 0.92,
    "moderate": 0.97,
    "relaxed": 0.99,
}

DISCIPLINE_STRESS: Dict[str, float] = {
    "tough": 0.05,
    "fair": 0.0,
    "lenient": -0.02,
}

DISCIPLINE_RELIEF: Dict[str, float] = {
    "tough": -0.2,
    "fair": -0.1,
    "lenient": 0.0,
}

DISCIPLINE_COMPLIANCE: Dict[str, float] = {
    "tough": 0.03,
    "fair": 0.0,
    "lenient": -0.05,
}


@dataclass
class PolicyApplication:
    needs_delta: Dict[str, float]
    compliance: float


def apply_policy_effects(student, policy_state: Dict[str, str], *, dt_minutes: float = 1.0) -> PolicyApplication:
    """
    Apply uniforms and discipline effects to a student and return the aggregated delta/compliance.
    """
    needs_delta: Dict[str, float] = {}
    uniforms = (policy_state.get("uniforms") or "moderate").lower()
    discipline = (policy_state.get("discipline") or "fair").lower()

    uniform_effect = UNIFORM_EFFECTS.get(uniforms, {})
    for need, rate in uniform_effect.items():
        delta = rate * dt_minutes
        needs_delta[need] = needs_delta.get(need, 0.0) + delta
        _adjust_need(student, need, delta)

    stress_mod = DISCIPLINE_STRESS.get(discipline, 0.0) * dt_minutes
    if stress_mod:
        needs_delta["stress"] = needs_delta.get("stress", 0.0) + stress_mod
        _adjust_need(student, "stress", stress_mod)

    # Discipline relief reduces stress and slowly resolves risk when students are out of line.
    relief = DISCIPLINE_RELIEF.get(discipline, 0.0)
    risk = float(student.stats.get("discipline_risk", 0.0))
    if relief < 0.0 and risk > 0.0:
        relieve_amount = relief * dt_minutes
        needs_delta["stress"] = needs_delta.get("stress", 0.0) + relieve_amount
        _adjust_need(student, "stress", relieve_amount)
        student.stats["discipline_risk"] = max(0.0, risk - dt_minutes)
    elif risk > 0.0:
        student.stats["discipline_risk"] = max(0.0, risk - 0.1 * dt_minutes)

    base = UNIFORM_COMPLIANCE.get(uniforms, 0.97)
    bonus = DISCIPLINE_COMPLIANCE.get(discipline, 0.0)
    penalty = min(0.25, float(student.stats.get("discipline_risk", 0.0)) * 0.01)
    compliance = max(0.0, min(1.0, base + bonus - penalty))

    return PolicyApplication(needs_delta=needs_delta, compliance=compliance)


def change_uniform(
    policy_state: Dict[str, str],
    new_level: str,
    *,
    costs: Dict[str, int],
    budget: int,
) -> Tuple[int, str]:
    """
    Update the uniforms level, deducting the configured budget cost.
    Returns the new budget balance and a caption describing the change.
    """
    target = new_level.lower()
    if target not in UNIFORM_EFFECTS:
        raise ValueError(f"Invalid uniform level: {new_level}")
    current = (policy_state.get("uniforms") or "moderate").lower()
    if target == current:
        return budget, f"Uniform policy remains {target.title()}."

    cost = int(costs.get("change_policy", 0))
    if budget - cost < 0:
        raise ValueError("Insufficient budget for policy change.")

    policy_state["uniforms"] = target
    budget_after = budget - cost
    return budget_after, f"Uniform policy set to {target.title()}."


def change_discipline(
    policy_state: Dict[str, str],
    new_level: str,
    *,
    costs: Dict[str, int],
    budget: int,
) -> Tuple[int, str]:
    """
    Update the discipline stance with the configured budget cost.
    Returns the new budget and descriptive caption.
    """
    target = new_level.lower()
    if target not in DISCIPLINE_STRESS:
        raise ValueError(f"Invalid discipline level: {new_level}")
    current = (policy_state.get("discipline") or "fair").lower()
    if target == current:
        return budget, f"Discipline policy remains {target.title()}."

    cost = int(costs.get("change_policy", 0))
    if budget - cost < 0:
        raise ValueError("Insufficient budget for policy change.")

    policy_state["discipline"] = target
    budget_after = budget - cost
    return budget_after, f"Discipline policy set to {target.title()}."


def _adjust_need(student, name: str, delta: float) -> None:
    if name not in student.needs:
        return
    updated = student.needs[name] + delta
    student.needs[name] = max(0.0, min(100.0, updated))
