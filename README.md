# AI Engineering: 26-Week Plan (AWS Track)

A 26-week, project-based plan to become an AI / LLM engineer and pass the **AWS Certified Machine Learning Engineer – Associate (MLA-C02)** exam.

**Owner:** gogirafoundation@gmail.com
**Start:** Monday 26 October 2026
**Target exam:** Thursday 15 April 2027 (standard release, not beta)
**Pace:** about 10 hours per week (roughly 4 theory, 6 hands-on). At 5 hours a week, keep the order and double the timeline.
**Background:** experienced Python / backend engineer
**Cloud:** AWS, Region `eu-north-1`

---

## Rules of the plan

1. **Every week ends with a deliverable pushed to GitHub.** No deliverable, no progress.
2. **Every theory item must produce code or a written explanation.** No tutorial hell.
3. **One full rest day per week.**
4. **Set the billing alarm in week 1** and tear down SageMaker endpoints and OpenSearch after every session.
5. **Start applying early:** CV and LinkedIn rewrite in week 11, then 3–5 tailored applications a week from week 12. Don't wait for the certificate.
6. **Check official AWS pages monthly.** Exam details, prices and dates change.

---

## Goals

**Practical**
- Build and deploy LLM APIs with streaming, structured output, retries, caching and cost controls.
- Build RAG systems with hybrid retrieval, reranking and measured quality.
- Create eval suites, tracing and CI quality gates.
- Build tool-using agents with guardrails, MCP servers and human approval.
- Fine-tune a small model with LoRA, deploy it on SageMaker and compare it with an API model.
- Run MLOps basics: pipelines, registry, monitoring, drift detection.

**Theory**
- How transformers, embeddings and sampling work.
- ML fundamentals: loss, bias and variance, metrics, data splits, leakage.
- Retrieval theory, evaluation methodology, LLM-as-judge bias.
- The AWS ML service landscape and security and cost trade-offs.

---

## Roadmap at a glance

| Phase | Weeks | Focus | Months |
|---|---|---|---|
| 1 | 1–4 | LLM application foundations | Oct–Nov 2026 |
| 2 | 5–8 | Retrieval and RAG | Nov–Dec 2026 |
| 3 | 9–11 | Evals and observability | Dec 2026–Jan 2027 |
| 4 | 12–15 | Agents | Jan–Feb 2027 |
| 5 | 16–20 | ML foundations, fine-tuning, MLOps | Feb–Mar 2027 |
| 6 | 21–26 | Certification and interviews | Mar–Apr 2027 |

---

## Weekly plan

### Phase 1: LLM application foundations (weeks 1–4)

| Week | Topic | Theory | Practical | Deliverable |
|---|---|---|---|---|
| 1 | Setup and LLM basics | Tokens, context windows, sampling, temperature | AWS account, billing alarm, least-privilege access, Bedrock access, call a model via Bedrock and a provider SDK | CLI chatbot with streaming |
| 2 | Structured output and tool use | JSON schema, function calling, why models fail at format | Pydantic validation, retry on parse failure, hand-written tool loop | FastAPI extraction endpoint with tests |
| 3 | Prompting and context engineering | System prompts, few-shot, chain-of-thought trade-offs, prompt caching, token economics | Versioned prompts, log tokens, latency and cost | Prompt library with cost and latency report |
| 4 | Production wrapper | Async I/O, SSE, backoff and jitter, rate limits, idempotency | Redis cache, timeouts, fallback model, Docker, deploy to ECS or Lambda, GitHub Actions | Deployed LLM gateway with README and diagram |

### Phase 2: Retrieval and RAG (weeks 5–8)

| Week | Topic | Theory | Practical | Deliverable |
|---|---|---|---|---|
| 5 | Embeddings and vector search | Embeddings, cosine similarity, HNSW, curse of dimensionality | Postgres with pgvector, embed 1,000 documents | Semantic search API |
| 6 | Ingestion and chunking | Chunking, overlap, metadata, parsing PDFs and HTML | S3 upload triggers Lambda or Step Functions, parse, chunk, embed, store | Automated ingestion pipeline |
| 7 | Better retrieval | BM25, hybrid search, reranking, query rewriting, recall@k, MRR | Hybrid search and reranker, compare with Bedrock Knowledge Bases and OpenSearch | Measured retriever comparison table |
| 8 | Generation, citations, guardrails | Grounding, citations, refusals, PII | Answers with citations, Bedrock Guardrails, no-answer handling, smoke eval | **Project 1 v1 (RAG service)** |

