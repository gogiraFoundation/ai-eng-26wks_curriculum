#!/usr/bin/env bash
# Apply IAM setup, then read the budgets named in .env.
# Sign in as root on the AWS_PROFILE in .env before running this.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-$ROOT/.env}"

env_get() {
  local key="$1" line value
  if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: missing ${ENV_FILE}." >&2
    exit 1
  fi
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
  [[ -f "$ENV_FILE" ]] || return 0
  line="$(grep -E "^${key}=" "$ENV_FILE" | tail -n 1 || true)"
  [[ -z "$line" ]] && return 0
  value="${line#*=}"
  value="${value%\"}"
  value="${value#\"}"
  printf '%s' "$value"
}

confirm_root() {
  local profile="$1" arn
  arn="$(aws sts get-caller-identity --profile "$profile" --query Arn --output text)"
  if [[ "$arn" != *:root ]]; then
    echo "Error: AWS_PROFILE=${profile} must be account root for apply." >&2
    echo "Caller is ${arn}" >&2
    echo "Run: bash infra/iam-setup/scripts/auth.sh sign-in" >&2
    echo "Sign in as root, then re-run this script." >&2
    exit 1
  fi
  echo "OK: root session on profile=${profile} (${arn})"
}

run_script() {
  local script_path="${ROOT}/infra/iam-setup/scripts/${1}.sh"
  if [[ ! -f "$script_path" ]]; then
    echo "Error: missing ${script_path}." >&2
    exit 1
  fi
  echo "run: ${1}"
  bash "$script_path"
}

main() {
  local profile region
  profile="$(env_optional AWS_PROFILE || true)"
  # .env key is REGION. AWS_REGION is the variable the AWS CLI reads.
  region="$(env_optional REGION || true)"
  [[ -z "$profile" ]] && profile="agent-toolkit"
  [[ -z "$region" ]] && region="${AWS_REGION:-}"
  [[ -z "$region" ]] && region="eu-north-1"

  export AWS_PROFILE="$profile"
  export AWS_REGION="$region"
  export AWS_DEFAULT_REGION="$region"

  # Do not auto-login here: apply must be an explicit root choice.
  confirm_root "$AWS_PROFILE"

  # Order matters: groups before policy attach; policies before role attach.
  run_script iam-groups
  run_script iam-security
  run_script iam-roles
  run_script iam-assign-users
  run_script iam-budgets
  run_script iam-list-principals

  echo
  echo "Apply finished. Sign the profile back in as the daily IAM user (not root):"
  echo "  bash infra/iam-setup/scripts/auth.sh sign-in"
}

main "$@"