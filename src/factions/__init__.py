"""Placeholder module for faction system."""
import random

def assign_factions(population, factions_list):
    """
    Assign each person a faction from the provided list.
    Currently assigns a random faction to each person if factions are enabled.
    """
    if not factions_list:
        # No factions defined, leave as unassigned
        return population
    for person in population:
        person['faction'] = random.choice(factions_list)
    return population
