import pandas as pd
import joblib

print("Loading model...")

# Load trained model

model = joblib.load("fraud_model.pkl")

# Ask user for CSV file

df = pd.read_csv("PS_20174392719_1491204439457_log.csv.zip")




# Required columns
features = [
    'step',
    'amount',
    'oldbalanceOrg',
    'newbalanceOrig',
    'oldbalanceDest',
    'newbalanceDest'
]

# Check missing columns
missing_cols = [col for col in features if col not in df.columns]

if missing_cols:
    print("Missing columns:", missing_cols)
    exit()

# Prediction
X = df[features]

predictions = model.predict(X)

# Add prediction column
df["Prediction"] = predictions

# Statistics
total = len(predictions)
fraud = int(sum(predictions))
safe = total - fraud

fraud_percentage = round(
    (fraud / total) * 100, 2
) if total > 0 else 0

print("\n===== FRAUD DETECTION RESULTS =====")
print("Total Transactions :", total)
print("Fraud Detected     :", fraud)
print("Safe Transactions  :", safe)
print("Fraud Percentage   :", fraud_percentage, "%")

# Save results
output_file = "prediction_results.csv"
df.to_csv(output_file, index=False)

print("\nResults saved to:", output_file)


