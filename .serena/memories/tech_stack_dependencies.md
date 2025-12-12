# Lumen Technology Stack & Dependencies

## Backend Dependencies (FastAPI/Python)

### Core Framework
- **FastAPI**: 0.104.1 - Web framework with automatic API documentation
- **Uvicorn**: 0.24.0 - ASGI server with standards support
- **Pydantic**: 2.5.0 - Data validation and serialization
- **SQLAlchemy**: 2.0.23 - ORM with advanced features
- **Alembic**: 1.13.1 - Database migration tool

### Database & Storage
- **psycopg2-binary**: 2.9.9 - PostgreSQL adapter
- **cloud-sql-python-connector**: 1.9.0 - Cloud SQL connection
- **google-cloud-storage**: 2.10.0 - File storage
- **google-cloud-firestore**: 2.11.1 - NoSQL database (if needed)

### Authentication & Security
- **firebase-admin**: 6.3.0 - Server-side Firebase SDK
- **python-jose[cryptography]**: 3.3.0 - JWT handling
- **passlib[bcrypt]**: 1.7.4 - Password hashing

### Google Cloud Services
- **google-cloud-secret-manager**: 2.17.0 - Secrets management
- **google-cloud-aiplatform**: 1.38.1 - AI/ML services
- **google-cloud-storage**: 2.10.0 - Object storage

### Image Processing & Utilities
- **Pillow**: 10.1.0 - Image manipulation
- **python-multipart**: 0.0.6 - File upload handling
- **httpx**: 0.25.2 - HTTP client
- **stripe**: 7.8.0 - Payment processing

### Monitoring & Logging
- **prometheus-client**: 0.19.0 - Metrics collection
- **structlog**: 23.2.0 - Structured logging
- **pydantic-settings**: 2.1.0 - Configuration management

## Frontend Dependencies (Expo/React Native)

### Core Framework
- **Expo**: ~49.0.0 - React Native development platform
- **React**: 18.2.0 - UI library
- **React Native**: 0.72.0 - Mobile framework
- **React Native Web**: ~0.19.0 - Web support

### Navigation & UI
- **@react-navigation/native**: ^6.1.0 - Navigation system
- **@react-navigation/stack**: ^6.3.0 - Stack navigator

### Services & Utilities
- **Firebase**: ^10.5.0 - Authentication and storage client
- **expo-image-picker**: ~14.3.0 - Image selection
- **expo-constants**: ~14.4.0 - App constants

### Development Tools
- **TypeScript**: ^5.1.0 - Type checking
- **@babel/core**: ^7.20.0 - JavaScript compiler
- **@types/react**: ~18.2.0 - React type definitions
- **@types/react-native**: ~0.72.0 - React Native types

## Current Frontend (Temporary Web Interface)
- **Vanilla JavaScript**: Direct DOM manipulation
- **jQuery**: Element selection and manipulation
- **Justified Gallery**: 500px-style photo mosaic layout
- **Firebase Web SDK**: Client-side authentication

## Infrastructure Dependencies

### Google Cloud Platform
- **Cloud Run**: Containerized backend hosting
- **Cloud SQL**: PostgreSQL database service
- **Cloud Storage**: Image and file storage
- **Cloud Build**: CI/CD pipeline
- **Secret Manager**: Secure configuration storage
- **Vertex AI**: ML/AI capabilities
- **Cloud Monitoring**: Application monitoring
- **Cloud Logging**: Centralized logging

### Development Tools
- **Docker**: Container platform
- **Terraform**: Infrastructure as code
- **Google Cloud SDK**: CLI tools and libraries

## Database Technology
- **PostgreSQL**: Primary database with JSONB support for flexible schemas
- **JSONB**: Schema flexibility for user profiles and metadata
- **UUID**: Primary keys for global uniqueness
- **Full-text search**: Built-in PostgreSQL capabilities

## Authentication Architecture
- **Firebase Authentication**: User management and social login
- **Firebase Admin SDK**: Server-side token verification
- **Google OAuth**: Primary authentication method
- **JWT Tokens**: Stateless authentication between client and server

## Storage Architecture
- **Google Cloud Storage**: Image and file storage with CDN
- **Firebase Storage**: Alternative client-side uploads (if needed)
- **Automatic thumbnails**: Server-side image processing

## Development Environment
- **Python**: 3.11.x (reference environment)
- **Node.js**: For frontend development
- **Linux**: Development server environment
- **Tailscale**: Network access and development connectivity