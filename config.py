import json
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppConfig:
    dim_file: Optional[str] = None
    subdealer_file: Optional[str] = None
    store_file: Optional[str] = None
    output_dir: str = "output"
    batch_mode: bool = False
    log_level: str = "INFO"
    config_file: Optional[str] = None
    input_pattern: str = "*.csv"


class ConfigError(Exception):
    pass


def _parse_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def load_config(config_file: Optional[str] = None) -> AppConfig:
    config_file = config_file or os.getenv("CLEANING_CONFIG_FILE")
    if config_file:
        if not os.path.exists(config_file):
            raise ConfigError(f"Configuration file not found: {config_file}")
        with open(config_file, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return AppConfig(**data)

    return AppConfig(
        dim_file=os.getenv("DIM_FILE"),
        subdealer_file=os.getenv("SUBDEALER_FILE"),
        store_file=os.getenv("STORE_FILE"),
        output_dir=os.getenv("OUTPUT_DIR", "output"),
        batch_mode=_parse_bool(os.getenv("BATCH_MODE")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        input_pattern=os.getenv("INPUT_PATTERN", "*.csv"),
    )
