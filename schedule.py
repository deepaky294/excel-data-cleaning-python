#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Wrapper script for scheduling the data cleaning pipeline."
    )
    parser.add_argument("--config", help="Optional JSON config file for the cleaning pipeline.")
    parser.add_argument("--report-type", choices=["dealer", "subdealer"], default="dealer",
                        help="Type of report to generate.")
    parser.add_argument("--dim-file", help="Path to the DimDealer or DimSubdealer file.")
    parser.add_argument("--store-file", help="Path to the store master file.")
    parser.add_argument("--output-dir", default="output", help="Directory to write output files.")
    parser.add_argument("--batch", action="store_true", help="Process input files in batch mode.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_path = Path(__file__).with_name("data_cleaning.py")
    if not script_path.exists():
        print(f"Error: data_cleaning.py not found at {script_path}", file=sys.stderr)
        return 1

    command = [sys.executable, str(script_path), "--report-type", args.report_type]

    if args.config:
        command.extend(["--config", args.config])
    if args.dim_file:
        command.extend(["--dim-file", args.dim_file])
    if args.store_file:
        command.extend(["--store-file", args.store_file])
    if args.output_dir:
        command.extend(["--output-dir", args.output_dir])
    if args.batch:
        command.append("--batch")

    result = subprocess.run(command)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
