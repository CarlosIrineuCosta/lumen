#!/usr/bin/env python3
"""
API Key Setup Script for Lumen Project CLI Tools
Sets up and validates API keys for Claude, GLM, and Codex CLI tools.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def setup_api_keys():
    """Interactive setup for API keys"""

    print("🔑 Lumen Project API Key Setup")
    print("=" * 40)
    print()

    # Load existing .env if it exists
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv()
        print("✅ Found existing .env file")
    else:
        print("⚠️  No .env file found, will create one")

    print()
    print("Please enter your API keys (press Enter to skip):")
    print("-" * 40)

    # Collect API keys
    api_keys = {}

    # Claude CLI Monthly Version
    existing_claude = os.getenv('CLAUDE_API_KEY', '')
    claude_key = input(f"Claude CLI Monthly API Key [{'existing_claude[:10]}...' if existing_claude else 'NOT SET'}]: ").strip()
    if claude_key:
        api_keys['CLAUDE_API_KEY'] = claude_key

    # Z.Ai GLM 4.6 Dev Plan
    existing_zai = os.getenv('ZAI_GLM_API_KEY', '')
    zai_key = input(f"Z.Ai GLM 4.6 Dev Plan Key [{'existing_zai[:10]}...' if existing_zai else 'NOT SET'}]: ").strip()
    if zai_key:
        api_keys['ZAI_GLM_API_KEY'] = zai_key

    # Standard GLM API Key (fallback)
    existing_glm = os.getenv('GLM_API_KEY', '')
    glm_key = input(f"Standard GLM API Key [{'existing_glm[:10]}...' if existing_glm else 'NOT SET'}]: ").strip()
    if glm_key:
        api_keys['GLM_API_KEY'] = glm_key

    # Codex API Key
    existing_codex = os.getenv('CODEX_API_KEY', '')
    codex_key = input(f"Codex API Key [{'existing_codex[:10]}...' if existing_codex else 'NOT SET'}]: ").strip()
    if codex_key:
        api_keys['CODEX_API_KEY'] = codex_key

    # Optional: Additional providers
    print()
    print("Optional additional providers (press Enter to skip):")
    print("-" * 40)

    existing_sambanova = os.getenv('SAMBANOVA_API_KEY', '')
    sambanova_key = input(f"SambaNova API Key [{'existing_sambanova[:10]}...' if existing_sambanova else 'NOT SET'}]: ").strip()
    if sambanova_key:
        api_keys['SAMBANOVA_API_KEY'] = sambanova_key

    existing_openrouter = os.getenv('OPENROUTER_API_KEY', '')
    openrouter_key = input(f"OpenRouter API Key [{'existing_openrouter[:10]}...' if existing_openrouter else 'NOT SET'}]: ").strip()
    if openrouter_key:
        api_keys['OPENROUTER_API_KEY'] = openrouter_key

    # Update .env file
    if api_keys:
        update_env_file(api_keys)
        print(f"\n✅ Updated {env_file} with {len(api_keys)} API keys")
    else:
        print("\n⚠️  No new API keys provided")

    return api_keys

def update_env_file(new_keys):
    """Update .env file with new API keys"""

    env_file = Path(".env")
    env_content = ""

    # Read existing content
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()

    # Update or add new keys
    lines = env_content.split('\n')
    updated_lines = []

    for key, value in new_keys.items():
        # Find existing line or add new one
        key_found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                key_found = True
                break

        if not key_found:
            lines.append(f"{key}={value}")

    # Write back to file
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))

def test_api_keys():
    """Test API key configurations"""

    print("\n🧪 Testing API Key Configurations")
    print("=" * 40)

    load_dotenv()

    # Test Claude CLI
    claude_key = os.getenv('CLAUDE_API_KEY')
    if claude_key:
        print(f"✅ Claude CLI: Key found ({claude_key[:10]}...)")
        try:
            import subprocess
            result = subprocess.run(['python', 'scripts/llm/claude_cli.py', '--prompt', 'test'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Claude CLI: Wrapper executable")
            else:
                print("⚠️  Claude CLI: Wrapper test failed")
        except Exception as e:
            print(f"⚠️  Claude CLI: Test error - {e}")
    else:
        print("❌ Claude CLI: No API key")

    # Test GLM
    glm_key = os.getenv('ZAI_GLM_API_KEY') or os.getenv('GLM_API_KEY')
    if glm_key:
        print(f"✅ GLM: Key found ({glm_key[:10]}...)")
        try:
            import subprocess
            result = subprocess.run(['python', 'scripts/llm/glm_cli.py', '--prompt', 'test'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ GLM: Wrapper executable")
            else:
                print("⚠️  GLM: Wrapper test failed")
        except Exception as e:
            print(f"⚠️  GLM: Test error - {e}")
    else:
        print("❌ GLM: No API key")

    # Test Codex
    codex_key = os.getenv('CODEX_API_KEY')
    if codex_key:
        print(f"✅ Codex: Key found ({codex_key[:10]}...)")
        try:
            import subprocess
            result = subprocess.run(['python', 'scripts/llm/codex_cli.py', '--prompt', 'test'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Codex: Wrapper executable")
            else:
                print("⚠️  Codex: Wrapper test failed")
        except Exception as e:
            print(f"⚠️  Codex: Test error - {e}")
    else:
        print("❌ Codex: No API key")

def show_instructions():
    """Show detailed setup instructions"""

    print("\n📋 API Key Setup Instructions")
    print("=" * 40)

    print("""
1. CLAUDE CLI MONTHLY VERSION:
   - Get your key from: https://console.anthropic.com/
   - This is for Claude CLI monthly subscription
   - Install Claude CLI: https://docs.anthropic.com/claude/docs/claude-cli

2. Z.AI GLM 4.6 DEV PLAN:
   - Get your key from: https://z.ai/
   - This is the dev plan key (not per-access)
   - Install Z.AI library: pip install zai

3. STANDARD GLM API:
   - Get your key from: https://open.bigmodel.cn/
   - Fallback option if Z.AI not available

4. CODEX API:
   - Get your key from: https://platform.openai.com/
   - For OpenAI Codex API access

5. OPTIONAL PROVIDERS:
   - SambaNova: https://cloud.sambanova.ai/
   - OpenRouter: https://openrouter.ai/

USAGE:
- Claude: python scripts/llm/claude_cli.py --prompt "your prompt"
- GLM: python scripts/llm/glm_cli.py --prompt "your prompt"
- Codex: python scripts/llm/codex_cli.py --prompt "your prompt"
""")

def main():
    """Main setup function"""

    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            test_api_keys()
        elif sys.argv[1] == '--help':
            show_instructions()
        else:
            print("Usage: python setup_api_keys.py [--test|--help]")
            sys.exit(1)
    else:
        show_instructions()
        api_keys = setup_api_keys()
        if api_keys:
            test_api_keys()

        print(f"\n🎉 Setup complete!")
        print(f"Run 'python {__file__} --test' to test your configuration")

if __name__ == '__main__':
    main()
