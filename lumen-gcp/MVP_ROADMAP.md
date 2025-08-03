# Lumen MVP Roadmap - Ready for User Testing

## Current Status
**AUTHENTICATION**: Complete - Firebase Google OAuth working with user avatars
**FRONTEND**: 500px-style Justified Gallery framework in place
**BACKEND**: Models complete, server startup in progress
**DATABASE**: PostgreSQL schema ready, needs initialization

## Critical MVP Features for Demo

### 1. USER MANAGEMENT
- [ ] **Logout button** in user profile dropdown
- [ ] **Profile edit form** with:
  - Display name, bio, city selection
  - Photography styles/specialties selection
  - Model-specific fields (gender, age, height, weight)
  - Profile image upload capability

### 2. IMAGE FUNCTIONALITY
- [ ] **Image upload system**:
  - Drag & drop interface
  - Firebase Storage integration
  - Automatic thumbnail generation
  - Basic metadata capture (camera data)
- [ ] **User uploads view**:
  - Display user's own photos
  - Edit/delete photo capabilities
  - Portfolio vs general feed toggle

### 3. PHOTO STREAM
- [ ] **Main photo feed**:
  - All photos in chronological stream
  - 500px-style mosaic layout (Justified Gallery)
  - Infinite scroll pagination
  - Basic filtering until advanced discovery is built

### 4. TECHNICAL INFRASTRUCTURE
- [ ] **Backend server** running successfully
- [ ] **Database initialization** with schema and seed data
- [ ] **API endpoints**:
  - Photo upload/management
  - User profile CRUD
  - Photo stream with pagination
- [ ] **Frontend-backend integration**:
  - Replace mock data with real API calls
  - Error handling and loading states

## Success Criteria
**"Minimalistic MVP for showing around and talking to people"**

1. User can sign in/sign out (DONE)
2. User can upload images
3. User can edit basic profile data
4. User can see their own uploads
5. User can browse photo stream (all photos)
6. 500px-style photo display works properly

## Technical Notes

### Database Schema
- Users: Flexible JSONB schema with mandatory model fields
- Photos: Collaborative tagging, metadata, privacy controls
- Cities: ~2500 geopolitically relevant locations
- Specialties: Art-focused categories (Portrait, Fashion, Lifestyle, Fitness, Pole Dance, Bikini)

### Firebase Integration
- Authentication: Google OAuth with domain authorization
- Storage: Image uploads with automatic thumbnail generation
- Security: Proper Firebase rules for user data isolation

### Gallery Implementation
- Justified Gallery library (same as 500px)
- Responsive mosaic layout
- Hover overlays with photographer info
- Lightbox with metadata display

## Research Tasks
- [ ] **500px open source repo**: Study gallery implementation patterns
- [ ] **GitHub setup**: Prepare repository for version control
- [ ] **Documentation coordination**: Sync with Claude Opus spec evolution

## Coordination Warning
Claude Opus is evolving business specs in parallel. Need unified documentation structure to prevent conflicts between planning and implementation pace.

## Next Session Priority
1. Fix backend server startup
2. Initialize database with real data
3. Implement image upload flow
4. Connect frontend to backend APIs
5. Add user profile management

This roadmap provides a working demo for user feedback before building advanced discovery and networking features.