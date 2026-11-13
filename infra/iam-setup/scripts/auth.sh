#!/usr/bin/env bash
# infra/iam-setup/scripts/auth.sh
# Short-lived AWS CLI auth via profile login. No access keys.
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

PROFILE="${AWS_PROFILE:-agent-toolkit}"
# .env key is REGION. AWS_REGION is the variable the AWS CLI reads.
REGION="$(env_optional REGION || true)"
[[ -z "$REGION" ]] && REGION="${AWS_REGION:-eu-north-1}"
export AWS_REGION="$REGION"
export AWS_DEFAULT_REGION="$REGION"

log_info()  { echo "INFO: $*"; }
log_error() { echo "ERROR: $*" >&2; }

usage() {
  cat <<EOF
Usage: $(basename "$0") <sign-in|sign-out|whoami>

  sign-in   aws login for PROFILE (${PROFILE}), clear Bedrock bearer token
  sign-out  unset common AWS env overrides for this shell
  whoami    print caller identity

Defaults: AWS_PROFILE=${PROFILE}  AWS_REGION=${REGION}
EOF
}

sign_in() {
  # Prefer profile credentials from aws login over env keys / Bedrock API tokens.
  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_BEARER_TOKEN_BEDROCK || true
  export AWS_PROFILE="$PROFILE"
  export AWS_REGION="$REGION"
  export AWS_DEFAULT_REGION="$REGION"

  log_info "Logging in profile=${AWS_PROFILE} region=${AWS_REGION}"
  aws login --region "$AWS_REGION" --profile "$AWS_PROFILE"
  whoami
}

sign_out() {
  unset AWS_PROFILE AWS_REGION AWS_DEFAULT_REGION \
        AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN \
        AWS_BEARER_TOKEN_BEDROCK || true
  log_info "AWS env overrides cleared for this shell"
}

whoami() {
  aws sts get-caller-identity --profile "${AWS_PROFILE:-$PROFILE}" --region "${AWS_REGION:-$REGION}"
}

main() {
  local cmd="${1:-}"
  case "$cmd" in
    sign-in|login)  sign_in ;;
    sign-out|logout) sign_out ;;
    whoami)         whoami ;;
    -h|--help|"")   usage; [[ -n "$cmd" ]] || exit 1 ;;
    *) log_error "Unknown command: $cmd"; usage; exit 1 ;;
  esac
}

main "$@"