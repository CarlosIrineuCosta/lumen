# LLM Response Formats

## GLM → Claude Communication

When GLM completes a task, it must respond in this XML format:

```xml
<implementation>
[Complete code here]
</implementation>

<files_changed>
path/to/file1.js
path/to/file2.py
</files_changed>

<explanation>
Brief explanation of what was implemented and why.
</explanation>

<test_commands>
# Commands to verify the implementation
python -m pytest backend/tests/test_new_feature.py
</test_commands>

<needs_review>
- Any architectural questions
- Areas requiring Claude's decision
- Uncertain implementation choices
</needs_review>
```

## Codex → Claude Communication

Similar format but with focus on backend:

```xml
<optimization>
[Code changes]
</optimization>

<performance_impact>
- Database queries reduced from X to Y
- Response time improved by Z%
</performance_impact>

<security_changes>
- Input validation added for X
- SQL injection protection for Y
</security_changes>

<needs_review>
[Any concerns or questions]
</needs_review>
```

## Review Format (Any LLM → Any LLM)

When reviewing another LLM's work:

```xml
<review>
<status>APPROVED|CHANGES_NEEDED|REJECTED</status>

<issues>
- Issue 1: Description and location
- Issue 2: Description and location
</issues>

<recommendations>
- Recommendation 1
- Recommendation 2
</recommendations>

<security_concerns>
[Any security issues found]
</security_concerns>

</review>
```

## Parsing Guidelines

All hook scripts should:
1. Extract content between XML tags
2. Validate structure before processing
3. Handle malformed responses gracefully
4. Log parsing errors for debugging

## Error Response Format

If an LLM encounters an error:

```xml
<error>
<type>TIMEOUT|INVALID_INPUT|EXECUTION_FAILED</type>
<message>Human-readable error description</message>
<details>
Technical details for debugging
</details>
</error>
```