### Phase 3: Evals and observability (weeks 9–11)

| Week | Topic | Theory | Practical | Deliverable |
|---|---|---|---|---|
| 9 | Eval foundations | Golden datasets, offline vs online evals, metric selection | Build a 50–100 case dataset | Versioned eval dataset |
| 10 | LLM-as-judge and RAG metrics | Faithfulness, answer relevance, context precision, judge biases | Judge prompts, calibrate against 30 human labels | Eval harness with judge-vs-human agreement |
| 11 | Tracing and CI gates | OpenTelemetry, span design, cost attribution | Langfuse or CloudWatch tracing, cost dashboard, CI job that fails on quality drop | **Project 1 complete** with write-up. CV and LinkedIn rewrite |

### Phase 4: Agents (weeks 12–15)

| Week | Topic | Theory | Practical | Deliverable |
|---|---|---|---|---|
| 12 | Agent patterns | Workflows vs agents, ReAct, routing, orchestrator-worker | Tool loop from scratch, no framework. **Book the exam.** Start applications | Minimal agent with three tools and a step budget |
| 13 | Tool design and MCP | Tool schemas, helpful errors, Model Context Protocol, A2A | MCP server wrapping an internal API | MCP server plus client demo |
| 14 | State and reliability | Checkpointing, memory types, idempotency, limits | LangGraph or similar, human-in-the-loop approval | Agent that survives a crash and resumes |
| 15 | Agent security and evals | Prompt injection, least-privilege tools, trajectory evals | Red-team your agent, deploy on Bedrock AgentCore | **Project 2 complete** with failure-case write-up |

### Phase 5: ML foundations, fine-tuning, MLOps (weeks 16–20)

| Week | Topic | Theory | Practical | Deliverable |
|---|---|---|---|---|
| 16 | Classical ML | Bias and variance, regularisation, precision, recall, F1, ROC-AUC, leakage | scikit-learn tabular project with proper splits | Notebook plus model card |
| 17 | Deep learning and transformers | Backprop, self-attention, positional encoding | Karpathy's makemore and nanoGPT | Tiny GPT plus one-page explanation |
| 18 | Fine-tuning | Full fine-tune vs LoRA/QLoRA, dataset quality, catastrophic forgetting | Hugging Face Transformers and PEFT on a small open model | Fine-tuned model with before/after scores |
| 19 | SageMaker | Training jobs, endpoints, JumpStart, Pipelines, Model Registry, Clarify, Model Monitor, Feature Store | Deploy the fine-tuned model, then delete the endpoint | SageMaker pipeline in code |
| 20 | MLOps | CI/CD for models, shadow and canary, drift, cost | Monitoring and rollback path | **Project 3 complete**: fine-tuned vs API model |

### Phase 6: Certification and interviews (weeks 21–26)

| Week | Focus | Practical |
|---|---|---|
| 21 | Domain: data preparation | Small ETL and feature pipeline (Glue, Athena, Feature Store) |
| 22 | Domain: model development | SageMaker tuning job, Bedrock customisation options |
| 23 | Domain: deployment and orchestration | Deploy an endpoint with CDK or Terraform |
| 24 | Domain: monitoring, security, cost | First full timed practice exam, weak-topic list |
| 25 | Exam week | Review weak areas, second practice exam, **sit MLA-C02 on 15 Apr 2027** |
| 26 | Interview intensive | Mock interviews, polish portfolio, apply to at least 10 roles |

Exam topics are spread across the whole plan, so weeks 21–24 are review plus small labs, in order of exam weight.

---

## Capstone projects

| # | Project | What to show | Interview talking point |
|---|---|---|---|
| 1 | Production RAG service | Hybrid retrieval, reranking, eval suite, tracing, cost per query | Quality went from X to Y after change Z |
| 2 | Tool-using agent | MCP server, approvals, injection tests, failure write-up | Where the agent failed and how you contained it |
| 3 | Fine-tune vs API model | LoRA fine-tune, SageMaker endpoint, cost and quality comparison | When fine-tuning is and is not worth it |

