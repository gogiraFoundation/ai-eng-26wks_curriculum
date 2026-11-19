Week 4 (16 Nov - 22 Nov 2026): Production LLM gateway

Goal: Turn your client code into a deployable service: async, streaming, retries, caching, fallback,
CI/CD.
Deliverable: Deployed LLM gateway (ECS Fargate or Lambda) with SSE streaming, Redis cache,
fallback model, CI, README + architecture diagram.
Exam link (MLA-C02): 3.1.7 (FM hosting/resource allocation), 3.3 (CI/CD), 4.3.8 (credential types),
4.1 (monitoring

Day 24 · Wed 18 Nov 2026 · Caching and fallback models
Time: 75 min. 20m Redis docs (strings, TTL) + Bedrock inference profiles (cross-region) · 40m
response cache keyed on hash(prompt_version, model, input), TTL 1h; fallback to a cheaper model
on repeated throttling · 15m log cache hit rate.
Free resources: Redis docs; Amazon Bedrock: Inference profiles; Amazon Bedrock: Intelligent
prompt routing
Task: Docker-compose with Redis; metrics line per request: cache_hit, model_used,
fallback=true/false.
Check yourself: What is a safe cache key for LLM responses, and when is caching wrong?

7
Day 25 · Thu 19 Nov 2026 · Containerise and pick a deployment target
Time: 75 min. 20m Docker get-started refresh · 30m multi-stage Dockerfile, non-root user · 25m
decide ECS Fargate vs Lambda (streaming, cold start, cost at your traffic) and write an ADR.
Free resources: Docker: Get started; Amazon ECS developer guide; AWS Lambda developer guide
Task: docs/adr-001-deploy-target.md with the decision and reasons.
Check yourself: When is Lambda a poor fit for streaming LLM responses?
Day 26 · Fri 20 Nov 2026 · Rest
Rest day. No study. Optional: a walk, sleep, and 5 minutes jotting down anything that confused you this
week.
Day 27 · Sat 21 Nov 2026 · Build day: deploy with CI/CD
Time: 3 h. 30m GitHub OIDC to AWS (no long-lived keys) · 90m GitHub Actions: test, build, push to
ECR, deploy (CDK or Terraform minimal) · 30m smoke test the deployed URL · 30m architecture
diagram (draw.io/Excalidraw, free).
Free resources: GitHub Docs: OpenID Connect in AWS; AWS CDK v2 developer guide; HashiCorp:
Terraform AWS get-started tutorials; GitHub Actions docs
Task: Live endpoint; pipeline green; tear down or scale to zero after testing.
Check yourself: Why use GitHub OIDC instead of access keys in CI?
Day 28 · Sun 22 Nov 2026 · Ship + review + exam hour
Time: 2 h. 40m README: features, latency/cost numbers, diagram, how to run · 40m Skill Builder
Bedrock course module on Bedrock APIs · 20m exam-map: 3.1.7, 3.3, 4.3.8 · 20m review; confirm
budget alarm has not fired.
Free resources: Skill Builder: Building Generative AI Applications Using Amazon Bedrock (free);
Official MLA-C02 exam guide (domains, task statements); AWS Budgets user guide
Task: Tag gateway-v1.0 ; Phase 1 done. Destroy any running stack you do not need.
Check yourself: What is your gateway’s p95 latency and cost per 1k requests?
Phase 2 · Retrieval and RAG
Week 5 (23 Nov - 29 Nov 2026): Embeddings and vector search
Goal: Understand embeddings and ANN indexes; build semantic search on pgvector and try S3
Vectors.
Deliverable: Semantic search API over ~1,000 documents (pgvector), with a note comparing it to
S3 Vectors.
Exam link (MLA-C02): 1.1.7 (vector databases: OpenSearch, RDS pgvector, S3), 1.2.5 (embedding
models).
Day 29 · Mon 23 Nov 2026 · What embeddings are and how similarity works
Time: 75 min. 30m Jay Alammar ‘Illustrated Word2vec’ · 25m Sentence Transformers quickstart: