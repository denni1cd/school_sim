"""Exercise the office shell interface for handling actions."""

import pytest

from school_sim.office import OfficeScreen


@pytest.fixture
def office_config():
    return {
        "policies": {"uniforms": "strict", "discipline": "fair", "costs": {"change_policy": 55}},
        "clubs": {
            "clubs": [
                {
                    "id": "art",
                    "name": "Art Club",
                    "room": "Classroom",
                    "meets_at": "08:30",
                    "capacity": 8,
                    "effects": {"stress": -0.3},
                }
            ],
            "costs": {"create_club": 125, "assign_student": 7},
        },
        "curriculum": {"active_track": "STEM"},
        "staff": {"staff": [{"role": "Headmistress", "name": "E. Sterling"}]},
    }


def build_office(config):
    return OfficeScreen(
        policies=config["policies"],
        clubs=config["clubs"],
        curriculum=config["curriculum"],
        staff=config["staff"],
    )


def test_toggle_office_modal(office_config):
    office = build_office(office_config)
    assert office.visible is False
    office.toggle()
    assert office.visible is True
    office.toggle()
    assert office.visible is False
    office.open()
    assert office.visible is True
    office.close()
    assert office.visible is False


def test_tab_cycle_and_selection(office_config):
    office = build_office(office_config)
    titles = office.tab_titles()
    assert titles[office.active_index] == "Policies"
    office.next_tab()
    assert office.tab_titles()[office.active_index] == "Clubs"
    office.previous_tab()
    assert office.tab_titles()[office.active_index] == "Policies"
    office.select_tab(3)
    assert office.tab_titles()[office.active_index] == "Staff"
    office.select_tab(99)  # out of range should not change selection
    assert office.tab_titles()[office.active_index] == "Staff"
    office.next_tab()
    office.next_tab()
    assert office.tab_titles()[office.active_index] == "Policies"


def test_tab_payloads_reflect_config(office_config):
    office = build_office(office_config)

    view = office.get_active_view()
    assert view.title == "Policies"
    combined = " ".join(view.lines)
    assert "Uniforms: Strict" in combined
    assert "Change policy cost: 55" in combined

    office.select_tab(1)
    club_view = office.get_active_view()
    assert club_view.title == "Clubs"
    clubs_text = " ".join(club_view.lines)
    assert "Art Club" in clubs_text
    assert "Members: 0/8" in clubs_text
    assert "Effects: stress -0.30" in clubs_text
    assert "Assign student cost: 7" in clubs_text

    office.select_tab(4)
    reports_view = office.get_active_view(
        {
            "time": "08:15",
            "budget": 980,
            "rating": 74.5,
            "rating_delta": -0.5,
            "students": [{"name": "Alice"}],
            "events": [{"caption": "Morning Assembly"}],
        }
    )
    reports_text = " ".join(reports_view.lines)
    assert "Current Time: 08:15" in reports_text
    assert "Budget: 980" in reports_text
    assert "Rating: 74.5" in reports_text
    assert "Rating delta: -0.5" in reports_text
    assert "Enrolled Students: 1" in reports_text
    assert "Morning Assembly" in reports_text


def test_club_view_reflects_membership_snapshot(office_config):
    office = build_office(office_config)
    office.select_tab(1)
    snapshot = {
        "clubs": [
            {
                "id": "art",
                "name": "Art Club",
                "room": "Classroom",
                "meets_at": "08:30",
                "capacity": 2,
                "members": ["Alice", "Becca", "Chloe"],
            }
        ]
    }
    office.clubs_config["clubs"][0]["capacity"] = 2
    club_view = office.get_active_view(snapshot)
    clubs_text = " ".join(club_view.lines)
    assert "Members: 3/2" in clubs_text
    assert "OVER CAPACITY by 1" in clubs_text
    assert "Roster: Alice, Becca, Chloe" in clubs_text
