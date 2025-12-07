# Lumen Architecture Summary - Poor Man's Modules Pattern

## Overview

Lumen is a professional photography platform built with vanilla JavaScript using a "Poor Man's Modules" pattern - global namespace objects providing modularity without build tools. Deployed on a Swiss VPS for data sovereignty and legal compliance.

## Quick Start for Development

- **Frontend**: Vanilla JavaScript with global modules (window.Lumen*)
- **Gallery**: justifiedGallery 3.8.1 + lightGallery 2.8.3
- **Backend**: FastAPI 0.104.1 + Python 3.11.x
- **Database**: PostgreSQL 16 with hybrid relational/JSONB schema
- **Auth**: Firebase Auth with JWT tokens (OAuth only)
- **Storage**: Local development storage (production uses `/var/www/lumen/storage/`)
- **Deployment**: Swiss EDIS VPS (83.172.136.127)
- **NO BUILD TOOLS**: Direct file serving, immediate refresh

## Architecture Pattern: Poor Man's Modules

### Why This Pattern?

- **No Build Process**: Edit, save, refresh - that's it
- **LLM-Friendly**: All files under 400 lines
- **Simple Debugging**: Everything visible in window object
- **Easy Testing**: Direct console access to all modules
- **Portable**: Copy modules to any project

### Module Structure3

```javascript
// Each module is a global object
window.LumenConfig = { /* configuration */ };
window.LumenAuth = { /* authentication */ };
window.LumenAPI = { /* API wrapper */ };
window.LumenGallery = { /* photo gallery */ };
window.LumenUpload = { /* upload handler */ };
window.LumenProfile = { /* user profiles */ };
window.LumenRouter = { /* routing */ };
window.LumenUtils = { /* utilities */ };
window.LumenTemplates = { /* HTML templates */ };
```

## Technology Stack

### Frontend

- **Pattern**: Poor Man's Modules (global namespace objects)
- **Language**: Vanilla JavaScript (no ES6 modules)
- **Gallery**: justifiedGallery for layout, lightGallery for viewing
- **Auth**: Firebase 10.7.0 via CDN (OAuth only)
- **Styling**: Glass morphism CSS with dark theme
- **Fonts**: Montserrat (headings), Roboto (body)
- **Build**: NONE - direct file serving

### Backend

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn ASGI with 2 workers
- **Language**: Python 3.11.x
- **Process Manager**: systemd
- **Cache**: Redis 6+
- **Web Server**: Nginx (reverse proxy)

### Database

- **Primary**: PostgreSQL 16
- **Schema**: Hybrid relational + JSONB
- **Migrations**: Alembic
- **ORM**: SQLAlchemy 2.0.23

### Infrastructure

- **Host**: EDIS Swiss VPS
- **IP**: 83.172.136.127
- **Storage**: Local filesystem (no cloud)
- **Cost**: €19.90/month
- **Security**: UFW firewall, Fail2Ban

## File Structure (All Files Under 400 Lines)

```
frontend/
├── index.html                 # Main HTML (150 lines max)
├── css/
│   ├── base.css              # Variables, typography (150 lines)
│   ├── glass.css             # Glass morphism (200 lines)
│   ├── components.css        # UI components (250 lines)
│   ├── layout.css            # Grid, responsive (200 lines)
│   └── gallery.css           # Gallery styles (150 lines)
├── js/
│   ├── config.js             # Configuration (50 lines)
│   ├── modules/
│   │   ├── auth.js           # Firebase auth (300 lines)
│   │   ├── api.js            # API wrapper (250 lines)
│   │   ├── gallery.js        # Photo gallery (400 lines)
│   │   ├── upload.js         # Upload handler (350 lines)
│   │   ├── profile.js        # Profile CRUD (350 lines)
│   │   ├── router.js         # View routing (200 lines)
│   │   └── utils.js          # Utilities (150 lines)
│   └── app.js                # Main coordinator (200 lines)
├── templates/
│   └── templates.js          # HTML templates (400 lines)
├── manifest.json             # PWA manifest
└── sw.js                     # Service worker
```

## Core Architecture Principles

### 1. Simplicity First

- No build tools, no transpilation
- Direct browser execution
- Refresh to see changes
- Console access to everything

### 2. Privacy & Compliance

- Swiss hosting for legal protection
- Local storage only (no cloud scanning)
- Complete data sovereignty
- GDPR compliant architecture

### 3. Design Philosophy

