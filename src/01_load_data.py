import pandas as pd

df = pd.read_csv("data/creditcard.csv")

print("Shape:", df.shape)

print("\nColonnes:")
print(df.columns.tolist())

print("\nDistribution des classes:")
print(df["Class"].value_counts())

print("\nPourcentage:")
print(df["Class"].value_counts(normalize=True) * 100)