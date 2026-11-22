Week 4 (16 Nov - 22 Nov 2026): Production LLM gateway

Goal: Turn your client code into a deployable service: async, streaming, retries, caching, fallback,
CI/CD.
Deliverable: Deployed LLM gateway (ECS Fargate or Lambda) with SSE streaming, Redis cache,
fallback model, CI, README + architecture diagram.
Exam link (MLA-C02): 3.1.7 (FM hosting/resource allocation), 3.3 (CI/CD), 4.3.8 (credential types),
4.1 (monitoring

Day 26 · Fri 20 Nov 2026 · Rest
Rest day. No study. Optional: a walk, sleep, and 5 minutes jotting down anything that confused you this
week.


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



Time: 3 h. 30m GitHub OIDC to AWS (no long-lived keys) · 90m GitHub Actions: test, build, push to ECR, deploy (CDK or Terraform minimal) · 30m smoke test the deployed URL · 30m architecture diagram (draw.io/Excalidraw, free).
Free resources: GitHub Docs: OpenID Connect in AWS; AWS CDK v2 developer guide; HashiCorp: Terraform AWS get-started tutorials; GitHub Actions docs
Task: Live endpoint; pipeline green; tear down or scale to zero after testing.
Check yourself: Why use GitHub OIDC instead of access keys in CI?
Day 28 · Sun 22 Nov 2026 · Ship + review + exam hour
Time: 2 h. 40m README: features, latency/cost numbers, diagram, how to run · 40m Skill Builder Bedrock course module on Bedrock APIs · 20m exam-map: 3.1.7, 3.3, 4.3.8 · 20m review; confirm budget alarm has not fired.
Free resources: Skill Builder: Building Generative AI Applications Using Amazon Bedrock (free); Official MLA-C02 exam guide (domains, task statements); AWS Budgets user guide
Task: Tag gateway-v1.0; Phase 1 done. Destroy any running stack you do not need.
Check yourself: What is your gateway's p95 latency and cost per 1k requests?
Phase 2 · Retrieval and RAG
Week 5 (23 Nov - 29 Nov 2026): Embeddings and vector search
Goal: Understand embeddings and ANN indexes; build semantic search on pgvector and try S3 Vectors.
Deliverable: Semantic search API over ~1,000 documents (pgvector), with a note comparing it to S3 Vectors.
Exam link (MLA-C02): 1.1.7 (vector databases: OpenSearch, RDS pgvector, S3), 1.2.5 (embedding models).
Day 29 · Mon 23 Nov 2026 · What embeddings are and how similarity works
Time: 75 min. 30m Jay Alammar 'Illustrated Word2vec' · 25m Sentence Transformers quickstart: embed 20 sentences, compute cosine similarity matrix · 20m note why cosine vs dot product vs L2 and when vectors are normalised.
Free resources: Jay Alammar: The Illustrated Word2vec; Sentence Transformers docs
Task: Notebook 05-embeddings.ipynb showing nearest neighbours for 5 queries.
Check yourself: Why does normalising vectors make cosine equal to dot product?
Day 30 · Tue 24 Nov 2026 · Choosing an embedding model
Time: 75 min. 20m MTEB leaderboard: filter by retrieval, size, licence · 20m Titan Text Embeddings docs (dimensions, normalisation) · 35m embed the same 200 docs with one local model and Titan; compare top-5 overlap on 10 queries.
Free resources: MTEB embedding leaderboard; Sentence Transformers: pretrained models; Amazon Titan Text Embeddings models
Task: Short table: model, dims, cost per 1k docs, overlap@5.
Check yourself: What matters more for your corpus: embedding quality or chunking?
Day 31 · Wed 25 Nov 2026 · ANN indexes: HNSW and IVF
Time: 75 min. 25m Pinecone Learn article on HNSW (free) + skim the HNSW paper abstract · 35m Postgres + pgvector in Docker, create HNSW index, tune m/ef_search · 15m note recall vs latency tradeoff.
Free resources: Pinecone Learn (free articles on vector search); Paper: HNSW (arXiv); pgvector (GitHub)
Task: Benchmark script: exact vs HNSW latency and recall@10 on 1,000 docs.
Check yourself: What do m and ef_search trade off in HNSW?
Day 32 · Thu 26 Nov 2026 · Managed options on AWS
Time: 75 min. 25m read S3 Vectors and OpenSearch Serverless vector collections docs · 25m Aurora PostgreSQL pgvector as a Bedrock KB · 25m write a comparison: cost model, scale, filtering, ops burden.
Free resources: Amazon S3 Vectors; Amazon OpenSearch Serverless: vector search collections; Aurora PostgreSQL as a Bedrock knowledge base (pgvector)
Task: docs/adr-002-vector-store.md choosing a store for Project 1 (default: pgvector locally, one managed option for comparison).
Check yourself: When would S3 Vectors beat OpenSearch Serverless, and vice versa?
Day 33 · Fri 27 Nov 2026 · Rest
Rest day. No study. Optional: a walk, sleep, and 5 minutes jotting down anything that confused you this week.

Day 34 · Sat 28 Nov 2026 · Build day: semantic search API
Time: 3 h. 30m pick a corpus you can share (e.g. AWS docs pages you are allowed to use, or an open dataset) · 90m ingest 1,000 docs, embed, store, /search?q= endpoint with metadata filters · 40m 20 hand-written queries with expected doc ids · 20m README.
Free resources: pgvector (GitHub); FastAPI docs; Sentence Transformers docs
Task: Search API with recall@5 on your 20 queries reported.
Check yourself: What is your recall@5 and which queries fail?
Day 35 · Sun 29 Nov 2026 · Ship + review + exam hour
Time: 2 h. 30m polish and push · 30m try S3 Vectors with 100 docs (small, then delete) · 40m exam-map 1.1.7 and 1.2.5 with a one-line 'when to choose' per store · 20m review.
Free resources: Amazon S3 Vectors; Official MLA-C01 vs MLA-C02 comparison
Task: Tag search-v0.1; delete any S3 vector bucket you created.
Check yourself: Which three AWS vector stores does task 1.1.7 name?
Week 6 (30 Nov - 6 Dec 2026): Ingestion and chunking pipeline
Goal: Event-driven ingestion: parse, clean, redact, chunk, embed, store, on AWS.
Deliverable: Automated pipeline: S3 upload → Lambda/Step Functions → parse → redact PII → chunk → embed → vector store.
Exam link (MLA-C02): 1.1.8 (diverse data), 1.2.7 (RAG document prep), 1.2.8 (mask/redact), 3.3.11 (KB refresh pipelines).
Day 36 · Mon 30 Nov 2026 · Chunking strategies
Time: 75 min. 25m Bedrock KB chunking docs (fixed, hierarchical, semantic) · 35m implement fixed-size with overlap and heading-aware chunking on 5 docs · 15m inspect chunk boundaries by eye.
Free resources: Amazon Bedrock KB: How content chunking works; DataTalksClub LLM Zoomcamp (free)
Task: chunking.py with 2 strategies and a printout of 3 chunk examples each.
Check yourself: When does overlap help, and when does it just duplicate cost?
Day 37 · Tue 1 Dec 2026 · Parsing PDFs and HTML
Time: 75 min. 20m Docling README + PyMuPDF basics · 40m parse 10 mixed PDFs/HTML pages, keep headings, tables and page numbers as metadata · 15m note when you would use Textract instead.
Free resources: Docling: document parsing for GenAI; PyMuPDF docs; Amazon Textract developer guide
Task: Parser outputs JSONL: text, source, page, section, doc_hash.
Check yourself: How do you keep table structure when parsing PDFs?
Day 38 · Wed 2 Dec 2026 · PII detection and redaction
Time: 75 min. 20m Comprehend PII docs · 20m Presidio quickstart · 35m add a redaction step (Presidio locally; note Comprehend as managed option) with a test file containing fake emails/phones.
Free resources: Amazon Comprehend: Detecting PII entities; Microsoft Presidio (PII detection/anonymisation)
Task: Test that asserts fake PII is masked before embedding.
Check yourself: Why redact before embedding rather than after retrieval?
Day 39 · Thu 3 Dec 2026 · Event-driven ingestion on AWS
Time: 75 min. 20m S3 event notifications + Step Functions concepts · 40m Lambda triggered by S3 put that parses+chunks one file; Step Functions for embed+store with retries · 15m idempotency via doc_hash.
Free resources: Amazon S3 Event Notifications; AWS Lambda developer guide; AWS Step Functions developer guide
Task: Upload a file to S3 and see chunks appear in your store; re-upload does not duplicate.
Check yourself: How do you make S3-triggered ingestion idempotent?
Day 40 · Fri 4 Dec 2026 · Rest
Rest day. No study. Optional: a walk, sleep, and 5 minutes jotting down anything that confused you this week.

Day 41 · Sat 5 Dec 2026 · Build day: full pipeline + reprocessing
Time: 3 h. 40m wire parse → redact → chunk → embed → upsert · 60m deletion/updates: when a doc changes, replace its chunks · 40m IaC for bucket, Lambda, state machine · 40m run on 100 docs, record time and cost.
Free resources: AWS Step Functions developer guide; AWS CDK v2 developer guide; AWS Lambda developer guide
Task: Pipeline handles add, update, delete; cost per 100 docs in README.
Check yourself: How do you delete a document's chunks when the source is removed?
Day 42 · Sun 6 Dec 2026 · Ship + review + exam hour
Time: 2 h. 40m README + diagram · 40m exam-map 1.1.8, 1.2.7, 1.2.8, 3.3.11 with examples from your code · 20m LeetCode-style warm-up: 1 easy hash-map problem · 20m review.
Free resources: Official MLA-C02 exam guide (domains, task statements); NeetCode practice list (free)
Task: Tag ingest-v1.0; tear down anything idle.
Check yourself: How does a knowledge-base refresh fit into an MLOps pipeline?