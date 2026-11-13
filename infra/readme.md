# Infrastructure

Infrastructure and environment setup for the AI Engineer learning projects (AWS track, MLA-C02 and LLM engineering).

**Owner:** station-chief
**Cloud:** AWS
**Region:** `eu-north-1` (Stockholm)
**AWS CLI profile:** `agent-toolkit`

## Files in this directory

| Path | Role |
|------|------|
| `readme.md` | This setup guide |
| `aws_setup.md` | Account checklist (budgets, MFA, profile). No keys |
| `run-setup.sh` | Apply IAM, then read the two budgets |
| `session-resources.sh` | List hourly resources in `eu-north-1`. Tear down only when asked |
| `iam-setup/` | Least-privilege groups, policies, and role `llm-cli` |

---

## 1. Overview

| Area | Choice | Notes |
|---|---|---|
| Cloud provider | AWS | New AWS experience (project-based account) |
| Default Region | `eu-north-1` | All Regional resources must be created here |
| Global exceptions | `us-east-1` | CloudFront, WAF, and CloudWatch Logs tied to global resources. Also the Budgets API (`AWS_BUDGETS_REGION`) and Agent Toolkit |
| Auth | `aws login` (browser sign-in) | Credentials last 12 hours, renewable for 90 days |
| AI tooling | Agent Toolkit for AWS | Skills + AWS MCP server, configured for Cursor |
| IaC | _TODO: CDK or Terraform_ | Not checked in yet |
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

Root on `agent-toolkit` is only for `run-setup.sh`, `iam-destroy-resource.sh destroy`, and `session-resources.sh teardown`. Daily work is the IAM user `afrotyche@gmail.com`. Sign the profile back in as that user when the root command finishes. Do not create long-lived access keys. IAM Identity Center is not set up yet.

### 3.3 Billing protection

`MonthlyCostBudget` (50 USD) and `My Zero-Spend Budget` (1 USD) already exist. `iam-budgets.sh` reads them in `us-east-1`. It does not create them. Set a spend limit in AWS Settings, Billing. Status of MFA and Identity Center: `aws_setup.md`.

At the end of a session, from the repo root:

```bash
bash infra/session-resources.sh
bash infra/session-resources.sh teardown
```

`teardown` deletes SageMaker endpoints, NAT gateways, and load balancers, and it stops notebooks and RDS. OpenSearch domains stay until you pass one quoted argument, because that deletes the index:

```bash
bash infra/session-resources.sh "teardown data"
```

Unattached volumes are listed and kept.

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

Checked in today:

```text
.
├── README.md
├── .env.example
├── infra/
│   ├── readme.md
│   ├── aws_setup.md
│   ├── run-setup.sh
│   ├── session-resources.sh
│   └── iam-setup/
│       ├── README.md
│       ├── policies/
│       ├── roles/llm-cli-trust.json
│       └── scripts/
└── notes/week01/
```

CDK, `projects/`, and `.github/workflows/` are not in the tree yet.

---

## 6. Environments and configuration

Scripts read `.env` with a line parser. They do not `source` it. Never commit `.env`.

| Key | Purpose |
|---|---|
| `AWS_PROFILE` | CLI profile. Root for apply and teardown, IAM user for daily work |
| `REGION` | Project Region, `eu-north-1`. Scripts export this value as `AWS_REGION` for the AWS CLI |
| `AWS_ACCOUNT_ID` | Account check, and `__AWS_ACCOUNT_ID__` in IAM documents |
| `AWS_IAM_USER_ARN` | Daily IAM user, and `__AWS_IAM_USER_ARN__` in the `llm-cli` trust policy |
| `AWS_BUDGETS_REGION` | `us-east-1` |
| `BUDGET_NAMES` | `MonthlyCostBudget` and `My Zero-Spend Budget` |

Group, role, and policy keys are in `iam-setup/README.md` and `.env.example`. `USER_NAME` and `USER_ROLE` are not IAM names. The scripts ignore them.

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

No CDK or Terraform project is checked in. IAM apply, as root:

```bash
bash infra/run-setup.sh
```

The Arn from `aws sts get-caller-identity` must end in `:root`. See `iam-setup/README.md`.

## 9. Teardown

Hourly resources, from the repo root. The second command needs root:

```bash
bash infra/session-resources.sh
bash infra/session-resources.sh teardown
```

Exit code 2 on the first command means something is still listed. IAM undo, which does not stop an hourly bill:

```bash
bash infra/iam-setup/scripts/iam-destroy-resource.sh destroy
```

---

## 10. Security checklist

- [ ] MFA on the root user, and root not used for daily work
- [ ] Least-privilege policies applied with `run-setup.sh` (groups and role `llm-cli`, not policies on the IAM user)
- [ ] No long-lived access keys. Remove `AWS_BEARER_TOKEN_BEDROCK` from `.env`
- [ ] GitHub Actions authenticates via OIDC
- [ ] Buckets private, encryption on (S3, EBS, RDS)
- [ ] KMS keys for sensitive data
- [ ] Bedrock Guardrails and PII handling for user-facing apps
- [ ] CloudTrail enabled
- [x] Budget alarm set (`MonthlyCostBudget`, `My Zero-Spend Budget`)
- [ ] Spend limit set in AWS Settings

---

## 11. Troubleshooting

| Symptom | Fix |
|---|---|
| `NoCredentials` | Run `aws login --region eu-north-1 --profile agent-toolkit` again |
| `aws-mcp` fails with `-32602 Invalid request parameters` | Add `AWS_MCP_PROXY_PROFILES` to the `aws-mcp` entry, restart Cursor |
| `AccessDenied` that used to work | Check spend limit and plan in AWS Settings |
| Service not available | Run `aws freetier get-account-plan-state` and check the supported services list |
| `aws: command not found` | Add `$HOME/.local/bin` to `PATH` |
| `run-setup.sh` stops on the first script | The Arn is not root. Sign in as root, then sign back in as the IAM user |

---

## 12. References

- [AWS CLI install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Agent Toolkit for AWS](https://github.com/aws/agent-toolkit-for-aws)
- [Amazon Bedrock docs](https://docs.aws.amazon.com/bedrock/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)