from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from config import get_settings, project_path
from services.data_profile import clean_numeric_frame, detect_target


settings = get_settings()


def _model_file() -> Path:
    return project_path(settings.model_path)


def _feature_file() -> Path:
    return project_path(settings.feature_path)


def model_available() -> bool:
    return _model_file().exists() and _feature_file().exists()


def _heuristic_probability(df: pd.DataFrame) -> float:
    numeric = clean_numeric_frame(df)
    if numeric.empty:
        return 0.35

    risk = 0.35
    debt_cols = [col for col in numeric.columns if "debt" in col.lower() or "liability" in col.lower()]
    income_cols = [col for col in numeric.columns if "income" in col.lower() or "profit" in col.lower()]
    cash_cols = [col for col in numeric.columns if "cash" in col.lower() or "working capital" in col.lower()]

    if debt_cols:
        risk += min(float(numeric[debt_cols].mean(axis=1).iloc[0]), 1.0) * 0.25
    if income_cols:
        risk -= min(max(float(numeric[income_cols].mean(axis=1).iloc[0]), 0), 1.0) * 0.18
    if cash_cols:
        risk -= min(max(float(numeric[cash_cols].mean(axis=1).iloc[0]), 0), 1.0) * 0.12

    return float(np.clip(risk, 0.02, 0.98))


def predict_bankruptcy(df: pd.DataFrame) -> dict[str, float | str | bool]:
    target = detect_target(df)
    features_df = df.drop(columns=[target]) if target else df
    numeric = clean_numeric_frame(features_df)

    if model_available() and not numeric.empty:
        model = joblib.load(_model_file())
        feature_names = joblib.load(_feature_file())
        aligned = numeric.reindex(columns=feature_names, fill_value=0)
        probability = float(model.predict_proba(aligned.head(1))[0][1])
        source = "trained_xgboost"
    else:
        probability = _heuristic_probability(df)
        source = "heuristic_fallback"

    score = round(probability * 100, 2)
    category = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    return {
        "risk_score": score,
        "category": category,
        "model_source": source,
        "model_available": model_available(),
    }
