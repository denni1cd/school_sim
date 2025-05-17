"""CLI entry point for the school simulation framework."""
import sys
import os
# Ensure the src directory is in the system path for module imports
sys.path.append(os.path.dirname(__file__))

import argparse
from core import config_loader
from population import generator
from output import exporter

def main():
    parser = argparse.ArgumentParser(description="Generate school population data.")
    parser.add_argument(
        "--config-dir",
        type=str,
        default="configs",
        help="Path to the configuration files directory."
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["csv", "json"],
        default="csv",
        help="Output format: 'csv' or 'json'."
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Output file path (including filename). Defaults to assets/population.<ext>."
    )
    args = parser.parse_args()

    # Load configurations
    configs = config_loader.load_configurations(args.config_dir)
    # Generate population data
    population_data = generator.generate_population(configs)

    # Determine output file path
    output_format = args.format.lower()
    if args.output_file:
        output_file = args.output_file
    else:
        output_file = os.path.join("assets", f"population.{output_format}")

    # Export data to the specified format
    exporter.export_data(population_data, output_file, format=output_format)
    print(
        f"Generated {len(population_data)} individuals (students and staff). "
        f"Data saved to {output_file}."
    )
if __name__ == "__main__":
    main()
