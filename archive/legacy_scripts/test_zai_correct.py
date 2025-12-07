#!/usr/bin/env python3
"""
Test ZAI with the correct authentication method from their documentation
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GLM_API_KEY")

# ZAI correct configuration from documentation
BASE_URL = "https://api.z.ai/api/anthropic"
HEADERS = {
    "x-api-key": API_KEY,  # Different header!
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

def test_zai_correct_auth(model="glm-4.6"):
    """Test ZAI with correct authentication from documentation"""

    data = {
        "model": model,
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": f"Hello! You are {model} via ZAI developer pack. Please confirm your identity and that you're working correctly."
            }
        ]
    }

    print(f"Testing ZAI with correct authentication")
    print(f"URL: {BASE_URL}/messages")
    print(f"Model: {model}")
    print(f"Headers: {HEADERS}")
    print(f"Data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(
            f"{BASE_URL}/messages",  # Different endpoint!
            headers=HEADERS,
            json=data,
            timeout=20
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            content = result['content'][0]['text']
            usage = result.get('usage', {})

            print(f"✅ SUCCESS!")
            print(f"Response: {content}")
            print(f"Usage: {usage}")
            return True, result
        else:
            print(f"❌ FAILED")
            print(f"Error Response: {response.text}")
            return False, response.text

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, str(e)

def test_alternative_models():
    """Test different model names that might work with ZAI"""

    # Possible model name variations
    model_variations = [
        "glm-4.6",
        "glm-4.5-air",
        "glm-4.5",
        "claude-3-5-sonnet",  # ZAI might map to this
        "gpt-4",           # Fallback
    ]

    print(f"\n{'='*60}")
    print("TESTING DIFFERENT MODEL NAMES")
    print(f"{'='*60}")

    results = {}

    for model in model_variations:
        success, response = test_zai_correct_auth(model)
        results[model] = success

        if success:
            print(f"\n🎉 FOUND WORKING MODEL: {model}")
            break

    return results

def main():
    print("ZAI CORRECT AUTHENTICATION TEST")
    print("=" * 60)
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-10:] if API_KEY else 'NOT_FOUND'}")
    print(f"Using ZAI's documented authentication method")

    # Test with correct authentication
    results = test_alternative_models()

    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}")

    working_models = [model for model, success in results.items() if success]

    if working_models:
        print(f"🎉 WORKING MODELS: {', '.join(working_models)}")
        print(f"\n✅ Update Simple Agents config:")
        print(f'{{')
        print(f'  "provider": "zai",')
        print(f'  "base_url": "{BASE_URL}",')
        print(f'  "model": "{working_models[0]}",')
        print(f'  "api_key": "your-api-key"')
        print(f'}}')
    else:
        print(f"❌ NO WORKING MODELS FOUND")
        print(f"Possible issues:")
        print(f"• API key not activated for developer pack")
        print(f"• Different authentication required")
        print(f"• Regional endpoint differences")

if __name__ == "__main__":
    main()