# src/population/generator.py

"""
Population generation module with slot-based, classifier-aware uniform assignment,
plus realistic height, weight, and body measurements for each individual.
"""

import random
from typing import List, Dict, Any, Optional
from population import names
from core.anthropometrics import get_height_weight, compute_body_measurements


def pick_uniform(role: str,
                 classifier: Optional[str],
                 configs: dict) -> Dict[str, Dict[str, Optional[str]]]:
    """
    For the given role ("student" or "staff"), pick one random item per slot.
    - configs['uniforms'][role][group][slot]['categories'] is a LIST of {name, items}.
    - If `classifier` is provided, pick only from that category.
    - Otherwise, flatten all categories and pick from the full items list.
    Returns a dict:
      {
        "clothing": { slot_name: chosen_item, ... },
        "accessories": { slot_name: chosen_item, ... }
      }
    """
    role_cfg = configs.get('uniforms', {}).get(role, {})
    outf = {"clothing": {}, "accessories": {}}

    for group in ("clothing", "accessories"):
        slots = role_cfg.get(group, {})
        for slot_name, slot_cfg in slots.items():
            categories = slot_cfg.get("categories", [])
            if classifier:
                # pick from the named category, if it exists
                items = next(
                    (cat["items"] for cat in categories if cat["name"] == classifier),
                    []
                )
            else:
                # flatten all categories into one list
                items = []
                for cat in categories:
                    items.extend(cat.get("items", []))
            outf[group][slot_name] = random.choice(items) if items else None

    return outf


def generate_population(configs: dict) -> List[Dict[str, Any]]:
    """
    Generate a list of individuals (students and optional staff) based on configuration.
    Each person receives:
      - realistic height & weight (in inches/pounds) sampled at specified percentiles
      - computed bust, waist, hip measurements (in inches)
      - slot-based uniform assignments (clothing & accessories)
    """
    pop_cfg = configs.get('population', {})
    name_cfg = configs.get('names', {})
    systems_cfg = configs.get('systems', {})

    # Name provider setup
    female_names = name_cfg.get('female_first', [])
    male_names   = name_cfg.get('male_first', [])
    last_names   = name_cfg.get('last', [])
    name_provider = names.NameProvider(female_names, male_names, last_names)

    # Population parameters
    students_count = pop_cfg.get('students', {}).get('count', 0)
    staff_count    = pop_cfg.get('staff', {}).get('count', 0)
    student_ages   = pop_cfg.get('students', {}).get('age_range', [0, 0])
    staff_ages     = pop_cfg.get('staff', {}).get('age_range', [0, 0])

    population: List[Dict[str, Any]] = []
    person_id = 1

    # Determine classifier for uniform selection (e.g., "warm", "cold"), if any
    classifier: Optional[str] = None

    # Generate student entries
    for _ in range(students_count):
        age = random.randint(*student_ages)
        name = name_provider.get_full_name(gender="female")

        # Height & weight sampling at configured percentiles
        height_in, weight_lb = get_height_weight(age_years=age)
        bust_in, waist_in, hip_in = compute_body_measurements(height_in)

        # Uniform assignment
        uniform = pick_uniform("student", classifier, configs)

        # Assemble the record
        record = {
            "id":        person_id,
            "name":      name,
            "age":       age,
            "role":      "Student",
            "height_in": height_in,
            "weight_lb": weight_lb,
            "bust_in":   bust_in,
            "waist_in":  waist_in,
            "hip_in":    hip_in,
        }
        # Merge uniform slots into the record
        record.update(uniform["clothing"])
        record.update(uniform["accessories"])

        population.append(record)
        person_id += 1

    # Generate staff entries
    for _ in range(staff_count):
        age = random.randint(*staff_ages)
        name = name_provider.get_full_name(gender="female")

        height_in, weight_lb = get_height_weight(age_years=age)
        bust_in, waist_in, hip_in = compute_body_measurements(height_in)

        uniform = pick_uniform("staff", classifier, configs)

        record = {
            "id":        person_id,
            "name":      name,
            "age":       age,
            "role":      "Staff",
            "height_in": height_in,
            "weight_lb": weight_lb,
            "bust_in":   bust_in,
            "waist_in":  waist_in,
            "hip_in":    hip_in,
        }
        record.update(uniform["clothing"])
        record.update(uniform["accessories"])

        population.append(record)
        person_id += 1

    # Placeholder hooks for future systems
    if systems_cfg.get('factions', {}).get('enabled'):
        try:
            from factions import assign_factions
            population = assign_factions(
                population,
                systems_cfg['factions'].get('types', [])
            )
        except ImportError:
            pass

    if systems_cfg.get('psychological_manipulation', {}).get('enabled'):
        try:
            from psychology import apply_influences
            population = apply_influences(population)
        except ImportError:
            pass

    return population
