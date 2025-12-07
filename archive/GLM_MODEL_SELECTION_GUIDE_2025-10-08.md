# Z.ai GLM Model Selection Guide

## Overview

Z.ai provides three GLM models optimized for different tasks. This guide helps you choose the right model for each scenario.

## Model Specifications

### GLM-4.5-Flash (FREE - Fastest)
- **Context:** 128K tokens
- **Max Output:** Up to 4K tokens
- **Strengths:**
  - **Completely FREE** with usage limits
  - Very fast response times
  - Good for general queries and simple coding
  - No credit card required
- **Best For:**
  - Development and testing
  - Simple code questions
  - Quick answers and explanations
  - Learning and experimentation
  - High-volume low-complexity tasks
- **Pricing:** FREE (usage limits apply)
- **Model ID:** `glm-4.5-flash`

### GLM-4.6 (Newest - Best for Coding)
- **Context:** 200K tokens
- **Max Output:** 128K tokens
- **Strengths:**
  - Superior coding performance (Python, JavaScript, Java, etc.)
  - Longest context window for complex agentic tasks
  - Advanced reasoning and tool use
  - Enhanced agent and search capabilities
  - Improved writing and role-playing
- **Best For:**
  - AI Coding assistance
  - Complex multi-file refactoring
  - Code generation and debugging
  - Smart office automation
  - Intelligent search tasks
- **Pricing:** Part of GLM Coding Plan ($3/month minimum)
- **Model ID:** `glm-4.6`

### GLM-4.5 (Flagship - Most Powerful)
- **Parameters:** 355B total / 32B active per forward pass
- **Context:** 128K tokens
- **Max Output:** 96K tokens
- **Architecture:** Mixture-of-Experts (MoE)
- **Strengths:**
  - Most powerful reasoning model
  - High parameter efficiency
  - Strong benchmark performance
  - Hybrid reasoning modes (thinking/non-thinking)
  - Native tool invocation
- **Best For:**
  - Complex web development
  - AI assistants requiring deep reasoning
  - Complex text translation
  - Multi-turn complex conversations
  - Content creation requiring nuance
  - Agent-oriented applications
- **Pricing:** Requires paid subscription
- **Model ID:** `glm-4.5`
- **Note:** REQUIRES CREDITS (not available on free tier)

### GLM-4.5-Air (Lightweight - Cost-Effective)
- **Parameters:** 106B total / 12B active
- **Context:** 128K tokens
- **Architecture:** Mixture-of-Experts (MoE)
- **Strengths:**
  - Cost-effective paid option
  - Competitive reasoning performance
  - Fast responses
  - Still maintains 128K context
  - Streaming output support
- **Best For:**
  - Fast responses for simple queries
  - File search and syntax checking
  - Simple code reviews
  - Front-end development tasks
  - High-volume API calls
  - Production workloads
- **Pricing:**
  - $0.2 per million input tokens
  - $1.1 per million output tokens
- **Model ID:** `glm-4.5-air`
- **Note:** REQUIRES CREDITS (not available on free tier)

## Recommended Usage Strategy

### Primary Model Selection

```
IF task requires:
  - Development/Learning → GLM-4.5-Flash (FREE)
  - Production Coding → GLM-4.6 (Paid)
  - Complex reasoning → GLM-4.5 (Paid)
  - High-volume simple tasks → GLM-4.5-Air (Paid)
```

### Multi-Agent Workflow

**Free Tier Setup (Recommended for Development):**
1. **GLM-4.5-Flash** - All development and testing tasks (FREE)
2. Upgrade to paid models only when you hit limitations

**Paid Subscription Setup:**
1. **GLM-4.6** - Main coding agent (ANTHROPIC_MODEL)
2. **GLM-4.5-Air** - Fast auxiliary tasks (ANTHROPIC_SMALL_FAST_MODEL)
3. **GLM-4.5** - Complex reasoning when needed

### Task-Specific Examples

