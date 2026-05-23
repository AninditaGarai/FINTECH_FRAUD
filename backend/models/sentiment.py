from __future__ import annotations

import os
from functools import lru_cache


POSITIVE = {"growth", "profit", "upgrade", "beat", "strong", "stable", "cash", "improve", "resilient"}
NEGATIVE = {"risk", "loss", "fraud", "debt", "pressure", "default", "bankrupt", "weak", "decline"}


@lru_cache
def _pipeline():
    if os.getenv("ENABLE_TRANSFORMER_SENTIMENT", "false").lower() not in {"1", "true", "yes"}:
        return None
    try:
        from transformers import pipeline

        return pipeline("sentiment-analysis")
    except Exception:
        return None


def analyze_sentiment(company: str, text: str | None = None) -> dict[str, float | str]:
    sample = text or f"{company} faces market pressure but shows improving cash flow and stable operations."
    model = _pipeline()
    if model:
        result = model(sample[:512])[0]
        return {
            "company": company,
            "label": result["label"],
            "score": round(float(result["score"]), 4),
            "source": "transformers",
        }

    words = {word.strip(".,;:!?").lower() for word in sample.split()}
    raw = len(words & POSITIVE) - len(words & NEGATIVE)
    label = "POSITIVE" if raw > 0 else "NEGATIVE" if raw < 0 else "NEUTRAL"
    score = min(abs(raw) / 5, 1.0)
    return {"company": company, "label": label, "score": round(score, 4), "source": "lexicon_fallback"}
