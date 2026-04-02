# Excel Data Cleaning Python

A lightweight Python pipeline for cleaning dealer and subdealer datasets in CSV or Excel format.

## Project Structure

- `data_cleaning.py` — main CLI entrypoint
- `data_loader.py` — file loading and type dispatch
- `data_cleaner.py` — business logic for dealer/subdealer cleaning and report generation
- `validator.py` — schema, null, and type validation helpers
- `config.py` — environment- and JSON-based configuration handling
- `utils.py` — logging and output helpers
- `requirements.txt` — runtime dependencies
- `.gitignore` — Python project ignore rules

## Installation

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### CLI

Single run for dealer input:

```bash
python data_cleaning.py \
  --report-type dealer \
  --dim-file path/to/DimDealer.csv \
  --store-file path/to/store_master.csv \
  --output-dir output
```

Single run for subdealer input:

```bash
python data_cleaning.py \
  --report-type subdealer \
  --dim-file path/to/DimSubdealer.csv \
  --store-file path/to/store_master.csv \
  --output-dir output
```

### Environment Variables

You can also configure the script with environment variables:

```bash
export DIM_FILE=sample_data/DimDealer.csv
export STORE_FILE=sample_data/store_master.csv
export OUTPUT_DIR=output
export LOG_LEVEL=DEBUG
python data_cleaning.py --report-type dealer
```

### JSON config file

```json
{
  "dim_file": "sample_data/DimDealer.csv",
  "store_file": "sample_data/store_master.csv",
  "output_dir": "output",
  "log_level": "INFO"
}
```

Run with:

```bash
python data_cleaning.py --config config.json --report-type dealer
```

## Output

The pipeline generates three output files for each report type:

- `Dealer_Insert.xlsx` / `Subdealer_Insert.xlsx`
- `Dealer_Incorrect_Data.xlsx` / `Subdealer_Incorrect_Data.xlsx`
- `Dealer_Update.xlsx` / `Subdealer_Update.xlsx`

Each workbook contains clearly named sheets for insert rows, incorrect data, and update mismatches.

## Sample data

Example raw input files are available in `sample_data/`:

- `sample_data/DimDealer_sample.csv`
- `sample_data/store_master_sample.csv`
- `sample_data/DimSubdealer_sample.csv`
- `sample_data/store_master_subdealer_sample.csv`

Generate sample cleaned output with:

```bash
python data_cleaning.py --report-type dealer --dim-file sample_data/DimDealer_sample.csv --store-file sample_data/store_master_sample.csv --output-dir sample_data/cleaned/dealer
python data_cleaning.py --report-type subdealer --dim-file sample_data/DimSubdealer_sample.csv --store-file sample_data/store_master_subdealer_sample.csv --output-dir sample_data/cleaned/subdealer
```

## Testing

Install dev dependencies and run pytest:

```bash
pip install -e .[dev]
pytest
```

## Scheduling

Use `schedule.py` as a cron or Airflow wrapper:

```bash
python schedule.py --report-type dealer --dim-file sample_data/DimDealer_sample.csv --store-file sample_data/store_master_sample.csv --output-dir output
```

A sample cron entry:

```cron
0 2 * * * cd /workspaces/excel-data-cleaning-python && /usr/bin/python3 schedule.py --report-type dealer --dim-file /workspaces/excel-data-cleaning-python/sample_data/DimDealer_sample.csv --store-file /workspaces/excel-data-cleaning-python/sample_data/store_master_sample.csv --output-dir /workspaces/excel-data-cleaning-python/output
```

## Developer tooling

- `pyproject.toml` configures black, ruff, and pytest.
- `.pre-commit-config.yaml` enables formatting and linting checks.
- `schedule.py` provides a simple scheduling wrapper.

## Improvements made

- Modular code split into reusable components
- Explicit validation for schema, nulls, and datatype expectations
- Structured logging using Python `logging`
- Error handling with custom exception classes
- Configurable paths via CLI, environment variables, or JSON config
- Cleaner output generation with reusable `write_excel_report()` helper
- PEP8-friendly style and docstring-friendly structure

## Suggested enhancements

- Add CLI batch mode for directory-wide processing
- Add unit tests for each module
- Add scheduling support with cron or Airflow
- Add a `sample_data/` folder with known good/bad test cases
- Add a `pyproject.toml` and pre-commit hooks for linting and formatting