| Task | Recommended Model | Reason |
|------|------------------|---------|
| Debugging Python code | GLM-4.6 | Superior coding performance |
| Writing complex documentation | GLM-4.5 | Best reasoning for nuance |
| File search/grep operations | GLM-4.5-Air | Fast, cost-effective |
| Multi-step refactoring | GLM-4.6 | Long context + coding focus |
| Code review comments | GLM-4.5-Air | Quick syntax checks |
| Architecture planning | GLM-4.5 | Deep reasoning required |
| Simple file edits | GLM-4.5-Air | Overkill to use expensive models |

## Cost Optimization

### Development vs Production

**Development:**
- Use GLM-4.5-Air for most tasks
- Only use GLM-4.6/4.5 when you hit complexity limits
- Saves ~80% on API costs during iteration

**Production:**
- Use appropriate model for task complexity
- GLM-4.6 for user-facing coding features
- GLM-4.5-Air for background tasks

### Estimated Costs

**Example: 1 hour coding session**
- All GLM-4.6: ~$0.50-2.00
- Mixed (4.6 + 4.5-Air): ~$0.20-0.80
- All GLM-4.5-Air: ~$0.10-0.30

Compare to Claude Sonnet 4: $3-15 for same session

## Integration Setup

### Environment Variables

```bash
# Option 1: Use Z.ai as drop-in replacement for Claude
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your_zai_key"
export ANTHROPIC_MODEL="glm-4.6"
export ANTHROPIC_SMALL_FAST_MODEL="glm-4.5-air"

# Option 2: Keep both available via switching script
source ./scripts/switch-ai-model.sh glm    # Use GLM
source ./scripts/switch-ai-model.sh claude # Use Claude
```

### Python SDK

```python
from zai import ZaiClient

client = ZaiClient(api_key="your_key")

# GLM-4.6 for coding
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[{"role": "user", "content": "Debug this code..."}],
    max_tokens=4096
)

# GLM-4.5-Air for quick tasks
response = client.chat.completions.create(
    model="glm-4.5-air",
    messages=[{"role": "user", "content": "Check syntax..."}],
    max_tokens=1024
)
```

### MCP Server (Advanced)

The `@z_ai/mcp-server` package provides native integration with Claude Code's MCP ecosystem.

## Current Status

**Installed:**
- ✅ Python SDK (zai-sdk) in backend/venv
- ✅ MCP Server (@z_ai/mcp-server) globally
- ✅ API key configured and working
- ✅ GLM-4.5-Flash (FREE) tested and working

**Working Models:**
- ✅ **GLM-4.5-Flash** - FREE tier, fully functional
- ⚠️ **GLM-4.6, GLM-4.5, GLM-4.5-Air** - Require paid subscription

**To Access Paid Models:**
1. Visit https://z.ai or https://open.bigmodel.cn
2. Login with your account
3. Purchase GLM Coding Plan (starts at $3/month)
4. Or add pay-as-you-go credits
5. Regenerate API key after subscribing

## Quick Reference

```bash
# Test GLM-4.5-Flash (FREE)
cd /home/cdc/Storage/NVMe/projects/lumen/backend
source venv/bin/activate
python3 ../scripts/tests/temp/test_GLM.py

# Or use Python SDK directly
python3 << EOF
from zai import ZaiClient
client = ZaiClient(api_key="90d7df3e421f48b99f78e9914f1b682b.cA7RAm4KIIBowBHN")
response = client.chat.completions.create(
    model="glm-4.5-flash",  # FREE model
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
EOF

# Switch to GLM (after adding credits for paid models)
source ./scripts/switch-ai-model.sh glm

# Switch back to Claude
source ./scripts/switch-ai-model.sh claude
```

## Further Reading

- Official Docs: https://docs.z.ai/guides/llm/glm-4.6
- API Reference: https://docs.z.ai/api-reference/introduction
- Claude Integration: https://docs.z.ai/scenario-example/develop-tools/claude
- GitHub: https://github.com/zai-org/GLM-4.5
