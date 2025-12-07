# Lumen Architecture Documentation - Poor Man's Modules Pattern

# System Overview

Lumen is a professional photography platform built with vanilla JavaScript using a "Poor Man's Modules" pattern - global namespace objects that provide modularity without build tools. The system is deployed on a Swiss EDIS VPS for legal compliance and data sovereignty.

# Architecture Pattern: Poor Man's Modules

# Why This Pattern?
After evaluating ES6 modules, React, and monolithic approaches, we chose this pattern because:
- **No Build Tools**: Direct browser execution, no compilation
- **LLM-Compatible**: Files under 400 lines for AI assistance
- **Simple Debugging**: All modules visible in window object
- **Easy Testing**: Direct access to all functionality
- **Portable**: Modules can be copied to other projects

# Module Structure
```javascript
// Each module is a global object
window.LumenConfig = { /* configuration */ };
window.LumenAuth = { /* authentication */ };
window.LumenAPI = { /* API wrapper */ };
window.LumenGallery = { /* photo gallery */ };
window.LumenRouter = { /* routing */ };
window.LumenUtils = { /* utilities */ };
```

# Technology Stack

## Frontend Layer
- **Vanilla JavaScript** - No frameworks, no transpilation
- **Poor Man's Modules** - Global namespace pattern
- **justifiedGallery 3.8.1** - Professional photo grid
- **lightGallery 2.8.3** - Full-featured photo viewer
- **Firebase Auth 10.7.0** - OAuth authentication only
- **Glass Morphism CSS** - Custom dark theme aesthetics

## Backend Layer (Unchanged)
- **FastAPI 0.104.1** with Python 3.11.x
- **Uvicorn** ASGI server with 2 workers
- **SQLAlchemy 2.0.23** ORM with Alembic migrations
- **Firebase Admin SDK** for token validation
- **Pillow** for image processing
- **Redis** for caching and sessions

## Database Layer
- **PostgreSQL 16** as primary database
- **Hybrid approach**: Relational tables with JSONB fields
- **Connection pooling** for performance
- **Local connection** at localhost:5432

## Storage Layer
- **Local filesystem** storage on VPS
- **Path structure**: `/var/www/lumen/storage/photos/{user_id}/{photo_id}_{variant}.jpg`
- **Image variants**: original, large, medium, small, thumb
- **No cloud dependencies** for data sovereignty

# Component Architecture

## Frontend Modules

### Core Modules (Global Objects)
```javascript
// Configuration - js/config.js (426 lines)
window.LumenConfig = {
    app: { name, version, environment },
    api: { baseURL, endpoints, timeout },
    firebase: { apiKey, authDomain, projectId },
    gallery: { rowHeight, margins, lightbox },
    upload: { maxFileSize, acceptedFileTypes },
    ui: { animations, theme, layout },
    // ... extensive configuration
};

// Authentication - js/modules/auth.js (246 lines)
window.LumenAuth = {
    user: null,
    token: null,
    init(), signIn(), signOut(),
    getToken(), isAuthenticated(), requireAuth(),
    syncUserProfile(), handleOnboarding()
};

// API Wrapper - js/modules/api.js
window.LumenAPI = {
    request(), get(), post(), put(), delete(),
    getPhotos(), uploadPhoto(), getUserProfile(),
    // ... API endpoints
};

// Gallery - js/modules/gallery.js
window.LumenGallery = {
    photos: [],
    show(), loadPhotos(), renderPhotos(),
    initJustifiedGallery(), initLightGallery(),
    // ... gallery management
};

// Upload - js/modules/upload.js
window.LumenUpload = {
    files: [],
    init(), processFiles(), uploadFile(),
    showProgress(), handleError(),
    // ... upload handling
};

// Router - js/modules/router.js
window.LumenRouter = {
    routes: {},
    init(), register(), navigate(), handleRoute(),
    // ... routing logic
};

// UI Module - js/modules/ui.js
window.LumenUI = {
    showModal(), hideModal(), showToast(),
    showLoading(), hideLoading(),
    // ... UI helpers
};

// Utils - js/modules/utils.js
window.LumenUtils = {
    showError(), showSuccess(), showWarning(),
    formatDate(), sanitizeHTML(),
    // ... utility functions
};
```

### Template System
```javascript
// Templates - templates/templates.js
window.LumenTemplates = {
    nav(),           // Navigation bar
    gallery(),       // Gallery container
    upload(),        // Upload interface
    profile(user),   // Profile page
    photoCard(photo), // Photo card component
    authModal(),     // Authentication modal
    searchOverlay(), // Search overlay
    settingsModal(),  // Settings modal
    // ... all HTML templates
};
```

# Module Communication

## 1. Direct Method Calls
```javascript
// Modules call each other directly
const token = LumenAuth.getToken();
const photos = await LumenAPI.getPhotos();
```

