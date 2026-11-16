# Day 18 lab log: prompt versioning and Bedrock Prompt Management

**Syllabus:** Day 18 · Thu 12 Nov 2026 · Prompt versioning and Bedrock Prompt Management  
**Time:** 75 min (20m docs · 40m YAML + Prompt Management · 15m pros/cons)  
**Deliverable:** Loader by name+version; one Prompt Management version invoked from code  
**Theory:** [day18_notes.md](./day18_notes.md)  
**Region:** `eu-north-1` · model: `eu.amazon.nova-micro-v1:0`

## Task status

- [ ] Read Bedrock Prompt Management docs
- [ ] `src/prompts/extract/v1.yaml` and `v2.yaml` with metadata
- [ ] Loader: select prompt by name + version from config
- [ ] Create prompt + version in Prompt Management; invoke via Converse
- [ ] Pros/cons of files vs Prompt Management
- [ ] Self-check: roll back a bad prompt in under a minute

## Check yourself

**How do you roll back a bad prompt version in under a minute?**

> Files: point config at the previous version id (`v1`) and redeploy/restart.  
> Prompt Management: set `modelId` / config ARN to the previous version ARN (`…:prompt/ID:1` instead of `:2`) and redeploy; draft keeps iterating without touching prod.