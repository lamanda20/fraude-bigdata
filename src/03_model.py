import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score


# 1. Charger les données
df = pd.read_csv("data/creditcard.csv")

# 2. Séparer features et target
X = df.drop("Class", axis=1)
y = df["Class"]

# 3. Normaliser Time et Amount
scaler = StandardScaler()
X[["Time", "Amount"]] = scaler.fit_transform(X[["Time", "Amount"]])

# 4. Split train / test
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 5. Créer le modèle
model = RandomForestClassifier(
    n_estimators=100,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

# 6. Entraîner le modèle
print("Entraînement du modèle...")
model.fit(X_train, y_train)

# 7. Prédictions avec seuil par défaut 0.5
y_pred_default = model.predict(X_test)

# 8. Probabilités
y_proba = model.predict_proba(X_test)[:, 1]

# 9. Prédictions avec seuil personnalisé 0.3
threshold = 0.3
y_pred_custom = (y_proba > threshold).astype(int)

# 10. Résultats
print("\n=== Résultats avec seuil par défaut 0.5 ===")
print(classification_report(y_test, y_pred_default))

print("\n=== Résultats avec seuil personnalisé 0.3 ===")
print(classification_report(y_test, y_pred_custom))

print("\n=== AUC-ROC ===")
print(roc_auc_score(y_test, y_proba))

# 11. Sauvegarde du modèle et du scaler
joblib.dump(model, "models/fraud_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")

print("\nModèle sauvegardé dans models/fraud_model.pkl")
print("Scaler sauvegardé dans models/scaler.pkl")