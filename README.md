# Lumen Photography Platform - Documentation Structure

**Last Updated**: August 3, 2025

## Documentation Organization

This project uses a prefix-based documentation system to maintain clear separation between technical implementation (Claude Code) and strategic planning (Claude Desktop).

### Document Prefixes

- **CODE-** : Technical implementation documents for Claude Code
- **STRATEGY-** : Business strategy and planning documents for Claude Desktop

### Documentation Files

#### Technical Implementation (Claude Code Territory)
- `CLAUDE.md` - Instructions for Claude Code (root directory)
- `docs/CODE-technical-implementation.md` - Complete technical specs, architecture, and implementation details
- `docs/CODE-current-status.md` - Current development state, what's working, what needs fixing
- `docs/CODE-api-reference.md` - API endpoints, request/response formats, authentication

#### Strategic Planning (Claude Desktop Territory)
- `docs/STRATEGY-business-framework.md` - Business model, monetization, growth strategy
- `docs/STRATEGY-content-policy.md` - Content moderation, artistic standards, platform philosophy
- `docs/STRATEGY-user-acquisition.md` - Marketing, user growth, community building

### Project Access

- **Development Server**: http://100.106.201.33:8080 (API) via Tailscale
- **Web Application**: http://100.106.201.33:8000/lumen-app.html
- **API Documentation**: http://100.106.201.33:8080/docs

### Quick Start

For development work, see `docs/CODE-technical-implementation.md`
For business decisions, see `docs/STRATEGY-business-framework.md`

### Archive

Previous documentation versions are stored in `docs/archive/` with date stamps.