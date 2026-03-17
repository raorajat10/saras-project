from __future__ import annotations

from flask import Flask, jsonify, request

from .utils import load_artifacts, score_customer


app = Flask(__name__)
MODEL_BUNDLE, TRANSFORMER_BUNDLE = load_artifacts()


@app.get("/")
def root():
    return jsonify(
        {
            "message": "Customer Churn API is running.",
            "available_routes": ["/", "/health", "/predict"],
            "model_version": MODEL_BUNDLE.get("model_version"),
        }
    )


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "model_version": MODEL_BUNDLE.get("model_version"),
            "threshold": MODEL_BUNDLE.get("threshold"),
        }
    )


@app.post("/predict")
def predict():
    payload = request.get_json(force=True) or {}
    customer = payload.get("customer", payload)
    result = score_customer(customer, MODEL_BUNDLE, TRANSFORMER_BUNDLE)
    return jsonify(
        {
            "churn_probability": result["churn_probability"],
            "churn_prediction": result["churn_prediction"],
        }
    )


if __name__ == "__main__":
    app.run(host="localhost", port=8000)
