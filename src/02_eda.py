import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/creditcard.csv")

print("Valeurs manquantes:")
print(df.isnull().sum().sum())

print("\nStatistiques Amount:")
print(df["Amount"].describe())

print("\nStatistiques Time:")
print(df["Time"].describe())

# 1. Distribution des classes
plt.figure(figsize=(6, 4))
sns.countplot(x="Class", data=df)
plt.title("Distribution des classes : 0 = normale, 1 = fraude")
plt.savefig("models/class_distribution.png")
plt.show()

# 2. Distribution des montants
plt.figure(figsize=(8, 4))
sns.histplot(df["Amount"], bins=50)
plt.title("Distribution des montants")
plt.xlabel("Amount")
plt.savefig("models/amount_distribution.png")
plt.show()

# 3. Montant selon classe
plt.figure(figsize=(6, 4))
sns.boxplot(x="Class", y="Amount", data=df)
plt.title("Montants par classe")
plt.ylim(0, 300)
plt.savefig("models/amount_by_class.png")
plt.show()

print("\nGraphiques sauvegardés dans le dossier models/")