Every project ships with tests, a Dockerfile, CI, an architecture diagram and a README that leads with results.

---

## Certification path

- **Main target:** AWS Certified Machine Learning Engineer – Associate (MLA-C02). The older MLA-C01 is retired, so don't buy C01 study material.
- **Exam plan:** sit the standard (non-beta) release. Book in week 12.
- **Domains:** four, weighted 28 / 24 / 24 / 24. Confirm the current weightings in the official exam guide.
- **Optional warm-up:** AWS Certified AI Practitioner (AIF-C01).
- **Stretch goal:** AWS Generative AI Developer – Professional (AIP-C01).
- Verify dates and prices on the [official certification page](https://aws.amazon.com/certification/certified-machine-learning-engineer-associate).

> The standard release date is not confirmed on the certification page yet. Re-check monthly.

---

## Interview preparation

- Coding: 2–3 LeetCode mediums per week from week 8, plus clean async Python and a retrieval function written from scratch.
- Mock system design once a week from week 20, and a behavioural rehearsal once a week from week 22.
- Strong-answer structure: **problem, options, trade-off, what you measured.**
- Topics to practise: RAG over 500k documents, reducing hallucinations, fine-tuning vs RAG vs prompting, evals and LLM-as-judge weaknesses, runaway agent loops, prompt injection, 1M-queries-a-day design, prompt and model rollback, PII and data residency, overfitting, drift.

## Job search

- **Titles:** AI Engineer, LLM Engineer, Applied AI Engineer, ML Platform Engineer, Backend Engineer (AI/ML), Solutions Engineer (AI).
- **CV:** lead with production, scale and reliability, then AI projects with metrics.
- **Applications:** 3–5 tailored applications a week from week 12.
- **Networking:** share project write-ups on LinkedIn, contribute to one open-source LLM tooling repo, message engineers with specific questions about their stack.

---

## Weekly review (Sundays, 20 minutes)

- [ ] Did I ship the deliverable?
- [ ] What confused me most? Write one paragraph explaining it simply.
- [ ] Update the project README with one measured result.
- [ ] Plan next week's two longest blocks in the calendar.

## Risks and fixes

| Risk | Fix |
|---|---|
| Falling behind | Drop theory depth, never drop the deliverable |
| Tutorial hell | Every theory item produces code or a written explanation |
| Surprise AWS bill | Billing alarm, delete endpoints, small instances, free tier |
| Exam changes | Re-check the official page monthly |
| Burnout | One full rest day a week |

---

## Free resources

- **Books and courses:** Hugging Face LLM course, fast.ai Practical Deep Learning, Andrej Karpathy's Neural Networks: Zero to Hero, DeepLearning.AI short courses
- **Docs:** Amazon Bedrock and SageMaker developer guides, AWS Well-Architected Machine Learning Lens, Model Context Protocol docs, Anthropic and OpenAI cookbooks
- **Certification prep:** the official MLA-C02 exam guide and sample questions, free AWS Skill Builder items
- **Blogs:** Eugene Yan, Hamel Husain, Simon Willison, Lilian Weng

Optional paid: *AI Engineering* and *Designing Machine Learning Systems* by Chip Huyen, Udemy and Tutorials Dojo practice exams (check they cover MLA-C02, not C01).

## Tools

FastAPI, Pydantic, pgvector or Qdrant, Redis, Docker, GitHub Actions, Langfuse, Ragas or custom evals, LangGraph, Terraform or CDK.

---

## Repository structure

```text
.
├── README.md
├── infra/                 # AWS setup, IaC, teardown scripts
├── notes/                 # daily notes (day-01-tokens.md, ...)
├── guides/                # daily study guides
├── weekly/                # one folder per week with its deliverable
└── projects/
    ├── 01-rag-service/
    ├── 02-tool-agent/
    └── 03-finetune-vs-api/
```

## Progress tracker

| Week | Deliverable | Status | Link |
|---|---|---|---|
| 1 | CLI chatbot with streaming | ⬜ | |
| 2 | FastAPI extraction endpoint | ⬜ | |
| 3 | Prompt library and cost report | ⬜ | |
| 4 | Deployed LLM gateway | ⬜ | |
| 5–26 | _(add as you go)_ | ⬜ | |