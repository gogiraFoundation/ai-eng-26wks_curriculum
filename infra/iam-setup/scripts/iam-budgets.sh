#!/bin/bash
# Read the budgets named in .env. Does not create a budget or a notification.
# Caller needs budgets:DescribeBudget (root, or a principal with budgets-read).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: missing ${ENV_FILE}." >&2
  exit 1
fi

env_get() {
  local key="$1" line value
  line="$(grep -E "^${key}=" "$ENV_FILE" | tail -n 1 || true)"
  if [[ -z "$line" ]]; then
    echo "Error: ${key} is missing from ${ENV_FILE}." >&2
    exit 1
  fi
  value="${line#*=}"
  value="${value%\"}"
  value="${value#\"}"
  printf '%s' "$value"
}

env_optional() {
  local key="$1" line value
  line="$(grep -E "^${key}=" "$ENV_FILE" | tail -n 1 || true)"
  [[ -z "$line" ]] && return 0
  value="${line#*=}"
  value="${value%\"}"
  value="${value#\"}"
  printf '%s' "$value"
}

AWS_ACCOUNT_ID="$(env_get AWS_ACCOUNT_ID)"
AWS_BUDGETS_REGION="$(env_get AWS_BUDGETS_REGION)"
BUDGET_NAMES="$(env_get BUDGET_NAMES)"
AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE

if [[ -z "$BUDGET_NAMES" ]]; then
  echo "Error: BUDGET_NAMES is empty in ${ENV_FILE}." >&2
  exit 1
fi

CALLER_ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
if [[ "$CALLER_ACCOUNT" != "$AWS_ACCOUNT_ID" ]]; then
  echo "Error: signed-in account ${CALLER_ACCOUNT} does not match AWS_ACCOUNT_ID." >&2
  exit 1
fi

IFS='|' read -r -a BUDGETS <<<"$BUDGET_NAMES"

dash() {
  if [[ -z "${1:-}" || "$1" == "None" || "$1" == "null" ]]; then
    printf '%s' "-"
  else
    printf '%s' "$1"
  fi
}

printf '%-24s %12s %12s %12s\n' "Name" "Limit USD" "Actual USD" "Forecast USD"

for name in "${BUDGETS[@]}"; do
  if ! row="$(aws budgets describe-budget \
      --account-id "$AWS_ACCOUNT_ID" \
      --budget-name "$name" \
      --region "$AWS_BUDGETS_REGION" \
      --query 'Budget.[BudgetLimit.Amount, CalculatedSpend.ActualSpend.Amount, CalculatedSpend.ForecastedSpend.Amount]' \
      --output text)"; then
    echo "Error: cannot read budget '${name}'." >&2
    exit 1
  fi
  read -r limit actual forecast <<<"$row"
  printf '%-24s %12s %12s %12s\n' \
    "$name" \
    "$(dash "$limit")" \
    "$(dash "$actual")" \
    "$(dash "$forecast")"
done