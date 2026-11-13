#!/bin/bash
# Create the IAM groups named in .env. An existing group is left in place.
# Caller must be the account root. The admin group can read IAM only.
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
IAM_GROUP_NAMES="$(env_get IAM_GROUP_NAMES)"
AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE

if [[ -z "$IAM_GROUP_NAMES" ]]; then
  echo "Error: IAM_GROUP_NAMES is empty in ${ENV_FILE}." >&2
  exit 1
fi

read -r CALLER_ACCOUNT CALLER_ARN <<<"$(aws sts get-caller-identity --query '[Account,Arn]' --output text)"

if [[ "$CALLER_ACCOUNT" != "$AWS_ACCOUNT_ID" ]]; then
  echo "Error: signed-in account ${CALLER_ACCOUNT} does not match AWS_ACCOUNT_ID." >&2
  exit 1
fi

if [[ "$CALLER_ARN" != *:root ]]; then
  echo "Error: create-group must run as root. Caller is ${CALLER_ARN}." >&2
  exit 1
fi
IFS='|' read -r -a GROUP_LIST <<<"$IAM_GROUP_NAMES" || true

for name in "${GROUP_LIST[@]}"; do
  if aws iam get-group --group-name "$name" >/dev/null 2>&1; then
    echo "exists: ${name}"
    continue
  fi
  aws iam create-group --group-name "$name" >/dev/null
  echo "created: ${name}"
done