# Day 17 prompt caching (Nova Micro)

| Metric | Uncached | Cached |
| :--- | ---: | ---: |
| Fresh input tokens (sum) | 33,789 | 1,031 |
| Cache write tokens (sum) | 0 | 1,638 |
| Cache read tokens (sum) | 0 | 31,120 |
| Output tokens (sum) | 2,544 | 2,551 |
| Latency p50 (ms) | 558 | 587 |
| Cost / 1k requests (USD) | $0.0835 | $0.0392 |
