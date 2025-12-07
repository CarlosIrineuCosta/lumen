---
description: Comprehensive project audit using multiple agents
---

# Comprehensive Project Audit

The `/audit` command performs a thorough analysis of your project, comparing documentation with actual implementation and validating configuration consistency.

## Usage

```bash
/audit [options]
```

## Options

- `--scope <scope>`: Audit scope
  - `all` (default): Complete audit of documentation, code, and configuration
  - `docs`: Documentation analysis only
  - `code`: Code structure analysis only
  - `config`: Configuration validation only
  - `quick`: Fast audit of docs and config

- `--output <path>`: Custom output path for the report
- `--format <format>`: Output format
  - `md` (default): Markdown report
  - `json`: JSON data for programmatic use

- `--parallel`: Enable parallel agent execution (default: true)
- `--update-docs`: Update documentation files with findings (default: false)

## Examples

```bash
# Comprehensive audit
/audit

# Quick audit of documentation and configuration
/audit --scope quick

# Audit specific components
/audit --scope docs,config

# Generate JSON output
/audit --format json

# Save to custom location
/audit --output /reports/project-audit.md
```

## Implementation

```bash
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

# Source the structure validator
source "$(dirname "$0")/lib/structure-validator.sh"

# Detect project type
detect_project_type

echo "# Comprehensive Project Audit"
echo "==========================="
echo

# Create todos for tracking
echo "Starting comprehensive audit..."
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
echo "Step 1: Analyzing documentation..."
update_todo 0 "IN_PROGRESS"

if [ "$PARALLEL" = true ]; then
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

# Step 2: Examine code structure
echo "Step 2: Examining code structure..."
update_todo 1 "IN_PROGRESS"

if [ "$PARALLEL" = true ]; then
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

# Step 3: Validate configuration
echo "Step 3: Validating configuration..."
update_todo 2 "IN_PROGRESS"

python3 "$PROJECT_ROOT/scripts/review_handler.py" \
    --project-root "$PROJECT_ROOT" \
    --scope config \
    --output /tmp/review_config.json \
    --format json

update_todo 2 "DONE"

# Step 4: Check tasks compliance
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

# Step 5: Generate comprehensive report
echo "Step 5: Generating report..."
update_todo 4 "IN_PROGRESS"

# Determine output path
if [ -z "$OUTPUT" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    OUTPUT="$PROJECT_ROOT/audit_report_$TIMESTAMP.md"
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
```

## Output

The audit command generates a comprehensive report with the following sections:

1. **Executive Summary**: High-level overview of findings
2. **Project Purpose**: What the project is meant to be (based on documentation)
3. **Current Implementation Status**: Actual state of the codebase
4. **Documentation vs Code Divergences**: Mismatches between docs and implementation
5. **Configuration Analysis**: Dependencies and environment variables validation
6. **Tasks Compliance**: Analysis of tasks_*.md vs actual state (if found)
7. **Recommendations**: Prioritized action items

## Integration

The audit command integrates with:

- **Agent System**: Uses multiple agents for parallel analysis
- **Hook System**: Triggers pre and post-audit hooks
- **Session State**: Updates audit status in session state
- **Documentation**: Can update existing docs with findings

## Notes

- Audits run in parallel by default for faster execution
- The command respects project structure and works with various architectures
- Sensitive information is never included in reports
- Reports are timestamped to maintain audit history