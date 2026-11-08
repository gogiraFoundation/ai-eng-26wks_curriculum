#!/bin/bash
# Apply IAM setup, then read the budgets named in .env.
# Sign in as root on the AWS_PROFILE in .env before running this.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

run_script() {
  local script_path="${ROOT}/infra/iam-setup/scripts/${1}.sh"
  if [[ ! -f "$script_path" ]]; then
    echo "Error: missing ${script_path}." >&2
    exit 1
  fi
  echo "run: ${1}"
  bash "$script_path"
}

run_script iam-groups
run_script iam-security
run_script iam-roles
run_script iam-assign-users
run_script iam-budgets