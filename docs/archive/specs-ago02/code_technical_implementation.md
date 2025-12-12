# Lumen - Technical Implementation Guidelines

**FOR DEVELOPERS AND CODE IMPLEMENTATION**

## System Architecture Overview

### Technology Stack
- **Backend**: FastAPI 0.104.1 (Python 3.11.13)
- **Frontend**: Vanilla JavaScript + Progressive Web App
- **Database**: PostgreSQL (Cloud SQL) - migrating from in-memory
- **Authentication**: Firebase Admin SDK 6.3.0 + JWT validation
- **Storage**: Google Cloud Storage (Bucket: lumen-photos-20250731)
- **Image Processing**: MozJPEG + Guetzli compression pipeline
- **AI Processing**: Vertex AI Vision API (batch processing)

### Infrastructure Requirements
- **Development**: Tailscale network (100.106.201.33:8080)
- **Production**: Google Cloud Platform (Project: lumen-photo-app-20250731)
- **Performance Targets**: <2s photo upload, <500ms thumbnail display, 4K TV output support

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    bio TEXT,
    profile_image_url VARCHAR(500),
    location_city VARCHAR(100),
    location_country VARCHAR(100),
    is_professional BOOLEAN DEFAULT false,
    portfolio_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Photos Table
```sql
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500) NOT NULL,
    title VARCHAR(200),
    description TEXT,
    camera_make VARCHAR(100),
    camera_model VARCHAR(100),
    lens VARCHAR(100),
    focal_length INTEGER,
    aperture DECIMAL(3,1),
    shutter_speed VARCHAR(20),
    iso INTEGER,
    location_latitude DECIMAL(10,8),
    location_longitude DECIMAL(11,8),
    location_name VARCHAR(200),
    tags TEXT[],
    is_public BOOLEAN DEFAULT true,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Engagement Table
```sql
CREATE TABLE photo_likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    photo_id UUID REFERENCES photos(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(photo_id, user_id)
);
```

## API Endpoints Structure

### Authentication
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/status` - Authentication status
- `GET /api/v1/auth/profile` - User profile (protected)

### Photo Management
- `POST /api/v1/photos/upload` - Upload with compression pipeline
- `GET /api/v1/photos/my-photos` - User's photos
- `GET /api/v1/photos/recent` - Recent photos feed (streaming)
- `GET /api/v1/photos/{id}` - Single photo details
- `PUT /api/v1/photos/{id}` - Update photo metadata
- `DELETE /api/v1/photos/{id}` - Delete photo

### Discovery and Search
- `GET /api/v1/photos/feed` - Last uploaded images stream
- `GET /api/v1/search/photos` - Tag-based photo search
- `GET /api/v1/photographers/nearby` - Geographic discovery

## Image Processing Pipeline

### Compression Strategy
```
Upload → Multiple Compression Outputs:
├── Thumbnail (optipng/jpegoptim) → Grid display
├── Web (MozJPEG) → Standard browsing  
├── Portfolio (Guetzli) → Professional presentation
└── TV (minimal compression) → 4K display
```

### MozJPEG Integration (Primary)
```javascript
const compress_images = require("compress-images");

compress_images(input_path, output_path, 
  { compress_force: false, statistic: true, autoupdate: true }, 
  false,
  { jpg: { engine: "mozjpeg", command: ["-quality", "60"] } },
  callback
);
```

### Guetzli Integration (Background)
```bash
# Background processing for portfolio images
guetzli --quality 84 input.jpg output.jpg
```

### Storage Structure
```
lumen-photos-20250731/
├── original/{user_id}/{photo_id}.jpg
├── thumbnails/{user_id}/{photo_id}_thumb.jpg  
├── web/{user_id}/{photo_id}_web.jpg
├── portfolio/{user_id}/{photo_id}_portfolio.jpg
└── tv/{user_id}/{photo_id}_4k.jpg
```

## Frontend Implementation

### Mosaic Grid System
**Primary Library**: Justified Gallery (used by 500px)
```javascript
$('#gallery').justifiedGallery({
    rowHeight: 200,
    maxRowHeight: 400,
    margins: 3,
    lastRow: 'nojustify'
});
```

**Fallback**: CSS Grid Masonry (Firefox support)
```css
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    grid-template-rows: masonry;
    gap: 10px;
}
```

### TV Integration Requirements
- **4K Output Support**: Images up to 3840x2160
- **HDMI/USB-C**: Phone-to-TV connection protocols
- **Navigation**: Touch gesture translation to TV remote
- **Performance**: Preloading for seamless swiping

### Authentication Fix Priority
1. Firebase auth state persistence
2. JWT token refresh logic
3. Registration flow completion
4. Login/logout state synchronization

## Geographic Discovery System

### GPS Precision Levels
- **Country**: Required for all users
- **City/Region**: Optional, enables local discovery
- **Neighborhood**: Privacy-controlled, never exact address
- **Coordinate Generation**: Major city GPS points for testing

