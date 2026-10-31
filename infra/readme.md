# Infrastructure

Infrastructure and environment setup for the AI Engineer learning projects (AWS track, MLA-C02 and LLM engineering).

**Owner:** gogirafoundation@gmail.com
**Cloud:** AWS
**Region:** `eu-north-1` (Stockholm)
**AWS CLI profile:** `agent-toolkit`

---

## 1. Overview

| Area | Choice | Notes |
|---|---|---|
| Cloud provider | AWS | New AWS experience (project-based account) |
| Default Region | `eu-north-1` | All Regional resources must be created here |
| Global exceptions | `us-east-1` | Only for CloudFront, WAF and CloudWatch Logs tied to global resources |
| Auth | `aws login` (browser sign-in) | Credentials last 12 hours, renewable for 90 days |
| AI tooling | Agent Toolkit for AWS | Skills + AWS MCP server, configured for Cursor |
| IaC | _TODO: CDK or Terraform_ | Pick one per project and keep it consistent |
| CI/CD | _TODO: GitHub Actions_ | |

Constraints of the new AWS experience:

- The account is called a **project**. Settings, billing and team members are managed in AWS Settings.
- All Regional resources go in the project Region. No cross-Region replication, no StackSets, no Lambda@Edge.
- Not available in `eu-north-1`: Rekognition, Textract, Personalize, App Runner.
- Some services depend on the plan (Free vs Paid). Check with `aws freetier get-account-plan-state`.
- A spend limit may pause the project. If you suddenly get `AccessDenied` on something that worked before, check AWS Settings, then Billing.

---

## 2. Prerequisites

