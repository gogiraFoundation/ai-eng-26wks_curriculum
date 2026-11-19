# production grade LLM 

Provider-agnostic streaming gateway using the Adapter / Strategy pattern. Your /chat/stream endpoint emits the exact same SSE event contract (token → usage / error) regardless of whether you set LLM_PROVIDER=ollama locally or switch to LLM_PROVIDER=bedrock

### Project Structure 

src/gateway/
├── __init__.py
├── schemas.py      # Shared request & normalized SSE event models
├── providers.py    # Ollama (httpx async) & Bedrock (ConverseStream) adapters
└── main.py         # FastAPI /chat/stream endpoint



### Design 

POST /chat/stream
        │
        ▼
  resolve provider  ← env LLM_PROVIDER or body.provider
        │
   ┌────┴────┐
   ▼         ▼
 Ollama    Bedrock
 (httpx)   (ConverseStream via asyncio.to_thread)
   │         │
   └────┬────┘
        ▼
  SSE: token* → usage | error