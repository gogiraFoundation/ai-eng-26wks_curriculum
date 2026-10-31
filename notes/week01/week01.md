# Week 1: Setup and LLM Basics

**Dates:** Mon 26 Oct – Sun 1 Nov 2026
**Deliverable:** `llm-cli` v0.1, a CLI chatbot with two backends and streaming

## Schedule

| Day | Date | Topic | Task |
|---|---|---|---|
| 1 | Mon 26 Oct | How LLMs work: tokens, next-token prediction, context windows | Create repo `ai-eng-26wk` with `/notes/week01.md`. Record 3 surprising tokenisation results (code, numbers, non-English). |
| 2 | Tue 27 Oct | AWS account hygiene: budget alarm, Identity Center user, least privilege | Commit `infra/iam-bedrock-policy.json` and a screenshot-free checklist in `notes/aws-setup.md` (budgets, MFA, SSO profile name). Never commit keys. |
| 3 | Wed 28 Oct | First Bedrock call with the Converse API | `src/bedrock_chat.py` prints the answer, input/output tokens, latency (ms) and estimated cost per call. |
| 4 | Thu 29 Oct | Sampling: temperature, top-p, max tokens, streaming | Add `--temperature` and `--stream` flags. Save a short table of output variance per temperature in the notes. |
| 5 | Fri 30 Oct | Rest day | |
| 6 | Sat 31 Oct | Build day: CLI chatbot with two backends | Working `llm-cli chat --provider bedrock\|direct` with streaming and a running token/cost total. |
| 7 | Sun 1 Nov | Ship and weekly review | Push the `llm-cli` v0.1 tag. Add `notes/exam-map.md` with the 4 exam domains and weights (28/24/24/24) to fill in every week. |

---

## Day 1: How LLMs work (75 min)

### Tasks

- [ ] **45 min:** watch Karpathy's *Intro to Large Language Models* (first 45 minutes)
- [ ] Tokenise 5 of your own code or doc snippets in the Tokenizer Playground […]
- [ ] Write "what a context window is" in 5 lines
- [ ] Create repo `ai-eng-26wk` with `/notes/week01.md` and record 3 surprising tokenisation results

### Resources

1. Karpathy, [Intro to Large Language Models](https://www.youtube.com/results?search_query=karpathy+intro+to+large+language+models) (YouTube, about 1 hour)
2. A Hugging Face Space for the tokenizer playground

### Self-check

**Why can the same text cost a different number of tokens on two models?**
Each model uses its own tokenizer, and each tokenizer splits text into different subword pieces. The same text therefore produces a different token count. Providers bill per token, so the cost differs too.

### My notes

**What a context window is (5 lines):**
1.
2.
3.
4.
5.

**3 surprising tokenisation results:**
1. Code:
2. Numbers:
3. Non-English:

---

## Week 1 checklist

- [ ] Repo `ai-eng-26wk` created
- [ ] AWS billing alarm and budget set
- [ ] MFA on, SSO profile named, no keys committed
- [ ] `src/bedrock_chat.py` prints tokens, latency and cost
- [ ] `--temperature` and `--stream` flags added, variance table saved
- [ ] `llm-cli chat --provider bedrock|direct` works with streaming
- [ ] `llm-cli` v0.1 tagged and pushed
- [ ] `notes/exam-map.md` created

## Sunday review

- Did I ship the deliverable?
- What confused me most? (one paragraph)
- One measured result added to the README
- Next week's two longest blocks planned in the calendar