#!/bin/bash
# Quick test script for multi-agent system

echo "=== Lumen Multi-Agent System Test ==="
echo ""

# Test 1: Check file structure
echo "1. Checking file structure..."
if [ -f "COORDINATION.md" ] && [ -f "scripts/agents/ai-agent.sh" ] && [ -f "scripts/agents/agent_coordinator.py" ]; then
    echo "   ✅ All files present"
else
    echo "   ❌ Missing files"
fi

# Test 2: Check Python
echo ""
echo "2. Checking Python..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python3 available"
else
    echo "   ❌ Python3 not found"
fi

# Test 3: Test coordinator
echo ""
echo "3. Testing coordinator..."
python3 scripts/agents/agent_coordinator.py list
if [ $? -eq 0 ]; then
    echo "   ✅ Coordinator working"
else
    echo "   ❌ Coordinator failed"
fi

# Test 4: Check for jq (needed for AI agent)
echo ""
echo "4. Checking dependencies..."
if command -v jq &> /dev/null; then
    echo "   ✅ jq installed"
else
    echo "   ❌ jq not found - install with: sudo apt-get install jq"
fi

echo ""
echo "=== Test Complete ==="
