from fastapi import FastAPI
from fastapi.responses import Response
import joblib
import numpy as np
import time

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry
)

app = FastAPI(title="Fraud Detection API")

# Registry Prometheus
registry = CollectorRegistry()

# Charger modèle et scaler
model = joblib.load("models/fraud_model.pkl")
scaler = joblib.load("models/scaler.pkl")

EXPECTED_COLUMNS = [
    "Time", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9",
    "V10", "V11", "V12", "V13", "V14", "V15", "V16", "V17", "V18",
    "V19", "V20", "V21", "V22", "V23", "V24", "V25", "V26", "V27",
    "V28", "Amount"
]

total_requests = 0
fraud_count = 0
total_latency = 0.0

REQUEST_COUNT = Counter(
    "fraud_total_transactions",
    "Total number of processed transactions",
    registry=registry
)

FRAUD_COUNT = Counter(
    "fraud_detected_total",
    "Total number of detected frauds",
    registry=registry
)

LATENCY = Histogram(
    "fraud_request_latency_seconds",
    "Prediction request latency in seconds",
    registry=registry
)

FRAUD_RATE = Gauge(
    "fraud_rate",
    "Current fraud rate",
    registry=registry
)

AVERAGE_LATENCY = Gauge(
    "fraud_average_latency_seconds",
    "Average prediction latency",
    registry=registry
)


@app.get("/")
def home():
    return {
        "message": "Fraud Detection API is running",
        "docs": "/docs",
        "metrics": "/metrics",
        "metrics_json": "/metrics-json"
    }


@app.post("/predict")
def predict(data: dict):
    global total_requests, fraud_count, total_latency

    start_time = time.time()

    try:
        features = [data[col] for col in EXPECTED_COLUMNS]
        features = np.array(features).reshape(1, -1)

        features[:, [0, 29]] = scaler.transform(features[:, [0, 29]])

        proba = model.predict_proba(features)[0][1]

        threshold = 0.3
        prediction = int(proba > threshold)

        latency = time.time() - start_time

        total_requests += 1
        total_latency += latency

        REQUEST_COUNT.inc()
        LATENCY.observe(latency)

        if prediction == 1:
            fraud_count += 1
            FRAUD_COUNT.inc()

        avg_latency = total_latency / total_requests if total_requests > 0 else 0
        fraud_rate = fraud_count / total_requests if total_requests > 0 else 0

        FRAUD_RATE.set(fraud_rate)
        AVERAGE_LATENCY.set(avg_latency)

        return {
            "transaction_id": data.get("transaction_id"),
            "fraud_probability": float(proba),
            "prediction": prediction,
            "latency": latency
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/metrics-json")
def metrics_json():
    avg_latency = total_latency / total_requests if total_requests > 0 else 0
    fraud_rate = fraud_count / total_requests if total_requests > 0 else 0

    return {
        "total_transactions": total_requests,
        "frauds_detected": fraud_count,
        "fraud_rate": fraud_rate,
        "average_latency": avg_latency
    }


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )