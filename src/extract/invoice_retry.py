# src/extract/invoice_retry.py
"""Parse invoice JSON with at most one repair regenerate."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from schemas.invoice import Invoice

GenerateFn = Callable[[str], str]
# generate_fn(prompt) -> raw model text (may be JSON or noisy JSON)


_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def strip_json_noise(raw: str) -> str:
    """Pull JSON out of common LLM wrappers (markdown fences, preamble)."""
    text = raw.strip()
    fenced = _FENCE_RE.search(text)
    if fenced:
        return fenced.group(1).strip()
    # If there is leading prose, take from first { or [
    for i, ch in enumerate(text):
        if ch in "{[":
            return text[i:]
    return text


def parse_invoice(raw: str) -> Invoice:
    """json.loads + Invoice.model_validate. No retry here."""
    payload: Any = json.loads(strip_json_noise(raw))
    return Invoice.model_validate(payload)


def format_parse_error(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        parts = [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()]
        return "ValidationError: " + "; ".join(parts)
    return f"{type(exc).__name__}: {exc}"


def extract_with_retry(
    document_text: str,
    generate_fn: GenerateFn,
    *,
    max_retries: int = 1,
) -> tuple[Invoice, int]:
    """
    Call generate_fn, parse/validate, retry at most `max_retries` times.

    Returns (invoice, retry_count). With max_retries=1, retry_count is 0 or 1.
    On final failure raises the last JSONDecodeError / ValidationError.
    """
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")

    base_prompt = (
        "Extract an invoice as a single JSON object matching the Invoice schema. "
        "No markdown, no commentary.\n\n"
        f"DOCUMENT:\n{document_text}"
    )

    prompt = base_prompt
    last_exc: Exception | None = None
    retries = 0

    for attempt in range(max_retries + 1):
        raw = generate_fn(prompt)
        try:
            return parse_invoice(raw), retries
        except (json.JSONDecodeError, ValidationError) as exc:
            last_exc = exc
            if attempt >= max_retries:
                break
            retries += 1
            prompt = (
                f"{base_prompt}\n\n"
                "Your previous JSON was invalid. Fix it.\n"
                f"ERROR:\n{format_parse_error(exc)}\n"
                f"PREVIOUS_OUTPUT:\n{raw}"
            )

    assert last_exc is not None
    raise last_exc