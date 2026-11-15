# Day 10 lab log: tool use / function calling on Bedrock

**Topic:** Converse tool loop until `stopReason == end_turn`, max 5 iterations  
**Deliverable:** `src/tools_loop.py`  
**Model:** `eu.amazon.nova-micro-v1:0`  
**Profile / region:** `agent-toolkit` / `eu-north-1`  
**Caller:** `arn:aws:iam::767397880814:user/afrotyche@gmail.com`  
**Theory:** [day_10_notes.md](./day_10_notes.md)  
**Depends on:** Day 6 Bedrock auth (IAM user + `botocore[crt]`)  
**Free resources:** Amazon Bedrock tool use; Anthropic Claude tool-use overview (concepts transfer)

## Task status

- [x] `toolConfig` with `get_weather` stub
- [x] Loop: `converse` → `tool_use` → `toolResult` → continue
- [x] Stop on `end_turn` (max 5 iterations)
- [x] Print each tool call name + input (+ result)
- [x] Lab run recorded below
- [x] Self-check: `tool_use` vs `end_turn` (answered below)

## Loop shape

```text
messages = [user turn]
for i in 1..5:
  response = converse(modelId, messages, toolConfig, inferenceConfig)
  stop = response["stopReason"]
  append assistant message from response["output"]["message"]
  if stop == "end_turn": break
  if stop == "tool_use":
    for each toolUse block: print name/input; run stub; collect toolResult
    append user message with toolResult content blocks
  else:
    break  # unexpected stop reason
```

## Results

| Run | Prompt (abbrev.) | Iterations | Tools called | Final stopReason | Notes |
|---|---|---:|---|---|---|
| 1 | Weather in Stockholm; use the tool | 2 | `get_weather` `{"city":"Stockholm"}` | `end_turn` | Stub returned 18°C cloudy; model summarised correctly |

```text
=== iteration 1 ===
stopReason=tool_use
tool_call name=get_weather input={"city": "Stockholm"}
tool_result={"city": "Stockholm", "celsius": 18, "condition": "cloudy"}

=== iteration 2 ===
stopReason=end_turn
assistant: The current weather in Stockholm is cloudy with a temperature of 18 degrees Celsius.
```

## Self-check: `tool_use` vs `end_turn`

| `stopReason` | Meaning | What your code must do |
|---|---|---|
| `tool_use` | Model wants a function run; assistant message has `toolUse` block(s) | Execute the tool(s), append a user message with matching `toolResult` / `toolUseId`, call `converse` again |
| `end_turn` | Model is finished; usually text only | Stop the loop; print/return the final assistant text |

In this lab: iteration 1 was `tool_use`; iteration 2 was `end_turn`.

## Commands

```bash
bash infra/iam-setup/scripts/auth.sh sign-in
bash infra/iam-setup/scripts/auth.sh whoami
unset AWS_BEARER_TOKEN_BEDROCK
PYTHONPATH=src .venv/bin/python src/tools_loop.py
```

## Observation

- Fresh `aws login` fixed the earlier browser 400 (do not reuse old authorize URLs).
- Tool loop uses non-stream `converse` and must echo the same `toolUseId` on `toolResult`.
- Next (Day 11): FastAPI skeleton (`uvicorn app:app` + curl example in README).