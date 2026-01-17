import tensorflow as tf
import pandas as pd
import numpy as np
import random

# 🔒 Fix randomness (training determinism)
tf.random.set_seed(42)
np.random.seed(42)
random.seed(42)

MODEL_PATH = "trained/memory_model.h5"


def load_data():
    df = pd.read_csv("data/petal_memory.csv")
    X = df.drop("memory_risk", axis=1).values
    y = df["memory_risk"].values
    return X, y


def build_model(input_dim):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(16, activation="relu", input_shape=(input_dim,)),
        tf.keras.layers.Dense(8, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid")
    ])
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    return model


def train():
    X, y = load_data()
    model = build_model(X.shape[1])
    model.fit(X, y, epochs=30, batch_size=8, verbose=1)
    model.save(MODEL_PATH)


def predict_mem(student_input):
    model = tf.keras.models.load_model(MODEL_PATH)
    student_input = np.array(student_input).reshape(1, -1)
    confidence = float(model.predict(student_input)[0][0])

    # Standardized petal output
    return {
        "memory_score": 1 - confidence,
        "memory_risk": int(confidence > 0.5),
        "memory_confidence": confidence
    }

if __name__ == "__main__":
    train()