#!/bin/bash
# List hourly resources in REGION. Delete or stop them only when asked.
# teardown: endpoints, NAT gateways, load balancers; stop notebooks and RDS.
# teardown data: also delete OpenSearch domains.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"
MODE="${1:-report}"
FOUND=0

if [[ "$MODE" != "report" && "$MODE" != "teardown" && "$MODE" != "teardown data" ]]; then
  echo "Usage: session-resources.sh [teardown|teardown data]" >&2
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

AWS_ACCOUNT_ID="$(env_get AWS_ACCOUNT_ID)"
REGION="$(env_get REGION)"
AWS_PROFILE="$(env_optional AWS_PROFILE || true)"
[[ -n "${AWS_PROFILE}" ]] && export AWS_PROFILE

read -r CALLER_ACCOUNT CALLER_ARN <<<"$(aws sts get-caller-identity --query '[Account,Arn]' --output text)"
if [[ "$CALLER_ACCOUNT" != "$AWS_ACCOUNT_ID" ]]; then
  echo "Error: signed-in account ${CALLER_ACCOUNT} does not match AWS_ACCOUNT_ID." >&2
  exit 1
fi
if [[ "$MODE" != "report" && "$CALLER_ARN" != *:root ]]; then
  echo "Error: teardown must run as root. Caller is ${CALLER_ARN}." >&2
  exit 1
fi

echo "account ${CALLER_ACCOUNT} region ${REGION} mode ${MODE}"

while IFS=$'\t' read -r name status; do
  [[ -z "${name:-}" || "$name" == "None" ]] && continue
  note "sagemaker-endpoint ${name} ${status}"
  if [[ "$MODE" != "report" ]]; then
    aws sagemaker delete-endpoint --endpoint-name "$name" --region "$REGION"
    echo "deleted endpoint: ${name}"
  fi
done < <(aws sagemaker list-endpoints --region "$REGION" \
  --query 'Endpoints[?EndpointStatus!=`Deleting`].[EndpointName,EndpointStatus]' --output text | tr '\t' '\n' | paste - -)

while IFS=$'\t' read -r name status; do
  [[ -z "${name:-}" || "$name" == "None" ]] && continue
  note "sagemaker-notebook ${name} ${status}"
  if [[ "$MODE" != "report" && "$status" == "InService" ]]; then
    aws sagemaker stop-notebook-instance --notebook-instance-name "$name" --region "$REGION"
    echo "stopped notebook: ${name}"
  fi
done < <(aws sagemaker list-notebook-instances --region "$REGION" \
  --query 'NotebookInstances[?NotebookInstanceStatus!=`Stopped`].[NotebookInstanceName,NotebookInstanceStatus]' --output text | tr '\t' '\n' | paste - -)

while IFS= read -r name; do
  [[ -z "$name" || "$name" == "None" ]] && continue
  note "opensearch-domain ${name}"
  if [[ "$MODE" == "teardown data" ]]; then
    aws opensearch delete-domain --domain-name "$name" --region "$REGION"
    echo "deleted domain: ${name}"
  fi
done < <(aws opensearch list-domain-names --region "$REGION" \
  --query 'DomainNames[].DomainName' --output text | tr '\t' '\n')

while IFS= read -r id; do
  [[ -z "$id" || "$id" == "None" ]] && continue
  note "nat-gateway ${id}"
  if [[ "$MODE" != "report" ]]; then
    aws ec2 delete-nat-gateway --nat-gateway-id "$id" --region "$REGION" >/dev/null
    echo "deleted nat gateway: ${id}"
  fi
done < <(aws ec2 describe-nat-gateways --region "$REGION" \
  --filter Name=state,Values=pending,available \
  --query 'NatGateways[].NatGatewayId' --output text | tr '\t' '\n')

while IFS=$'\t' read -r arn name; do
  [[ -z "${arn:-}" || "$arn" == "None" ]] && continue
  note "load-balancer ${name}"
  if [[ "$MODE" != "report" ]]; then
    aws elbv2 delete-load-balancer --load-balancer-arn "$arn" --region "$REGION"
    echo "deleted load balancer: ${name}"
  fi
done < <(aws elbv2 describe-load-balancers --region "$REGION" \
  --query 'LoadBalancers[].[LoadBalancerArn,LoadBalancerName]' --output text | tr '\t' '\n' | paste - -)

while IFS=$'\t' read -r id status; do
  [[ -z "${id:-}" || "$id" == "None" ]] && continue
  note "rds-instance ${id} ${status}"
  if [[ "$MODE" != "report" && "$status" == "available" ]]; then
    aws rds stop-db-instance --db-instance-identifier "$id" --region "$REGION" >/dev/null
    echo "stopped db instance: ${id}"
  fi
done < <(aws rds describe-db-instances --region "$REGION" \
  --query 'DBInstances[?DBInstanceStatus!=`stopped`].[DBInstanceIdentifier,DBInstanceStatus]' --output text | tr '\t' '\n' | paste - -)

while IFS=$'\t' read -r id status; do
  [[ -z "${id:-}" || "$id" == "None" ]] && continue
  note "rds-cluster ${id} ${status}"
  if [[ "$MODE" != "report" && "$status" == "available" ]]; then
    aws rds stop-db-cluster --db-cluster-identifier "$id" --region "$REGION" >/dev/null
    echo "stopped db cluster: ${id}"
  fi
done < <(aws rds describe-db-clusters --region "$REGION" \
  --query 'DBClusters[?Status!=`stopped`].[DBClusterIdentifier,Status]' --output text | tr '\t' '\n' | paste - -)

while IFS= read -r id; do
  [[ -z "$id" || "$id" == "None" ]] && continue
  note "unattached-volume ${id}"
done < <(aws ec2 describe-volumes --region "$REGION" \
  --filters Name=status,Values=available \
  --query 'Volumes[].VolumeId' --output text | tr '\t' '\n')

if [[ "$FOUND" -eq 0 ]]; then
  echo "none"
  exit 0
fi
if [[ "$MODE" == "report" ]]; then
  exit 2
fi