---
description: Frontend UI development and design implementation
---

# UI Development & Design Implementation

Focus on frontend development for $ARGUMENTS:

## 1. Analysis Phase

### Current UI Assessment
```bash
echo "=== UI DEVELOPMENT ANALYSIS ==="

# Check current frontend structure
echo "Frontend structure:"
find opusdev/frontend -name "*.html" -o -name "*.css" -o -name "*.js" | head -10

# Identify UI components and patterns
echo ""
echo "UI Components found:"
grep -r "class=" opusdev/frontend/*.html | grep -E "(component|widget|ui-)" | head -5

# Check responsive design implementation
echo ""
echo "Responsive design elements:"
grep -r "@media" opusdev/frontend/*.css | head -3
```

### Design System Review
```bash
# Check for existing design patterns
echo "=== DESIGN SYSTEM REVIEW ==="

echo "CSS Variables (Design tokens):"
grep -r ":root" opusdev/frontend/*.css | head -5

echo ""
echo "Color scheme:"
grep -r "color:" opusdev/frontend/*.css | head -5

echo ""
echo "Typography system:"
grep -r "font-" opusdev/frontend/*.css | head -5
```

## 2. UI Development Tasks

### Component Creation/Modification
```bash
echo "=== UI COMPONENT DEVELOPMENT ==="

# Determine component type based on arguments
COMPONENT_TYPE="$ARGUMENTS"

case $COMPONENT_TYPE in
    *photo*|*gallery*|*image*)
        echo "Working on photo/gallery components"
        COMPONENT_DIR="opusdev/frontend/components/gallery"
        ;;
    *profile*|*user*)
        echo "Working on user profile components"
        COMPONENT_DIR="opusdev/frontend/components/profile"
        ;;
    *auth*|*login*)
        echo "Working on authentication UI"
        COMPONENT_DIR="opusdev/frontend/components/auth"
        ;;
    *)
        echo "Working on general UI components"
        COMPONENT_DIR="opusdev/frontend/components/common"
        ;;
esac

# Create component directory if needed
mkdir -p "$COMPONENT_DIR"
echo "Component directory: $COMPONENT_DIR"
```

### HTML Structure Implementation
```bash
echo "=== HTML STRUCTURE ==="

# Implement semantic HTML structure
echo "Implementing semantic HTML for: $ARGUMENTS"

# Check for accessibility attributes
echo "Accessibility checklist:"
echo "- [ ] Proper heading hierarchy (h1-h6)"
echo "- [ ] Alt text for images"
echo "- [ ] ARIA labels where needed"
echo "- [ ] Keyboard navigation support"
echo "- [ ] Color contrast compliance"
```

### CSS Styling Implementation
```bash
echo "=== CSS STYLING ==="

# Follow existing design patterns
echo "Applying Lumen design system styles"

# Responsive design implementation
echo "Responsive breakpoints:"
echo "- Mobile: 320px-768px"
echo "- Tablet: 768px-1024px"  
echo "- Desktop: 1024px+"

# Check for CSS Grid/Flexbox usage
echo ""
echo "Layout system:"
grep -r "display: grid\|display: flex" opusdev/frontend/*.css | head -3
```

## 3. Design System Integration

### Lumen Visual Identity
```bash
echo "=== LUMEN DESIGN SYSTEM ==="

# Lumen-specific design principles
echo "Design Principles:"
echo "- Clean, professional photography focus"
echo "- Dark mode support for photo viewing"
echo "- 500px-style gallery layouts"
echo "- Minimalist, distraction-free interface"
echo "- High contrast for accessibility"

# Color palette
echo ""
echo "Lumen Color Palette:"
echo "- Primary: Professional photography blues/grays"
echo "- Secondary: Accent colors for CTAs"
echo "- Background: Dark mode for photo viewing"
echo "- Text: High contrast for readability"
```

### Component Standards
```bash
echo "=== COMPONENT STANDARDS ==="

# UI component requirements
echo "Component Requirements:"
echo "- [ ] Responsive design (mobile-first)"
echo "- [ ] Dark/light mode compatibility"
echo "- [ ] Accessible by default (WCAG 2.1 AA)"
echo "- [ ] Consistent with photo gallery theme"
echo "- [ ] Touch-friendly (min 44px touch targets)"
echo "- [ ] Loading states for async operations"
```

## 4. Interactive Features

### JavaScript Implementation
```bash
echo "=== JAVASCRIPT FUNCTIONALITY ==="

# Check existing JavaScript patterns
echo "Current JS patterns:"
grep -r "function\|const\|let" opusdev/frontend/*.js | head -5

# Firebase integration for UI
echo ""
echo "Firebase UI Integration:"
echo "- [ ] Authentication state management"
echo "- [ ] Real-time data updates"  
echo "- [ ] Image upload progress"
echo "- [ ] Error handling and user feedback"
```

