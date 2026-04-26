# Fraud Detection Project Run Guide

This project has four main parts:

- **FastAPI API**: loads the fraud model and exposes prediction endpoints.
- **Kafka + ZooKeeper**: runs the message broker used for streaming transactions.
- **Kafka consumer**: reads transactions from Kafka, calls the API, and saves predictions.
- **Kafka producer**: sends sample transactions from the CSV dataset into Kafka.

## First-Time Setup

Run these commands once when setting up the project on a new machine.

```powershell
cd "C:\Users\l\Desktop\Genie Info\projects\Big Data\app\fraude-bigdata"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

What they do:

- `cd ...` moves the terminal into the project folder.
- `python -m venv .venv` creates a local Python virtual environment.
- `.\.venv\Scripts\Activate.ps1` activates the virtual environment.
- `pip install -r requirements.txt` installs the Python packages needed by the project.

You also need Docker Desktop installed and running.

After Docker Desktop is ready, start Kafka and ZooKeeper:

```powershell
docker compose up -d
```

The `-d` option runs the containers in the background.

## Required Data File

The API can run with the existing model files in `models/`.

The producer requires this file:

```text
data/creditcard.csv
```

If that file is missing, `python streaming\kafka_producer.py` will fail.

## Daily Commands

Every time you open a new terminal for this project, run:

```powershell
cd "C:\Users\l\Desktop\Genie Info\projects\Big Data\app\fraude-bigdata"
.\.venv\Scripts\Activate.ps1
```

Each new terminal needs the virtual environment activated again.

Then make sure Docker services are running:

```powershell
docker compose up -d
```

You can check them with:

```powershell
docker compose ps
```

## Normal Run Order

Use three terminals after Kafka is running.

### Terminal 1: Start the API

```powershell
python -m uvicorn api.app:app --reload
```

Wait until you see something like:

```text
Uvicorn running on http://127.0.0.1:8000
```

Keep this terminal open. The API is a server, so it does not finish by itself.

You can test it in the browser:

```text
http://127.0.0.1:8000/docs
```

### Terminal 2: Start the Kafka Consumer

```powershell
python streaming\kafka_to_api.py
```

Conditions before running this:

- Docker services should be running.
- The API should already be running.

This script listens for Kafka messages forever, so it does not finish by itself.

Keep this terminal open.

### Terminal 3: Run the Kafka Producer

```powershell
python streaming\kafka_producer.py
```

Conditions before running this:

- Docker services should be running.
- The API should be running.
- The consumer should be running.
- `data/creditcard.csv` should exist.

This script sends sample transactions to Kafka, then finishes.

## Full Run Sequence

```text
1. docker compose up -d
2. python -m uvicorn api.app:app --reload
3. python streaming\kafka_to_api.py
4. python streaming\kafka_producer.py
```

Do not wait for the API or consumer to finish. They are meant to stay open.

Only wait until they are ready, then continue in another terminal.

## When You Are Done

Stop the API and consumer terminals with:

```text
Ctrl + C
```

Stop Kafka and ZooKeeper:

```powershell
docker compose down
```

## Useful Checks

Check Docker services:

```powershell
docker compose ps
```

Check recent predictions:

```powershell
Get-Content models\predictions.csv -Tail 10
```

Check the API documentation:

```text
http://127.0.0.1:8000/docs
```
