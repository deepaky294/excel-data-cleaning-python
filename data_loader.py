import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional


class DataLoadError(Exception):
    pass


def load_dataframe(path: str, dtype: Optional[Dict[str, Any]] = None, usecols: Optional[List[str]] = None) -> pd.DataFrame:
    path_obj = Path(path)
    if not path_obj.exists():
        raise DataLoadError(f"File not found: {path}")

    suffix = path_obj.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path_obj, dtype=dtype, usecols=usecols, low_memory=False)
    if suffix in {".xls", ".xlsx"}:
        return pd.read_excel(path_obj, dtype=dtype, usecols=usecols)

    raise DataLoadError(f"Unsupported file type: {suffix}")


def list_files(directory: str, pattern: str = "*.csv") -> List[Path]:
    path_obj = Path(directory)
    if not path_obj.exists() or not path_obj.is_dir():
        raise DataLoadError(f"Input directory not found: {directory}")
    return sorted(path_obj.glob(pattern))
