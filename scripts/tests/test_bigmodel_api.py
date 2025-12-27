#!/usr/bin/env python3
"""
Test script to compare BigModel.cn vs ZAI API endpoints
Updated for glm-4.7 testing (2025-12-26)
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GLM_API_KEY") or os.getenv("ZAI_GLM_API_KEY") or os.getenv("ZAI_API_KEY")

# Different endpoints to test
ENDPOINTS = {
    "BigModel.cn": "https://open.bigmodel.cn/api/paas/v4/",
    "ZAI": "https://api.z.ai/api/paas/v4/"
}

MODELS = ["glm-4.5", "glm-4.6", "glm-4.7"]

def test_endpoint(endpoint_name, base_url, model):
    """Test a specific endpoint and model combination"""

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': f"Hello! You are {model} responding via {endpoint_name}. Please confirm."
            }
        ],
        'max_tokens': 100,
        'temperature': 0.3
    }

    print(f"\nTesting {endpoint_name} + {model}")
    print(f"URL: {base_url}chat/completions")

    try:
        response = requests.post(
            f"{base_url}chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ SUCCESS: {content[:100]}...")
            return True
        else:
            print(f"❌ FAILED: {response.text}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Test all endpoint/model combinations"""

    print("API ENDPOINT COMPARISON TEST")
    print("=" * 50)
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-10:] if API_KEY else 'NOT_FOUND'}")

    results = {}

    for endpoint_name, base_url in ENDPOINTS.items():
        for model in MODELS:
            key = f"{endpoint_name}-{model}"
            results[key] = test_endpoint(endpoint_name, base_url, model)

    print(f"\n{'='*50}")
    print("RESULTS SUMMARY")
    print(f"{'='*50}")

    for combo, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{combo}: {status}")

    working = [k for k, v in results.items() if v]
    if working:
        print(f"\n🎉 Working combinations: {', '.join(working)}")
    else:
        print(f"\n💥 No working combinations found")

if __name__ == "__main__":
    main()