# Lumen Development Documentation - Poor Man's Modules Pattern

# Development Overview

This document provides comprehensive guidelines for developing the Lumen photography platform using the Poor Man's Modules pattern - a simple, build-free approach using global namespace objects.

# Technology Stack

## Frontend Architecture (Poor Man's Modules)
- **Vanilla JavaScript** - No ES6 modules, no build tools
- **Global Namespace Pattern** - All modules under window.Lumen*
- **justifiedGallery 3.8.1** - Professional photo grid layout
- **lightGallery 2.8.3** - Touch-enabled photo viewer
- **Firebase 10.7.0** - Authentication via CDN
- **Glass Morphism CSS** - Custom dark theme
- **No Build Process** - Direct file serving

## Backend Stack
- **FastAPI 0.104.1** + Python 3.11.x
- **PostgreSQL 16** + Redis 6+
- **SQLAlchemy 2.0.23** (ORM)
- **Alembic** (migrations)
- **Firebase Admin SDK**
- **Uvicorn** (ASGI server)

# Local Development Setup

## Prerequisites
- **Python 3.11.x** for backend
- **PostgreSQL 16** for database
- **Redis 6+** for caching (optional in dev)
- **Git** for version control
- **Any static file server** for frontend

**No Node.js/npm Required** - Frontend uses CDN dependencies

## Initial Setup

## 1. Clone Repository
```bash
git clone https://github.com/yourusername/lumen.git
cd lumen
```

## 2. Frontend Setup (No Build Tools)
```bash
cd frontend

# Verify file structure
ls -la
# Expected structure:
# index.html
# css/
#   base.css, glass.css, components.css, layout.css, gallery.css
# js/
#   config.js
#   app.js
#   modules/
#     auth.js, api.js, gallery.js, upload.js, profile.js, router.js, utils.js
# templates/
#   templates.js

# Start any static server:

# Option 1: Python (recommended)
python -m http.server 8000

# Option 2: PHP
php -S localhost:8000

# Option 3: If you have Node.js
npx http-server -p 8000 -c-1

# Frontend available at http://localhost:8000
```

## 3. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://lumen_dev:password@localhost/lumen_development
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=development-secret-key-change-in-production
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-key.json
STORAGE_PATH=./storage
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=["http://localhost:8000","http://100.106.201.33:8000"]
EOF

# Run database migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

# Module Development Guide

## Creating a New Module

## Step 1: Create Module File
Create a new file in `js/modules/` (max 400 lines):

```javascript
// js/modules/example.js

/**
 * Module: LumenExample
 * Purpose: Example functionality
 * Dependencies: LumenAuth, LumenAPI
 * Events Dispatched: example-loaded, example-error
 * Max Lines: 400
 */

window.LumenExample = {
    // Module state
    data: null,
    loading: false,
    
    // Initialization
    init() {
        console.log('LumenExample initialized');
        this.setupEventListeners();
    },
    
    // Setup event listeners
    setupEventListeners() {
        document.addEventListener('auth-changed', (e) => {
            if (e.detail.user) {
                this.onUserAuthenticated(e.detail.user);
            }
        });
    },
    
    // Public methods
    async loadData() {
        if (this.loading) return;
        
        this.loading = true;
        LumenUtils.showLoading();
        
        try {
            this.data = await LumenAPI.get('/example');
            this.render();
            this.dispatch('example-loaded', this.data);
        } catch (error) {
            console.error('Failed to load example:', error);
            LumenUtils.showError('Failed to load data');
            this.dispatch('example-error', error);
        } finally {
            this.loading = false;
            LumenUtils.hideLoading();
        }
    },
    
    // Render to DOM
    render() {
        const container = document.getElementById('content');
        container.innerHTML = LumenTemplates.example(this.data);
    },
    
    // Event dispatcher helper
    dispatch(eventName, detail) {
        document.dispatchEvent(new CustomEvent(eventName, { detail }));
    },
    
    // Cleanup
    destroy() {
        this.data = null;
        this.loading = false;
    }
};
```

## Step 2: Add to index.html
Add script tag in correct load order:

```html
<!-- After other modules, before app.js -->
<script src="js/modules/example.js"></script>
```

