import json
import time
import pandas as pd
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

df = pd.read_csv("data/creditcard.csv")

sample_df = pd.concat([
    df[df["Class"] == 0].head(30),
    df[df["Class"] == 1].head(20)
])

for i, row in sample_df.iterrows():
    transaction = row.drop("Class").to_dict()
    transaction["transaction_id"] = int(i)

    producer.send("transactions", transaction)
    producer.flush()

    print(f"Transaction envoyée vers Kafka : {i}")
    time.sleep(0.5)

producer.close()