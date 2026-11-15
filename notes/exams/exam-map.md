# MLA-C02 exam map

Source: AWS Certified Machine Learning Engineer – Associate (MLA-C02) content outline. Weights are the share of scored questions. Fill the Week column each Sunday.

| Domain | Weight | Week |
| --- | ---: | --- |
| 1. Data Preparation for ML and AI | 28% | |
| 2. ML Model and Foundation Model (FM) Development | 24% | Week 1: Bedrock Converse, sampling, streaming CLI. Week 2: task-specific extract prompt + schema (2.2.8) |
| 3. Deployment and Orchestration of ML and AI Workflows | 24% | Week 2: recorded prompt tests + GitHub Actions pytest (3.3.9) |
| 4. Operating, Monitoring, and Securing ML and AI Solutions | 24% | Week 1: budgets, least-privilege IAM, session teardown |

## Skills touched this week

| Skill | Statement (MLA-C02) | Week 2 evidence |
| --- | --- | --- |
| 2.2.8 | Apply customisation techniques for AI solutions (e.g. task-specific prompt engineering, fine-tuning) | Invoice JSON Schema / Pydantic (`extra=forbid`); extract contract; one repair turn that re-prompts for valid JSON |
| 3.3.9 | Implement AI model testing frameworks, including prompt testing | 15 `recorded/` vs `expected/` cases; field accuracy; retry unit tests; CI runs `pytest` with no live LLM |

## Skill Builder (Day 14, 40 min)

[Foundations of Prompt Engineering](https://skillbuilder.aws/learn/VF6H4SZ1BU/foundations-of-prompt-engineering) — first half (FM basics + prompt essentials / zero- and few-shot). Log three bullets in `notes/week02/day_14/day14_notes.md` that map to the invoice extract prompt.