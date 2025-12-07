#!/usr/bin/env python3
"""
Test script to discover available models through ZAI API
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GLM_API_KEY")

# ZAI endpoints to try
ENDPOINTS_TO_TRY = [
    "https://api.z.ai/api/paas/v4/",
    "https://api.z.ai/v1/",
    "https://api.z.ai/api/v1/",
]

def test_models_list(endpoint_url):
    """Try to get list of available models"""

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    print(f"\nTesting models endpoint: {endpoint_url}models")

    try:
        response = requests.get(f"{endpoint_url}models", headers=headers, timeout=15)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            models = response.json()
            print(f"✅ Available models: {json.dumps(models, indent=2)}")
            return models
        else:
            print(f"❌ Failed: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_chat_completion(endpoint_url, model):
    """Test chat completion with specific model"""

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': f"Hello! You are {model}. Please confirm your identity."
            }
        ],
        'max_tokens': 100,
        'temperature': 0.3
    }

    print(f"\nTesting {model} via {endpoint_url}")

    try:
        response = requests.post(
            f"{endpoint_url}chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ SUCCESS: {content}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Test ZAI API endpoints and models"""

    print("ZAI MODEL DISCOVERY TEST")
    print("=" * 50)
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-10:] if API_KEY else 'NOT_FOUND'}")

    # Models to test based on your subscription
    MODELS_FROM_SUBSCRIPTION = [
        "glm-4.6",
        "glm-4.5-air",
        "glm-4.5",
        "glm-4.5-flash"
    ]

    # Test each endpoint for models list
    for endpoint in ENDPOINTS_TO_TRY:
        models = test_models_list(endpoint)
        if models:
            print(f"\n✅ Found models via {endpoint}")
            break

    # Test chat completions with models from your subscription
    print(f"\n{'='*50}")
    print("TESTING CHAT COMPLETIONS")
    print(f"{'='*50}")

    results = {}

    for endpoint in ENDPOINTS_TO_TRY:
        for model in MODELS_FROM_SUBSCRIPTION:
            key = f"{endpoint}-{model}"
            results[key] = test_chat_completion(endpoint, model)

    print(f"\n{'='*50}")
    print("RESULTS SUMMARY")
    print(f"{'='*50}")

    working = []
    for combo, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{combo}: {status}")
        if success:
            working.append(combo)

    if working:
        print(f"\n🎉 Working combinations: {', '.join(working)}")
    else:
        print(f"\n💥 No working combinations found")

if __name__ == "__main__":
    main()