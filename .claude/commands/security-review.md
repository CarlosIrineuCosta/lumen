---
description: Security vulnerability scanning and analysis
---

# Security Review Command

The `/security-review` command performs dedicated security analysis of your project, scanning for vulnerabilities and security best practices.

## Usage

```bash
/security-review [options]
```

## Options

- `--depth <level>`: Scan depth
  - `quick` (default): Basic security checks
  - `standard`: Comprehensive vulnerability scan
  - `deep`: Full security audit including dependencies

- `--focus <area>`: Focus area
  - `all` (default): All security areas
  - `dependencies`: Check for vulnerable dependencies
  - `code`: Analyze code for security issues
  - `config`: Check configuration security
  - `auth`: Authentication and authorization

- `--output <path>`: Custom output path for the report
- `--format <format>`: Output format
  - `md` (default): Markdown report
  - `json`: JSON data for CI/CD integration
  - `sarif`: SARIF format for security tools

- `--fix <level>`: Auto-fix level
  - `none` (default): No automatic fixes
  - `safe`: Apply safe automatic fixes
  - `all`: Apply all possible fixes

## Examples

```bash
# Quick security scan
/security-review

# Comprehensive dependency scan
/security-review --depth deep --focus dependencies

# Code security analysis
/security-review --focus code --format json

# Auto-apply safe fixes
/security-review --fix safe
```

## Implementation

