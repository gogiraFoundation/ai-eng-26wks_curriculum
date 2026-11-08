#!/bin/bash
# Create role llm-cli from .env and attach its Bedrock policies.
# An existing role is kept. Its trust policy is set from llm-cli-trust.json.
# Caller must be the account root.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"
TRUST_FILE="${ROOT}/infra/iam-setup/roles/llm-cli-trust.json"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: missing ${ENV_FILE}." >&2
  exit 1
fi

if [[ ! -f "$TRUST_FILE" ]]; then
  echo "Error: missing ${TRUST_FILE}." >&2
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
IAM_ROLE_NAME="$(env_get IAM_ROLE_NAME)"
IAM_ROLE_POLICIES="$(env_get IAM_ROLE_POLICIES)"
AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE

if [[ -z "$IAM_ROLE_NAME" || -z "$IAM_ROLE_POLICIES" ]]; then
  echo "Error: IAM_ROLE_NAME or IAM_ROLE_POLICIES is empty in ${ENV_FILE}." >&2
  exit 1
fi

read -r CALLER_ACCOUNT CALLER_ARN <<<"$(aws sts get-caller-identity --query '[Account,Arn]' --output text)"

if [[ "$CALLER_ACCOUNT" != "$AWS_ACCOUNT_ID" ]]; then
  echo "Error: signed-in account ${CALLER_ACCOUNT} does not match AWS_ACCOUNT_ID." >&2
  exit 1
fi

if [[ "$CALLER_ARN" != *:root ]]; then
  echo "Error: create-role must run as root. Caller is ${CALLER_ARN}." >&2
  exit 1
fi

if aws iam get-role --role-name "$IAM_ROLE_NAME" >/dev/null 2>&1; then
  echo "exists: ${IAM_ROLE_NAME}"
else
  aws iam create-role \
    --role-name "$IAM_ROLE_NAME" \
    --assume-role-policy-document "file://${TRUST_FILE}" \
    >/dev/null
  echo "created: ${IAM_ROLE_NAME}"
fi

aws iam update-assume-role-policy \
  --role-name "$IAM_ROLE_NAME" \
  --policy-document "file://${TRUST_FILE}"

IFS='|' read -r -a POLICIES <<<"$IAM_ROLE_POLICIES"

for name in "${POLICIES[@]}"; do
  aws iam attach-role-policy \
    --role-name "$IAM_ROLE_NAME" \
    --policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${name}"
  echo "attached: ${name}"
done