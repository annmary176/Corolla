from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import os
from typing import Dict

app = FastAPI()

# Paths - Ensure these directories exist
MODEL_PATH = "trained/decision_tree_model.pkl"
TARGETS = ["dyslexia", "dyscalculia", "dysgraphia", "adhd"]

class TestData(BaseModel):
    # Features used by the decision tree
    reading_score: float
    logic_score: float
    writing_score: float
    memory_score: float
    reading_time: float
    logic_time: float
    writing_time: float
    memory_time: float

@app.post("/predict-results")
async def get_prediction(data: TestData):
    if not os.path.exists(MODEL_PATH):
        # Fallback logic if model file is missing during dev
        avg_score = (data.reading_score + data.logic_score + data.writing_score + data.memory_score) / 4
        return {
            "performance_level": "High" if avg_score > 75 else "Moderate" if avg_score > 40 else "Low",
            "overall_avg": round(avg_score, 2),
            "petals": {
                "dyslexia": 15.0,
                "dyscalculia": 20.0,
                "dysgraphia": 10.0,
                "adhd": 5.0
            },
            "status": "using_fallback"
        }
    
    try:
        model = joblib.load(MODEL_PATH)
        user_features = data.dict()
        df = pd.DataFrame([user_features])
        preds = model.predict(df)[0]
        
        avg_score = (data.reading_score + data.logic_score + data.writing_score + data.memory_score) / 4
        
        return {
            "performance_level": "High" if avg_score > 75 else "Moderate" if avg_score > 40 else "Low",
            "overall_avg": round(avg_score, 2),
            "petals": {
                "dyslexia": round(float(preds[0]) * 100, 2),
                "dyscalculia": round(float(preds[1]) * 100, 2),
                "dysgraphia": round(float(preds[2]) * 100, 2),
                "adhd": round(float(preds[3]) * 100, 2),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)