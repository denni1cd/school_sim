from school_sim.office import OfficeScreen


def test_reports_include_breakdown_and_transactions():
    office = OfficeScreen()
    snapshot = {
        "time": "08:30",
        "budget": 950,
        "rating": 78.4,
        "rating_delta": 1.2,
        "students": [{"name": "Alice"}],
        "events": [{"caption": "Morning assembly"}],
        "rating_breakdown": {"needs": 58.0, "compliance": 18.0, "clubs": 9.0, "attendance": 7.0},
        "economy_history": [
            {"time": "08:10", "reason": "Policy change: uniforms -> Strict", "delta": -50, "balance": 950},
            {"time": "08:15", "reason": "Club assignment: Alice -> Art Club", "delta": -5, "balance": 945},
        ],
        "policy_history": [
            {
                "time": "08:20",
                "policy": "uniforms",
                "value": "Strict",
                "delta": -50,
                "balance": 950,
                "caption": "Uniform policy set to Strict.",
            }
        ],
        "attendance_ratio": 0.92,
    }

    lines = office._build_reports_lines(snapshot)
    text = " ".join(lines)
    assert "Rating components" in text
    assert "Needs: 58.0" in text
    assert "Transactions:" in text
    assert any("Policy change" in line for line in lines)
    assert "Recent policy changes" in text
