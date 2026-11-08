# AWS account checklist

Values the scripts use live in `.env`. This file records what is done. Do not commit keys.

**Account:** `767397880814`
**Project Region:** `eu-north-1`
**Budgets API Region:** `us-east-1`
**CLI profile:** `agent-toolkit`

## Done

- [x] Opt-in Regions left disabled. Create Regional resources only in `eu-north-1`.
- [x] Budgets present: `MonthlyCostBudget` at 50 USD, `My Zero-Spend Budget` at 1 USD. `iam-budgets.sh` reads them. It does not create them.
- [x] Daily IAM user `afrotyche@gmail.com` (`AWS_IAM_USER_ARN`), group `research_and_development`.

## Not done

- [ ] MFA on the root user. Root is for the three commands below. Sign `agent-toolkit` back in as the IAM user afterwards.
- [ ] IAM Identity Center user, and an SSO profile name recorded here.
- [ ] No long-lived access keys. Remove `AWS_BEARER_TOKEN_BEDROCK` from `.env`. The IAM scripts do not read it.

## Commands

Sign in as root on `agent-toolkit` and confirm the Arn ends in `:root`. From the repo root:

```bash
bash infra/run-setup.sh
bash infra/session-resources.sh
bash infra/iam-setup/scripts/iam-destroy-resource.sh destroy