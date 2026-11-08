#!/bin/bash
# Remove the groups, customer managed policies, and role created by run-setup.sh.
# Does not delete the IAM user, the budgets, or SignInLocalDevelopmentAccess.
# Caller must be the account root. Pass the argument: destroy
set -euo pipefail

if [[ "${1:-}" != "destroy" ]]; then
  echo "Error: pass 'destroy' to remove the IAM resources from .env." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"
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

known_group_policy() {
  local arn="$1" name
  [[ "$arn" == "$SIGN_IN_POLICY" ]] && return 0
  for name in "${POLICIES[@]}"; do
    [[ "$arn" == "$(policy_arn "$name")" ]] && return 0
  done
  return 1
}

known_role_policy() {
  local arn="$1" name
  for name in "${ROLE_POLICIES[@]}"; do
    [[ "$arn" == "$(policy_arn "$name")" ]] && return 0
  done
  return 1
}

AWS_ACCOUNT_ID="$(env_get AWS_ACCOUNT_ID)"
AWS_IAM_USER_ARN="$(env_get AWS_IAM_USER_ARN)"
IAM_GROUP_NAMES="$(env_get IAM_GROUP_NAMES)"
IAM_ROLE_NAME="$(env_get IAM_ROLE_NAME)"
IAM_ROLE_POLICIES="$(env_get IAM_ROLE_POLICIES)"
AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE

IAM_USER="${AWS_IAM_USER_ARN##*/}"
IFS='|' read -r -a GROUPS <<<"$IAM_GROUP_NAMES"
IFS='|' read -r -a ROLE_POLICIES <<<"$IAM_ROLE_POLICIES"

read -r CALLER_ACCOUNT CALLER_ARN <<<"$(aws sts get-caller-identity --query '[Account,Arn]' --output text)"

if [[ "$CALLER_ACCOUNT" != "$AWS_ACCOUNT_ID" ]]; then
  echo "Error: signed-in account ${CALLER_ACCOUNT} does not match AWS_ACCOUNT_ID." >&2
  exit 1
fi

if [[ "$CALLER_ARN" != *:root ]]; then
  echo "Error: destroy must run as root. Caller is ${CALLER_ARN}." >&2
  exit 1
fi

if aws iam get-role --role-name "$IAM_ROLE_NAME" >/dev/null 2>&1; then
  inline="$(aws iam list-role-policies --role-name "$IAM_ROLE_NAME" --query 'PolicyNames[]' --output text)"
  profiles="$(aws iam list-instance-profiles-for-role --role-name "$IAM_ROLE_NAME" --query 'InstanceProfiles[].InstanceProfileName' --output text)"
  if [[ -n "$inline" && "$inline" != "None" ]]; then
    echo "Error: role ${IAM_ROLE_NAME} has inline policies: ${inline}." >&2
    exit 1
  fi
  if [[ -n "$profiles" && "$profiles" != "None" ]]; then
    echo "Error: role ${IAM_ROLE_NAME} is in an instance profile: ${profiles}." >&2
    exit 1
  fi
  while IFS= read -r arn; do
    [[ -z "$arn" || "$arn" == "None" ]] && continue
    if ! known_role_policy "$arn"; then
      echo "Error: role ${IAM_ROLE_NAME} has an unexpected policy: ${arn}." >&2
      exit 1
    fi
    aws iam detach-role-policy --role-name "$IAM_ROLE_NAME" --policy-arn "$arn"
    echo "detached from role: ${arn}"
  done < <(aws iam list-attached-role-policies --role-name "$IAM_ROLE_NAME" \
    --query 'AttachedPolicies[].PolicyArn' --output text | tr '\t' '\n')
  aws iam delete-role --role-name "$IAM_ROLE_NAME"
  echo "deleted role: ${IAM_ROLE_NAME}"
else
  echo "absent role: ${IAM_ROLE_NAME}"
fi

for group in "${GROUPS[@]}"; do
  if ! aws iam get-group --group-name "$group" >/dev/null 2>&1; then
    echo "absent group: ${group}"
    continue
  fi
  inline="$(aws iam list-group-policies --group-name "$group" --query 'PolicyNames[]' --output text)"
  if [[ -n "$inline" && "$inline" != "None" ]]; then
    echo "Error: group ${group} has inline policies: ${inline}." >&2
    exit 1
  fi
  while IFS= read -r user; do
    [[ -z "$user" || "$user" == "None" ]] && continue
    if [[ "$user" != "$IAM_USER" ]]; then
      echo "Error: group ${group} contains ${user}. This script only removes ${IAM_USER}." >&2
      exit 1
    fi
    aws iam remove-user-from-group --group-name "$group" --user-name "$user"
    echo "removed: ${user} from ${group}"
  done < <(aws iam get-group --group-name "$group" --query 'Users[].UserName' --output text | tr '\t' '\n')
  while IFS= read -r arn; do
    [[ -z "$arn" || "$arn" == "None" ]] && continue
    if ! known_group_policy "$arn"; then
      echo "Error: group ${group} has an unexpected policy: ${arn}." >&2
      exit 1
    fi
    aws iam detach-group-policy --group-name "$group" --policy-arn "$arn"
    echo "detached from ${group}: ${arn}"
  done < <(aws iam list-attached-group-policies --group-name "$group" \
    --query 'AttachedPolicies[].PolicyArn' --output text | tr '\t' '\n')
  aws iam delete-group --group-name "$group"
  echo "deleted group: ${group}"
done

for name in "${POLICIES[@]}"; do
  arn="$(policy_arn "$name")"
  if ! aws iam get-policy --policy-arn "$arn" >/dev/null 2>&1; then
    echo "absent policy: ${name}"
    continue
  fi
  left="$(aws iam list-entities-for-policy --policy-arn "$arn" \
    --query 'length(PolicyGroups) + length(PolicyUsers) + length(PolicyRoles)' --output text)"
  if [[ "$left" != "0" ]]; then
    echo "Error: policy ${name} is still attached to ${left} entities." >&2
    exit 1
  fi
  while IFS= read -r version; do
    [[ -z "$version" || "$version" == "None" ]] && continue
    aws iam delete-policy-version --policy-arn "$arn" --version-id "$version"
  done < <(aws iam list-policy-versions --policy-arn "$arn" \
    --query 'Versions[?IsDefaultVersion==`false`].VersionId' --output text | tr '\t' '\n')
  aws iam delete-policy --policy-arn "$arn"
  echo "deleted policy: ${name}"
done