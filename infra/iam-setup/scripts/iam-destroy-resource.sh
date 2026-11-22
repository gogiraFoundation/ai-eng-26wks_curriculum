#!/bin/bash
# Find (and optionally tear down) hourly billable compute in REGION.
# NEVER touches IAM users, groups, roles, or Bedrock policies.
#
# Usage:
#   bash infra/iam-setup/scripts/iam-destroy-resource.sh            # report
#   bash infra/iam-setup/scripts/iam-destroy-resource.sh teardown   # stop/delete billable
#   bash infra/iam-setup/scripts/iam-destroy-resource.sh "teardown data"  # + OpenSearch
#
# Intentional IAM lab wipe (breaks Bedrock until re-setup):
#   bash infra/iam-setup/scripts/iam-destroy-lab-iam.sh destroy
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"
MODE="${1:-report}"
FOUND=0
SKIPPED=0

if [[ "${1:-}" == "destroy" ]]; then
  echo "Error: this script no longer destroys IAM (that broke Bedrock access)." >&2
  echo "Billable compute:  bash $0 teardown" >&2
  echo "Lab IAM wipe:      bash ${SCRIPT_DIR}/iam-destroy-lab-iam.sh destroy" >&2
  exit 1
fi

if [[ "$MODE" != "report" && "$MODE" != "teardown" && "$MODE" != "teardown data" ]]; then
  echo "Usage: iam-destroy-resource.sh [teardown|teardown data]" >&2
  echo "  (default) report     list billable resources" >&2
  echo "  teardown             stop/delete billable compute (not IAM)" >&2
  echo "  teardown data        also delete OpenSearch domains" >&2
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

note() {
  FOUND=1
  printf '%s\n' "$1"
}

skip_denied() {
  # Soft-fail AccessDenied so least-privilege users still get a partial report.
  SKIPPED=1
  printf 'skip (AccessDenied): %s\n' "$1" >&2
}

aws_ok() {
  # Run aws; on AccessDenied print skip and return 1; other failures return 2.
  local out
  if out="$( "$@" 2>&1 )"; then
    printf '%s' "$out"
    return 0
  fi
  if [[ "$out" == *AccessDenied* || "$out" == *UnauthorizedOperation* || "$out" == *"not authorized"* ]]; then
    skip_denied "$*"
    return 1
  fi
  printf '%s\n' "$out" >&2
  return 2
}

AWS_ACCOUNT_ID="$(env_get AWS_ACCOUNT_ID)"
REGION="$(env_get REGION)"
AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE
export AWS_REGION="$REGION"
export AWS_DEFAULT_REGION="$REGION"

read -r CALLER_ACCOUNT CALLER_ARN <<<"$(aws sts get-caller-identity --query '[Account,Arn]' --output text)"
if [[ "$CALLER_ACCOUNT" != "$AWS_ACCOUNT_ID" ]]; then
  echo "Error: signed-in account ${CALLER_ACCOUNT} does not match AWS_ACCOUNT_ID." >&2
  exit 1
fi
if [[ "$MODE" != "report" && "$CALLER_ARN" != *:root ]]; then
  echo "Error: teardown must run as root. Caller is ${CALLER_ARN}." >&2
  echo "Tip: report mode works as the IAM user; teardown needs root." >&2
  exit 1
fi

echo "account ${CALLER_ACCOUNT} region ${REGION} mode ${MODE}"
echo "scope: billable compute only (IAM / Bedrock policies untouched)"

# --- SageMaker endpoints ---
if out="$(aws_ok aws sagemaker list-endpoints --region "$REGION" \
  --query 'Endpoints[?EndpointStatus!=`Deleting`].[EndpointName,EndpointStatus]' --output text)"; then
  while IFS=$'\t' read -r name status; do
    [[ -z "${name:-}" || "$name" == "None" ]] && continue
    note "sagemaker-endpoint ${name} ${status}"
    if [[ "$MODE" != "report" ]]; then
      aws sagemaker delete-endpoint --endpoint-name "$name" --region "$REGION"
      echo "deleted endpoint: ${name}"
    fi
  done < <(printf '%s\n' "$out" | tr '\t' '\n' | paste - -)
fi

# --- SageMaker notebooks ---
if out="$(aws_ok aws sagemaker list-notebook-instances --region "$REGION" \
  --query 'NotebookInstances[?NotebookInstanceStatus!=`Stopped`].[NotebookInstanceName,NotebookInstanceStatus]' --output text)"; then
  while IFS=$'\t' read -r name status; do
    [[ -z "${name:-}" || "$name" == "None" ]] && continue
    note "sagemaker-notebook ${name} ${status}"
    if [[ "$MODE" != "report" && "$status" == "InService" ]]; then
      aws sagemaker stop-notebook-instance --notebook-instance-name "$name" --region "$REGION"
      echo "stopped notebook: ${name}"
    fi
  done < <(printf '%s\n' "$out" | tr '\t' '\n' | paste - -)
fi

# --- OpenSearch ---
if out="$(aws_ok aws opensearch list-domain-names --region "$REGION" \
  --query 'DomainNames[].DomainName' --output text)"; then
  while IFS= read -r name; do
    [[ -z "$name" || "$name" == "None" ]] && continue
    note "opensearch-domain ${name}"
    if [[ "$MODE" == "teardown data" ]]; then
      aws opensearch delete-domain --domain-name "$name" --region "$REGION"
      echo "deleted domain: ${name}"
    fi
  done < <(printf '%s\n' "$out" | tr '\t' '\n')
fi

