from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd


TARGET_COLUMNS = {"bankrupt?", "bankrupt", "is_bankrupt", "default", "label"}


@dataclass
class DataProfile:
    row_count: int
    column_count: int
    numeric_columns: list[str]
    target_column: str | None
    missing_values: int


def normalize_column(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {normalize_column(col): col for col in df.columns}
    for candidate in candidates:
        key = normalize_column(candidate)
        if key in normalized:
            return normalized[key]
    return None


def detect_target(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if normalize_column(col) in TARGET_COLUMNS:
            return col
    return None


def profile_dataframe(df: pd.DataFrame) -> DataProfile:
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    return DataProfile(
        row_count=int(len(df)),
        column_count=int(len(df.columns)),
        numeric_columns=numeric_columns,
        target_column=detect_target(df),
        missing_values=int(df.isna().sum().sum()),
    )


def clean_numeric_frame(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan)
    return numeric.fillna(numeric.median(numeric_only=True)).fillna(0)
