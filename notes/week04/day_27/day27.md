# Day 27 lab log: deploy with CI/CD

**Syllabus:** Day 27 · Sat 21 Nov 2026 · Build day: deploy with CI/CD  
**Time:** 3 h (30m GitHub OIDC · 90m Actions → ECR → ECS · 30m smoke · 30m diagram)  
**Deliverable:** Live gateway URL; green pipeline; tear down or desired count = 0 after smoke  
**Decision:** [ADR-001](../../../docs/adr-001-deploy-target.md) → **ECS Fargate ARM64** in `eu-north-1`  
**Theory:** [day27_notes.md](./day27_notes.md)  
**Repo:** `gogiraFoundation/ai-eng-26wks_curriculum`  
**Free resources:** [GitHub OIDC → AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services) · [AWS Security Blog: IAM + GitHub OIDC](https://aws.amazon.com/blogs/security/use-iam-roles-to-connect-github-actions-to-actions-in-aws/) · [ECS developer guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html) · [CDK v2](https://docs.aws.amazon.com/cdk/v2/guide/home.html)

## Task status

- [ ] Confirm spend limit / budget alarm (AWS Settings → Billing)
- [ ] GitHub OIDC IdP + deploy role (trust locked to this repo)
- [ ] ECR repository + push `gateway` image (linux/arm64)
- [ ] Minimal ECS: cluster + task def + service (public IP lab; no ALB)
- [ ] GitHub Actions: test → build → push → deploy
- [ ] Smoke `https://…` or public IP `:8000` `/health` + `/chat`
- [ ] Architecture diagram (Excalidraw / draw.io)
- [ ] Scale to 0 or destroy stack
- [ ] Self-check: why OIDC instead of access keys

## Lab shape (cheap)

```text
GitHub Actions (OIDC)
        │
        ▼
   ECR :gateway
        │
        ▼
 ECS Fargate task (ARM)
   LLM_PROVIDER=bedrock
   AWS_REGION=eu-north-1
   (Redis optional; cache soft-fails if missing)
        │
        ▼
  public IP:8000  ← tear down after smoke

### Commands (order)

# 0) Budget / spend
# AWS Settings → Billing → confirm spend limit; Budgets console for alarms

# 1) After OIDC role exists (root/admin one-time):
#    Role name e.g. github-deploy-gateway
#    Trust: token.actions.githubusercontent.com
#    Condition sub: repo:gogiraFoundation/ai-eng-26wks_curriculum:*

# 2) Local image sanity (ARM)
docker build -f docker/dockerfile -t gateway:day27 .
docker run --rm -p 8000:8000 \
  -e LLM_PROVIDER=bedrock \
  -e AWS_REGION=eu-north-1 \
  -e AWS_PROFILE=agent-toolkit \
  -v "$HOME/.aws:/home/appuser/.aws:ro" \
  gateway:day27

# 3) CI path (once workflow + infra land)
git push origin HEAD
# watch Actions → ECR push → ECS service update
curl -s http://<PUBLIC_IP>:8000/health

# 4) Stop billing
aws ecs update-service --cluster gateway --service gateway --desired-count 0 \
  --region eu-north-1 --profile agent-toolkit
# or destroy the CloudFormation/CDK stack