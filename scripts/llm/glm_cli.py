#!/usr/bin/env python3
"""
GLM CLI wrapper for Lumen project.
Supports Z.Ai GLM dev plan (glm-4.7) and standard GLM API.
Documentation: https://docs.z.ai/guides/llm/glm-4.7
"""

import sys
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def call_glm(prompt, model='glm-4.7', timeout=300):
    """
    Call GLM CLI with prompt.

    Supports Z.Ai GLM 4.7 dev plan and standard GLM API.
    Default model: glm-4.7 (latest, enhanced programming capabilities)
    """

    # Try Z.Ai GLM dev plan key first
    zai_glm_api_key = os.getenv('ZAI_GLM_API_KEY') or os.getenv('ZAI_API_KEY')
    glm_api_key = os.getenv('GLM_API_KEY')

    if not zai_glm_api_key and not glm_api_key:
        print("ERROR: Neither ZAI_GLM_API_KEY nor GLM_API_KEY found in environment variables.", file=sys.stderr)
        print("Please add your GLM API key to .env file.", file=sys.stderr)
        return ""

    # Z.Ai GLM 4.6 implementation (preferred)
    if zai_glm_api_key:
        try:
            from zai import ZaiClient
            client = ZaiClient(api_key=zai_glm_api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            return response.choices[0].message.content
        except ImportError:
            print("Z.Ai library not found. Install with: pip install zai", file=sys.stderr)
        except Exception as e:
            print(f"Z.Ai GLM API error: {e}", file=sys.stderr)

    # Fallback to standard GLM API
    if glm_api_key:
        import requests
        base_url = os.getenv('GLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4/')
        try:
            response = requests.post(
                f"{base_url}chat/completions",
                headers={
                    'Authorization': f'Bearer {glm_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': model,
                    'messages': [{"role": "user", "content": prompt}],
                    'max_tokens': 4000
                },
                timeout=timeout
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"GLM API error: {response.status_code} - {response.text}", file=sys.stderr)
                return ""
        except Exception as e:
            print(f"GLM API exception: {e}", file=sys.stderr)
            return ""

    # PLACEHOLDER for CLI binary approach
    # Example if you have a glm CLI binary:
    # import subprocess
    # try:
    #     result = subprocess.run(
    #         ['glm', 'chat', '--model', model, '--prompt', prompt],
    #         capture_output=True,
    #         text=True,
    #         timeout=timeout
    #     )
    #     if result.returncode == 0:
    #         return result.stdout
    #     else:
    #         print(f"GLM CLI error: {result.stderr}", file=sys.stderr)
    #         return ""
    # except FileNotFoundError:
    #     print("GLM CLI binary not found.", file=sys.stderr)
    #     return ""
    # except subprocess.TimeoutExpired:
    #     print("GLM CLI timeout", file=sys.stderr)
    #     return ""

    print(f"GLM CLI wrapper called with prompt:\n{prompt[:200]}...", file=sys.stderr)
    print("No working GLM implementation found. Please check your API keys.", file=sys.stderr)
    return ""

def main():
    parser = argparse.ArgumentParser(description='GLM CLI wrapper')
    parser.add_argument('--prompt', required=True, help='Prompt to send to GLM')
    parser.add_argument('--model', default='glm-4', help='Model to use')
    args = parser.parse_args()

    output = call_glm(args.prompt, args.model)
    print(output)

if __name__ == '__main__':
    main()
