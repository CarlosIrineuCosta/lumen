#!/usr/bin/env python3
"""
Test script to understand ZAI API calls with GLM-4.5 and GLM-4.6
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from your .env file
API_KEY = os.getenv("GLM_API_KEY")
BASE_URL = "https://api.z.ai/api/paas/v4/"  # ZAI API endpoint
MODELS_TO_TEST = ["glm-4.5", "glm-4.6"]  # Models we want to test

def test_model(model_name, prompt="Hello! Please respond briefly and tell me what model you are."):
    """Test a specific GLM model via ZAI API"""

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': model_name,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': 150,
        'temperature': 0.3
    }

    print(f"\n{'='*60}")
    print(f"Testing Model: {model_name}")
    print(f"API Endpoint: {BASE_URL}chat/completions")
    print(f"{'='*60}")

    try:
        print(f"Making request to {BASE_URL}chat/completions...")
        print(f"Headers: {headers}")
        print(f"Data: {json.dumps(data, indent=2)}")

        response = requests.post(
            f"{BASE_URL}chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCESS - Model {model_name} responded!")
            print(f"Response content: {result['choices'][0]['message']['content']}")
            print(f"Usage info: {result.get('usage', 'No usage info provided')}")
            return True
        else:
            print(f"\n❌ FAILED - Status {response.status_code}")
            print(f"Error response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST FAILED: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON DECODE ERROR: {e}")
        print(f"Raw response: {response.text}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def main():
    """Main test function"""

    print("ZAI API TEST - GLM Models")
    print("=" * 60)
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-10:] if API_KEY else 'NOT_FOUND'}")
    print(f"Base URL: {BASE_URL}")

    if not API_KEY:
        print("❌ ERROR: GLM_API_KEY not found in environment variables")
        return

    # Test each model
    results = {}
    for model in MODELS_TO_TEST:
        results[model] = test_model(model)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for model, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{model}: {status}")

    working_models = [model for model, success in results.items() if success]
    if working_models:
        print(f"\n🎉 Working models: {', '.join(working_models)}")
    else:
        print(f"\n💥 No models are working. Check your API key and endpoint.")

if __name__ == "__main__":
    main()