## Step 3: Register Route (if needed)
In `js/modules/router.js` or `js/app.js`:

```javascript
LumenRouter.register('example', () => {
    if (LumenAuth.requireAuth()) {
        LumenExample.loadData();
    }
});
```

## Step 4: Add Template
In `templates/templates.js`:

```javascript
window.LumenTemplates.example = function(data) {
    return `
        <div class="example-container glass-card">
            <h2 class="font-display">Example</h2>
            <div class="example-content">
                ${data ? data.map(item => `
                    <div class="example-item">
                        ${item.name}
                    </div>
                `).join('') : 'No data'}
            </div>
        </div>
    `;
};
```

# Module Communication Patterns

## Pattern 1: Direct Method Calls
```javascript
// Module A calls Module B directly
window.LumenModuleA = {
    doSomething() {
        const token = LumenAuth.getToken();
        if (token) {
            LumenModuleB.processWithToken(token);
        }
    }
};
```

## Pattern 2: Custom Events
```javascript
// Module A dispatches event
window.LumenModuleA = {
    updateData(data) {
        this.data = data;
        document.dispatchEvent(new CustomEvent('data-updated', {
            detail: { data }
        }));
    }
};

// Module B listens for event
window.LumenModuleB = {
    init() {
        document.addEventListener('data-updated', (e) => {
            this.handleDataUpdate(e.detail.data);
        });
    }
};
```

## Pattern 3: Shared State
```javascript
// Modules can read each other's public state
window.LumenModuleA = {
    checkOtherModule() {
        if (LumenAuth.user && LumenGallery.photos.length > 0) {
            this.enableFeature();
        }
    }
};
```

# Development Workflow

## File Watchers Not Needed
Since there's no build process, changes are immediate:

1. Edit any file
2. Save the file
3. Refresh browser (F5)
4. Changes are live

# Browser Developer Tools

## Console Access to Modules
```javascript
// Test any module directly in console
LumenAuth.user
LumenGallery.photos
LumenAPI.get('/photos')
LumenRouter.navigate('profile')
```

## Debugging
```javascript
// Set breakpoints in module methods
window.LumenGallery.loadPhotos = function() {
    debugger; // Breakpoint here
    // Original method code
};
```

## Performance Monitoring
```javascript
// Measure module performance
console.time('Gallery Load');
await LumenGallery.loadPhotos();
console.timeEnd('Gallery Load');
```

# Testing Modules

## Manual Testing Checklist
```javascript
// Run these in browser console

// 1. Check all modules loaded
console.log('Modules loaded:', Object.keys(window).filter(k => k.startsWith('Lumen')));

// 2. Test authentication
await LumenAuth.signIn();
console.log('User:', LumenAuth.user);

// 3. Test API
const photos = await LumenAPI.get('/photos');
console.log('Photos:', photos);

// 4. Test gallery
LumenGallery.show();

// 5. Test routing
LumenRouter.navigate('profile');
```

## Simple Test Runner
Create `test.html` for module testing:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Lumen Module Tests</title>
</head>
<body>
    <div id="results"></div>
    
    <!-- Load all modules -->
    <script src="js/config.js"></script>
    <script src="js/modules/utils.js"></script>
    <script src="js/modules/auth.js"></script>
    <script src="js/modules/api.js"></script>
    
    <script>
        const tests = {
            'Config exists': () => {
                console.assert(window.LumenConfig, 'Config not found');
                console.assert(window.LumenConfig.api.baseURL, 'API URL not configured');
            },
            
            'Auth module exists': () => {
                console.assert(window.LumenAuth, 'Auth module not found');
                console.assert(typeof LumenAuth.signIn === 'function', 'signIn not a function');
            },
            
            'API module exists': () => {
                console.assert(window.LumenAPI, 'API module not found');
                console.assert(typeof LumenAPI.get === 'function', 'get not a function');
            }
        };
        
        // Run tests
        let passed = 0, failed = 0;
        for (const [name, test] of Object.entries(tests)) {
            try {
                test();
                console.log('✓', name);
                passed++;
            } catch (error) {
                console.error('✗', name, error);
                failed++;
            }
        }
        
        document.getElementById('results').textContent = 
            `Tests: ${passed} passed, ${failed} failed`;
    </script>
