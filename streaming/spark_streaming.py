import os

# Configuration Windows / Hadoop
os.environ["HADOOP_HOME"] = "C:\\hadoop"
os.environ["PATH"] = "C:\\hadoop\\bin;" + os.environ["PATH"]

# Charger hadoop.dll
os.add_dll_directory("C:\\hadoop\\bin")

# Connector Kafka pour Spark 3.5.1
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 pyspark-shell"
)

import csv
import requests
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, DoubleType, IntegerType


# 1. Créer Spark Session
spark = SparkSession.builder \
    .appName("FraudDetectionStreaming") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "2") \
    .config("spark.driver.extraJavaOptions", "-Djava.library.path=C:/hadoop/bin") \
    .config("spark.executor.extraJavaOptions", "-Djava.library.path=C:/hadoop/bin") \
    .config("spark.sql.streaming.checkpointLocation", "models/checkpoint") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


# 2. Schéma des transactions
schema = StructType([
    StructField("Time", DoubleType(), True),
    StructField("V1", DoubleType(), True),
    StructField("V2", DoubleType(), True),
    StructField("V3", DoubleType(), True),
    StructField("V4", DoubleType(), True),
    StructField("V5", DoubleType(), True),
    StructField("V6", DoubleType(), True),
    StructField("V7", DoubleType(), True),
    StructField("V8", DoubleType(), True),
    StructField("V9", DoubleType(), True),
    StructField("V10", DoubleType(), True),
    StructField("V11", DoubleType(), True),
    StructField("V12", DoubleType(), True),
    StructField("V13", DoubleType(), True),
    StructField("V14", DoubleType(), True),
    StructField("V15", DoubleType(), True),
    StructField("V16", DoubleType(), True),
    StructField("V17", DoubleType(), True),
    StructField("V18", DoubleType(), True),
    StructField("V19", DoubleType(), True),
    StructField("V20", DoubleType(), True),
    StructField("V21", DoubleType(), True),
    StructField("V22", DoubleType(), True),
    StructField("V23", DoubleType(), True),
    StructField("V24", DoubleType(), True),
    StructField("V25", DoubleType(), True),
    StructField("V26", DoubleType(), True),
    StructField("V27", DoubleType(), True),
    StructField("V28", DoubleType(), True),
    StructField("Amount", DoubleType(), True),
    StructField("transaction_id", IntegerType(), True),
])


# 3. Lire Kafka
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "transactions") \
    .option("startingOffsets", "latest") \
    .load()


# 4. Parser JSON
transactions_df = raw_df.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), schema).alias("data")) \
    .select("data.*")


# 5. Stockage CSV
output_file = "models/spark_predictions.csv"

if not os.path.exists(output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "transaction_id",
            "amount",
            "fraud_probability",
            "prediction",
            "latency"
        ])


# 6. Fonction exécutée à chaque micro-batch Spark
def process_batch(batch_df, batch_id):
    rows = batch_df.collect()

    if len(rows) == 0:
        return

    print(f"\nMicro-batch Spark {batch_id} : {len(rows)} transactions")

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for row in rows:
            transaction = row.asDict()

            try:
                response = requests.post(
                    "http://127.0.0.1:8000/predict",
                    json=transaction
                )

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
                    f"TX {transaction.get('transaction_id')} → "
                    f"proba={result.get('fraud_probability')} | "
                    f"prediction={result.get('prediction')}"
                )

                if result.get("prediction") == 1:
                    print(f"🚨 FRAUDE DÉTECTÉE par Spark : TX {transaction.get('transaction_id')}")

            except Exception as e:
                print("Erreur API :", e)


# 7. Lancer Spark Streaming
query = transactions_df.writeStream \
    .foreachBatch(process_batch) \
    .outputMode("append") \
    .start()

print("Spark Structured Streaming lancé...")
print("En attente des transactions Kafka...")

query.awaitTermination()