# IAM scripts

Wrappers for `../README.md`. They read `.env` and do not `source` it. `infra/run-setup.sh` runs the first five in this order. Sign in as root on `AWS_PROFILE` first.

| Script | Does |
| --- | --- |
| `iam-groups.sh` | Create `IAM_GROUP_NAMES`. An existing group is left in place |
| `iam-security.sh` | Create the customer managed policies and attach them to groups |
| `iam-roles.sh` | Create `IAM_ROLE_NAME` and attach `IAM_ROLE_POLICIES` |
| `iam-assign-users.sh` | Put `AWS_IAM_USER_ARN` in `IAM_USER_GROUP` only, and detach policies on that user |
| `iam-budgets.sh` | Read `BUDGET_NAMES` in `AWS_BUDGETS_REGION`. Does not create a budget |
| `iam-destroy-resource.sh` | Undo the groups, customer policies, and role. Requires the argument `destroy` |

`iam-destroy-resource.sh` does not delete the IAM user, the budgets, or `SignInLocalDevelopmentAccess`. Hourly resources are `infra/session-resources.sh`, not this directory.