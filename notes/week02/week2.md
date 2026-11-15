Structured ouput and tool use

Goal and deliverable:       FastAPI /extract endpoint (e.g. invoice text to  

                            JSON)   with Pydantic validation, retry-on-parse-failure and tests.
Exam link
2.2.8 (task-specific prompt engineering), 3.3.9 (prompt testing).

| Day | Date      | Topic                                    | Task                                                                                               |
| --- | --------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 8   | Mon 2 Nov | JSON schema and why models break format  | schemas/invoice.py and notes/format-failures.md listing observed failures and a fix idea for each. |
| 9   | Tue 3 Nov | Validation + retry on parse failure      | Unit tests that inject malformed JSON and assert exactly one retry fixes it.                       |
| 10  | Wed 4 Nov | Tool use / function calling on Bedrock   | src/tools_loop.py: loop until stop reason is end_turn, max 5 iterations, printing each tool call.  |
| 11  | Thu 5 Nov | FastAPI service skeleton                 | uvicorn app:app works locally; a curl example in README.                                           |
| 12  | Fri 6 Nov | Rest                                     | No study                                                                                           |
| 13  | Sat 7 Nov | Build day: extraction service with tests | Accuracy table per field in README (e.g. total 15/15, date 13/15).                                 |
| 14  | Sun 8 Nov | Ship + review + exam hour                | Green CI badge on the repo; tag extract-v0.1.                                                      |

Time boxes, the full resource links and self-check questions for every day are in the daily-guides file (see Files).
Free vs paid resources

| Item                                                                                           | Cost          | Use in plan                                                                               |
| ---------------------------------------------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------- |
| Skill Builder MLA-C02 Exam Prep Plan, free courses, 20-question Official Practice Question Set | Free          | Weeks 16-25                                                                               |
| Skill Builder Official Practice Exam, enhanced prep, most labs                                 | Subscription  | Optional: 1 month in week 24 (from $29/month per AWS)                                     |
| AWS usage (Bedrock, SageMaker, OpenSearch, AgentCore)                                          | Pay-as-you-go | $100 sign-up credits plus up to $100 more; budgets on day 2; tear down after each session |
| Colab and Kaggle GPUs, Hugging Face Hub                                                        | Free tiers    | Weeks 17-18 training                                                                      |
| Chip Huyen and Géron books, Udemy, Tutorials Dojo                                              | Paid          | Optional, not needed                                                                      |
| MLA-C02 exam fee                                                                               | Paid          | Beta was $75. GA price not yet published (MLA-C01 was $150)                               |