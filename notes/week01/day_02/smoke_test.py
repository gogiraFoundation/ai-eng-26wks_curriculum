import boto3

session = boto3.Session(profile_name="agent-toolkit", region_name="eu-north-1")
client = session.client("bedrock-runtime")

response = client.converse(
    modelId="eu.amazon.nova-micro-v1:0",
    messages=[
        {
            "role": "user",
            "content": [{"text": "Reply with one sentence."}],
        }
    ],
    inferenceConfig={"maxTokens": 64, "temperature": 0},
)

print(response["output"]["message"]["content"][0]["text"])
print(response["usage"])
print(response["metrics"]["latencyMs"])