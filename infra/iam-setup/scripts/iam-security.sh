#!/bin/bash
# Create the customer managed policies and attach them to groups.
# Policy JSON may contain __AWS_ACCOUNT_ID__ and __IAM_ROLE_NAME__.
# Those tokens are filled from .env into a temporary document. The files
# in the repo are not rewritten. An existing policy gets a new default
# version. An attachment that is already present is skipped.
# Groups are not created here. Caller must be the account root.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"
POLICY_DIR="${ROOT}/infra/iam-setup/policies"
SIGN_IN_POLICY="arn:aws:iam::aws:policy/SignInLocalDevelopmentAccess"
WORK=""

cleanup() {
  [[ -n "${WORK}" ]] && rm -rf "$WORK"
}
trap cleanup EXIT

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

# Fill account and role tokens. Leave IAM policy variables such as
# ${aws:username} untouched. Fail if a token is still present, so a
# document cannot be uploaded with a literal placeholder.
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
  local name="$1" src rendered arn
  src="${POLICY_DIR}/${name}.json"
  rendered="${WORK}/${name}.json"
  arn="$(policy_arn "$name")"
  if [[ ! -f "$src" ]]; then
    echo "Error: missing ${src}." >&2
    exit 1
  fi
  render_document "$src" "$rendered"
  if aws iam get-policy --policy-arn "$arn" >/dev/null 2>&1; then
    put_policy_version "$arn" "$rendered"
    echo "updated: ${name}"
    return
  fi
  aws iam create-policy \
    --policy-name "$name" \
    --policy-document "file://${rendered}" >/dev/null
  echo "created: ${name}"
}

# AttachGroupPolicy is not idempotent. A second attach returns an error
# (often LimitExceeded) and set -e would stop the script. Skip when the
# ARN is already on the group.
attach_group() {
  local group="$1" policy="$2" arn found
  if [[ "$policy" == arn:* ]]; then
    arn="$policy"
  else
    arn="$(policy_arn "$policy")"
  fi
  found="$(aws iam list-attached-group-policies \
    --group-name "$group" \
    --query "AttachedPolicies[?PolicyArn=='${arn}'].PolicyArn | [0]" \
    --output text)"
  if [[ "$found" == "$arn" ]]; then
    echo "exists: ${group} ${policy}"
    return 0
  fi
  aws iam attach-group-policy --group-name "$group" --policy-arn "$arn"
  echo "attached: ${group} ${policy}"
}

AWS_ACCOUNT_ID="$(env_get AWS_ACCOUNT_ID)"
IAM_ROLE_NAME="$(env_get IAM_ROLE_NAME)"
AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE

if [[ ! "$AWS_ACCOUNT_ID" =~ ^[0-9]{12}$ ]]; then
  echo "Error: AWS_ACCOUNT_ID must be 12 digits." >&2
  exit 1
fi

if [[ -z "$IAM_ROLE_NAME" || ! "$IAM_ROLE_NAME" =~ ^[A-Za-z0-9+=,.@_-]+$ ]]; then
  echo "Error: IAM_ROLE_NAME is empty or has characters that cannot go in a policy ARN." >&2
  exit 1
fi

read -r CALLER_ACCOUNT CALLER_ARN <<<"$(aws sts get-caller-identity --query '[Account,Arn]' --output text)"

if [[ "$CALLER_ACCOUNT" != "$AWS_ACCOUNT_ID" ]]; then
  echo "Error: signed-in account ${CALLER_ACCOUNT} does not match AWS_ACCOUNT_ID." >&2
  exit 1
fi

if [[ "$CALLER_ARN" != *:root ]]; then
  echo "Error: policy changes must run as root. Caller is ${CALLER_ARN}." >&2
  exit 1
fi

WORK="$(mktemp -d)"

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