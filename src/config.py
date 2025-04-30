# src/config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_EPW_DIR = BASE_DIR / 'raw' / 'epw_raw'
RAW_INMET_DIR = BASE_DIR / 'raw' / 'inmet_raw'
EXPORT_DIR = BASE_DIR / 'raw' / 'climate_csv'