### Natural Language Query Processing
```javascript
// Gemini API integration for query conversion
const query = "Connect me with Portuguese photographers shooting nudes outdoors";
const tags = await convertToTags(query); 
// Result: ["Portugal", "nude", "outdoor", "photographer"]
```

### Search Implementation
```sql
-- Geographic radius search
SELECT u.*, p.* FROM users u 
JOIN photos p ON u.id = p.user_id 
WHERE ST_DWithin(
    ST_Point(p.location_longitude, p.location_latitude)::geography,
    ST_Point($longitude, $latitude)::geography,
    30000  -- 30km radius
) AND p.tags && $search_tags;
```

## Performance Optimization

### Caching Strategy
- **Browser**: Static assets, thumbnails
- **CDN**: Global image delivery
- **Database**: Query result caching
- **API**: Response caching for discovery feeds

### Image Loading
- **Lazy loading**: Intersection Observer API
- **Progressive enhancement**: WebP with JPEG fallback
- **Preloading**: Adjacent images in sequence
- **Compression ratios**: 200-300KB web, <2MB 4K

### Database Optimization
- **Indexes**: location coordinates, tags, upload_date
- **Connection pooling**: Async database connections
- **Query optimization**: Efficient joins for discovery

## Cost Analysis (Infrastructure)

### Google Cloud Services
- **Storage**: ~$4/month for 200GB (1000 users)
- **Bandwidth**: ~$4/month for image delivery
- **AI Processing**: ~$10/month for tagging
- **Database**: ~$50/month Cloud SQL instance
- **Total**: ~$68/month infrastructure cost

### Scaling Considerations
- **Horizontal**: Stateless API design
- **Database**: Read replicas for discovery queries
- **Storage**: Multi-region for global delivery
- **Processing**: Background queues for compression

## Critical Technical Fixes

### Authentication System
1. **Token validation timing** in registration flow
2. **Firebase auth state** persistence between pages  
3. **Registration completion** logic in backend
4. **Frontend state management** during auth transitions

### Database Migration
1. **Cloud SQL setup** with proper schema
2. **Data migration** from in-memory to persistent
3. **API endpoint updates** to use database
4. **Connection pooling** and error handling

### Photo Discovery
1. **Last uploaded API** endpoint implementation
2. **Real-time feed** with pagination
3. **Photo interaction** infrastructure (likes, views)
4. **Streaming updates** for new uploads

## Development Environment

### Backend Setup
```bash
cd lumen-gcp/backend
source venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=firebase_service_account.json
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Frontend Setup  
```bash
cd lumen-gcp/frontend
python3 -m http.server 8000
```

### Environment Variables
```
GCP_PROJECT_ID=lumen-photo-app-20250731
STORAGE_BUCKET_NAME=lumen-photos-20250731
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Technical Research Priorities

### Image Compression Libraries
- **MozJPEG**: Node.js integration (`compress-images`, `mozjpeg-bin`)
- **Guetzli**: CLI integration for background processing
- **WebP**: `cwebp` for modern browser support
- **Performance**: Compression speed vs quality analysis

### Mosaic Grid Implementation
- **Justified Gallery**: Professional photography focus
- **CSS Grid Masonry**: Native browser support (Firefox)
- **Performance**: Large image gallery optimization
- **Mobile**: Touch gesture navigation

### TV Integration Research
- **HDMI Output**: Phone connection protocols
- **Wireless Display**: Chromecast, AirPlay compatibility  
- **4K Performance**: Image loading and navigation
- **Remote Control**: Navigation interface adaptation

### GPS and Discovery
- **Coordinate Precision**: Privacy vs functionality balance
- **Search Algorithms**: Efficient geographic queries
- **Caching**: Location-based discovery optimization
- **API Integration**: Travel planning and coordination services

## Implementation Sequence

### Phase 1: Core Fixes (Week 1)
1. Authentication system repair
2. Database migration to PostgreSQL  
3. Photo discovery feed implementation
4. Basic mosaic grid layout

### Phase 2: Image Pipeline (Week 2)
1. MozJPEG compression integration
2. Multiple format generation
3. TV-quality image support
4. Performance optimization

### Phase 3: Discovery (Week 3)  
1. Geographic search implementation
2. Natural language query processing
3. Tag-based discovery system
4. User interaction features

### Phase 4: Polish (Week 4)
1. Mobile responsive optimization
2. TV integration testing
3. Performance monitoring
4. Production deployment preparation

## Quality Assurance

### Testing Requirements
- **Authentication flow**: Registration → login → upload → browse
- **Image processing**: Upload → compression → display → TV output
- **Geographic discovery**: Location → search → results → contact
- **Performance**: Load times, compression ratios, mobile responsiveness

### Monitoring
- **Image processing**: Compression times and quality
- **Discovery performance**: Search response times
- **Storage costs**: Usage tracking and optimization
- **User experience**: Loading times and error rates

---

*This document provides technical implementation guidelines for developers working on Lumen platform. For business strategy and content policy decisions, refer to strategy_business_framework.md*