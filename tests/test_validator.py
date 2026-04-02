import pandas as pd
import pytest

from validator import ValidationError, validate_column_types, validate_non_null, validate_schema


def test_validate_schema_raises_for_missing_column():
    df = pd.DataFrame({"a": [1]})

    with pytest.raises(ValidationError, match="Missing expected columns"):
        validate_schema(df, ["a", "b"])


def test_validate_non_null_raises_for_missing_values():
    df = pd.DataFrame({"a": [1, None], "b": ["x", "y"]})

    with pytest.raises(ValidationError, match="a=1"):
        validate_non_null(df, ["a", "b"])


def test_validate_column_types_detects_mismatch():
    df = pd.DataFrame({"a": ["x", "y"], "b": [1, 2]})

    with pytest.raises(ValidationError, match="a should be numeric"):
        validate_column_types(df, {"a": "numeric", "b": "string"})


def test_validate_column_types_accepts_valid_types():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})

    validate_column_types(df, {"a": "numeric", "b": "string"})
