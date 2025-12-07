# Lumen Tech Stack - Quick Reference

**Architecture**: Poor Man's Modules (PMM) - Global namespace pattern
**Build Tools**: NONE - Direct file serving
**Deployment**: Swiss EDIS VPS (€19.90/month)

# Frontend

## Core
- **Pattern**: `window.Lumen*` global objects
- **Language**: Vanilla JavaScript (NO ES6 modules)
- **Framework**: NONE (no React, Vue, Alpine)
- **Max File Size**: 400 lines (LLM limit)

## Libraries (via CDN)
- **jQuery 3.7.1** - Required for gallery
- **justifiedGallery 3.8.1** - Photo grid layout
- **lightGallery 2.8.3** - Photo viewer
- **Firebase 10.7.0** - Auth only (OAuth)
- **FilePond 4.30.4** - File uploads (planned)
- **Masonry 4.0** - Grid layout system

## Design
- **CSS**: Custom Glass Morphism (glassmorphism-core.css)
- **Component Library**: Custom glass components (104+ components)
- **Fonts**: Montserrat (headings), Roboto (body)
- **Icons**: Lucide or Heroicons (via CDN)
- **Theme**: Dark (#0A0A0A background)
- **NO Tailwind/Alpine/Preline** (Custom implementation)

# Backend

## Core
- **FastAPI 0.104.1** - Web framework
- **Python 3.11.x** - Language
- **Uvicorn** - ASGI server (2 workers)
- **systemd** - Process manager

## Database
- **PostgreSQL 16** - Primary database
- **Redis 6+** - Caching/sessions
- **SQLAlchemy 2.0.23** - ORM
- **Alembic** - Migrations

## Libraries
- **Firebase Admin SDK** - Token validation
- **Pillow** - Image processing
- **python-multipart** - File uploads
- **pydantic** - Data validation

# Infrastructure

## Server
- **EDIS Global** - Swiss VPS
- **Location**: Zurich
- **IP**: 83.172.136.127
- **OS**: Ubuntu 22.04 LTS
- **Storage**: Local filesystem only

## Web Server
- **Nginx** - Reverse proxy
- **Certbot** - SSL certificates
- **UFW** - Firewall
- **Fail2Ban** - Security

# Critical Rules

## ALWAYS
✅ `credentials: 'include'` in fetch
✅ Global objects (`window.Lumen*`)
✅ Files under 400 lines
✅ Direct CDN links
✅ Local storage only

## NEVER
❌ ES6 modules (import/export)
❌ Build tools (Vite, Webpack)
❌ NPM/Node.js for frontend
❌ React, Vue, Angular
❌ Cloud storage (AWS, Firebase Storage)  

# Script Loading Order

```html
<!-- 1. Glass Morphism CSS -->
<link rel="stylesheet" href="css/glassmorphism-core.css">

<!-- 2. jQuery (required first for galleries) -->
<script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>

<!-- 3. Gallery libraries -->
<script src="https://unpkg.com/masonry-layout@4/dist/masonry.pkgd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/lightgallery@2.8.3/lightgallery.min.js"></script>

<!-- 4. Firebase -->
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-auth-compat.js"></script>

<!-- 5. File Upload -->
<script src="https://unpkg.com/filepond/dist/filepond.min.js"></script>
<script src="https://unpkg.com/filepond-plugin-image-preview/dist/filepond-plugin-image-preview.min.js"></script>

<!-- 6. Our modules (order matters!) -->
<script src="config/glass-theme.js"></script>
<script src="js/glass-config-loader.js"></script>
<script src="js/config.js"></script>
<script src="js/templates.js"></script>
<script src="js/modules/utils.js"></script>
<script src="js/modules/api.js"></script>
<script src="js/modules/auth.js"></script>
<script src="js/modules/ui.js"></script>
<script src="js/modules/router.js"></script>
<script src="js/modules/gallery.js"></script>
<script src="js/modules/upload.js"></script>
<script src="js/modules/profile.js"></script>
<script src="js/modules/settings.js"></script>
<script src="js/modules/search.js"></script>
<script src="js/app.js"></script>
```

# Glass Morphism Usage

```javascript
// Modal example with Glass Morphism
window.LumenProfile = {
    showEditModal() {
        // Glass modal HTML
        const modal = `
            <dialog id="edit-profile-modal" class="glass-modal">
                <div class="glass-modal-box">
                    <h3 class="glass-card-title">Edit Profile</h3>
                    <!-- Modal content -->
                    <div class="glass-modal-action">
                        <button class="glass-btn glass-btn-primary">Save</button>
                        <button class="glass-btn glass-btn-ghost">Cancel</button>
                    </div>
                </div>
            </dialog>
        `;

        // Show glass modal
        const modalElement = document.getElementById('edit-profile-modal');
        if (modalElement) {
            modalElement.classList.add('modal-open');
            modalElement.showModal();
        }
    }
};
```

# Development URLs

- **Frontend**: http://100.106.201.33:8000
- **Backend API**: http://100.106.201.33:8080
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

# File Structure

```
frontend/
├── index.html          (150 lines max)
├── css/               (all < 250 lines)
│   └── glass.css      (core glass morphism styles)
├── js/
│   ├── config.js      (50 lines)
│   └── modules/       (all < 400 lines)
└── templates/         (400 lines max)

backend/
├── app/
│   ├── api/          (endpoints)
│   ├── models/       (SQLAlchemy)
│   └── main.py       (FastAPI app)
└── requirements.txt
```

---

**One Rule**: If it needs a build step, we don't use it.  
**Exception**: None.
