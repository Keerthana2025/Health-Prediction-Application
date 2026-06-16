import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Loading the dataset
data = pd.read_csv("patient_data.csv")

# Features added
X = data[['Glucose', 'Haemoglobin', 'Cholesterol']]

# Target
y = data['Condition']

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
joblib.dump(model, "models/health_model.pkl")

print("Model trained successfully!")