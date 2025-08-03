# Lumen - UI/UX Specifications

## Design Philosophy

### Core Principles
- **Photography First**: Images dominate, text supports
- **Professional Aesthetic**: Sophisticated, not playful
- **Clarity Over Cleverness**: Intuitive navigation
- **Respect for Content**: No distractions from the work

### Visual Language
- **Typography**: Montserrat (headers), Roboto (body)
- **Color Palette**: Neutral grays, pure black/white, minimal accent colors
- **Layout**: Clean grid system, generous whitespace
- **NO EMOJIS**: Professional platform, not social media

## Information Architecture

### User View Levels

**Public View (Not Logged In)**:
- Gallery posts (public feed)
- Portfolio (curated professional work)
- Username, city/country
- Basic artistic style/genre

**Authenticated View (Logged In)**:
- Everything in public view
- Full gallery access
- Professional details (equipment, skills)
- Travel schedule
- Contact button (respects user's contact mode)
- Availability calendar (general)

**Connected View (Accepted Connection)**:
- Everything in authenticated view
- Specific professional attributes
- Direct contact information
- Detailed availability calendar
- Restricted gallery access (if granted)

**Restricted Section** (User Controlled):
- Private gallery requiring explicit permission
- For sensitive work or premium content
- Permission granted per viewer
- Not indexed in searches

## Core User Flows

### Registration Flow
```
1. Email/Username/Password
2. Age Verification Checkbox
   □ I confirm I am 18+ (or legal age in my jurisdiction)
   □ I understand this platform contains artistic nudity
3. Location (Country required, City optional)
4. Account Type (Photographer/Model/Both)
5. Payment Selection (tiers clearly explained)
6. Email Verification
7. Welcome/Onboarding
```

### Photo Upload Flow
```
1. Select Images (drag & drop or browse)
2. For each image:
   - Title (optional)
   - Location (optional, privacy-aware)
   - □ Include in Portfolio
   - Camera/Lens data (auto-extracted from EXIF)
3. Batch Upload Progress
4. Compression Status Indicator
5. Success → View in Gallery
```

### Discovery Flow
```
Main Feed (Mosaic Grid)
    ↓ Click Image
Single Image View (Full Screen)
    ↓ Swipe Horizontally  
Browse User's Gallery
    ↓ Click Username
User Profile View
    ↓ Connection Request (if applicable)
```

## Key Interface Components

### Navigation Header
- Logo (left)
- Search (center)
- User Menu (right): Profile, Settings, Logout
- Upload Button (prominent, always visible)

### Mosaic Grid Gallery
- Variable image sizes based on aspect ratio
- Lazy loading with progressive enhancement
- Hover: Subtle overlay with photographer name
- Click: Full-screen image view
- No engagement metrics visible

### Profile Page Layout
```
[Header Image]
[Avatar] [Username] [Location] [Contact Mode Indicator]
[Bio - 2-3 lines max]

[Tabs]
Gallery | Portfolio | About | Calendar

[Content Area - Mosaic Grid or Info]
```

### Contact System
**Three Contact Modes** (User Selectable):
1. **Gallery Mode**: No contact button visible
2. **Selective Mode**: "Request Connection" with criteria
3. **Discovery Mode**: "Contact" button visible

### NSFW Content Handling

**Settings Options**:
```
Content Filtering:
○ Show all content (including artistic nudity)
○ Blur NSFW content (click to reveal)
○ Hide NSFW content completely
```

**NSFW Image Treatment**:
- Blurred by default if user setting requires
- Click to reveal with warning
- "NSFW" badge in corner (subtle, not prominent)

## Professional Features

### Calendar/Availability System
**Public View**:
- Month view with general availability
- "Available for projects" / "Busy" indicators

**Connected View**:
- Detailed calendar with specific dates/times
- Timezone conversion
- Project scheduling interface

### Location System
```
Based in: [City, Country] (permanent)
Currently: [City, Country] (if different)
Upcoming Travel:
  - Tokyo, Japan (Mar 15-30)
  - Berlin, Germany (Apr 10-20)
  [+ Add Travel]
```

### Professional Attributes
**Models** (Private until connection):
```
Physical Attributes:
- Height: ___cm
- Age Range: [20-25] [25-30] [30-35] etc
- Hair: [Natural Color] [Current Color if different]
- Eyes: [Color] □ Contacts
- Modifications: [List tattoos/piercings with location]

Skills & Training:
□ Dance (specify: ballet, contemporary, etc)
□ Yoga □ Pole □ Aerial □ Underwater
□ Other: _______
```

**Photographers** (Visible to authenticated users):
```
Equipment:
- Primary Camera: _______
- Specialty Equipment: □ 8x10 View □ Underwater □ Drone
- Lighting: □ Natural □ Studio □ Both

Workflow:
○ Digital Only ○ Film Only ○ Hybrid
Post-Processing: □ Minimal □ Extensive
```

## Mobile Responsiveness

### Breakpoints
- Desktop: 1200px+ (full mosaic grid)
- Tablet: 768px-1199px (reduced columns)
- Mobile: <768px (single column, swipe galleries)

### Mobile-Specific Features
- Bottom navigation bar
- Swipe between images
- Pull-to-refresh on feeds
- Camera-first upload flow

## Interaction Patterns

### Image Interactions
- **Single Tap**: Full screen view
- **Double Tap**: Add to favorites (private collection)
- **Long Press**: Share options (external only)
- **Swipe**: Navigate gallery

### Loading States
- Skeleton screens for image grids
- Progressive image loading (blur to sharp)
- Infinite scroll with loading indicator
- "No more content" message at end

### Error Handling
- Friendly error messages
- Retry options for failed uploads
- Offline mode indicators
- Graceful degradation

## TV/Large Display Mode

### Activation
- Settings → TV Mode
- QR code for phone control
- Automatic detection via HDMI/casting

### TV Interface
- Full-screen image display
- Minimal UI elements
- Phone becomes remote control
- Smooth transitions between images
- 4K image quality prioritized

## Accessibility

### Standards
- WCAG 2.1 AA compliance
- Keyboard navigation throughout
- Screen reader support
- High contrast mode option

### Image Descriptions
- Optional alt text for portfolio images
- Automatic EXIF data reading
- Voice navigation support

## Performance Targets

### Speed Metrics
- Time to First Image: <2 seconds
- Full Gallery Load: <5 seconds
- Upload Start: <1 second after selection
- Search Results: <500ms

### Optimization
- CDN for global image delivery
- WebP with JPEG fallback
- Responsive image sizing
- Browser caching strategy

## Security UI Elements

### Age Verification
- Clear, legally compliant language
- Cannot be skipped or dismissed
- Remembers verification per device

### Report/Flag System
- Subtle flag icon on images
- Categories: Spam, Inappropriate, Copyright
- Quick report with optional details
- Confirmation of report received

## Future UI Considerations

### AI Integration (Later Phases)
- Natural language search bar
- Auto-tagging suggestions (user controlled)
- Smart gallery organization options

### Social Features (Minimal)
- Following (for updates only)
- Private collections/mood boards
- Collaborative project spaces

## Design System Components

### Buttons
- Primary: Black background, white text
- Secondary: White background, black border
- Disabled: Gray background, darker gray text
- Hover: Subtle shade change, no color shifts

### Forms
- Minimal borders (bottom line only)
- Floating labels
- Clear error states
- Inline validation

### Modals
- Dark overlay (60% opacity)
- Centered content
- Clear close button
- ESC key dismissal

### Toast Notifications
- Bottom center position
- Auto-dismiss after 4 seconds
- Action buttons when relevant
- Queue multiple notifications

---

*This document defines the user interface and experience standards for Lumen platform. For technical implementation details, see code_technical_implementation.md*