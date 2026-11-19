# Day 21 lab log: Week 3 review + ship

**Syllabus:** Day 21 · Token economics write-up, Skill Builder (2nd half), exam-map, weekly review  
**Deliverable:** Push + tag `prompts-v0.1`  
**Theory:** [day21_notes.md](./day21_notes.md) · one-pager: [token-economics.md](./token-economics.md)  
**Evidence:** Day 17 `reports/day17/` · Day 20 `reports/prompt-cost-latency.md` (`0c597a3e`)

## Task status

- [ ] One-page token economics explainer (own words + Day 17/20 evidence)
- [ ] Skill Builder: Foundations of Prompt Engineering (second half)
- [ ] exam-map: 3.3.7, 4.2.9, 4.2.10 with Week 3 evidence
- [ ] Weekly review (done / waiting on Bedrock / carries to Week 4)
- [ ] Push + tag `prompts-v0.1`
- [ ] Self-check: two sentences for a product manager

## Time box (~2 h)

| Block | Focus |
|---|---|
| ~40m | Write `token-economics.md` |
| 40m | Skill Builder second half |
| 20m | Update `notes/exams/exam-map.md` |
| 20m | Weekly review + tag |

## Check yourself

**How would you explain token economics to a product manager in two sentences?**

>We pay per token: long prompts and big models raise cost even when quality does not. This week, caching halved our per-1k cost without faster latency, and Nova Micro with prompt v3 beat Lite on both accuracy and price, so we ship that default.

## Tag

```bash
git status
git add -A   # do NOT add .env
git commit -m "$(cat <<'EOF'
Ship Week 3 prompt library, caching, and cost harness.

EOF
)"
git push
git tag -a prompts-v0.1 -m "Week 3: prompts, caching, harness"
git push origin prompts-v0.1