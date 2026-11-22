# Gateway infra (Day 27, lean)

Region: `eu-north-1` · Arch: `linux/arm64` · No ALB · Public IP Fargate  
Tear down: `aws ecs update-service --desired-count 0` or delete resources in reverse.

## One-time (root/admin)

```bash
export AWS_PROFILE=YOUR_ROOT_OR_ADMIN_PROFILE
export AWS_REGION=YOUR_AWS_REGION
export AWS_ACCOUNT_ID=YOUR_AWS_ACCOUNT_ID
export GITHUB_ORG=YOUR_ORGANIZATION
export GITHUB_REPO=ai-eng-26wks_curriculum
bash infra/gateway/bootstrap-iam.sh


### App resources + first deploy
export AWS_PROFILE=YOUR_ROOT_OR_ADMIN_PROFILE   # or a user that can ECR/ECS

export AWS_REGION=YOUR_AWS_REGION
export AWS_ACCOUNT_ID=YOUR_AWS_ACCOUNT_ID
bash infra/gateway/bootstrap-ecs.sh