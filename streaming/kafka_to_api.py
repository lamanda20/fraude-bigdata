import json
import csv
import os
import requests
from datetime import datetime
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

url = "http://127.0.0.1:8000/predict"

output_file = "models/predictions.csv"

# Créer le header si le fichier n'existe pas
file_exists = os.path.exists(output_file)

with open(output_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    if not file_exists:
        writer.writerow([
            "timestamp",
            "transaction_id",
            "amount",
            "fraud_probability",
            "prediction",
            "latency"
        ])

    print("Kafka → API ML → Stockage CSV en cours...")

    for message in consumer:
        transaction = message.value

        try:
            response = requests.post(url, json=transaction)
            result = response.json()

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            writer.writerow([
                timestamp,
                transaction.get("transaction_id"),
                transaction.get("Amount"),
                result.get("fraud_probability"),
                result.get("prediction"),
                result.get("latency")
            ])

            f.flush()

            print(
                f"Transaction {transaction.get('transaction_id')} → "
                f"proba={result.get('fraud_probability')} | "
                f"prediction={result.get('prediction')}"
            )

            if result.get("prediction") == 1:
                print(f"🚨 FRAUDE DÉTECTÉE : transaction {transaction.get('transaction_id')}")

        except Exception as e:
            print("Erreur :", e)