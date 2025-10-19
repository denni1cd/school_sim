from dataclasses import dataclass

@dataclass
class GameClock:
    minutes_per_tick: float
    day_length_minutes: int = 24*60
    minute: float = 8*60
    def tick(self):
        self.minute = (self.minute + self.minutes_per_tick) % self.day_length_minutes
    def get_time_str(self) -> str:
        m = int(self.minute) % self.day_length_minutes
        h, mm = divmod(m, 60)
        return f"{h:02d}:{mm:02d}"
    def minutes_until(self, hhmm:str) -> float:
        h,m = map(int, hhmm.split(":")); target=(h*60+m)%self.day_length_minutes
        cur=int(self.minute)%self.day_length_minutes
        return float((target-cur)%self.day_length_minutes)
