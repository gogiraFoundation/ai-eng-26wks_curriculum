from __future__ import annotations

import json
from pathlib import Path

import pytest

from extract.invoice_retry import extract_with_retry, parse_invoice

FIX = Path(__file__).parent / "fixtures"
CASE_IDS = [f"{i:02d}" for i in range(1, 16)]


def _json(folder: str, case_id: str) -> dict:
    return json.loads((FIX / folder / f"{case_id}.json").read_text())


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_recorded_case_matches_expected(case_id: str) -> None:
    recorded = json.dumps(_json("recorded", case_id))
    expected = _json("expected", case_id)
    invoice_text = (FIX / "invoices" / f"{case_id}.txt").read_text()

    def generate_fn(prompt: str) -> str:
        return recorded

    invoice, retries = extract_with_retry(invoice_text, generate_fn, max_retries=1)
    assert retries == 0
    assert invoice.invoice_id == expected["invoice_id"]
    assert invoice.vendor == expected["vendor"]
    assert str(invoice.currency) == expected["currency"]
    assert str(invoice.total) == expected["total"]
    assert len(invoice.line_items) == len(expected["line_items"])


def test_parse_invoice_direct() -> None:
    inv = parse_invoice(json.dumps(_json("recorded", "01")))
    assert inv.invoice_id == "INV-1001"