# Customer Churn API

This project deploys a customer churn prediction model as a real-time Flask API and includes a batch scoring script that sends each customer record to the API, saves scored results, and writes monitoring logs.

## Project Structure

```text
customer-churn-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── model.pkl
│   ├── transformer.pkl
│   └── utils.py
├── test_data/
│   ├── sample_input.json
│   └── all_customers.csv
├── batch.py
├── requirements.txt
├── README.md
└── .gitignore
```

## How to Run

From the project root:

```bash
python -m app.main
```

The API listens on `http://localhost:8000`.

To test the batch pipeline:

```bash
python batch.py --input test_data/all_customers.csv
```

This creates `scored_customers.csv` and writes monitoring information to `logs/batch_log.txt`.

## Example Request

Send `test_data/sample_input.json` to `POST /predict`:

```json
{
  "customer": {
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 1,
    "PhoneService": "No",
    "MultipleLines": "No phone service",
    "InternetService": "DSL",
    "OnlineSecurity": "No",
    "OnlineBackup": "Yes",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 29.85,
    "TotalCharges": 29.85,
    "tenure_years": 0.08333333333333333,
    "spend_per_month": 29.85
  }
}
```

## Maintenance Plan

### Retraining

Retrain the model monthly using the newest labeled churn data, or sooner if business behavior changes sharply. The same preprocessing logic used in training must be reused so live and batch predictions stay consistent. Before replacing the deployed model, compare the new model against the previous version on a holdout set and keep the better one. Save the updated `model.pkl`, `transformer.pkl`, and evaluation summary together so the deployment can always be reproduced.

### Drift Detection

Monitor average churn probability, failed requests, and shifts in important input fields such as `tenure`, `MonthlyCharges`, and `TotalCharges`. Compare current batch behavior with the values seen during validation and recent production runs. If prediction rate or average probability moves materially without a business explanation, review the data pipeline, inspect recent customer mix, and rerun evaluation on fresh labeled data.

### Versioning

Version the model and transformer together because they must stay compatible. Every deployment should record the training date, evaluation metrics, threshold, and input schema. Keep older pickles so rollback is immediate if a new release causes unstable predictions. Document each update in the repo with a short note describing what changed, why it changed, and how the new model performed against the previous version.
