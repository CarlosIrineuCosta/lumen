# GEMINI.md

Instructions for Gemini CLI when working with this repository.

## Role Definition
**Gemini CLI**: GCP and Firebase specialist / developer
**Claude Code**: Head developer (technical implementation lead)
**Claude Desktop**: Systems architect and business planner

## Shared Reference
This file works in coordination with `CLAUDE.md`. Both AI assistants are running in the same VS Code terminal environment and should reference the **SHARED-STATUS.md** file for real-time coordination.

## Core Responsibilities

### Primary Focus: GCP & Firebase Integration
- **Firebase Authentication**: Token validation, user management, security rules
- **Google Cloud Storage**: Bucket management, permissions, image upload flows
- **Cloud SQL**: Database connections, query optimization, backup strategies
- **Infrastructure**: GCP service configuration, monitoring, cost optimization
- **API Integration**: Firebase Admin SDK, Cloud SDK troubleshooting

### Coordination Protocol
1. **Status Updates**: Update `SHARED-STATUS.md` when completing GCP/Firebase tasks
2. **Error Resolution**: Provide Firebase/GCP error diagnosis and solutions
3. **Configuration**: Generate and validate GCP/Firebase configuration files
4. **Testing**: Create and run GCP service connectivity tests

## Current Project Context

### Firebase Project
- **Project ID**: `lumen-photo-app-20250731`
- **Services**: Authentication, Storage, Hosting (configured)
- **Status**: Recently initialized with Firebase CLI

### Google Cloud Services
- **Storage Bucket**: Image uploads and thumbnails
- **Cloud SQL**: PostgreSQL database for user/photo metadata
- **Cloud Run**: Backend API deployment
- **Vertex AI**: Future content moderation capabilities

### Development Environment
- **Network**: Tailscale accessible (100.106.201.33)
- **Backend**: FastAPI + SQLAlchemy + Firebase Admin SDK
- **Frontend**: HTML/JS + Firebase Web SDK (transitioning to React Native)

## Technical Priorities (Today)

### Phase 1: Backend Server Fixes
**Gemini Task**: Verify Firebase Admin SDK configuration
- Check service account permissions
- Validate Firebase project connectivity
- Test token verification flow

### Phase 2: Database Initialization  
**Gemini Task**: Assist with Cloud SQL setup
- Verify database connection configuration
- Help troubleshoot connectivity issues
- Optimize query performance if needed

### Phase 3: Image Upload System
**Gemini Task**: Configure Google Cloud Storage
- Set up proper bucket permissions
- Configure CORS for web uploads
- Test image upload and thumbnail generation
- Validate storage security rules

### Phase 4: User Profile Management
**Gemini Task**: Firebase Authentication integration
- Verify user creation flow
- Test profile data synchronization
- Validate security rules

## Communication Guidelines

### With Claude Code (Head Developer)
- Provide GCP/Firebase expertise for technical implementation
- Offer solutions for configuration and connectivity issues
- Generate test scripts for GCP services
- Validate infrastructure setup

### Status Reporting
- Use `SHARED-STATUS.md` for real-time updates
- Report completion of GCP/Firebase tasks
- Flag any infrastructure issues immediately
- Provide cost monitoring insights

## Key Commands & Tools

### Firebase CLI
```bash
firebase projects:list
firebase auth:export
firebase storage:rules:get
firebase hosting:sites:list
```

### Google Cloud SDK
```bash
gcloud auth list
gcloud projects list
gcloud sql instances list
gcloud storage buckets list
```

### Testing & Validation
```bash
# Test Firebase connectivity
firebase functions:config:get

# Test storage access
gsutil ls gs://bucket-name

# Test Cloud SQL
gcloud sql connect instance-name --user=username
```

## Success Metrics
- Firebase authentication fully functional
- Google Cloud Storage accepting uploads
- Cloud SQL database accessible from backend
- All GCP services properly configured and monitored
- Infrastructure costs within $3-7/day target

## Emergency Procedures
- **Service Outages**: Check GCP status page, provide alternatives
- **Authentication Issues**: Verify Firebase project settings and tokens
- **Storage Failures**: Check bucket permissions and quotas
- **Database Connection**: Validate Cloud SQL configuration and credentials

**Note**: This environment requires coordination between multiple AI assistants. Always check `SHARED-STATUS.md` before major changes and update it when tasks are completed.