#!/usr/bin/env python3
"""
Test ZAI Developer Pack with the exact models you paid for
Based on your billing: glm-4.6 and glm-4.5-air
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GLM_API_KEY")

# ZAI Developer Pack endpoints to try
ENDPOINTS = [
    "https://api.z.ai/api/paas/v4/",      # Standard GLM endpoint
    "https://api.z.ai/api/anthropic/",     # Anthropic-compatible endpoint
    "https://api.z.ai/api/v1/",            # Alternative v1 endpoint
]

# Models you actually paid for (from your billing)
MODELS_YOU_PAID_FOR = [
    "glm-4.6",
    "glm-4.5-air"
]

def test_exact_combination(endpoint_url, model):
    """Test exact endpoint and model combination"""

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': f"Hello! You are {model} via ZAI developer pack. Please confirm your model name and that you're working."
            }
        ],
        'max_tokens': 100,
        'temperature': 0.3
    }

    print(f"\n{'='*60}")
    print(f"Testing: {endpoint_url} + {model}")
    print(f"{'='*60}")

    try:
        response = requests.post(
            f"{endpoint_url}chat/completions",
            headers=headers,
            json=data,
            timeout=20
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            usage = result.get('usage', {})

            print(f"✅ SUCCESS!")
            print(f"Model Response: {content}")
            print(f"Usage: {usage}")

            return True, response.json()
        else:
            print(f"❌ FAILED")
            print(f"Error Response: {response.text}")
            return False, response.text

    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT")
        return False, "Request timeout"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, str(e)

def main():
    """Test the exact models and endpoints you paid for"""

    print("ZAI DEVELOPER PACK - PAID MODEL TEST")
    print("=" * 60)
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-10:]}")
    print(f"Models you paid for: {', '.join(MODELS_YOU_PAID_FOR)}")

    # Test all combinations
    results = {}

    for endpoint in ENDPOINTS:
        for model in MODELS_YOU_PAID_FOR:
            combo_key = f"{endpoint.replace('https://api.z.ai/', '')}-{model}"
            success, response = test_exact_combination(endpoint, model)
            results[combo_key] = {
                'success': success,
                'response': response
            }

    # Summary
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")

    working_combinations = []

    for combo, result in results.items():
        status = "✅ WORKING" if result['success'] else "❌ FAILED"
        print(f"{combo}: {status}")

        if result['success']:
            working_combinations.append(combo)

    if working_combinations:
        print(f"\n🎉 WORKING COMBINATIONS FOUND:")
        for combo in working_combinations:
            print(f"  • {combo}")

        print(f"\n✅ You can use these in Simple Agents!")
        print(f"Update your .simple-agents/config.json with the working endpoint and model.")
    else:
        print(f"\n💥 NO WORKING COMBINATIONS")
        print(f"This might indicate:")
        print(f"  • Different endpoint URL for developer pack")
        print(f"  • Different model names in developer pack")
        print(f"  • Separate activation required")
        print(f"  • Regional endpoint differences")

if __name__ == "__main__":
    main()