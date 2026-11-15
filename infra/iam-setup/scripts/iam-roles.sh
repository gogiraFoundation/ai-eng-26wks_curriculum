#!/bin/bash
# Create the role from .env and attach its Bedrock policies.
# An existing role is kept. llm-cli-trust.json may contain
# __AWS_ACCOUNT_ID__ and __AWS_IAM_USER_ARN__. Those tokens are filled
# from .env into a temporary document. The file in the repo is not
# rewritten. A policy already attached to the role is left in place.
# Caller must be the account root.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"
TRUST_FILE="${ROOT}/infra/iam-setup/roles/llm-cli-trust.json"
WORK=""

cleanup() {
  [[ -n "${WORK}" ]] && rm -rf "$WORK"
}
trap cleanup EXIT

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

# Fill account and user tokens. Fail if a token is still present, so the
# trust policy cannot be uploaded with a literal placeholder.
render_document() {
  local src="$1" dest="$2" text
  text="$(<"$src")"
  if [[ -n "${AWS_ACCOUNT_ID:-}" ]]; then
    text="${text//__AWS_ACCOUNT_ID__/${AWS_ACCOUNT_ID}}"
  fi
  if [[ -n "${AWS_IAM_USER_ARN:-}" ]]; then
    text="${text//__AWS_IAM_USER_ARN__/${AWS_IAM_USER_ARN}}"
  fi
  if [[ -n "${IAM_ROLE_NAME:-}" ]]; then
    text="${text//__IAM_ROLE_NAME__/${IAM_ROLE_NAME}}"
  fi
  printf '%s\n' "$text" > "$dest"
  if grep -E -q '__AWS_ACCOUNT_ID__|__AWS_IAM_USER_ARN__|__IAM_ROLE_NAME__' "$dest"; then
    echo "Error: ${src} still has a placeholder. Set the matching key in ${ENV_FILE}." >&2
    exit 1
  fi
}

AWS_ACCOUNT_ID="$(env_get AWS_ACCOUNT_ID)"
AWS_IAM_USER_ARN="$(env_get AWS_IAM_USER_ARN)"
IAM_ROLE_NAME="$(env_get IAM_ROLE_NAME)"
IAM_ROLE_POLICIES="$(env_get IAM_ROLE_POLICIES)"
AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE

if [[ ! "$AWS_ACCOUNT_ID" =~ ^[0-9]{12}$ ]]; then
  echo "Error: AWS_ACCOUNT_ID must be 12 digits." >&2
  exit 1
fi

case "$AWS_IAM_USER_ARN" in
  arn:aws:iam::"${AWS_ACCOUNT_ID}":user/*) ;;
  *)
    echo "Error: AWS_IAM_USER_ARN is not a user in account ${AWS_ACCOUNT_ID}." >&2
    exit 1
    ;;
esac

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

WORK="$(mktemp -d)"
RENDERED_TRUST="${WORK}/llm-cli-trust.json"
render_document "$TRUST_FILE" "$RENDERED_TRUST"

if aws iam get-role --role-name "$IAM_ROLE_NAME" >/dev/null 2>&1; then
  echo "exists: ${IAM_ROLE_NAME}"
else
  aws iam create-role \
    --role-name "$IAM_ROLE_NAME" \
    --assume-role-policy-document "file://${RENDERED_TRUST}" \
    >/dev/null
  echo "created: ${IAM_ROLE_NAME}"
fi

aws iam update-assume-role-policy \
  --role-name "$IAM_ROLE_NAME" \
  --policy-document "file://${RENDERED_TRUST}"

IFS='|' read -r -a POLICIES <<<"$IAM_ROLE_POLICIES"

# AttachRolePolicy is not idempotent. A second attach returns an error
# (often LimitExceeded) and set -e would stop the script. Skip when the
# ARN is already on the role.
for name in "${POLICIES[@]}"; do
  arn="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${name}"
  found="$(aws iam list-attached-role-policies \
    --role-name "$IAM_ROLE_NAME" \
    --query "AttachedPolicies[?PolicyArn=='${arn}'].PolicyArn | [0]" \
    --output text)"
  if [[ "$found" == "$arn" ]]; then
    echo "exists: ${name}"
    continue
  fi
  aws iam attach-role-policy \
    --role-name "$IAM_ROLE_NAME" \
    --policy-arn "$arn"
  echo "attached: ${name}"
done