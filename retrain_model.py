"""
retrain_model.py
────────────────
Retrains risk_model.pkl using your original project_data.csv.
Identical logic to your original training script — fixes the
InconsistentVersionWarning by rebuilding with your current sklearn.

Run from your project root (same folder as project_data.csv):
    python retrain_model.py
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import sklearn

print("=" * 50)
print(f"  sklearn version : {sklearn.__version__}")
print("=" * 50)

# ── Load CSV ──────────────────────────────────────────
df = pd.read_csv("project_data.csv")

print(f"\n  Rows    : {len(df)}")
print(f"  Columns : {list(df.columns)}")
print(f"\n  Label distribution:")
print(df["delayed"].value_counts().to_string())

# ── Features & label ──────────────────────────────────
X = df.drop("delayed", axis=1)
y = df["delayed"]

# ── Same split as original ────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Same model as original ────────────────────────────
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ── Evaluate ──────────────────────────────────────────
y_pred = model.predict(X_test)
print(f"\n  Accuracy : {accuracy_score(y_test, y_pred):.4f}")
print("\n  Classification Report:")
print(classification_report(y_test, y_pred,
      target_names=["On Track", "Delayed"]))

# ── Save ──────────────────────────────────────────────
joblib.dump(model, "risk_model.pkl")
print(f"  ✅  Saved risk_model.pkl  (sklearn {sklearn.__version__})")
print("  ✅  No more version warning — run: python app.py")
print("=" * 50)