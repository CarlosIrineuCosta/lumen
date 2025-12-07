# Lumen Frontend Documentation - Poor Man's Modules Architecture

## Technology Stack

### Core Architecture
- **Poor Man's Modules Pattern** - Global namespace objects (window.Lumen*)
- **Vanilla JavaScript** - No ES6 modules, no build tools required
- **justifiedGallery 3.8.1** - Professional photo grid layout
- **lightGallery 2.8.3** - Professional photo viewer with gestures
- **Glass Morphism Design System** - Custom CSS utilities for sophisticated aesthetics
- **Firebase 10.7.0** - Authentication and user management (OAuth only)
- **CDN Dependencies** - All libraries served via CDN links

### Why Poor Man's Modules
- **Simplicity**: No build process, no module bundlers
- **LLM-Friendly**: Files under 400 lines for AI assistance
- **Debugging**: Everything visible in window object
- **Compatibility**: Works in all modern browsers
- **Portability**: Modules easily copied to other projects

## Module Architecture

### Global Namespace Pattern
All modules are attached to the window object under the `Lumen` namespace:

```javascript
window.LumenConfig = { /* configuration */ };
window.LumenAuth = { /* authentication module */ };
window.LumenAPI = { /* API wrapper module */ };
window.LumenGallery = { /* gallery module */ };
window.LumenUpload = { /* upload module */ };
window.LumenProfile = { /* profile module */ };
window.LumenRouter = { /* routing module */ };
window.LumenUtils = { /* utility functions */ };
window.LumenTemplates = { /* HTML templates */ };
```

### File Structure (Max 400 Lines Per File)
```
frontend/
├── index.html                 # Main HTML (150 lines max)
├── css/
│   ├── base.css              # Variables, typography (150 lines)
│   ├── glass.css             # Glass morphism system (200 lines)
│   ├── components.css        # Reusable components (250 lines)
│   ├── layout.css            # Grid, responsive (200 lines)
│   └── gallery.css           # Gallery-specific styles (150 lines)
├── js/
│   ├── config.js             # Configuration (50 lines)
│   ├── modules/
│   │   ├── auth.js           # Firebase auth (300 lines)
│   │   ├── api.js            # API wrapper (250 lines)
│   │   ├── gallery.js        # Photo gallery (400 lines)
│   │   ├── upload.js         # Upload handler (350 lines)
│   │   ├── profile.js        # Profile CRUD (350 lines)
│   │   ├── router.js         # View routing (200 lines)
│   │   └── utils.js          # Shared utilities (150 lines)
│   └── app.js                # Main coordinator (200 lines)
├── templates/
│   └── templates.js          # All HTML templates (400 lines)
├── manifest.json             # PWA manifest
├── sw.js                     # Service worker
└── serve.py                  # Development server
```

## Design System

### Glass Morphism Aesthetic
The design follows a sophisticated glass-inspired dark theme:

```css
:root {
    /* Base Colors - NO pastels, sophisticated palette */
    --bg-primary: #0a0a0a;        /* Deep black background */
    --bg-secondary: #1a1a2e;       /* Dark surface */
    --text-primary: #e0e0e0;       /* Light text */
    --text-secondary: #a0a0a0;     /* Muted text */
    --accent: #667eea;             /* Indigo accent */
    
    /* Glass Effects */
    --glass-bg: rgba(17, 25, 40, 0.75);
    --glass-bg-light: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.125);
    --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    --glass-blur: blur(16px);
}
```

### Typography System
```css
/* Font Stack - Sophisticated, not trivial */
--font-display: 'Montserrat', sans-serif;  /* Headings */
--font-body: 'Roboto', sans-serif;         /* Body text */

/* No Comic Sans, Papyrus, or other trivial fonts */
```

### Glass Components
```css
/* Core Glass Classes */
.glass, .glass-card {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur) saturate(180%);
    -webkit-backdrop-filter: var(--glass-blur) saturate(180%);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    box-shadow: var(--glass-shadow);
}

.glass-nav {
    background: rgba(10, 10, 10, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--glass-border);
}

.glass-hover {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-hover:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.45);
}
```

## Module Implementation Guide

### 1. Configuration Module (js/config.js)
```javascript
window.LumenConfig = {
    api: {
        baseURL: 'http://100.106.201.33:8080/api',
        timeout: 10000
    },
    firebase: {
        apiKey: "AIzaSyCt8ERvmCTaV5obZHBTqOAOSCMTq-v16nE",
        authDomain: "lumen-photo-app-20250731.firebaseapp.com",
        projectId: "lumen-photo-app-20250731"
    },
    gallery: {
        itemsPerPage: 20,
        rowHeight: 200,
        margins: 5
    }
};
```

### 2. Authentication Module (js/modules/auth.js)
```javascript
window.LumenAuth = {
    user: null,
    token: null,
    
    init() {
        // Initialize Firebase
        // Set up auth state listener
        // Dispatch custom events
    },
    
    async signIn() {
        // Google OAuth flow
    },
    
    async signOut() {
        // Clear auth state
    },
    
    getToken() {
        return this.token;
    },
    
    isAuthenticated() {
        return !!this.user;
    }
};
```

