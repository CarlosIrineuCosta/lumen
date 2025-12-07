# Lumen Frontend (Poor Man's Modules)

## Overview
This is the frontend for Lumen Photography Platform, built with:
- Poor Man's Modules (global namespace pattern)
- Custom Glass Morphism UI (104+ component library)
- Vanilla JavaScript (no build tools)
- Glass morphism design
- PWA support

## No Build Process Required! 🎉
Just open `index.html` in a browser or run the server.

## Quick Start

### 1. Start the Backend (Required)
```bash
cd ../backend
python -m uvicorn app.main:app --reload --port 8080
```

### 2. Start the Frontend
```bash
# Option A: Python server (recommended)
python serve.py

# Option B: Any HTTP server
npx http-server -p 8000
# or
python -m http.server 8000
```

### 3. Access the Application
- Frontend: http://localhost:8000
- Backend API: http://localhost:8080/docs

## Features Implemented
- [x] Poor Man's Modules architecture
- [x] Glass morphism UI design (104+ components)
- [x] Photo gallery with masonry layout
- [x] Basic navigation (Gallery, Upload, Profile)
- [x] PWA manifest and service worker
- [x] Responsive design
- [x] API service layer
- [x] Demo data fallback

## Features To Implement
- [ ] Firebase Authentication integration
- [ ] Real photo upload with FilePond
- [ ] User profiles with data from backend
- [ ] Photo search and filtering
- [ ] Social features (likes, comments)
- [ ] Series/collections
- [ ] Touch gestures for mobile

## Project Structure
```
frontend/
├── index.html              # Main application entry point
├── manifest.json           # PWA configuration
├── sw.js                  # Service worker for offline support
├── serve.py               # Development server
├── README.md              # This file
├── css/
│   ├── glassmorphism-core.css  # Glass morphism component library
│   ├── base.css              # Base styles
│   ├── components.css         # UI components
│   ├── layout.css            # Layout styles
│   └── gallery.css           # Gallery-specific styles
├── js/
│   ├── config.js             # Application configuration
│   ├── app.js               # Main application coordinator
│   ├── templates.js          # HTML templates
│   └── modules/             # Poor Man's Modules
│       ├── auth.js           # Authentication module
│       ├── api.js            # API wrapper module
│       ├── gallery.js        # Gallery module
│       ├── upload.js         # Upload module
│       ├── profile.js        # Profile module
│       ├── router.js         # Routing module
│       ├── search.js         # Search module
│       ├── settings.js       # Settings module
│       ├── ui.js            # UI helpers module
│       └── utils.js          # Utility functions
├── config/
│   └── glass-theme.js       # Glass morphism theme configuration
├── templates/
│   └── templates.js         # HTML templates
└── assets/
    └── icons/               # PWA icons
```

## Customization

### Glass Effect Colors
Edit the CSS variables in `index.html`:
```css
:root {
    --glass-bg: rgba(17, 25, 40, 0.75);
    --glass-border: rgba(255, 255, 255, 0.125);
    --glass-light: rgba(255, 255, 255, 0.1);
}
```

### API Configuration
Edit the API baseURL in `index.html`:
```javascript
const API = {
    baseURL: 'http://localhost:8080/api/v1',
    // ...
}
```

## Development Tips

1. **No Build Tools**: Direct file serving, no compilation needed
2. **Poor Man's Modules**: All functionality in window.Lumen* global objects
3. **Glass Morphism**: Use glass-* CSS classes for UI components
4. **Demo Mode**: Works with demo data if backend is unavailable
5. **PWA Installation**: Use Chrome menu > "Install Lumen"
6. **Mobile Testing**: Use Chrome DevTools device mode

## Troubleshooting

### CORS Issues
- Ensure backend allows `http://localhost:8000`
- Check backend `.env` file for `ALLOWED_ORIGINS`
- Verify credentials: 'include' in all fetch requests

### Photos Not Loading
- Check if backend is running on port 8080
- Verify API endpoints in browser console
- Check LumenAPI module initialization
- Falls back to demo images automatically

### PWA Not Installing
- Must be served over HTTP (not file://)
- Use the provided `serve.py` script
- Check for HTTPS in production

### Module Not Defined
- Check script loading order in index.html
- Verify module exists in window object: `window.LumenModule`
- Check browser console for initialization errors

## Next Steps

1. **Complete Firebase Auth Integration**
   - Finish Firebase SDK integration
   - Complete login/signup flows in LumenAuth module
   - Connect to backend auth endpoints

2. **Photo Upload Enhancement**
   - Complete FilePond integration in LumenUpload module
   - Add metadata forms with glass morphism
   - Progress indicators with glass components

3. **Enhanced Glass Morphism UI**
   - Add more glass components to glassmorphism-core.css
   - Implement smooth transitions with CSS variables
   - Add loading skeletons with glass effects

## Notes
- Built with Poor Man's Modules pattern for simplicity
- Custom Glass Morphism UI system (104+ components)
- All code is readable and maintainable
- No build tools or npm required
- Perfect for LLM-assisted development
- Each module kept under 400 lines for AI assistance

## Support
See `/docs/MIGRATION_TO_SIMPLE_STACK.md` for detailed migration documentation.