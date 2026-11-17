
Also paste a short `day18_notes.md` if it is still empty:

```markdown
# Day 18 notes: prompt versioning

**Lab log:** [day18.md](./day18.md)  
**Exam link:** 3.3.7 (manage prompts, e.g. Bedrock Prompt Management)

## Files vs Prompt Management

| Approach | Pros | Cons |
|---|---|---|
| Git YAML (`extract/v1.yaml`) | Diffable, PR review, offline/CI | Needs deploy/restart to switch |
| Prompt Management | Version ARN pin, console test, independent of app code | Extra IAM; harder to diff |

## Lesson from `:1` → `:2`

Vague line-item wording produced `product`/`price`. Explicit field names in the managed prompt fixed shape without changing the model id.