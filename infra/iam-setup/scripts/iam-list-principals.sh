#!/usr/bin/env bash
# infra/iam-setup/scripts/iam-list-principals.sh
# Read-only inventory: IAM users (groups + policies) and roles (trust summary).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"

env_optional() {
  local key="$1" line value
  [[ -f "$ENV_FILE" ]] || return 0
  line="$(grep -E "^${key}=" "$ENV_FILE" | tail -n 1 || true)"
  [[ -z "$line" ]] && return 0
  value="${line#*=}"
  value="${value%\"}"
  value="${value#\"}"
  printf '%s' "$value"
}

AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
# .env key is REGION. AWS_REGION is the variable the AWS CLI reads.
file_region="$(env_optional REGION || true)"
if [[ -n "$file_region" ]]; then
  AWS_REGION="$file_region"
elif [[ -z "${AWS_REGION:-}" ]]; then
  AWS_REGION="eu-north-1"
fi
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE
export AWS_REGION
export AWS_DEFAULT_REGION="$AWS_REGION"

aws_cli() {
  if [[ -n "${AWS_PROFILE:-}" ]]; then
    aws --profile "$AWS_PROFILE" --region "$AWS_REGION" "$@"
  else
    aws --region "$AWS_REGION" "$@"
  fi
}

join_or_dash() {
  local s
  s="$(paste -sd ', ' - 2>/dev/null || true)"
  [[ -n "$s" ]] && printf '%s' "$s" || printf '%s' "-"
}

echo "Caller:"
aws_cli sts get-caller-identity --output table
echo

echo "=== IAM users ==="
USERS="$(aws_cli iam list-users --query 'Users[].UserName' --output text)"
if [[ -z "${USERS// }" ]]; then
  echo "(no IAM users)"
else
  printf '%-40s %-35s %-40s %s\n' "USER" "GROUPS" "ATTACHED_POLICIES" "INLINE_POLICIES"
  printf '%-40s %-35s %-40s %s\n' "----" "------" "-----------------" "---------------"
  for user in $USERS; do
    groups="$(aws_cli iam list-groups-for-user --user-name "$user" \
      --query 'Groups[].GroupName' --output text | tr '\t' '\n' | join_or_dash)"
    attached="$(aws_cli iam list-attached-user-policies --user-name "$user" \
      --query 'AttachedPolicies[].PolicyName' --output text | tr '\t' '\n' | join_or_dash)"
    inline="$(aws_cli iam list-user-policies --user-name "$user" \
      --query 'PolicyNames' --output text | tr '\t' '\n' | join_or_dash)"
    printf '%-40s %-35s %-40s %s\n' "$user" "$groups" "$attached" "$inline"
  done
fi

echo
echo
echo "=== IAM groups (members + attached policies) ==="
GROUP_NAMES="$(aws_cli iam list-groups --query 'Groups[].GroupName' --output text)"
if [[ -z "${GROUP_NAMES// }" ]]; then
  echo "(no IAM groups)"
else
  printf '%-35s %-40s %s\n' "GROUP" "MEMBERS" "ATTACHED_POLICIES"
  printf '%-35s %-40s %s\n' "-----" "-------" "-----------------"
  for group in $GROUP_NAMES; do
    members="$(aws_cli iam get-group --group-name "$group" \
      --query 'Users[].UserName' --output text | tr '\t' '\n' | join_or_dash)"
    attached="$(aws_cli iam list-attached-group-policies --group-name "$group" \
      --query 'AttachedPolicies[].PolicyName' --output text | tr '\t' '\n' | join_or_dash)"
    printf '%-35s %-40s %s\n' "$group" "$members" "$attached"
  done
fi

echo
echo "=== IAM roles (assume-role trust principals) ==="
ROLES="$(aws_cli iam list-roles --query 'Roles[].RoleName' --output text)"
if [[ -z "${ROLES// }" ]]; then
  echo "(no IAM roles)"
else
  printf '%-40s %s\n' "ROLE" "TRUST_AWS_PRINCIPALS"
  printf '%-40s %s\n' "----" "--------------------"
  for role in $ROLES; do
    # Service roles (lambda.amazonaws.com etc.) show under Service; users/roles under AWS.
    principals="$(aws_cli iam get-role --role-name "$role" \
      --query 'Role.AssumeRolePolicyDocument.Statement[].Principal.[AWS,Service]' \
      --output text 2>/dev/null | tr '\t' '\n' | sed '/^None$/d;/^$/d' | sort -u | join_or_dash)"
    printf '%-40s %s\n' "$role" "$principals"
  done
fi