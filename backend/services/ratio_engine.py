from __future__ import annotations

import math

import pandas as pd

from services.data_profile import find_column


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator in (0, None) or math.isnan(float(denominator)):
        return 0.0
    return float(numerator) / float(denominator)


def _first_value(df: pd.DataFrame, candidates: list[str], fallback: float | None = None) -> float | None:
    col = find_column(df, candidates)
    if col is None:
        return fallback
    value = pd.to_numeric(df[col], errors="coerce").dropna()
    return float(value.iloc[0]) if not value.empty else fallback


def calculate_ratios(df: pd.DataFrame) -> dict[str, float]:
    """Works with conventional statements and the bankruptcy dataset's ratio columns."""
    current_ratio = _first_value(df, ["Current Ratio"])
    debt_ratio = _first_value(df, ["Debt ratio %", "Debt Ratio"])
    profit_margin = _first_value(df, ["Net Income to Total Assets", "Profit Margin"])
    cash_flow_health = _first_value(df, ["Cash Flow to Liability", "CFO to Assets"])
    liquidity = _first_value(df, ["Working Capital to Total Assets", "Current Assets/Total Assets"])

    if current_ratio is None:
        current_assets = _first_value(df, ["CurrentAssets", "Current Assets"])
        current_liabilities = _first_value(df, ["CurrentLiabilities", "Current Liabilities"])
        current_ratio = _safe_divide(current_assets or 0, current_liabilities or 0)

    if debt_ratio is None:
        total_debt = _first_value(df, ["TotalDebt", "Total Debt"])
        total_assets = _first_value(df, ["TotalAssets", "Total Assets"])
        debt_ratio = _safe_divide(total_debt or 0, total_assets or 0)

    if profit_margin is None:
        net_income = _first_value(df, ["NetIncome", "Net Income"])
        revenue = _first_value(df, ["Revenue", "Sales"])
        profit_margin = _safe_divide(net_income or 0, revenue or 0)

    if cash_flow_health is None:
        operating_cash_flow = _first_value(df, ["OperatingCashFlow", "Operating Cash Flow", "Cash flow rate"])
        current_liabilities = _first_value(df, ["CurrentLiabilities", "Current Liability to Assets"])
        cash_flow_health = _safe_divide(operating_cash_flow or 0, current_liabilities or 0)

    ratios = {
        "current_ratio": current_ratio or 0,
        "debt_ratio": debt_ratio or 0,
        "profit_margin": profit_margin or 0,
        "cash_flow_health": cash_flow_health or 0,
        "liquidity_strength": liquidity or 0,
    }
    return {key: round(float(value), 4) for key, value in ratios.items()}


def ratio_trends(df: pd.DataFrame) -> list[dict[str, float | int]]:
    rows = []
    sample = df.head(24)
    for idx in range(len(sample)):
        row_ratios = calculate_ratios(sample.iloc[[idx]])
        rows.append({"period": idx + 1, **row_ratios})
    return rows
