Day 17 · Wed 11 Nov 2026 · Prompt caching and token economics
Time: 75 min. 20m read Bedrock prompt caching + Claude prompt caching docs · 40m put a long
static instruction block first, enable caching on a supported model, measure cached vs uncached
latency and cost over 20 calls · 15m compute cost per 1k requests.
Free resources: Amazon Bedrock: Prompt caching; Claude docs: Prompt caching; Amazon Bedrock
pricing
Task: A small table: tokens, cache read/write tokens, latency p50, cost per 1k requests.
Check yourself: What prompt layout maximises cache hits?
Day 18 · Thu 12 Nov 2026 · Prompt versioning and Bedrock Prompt Management
Time: 75 min. 20m read Bedrock Prompt Management · 40m store prompts as files
prompts/extract/v1.yaml , v2.yaml with metadata (model, temperature, owner); create the same
prompt in Prompt Management and invoke a version · 15m note pros/cons of each.
Free resources: Amazon Bedrock: Prompt management
Task: Loader that selects prompt by name+version from config; one Prompt Management version
invoked from code.
Check yourself: How do you roll back a bad prompt version in under a minute