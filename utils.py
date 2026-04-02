import logging
from pathlib import Path
from typing import Dict

import pandas as pd


DEFAULT_LOG_FORMAT = "[%(asctime)s] %(levelname)s:%(name)s: %(message)s"


def configure_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("excel_data_cleaning")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level.upper())
    return logger


def ensure_directory(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_excel_report(file_path: str, sheets: Dict[str, pd.DataFrame], engine: str = "openpyxl") -> None:
    file_path = Path(file_path)
    with pd.ExcelWriter(file_path, engine=engine) as writer:
        for sheet_name, sheet_df in sheets.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
