"""
FastAPI REST API for Fraud Detection
Use this when you want to expose the model to other applications
like ICICI Bank's backend system
"""
import os
import sys
import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))
from predict import load_model, predict

app = FastAPI(
    title="Fraud Detection API",
    description="MLOps Course — Suresh D R | AI Product Developer",
    version="1.0.0"
)

@app.on_event("startup")
def load():
    global model
    model = load_model("models/fraud_model.pkl")

class Transaction(BaseModel):
    amount: float
    hour: int
    day_of_week: int
    merchant_type: str
    customer_age: int
    num_prev_txns: int
    avg_txn_amount: float

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    risk_level: str

@app.get("/")
def root():
    return {"message": "Fraud Detection API is running", "status": "healthy"}

@app.get("/health")
def health():
    return {"status": "healthy", "model": "loaded"}

@app.post("/predict", response_model=PredictionResponse)
def predict_fraud(txn: Transaction):
    result = predict(model, txn.dict())
    return PredictionResponse(
        prediction=result["prediction"],
        confidence=result["confidence"],
        risk_level=result["risk_level"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
