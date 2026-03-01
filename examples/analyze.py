"""examples/analyze.py – SnapAPI v2 Python SDK (BYOK)"""
import os
from snapapi import SnapAPI, AnalyzeOptions

client = SnapAPI(api_key=os.environ.get("SNAPAPI_KEY", "sk_live_YOUR_KEY"))


def main():
    # 1. Free-form with OpenAI
    result = client.analyze(AnalyzeOptions(
        url="https://example.com",
        prompt="Summarize the main content of this page in 3 bullet points.",
        provider="openai",
        api_key=os.environ.get("OPENAI_API_KEY", "sk-YOUR_KEY"),
        include_screenshot=False,
        include_metadata=True,
        block_ads=True,
    ))
    print("Analysis:", result.result)
    print("Model:", result.model)

    # 2. Structured JSON output with Anthropic
    structured = client.analyze(AnalyzeOptions(
        url="https://stripe.com/pricing",
        prompt="Extract all pricing plans with their names, prices, and features.",
        provider="anthropic",
        api_key=os.environ.get("ANTHROPIC_API_KEY", "sk-ant-YOUR_KEY"),
        json_schema={
            "type": "object",
            "properties": {
                "plans": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "price": {"type": "string"},
                            "features": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
        },
        include_screenshot=True,
    ))
    import json
    print("Plans:", json.dumps(structured.result, indent=2, default=str))


if __name__ == "__main__":
    main()