# --- NAT gateways ---
if out="$(aws_ok aws ec2 describe-nat-gateways --region "$REGION" \
  --filter Name=state,Values=pending,available \
  --query 'NatGateways[].NatGatewayId' --output text)"; then
  while IFS= read -r id; do
    [[ -z "$id" || "$id" == "None" ]] && continue
    note "nat-gateway ${id}"
    if [[ "$MODE" != "report" ]]; then
      aws ec2 delete-nat-gateway --nat-gateway-id "$id" --region "$REGION" >/dev/null
      echo "deleted nat gateway: ${id}"
    fi
  done < <(printf '%s\n' "$out" | tr '\t' '\n')
fi

# --- Load balancers ---
if out="$(aws_ok aws elbv2 describe-load-balancers --region "$REGION" \
  --query 'LoadBalancers[].[LoadBalancerArn,LoadBalancerName]' --output text)"; then
  while IFS=$'\t' read -r arn name; do
    [[ -z "${arn:-}" || "$arn" == "None" ]] && continue
    note "load-balancer ${name}"
    if [[ "$MODE" != "report" ]]; then
      aws elbv2 delete-load-balancer --load-balancer-arn "$arn" --region "$REGION"
      echo "deleted load balancer: ${name}"
    fi
  done < <(printf '%s\n' "$out" | tr '\t' '\n' | paste - -)
fi

# --- RDS ---
if out="$(aws_ok aws rds describe-db-instances --region "$REGION" \
  --query 'DBInstances[?DBInstanceStatus!=`stopped`].[DBInstanceIdentifier,DBInstanceStatus]' --output text)"; then
  while IFS=$'\t' read -r id status; do
    [[ -z "${id:-}" || "$id" == "None" ]] && continue
    note "rds-instance ${id} ${status}"
    if [[ "$MODE" != "report" && "$status" == "available" ]]; then
      aws rds stop-db-instance --db-instance-identifier "$id" --region "$REGION" >/dev/null
      echo "stopped db instance: ${id}"
    fi
  done < <(printf '%s\n' "$out" | tr '\t' '\n' | paste - -)
fi

if out="$(aws_ok aws rds describe-db-clusters --region "$REGION" \
  --query 'DBClusters[?Status!=`stopped`].[DBClusterIdentifier,Status]' --output text)"; then
  while IFS=$'\t' read -r id status; do
    [[ -z "${id:-}" || "$id" == "None" ]] && continue
    note "rds-cluster ${id} ${status}"
    if [[ "$MODE" != "report" && "$status" == "available" ]]; then
      aws rds stop-db-cluster --db-cluster-identifier "$id" --region "$REGION" >/dev/null
      echo "stopped db cluster: ${id}"
    fi
  done < <(printf '%s\n' "$out" | tr '\t' '\n' | paste - -)
fi

# --- Unattached EBS (report only; delete is easy to regret) ---
if out="$(aws_ok aws ec2 describe-volumes --region "$REGION" \
  --filters Name=status,Values=available \
  --query 'Volumes[].VolumeId' --output text)"; then
  while IFS= read -r id; do
    [[ -z "$id" || "$id" == "None" ]] && continue
    note "unattached-volume ${id}"
  done < <(printf '%s\n' "$out" | tr '\t' '\n')
fi

# --- ECS Fargate: scale services to 0 (and delete on teardown) ---
if clusters="$(aws_ok aws ecs list-clusters --region "$REGION" --query 'clusterArns[]' --output text)"; then
  for cluster_arn in $clusters; do
    [[ -z "$cluster_arn" || "$cluster_arn" == "None" ]] && continue
    cluster="${cluster_arn##*/}"
    if services="$(aws_ok aws ecs list-services --cluster "$cluster" --region "$REGION" \
      --query 'serviceArns[]' --output text)"; then
      for service_arn in $services; do
        [[ -z "$service_arn" || "$service_arn" == "None" ]] && continue
        service="${service_arn##*/}"
        desired="$(aws ecs describe-services --cluster "$cluster" --services "$service" \
          --region "$REGION" --query 'services[0].desiredCount' --output text 2>/dev/null || echo "?")"
        running="$(aws ecs describe-services --cluster "$cluster" --services "$service" \
          --region "$REGION" --query 'services[0].runningCount' --output text 2>/dev/null || echo "?")"
        note "ecs-service ${cluster}/${service} desired=${desired} running=${running}"
        if [[ "$MODE" != "report" ]]; then
          aws ecs update-service --cluster "$cluster" --service "$service" \
            --desired-count 0 --region "$REGION" >/dev/null
          echo "scaled to 0: ${cluster}/${service}"
          aws ecs delete-service --cluster "$cluster" --service "$service" \
            --force --region "$REGION" >/dev/null
          echo "deleted service: ${cluster}/${service}"
        fi
      done
    fi
  done
fi

# --- ECR: report only (storage is small; emptying shared repos is easy to regret) ---
if repos="$(aws_ok aws ecr describe-repositories --region "$REGION" \
  --query 'repositories[].repositoryName' --output text)"; then
  while IFS= read -r repo; do
    [[ -z "$repo" || "$repo" == "None" ]] && continue
    note "ecr-repository ${repo} (report only; empty manually if needed)"
  done < <(printf '%s\n' "$repos" | tr '\t' '\n')
fi

if [[ "$FOUND" -eq 0 ]]; then
  echo "none"
  if [[ "$SKIPPED" -eq 1 ]]; then
    echo "(some APIs skipped due to AccessDenied; re-run as root for a full scan)" >&2
  fi
  exit 0
fi
if [[ "$MODE" == "report" ]]; then
  if [[ "$SKIPPED" -eq 1 ]]; then
    echo "(some APIs skipped due to AccessDenied; re-run as root for a full scan)" >&2
  fi
  exit 2
fi
