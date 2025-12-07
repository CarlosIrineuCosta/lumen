# Review Templates and Standards

This document defines templates and standards for consistent review reporting across the project.

# General Report Template

Use this template for all review reports to ensure consistency.

```markdown
# {REPORT_TITLE} - {DATE}

**Review Type:** {REVIEW_TYPE}
**Review Scope:** {REVIEW_SCOPE}
**Reviewers:** {REVIEWERS}
**Duration:** {DURATION}

# Executive Summary

{HIGH_LEVEL_SUMMARY}

# Findings Summary

{FINDINGS_SUMMARY_TABLE}

# Detailed Findings

{DETAILED_FINDINGS}

# Risk Assessment

{RISK_ASSESSMENT}

# Recommendations

{RECOMMENDATIONS}

# Action Items

{ACTION_ITEMS}

# Appendix

{APPENDIX}
```

# Finding Categories

## Documentation Issues

Template for documentation findings:

```markdown
**Type:** Documentation
**Severity:** {CRITICAL|HIGH|MEDIUM|LOW}
**File:** {FILE_PATH}
**Line:** {LINE_NUMBER}
**Description:** {DESCRIPTION}
**Impact:** {IMPACT_ON_PROJECT}
**Recommendation:** {RECOMMENDATION}
```

## Code Issues

Template for code findings:

```markdown
**Type:** Code
**Severity:** {CRITICAL|HIGH|MEDIUM|LOW}
**File:** {FILE_PATH}
**Line:** {LINE_NUMBER}
**Description:** {DESCRIPTION}
**Pattern:** {ANTI_PATTERN_OR_VULNERABILITY}
**Impact:** {IMPACT_ON_FUNCTIONALITY_OR_SECURITY}
**Recommendation:** {RECOMMENDATION}
**Example:** {CODE_EXAMPLE_IF_APPLICABLE}
```

## Configuration Issues

Template for configuration findings:

```markdown
**Type:** Configuration
**Severity:** {CRITICAL|HIGH|MEDIUM|LOW}
**File:** {CONFIG_FILE}
**Setting:** {SETTING_NAME}
**Current Value:** {CURRENT_VALUE}
**Recommended Value:** {RECOMMENDED_VALUE}
**Description:** {DESCRIPTION}
**Impact:** {IMPACT_ON_SYSTEM}
**Recommendation:** {RECOMMENDATION}
```

# Severity Levels

## Critical
- Security vulnerabilities that can be exploited
- Data loss or corruption risks
- System failure or downtime risks
- Legal or compliance violations

## High
- Performance issues affecting user experience
- Security best practices violations
- Potential bugs in production code
- Missing critical functionality

## Medium
- Code quality issues
- Minor performance improvements
- Documentation gaps for important features
- Configuration inconsistencies

## Low
- Style or formatting issues
- Minor documentation improvements
- Nice-to-have features
- Code organization suggestions

# Review Types

## Comprehensive Review
- Scope: All aspects of project
- Duration: 2-3 hours
- Deliverables: Full report with all sections

## Quick Review
- Scope: Documentation and configuration only
- Duration: 30-60 minutes
- Deliverables: Summary report with critical/high issues

## Security Review
- Scope: Security vulnerabilities and best practices
- Duration: 1-2 hours
- Deliverables: Security-focused report with risk assessment

## Documentation Review
- Scope: Documentation completeness and accuracy
- Duration: 1 hour
- Deliverables: Documentation gap analysis

## Code Review
- Scope: Code quality and best practices
- Duration: 1-2 hours
- Deliverables: Code quality report with examples

# Output Formats

## Markdown Format
- Default format for human-readable reports
- Supports GitHub rendering
- Easy to edit and comment

## JSON Format
```json
{
  "metadata": {
    "title": "Report Title",
    "date": "YYYY-MM-DD",
    "type": "comprehensive",
    "version": "1.0"
  },
  "summary": {
    "total_findings": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  },
  "findings": [
    {
      "id": "UNIQUE_ID",
      "type": "documentation|code|configuration|security",
      "severity": "critical|high|medium|low",
      "title": "Finding Title",
      "description": "Detailed description",
      "file": "path/to/file",
      "line": 123,
      "recommendation": "Recommendation text",
      "impact": "Impact description"
    }
  ],
  "recommendations": [
    {
      "priority": 1,
      "title": "Recommendation Title",
      "description": "Detailed recommendation"
    }
  ]
}
```

## SARIF Format (Security)
For integration with security tools:

```json
{
  "$schema": "https://json.schemastore.org/sarif-2.1.0",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Security Review",
          "version": "1.0.0"
        }
      },
      "results": [
        {
          "ruleId": "SEC001",
          "level": "error",
          "message": {
            "text": "Security issue description"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "file.py"
                },
                "region": {
                  "startLine": 123
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

# Best Practices

## Review Process
1. Define scope and objectives
2. Use appropriate templates
3. Document all findings with evidence
4. Prioritize by severity and impact
5. Provide actionable recommendations
6. Follow up on action items

## Writing Findings
- Be specific and factual
- Include file paths and line numbers
- Explain the impact, not just the issue
- Provide clear, actionable recommendations
- Include code examples for fixes

## Report Quality
- Proofread before publishing
- Ensure consistent formatting
- Verify all links and references
- Check for duplicate findings
- Validate severity assignments

# Integration Guidelines

## Git Integration
- Commit review reports to docs/reviews/
- Use conventional commit format
- Reference issue or PR numbers
- Keep reports in version control

## CI/CD Integration
- Use JSON format for automated processing
- Fail build on critical findings
- Generate trends and metrics
- Integrate with ticketing systems

## Agent Integration
- Each agent focuses on specific category
- Use standardized finding format
- Coordinate to avoid duplicates
- Aggregate results for final report

# Review Checklist

## Before Starting
- [ ] Define review scope and objectives
- [ ] Select appropriate template
- [ ] Identify stakeholders
- [ ] Schedule sufficient time
- [ ] Prepare tools and resources

## During Review
- [ ] Document all findings
- [ ] Capture evidence
- [ ] Assess severity objectively
- [ ] Write clear recommendations
- [ ] Track progress

## After Review
- [ ] Review and edit report
- [ ] Validate findings
- [ ] Share with stakeholders
- [ ] Create action items
- [ ] Schedule follow-up

# Example Reports

See the following examples for reference:
- Comprehensive Review Example
- Security Review Example
- Documentation Review Example

# Maintenance

- Update templates regularly
- Add new finding types as needed
- Incorporate feedback from users
- Stay current with best practices
- Review and improve process