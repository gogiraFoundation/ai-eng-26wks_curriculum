#!/bin/bash
# Create the customer managed policies and attach them to groups.
# An existing policy gets a new default version. Groups are not created here.
# Caller must be the account root.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"
POLICY_DIR="${ROOT}/infra/iam-setup/policies"
SIGN_IN_POLICY="arn:aws:iam::aws:policy/SignInLocalDevelopmentAccess"

POLICIES=(
  console-self
  bedrock-discover
  bedrock-invoke-nova
  bedrock-require-inference-profile
  bedrock-deny-expensive
  budgets-read
  iam-read
  assume-llm-cli
)

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

policy_arn() {
  printf 'arn:aws:iam::%s:policy/%s' "$AWS_ACCOUNT_ID" "$1"
}

put_policy_version() {
  local arn="$1" file="$2" out status old
  set +e
  out="$(aws iam create-policy-version \
    --policy-arn "$arn" \
    --policy-document "file://${file}" \
    --set-as-default 2>&1)"
  status=$?
  set -e
  if [[ "$status" -eq 0 ]]; then
    return 0
  fi
  if [[ "$out" != *LimitExceeded* ]]; then
    echo "$out" >&2
    exit 1
  fi
  old="$(aws iam list-policy-versions --policy-arn "$arn" \
    --query 'sort_by(Versions[?IsDefaultVersion==`false`], &CreateDate)[0].VersionId' \
    --output text)"
  aws iam delete-policy-version --policy-arn "$arn" --version-id "$old"
  aws iam create-policy-version \
    --policy-arn "$arn" \
    --policy-document "file://${file}" \
    --set-as-default >/dev/null
}

create_or_update() {
  local name="$1" file arn
  file="${POLICY_DIR}/${name}.json"
  arn="$(policy_arn "$name")"
  if [[ ! -f "$file" ]]; then
    echo "Error: missing ${file}." >&2
    exit 1
  fi
  if aws iam get-policy --policy-arn "$arn" >/dev/null 2>&1; then
    put_policy_version "$arn" "$file"
    echo "updated: ${name}"
    return
  fi
  aws iam create-policy \
    --policy-name "$name" \
    --policy-document "file://${file}" >/dev/null
  echo "created: ${name}"
}

attach_group() {
  local group="$1" policy="$2" arn
  if [[ "$policy" == arn:* ]]; then
    arn="$policy"
  else
    arn="$(policy_arn "$policy")"
  fi
  aws iam attach-group-policy --group-name "$group" --policy-arn "$arn"
  echo "attached: ${group} ${policy}"
}

AWS_ACCOUNT_ID="$(env_get AWS_ACCOUNT_ID)"
AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE

read -r CALLER_ACCOUNT CALLER_ARN <<<"$(aws sts get-caller-identity --query '[Account,Arn]' --output text)"

if [[ "$CALLER_ACCOUNT" != "$AWS_ACCOUNT_ID" ]]; then
  echo "Error: signed-in account ${CALLER_ACCOUNT} does not match AWS_ACCOUNT_ID." >&2
  exit 1
fi

if [[ "$CALLER_ARN" != *:root ]]; then
  echo "Error: policy changes must run as root. Caller is ${CALLER_ARN}." >&2
  exit 1
fi

for name in "${POLICIES[@]}"; do
  create_or_update "$name"
done

attach_group research_and_development console-self
attach_group research_and_development "$SIGN_IN_POLICY"
attach_group research_and_development bedrock-discover
attach_group research_and_development bedrock-invoke-nova
attach_group research_and_development bedrock-require-inference-profile
attach_group research_and_development bedrock-deny-expensive
attach_group research_and_development assume-llm-cli

attach_group admins console-self
attach_group admins "$SIGN_IN_POLICY"
attach_group admins iam-read
attach_group admins budgets-read
attach_group admins bedrock-discover
attach_group admins bedrock-deny-expensive

attach_group shared_resource_manager console-self
attach_group shared_resource_manager "$SIGN_IN_POLICY"
attach_group shared_resource_manager budgets-read