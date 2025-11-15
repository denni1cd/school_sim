from types import SimpleNamespace

from school_sim import curriculum


def _student():
    return SimpleNamespace(needs={"stress": 40.0, "hygiene": 40.0, "energy": 40.0})


def test_stem_track_increases_stress_and_costs_hygiene():
    general_state = {"active_track": "General"}
    stem_state = {"active_track": "General"}
    curriculum.set_track("STEM", state=stem_state)

    student_general = _student()
    delta_general = curriculum.apply_classroom_modifiers(student_general, state=general_state, dt_minutes=1)

    student_stem = _student()
    delta_stem = curriculum.apply_classroom_modifiers(student_stem, state=stem_state, dt_minutes=1)

    assert delta_stem["stress"] > delta_general.get("stress", 0.0)
    assert delta_stem["hygiene"] < delta_general.get("hygiene", 0.0)
    assert delta_stem["energy"] < delta_general.get("energy", 0.0)


def test_arts_track_relieves_stress_compared_to_general():
    general_state = {"active_track": "General"}
    arts_state = {"active_track": "General"}
    curriculum.set_track("Arts", state=arts_state)

    student_general = _student()
    delta_general = curriculum.apply_classroom_modifiers(student_general, state=general_state, dt_minutes=1)

    student_arts = _student()
    delta_arts = curriculum.apply_classroom_modifiers(student_arts, state=arts_state, dt_minutes=1)

    assert delta_arts.get("stress", 0.0) < delta_general.get("stress", 0.0)
    assert delta_arts.get("energy", 0.0) < delta_general.get("energy", 0.0)
