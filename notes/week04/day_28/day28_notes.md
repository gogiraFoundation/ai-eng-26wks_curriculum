# Day 28 notes: credentials, p95, Phase 1 ship

## Credential types (4.3.8)

| Context | Credential | Notes |
|---|---|---|
| Local uvicorn / Docker | `aws login` profile (`AWS_PROFILE=agent-toolkit`) | Needs writable `~/.aws` in container for login cache |
| GitHub Actions deploy | OIDC → `AssumeRoleWithWebIdentity` | No long-lived keys in secrets |
| ECS task runtime | Task IAM role | Do **not** set `AWS_PROFILE` in the task |

## p95 method (2026-11-22)

20 × `POST /chat` with Bedrock `eu.amazon.nova-micro-v1:0`, unique message suffix per call (avoid Redis collapsing samples). Sort `usage.latency_ms`; p95 index ≈ `0.95 * (n-1)`.

- p50 = 268.5 ms · p95 = **305 ms**
- Cost / 1k ≈ **$0.00160** using EU CRIS Nova Micro rates (~$0.046 / 1M in, ~$0.184 / 1M out)

## Phase 1 honesty

Docker + Bedrock SSE proven. ECS/OIDC blocked until account root runs `infra/gateway/bootstrap-iam.sh`. Tag `gateway-v1.0` marks the local/Docker ship, not a live public URL.
