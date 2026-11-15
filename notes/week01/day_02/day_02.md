# Day 02: AWS Account Hygiene (Budget Alarm, Identity Center User, Least Privilege)

## What is IAM?

AWS Identity and Access Management (IAM) is a web service for securely controlling access to AWS resources and protecting the security of your account. The recommended pattern is to manage people through **IAM Identity Center**: put each user in a group, then attach a policy to that group so everyone in it gets the same permissions and shared resources.

## Budget alarm

Use **AWS Budgets** to set spending thresholds and get notifications when actual or forecast spend crosses them (for example at 50%, 80% and 100% of a monthly limit).

Live budgets on the primary billing view (1 Nov 2026). Both are healthy. A dash means AWS has not produced that figure yet; a new account with no spend often has no forecast.

| Name | Limit (USD) | Amount used | Forecast | Current vs budgeted | Health |
|---|---:|---:|---:|---:|---|
| MonthlyCostBudget | 50.00 | 0.00 | - | 0.00% | Healthy |
| My Zero-Spend Budget | 1.00 | - | - | 0.00% | Healthy |

`MonthlyCostBudget` is the monthly cap. `My Zero-Spend Budget` is the early warning: it trips near the first dollar of spend.

## Region

Project Region: `eu-north-1` (Stockholm). The `agent-toolkit` CLI profile already uses it.

The console list is the default Regions. They are enabled automatically and cannot be turned off. Stockholm is on that list. The line "17 Regions that are not enabled" refers to opt-in Regions launched after 20 March 2019. Leave those disabled. Create resources only in `eu-north-1`.

## Security best practices _(added, please review)_

- Turn on MFA for the root user, and don't use root for daily work.
- Sign in through IAM Identity Center with short-lived credentials. Don't create long-lived access keys.
- Grant least privilege: only the actions and resources a user or app needs.
- Attach policies to groups or roles, not to individual users.
- Never commit keys or secrets to Git.
- Enable CloudTrail for auditing, and review permissions regularly.

## Bedrock policy

An Amazon Bedrock policy is a JSON document that defines who can access your generative AI models and what they can do with them. It is used in two ways.

### 1. Identity-based permissions (IAM policies)

The most common use. The policy is attached to a group, role or user to give developers permission to use Bedrock. It splits access into three tiers:

| Tier | What it controls | Example actions |
|---|---|---|
| **Inference** (using models) | Who can send prompts and receive answers | `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream` |
| **Discovery** (reading metadata) | Who can see which models are available in a Region | `bedrock:ListFoundationModels`, `bedrock:GetFoundationModel` |
| **Administration and customization** (high risk) | Who can create custom fine-tuned models, manage knowledge bases (RAG) or set up agents | `bedrock:CreateModelCustomizationJob`, `bedrock:CreateAgent` |

### 2. Organization-wide governance (AWS Organizations)

A Bedrock policy can also act as a company-wide guardrail across multiple accounts. Managed through AWS Organizations, these central policies let a company enforce **Amazon Bedrock Guardrails** automatically across business units and sub-accounts. For example, a security team can make sure model responses across the company block PII leakage or toxic content, without configuring guardrails by hand in every application.

## Why use Bedrock policies?

- **Cost management:** models charge per token. A strict policy can limit expensive models (premium or "ultra" tiers) to specific applications and prevent accidental large bills.
- **Data security:** keeps data boundaries clear by allowing only authorised applications to reach proprietary vector databases (Knowledge Bases) or custom-trained models.
- **Least privilege:** a production app should only be allowed to invoke a model, never to modify or delete model configurations.

## Day 2 task checklist

- [x] Budget alarm created (`MonthlyCostBudget` at $50, `My Zero-Spend Budget` at $1; both healthy, $0 spend)
- [ ] MFA enabled and Identity Center user created
- [ ] SSO profile named (check it matches the `agent-toolkit` profile or note the new name)
- [ ] `infra/iam-setup/` policies committed
- [ ] `notes/aws-setup.md` checklist committed (budgets, MFA, SSO profile name, no screenshots)
- [ ] No keys committed