### Photo Gallery Specific UI
```bash
echo "=== PHOTO GALLERY UI ==="

# Justified Gallery implementation (500px style)
echo "Gallery Features:"
echo "- [ ] Justified layout (500px style)"
echo "- [ ] Lightbox with metadata display"
echo "- [ ] Infinite scroll loading"
echo "- [ ] Grid view toggle"
echo "- [ ] Photo zoom and pan"
echo "- [ ] Keyboard navigation (arrow keys)"

# Performance considerations
echo ""
echo "Performance Optimizations:"
echo "- [ ] Lazy loading for images"
echo "- [ ] WebP format support"
echo "- [ ] Image size optimization"
echo "- [ ] CDN integration for fast loading"
```

## 5. Testing and Validation

### Visual Testing
```bash
echo "=== VISUAL TESTING ==="

# Browser testing
echo "Browser Compatibility:"
echo "- [ ] Chrome (latest 2 versions)"
echo "- [ ] Firefox (latest 2 versions)" 
echo "- [ ] Safari (latest 2 versions)"
echo "- [ ] Mobile browsers (iOS Safari, Chrome Mobile)"

# Responsive testing
echo ""
echo "Responsive Testing:"
echo "Testing URLs:"
echo "- Desktop: http://100.106.201.33:8000/lumen-app.html"
echo "- Mobile simulation: Chrome DevTools device emulation"
```

### Accessibility Testing
```bash
echo "=== ACCESSIBILITY TESTING ==="

# Automated accessibility checks
echo "Accessibility Validation:"
echo "- [ ] Screen reader compatibility"
echo "- [ ] Keyboard-only navigation"
echo "- [ ] Color contrast ratios"
echo "- [ ] Focus indicators visible"
echo "- [ ] Alt text for all images"

# Tools for testing
echo ""
echo "Testing Tools:"
echo "- Chrome DevTools Lighthouse"
echo "- axe DevTools extension"
echo "- Manual keyboard navigation testing"
```

## 6. Performance Optimization

### Frontend Performance
```bash
echo "=== PERFORMANCE OPTIMIZATION ==="

# CSS optimization
echo "CSS Optimization:"
echo "- [ ] Minify CSS for production"
echo "- [ ] Remove unused CSS rules"
echo "- [ ] Optimize critical CSS loading"
echo "- [ ] Use CSS Grid/Flexbox efficiently"

# JavaScript optimization
echo ""
echo "JavaScript Optimization:"
echo "- [ ] Minimize DOM manipulation"
echo "- [ ] Debounce scroll/resize events"
echo "- [ ] Lazy load non-critical scripts"
echo "- [ ] Use modern ES6+ features efficiently"

# Image optimization
echo ""
echo "Image Optimization:"
echo "- [ ] WebP format with fallbacks"
echo "- [ ] Responsive image sizing"
echo "- [ ] Lazy loading implementation"
echo "- [ ] Progressive JPEG loading"
```

## 7. Integration with Backend

### API Integration
```bash
echo "=== BACKEND INTEGRATION ==="

# API endpoints for UI
echo "API Integration Points:"
echo "- Authentication: /api/v1/auth/"
echo "- User profiles: /api/v1/users/"
echo "- Photo uploads: /api/v1/photos/"
echo "- Gallery data: /api/v1/gallery/"

# Error handling
echo ""
echo "Error Handling:"
echo "- [ ] Network error graceful degradation"
echo "- [ ] Loading states during API calls"
echo "- [ ] User-friendly error messages"
echo "- [ ] Retry logic for failed requests"
```

### Real-time Features
```bash
echo "=== REAL-TIME FEATURES ==="

# Firebase real-time integration
echo "Real-time UI Updates:"
echo "- [ ] Live photo upload progress"
echo "- [ ] Instant profile updates"
echo "- [ ] Real-time comment/like updates"
echo "- [ ] Online status indicators"
```

## 8. UI Quality Checklist

### Pre-deployment Checklist
```bash
echo "=== UI QUALITY CHECKLIST ==="

echo "✅ Visual Design:"
echo "- [ ] Consistent with Lumen brand"
echo "- [ ] Professional photography focus"
echo "- [ ] Clean, minimal interface"
echo "- [ ] Proper spacing and typography"

echo ""
echo "✅ Functionality:"
echo "- [ ] All interactive elements work"
echo "- [ ] Forms validate properly"
echo "- [ ] Navigation is intuitive"
echo "- [ ] Search functionality works"

echo ""
echo "✅ Performance:"
echo "- [ ] Fast loading times (<3s)"
echo "- [ ] Smooth animations and transitions"
echo "- [ ] Efficient image loading"
echo "- [ ] No JavaScript errors in console"

echo ""
echo "✅ Accessibility:"
echo "- [ ] WCAG 2.1 AA compliance"
echo "- [ ] Keyboard navigation"
echo "- [ ] Screen reader support"
echo "- [ ] High contrast mode support"
```

## Implementation Notes

- **Design System**: Follow Lumen's clean, professional aesthetic
- **Photo Focus**: Prioritize image viewing experience
- **Mobile First**: Start with mobile design, enhance for desktop
- **Performance**: Optimize for fast photo loading
- **Accessibility**: Ensure inclusive design principles

This command integrates with:
- `/check` for UI testing validation
- `/dev` for local development environment
- Backend APIs for data integration