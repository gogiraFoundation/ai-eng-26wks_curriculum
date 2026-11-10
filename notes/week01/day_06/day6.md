# Day 6 lab log: Build Day: CLI chatbot with two backends (Real-time Streaming Token & Cost Logic)

Tasks:
        Working llm-cli chat --provider
        bedrock|direct with streaming anf a running token/cost total


**Script:** `src/day_06_build/stream_cli`  
**Model:** `qwen2.5:7b`  | `bredrock:micro_nova`
**Prompt:** Write a single sentence describing a mysterious old key found in an attic, using highly poetic imagery.  
**Held constant:** `top_p=0.9`, `max_tokens=200`, `keep_alive=10m`  
**Theory:** see [day6_notes.md](./day6_notes.md)

## Task status

                Working llm-cli chat --provider
                bedrock|direct with streaming anf a running token/cost total


## Results summary


## Observation

## Commands used

```bash
python src/local/llm_client.py --temperature 0
python src/local/llm_client.py --temperature 0.5
python src/local/llm_client.py --temperature 1.0
python src/local/llm_client.py --temperature 1.0 --stream
python src/local/llm_client.py --temperature 1.5
python src/local/llm_client.py --temperature 2.0
python src/local/llm_client.py --temperature 2.5
python src/local/llm_client.py --temperature 3.0