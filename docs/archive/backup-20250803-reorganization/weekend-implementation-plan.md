# Weekend Implementation Plan - Lumen Photography Platform

## Overview
Migrating to production-ready architecture with business-focused features.

## Phase 1: Database Foundation (Saturday Morning)

### 1. PostgreSQL Schema Implementation
```sql
-- Create new database schema with:
-- - Smart geopolitical cities filtering
-- - Photographer/Model only user types  
-- - Art-focused specialties (no brands/street)
-- - Flexible JSONB for future expansion
-- - Model characteristics (mandatory: gender, age, height, weight)
```

### 2. Seed Data Creation
- User types: Photographer, Model
- Specialties: Art Nude, Portrait, Dance, Yoga, Tattoo, Creative, Editorial, Beauty
- Cities: ~2,500 filtered from GeoNames (geopolitically relevant)

### 3. Migration Script
- Backup current in-memory data
- Migrate existing users/photos to PostgreSQL
- Preserve Firebase UIDs and photo URLs

## Phase 2: Frontend Migration (Saturday Afternoon)

### 1. Deploy Lumen Prototype
- Move claudesk-code/lumen-prototype to lumen-gcp/frontend
- Integrate Firebase authentication
- Connect to new backend API endpoints

### 2. Discovery Modes Implementation
- Latest Work (chronological feed)
- Photographers (people-first discovery)
- Models (people-first discovery)  
- Nearby (30km geographic matching)

### 3. Authentication Fix
- Single login page with progressive data entry
- Required fields: handle, name, city, user_type
- Model-specific mandatory fields: gender, age, height, weight

## Phase 3: API Integration (Sunday)

### 1. New Discovery Endpoints
```python
GET /api/v1/discovery/photographers
GET /api/v1/discovery/models  
GET /api/v1/discovery/nearby?city_id=123
GET /api/v1/photos/recent
```

### 2. Profile Management
```python
POST /api/v1/profile/complete  # Progressive data entry
PUT /api/v1/profile/specialties
PUT /api/v1/profile/characteristics  # Models only
```

### 3. Image Processing Pipeline
- Entry points for future MozJPEG compression
- Multiple format generation structure
- Maintain current Pillow for now

## Phase 4: Professional Features (Sunday Evening)

### 1. Collaborator Tagging
- @ mention system (users vs text)
- Real-time user lookup
- Photographer/model role assignment

### 2. Geographic Privacy
- City required for matching
- Privacy controls for display
- "São Paulo, Brazil" vs "Brazil" options

### 3. Admin Interface (Basic)
- Manual AI tagging trigger
- User management
- Content moderation tools

## Success Criteria

### Technical
- PostgreSQL migration complete with zero data loss
- New frontend fully functional with auth
- Discovery modes working with real data
- Geographic search operational

### Business
- Photographer-first design implemented
- Model discovery and characteristics functional
- Professional networking foundation ready
- Art-focused specialties system active

## Deployment Strategy
- Keep current backend running during migration
- Test new features on development branch
- Gradual rollout with fallback capability
- Preserve existing user authentication

## Next Steps Post-Weekend
- AI tagging integration (Google Vision)
- TV display mode implementation
- Portfolio vs feed separation
- Magazine integration planning

---
*Ready to build a professional photography platform that serves creators, not exploits them.*