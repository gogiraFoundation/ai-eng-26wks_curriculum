# Day 18 lab log: prompt versioning and Bedrock Prompt Management

**Syllabus:** Day 18 · Thu 12 Nov 2026 · Prompt versioning and Bedrock Prompt Management  
**Time:** 75 min (20m docs · 40m YAML + Prompt Management · 15m pros/cons)  
**Deliverable:** Loader by name+version; one Prompt Management version invoked from code  
**Theory:** [day18_notes.md](./day18_notes.md)  
**Region:** `eu-north-1` · model: `eu.amazon.nova-micro-v1:0`

## Task status

- [ ] Read Bedrock Prompt Management docs
- [ ] `src/prompts/extract/v1.yaml` and `v2.yaml` with metadata
- [ ] Loader: select prompt by name + version from config
- [ ] Create prompt + version in Prompt Management; invoke via Converse
- [ ] Pros/cons of files vs Prompt Management
- [ ] Self-check: roll back a bad prompt in under a minute

## Check yourself

**How do you roll back a bad prompt version in under a minute?**

> Files: point config at the previous version id (`v1`) and redeploy/restart.  
> Prompt Management: set `modelId` / config ARN to the previous version ARN (`…:prompt/ID:1` instead of `:2`) and redeploy; draft keeps iterating without touching prod.

## Task status
- [x] Read Bedrock Prompt Management docs
- [x] `src/prompts/extract/v1.yaml` and `v2.yaml` with metadata
- [x] Loader: select prompt by name + version from config
- [x] Create prompt + version in Prompt Management; invoke via Converse
- [x] Pros/cons of files vs Prompt Management
- [x] Self-check: roll back a bad prompt in under a minute
## Results
- Prompt id: `Q080HSE5OV`
- File prompts: `src/prompts/extract/v1.yaml`, `v2.yaml` via `src/prompts/loader.py`
- IAM: `bedrock-prompt-management` attached to `research_and_development`
- Active pin: set `BEDROCK_PROMPT_ARN` to `:2` for the stricter schema; flip to `:1` to roll back

### Prompt Management `:1` (first ship)
ARN: `arn:aws:bedrock:eu-north-1:767397880814:prompt/Q080HSE5OV:1`  
Usage: 101 in / 115 out / 216 total  
Line items used wrong keys (`product` / `price`):
```json
{
  "invoice_id": "INV-1001",
  "invoice_date": "2026-11-13",
  "vendor": "Acme Inc.",
  "currency": "USD",
  "total": 100.00,
  "line_items": [
    {
      "product": "Product A",
      "quantity": 1,
      "price": 100.00,
      "total": 100.00
    }
  ]
}

### Prompt Management `:2` (stricter schema)
ARN: `arn:aws:bedrock:eu-north-1:767397880814:prompt/Q080HSE5OV:2` 
Line items used wrong keys (`product` / `price`):
```json
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
      "total": "100.00"
    }
  ]
}

# Commands
bash infra/iam-setup/scripts/auth.sh sign-in
PYTHONPATH=src .venv/bin/python -c "from prompts.loader import load_prompt; print(load_prompt('extract','v2')['version'])"
# create scripts only when shipping a new version; do not re-run casually
# PYTHONPATH=src .venv/bin/python scripts/create_prompt_management_v2.py