## 2. Custom Events
```javascript
// Dispatch event from auth module
document.dispatchEvent(new CustomEvent('auth-changed', {
    detail: { user, token }
}));

// Listen in gallery module
document.addEventListener('auth-changed', (e) => {
    if (e.detail.user) {
        LumenGallery.loadUserPhotos();
    }
});
```

## 3. Shared State
```javascript
// Modules can read each other's state
if (LumenAuth.user) {
    LumenProfile.displayUser(LumenAuth.user);
}
```

# File Structure

```
frontend/
├── index.html                 # Main HTML (154 lines)
├── css/
│   ├── glassmorphism-core.css  # Glass morphism framework (1308 lines)
│   ├── base.css              # Variables, typography
│   ├── components.css        # UI components
│   ├── layout.css            # Grid, responsive
│   ├── gallery.css           # Gallery styles
│   ├── profile.css           # Profile-specific styles
│   └── responsive.css       # Media queries
├── js/
│   ├── config.js             # Configuration (426 lines)
│   ├── app.js               # Main coordinator (505 lines)
│   ├── glass-config-loader.js # Theme configuration
│   ├── templates.js          # HTML templates
│   ├── diagnostics.js        # Debugging tools
│   ├── i18n-helper.js       # Internationalization
│   └── modules/             # Poor Man's Modules
│       ├── auth.js           # Authentication (246 lines)
│       ├── api.js            # API wrapper
│       ├── gallery.js        # Photo gallery
│       ├── upload.js         # Upload handler
│       ├── profile.js        # Profile CRUD
│       ├── router.js         # View routing
│       ├── search.js         # Search functionality
│       ├── settings.js       # Settings management
│       ├── ui.js            # UI helpers
│       └── utils.js          # Utility functions
├── config/
│   └── glass-theme.js       # Glass morphism theme variables
├── templates/
│   └── templates.js         # HTML templates
├── i18n/                  # Internationalization
│   ├── en.js
│   ├── es.js
│   ├── fr.js
│   └── languages.js
├── manifest.json             # PWA manifest
├── sw.js                   # Service worker
└── assets/
    └── icons/               # PWA icons
```

# Data Flow

## Authentication Flow
```
1. User clicks "Sign In"
2. LumenAuth.signIn() → Firebase OAuth
3. Firebase returns user + token
4. LumenAuth stores user/token
5. Custom event 'auth-changed' dispatched
6. All modules update based on auth state
```

## Photo Loading Flow
```
1. LumenRouter navigates to gallery
2. LumenGallery.show() renders template
3. LumenAPI.getPhotos() fetches data
4. Photos rendered to DOM
5. justifiedGallery creates grid
6. lightGallery initialized for viewing
```

## Upload Flow
```
1. User selects files
2. LumenUpload validates files
3. LumenAPI.uploadPhoto() sends to backend
4. Backend processes and stores
5. Success response with photo data
6. Gallery refreshes to show new photo
```

# API Architecture

## Endpoint Structure
```
/api/auth/*       # Authentication endpoints
/api/photos/*     # Photo CRUD operations
/api/series/*     # Series/collection management
/api/users/*      # User profiles and settings
/api/search/*     # Content search
```

## CORS Configuration
```javascript
// Critical: All API calls must include credentials
fetch(url, {
    credentials: 'include',  // Required for CORS
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

# Security Architecture

## Frontend Security
- **No sensitive data in localStorage**
- **Tokens in memory only**
- **XSS prevention via textContent**
- **CORS credentials on all requests**

## Backend Security
- **JWT validation middleware**
- **Role-based access control**
- **SQL injection prevention via ORM**
- **File upload validation**

## Infrastructure Security
- **UFW firewall rules**
- **Fail2ban for brute force protection**
- **HTTPS only in production**
- **Swiss jurisdiction for privacy**

# Performance Architecture

## Frontend Optimization
- **Lazy loading with Intersection Observer**
- **Image variants for different sizes**
- **justifiedGallery for efficient layout**
- **Module-level caching**

## Backend Optimization
- **Redis caching layer**
- **Database connection pooling**
- **Async request handling**
- **Image processing queue**

## CDN Strategy
- **External libraries from CDN**
- **Local assets for critical path**
- **Service worker for offline support**

# Deployment Architecture

## Development Environment
```bash
# Frontend - No build needed
cd frontend
python -m http.server 8000

# Backend
cd backend
uvicorn app.main:app --reload --port 8080
```

## Production Environment
```bash
# Swiss EDIS VPS
IP: 83.172.136.127
Path: /var/www/lumen/

