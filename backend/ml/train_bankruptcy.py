from __future__ import annotations

import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from config import project_path
from services.data_profile import clean_numeric_frame, detect_target


def candidate_paths() -> list[Path]:
    paths = []
    if os.getenv("DATASET_PATH"):
        paths.append(Path(os.environ["DATASET_PATH"]))
    paths.extend(
        [
            project_path("data", "data.csv"),
            Path(r"C:\Users\USER\Downloads\archive (2)\data.csv"),
        ]
    )
    return paths


def resolve_dataset() -> Path:
    for path in candidate_paths():
        if path.exists():
            return path
    raise FileNotFoundError("Could not find data.csv. Set DATASET_PATH or put it in backend/data/data.csv.")


def train(dataset_path: str | None = None) -> dict:
    path = Path(dataset_path) if dataset_path else resolve_dataset()
    data = pd.read_csv(path)
    target = detect_target(data)
    if target is None:
        raise ValueError("Training dataset needs a target column such as 'Bankrupt?'.")

    y = data[target].astype(int)
    x = clean_numeric_frame(data.drop(columns=[target]))
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    negative, positive = y_train.value_counts().sort_index().tolist()
    scale_pos_weight = negative / max(positive, 1)
    model = XGBClassifier(
        n_estimators=350,
        max_depth=4,
        learning_rate=0.04,
        subsample=0.9,
        colsample_bytree=0.85,
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight,
        random_state=42,
    )
    model.fit(x_train, y_train)

    probability = model.predict_proba(x_test)[:, 1]
    prediction = (probability >= 0.5).astype(int)
    auc = roc_auc_score(y_test, probability)

    model_path = project_path("models", "bankruptcy_model.pkl")
    feature_path = project_path("models", "bankruptcy_features.pkl")
    joblib.dump(model, model_path)
    joblib.dump(x.columns.tolist(), feature_path)

    return {
        "dataset": str(path),
        "rows": int(len(data)),
        "features": int(len(x.columns)),
        "roc_auc": round(float(auc), 4),
        "report": classification_report(y_test, prediction, output_dict=True),
        "model_path": str(model_path),
    }


if __name__ == "__main__":
    print(train())
