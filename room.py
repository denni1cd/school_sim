from dataclasses import dataclass

@dataclass
class Room:
    name: str
    room_type: str  # "classroom", "cafeteria", "dorm", "bathroom", "lounge"
    x: int
    y: int
    width: int
    height: int

    def apply_effects(self, student, minutes: float):
        """
        Apply the passive effects of being in this room for `minutes` minutes.
        Example rules for Milestone 2:
        - cafeteria: hunger goes down
        - dorm: energy goes up
        - classroom: stress goes up, knowledge goes up
        - lounge: stress goes down
        - bathroom: hygiene goes up
        """
        if self.room_type == "cafeteria":
            student.needs["hunger"] = max(0, student.needs["hunger"] - 0.8 * minutes)
        elif self.room_type == "dorm":
            student.needs["energy"] = min(100, student.needs["energy"] + 0.6 * minutes)
        elif self.room_type == "classroom":
            student.needs["stress"] = min(100, student.needs["stress"] + 0.4 * minutes)
            student.stats["knowledge"] += 0.5 * minutes
        elif self.room_type == "lounge":
            student.needs["stress"] = max(0, student.needs["stress"] - 0.7 * minutes)
            student.needs["social"] = min(100, student.needs["social"] + 0.4 * minutes)
        elif self.room_type == "bathroom":
            student.needs["hygiene"] = min(100, student.needs["hygiene"] + 1.0 * minutes)
