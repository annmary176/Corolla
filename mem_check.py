import numpy as np
from tensorflow.keras.models import load_model

MODEL_PATH = r"C:\Users\joyal\OneDrive\Documents\Corolla\trained\memory_model.h5"
model = load_model(MODEL_PATH)

def predict_from_values(recall_acc, response_time, sequence, error_count):
    """
    Hard-coded input prediction
    """

    # Shape must be (1, number_of_features)
    input_data = np.array([
        [recall_acc, response_time, sequence, error_count]
    ])

    prediction = model.predict(input_data)

    # If model outputs probability
    score = float(prediction[0][0] * 100)

    if score > 75:
        risk = "Low"
    elif score > 40:
        risk = "Medium"
    else:
        risk = "High"

    return {
        "memory_percentage": round(score, 2),
        "memory_risk": risk,
        "memory_confidence": "High"
    }