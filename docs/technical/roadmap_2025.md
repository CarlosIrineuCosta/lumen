# Lumen Platform - Development Status & Roadmap

**Project Start Date**: August 10, 2025  
**Last Updated**: August 11, 2025  

*IMPORTANT: Always update the "Last Updated" date when making changes to this roadmap*

## COMPLETED FEATURES

**Note**: Detailed completed feature tracking has been moved to GitHub Projects. See GitHub Issues with "completed" milestone for full feature history.

**Major Milestones Achieved**:
- Complete authentication system with Firebase integration
- PostgreSQL database with optimized schema (Firebase UID primary keys)
- Photo management system (upload, display, editing, deletion)
- User profile system with comprehensive editing capabilities
- Discovery and social features (feeds, search, likes)
- Performance optimizations (dynamic URL generation, database indexes)

**GitHub Tracking**: 
- **Feature Roadmap**: [Lumen Feature Roadmap 2025 Project](https://github.com/users/CarlosIrineuCosta/projects/3)
- **Completed Features**: [GitHub Issues - Completed](https://github.com/CarlosIrineuCosta/lumen-photo/issues?q=is%3Aissue+is%3Aclosed+label%3Acompleted)
- **All Issues**: [GitHub Issues](https://github.com/CarlosIrineuCosta/lumen-photo/issues)

## CRITICAL ISSUES

### Performance Crisis
- **Database queries are TOO SLOW** (multi-second response times)
- Photo loading takes forever
- No caching strategy
- Signed URLs regenerated on every request

### Missing Core Features
1. **Photo Discovery Feed** - Not implemented
2. **Search System** - Completely missing
3. **Geographic Features** - No nearby/location functionality
4. **Portfolio Curation** - Can mark as portfolio but no management tools

## IMMEDIATE PRIORITIES

### 1. Fix Performance (URGENT)
**Problem**: Database/API responses taking 3-5+ seconds
**Solutions Needed**:
- Add database indexes on frequently queried columns
- Implement Redis caching for photo URLs
- Generate signed URLs once and cache them
- Optimize database queries (N+1 problems?)
- Consider CDN for image delivery

### 2. Implement Discovery System
**Current State**: All tabs show same "/photos/recent" endpoint
**Needed**:
- `/photos/discover` - Curated/trending photos
- `/photos/following` - Photos from followed users (need follow system)
- `/photos/nearby` - Geographic discovery (need GPS data)
- Proper pagination with cursor-based loading

### 3. Search Implementation
**Components Needed**:
- Basic text search for titles/descriptions
- Tag-based filtering
- User search (photographers/models)
- Location-based search
- Advanced filters (camera, settings, date range)

### 4. TV Display Feature Analysis
**Questions to Research**:
- What resolution are we targeting? (4K = 3840x2160)
- Current photo sizes in storage?
- Bandwidth requirements for 4K streaming?
- How to connect phone to TV? (Chromecast? HDMI? Web app?)
**Reality Check**: This might not be feasible with current performance

## DATABASE PERFORMANCE FIXES

### Immediate Actions Required
```sql
-- Add these indexes NOW
CREATE INDEX idx_photos_user_id ON photos(user_id);
CREATE INDEX idx_photos_upload_date ON photos(upload_date DESC);
CREATE INDEX idx_photos_is_public ON photos(is_public);
CREATE INDEX idx_photos_is_portfolio ON photos(is_portfolio);
CREATE INDEX idx_photos_composite ON photos(user_id, is_public, upload_date DESC);

-- Check query performance
EXPLAIN ANALYZE SELECT * FROM photos WHERE is_public = true ORDER BY upload_date DESC LIMIT 20;
```

### Caching Strategy
1. **Redis for URL caching** (1-hour expiry)
2. **CloudFlare CDN** for image delivery
3. **Browser caching** headers for static assets
4. **Query result caching** for popular feeds

## REALISTIC 30-DAY ROADMAP

### Day 1-7: Performance Emergency
- [ ] Add database indexes
- [ ] Implement basic Redis caching
- [ ] Profile slow queries with EXPLAIN
- [ ] Set up monitoring (response times, query times)

### Day 8-14: Discovery Features
- [ ] Implement distinct discover endpoint
- [ ] Add follow/unfollow system
- [ ] Create following feed
- [ ] Basic recommendation algorithm

### Day 15-21: Search System
- [ ] Text search with PostgreSQL full-text
- [ ] Tag filtering UI and backend
- [ ] User search functionality
- [ ] Search result pagination

### Day 22-30: Polish & Optimize
- [ ] Lazy loading improvements
- [ ] Image optimization pipeline
- [ ] Performance monitoring dashboard
- [ ] User feedback implementation

## TECHNICAL DEBT

### Backend Issues
- No error handling in photo service
- Missing transaction management
- No rate limiting
- No background job processing
- Synchronous image processing (blocking)

### Frontend Issues
- No state management (everything in app.js)
- No proper error handling
- Missing loading states in many places
- No offline capability despite being "PWA"

### Infrastructure Issues
- No monitoring or alerting
- No backup strategy
- No CI/CD pipeline
- Manual deployment only

## TV DISPLAY REALITY CHECK

### Current Blockers
1. **Performance**: Can't even load 20 photos quickly
2. **Image Sizes**: Unknown optimization level
3. **Bandwidth**: 4K images = 8-15MB each
4. **Technical**: How to connect phone → TV?

### Feasibility Assessment
**Not viable until**:
- Performance issues solved
- CDN implemented
- Image optimization pipeline built
- Clear technical approach defined

**Consider Instead**:
- Start with 1080p support
- Progressive image loading
- Slideshow mode with preloading
- Web-based TV app (not phone connection)

## SEARCH SYSTEM DESIGN

### Phase 1: Basic Search
```python
# PostgreSQL full-text search
ALTER TABLE photos ADD COLUMN search_vector tsvector;
UPDATE photos SET search_vector = 
  to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description,''));
CREATE INDEX idx_photos_search ON photos USING GIN(search_vector);
```

### Phase 2: Advanced Filters
- Camera make/model
- Technical settings (ISO, aperture, etc.)
- Date ranges
- Location radius
- User type (photographer/model)

### Phase 3: AI Enhancement
- Natural language queries
- Similar photo search
- Auto-tagging with Vertex AI
- Content-based recommendations

## NEXT SESSION PRIORITIES

1. **Run database indexes** (5 minutes)
2. **Profile slow queries** (30 minutes)
3. **Implement basic caching** (2 hours)
4. **Test performance improvements** (30 minutes)
5. **Start discovery feed** (2 hours)

## KEY METRICS TO TRACK

- **API Response Time**: Target < 200ms
- **Image Load Time**: Target < 1s for thumbnail
- **Database Query Time**: Target < 50ms
- **Page Load Time**: Target < 2s
- **User Engagement**: Photos per session

## CRITICAL QUESTIONS

1. Why are database queries so slow? (Missing indexes? Bad queries? Network?)
2. What's the actual image size distribution?
3. How many concurrent users expected?
4. What's the infrastructure budget?
5. Geographic scope (Brazil only? Global?)

---

## CRITICAL DATABASE ARCHITECTURE DECISIONS

### Root Cause Analysis: ID Format Inconsistency

**Problem Discovered**: Database vs GCS ID format mismatch breaking photo display
- **Database**: Uses UUID format (36-char): `141303d1-8db6-4fc4-83c0-7ca520e4dc64`
- **GCS Paths**: Uses Firebase UID format (28-char): `9pGzwsVBRMaSxMOZ6QNTJJjnl1b2`
- **Result**: PhotoService can't generate correct GCS paths → broken image loading

### Strategic Decision: Swiss VPS Migration

**Motivation**: 
- Cost reduction: Google Cloud SQL R$ 12/month for 2 users
- Legal protection: Artistic nude content needs clear hosting policies
- Privacy compliance: EU/Swiss laws stronger than US-based hosting

**Migration Plan**:
- **Provider**: EDIS Global Switzerland (Zurich datacenter)
- **Cost**: €4.99/month for KVM Smart (1GB RAM, 15GB SSD, 1TB traffic)
- **Storage**: Scaleway Object Storage (Paris) - €0.02/GB/month
- **Authentication**: Keep Firebase OAuth (free, reliable)

### Database Centralization Requirements

**Current Problem**: Scattered authentication and ID validation across multiple files
- Tests recreating auth logic individually
- PhotoService doing own database connections  
- Inconsistent ID format handling throughout system

**Solution**: Centralized services architecture
```python
# Single source of truth for all authentication
class AuthService:
    @staticmethod
    def get_current_user() -> User
    @staticmethod
    def validate_token(token: str) -> dict

# Single source of truth for all ID handling  
class IDValidationService:
    @staticmethod
    def normalize_firebase_uid(uid: str) -> str
    @staticmethod
    def validate_uuid(uuid_str: str) -> UUID
    @staticmethod
    def get_gcs_path(firebase_uid: str, photo_id: UUID) -> str
```

### Technical Implementation Strategy

**Phase 1: Use Firebase UID Everywhere (Recommended)**
- Change database `users.id` to store Firebase UID directly (28-char string)
- Keep GCS paths using Firebase UID (no file migration needed)
- No complex mapping logic required
- Single source of truth for user identity

**Migration Steps**:
1. Export existing user data with Firebase UID mapping
2. Update database schema to use Firebase UID as primary key
3. Update all foreign key references
4. Centralize all ID validation in single service

### Cost-Benefit Analysis

**Current Google Cloud**:
- Cloud SQL: R$ 12/month (fixed cost regardless of users)
- GCS: Variable but minimal for current usage
- Firebase Auth: Free up to 50k MAU

**Proposed Swiss Infrastructure**:
- VPS: €4.99/month (~R$ 30/month)
- Object Storage: €2-5/month for 1TB
- Firebase Auth: Still free
- **Total**: ~€7-10/month vs R$ 12 + GCS

**Break-even Point**: 10 users paying €5/month = €50 revenue covers all costs

### Legal and Privacy Advantages

**Swiss Hosting Benefits**:
- Clear artistic nude content policies
- Banking-grade privacy laws
- No US PATRIOT Act exposure
- GDPR compliance built-in
- Crypto payment options for user privacy

**EU Object Storage Benefits**:
- GDPR compliant by design
- Right to be forgotten easier to implement
- Data sovereignty for European users
- No US data transfer concerns

### Implementation Timeline

**Day 1**: Order EDIS Global VPS, setup basic infrastructure
**Day 2**: Migrate backend code, implement centralized services  
**Day 3**: Export/import data, test full pipeline
**Day 4**: DNS/SSL setup, production deployment

**Scaling Strategy**: When 10+ paying users, upgrade to larger VPS tier

---

**Bottom Line**: Fix performance first, then add features. The platform is architecturally sound but needs serious optimization before adding complexity like TV display or AI search. Migration to Swiss infrastructure solves both cost and legal concerns while maintaining technical simplicity.
