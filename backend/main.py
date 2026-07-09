from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from validator import aggregator

app = FastAPI(title="ESG Carbon Credit Discrepancy Detector")

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:5173", 
                   "http://localhost:3000", 
                   "https://esg-carbon-credit-validator.vercel.app"],  # Vite's default dev server port
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_data() -> pd.DataFrame:
    return pd.read_csv("transactions.csv")

@app.get("/api/summary")
def get_summary():
    df = _load_data()
    report = aggregator(df)
    return {
        "total_transactions": len(df),
        "flagged_rows": len(report),
    }
@app.get("/api/report")
def get_report():
    df = _load_data()
    report = aggregator(df)
    report = report.astype(object).where(pd.notnull(report), None)

    return report.to_dict(orient = 'records')