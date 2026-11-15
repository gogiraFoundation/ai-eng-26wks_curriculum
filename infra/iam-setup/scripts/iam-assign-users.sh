#!/bin/bash
# Put the IAM user from AWS_IAM_USER_ARN into IAM_USER_GROUP only.
# Removes the user from every other group and detaches policies on the user.
# Caller must be the account root.
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
AWS_IAM_USER_ARN="$(env_get AWS_IAM_USER_ARN)"
IAM_USER_GROUP="$(env_get IAM_USER_GROUP)"
AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE

if [[ -z "$IAM_USER_GROUP" ]]; then
  echo "Error: IAM_USER_GROUP is empty in ${ENV_FILE}." >&2
  exit 1
fi

case "$AWS_IAM_USER_ARN" in
  arn:aws:iam::"${AWS_ACCOUNT_ID}":user/*) ;;
  *)
    echo "Error: AWS_IAM_USER_ARN is not a user in account ${AWS_ACCOUNT_ID}." >&2
    exit 1
    ;;
esac

IAM_USER="${AWS_IAM_USER_ARN##*/}"

read -r CALLER_ACCOUNT CALLER_ARN <<<"$(aws sts get-caller-identity --query '[Account,Arn]' --output text)"

if [[ "$CALLER_ACCOUNT" != "$AWS_ACCOUNT_ID" ]]; then
  echo "Error: signed-in account ${CALLER_ACCOUNT} does not match AWS_ACCOUNT_ID." >&2
  exit 1
fi

if [[ "$CALLER_ARN" != *:root ]]; then
  echo "Error: group membership must run as root. Caller is ${CALLER_ARN}." >&2
  exit 1
fi

aws iam get-user --user-name "$IAM_USER" >/dev/null
aws iam get-group --group-name "$IAM_USER_GROUP" >/dev/null

in_target=0
while IFS= read -r group; do
  [[ -z "$group" || "$group" == "None" ]] && continue
  if [[ "$group" == "$IAM_USER_GROUP" ]]; then
    in_target=1
    continue
  fi
  aws iam remove-user-from-group --user-name "$IAM_USER" --group-name "$group"
  echo "removed: ${IAM_USER} from ${group}"
done < <(aws iam list-groups-for-user --user-name "$IAM_USER" \
  --query 'Groups[].GroupName' --output text | tr '\t' '\n')

if [[ "$in_target" -eq 0 ]]; then
  aws iam add-user-to-group --user-name "$IAM_USER" --group-name "$IAM_USER_GROUP"
  echo "added: ${IAM_USER} to ${IAM_USER_GROUP}"
else
  echo "member: ${IAM_USER} in ${IAM_USER_GROUP}"
fi

while IFS= read -r arn; do
  [[ -z "$arn" || "$arn" == "None" ]] && continue
  aws iam detach-user-policy --user-name "$IAM_USER" --policy-arn "$arn"
  echo "detached: ${arn}"
done < <(aws iam list-attached-user-policies --user-name "$IAM_USER" \
  --query 'AttachedPolicies[].PolicyArn' --output text | tr '\t' '\n')

while IFS= read -r inline_name; do
  [[ -z "$inline_name" || "$inline_name" == "None" ]] && continue
  aws iam delete-user-policy --user-name "$IAM_USER" --policy-name "$inline_name"
  echo "deleted inline: ${inline_name}"
done < <(aws iam list-user-policies --user-name "$IAM_USER" \
  --query 'PolicyNames[]' --output text | tr '\t' '\n')