- macOS with a shell (zsh)
- [`uv`](https://docs.astral.sh/uv/) installed
- AWS CLI v2 (`aws --version` should print 2.x)
- Git and a GitHub account
- Docker (needed from Phase 1 week 4 onward)
- Python 3.11+ for the application code

---

## 3. AWS account setup

### 3.1 Install the CLI

```bash
curl -fsSL 'https://awscli.amazonaws.com/v2/install.sh' | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
aws --version
```

### 3.2 Sign in

```bash
aws configure set region eu-north-1 --profile agent-toolkit
aws login --region eu-north-1 --profile agent-toolkit
aws sts get-caller-identity --profile agent-toolkit
```

Expected: an `Account` and `Arn` are returned.

> **Security note:** the current login uses the root user. For everyday work, create a limited user or role (least privilege) and switch the profile to it. Never create long-lived access keys. Prefer IAM Identity Center and GitHub OIDC for CI.

### 3.3 Billing protection (do this first)

- Create a billing alarm or budget in the Billing and Cost Management console.
- Set a spend limit in AWS Settings, Billing.
- Tear down hourly-billed resources after every session (SageMaker endpoints, OpenSearch, NAT gateways, RDS).

---

## 4. Agent Toolkit for AWS

Installed with:

```bash
aws configure agent-toolkit --yes --region us-east-1 --profile agent-toolkit
```

The Agent Toolkit service itself is only available in `us-east-1`, regardless of your project Region.

| Item | Location |
|---|---|
| Skills (24 default AWS skills) | `~/.cursor/skills` |
| MCP server config | `~/.cursor/mcp.json` (entry `aws-mcp`) |
| Rules | `~/.cursor/rules/aws-agent-toolkit.mdc` |

The `aws-mcp` entry must carry the profile, or the server fails to start:

```json
"aws-mcp": {
  "command": "uvx",
  "args": ["mcp-proxy-for-aws@latest", "https://aws-mcp.us-east-1.api.aws/mcp", "--metadata", "INSTALL_SOURCE=aws-cli"],
  "env": { "AWS_MCP_PROXY_PROFILES": "agent-toolkit" }
}
```

Add another account later:

1. `aws login --profile <name>`
2. Add the name to the space-separated `AWS_MCP_PROXY_PROFILES` list
3. Restart Cursor

List available skills:

```bash
aws agent-toolkit list-available-skills --region us-east-1 --profile agent-toolkit
```

---

## 5. Repository layout

_Adjust to match your repo._

```text
.
├── README.md
├── infra/
│   ├── README.md          # this file
│   ├── cdk/ or terraform/ # infrastructure as code
│   └── scripts/           # setup and teardown helpers
├── notes/
│   └── day-01-tokens.md
├── projects/
│   ├── 01-rag-service/
│   ├── 02-tool-agent/
│   └── 03-finetune-vs-api/
└── .github/workflows/     # CI
```

---

## 6. Environments and configuration

| Variable | Purpose | Example |
|---|---|---|
| `AWS_PROFILE` | CLI profile to use | `agent-toolkit` |
| `AWS_REGION` | Default Region | `eu-north-1` |
| `BEDROCK_MODEL_ID` | Model used by the app | _TODO_ |

- Never commit secrets. Use `.env` (git-ignored) locally and AWS Secrets Manager or SSM Parameter Store in AWS.
- Keep a `.env.example` listing every variable with no real values.

---

## 7. Planned infrastructure by phase

| Phase | Weeks | AWS services |
|---|---|---|
| 1. LLM foundations | 1–4 | Bedrock, IAM, ECS or Lambda, ECR, ElastiCache (Redis) |
| 2. Retrieval and RAG | 5–8 | RDS/Aurora pgvector, S3, Lambda, Step Functions, OpenSearch Serverless, Bedrock Knowledge Bases and Guardrails |
| 3. Evals and observability | 9–11 | CloudWatch, OpenTelemetry, Langfuse |
| 4. Agents | 12–15 | Lambda, Bedrock AgentCore, Step Functions |
| 5. ML, fine-tuning, MLOps | 16–20 | SageMaker (training, endpoints, Pipelines, Model Registry, Model Monitor) |
| 6. Certification | 21–26 | Glue, Athena, CodePipeline, KMS, VPC endpoints |

Availability for each service in `eu-north-1` must be checked before you build on it.

---

## 8. Deploy

```bash
# example, replace with the real commands for your IaC tool
cd infra/cdk
npx cdk bootstrap aws://<ACCOUNT_ID>/eu-north-1 --profile agent-toolkit
npx cdk diff   --profile agent-toolkit
npx cdk deploy --profile agent-toolkit
```

## 9. Teardown

```bash
npx cdk destroy --profile agent-toolkit
aws sagemaker list-endpoints --region eu-north-1 --profile agent-toolkit
```

After each session confirm nothing is still billing: endpoints, OpenSearch domains, NAT gateways, load balancers, unattached volumes.

---

## 10. Security checklist

- [ ] MFA on the root user, and root not used for daily work
- [ ] Least-privilege IAM roles; no long-lived access keys
- [ ] GitHub Actions authenticates via OIDC
- [ ] Buckets private, encryption on (S3, EBS, RDS)
- [ ] KMS keys for sensitive data
- [ ] Bedrock Guardrails and PII handling for user-facing apps
- [ ] CloudTrail enabled
- [ ] Budget alarm and spend limit set

---

## 11. Troubleshooting

| Symptom | Fix |
|---|---|
| `NoCredentials` | Run `aws login --region eu-north-1 --profile agent-toolkit` again |
| `aws-mcp` fails with `-32602 Invalid request parameters` | Add `AWS_MCP_PROXY_PROFILES` to the `aws-mcp` entry, restart Cursor |
| `AccessDenied` that used to work | Check spend limit and plan in AWS Settings |
| Service not available | Run `aws freetier get-account-plan-state` and check the supported services list |
| `aws: command not found` | Add `$HOME/.local/bin` to `PATH` |

---

## 12. References

- [AWS CLI install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Agent Toolkit for AWS](https://github.com/aws/agent-toolkit-for-aws)
- [Amazon Bedrock docs](https://docs.aws.amazon.com/bedrock/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)