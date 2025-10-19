from game.core.time_clock import GameClock
def test_clock_wraps_day():
 c=GameClock(60,24*60,23*60); c.tick(); assert c.get_time_str()=='00:00'
