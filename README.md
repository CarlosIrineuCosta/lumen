# Lumen Photography Platform

Professional photography platform designed as an ethical alternative to Instagram, prioritizing photographers' artistic freedom, professional networking, and quality over engagement metrics.

**Last Updated**: August 13, 2025

## Quick Links

- **Development Server**: http://100.106.201.33:8080 (API) via Tailscale
- **Web Application**: http://100.106.201.33:8000
- **API Documentation**: http://100.106.201.33:8080/docs

## Documentation Structure

### 📁 Core Documents
- [`CLAUDE.md`](CLAUDE.md) - Instructions for AI assistants (Claude Code & Gemini CLI)
- [`PROJECT_VISION.md`](PROJECT_VISION.md) - Platform philosophy and core principles
- [`SHARED-STATUS.md`](SHARED-STATUS.md) - Real-time coordination between AI assistants
- [`README1st-13aug2025.md`](README1st-13aug2025.md) - Swiss VPS migration plan (today's priority)

### 📁 Technical Documentation (`/docs/technical/`)
- [`TECHNICAL-GUIDE.md`](docs/technical/TECHNICAL-GUIDE.md) - Complete technical implementation guide
- [`API-REFERENCE.md`](docs/technical/API-REFERENCE.md) - API endpoints and usage
- [`DATABASE-ARCHITECTURE.md`](docs/technical/DATABASE-ARCHITECTURE.md) - Critical database decisions

### 📁 Business Documentation (`/docs/business/`)
- [`business-framework.md`](docs/business/business-framework.md) - Business model and monetization
- [`content-policy.md`](docs/business/content-policy.md) - Content moderation guidelines
- [`user-acquisition.md`](docs/business/user-acquisition.md) - Growth and marketing strategy
- [`database-cost-analysis.md`](docs/business/database-cost-analysis.md) - Infrastructure cost analysis

### 📁 PWA Development (`/opusdev/`)
- [`README.md`](opusdev/README.md) - PWA-specific documentation
- [`DEVELOPMENT_ROADMAP_2025.md`](opusdev/DEVELOPMENT_ROADMAP_2025.md) - Current priorities and roadmap
- [`CLAUDE_INSTRUCTIONS.md`](opusdev/CLAUDE_INSTRUCTIONS.md) - Claude Desktop specific instructions

### 📁 Archive (`/docs/archive/`)
Historical documentation and session notes for reference.

## Quick Start

### Development Setup
```bash
# Start all services
./scripts/server-manager.sh start

# Check status
./scripts/server-manager.sh status

# Access points
# Backend API: http://100.106.201.33:8080
# Frontend App: http://100.106.201.33:8000
# API Docs: http://100.106.201.33:8080/docs
```

### For Developers
1. Read [`TECHNICAL-GUIDE.md`](docs/technical/TECHNICAL-GUIDE.md) for architecture overview
2. Check [`API-REFERENCE.md`](docs/technical/API-REFERENCE.md) for endpoint details
3. Review [`DATABASE-ARCHITECTURE.md`](docs/technical/DATABASE-ARCHITECTURE.md) for critical decisions

### For Business Planning
1. Read [`PROJECT_VISION.md`](PROJECT_VISION.md) for platform philosophy
2. Check [`business-framework.md`](docs/business/business-framework.md) for business model
3. Review [`content-policy.md`](docs/business/content-policy.md) for moderation approach

## Project Overview

Lumen is a professional photography platform with:
- **No ads** - Clean, distraction-free experience
- **No algorithms** - Chronological, user-controlled discovery
- **Uncensored artistic expression** - Support for professional photography
- **People-first discovery** - Find photographers/models, not just images
- **Subscription model** - $5-150/year, no data exploitation

## Technology Stack

- **Backend**: FastAPI 0.104.1 (Python 3.11.x)
- **Frontend**: PWA with vanilla JavaScript
- **Database**: PostgreSQL via Cloud SQL
- **Authentication**: Firebase Admin SDK
- **Storage**: Google Cloud Storage
- **Infrastructure**: Google Cloud Platform

## Current Status

### ✅ Working Features
- Complete user registration and authentication
- Photo upload and management pipeline
- User profiles with photographer/model support
- Discovery feeds and search functionality
- Like system and social features

### 🚧 In Progress
- Swiss VPS migration planning
- Performance optimization
- Advanced geographic search
- Mobile PWA improvements

### 📋 Next Priorities
1. Execute Swiss VPS migration (see [`README1st-13aug2025.md`](README1st-13aug2025.md))
2. Performance optimization (caching, CDN)
3. Advanced search implementation
4. Payment system integration

## Contributing

This project uses AI-assisted development with:
- **Claude Code**: Technical implementation lead
- **Claude Desktop**: Systems architect
- **Gemini CLI**: GCP/Firebase specialist

Always check [`SHARED-STATUS.md`](SHARED-STATUS.md) for current coordination status.

---

For detailed information, explore the documentation structure above.