"""데이터 로딩 유틸리티."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_policies() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "policies.csv")


def load_energy_stats() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "energy_stats.csv")


def load_energy_news() -> list[str]:
    path = DATA_DIR / "energy_news.txt"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
