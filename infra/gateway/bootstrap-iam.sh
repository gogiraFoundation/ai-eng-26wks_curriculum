#!/usr/bin/env bash

# One-time: GitHub OIDC IdP + github-deploy-gateway + ECS task/exec roles
set -euo pipefail

: "${AWS_ACCOUNT_ID:?}"
: "${AWS_REGION:?}"
: "${GITHUB_ORG:?}"
: "${GITHUB_REPO:?}"

OIDC_URL="https://token.actions.githubusercontent.com"
OIDC_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
DEPLOY_ROLE="github-deploy-gateway"
TASK_ROLE="gateway-task-role"
EXEC_ROLE="gateway-exec-role"

echo "Caller:"
aws sts get-caller-identity

# --- OIDC provider (ignore if exists) ---
if ! aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_ARN" >/dev/null 2>&1; then
  THUMBPRINT="ffffffffffffffffffffffffffffffffffffffff"
  aws iam create-open-id-connect-provider \
    --url "$OIDC_URL" \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list "$THUMBPRINT"
  echo "Created OIDC provider"
else
  echo "OIDC provider exists"
fi

# --- Deploy role trust (GitHub Actions → this repo) ---
cat > /tmp/github-deploy-trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "${OIDC_ARN}"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:${GITHUB_ORG}/${GITHUB_REPO}:*"
      }
    }
  }]
}
EOF

if ! aws iam get-role --role-name "$DEPLOY_ROLE" >/dev/null 2>&1; then
  aws iam create-role --role-name "$DEPLOY_ROLE" \
    --assume-role-policy-document file:///tmp/github-deploy-trust.json
else
  aws iam update-assume-role-policy --role-name "$DEPLOY_ROLE" \
    --policy-document file:///tmp/github-deploy-trust.json
fi

cat > /tmp/github-deploy-perm.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EcrAuth",
      "Effect": "Allow",
      "Action": ["ecr:GetAuthorizationToken"],
      "Resource": "*"
    },
    {
      "Sid": "EcrPush",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:DescribeRepositories"
      ],
      "Resource": "arn:aws:ecr:${AWS_REGION}:${AWS_ACCOUNT_ID}:repository/gateway"
    },
    {
      "Sid": "EcsDeploy",
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:DescribeClusters",
        "ecs:DescribeTaskDefinition",
        "ecs:RegisterTaskDefinition"
      ],
      "Resource": "*"
    },
    {
      "Sid": "PassTaskRoles",
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": [
        "arn:aws:iam::${AWS_ACCOUNT_ID}:role/${TASK_ROLE}",
        "arn:aws:iam::${AWS_ACCOUNT_ID}:role/${EXEC_ROLE}"
      ]
    }
  ]
}
EOF
aws iam put-role-policy --role-name "$DEPLOY_ROLE" \
  --policy-name github-deploy-inline --policy-document file:///tmp/github-deploy-perm.json

# --- ECS task execution role (pull image + logs) ---
cat > /tmp/ecs-tasks-trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

if ! aws iam get-role --role-name "$EXEC_ROLE" >/dev/null 2>&1; then
  aws iam create-role --role-name "$EXEC_ROLE" \
    --assume-role-policy-document file:///tmp/ecs-tasks-trust.json
  aws iam attach-role-policy --role-name "$EXEC_ROLE" \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
fi

# --- Task role (Bedrock Nova via inference profile) ---
if ! aws iam get-role --role-name "$TASK_ROLE" >/dev/null 2>&1; then
  aws iam create-role --role-name "$TASK_ROLE" \
    --assume-role-policy-document file:///tmp/ecs-tasks-trust.json
fi

# Attach existing customer policies if present; else inline Nova invoke
for P in bedrock-invoke-nova bedrock-require-inference-profile; do
  ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${P}"
  if aws iam get-policy --policy-arn "$ARN" >/dev/null 2>&1; then
    aws iam attach-role-policy --role-name "$TASK_ROLE" --policy-arn "$ARN" || true
  fi
done

cat > /tmp/task-bedrock.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
      "bedrock:Converse",
      "bedrock:ConverseStream"
    ],
    "Resource": [
      "arn:aws:bedrock:${AWS_REGION}:${AWS_ACCOUNT_ID}:inference-profile/eu.amazon.nova-micro-v1:0",
      "arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0"
    ]
  }]
}
EOF
aws iam put-role-policy --role-name "$TASK_ROLE" \
  --policy-name gateway-bedrock-inline --policy-document file:///tmp/task-bedrock.json

echo "Done. Deploy role ARN:"
echo "arn:aws:iam::${AWS_ACCOUNT_ID}:role/${DEPLOY_ROLE}"