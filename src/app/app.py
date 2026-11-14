# src/app.py
from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from extract.invoice_retry import extract_with_retry
from schemas.invoice import Invoice

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("extract")

app = FastAPI(title="invoice-extract", version="0.1.0")


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw invoice text")


def stub_generate(prompt: str) -> str:
    """Day 11 local stub: always return a schema-valid invoice JSON."""
    return json.dumps(
        {
            "invoice_id": "INV-1001",
            "invoice_date": "2026-11-13",
            "vendor": "Acme Inc.",
            "currency": "USD",
            "total": "100.00",
            "line_items": [
                {
                    "description": "Product A",
                    "quantity": 1,
                    "unit_price": "100.00",
                    "total": "100.00",
                }
            ],
        }
    )


@app.post("/extract", response_model=Invoice)
def extract(body: ExtractRequest) -> Invoice:
    request_id = str(uuid.uuid4())
    try:
        invoice, retries = extract_with_retry(
            body.text,
            stub_generate,
            max_retries=1,
        )
    except Exception as exc:
        log.info(
            json.dumps(
                {
                    "event": "extract_failed",
                    "request_id": request_id,
                    "retries": 1,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
        )
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    log.info(
        json.dumps(
            {
                "event": "extract_ok",
                "request_id": request_id,
                "retries": retries,
                "invoice_id": invoice.invoice_id,
            }
        )
    )
    return invoice
    