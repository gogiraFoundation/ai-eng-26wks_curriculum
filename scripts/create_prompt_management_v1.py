# scripts/loader.py
#!/usr/bin/env python3
"""Create extract prompt v1 in Prompt Management and Converse once."""

from __future__ import annotations

import json

import boto3
from botocore.config import Config

PROFILE = "agent-toolkit"
REGION = "eu-north-1"
MODEL_ID = "eu.amazon.nova-micro-v1:0"  # inference profile id used in your project

SYSTEM = (
    "You extract invoices into one JSON object only. No markdown fences.\n"
    "Required keys: invoice_id, invoice_date, vendor, currency, total, line_items."
)
# Prompt Management TEXT templates use {{var}} placeholders.
TEMPLATE = SYSTEM + "\n\nDOCUMENT:\n{{document}}"

session = boto3.Session(profile_name=PROFILE, region_name=REGION)
agent = session.client("bedrock-agent", config=Config(retries={"max_attempts": 5, "mode": "adaptive"}))
runtime = session.client("bedrock-runtime", config=Config(retries={"max_attempts": 5, "mode": "adaptive"}))

created = agent.create_prompt(
    name="invoice-extract",
    description="Week 3 Day 18 extract prompt",
    defaultVariant="default",
    variants=[
        {
            "name": "default",
            "modelId": MODEL_ID,
            "templateType": "TEXT",
            "inferenceConfiguration": {"text": {"temperature": 0.0, "maxTokens": 1024}},
            "templateConfiguration": {"text": {"text": TEMPLATE}},
        }
    ],
)
prompt_id = created["id"]
versioned = agent.create_prompt_version(promptIdentifier=prompt_id, description="v1 ship")
arn = versioned["arn"]  # …:prompt/ID:1
print("version ARN:", arn)

sample = (  # tiny smoke doc
    "Invoice INV-1001\nDate: 2026-11-13\nVendor: Acme Inc.\n"
    "Currency: USD\nLine: Product A x1 @ 100.00 = 100.00\nTotal: 100.00"
)
resp = runtime.converse(
    modelId=arn,
    promptVariables={"document": {"text": sample}},
)
print(resp["output"]["message"]["content"][0]["text"])
print(json.dumps(resp.get("usage", {}), indent=2))