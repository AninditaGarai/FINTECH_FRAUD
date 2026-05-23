from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest

from services.data_profile import clean_numeric_frame


def detect_fraud(df: pd.DataFrame) -> dict[str, float | int | list[dict[str, float | int]]]:
    values = clean_numeric_frame(df)
    if values.empty or len(values) < 2:
        return {"anomalies": 0, "fraud_score": 0.0, "flagged_rows": []}

    contamination = min(0.15, max(0.02, 10 / max(len(values), 1)))
    detector = IsolationForest(contamination=contamination, random_state=42)
    pred = detector.fit_predict(values)
    scores = detector.decision_function(values)
    flagged = []

    for idx, label in enumerate(pred):
        if label == -1:
            flagged.append({"row": int(idx), "anomaly_score": round(float(-scores[idx]), 4)})

    anomalies = len(flagged)
    fraud_score = min(round((anomalies / len(values)) * 500, 2), 100.0)
    return {
        "anomalies": anomalies,
        "fraud_score": fraud_score,
        "flagged_rows": flagged[:25],
    }
