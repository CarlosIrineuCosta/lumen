# claudesk-tasks.md - Lumen Development Task Coordination

## Purpose
This document coordinates tasks between Claude instances to avoid overlap and confusion when working on Lumen development.

## Current Development State (As of Today)
- **Backend**: L:/projects/wasenet/lumen-gcp/backend (FastAPI)
- **Frontend**: L:/projects/wasenet/lumen-gcp/frontend (Vanilla JS)
- **Specs**: L:/projects/wasenet/docs/specs-ago02/
- **Main Issue**: Authentication system broken (registration/login flow)

## Active Work Streams

### Stream 1: Authentication Fix (CRITICAL)
**Status**: In Progress
**Owner**: [Assign to specific Claude instance]
**Tasks**:
1. Fix registration flow completion
2. Fix login state persistence  
3. Fix JWT token validation
4. Test full auth cycle

### Stream 2: Database Migration
**Status**: Planning
**Owner**: [Assign to specific Claude instance]
**Tasks**:
1. Design PostgreSQL schema
2. Migrate from in-memory storage
3. Update all API endpoints
4. Test data persistence

### Stream 3: Photo Discovery
**Status**: Not Started
**Owner**: [Assign to specific Claude instance]
**Tasks**:
1. Implement recent photos feed
2. Add pagination
3. Create photo interaction system
4. Build discovery API

### Stream 4: UI/UX Implementation
**Status**: Documented, Not Implemented
**Owner**: [Assign to specific Claude instance]
**Tasks**:
1. Implement mosaic grid gallery
2. Add NSFW toggle system
3. Build calendar/availability UI
4. Create connection request flow

## Completed Today

### By Main Claude:
- ✅ Created lumen_ui_ux_specifications.md
- ✅ Created lumen_security_infrastructure_addendum.md  
- ✅ Created lumen_business_framework_updated.md
- ✅ Created lumen_premium_pricing_strategy.md
- ✅ Analyzed competitor platforms (Model Mayhem, 500px)
- ✅ Defined privacy tiers and professional features

### By Code Claude:
- [To be filled in after sync]

## Tomorrow's Priorities

### Sanity Check Meeting
1. Review Code's progress
2. Sync on authentication fixes
3. Decide on immediate priorities
4. Assign clear ownership

### Critical Path
1. **Fix Auth** (blocks everything)
2. **Database Migration** (enables persistence)
3. **Photo Discovery** (core feature)
4. **Payment Integration** (revenue)

## Task Assignment Rules

### To Avoid Conflicts:
1. Only one Claude works on a file at a time
2. Clear ownership of features/modules
3. Document changes in this file
4. Use git commits with clear messages

### Communication Protocol:
- Update this file when starting work
- Note blockers immediately
- Request handoff explicitly
- Document completion status

## Current Blockers

### Technical:
- Authentication system broken
- No persistent storage
- No photo discovery API

### Business:
- Need Stripe account setup
- Need legal entity formation
- Need terms of service draft

## Environment Info

### Development Access:
- Linux Dev Box: 100.106.201.33:8080 (Tailscale)
- Frontend: http://localhost:8000
- Backend: http://localhost:8080

### Key Files:
- Backend entry: app/main.py
- Frontend entry: index.html
- Auth logic: app/auth.py
- Database (future): app/database.py

## Version Control

### Git Strategy:
- Main branch: stable code only
- Feature branches for major work
- Commit often with clear messages
- Pull before starting work

## Notes for Tomorrow

1. Check if Code has local changes not committed
2. Decide on PostgreSQL vs Cloud SQL
3. Plan the auth fix approach
4. Set realistic deadlines

---

*Update this file throughout development to maintain coordination*