from __future__ import annotations

import tempfile
from typing import Annotated

import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import get_settings
from database import AnalysisRecord, get_db, init_db
from ml.train_bankruptcy import train
from models.bankruptcy import predict_bankruptcy
from models.fraud import detect_fraud
from models.sentiment import analyze_sentiment
from services.data_profile import profile_dataframe
from services.market_data import stock_correlation
from services.pdf_parser import parse_pdf
from services.ratio_engine import calculate_ratios, ratio_trends
from services.report_generator import build_recommendations, generate_report


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def home() -> dict[str, str]:
    return {"message": settings.app_name, "status": "running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload_csv")
async def upload_csv(
    file: Annotated[UploadFile, File(...)],
    db: Session = Depends(get_db),
) -> dict:
    try:
        df = pd.read_csv(file.file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {exc}") from exc

    profile = profile_dataframe(df)
    ratios = calculate_ratios(df)
    bankruptcy = predict_bankruptcy(df)
    fraud = detect_fraud(df)
    sentiment = analyze_sentiment(file.filename or "Uploaded company")
    recommendations = build_recommendations(ratios, bankruptcy, fraud, sentiment)
    report = generate_report(ratios, bankruptcy, fraud, sentiment)
    trends = ratio_trends(df)

    record = AnalysisRecord(
        filename=file.filename or "upload.csv",
        risk_score=bankruptcy["risk_score"],
        risk_category=bankruptcy["category"],
        fraud_score=fraud["fraud_score"],
        ratios=ratios,
        recommendations=recommendations,
        report=report,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "analysis_id": record.id,
        "profile": profile.__dict__,
        "ratios": ratios,
        "bankruptcy": bankruptcy,
        "fraud": fraud,
        "sentiment": sentiment,
        "recommendations": recommendations,
        "trends": trends,
        "report": report,
    }


@app.post("/upload_pdf")
async def upload_pdf(file: Annotated[UploadFile, File(...)]) -> dict:
    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp:
        temp.write(await file.read())
        temp.flush()
        return parse_pdf(temp.name)


@app.post("/train")
def train_model(dataset_path: str | None = None) -> dict:
    try:
        return train(dataset_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/sentiment/{company}")
def sentiment(company: str, text: str | None = None) -> dict:
    return analyze_sentiment(company, text)


@app.get("/market/correlation")
def correlation(symbols: str = "AAPL,MSFT,JPM,V,MA") -> dict:
    cleaned = [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]
    return stock_correlation(cleaned[:8])


@app.get("/analyses")
def analyses(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).limit(20).all()
    return [
        {
            "id": row.id,
            "filename": row.filename,
            "risk_score": row.risk_score,
            "risk_category": row.risk_category,
            "fraud_score": row.fraud_score,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
