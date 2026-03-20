from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd


LOGS_DIR = Path("logs")
OUTPUT_PATH = Path("scored_customers.csv")
API_URL = "http://localhost:8000/predict"


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def configure_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(LOGS_DIR / "batch_log.txt", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(file_handler)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging()
    logging.info("Batch scoring started for input: %s", args.input)

    frame = pd.read_csv(args.input)
    if "Unnamed: 0" in frame.columns:
        frame = frame.drop(columns=["Unnamed: 0"])

    feature_columns = [column for column in frame.columns if column not in {"Churn", "customerID"}]
    results = []
    probabilities = []
    failures = 0

    total_rows = len(frame)

    for index, (_, row) in enumerate(frame.iterrows(), start=1):
        customer = {column: row[column] for column in feature_columns}
        payload = {"customer": customer}
        try:
            response = post_json(API_URL, payload)
            probabilities.append(response["churn_probability"])
            result_row = row.to_dict()
            result_row["churn_probability"] = response["churn_probability"]
            result_row["churn_prediction"] = response["churn_prediction"]
            results.append(result_row)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            failures += 1
            logging.exception("Failed prediction for customerID=%s: %s", row.get("customerID"), exc)

        if index == 1 or index % 10 == 0 or index == total_rows:
            logging.info("Processed %s/%s customers", index, total_rows)

    pd.DataFrame(results).to_csv(OUTPUT_PATH, index=False)

    average_probability = round(sum(probabilities) / len(probabilities), 4) if probabilities else 0.0
    logging.info("Total requests: %s", len(frame))
    logging.info("Failures: %s", failures)
    logging.info("Average churn probability: %s", average_probability)


if __name__ == "__main__":
    try:
        main()
    finally:
        logging.shutdown()
