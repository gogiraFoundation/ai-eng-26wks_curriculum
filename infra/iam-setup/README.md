# IAM setup (least privilege)

Policy and trust documents for Week 1. `infra/run-setup.sh` applies them as root. Daily work uses the IAM user in `AWS_IAM_USER_ARN`, and that user belongs only to `IAM_USER_GROUP` (`research_and_development`). These files do not clear Bedrock `Error 002` (account entitlement). Support must lift that separately.

**Account:** `767397880814` (`AWS_ACCOUNT_ID`)
**Project Region:** `eu-north-1`
**Budgets API Region:** `us-east-1` (`AWS_BUDGETS_REGION`)

Do not commit `.env`.

## Layout

| Path | Purpose |
|------|---------|
| `policies/console-self.json` | Own user read, own MFA, account password policy |
| `policies/bedrock-discover.json` | List and get foundation models and inference profiles |
| `policies/bedrock-invoke-nova.json` | Invoke Nova Micro and Nova Lite via EU inference profiles |
| `policies/bedrock-require-inference-profile.json` | Deny bare foundation-model invoke (no profile ARN) |
| `policies/bedrock-deny-expensive.json` | Deny Opus and provisioned throughput |
| `policies/budgets-read.json` | Read budgets and Cost Explorer |
| `policies/iam-read.json` | Read IAM users, groups, roles, and policies |
| `policies/assume-llm-cli.json` | Allow `sts:AssumeRole` on `llm-cli` |
| `roles/llm-cli-trust.json` | Trust policy for role `llm-cli` |
| `scripts/iam-groups.sh` | Create the groups in `IAM_GROUP_NAMES` |
| `scripts/iam-security.sh` | Create the customer managed policies and attach them to groups |
| `scripts/iam-roles.sh` | Create `IAM_ROLE_NAME` and attach `IAM_ROLE_POLICIES` |
| `scripts/iam-assign-users.sh` | Put the IAM user in `IAM_USER_GROUP` only, and detach policies on that user |
| `scripts/iam-budgets.sh` | Read `BUDGET_NAMES`. Does not create a budget |
| `scripts/iam-destroy-resource.sh` | Undo the groups, customer policies, and role. Argument: `destroy` |
| `scripts/README.md` | What each script does |
| `../run-setup.sh` | Run the five scripts in that order |

AWS managed policy (attach by name, do not copy into this repo): `SignInLocalDevelopmentAccess`.

## Attachment map

| Principal | Attach |
|-----------|--------|
| Group `research_and_development` | `console-self`, `SignInLocalDevelopmentAccess`, `bedrock-discover`, `bedrock-invoke-nova`, `bedrock-require-inference-profile`, `bedrock-deny-expensive`, `assume-llm-cli` |
| Group `admins` | `console-self`, `SignInLocalDevelopmentAccess`, `iam-read`, `budgets-read`, `bedrock-discover`, `bedrock-deny-expensive` |
| Group `shared_resource_manager` | `console-self`, `SignInLocalDevelopmentAccess`, `budgets-read` |
| Group `user_clients` | (none) |
| Role `llm-cli` | `bedrock-invoke-nova`, `bedrock-require-inference-profile`, `bedrock-deny-expensive` |

`iam-security.sh` owns the group rows. `iam-roles.sh` owns the role row. Neither script attaches a policy to the IAM user.

## Environment

The scripts read these keys from `.env`. They do not `source` the file.

| Key | Used for |
|-----|----------|
| `AWS_ACCOUNT_ID` | Account check, policy ARNs, and `__AWS_ACCOUNT_ID__` in policy documents |
| `AWS_PROFILE` | CLI profile. Must be a root session for apply |
| `AWS_IAM_USER_ARN` | User placed in `IAM_USER_GROUP`, and `__AWS_IAM_USER_ARN__` in the trust policy |
| `IAM_GROUP_NAMES` | `research_and_development\|admins\|shared_resource_manager\|user_clients` |
| `IAM_ROLE_NAME` | `llm-cli`, and `__IAM_ROLE_NAME__` in `assume-llm-cli.json` |
| `IAM_ROLE_POLICIES` | `bedrock-invoke-nova\|bedrock-require-inference-profile\|bedrock-deny-expensive` |
| `IAM_USER_GROUP` | `research_and_development` |
| `AWS_BUDGETS_REGION` | `us-east-1` |
| `BUDGET_NAMES` | `MonthlyCostBudget\|My Zero-Spend Budget` |

`policies/console-self.json`, `policies/assume-llm-cli.json`, `policies/bedrock-invoke-nova.json`, and `roles/llm-cli-trust.json` use `__AWS_ACCOUNT_ID__`, `__AWS_IAM_USER_ARN__`, and `__IAM_ROLE_NAME__`. `iam-security.sh` and `iam-roles.sh` substitute those tokens from `.env` into a temporary document before each upload. The files in the repo are not rewritten.

## Apply (root only)

Sign in as root on `AWS_PROFILE`, then confirm the caller before applying:

```bash
aws login --region eu-north-1 --profile agent-toolkit
aws sts get-caller-identity --profile agent-toolkit
```

The Arn must end in `:root`. If it is `user/afrotyche@gmail.com`, `iam-groups.sh` stops and the later scripts do not run.

From the repo root:

```bash
bash infra/run-setup.sh
```

A failed script stops the runner. A second run is safe: existing groups and the role are left in place, policy documents are rendered from `.env` and published as a new default version, and attachments that are already present are skipped. `AttachGroupPolicy` and `AttachRolePolicy` are not idempotent, so the scripts check the attachment list first. The user stays in `research_and_development`. `iam-assign-users.sh` also removes that user from every other group and deletes managed and inline policies attached to the user.

After apply, sign in again as the IAM user on the same profile. Do not leave root on `agent-toolkit`.

## Verify as the IAM user

```bash
aws login --region eu-north-1 --profile agent-toolkit
aws sts get-caller-identity --profile agent-toolkit
aws bedrock list-inference-profiles --region eu-north-1 --profile agent-toolkit --type-equals SYSTEM_DEFINED --max-results 5
bash infra/iam-setup/scripts/iam-budgets.sh
```

`get-caller-identity` must show `user/afrotyche@gmail.com`. The budgets script prints `MonthlyCostBudget` and `My Zero-Spend Budget`. The research user cannot read budgets. Root can, and so can a principal with `budgets-read` (`admins`, `shared_resource_manager`).

Assume `llm-cli` only for the app, not as a second human login:

```bash
aws sts assume-role \
  --role-arn arn:aws:iam::767397880814:role/llm-cli \
  --role-session-name llm-cli-local \
  --profile agent-toolkit
```

## Remove the IAM setup (root only)

This deletes the groups, the eight customer managed policies, and role `llm-cli`. It leaves the IAM user, both budgets, and `SignInLocalDevelopmentAccess`.

```bash
bash infra/iam-setup/scripts/iam-destroy-resource.sh destroy

## Notes

- Invoke must use inference profile ids such as `eu.amazon.nova-micro-v1:0`. Bare model ids are denied.
- Foundation-model ARNs in `bedrock-invoke-nova.json` use Region `*` so EU profile routing to Frankfurt, Ireland, or Paris still works. Do not add `aws:RequestedRegion` on that allow.
- Do not add a Lambda trust principal until week 4, when the function ARN can be named with `aws:SourceAccount` and `aws:SourceArn`.

