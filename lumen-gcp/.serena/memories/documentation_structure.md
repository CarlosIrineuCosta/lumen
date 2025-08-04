# Documentation Structure & AI Coordination Rules

## Document Organization System

### Prefix-Based Separation
- **CODE-** prefix: Technical implementation documents (Claude Code territory)
- **STRATEGY-** prefix: Business strategy and planning documents (Claude Desktop territory)

### Claude Code Responsibilities
- Work ONLY with **CODE-** prefixed files for implementation details
- Read any file for context, but modify only CODE- files
- Focus on technical specs, current status, and API documentation
- Reference files: `docs/CODE-technical-implementation.md`, `docs/CODE-current-status.md`, `docs/CODE-api-reference.md`

### Documentation Rules
- **NEVER CREATE NEW .md FILES** unless explicitly requested by user
- Update existing CODE- files when implementation changes occur
- Maintain technical accuracy in all CODE- documentation
- Keep documentation concurrent with actual implementation state
- No overlap with STRATEGY- files (handled by Claude Desktop)

### Key Documents Structure

#### Root Level
- `README.md` - Master index explaining documentation structure
- `CLAUDE.md` - Instructions for Claude Code (THIS file)

#### Technical Documentation (CODE- prefix)
- `docs/CODE-technical-implementation.md` - Comprehensive technical specs, architecture, implementation details
- `docs/CODE-current-status.md` - Current development state, what's working, needs fixing
- `docs/CODE-api-reference.md` - Complete API endpoints documentation with examples

#### Strategic Documentation (STRATEGY- prefix - READ ONLY)
- `docs/STRATEGY-business-framework.md` - Business model, monetization, growth strategy
- `docs/STRATEGY-content-policy.md` - Content moderation, artistic standards, philosophy  
- `docs/STRATEGY-user-acquisition.md` - Marketing, user growth, community building

## Archive System
- All original files preserved in `docs/archive/backup-[DATE]-reorganization/`
- Complete backup ensures no information loss during reorganization

## Benefits of This Structure
1. **Clear Separation**: Each AI knows exactly which files to work with
2. **No Conflicts**: Prevents simultaneous editing conflicts between AIs
3. **Consolidated Information**: Merged redundant content into authoritative documents
4. **Easy Navigation**: Prefix immediately shows document purpose
5. **Simultaneous Work**: Both AIs can work on project without stepping on each other

## Implementation Guidelines
- When making code changes, update relevant CODE- documentation
- When reading project context, can reference any file but respect modification boundaries
- Focus on keeping CODE- files accurate and current with implementation reality
- Never duplicate information between CODE- and STRATEGY- files