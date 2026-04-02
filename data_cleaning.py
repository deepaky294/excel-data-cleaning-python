import argparse
import sys
from pathlib import Path
from typing import List, Optional

from config import AppConfig, ConfigError, load_config
from data_cleaner import DealerReportCleaner, SubdealerReportCleaner
from data_loader import DataLoadError, load_dataframe, list_files
from validator import ValidationError, validate_non_null, validate_schema, validate_column_types
from utils import configure_logging, ensure_directory


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Excel and CSV cleaning pipeline for dealer and subdealer reports."
    )
    parser.add_argument("--config", help="Path to a JSON configuration file.")
    parser.add_argument("--report-type", choices=["dealer", "subdealer"], default="dealer",
                        help="Type of report to generate.")
    parser.add_argument("--dim-file", help="Path to the DimDealer or DimSubdealer source file.")
    parser.add_argument("--store-file", help="Path to the store master source file.")
    parser.add_argument("--output-dir", default="output", help="Directory where output files are written.")
    parser.add_argument("--batch", action="store_true", help="Process a directory of input files in batch mode.")
    parser.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR).")
    return parser.parse_args(argv)


def merge_config(args: argparse.Namespace, config: AppConfig) -> AppConfig:
    if args.dim_file:
        config.dim_file = args.dim_file
    if args.store_file:
        config.store_file = args.store_file
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.log_level:
        config.log_level = args.log_level
    if args.batch:
        config.batch_mode = True
    return config


def validate_input_files(report_type: str, config: AppConfig) -> None:
    missing = []
    if report_type == "dealer" and not config.dim_file:
        missing.append("--dim-file or DIM_FILE")
    if report_type == "subdealer" and not config.dim_file:
        missing.append("--dim-file or SUBDEALER_FILE")
    if not config.store_file:
        missing.append("--store-file or STORE_FILE")
    if missing:
        raise ValueError(f"Missing required arguments: {', '.join(missing)}")


def build_validators(report_type: str):
    if report_type == "dealer":
        dim_columns = ["Dealer", "DealerCategory", "Division", "DealerTier", "SalesOffice", "ASEPositionCode"]
        store_columns = ["sap_code", "ase_position_code", "category", "dealer_tier", "division2", "sales_office2"]
        schema = {
            "Dealer": "string",
            "DealerCategory": "string",
            "Division": "string",
            "DealerTier": "string",
            "SalesOffice": "string",
            "sap_code": "string",
        }
    else:
        dim_columns = ["Division", "SalesOffice", "ASEPositionCode"]
        store_columns = []
        schema = {"Division": "string", "SalesOffice": "string"}
    return dim_columns, store_columns, schema


def process_report(report_type: str, config: AppConfig) -> None:
    output_dir = ensure_directory(config.output_dir)

    dim_path = Path(config.dim_file)
    if config.batch_mode:
        if not dim_path.is_dir():
            raise ValueError("Batch mode requires --dim-file to be a directory path.")

        input_files = list_files(str(dim_path), config.input_pattern)
        if not input_files:
            raise ValueError(f"No files found in batch directory: {dim_path}")

        for entry in input_files:
            print(f"Processing {entry}")
            dim_df = load_dataframe(str(entry))
            store_df = load_dataframe(config.store_file)
            _process_single_file(report_type, dim_df, store_df, output_dir, entry.stem)
    else:
        dim_df = load_dataframe(str(dim_path))
        store_df = load_dataframe(config.store_file)
        _process_single_file(report_type, dim_df, store_df, output_dir)


def _process_single_file(report_type: str, dim_df, store_df, output_dir: Path, suffix: str = "") -> None:
    dim_cols, store_cols, schema = build_validators(report_type)
    validate_schema(dim_df, dim_cols)
    validate_non_null(dim_df, [col for col in dim_cols if col in dim_df.columns])
    validate_column_types(dim_df, schema)
    if store_cols:
        validate_schema(store_df, store_cols)

    if report_type == "dealer":
        cleaner = DealerReportCleaner(dim_df, store_df)
    else:
        cleaner = SubdealerReportCleaner(dim_df, store_df)

    if suffix:
        output_dir = output_dir / suffix
        output_dir.mkdir(parents=True, exist_ok=True)

    paths = cleaner.export_reports(str(output_dir))
    print("Generated files:")
    for path in paths:
        print(f" - {path}")


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    config = merge_config(args, config)
    logger = configure_logging(config.log_level)
    logger.info("Starting cleaning workflow")

    try:
        validate_input_files(args.report_type, config)
        process_report(args.report_type, config)
        logger.info("Cleaning finished successfully")
        return 0
    except (ValueError, DataLoadError, ValidationError, Exception) as exc:
        logger.exception("Processing failed")
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
