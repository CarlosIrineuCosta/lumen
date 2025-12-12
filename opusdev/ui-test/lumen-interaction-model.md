# Lumen Interaction Model & Tagging System

## Core Navigation Structure

### Primary Views

**Home (Feed)**
- Chronological stream from followed photographers
- No algorithmic manipulation
- Persistent navigation access
- Infinite scroll with lazy loading

**Discover**
- Grid layout of all recent uploads
- Filter by tags, time, location
- "Rising" section (24h momentum)
- Search with tag suggestions

**Profile**
- Always accessible
- Portfolio grid, stats, activity
- Quick upload button
- Settings and privacy controls

## Smart Tagging System (3 Tags Maximum)

### Tag Categories with Semantic Grouping

**SETTING** (Choose 1)
- Studio
- Urban  
- Nature
- Indoor
- Underwater

**STYLE** (Choose 1)
- Portrait
- Fashion
- Fine Art
- Documentary
- Editorial
- Boudoir

**CONTENT** (Choose 0-1)
- Artistic Nude
- Implied Nude
- Lingerie
- Swimwear

**PROCESS** (Optional)
- Film (35mm/120/4x5/8x10)
- Instant Film
- Alternative Process

**LIGHTING** (Optional)
- Natural Light
- Studio Lighting
- Mixed Light

### Image Properties (User-Editable)

**Visual Properties** (Set during upload)
- Color Mode: [Color] [B&W] [Monochrome] [Split-tone] [Selective Color]
- Aspect Ratio: Auto-detect with manual override
- Orientation: [Landscape] [Portrait] [Square] [Panoramic]

**Technical Properties** (Optional, from EXIF or manual)
- Camera/Lens 
- ISO/Aperture/Shutter Speed
- Date/Time taken
- Location (GPS or manual pin)

**Client-Side Detection** (JavaScript, no server cost)
```javascript
// Simple B&W detection in browser
function detectColorMode(imageData) {
  // Calculate RGB channel variance
  // If variance < threshold, likely B&W
  // User confirms or overrides
  // No AI needed, runs instantly
}
```

### Tag Selection Interface
```
[SETTING: Urban ▼] [STYLE: Fine Art ▼] [CONTENT: None ▼]

Optional: [Process] [Lighting]

Properties: [●Color ○B&W] [3:2 ratio ▼] [Landscape]
```

Maximum 3 active tags enforced by UI. Categories are mutually exclusive within their group.

## Social Interactions

### Appreciation System
- **Private counts** - Only photographer sees total
- Single tap to appreciate
- Weekly digest emails
- No public vanity metrics

### Comments
- **Public by default**
- **Private option** when:
  - Mutual connection exists
  - Verified professional account
  - Owner enables private feedback
- Private comments show lock icon

### Connections
- **Follow** - See in feed
- **Connect** - Mutual follow (enables DMs)
- **Collaborate** - Professional credit

## Photo Navigation

### Context-Aware Swiping
- From Home → Navigate followed photos
- From Discover → Navigate discover stream  
- From Profile → Navigate that portfolio
- From Search → Navigate results

### Gesture Controls
- Double tap: Appreciate
- Pinch: Zoom
- Long press: Actions menu
- Swipe up: Details
- Swipe down: Return
- Swipe left/right: Prev/Next

## Upload Flow

1. **Select photos** (batch supported)
2. **Auto-detect properties** (client-side)
   - Color analysis via canvas API
   - Dimension calculations
   - EXIF extraction attempt
3. **User confirms/adjusts properties**
   - Override any auto-detection
   - Add missing technical data
4. **Apply smart tags** (semantic categories)
5. **Privacy settings**
6. **Publish**

### Property Detection Without AI

**Browser-Based Analysis**
- Load image to canvas element
- Sample pixels for color variance
- Calculate aspect ratio from dimensions
- Extract EXIF if present
- Total time: <100ms per image
- Zero server cost

**User Override UI**
```
Auto-detected: B&W, 3:2, Landscape
[✓ Correct] [✗ Override]

If Override:
Color Mode: [Select...]
Aspect: [Select...]
Orientation: [Select...]
```

## AI Cost Optimization

### Phased Approach

**Phase 1: Zero AI** (Launch)
- Manual tagging with smart categories
- Client-side property detection
- Community-suggested tags

**Phase 2: Pattern Analysis** (6 months)
- Analyze tag combinations
- Build photographer profiles
- Identify common patterns

**Phase 3: Lightweight Suggestions** (1 year)
- Suggest tags based on:
  - Photographer's history
  - Visual similarity (perceptual hashing)
  - Time/location patterns
- Run on 256px thumbnails
- Cache suggestions per user

**Phase 4: Optional Premium AI**
- Full scene recognition
- Advanced categorization
- Batch processing during off-peak

### Cost Reduction Strategies
- Perceptual hashing for similarity (free)
- Client-side preprocessing
- Thumbnail analysis only
- User feedback loop for training

## Example Valid Tag Combinations

✅ **Valid:**
- `[Urban] [Portrait] [Natural Light]` + Color Mode: B&W
- `[Studio] [Fashion] [Lingerie]` + Split-tone
- `[Nature] [Fine Art] [Film]` + Color Mode: Color
- `[Studio] [Boudoir] [Studio Lighting]` + Monochrome

❌ **Invalid (Prevented by UI):**
- Urban + Boudoir (boudoir requires indoor/studio)
- Multiple settings (Urban + Nature)
- More than 3 tags total

## Implementation Priority

1. **Week 1**: Client-side property detection
2. **Week 2**: Smart category tagging UI
3. **Month 1**: Launch with manual system
4. **Month 6**: Analyze patterns
5. **Year 1**: Introduce suggestions (no AI)
6. **Year 2**: Consider AI features