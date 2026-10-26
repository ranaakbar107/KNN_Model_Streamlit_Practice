from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import joblib
import numpy as np

# The model lives in this dict so your routes can reach it after startup.
ml_model = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO 1: Load "model.pkl" at startup
    ml_model["predictor"] = joblib.load("model.pkl")

    yield

    # TODO 2: Clear the model on shutdown
    ml_model.clear()


app = FastAPI(title="Diabetes Risk API", lifespan=lifespan)


# ── Request shape: what the caller SENDS ─────────────────────────────────────
class PatientFeatures(BaseModel):
    # TODO 3: Declare the 8 fields in exact training order
    Pregnancies: int
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: int


# ── Response shape: what you SEND BACK ───────────────────────────────────────
class PredictionResult(BaseModel):
    # TODO 4: Declare the three response fields
    prediction: int
    result_label: str
    confidence: float


@app.get("/")
def health():
    # Health check endpoint
    return {"status": "running", "model_loaded": "predictor" in ml_model}


@app.post("/predict", response_model=PredictionResult)
def predict(features: PatientFeatures):
    model = ml_model.get("predictor")
    if model is None:
        # TODO 5: Raise HTTPException if model is not loaded
        raise HTTPException(status_code=503, detail="Model not loaded")

    # TODO 6: Build 2D input array in the exact training column order
    X = np.array([[
        features.Pregnancies,
        features.Glucose,
        features.BloodPressure,
        features.SkinThickness,
        features.Insulin,
        features.BMI,
        features.DiabetesPedigreeFunction,
        features.Age
    ]])

    # TODO 7: Get the prediction (0 or 1)
    pred = int(model.predict(X)[0])

    # TODO 8: Get the confidence (probability of the predicted class)
    conf = round(float(model.predict_proba(X)[0][pred]), 3)

    # TODO 9: Return the structured PredictionResult
    label = "Diabetic" if pred == 1 else "Not Diabetic"
    
    return PredictionResult(
        prediction=pred,
        result_label=label,
        confidence=conf
    )