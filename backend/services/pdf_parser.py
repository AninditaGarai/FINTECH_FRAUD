from __future__ import annotations

import re

import pdfplumber


PATTERNS = {
    "revenue": r"(?:revenue|sales)\s*[:\-]?\s*[$]?\s*([\d,]+(?:\.\d+)?)",
    "debt": r"(?:debt|borrowings)\s*[:\-]?\s*[$]?\s*([\d,]+(?:\.\d+)?)",
    "net_income": r"(?:net income|profit after tax)\s*[:\-]?\s*[$]?\s*([\d,]+(?:\.\d+)?)",
    "current_assets": r"current assets\s*[:\-]?\s*[$]?\s*([\d,]+(?:\.\d+)?)",
    "current_liabilities": r"current liabilities\s*[:\-]?\s*[$]?\s*([\d,]+(?:\.\d+)?)",
}


def _number(value: str) -> float:
    return float(value.replace(",", ""))


def parse_pdf(path: str) -> dict[str, list[float] | str]:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += "\n" + (page.extract_text() or "")

    extracted: dict[str, list[float] | str] = {"raw_text_preview": text[:1000]}
    for key, pattern in PATTERNS.items():
        extracted[key] = [_number(match) for match in re.findall(pattern, text, flags=re.IGNORECASE)]
    return extracted
