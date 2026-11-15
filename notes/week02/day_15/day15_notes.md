
Day 13 · Sat 7 Nov 2026 · Build day: extraction service with tests
Time: 3 h. 30m build 15 synthetic invoices (vary formats, currencies, missing fields) · 90m finish
endpoint, tool loop for currency normalisation, pytest suite with recorded responses (no live calls in
CI) · 40m measure field-level accuracy on the 15 cases · 20m README.
Free resources: pytest docs; FastAPI docs; Amazon Bedrock: Tool use
Task: Accuracy table per field in README (e.g. total 15/15, date 13/15).
Check yourself: Why record responses for tests instead of calling the model in CI?
