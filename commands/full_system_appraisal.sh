#!/bin/bash
# Full System Appraisal with Cross-Check
# Usage: ./agent-system/commands/full_system_appraisal.sh

set -e

echo "🔍 LUMEN SYSTEM APPRAISAL"
echo "=========================="
echo "Date: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}Step 1: Primary Appraisal by GLM${NC}"
echo "----------------------------------"
echo "Running comprehensive system evaluation..."
echo ""

# Run GLM appraisal
echo "GLM_APPRAISAL_START=$(date)" > .appraisal_log.txt
claude --prompt "$(cat agent-system/prompts/complete_system_appraisal.txt)" \
    --model glm-4.5-flash \
    --output appraisal_report_glm.md \
    --temperature 0.3 \
    --max-tokens 8000

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ GLM appraisal completed${NC}"
    echo "Report saved to: appraisal_report_glm.md"
else
    echo -e "${RED}✗ GLM appraisal failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 2: Cross-Check by Codex${NC}"
echo "----------------------------------"
echo "Having another LLM verify the findings..."
echo ""

# Run Codex cross-check
echo "CROSS_CHECK_START=$(date)" >> .appraisal_log.txt
claude --prompt "You are cross-checking the system appraisal in appraisal_report_glm.md. Follow the 'CROSS-CHECK PROMPT FOR DIFFERENT LLM' section from agent-system/prompts/complete_system_appraisal.txt. Provide your independent assessment." \
    --model codex \
    --output appraisal_crosscheck_codex.md \
    --temperature 0.2 \
    --max-tokens 6000

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Codex cross-check completed${NC}"
    echo "Report saved to: appraisal_crosscheck_codex.md"
else
    echo -e "${RED}✗ Codex cross-check failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 3: Synthesizing Final Report${NC}"
echo "----------------------------------"
echo "Creating unified appraisal report..."

# Create unified report
cat > APPRAISAL_UNIFIED_REPORT.md << EOF
# Lumen Photography Platform - Unified Appraisal Report
**Date**: $(date)
**Appraised by**: GLM (Primary) + Codex (Cross-check)
---

## Executive Summary

### Appraiser Scores:
- **GLM Assessment**: [Will be filled after reading report]
- **Codex Cross-Check**: [Will be filled after reading report]
- **Unified Score**: [Will be calculated]

---

## Primary Appraisal (GLM)

$(cat appraisal_report_glm.md)

---

## Cross-Check Analysis (Codex)

$(cat appraisal_crosscheck_codex.md)

---

## Unified Recommendations

[To be filled after reviewing both reports]

---

## Appraisal Log

$(cat .appraisal_log.txt)

EOF

echo -e "${GREEN}✓ Unified report created: APPRAISAL_UNIFIED_REPORT.md${NC}"

echo ""
echo -e "${BLUE}Step 4: Optional: Third Opinion (Gemini)${NC}"
echo "-----------------------------------"
read -p "Run third appraisal with Gemini for additional perspective? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running Gemini appraisal..."
    claude --prompt "You are providing a third perspective on the Lumen system appraisal. Read both appraisal_report_glm.md and appraisal_crosscheck_codex.md, then provide your own comprehensive assessment following the same structure. Focus on finding any missed issues or correcting any misassessments." \
        --model gemini \
        --output appraisal_perspective_gemini.md \
        --temperature 0.3 \
        --max-tokens 8000

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Gemini perspective completed${NC}"
        # Add Gemini to unified report
        echo "" >> APPRAISAL_UNIFIED_REPORT.md
        echo "---" >> APPRAISAL_UNIFIED_REPORT.md
        echo "" >> APPRAISAL_UNIFIED_REPORT.md
        echo "## Third Perspective (Gemini)" >> APPRAISAL_UNIFIED_REPORT.md
        echo "" >> APPRAISAL_UNIFIED_REPORT.md
        echo "$(cat appraisal_perspective_gemini.md)" >> APPRAISAL_UNIFIED_REPORT.md
    else
        echo -e "${YELLOW}⚠ Gemini appraisal failed${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✅ Appraisal Complete!${NC}"
echo ""
echo "Generated Reports:"
echo "  - appraisal_report_glm.md (Primary appraisal)"
echo "  - appraisal_crosscheck_codex.md (Cross-check)"
if [ -f appraisal_perspective_gemini.md ]; then
    echo "  - appraisal_perspective_gemini.md (Third opinion)"
fi
echo "  - APPRAISAL_UNIFIED_REPORT.md (Consolidated report)"
echo ""
echo "Next steps:"
echo "1. Review APPRAISAL_UNIFIED_REPORT.md"
echo "2. Prioritize critical issues"
echo "3. Create action plan"