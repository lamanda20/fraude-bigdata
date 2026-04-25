from fastapi import FastAPI
import joblib
import numpy as np
import time

app = FastAPI(title="Fraud Detection API")

# Charger modèle et scaler
model = joblib.load("models/fraud_model.pkl")
scaler = joblib.load("models/scaler.pkl")

# Variables de monitoring
total_requests = 0
fraud_count = 0
total_latency = 0.0


@app.get("/")
def home():
    return {
        "message": "Fraud Detection API is running"
    }


@app.post("/predict")
def predict(data: dict):
    global total_requests, fraud_count, total_latency

    start_time = time.time()

    try:
        expected_columns = [
            "Time", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9",
            "V10", "V11", "V12", "V13", "V14", "V15", "V16", "V17", "V18",
            "V19", "V20", "V21", "V22", "V23", "V24", "V25", "V26", "V27",
            "V28", "Amount"
        ]

        features = [data[col] for col in expected_columns]
        features = np.array(features).reshape(1, -1)

        # Normaliser Time et Amount
        features[:, [0, 29]] = scaler.transform(features[:, [0, 29]])

        # Prédiction
        proba = model.predict_proba(features)[0][1]

        # Seuil optimisé
        threshold = 0.3
        prediction = int(proba > threshold)

        latency = time.time() - start_time

        # Mise à jour monitoring
        total_requests += 1
        total_latency += latency

        if prediction == 1:
            fraud_count += 1

        return {
            "transaction_id": data.get("transaction_id"),
            "fraud_probability": float(proba),
            "prediction": prediction,
            "latency": latency
        }

    except Exception as e:
        return {
            "error": str(e)
        }


@app.get("/metrics")
def metrics():
    avg_latency = total_latency / total_requests if total_requests > 0 else 0
    fraud_rate = fraud_count / total_requests if total_requests > 0 else 0

    return {
        "total_transactions": total_requests,
        "frauds_detected": fraud_count,
        "fraud_rate": fraud_rate,
        "average_latency": avg_latency
    }