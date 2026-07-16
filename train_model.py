import pandas as pd
import joblib
import json

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

print("Loading dataset...")

# Load dataset
df = pd.read_csv("PS_20174392719_1491204439457_log.csv.zip")

print("Dataset loaded successfully!")

# Keep all fraud cases
fraud_df = df[df['isFraud'] == 1]

# Sample safe cases
safe_df = df[df['isFraud'] == 0].sample(
    n=500000,
    random_state=42
)

# Combine both
df = pd.concat([fraud_df, safe_df])

# Shuffle dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df = pd.get_dummies(df, columns=["type"], drop_first=True)
# ================= FEATURE ENGINEERING =================

df["orgDiff"] = df["oldbalanceOrg"] - df["newbalanceOrig"]
df["destDiff"] = df["newbalanceDest"] - df["oldbalanceDest"]


print(df['isFraud'].value_counts())

print("Using 500,000 records")

# Features
X = df[
    [
        'step',
        'amount',
        'oldbalanceOrg',
        'newbalanceOrig',
        'oldbalanceDest',
        'newbalanceDest',
        'orgDiff',
        'destDiff',
        'type_CASH_OUT',
        'type_DEBIT',
        'type_PAYMENT',
        'type_TRANSFER'
    ]
]
# Target
y = df['isFraud']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ================= MODELS =================

models = {
    "Random Forest": RandomForestClassifier(
    
    n_estimators=500,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features=0.7,
    class_weight="balanced_subsample",
    bootstrap=True,
    random_state=42,
    n_jobs=-1

    ),
    "Decision Tree": DecisionTreeClassifier(
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=42
    ),

    "Extra Trees": ExtraTreesClassifier(
    n_estimators=300,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
    )
}


results = {}

best_model = None
best_model_name = ""
best_f1 = -1

print("\nTraining Models...\n")

for name, model in models.items():

    print(f"Training {name}...")

    model.fit(X_train, y_train)
    train_pred = model.predict(X_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)

    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, y_pred)

    print(f"Train Accuracy : {train_acc*100:.2f}%")
    print(f"Test Accuracy  : {test_acc*100:.2f}%")
    print(f"Gap            : {(train_acc-test_acc)*100:.2f}%")

    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    results[name] = {
        "accuracy": round(accuracy * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1 * 100, 2),
        "roc_auc": round(auc, 4)
    }

    print("\n" + "=" * 30)
    print(name)
    print("=" * 30)
    print(f"Accuracy : {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall   : {recall * 100:.2f}%")
    print(f"F1 Score : {f1 * 100:.2f}%")
    print(f"ROC AUC  : {auc:.4f}")

    # Select best model using F1 Score
    if f1 > best_f1:
        best_f1 = f1
        best_model = model
        best_model_name = name

# ================= SAVE BEST MODEL =================

joblib.dump(best_model, "fraud_model.pkl")

importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": best_model.feature_importances_
})

print(importance.sort_values(by="Importance", ascending=False))
print("\n" + "=" * 40)
print(f"BEST MODEL SELECTED : {best_model_name}")
print("=" * 40)

best_metrics = results[best_model_name]
fraud_cases = int(y.sum())
safe_cases = int(len(y) - y.sum())
# Save metrics
metrics = {
    "best_model": best_model_name,
    "accuracy": best_metrics["accuracy"],
    "precision": best_metrics["precision"],
    "recall": best_metrics["recall"],
    "f1_score": best_metrics["f1_score"],
    "all_models": results,
    "fraud_cases": fraud_cases,
    "safe_cases": safe_cases,
}

with open("metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

print("\nfraud_model.pkl saved successfully!")
print("metrics.json saved successfully!")

print("\nTraining Completed Successfully!")