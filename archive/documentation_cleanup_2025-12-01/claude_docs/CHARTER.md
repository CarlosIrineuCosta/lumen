# Lumen Project Charter

## System Architecture

### Components
- **Frontend**: PMM pattern with vanilla JS, glass UI
- **Backend**: FastAPI + PostgreSQL + Redis
- **Authentication**: Firebase (frontend) + JWT validation (backend)
- **Storage**: Local file system for photos

### LLM Orchestration Architecture

```
Claude Code (Primary Orchestrator)
├── Planning & Architecture
├── Frontend Implementation (auth, router, UI)
├── Task Coordination
└── Delegates to:
    ├── GLM (Testing, Documentation, Implementations)
    └── Codex (Backend Optimization, Security)
```

## Task Routing Rules

### Route to GLM when:
- Writing tests (pytest, integration tests)
- Creating documentation
- Implementing well-defined features
- Refactoring with clear specifications
- Quality assurance and validation work

### Route to Codex when:
- Backend performance optimization
- Database query optimization
- Security audits and fixes
- Infrastructure improvements
- Connection pooling and caching

### Keep in Claude when:
- Architectural decisions
- Authentication state management
- Router coordination logic
- Cross-component integration
- Complex reasoning about system behavior

## Cross-Agent Verification Protocol

**Rule**: The LLM that implements CANNOT be the one that reviews.

- GLM's work reviewed by → Codex
- Codex's work reviewed by → Claude Code subagent
- Claude's work reviewed by → GLM

## Success Criteria

### Technical
- All tests pass
- No authentication race conditions
- API response < 100ms
- Frontend modules < 400 lines each

### Quality
- Cross-agent review passed
- Documentation updated
- No security vulnerabilities
- Mobile responsive

## Project Constraints

### No Build Tools Philosophy
- Vanilla JavaScript only
- No React, Vue, Angular
- No webpack, Vite, etc.
- PMM (Poor Man's Modules) pattern
- Global window.Lumen* objects

### Module Size Limit
- Maximum 400 lines per module
- Break larger modules into smaller ones
- Clear separation of concerns

### Testing Requirements
- Backend: pytest with >70% coverage
- Frontend: Manual testing + integration tests
- All new features must have tests
- GLM handles most test generation

## Current Focus

As of November 15, 2025:
- Fix authentication race condition
- Stabilize API connections
- Resolve module reference errors
- Get to working MVP
