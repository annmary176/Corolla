import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.multioutput import MultiOutputRegressor
import joblib

DATA_PATH = "data/vectortreeper.csv" # 🔃
MODEL_PATH = "trained/decision_tree_model.pkl" # 🔃

TARGETS = ["dyslexia", "dyscalculia", "dysgraphia", "adhd"]

def load_data():
    df = pd.read_csv(DATA_PATH)

    X = df.drop(TARGETS, axis=1)
    y = df[TARGETS]

    return X, y

def train():
    X, y = load_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    base_model = DecisionTreeRegressor(
        max_depth=5,
        min_samples_leaf=3
    )

    model = MultiOutputRegressor(base_model)
    model.fit(X_train, y_train)

    joblib.dump(model, MODEL_PATH)
    print("Model trained and saved.")


def predict(user_features: dict):
    model = joblib.load(MODEL_PATH)

    df = pd.DataFrame([user_features])

    preds = model.predict(df)[0]

    return {
        "dyslexia": round(float(preds[0]) * 100, 2),
        "dyscalculia": round(float(preds[1]) * 100, 2),
        "dysgraphia": round(float(preds[2]) * 100, 2),
        "adhd": round(float(preds[3]) * 100, 2),
    }


if __name__ == "__main__":
    train()