### 3. API Module with CORS Fix (js/modules/api.js)
```javascript
window.LumenAPI = {
    async request(endpoint, options = {}) {
        const config = {
            ...options,
            credentials: 'include', // CRITICAL for CORS
            headers: {
                'Authorization': `Bearer ${LumenAuth.getToken()}`,
                ...options.headers
            }
        };
        
        return fetch(`${LumenConfig.api.baseURL}${endpoint}`, config);
    }
};
```

### 4. Gallery Module (js/modules/gallery.js)
```javascript
window.LumenGallery = {
    photos: [],
    lgInstance: null,
    
    async show() {
        // Render gallery template
        // Load photos from API
        // Initialize justifiedGallery
        // Setup lightGallery
    },
    
    initJustifiedGallery() {
        $('#gallery-grid').justifiedGallery({
            rowHeight: LumenConfig.gallery.rowHeight,
            margins: LumenConfig.gallery.margins,
            lastRow: 'nojustify'
        });
    },
    
    initLightGallery() {
        this.lgInstance = lightGallery(document.getElementById('gallery-grid'), {
            plugins: [lgZoom, lgThumbnail],
            addClass: 'lg-glass-theme'
        });
    }
};
```

## Script Loading Order

The order is critical for proper initialization:

```html
<!-- External Libraries (CDN) -->
<script src="jquery.min.js"></script>
<script src="justifiedGallery.min.js"></script>
<script src="lightgallery.min.js"></script>
<script src="firebase-app-compat.js"></script>
<script src="firebase-auth-compat.js"></script>

<!-- Application Scripts (order matters!) -->
<script src="js/config.js"></script>
<script src="templates/templates.js"></script>
<script src="js/modules/utils.js"></script>
<script src="js/modules/auth.js"></script>
<script src="js/modules/api.js"></script>
<script src="js/modules/router.js"></script>
<script src="js/modules/gallery.js"></script>
<script src="js/modules/upload.js"></script>
<script src="js/modules/profile.js"></script>
<script src="js/app.js"></script>
```

## Inter-Module Communication

Modules communicate via:
1. **Direct Method Calls**: `LumenAuth.getToken()`
2. **Custom Events**: `document.dispatchEvent(new CustomEvent('auth-changed'))`
3. **Shared State**: Via window.Lumen* objects

Example:
```javascript
// Auth module dispatches event
document.dispatchEvent(new CustomEvent('auth-changed', { 
    detail: { user, token } 
}));

// Gallery module listens
document.addEventListener('auth-changed', (e) => {
    if (e.detail.user) {
        this.loadUserPhotos();
    }
});
```

## Development Workflow

### No Build Process Required
```bash
# Navigate to frontend
cd frontend

# Start any static file server
python -m http.server 8000
# OR
npx http-server -p 8000

# Open browser to http://localhost:8000
```

### Adding New Modules
1. Create file in `js/modules/` (max 400 lines)
2. Define global object: `window.LumenModuleName = { ... }`
3. Add script tag to index.html in correct position
4. Register routes if needed in router module

### Testing Checklist
- [ ] All scripts load without 404 errors
- [ ] No console errors on page load
- [ ] Authentication flow works
- [ ] Gallery displays photos
- [ ] justifiedGallery creates proper grid
- [ ] lightGallery opens on photo click
- [ ] Glass morphism effects visible
- [ ] CORS requests include credentials

## Common Pitfalls & Solutions

### CORS Errors
**Problem**: API calls fail with CORS errors
**Solution**: Always include `credentials: 'include'` in fetch options

### Module Not Found
**Problem**: `LumenModule is not defined`
**Solution**: Check script load order in index.html

### Gallery Not Rendering
**Problem**: Photos load but gallery is blank
**Solution**: Ensure jQuery loads before justifiedGallery

### File Too Large
**Problem**: Module exceeds 400 lines
**Solution**: Split into sub-modules or move templates out

## Performance Optimization

### Lazy Loading
- Load modules only when needed
- Use Intersection Observer for infinite scroll
- Defer non-critical scripts

### Caching Strategy
- Cache API responses in module state
- Use browser localStorage for user preferences
- Implement service worker for offline support

## Security Considerations

### Authentication
- Never store tokens in localStorage
- Use httpOnly cookies when possible
- Validate tokens on every API request

### XSS Prevention
- Sanitize all user input
- Use textContent instead of innerHTML
- Escape HTML in templates

### CORS Configuration
- Whitelist specific origins
- Include credentials only when necessary
- Validate origins on backend

## Browser Support

### Minimum Requirements
- Chrome 90+
- Firefox 89+
- Safari 14+
- Edge 90+

### Progressive Enhancement
- Core functionality works without JavaScript
- Enhanced features for modern browsers
- Graceful degradation for older browsers

---

This architecture provides a simple, maintainable, and performant solution without the complexity of modern build tools while maintaining professional standards.