# Services
systemctl status lumen-backend
systemctl status nginx
systemctl status postgresql
systemctl status redis
```

# Database Schema

## Core Tables
```sql
-- Users (Firebase UID as primary key)
users (
    firebase_uid VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE,
    display_name VARCHAR,
    profile_data JSONB,
    created_at TIMESTAMP
)

-- Photos with metadata
photos (
    id UUID PRIMARY KEY,
    user_id VARCHAR REFERENCES users,
    title VARCHAR,
    metadata JSONB,
    upload_date TIMESTAMP
)

-- Series/Collections
series (
    id UUID PRIMARY KEY,
    user_id VARCHAR REFERENCES users,
    title VARCHAR,
    description TEXT,
    settings JSONB
)
```

# Module Development Guidelines

## Creating New Modules
1. **File Location**: `js/modules/modulename.js`
2. **Global Object**: `window.LumenModuleName = { ... }`
3. **Max Lines**: 400 lines per file
4. **Dependencies**: List in comments at top
5. **Events**: Document custom events

## Module Template
```javascript
/**
 * Module: LumenExample
 * Dependencies: LumenAuth, LumenAPI
 * Events: example-loaded, example-error
 */
window.LumenExample = {
    // State
    data: null,
    
    // Initialization
    init() {
        this.setupEventListeners();
    },
    
    // Public methods
    async load() {
        try {
            this.data = await LumenAPI.get('/example');
            this.dispatch('example-loaded', this.data);
        } catch (error) {
            this.dispatch('example-error', error);
        }
    },
    
    // Private methods (convention: prefix with _)
    _processData(data) {
        // Internal processing
    },
    
    // Event helpers
    dispatch(eventName, detail) {
        document.dispatchEvent(new CustomEvent(eventName, { detail }));
    },
    
    // Cleanup
    destroy() {
        // Remove listeners, clear state
    }
};
```

# Testing Strategy

## Manual Testing
- Open browser console
- Access modules directly: `LumenAuth.user`
- Call methods: `LumenGallery.loadPhotos()`
- Check network tab for API calls
- Verify CORS headers

## Automated Testing
```javascript
// Simple test runner
const tests = {
    'Auth module exists': () => {
        console.assert(window.LumenAuth, 'Auth module not found');
    },
    'API includes credentials': async () => {
        // Mock fetch and verify credentials: 'include'
    }
};
```

# Migration Path

## From Current Monolithic index.html
1. Extract Alpine.js logic to modules
2. Convert x-data to module state
3. Replace Alpine directives with vanilla JS
4. Move templates to templates.js
5. Test each module independently

## Future Considerations
- Could add TypeScript definitions for IDE support
- Could implement ES6 modules when needed
- Could add build step if complexity grows
- Pattern scales to dozens of modules

# EDIS Server Sync Requirements

**Status**: Pending implementation until stability returns

## Database Schema Changes to Sync
```sql
-- New tables/columns to sync when EDIS connection is stable
ALTER TABLE photos ADD COLUMN IF NOT EXISTS storage_path VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS edis_synced BOOLEAN DEFAULT FALSE;
ALTER TABLE series ADD COLUMN IF NOT EXISTS edis_synced BOOLEAN DEFAULT FALSE;

-- New sync tracking table
CREATE TABLE IF NOT EXISTS edis_sync_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    sync_status VARCHAR(20) NOT NULL, -- pending, success, failed
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP
);
```

## File Structure Changes to Sync
```
/var/www/lumen/storage/photos/{user_id}/{photo_id}_{variant}.jpg
/var/www/lumen/storage/backups/          # Database backups
/var/www/lumen/storage/logs/             # Sync logs
/var/www/lumen/config/production.env   # Production config
```

## Configuration Files to Sync
```bash
# Backend configuration
/var/www/lumen/backend/.env
/var/www/lumen/backend/alembic.ini
/var/www/lumen/backend/requirements.txt

# Nginx configuration
/etc/nginx/sites-available/lumen
/etc/nginx/nginx.conf

# System services
/etc/systemd/system/lumen-backend.service
/etc/systemd/system/lumen-celery.service
```

## Deployment Scripts to Sync
```bash
#!/bin/bash
# sync-to-edis.sh - Main deployment script

# 1. Database migration
alembic upgrade head

# 2. File synchronization
rsync -avz --delete ./storage/ edis:/var/www/lumen/storage/

# 3. Configuration updates
scp .env production edis:/var/www/lumen/backend/

# 4. Service restart
ssh edis "systemctl restart lumen-backend"
```

## Sync Priority Order
1. **Database schema** (critical - data integrity)
2. **User data** (photos, profiles, series)
3. **Configuration files** (environment, services)
4. **Static assets** (templates, CSS, JS)
5. **System services** (nginx, systemd)

---

This architecture provides enterprise-grade functionality with startup simplicity, prioritizing maintainability and developer experience over using the latest frameworks.