- **Glass Morphism UI**: Dark theme (#0A0A0A) with backdrop blur
- **Typography**: Montserrat + Roboto (no Comic Sans!)
- **Responsive**: Mobile-first design
- **Professional**: Gallery-focused experience

### 4. Performance

- CDN for external libraries
- Lazy loading with Intersection Observer
- Image variants (thumb, small, medium, large, original)
- Module-level state caching

### 5. Security

- Firebase Auth with JWT validation
- CORS with credentials on all requests
- Role-based access control
- No sensitive data in localStorage

## Key System Components

### Frontend Modules

```javascript
// Configuration
window.LumenConfig = {
    api: { baseURL: 'http://100.106.201.33:8080/api' },
    firebase: { /* OAuth config */ },
    gallery: { itemsPerPage: 20, rowHeight: 200 }
};

// Authentication
window.LumenAuth = {
    user: null,
    token: null,
    signIn(), signOut(), getToken()
};

// API Wrapper (with CORS fix)
window.LumenAPI = {
    request(endpoint, options) {
        // CRITICAL: Always include credentials
        options.credentials = 'include';
    }
};

// Gallery with justifiedGallery + lightGallery
window.LumenGallery = {
    initJustifiedGallery(),
    initLightGallery()
};
```

### API Endpoints

```
/api/auth/*    - Authentication
/api/photos/*  - Photo CRUD operations
/api/series/*  - Collections management
/api/users/*   - User profiles
/api/search/*  - Content search
```

### Database Tables

```sql
users (firebase_uid PRIMARY KEY)
photos (id, user_id, metadata JSONB)
series (id, user_id, settings JSONB)
photo_collaborators
photo_likes, photo_comments
```

## Development Workflow

### No Build Process!

```bash
# Frontend - Just serve files
cd frontend
python -m http.server 8000
# Open http://localhost:8000

# Backend
cd backend
uvicorn app.main:app --reload --port 8080
```

### Testing in Browser Console

```javascript
// Access any module directly
LumenAuth.user
LumenGallery.photos
await LumenAPI.get('/photos')

// Test functionality
LumenRouter.navigate('gallery')
LumenGallery.loadPhotos()
```

### Adding Features

1. Create module file (max 400 lines)
2. Add to index.html script tags
3. Refresh browser
4. Test in console

## Common Issues & Solutions

### CORS Errors

**Always** include `credentials: 'include'` in fetch:

```javascript
fetch(url, {
    credentials: 'include',  // CRITICAL!
    headers: { 'Authorization': `Bearer ${token}` }
})
```

### Module Not Found

Check script load order in index.html:

```html
<!-- Order matters! -->
<script src="js/config.js"></script>
<script src="js/modules/utils.js"></script>
<script src="js/modules/auth.js"></script>
<script src="js/modules/api.js"></script>
<!-- ... etc -->
```

### Gallery Not Rendering

Ensure jQuery loads before justifiedGallery:

```html
<script src="jquery.min.js"></script>
<script src="justifiedGallery.min.js"></script>
```

## Migration from Current Stack

### From Alpine.js Monolith (current index.html)

1. Extract Alpine x-data to module state
2. Convert x-show/x-if to vanilla JS
3. Replace @click with addEventListener
4. Move templates to templates.js

### Code to Reuse

- `frontend-deprecated/js/app.js` - Firebase auth logic
- `frontend-v2-vite-deprecated/src/glass-theme.css` - Glass styles
- Current `index.html` - API endpoints and logic

## Key Features

### For Photographers

- Portfolio management with series/collections
- Privacy controls (public/private)
- High-quality image preservation
- Glass morphism professional aesthetic
- Fast, responsive gallery

### For Models

- Profile showcase
- Photographer connections
- Portfolio curation
- Location preferences
- Booking availability

### Technical Features

- No build tools required
- Direct browser debugging
- Module pattern scales to 50+ modules
- Each file readable by LLMs
- Instant development feedback

## Important Notes

1. **NO BUILD TOOLS**: This is intentional - simplicity over complexity
2. **Global Namespace**: All modules under window.Lumen*
3. **File Size Limit**: 400 lines max per file
4. **Glass Morphism**: Dark, sophisticated design
5. **Local Storage**: All data on Swiss VPS
6. **Firebase**: Auth only, not full Firebase
7. **CORS Fix**: Always use credentials: 'include'

## Related Documentation

- [FRONTEND.md](./FRONTEND.md) - Frontend implementation details
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed architecture
- [DEVELOPMENT.md](./DEVELOPMENT.md) - Development guidelines
- [MODULAR_IMPLEMENTATION_PLAN_2025-09-07.md](./MODULAR_IMPLEMENTATION_PLAN_2025-09-07.md) - Implementation plan
- [CLAUDE_CODE_INSTRUCTIONS.md](./CLAUDE_CODE_INSTRUCTIONS.md) - Instructions for Claude Code

## Why This Architecture?

After trying ES6 modules (CORS issues), React (too complex), and Alpine.js (829-line monolith), we chose this pattern because:

1. **It works** - Proven pattern from jQuery era
2. **It's simple** - No toolchain to break
3. **It's debuggable** - Everything in window object
4. **It's LLM-friendly** - Small, focused files
5. **It's fast** - No build step, instant refresh

This is professional software built with startup simplicity.

---

**Current Status**: Documentation updated, ready for implementation with Claude Code