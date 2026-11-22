# scripts/create_prompt_management_v2.py
#!/usr/bin/env python3
"""Create extract prompt v2 in Prompt Management and Converse once."""

from __future__ import annotations

import json
import boto3
from botocore.config import Config

PROMPT_ID = "Q080HSE5OV"
MODEL_ID = "eu.amazon.nova-micro-v1:0"
TEMPLATE = (
    "You extract invoices into one JSON object only. No markdown fences.\n"
    "Required keys: invoice_id, invoice_date (YYYY-MM-DD), vendor, currency (USD|EUR|GBP),\n"
    "total (decimal string with 2 places),\n"
    "line_items: array of {description, quantity, unit_price, total} — not product/price.\n"
    "DOCUMENT:\n{{document}}"
)

session = boto3.Session(profile_name="agent-toolkit", region_name="eu-north-1")
agent = session.client(
    "bedrock-agent",
    config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
)

agent.update_prompt(
    promptIdentifier=PROMPT_ID,
    name="invoice-extract",
    defaultVariant="default",
    variants=[
        {
            "name": "default",
            "modelId": MODEL_ID,
            "templateType": "TEXT",
            "inferenceConfiguration": {
                "text": {"temperature": 0.0, "maxTokens": 1024}
            },
            "templateConfiguration": {"text": {"text": TEMPLATE}},
        }
    ],
)
ver = agent.create_prompt_version(
    promptIdentifier=PROMPT_ID,
    description="v2 stricter line_items",
)
print("version ARN:", ver["arn"])
print("version:", ver["version"])