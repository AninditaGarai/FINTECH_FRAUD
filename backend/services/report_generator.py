from __future__ import annotations


def build_recommendations(ratios: dict, bankruptcy: dict, fraud: dict, sentiment: dict | None = None) -> list[str]:
    recommendations = []
    if bankruptcy["risk_score"] >= 70:
        recommendations.append("Avoid new exposure until leverage, liquidity, and cash conversion improve.")
    elif bankruptcy["risk_score"] >= 40:
        recommendations.append("Hold or monitor closely; require stronger covenant checks before investing.")
    else:
        recommendations.append("Risk profile is acceptable for further due diligence.")

    if ratios.get("debt_ratio", 0) > 0.55:
        recommendations.append("Debt burden is elevated; inspect repayment schedule and refinancing risk.")
    if ratios.get("cash_flow_health", 0) < 0.2:
        recommendations.append("Cash flow cover is thin; prioritize operating cash flow trend analysis.")
    if fraud.get("fraud_score", 0) > 40:
        recommendations.append("Anomaly score is high; audit source transactions and unusual line items.")
    if sentiment and sentiment.get("label") == "NEGATIVE":
        recommendations.append("External sentiment is negative; watch market and news-driven downside risk.")
    return recommendations


def generate_report(ratios: dict, bankruptcy: dict, fraud: dict, sentiment: dict | None = None) -> str:
    recommendations = build_recommendations(ratios, bankruptcy, fraud, sentiment)
    return f"""Financial Risk Intelligence Report

Overall Risk: {bankruptcy['category']} ({bankruptcy['risk_score']}%)
Model Source: {bankruptcy['model_source']}

Ratio Snapshot
- Current Ratio: {ratios['current_ratio']}
- Debt Ratio: {ratios['debt_ratio']}
- Profitability: {ratios['profit_margin']}
- Cash Flow Health: {ratios['cash_flow_health']}
- Liquidity Strength: {ratios['liquidity_strength']}

Fraud and Anomaly Review
- Fraud Score: {fraud['fraud_score']}%
- Anomalous Rows: {fraud['anomalies']}

Investment View
{chr(10).join(f"- {item}" for item in recommendations)}
"""
