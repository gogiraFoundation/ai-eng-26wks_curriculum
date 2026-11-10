from llm_cli.providers.bedrock import BedrockProvider
from llm_cli.providers.ollama import OllamaProvider


def get_provider(name: str, model: str | None = None):
    if name == "direct":
        return OllamaProvider(model=model) if model else OllamaProvider()
    if name == "bedrock":
        return BedrockProvider(model=model) if model else BedrockProvider()
    raise ValueError(f"Unknown provider: {name}")