from typing import Dict, Iterable, List

import pandas as pd


class ValidationError(Exception):
    pass


def validate_schema(df: pd.DataFrame, expected_columns: Iterable[str]) -> None:
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        raise ValidationError(f"Missing expected columns: {', '.join(missing_columns)}")


def validate_non_null(df: pd.DataFrame, required_columns: Iterable[str]) -> None:
    missing_values = {col: int(df[col].isna().sum()) for col in required_columns if col in df.columns}
    errors = {col: count for col, count in missing_values.items() if count > 0}
    if errors:
        message = ", ".join(f"{col}={count}" for col, count in errors.items())
        raise ValidationError(f"Required non-null columns contain missing values: {message}")


def validate_column_types(df: pd.DataFrame, schema: Dict[str, str]) -> None:
    type_errors = []

    for column, expected_type in schema.items():
        if column not in df.columns:
            continue
        actual_dtype = str(df[column].dtype)
        if expected_type == "string" and not pd.api.types.is_string_dtype(df[column]):
            type_errors.append(f"{column} should be string but is {actual_dtype}")
        elif expected_type == "numeric" and not pd.api.types.is_numeric_dtype(df[column]):
            type_errors.append(f"{column} should be numeric but is {actual_dtype}")

    if type_errors:
        raise ValidationError("Invalid column types: " + "; ".join(type_errors))
