# Core Documentation - Single Sources of Truth

**These files are permanent and authoritative. They define the Lumen project.**

## Architecture & Design
- **TECH_STACK.md** - All technology choices in one place (CONSULT FIRST)
- **ARCHITECTURE_SUMMARY.md** - High-level PMM architecture overview
- **ARCHITECTURE.md** - Detailed technical architecture

## Implementation Guides
- **FRONTEND.md** - Frontend implementation with PMM pattern
- **API.md** - Backend API specification
- **features.md** - Complete feature roadmap

## Operations
- **DEVELOPMENT.md** - Local development setup
- **DEPLOYMENT.md** - Production deployment procedures

## Critical Rules

1. **These files are the truth** - If there's a conflict, these files win
2. **No build tools** - PMM pattern only
3. **Files under 400 lines** - LLM compatibility
4. **Global namespace** - window.Lumen*

## Quick Answers

**What framework?** None - Vanilla JS with PMM  
**What CSS framework?** None - Glass morphism custom CSS  
**What gallery?** justifiedGallery + lightGallery  
**What auth?** Firebase OAuth only  
**What backend?** FastAPI + PostgreSQL 16  
**What server?** Swiss EDIS VPS  
**Build process?** NONE - Direct file serving  

---

*If it's not in /core/, it's not core truth.*