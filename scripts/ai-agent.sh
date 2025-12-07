#!/bin/bash
# Multi-Provider AI Agent Interface for Lumen Project
# Supports: SambaNova (cloud), OpenRouter (cloud)

set -e

# Configuration
SAMBANOVA_URL="https://api.sambanova.ai/v1"
OPENROUTER_URL="https://openrouter.ai/api/v1"

# Default models
SAMBANOVA_MODEL="Meta-Llama-3.1-8B-Instruct"
OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"

# Usage function
usage() {
    cat << EOF
Usage: $0 <provider> "<prompt>" [model] [files...]

Providers:
  sambanova  - SambaNova Cloud (fast, performance analysis)
  openrouter - OpenRouter (powerful, architecture review)
  auto       - Auto-select based on availability

Examples:
  $0 sambanova "Analyze DB performance"
  $0 openrouter "Architecture review" anthropic/claude-3.5-sonnet
  $0 auto "Quick code review"

EOF
    exit 1
}
# Check arguments
if [ $# -lt 2 ]; then
    usage
fi

PROVIDER=$1
PROMPT=$2
MODEL=${3:-""}
shift 3 || shift $#

# Function to check if service is available
check_service() {
    local url=$1
    curl -s -f -o /dev/null "$url/models" 2>/dev/null
}

# Function to read files
read_files() {
    local content=""
    for file in "$@"; do
        if [ -f "$file" ]; then
            content+="\\n\\nFile: $file\\n"
            content+=$(cat "$file" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | tr '\n' ' ')
        fi
    done
    echo "$content"
}

# SambaNova function
call_sambanova() {
    local prompt=$1
    local model=${2:-$SAMBANOVA_MODEL}
    local files_content=$(read_files "${@:3}")
    
    if [ -z "$SAMBANOVA_API_KEY" ]; then
        echo "ERROR: SAMBANOVA_API_KEY not set" >&2
        return 1
    fi
    
    local data=$(cat <<EOF
{
  "model": "$model",
  "messages": [
    {"role": "system", "content": "You are a performance analyst for the Lumen platform. Focus on optimization opportunities."},
    {"role": "user", "content": "$prompt$files_content"}
  ],
  "temperature": 0.3
}
EOF
)
    
    curl -s -X POST "$SAMBANOVA_URL/chat/completions" \
        -H "Authorization: Bearer $SAMBANOVA_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$data" | jq -r '.choices[0].message.content'
}

# OpenRouter function
call_openrouter() {
    local prompt=$1
    local model=${2:-$OPENROUTER_MODEL}
    local files_content=$(read_files "${@:3}")
    
    if [ -z "$OPENROUTER_API_KEY" ]; then
        echo "ERROR: OPENROUTER_API_KEY not set" >&2
        return 1
    fi
    
    local data=$(cat <<EOF
{
  "model": "$model",
  "messages": [
    {"role": "system", "content": "You are a senior architect reviewing the Lumen platform. Provide strategic insights."},
    {"role": "user", "content": "$prompt$files_content"}
  ]
}
EOF
)
    
    curl -s -X POST "$OPENROUTER_URL/chat/completions" \
        -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$data" | jq -r '.choices[0].message.content'
}

# Auto-select provider
auto_select() {
    local prompt=$1
    shift

    # Priority: SambaNova > OpenRouter
    if [ -n "$SAMBANOVA_API_KEY" ] && check_service "$SAMBANOVA_URL"; then
        echo "Using SambaNova (cloud)..." >&2
        call_sambanova "$prompt" "" "$@"
    elif [ -n "$OPENROUTER_API_KEY" ]; then
        echo "Using OpenRouter (cloud)..." >&2
        call_openrouter "$prompt" "" "$@"
    else
        echo "ERROR: No AI providers available" >&2
        echo "Please set SAMBANOVA_API_KEY or OPENROUTER_API_KEY" >&2
        return 1
    fi
}

# Main execution
case "$PROVIDER" in
    sambanova)
        call_sambanova "$PROMPT" "$MODEL" "$@"
        ;;
    openrouter)
        call_openrouter "$PROMPT" "$MODEL" "$@"
        ;;
    auto)
        auto_select "$PROMPT" "$@"
        ;;
    *)
        echo "ERROR: Unknown provider: $PROVIDER" >&2
        usage
        ;;
esac
