#!/usr/bin/env python3
"""
Codex CLI wrapper for Lumen project.
Supports OpenAI API and Cursor IDE CLI.

Latest Models (as of 2025-11-16):
- gpt-4o-2024-11-20: Latest GPT-4 Omni (recommended)
- gpt-4o-mini-2024-07-18: Latest GPT-4 Mini
- gpt-4-turbo-2024-04-09: GPT-4 Turbo
- gpt-4-0125-preview: GPT-4 Preview
- gpt-3.5-turbo-0125: GPT-3.5 Turbo
- o1-preview: OpenAI o1 Preview (reasoning model)
- o1-mini: OpenAI o1 Mini (reasoning model)
"""

import sys
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def call_codex(prompt, model='gpt-4o-2024-11-20', timeout=300):
    """Call Codex CLI with prompt."""

    codex_api_key = os.getenv('CODEX_API_KEY')

    if not codex_api_key:
        print("ERROR: CODEX_API_KEY not found in environment variables.", file=sys.stderr)
        print("Please add your Codex API key to .env file.", file=sys.stderr)
        return ""

    # OpenAI Chat Completions API implementation (updated for latest models)
    import requests
    try:
        # Use chat completions endpoint for newer models
        if model.startswith(('gpt-4o', 'gpt-4-turbo', 'o1-')):
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {codex_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 4000,
                    'temperature': 0.1
                },
                timeout=timeout
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}", file=sys.stderr)
                return ""
        else:
            # Legacy completions endpoint for older models
            response = requests.post(
                'https://api.openai.com/v1/completions',
                headers={
                    'Authorization': f'Bearer {codex_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': model,
                    'prompt': prompt,
                    'max_tokens': 4000,
                    'temperature': 0.1
                },
                timeout=timeout
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['text']
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}", file=sys.stderr)
                return ""
    except Exception as e:
        print(f"OpenAI API exception: {e}", file=sys.stderr)

    # PLACEHOLDER for Cursor IDE CLI approach
    # Example if you have Cursor CLI:
    # import subprocess
    # try:
    #     result = subprocess.run(
    #         ['cursor', 'ask', '--prompt', prompt],
    #         capture_output=True,
    #         text=True,
    #         timeout=timeout
    #     )
    #     if result.returncode == 0:
    #         return result.stdout
    #     else:
    #         print(f"Cursor CLI error: {result.stderr}", file=sys.stderr)
    #         return ""
    # except FileNotFoundError:
    #     print("Cursor CLI binary not found.", file=sys.stderr)
    #     return ""
    # except subprocess.TimeoutExpired:
    #     print("Cursor CLI timeout", file=sys.stderr)
    #     return ""

    print(f"Codex CLI wrapper called with prompt:\n{prompt[:200]}...", file=sys.stderr)
    print("No working Codex implementation found. Please check your API keys.", file=sys.stderr)
    return ""

def main():
    parser = argparse.ArgumentParser(description='OpenAI/Codex CLI wrapper')
    parser.add_argument('--prompt', required=True, help='Prompt to send to OpenAI')
    parser.add_argument('--model', default='gpt-4o-2024-11-20',
                       choices=[
                           'gpt-4o-2024-11-20',
                           'gpt-4o-mini-2024-07-18',
                           'gpt-4-turbo-2024-04-09',
                           'gpt-4-0125-preview',
                           'gpt-3.5-turbo-0125',
                           'o1-preview',
                           'o1-mini',
                           'text-davinci-003',
                           'code-davinci-002'
                       ],
                       help='Model to use (default: gpt-4o-2024-11-20)')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds')
    args = parser.parse_args()

    output = call_codex(args.prompt, args.model, args.timeout)
    print(output)

if __name__ == '__main__':
    main()
