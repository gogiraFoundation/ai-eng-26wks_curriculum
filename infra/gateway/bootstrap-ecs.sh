#!/usr/bin/env bash
# ECR + cluster + SG + first arm64 image + Fargate service (public IP)
set -euo pipefail

: "${AWS_ACCOUNT_ID:?}"
: "${AWS_REGION:?}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REPO="gateway"
CLUSTER="gateway"
SERVICE="gateway"
TASK_FAMILY="gateway"
EXEC_ROLE="arn:aws:iam::${AWS_ACCOUNT_ID}:role/gateway-exec-role"
TASK_ROLE="arn:aws:iam::${AWS_ACCOUNT_ID}:role/gateway-task-role"
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest"

echo "Caller:"; aws sts get-caller-identity

# ECR
aws ecr describe-repositories --repository-names "$REPO" --region "$AWS_REGION" >/dev/null 2>&1 \
  || aws ecr create-repository --repository-name "$REPO" --region "$AWS_REGION"

# Logs
aws logs create-log-group --log-group-name /ecs/gateway --region "$AWS_REGION" 2>/dev/null || true

# Default VPC + public subnets
VPC=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true \
  --query 'Vpcs[0].VpcId' --output text --region "$AWS_REGION")
SUBNETS=$(aws ec2 describe-subnets --filters Name=vpc-id,Values="$VPC" \
  --query 'Subnets[*].SubnetId' --output text --region "$AWS_REGION")
SUBNET_CSV=$(echo "$SUBNETS" | tr '\t' ',')

SG=$(aws ec2 describe-security-groups \
  --filters Name=vpc-id,Values="$VPC" Name=group-name,Values=gateway-sg \
  --query 'SecurityGroups[0].GroupId' --output text --region "$AWS_REGION")
if [[ "$SG" == "None" || -z "$SG" ]]; then
  SG=$(aws ec2 create-security-group --group-name gateway-sg \
    --description "gateway lab :8000" --vpc-id "$VPC" \
    --query GroupId --output text --region "$AWS_REGION")
  aws ec2 authorize-security-group-ingress --group-id "$SG" \
    --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region "$AWS_REGION"
fi
echo "SG=$SG VPC=$VPC SUBNETS=$SUBNET_CSV"

# Build + push arm64
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

docker buildx create --use --name gatewaybuilder 2>/dev/null || docker buildx use gatewaybuilder
docker buildx build \
  -f "$ROOT/docker/dockerfile" \
  --platform linux/arm64 \
  -t "$IMAGE_URI" \
  --push \
  "$ROOT"

# Cluster
aws ecs describe-clusters --clusters "$CLUSTER" --region "$AWS_REGION" \
  --query 'clusters[0].status' --output text 2>/dev/null | grep -q ACTIVE \
  || aws ecs create-cluster --cluster-name "$CLUSTER" --region "$AWS_REGION"

# Task definition
cat > /tmp/gateway-td.json <<EOF
{
  "family": "${TASK_FAMILY}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "${EXEC_ROLE}",
  "taskRoleArn": "${TASK_ROLE}",
  "runtimePlatform": {
    "cpuArchitecture": "ARM64",
    "operatingSystemFamily": "LINUX"
  },
  "containerDefinitions": [{
    "name": "gateway",
    "image": "${IMAGE_URI}",
    "essential": true,
    "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
    "environment": [
      {"name": "LLM_PROVIDER", "value": "bedrock"},
      {"name": "AWS_REGION", "value": "${AWS_REGION}"},
      {"name": "BEDROCK_MODEL", "value": "eu.amazon.nova-micro-v1:0"},
      {"name": "PROMPT_VERSION", "value": "v1"}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/gateway",
        "awslogs-region": "${AWS_REGION}",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }]
}
EOF
aws ecs register-task-definition --cli-input-json file:///tmp/gateway-td.json --region "$AWS_REGION"

# Service
if aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --region "$AWS_REGION" --query 'services[0].status' --output text 2>/dev/null | grep -q ACTIVE; then
  aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" \
    --task-definition "$TASK_FAMILY" --force-new-deployment --region "$AWS_REGION"
else
  aws ecs create-service \
    --cluster "$CLUSTER" \
    --service-name "$SERVICE" \
    --task-definition "$TASK_FAMILY" \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_CSV}],securityGroups=[${SG}],assignPublicIp=ENABLED}" \
    --region "$AWS_REGION"
fi

echo "Wait ~60s then:"
echo "  aws ecs list-tasks --cluster $CLUSTER --service-name $SERVICE --region $AWS_REGION"
echo "  aws ecs describe-tasks --cluster $CLUSTER --tasks <TASK_ARN> --region $AWS_REGION \\
    --query 'tasks[0].attachments[0].details'"