import joblib
import pandas as pd
import numpy as np
import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

try:
    model = joblib.load('saved_models/nepal_fraud_rf_model.joblib')
except Exception as e:
    print(f"CRITICAL ERROR: Could not load model. Error: {e}")

app = FastAPI(title="BuddhaAI: API Gateway")

class TransactionInput(BaseModel):
    step: int
    type: str  # 'PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT'
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float

def log_to_abc_db(data, prob, verdict, risk, reason):
    try:
        conn = sqlite3.connect('abc.db')
        c = conn.cursor()
        c.execute('''INSERT INTO txn_logs 
                     (step, type, amount, oldbalanceOrg, newbalanceOrig, 
                      oldbalanceDest, newbalanceDest, fraud_probability, 
                      prediction, risk_level) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data.step, data.type, data.amount, data.oldbalanceOrg, data.newbalanceOrig, 
                   data.oldbalanceDest, data.newbalanceDest, prob, verdict, risk))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Logging Error: {e}")

@app.post("/predict")
def analyze_transaction(data: TransactionInput):
    amount_log = np.log1p(data.amount)
    
    errorBalanceOrig = data.newbalanceOrig + data.amount - data.oldbalanceOrg
    errorBalanceDest = data.oldbalanceDest + data.amount - data.newbalanceDest
    
    type_mapping = {'CASH_OUT': 0, 'DEBIT': 0, 'PAYMENT': 0, 'TRANSFER': 0}
    if data.type in type_mapping:
        type_mapping[data.type] = 1

    input_data = pd.DataFrame([{
        'step': data.step,
        'oldbalanceOrg': data.oldbalanceOrg,
        'newbalanceOrig': data.newbalanceOrig,
        'oldbalanceDest': data.oldbalanceDest,
        'newbalanceDest': data.newbalanceDest,
        'errorBalanceOrig': errorBalanceOrig,
        'errorBalanceDest': errorBalanceDest,
        'amount_log': amount_log,
        'type_CASH_OUT': type_mapping['CASH_OUT'],
        'type_DEBIT': type_mapping['DEBIT'],
        'type_PAYMENT': type_mapping['PAYMENT'],
        'type_TRANSFER': type_mapping['TRANSFER']
    }])

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    verdict = "FRAUD" if prediction == 1 else "LEGITIMATE"
    
    if probability > 0.8:
        risk = "High"
        reason = "High probability pattern matched known theft behavior."
    elif probability > 0.4:
        risk = "Medium"
        reason = "Unusual activity detected. Secondary verification suggested."
    else:
        risk = "Low"
        reason = "Transaction behavior consistent with legitimate historical data."

    log_to_abc_db(data, float(probability), verdict, risk, reason)

    return {
        "verdict": verdict,
        "probability": round(float(probability), 4),
        "risk": risk,
        "reason": reason
    }

@app.get("/status")
def system_status():
    return {"status": "Active", "engine": "Random Forest v1.0", "location": "Nepal Local Server"}