</body>
</html>
```

# Common Development Tasks

## Adding a New View/Page

1. Create template in `templates/templates.js`:
```javascript
window.LumenTemplates.newView = function(data) {
    return `<div class="new-view">...</div>`;
};
```

2. Create module in `js/modules/newview.js`:
```javascript
window.LumenNewView = {
    show() {
        document.getElementById('content').innerHTML =
            LumenTemplates.newView(this.data);
    }
};
```

3. Register route:
```javascript
LumenRouter.register('newview', () => LumenNewView.show());
```

4. Add navigation link:
```html
<a href="#newview">New View</a>
```

# Working with the Gallery

## Refresh Gallery
```javascript
// After uploading a photo
await LumenGallery.loadPhotos();
LumenGallery.initJustifiedGallery();
```

## Add Filter
```javascript
// Extend gallery module
LumenGallery.filterByTag = function(tag) {
    const filtered = this.photos.filter(p => p.tags.includes(tag));
    this.renderPhotos(filtered);
};
```

# API Development

## Adding New API Endpoint
```javascript
// In js/modules/api.js
window.LumenAPI.newEndpoint = async function(data) {
    return this.post('/new-endpoint', data);
};
```

## Handling API Errors
```javascript
// Consistent error handling
try {
    const result = await LumenAPI.someCall();
} catch (error) {
    if (error.status === 401) {
        // Auth error - redirect to login
        LumenAuth.signIn();
    } else if (error.status === 404) {
        LumenUtils.showError('Not found');
    } else {
        LumenUtils.showError('Something went wrong');
    }
}
```

# CSS Development

## Adding Glass Components
```css
/* In css/glass.css */
.glass-new-component {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: 8px;
    padding: 1rem;
}
```

## Responsive Design
```css
/* In css/layout.css */
@media (max-width: 768px) {
    .gallery-grid {
        column-count: 2;
    }
}

@media (max-width: 480px) {
    .gallery-grid {
        column-count: 1;
    }
}
```

# Troubleshooting

## Module Not Defined
**Error**: `Uncaught ReferenceError: LumenModule is not defined`
**Solution**: Check script load order in index.html

## CORS Errors
**Error**: `CORS policy: No 'Access-Control-Allow-Origin'`
**Solution**: Ensure `credentials: 'include'` in all fetch calls

## Gallery Not Rendering
**Error**: Gallery loads but doesn't display
**Solution**: Check jQuery is loaded before justifiedGallery

## Auth Token Missing
**Error**: API returns 401 Unauthorized
**Solution**: Wait for auth initialization:
```javascript
document.addEventListener('auth-ready', () => {
    // Now safe to make API calls
});
```

# Performance Tips

## Module Loading
- Load critical modules first (config, auth, api)
- Defer non-critical modules
- Use async for independent modules

## DOM Manipulation
- Batch DOM updates
- Use DocumentFragment for multiple elements
- Cache DOM queries in module state

## API Calls
- Implement request debouncing
- Cache responses in module state
- Use pagination for large datasets

# Production Deployment

## Pre-deployment Checklist
- [ ] Remove console.log statements
- [ ] Optimize CSS variables for production
- [ ] Update API URLs in config.js
- [ ] Test all glass modules in production mode
- [ ] Verify CORS configuration with credentials: 'include'
- [ ] Check Firebase configuration
- [ ] Test glass morphism effects across browsers
- [ ] Verify service worker registration

## Deployment Steps
```bash
# 1. Copy files to server
scp -r frontend/* user@server:/var/www/lumen/frontend/

# 2. No build step needed!
# All files served directly

# 3. Verify permissions
ssh user@server
chmod -R 755 /var/www/lumen/frontend

# 4. Test in production
curl -I https://yourdomain.com
```

## Glass Morphism Production Notes
- CSS variables are injected by glass-config-loader.js
- Backdrop filters may need vendor prefixes for older browsers
- Test glass effects on target browsers before deployment
- Consider fallback for browsers without backdrop-filter support

---

This development approach prioritizes simplicity, maintainability, and developer experience. No build tools means less complexity and faster development cycles.