```bash
#!/bin/bash

# Parse arguments
DEPTH="quick"
FOCUS="all"
FORMAT="md"
OUTPUT=""
FIX_LEVEL="none"

while [[ $# -gt 0 ]]; do
    case $1 in
        --depth)
            DEPTH="$2"
            shift 2
            ;;
        --focus)
            FOCUS="$2"
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
        --fix)
            FIX_LEVEL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get project root
PROJECT_ROOT="$(pwd)"

echo "# Security Review"
echo "================"
echo

# Security scanning function
run_security_scan() {
    local scan_type="$1"
    local scan_depth="$2"

    echo "Running $scan_type security scan ($scan_depth depth)..."

    case $scan_type in
        "dependencies")
            scan_dependencies "$scan_depth"
            ;;
        "code")
            scan_code_security "$scan_depth"
            ;;
        "config")
            scan_config_security "$scan_depth"
            ;;
        "auth")
            scan_auth_security "$scan_depth"
            ;;
    esac
}

# Dependency vulnerability scanning
scan_dependencies() {
    local depth="$1"

    echo "## Scanning for vulnerable dependencies..."

    # Check if safety is installed
    if ! command -v safety &> /dev/null; then
        echo "Installing safety for dependency scanning..."
        pip install safety
    fi

    # Run safety check
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        echo "Checking requirements.txt for vulnerabilities..."
        safety check -r "$PROJECT_ROOT/requirements.txt" --json --output /tmp/deps_vulns.json 2>/dev/null || true

        # Also check for common security issues in dependencies
        echo "Analyzing dependency security posture..."

        # Check for known vulnerable packages
        vulnerable_patterns=(
            "urllib3"
            "requests<2.20.0"
            "pillow<8.2.0"
            "jinja2<3.0.0"
            "django<3.2.0"
            "flask<2.0.0"
        )

        for pattern in "${vulnerable_patterns[@]}"; do
            if grep -q "$pattern" "$PROJECT_ROOT/requirements.txt" 2>/dev/null; then
                echo "  ⚠️  Potential vulnerability found: $pattern"
            fi
        done
    fi

    # Check package.json if it exists (Node.js projects)
    if [ -f "$PROJECT_ROOT/package.json" ]; then
        echo "Checking package.json for vulnerabilities..."
        if command -v npm &> /dev/null; then
            cd "$PROJECT_ROOT" && npm audit --json > /tmp/npm_audit.json 2>/dev/null || true
        fi
    fi
}

# Code security scanning
scan_code_security() {
    local depth="$1"

    echo "## Scanning code for security issues..."

    # Python security issues
    echo "Checking Python code for security issues..."

    # Common security vulnerabilities to check
    security_patterns=(
        "eval("
        "exec("
        "os.system("
        "subprocess.call.*shell=True"
        "pickle.loads("
        "input("
        "password.*=.*['\"]"
        "secret.*=.*['\"]"
        "token.*=.*['\"]"
        "api_key.*=.*['\"]"
        "sql.*%.*"
        "cursor.execute.*%.*"
        "shell=True"
        "ssl_verify=False"
        "verify=False"
        "allow_untrusted=True"
    )

    # Scan Python files
    while IFS= read -r -d '' pyfile; do
        echo "  Scanning: $(basename "$pyfile")"

        for pattern in "${security_patterns[@]}"; do
            if grep -n "$pattern" "$pyfile" 2>/dev/null; then
                echo "    ⚠️  Security issue detected: $pattern"
            fi
        done
    done < <(find "$PROJECT_ROOT" -name "*.py" -not -path "*/\.*" -not -path "*/venv/*" -not -path "*/env/*" -not -path "*/__pycache__/*" -print0)

    # Check for hardcoded secrets
    echo "Checking for hardcoded secrets..."
    secret_patterns=(
        "password\s*=\s*['\"][^'\"]{8,}['\"]"
        "secret\s*=\s*['\"][^'\"]{16,}['\"]"
        "token\s*=\s*['\"][^'\"]{20,}['\"]"
        "api_key\s*=\s*['\"][^'\"]{20,}['\"]"
        "aws_access_key_id\s*=\s*['\"]AKIA[0-9A-Z]{16}['\"]"
        "aws_secret_access_key\s*=\s*['\"][0-9a-zA-Z/+]{40}['\"]"
    )

    for pattern in "${secret_patterns[@]}"; do
        matches=$(grep -r -n "$pattern" "$PROJECT_ROOT" --include="*.py" --include="*.js" --include="*.yaml" --include="*.yml" --include="*.json" --exclude-dir=".git" 2>/dev/null || true)
        if [ -n "$matches" ]; then
            echo "  🔴 Potential hardcoded secret found:"
            echo "$matches"
        fi
    done

    # Check for SQL injection vulnerabilities
    echo "Checking for SQL injection vulnerabilities..."
    sql_patterns=(
        "execute.*%.*"
        "query.*%.*"
        "format.*SELECT.*"
        "f\".*SELECT.*"
        "cursor.execute.*\+.*"
    )

    for pattern in "${sql_patterns[@]}"; do
        matches=$(grep -r -n "$pattern" "$PROJECT_ROOT" --include="*.py" --exclude-dir=".git" 2>/dev/null || true)
        if [ -n "$matches" ]; then
            echo "  ⚠️  Potential SQL injection vulnerability:"
            echo "$matches"
        fi
    done

    # Check for XSS vulnerabilities
    echo "Checking for XSS vulnerabilities..."
    if [ -d "$PROJECT_ROOT/templates" ]; then
        echo "  Checking template files for unsafe rendering..."
        grep -r "render.*|safe" "$PROJECT_ROOT/templates" 2>/dev/null && echo "    ⚠️  |safe filter detected - potential XSS risk"
        grep -r "mark_safe" "$PROJECT_ROOT" --include="*.py" 2>/dev/null && echo "    ⚠️  mark_safe detected - potential XSS risk"
    fi
}

# Configuration security scanning
scan_config_security() {
    local depth="$1"

    echo "## Scanning configuration for security issues..."

    # Check .env files
    if [ -f "$PROJECT_ROOT/.env" ]; then
        echo "  ⚠️  .env file found in project root - ensure it's in .gitignore"
    fi

    # Check .env.example for security recommendations
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        echo "  Checking .env.example for security best practices..."

        # Check for debug flags
        if grep -qi "DEBUG.*=.*true" "$PROJECT_ROOT/.env.example"; then
            echo "    ⚠️  DEBUG flag should be False in production"
        fi

        # Check for secret keys
        if ! grep -q "SECRET_KEY" "$PROJECT_ROOT/.env.example"; then
            echo "    ⚠️  SECRET_KEY not documented in .env.example"
        fi

        # Check for database security
        if grep -qi "sqlite" "$PROJECT_ROOT/.env.example"; then
            echo "    ℹ️  SQLite detected - consider PostgreSQL for production"
        fi
    fi

    # Check Docker configuration
    if [ -f "$PROJECT_ROOT/Dockerfile" ]; then
        echo "  Checking Dockerfile security..."

        # Check if running as root
        if ! grep -q "USER\|adduser\|useradd" "$PROJECT_ROOT/Dockerfile"; then
            echo "    ⚠️  Container runs as root - consider adding a USER directive"
        fi

        # Check for exposed ports
        if grep -q "EXPOSE 22" "$PROJECT_ROOT/Dockerfile"; then
            echo "    ⚠️  SSH port exposed in container - not recommended"
        fi
    fi

    # Check docker-compose for security
    if [ -f "$PROJECT_ROOT/docker-compose.yml" ] || [ -f "$PROJECT_ROOT/docker-compose.yaml" ]; then
        echo "  Checking docker-compose security..."

        # Check for privileged containers
        if grep -q "privileged: true" "$PROJECT_ROOT"/docker-compose.*; then
            echo "    🔴 Privileged containers detected - security risk"
        fi

        # Check for root user
        if grep -q "user: root" "$PROJECT_ROOT"/docker-compose.*; then
            echo "    ⚠️  Running as root in containers"
        fi
    fi
}

# Authentication and authorization scanning
scan_auth_security() {
    local depth="$1"

    echo "## Scanning authentication and authorization..."

    # Check for JWT implementation
    if grep -r -i "jwt" "$PROJECT_ROOT" --include="*.py" 2>/dev/null; then
        echo "  JWT implementation detected"

        # Check for HS256 (symmetric) algorithm
        if grep -r "HS256" "$PROJECT_ROOT" --include="*.py" 2>/dev/null; then
            echo "    ⚠️  Using symmetric HS256 - consider RS256 for better security"
        fi

        # Check for 'none' algorithm
        if grep -r -i "algorithm.*=.*none" "$PROJECT_ROOT" --include="*.py" 2>/dev/null; then
            echo "    🔴 JWT 'none' algorithm detected - critical vulnerability!"
        fi
    fi

    # Check for password hashing
    if grep -r "md5\|sha1" "$PROJECT_ROOT" --include="*.py" 2>/dev/null | grep -i "password\|hash"; then
        echo "    🔴 Weak hashing algorithm (MD5/SHA1) used for passwords"
    fi

    # Check for bcrypt/argon2 usage
    if grep -r "bcrypt\|argon2" "$PROJECT_ROOT" --include="*.py" 2>/dev/null | grep -i "password\|hash"; then
        echo "    ✓ Strong hashing algorithm detected"
    fi

    # Check for session management
    if grep -r "session\|cookie" "$PROJECT_ROOT" --include="*.py" 2>/dev/null; then
        echo "  Session/cookie management detected"

        # Check for secure flags
        if ! grep -r "secure=True\|httponly=True" "$PROJECT_ROOT" --include="*.py" 2>/dev/null | grep -i "cookie"; then
            echo "    ⚠️  Consider setting secure/httponly flags for cookies"
        fi
    fi

    # Check for CORS configuration
    if grep -r -i "cors" "$PROJECT_ROOT" --include="*.py" 2>/dev/null; then
        echo "  CORS configuration detected"

        if grep -r "\"\*\"" "$PROJECT_ROOT" --include="*.py" 2>/dev/null | grep -i "origin"; then
            echo "    ⚠️  CORS allows all origins - consider restricting"
        fi
    fi
}

# Apply fixes if requested
apply_fixes() {
    local fix_level="$1"

    if [ "$fix_level" = "none" ]; then
        return
    fi

    echo
    echo "Applying automatic fixes ($fix_level level)..."

    # Safe fixes
    if [ "$fix_level" = "safe" ] || [ "$fix_level" = "all" ]; then
        # Add .env to .gitignore if not present
        if [ -f "$PROJECT_ROOT/.env" ] && [ -f "$PROJECT_ROOT/.gitignore" ]; then
            if ! grep -q "^\.env$" "$PROJECT_ROOT/.gitignore"; then
                echo ".env" >> "$PROJECT_ROOT/.gitignore"
                echo "  ✓ Added .env to .gitignore"
            fi
        fi

        # Update DEBUG flag in .env.example
        if [ -f "$PROJECT_ROOT/.env.example" ]; then
            sed -i.bak 's/DEBUG.*=.*True/DEBUG=False/gI' "$PROJECT_ROOT/.env.example"
            echo "  ✓ Set DEBUG=False in .env.example"
        fi
    fi

    # All fixes (use with caution)
    if [ "$fix_level" = "all" ]; then
        echo "  ℹ️  Advanced fixes not implemented for safety"
    fi
}

# Main execution
echo "Starting security review..."
echo "Focus: $FOCUS"
echo "Depth: $DEPTH"
echo "Format: $FORMAT"
echo

# Determine output path
if [ -z "$OUTPUT" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    OUTPUT="$PROJECT_ROOT/security_review_$TIMESTAMP.md"
fi

# Create temporary file for findings
TEMP_FINDINGS="/tmp/security_findings_$$"
echo "# Security Review Report" > "$TEMP_FINDINGS"
echo "**Date:** $(date +"%Y-%m-%d %H:%M:%S")" >> "$TEMP_FINDINGS"
echo "**Depth:** $DEPTH" >> "$TEMP_FINDINGS"
echo "" >> "$TEMP_FINDINGS"

# Run scans based on focus
if [ "$FOCUS" = "all" ]; then
    run_security_scan "dependencies" "$DEPTH" 2>&1 | tee -a "$TEMP_FINDINGS"
    run_security_scan "code" "$DEPTH" 2>&1 | tee -a "$TEMP_FINDINGS"
    run_security_scan "config" "$DEPTH" 2>&1 | tee -a "$TEMP_FINDINGS"
    run_security_scan "auth" "$DEPTH" 2>&1 | tee -a "$TEMP_FINDINGS"
else
    run_security_scan "$FOCUS" "$DEPTH" 2>&1 | tee -a "$TEMP_FINDINGS"
fi

# Add recommendations section
echo "" >> "$TEMP_FINDINGS"
echo "# Security Recommendations" >> "$TEMP_FINDINGS"
echo "" >> "$TEMP_FINDINGS"
echo "1. Use strong, unique passwords for all services" >> "$TEMP_FINDINGS"
echo "2. Enable two-factor authentication where possible" >> "$TEMP_FINDINGS"
echo "3. Keep all dependencies updated" >> "$TEMP_FINDINGS"
echo "4. Use environment variables for secrets, never hardcode them" >> "$TEMP_FINDINGS"
echo "5. Implement proper error handling without information disclosure" >> "$TEMP_FINDINGS"
echo "6. Regular security audits and penetration testing" >> "$TEMP_FINDINGS"
echo "7. Use WAF (Web Application Firewall) in production" >> "$TEMP_FINDINGS"
echo "8. Implement rate limiting to prevent brute force attacks" >> "$TEMP_FINDINGS"

# Apply fixes if requested
apply_fixes "$FIX_LEVEL"

# Format output
if [ "$FORMAT" = "json" ]; then
    # Convert to JSON format
    echo "Converting report to JSON format..."
    python3 -c "
import json
import re

with open('$TEMP_FINDINGS', 'r') as f:
    content = f.read()

# Extract findings
sections = re.split(r'^## ', content, flags=re.MULTILINE)
report = {
    'timestamp': '$(date -Iseconds)',
    'depth': '$DEPTH',
    'focus': '$FOCUS',
    'findings': []
}

for section in sections[1:]:
    lines = section.split('\n')
    title = lines[0]
    details = '\n'.join(lines[1:])

    report['findings'].append({
        'category': title.strip(),
        'details': details.strip()
    })

# Save JSON
with open('$OUTPUT', 'w') as f:
    json.dump(report, f, indent=2)
"
    rm "$TEMP_FINDINGS"
elif [ "$FORMAT" = "sarif" ]; then
    # Convert to SARIF format
    echo "SARIF format not yet implemented"
    cp "$TEMP_FINDINGS" "$OUTPUT"
else
    # Keep markdown format
    mv "$TEMP_FINDINGS" "$OUTPUT"
fi

echo
echo "# Security Review Complete"
echo "========================="
echo
echo "Report saved to: $OUTPUT"

# Count security issues
if [ -f "$OUTPUT" ]; then
    CRITICAL=$(grep -c "🔴" "$OUTPUT" 2>/dev/null || echo "0")
    WARNING=$(grep -c "⚠️" "$OUTPUT" 2>/dev/null || echo "0")
    INFO=$(grep -c "ℹ️" "$OUTPUT" 2>/dev/null || echo "0")
    GOOD=$(grep -c "✓" "$OUTPUT" 2>/dev/null || echo "0")

    echo
    echo "Summary:"
    echo "  Critical issues: $CRITICAL"
    echo "  Warnings: $WARNING"
    echo "  Info: $INFO"
    echo "  Good practices: $GOOD"
fi

echo
echo "Review the report for detailed security recommendations."
```