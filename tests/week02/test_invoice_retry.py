import json
from datetime import date

import pytest
from extract.invoice_retry import extract_with_retry

VALID = {
    "invoice_id": "INV-1",
    "invoice_date": str(date.today()),
    "vendor": "Acme",
    "currency": "USD",
    "total": "10.00",
    "line_items": [
        {"description": "A", "quantity": 1, "unit_price": "10.00", "total": "10.00"}
    ],
}


def test_one_retry_fixes_malformed_json():
    calls: list[str] = []

    def generate_fn(prompt: str) -> str:
        calls.append(prompt)
        if len(calls) == 1:
            return "{'vendor': 'Acme'}"  # invalid JSON (Python dict literal)
        return json.dumps(VALID)

    invoice, retries = extract_with_retry("Invoice text…", generate_fn, max_retries=1)
    assert retries == 1
    assert len(calls) == 2
    assert "ERROR:" in calls[1]
    assert invoice.vendor == "Acme"


def test_exhausted_retries_raise():
    def generate_fn(prompt: str) -> str:
        return "{not json"

    with pytest.raises(json.JSONDecodeError):
        extract_with_retry("doc", generate_fn, max_retries=1)