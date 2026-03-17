from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd


APP_DIR = Path(__file__).resolve().parent
MODEL_PATH = APP_DIR / "model.pkl"
TRANSFORMER_PATH = APP_DIR / "transformer.pkl"


def load_artifacts() -> tuple[dict[str, Any], dict[str, Any]]:
    with MODEL_PATH.open("rb") as handle:
        model_bundle = pickle.load(handle)
    with TRANSFORMER_PATH.open("rb") as handle:
        transformer_bundle = pickle.load(handle)
    return model_bundle, transformer_bundle


def customer_to_frame(customer: dict[str, Any], feature_order: list[str], numeric_columns: list[str]) -> pd.DataFrame:
    frame = pd.DataFrame([customer], columns=feature_order)
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def score_customer(
    customer: dict[str, Any],
    model_bundle: dict[str, Any],
    transformer_bundle: dict[str, Any],
) -> dict[str, Any]:
    feature_order = transformer_bundle["feature_order"]
    numeric_columns = transformer_bundle["numeric_columns"]
    transformer = transformer_bundle["transformer"]
    model = model_bundle["model"]
    threshold = model_bundle["threshold"]

    frame = customer_to_frame(customer, feature_order, numeric_columns)
    transformed = transformer.transform(frame)
    probability = float(model.predict_proba(transformed)[:, 1][0])
    prediction = "Yes" if probability >= threshold else "No"
    return {
        "churn_probability": round(probability, 6),
        "churn_prediction": prediction,
        "model_version": model_bundle.get("model_version", "churn-flask"),
    }
