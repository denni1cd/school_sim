"""Output formatting module (CSV/JSON exporter)."""
import csv
import json
import os

def export_data(population_data, file_path: str, format: str = "csv"):
    """
    Export the population data to a file in the specified format (CSV or JSON).
    """
    fmt = format.lower()
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if fmt == "csv":
        # Write CSV
        with open(file_path, 'w', newline='') as csvfile:
            if not population_data:
                return  # nothing to write
            # Use the keys of the first dict as CSV fieldnames
            fieldnames = population_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for person in population_data:
                writer.writerow(person)
    elif fmt == "json":
        # Write JSON
        with open(file_path, 'w') as jsonfile:
            json.dump(population_data, jsonfile, indent=4)
    else:
        raise ValueError(f"Unsupported format: {format}")
