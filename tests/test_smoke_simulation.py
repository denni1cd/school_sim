from game.app import main


def test_smoke_sim_runs():
    result = main(ticks=240)
    assert "npc_states" in result
    assert len(result["npc_states"]) >= 7