#!/bin/bash
# Quick one-liner test for hooks absolute paths fix
echo "Testing hooks from $(pwd):"
python /home/cdc/Storage/projects/lumen/.claude/hooks/core/completion_checker.py >/dev/null 2>&1 && echo "✅ SUCCESS" || echo "❌ FAILED"