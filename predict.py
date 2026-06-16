import joblib

model = joblib.load("models/health_model.pkl")

def predict_health(glucose, haemoglobin, cholesterol):

    prediction = model.predict(
        [[glucose, haemoglobin, cholesterol]]
    )

    return prediction[0]