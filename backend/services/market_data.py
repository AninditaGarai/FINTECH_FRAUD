from __future__ import annotations

import pandas as pd


def stock_correlation(symbols: list[str]) -> dict:
    try:
        import yfinance as yf

        prices = yf.download(symbols, period="6mo", progress=False, auto_adjust=True)["Close"]
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(symbols[0])
        corr = prices.pct_change().dropna().corr().round(3)
        return {"symbols": list(corr.columns), "matrix": corr.values.tolist(), "source": "yfinance"}
    except Exception as exc:
        fallback = [[1.0 if i == j else 0.35 for j in range(len(symbols))] for i in range(len(symbols))]
        return {"symbols": symbols, "matrix": fallback, "source": f"fallback: {exc.__class__.__name__}"}
