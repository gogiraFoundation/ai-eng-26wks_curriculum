from __future__ import annotations

import json
from pathlib import Path

import pytest

from extract.invoice_retry import extract_with_retry, parse_invoice

FIX = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIX / "recorded" / name).read_text())


def test_recorded_case_01_parses_and_matches_expected():
    recorded = json.dumps(_load("01.json"))
    expected = json.loads((FIX / "expected" / "01.json").read_text())

    def generate_fn(prompt: str) -> str:
        return recorded

    invoice, retries = extract_with_retry(
        (FIX / "invoices" / "01.txt").read_text(),
        generate_fn,
        max_retries=1,
    )
    assert retries == 0
    assert invoice.invoice_id == expected["invoice_id"]
    assert invoice.vendor == expected["vendor"]
    assert str(invoice.currency) == expected["currency"]
    assert str(invoice.total) == expected["total"]


def test_parse_invoice_direct():
    raw = json.dumps(_load("01.json"))
    inv = parse_invoice(raw)
    assert inv.invoice_id == "INV-1001"