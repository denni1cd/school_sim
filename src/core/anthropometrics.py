# src/core/anthropometrics.py

import csv
import os
import bisect
from typing import Tuple

# Conversion constants
CM_TO_IN = 1 / 2.54   # inches per centimeter :contentReference[oaicite:8]{index=8}
KG_TO_LB = 2.20462262185  # pounds per kilogram :contentReference[oaicite:9]{index=9}

def _load_percentiles(csv_path: str) -> dict[float, dict[str, float]]:
    """
    Load percentile data from a CDC growth chart CSV.
    Returns a mapping: age_in_months -> { 'P25': val, 'P50': val, ... }.
    """
    data = {}
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            age = float(row['Agemos'])
            # Extract percentiles into a sub-dict
            data[age] = {key: float(row[key]) for key in row 
                         if key.startswith('P')}
    return data

# === UPDATE THIS BLOCK ===
# Point to your configs folder where the two CSVs live:
BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'configs')
HEIGHT_DATA = _load_percentiles(os.path.join(BASE_DIR, 'female_height_2_20.csv'))
WEIGHT_DATA = _load_percentiles(os.path.join(BASE_DIR, 'female_weight_2_20.csv'))

def _clamp_age(age_years: float) -> float:
    """Clamp age to [2, 20] years and convert to months."""
    months = max(24.0, min(age_years * 12.0, 20 * 12.0))
    return months

def _interp(age: float, target_p: float, 
            data_map: dict[float, dict[str, float]]) -> float:
    """
    Linear interpolate between the nearest percentiles for the target percentile.
    e.g., target_p=40.0 will interpolate between P25 and P50 if needed.
    """
    ages = sorted(data_map.keys())
    # Clamp to available age range
    age = max(ages[0], min(age, ages[-1]))
    # Find bracket indices
    i = bisect.bisect_left(ages, age)
    age_lo, age_hi = (ages[i-1], ages[i]) if i > 0 and ages[i] != age else (age, age)
    row_lo, row_hi = data_map[age_lo], data_map[age_hi]
    # Percentile keys
    p_keys = sorted(int(k[1:]) for k in row_lo.keys())
    # Find bracket for target_p
    for j in range(len(p_keys)-1):
        p_lo, p_hi = p_keys[j], p_keys[j+1]
        if p_lo <= target_p <= p_hi:
            val_lo = row_lo[f'P{p_lo}']
            val_hi = row_lo[f'P{p_hi}']
            # Interpolate percentile within this bracket
            frac = (target_p - p_lo) / (p_hi - p_lo)
            return val_lo + frac * (val_hi - val_lo)
    # Fallback if out of bracket
    return row_lo[f'P{p_keys[-1]}']

def get_height_weight(age_years: float,
                      height_pct: float = 40.0,
                      weight_pct: float = 35.0
                      ) -> Tuple[float, float]:
    """
    Return (height_in_inches, weight_in_pounds) for a given age.
    - Clamps age >20 to 20 years                                      :contentReference[oaicite:10]{index=10}
    - Samples height at `height_pct` percentile                        :contentReference[oaicite:11]{index=11}
    - Samples weight at `weight_pct` percentile                        :contentReference[oaicite:12]{index=12}
    - Converts cm->inches and kg->pounds                               :contentReference[oaicite:13]{index=13} :contentReference[oaicite:14]{index=14}
    - Rounds both to 2 decimals
    """
    months = _clamp_age(age_years)
    # Interpolate raw values
    raw_cm = _interp(months, height_pct, HEIGHT_DATA)
    raw_kg = _interp(months, weight_pct, WEIGHT_DATA)
    # Convert & round
    height_in = round(raw_cm * CM_TO_IN, 2)
    weight_lb = round(raw_kg * KG_TO_LB, 2)
    return height_in, weight_lb

def compute_body_measurements(height_in: float) -> Tuple[float, float, float]:
    """
    Compute (bust, waist, hip) circumferences in inches based on height.
    - Waist-to-height ratio ≈ 0.45                                    :contentReference[oaicite:15]{index=15}
    - Waist-to-hip ratio ≈ 0.85                                       :contentReference[oaicite:16]{index=16}
    - Bust ≈ hip circumference (hourglass approximation)             :contentReference[oaicite:17]{index=17}
    - Rounds each to 2 decimals
    """
    waist = round(height_in * 0.45, 2)
    hip   = round(waist / 0.85, 2)
    bust  = round(hip, 2)
    return bust, waist, hip
