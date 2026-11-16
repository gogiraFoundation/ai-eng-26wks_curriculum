Day 17 · Wed 11 Nov 2026 · Prompt caching and token economics
Time: 75 min. 20m read Bedrock prompt caching + Claude prompt caching docs · 40m put a long
static instruction block first, enable caching on a supported model, measure cached vs uncached
latency and cost over 20 calls · 15m compute cost per 1k requests.
Free resources: Amazon Bedrock: Prompt caching; Claude docs: Prompt caching; Amazon Bedrock
pricing
Task: A small table: tokens, cache read/write tokens, latency p50, cost per 1k requests.
Check yourself: What prompt layout maximises cache hits?