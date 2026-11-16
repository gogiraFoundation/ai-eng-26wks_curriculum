# Prompt and context layering

Rules for what goes in each layer when calling models (invoice extract and later agents). Keep the context window small and high-signal.

1. **System:** stable behaviour only — role, output contract (JSON schema / forbidden extras), safety limits, and default style. Versioned files under `invoice/`. Do not put per-request documents here.
2. **User:** the task instance — raw invoice text, request id, and any one-off instructions for this call.
3. **Few-shot examples:** curated input → output pairs that teach format. Prefer a small fixed set; hold them out of eval scoring. Treat as prompt content, not live retrieval.
4. **Retrieved context:** vendor-specific quirks, policy snippets, currency tables, prior invoice chunks — loaded **just in time** for this document, not pasted into the system prompt for every call.
5. **Tool results:** short, structured returns (ids, totals, normalised currency). Prefer re-fetchable summaries over dumping large blobs into history.
6. **Conversation / agent history:** keep only what the next turn needs; compact or drop stale tool payloads rather than growing the window unbounded.
7. **Secrets and PII:** never in prompts or logs that ship to the model beyond what the task requires; keep keys in env / IAM, not in `system.txt`.
8. **Altitude:** system rules specific enough to enforce JSON shape, flexible enough not to hard-code brittle per-vendor logic (that belongs in retrieved context or code).

## Check yourself

**What belongs in the system prompt versus retrieved context?**

System = durable instructions and schema. Retrieved = document- or vendor-specific facts that change per request. If you would edit it for every invoice, it is not system context.