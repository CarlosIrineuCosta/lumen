#!/bin/bash

# Parse arguments
SCOPE="all"
FORMAT="md"
OUTPUT=""
PARALLEL=true
UPDATE_DOCS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --scope)
            SCOPE="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --no-parallel)
            PARALLEL=false
            shift
            ;;
        --update-docs)
            UPDATE_DOCS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get project root
PROJECT_ROOT="$(pwd)"

echo "# Comprehensive Project Audit"
echo "==========================="
echo

# Create todos for tracking
echo "Starting comprehensive audit with scope: $SCOPE"
echo "Format: $FORMAT"
echo

# Initialize todo tracking
todo=(
    "Analyzing documentation"
    "Examining code structure"
    "Validating configuration"
    "Checking tasks compliance"
    "Generating report"
    "Updating documentation"
)

# Function to update todo status
update_todo() {
    local index=$1
    local status=$2
    todo[$index]="${todo[$index]} [$status]"
}

# Step 1: Analyze documentation
if [[ "$SCOPE" == "all" || "$SCOPE" == "docs" || "$SCOPE" == "quick" ]]; then
    echo "Step 1: Analyzing documentation..."
    update_todo 0 "IN_PROGRESS"

    if [ "$PARALLEL" = true ] && [ "$SCOPE" == "all" ]; then
        # Use parallel agent execution
        python3 "$PROJECT_ROOT/scripts/review_integration.py" \
            --project-root "$PROJECT_ROOT" \
            --review-type comprehensive \
            > /tmp/review_docs_output.json 2>&1 &
        DOCS_PID=$!
    else
        # Sequential execution
        python3 "$PROJECT_ROOT/scripts/review_handler.py" \
            --project-root "$PROJECT_ROOT" \
            --scope docs \
            --output /tmp/review_docs.json \
            --format json
    fi

    update_todo 0 "DONE"
fi

# Step 2: Examine code structure
if [[ "$SCOPE" == "all" || "$SCOPE" == "code" ]]; then
    echo "Step 2: Examining code structure..."
    update_todo 1 "IN_PROGRESS"

    if [ "$PARALLEL" = true ] && [ "$SCOPE" == "all" ]; then
        # Already running in parallel
        wait $DOCS_PID
    else
        python3 "$PROJECT_ROOT/scripts/review_handler.py" \
            --project-root "$PROJECT_ROOT" \
            --scope code \
            --output /tmp/review_code.json \
            --format json
    fi

    update_todo 1 "DONE"
fi

# Step 3: Validate configuration
if [[ "$SCOPE" == "all" || "$SCOPE" == "config" || "$SCOPE" == "quick" ]]; then
    echo "Step 3: Validating configuration..."
    update_todo 2 "IN_PROGRESS"

    python3 "$PROJECT_ROOT/scripts/review_handler.py" \
        --project-root "$PROJECT_ROOT" \
        --scope config \
        --output /tmp/review_config.json \
        --format json

    update_todo 2 "DONE"
fi

# Step 4: Check tasks compliance
if [[ "$SCOPE" == "all" ]]; then
    echo "Step 4: Checking tasks compliance..."
    update_todo 3 "IN_PROGRESS"

    # Look for tasks file
    TASKS_FILE=$(find "$PROJECT_ROOT" -name "tasks_*.md" -type f | head -n 1)

    if [ -n "$TASKS_FILE" ]; then
        echo "Found tasks file: $TASKS_FILE"
        python3 "$PROJECT_ROOT/scripts/review_handler.py" \
            --project-root "$PROJECT_ROOT" \
            --scope tasks \
            --output /tmp/review_tasks.json \
            --format json
    else
        echo "No tasks file found"
    fi

    update_todo 3 "DONE"
fi

# Step 5: Generate comprehensive report
echo "Step 5: Generating report..."
update_todo 4 "IN_PROGRESS"

# Determine output path
if [ -z "$OUTPUT" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    OUTPUT="$PROJECT_ROOT/audit_report_$TIMESTAMP.$FORMAT"
fi

# Run the review handler with all scopes
python3 "$PROJECT_ROOT/scripts/review_handler.py" \
    --project-root "$PROJECT_ROOT" \
    --scope "$SCOPE" \
    --output "$OUTPUT" \
    --format "$FORMAT"

update_todo 4 "DONE"

# Step 6: Update documentation if requested
if [ "$UPDATE_DOCS" = true ]; then
    echo "Step 6: Updating documentation..."
    update_todo 5 "IN_PROGRESS"

    # Update README with review summary
    if [ -f "$OUTPUT" ] && [ "$FORMAT" = "md" ]; then
        # Extract summary and add to README
        SUMMARY=$(sed -n '/# Executive Summary/,/^#/p' "$OUTPUT" | sed '$d')

        # Backup original README
        if [ -f "$PROJECT_ROOT/README.md" ]; then
            cp "$PROJECT_ROOT/README.md" "$PROJECT_ROOT/README.md.backup"
        fi

        # Add review status to README
        cat >> "$PROJECT_ROOT/README.md" << EOF

# Last Review Status

**Date:** $(date +"%Y-%m-%d %H:%M:%S")
**Report:** [$(basename "$OUTPUT")]($(basename "$OUTPUT"))

$SUMMARY
EOF
    fi

    update_todo 5 "DONE"
fi

# Display summary
echo
echo "# Audit Summary"
echo "==============="
echo
echo "Report generated: $OUTPUT"
echo "Audit scope: $SCOPE"
echo "Format: $FORMAT"

# Count issues if markdown report
if [ "$FORMAT" = "md" ] && [ -f "$OUTPUT" ]; then
    CRITICAL=$(grep -c "CRITICAL" "$OUTPUT" || echo "0")
    HIGH=$(grep -c "HIGH" "$OUTPUT" || echo "0")
    MEDIUM=$(grep -c "MEDIUM" "$OUTPUT" || echo "0")
    LOW=$(grep -c "LOW" "$OUTPUT" || echo "0")

    echo
    echo "Issues found:"
    echo "  Critical: $CRITICAL"
    echo "  High: $HIGH"
    echo "  Medium: $MEDIUM"
    echo "  Low: $LOW"
fi

# Display todos completion
echo
echo "# Tasks Completed"
echo "================"
for task in "${todo[@]}"; do
    echo "✓ $task"
done

echo
echo "Audit complete! Check the report for detailed findings."