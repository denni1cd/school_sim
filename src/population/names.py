"""Name provider module for generating names."""
import random

class NameProvider:
    """Provides random name generation given lists of names."""
    def __init__(self, female_first_names: list[str], male_first_names: list[str], last_names: list[str]):
        self.female_first_names = female_first_names if female_first_names else []
        self.male_first_names = male_first_names if male_first_names else []
        self.last_names = last_names if last_names else []

    def get_full_name(self, gender: str = "female") -> str:
        """Return a random full name for the specified gender."""
        if gender.lower() == "female":
            if not self.female_first_names:
                first_name = ""
            else:
                first_name = random.choice(self.female_first_names)
        elif gender.lower() == "male":
            if not self.male_first_names:
                # Fallback to female names if male names list is not available
                first_name = random.choice(self.female_first_names) if self.female_first_names else ""
            else:
                first_name = random.choice(self.male_first_names)
        else:
            # If gender not specified, default to female names list
            first_name = random.choice(self.female_first_names) if self.female_first_names else ""
        if self.last_names:
            last_name = random.choice(self.last_names)
        else:
            last_name = ""
        full_name = f"{first_name} {last_name}".strip()
        return full_name
